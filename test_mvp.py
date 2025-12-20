"""
MVP Test Script - Find 1 deal and send SMS
Run this to test your complete pipeline!
"""
import os
import sys
from dotenv import load_dotenv
from amadeus import Client
from twilio.rest import Client as TwilioClient

# Load environment
load_dotenv()

# Initialize clients
try:
    amadeus = Client(
        client_id=os.getenv('AMADEUS_API_KEY'),
        client_secret=os.getenv('AMADEUS_API_SECRET')
    )
    print("✅ Amadeus client initialized")
except Exception as e:
    print(f"❌ Amadeus client failed: {e}")
    sys.exit(1)

try:
    twilio = TwilioClient(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    print("✅ Twilio client initialized")
except Exception as e:
    print(f"❌ Twilio client failed: {e}")
    sys.exit(1)


def find_one_deal(origin='SYD', max_price=800):
    """
    Find cheapest destination from origin
    """
    print(f"\n🔍 Searching for deals from {origin} under ${max_price}...")
    
    try:
        response = amadeus.shopping.flight_destinations.get(
            origin=origin,
            maxPrice=max_price
        )
        
        if not response.data:
            print("❌ No deals found")
            return None
        
        # Get the cheapest one
        best_deal = min(response.data, key=lambda x: float(x['price']['total']))
        
        deal = {
            'origin': origin,
            'destination': best_deal['destination'],
            'price': float(best_deal['price']['total']),
            'departure_date': best_deal.get('departureDate', 'Various dates'),
            'return_date': best_deal.get('returnDate', 'One way'),
            'destination_name': best_deal.get('destination', 'Unknown')
        }
        
        print(f"✅ Found: {deal['origin']} → {deal['destination']} for ${deal['price']}")
        print(f"   Departure: {deal['departure_date']}")
        
        return deal
        
    except Exception as e:
        print(f"❌ Error searching flights: {e}")
        return None


def send_sms_alert(deal, phone_number):
    """
    Send SMS alert about the deal
    """
    # Format message (under 160 chars for single SMS)
    message = f"""🚨 FARE ALERT
{deal['origin']}→{deal['destination']}
${int(deal['price'])} 
Depart: {deal['departure_date'][:10]}
Book: fareglitch.com"""
    
    print(f"\n📱 Sending SMS to {phone_number}...")
    print(f"Message preview:\n{'-'*40}\n{message}\n{'-'*40}")
    print(f"Length: {len(message)} chars")
    
    try:
        result = twilio.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=phone_number
        )
        
        print(f"\n✅ SMS Sent!")
        print(f"   Message SID: {result.sid}")
        print(f"   Status: {result.status}")
        print(f"   From: {os.getenv('TWILIO_PHONE_NUMBER')}")
        print(f"   To: {phone_number}")
        return True
        
    except Exception as e:
        print(f"\n❌ SMS Failed: {e}")
        return False


def show_instagram_post(deal):
    """
    Show what to post on Instagram
    """
    print("\n" + "="*50)
    print("📸 INSTAGRAM POST (Post this 1 hour after SMS)")
    print("="*50)
    
    caption = f"""🚨 ERROR FARE ALERT

{deal['origin']} → {deal['destination']}
${int(deal['price'])} (Check Skyscanner for normal price)

Dates: {deal['departure_date'][:10]}
Type: Check airline/stops on booking site

⚠️ This deal may be gone soon. Airlines can correct pricing errors at any time.

📱 Want these alerts 1 HOUR before I post them?
👉 DM "ALERTS" to subscribe ($5/month)

#cheapflights #errorfare #travel #{deal['destination'].lower()}"""
    
    print(f"\nCaption:\n{caption}\n")
    print("Image: Use Canva.com -> Instagram Post -> Travel template")
    print(f"  - Headline: 🚨 ERROR FARE ALERT")
    print(f"  - Route: {deal['origin']} → {deal['destination']}")
    print(f"  - Price: ${int(deal['price'])}")
    print(f"  - Bottom: 'DM ALERTS to subscribe'")


def main():
    """
    MVP Flow: Find deal → Send SMS → Show Instagram template
    """
    print("\n" + "="*60)
    print("🚀 FAREGLITCH MVP TEST")
    print("="*60)
    
    # Check environment variables
    required_vars = [
        'AMADEUS_API_KEY',
        'AMADEUS_API_SECRET', 
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER',
        'YOUR_PHONE_NUMBER'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("\nAdd these to your .env file and try again.")
        sys.exit(1)
    
    # Step 1: Find a deal
    print("\n" + "="*60)
    print("STEP 1: FINDING DEAL")
    print("="*60)
    
    deal = find_one_deal(origin='SYD', max_price=800)
    
    if not deal:
        print("\n❌ No deals found. Try:")
        print("  1. Increase max_price (e.g., 1000)")
        print("  2. Try different origin (e.g., MEL, BNE)")
        print("  3. Check Amadeus API quota")
        sys.exit(1)
    
    # Step 2: Send SMS
    print("\n" + "="*60)
    print("STEP 2: SENDING SMS ALERT")
    print("="*60)
    
    phone = os.getenv('YOUR_PHONE_NUMBER')
    
    success = send_sms_alert(deal, phone)
    
    if not success:
        print("\n❌ SMS failed. Check:")
        print("  1. Twilio account has credit ($15 free trial)")
        print("  2. Phone number is verified")
        print("  3. Phone number includes country code (+61)")
        sys.exit(1)
    
    # Step 3: Show Instagram post
    print("\n" + "="*60)
    print("STEP 3: INSTAGRAM POST")
    print("="*60)
    
    show_instagram_post(deal)
    
    # Success!
    print("\n" + "="*60)
    print("✅ MVP TEST SUCCESSFUL!")
    print("="*60)
    
    print("\n🎉 What just happened:")
    print("  1. ✅ Found a flight deal using Amadeus API")
    print("  2. ✅ Sent SMS alert via Twilio")
    print("  3. ✅ Generated Instagram post template")
    
    print("\n📱 Next Steps:")
    print("  1. Check your phone for the SMS (may take 10-30 seconds)")
    print("  2. Wait 1 hour")
    print("  3. Post to Instagram using template above")
    print("  4. Add 'DM ALERTS' to your Instagram bio")
    print("  5. Run this script daily to find new deals")
    
    print("\n💰 To Get Your First Subscriber:")
    print("  1. Post the deal to Instagram")
    print("  2. Tell friends 'DM me ALERTS'")
    print("  3. When someone DMs, send them Stripe payment link")
    print("  4. Add them to database when paid")
    
    print("\n🚀 You're live! Go build your business.")


if __name__ == "__main__":
    main()
