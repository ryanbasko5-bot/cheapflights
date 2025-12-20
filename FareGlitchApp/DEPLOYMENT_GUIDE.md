# FareGlitch Mobile App - Deployment Guide

## 🚀 Quick Deploy to iOS & Android

### Prerequisites
1. **Expo Account**: Sign up at https://expo.dev
2. **Apple Developer Account** ($99/year): https://developer.apple.com (for iOS App Store)
3. **Google Play Console Account** ($25 one-time): https://play.google.com/console (for Android Play Store)

---

## 📱 Build & Deploy Instructions

### Step 1: Install EAS CLI
```bash
npm install -g eas-cli
```

### Step 2: Login to Expo
```bash
cd /workspaces/cheapflights/FareGlitchApp
eas login
```

### Step 3: Configure Project
```bash
eas build:configure
```
This will create your project in Expo and update the `projectId` in `app.json`

---

## 🍎 iOS Deployment

### Option A: TestFlight (Beta Testing)
```bash
# Build for iOS
eas build --platform ios

# After build completes, submit to TestFlight
eas submit --platform ios
```

**What you need:**
- Apple Developer account credentials
- App-specific password (create at appleid.apple.com)

### Option B: Direct Download (Testing Only)
```bash
# Build an iOS Simulator version (Mac only)
eas build --platform ios --profile preview
```

---

## 🤖 Android Deployment

### Option A: Google Play Store (Production)
```bash
# Build Android App Bundle (AAB) for Play Store
eas build --platform android --profile production

# Submit to Play Store
eas submit --platform android
```

### Option B: Direct APK (Testing)
```bash
# Build APK for direct installation
eas build --platform android --profile preview
```

**What you need:**
- Google Play Console account
- App signing key (EAS creates this automatically)

---

## 🎯 Testing Before Launch

### 1. Build Preview Versions
```bash
# Build both platforms for testing
eas build --platform all --profile preview
```

### 2. Download and Test
- **iOS**: Download .ipa and install via TestFlight or Xcode
- **Android**: Download .apk and install directly on device

### 3. Share with Beta Testers
```bash
# iOS: Automatically distributed via TestFlight
# Android: Share APK link from Expo dashboard
```

---

## 📊 Build Profiles Explained

### `development`
- For development/debugging
- Includes dev tools
- Larger app size

### `preview`
- For testing before production
- iOS: Simulator build or ad-hoc distribution
- Android: APK for direct install
- Smaller than development, not for stores

### `production`
- For App Store & Play Store submission
- Optimized and minified
- Signed for distribution

---

## 🔄 Complete Launch Workflow

### 1. Initial Setup (One-time)
```bash
cd /workspaces/cheapflights/FareGlitchApp
npm install -g eas-cli
eas login
eas build:configure
```

### 2. Build for Both Platforms
```bash
# Production builds for app stores
eas build --platform all --profile production
```

### 3. Monitor Build
- Go to https://expo.dev
- Watch build progress (takes 10-20 minutes)
- Download builds when complete

### 4. Submit to Stores
```bash
# iOS
eas submit --platform ios --latest

# Android  
eas submit --platform android --latest
```

---

## 🛠️ Alternative: Build Locally (Advanced)

### iOS (Mac Required)
```bash
# Install dependencies
npx expo prebuild

# Open in Xcode
npx expo run:ios

# Build archive in Xcode
# Product > Archive > Distribute App
```

### Android
```bash
# Install dependencies
npx expo prebuild

# Open in Android Studio
npx expo run:android

# Build in Android Studio
# Build > Generate Signed Bundle/APK
```

---

## 📝 Store Listing Requirements

### iOS App Store
- **App Name**: FareGlitch
- **Subtitle**: Flight Deals Before Instagram
- **Description**: Join 500+ travelers getting $200+ flight deal alerts
- **Keywords**: flights, deals, travel, cheap flights, fare alerts
- **Category**: Travel
- **Screenshots**: 6.5" iPhone (required), 12.9" iPad (optional)
- **Privacy Policy URL**: Required
- **Support URL**: Required

### Google Play Store
- **App Name**: FareGlitch  
- **Short Description**: Get flight deals 1 hour before Instagram (80 chars max)
- **Full Description**: Detailed description (4000 chars max)
- **Category**: Travel & Local
- **Content Rating**: Everyone
- **Screenshots**: Phone (min 2), Tablet (optional)
- **Feature Graphic**: 1024x500px
- **Privacy Policy URL**: Required

---

## 🎨 Assets Needed

### App Icons
- **iOS**: 1024x1024px PNG (no transparency)
- **Android**: 512x512px PNG

### Splash Screens
- **iOS**: 1242x2688px PNG
- **Android**: Adaptive icon + background

### Screenshots (for stores)
- **iPhone**: 1242x2688px (6.7")
- **Android**: 1080x1920px minimum

---

## 💡 Quick Start Commands

### Build Everything
```bash
# One command to build both platforms
eas build --platform all --profile production
```

### Update App (After Initial Release)
```bash
# Increment version in app.json
# Then rebuild and submit
eas build --platform all --profile production
eas submit --platform all --latest
```

### Over-The-Air Updates (No App Store Review)
```bash
# For minor updates (JS/assets only)
eas update --branch production --message "Bug fixes"
```

---

## 🚨 Common Issues

### Build Failed?
- Check `app.json` has correct `bundleIdentifier` and `package`
- Ensure all dependencies are installed
- Review build logs at expo.dev

### Can't Submit to Stores?
- Verify Apple Developer/Play Console accounts are active
- Check app signing certificates
- Ensure privacy policy URL is valid

### App Rejected?
- Add missing privacy policy
- Follow App Store Review Guidelines
- Test all functionality thoroughly

---

## 📞 Support Resources

- **Expo Docs**: https://docs.expo.dev
- **EAS Build**: https://docs.expo.dev/build/introduction/
- **App Store Connect**: https://appstoreconnect.apple.com
- **Play Console**: https://play.google.com/console

---

## ✅ Ready to Launch?

Run this command to start building:
```bash
cd /workspaces/cheapflights/FareGlitchApp
eas build --platform all --profile production
```

The build will take 15-20 minutes. You'll get download links for both iOS and Android builds when complete!
