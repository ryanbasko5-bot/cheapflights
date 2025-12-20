# 🔑 How to Find Your HubSpot API Key

## Method 1: Private App Access Token (Recommended - New HubSpot)

### Step 1: Go to Settings
1. Log in to HubSpot: https://app.hubspot.com
2. Click the **settings gear icon** (top right)

### Step 2: Create Private App
1. In left sidebar, go to: **Integrations** → **Private Apps**
2. Click: **"Create a private app"**
3. Fill in:
   - **Name**: FareGlitch API
   - **Description**: Automated deal posting
4. Click the **"Scopes"** tab
5. Enable these permissions:
   - ✅ `content` (read & write)
   - ✅ `crm.objects.contacts` (read & write)
   
6. Click **"Create app"**
7. Copy the **Access Token** (starts with `pat-na1-` or `pat-eu1-`)

**This is your API key!**

Format: `pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## Method 2: Legacy API Key (Older HubSpot Accounts)

### Step 1: Go to Integrations
1. Log in: https://app.hubspot.com
2. Click **settings gear icon** (top right)
3. In left sidebar: **Integrations** → **API Key**

### Step 2: Generate Key
1. If you see "Generate New Key", click it
2. If you see an existing key, click "Show"
3. Copy the key

**Note**: If you don't see "API Key" option, use Method 1 (Private Apps)

---

## Method 3: Can't Find It? Use Manual Posting (Works Now!)

### HubSpot isn't required for MVP!

You can post deals manually to HubSpot website:

1. **Log in**: https://app.hubspot.com
2. **Go to**: Marketing → Website → Blog
3. **Click**: "Create blog post"
4. **Use this template**:

```
Title: 🚨 SYD → BKK for $360

Content:
------------------
🚨 ERROR FARE ALERT

Sydney → Bangkok
$360 AUD (Normally $600+)

📅 Departure: Dec 28, 2025
✈️ Airline: Batik Air
🛫 Stops: 1 stop

⚠️ This deal may be gone soon! Airlines can correct pricing errors within 24-48 hours.

[Book Now Button] → Link to Skyscanner/Kayak

📱 Want these alerts 1 HOUR before we post them?
Subscribe to SMS alerts: [Your Stripe link]
------------------
```

5. **Publish!**

Takes 2 minutes per deal.

---

## 🎯 Quick Decision Tree

**Do you have HubSpot Marketing Hub (Paid)?**
- YES → Use Method 1 (Private Apps)
- NO → Use Method 2 (Legacy API Key) or just post manually

**Can't find API settings?**
- Your account might not have API access
- **Solution**: Post manually (totally fine for MVP!)
- **Or**: Skip HubSpot and just use Instagram

**Want to skip HubSpot entirely?**
- Totally fine! Focus on Instagram
- HubSpot is optional for MVP
- Most subscribers come from Instagram anyway

---

## ✅ For Tonight: Skip HubSpot!

You don't need HubSpot API for MVP. Just:

1. ✅ Send SMS (working!)
2. ✅ Post to Instagram (use caption generator)
3. ⏰ Add HubSpot later when you have 50+ subscribers

**Focus on Instagram → That's where customers come from!**

---

## 🚀 Your Current Status

What's working **right now** without any HubSpot setup:
- ✅ Amadeus finding deals
- ✅ Twilio sending SMS (with local currency!)
- ✅ Currency conversion
- ✅ Instagram caption generator

**You can launch tonight without HubSpot!**

Want to skip it for now and just focus on Instagram?
