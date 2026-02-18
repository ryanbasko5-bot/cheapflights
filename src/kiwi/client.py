"""
Kiwi.com Tequila API Integration
Better than Amadeus for:
- Historical price data built-in
- More flexible search
- Better for mistake fares
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class KiwiClient:
    """Client for Kiwi.com Tequila API"""
    
    BASE_URL = "https://api.tequila.kiwi.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('KIWI_API_KEY')
        if not self.api_key or self.api_key == 'your_api_key_here':
            raise ValueError("KIWI_API_KEY not set. Get one from: https://tequila.kiwi.com/portal/login")
        
        self.headers = {
            'apikey': self.api_key,
            'Accept': 'application/json'
        }
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        date_from: str,
        date_to: str,
        return_from: Optional[str] = None,
        return_to: Optional[str] = None,
        adults: int = 1,
        currency: str = 'USD',
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for flights
        
        Args:
            origin: IATA airport code (e.g., 'JFK')
            destination: IATA airport code (e.g., 'LHR')
            date_from: Earliest departure date (YYYY-MM-DD)
            date_to: Latest departure date (YYYY-MM-DD)
            return_from: Earliest return date (for round trip)
            return_to: Latest return date (for round trip)
            adults: Number of passengers
            currency: Currency code
            max_results: Max results to return
        """
        endpoint = f"{self.BASE_URL}/v2/search"
        
        params = {
            'fly_from': origin,
            'fly_to': destination,
            'date_from': date_from,
            'date_to': date_to,
            'adults': adults,
            'curr': currency,
            'limit': max_results,
            'sort': 'price',  # Sort by cheapest first
            'flight_type': 'round' if return_from else 'oneway'
        }
        
        if return_from and return_to:
            params['return_from'] = return_from
            params['return_to'] = return_to
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Kiwi API error: {str(e)}")
            return []
    
    def get_cheapest_flight(
        self,
        origin: str,
        destination: str,
        days_ahead: int = 45,
        trip_length: int = 7,
        currency: str = 'USD'
    ) -> Optional[Dict]:
        """Get cheapest flight for a route"""
        
        date_from = (datetime.now() + timedelta(days=days_ahead)).strftime('%d/%m/%Y')
        date_to = (datetime.now() + timedelta(days=days_ahead + 3)).strftime('%d/%m/%Y')
        return_from = (datetime.now() + timedelta(days=days_ahead + trip_length)).strftime('%d/%m/%Y')
        return_to = (datetime.now() + timedelta(days=days_ahead + trip_length + 3)).strftime('%d/%m/%Y')
        
        flights = self.search_flights(
            origin=origin,
            destination=destination,
            date_from=date_from,
            date_to=date_to,
            return_from=return_from,
            return_to=return_to,
            currency=currency,
            max_results=1
        )
        
        if flights:
            flight = flights[0]
            return {
                'price': flight['price'],
                'currency': flight.get('currency', currency),
                'departure': flight['local_departure'],
                'return': flight['local_arrival'],
                'booking_link': flight['deep_link'],
                'airlines': ', '.join(flight.get('airlines', [])),
                'route': flight['route']
            }
        
        return None
    
    def get_price_range(
        self,
        origin: str,
        destination: str,
        currency: str = 'USD'
    ) -> Optional[Dict]:
        """
        Get price statistics for a route by sampling multiple dates
        This gives us a "typical price" baseline
        """
        prices = []
        
        # Sample 5 different future periods
        for days_ahead in [30, 45, 60, 75, 90]:
            flight = self.get_cheapest_flight(origin, destination, days_ahead, currency=currency)
            if flight:
                prices.append(flight['price'])
        
        if len(prices) >= 3:
            prices.sort()
            return {
                'min': min(prices),
                'max': max(prices),
                'median': prices[len(prices) // 2],
                'average': sum(prices) / len(prices),
                'samples': len(prices)
            }
        
        return None
    
    def find_deals(
        self,
        routes: List[tuple],
        min_savings_pct: float = 20.0
    ) -> List[Dict]:
        """
        Find deals across multiple routes
        
        Args:
            routes: List of (origin, destination, route_name) tuples
            min_savings_pct: Minimum savings percentage to qualify as deal
        
        Returns:
            List of deals with pricing data
        """
        deals = []
        
        for origin, dest, route_name in routes:
            print(f"📊 Scanning {route_name}...")
            
            # Get currency for origin airport
            from src.utils.currency import get_currency_for_airport
            currency = get_currency_for_airport(origin)
            
            # Get typical price range
            price_stats = self.get_price_range(origin, dest, currency)
            
            if not price_stats:
                print(f"   ⚠️  Insufficient data - skipping")
                continue
            
            typical_price = price_stats['median']
            print(f"   📈 Typical price: {currency} {typical_price:.0f}")
            
            # Get current best price
            current = self.get_cheapest_flight(origin, dest, days_ahead=45, currency=currency)
            
            if not current:
                print(f"   ⚠️  No current prices - skipping")
                continue
            
            current_price = current['price']
            print(f"   💰 Current price: {currency} {current_price:.0f}")
            
            # Calculate savings
            savings_pct = ((typical_price - current_price) / typical_price) * 100
            
            if savings_pct >= min_savings_pct:
                emoji = "⚡" if savings_pct >= 50 else "✅"
                label = "MISTAKE FARE" if savings_pct >= 50 else "Great Deal"
                print(f"   {emoji} {savings_pct:.0f}% off - {label}")
                
                deals.append({
                    'origin': origin,
                    'destination': dest,
                    'route_name': route_name,
                    'current_price': current_price,
                    'typical_price': typical_price,
                    'savings_pct': savings_pct,
                    'currency': currency,
                    'booking_link': current['booking_link'],
                    'airlines': current['airlines'],
                    'departure': current['departure'],
                    'return': current['return'],
                    'is_mistake': savings_pct >= 50,
                    'price_stats': price_stats
                })
            else:
                print(f"   ➖ Only {savings_pct:.0f}% off - not a deal")
            
            print("")
        
        return deals


# Test if API key is configured
def test_kiwi_api():
    """Test Kiwi API connection"""
    try:
        client = KiwiClient()
        print("✅ Kiwi API configured")
        
        # Test search
        print("\n🔍 Testing flight search JFK → LHR...")
        flight = client.get_cheapest_flight('JFK', 'LHR', currency='USD')
        
        if flight:
            print(f"✅ Found flight: USD {flight['price']}")
            print(f"   Airlines: {flight['airlines']}")
            print(f"   Link: {flight['booking_link'][:50]}...")
            return True
        else:
            print("❌ No flights found")
            return False
            
    except ValueError as e:
        print(f"❌ {str(e)}")
        print("\n📝 Setup instructions:")
        print("   1. Go to: https://tequila.kiwi.com/portal/login")
        print("   2. Sign up (free)")
        print("   3. Get API key from dashboard")
        print("   4. Add to .env: KIWI_API_KEY=your_key_here")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == '__main__':
    test_kiwi_api()
