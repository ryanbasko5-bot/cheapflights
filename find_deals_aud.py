#!/usr/bin/env python3
"""
LOCATION-AWARE DEAL FINDER
Shows deals in user's local currency so they match what they see on Google Flights
"""

from datetime import datetime, timedelta, UTC
from typing import List, Dict
from src.integrations.duffel_client import DuffelClient
from src.integrations.serpapi_client import SerpAPIClient
from src.utils.database import get_db_session, init_db
from src.models.database import Deal, DealStatus

init_db()

# For Australian users - show in AUD
USER_CURRENCY = 'AUD'  # Change based on user location

# Popular routes FROM Australia
AUSTRALIA_ROUTES = [
    ('SYD', 'DPS', 'Sydney → Bali'),
    ('MEL', 'SIN', 'Melbourne → Singapore'),
    ('SYD', 'LAX', 'Sydney → Los Angeles'),
    ('BNE', 'NRT', 'Brisbane → Tokyo'),
    ('PER', 'LHR', 'Perth → London'),
    ('SYD', 'AKL', 'Sydney → Auckland'),
]

def find_deals_for_location():
    """Find deals in user's currency"""
    print(f"🌏 LOCATION-AWARE DEAL FINDER")
    print(f"=" * 60)
    print(f"Finding deals in {USER_CURRENCY} (Australian dollars)")
    print("")
    
    try:
        serp = SerpAPIClient()
        print("✅ Using Google Flights data (SerpAPI)")
    except Exception as e:
        print(f"❌ SerpAPI not available: {str(e)}")
        return
    
    deals = []
    
    for origin, dest, route_name in AUSTRALIA_ROUTES:
        print(f"\n📊 {route_name}...")
        
        dep_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        ret_date = (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d')
        
        # Get Google Flights price in user's currency
        google_price = serp.search_google_flights(
            origin, dest, dep_date, ret_date, USER_CURRENCY
        )
        
        if not google_price:
            print("   ⚠️  No prices found")
            continue
        
        current_price = google_price['price']
        print(f"   💰 Google Flights: {USER_CURRENCY} {current_price:.0f}")
        
        # Sample multiple dates for "typical" price
        typical_prices = []
        for days_ahead in [30, 60, 90]:
            dep = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            ret = (datetime.now() + timedelta(days=days_ahead + 7)).strftime('%Y-%m-%d')
            
            result = serp.search_google_flights(origin, dest, dep, ret, USER_CURRENCY)
            if result:
                typical_prices.append(result['price'])
        
        if len(typical_prices) >= 2:
            typical_prices.sort()
            typical_price = typical_prices[len(typical_prices) // 2]
            
            print(f"   📊 Typical price: {USER_CURRENCY} {typical_price:.0f}")
            
            savings_pct = ((typical_price - current_price) / typical_price) * 100
            
            if savings_pct >= 15:  # 15%+ is a good deal from Australia
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
                    'currency': USER_CURRENCY,
                    'booking_link': f"https://www.google.com/travel/flights?q={origin}%20to%20{dest}",
                    'is_mistake': savings_pct >= 50
                })
            else:
                print(f"   ➖ Only {savings_pct:.0f}% off")
    
    if not deals:
        print("\n⚠️  No deals found with 15%+ savings")
        return
    
    # Save to database
    print(f"\n💾 Saving {len(deals)} deals in {USER_CURRENCY}...")
    
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
        
        db.commit()
    
    print(f"\n🎯 SUCCESS! {len(deals)} deals in {USER_CURRENCY}")
    print(f"   ✅ Prices match what you see on Google Flights!")
    print(f"   ✅ No currency conversion surprises")
    print(f"\n   View at: http://localhost:8888")

if __name__ == '__main__':
    find_deals_for_location()
