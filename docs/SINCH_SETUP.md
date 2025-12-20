# Sinch SMS Setup Guide

**Why Sinch?** Reliable, global SMS delivery with competitive pricing and excellent API.

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Sinch Account

1. Go to: https://dashboard.sinch.com/signup
2. Sign up with email (free trial available)
3. Verify your email

### Step 2: Get Your Credentials

1. Log in to https://dashboard.sinch.com
2. Click **"SMS"** in the left sidebar
3. Click **"APIs"** tab
4. You'll see:
   - **Service Plan ID**: e.g., `abc123def456`
   - **API Token**: Click "Show" to reveal

### Step 3: Get a Phone Number

1. In the Sinch dashboard, go to **"Numbers"**
2. Click **"Buy Number"**
3. Select your country (Australia, US, etc.)
4. Choose a phone number
5. Complete purchase (some countries offer free trial numbers)

### Step 4: Add to .env File

```env
# Sinch SMS Configuration
SINCH_SERVICE_PLAN_ID=your_service_plan_id_here
SINCH_API_TOKEN=your_api_token_here
SINCH_PHONE_NUMBER=+61412345678  # Your purchased number
```

---

## 💰 Pricing

**Trial Account**:
- Free credits to test SMS
- Usually $2-5 USD in free credit
- Perfect for MVP testing

**Pay-As-You-Go**:
- **Australia**: ~$0.07 USD per SMS
- **USA/Canada**: ~$0.01 USD per SMS
- **Europe**: ~$0.05 USD per SMS
- **Asia**: ~$0.03-0.08 USD per SMS

**Your Economics**:
- You charge: $5/month subscription
- Cost per SMS: ~$0.05
- If you send 10 alerts/month: Profit = $4.50
- Break-even: 1 SMS per subscriber

---

## 🧪 Testing Your Setup

### Test 1: Verify Credentials

```bash
cd /workspaces/cheapflights
python3 -c "
from clx.xms import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    service_plan_id=os.getenv('SINCH_SERVICE_PLAN_ID'),
    token=os.getenv('SINCH_API_TOKEN')
)
print('✅ Sinch client initialized successfully!')
"
```

### Test 2: Send Test SMS

```bash
# Run the MVP test script
python3 test_mvp.py
```

Expected output:
```
✅ Amadeus client initialized
✅ Sinch client initialized

🔍 Searching for deals from SYD under $800...
✅ Found: SYD → DPS for $456

📱 Sending SMS to +61412345678...
✅ SMS Sent!
   Batch ID: 01abc123-def4-5678-90ab-cdef12345678
   Status: Queued for delivery
```

---

## 📱 SMS Format Best Practices

### Keep it Under 160 Characters

**Why?** 
- 1 SMS segment = 160 chars = cheapest
- 161+ chars = 2 segments = 2x cost

**Your Format** (148 chars):
```
🚨 FARE ALERT
SYD→LAX
$200
Depart: 2025-12-15
Book: fareglitch.com
```

### Include These Elements

✅ **Urgency**: 🚨 emoji, "ALERT"  
✅ **Value**: Show the price immediately  
✅ **Action**: Direct booking link  
✅ **Deadline**: Create FOMO ("Expires in 48hrs")

### Avoid These

❌ Long explanations  
❌ Multiple links  
❌ Fancy formatting (may break)  
❌ Special characters that don't render

---

## 🔒 Compliance (IMPORTANT!)

### You MUST Include

1. **Opt-in consent**: User must explicitly agree to receive SMS
2. **Opt-out option**: Every SMS should allow "Reply STOP to unsubscribe"
3. **Frequency**: Tell users how often they'll receive messages
4. **Cost disclosure**: "Msg & data rates may apply"

### Example Opt-In Flow

**User**: DMs "ALERTS" on Instagram

**You**: 
```
By replying YES, you agree to receive SMS alerts 
about flight deals. Reply STOP anytime to opt out. 
Msg & data rates may apply. $5/month subscription.
```

**User**: YES

**You**: 
```
✅ Welcome! You'll now receive instant SMS alerts 
when we find error fares. First alert coming soon!
```

### Handle STOP Requests

Sinch automatically handles STOP/UNSUBSCRIBE keywords, but you should also:

```python
# In your SMS webhook handler
@app.post("/sms/webhook")
def handle_incoming_sms(request):
    message = request.body.get('message', '').upper()
    phone = request.body.get('from')
    
    if message in ['STOP', 'UNSUBSCRIBE', 'CANCEL']:
        # Deactivate subscriber in database
        db.query(Subscriber).filter_by(
            phone_number=phone
        ).update({'is_active': False})
        db.commit()
        
        return {
            "message": "You're unsubscribed. Sorry to see you go!"
        }
```

---

## 🌍 International SMS

### Phone Number Format (E.164)

Always use international format with country code:

✅ **Correct**:
- Australia: `+61412345678`
- USA: `+14155551234`
- UK: `+447911123456`

❌ **Wrong**:
- `0412 345 678` (missing country code)
- `61412345678` (missing +)
- `+61 412 345 678` (spaces - may work but avoid)

### Regional Considerations

| Region | Cost | Delivery Time | Notes |
|--------|------|---------------|-------|
| **Australia** | $0.07/SMS | Instant | High delivery rate |
| **USA/Canada** | $0.01/SMS | Instant | Very cheap, reliable |
| **Europe** | $0.05/SMS | 1-2 sec | May need local sender ID |
| **Asia** | $0.03-0.08 | 1-5 sec | Varies by country |

---

## 🔧 Troubleshooting

### Error: "Invalid credentials"

**Fix**: Double-check your `.env` file:
```bash
# Print your credentials (be careful - don't commit this!)
cat .env | grep SINCH
```

Make sure:
- Service Plan ID is correct
- API Token has no extra spaces
- You're using the correct token (not your password)

### Error: "Invalid phone number"

**Fix**: Use E.164 format
```python
# ❌ Wrong
phone = "0412345678"

# ✅ Correct
phone = "+61412345678"
```

### SMS Not Delivered

Check Sinch logs:
1. Go to https://dashboard.sinch.com
2. Click **"SMS" → "Logs"**
3. Check delivery status:
   - **Queued**: SMS sent, waiting for delivery
   - **Delivered**: Success!
   - **Failed**: Check error message

Common causes:
- Phone number blocked you
- Invalid phone number
- Carrier issue (retry later)
- Insufficient credits

### Rate Limits

**Sinch Limits**:
- Default: 10 SMS/second
- Increase limit by contacting support

**Your Usage**:
- 100 subscribers = 100 SMS/batch
- At 10/sec = 10 seconds to send all
- For most MVPs, this is fine

---

## 📊 Monitoring & Analytics

### Track These Metrics

```python
# In your database
CREATE TABLE sms_logs (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER,
    batch_id VARCHAR(100),  -- Sinch batch ID
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    status VARCHAR(20),  -- queued, delivered, failed
    cost DECIMAL(10,4),  -- Track your costs
    clicked BOOLEAN  -- Did they click the link?
);
```

### Dashboard Metrics

- **Delivery Rate**: `delivered / sent`
- **Cost per SMS**: `total_cost / total_sent`
- **ROI**: `(revenue - sms_costs) / sms_costs`
- **Click Rate**: `clicks / delivered`

---

## 🚀 Production Checklist

Before launching to real users:

- [ ] Verified account with Sinch (remove trial limits)
- [ ] Purchased phone number in target country
- [ ] Added opt-in flow to Instagram bot
- [ ] Implemented STOP handling
- [ ] Set up SMS logging in database
- [ ] Tested SMS delivery to yourself
- [ ] Checked cost per SMS in target regions
- [ ] Set up Stripe for subscription payments
- [ ] Created webhook for incoming SMS
- [ ] Added monitoring for failed deliveries

---

## 💡 Pro Tips

### 1. Use Link Shorteners

**Instead of**: `https://www.fareglitch.com/deals/001`  
**Use**: `fareglitch.com/d/001`

Saves characters + looks cleaner

### 2. Schedule Carefully

**Avoid**:
- After 9pm local time (annoying)
- Before 7am local time (annoying)

**Best times**:
- 9am-12pm (morning coffee)
- 1pm-4pm (afternoon break)

### 3. A/B Test Messages

Try different formats:

**Version A**: Emoji-heavy
```
🚨✈️ ALERT
SYD→LAX $200
👉 fareglitch.com/d/001
```

**Version B**: Text-only
```
FARE ALERT
SYD to LAX: $200
Book: fareglitch.com/d/001
```

Track click rates and use the winner.

### 4. Personalize When Possible

```python
# Generic (boring)
message = f"🚨 FARE ALERT\nSYD→LAX\n$200"

# Personalized (better)
message = f"Hi {subscriber.first_name}! 🚨\nYour alert: SYD→LAX\n$200"
```

Personalization can increase click rates by 20-30%.

---

## 🆘 Support

**Sinch Documentation**: https://developers.sinch.com/docs/sms/  
**Sinch Support**: https://dashboard.sinch.com/support  
**Python SDK Docs**: https://github.com/sinch/sinch-python-sdk

**Your MVP Issues**: Check `/workspaces/cheapflights/test_mvp.py` for debugging

---

**You're all set!** 🎉

Run `python3 test_mvp.py` to send your first SMS alert and launch your MVP tonight!
