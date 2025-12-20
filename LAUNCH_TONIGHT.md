# 🚀 TONIGHT'S LAUNCH CHECKLIST

**Goal**: Send your first SMS alert in the next 2 hours!

---

## ✅ What's Already Done

- ✅ Amadeus API credentials configured
- ✅ Project code fully built
- ✅ SMS system switched to Sinch
- ✅ Test script ready
- ✅ Database models created

---

## 🎯 What You Need To Do (90 minutes)

### 1️⃣ Get Sinch Account (15 mins)

**Action**: Sign up at https://dashboard.sinch.com/signup

**Get These**:
- [ ] Service Plan ID
- [ ] API Token  
- [ ] Phone Number (buy one in your country)

**Guide**: See `/workspaces/cheapflights/docs/SINCH_SETUP.md`

---

### 2️⃣ Update .env File (5 mins)

**File**: `/workspaces/cheapflights/.env`

**Replace these lines**:
```env
SINCH_SERVICE_PLAN_ID=your_service_plan_id_here  # ← Paste your Service Plan ID
SINCH_API_TOKEN=your_api_token_here              # ← Paste your API Token
SINCH_PHONE_NUMBER=+1234567890                   # ← Your Sinch number

YOUR_PHONE_NUMBER=+61412345678                   # ← YOUR phone (to receive test SMS)
```

**Format**: Use international format (e.g., +61412345678, +14155551234)

---

### 3️⃣ Install Dependencies (10 mins)

```bash
cd /workspaces/cheapflights

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Verify installation
python3 -c "from clx.xms import Client; print('✅ Sinch SDK installed')"
python3 -c "from amadeus import Client; print('✅ Amadeus SDK installed')"
```

---

### 4️⃣ Test Amadeus API (10 mins)

**Quick test**:
```bash
python3 -c "
from amadeus import Client
import os
from dotenv import load_dotenv

load_dotenv()

amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY'),
    client_secret=os.getenv('AMADEUS_API_SECRET')
)

# Find cheap destinations from Sydney
response = amadeus.shopping.flight_destinations.get(
    origin='SYD',
    maxPrice=800
)

print(f'✅ Found {len(response.data)} destinations!')
print(f'Cheapest: {response.data[0][\"destination\"]} for ${response.data[0][\"price\"][\"total\"]}')
"
```

**Expected output**:
```
✅ Found 47 destinations!
Cheapest: DPS for $456
```

---

### 5️⃣ Test Sinch SMS (10 mins)

**Quick test**:
```bash
python3 -c "
from clx.xms import Client
import os
from dotenv import load_dotenv

load_dotenv()

sinch = Client(
    service_plan_id=os.getenv('SINCH_SERVICE_PLAN_ID'),
    token=os.getenv('SINCH_API_TOKEN')
)

# Send test SMS to yourself
result = sinch.create_batch_mt(
    sender=os.getenv('SINCH_PHONE_NUMBER'),
    recipients=[os.getenv('YOUR_PHONE_NUMBER')],
    body='🚨 TEST: Your FareGlitch SMS alerts are working!'
)

print(f'✅ SMS sent! Batch ID: {result.batch_id}')
print(f'Check your phone: {os.getenv(\"YOUR_PHONE_NUMBER\")}')
"
```

**Expected**: You should receive an SMS within 10 seconds!

---

### 6️⃣ Run Full MVP Test (15 mins)

**This will**:
1. Search for real flight deals
2. Find the cheapest one
3. Send you an SMS alert
4. Show Instagram post preview

```bash
python3 test_mvp.py
```

**Expected output**:
```
✅ Amadeus client initialized
✅ Sinch client initialized

🔍 Searching for deals from SYD under $800...
✅ Found: SYD → DPS for $456

📱 Sending SMS to +61412345678...
Message preview:
----------------------------------------
🚨 FARE ALERT
SYD→DPS
$456
Depart: 2025-12-15
Book: fareglitch.com
----------------------------------------
Length: 67 chars

✅ SMS Sent!
   Batch ID: 01abc123-def4-5678-90ab-cdef12345678
   Status: Queued for delivery

==================================================
📸 INSTAGRAM POST (Post this 1 hour after SMS)
==================================================

🚨 ERROR FARE ALERT

SYD → DPS
$456

Want alerts 1 HOUR BEFORE we post?
DM "ALERTS" to subscribe

#errorfare #cheapflights
```

**Check your phone** - you should have received the SMS!

---

### 7️⃣ Post to Instagram (20 mins)

**Manual MVP Version**:

1. **Create Instagram Business Account** (if you don't have one)
   - Go to instagram.com
   - Click "Switch to Professional Account"
   - Choose "Business"

2. **Create Post Template** using Canva (free):
   - Go to canva.com
   - Search "Instagram Post"
   - Design: Flight route map + price overlay
   - Example: https://www.canva.com/templates/instagram-posts/

3. **Post Your First Deal**:
   - Use the caption from test_mvp.py output
   - Add image from Canva
   - Add to bio: "DM ALERTS for instant notifications"

---

## 🎉 You're Live!

### What You Can Do Now

✅ **Manually find deals**: Run `python3 test_mvp.py` whenever you want  
✅ **Send SMS alerts**: You have working SMS system  
✅ **Post to Instagram**: Manual for now, automate later  

### Next Steps (Tomorrow+)

- [ ] Set up Stripe for subscription payments
- [ ] Create Instagram DM bot for signups
- [ ] Automate scanner to run every hour
- [ ] Add database logging for subscribers
- [ ] Build subscriber management dashboard

---

## 🆘 Troubleshooting

### "Amadeus API error"
**Fix**: Check your API key in .env file. Make sure there are no spaces.

### "Sinch client failed"
**Fix**: 
1. Check Service Plan ID and API Token
2. Make sure you copied them correctly from dashboard
3. No extra spaces in .env file

### "SMS not received"
**Check**:
1. Phone number format: Must be +COUNTRYCODE + number (e.g., +61412345678)
2. Sinch dashboard logs: https://dashboard.sinch.com → SMS → Logs
3. Wait 30 seconds - international SMS can be slow

### "No deals found"
**Try**:
- Different origin: `python3 test_mvp.py --origin LAX`
- Higher max price: Change `max_price=800` to `max_price=1500` in test_mvp.py

---

## 📊 Today's Success Metrics

By the end of tonight, you should have:

- [x] Amadeus API working ✅ (already done!)
- [ ] Sinch account set up
- [ ] SMS alerts working (received test SMS)
- [ ] Found at least 1 real deal
- [ ] Posted 1 deal to Instagram

**Time Investment**: ~90 minutes  
**Result**: Working MVP that can make money tomorrow!

---

## 💰 Revenue Reality Check

**Scenario**: 10 SMS subscribers @ $5/month

**Revenue**: $50/month  
**SMS Costs**: ~$5/month (100 SMS @ $0.05 each)  
**Profit**: $45/month

**That's $540/year** from just 10 people!

Get 100 subscribers = $5,400/year  
Get 1,000 subscribers = $54,000/year

---

## 🚀 Ready?

```bash
# Step 1: Check Amadeus (should already work)
python3 -c "from amadeus import Client; print('Ready!')"

# Step 2: Get Sinch credentials
# Go to: https://dashboard.sinch.com/signup

# Step 3: Update .env file

# Step 4: Test everything
python3 test_mvp.py

# Step 5: Post to Instagram

# Step 6: You're live! 🎉
```

**Let's go make money! 💸**
