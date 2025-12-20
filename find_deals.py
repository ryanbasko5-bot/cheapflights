"""
Find Real Deals - Works with Amadeus Test API
"""
import os
from dotenv import load_dotenv
from amadeus import Client
from twilio.rest import Client as TwilioClient
from datetime import datetime, timedelta

load_dotenv()

print("="*60)
print("🔍 FINDING REAL FLIGHT DEALS")
print("="*60)

# Initialize
amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)

print("\n✅ Amadeus client initialized (Test Environment)")

# Try Flight Offers Search (works better in test)
print("\n🔍 Searching for cheap flights from SYD...")

# Search next month
departure_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

try:
    # Search for actual flights
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='SYD',
        destinationLocationCode='BKK',  # Bangkok (usually cheap from Sydney)
        departureDate=departure_date,
        adults=1,
        max=5
    )
    
    if response.data:
        print(f"✅ Found {len(response.data)} flights!")
        
        # Get cheapest
        cheapest = min(response.data, key=lambda x: float(x['price']['total']))
        
        deal = {
            'origin': 'SYD',
            'destination': 'BKK',
            'destination_name': 'Bangkok',
            'price': float(cheapest['price']['total']),
            'currency': cheapest['price']['currency'],
            'departure_date': cheapest['itineraries'][0]['segments'][0]['departure']['at'][:10],
            'airline': cheapest['itineraries'][0]['segments'][0]['carrierCode'],
            'stops': len(cheapest['itineraries'][0]['segments']) - 1
        }
        
        print(f"\n💰 BEST DEAL FOUND:")
        print(f"   Route: {deal['origin']} → {deal['destination']} ({deal['destination_name']})")
        print(f"   Price: {deal['currency']} ${deal['price']}")
        print(f"   Date: {deal['departure_date']}")
        print(f"   Airline: {deal['airline']}")
        print(f"   Stops: {deal['stops']}")
        
        # Format SMS
        message = f"""🚨 FARE ALERT
{deal['origin']}→{deal['destination']}
${int(deal['price'])} {deal['currency']}
Depart: {deal['departure_date']}
Book: fareglitch.com"""
        
        print(f"\n📱 SMS MESSAGE ({len(message)} chars):")
        print("-"*40)
        print(message)
        print("-"*40)
        
        # Send SMS
        print(f"\n📤 Sending to: {os.getenv('YOUR_PHONE_NUMBER')}")
        
        twilio = TwilioClient(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        result = twilio.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=os.getenv('YOUR_PHONE_NUMBER')
        )
        
        print(f"✅ SMS SENT! (SID: {result.sid})")
        
        # Instagram post
        print("\n" + "="*60)
        print("📸 INSTAGRAM POST TEMPLATE")
        print("="*60)
        
        caption = f"""🚨 ERROR FARE ALERT

{deal['origin']} → {deal['destination']} ({deal['destination_name']})
${int(deal['price'])} {deal['currency']}

Departure: {deal['departure_date']}
Airline: {deal['airline']}
Stops: {'Direct' if deal['stops'] == 0 else f'{deal["stops"]} stop(s)'}

⚠️ This deal may be gone soon!

📱 Want alerts 1 HOUR before I post them?
👉 DM "ALERTS" to subscribe ($5/month)

Link in bio to book!

#cheapflights #sydneyflights #bangkok #traveldeals #fareglitch #errorfare"""

        print(f"\n{caption}")
        
        print("\n" + "="*60)
        print("✅ COMPLETE! CHECK YOUR PHONE!")
        print("="*60)
        
        print("\n📸 CREATE INSTAGRAM IMAGE:")
        print("  1. Go to Canva.com")
        print("  2. Search 'Instagram Post' → 'Travel'")
        print("  3. Add text:")
        print(f"     🚨 ERROR FARE")
        print(f"     {deal['origin']} → {deal['destination']}")
        print(f"     ${int(deal['price'])} {deal['currency']}")
        print(f"     DM ALERTS to subscribe")
        print("  4. Download & post to Instagram!")
        
    else:
        print("❌ No flights found")
        print("Try different destination or date")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying alternative destinations...")
    
    # Try multiple destinations
    destinations = ['BKK', 'DPS', 'SIN', 'HKT', 'KUL']
    
    for dest in destinations:
        try:
            print(f"\n🔍 Trying {dest}...")
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode='SYD',
                destinationLocationCode=dest,
                departureDate=departure_date,
                adults=1,
                max=3
            )
            
            if response.data:
                price = float(response.data[0]['price']['total'])
                print(f"   ✅ Found! ${price}")
                break
        except:
            print(f"   ❌ No data for {dest}")
            continue
