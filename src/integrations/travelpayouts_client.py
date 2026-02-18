"""
TRAVELPAYOUTS CLIENT - Affiliate + API
MAKES MONEY while getting data - affiliate commissions on every booking
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class TravelpayoutsClient:
    """Client for Travelpayouts API"""
    
    BASE_URL = "http://api.travelpayouts.com/v2"
    
    def __init__(self, token: Optional[str] = None, marker: Optional[str] = None):
        self.token = token or os.getenv('TRAVELPAYOUTS_TOKEN')
        self.marker = marker or os.getenv('TRAVELPAYOUTS_MARKER')
        
        if not self.token or self.token == 'your_token_here':
            raise ValueError("Get Travelpayouts token from: https://www.travelpayouts.com/")
    
    def search_cheap_flights(
        self,
        origin: str,
        destination: str,
        currency: str = 'USD'
    ) -> Optional[Dict]:
        """Find cheapest flights (uses aggregated data)"""
        
        params = {
            'origin': origin,
            'destination': destination,
            'currency': currency,
            'token': self.token
        }
        
        try:
            response = requests.get(
                f'{self.BASE_URL}/prices/latest',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and data['data']:
                # Get cheapest from results
                prices = [d for d in data['data'].values() if isinstance(d, dict)]
                if prices:
                    cheapest = min(prices, key=lambda x: x.get('value', float('inf')))
                    return {
                        'price': cheapest['value'],
                        'currency': currency,
                        'airline': cheapest.get('airline', 'Multiple'),
                        'departure_date': cheapest.get('departure_at', ''),
                        'return_date': cheapest.get('return_at', '')
                    }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Travelpayouts API error: {str(e)}")
            return None
    
    def get_affiliate_link(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None
    ) -> str:
        """Generate affiliate link (earns commission)"""
        
        # Aviasales affiliate link
        base = "https://www.aviasales.com/search"
        params = f"{origin}{destination}{departure_date.replace('-', '')}"
        
        if return_date:
            params += return_date.replace('-', '')
        
        if self.marker:
            return f"{base}/{params}?marker={self.marker}"
        
        return f"{base}/{params}"
    
    def get_calendar_prices(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        currency: str = 'USD'
    ) -> Dict:
        """Get prices for nearby dates (find best deal window)"""
        
        params = {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'currency': currency,
            'token': self.token
        }
        
        try:
            response = requests.get(
                f'{self.BASE_URL}/prices/month-matrix',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Travelpayouts API error: {str(e)}")
            return {}


def test_travelpayouts():
    """Test Travelpayouts API"""
    try:
        client = TravelpayoutsClient()
        print("✅ Travelpayouts configured")
        print("💰 You'll earn commission on bookings!")
        return True
    except ValueError as e:
        print(f"❌ {str(e)}")
        print("\n📝 Quick setup:")
        print("   1. Go to: https://www.travelpayouts.com/")
        print("   2. Sign up (instant approval)")
        print("   3. Get API token + Affiliate Marker")
        print("   4. Update .env:")
        print("      TRAVELPAYOUTS_TOKEN=your_token")
        print("      TRAVELPAYOUTS_MARKER=your_affiliate_id")
        return False

if __name__ == '__main__':
    test_travelpayouts()
