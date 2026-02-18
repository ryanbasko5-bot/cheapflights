#!/usr/bin/env python3
"""Quick scan of top 10 routes most likely to have mistake fares"""

import os
import sys
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from amadeus import Client, ResponseError

from src.utils.database import get_db_session, init_db
from src.models.database import Deal, DealStatus
from src.utils.currency import get_currency_for_airport

load_dotenv()
init_db()

amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET'),
    hostname='test'
)

# Top 10 routes where mistake fares are most common
# Focus on long-haul where pricing errors are bigger
TOP_ROUTES = [
    ('JFK', 'NRT', 'New York → Tokyo', 450),  # Trans-Pacific
    ('LAX', 'SYD', 'LA → Sydney', 850),  # Long-haul Pacific
    ('LHR', 'SIN', 'London → Singapore', 550),  # Long-haul Asia
    ('SYD', 'DPS', 'Sydney → Bali', 300),  # Popular leisure
    ('JFK', 'LHR', 'New York → London', 400),  # Trans-Atlantic
    ('LAX', 'CDG', 'LA → Paris', 450),  # Trans-Atlantic
    ('SFO', 'HKG', 'San Francisco → Hong Kong', 600),  # Trans-Pacific
    ('LHR', 'DXB', 'London → Dubai', 350),  # Middle East
    ('MIA', 'GRU', 'Miami → São Paulo', 500),  # South America
    ('JFK', 'SYD', 'New York → Sydney', 1200),  # Ultra long-haul
]

def search_route(origin, dest, typical_price, cabin='ECONOMY'):
    """Search one route and check for deals"""
    try:
        # Search 45 days out
        dep_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=dep_date,
            adults=1,
            currencyCode=get_currency_for_airport(origin),
            travelClass=cabin,
            max=5
        )
        
        if not response.data:
            return None
            
        # Get cheapest offer
        cheapest = min(response.data, key=lambda x: float(x['price']['total']))
        price = float(cheapest['price']['total'])
        currency = cheapest['price']['currency']
        
        # Calculate savings
        savings_pct = ((typical_price - price) / typical_price) * 100
        
        return {
            'price': price,
            'currency': currency,
            'typical': typical_price,
            'savings_pct': savings_pct,
            'is_mistake': savings_pct > 50
        }
        
    except ResponseError as e:
        print(f"   ❌ API Error: {e.description}")
        return None

def main():
    print("🔍 QUICK MISTAKE FARE SCAN - Top 10 Routes")
    print("=" * 60)
    
    deals_found = []
    
    for i, (orig, dest, route_name, typical) in enumerate(TOP_ROUTES, 1):
        print(f"\n[{i}/10] {route_name}...")
        
        result = search_route(orig, dest, typical)
        
        if result:
            emoji = "⚡" if result['is_mistake'] else "✅"
            label = "MISTAKE FARE" if result['is_mistake'] else "Good Deal"
            
            print(f"   {emoji} {result['currency']} {result['price']:.0f} (typical {result['typical']}) = {result['savings_pct']:.0f}% off - {label}")
            
            if result['savings_pct'] >= 25:  # Save deals with 25%+ savings
                deals_found.append({
                    'origin': orig,
                    'dest': dest,
                    'route': route_name,
                    'price': result['price'],
                    'typical': result['typical'],
                    'currency': result['currency'],
                    'savings_pct': result['savings_pct'],
                    'is_mistake': result['is_mistake']
                })
    
    # Save top deals to database
    if deals_found:
        print(f"\n\n💾 Saving {len(deals_found)} deals to database...")
        
        with next(get_db_session()) as db:
            # Clear old deals
            db.query(Deal).delete()
            db.commit()
            
            for idx, d in enumerate(deals_found, 1):
                prefix = 'MF' if d['is_mistake'] else 'VD'
                deal_num = f"{prefix}{idx:03d}"
                
                savings_amt = d['typical'] - d['price']
                
                headline = f"{'⚡' if d['is_mistake'] else '✈️'} {d['route']} - Save {d['savings_pct']:.0f}%!"
                desc = f"{'MISTAKE FARE! ' if d['is_mistake'] else ''}{d['currency']} {d['price']:.0f} (typical: {d['currency']} {d['typical']})"
                
                booking_url = f"https://www.google.com/travel/flights?q={d['origin']}%20to%20{d['dest']}"
                
                deal = Deal(
                    deal_number=deal_num,
                    origin=d['origin'],
                    destination=d['dest'],
                    route_description=d['route'],
                    teaser_headline=headline,
                    teaser_description=desc,
                    normal_price=d['typical'],
                    mistake_price=d['price'],
                    savings_amount=savings_amt,
                    savings_percentage=d['savings_pct'],
                    currency=d['currency'],
                    cabin_class='ECONOMY',
                    airline='Multiple',
                    booking_link=booking_url,
                    unlock_fee=0.0,
                    status=DealStatus.PUBLISHED,
                    published_at=datetime.now(UTC),
                    expires_at=datetime.now(UTC) + timedelta(hours=6 if d['is_mistake'] else 72),
                    travel_dates_start=datetime.now(UTC) + timedelta(days=45),
                    travel_dates_end=datetime.now(UTC) + timedelta(days=52)
                )
                db.add(deal)
                print(f"   ✅ {deal_num}: {d['route']} - {d['currency']} {d['price']:.0f} ({d['savings_pct']:.0f}% off)")
            
            db.commit()
        
        print(f"\n🎯 SUCCESS! {len(deals_found)} deals saved")
        print("   View at: http://localhost:8888")
    else:
        print("\n⚠️  No deals found with 25%+ savings")

if __name__ == '__main__':
    main()
