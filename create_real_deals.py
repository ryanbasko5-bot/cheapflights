"""
Create Real Deals from Previous Amadeus Test Results
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import Deal, DealStatus
from src.utils.database import get_db_session, init_db

print("Creating real flight deals with booking links...")

init_db()

# Based on our previous Amadeus API test results
real_deals = [
    {
        'deal_number': 'FG001',
        'origin': 'JFK',
        'destination': 'LAX',
        'route_description': 'New York (JFK) → Los Angeles (LAX)',
        'teaser_headline': '🔥 NYC to LA - Save 76%!',
        'teaser_description': 'Fly economy class for just €71 (normally €300)',
        'normal_price': 300.00,
        'mistake_price': 71.39,
        'savings_amount': 228.61,
        'savings_percentage': 76.2,
        'currency': 'EUR',
        'cabin_class': 'ECONOMY',
        'airline': 'Multiple Airlines',
        'booking_url': 'https://www.google.com/travel/flights?q=flights%20from%20JFK%20to%20LAX',
    },
    {
        'deal_number': 'FG002',
        'origin': 'LHR',
        'destination': 'DXB',
        'route_description': 'London (LHR) → Dubai (DXB)',
        'teaser_headline': '🌍 London to Dubai - Save 26%!',
        'teaser_description': 'Fly economy class for just €331 (normally €450)',
        'normal_price': 450.00,
        'mistake_price': 331.67,
        'savings_amount': 118.33,
        'savings_percentage': 26.3,
        'currency': 'EUR',
        'cabin_class': 'ECONOMY',
        'airline': 'Multiple Airlines',
        'booking_url': 'https://www.google.com/travel/flights?q=flights%20from%20LHR%20to%20DXB',
    },
    {
        'deal_number': 'FG003',
        'origin': 'SYD',
        'destination': 'DPS',
        'route_description': 'Sydney (SYD) → Bali (DPS)',
        'teaser_headline': '🏝️ Sydney to Bali - Save 73%!',
        'teaser_description': 'Fly economy class for just €159 (normally €600)',
        'normal_price': 600.00,
        'mistake_price': 159.26,
        'savings_amount': 440.74,
        'savings_percentage': 73.5,
        'currency': 'EUR',
        'cabin_class': 'ECONOMY',
        'airline': 'Multiple Airlines',
        'booking_url': 'https://www.google.com/travel/flights?q=flights%20from%20SYD%20to%20DPS',
    },
    {
        'deal_number': 'FG004',
        'origin': 'LAX',
        'destination': 'NRT',
        'route_description': 'Los Angeles (LAX) → Tokyo (NRT)',
        'teaser_headline': '🗼 LA to Tokyo - Save 64%!',
        'teaser_description': 'Fly economy class for just €291 (normally €800)',
        'normal_price': 800.00,
        'mistake_price': 291.20,
        'savings_amount': 508.80,
        'savings_percentage': 63.6,
        'currency': 'EUR',
        'cabin_class': 'ECONOMY',
        'airline': 'Multiple Airlines',
        'booking_url': 'https://www.google.com/travel/flights?q=flights%20from%20LAX%20to%20NRT',
    },
]

with next(get_db_session()) as db:
    # Clear existing deals
    db.query(Deal).delete()
    db.commit()
    print("✅ Cleared old test deals")
    
    # Create new deals
    for deal_data in real_deals:
        deal = Deal(
            deal_number=deal_data['deal_number'],
            origin=deal_data['origin'],
            destination=deal_data['destination'],
            route_description=deal_data['route_description'],
            teaser_headline=deal_data['teaser_headline'],
            teaser_description=deal_data['teaser_description'],
            normal_price=deal_data['normal_price'],
            mistake_price=deal_data['mistake_price'],
            savings_amount=deal_data['savings_amount'],
            savings_percentage=deal_data['savings_percentage'],
            currency=deal_data['currency'],
            cabin_class=deal_data['cabin_class'],
            airline=deal_data['airline'],
            booking_url=deal_data['booking_url'],
            unlock_fee=0.0,
            status=DealStatus.ACTIVE,
            published_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=3),
            travel_dates_start=datetime.utcnow() + timedelta(days=30),
            travel_dates_end=datetime.utcnow() + timedelta(days=37),
        )
        db.add(deal)
        print(f"✅ Created {deal_data['deal_number']}: {deal_data['route_description']} - Save {deal_data['savings_percentage']:.0f}%")
    
    db.commit()

print(f"\n🎉 SUCCESS! Created {len(real_deals)} real deals")
print("\n🌐 Now visit http://127.0.0.1:8888 and:")
print("   1. Sign in as premium@test.com")
print("   2. See all 4 real flight deals")
print("   3. Click any deal to see the booking link on Google Flights!")
