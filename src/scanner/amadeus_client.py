"""
Amadeus API Client

Wrapper for Amadeus Flight Inspiration Search API.
Uses cached data to find price anomalies without aggressive live scraping.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from amadeus import Client, ResponseError

from src.config import settings

logger = logging.getLogger(__name__)


class AmadeusScanner:
    """
    Amadeus API client for finding mistake fares.
    
    Uses the "Flight Inspiration Search" endpoint which returns cached pricing
    data, avoiding the Look-to-Book ratio issues with live search APIs.
    """
    
    def __init__(self):
        """Initialize Amadeus client."""
        self.client = Client(
            client_id=settings.amadeus_api_key,
            client_secret=settings.amadeus_api_secret,
            hostname="test" if settings.amadeus_env == "test" else "production"
        )
        
    def search_inspiration(
        self,
        origin: str,
        max_price: Optional[int] = None,
        departure_date_start: Optional[str] = None,
        departure_date_end: Optional[str] = None,
        destination: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Use Flight Inspiration Search API - queries CACHED data, not live inventory.
        This is the legal "loophole" - we're filtering market intelligence, not scraping.
        
        Args:
            origin: IATA airport code (e.g., "SYD", "JFK")
            max_price: Maximum price to filter by
            departure_date_start: YYYY-MM-DD format (optional)
            departure_date_end: YYYY-MM-DD format (optional)
            destination: Specific destination (optional)
            
        Returns:
            List of destination pricing data from Amadeus cache
        """
        try:
            # Use Flight INSPIRATION Search (cached data, not live inventory)
            params = {"origin": origin}
            if max_price:
                params["maxPrice"] = max_price
            if destination:
                params["destination"] = destination
            if departure_date_start:
                params["departureDate"] = f"{departure_date_start},{departure_date_end or departure_date_start}"
                
            # This endpoint returns CACHED prices found by other users
            # It does NOT hit airline reservation systems directly
            response = self.client.shopping.flight_destinations.get(**params)
            
            if response.data:
                logger.info(f"📊 Inspiration API: Found {len(response.data)} cached destinations from {origin}")
                return [self._parse_flight_destination(item) for item in response.data]
            return []
            
        except ResponseError as error:
            logger.error(f"Amadeus API error: {error}")
            return []
            
    def search_flight_inspiration(
        self,
        origin: str,
        destination: Optional[str] = None,
        max_price: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for flight inspiration (cached pricing trends).
        
        Args:
            origin: IATA airport code
            destination: Optional destination IATA code
            max_price: Maximum price filter
            
        Returns:
            List of flight pricing data
        """
        try:
            params = {"origin": origin}
            if destination:
                params["destination"] = destination
            if max_price:
                params["maxPrice"] = max_price
                
            # Use Flight Inspiration Search - returns cached data
            response = self.client.shopping.flight_dates.get(**params)
            
            if response.data:
                logger.info(f"Found {len(response.data)} flight options from {origin}")
                return [self._parse_flight_date(item) for item in response.data]
            return []
            
        except ResponseError as error:
            logger.error(f"Amadeus API error: {error}")
            return []
            
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
            "links": data.get("links", {})
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
    Detects price anomalies by comparing cached inspiration data to historical averages.
    
    This is the "Market Intelligence" filter - we're not scraping, we're analyzing
    publicly available cached data from Amadeus to identify pricing anomalies.
    """
    
    def __init__(self, db_session):
        """
        Initialize detector with database session.
        
        Args:
            db_session: SQLAlchemy session for price history lookups
        """
        self.db = db_session
        self.scanner = AmadeusScanner()
        
    async def scan_routes(
        self,
        origins: List[str],
        min_savings: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Scan multiple origin airports for price anomalies.
        
        Args:
            origins: List of IATA airport codes to scan
            min_savings: Minimum dollar savings to flag (default from config)
            threshold: Price drop percentage threshold (default from config)
            
        Returns:
            List of detected anomalies
        """
        min_savings = min_savings or settings.min_savings_amount
        threshold = threshold or settings.price_drop_threshold
        
        anomalies = []
        
        for origin in origins:
            logger.info(f"🔍 Querying Amadeus Inspiration API for {origin}...")
            
            # Get CACHED prices from Inspiration API (not live scraping)
            destinations = self.scanner.search_inspiration(origin)
            
            for dest_data in destinations:
                anomaly = await self._check_for_anomaly(
                    dest_data,
                    min_savings=min_savings,
                    threshold=threshold
                )
                
                if anomaly:
                    anomalies.append(anomaly)
                    logger.warning(
                        f"🚨 ANOMALY DETECTED: {anomaly['route']} - "
                        f"${anomaly['current_price']} (normally ${anomaly['historical_avg']})"
                    )
                    
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
    # US Major Hubs
    "JFK", "EWR", "LGA",  # New York
    "LAX", "SFO",  # California
    "ORD",  # Chicago
    "MIA", "FLL",  # Florida
    "DFW", "IAH",  # Texas
    "SEA", "BOS", "DCA",
    
    # European Hubs
    "LHR", "CDG", "FRA", "AMS", "MAD",
    
    # Asian Hubs
    "NRT", "HND", "ICN", "HKG", "SIN",
]
