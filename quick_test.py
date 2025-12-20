"""
Quick Test - Just send SMS with mock deal data (Twilio)
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Mock deal (simulate what Amadeus would return)
mock_deal = {
    'origin': 'SYD',
    'destination': 'DPS',
    'price': 399,
    'departure_date': '2025-12-15',
    'destination_name': 'Bali'
}

print("="*60)
print("🚀 QUICK SMS TEST")
print("="*60)

print(f"\n📦 Mock Deal:")
print(f"   {mock_deal['origin']} → {mock_deal['destination']}")
print(f"   ${mock_deal['price']}")
print(f"   Depart: {mock_deal['departure_date']}")

# Initialize Twilio
try:
    twilio_client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    print("\n✅ Twilio client initialized")
except Exception as e:
    print(f"\n❌ Twilio initialization failed: {e}")
    exit(1)

# Format SMS
message = f"""🚨 FARE ALERT
{mock_deal['origin']}→{mock_deal['destination']}
${mock_deal['price']} 
Depart: {mock_deal['departure_date']}
Book: fareglitch.com"""

print(f"\n📱 Message ({len(message)} chars):")
print("-"*40)
print(message)
print("-"*40)

# Send SMS via Twilio
phone = os.getenv('YOUR_PHONE_NUMBER')
print(f"\n📤 Sending to: {phone}")

try:
    message_obj = twilio_client.messages.create(
        body=message,
        from_=from_number,
        to=phone
    )
    
    print(f"\n✅ SMS SENT!")
    print(f"   Message SID: {message_obj.sid}")
    print(f"   Status: {message_obj.status}")
    print(f"   From: {from_number}")
    print(f"   To: {phone}")
    print(f"\n📱 Check your phone ({phone}) in 10-30 seconds!")
    
except Exception as e:
    print(f"\n❌ SMS Failed: {e}")
    print(f"\nDebug Info:")
    print(f"  Account SID: {os.getenv('TWILIO_ACCOUNT_SID')}")
    print(f"  Auth Token: {os.getenv('TWILIO_AUTH_TOKEN')[:10]}...")
    print(f"  From: {from_number}")
    print(f"  To: {phone}")
    exit(1)

print("\n" + "="*60)
print("✅ TEST COMPLETE!")
print("="*60)
print("\n🎉 If you received the SMS, your setup works!")
print("📱 Check your phone now")
