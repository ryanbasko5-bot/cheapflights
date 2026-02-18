# 🧪 FareGlitch Testing Guide

**Your complete guide to testing the FareGlitch platform**

---

## 🎯 What's Running Right Now

✅ **Website**: Port 8888  
✅ **API Backend**: Port 8000  
✅ **Database**: SQLite with test data loaded  

---

## 📱 Test Accounts

### Premium Member (Pays $5/month)
- **Email**: `premium@test.com`
- **Phone**: `+61411111111`
- **Benefits**: 
  - ⚡ See ALL deals immediately
  - 🕐 1-hour early access before public
  - 💰 No unlock fees

### Free Member
- **Email**: `free@test.com`
- **Phone**: `+61422222222`
- **Benefits**:
  - ✅ See deals after 1-hour delay
  - 💵 Must pay to unlock full details

---

## ✈️ Test Deals in Database

### Deal 1: TEST001 - Sydney → LA
- **Status**: Just published (< 1 hour old)
- **Visible to**: Premium members ONLY
- **Savings**: A$1,120 (62% off!)
- **Normal**: A$1,800
- **Deal**: A$680

### Deal 2: TEST002 - London → Bangkok  
- **Status**: 30 minutes old
- **Visible to**: Premium members ONLY
- **Savings**: £382 (56% off!)
- **Normal**: £680
- **Deal**: £298

### Deal 3: TEST003 - New York → Tokyo
- **Status**: 2 hours old (PUBLIC)
- **Visible to**: Everyone (including non-members)
- **Savings**: $855 (57% off!)
- **Normal**: $1,500
- **Deal**: $645 (Business Class!)

---

## 🌐 How to Access the Website

### Option 1: In Codespaces (Recommended)

1. **Look for "Ports" tab** at the bottom of VS Code
2. **Find port 8888** - it should show as "Public" or "Private"
3. **Click the globe icon** or "Open in Browser"
4. **Or copy the forwarded URL** - it looks like:
   ```
   https://[your-codespace-name]-8888.app.github.dev
   ```

### Option 2: Local Access

If you're running locally (not in Codespaces):
```
http://localhost:8888
```

---

## 🎬 Test Scenarios

### Scenario 1: **Public User (Not Logged In)**

**What you'll see:**
```
✅ Only TEST003 (2 hours old)
❌ Cannot see TEST001 or TEST002 (too new)
```

**Steps:**
1. Open website
2. Scroll to "Recent Deals" section
3. You should see 1 deal: New York → Tokyo

**Expected behavior:**
- See teaser with savings percentage
- See "🔒 Members Only" for hidden deals
- Can click "Subscribe Now" to upgrade

---

### Scenario 2: **Premium Member Login**

**What you'll see:**
```
✅ ALL 3 deals (TEST001, TEST002, TEST003)
⚡ Immediate access to newest deals
💰 Full booking details shown
```

**Steps:**
1. Click "Sign In" in navigation
2. Enter email: `premium@test.com`
3. Enter phone: `+61411111111` (optional)
4. Click "Sign In"
5. You'll be redirected to homepage

**Expected behavior:**
- See ALL deals immediately
- "ACTIVE DEAL" or "MISTAKE FARE" badges
- Direct booking links visible
- No unlock fees

**API Test:**
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"premium@test.com","phone_number":"+61411111111"}'

# Copy the access_token from response

# Get deals with premium access
curl http://localhost:8000/deals/active \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Scenario 3: **Premium vs Free Comparison**

**Side-by-side test:**

1. **Open 2 browser windows** (or use incognito for one)
2. **Window 1**: Login as `premium@test.com`
3. **Window 2**: Don't login (or login as `free@test.com`)
4. **Compare** what you see!

**Result:**
```
Premium Window:     | Free/Public Window:
--------------------|--------------------
3 deals visible     | 1 deal visible
Full details shown  | Locked content
Book now buttons    | "Subscribe" CTA
```

---

### Scenario 4: **Time-Based Access (Watch the Clock)**

The system uses a **1-hour delay** for non-premium users.

**To test this:**

1. Check current deals as public user
2. Create a new deal (see below)
3. Public users won't see it for 1 hour
4. Premium users see it immediately

**Create a test deal:**
```python
python3 -c "
from src.utils.database import get_db_session
from src.models.database import Deal, DealStatus
from datetime import datetime, timedelta, UTC

db = next(get_db_session())

deal = Deal(
    deal_number='TEST004',
    origin='LAX',
    destination='SYD',
    route_description='LA → Sydney',
    teaser_headline='🔥 LA to Sydney - Save 65%!',
    teaser_description='USD 500 (typical: USD 1,400)',
    normal_price=1400,
    mistake_price=500,
    savings_amount=900,
    savings_percentage=64.3,
    currency='USD',
    cabin_class='ECONOMY',
    airline='Qantas',
    booking_link='https://www.google.com/flights',
    unlock_fee=0.0,
    status=DealStatus.PUBLISHED,
    published_at=datetime.now(UTC),  # Just now!
    expires_at=datetime.now(UTC) + timedelta(hours=6),
    travel_dates_start=datetime.now(UTC) + timedelta(days=45),
    travel_dates_end=datetime.now(UTC) + timedelta(days=52)
)

db.add(deal)
db.commit()
print('✅ Created TEST004 - visible to premium only for next hour!')
"
```

---

## 🔍 API Testing

### Get All Deals (Public View)
```bash
curl http://localhost:8000/deals/active
```
**Returns**: Only deals > 1 hour old

### Get All Deals (Premium View)
```bash
# First, login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"premium@test.com"}' | jq -r '.access_token')

# Then get deals with token
curl http://localhost:8000/deals/active \
  -H "Authorization: Bearer $TOKEN"
```
**Returns**: ALL active deals

### Test Authentication
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```
**Returns**: User profile with premium status

### API Documentation
Visit: `http://localhost:8000/docs`

Interactive Swagger UI with all endpoints!

---

## 🎨 Website Features to Test

### Navigation
- ✅ Click "Home" - goes to homepage
- ✅ Click "About" - see company info
- ✅ Click "Blog" - travel tips
- ✅ Click "Sign In" - login page

### Homepage Sections
1. **Hero**: Big headline with CTA
2. **Stats**: $200+ savings, 60 min access, 500+ subscribers
3. **Mistake Fares**: Explanation section
4. **Recent Deals**: Live deals from API
5. **Pricing**: $5/month subscription
6. **FAQ**: Common questions
7. **Footer**: Social links

### Deal Display
Each deal card shows:
- ✅ Route (e.g., "JFK → LAX")
- ✅ Normal price (crossed out)
- ✅ Deal price (big and bold)
- ✅ Savings amount & percentage
- ✅ Status badge (ACTIVE/MEMBERS ONLY)
- ✅ Booking button (if unlocked)

### Responsive Design
Try resizing your browser - should work on:
- 📱 Mobile (320px+)
- 📱 Tablet (768px+)
- 💻 Desktop (1024px+)

---

## 🐛 Common Issues & Solutions

### "Can't access website"
**Solution**: 
- In Codespaces, check the Ports tab
- Make sure port 8888 is forwarded
- Click the globe icon to open

### "No deals showing"
**Solution**:
```bash
# Reload test data
python3 setup_test_data.py
```

### "API not responding"
**Solution**:
```bash
# Check if running
ps aux | grep uvicorn

# Restart if needed
pkill uvicorn
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### "Login doesn't work"
**Solution**:
- Check that API is running on port 8000
- Open browser console (F12) to see errors
- Make sure using exact emails: `premium@test.com` or `free@test.com`

---

## 📊 Success Metrics

After testing, you should be able to:
- ✅ See different deals based on login status
- ✅ Login with test accounts
- ✅ Navigate all pages smoothly
- ✅ See time-delayed access working
- ✅ View deal details with booking links
- ✅ Confirm responsive design works

---

## 🚀 Next Steps After Testing

Once you've confirmed everything works:

1. **Configure Real APIs** - Add actual API keys for:
   - Kiwi.com (flight search)
   - Amadeus (flight data)
   - SerpAPI (Google Flights)

2. **Find Real Deals** - Run:
   ```bash
   python3 kiwi_deal_finder.py
   ```

3. **Set Up SMS Alerts** - Configure Twilio/Sinch

4. **Deploy to Production** - Railway, Vercel, or AWS

5. **Launch Instagram** - Start building followers

---

## 💡 Pro Tips

- **Clear browser cache** between tests
- **Use incognito mode** for fresh sessions
- **Check browser console** (F12) for errors
- **Monitor API logs**: `tail -f api.log`
- **Test on mobile** using Codespaces on phone

---

## 🎯 The Full User Journey

**New Visitor Flow:**
1. Land on homepage → See 1 old deal
2. Click "Subscribe Now" → See pricing
3. Sign up via HubSpot form
4. Receive welcome email
5. Login → See ALL deals
6. Book a $200 flight → Save money!

**The Business Model:**
- Free users see deals **1 hour late** (often sold out)
- Premium ($5/mo) get **instant SMS alerts**
- Instagram followers see it **after 1 hour** (builds audience)
- Everyone wins: Users save money, you earn recurring revenue

---

**🎉 Happy Testing!**

Need help? Check the logs:
- API: `tail -f api.log`
- Website: Browser console (F12)
- Database: `sqlite3 fareglitch.db`
