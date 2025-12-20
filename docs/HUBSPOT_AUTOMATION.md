# 🌐 HUBSPOT WEBSITE + AUTOMATION SETUP

## 🎯 The Complete Flow

```
DEAL FOUND
    ↓
[0 min]  SMS to subscribers (INSTANT) ← You're here
    ↓
[60 min] Auto-post to HubSpot website
    ↓
[60 min] Auto-post to Instagram
```

---

## 📋 PART 1: HubSpot Website Setup (20 mins)

### Step 1: Create HubSpot Account
1. Go to: https://app.hubspot.com/signup-hubspot/crm
2. Sign up (Free CRM forever)
3. Skip onboarding

### Step 2: Create "Deals" Page

1. **Navigate**: Marketing → Website → Website Pages
2. **Create**: Blog post template
3. **Title**: "Flight Deals"
4. **URL**: `yourdomain.com/deals`

**Template Structure**:
```html
<!-- Deal Card Template -->
<div class="deal-card">
  <h2>🚨 {ORIGIN} → {DESTINATION}</h2>
  <div class="price">${PRICE} {CURRENCY}</div>
  <p>Departure: {DATE}</p>
  <p>Airline: {AIRLINE}</p>
  <a href="{BOOKING_LINK}" class="btn">Book Now</a>
</div>
```

### Step 3: Get HubSpot API Key

1. **Go to**: Settings (gear icon) → Integrations → API Key
2. **Create key**
3. **Copy**: `pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## 📋 PART 2: Instagram API Setup (30 mins)

### Step 1: Convert to Business Account
1. Instagram → Settings → Account
2. Switch to Professional Account
3. Choose "Business"
4. Connect to Facebook Page (required)

### Step 2: Get Facebook App Access Token

1. Go to: https://developers.facebook.com/apps
2. Create App → "Business"
3. Add Instagram API
4. Get Access Token (Settings → Basic)

### Step 3: Get Instagram Business Account ID

```bash
curl "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_ACCESS_TOKEN"
```

---

## 🔧 PART 3: Automated Workflow

I'll create a complete automation script that:
1. ✅ Converts prices to recipient's local currency
2. ✅ Sends SMS instantly to subscribers
3. ✅ Waits 1 hour
4. ✅ Auto-posts to HubSpot website
5. ✅ Auto-posts to Instagram

### Currency Conversion

We'll use your recipient's phone number country code to determine currency:
- `+61` (Australia) → AUD
- `+1` (US/Canada) → USD
- `+44` (UK) → GBP
- `+65` (Singapore) → SGD
- etc.

---

## 🚀 QUICK START

### Get Your API Keys:

1. **HubSpot API Key**: 
   - Settings → Integrations → API Key
   - Format: `pat-na1-xxxxx`

2. **Instagram Access Token**:
   - https://developers.facebook.com/tools/explorer
   - Permissions: `instagram_basic`, `instagram_content_publish`

3. **Instagram Business Account ID**:
   - Run: `curl "https://graph.facebook.com/v18.0/me/accounts?access_token=TOKEN"`

4. **Currency API** (Free):
   - https://exchangerate-api.com (free tier: 1500 requests/month)
   - No signup needed for basic use!

---

## ✅ WHAT TO SEND ME

Once you have:
- [ ] HubSpot API Key
- [ ] Instagram Access Token  
- [ ] Instagram Business Account ID

I'll update the automation script to:
1. Send SMS with prices in recipient's currency
2. Auto-post to HubSpot after 1 hour
3. Auto-post to Instagram after 1 hour
4. Handle everything automatically!

---

## 💡 FOR NOW (Manual MVP)

Until APIs are set up, here's the manual flow:

**When you find a deal:**
```bash
# 1. Send SMS (instant)
python find_deals.py

# 2. Wait 1 hour, then manually:
#    - Copy Instagram caption from output
#    - Post to Instagram
#    - Add to HubSpot website
```

**Next time I'll make it 100% automated!**
