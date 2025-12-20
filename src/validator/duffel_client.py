"""
Duffel API Client for Fare Validation

Uses Duffel API to validate that detected fares are actually bookable.
This maintains a healthy Look-to-Book ratio by only checking validated leads.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class DuffelValidator:
    """
    Duffel API client for validating mistake fares.
    
    Confirms that a detected fare is actually bookable before alerting.
    """
    
    BASE_URL = "https://api.duffel.com"
    
    def __init__(self):
        """Initialize Duffel client."""
        self.api_token = settings.duffel_api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Duffel-Version": "v1",
            "Content-Type": "application/json"
        }
        
    async def validate_fare(
        self,
        origin: str,
        destination: str,
        expected_price: float,
        departure_date: Optional[str] = None,
        price_tolerance: float = 0.15  # Allow 15% variance
    ) -> bool:
        """
        Validate that a fare is actually bookable.
        
        Args:
            origin: IATA origin code
            destination: IATA destination code
            expected_price: The price we expect to find
            departure_date: Optional specific departure date (YYYY-MM-DD)
            price_tolerance: Acceptable price variance (default 15%)
            
        Returns:
            True if fare is bookable within tolerance, False otherwise
        """
        if not self.api_token:
            logger.warning("Duffel API token not configured, skipping validation")
            return False
            
        try:
            # Create offer request
            offer_request = await self._create_offer_request(
                origin=origin,
                destination=destination,
                departure_date=departure_date
            )
            
            if not offer_request:
                return False
                
            # Get offers
            offers = await self._get_offers(offer_request["id"])
            
            if not offers:
                logger.warning(f"No offers found for {origin} to {destination}")
                return False
                
            # Check if any offer matches our expected price
            min_price = expected_price * (1 - price_tolerance)
            max_price = expected_price * (1 + price_tolerance)
            
            for offer in offers:
                offer_price = float(offer.get("total_amount", 0))
                
                if min_price <= offer_price <= max_price:
                    logger.info(
                        f"✅ Fare validated: {origin}-{destination} "
                        f"at ${offer_price} (expected ${expected_price})"
                    )
                    return True
                    
            logger.info(
                f"❌ No offers within tolerance. Expected ${expected_price}, "
                f"found range ${offers[0].get('total_amount')} - ${offers[-1].get('total_amount')}"
            )
            return False
            
        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return False
            
    async def _create_offer_request(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create an offer request for flight search."""
        # Default to 2 weeks from now if no date specified
        if not departure_date:
            departure = datetime.now() + timedelta(days=14)
            departure_date = departure.strftime("%Y-%m-%d")
            
        # Return date 7 days later
        return_date = (datetime.strptime(departure_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        
        payload = {
            "data": {
                "slices": [
                    {
                        "origin": origin,
                        "destination": destination,
                        "departure_date": departure_date
                    },
                    {
                        "origin": destination,
                        "destination": origin,
                        "departure_date": return_date
                    }
                ],
                "passengers": [
                    {
                        "type": "adult"
                    }
                ],
                "cabin_class": "economy"  # Can be parameterized later
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/air/offer_requests",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 201:
                    return response.json().get("data")
                else:
                    logger.error(f"Offer request failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating offer request: {e}")
            return None
            
    async def _get_offers(self, offer_request_id: str) -> list:
        """Retrieve offers for an offer request."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/air/offers",
                    headers=self.headers,
                    params={"offer_request_id": offer_request_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Get offers failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting offers: {e}")
            return []
            
    async def get_booking_link(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a direct booking link for the fare.
        
        Args:
            origin: IATA origin code
            destination: IATA destination code
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD)
            
        Returns:
            Deep link to Google Flights or booking page
        """
        # Generate Google Flights deep link
        # Format: https://www.google.com/flights?hl=en#flt={origin}.{dest}.{date}*{dest}.{origin}.{return}
        
        if not return_date:
            return_date = (datetime.strptime(departure_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
            
        # Convert YYYY-MM-DD to YYYY-MM-DD format for Google Flights
        dep_formatted = departure_date.replace("-", "")
        ret_formatted = return_date.replace("-", "")
        
        link = (
            f"https://www.google.com/flights?hl=en#flt="
            f"{origin}.{destination}.{dep_formatted}*"
            f"{destination}.{origin}.{ret_formatted}"
        )
        
        return link


class KiwiValidator:
    """
    Alternative validator using Kiwi.com Tequila API.
    
    Can be used as backup if Duffel has issues.
    """
    
    BASE_URL = "https://api.tequila.kiwi.com"
    
    def __init__(self):
        """Initialize Kiwi client."""
        self.api_key = settings.kiwi_api_key
        self.headers = {
            "apikey": self.api_key
        }
        
    async def validate_fare(
        self,
        origin: str,
        destination: str,
        expected_price: float,
        departure_date: Optional[str] = None,
        price_tolerance: float = 0.15
    ) -> bool:
        """
        Validate fare using Kiwi API.
        
        Args:
            origin: IATA origin code
            destination: IATA destination code
            expected_price: Expected price
            departure_date: Departure date
            price_tolerance: Price variance tolerance
            
        Returns:
            True if validated, False otherwise
        """
        if not self.api_key:
            logger.warning("Kiwi API key not configured")
            return False
            
        try:
            params = {
                "fly_from": origin,
                "fly_to": destination,
                "date_from": departure_date or (datetime.now() + timedelta(days=14)).strftime("%d/%m/%Y"),
                "date_to": departure_date or (datetime.now() + timedelta(days=14)).strftime("%d/%m/%Y"),
                "ret_from_diff_airport": 0,
                "ret_to_diff_airport": 0,
                "one_for_city": 1,
                "adults": 1,
                "curr": "USD"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/v2/search",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    flights = data.get("data", [])
                    
                    if not flights:
                        return False
                        
                    # Check if any flight matches expected price
                    min_price = expected_price * (1 - price_tolerance)
                    max_price = expected_price * (1 + price_tolerance)
                    
                    for flight in flights:
                        price = flight.get("price", 0)
                        if min_price <= price <= max_price:
                            logger.info(f"✅ Kiwi validated: {origin}-{destination} at ${price}")
                            return True
                            
                return False
                
        except Exception as e:
            logger.error(f"Kiwi validation error: {e}")
            return False
