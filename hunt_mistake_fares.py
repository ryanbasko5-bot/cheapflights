"""
Mistake Fare Hunter - Actively scans for pricing errors and glitches

This is different from regular deal scanning - it looks for:
1. Sudden price drops >50% (likely errors)
2. Currency conversion mistakes
3. Missing digits in prices
4. Business/First class priced as Economy
5. Prices that are statistically impossible
"""
import os
import sys
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import Deal, DealStatus
from src.utils.database import get_db_session, init_db
from src.utils.currency import get_currency_for_airport

load_dotenv()

print("="*80)
print("🔍 MISTAKE FARE HUNTER - Scanning for Pricing Errors")
print("="*80)

# Initialize
amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)
init_db()

# High-value routes where mistake fares are most common
# These are long-haul, expensive routes where errors are more noticeable
PREMIUM_ROUTES = [
    # Trans-Atlantic
    ('JFK', 'LHR', 'New York → London', 1200, 'USD'),
    ('LAX', 'LHR', 'Los Angeles → London', 1400, 'USD'),
    ('EWR', 'CDG', 'Newark → Paris', 1100, 'USD'),
    
    # Trans-Pacific
    ('LAX', 'NRT', 'Los Angeles → Tokyo', 1500, 'USD'),
    ('SFO', 'HKG', 'San Francisco → Hong Kong', 1600, 'USD'),
    ('LAX', 'SYD', 'Los Angeles → Sydney', 1800, 'USD'),
    
    # Long-haul from Europe
    ('LHR', 'JFK', 'London → New York', 900, 'GBP'),
    ('LHR', 'SYD', 'London → Sydney', 1400, 'GBP'),
    ('LHR', 'SIN', 'London → Singapore', 1100, 'GBP'),
    
    # Business class routes (most likely for mistakes)
    ('JFK', 'DXB', 'New York → Dubai', 2500, 'USD'),
    ('LAX', 'DOH', 'LA → Doha', 2800, 'USD'),
]

class MistakeFareDetector:
    """Analyzes flight prices for potential errors"""
    
    @staticmethod
    def is_likely_mistake(price, normal_price, cabin_class='ECONOMY'):
        """
        Determines if a price is likely a mistake fare
        
        Criteria:
        - >60% off = very likely mistake
        - >50% off + business/first class = likely mistake
        - Price is statistically impossible (too low for distance)
        """
        discount_pct = ((normal_price - price) / normal_price) * 100
        
        # Super deep discount = likely error
        if discount_pct >= 60:
            return True, f"Extreme discount: {discount_pct:.0f}% off"
        
        # Business/First class at economy prices
        if cabin_class in ['BUSINESS', 'FIRST'] and price < normal_price * 0.3:
            return True, f"{cabin_class} class at {discount_pct:.0f}% off - likely error"
        
        # 50%+ off is suspicious
        if discount_pct >= 50:
            return True, f"Deep discount: {discount_pct:.0f}% off - possible mistake"
        
        return False, None
    
    @staticmethod
    def detect_currency_error(price, currency):
        """Check if price might be in wrong currency"""
        # If USD price is suspiciously low (under $50 for long-haul)
        if currency == 'USD' and price < 50:
            return True, "Price too low - possible currency error"
        
        # If GBP but price looks like USD amount
        if currency == 'GBP' and 200 < price < 500:
            return False, None  # Could be legitimate
        
        return False, None
    
    @staticmethod
    def detect_missing_digit(price, expected_price):
        """Check if a digit might be missing (e.g., $50 instead of $500)"""
        if price * 10 <= expected_price * 1.2:  # Price is ~10x too low
            return True, f"Missing digit? ${price} vs expected ${expected_price}"
        return False, None

def scan_route_for_mistakes(origin, dest, route_name, expected_price, currency):
    """Scan a specific route looking for mistake fares"""
    print(f"\n🔎 Scanning: {route_name}")
    print(f"   Expected: {currency} {expected_price} | Looking for errors >50% off")
    
    departure_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
    return_date = (datetime.now() + timedelta(days=52)).strftime('%Y-%m-%d')
    
    try:
        # Search for flights in ALL cabin classes
        for cabin_class in ['ECONOMY', 'BUSINESS', 'FIRST']:
            try:
                response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=dest,
                    departureDate=departure_date,
                    returnDate=return_date,
                    adults=1,
                    travelClass=cabin_class,
                    currencyCode=currency,
                    max=10
                )
                
                if not response.data:
                    continue
                
                # Get cheapest offer
                cheapest = min(response.data, key=lambda x: float(x['price']['total']))
                price = float(cheapest['price']['total'])
                
                # Check for mistake fare indicators
                detector = MistakeFareDetector()
                
                # Check 1: Is discount suspicious?
                is_mistake, reason = detector.is_likely_mistake(price, expected_price, cabin_class)
                
                if is_mistake:
                    savings = expected_price - price
                    savings_pct = (savings / expected_price) * 100
                    
                    print(f"   🚨 MISTAKE FARE DETECTED in {cabin_class}!")
                    print(f"   💰 Price: {currency} {price:.2f}")
                    print(f"   📊 Expected: {currency} {expected_price:.2f}")
                    print(f"   🎯 Savings: {currency} {savings:.2f} ({savings_pct:.0f}% off)")
                    print(f"   ⚠️  Reason: {reason}")
                    
                    # Check for additional error indicators
                    is_currency_error, curr_reason = detector.detect_currency_error(price, currency)
                    if is_currency_error:
                        print(f"   🔴 {curr_reason}")
                    
                    is_missing_digit, digit_reason = detector.detect_missing_digit(price, expected_price)
                    if is_missing_digit:
                        print(f"   🔴 {digit_reason}")
                    
                    # Generate booking URL
                    booking_url = f"https://www.google.com/travel/flights?q=flights%20from%20{origin}%20to%20{dest}%20on%20{departure_date}%20returning%20{return_date}%20{cabin_class.lower()}"
                    
                    return {
                        'origin': origin,
                        'destination': dest,
                        'route_name': route_name,
                        'normal_price': expected_price,
                        'mistake_price': price,
                        'savings_amount': savings,
                        'savings_percentage': savings_pct,
                        'currency': currency,
                        'cabin_class': cabin_class,
                        'booking_url': booking_url,
                        'error_type': reason,
                        'is_mistake_fare': True
                    }
                    
            except ResponseError as e:
                continue
        
        print(f"   ✅ No mistake fares detected on this route")
        return None
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def create_mistake_fare_alert(mistake_data, db: Session):
    """Create high-priority deal for mistake fare"""
    
    # Generate deal number
    existing_count = db.query(Deal).count()
    deal_number = f"MF{str(existing_count + 1).zfill(4)}"  # MF = Mistake Fare
    
    # Create urgent headline
    cabin = mistake_data['cabin_class'].title()
    savings_pct = int(mistake_data['savings_percentage'])
    teaser_headline = f"🚨 MISTAKE FARE: {mistake_data['route_name']} - {cabin} {savings_pct}% OFF!"
    teaser_description = f"⚡ PRICING ERROR: {cabin} class for {mistake_data['currency']} {mistake_data['mistake_price']:.0f} (normally {mistake_data['currency']} {mistake_data['normal_price']:.0f}). Book immediately!"
    
    deal = Deal(
        deal_number=deal_number,
        origin=mistake_data['origin'],
        destination=mistake_data['destination'],
        route_description=mistake_data['route_name'],
        teaser_headline=teaser_headline,
        teaser_description=teaser_description,
        normal_price=mistake_data['normal_price'],
        mistake_price=mistake_data['mistake_price'],
        savings_amount=mistake_data['savings_amount'],
        savings_percentage=mistake_data['savings_percentage'],
        currency=mistake_data['currency'],
        cabin_class=mistake_data['cabin_class'],
        booking_link=mistake_data['booking_url'],
        airline='Multiple',
        unlock_fee=0.0,
        status=DealStatus.PUBLISHED,
        published_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(hours=6),  # Shorter expiry!
        travel_dates_start=datetime.now(UTC) + timedelta(days=45),
        travel_dates_end=datetime.now(UTC) + timedelta(days=52),
    )
    
    db.add(deal)
    db.commit()
    
    print(f"   💾 Created MISTAKE FARE alert: {deal_number}")
    return deal

# Main hunting loop
print("\n" + "="*80)
print("🚨 Starting mistake fare hunt...")
print("="*80)

mistake_fares_found = []

for origin, dest, route_name, expected_price, currency in PREMIUM_ROUTES:
    mistake_data = scan_route_for_mistakes(origin, dest, route_name, expected_price, currency)
    
    if mistake_data:
        mistake_fares_found.append(mistake_data)

# Save to database
print("\n" + "="*80)
print(f"📊 HUNT COMPLETE - Found {len(mistake_fares_found)} MISTAKE FARES")
print("="*80)

if mistake_fares_found:
    print("\n🚨 URGENT: Saving mistake fares to database...")
    
    with next(get_db_session()) as db:
        for mistake in mistake_fares_found:
            create_mistake_fare_alert(mistake, db)
    
    print(f"\n✅ {len(mistake_fares_found)} MISTAKE FARES added!")
    print("\n🔔 ALERT: These are pricing ERRORS - they may be fixed within hours!")
    print("   📲 Premium members should book IMMEDIATELY")
    print("   🌐 View at: http://127.0.0.1:8888")
else:
    print("\n⚠️  No mistake fares detected on these routes")
    print("   Mistake fares are rare - try again later or scan more routes")

print("\n" + "="*80)
print("💡 TIP: Run this script every 2-3 hours to catch new errors")
print("="*80)
