# SMS Alert Business Model - Implementation Guide

## 🎯 The Core Monetization Strategy

**Stop selling "unlocks". Start selling TIME.**

### The Exclusivity Window

```
ERROR FARE DETECTED
        ↓
[0 min]  SMS sent to PAYING subscribers ($5/month)
        ↓
[60 min] Posted to Instagram (FREE followers)
        ↓
[Result] Subscribers get 1-hour head start
```

**Value Proposition**: In error fare hunting, 1 hour = everything. Fares can be corrected in minutes.

## 💰 Revenue Model

### Tier 1: Free (Instagram Only)
- **Price**: $0
- **Delivery**: Instagram posts (1hr after SMS)
- **Purpose**: Build audience, drive conversions
- **Link**: "Link in bio" (friction)

### Tier 2: SMS Alerts (Recommended)
- **Price**: $5/month
- **Delivery**: Instant SMS when deal found
- **Value**: Direct booking link in SMS
- **Head Start**: 1 hour before Instagram

### Tier 3: Pay-Per-Alert
- **Price**: $2/alert
- **Delivery**: SMS for selected deals only
- **Use Case**: Casual users, regional filtering
- **Billing**: Charge after each alert sent

## 📱 The SMS Flow

### 1. Subscriber Signs Up

```
User: DMs "ALERTS" on Instagram
Bot:  "Reply with your phone number to get instant alerts"
User: "+61412345678"
Bot:  "Reply SYDNEY to get deals from Sydney"
User: "SYDNEY"
Bot:  "Great! $5/month. Reply PAY to subscribe"
User: "PAY"
Bot:  [Stripe payment link]
```

**Implementation**: Instagram DM bot + Stripe Checkout

### 2. Deal Detected

```python
# Scanner finds anomaly
anomaly = {
    "origin": "SYD",
    "destination": "LAX", 
    "normal_price": 800,
    "mistake_price": 200,
    "savings_pct": 75
}

# Validate it's real
is_valid = validator.validate_fare(anomaly)

if is_valid:
    # Get subscribers matching criteria
    subscribers = db.query(Subscriber).filter(
        Subscriber.is_active == True,
        Subscriber.regions.contains("north-america"),
        Subscriber.subscription_expires_at > datetime.now()
    ).all()
    
    # Send SMS immediately
    for sub in subscribers:
        sms.send_instant_alert(sub.phone_number, deal)
```

### 3. SMS Message Format

```
🚨 ERROR FARE ALERT
SYD→LAX
$200 (Normally $800)
SAVE 75%
BOOK NOW: fareglitch.com/d/001
⚠️ Expires in 48hrs
```

**Length**: <160 chars (single SMS segment)  
**Tone**: Urgent, actionable  
**Link**: Shortened URL with tracking  

### 4. Instagram Post (1hr later)

```python
import time
from datetime import datetime, timedelta

# Schedule post
post_time = datetime.now() + timedelta(hours=1)

# Wait
time.sleep(3600)  # 1 hour

# Post to Instagram
instagram.post(
    image=deal_image,
    caption=f"""
🚨 ERROR FARE ALERT

SYD → LAX
$200 (Save 75%)

⚠️ DEAL MAY BE GONE
Want alerts 1 HOUR BEFORE we post?
DM "ALERTS" to subscribe

#errorfare #cheapflights
"""
)
```

## 🔧 Technical Implementation

### Setup Twilio (SMS)

1. **Sign up**: https://www.twilio.com/try-twilio
2. **Get credentials**:
   - Account SID
   - Auth Token
   - Phone Number (+1234567890)
3. **Add to .env**:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Setup Stripe (Payments)

1. **Create product**: "SMS Alerts Subscription"
2. **Price**: $5/month recurring
3. **Webhook**: Listen for `invoice.paid` events
4. **On payment**:
   - Activate subscriber
   - Set expiry date (+30 days)

### Setup Instagram Bot (Lead Gen)

**Option A: Manual (MVP)**
- Monitor DMs manually
- Reply with payment link
- Add phone numbers to database

**Option B: Automated (Scale)**
- Instagram Graph API (requires business account)
- Bot responds to "ALERTS" keyword
- Collects phone + preferences
- Sends Stripe checkout link

### Database Schema

```sql
CREATE TABLE subscribers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    subscription_type VARCHAR(20),  -- 'sms_monthly' or 'pay_per_alert'
    is_active BOOLEAN DEFAULT true,
    subscribed_at TIMESTAMP DEFAULT NOW(),
    subscription_expires_at TIMESTAMP,
    regions TEXT,  -- JSON: ["asia", "north-america"]
    total_alerts_received INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE alert_logs (
    id SERIAL PRIMARY KEY,
    subscriber_id INTEGER REFERENCES subscribers(id),
    deal_id INTEGER REFERENCES deals(id),
    sent_at TIMESTAMP DEFAULT NOW(),
    twilio_message_sid VARCHAR(50),
    charged_amount DECIMAL(10,2),
    booking_link_clicked BOOLEAN DEFAULT false
);
```

## 📈 Growth Strategy

### Month 1: Manual MVP
- Instagram: 0 → 500 followers
- SMS Subscribers: 0 → 10
- Revenue: $50/month
- Process: Manual DMs, manual deal posting

### Month 2-3: Automation
- Instagram: 500 → 2,000 followers
- SMS Subscribers: 10 → 50
- Revenue: $250/month
- Process: Automated scanner, manual SMS approval

### Month 4-6: Scale
- Instagram: 2,000 → 10,000 followers
- SMS Subscribers: 50 → 200
- Revenue: $1,000/month
- Process: Full automation, Instagram bot

## 🎯 Key Metrics

Track these in your dashboard:

```python
# Conversion Rate (Instagram → SMS)
conversion_rate = sms_subscribers / instagram_followers

# Alert Value
avg_alert_value = total_revenue / total_alerts_sent

# Churn Rate
churn_rate = cancellations / total_subscribers

# Click-Through Rate
ctr = link_clicks / sms_sent
```

**Targets**:
- Conversion Rate: >2%
- Churn Rate: <10%/month
- CTR: >40%

## 💡 Optimization Tips

### Increase Conversions
1. **Instagram bio**: "Get deals 1hr before we post here → DM ALERTS"
2. **Stories**: Show example of SMS subscribers winning
3. **Proof**: "Sarah booked SYD→LAX for $200 via SMS alert"
4. **Urgency**: "Only 5 spots left at this price"

### Reduce Churn
1. **Quality over quantity**: Only send verified deals
2. **Regional filtering**: Don't spam with irrelevant routes
3. **Success stories**: "How many subscribers booked this?"
4. **Transparency**: "Airline may cancel. We'll notify immediately."

### Increase Revenue
1. **Upsell**: "Upgrade to PREMIUM for business class alerts"
2. **Annual plan**: "$50/year (save $10)"
3. **Referrals**: "Refer a friend, get 1 month free"
4. **Regions**: "Add Europe alerts for +$3/month"

## 🚨 The Instagram Strategy

### Post Structure

**Image**: Flight route map with price overlay  
**Hook**: "🚨 ERROR FARE ALERT"  
**Details**: Route, price, savings  
**CTA**: "DM ALERTS for 1hr head start"  
**Hashtags**: #errorfare #cheapflights #traveldeals  

### Post Frequency

- **Timing**: 1hr after SMS sent
- **Frequency**: As deals found (2-5x/week)
- **Stories**: Daily engagement content
- **Reels**: "How to book error fares" tutorials

### Growth Tactics

1. **Follow travel hashtags**: #cheapflights #travelhacks
2. **Comment on travel posts**: Add value, not spam
3. **Collaborate**: Partner with travel influencers
4. **Giveaway**: "Follow + DM ALERTS for chance to win"
5. **Testimonials**: Repost customer success stories

## ⚖️ Legal Compliance

### SMS Requirements (TCPA/GDPR)

✅ **Must have**: Explicit opt-in  
✅ **Must include**: "Reply STOP to unsubscribe"  
✅ **Must honor**: Opt-outs immediately  
✅ **Must not**: Send after 9pm local time  

### Example Opt-In Flow

```
User: "ALERTS"
Bot:  "By subscribing, you agree to receive SMS alerts 
       about flight deals. Reply STOP anytime to opt out.
       Msg & data rates may apply. $5/month."
User: "YES"
Bot:  "Great! [payment link]"
```

### Unsubscribe Handling

```python
# Twilio webhook for incoming SMS
@app.post("/sms/webhook")
def handle_incoming_sms(request):
    message = request.form['Body'].strip().upper()
    phone = request.form['From']
    
    if message == "STOP":
        subscriber = db.query(Subscriber).filter_by(
            phone_number=phone
        ).first()
        
        subscriber.is_active = False
        db.commit()
        
        return "You're unsubscribed. Sorry to see you go!"
```

## 🎓 Example: Complete Deal Flow

```python
# 1. Scanner detects anomaly
deal = scanner.find_anomalies()

# 2. Validate it's real
if validator.confirm(deal):
    
    # 3. Create deal record
    db_deal = Deal(
        origin="SYD",
        destination="LAX",
        mistake_price=200,
        booking_link="https://skyscanner.com/..."
    )
    db.add(db_deal)
    
    # 4. Send SMS to subscribers IMMEDIATELY
    subscribers = db.query(Subscriber).filter(
        Subscriber.is_active == True,
        Subscriber.subscription_expires_at > datetime.now()
    ).all()
    
    for sub in subscribers:
        sms_result = twilio.send(
            to=sub.phone_number,
            body=f"🚨 ERROR FARE\nSYD→LAX\n$200 (Save 75%)\n{deal.booking_link}"
        )
        
        # Log it
        log = AlertLog(
            subscriber_id=sub.id,
            deal_id=db_deal.id,
            twilio_message_sid=sms_result.sid
        )
        db.add(log)
    
    db.commit()
    
    # 5. Schedule Instagram post for 1hr later
    scheduler.add_job(
        post_to_instagram,
        'date',
        run_date=datetime.now() + timedelta(hours=1),
        args=[db_deal]
    )
```

---

## 🚀 Quick Start Checklist

- [ ] Set up Twilio account
- [ ] Configure Stripe subscriptions
- [ ] Create Instagram business account
- [ ] Add "DM ALERTS" to bio
- [ ] Test SMS sending locally
- [ ] Create first deal manually
- [ ] Send test SMS to yourself
- [ ] Post to Instagram 1hr later
- [ ] Monitor conversion rate
- [ ] Iterate on messaging

**The key**: You're not selling data. You're selling TIME. The 1-hour exclusivity window is your moat.
