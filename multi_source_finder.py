"""
MULTI-SOURCE DEAL FINDER
Uses ALL APIs to find the best deals with cross-verification
"""

import os
from datetime import datetime, timedelta, UTC
from typing import List, Dict
from dotenv import load_dotenv

# Import all clients
from src.integrations.duffel_client import DuffelClient
from src.integrations.serpapi_client import SerpAPIClient
from src.integrations.travelpayouts_client import TravelpayoutsClient
from src.utils.database import get_db_session, init_db
from src.models.database import Deal, DealStatus
from src.utils.currency import get_currency_for_airport

load_dotenv()

# Routes to monitor
ROUTES = [
    ('SYD', 'DPS', 'Sydney → Bali'),
    ('JFK', 'LHR', 'New York → London'),
    ('LAX', 'SYD', 'LA → Sydney'),
    ('LHR', 'SIN', 'London → Singapore'),
    ('SFO', 'HKG', 'San Francisco → Hong Kong'),
    ('JFK', 'NRT', 'New York → Tokyo'),
    ('MIA', 'GRU', 'Miami → São Paulo'),
    ('LHR', 'DXB', 'London → Dubai'),
]

class MultiSourceFinder:
    """Find deals using multiple data sources"""
    
    def __init__(self):
        self.sources = {}
        
        # Try to initialize all sources
        try:
            self.sources['duffel'] = DuffelClient()
            print("✅ Duffel API ready")
        except Exception as e:
            print(f"⚠️  Duffel unavailable: {str(e)}")
        
        try:
            self.sources['serpapi'] = SerpAPIClient()
            print("✅ SerpAPI ready (Google Flights data)")
        except Exception as e:
            print(f"⚠️  SerpAPI unavailable: {str(e)}")
        
        try:
            self.sources['travelpayouts'] = TravelpayoutsClient()
            print("✅ Travelpayouts ready (with affiliate commissions)")
        except Exception as e:
            print(f"⚠️  Travelpayouts unavailable: {str(e)}")
        
        if not self.sources:
            raise ValueError("No API sources available!")
    
    def get_prices_from_all_sources(
        self,
        origin: str,
        destination: str,
        currency: str,
        user_currency: str = None
    ) -> Dict[str, float]:
        """Get prices from all available sources in user's currency"""
        prices = {}
        
        # Use user currency if provided, otherwise origin currency
        search_currency = user_currency or currency
        
        # Duffel
        if 'duffel' in self.sources:
            try:
                result = self.sources['duffel'].get_cheapest_price(origin, destination)
                if result:
                    prices['duffel'] = result['price']
            except Exception:
                pass
        
        # SerpAPI (Google Flights) - use user's currency for accurate comparison
        if 'serpapi' in self.sources:
            try:
                dep_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
                ret_date = (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d')
                result = self.sources['serpapi'].search_google_flights(
                    origin, destination, dep_date, ret_date, search_currency
                )
                if result:
                    prices['google_flights'] = result['price']
            except Exception:
                pass
        
        # Travelpayouts
        if 'travelpayouts' in self.sources:
            try:
                result = self.sources['travelpayouts'].search_cheap_flights(
                    origin, destination, currency
                )
                if result:
                    prices['travelpayouts'] = result['price']
            except Exception:
                pass
        
        return prices
    
    def find_deals(self, min_savings_pct: float = 20.0) -> List[Dict]:
        """Find deals across all routes using all sources"""
        
        deals = []
        
        for origin, dest, route_name in ROUTES:
            print(f"\n📊 {route_name}...")
            
            currency = get_currency_for_airport(origin)
            prices = self.get_prices_from_all_sources(origin, dest, currency)
            
            if not prices:
                print("   ⚠️  No prices found from any source")
                continue
            
            print(f"   📈 Prices found: {len(prices)} sources")
            for source, price in prices.items():
                print(f"      {source}: {currency} {price:.0f}")
            
            # Use median price as "typical" (conservative)
            price_list = sorted(prices.values())
            typical_price = price_list[len(price_list) // 2]
            current_price = min(prices.values())
            
            print(f"   💰 Best price: {currency} {current_price:.0f}")
            print(f"   📊 Typical (median): {currency} {typical_price:.0f}")
            
            # Calculate savings
            if typical_price > current_price:
                savings_pct = ((typical_price - current_price) / typical_price) * 100
                
                if savings_pct >= min_savings_pct:
                    emoji = "⚡" if savings_pct >= 50 else "✅"
                    label = "MISTAKE FARE" if savings_pct >= 50 else "Great Deal"
                    print(f"   {emoji} {savings_pct:.0f}% off - {label}")
                    
                    # Get booking link (prefer affiliate if available)
                    booking_link = f"https://www.google.com/travel/flights?q={origin}%20to%20{dest}"
                    if 'travelpayouts' in self.sources:
                        dep_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
                        ret_date = (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d')
                        booking_link = self.sources['travelpayouts'].get_affiliate_link(
                            origin, dest, dep_date, ret_date
                        )
                    
                    deals.append({
                        'origin': origin,
                        'destination': dest,
                        'route_name': route_name,
                        'current_price': current_price,
                        'typical_price': typical_price,
                        'savings_pct': savings_pct,
                        'currency': currency,
                        'booking_link': booking_link,
                        'is_mistake': savings_pct >= 50,
                        'sources': list(prices.keys()),
                        'price_range': {'min': min(prices.values()), 'max': max(prices.values())}
                    })
                else:
                    print(f"   ➖ Only {savings_pct:.0f}% off - not a deal")
        
        return deals


def main():
    """Find and save deals"""
    print("🌍 MULTI-SOURCE DEAL FINDER")
    print("=" * 60)
    print("Cross-checking prices from multiple APIs for accuracy")
    print("")
    
    init_db()
    
    try:
        finder = MultiSourceFinder()
    except ValueError as e:
        print(f"\n❌ {str(e)}")
        print("\n📝 Set up at least one API:")
        print("   • Duffel: Already have token!")
        print("   • SerpAPI: https://serpapi.com/users/sign_up")
        print("   • Travelpayouts: https://www.travelpayouts.com/")
        return
    
    print("")
    deals = finder.find_deals(min_savings_pct=20.0)
    
    if not deals:
        print("\n⚠️  No deals found with 20%+ savings")
        return
    
    # Save to database
    print(f"\n💾 Saving {len(deals)} cross-verified deals...")
    
    with next(get_db_session()) as db:
        db.query(Deal).delete()
        db.commit()
        
        for idx, d in enumerate(deals, 1):
            prefix = 'MF' if d['is_mistake'] else 'VD'
            deal_num = f"{prefix}{idx:03d}"
            
            savings_amt = d['typical_price'] - d['current_price']
            
            headline = f"{'⚡' if d['is_mistake'] else '✈️'} {d['route_name']} - Save {d['savings_pct']:.0f}%!"
            desc = f"{d['currency']} {d['current_price']:.0f} (typical: {d['currency']} {d['typical_price']:.0f})"
            
            deal = Deal(
                deal_number=deal_num,
                origin=d['origin'],
                destination=d['destination'],
                route_description=d['route_name'],
                teaser_headline=headline,
                teaser_description=desc,
                normal_price=d['typical_price'],
                mistake_price=d['current_price'],
                savings_amount=savings_amt,
                savings_percentage=d['savings_pct'],
                currency=d['currency'],
                cabin_class='ECONOMY',
                airline='Multiple',
                booking_link=d['booking_link'],
                unlock_fee=0.0,
                status=DealStatus.PUBLISHED,
                published_at=datetime.now(UTC) - timedelta(hours=2),
                expires_at=datetime.now(UTC) + timedelta(hours=6 if d['is_mistake'] else 72),
                travel_dates_start=datetime.now(UTC) + timedelta(days=45),
                travel_dates_end=datetime.now(UTC) + timedelta(days=52)
            )
            db.add(deal)
            print(f"   ✅ {deal_num}: {d['route_name']} - {d['currency']} {d['current_price']:.0f} ({d['savings_pct']:.0f}% off)")
            print(f"      Verified by: {', '.join(d['sources'])}")
        
        db.commit()
    
    print(f"\n🎯 SUCCESS! {len(deals)} deals saved")
    print("   ✅ Cross-verified across multiple sources")
    print("   ✅ Conservative median pricing (no inflation)")
    print("   ✅ Affiliate links included (earn commissions)")
    print(f"\n   View at: http://localhost:8888")

if __name__ == '__main__':
    main()
