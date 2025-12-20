# In-App Purchase Setup Guide

## Overview
Your FareGlitch app now supports native in-app purchases through Apple App Store and Google Play Store.

## ⚠️ IMPORTANT: Product IDs
The subscription product ID is: `com.fareglitch.app.monthly`

You MUST create this exact product ID in both stores, or change it in `/services/subscriptionService.js`

---

## iOS Setup (App Store Connect)

### 1. Sign Agreements
1. Go to https://appstoreconnect.apple.com
2. Click **Agreements, Tax, and Banking**
3. Complete **Paid Apps Agreement** (required for in-app purchases)
4. Add banking info and tax forms

### 2. Create Subscription Product
1. Go to **My Apps** → Select FareGlitch
2. Click **Subscriptions** tab
3. Click **+** to create new subscription group
   - Name: "FareGlitch Premium"
4. Click **+** to create subscription
   - **Product ID**: `com.fareglitch.app.monthly` (MUST MATCH CODE)
   - **Reference Name**: "FareGlitch Monthly Premium"
   - **Subscription Duration**: 1 Month
5. Add pricing:
   - Base Price: $4.99 USD
   - Click **Set Starting Price**
6. Add App Store localization:
   - **Display Name**: "FareGlitch Premium"
   - **Description**: "Get unlimited flight deal alerts and save $200+ per booking"
7. **Save**

### 3. Add Free Trial (Optional)
1. In your subscription, click **Subscription Prices**
2. Click **Add Introductory Offer**
3. Select:
   - **Free Trial**
   - Duration: 7 days
4. **Save**

### 4. Submit for Review
- Subscription groups must be reviewed by Apple
- Add screenshots showing subscription benefits
- Usually approved within 24-48 hours

---

## Android Setup (Google Play Console)

### 1. Set Up Merchant Account
1. Go to https://play.google.com/console
2. Navigate to **Setup** → **Merchant account**
3. Link a Google Payments merchant account
4. Complete verification

### 2. Create Subscription Product
1. Go to your app → **Monetize** → **Subscriptions**
2. Click **Create subscription**
3. Fill in:
   - **Product ID**: `com.fareglitch.app.monthly` (MUST MATCH CODE)
   - **Name**: "FareGlitch Premium"
   - **Description**: "Get unlimited flight deal alerts and save $200+ per booking"
4. Set pricing:
   - **Price**: $4.99 USD
   - Google Play will auto-convert to local currencies
5. Set billing period:
   - **Period**: Monthly
   - **Renewal**: Recurring
6. Add free trial (optional):
   - **Free trial period**: 7 days
7. Click **Activate**

---

## Testing In-App Purchases

### iOS Testing (TestFlight)
1. Add test users in App Store Connect:
   - **Users and Access** → **Sandbox Testers**
   - Add email addresses
2. Build app with: `eas build --platform ios --profile preview`
3. Install on TestFlight
4. Sign in with sandbox tester account
5. Test subscription purchase (you won't be charged)

### Android Testing
1. Add test users in Google Play Console:
   - **Setup** → **License testing**
   - Add Gmail addresses
2. Build app with: `eas build --platform android --profile preview`
3. Install APK on device
4. Sign in with test Gmail account
5. Test subscription (test users aren't charged)

---

## How It Works in the App

### Profile Screen Features:
- Shows current subscription status (Free Trial / Premium)
- Displays localized price from App Store/Play Store
- "Start Free Trial" button → Opens native payment sheet
- "Restore Purchases" → Restores previous subscriptions
- Loading indicator during purchase
- Success/error alerts

### User Flow:
1. User taps "Start Free Trial"
2. Native payment sheet appears (Face ID/Touch ID on iOS)
3. User confirms purchase
4. App verifies receipt
5. Subscription activated ✓
6. Button changes to "Active Subscription ✓"

---

## Important Notes

### Revenue Split:
- **Apple**: Takes 30% first year, 15% after
- **Google**: Takes 15% always
- **Your $4.99 subscription**:
  - Apple: You get $3.49 (first year) → $4.24 (after year 1)
  - Google: You get $4.24

### Backend Verification (TODO):
The code includes a placeholder for server-side receipt verification:
```javascript
// await verifyPurchaseWithBackend(receipt);
```

You should:
1. Create an API endpoint to verify receipts
2. Store subscription status in your database
3. Sync with HubSpot contacts

### Stripe vs In-App Purchases:
- **Website**: Use Stripe (2.9% fee)
- **iOS App**: MUST use Apple IAP (30% fee)
- **Android App**: MUST use Google Play Billing (15% fee)
- This is Apple and Google's requirement - no exceptions!

---

## Troubleshooting

### "Subscription not available"
- Make sure product IDs match exactly
- Product must be approved in App Store Connect
- Android: Product must be "Active" in Play Console

### Purchases not restoring
- iOS: User must be signed in with same Apple ID
- Android: User must be signed in with same Google account

### Testing charges real money
- Make sure you're using sandbox testers (iOS) or license testers (Android)
- Never test with real accounts!

---

## Next Steps

1. ✅ Code is ready - in-app purchases integrated
2. ⏳ Create subscription products in App Store Connect
3. ⏳ Create subscription products in Google Play Console  
4. ⏳ Add test users for both platforms
5. ⏳ Build and test with preview builds
6. ⏳ Submit for review
7. ⏳ Build backend receipt verification (optional but recommended)

Once approved, users can subscribe directly in the app with Apple Pay, Google Pay, or credit cards! 🎉
