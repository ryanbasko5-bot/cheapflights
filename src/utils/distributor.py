"""
Automated Deal Distribution System
1. Send SMS instantly (with local currency)
2. Wait 1 hour
3. Auto-post to HubSpot website
4. Auto-post to Instagram
"""
import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from twilio.rest import Client as TwilioClient

# Import our currency converter
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.currency import get_currency_from_phone, convert_currency, format_price_for_sms

load_dotenv()


class DealDistributor:
    """
    Handles the complete deal distribution workflow
    """
    
    def __init__(self):
        # Twilio for SMS
        self.twilio = TwilioClient(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        # HubSpot (optional - set in .env)
        self.hubspot_api_key = os.getenv('HUBSPOT_API_KEY')
        
        # Instagram (optional - set in .env)
        self.instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.instagram_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        
        # Instagram delay (1 hour default)
        self.instagram_delay_hours = int(os.getenv('INSTAGRAM_DELAY_HOURS', 1))
    
    
    def send_sms_with_local_currency(self, deal: dict, subscriber_phone: str):
        """
        Send SMS alert with price converted to subscriber's local currency
        
        Args:
            deal: Deal dictionary with origin, destination, price, currency, etc.
            subscriber_phone: Phone number (e.g., '+61412345678')
        """
        # Detect subscriber's currency from phone number
        subscriber_currency = get_currency_from_phone(subscriber_phone)
        
        # Convert price
        converted = convert_currency(
            amount=deal['price'],
            from_currency=deal['currency'],
            to_currency=subscriber_currency
        )
        
        # Format price nicely
        formatted_price = format_price_for_sms(converted['amount'], converted['currency'])
        
        # Build SMS message
        message = f"""🚨 FARE ALERT
{deal['origin']}→{deal['destination']}
{formatted_price}
Depart: {deal['departure_date']}
Book: fareglitch.com.au"""
        
        print(f"\n📱 Sending to {subscriber_phone}")
        print(f"   Original: {deal['price']} {deal['currency']}")
        print(f"   Converted: {formatted_price}")
        print(f"   Message: {len(message)} chars")
        
        try:
            result = self.twilio.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=subscriber_phone
            )
            
            print(f"   ✅ Sent! (SID: {result.sid})")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
    
    
    def post_to_hubspot(self, deal: dict):
        """
        Auto-post deal to HubSpot website via API
        
        Args:
            deal: Deal dictionary
        """
        if not self.hubspot_api_key:
            print("\n⚠️ HubSpot API key not set (skipping)")
            return False
        
        print("\n🌐 Posting to HubSpot website...")
        
        try:
            # Create blog post via HubSpot API
            url = "https://api.hubapi.com/content/api/v2/blog-posts"
            
            headers = {
                "Authorization": f"Bearer {self.hubspot_api_key}",
                "Content-Type": "application/json"
            }
            
            # Format post content
            title = f"🚨 {deal['origin']} → {deal['destination']} for {deal['currency']} ${int(deal['price'])}"
            
            content = f"""
            <div class="deal-card">
                <h2>🚨 Error Fare Alert</h2>
                <h3>{deal['origin']} → {deal['destination_name']}</h3>
                <div class="price">{deal['currency']} ${int(deal['price'])}</div>
                <p><strong>Departure:</strong> {deal['departure_date']}</p>
                <p><strong>Airline:</strong> {deal['airline']}</p>
                <p><strong>Stops:</strong> {deal['stops']} stop(s)</p>
                <p>⚠️ <em>This deal may be gone soon! Airlines can correct pricing errors at any time.</em></p>
                <a href="https://www.skyscanner.com.au/transport/flights/{deal['origin'].lower()}/{deal['destination'].lower()}/" 
                   class="btn btn-primary" target="_blank">Search Flights</a>
            </div>
            """
            
            payload = {
                "name": title,
                "post_body": content,
                "publish_immediately": True,
                "meta_description": f"Save big on flights from {deal['origin']} to {deal['destination']}!",
                "slug": f"deal-{deal['origin'].lower()}-{deal['destination'].lower()}-{datetime.now().strftime('%Y%m%d')}",
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                post_data = response.json()
                post_url = post_data.get('url', 'N/A')
                print(f"   ✅ Posted! {post_url}")
                return True
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    
    def post_to_instagram(self, deal: dict, image_path: str = None):
        """
        Auto-post deal to Instagram via API
        
        Args:
            deal: Deal dictionary
            image_path: Optional path to image (if None, uses caption only)
        """
        if not self.instagram_token or not self.instagram_account_id:
            print("\n⚠️ Instagram credentials not set (skipping)")
            print("   Manual posting required - use caption below:")
            self._print_instagram_caption(deal)
            return False
        
        print("\n📸 Posting to Instagram...")
        
        try:
            # Format caption
            caption = f"""🚨 ERROR FARE ALERT

{deal['origin']} → {deal['destination']} ({deal['destination_name']})
{deal['currency']} ${int(deal['price'])}

Departure: {deal['departure_date']}
Airline: {deal['airline']}
Stops: {'Direct' if deal['stops'] == 0 else f"{deal['stops']} stop(s)"}

⚠️ May be gone by tomorrow!

📱 Want alerts 1 HOUR before I post?
👉 DM "ALERTS" ($5/month)

Link in bio to book!

#cheapflights #sydneyflights #traveldeals #errorfare #flighthacks"""
            
            # Instagram API endpoint
            url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media"
            
            payload = {
                "caption": caption,
                "access_token": self.instagram_token
            }
            
            # If image provided, upload it
            if image_path and os.path.exists(image_path):
                payload["image_url"] = image_path
            
            # Create media container
            response = requests.post(url, data=payload)
            
            if response.status_code == 200:
                media_id = response.json()['id']
                
                # Publish the post
                publish_url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/media_publish"
                publish_payload = {
                    "creation_id": media_id,
                    "access_token": self.instagram_token
                }
                
                publish_response = requests.post(publish_url, data=publish_payload)
                
                if publish_response.status_code == 200:
                    print(f"   ✅ Posted to Instagram!")
                    return True
                else:
                    print(f"   ❌ Publish failed: {publish_response.text}")
                    return False
            else:
                print(f"   ❌ Media creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("\n📋 Use this caption for manual posting:")
            self._print_instagram_caption(deal)
            return False
    
    
    def _print_instagram_caption(self, deal: dict):
        """Print Instagram caption for manual posting"""
        caption = f"""🚨 ERROR FARE ALERT

{deal['origin']} → {deal['destination']} ({deal['destination_name']})
{deal['currency']} ${int(deal['price'])}

Departure: {deal['departure_date']}
Airline: {deal['airline']}
Stops: {'Direct' if deal['stops'] == 0 else f"{deal['stops']} stop(s)"}

⚠️ May be gone by tomorrow!

📱 Want alerts 1 HOUR before I post?
👉 DM "ALERTS" ($5/month)

Link in bio to book!

#cheapflights #sydneyflights #traveldeals #errorfare #flighthacks"""
        
        print("\n" + "="*60)
        print("📸 INSTAGRAM CAPTION (copy this):")
        print("="*60)
        print(caption)
        print("="*60)
    
    
    def distribute_deal(self, deal: dict, subscribers: list):
        """
        Complete automated workflow:
        1. Send SMS instantly (all subscribers)
        2. Wait 1 hour
        3. Post to HubSpot
        4. Post to Instagram
        
        Args:
            deal: Deal dictionary
            subscribers: List of phone numbers
        """
        print("\n" + "="*60)
        print("🚀 AUTOMATED DEAL DISTRIBUTION")
        print("="*60)
        
        # STEP 1: Send SMS to all subscribers (INSTANT)
        print(f"\n⏰ Step 1: Sending SMS to {len(subscribers)} subscribers...")
        
        for phone in subscribers:
            self.send_sms_with_local_currency(deal, phone)
            time.sleep(1)  # Rate limiting
        
        print(f"\n✅ SMS sent to all subscribers!")
        
        # STEP 2: Wait 1 hour
        print(f"\n⏳ Step 2: Waiting {self.instagram_delay_hours} hour(s) before public posting...")
        print(f"   Current time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Will post at: {(datetime.now() + timedelta(hours=self.instagram_delay_hours)).strftime('%H:%M:%S')}")
        
        # For MVP: Don't actually wait, just show what would happen
        # Uncomment below for production:
        # time.sleep(self.instagram_delay_hours * 3600)
        
        print(f"\n   (Skipping wait for MVP demo)")
        
        # STEP 3: Post to HubSpot
        print(f"\n🌐 Step 3: Posting to HubSpot website...")
        self.post_to_hubspot(deal)
        
        # STEP 4: Post to Instagram
        print(f"\n📸 Step 4: Posting to Instagram...")
        self.post_to_instagram(deal)
        
        print("\n" + "="*60)
        print("✅ DISTRIBUTION COMPLETE!")
        print("="*60)


# Test/Demo
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Mock deal
    test_deal = {
        'origin': 'SYD',
        'destination': 'BKK',
        'destination_name': 'Bangkok',
        'price': 202.57,
        'currency': 'EUR',
        'departure_date': '2025-12-28',
        'airline': 'OD',
        'stops': 1
    }
    
    # Mock subscribers (different countries)
    test_subscribers = [
        '+61411246861',  # Australia → AUD
        # '+14155551234',  # US → USD
        # '+447700900123', # UK → GBP
    ]
    
    distributor = DealDistributor()
    distributor.distribute_deal(test_deal, test_subscribers)
