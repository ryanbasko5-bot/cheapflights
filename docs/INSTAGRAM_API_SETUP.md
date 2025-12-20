# 📸 Instagram API Setup - COMPLETE GUIDE

**Goal**: Get your Instagram Access Token to auto-post deals

---

## ⚠️ IMPORTANT PREREQUISITES

Before you start, you MUST have:
1. ✅ **Instagram Business Account** (not personal!)
2. ✅ **Facebook Page** connected to your Instagram
3. ✅ **At least 1 post** on your Instagram account

If you don't have these, Instagram API won't work!

---

## 🔄 STEP 1: Convert to Business Account (5 mins)

### On Instagram Mobile App:
1. Open Instagram app
2. Go to **your profile**
3. Tap **☰ (hamburger menu)** → **Settings**
4. Tap **Account**
5. Scroll down → Tap **Switch to Professional Account**
6. Choose **Business**
7. **Connect to Facebook Page** (if you don't have one, create it first!)

**Screenshot location**: Settings → Account → Switch to Professional Account

---

## 📘 STEP 2: Create Facebook Page (if needed)

### If you don't have a Facebook Page:
1. Go to: https://www.facebook.com/pages/create
2. Choose **Business or Brand**
3. Name: "FareGlitch"
4. Category: "Travel & Transportation"
5. Create Page
6. **Link to Instagram**: Settings → Instagram → Connect Account

---

## 🔧 STEP 3: Create Facebook Developer App

### 3.1: Go to Facebook Developers
**URL**: https://developers.facebook.com

**Can't find it?** 
- If you see your normal Facebook, click your profile picture (top right)
- Scroll down → **"For Developers"** or go directly to URL above

### 3.2: Create an App
1. Click **"My Apps"** (top right)
2. Click **"Create App"** (green button)
3. **Select an app type**: Choose **"Business"** (NOT Consumer or Other)
4. Click **Next**
5. Fill in:
   - **App name**: FareGlitch
   - **App contact email**: your email
   - **Business Account**: (can skip)
6. Click **"Create App"**

### 3.3: Add Instagram Product
1. You're now on your app dashboard
2. Scroll down to **"Add products to your app"**
3. Find **"Instagram"** or **"Instagram Graph API"**
4. Click **"Set Up"** button

**Can't find Instagram?**
- Look for "Instagram Basic Display" - that's the wrong one
- You need "Instagram" or "Instagram Graph API"
- If you only see "Instagram Basic Display", your app type is wrong - start over and choose "Business"

---

## 🔑 STEP 4: Get Access Token

### 4.1: Go to Graph API Explorer
**URL**: https://developers.facebook.com/tools/explorer

### 4.2: Configure Explorer
1. Top right: Select **your app** from dropdown ("FareGlitch")
2. Next to it: Select **"User Token"** (not App Token)
3. Click **"Generate Access Token"** button

### 4.3: Add Permissions
1. Click **"Add a Permission"** or permissions icon
2. Search and enable:
   - ✅ `instagram_basic`
   - ✅ `instagram_content_publish` ⭐ **CRITICAL**
   - ✅ `pages_show_list`
   - ✅ `pages_read_engagement`
3. Click **"Generate Access Token"** again
4. **Log in** and **approve** all permissions

### 4.4: Copy Token
- You'll see a long token in the "Access Token" field
- Click **"Copy"** or select all and copy
- Format: `EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**This is your Instagram Access Token!**

---

## 🆔 STEP 5: Get Instagram Business Account ID

### 5.1: Get Your Facebook Page ID
In Graph API Explorer (same page):
1. Keep your token from Step 4
2. In the query field (right side), enter: `me/accounts`
3. Click **Submit**
4. Look for your page (FareGlitch)
5. Copy the **"id"** number (e.g., `123456789012345`)

### 5.2: Get Instagram Business Account ID
1. In the query field, enter: `YOUR_PAGE_ID?fields=instagram_business_account`
2. Replace `YOUR_PAGE_ID` with the number from 5.1
3. Click **Submit**
4. Copy the **instagram_business_account → id** number
5. Format: `17841401234567890`

**This is your Instagram Business Account ID!**

---

## ⚠️ Common Problems & Solutions

### Problem 1: "Can't find Instagram in products"
**Solution**: 
- Your app type is wrong
- Delete app and create new one
- Choose **"Business"** type (not Consumer)

### Problem 2: "No Instagram account found"
**Solution**:
- Your Instagram is not a Business account
- Go back to Step 1 and convert it
- Make sure it's connected to Facebook Page

### Problem 3: "Token doesn't work"
**Solution**:
- Token expires in 1-2 hours by default
- You need to generate a **Long-Lived Token** (60 days)
- Use this URL after getting your token:
```
https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN
```

### Problem 4: "Permission denied when posting"
**Solution**:
- Make sure you enabled `instagram_content_publish` permission
- Re-generate token after adding permission
- Some accounts need to complete "Business Verification" (Settings → Basic → Business Verification)

---

## ✅ FINAL CHECKLIST

You should have:
- [ ] Instagram Business Account (converted from personal)
- [ ] Facebook Page (connected to Instagram)
- [ ] Facebook Developer App (Business type)
- [ ] Access Token (starts with EAA...)
- [ ] Instagram Business Account ID (17 digits)

---

## 🚀 What to Send Me

Once you have these 2 things, send me:

1. **Access Token**: `EAAxxxxxxxxxxxxx...` (very long)
2. **Instagram Business Account ID**: `17841401234567890` (17 digits)

I'll add them to `.env` and test!

---

## 🎯 OR - Skip Instagram API for MVP!

**Too complicated?** You can launch tonight without Instagram API:

1. ✅ SMS alerts work (main product!)
2. ✅ Find deals automatically
3. ✅ Use Instagram caption generator
4. ✅ **Post manually** to Instagram (copy/paste caption)

**Manual posting takes 2 minutes** - totally fine for MVP!

**Add automation later** when you have 50+ subscribers.

---

## 📞 Quick Help URLs

- **Instagram Business Account**: https://help.instagram.com/502981923235522
- **Facebook Page Setup**: https://www.facebook.com/pages/create
- **Developer Console**: https://developers.facebook.com/apps
- **Graph API Explorer**: https://developers.facebook.com/tools/explorer
- **Documentation**: https://developers.facebook.com/docs/instagram-api

---

## 💡 My Recommendation

**For tonight's launch**: Skip Instagram API!

Just:
1. Run `python find_deals.py`
2. Copy the Instagram caption from output
3. Post manually to Instagram (takes 2 mins)
4. Focus on getting your first customer!

**Add automation in 1-2 weeks** when you have subscribers and need to scale.

Sound good?
