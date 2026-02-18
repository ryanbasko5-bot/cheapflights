"""
Scan for Real Flight Deals using Amadeus API
Creates deals in database with proper booking links
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import Deal, DealStatus
from src.utils.database import get_db_session, init_db
from src.utils.currency import get_currency_for_airport, format_price

load_dotenv()

print("="*80)
print("🔍 SCANNING FOR REAL FLIGHT DEALS")
print("="*80)

# Initialize Amadeus
amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)

print("\n✅ Connected to Amadeus Test API (real flight data)")
print(f"✅ Database initialized\n")

# Initialize database
init_db()

# Popular routes to scan (origin, destination, typical normal price)
ROUTES_TO_SCAN = [
    ('JFK', 'LAX', 'New York → Los Angeles', 300, 'USD'),
    ('LHR', 'DXB', 'London → Dubai', 450, 'GBP'),
    ('SYD', 'BKK', 'Sydney → Bangkok', 600, 'AUD'),
    ('LAX', 'NRT', 'Los Angeles → Tokyo', 800, 'USD'),
    ('SFO', 'LHR', 'San Francisco → London', 900, 'USD'),
    ('MIA', 'CDG', 'Miami → Paris', 700, 'USD'),
    ('DFW', 'BCN', 'Dallas → Barcelona', 750, 'USD'),
    ('ORD', 'FCO', 'Chicago → Rome', 800, 'USD'),
]

def generate_booking_url(origin, destination, departure_date, return_date=None):
    """Generate Google Flights search URL"""
    base_url = "https://www.google.com/travel/flights"
    
    if return_date:
        # Round trip
        url = f"{base_url}?q=flights%20from%20{origin}%20to%20{destination}%20on%20{departure_date}%20returning%20{return_date}"
    else:
        # One way
        url = f"{base_url}?q=flights%20from%20{origin}%20to%20{destination}%20on%20{departure_date}"
    
    return url

def scan_route(origin, destination, route_name, normal_price, currency):
    """Scan a route for deals"""
    print(f"\n📍 Scanning: {route_name}")
    print(f"   Expected normal price: {currency} {normal_price}")
    
    # Search dates (1-2 months out)
    departure_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
    return_date = (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d')
    
    try:
        # Search for flights
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            returnDate=return_date,
            adults=1,
            currencyCode=currency,
            max=10
        )
        
        if not response.data:
            print(f"   ❌ No flights found")
            return None
        
        # Get cheapest offer
        cheapest = min(response.data, key=lambda x: float(x['price']['total']))
        price = float(cheapest['price']['total'])
        
        # Calculate savings
        savings_amount = normal_price - price
        savings_percentage = (savings_amount / normal_price) * 100
        
        print(f"   💰 Found: {currency} {price:.2f}")
        print(f"   💵 Normal: {currency} {normal_price:.2f}")
        print(f"   🎯 Savings: {currency} {savings_amount:.2f} ({savings_percentage:.1f}%)")
        
        # Only create deal if there's at least 20% savings
        if savings_percentage >= 20:
            print(f"   ✅ DEAL FOUND! Saving {savings_percentage:.0f}%")
            
            # Get flight details
            itinerary = cheapest['itineraries'][0]
            segments = itinerary['segments']
            
            # Cabin class
            cabin_class = segments[0].get('cabin', 'ECONOMY')
            
            # Airline
            carrier_code = segments[0]['carrierCode']
            
            # Generate booking URL
            booking_url = generate_booking_url(origin, destination, departure_date, return_date)
            
            # Create deal object
            deal_data = {
                'origin': origin,
                'destination': destination,
                'route_name': route_name,
                'normal_price': normal_price,
                'mistake_price': price,
                'savings_amount': savings_amount,
                'savings_percentage': savings_percentage,
                'currency': currency,
                'cabin_class': cabin_class,
                'carrier_code': carrier_code,
                'departure_date': departure_date,
                'return_date': return_date,
                'booking_url': booking_url
            }
            
            return deal_data
        else:
            print(f"   ⚠️  Only {savings_percentage:.0f}% savings - not a great deal")
            return None
            
    except ResponseError as error:
        print(f"   ❌ Error: {error}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return None

def create_deal_in_db(deal_data, db: Session):
    """Create deal in database"""
    
    # Generate deal number
    existing_count = db.query(Deal).count()
    deal_number = f"FG{str(existing_count + 1).zfill(4)}"
    
    # Create teaser
    savings_pct = int(deal_data['savings_percentage'])
    teaser_headline = f"🔥 {deal_data['route_name']} - Save {savings_pct}%!"
    teaser_description = f"Fly {deal_data['cabin_class'].lower()} class for just {deal_data['currency']} {deal_data['mistake_price']:.0f} (normally {deal_data['currency']} {deal_data['normal_price']:.0f})"
    
    # Create deal
    deal = Deal(
        deal_number=deal_number,
        origin=deal_data['origin'],
        destination=deal_data['destination'],
        route_description=deal_data['route_name'],
        teaser_headline=teaser_headline,
        teaser_description=teaser_description,
        normal_price=deal_data['normal_price'],
        mistake_price=deal_data['mistake_price'],
        savings_amount=deal_data['savings_amount'],
        savings_percentage=deal_data['savings_percentage'],
        currency=deal_data['currency'],
        cabin_class=deal_data['cabin_class'],
        booking_url=deal_data['booking_url'],
        airline=deal_data.get('carrier_code', 'Multiple'),
        unlock_fee=0.0,  # Free for premium members
        status=DealStatus.ACTIVE,
        published_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=2),
        travel_dates_start=datetime.strptime(deal_data['departure_date'], '%Y-%m-%d'),
        travel_dates_end=datetime.strptime(deal_data['return_date'], '%Y-%m-%d') if deal_data.get('return_date') else None,
    )
    
    db.add(deal)
    db.commit()
    
    print(f"   💾 Saved to database as {deal_number}")
    return deal

# Main scanning loop
print("\n" + "="*80)
print("Starting route scans...")
print("="*80)

deals_found = []

for origin, destination, route_name, normal_price, currency in ROUTES_TO_SCAN:
    deal_data = scan_route(origin, destination, route_name, normal_price, currency)
    
    if deal_data:
        deals_found.append(deal_data)

# Save to database
print("\n" + "="*80)
print(f"📊 SCAN COMPLETE - Found {len(deals_found)} deals")
print("="*80)

if deals_found:
    print("\n💾 Saving deals to database...")
    
    with next(get_db_session()) as db:
        for deal_data in deals_found:
            create_deal_in_db(deal_data, db)
    
    print(f"\n✅ SUCCESS! {len(deals_found)} real deals added to database")
    print("\n🌐 You can now:")
    print("   1. View them on your website at http://127.0.0.1:8888")
    print("   2. Sign in as premium@test.com to see all deals immediately")
    print("   3. Click the booking links to see real flight prices on Google Flights")
else:
    print("\n⚠️  No deals found meeting the 20% savings threshold")
    print("   This is normal - mistake fares are rare!")
    print("   Try running this script multiple times or adjusting the normal price estimates")

print("\n" + "="*80)
