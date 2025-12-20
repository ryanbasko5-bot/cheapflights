# 🚀 QUICK START - Deploy FareGlitch in 2 Hours

Follow these steps in order. Total time: **2-3 hours** to go live!

---

## ⏱️ STEP 1: Get API Keys (30 minutes)

### Amadeus API (FREE)
1. Go to: https://developers.amadeus.com/register
2. Create account
3. Create new app
4. Copy `API Key` and `API Secret`

### HubSpot API (FREE)
1. Go to: https://app.hubspot.com/
2. Create free account
3. Settings → Integrations → Private Apps
4. Create app with scopes: `contacts`, `timeline`, `crm.objects.deals`
5. Copy `Access Token`

### Sinch SMS (Pay-as-you-go)
1. Go to: https://dashboard.sinch.com/signup
2. Create account
3. SMS → Services → Create new service
4. Copy `Service Plan ID` and `API Token`
5. Buy a phone number (~$1/month)

---

## ⏱️ STEP 2: Deploy Backend (30 minutes)

### Option A: Railway (Recommended - Easiest)

1. **Push to GitHub:**
   ```bash
   cd /workspaces/cheapflights
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Railway:**
   - Go to: https://railway.app/
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repo
   - Railway auto-detects Docker Compose!

3. **Add Environment Variables:**
   Click on the API service → Variables → Add:
   ```
   AMADEUS_API_KEY=your_key_from_step_1
   AMADEUS_API_SECRET=your_secret_from_step_1
   AMADEUS_ENV=test
   
   HUBSPOT_API_KEY=your_token_from_step_1
   HUBSPOT_PORTAL_ID=your_portal_id
   
   SINCH_SERVICE_PLAN_ID=your_id_from_step_1
   SINCH_API_TOKEN=your_token_from_step_1
   SINCH_PHONE_NUMBER=+1234567890
   
   DATABASE_URL=postgresql://postgres:password@postgres:5432/fareglitch
   API_SECRET_KEY=random-secret-key-here-change-this
   
   ENABLE_AUTO_PUBLISH=false
   ENABLE_SMS_ALERTS=true
   DEBUG_MODE=false
   ```

4. **Get Your API URL:**
   - Railway will show: `https://your-app.up.railway.app`
   - Copy this URL!

5. **Initialize Database:**
   ```bash
   # In Railway terminal:
   python -c "from src.models.database import init_db; init_db()"
   ```

### Option B: Render (Free Tier)

1. Go to: https://render.com/
2. New → Web Service
3. Connect GitHub repo
4. Build command: `docker-compose build`
5. Start command: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`
6. Add environment variables (same as above)
7. Create PostgreSQL database (free tier)
8. Deploy!

---

## ⏱️ STEP 3: Connect Website to Backend (15 minutes)

1. **Update API URL in website:**
   ```bash
   cd /workspaces/cheapflights/website
   ```

   Edit `script.js` line 37-41:
   ```javascript
   // BEFORE:
   const response = await fetch('/api/subscribe', {
   
   // AFTER (replace with YOUR Railway URL):
   const response = await fetch('https://your-app.up.railway.app/api/subscribe', {
   ```

2. **Test locally:**
   ```bash
   # Open website/index.html in browser
   # Or use Python server:
   python3 -m http.server 8080
   # Visit: http://localhost:8080
   ```

3. **Test form submission:**
   - Enter phone number: +61411123456
   - Click subscribe
   - Should see success message!

4. **Deploy website (FREE):**
   
   **Option A: Netlify**
   ```bash
   # Install Netlify CLI:
   npm install -g netlify-cli
   
   # Deploy:
   cd website
   netlify deploy --prod
   ```
   
   **Option B: Vercel**
   ```bash
   npm install -g vercel
   cd website
   vercel --prod
   ```
   
   **Option C: GitHub Pages**
   - Push to GitHub
   - Settings → Pages → Deploy from main branch

---

## ⏱️ STEP 4: Test Mobile App (30 minutes)

1. **Update API URL:**
   ```bash
   cd /workspaces/cheapflights/FareGlitchApp
   ```

   Edit `config/api.js` line 4:
   ```javascript
   const API_BASE_URL = __DEV__ 
     ? 'http://localhost:8000'
     : 'https://your-app.up.railway.app';  // YOUR RAILWAY URL
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start Expo:**
   ```bash
   npx expo start
   ```

4. **Test on phone:**
   - Download "Expo Go" app
   - Scan QR code
   - App should load!
   - Pull to refresh deals
   - Should fetch from your API

---

## ⏱️ STEP 5: Test End-to-End (15 minutes)

### Test Website Flow:
1. Visit your deployed website
2. Enter phone number
3. Click subscribe
4. Check SMS received
5. Check HubSpot for new contact

### Test App Flow:
1. Open app in Expo Go
2. Pull to refresh on Deals screen
3. Should see deals from API
4. Check loading states work

### Test Backend:
1. Visit: `https://your-app.up.railway.app/docs`
2. Should see FastAPI docs
3. Test `/api/deals/recent` endpoint
4. Test `/api/subscribe` endpoint

---

## ⏱️ STEP 6: Run Scanner (15 minutes)

1. **Manual test:**
   ```bash
   # In Railway console or locally:
   python -m src.scanner.main --test
   ```

2. **Enable automatic scanning:**
   Update Railway environment variables:
   ```
   ENABLE_AUTO_PUBLISH=true
   ```

3. **Scanner runs every hour automatically!**

---

## 🎉 YOU'RE LIVE!

**What's Working:**
- ✅ Website with mobile responsiveness
- ✅ Form submits to backend
- ✅ Backend API processing requests
- ✅ HubSpot integration
- ✅ SMS alerts (when deals found)
- ✅ Mobile app fetching real data
- ✅ Scanner running automatically

**Your Stack:**
- Frontend: Netlify/Vercel (FREE)
- Backend: Railway ($5/month)
- Database: PostgreSQL (included)
- Mobile: Expo (FREE)

**Total Monthly Cost: $5**

---

## 📱 BONUS: Build App for Stores (You're Ready!)

Your app is already fully configured with:
- ✅ EAS Build setup complete
- ✅ In-app subscriptions implemented
- ✅ Product IDs configured
- ✅ iOS/Android identifiers set

**Build for production:**

```bash
cd FareGlitchApp

# Update API URL first
# Edit config/api.js with your Railway URL

# Build for both stores
eas build --platform all --profile production

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

**Your Product ID:** `com.fareglitch.app.monthly`
**iOS Bundle:** `com.fareglitch.app`
**Android Package:** `com.fareglitch.app`

Apps usually approved in 1-3 days!

---

## 🚨 TROUBLESHOOTING

### "API not reachable"
- Check Railway logs for errors
- Verify environment variables set
- Check DATABASE_URL is correct

### "SMS not sending"
- Verify Sinch credentials
- Check phone number format: +61411123456
- Ensure Sinch service has credit

### "No deals found"
- Scanner needs time to find anomalies
- Test mode: `python -m src.scanner.main --test`
- Check Amadeus API credentials

### "HubSpot error"
- Verify API token has correct scopes
- Check portal ID is correct
- Test in HubSpot API explorer

---

## 📞 NEXT STEPS

### This Week:
1. Get 10 friends to test
2. Fix any bugs found
3. Collect feedback
4. Start scanner in production mode

### Next Week:
1. Join Apple Developer Program ($99/year)
2. Join Google Play Developer ($25 once)
3. Build production app: `eas build --platform all`
4. Submit to app stores

### Month 1:
1. Monitor scanner for false positives
2. Adjust thresholds if needed
3. Grow Instagram following
4. Get first paying subscribers!

---

## 🎯 SUCCESS METRICS

**Week 1 Goals:**
- [ ] 10 test signups
- [ ] 1 real deal found by scanner
- [ ] SMS alert sent successfully
- [ ] 0 crashes/errors

**Month 1 Goals:**
- [ ] 100 signups
- [ ] 10+ deals found
- [ ] App store submissions complete
- [ ] $50 MRR (10 paid subscribers)

**Month 3 Goals:**
- [ ] 1,000 signups
- [ ] 50+ deals found
- [ ] Apps approved in stores
- [ ] $500 MRR (100 paid subscribers)

---

## 💡 TIPS

1. **Test with real phone numbers first** - SMS alerts are the core feature
2. **Monitor Amadeus API usage** - Free tier has limits
3. **Check HubSpot contacts daily** - Ensure integration working
4. **Start scanner conservatively** - 1 hour intervals, increase later
5. **Keep DEBUG_MODE=true initially** - Easier troubleshooting

---

## ✅ COMPLETION CHECKLIST

Before calling it "done":

- [ ] Backend deployed and accessible
- [ ] Website deployed and mobile-responsive
- [ ] Form submission works
- [ ] SMS alerts sending
- [ ] HubSpot contacts created
- [ ] Mobile app fetching from API
- [ ] Scanner running automatically
- [ ] Tested on real devices
- [ ] All API keys configured
- [ ] Database initialized

**When all checked, you're LIVE! 🚀**

---

Need help? Check:
- `DEPLOYMENT_GUIDE.md` - Detailed backend setup
- `MOBILE_APP_DEPLOYMENT.md` - App store submission
- `AUDIT_REPORT.md` - Full system audit
- Railway docs: https://docs.railway.app/
- Expo docs: https://docs.expo.dev/
