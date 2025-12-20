# 📱 iOS & ANDROID APP DEPLOYMENT GUIDE

## Current App Status: ✅ Code Complete, ⚠️ Not Built/Published

Your React Native Expo app is ready but needs building and publishing.

---

## 🚀 OPTION 1: Expo Go (Testing Only)

**Good for:** Development testing
**Cost:** Free
**Time:** 5 minutes

### Steps:
```bash
cd FareGlitchApp
npm install
npx expo start
```

Scan QR code with Expo Go app on your phone.

**⚠️ Limitation:** Not a standalone app, requires Expo Go installed.

---

## 📦 OPTION 2: EAS Build (Production Builds)

**Good for:** TestFlight/Internal testing
**Cost:** Free (with limitations)
**Time:** 30 minutes

### Setup EAS Build:
```bash
cd FareGlitchApp

# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure EAS
eas build:configure

# Build for iOS
eas build --platform ios --profile preview

# Build for Android
eas build --platform android --profile preview
```

This creates installable `.ipa` (iOS) and `.apk` (Android) files.

### Install on Device:
- **iOS:** Upload to TestFlight
- **Android:** Download APK directly to device

---

## 🏪 OPTION 3: App Store & Google Play (Full Launch)

### iOS App Store ($99/year)

1. **Join Apple Developer Program**
   - Go to https://developer.apple.com/programs/
   - Cost: $99/year
   - Approval: 1-2 days

2. **Update app.json:**
   ```json
   {
     "expo": {
       "name": "FareGlitch",
       "slug": "fareglitch",
       "ios": {
         "bundleIdentifier": "com.fareglitch.app",
         "buildNumber": "1.0.0",
         "supportsTablet": true
       }
     }
   }
   ```

3. **Create App Store Connect Entry:**
   - Go to https://appstoreconnect.apple.com/
   - Create new app
   - Fill in metadata, screenshots, description

4. **Build & Submit:**
   ```bash
   eas build --platform ios --profile production
   eas submit --platform ios
   ```

5. **Review:** Apple reviews in 1-3 days

### Android Google Play ($25 one-time)

1. **Create Google Play Developer Account**
   - Go to https://play.google.com/console/signup
   - One-time fee: $25

2. **Update app.json:**
   ```json
   {
     "expo": {
       "android": {
         "package": "com.fareglitch.app",
         "versionCode": 1,
         "adaptiveIcon": {
           "foregroundImage": "./assets/adaptive-icon.png",
           "backgroundColor": "#1E5BA8"
         }
       }
     }
   }
   ```

3. **Build & Submit:**
   ```bash
   eas build --platform android --profile production
   eas submit --platform android
   ```

4. **Review:** Usually approved in 1-3 days

---

## 🔧 CRITICAL FIXES NEEDED IN APP

### 1. Connect to Real Backend API

**Current Issue:** App has hardcoded mock data

**Fix in `/FareGlitchApp/screens/DealsScreen.js`:**

```javascript
// Replace line ~140 with:
const [deals, setDeals] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  fetchDeals();
}, []);

const fetchDeals = async () => {
  try {
    const response = await fetch('https://YOUR-API-URL/api/deals/recent');
    const data = await response.json();
    setDeals(data);
  } catch (error) {
    console.error('Failed to fetch deals:', error);
  } finally {
    setLoading(false);
  }
};
```

### 2. Implement In-App Subscriptions

**Current Issue:** Subscribe button doesn't do anything

**Fix needed:**
- Set up Stripe or RevenueCat
- Implement subscription flow
- Connect to backend subscription API

See: `IN_APP_PURCHASE_SETUP.md` in the app folder

### 3. Push Notifications Setup

**Required for deal alerts:**

```bash
# Configure push notifications
eas credentials

# Get push token
expo install expo-notifications
```

Add to `ProfileScreen.js`:
```javascript
import * as Notifications from 'expo-notifications';

const registerForPushNotifications = async () => {
  const { status } = await Notifications.requestPermissionsAsync();
  if (status === 'granted') {
    const token = await Notifications.getExpoPushTokenAsync();
    // Send token to your backend
    await fetch('https://YOUR-API/subscribe-push', {
      method: 'POST',
      body: JSON.stringify({ token: token.data })
    });
  }
};
```

---

## 📋 APP SUBMISSION CHECKLIST

### Before Submitting:

- [ ] Update API endpoints from localhost to production
- [ ] Add privacy policy URL (required by both stores)
- [ ] Create app icon (1024x1024 PNG)
- [ ] Take screenshots for each device size
- [ ] Write app description (4000 chars max)
- [ ] Set up in-app subscriptions
- [ ] Test on real devices
- [ ] Configure push notifications
- [ ] Set app version and build number
- [ ] Add age rating and content warnings

### Required Assets:

**App Icon:** 1024x1024px PNG (no transparency)
**Screenshots:**
- iPhone: 1284x2778 (iPhone 13 Pro Max)
- iPad: 2048x2732 (12.9" iPad Pro)
- Android: 1080x1920

**Promotional:**
- Feature graphic (Android): 1024x500
- Promo video (optional): Up to 30 seconds

---

## 💰 TOTAL COSTS

| Service | Cost | Required? |
|---------|------|-----------|
| Apple Developer | $99/year | Yes (iOS) |
| Google Play | $25 once | Yes (Android) |
| EAS Build | Free tier OK | Yes |
| Expo Account | Free | Yes |

**Total First Year:**
- iOS only: $99
- Android only: $25
- Both: $124

---

## 🎯 RECOMMENDED PATH

### Week 1: Testing
```bash
cd FareGlitchApp
npm install
npx expo start
```
Test with Expo Go on your phone

### Week 2: TestFlight (iOS) / APK (Android)
```bash
eas build:configure
eas build --platform all --profile preview
```
Share with friends for testing

### Week 3-4: Full Launch
1. Join Apple/Google developer programs
2. Create app store listings
3. Build production versions
4. Submit for review

---

## ⚠️ URGENT: Update These Files

1. **`FareGlitchApp/screens/DealsScreen.js`** - Line 140: Add real API
2. **`FareGlitchApp/screens/ProfileScreen.js`** - Add subscription flow
3. **`FareGlitchApp/app.json`** - Update bundle IDs and version
4. **`FareGlitchApp/services/subscriptionService.js`** - Implement real payments

---

## 📞 NEXT STEPS

1. **Deploy backend first** (see DEPLOYMENT_GUIDE.md)
2. **Update app API endpoints** to point to live backend
3. **Test with EAS Build**
4. **Submit to stores** when ready

Need help? Check:
- Expo docs: https://docs.expo.dev/
- EAS Build: https://docs.expo.dev/build/introduction/
- App Store: https://developer.apple.com/app-store/submissions/
