# 💳 Setting Up Stripe Payment Links (5 minutes)

**Goal**: Create a payment link to send to Instagram subscribers.

---

## Quick Setup

### Step 1: Create Stripe Account

**URL**: https://dashboard.stripe.com/register

1. Sign up with email
2. Skip onboarding for now (can complete later)
3. You'll land on the dashboard

**Note**: You can accept payments immediately in test mode!

---

### Step 2: Create Payment Link

#### Option A: Subscription ($5/month) - RECOMMENDED

1. Go to: https://dashboard.stripe.com/payment-links
2. Click **"New"**
3. Fill in:
   - **Product name**: "FareGlitch SMS Alerts"
   - **Description**: "Get flight deals 1 hour before Instagram"
   - **Price**: $5.00 AUD
   - **Billing period**: Monthly (recurring)
4. Click **"Create link"**
5. Copy the link (e.g., `https://buy.stripe.com/test_xxxxx`)

**Your payment link**: `_________________________________`

#### Option B: Pay-Per-Alert ($2/alert)

1. Create another link
2. Fill in:
   - **Product name**: "FareGlitch Single Alert"
   - **Description**: "Get one flight deal alert via SMS"
   - **Price**: $2.00 AUD
   - **Billing period**: One time
3. Click **"Create link"**

---

### Step 3: Test It Works

1. Click your payment link
2. Use test card: `4242 4242 4242 4242`
3. Any future expiry date
4. Any CVC
5. Complete payment

**You should see**: "Payment successful!"

---

### Step 4: Get Notified of Payments

#### Set Up Webhook (Optional - for automation)

1. Go to: https://dashboard.stripe.com/webhooks
2. Click **"Add endpoint"**
3. Endpoint URL: `https://yourdomain.com/webhook/stripe`
4. Select events:
   - `checkout.session.completed`
   - `invoice.paid`
   - `customer.subscription.deleted`

**For MVP**: Skip this! Check Stripe dashboard manually for payments.

---

## Using the Payment Link

### When Someone DMs "ALERTS"

**Your reply**:
```
Hey! 👋

SMS alerts are $5/month - you get deals 1 HOUR before I post them here.

Example: Yesterday's Bali deal was $420. 
SMS subscribers booked at 6pm.
Instagram followers saw it at 7pm (already sold out).

Ready to join?
👉 Pay here: [YOUR STRIPE LINK]

Then reply with your phone number!
```

### After They Pay

1. **Check Stripe Dashboard**: https://dashboard.stripe.com/payments
2. **See the payment**: Note their email
3. **They send phone number**: e.g., "+61412345678"
4. **Add to database**:
   ```bash
   python scripts/add_subscriber.py +61412345678 sms_monthly
   ```
5. **Confirm**:
   ```
   ✅ You're in! Next deal drops soon.
   You'll get SMS 1hr before Instagram.
   ```

---

## Payment Link Templates

### Instagram Bio
```
🚨 Flight error fares
💰 $5/mo for 1hr early access
👇 Link to subscribe
```
(Put Stripe link in bio)

### Instagram Story
```
[Screenshot of deal]

"SMS subscribers got this at 6pm"
"Posted here at 7pm"

Want early access?
[Swipe up / Link in bio]
```

### Direct Message Response
```
SMS Alerts: $5/month

What you get:
✅ Instant SMS when deal found
✅ 1 hour before Instagram
✅ Direct booking links
✅ No ghost fares

Pay: [stripe link]
Then send your phone number!
```

---

## Automating Payments (Later)

### For now (Manual - Week 1-2):
1. Check Stripe daily for payments
2. Match email to Instagram DM
3. Add subscriber manually
4. Send confirmation DM

### Future (Automated - Month 2+):
1. Webhook receives payment event
2. API automatically creates subscriber
3. SMS sent: "Welcome! Next deal soon."
4. No manual work needed

**Code for this**: Already in `src/api/main.py` (not needed for MVP)

---

## Pricing Strategy

### Month 1: $5/month
- Simple, recurring
- Easy to understand
- Most people choose this

### Month 2: Test variations
- $7/month (premium, business class deals)
- $10/month (global, all airports)
- $2/alert (pay-per-use)

### Month 3+: Optimize
- A/B test pricing
- Add annual plan ($50/year, save $10)
- Family plan ($12/month, 3 phones)

---

## Stripe Pro Tips

### Test Mode vs Live Mode

**Test mode** (toggle in dashboard):
- Use test card: `4242 4242 4242 4242`
- No real money
- Perfect for MVP testing

**Live mode**:
- Real payments
- Need to activate account (provide business info)
- Can take 1-2 days approval

**For tonight**: Use test mode to verify everything works!

### Avoiding Chargebacks

Add this to your Stripe product description:
```
IMPORTANT: This is an ALERT SERVICE, not flight booking.
We notify you of deals. You book directly with airlines.
Flight prices/availability may change. No refunds for
expired deals or price changes by airlines.
```

### Tax Handling

**For now**: Don't worry about it (under $75k AUD/year)

**Later**: Stripe Tax can handle GST automatically

---

## Going Live Checklist

When you're ready to accept real money:

- [ ] Activate Stripe account (provide business details)
- [ ] Switch from test mode to live mode
- [ ] Update payment links (will get new URLs)
- [ ] Test with real card (your own)
- [ ] Update Instagram bio with live link

**Timeline**: Do this after first 5 test subscribers (Week 2)

---

## Revenue Tracking

### In Stripe Dashboard

**View**:
- Total revenue: Dashboard home
- Monthly recurring revenue (MRR): Subscriptions tab
- Churn rate: Subscriptions > Analytics

**Goal tracking**:
- Week 1: $0 (test mode)
- Week 2: $25 (5 subscribers × $5)
- Month 1: $100 (20 subscribers)
- Month 3: $500 (100 subscribers)

---

## Quick Commands

```bash
# Test Stripe webhook locally (optional)
stripe listen --forward-to localhost:8000/webhook/stripe

# View Stripe events
stripe events list

# View subscriptions
stripe subscriptions list
```

**Install Stripe CLI**: https://stripe.com/docs/stripe-cli

---

## Common Issues

### "Payment link doesn't work"

**Check**:
1. Are you in test mode? (Use test card)
2. Link copied correctly? (No spaces)
3. Product activated? (Check Products tab)

### "How do I get paid?"

**Payout schedule**:
- First payout: 7 days after first payment
- Then: Automatic every 2 days to your bank

**Setup bank account**: 
https://dashboard.stripe.com/settings/payouts

### "Customer wants refund"

**Process**:
1. Go to: https://dashboard.stripe.com/payments
2. Find the payment
3. Click "Refund"
4. Remove from subscriber database:
   ```bash
   python scripts/add_subscriber.py +61412345678 --deactivate
   ```

---

## Your Links (Fill These In)

**Stripe Dashboard**: https://dashboard.stripe.com

**Monthly Subscription Link**: 
```
_______________________________________________
```

**Pay-Per-Alert Link**:
```
_______________________________________________
```

**Instagram Profile**:
```
_______________________________________________
```

---

## 🚀 You're Ready!

You now have:
- ✅ Payment link to collect money
- ✅ Process to activate subscribers
- ✅ Revenue tracking

**Next**: Copy your Stripe link and add to Instagram bio!

**Pro tip**: Post a Story showing how it works:
```
"Here's what SMS subscribers get"
[Screenshot of SMS alert]
"Want this? Link in bio 👆"
```
