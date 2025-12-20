"""
Send test SMS to specific number
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Test recipient
to_number = "+61410178010"

# Mock deal
deal = {
    'origin': 'SYD',
    'destination': 'BKK',
    'price': 202.57,
    'currency': 'EUR',
    'departure_date': '2025-12-28'
}

print("="*60)
print("📱 SENDING TEST SMS")
print("="*60)

# Initialize Twilio
twilio = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

# Convert price to AUD (Australian number)
from src.utils.currency import convert_currency, format_price_for_sms

converted = convert_currency(deal['price'], deal['currency'], 'AUD')
formatted_price = format_price_for_sms(converted['amount'], 'AUD')

# Format message
message = f"""🚨 FARE ALERT
{deal['origin']}→{deal['destination']}
{formatted_price}
Depart: {deal['departure_date']}
Book: fareglitch.com"""

print(f"\n📤 To: {to_number}")
print(f"📝 Message ({len(message)} chars):")
print("-"*40)
print(message)
print("-"*40)

print(f"\n💱 Price Conversion:")
print(f"   Original: €{deal['price']}")
print(f"   Converted: {formatted_price}")

try:
    result = twilio.messages.create(
        body=message,
        from_=os.getenv('TWILIO_PHONE_NUMBER'),
        to=to_number
    )
    
    print(f"\n✅ SMS SENT!")
    print(f"   Message SID: {result.sid}")
    print(f"   Status: {result.status}")
    print(f"   From: {os.getenv('TWILIO_PHONE_NUMBER')}")
    print(f"   To: {to_number}")
    print(f"\n📱 Check the phone in 10-30 seconds!")
    
except Exception as e:
    print(f"\n❌ Failed: {e}")

print("\n" + "="*60)
