"""
SERPAPI CLIENT - Google Flights Scraper
SOLVES PRICING ACCURACY: Gets exact data users see on Google Flights
"""

import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

class SerpAPIClient:
    """Client for SerpAPI Google Flights"""
    
    BASE_URL = "https://serpapi.com/search"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPAPI_KEY')
        if not self.api_key or self.api_key == 'your_key_here':
            raise ValueError("Get SerpAPI key from: https://serpapi.com/users/sign_up")
    
    def search_google_flights(
        self,
        origin: str,
        destination: str,
        outbound_date: str,
        return_date: Optional[str] = None,
        currency: str = 'USD'
    ) -> Optional[Dict]:
        """
        Search Google Flights - gets EXACT data from Google
        
        Args:
            origin: IATA code (e.g., 'JFK')
            destination: IATA code (e.g., 'LHR')
            outbound_date: YYYY-MM-DD
            return_date: YYYY-MM-DD (optional for one-way)
            currency: Currency code
        """
        
        params = {
            'engine': 'google_flights',
            'departure_id': origin,
            'arrival_id': destination,
            'outbound_date': outbound_date,
            'currency': currency,
            'hl': 'en',
            'api_key': self.api_key
        }
        
        if return_date:
            params['return_date'] = return_date
            params['type'] = '1'  # Round trip
        else:
            params['type'] = '2'  # One way
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Get cheapest flight
            if 'best_flights' in data and data['best_flights']:
                cheapest = data['best_flights'][0]
                return {
                    'price': cheapest['price'],
                    'currency': currency,
                    'airline': cheapest['flights'][0]['airline'],
                    'duration': cheapest['total_duration'],
                    'google_booking_link': cheapest.get('booking_token', '')
                }
            
            # Fallback to other flights
            elif 'other_flights' in data and data['other_flights']:
                cheapest = data['other_flights'][0]
                return {
                    'price': cheapest['price'],
                    'currency': currency,
                    'airline': cheapest['flights'][0]['airline'],
                    'duration': cheapest['total_duration'],
                    'google_booking_link': cheapest.get('booking_token', '')
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"SerpAPI error: {str(e)}")
            return None
    
    def get_price_history(
        self,
        origin: str,
        destination: str
    ) -> Optional[Dict]:
        """Get price insights and typical prices from Google"""
        
        params = {
            'engine': 'google_flights',
            'departure_id': origin,
            'arrival_id': destination,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'price_insights' in data:
                return data['price_insights']
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"SerpAPI error: {str(e)}")
            return None


def test_serpapi():
    """Test SerpAPI"""
    try:
        client = SerpAPIClient()
        print("✅ SerpAPI configured")
        return True
    except ValueError as e:
        print(f"❌ {str(e)}")
        print("\n📝 Quick setup:")
        print("   1. Go to: https://serpapi.com/users/sign_up")
        print("   2. Sign up (100 free searches/month)")
        print("   3. Copy API key")
        print("   4. Update .env: SERPAPI_KEY=your_key")
        return False

if __name__ == '__main__':
    test_serpapi()
