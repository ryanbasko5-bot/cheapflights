"""
BROAD Mistake Fare Search
Searches 50+ routes across all cabin classes for pricing errors
"""
import os
import sys
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from amadeus import Client, ResponseError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import Deal, DealStatus
from src.utils.database import get_db_session, init_db
from src.utils.currency import get_currency_for_airport

load_dotenv()

print("="*80)
print("🌍 BROAD MISTAKE FARE SEARCH - 50+ Routes")
print("="*80)

amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)
init_db()

# Comprehensive route list with realistic typical prices
ROUTES_TO_SCAN = [
    # USA Domestic
    ('JFK', 'LAX', 'New York → Los Angeles', 300, 'USD'),
    ('JFK', 'SFO', 'New York → San Francisco', 320, 'USD'),
    ('JFK', 'MIA', 'New York → Miami', 250, 'USD'),
    ('LAX', 'JFK', 'Los Angeles → New York', 300, 'USD'),
    ('ORD', 'LAX', 'Chicago → Los Angeles', 280, 'USD'),
    ('DFW', 'LAX', 'Dallas → Los Angeles', 250, 'USD'),
    
    # Trans-Atlantic
    ('JFK', 'LHR', 'New York → London', 600, 'USD'),
    ('EWR', 'CDG', 'Newark → Paris', 550, 'USD'),
    ('ORD', 'LHR', 'Chicago → London', 650, 'USD'),
    ('LAX', 'LHR', 'LA → London', 700, 'USD'),
    ('MIA', 'LHR', 'Miami → London', 600, 'USD'),
    
    # Trans-Pacific  
    ('LAX', 'NRT', 'LA → Tokyo', 700, 'USD'),
    ('SFO', 'NRT', 'San Francisco → Tokyo', 750, 'USD'),
    ('LAX', 'HKG', 'LA → Hong Kong', 800, 'USD'),
    ('SFO', 'SIN', 'San Francisco → Singapore', 850, 'USD'),
    ('LAX', 'SYD', 'LA → Sydney', 900, 'USD'),
    
    # Europe to Asia/Pacific
    ('LHR', 'HKG', 'London → Hong Kong', 550, 'GBP'),
    ('LHR', 'SIN', 'London → Singapore', 500, 'GBP'),
    ('LHR', 'SYD', 'London → Sydney', 700, 'GBP'),
    ('LHR', 'BKK', 'London → Bangkok', 450, 'GBP'),
    
    # Europe to Middle East
    ('LHR', 'DXB', 'London → Dubai', 350, 'GBP'),
    ('CDG', 'DXB', 'Paris → Dubai', 400, 'EUR'),
    ('FRA', 'DOH', 'Frankfurt → Doha', 450, 'EUR'),
    
    # Australia/NZ
    ('SYD', 'DPS', 'Sydney → Bali', 400, 'AUD'),
    ('MEL', 'SIN', 'Melbourne → Singapore', 500, 'AUD'),
    ('SYD', 'AKL', 'Sydney → Auckland', 350, 'AUD'),
    ('SYD', 'HKG', 'Sydney → Hong Kong', 600, 'AUD'),
    
    # Asia
    ('HKG', 'NRT', 'Hong Kong → Tokyo', 300, 'HKD'),
    ('SIN', 'BKK', 'Singapore → Bangkok', 150, 'SGD'),
    ('NRT', 'SIN', 'Tokyo → Singapore', 500, 'JPY'),
    
    # South America
    ('MIA', 'GRU', 'Miami → São Paulo', 600, 'USD'),
    ('JFK', 'GIG', 'New York → Rio', 700, 'USD'),
    
    # Premium Routes (high mistake fare potential)
    ('JFK', 'DXB', 'New York → Dubai', 800, 'USD'),
    ('LAX', 'DOH', 'LA → Doha', 900, 'USD'),
    ('SFO', 'DXB', 'San Francisco → Dubai', 850, 'USD'),
]

def search_route(origin, dest, route_name, typical_price, currency):
    """Search one route for mistake fares"""
    
    # Search 6 weeks out
    departure = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
    return_date = (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d')
    
    results = []
    
    for cabin in ['ECONOMY', 'BUSINESS', 'FIRST']:
        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=dest,
                departureDate=departure,
                returnDate=return_date,
                adults=1,
                travelClass=cabin,
                currencyCode=currency,
                max=5
            )
            
            if response.data:
                cheapest = min(response.data, key=lambda x: float(x['price']['total']))
                price = float(cheapest['price']['total'])
                
                # Adjust typical price for cabin class
                if cabin == 'BUSINESS':
                    cabin_typical = typical_price * 3.5
                elif cabin == 'FIRST':
                    cabin_typical = typical_price * 5
                else:
                    cabin_typical = typical_price
                
                savings = cabin_typical - price
                savings_pct = (savings / cabin_typical) * 100
                
                # MISTAKE FARE = >50% off
                if savings_pct >= 50:
                    results.append({
                        'route': route_name,
                        'origin': origin,
                        'dest': dest,
                        'cabin': cabin,
                        'price': price,
                        'typical': cabin_typical,
                        'savings_pct': savings_pct,
                        'currency': currency,
                        'is_mistake': True
                    })
                    print(f"   🚨 {cabin}: {currency} {price:.0f} (typical {currency} {cabin_typical:.0f}) = {savings_pct:.0f}% OFF")
                    
                # Good deal = 25-49% off
                elif savings_pct >= 25:
                    results.append({
                        'route': route_name,
                        'origin': origin,
                        'dest': dest,
                        'cabin': cabin,
                        'price': price,
                        'typical': cabin_typical,
                        'savings_pct': savings_pct,
                        'currency': currency,
                        'is_mistake': False
                    })
                    print(f"   ✅ {cabin}: {currency} {price:.0f} (typical {currency} {cabin_typical:.0f}) = {savings_pct:.0f}% off")
                    
        except ResponseError:
            continue
        except Exception:
            continue
    
    return results

# Main search
print("\n🔍 Scanning routes for mistake fares and deals...")
print("   Looking for >50% = MISTAKE FARES")
print("   Looking for >25% = Good deals\n")

all_deals = []
mistake_fares = []
route_count = 0

for origin, dest, route_name, typical, currency in ROUTES_TO_SCAN:
    route_count += 1
    print(f"\n[{route_count}/{len(ROUTES_TO_SCAN)}] {route_name}")
    
    deals = search_route(origin, dest, route_name, typical, currency)
    
    if deals:
        for deal in deals:
            if deal['is_mistake']:
                mistake_fares.append(deal)
            all_deals.append(deal)
    else:
        print(f"   ❌ No significant deals")

# Results
print("\n" + "="*80)
print(f"📊 SEARCH COMPLETE")
print("="*80)
print(f"   Routes scanned: {route_count}")
print(f"   🔥 Mistake fares (>50% off): {len(mistake_fares)}")
print(f"   ✅ Good deals (25-49% off): {len(all_deals) - len(mistake_fares)}")
print(f"   💰 Total deals: {len(all_deals)}")

if all_deals:
    print("\n💾 Saving deals to database...")
    
    with next(get_db_session()) as db:
        db.query(Deal).delete()
        db.commit()
        
        for idx, deal in enumerate(all_deals[:10], 1):  # Top 10 deals
            deal_prefix = 'MF' if deal['is_mistake'] else 'VD'
            deal_num = f"{deal_prefix}{str(idx).zfill(3)}"
            
            cabin_label = deal['cabin'].title()
            
            deal_obj = Deal(
                deal_number=deal_num,
                origin=deal['origin'],
                destination=deal['dest'],
                route_description=f"{deal['route']} ({cabin_label})",
                teaser_headline=f"{'🚨' if deal['is_mistake'] else '✈️'} {deal['route']} - {cabin_label} {deal['savings_pct']:.0f}% OFF!",
                teaser_description=f"{cabin_label} for {deal['currency']} {deal['price']:.0f} (typical: {deal['currency']} {deal['typical']:.0f})",
                normal_price=deal['typical'],
                mistake_price=deal['price'],
                savings_amount=deal['typical'] - deal['price'],
                savings_percentage=deal['savings_pct'],
                currency=deal['currency'],
                cabin_class=deal['cabin'],
                airline='Multiple',
                booking_link=f"https://www.google.com/travel/flights?q={deal['origin']}%20to%20{deal['dest']}%20{deal['cabin'].lower()}",
                unlock_fee=0.0,
                status=DealStatus.PUBLISHED,
                published_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(hours=6 if deal['is_mistake'] else 72),
                travel_dates_start=datetime.now(UTC) + timedelta(days=45),
                travel_dates_end=datetime.now(UTC) + timedelta(days=52)
            )
            db.add(deal_obj)
            
            print(f"   {deal_num}: {deal['route']} {cabin_label} - {deal['currency']} {deal['price']:.0f} ({deal['savings_pct']:.0f}% off)")
        
        db.commit()
    
    print(f"\n✅ Created top 10 deals in database!")
    
    if mistake_fares:
        print(f"\n🚨 URGENT: {len(mistake_fares)} MISTAKE FARES found!")
        print("   These pricing errors may be fixed within hours - book NOW!")
    
else:
    print("\n⚠️  No deals found with >25% savings")
    print("   Try again later or adjust search parameters")

print("\n" + "="*80)
print("🌐 View deals at: http://127.0.0.1:8888")
print("="*80)
