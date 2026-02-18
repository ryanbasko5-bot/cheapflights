"""
DUFFEL API CLIENT
Already have credentials - fastest to integrate!
NDC partnerships with airlines = accurate real-time pricing
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class DuffelClient:
    """Client for Duffel Flights API"""
    
    BASE_URL = "https://api.duffel.com"
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv('DUFFEL_API_TOKEN')
        if not self.api_token:
            raise ValueError("DUFFEL_API_TOKEN not found in .env")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Duffel-Version': 'v2',
            'Accept': 'application/json'
        }
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1,
        cabin_class: str = 'economy'
    ) -> List[Dict]:
        """Search for flights"""
        
        slices = [{
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date
        }]
        
        if return_date:
            slices.append({
                'origin': destination,
                'destination': origin,
                'departure_date': return_date
            })
        
        payload = {
            'data': {
                'slices': slices,
                'passengers': [{'type': 'adult'} for _ in range(passengers)],
                'cabin_class': cabin_class
            }
        }
        
        try:
            response = requests.post(
                f'{self.BASE_URL}/air/offer_requests',
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            # Get offers
            if 'data' in data and 'offers' in data['data']:
                return data['data']['offers']
            
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"Duffel API error: {str(e)}")
            return []
    
    def get_cheapest_price(
        self,
        origin: str,
        destination: str,
        days_ahead: int = 45
    ) -> Optional[Dict]:
        """Get cheapest flight price"""
        
        dep_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        ret_date = (datetime.now() + timedelta(days=days_ahead + 7)).strftime('%Y-%m-%d')
        
        offers = self.search_flights(origin, destination, dep_date, ret_date)
        
        if offers:
            cheapest = min(offers, key=lambda x: float(x['total_amount']))
            return {
                'price': float(cheapest['total_amount']),
                'currency': cheapest['total_currency'],
                'airline': cheapest['owner']['name'] if 'owner' in cheapest else 'Multiple',
                'cabin': cheapest['slices'][0]['segments'][0]['passengers'][0]['cabin_class_marketing_name']
            }
        
        return None


def test_duffel():
    """Test Duffel API"""
    try:
        client = DuffelClient()
        print("✅ Duffel API configured")
        print("🔍 Testing flight search JFK → LHR...")
        
        result = client.get_cheapest_price('JFK', 'LHR')
        
        if result:
            print(f"✅ Found flight: {result['currency']} {result['price']}")
            print(f"   Airline: {result['airline']}")
            print(f"   Cabin: {result['cabin']}")
            return True
        else:
            print("⚠️  No results (may need to wait for offers)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_duffel()
