# 🎯 COMPLETE GUIDE - What I Just Built For You

## 🚀 Summary

I've completely configured your FareGlitch system with:
1. ✅ **Production Amadeus API** - Real flight data
2. ✅ **Member Authentication** - JWT-based login system
3. ✅ **Time-Delayed Deals** - Premium members see deals 1 hour before public
4. ✅ **Dynamic Website** - Automatically loads deals from API
5. ✅ **Sign-In System** - Member portal

---

## 🔑 How It Works

### For Premium Members ($5/month):
1. Sign in → Get JWT token
2. Visit website → See ALL deals **immediately**
3. Get SMS alerts the moment deals are found
4. 1-hour exclusive access before Instagram/public

### For Non-Members (Free):
1. Visit website → See only deals published **>1 hour ago**
2. Can follow on Instagram (gets deals after 1 hour)
3. Encouraged to upgrade to premium

### The Business Model:
- Find flight deals via Amadeus API
- Send to premium members immediately
- Wait 1 hour
- Post to Instagram (50K followers)
- Non-members see it on website after 1 hour
- By then, deal is usually gone → encourages sign-ups

---

## 📁 What Files Changed

### New Files Created:
1. `/website/api.js` - Frontend API client with authentication
2. `/website/signin.html` - New sign-in page
3. `/src/api/auth.py` - Authentication and authorization logic
4. `/setup_test_data.py` - Creates test subscribers and deals
5. `/launch_api.sh` - One-command API launch
6. `/PRODUCTION_READY.md` - Complete deployment guide

### Modified Files:
1. `.env` - Changed `AMADEUS_ENV=test` → `AMADEUS_ENV=production`
2. `/src/api/main.py` - Added auth endpoints and member-filtered deals
3. `/website/index.html` - Replaced static deals with dynamic loading
4. `/requirements.txt` - Added JWT and password hashing libraries

---

## 🎮 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd /workspaces/cheapflights
pip install -r requirements.txt
```

### Step 2: Create Test Data
```bash
python setup_test_data.py
```

This creates:
- 2 test subscribers (premium + free)
- 3 test deals (just published, 30 mins ago, 2 hours ago)

### Step 3: Start API Server
```bash
./launch_api.sh
```

API runs at `http://localhost:8000`

### Step 4: Open Website
```bash
cd website
python -m http.server 8080
```

Website at `http://localhost:8080/index.html`

---

## 🧪 Testing the System

### Test 1: View Deals Without Login
1. Open `http://localhost:8080/index.html`
2. You should see:
   - ❌ TEST001 & TEST002: **Locked** (published <1 hour ago)
   - ✅ TEST003: **Visible** (published 2 hours ago)

### Test 2: Login as Premium Member
1. Go to `http://localhost:8080/signin.html`
2. Enter:
   - Email: `premium@test.com`
   - Phone: `+61411111111`
3. Click "Sign In"
4. Redirected to home page
5. You should now see:
   - ✅ **ALL 3 DEALS** (TEST001, TEST002, TEST003)
   - Badge: "⭐ You're a premium member"

### Test 3: Login as Free Member
1. Sign out (clear localStorage or use incognito)
2. Sign in with:
   - Email: `free@test.com`
   - Phone: `+61422222222`
3. Same as Test 1 - only sees TEST003

### Test 4: API Direct Testing
Visit `http://localhost:8000/docs`

Try:
1. **POST /auth/login** 
   ```json
   {
     "email": "premium@test.com",
     "phone_number": "+61411111111"
   }
   ```
   → Copy the `access_token`

2. **GET /deals/active**
   - Click "Authorize" → Paste token
   - Execute → Should see all 3 deals

3. **GET /auth/me**
   → Should show your subscriber info

---

## 🔐 Authentication Flow

### How JWT Works:
```
1. User enters email/phone
   ↓
2. API checks if subscriber exists
   ↓
3. API creates JWT token (expires in 7 days)
   ↓
4. Frontend stores token in localStorage
   ↓
5. All API calls include: Authorization: Bearer <token>
   ↓
6. API validates token and checks membership status
   ↓
7. Returns filtered deals based on membership
```

### Token Contents:
```json
{
  "sub": "+61411111111",  // phone number
  "exp": 1640000000       // expiration timestamp
}
```

---

## ⏰ Time Delay Logic

### Code Location: `/src/api/auth.py`

```python
def can_see_deal(deal, subscriber):
    # Premium members see everything immediately
    if is_premium_member(subscriber):
        return True
    
    # Non-members must wait 1 hour
    hours_since_published = (now - deal.published_at).hours
    return hours_since_published >= 1.0
```

### In Practice:
| Time | Premium | Non-Member |
|------|---------|------------|
| 00:00 - Deal published | ✅ Sees it | ❌ Locked |
| 00:30 - 30 mins later | ✅ Sees it | ❌ Locked |
| 01:00 - 1 hour later | ✅ Sees it | ✅ **Now visible** |
| 02:00 - Usually sold out | ✅ Sees it | ✅ But too late |

---

## 🗄️ Database Schema

### Subscribers Table
```sql
phone_number         VARCHAR (unique)
email                VARCHAR
subscription_type    VARCHAR (free / sms_monthly / pay_per_alert)
is_active            BOOLEAN
subscription_expires_at TIMESTAMP
```

### Deals Table
```sql
deal_number          VARCHAR (e.g., "DEAL001")
origin               VARCHAR (e.g., "SYD")
destination          VARCHAR (e.g., "LAX")
normal_price         FLOAT
mistake_price        FLOAT
savings_amount       FLOAT
published_at         TIMESTAMP  ← Used for 1-hour delay
expires_at           TIMESTAMP
status               VARCHAR (published / expired)
```

---

## 🌐 Website Integration

### Frontend Flow:
```javascript
// 1. On page load
const user = fareglitchAPI.getCurrentUser();

// 2. Check if premium
if (user && user.is_premium) {
    statusElement.text = "⭐ Premium member";
}

// 3. Fetch deals (API handles filtering)
const deals = await fareglitchAPI.getActiveDeals();

// 4. Render deals
deals.forEach(deal => {
    if (isDealAvailable(deal)) {
        // Show full details
    } else {
        // Show "Members Only" lock
    }
});
```

---

## 🚢 Deployment

### Deploy API (Choose One):

#### Railway (Recommended - Free Tier)
```bash
railway login
railway init
railway up
```

Update `API_BASE_URL` in `/website/api.js`:
```javascript
const API_BASE_URL = 'https://fareglitch-api.railway.app';
```

#### Heroku
```bash
heroku create fareglitch-api
git push heroku main
```

#### Docker
```bash
docker build -t fareglitch-api .
docker run -p 8000:8000 fareglitch-api
```

### Deploy Website (Choose One):

#### Vercel (Recommended)
```bash
cd website
vercel
```

#### Netlify
```bash
cd website
netlify deploy
```

#### GitHub Pages
```bash
# Push website folder to gh-pages branch
git subtree push --prefix website origin gh-pages
```

---

## 📊 Next Steps Priority

### Tonight (Must Do):
1. ✅ Test everything locally
2. ✅ Create 1-2 real deals manually
3. ✅ Deploy API to Railway
4. ✅ Deploy website to Vercel
5. ✅ Update API URL in website

### This Week:
1. 🔄 Connect HubSpot for subscriber management
2. 💳 Integrate Stripe for $5/month subscriptions
3. 📱 Set up Twilio SMS alerts
4. 🤖 Automate flight scanning
5. 📸 Test Instagram integration

### This Month:
1. 📱 Launch mobile app (code is ready)
2. 📈 Marketing: Instagram ads, influencers
3. 💰 Get first 100 paying subscribers
4. 📊 Analytics and tracking
5. 🎯 A/B test pricing

---

## 🐛 Common Issues

### "No deals showing on website"
- Check API is running: `http://localhost:8000/`
- Check deals exist: `http://localhost:8000/docs` → GET /deals/active
- Check browser console for errors (F12)

### "Login not working"
- Verify subscriber exists in database
- Check email/phone match exactly
- Look at API logs for errors

### "All deals locked even for premium"
- Verify login worked (check localStorage for token)
- Test `/auth/me` endpoint - should return user
- Check subscription_type is "sms_monthly"
- Verify subscription_expires_at is in future

### "CORS error"
- API must be running
- Check CORS settings in `/src/api/main.py`
- For production, update `allow_origins` to your domain

---

## 💡 Pro Tips

1. **Test with browser incognito** - Easier than clearing localStorage
2. **Use API docs** - `http://localhost:8000/docs` is your friend
3. **Check API logs** - Terminal shows all errors
4. **Browser console** - F12 → Console shows JavaScript errors
5. **Manual deal creation** - Use Python script vs waiting for scanner

---

## 📞 You're Ready!

Everything is set up. The system:
- ✅ Connects to production Amadeus API
- ✅ Authenticates members with JWT
- ✅ Shows deals to premium members immediately
- ✅ Delays deals 1 hour for non-members
- ✅ Automatically updates website from API
- ✅ Has sign-in functionality

Just run:
```bash
python setup_test_data.py  # Create test data
./launch_api.sh            # Start API
cd website && python -m http.server 8080  # Start website
```

Then visit `http://localhost:8080` and test!

---

## 📝 Summary of Changes

| What | Before | After |
|------|--------|-------|
| Amadeus | Test mode | ✅ Production mode |
| Deals | Static HTML | ✅ Dynamic API loading |
| Members | No auth | ✅ JWT authentication |
| Access | Everyone sees same | ✅ Premium gets 1-hour early access |
| Sign-in | No page | ✅ Full sign-in page |
| API | Basic endpoints | ✅ Auth + filtered deals |

🎉 **You're production-ready!**
