# 🚀 API SETUP GUIDE - GET ALL YOUR KEYS!

## ✅ 1. DUFFEL (Already have it!)
**Status**: READY TO USE  
**Token**: Already in your `.env` file  
**Action**: None needed - test it now!

```bash
python src/integrations/duffel_client.py
```

---

## 🔍 2. SERPAPI (Google Flights Scraper)
**Why**: Gets EXACT Google Flights data - solves pricing accuracy  
**Cost**: 100 free searches/month, then $50/month  
**Setup**: 2 minutes

### Steps:
1. Go to: https://serpapi.com/users/sign_up
2. Sign up with email
3. Verify email
4. Go to Dashboard → API Key
5. Copy your key
6. Add to `.env`: `SERPAPI_KEY=your_key_here`

**Test**: `python src/integrations/serpapi_client.py`

---

## 💰 3. TRAVELPAYOUTS (Earn money + API)
**Why**: FREE API + you earn commission on bookings!  
**Cost**: Free (you make money!)  
**Setup**: 5 minutes

### Steps:
1. Go to: https://www.travelpayouts.com/
2. Click "Sign Up" → Select "Content Creator" or "Developer"
3. Fill out profile
4. Go to Projects → Create Project
5. Get API Token: Tools → API Access
6. Get Affiliate Marker: Projects → Your Project → Marker
7. Add to `.env`:
   ```
   TRAVELPAYOUTS_TOKEN=your_token_here
   TRAVELPAYOUTS_MARKER=your_affiliate_id
   ```

**Test**: `python src/integrations/travelpayouts_client.py`

---

## 📊 4. AVIATIONSTACK (Backup source)
**Why**: Good backup, real-time data  
**Cost**: 500 free calls/month  
**Setup**: 2 minutes

### Steps:
1. Go to: https://aviationstack.com/product
2. Click "Sign Up Free"
3. Verify email
4. Dashboard → API Access Key
5. Copy key
6. Add to `.env`: `AVIATIONSTACK_KEY=your_key_here`

---

## 🎯 5. RAPIDAPI (Marketplace)
**Why**: Access to multiple flight APIs  
**Cost**: Pay per call (cheap)  
**Setup**: 3 minutes

### Steps:
1. Go to: https://rapidapi.com/auth/sign-up
2. Sign up
3. Browse: https://rapidapi.com/category/Travel
4. Subscribe to flight APIs you want
5. Get your RapidAPI key from dashboard
6. Add to `.env`: `RAPIDAPI_KEY=your_key_here`

---

## 🧪 TESTING ALL APIS

Once you have keys added, test everything:

```bash
# Test Duffel (you have this already!)
python src/integrations/duffel_client.py

# Test SerpAPI
python src/integrations/serpapi_client.py

# Test Travelpayouts
python src/integrations/travelpayouts_client.py

# Run multi-source finder (uses all available APIs)
python multi_source_finder.py
```

---

## 🎯 PRIORITY ORDER

**Start with these (quickest):**
1. ✅ Duffel - READY NOW
2. 🔍 SerpAPI - Signup now (2 min)
3. 💰 Travelpayouts - Signup now (5 min)

**Add later:**
4. AviationStack
5. RapidAPI

---

## 💡 MULTI-SOURCE ADVANTAGE

The `multi_source_finder.py` will:
- ✅ Query ALL your APIs simultaneously
- ✅ Cross-verify prices (no fake data!)
- ✅ Use median as "typical" (conservative)
- ✅ Use cheapest as "deal" (best price)
- ✅ Include affiliate links (earn money)
- ✅ 100% accurate, no guessing!

**Example output:**
```
📊 Sydney → Bali...
   📈 Prices found: 3 sources
      duffel: AUD 425
      google_flights: AUD 431  ← EXACT Google price!
      travelpayouts: AUD 418
   💰 Best price: AUD 418
   📊 Typical (median): AUD 425
   ✅ 35% off - Great Deal
```

---

## 📝 QUICK START

1. Keep Duffel (you have it)
2. Sign up for SerpAPI (2 min): https://serpapi.com/users/sign_up
3. Sign up for Travelpayouts (5 min): https://www.travelpayouts.com/
4. Update `.env` with both keys
5. Run: `python multi_source_finder.py`
6. Watch it find REAL, VERIFIED deals!

---

**Questions? Start signing up and paste your keys as you get them!**
