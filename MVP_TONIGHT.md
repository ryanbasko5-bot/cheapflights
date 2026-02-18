# 🚀 Launch Your MVP TONIGHT

**Goal**: Get your first SMS alert working in < 2 hours.

---

## ⏱️ Timeline (2 Hours Max)

- **0:00-0:20** → API Setup (Amadeus + Twilio)
- **0:20-0:40** → Configure Environment
- **0:40-1:00** → Test Scanner
- **1:00-1:20** → Send First SMS
- **1:20-2:00** → Instagram Post + Buffer

---

## 🎯 Step 1: Get API Keys (20 mins)

### 1.1 Amadeus API (Flight Data)

**URL**: https://developers.amadeus.com/register

1. Click "Register"
2. Fill in basic info
3. Go to "My Apps" → "Create New App"
4. Select **"Flight Inspiration Search"** API
5. Copy credentials:
   ```
   API Key: [YOUR_KEY]
   API Secret: [YOUR_SECRET]
   ```

**Test Environment**: Free, 10,000 calls/month

### 1.2 Sinch SMS (Alerts)

**URL**: https://dashboard.sinch.com/signup

1. Sign up (free trial available)
2. Get credentials from **SMS → APIs** tab:
   ```
   Service Plan ID: abc123def456
   API Token: [YOUR_TOKEN]
   ```
3. Buy a **phone number** from **Numbers** tab

**Trial**: Free credits to test (~$2-5 USD)

**Full Guide**: See `/docs/SINCH_SETUP.md`

### 1.3 Duffel API (Validation) - OPTIONAL for MVP

**URL**: https://duffel.com/signup

1. Sign up
2. Get API token
3. **For MVP**: Skip this, validate manually

---

## ⚙️ Step 2: Configure Environment (20 mins)

### 2.1 Clone & Setup

```bash
cd /workspaces/cheapflights

# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 2.2 Fill in `.env` file

```env
# Amadeus API (Required) - copy from your .env file
AMADEUS_API_KEY=<copy from your .env>
AMADEUS_API_SECRET=<copy from your .env>

# Sinch SMS (Required) - GET FROM dashboard.sinch.com
SINCH_SERVICE_PLAN_ID=your_service_plan_id_here
SINCH_API_TOKEN=your_api_token_here
SINCH_PHONE_NUMBER=+1234567890

# Your test phone number
YOUR_PHONE_NUMBER=+61412345678

# Duffel API (Skip for MVP)
# DUFFEL_API_KEY=duffel_test_xxx

# Database (Use SQLite for MVP)
DATABASE_URL=sqlite:///./fareglitch.db

# Simple config
ALERT_FEE=5.00
INSTAGRAM_DELAY_HOURS=1
ENABLE_SLACK_ALERTS=false
```

### 2.3 Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

---

## 🔍 Step 3: Test Scanner (20 mins)

### 3.1 Create Test Script

Create `test_mvp.py`:

```python
"""
MVP Test Script - Find 1 deal and send SMS
"""
import os
from dotenv import load_dotenv
from amadeus import Client
from twilio.rest import Client as TwilioClient

# Load environment
load_dotenv()

# Initialize clients
amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)

twilio = TwilioClient(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

def find_one_deal(origin='SYD', max_price=800):
    """
    Find cheapest destination from origin
    """
    print(f"🔍 Searching for deals from {origin}...")
    
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
            'return_date': best_deal.get('returnDate', 'One way')
        }
        
        print(f"✅ Found: {deal['origin']} → {deal['destination']} for ${deal['price']}")
        return deal
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def send_sms_alert(deal, phone_number):
    """
    Send SMS alert about the deal
    """
    # Format message (under 160 chars for single SMS)
    message = f"""🚨 FARE ALERT
{deal['origin']}→{deal['destination']}
${deal['price']} 
Depart: {deal['departure_date']}
Book: fareglitch.com"""
    
    print(f"\n📱 Sending SMS to {phone_number}...")
    print(f"Message:\n{message}\n")
    
    try:
        result = twilio.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=phone_number
        )
        
        print(f"✅ SMS Sent! Message SID: {result.sid}")
        print(f"Status: {result.status}")
        return True
        
    except Exception as e:
        print(f"❌ SMS Failed: {e}")
        return False

def main():
    """
    MVP Flow: Find deal → Send SMS
    """
    print("="*50)
    print("🚀 FAREGLITCH MVP TEST")
    print("="*50 + "\n")
    
    # Step 1: Find a deal
    deal = find_one_deal(origin='SYD', max_price=800)
    
    if not deal:
        print("\n❌ No deals found. Try again or increase max_price.")
        return
    
    # Step 2: Send SMS
    phone = os.getenv('YOUR_PHONE_NUMBER')
    
    if not phone:
        print("\n❌ Set YOUR_PHONE_NUMBER in .env file")
        return
    
    success = send_sms_alert(deal, phone)
    
    if success:
        print("\n" + "="*50)
        print("✅ MVP TEST SUCCESSFUL!")
        print("="*50)
        print("\nNext steps:")
        print("1. Check your phone for SMS")
        print("2. Post this deal to Instagram (manual for MVP)")
        print("3. Add more subscribers to database")
    else:
        print("\n❌ MVP test failed. Check your Twilio credentials.")

if __name__ == "__main__":
    main()
```

### 3.2 Run Test

```bash
python test_mvp.py
```

**Expected Output**:
```
==================================================
🚀 FAREGLITCH MVP TEST
==================================================

🔍 Searching for deals from SYD...
✅ Found: SYD → DPS for $420

📱 Sending SMS to +61412345678...
Message:
🚨 FARE ALERT
SYD→DPS
$420 
Depart: 2025-12-15
Book: fareglitch.com

✅ SMS Sent! Message SID: SMxxxxxxxxx
Status: queued

==================================================
✅ MVP TEST SUCCESSFUL!
==================================================

Next steps:
1. Check your phone for SMS
2. Post this deal to Instagram (manual for MVP)
3. Add more subscribers to database
```

**Check your phone** - you should receive the SMS in 10-30 seconds!

---

## 📱 Step 4: Send Your First Real Alert (20 mins)

### 4.1 Manual Process (Tonight)

For MVP, do this manually:

1. **Run scanner once per day**:
   ```bash
   python test_mvp.py
   ```

2. **Review the deal**:
   - Is the price actually good?
   - Can you find it on Skyscanner?
   - Is it bookable?

3. **If good, send SMS** (script does this automatically)

4. **Wait 1 hour**

5. **Post to Instagram**:
   - Screenshot the deal
   - Use Canva to make it pretty
   - Caption: "🚨 ERROR FARE: SYD→Bali $420"
   - Hashtags: #cheapflights #errorfare #bali

### 4.2 Get Your First Subscriber

**Option A: Test with yourself**
```bash
# Add your phone to database
python -c "
from src.models.database import engine, Base, Subscriber
from sqlalchemy.orm import Session

Base.metadata.create_all(engine)

with Session(engine) as session:
    sub = Subscriber(
        phone_number='+61412345678',
        subscription_type='sms_monthly',
        is_active=True,
        regions='oceania,asia'
    )
    session.add(sub)
    session.commit()
    print('✅ Added subscriber!')
"
```

**Option B: Get a real subscriber**
- Post on Instagram: "DM ALERTS to get deals 1hr before I post them"
- When someone DMs, manually add their number to database
- Send them payment link (Stripe/PayPal)
- Activate subscription when paid

---

## 📸 Step 5: Instagram Post (20 mins)

### 5.1 Create Post in Canva

**Template** (Free):
1. Go to Canva.com
2. Search "Instagram Post Travel"
3. Pick a template
4. Edit:
   - **Headline**: "🚨 ERROR FARE ALERT"
   - **Route**: "SYD → BALI"
   - **Price**: "$420" (with strikethrough of normal price)
   - **Savings**: "SAVE $380"
   - **Bottom**: "DM 'ALERTS' for instant notifications"

### 5.2 Post Caption

```
🚨 ERROR FARE ALERT

Sydney → Bali
$420 (Normally $800)
SAVE $380 (52% off)

Dates: Dec 15 - Dec 22
Airline: Jetstar
Type: Direct flight

⚠️ This deal may be gone soon. Airlines can correct pricing errors at any time.

📱 Want these alerts 1 HOUR before I post them?
👉 DM "ALERTS" to subscribe ($5/month)

✈️ Found this deal? Tag us!

#cheapflights #errorfare #bali #sydneyflights #travelhack #cheaptravel #flightdeals #budgettravel #wanderlust #travelaustralia
```

### 5.3 Post Timing

- **SMS sent**: 6pm
- **Instagram post**: 7pm (1 hour later)
- **Best times**: 6-8pm AEST (when people planning trips)

---

## 🎉 Step 6: You're Live! (20 mins buffer)

### MVP Checklist

- ✅ Amadeus API working (finding deals)
- ✅ Twilio SMS working (sending alerts)
- ✅ Test SMS received on your phone
- ✅ First Instagram post created
- ✅ Database initialized (subscribers table)
- ✅ `.env` file configured

### Your MVP Tonight

**What you have**:
- ✅ Scanner that finds deals
- ✅ SMS alert system
- ✅ Manual Instagram workflow
- ✅ Database for subscribers

**What you don't have (yet)**:
- ❌ Automated scheduling
- ❌ Payment processing
- ❌ Instagram auto-posting
- ❌ Web dashboard

**That's okay!** You can:
1. Run scanner manually once per day
2. Review deals before sending
3. Send SMS automatically (script does it)
4. Post to Instagram manually
5. Add subscribers manually

---

## 📊 Day 1 Goals (Realistic)

### Tonight
- [ ] APIs configured
- [ ] First test SMS sent to yourself
- [ ] Database created
- [ ] First Instagram post scheduled for tomorrow

### Tomorrow
- [ ] Post first deal to Instagram
- [ ] Add "DM ALERTS" to bio
- [ ] Tell 5 friends about it
- [ ] Goal: 1 real subscriber by end of day

### Week 1
- [ ] Run scanner daily
- [ ] Post 2-3 deals to Instagram
- [ ] Get 5 SMS subscribers
- [ ] Revenue: $25/month

---

## 🐛 Troubleshooting

### Issue: "Amadeus API returns no results"

```bash
# Try a broader search
python -c "
from amadeus import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)

response = client.shopping.flight_destinations.get(
    origin='SYD',
    maxPrice=1000  # Increase limit
)

print(f'Found {len(response.data)} destinations')
for dest in response.data[:5]:
    print(f\"{dest['destination']}: ${dest['price']['total']}\")
"
```

### Issue: "Twilio SMS not sending"

**Check**:
1. Phone number includes country code (+61 for Australia)
2. Twilio trial account verified your number
3. Account SID/Auth Token are correct

**Test directly**:
```bash
python -c "
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

message = client.messages.create(
    body='Test from FareGlitch',
    from_=os.getenv('TWILIO_PHONE_NUMBER'),
    to=os.getenv('YOUR_PHONE_NUMBER')
)

print(f'Message sent: {message.sid}')
"
```

### Issue: "Database error"

```bash
# Reinitialize database
python -c "
from src.models.database import engine, Base
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print('Database recreated!')
"
```

---

## 💰 Revenue Timeline

### Week 1: $0
- Testing, learning, posting
- Goal: 5 Instagram followers

### Week 2: $25
- 5 SMS subscribers @ $5/mo
- Posted 5 deals

### Month 1: $100
- 20 SMS subscribers
- 500 Instagram followers
- Posted 20 deals

### Month 3: $500
- 100 SMS subscribers
- 5,000 Instagram followers
- Automated workflow

### Month 6: $1,000+
- 200 SMS subscribers
- 10,000 Instagram followers
- Considering full-time

---

## 📝 Quick Commands Reference

```bash
# Test Amadeus API
python test_mvp.py

# Initialize database
python -c "from src.models.database import init_db; init_db()"

# Add subscriber manually
python scripts/add_subscriber.py +61412345678 sms_monthly

# Check database
sqlite3 fareglitch.db "SELECT * FROM subscribers"

# Send test SMS
python -c "from src.utils.sms_alerts import SMSAlertManager; mgr = SMSAlertManager(); mgr.send_instant_alert('+61412345678', {'origin':'SYD','destination':'DPS','price':420})"
```

---

## 🎯 Success Criteria for Tonight

By the end of tonight, you should have:

1. ✅ Received a test SMS on your phone
2. ✅ Found at least 1 real deal from Sydney
3. ✅ Created Instagram account (if not already)
4. ✅ Scheduled your first post for tomorrow
5. ✅ Database set up with your first subscriber (you)

**Time to beat**: 2 hours  
**Minimum viable**: Test SMS received

---

## 🚀 Next Steps (Tomorrow)

1. **Morning**: Post your first deal to Instagram
2. **Afternoon**: Add "DM ALERTS to subscribe" to bio
3. **Evening**: Run scanner again, look for new deals
4. **Before bed**: Message 10 friends about your new project

**The goal**: Get your first PAYING subscriber within 7 days.

---

## 💡 Pro Tips

1. **Start with one city**: SYD only for first week
2. **Manual is fine**: Don't automate until you have 10 subscribers
3. **Quality over quantity**: Only send REAL deals
4. **Be transparent**: "This may not work, airline may cancel"
5. **Document everything**: What worked, what didn't
6. **Instagram is key**: It's your lead magnet, post daily

---

## ❓ FAQ

**Q: Do I need a website?**  
A: No! Use Instagram bio link to Stripe payment page.

**Q: How do I verify deals are real?**  
A: Search on Skyscanner/Google Flights. If you can find it, it's real.

**Q: What if subscriber doesn't pay?**  
A: Use Stripe payment links. Don't activate until paid.

**Q: How many deals per day?**  
A: Start with 1-2 per week. Quality > Quantity.

**Q: What if I can't find any deals?**  
A: Increase max_price to $1000, expand to more cities (MEL, BNE).

---

**NOW GO BUILD IT! 🚀**

You have everything you need. Stop reading, start coding.

**Timeline starts... NOW.**
