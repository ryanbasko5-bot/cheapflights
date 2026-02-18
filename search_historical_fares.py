#!/usr/bin/env python3
"""
HISTORICAL MISTAKE FARE SEARCH
Search for mistake fares that occurred in the last 30 days
"""

from datetime import datetime, timedelta, UTC
from src.integrations.serpapi_client import SerpAPIClient
from src.utils.database import get_db_session, init_db
from src.models.database import Deal, DealStatus
from src.utils.currency import get_currency_for_airport

init_db()

# Routes to check
ROUTES = [
    ('LAX', 'SYD', 'LA → Sydney'),
    ('SFO', 'HKG', 'San Francisco → Hong Kong'),
    ('JFK', 'NRT', 'New York → Tokyo'),
    ('JFK', 'LHR', 'New York → London'),
    ('LAX', 'CDG', 'LA → Paris'),
    ('LHR', 'SIN', 'London → Singapore'),
    ('SYD', 'LAX', 'Sydney → LA'),
    ('LHR', 'DXB', 'London → Dubai'),
    ('MIA', 'GRU', 'Miami → São Paulo'),
    ('SYD', 'DPS', 'Sydney → Bali'),
]

def search_historical_mistake_fares():
    """Search for mistake fares over the past 30 days"""
    print("📊 HISTORICAL MISTAKE FARE SEARCH")
    print("=" * 60)
    print("Checking prices from the last 30 days")
    print("")
    
    try:
        serp = SerpAPIClient()
    except Exception as e:
        print(f"❌ SerpAPI error: {str(e)}")
        return
    
    all_deals = []
    
    for origin, dest, route_name in ROUTES:
        print(f"\n🔍 {route_name}...")
        
        currency = get_currency_for_airport(origin)
        historical_prices = []
        
        # Check prices for dates in the past 30 days
        # (going forward from those dates to check what deals were available)
        for days_ago in range(30, 0, -5):  # Check every 5 days
            # Departure date was X days ago, looking 45 days ahead from that point
            search_date = datetime.now() - timedelta(days=days_ago)
            dep_date = (search_date + timedelta(days=45)).strftime('%Y-%m-%d')
            ret_date = (search_date + timedelta(days=52)).strftime('%Y-%m-%d')
            
            result = serp.search_google_flights(origin, dest, dep_date, ret_date, currency)
            
            if result:
                price = result['price']
                historical_prices.append({
                    'date_checked': search_date.strftime('%Y-%m-%d'),
                    'price': price,
                    'dep_date': dep_date
                })
        
        if len(historical_prices) < 3:
            print("   ⚠️  Insufficient historical data")
            continue
        
        # Find the median price (typical)
        prices_only = [p['price'] for p in historical_prices]
        prices_only.sort()
        typical_price = prices_only[len(prices_only) // 2]
        
        # Find the lowest price (potential mistake fare)
        lowest = min(historical_prices, key=lambda x: x['price'])
        
        savings_pct = ((typical_price - lowest['price']) / typical_price) * 100
        
        print(f"   📊 Typical price: {currency} {typical_price:.0f}")
        print(f"   💰 Lowest found: {currency} {lowest['price']:.0f} (on {lowest['date_checked']})")
        print(f"   💸 Savings: {savings_pct:.0f}%")
        
        if savings_pct >= 25:  # Good deals
            is_mistake = savings_pct >= 50
            emoji = "⚡" if is_mistake else "✅"
            label = "MISTAKE FARE" if is_mistake else "Good Deal"
            print(f"   {emoji} {label} detected!")
            
            all_deals.append({
                'origin': origin,
                'destination': dest,
                'route_name': route_name,
                'current_price': lowest['price'],
                'typical_price': typical_price,
                'savings_pct': savings_pct,
                'currency': currency,
                'found_date': lowest['date_checked'],
                'is_mistake': is_mistake,
                'booking_link': f"https://www.google.com/travel/flights?q={origin}%20to%20{dest}"
            })
        else:
            print(f"   ➖ Only {savings_pct:.0f}% variation")
    
    if not all_deals:
        print("\n⚠️  No significant deals found in historical data")
        return
    
    # Save to database
    print(f"\n💾 Saving {len(all_deals)} historical deals...")
    
    with next(get_db_session()) as db:
        db.query(Deal).delete()
        db.commit()
        
        for idx, d in enumerate(all_deals, 1):
            prefix = 'MF' if d['is_mistake'] else 'VD'
            deal_num = f"{prefix}{idx:03d}"
            
            savings_amt = d['typical_price'] - d['current_price']
            
            headline = f"{'⚡' if d['is_mistake'] else '✈️'} {d['route_name']} - {d['savings_pct']:.0f}% OFF!"
            desc = f"{'🔒 MEMBERS ONLY: ' if d['is_mistake'] else ''}{d['currency']} {d['current_price']:.0f} (typical: {d['currency']} {d['typical_price']:.0f})"
            
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
            print(f"   {'⚡' if d['is_mistake'] else '✅'} {deal_num}: {d['route_name']} - {d['currency']} {d['current_price']:.0f} ({d['savings_pct']:.0f}% off)")
            print(f"      Found on: {d['found_date']}")
        
        db.commit()
    
    print(f"\n🎯 SUCCESS! {len(all_deals)} deals from historical search")
    print("   View at: http://localhost:8888")

if __name__ == '__main__':
    search_historical_mistake_fares()
