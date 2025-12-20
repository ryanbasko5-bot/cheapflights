# FareGlitch App Troubleshooting

## Common Issues & Solutions

### "Problem running the requested app"

This error usually happens when trying to preview/run the app locally. Here are the solutions:

#### Quick Fixes:

1. **Clear Expo Cache**
   ```bash
   cd /workspaces/cheapflights/FareGlitchApp
   rm -rf .expo node_modules/.cache
   expo start -c
   ```

2. **Reinstall Dependencies**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Test with Simple App**
   ```bash
   # Temporarily rename App.js and use test-app.js
   mv App.js App.js.backup
   mv test-app.js App.js
   npm start
   # If it works, the issue is in your app code
   ```

---

## Building for Production (Recommended Approach)

**You don't need to run the app locally to deploy it!** You can build and deploy directly:

### Option 1: Direct Build (Skip Local Testing)
```bash
cd /workspaces/cheapflights/FareGlitchApp

# Login to Expo
eas login

# Build for both platforms
eas build --platform all --profile production

# Submit to app stores
eas submit --platform ios
eas submit --platform android
```

### Option 2: Preview Build First
```bash
# Build preview versions for testing on real devices
eas build --platform all --profile preview

# Download the builds from expo.dev dashboard
# Test on physical devices, then build production
```

---

## Why You Can't Run Locally in Codespaces

**Codespaces limitation**: This dev container environment can't run the Expo preview properly because:
- No iOS simulator available (needs macOS)
- No Android emulator configured
- Network restrictions for Expo Go app

**Solution**: Build with EAS and test on real devices or use the web version.

---

## Web Preview (Works in Codespaces)

```bash
cd /workspaces/cheapflights/FareGlitchApp
npm run web
```

This will open a web version in the browser. Note: Some features won't work on web (push notifications, in-app purchases).

---

## Check Build Status

After running `eas build`, check your builds at:
- Dashboard: https://expo.dev
- Build logs show any errors in your code
- Download .apk or .ipa files directly from dashboard

---

## Common App Code Issues

### Missing Images
If you see errors about images not loading:
```javascript
// Instead of require()
<Image source={require('../assets/images/logo.jpg')} />

// Use a fallback or conditional rendering
<Image source={require('../assets/images/logo.jpg')} 
  onError={() => console.log('Image failed to load')} />
```

### API Configuration
Make sure your API endpoints in the app are configured:
```javascript
// In services or config file
const API_BASE_URL = 'https://your-backend-url.com';
```

---

## Production Deployment Checklist

Before deploying to app stores:

- [ ] Update version in `app.json`
- [ ] Test all screens navigate correctly
- [ ] Configure API endpoints for production
- [ ] Add proper app icons (icon.png, adaptive-icon.png)
- [ ] Test in-app purchases (if using)
- [ ] Configure push notifications
- [ ] Add privacy policy URL
- [ ] Test on multiple device sizes

---

## Get Help

1. **Check Expo Status**: https://status.expo.dev
2. **View Build Logs**: https://expo.dev (your project > builds)
3. **Expo Documentation**: https://docs.expo.dev
4. **React Native Docs**: https://reactnative.dev

---

## Testing Strategy

Since local preview doesn't work well in Codespaces:

1. **Build Preview APK** → Test on Android device
2. **Build iOS Simulator** → Test on Mac with Xcode
3. **Use Web Preview** → Quick UI testing
4. **Build Production** → Deploy to TestFlight/Play Store beta
5. **Get Beta Testers** → Real-world testing before public launch

You can deploy to production without ever running locally! EAS handles the build process in the cloud.
