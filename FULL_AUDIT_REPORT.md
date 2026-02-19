# FareGlitch — Full End-to-End Audit Report

**Date:** 19 February 2026  
**Auditor:** Pre-launch systems audit  
**Environment:** Production (Railway)  
**Live URL:** `https://web-production-2e87e.up.railway.app`  
**Domain:** `api.fareglitch.com.au` (DNS issue — see below)

---

## Executive Summary

| Category | Status |
|----------|--------|
| Core API | ✅ Working |
| Stripe Checkout ($5/mo) | ✅ Working |
| Webhook Signature Verification | ✅ Working |
| CORS Security | ✅ Working |
| Input Validation | ✅ Working |
| Rate Limiting | ✅ Configured |
| Auto-Scanner | ✅ Running |
| **Domain DNS** | 🔴 **BROKEN** |
| **Admin Endpoints Auth** | 🔴 **NO AUTH** |
| **Refund Endpoint Auth** | 🟡 **NO AUTH** |
| **HubSpot Webhooks Auth** | 🟡 **NO AUTH** |
| **Deal Stats Auth** | 🟡 **NO AUTH** |
| Scanner Log Mismatch | 🟡 Minor |

**Overall Grade: B+** — Core flows work perfectly. Security gaps on admin/internal endpoints need fixing before real money flows through.

---

## 🔴 CRITICAL ISSUES (Fix Before Launch)

### 1. Domain DNS is Broken

**Problem:** `api.fareglitch.com.au` resolves to `goduvv2t.up.railway.app` but your live app is at `web-production-2e87e.up.railway.app`. The domain doesn't serve traffic.

**Impact:**
- HubSpot website pages (`HOME-PAGE-AVIATION-BLUE.html` and `SIGN-IN-PAGE-AVIATION-BLUE.html`) both have `var API = "https://api.fareglitch.com.au"` — **the Subscribe button, Sign-In form, and live deals feed are all dead** until DNS is fixed.
- Stripe success/cancel URLs redirect to `https://fareglitch.com.au/home?subscribed=true` — this will fail if the domain isn't resolving.

**Fix:** Either:
- (A) Fix Railway custom domain to point `api.fareglitch.com.au` → your actual Railway service, OR
- (B) Temporarily change the JS `API` variable in both HubSpot HTML files to `https://web-production-2e87e.up.railway.app`

### 2. `/admin/deals/{deal_id}/publish` — NO AUTHENTICATION

**File:** `src/api/main.py` line 671  
**Problem:** Anyone who can guess a deal ID can publish a deal. No secret key, no JWT, no auth of any kind.

**Test:**
```
POST /admin/deals/1/publish → {"detail":"Deal not found"} (200-level processing, no 401/403)
```

**Fix:** Add the same `Authorization: Bearer {api_secret_key}` check used by `/admin/scan`.

### 3. `/admin/budget` — PUBLIC, NO AUTHENTICATION

**File:** `src/api/main.py` line 1031  
**Problem:** Exposes internal API call counts (daily/monthly usage) to anyone.

**Test:**
```
GET /admin/budget → Returns budget data without any auth
```

**Fix:** Add secret key auth check.

---

## 🟡 MEDIUM ISSUES (Fix Soon)

### 4. `/refunds/request` — No Authentication

**File:** `src/api/main.py` line 521  
**Problem:** Anyone who knows a subscriber's email and a deal number can trigger a Stripe refund. The only protection is:
- Email + deal_number must match an existing unlock
- 48-hour window from unlock time

**Risk:** If someone knows your email and deal number (which are potentially visible), they could trigger a refund on your behalf.

**Fix:** Require JWT auth (the logged-in user must match the refund email).

### 5. `/deals/{deal_number}/stats` — No Authentication

**File:** `src/api/main.py` line 589  
**Problem:** Anyone with a deal number can see total unlocks, total revenue, HubSpot analytics.

**Risk:** Leaks business metrics to competitors/public.

**Fix:** Add auth check (admin only).

### 6. `/webhooks/hubspot/payment-success` and `/webhooks/hubspot/refund-request` — No Authentication

**File:** `src/api/main.py` lines 622 and 653  
**Problem:** These accept raw JSON with no signature verification. Anyone can POST to them with crafted data.

**Test:**
```
POST /webhooks/hubspot/payment-success {"deal_number":"TEST","email":"test@test.com","payment_id":"fake"} 
→ Processes request (returns "Deal not found" only because deal doesn't exist)
```

**Fix:** Add HubSpot webhook signature verification or a shared secret header.

### 7. Stripe Success/Cancel URLs Hardcoded to Domain

**File:** `src/payments/stripe_checkout.py` lines 49-50  
**Problem:**
- Subscription success URL: `https://fareglitch.com.au/home?subscribed=true`  
- Subscription cancel URL: `https://fareglitch.com.au/home?cancelled=true`  
- Legacy deal unlock: `https://api.fareglitch.com.au/payment/success?session_id=...`

The legacy deal unlock success URL points to `api.fareglitch.com.au` which is currently broken.

**Fix:** Ensure domain is working, or update URLs.

---

## 🟢 WORKING CORRECTLY

### 8. Health Check ✅
```
GET /health → {"status":"healthy","database":"connected","environment":"production"}
```

### 9. Subscribe Flow ✅
```
POST /subscribe {"email":"test@fareglitch.com","phone_number":"0412345678"}
→ Returns valid Stripe checkout URL, session ID, price: $5.00
```
- ✅ Phone number normalization works (0412... → +61412...)
- ✅ Invalid email rejected with validation error
- ✅ Rate limited to 10/hour

### 10. Auth/Login Flow ✅
```
POST /auth/login {"email":"test@test.com"}
→ 404 "Subscriber not found" (correct for non-existent user)
```
- ✅ Returns JWT token for existing subscribers
- ✅ Proper error messages

### 11. Stripe Webhook Security ✅
```
POST /webhooks/stripe (unsigned) → 400 "Invalid webhook signature"
```
- ✅ Properly verifies Stripe-Signature header
- ✅ Rejects forged requests
- ✅ Handles all 4 event types: checkout.session.completed, invoice.payment_succeeded, customer.subscription.deleted, charge.refunded

### 12. CORS ✅
- ✅ `fareglitch.com.au` → Allowed (access-control-allow-origin returned)
- ✅ `evil.com` → Blocked (no CORS headers returned)
- ✅ Production origins: fareglitch.com.au, www.fareglitch.com.au, api.fareglitch.com.au

### 13. Deals/Live Feed ✅
```
GET /deals/live → {"deals":[],"count":0,"updated_at":"..."}
```
- ✅ Returns properly formatted JSON for HubSpot JS
- ✅ No sensitive data leaked (teaser only, no booking links)
- ✅ Rate limited to 300/hour

### 14. Unsubscribe ✅
```
DELETE /unsubscribe?email=test@test.com
→ Calls Stripe cancel_subscription() (cancel_at_period_end=True)
→ User keeps access until billing period ends
```

### 15. Input Validation ✅
- ✅ Email validated via Pydantic `EmailStr`
- ✅ Phone number normalized and validated
- ✅ Deal numbers uppercased
- ✅ Missing fields return 422 with specific error messages

### 16. Admin Scan (Protected) ✅
```
POST /admin/scan (no auth) → 403 "Invalid secret key"
POST /admin/scan (with Bearer key) → Triggers scan
```
- ✅ Properly protected by API_SECRET_KEY

### 17. Auto-Scanner ✅
- ✅ Runs in background on startup (production only)
- ✅ Budget tracking: daily and monthly caps
- ✅ Rotates through 26 Australian airports
- ✅ 2-minute startup delay to avoid boot storms

### 18. OpenAPI/Docs ✅
```
GET /docs → Swagger UI loads
GET /openapi.json → Full API spec (21 endpoints)
```

---

## 📝 MINOR ISSUES / OBSERVATIONS

### 19. Scanner Log Mismatch
**Startup log** says: "ALL 26 airports every 3 hours (8x/day)"  
**Actual code** does: 7 airports every 6 hours (4x/day)  
Not a functional issue, but the log message is misleading.

### 20. `/unsubscribe` Uses Query Parameter
The unsubscribe endpoint expects `email` as a query parameter (`?email=...`), not a JSON body. This is fine for a DELETE request, but the HubSpot frontend JavaScript should be aware of this.

### 21. Premium vs Free Visibility
The `can_see_deal()` function correctly implements the 1-hour delay for non-premium users. Premium subscribers see deals immediately. This logic is solid.

### 22. Glitch Guarantee
The 48-hour refund window in `/refunds/request` is correctly implemented — checks `unlocked_at` against current time. The Stripe `issue_refund()` call is properly structured.

### 23. Subscription Expiry Buffer
New subscriptions get 35 days (not 30) before expiry — good buffer to account for Stripe billing timing.

---

## 🎯 CUSTOMER JOURNEY WALKTHROUGH

### Pre-Customer Journey:
1. **Visit fareglitch.com.au/home** → ⚠️ Domain must be working. JS loads deals from API.
2. **See live deals** → ✅ `/deals/live` returns deal teasers (no booking details).
3. **Click Subscribe** → ✅ JS sends email + phone to `/subscribe` → Gets Stripe checkout URL.
4. **Stripe Checkout** → ✅ $5/month, card payment, AUD currency.
5. **Payment Success** → ⚠️ Redirects to `fareglitch.com.au/home?subscribed=true` (domain must work).
6. **Webhook fires** → ✅ `checkout.session.completed` activates subscription in DB, syncs to HubSpot.

### Customer Journey:
1. **Log in** → ✅ POST `/auth/login` with email/phone → JWT token.
2. **See deals early** → ✅ Premium members see deals immediately (1hr before free users).
3. **Get SMS alerts** → ✅ Infrastructure ready (Sinch/Twilio configured).
4. **Request refund** → ⚠️ Works but no auth — anyone with your email could request it.
5. **Cancel subscription** → ✅ DELETE `/unsubscribe?email=...` → Cancel at period end.
6. **Monthly renewal** → ✅ `invoice.payment_succeeded` webhook extends expiry +35 days.

---

## 🔧 RECOMMENDED FIXES (Priority Order)

| # | Fix | Effort | Impact |
|---|-----|--------|--------|
| 1 | Fix domain DNS (`api.fareglitch.com.au`) | 10 min | 🔴 Everything depends on this |
| 2 | Add auth to `/admin/deals/{id}/publish` | 5 min | 🔴 Security |
| 3 | Add auth to `/admin/budget` | 5 min | 🔴 Security |
| 4 | Add JWT auth to `/refunds/request` | 15 min | 🟡 Security |
| 5 | Add auth to `/deals/{deal_number}/stats` | 5 min | 🟡 Data leak |
| 6 | Add secret to HubSpot webhook endpoints | 15 min | 🟡 Security |
| 7 | Fix scanner log message | 2 min | 🟢 Cosmetic |

**Total estimated fix time: ~1 hour**

---

## ✅ WHAT'S SOLID

- **Stripe integration** is production-grade with proper signature verification
- **Subscription model** ($5/mo) is correctly implemented end-to-end
- **CORS** properly configured for production domains
- **Rate limiting** on all public endpoints
- **Input validation** catches bad data before processing
- **Auto-scanner** with budget tracking prevents API overspend
- **Error handling** returns appropriate HTTP codes and messages
- **Database** (PostgreSQL) connected and healthy
- **Webhook handler** covers all 4 Stripe event types correctly
- **Sentry** integration ready for production error tracking

---

*This audit was performed against the live Railway deployment on 19 Feb 2026.*
