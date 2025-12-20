#!/usr/bin/env python3
"""
Quick setup checker - Run this before test_mvp.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 CHECKING YOUR MVP SETUP\n")
print("="*60)

checks = []

# Check 1: Amadeus
amadeus_key = os.getenv('AMADEUS_API_KEY')
amadeus_secret = os.getenv('AMADEUS_API_SECRET')

if amadeus_key and amadeus_key != 'your_amadeus_api_key_here':
    print("✅ Amadeus API Key configured")
    checks.append(True)
else:
    print("❌ Amadeus API Key missing")
    print("   → Get it from: https://developers.amadeus.com/register")
    checks.append(False)

if amadeus_secret and amadeus_secret != 'your_amadeus_api_secret_here':
    print("✅ Amadeus API Secret configured")
    checks.append(True)
else:
    print("❌ Amadeus API Secret missing")
    checks.append(False)

# Check 2: Twilio
twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')

if twilio_sid and twilio_sid.startswith('AC'):
    print("✅ Twilio Account SID configured")
    checks.append(True)
else:
    print("❌ Twilio Account SID missing")
    print("   → Get it from: https://www.twilio.com/console")
    checks.append(False)

if twilio_token and twilio_token != 'your_twilio_auth_token_here':
    print("✅ Twilio Auth Token configured")
    checks.append(True)
else:
    print("❌ Twilio Auth Token missing")
    checks.append(False)

if twilio_phone and twilio_phone != '+1234567890':
    print(f"✅ Twilio Phone Number configured: {twilio_phone}")
    checks.append(True)
else:
    print("❌ Twilio Phone Number missing")
    checks.append(False)

# Check 3: Your phone
your_phone = os.getenv('YOUR_PHONE_NUMBER')

if your_phone and your_phone != '+61412345678':
    print(f"✅ Your test phone configured: {your_phone}")
    checks.append(True)
else:
    print("❌ Your test phone number missing")
    print("   → Add YOUR_PHONE_NUMBER=+61... to .env")
    checks.append(False)

# Summary
print("\n" + "="*60)

if all(checks):
    print("🎉 ALL CHECKS PASSED!")
    print("\nYou're ready to run:")
    print("  python test_mvp.py")
else:
    print(f"⚠️  {sum(checks)}/{len(checks)} checks passed")
    print("\nFix the ❌ items above, then run:")
    print("  python check_setup.py")

print("="*60)
