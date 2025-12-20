# 🎯 START HERE - Your 2-Hour MVP

**Current time**: Get your phone ready, we're going live tonight!

---

## ⚡ Quick Start (Copy/Paste Each Step)

### Step 1: Get API Keys (20 mins)

Open these links in new tabs:

1. **Amadeus** (Flight Data): https://developers.amadeus.com/register
   - Sign up → Create App → Copy API Key + Secret

2. **Twilio** (SMS): https://www.twilio.com/try-twilio
   - Sign up → Get a Phone Number → Copy Account SID + Auth Token

### Step 2: Configure Environment (5 mins)

```bash
# Copy template
cp .env.example .env

# Edit the file
nano .env
```

**Paste your API keys**:
```env
# Amadeus (from step 1)
AMADEUS_API_KEY=YOUR_KEY_HERE
AMADEUS_API_SECRET=YOUR_SECRET_HERE

# Twilio (from step 1)
TWILIO_ACCOUNT_SID=ACxxxxxxxxx
TWILIO_AUTH_TOKEN=YOUR_TOKEN_HERE
TWILIO_PHONE_NUMBER=+1234567890

# Your phone (to receive test SMS)
YOUR_PHONE_NUMBER=+61412345678  # Your actual number!

# Database (use SQLite for now)
DATABASE_URL=sqlite:///./fareglitch.db
```

**Save**: `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Install Dependencies (5 mins)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Check Setup (2 mins)

```bash
python check_setup.py
```

**Expected output**:
```
✅ Amadeus API Key configured
✅ Amadeus API Secret configured
✅ Twilio Account SID configured
✅ Twilio Auth Token configured
✅ Twilio Phone Number configured
✅ Your test phone configured

🎉 ALL CHECKS PASSED!
```

If you see ❌, fix those items in your `.env` file.

### Step 5: Send Your First SMS! (5 mins)

```bash
python test_mvp.py
```

**What happens**:
1. Finds cheapest flight from Sydney
2. Sends SMS to your phone
3. Shows Instagram post template

**Check your phone** - SMS should arrive in 10-30 seconds!

### Step 6: Add Yourself as Subscriber (2 mins)

```bash
python scripts/add_subscriber.py +61412345678 sms_monthly
```

Replace `+61412345678` with your actual phone number.

### Step 7: Create Instagram Account (10 mins)

If you don't have one yet:

1. Download Instagram app
2. Create account: `@fareglitch` (or your preferred name)
3. Bio: "🚨 Mistake fare alerts | DM 'ALERTS' for 1hr early access | $5/mo"
4. Profile pic: Use Canva to make a simple logo

### Step 8: Post Your First Deal (20 mins)

Wait for `test_mvp.py` to show you the Instagram template, then:

1. Go to **Canva.com** (free)
2. Search "Instagram Post Travel"
3. Pick a template
4. Edit with your deal details
5. Download image
6. Post to Instagram with the caption from `test_mvp.py`

---

## ✅ Success Checklist

By end of tonight, you should have:

- [x] Received test SMS on your phone
- [x] Created Instagram account
- [x] Posted first deal
- [x] Added yourself as first subscriber
- [x] Sent message to 5 friends about your new project

---

## 📊 Your First Week Schedule

### Day 1 (Tonight)
- ✅ Complete setup
- ✅ Send test SMS
- ✅ Create Instagram

### Day 2
- Run `python test_mvp.py` in morning
- Post deal to Instagram
- Tell 10 friends

### Day 3-7
- Run scanner daily (same time each day)
- Post 2-3 deals to Instagram
- Goal: Get 1 paying subscriber by Sunday

---

## 💰 Getting Your First Paying Subscriber

### The Process

1. **Someone DMs you "ALERTS"** on Instagram

2. **Reply**:
   ```
   Hey! 🚨 SMS alerts are $5/month.
   
   You'll get deals 1 HOUR before I post them here.
   
   Pay here: [Your Stripe/PayPal link]
   
   Then reply with your phone number!
   ```

3. **Create Stripe payment link**:
   - Go to: https://dashboard.stripe.com/payment-links
   - Create product: "SMS Alerts - $5/month"
   - Copy link

4. **When they pay**:
   ```bash
   python scripts/add_subscriber.py +61412345678 sms_monthly
   ```

5. **Test it works**:
   ```bash
   python test_mvp.py
   ```
   They should receive the SMS!

---

## 🚨 Common Issues

### "No deals found"

**Solution**: Increase max price
```python
# Edit test_mvp.py, line 64:
deal = find_one_deal(origin='SYD', max_price=1000)  # Was 800
```

### "SMS not sending"

**Checks**:
1. Twilio trial account verified your phone?
2. Phone number has `+` country code?
3. Twilio account has credit?

**Test directly**:
```bash
# In Twilio console, send test SMS manually
https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms
```

### "Amadeus API error"

**Check quota**:
- Test account: 10,000 calls/month
- That's ~300 calls/day
- Each `test_mvp.py` run = 1 call

**View usage**: https://developers.amadeus.com/my-apps

---

## 🎯 Tomorrow's Tasks

1. **Morning**: Run scanner, find new deal
2. **Post to Instagram**: Use yesterday's template
3. **Engage**: Comment on travel hashtags
4. **Message friends**: "Check out my new project!"
5. **Goal**: Get first subscriber to pay

---

## 💡 Pro Tips

### Posting to Instagram

**Best times** (AEST):
- 7-9am (commute browsing)
- 12-1pm (lunch break)
- 6-8pm (evening planning)

**Best hashtags**:
```
#cheapflights #errorfare #traveldeals 
#sydneytravel #australiatravel #travelhacks
#budgettravel #wanderlust #travelgram
```

**Post frequency**: 
- Week 1: 3-5 posts (build content)
- Week 2+: Daily (when you have workflow)

### Growing Instagram

1. **Follow travel accounts**: 50/day in your niche
2. **Comment genuinely**: "Great tip!" on travel posts
3. **Use Stories**: Show your process, "Found this deal today!"
4. **Reels**: "How I find $200 flights" (after you have 10+ deals)

### Finding More Deals

Try different cities:
```python
# In test_mvp.py
deal = find_one_deal(origin='MEL', max_price=1000)  # Melbourne
deal = find_one_deal(origin='BNE', max_price=1000)  # Brisbane
deal = find_one_deal(origin='PER', max_price=1500)  # Perth
```

Try international:
```python
deal = find_one_deal(origin='LAX', max_price=500)  # Los Angeles
deal = find_one_deal(origin='LHR', max_price=300)  # London
```

---

## 📱 Commands Quick Reference

```bash
# Check setup
python check_setup.py

# Find deal and send SMS
python test_mvp.py

# Add subscriber
python scripts/add_subscriber.py +61412345678 sms_monthly

# List all subscribers
python scripts/add_subscriber.py --list

# Initialize database
python -c "from src.models.database import init_db; init_db()"
```

---

## 🚀 Ready to Launch?

### Pre-flight Checklist

- [ ] `.env` file configured with real API keys
- [ ] `python check_setup.py` passes all checks
- [ ] Received test SMS on your phone
- [ ] Instagram account created
- [ ] Stripe payment link created
- [ ] Told 3 friends about your project

### 🎉 If all checked, you're LIVE!

**Your first goal**: Get 1 paying subscriber within 7 days.

**Timeline**:
- Week 1: 1 subscriber ($5/mo)
- Week 2: 5 subscribers ($25/mo)  
- Month 1: 20 subscribers ($100/mo)
- Month 3: 100 subscribers ($500/mo)

---

## ❓ Need Help?

**Documentation**:
- Full setup: `docs/SETUP_GUIDE.md`
- Business model: `docs/SMS_BUSINESS_MODEL.md`
- API details: `docs/API.md`

**Quick fixes**:
- Can't find deals? Increase max_price
- SMS not sending? Check Twilio console
- API errors? Check quota at Amadeus console

---

## 🎓 What You've Built

You now have:
- ✅ Scanner that finds flight deals (Amadeus)
- ✅ SMS alert system (Twilio)
- ✅ Subscriber database
- ✅ Instagram growth plan
- ✅ $5/month recurring revenue model

**This is enough to get your first 10 subscribers.**

Don't overthink it. Post deals. Get subscribers. Make money.

---

**NOW GO LAUNCH! ⚡**

Stop reading. Start executing.

Your first SMS alert awaits:
```bash
python test_mvp.py
```
