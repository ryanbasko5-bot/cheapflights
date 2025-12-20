"""
Debug Sinch SMS - Check configuration and test with detailed logging
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("🔍 SINCH SMS DEBUG")
print("="*60)

# Get credentials
service_plan_id = os.getenv('SINCH_SERVICE_PLAN_ID')
api_token = os.getenv('SINCH_API_TOKEN')
from_number = os.getenv('SINCH_PHONE_NUMBER')
to_number = os.getenv('YOUR_PHONE_NUMBER')

print("\n📋 Configuration:")
print(f"  Service Plan ID: {service_plan_id}")
print(f"  API Token: {api_token[:10]}...{api_token[-4:]}")
print(f"  From Number: {from_number}")
print(f"  To Number: {to_number}")

# Check for issues
issues = []
if not service_plan_id or service_plan_id == 'your_service_plan_id_here':
    issues.append("❌ Service Plan ID not set")
if not api_token or api_token == 'your_api_token_here':
    issues.append("❌ API Token not set")
if not from_number or from_number == '+1234567890':
    issues.append("❌ From number not set")
if not to_number:
    issues.append("❌ Your phone number not set")

if issues:
    print("\n🚨 Configuration Issues:")
    for issue in issues:
        print(f"  {issue}")
    exit(1)

print("\n✅ Configuration looks good!")

# Test API connection
print("\n📡 Testing Sinch API connection...")

url = f"https://us.sms.api.sinch.com/xms/v1/{service_plan_id}/batches"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

message = "Test from FareGlitch. Reply STOP to opt out."

payload = {
    "from": from_number,
    "to": [to_number],
    "body": message
}

print(f"\n📤 Sending test SMS...")
print(f"  URL: {url}")
print(f"  From: {from_number}")
print(f"  To: {to_number}")
print(f"  Message: {message}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print(f"\n📊 Response:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response Body: {response.text}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"\n✅ SMS Request Accepted!")
        print(f"  Batch ID: {result.get('id', 'N/A')}")
        print(f"  Status: {result.get('type', 'N/A')}")
        print(f"  Created: {result.get('created_at', 'N/A')}")
        
        # Check if there are any delivery issues mentioned
        if 'canceled' in result:
            print(f"  ⚠️ Canceled: {result['canceled']}")
        
        print(f"\n📱 SMS should arrive in 10-60 seconds")
        print(f"\n💡 Common reasons for no delivery:")
        print(f"  1. Phone number format (needs country code +61)")
        print(f"  2. Sinch account not verified")
        print(f"  3. Destination country not enabled")
        print(f"  4. Free trial restrictions")
        print(f"  5. From number not active/verified")
        
        print(f"\n🔍 Check delivery status:")
        print(f"  https://dashboard.sinch.com/sms/logs")
        
    else:
        print(f"\n❌ SMS Request Failed!")
        print(f"\n💡 Possible issues:")
        if response.status_code == 401:
            print(f"  - Invalid API token or Service Plan ID")
        elif response.status_code == 400:
            print(f"  - Invalid phone number format")
            print(f"  - From number not configured correctly")
        elif response.status_code == 403:
            print(f"  - Account not authorized")
            print(f"  - Country/region not enabled")
        
except requests.exceptions.Timeout:
    print(f"\n❌ Request timed out")
    print(f"  - Check internet connection")
    print(f"  - Sinch API may be down")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
