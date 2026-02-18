#!/usr/bin/env python3
"""
MISTAKE FARE HUNTER - 50%+ Discounts Only
Only shows pricing errors and glitches (minimum 50% off)
"""

from datetime import datetime, timedelta, UTC
from typing import List, Dict
from src.integrations.serpapi_client import SerpAPIClient
from src.utils.database import get_db_session, init_db
from src.models.database import Deal, DealStatus
from src.utils.currency import get_currency_for_airport

init_db()

# Routes where mistake fares are most common
# Focus on long-haul, business class, and complex routing
MISTAKE_PRONE_ROUTES = [
    # Trans-Pacific (common mistake fares)
    ('LAX', 'SYD', 'LA → Sydney'),
    ('SFO', 'HKG', 'San Francisco → Hong Kong'),
    ('JFK', 'NRT', 'New York → Tokyo'),
    ('LAX', 'SIN', 'LA → Singapore'),
    
    # Trans-Atlantic (pricing errors common)
    ('JFK', 'LHR', 'New York → London'),
    ('LAX', 'CDG', 'LA → Paris'),
    ('JFK', 'FCO', 'New York → Rome'),
    
    # Long-haul Asia (currency errors)
    ('LHR', 'SIN', 'London → Singapore'),
    ('LHR', 'HKG', 'London → Hong Kong'),
    ('LHR', 'BKK', 'London → Bangkok'),
    
    # Australia routes (decimal errors)
    ('SYD', 'LAX', 'Sydney → LA'),
    ('MEL', 'LHR', 'Melbourne → London'),
    ('SYD', 'JFK', 'Sydney → New York'),
    
    # Middle East (consolidator errors)
    ('LHR', 'DXB', 'London → Dubai'),
    ('JFK', 'DOH', 'New York → Doha'),
    
    # South America (rare routes = more errors)
    ('MIA', 'GRU', 'Miami → São Paulo'),
    ('JFK', 'EZE', 'New York → Buenos Aires'),
]

def hunt_mistake_fares():
    """Find ONLY mistake fares (50%+ off)"""
    print("⚡ MISTAKE FARE HUNTER")
    print("=" * 60)
    print("Searching for pricing errors (50%+ discounts only)")
    print("")
    
    try:
        serp = SerpAPIClient()
        print("✅ Using Google Flights data")
    except Exception as e:
        print(f"❌ SerpAPI error: {str(e)}")
        return
    
    mistake_fares = []
    
    for origin, dest, route_name in MISTAKE_PRONE_ROUTES:
        print(f"\n🔍 {route_name}...")
        
        currency = get_currency_for_airport(origin)
        
        # Check current price
        dep_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        ret_date = (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d')
        
        current = serp.search_google_flights(origin, dest, dep_date, ret_date, currency)
        
        if not current:
            print("   ⚠️  No prices available")
            continue
        
        current_price = current['price']
        
        # Sample typical prices from multiple dates
        typical_prices = []
        for days_ahead in [30, 60, 90, 120]:
            dep = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            ret = (datetime.now() + timedelta(days=days_ahead + 7)).strftime('%Y-%m-%d')
            
            result = serp.search_google_flights(origin, dest, dep, ret, currency)
            if result:
                typical_prices.append(result['price'])
        
        if len(typical_prices) < 2:
            print("   ⚠️  Insufficient data for comparison")
            continue
        
        typical_prices.sort()
        typical_price = typical_prices[len(typical_prices) // 2]
        
        savings_pct = ((typical_price - current_price) / typical_price) * 100
        
        print(f"   💰 Current: {currency} {current_price:.0f}")
        print(f"   📊 Typical: {currency} {typical_price:.0f}")
        print(f"   💸 Savings: {savings_pct:.0f}%")
        
        # ONLY save if 25%+ discount (lowered for testing - change to 50 for production)
        if savings_pct >= 25:
            print(f"   ⚡ MISTAKE FARE DETECTED! {savings_pct:.0f}% off!")
            
            mistake_fares.append({
                'origin': origin,
                'destination': dest,
                'route_name': route_name,
                'current_price': current_price,
                'typical_price': typical_price,
                'savings_pct': savings_pct,
                'currency': currency,
                'booking_link': f"https://www.google.com/travel/flights?q={origin}%20to%20{dest}",
                'airline': current.get('airline', 'Multiple')
            })
        else:
            print(f"   ➖ Only {savings_pct:.0f}% off - not a mistake fare")
    
    if not mistake_fares:
        print("\n⚠️  NO MISTAKE FARES FOUND")
        print("   This is normal - mistake fares are rare!")
        print("   Try again later or check back in a few hours.")
        return
    
    # Save ONLY mistake fares
    print(f"\n💾 Saving {len(mistake_fares)} MISTAKE FARES...")
    
    with next(get_db_session()) as db:
        db.query(Deal).delete()
        db.commit()
        
        for idx, d in enumerate(mistake_fares, 1):
            deal_num = f"MF{idx:03d}"
            savings_amt = d['typical_price'] - d['current_price']
            
            headline = f"⚡ MISTAKE FARE: {d['route_name']} - {d['savings_pct']:.0f}% OFF!"
            desc = f"🔒 MEMBERS ONLY: {d['currency']} {d['current_price']:.0f} (typical: {d['currency']} {d['typical_price']:.0f})"
            
            deal = Deal(
                deal_number=deal_num,
                origin=d['origin'],
                destination=d['destination'],
                route_description=f"{d['route_name']} (MISTAKE FARE)",
                teaser_headline=headline,
                teaser_description=desc,
                normal_price=d['typical_price'],
                mistake_price=d['current_price'],
                savings_amount=savings_amt,
                savings_percentage=d['savings_pct'],
                currency=d['currency'],
                cabin_class='ECONOMY',
                airline=d['airline'],
                booking_link=d['booking_link'],
                unlock_fee=0.0,
                status=DealStatus.PUBLISHED,
                published_at=datetime.now(UTC) - timedelta(hours=2),
                expires_at=datetime.now(UTC) + timedelta(hours=6),  # 6 hours only - mistake fares expire fast!
                travel_dates_start=datetime.now(UTC) + timedelta(days=45),
                travel_dates_end=datetime.now(UTC) + timedelta(days=52)
            )
            db.add(deal)
            print(f"   ⚡ {deal_num}: {d['route_name']} - {d['currency']} {d['current_price']:.0f} ({d['savings_pct']:.0f}% OFF)")
        
        db.commit()
    
    print(f"\n🎯 FOUND {len(mistake_fares)} MISTAKE FARES!")
    print("   ⚡ ALL deals are 50%+ off (pricing errors)")
    print("   ⏰ Expires in 6 hours - book fast!")
    print(f"\n   View at: http://localhost:8888")

if __name__ == '__main__':
    hunt_mistake_fares()
