"""
Amadeus Multi-API Client

Uses 3 Amadeus APIs together for robust mistake fare detection:

1. Flight Inspiration Search  → Cast a wide net (cached prices, cheap)
2. Flight Offers Search       → Confirm deal is bookable right now (live)
3. Flight Price Analysis      → Verify price is abnormally low (analytics)

Pipeline: Inspiration finds candidates → Offers confirms they're real →
          Price Analysis proves they're actually anomalies.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from amadeus import Client, ResponseError

from src.config import settings

logger = logging.getLogger(__name__)


class AmadeusScanner:
    """
    Multi-API Amadeus client for finding and verifying mistake fares.
    """

    def __init__(self):
        """Initialize Amadeus client."""
        self.client = Client(
            client_id=settings.amadeus_api_key,
            client_secret=settings.amadeus_api_secret,
            hostname="test" if settings.amadeus_env == "test" else "production",
        )

    # ------------------------------------------------------------------
    # API 1: Flight Inspiration Search (cached, cheap, wide net)
    # ------------------------------------------------------------------
    def search_inspiration(
        self,
        origin: str,
        max_price: Optional[int] = None,
        departure_date_start: Optional[str] = None,
        departure_date_end: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Flight Inspiration Search — returns CACHED pricing data.
        Low cost, no look-to-book concerns. Casts a wide net.
        """
        try:
            params = {"origin": origin}
            if max_price:
                params["maxPrice"] = max_price
            if destination:
                params["destination"] = destination
            if departure_date_start:
                params["departureDate"] = (
                    f"{departure_date_start},{departure_date_end or departure_date_start}"
                )

            response = self.client.shopping.flight_destinations.get(**params)

            if response.data:
                logger.info(
                    f"📊 Inspiration API: {len(response.data)} destinations from {origin}"
                )
                return [self._parse_flight_destination(item) for item in response.data]
            return []

        except ResponseError as error:
            logger.error(f"Inspiration API error for {origin}: {error}")
            return []

    # ------------------------------------------------------------------
    # API 1b: Flight Cheapest Date Search (cached, date-level prices)
    # ------------------------------------------------------------------
    def search_cheapest_dates(
        self,
        origin: str,
        destination: str,
    ) -> List[Dict[str, Any]]:
        """
        Flight Cheapest Date Search — cached date-level pricing.
        Useful to find the absolute cheapest travel dates for a route.
        """
        try:
            response = self.client.shopping.flight_dates.get(
                origin=origin, destination=destination
            )
            if response.data:
                logger.info(
                    f"📅 Cheapest Dates: {len(response.data)} dates for {origin}→{destination}"
                )
                return [self._parse_flight_date(item) for item in response.data]
            return []

        except ResponseError as error:
            logger.error(f"Cheapest Dates API error {origin}→{destination}: {error}")
            return []

    # ------------------------------------------------------------------
    # API 2: Flight Offers Search (live inventory — confirms bookability)
    # ------------------------------------------------------------------
    def verify_offer_exists(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        max_results: int = 3,
    ) -> Optional[Dict[str, Any]]:
        """
        Flight Offers Search — hits LIVE inventory.
        Use sparingly (costs more, affects look-to-book ratio).
        Only call this to verify a candidate from Inspiration API.

        Returns the cheapest live offer if found, or None.
        """
        try:
            params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": departure_date,
                "adults": adults,
                "max": max_results,
                "currencyCode": "USD",
            }
            if return_date:
                params["returnDate"] = return_date

            response = self.client.shopping.flight_offers_search.get(**params)

            if response.data:
                cheapest = response.data[0]
                price = float(cheapest["price"]["total"])
                airline = (
                    cheapest.get("validatingAirlineCodes", ["??"])[0]
                )
                segments = cheapest.get("itineraries", [{}])[0].get("segments", [])
                cabin = "economy"
                if segments:
                    cabin = (
                        segments[0]
                        .get("travelerPricings", [{}])[0]
                        .get("fareDetailsBySegment", [{}])[0]
                        .get("cabin", "ECONOMY")
                        if "travelerPricings" in cheapest
                        else "economy"
                    )
                    # Try to extract cabin from the offer itself
                    for tp in cheapest.get("travelerPricings", []):
                        for fd in tp.get("fareDetailsBySegment", []):
                            cabin = fd.get("cabin", "ECONOMY").lower()
                            break
                        break

                logger.info(
                    f"✈️  Live Offer: {origin}→{destination} ${price} ({airline})"
                )
                return {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "price": price,
                    "currency": cheapest["price"].get("currency", "USD"),
                    "airline": airline,
                    "cabin_class": cabin,
                    "offer_id": cheapest.get("id"),
                    "bookable": True,
                    "raw_offer": cheapest,
                }
            return None

        except ResponseError as error:
            logger.error(f"Offers Search error {origin}→{destination}: {error}")
            return None

    # ------------------------------------------------------------------
    # API 3: Flight Price Analysis (is this price abnormally low?)
    # ------------------------------------------------------------------
    def analyze_price(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        one_way: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Flight Price Analysis — returns min/max/median historical pricing.
        Tells you whether a price is ACTUALLY a deal vs just normally cheap.

        Returns price analysis data or None.
        """
        try:
            params = {
                "originIataCode": origin,
                "destinationIataCode": destination,
                "departureDate": departure_date,
            }
            if one_way:
                params["oneWay"] = "true"

            response = self.client.analytics.itinerary_price_metrics.get(**params)

            if response.data:
                metrics = response.data[0]
                price_metrics = {}
                for pm in metrics.get("priceMetrics", []):
                    quartile = pm.get("quartileRanking")
                    amount = float(pm.get("amount", 0))
                    price_metrics[quartile] = amount

                result = {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "currency": metrics.get("currencyCode", "USD"),
                    "price_first_quartile": price_metrics.get("FIRST", 0),
                    "price_median": price_metrics.get("MEDIUM", 0),
                    "price_third_quartile": price_metrics.get("THIRD", 0),
                    "price_minimum": price_metrics.get("MINIMUM", 0),
                    "price_maximum": price_metrics.get("MAXIMUM", 0),
                }
                logger.info(
                    f"📈 Price Analysis {origin}→{destination}: "
                    f"min=${result['price_minimum']} median=${result['price_median']} "
                    f"max=${result['price_maximum']}"
                )
                return result

            return None

        except ResponseError as error:
            logger.error(f"Price Analysis error {origin}→{destination}: {error}")
            return None

    # ------------------------------------------------------------------
    # Parsers
    # ------------------------------------------------------------------
    def _parse_flight_destination(self, data: Dict) -> Dict[str, Any]:
        """Parse flight destination response."""
        return {
            "type": data.get("type"),
            "origin": data.get("origin"),
            "destination": data.get("destination"),
            "departure_date": data.get("departureDate"),
            "return_date": data.get("returnDate"),
            "price": float(data.get("price", {}).get("total", 0)),
            "currency": data.get("price", {}).get("currency", "USD"),
            "links": data.get("links", {}),
        }

    def _parse_flight_date(self, data: Dict) -> Dict[str, Any]:
        """Parse flight date response."""
        return {
            "type": data.get("type"),
            "origin": data.get("origin"),
            "destination": data.get("destination"),
            "departure_date": data.get("departureDate"),
            "return_date": data.get("returnDate"),
            "price": float(data.get("price", {}).get("total", 0)),
            "currency": data.get("price", {}).get("currency", "USD"),
        }


class PriceAnomalyDetector:
    """
    3-API Pipeline for detecting verified mistake fares.

    Step 1: Inspiration API → find cheap candidates (cached, cheap calls)
    Step 2: Price Analysis API → is this price abnormally low? (analytics)
    Step 3: Offers Search API → confirm it's actually bookable right now (live)

    Only deals that pass ALL 3 checks get published.
    """

    def __init__(self, db_session):
        self.db = db_session
        self.scanner = AmadeusScanner()

    async def scan_routes(
        self,
        origins: List[str],
        min_savings: int = None,
        threshold: float = None,
    ) -> List[Dict[str, Any]]:
        """Scan multiple origins through the 3-API pipeline."""
        min_savings = min_savings or settings.min_savings_amount
        threshold = threshold or settings.price_drop_threshold

        anomalies = []

        for origin in origins:
            logger.info(f"🔍 Step 1: Inspiration API for {origin}...")

            # --- STEP 1: Cast wide net with Inspiration API (cached) ---
            destinations = self.scanner.search_inspiration(origin)

            for dest_data in destinations:
                candidate = await self._check_for_anomaly(
                    dest_data, min_savings=min_savings, threshold=threshold
                )
                if not candidate:
                    continue

                dep_date = candidate.get("departure_date")
                dest = candidate["destination"]

                # --- STEP 2: Price Analysis — is this actually abnormal? ---
                if dep_date:
                    logger.info(f"📈 Step 2: Price Analysis for {origin}→{dest}...")
                    analysis = self.scanner.analyze_price(origin, dest, dep_date)

                    if analysis:
                        median = analysis.get("price_median", 0)
                        minimum = analysis.get("price_minimum", 0)
                        current = candidate["current_price"]

                        candidate["price_median"] = median
                        candidate["price_minimum"] = minimum
                        candidate["price_maximum"] = analysis.get("price_maximum", 0)

                        # If price is above the median, it's not a deal
                        if median > 0 and current >= median:
                            logger.info(
                                f"  ↳ Skipped: ${current} >= median ${median}"
                            )
                            continue

                        # Calculate how far below median
                        if median > 0:
                            pct_below_median = (median - current) / median
                            candidate["pct_below_median"] = pct_below_median
                            logger.info(
                                f"  ↳ {int(pct_below_median*100)}% below median ✅"
                            )

                # --- STEP 3: Live verification — is it bookable? ---
                if dep_date:
                    logger.info(f"✈️  Step 3: Live verify {origin}→{dest}...")
                    live_offer = self.scanner.verify_offer_exists(
                        origin,
                        dest,
                        dep_date,
                        return_date=candidate.get("return_date"),
                    )

                    if live_offer:
                        # Update candidate with live data
                        candidate["current_price"] = live_offer["price"]
                        candidate["airline"] = live_offer.get("airline")
                        candidate["cabin_class"] = live_offer.get("cabin_class")
                        candidate["bookable"] = True
                        candidate["booking_link"] = (
                            f"https://www.google.com/travel/flights?"
                            f"q=flights+from+{origin}+to+{dest}+on+{dep_date}"
                        )

                        # Recalculate savings with live price
                        historical = candidate["historical_avg"]
                        live_price = live_offer["price"]
                        candidate["savings_amount"] = historical - live_price
                        candidate["savings_percentage"] = (
                            (historical - live_price) / historical
                            if historical > 0
                            else 0
                        )

                        # Final check — still meets thresholds?
                        if (
                            candidate["savings_amount"] >= min_savings
                            and candidate["savings_percentage"] >= threshold
                        ):
                            logger.warning(
                                f"🚨 VERIFIED DEAL: {candidate['route']} - "
                                f"${live_price} (normally ${historical}, "
                                f"save {int(candidate['savings_percentage']*100)}%) "
                                f"[{live_offer.get('airline', '??')}]"
                            )
                            anomalies.append(candidate)
                        else:
                            logger.info(
                                f"  ↳ Live price ${live_price} no longer meets thresholds"
                            )
                    else:
                        logger.info(f"  ↳ Not bookable — skipping")
                else:
                    # No departure date — can't verify, use historical check only
                    anomalies.append(candidate)
                    logger.warning(
                        f"🚨 ANOMALY (unverified): {candidate['route']} - "
                        f"${candidate['current_price']}"
                    )

                # Small delay between API calls to stay within rate limits
                import asyncio
                await asyncio.sleep(1)

        return anomalies
        
    async def _check_for_anomaly(
        self,
        dest_data: Dict[str, Any],
        min_savings: int,
        threshold: float
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a price represents an anomaly.
        
        Args:
            dest_data: Destination pricing data
            min_savings: Minimum savings threshold
            threshold: Percentage drop threshold
            
        Returns:
            Anomaly data if detected, None otherwise
        """
        from src.models.database import PriceHistory
        from sqlalchemy import func
        
        origin = dest_data["origin"]
        destination = dest_data["destination"]
        current_price = dest_data["price"]
        
        # Get historical average for this route
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        avg_price = self.db.query(func.avg(PriceHistory.price)).filter(
            PriceHistory.origin == origin,
            PriceHistory.destination == destination,
            PriceHistory.checked_at >= thirty_days_ago
        ).scalar()
        
        if not avg_price:
            # No historical data - store current price and skip
            await self._store_price_history(dest_data)
            return None
            
        # Calculate savings
        savings_amount = avg_price - current_price
        savings_percentage = (savings_amount / avg_price) if avg_price > 0 else 0
        
        # Check if it meets anomaly criteria
        if savings_amount >= min_savings and savings_percentage >= threshold:
            return {
                "origin": origin,
                "destination": destination,
                "route": f"{origin} to {destination}",
                "current_price": current_price,
                "historical_avg": float(avg_price),
                "savings_amount": savings_amount,
                "savings_percentage": savings_percentage,
                "currency": dest_data["currency"],
                "departure_date": dest_data.get("departure_date"),
                "return_date": dest_data.get("return_date"),
                "detected_at": datetime.now().isoformat()
            }
            
        # Store current price for future comparisons
        await self._store_price_history(dest_data)
        return None
        
    async def _store_price_history(self, dest_data: Dict[str, Any]):
        """Store price data for historical comparison."""
        from src.models.database import PriceHistory
        
        price_record = PriceHistory(
            origin=dest_data["origin"],
            destination=dest_data["destination"],
            price=dest_data["price"],
            currency=dest_data["currency"],
            data_source="amadeus",
            checked_at=datetime.now()
        )
        
        self.db.add(price_record)
        self.db.commit()


# Pre-defined list of major airport hubs to scan
MAJOR_HUBS = [
    # 🇦🇺 Australia (primary market)
    "SYD", "MEL", "BNE", "PER", "ADL", "OOL", "CBR",

    # US Major Hubs
    "JFK", "LAX", "SFO", "ORD", "MIA", "DFW", "SEA",

    # European Hubs
    "LHR", "CDG", "FRA", "AMS", "MAD",

    # Asian Hubs (popular from AU)
    "NRT", "HND", "ICN", "HKG", "SIN", "BKK", "DPS",
]


def get_scan_batch(batch_size: int = None) -> List[str]:
    """
    Return ALL airports to scan every time.

    With a $100 AUD/month budget we can afford ~5,000 calls/month.
    Scanning all 26 airports every 3 hours (8x/day):
      26 calls × 8 scans = 208 Inspiration calls/day
      + anomaly verification calls (~20-30/day)
      ≈ 230-240 calls/day × 30 = ~7,000/month
      First 2,000 free, remaining ~5,000 × ~€0.01 ≈ €50 ≈ $85 AUD
    """
    return MAJOR_HUBS.copy()
