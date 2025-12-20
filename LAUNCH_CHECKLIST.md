# FareGlitch Launch Checklist

## Pre-Launch (Week 1-2)

### API Accounts Setup
- [ ] **Amadeus for Developers**
  - [ ] Register at https://developers.amadeus.com/register
  - [ ] Create test app
  - [ ] Copy API Key and Secret to `.env`
  - [ ] Test with: `python -m src.scanner.main --test --origins JFK`
  
- [ ] **Duffel**
  - [ ] Register at https://duffel.com/signup
  - [ ] Get API token
  - [ ] Add to `.env`
  - [ ] Test validation works
  
- [ ] **HubSpot Professional**
  - [ ] Verify subscription is active
  - [ ] Get API key from Settings → Integrations
  - [ ] Get Portal ID
  - [ ] Add to `.env`

### Infrastructure Setup
- [ ] **Database**
  - [ ] Install PostgreSQL or use Docker
  - [ ] Run `./scripts/init_db.sh`
  - [ ] Verify tables created: `psql fareglitch -c "\dt"`
  
- [ ] **Environment**
  - [ ] Run `./scripts/setup.sh`
  - [ ] Configure `.env` with all API keys
  - [ ] Test: `python -m src.scanner.main --test`
  
- [ ] **Slack Alerts**
  - [ ] Create #fareglitch-alerts channel
  - [ ] Create incoming webhook
  - [ ] Add webhook URL to `.env`
  - [ ] Test: Send test alert

### Code Verification
- [ ] **Run Tests**
  - [ ] `pytest tests/ -v` (all pass)
  - [ ] `pytest tests/ --cov=src` (>80% coverage)
  
- [ ] **Start Services**
  - [ ] API: `uvicorn src.api.main:app --reload`
  - [ ] Scanner: `python -m src.scanner.main --interval 3600`
  - [ ] Verify http://localhost:8000/docs works

## HubSpot Configuration (Week 2)

### Custom Properties
- [ ] **Contact Properties** (Settings → Properties → Contact)
  - [ ] `deal_unlock_timestamp` (Date)
  - [ ] `deal_to_deliver` (Single-line text)
  - [ ] `last_deal_unlocked` (Single-line text)
  - [ ] `total_deals_unlocked` (Number)
  - [ ] `last_refund_date` (Date)
  - [ ] `last_refund_reason` (Multi-line text)

- [ ] **Product Properties** (Commerce Hub → Products → Properties)
  - [ ] `deal_number` (Single-line text)
  - [ ] `deal_origin` (Single-line text)
  - [ ] `deal_destination` (Single-line text)
  - [ ] `deal_savings` (Number)

### Commerce Setup
- [ ] **Payment Processing**
  - [ ] Go to Commerce Hub → Payments
  - [ ] Connect Stripe account
  - [ ] Test payment link creation
  - [ ] Set default currency: USD

### Email Templates
- [ ] **Deal Details Delivery**
  - [ ] Create template (see docs/HUBSPOT_SETUP.md)
  - [ ] Add personalization tokens
  - [ ] Test send
  - [ ] Set as active
  
- [ ] **Refund Confirmation**
  - [ ] Create template
  - [ ] Test send
  - [ ] Set as active

### Workflows
- [ ] **Deal Delivery Workflow**
  - [ ] Create contact-based workflow
  - [ ] Trigger: `deal_unlock_timestamp` is known
  - [ ] Action 1: Send "Deal Details Delivery" email
  - [ ] Action 2: Add to "Active Customers" list
  - [ ] Action 3: Set lifecycle stage = Customer
  - [ ] Turn ON
  
- [ ] **Glitch Guarantee Workflow**
  - [ ] Create ticket-based workflow
  - [ ] Trigger: Ticket in "Refund Request" stage
  - [ ] Action 1: Call webhook
  - [ ] Action 2: Send refund confirmation
  - [ ] Turn ON

### Landing Page
- [ ] **Deal Teaser Template**
  - [ ] Create template in Marketing → Website
  - [ ] Add hero section
  - [ ] Add pricing comparison
  - [ ] Add "Unlock" CTA
  - [ ] Add FAQ section
  - [ ] Use smart content to hide booking details
  - [ ] Publish template

## Testing Phase (Week 3)

### Create Test Deal
- [ ] Run: `python scripts/create_deal.py`
- [ ] Verify appears in database
- [ ] Verify appears in API: `curl http://localhost:8000/deals/active`

### Test Full Unlock Flow
- [ ] Visit teaser page
- [ ] Click "Unlock for $7"
- [ ] Complete payment (test mode)
- [ ] Verify email received
- [ ] Verify booking link works
- [ ] Check contact created in HubSpot
- [ ] Check workflow triggered

### Test Refund Flow
- [ ] Create support ticket in HubSpot
- [ ] Set pipeline to "Refund Request"
- [ ] Verify webhook called
- [ ] Verify refund processed
- [ ] Verify confirmation email sent

### Load Testing
- [ ] Test API with 100 concurrent requests
- [ ] Verify scanner handles errors gracefully
- [ ] Test database connection pooling
- [ ] Monitor memory usage

## Soft Launch (Week 4)

### Find First Real Deal
- [ ] Monitor FlyerTalk: https://www.flyertalk.com/forum/mileage-run-discussion-372/
- [ ] Check SecretFlying: https://www.secretflying.com/
- [ ] Verify deal on airline website
- [ ] Manually create deal in database

### Publish First Deal
- [ ] Review deal data
- [ ] Create product in HubSpot
- [ ] Create payment link
- [ ] Publish landing page
- [ ] Post to social media (teaser)
- [ ] Monitor Slack for unlocks

### Monitor Performance
- [ ] Check database for unlocks every hour
- [ ] Monitor email deliverability
- [ ] Track conversion rate
- [ ] Watch for refund requests
- [ ] Check airline doesn't cancel fare

### Gather Feedback
- [ ] Send survey to first 10 customers
- [ ] Ask: "Did you book successfully?"
- [ ] Ask: "What could be improved?"
- [ ] Adjust messaging based on feedback

## Production Deployment

### Infrastructure
- [ ] **Domain & SSL**
  - [ ] Purchase domain: fareglitch.com
  - [ ] Set up SSL certificate
  - [ ] Configure DNS
  
- [ ] **Hosting**
  - [ ] Deploy to AWS/GCP/DigitalOcean
  - [ ] Set up load balancer
  - [ ] Configure auto-scaling
  - [ ] Set up database backups
  
- [ ] **Monitoring**
  - [ ] Set up Sentry for error tracking
  - [ ] Configure uptime monitoring
  - [ ] Set up log aggregation
  - [ ] Create alerting rules

### Security
- [ ] **API Keys**
  - [ ] Rotate all API keys to production
  - [ ] Use secrets manager (AWS Secrets Manager, etc.)
  - [ ] Enable API rate limiting
  
- [ ] **Database**
  - [ ] Enable SSL connections
  - [ ] Set up automated backups
  - [ ] Restrict network access
  - [ ] Enable query logging

### Performance
- [ ] **Caching**
  - [ ] Implement Redis for API responses
  - [ ] Cache deal teasers (1 hour TTL)
  - [ ] Cache price history queries
  
- [ ] **CDN**
  - [ ] Set up CloudFlare/Fastly
  - [ ] Cache static assets
  - [ ] Enable image optimization

## Marketing Launch

### Website
- [ ] **Homepage**
  - [ ] Value proposition
  - [ ] How it works
  - [ ] Featured deals
  - [ ] Testimonials
  - [ ] FAQ
  
- [ ] **Legal Pages**
  - [ ] Terms of Service
  - [ ] Privacy Policy
  - [ ] Refund Policy (Glitch Guarantee)
  - [ ] Cookie Policy

### Social Media
- [ ] **Accounts**
  - [ ] Twitter/X: @fareglitch
  - [ ] Instagram: @fareglitch
  - [ ] TikTok: @fareglitch
  - [ ] Facebook Page
  
- [ ] **Content Strategy**
  - [ ] Post deal teasers 3x/week
  - [ ] Share travel tips
  - [ ] Post customer success stories
  - [ ] Run engagement campaigns

### Paid Acquisition
- [ ] **Facebook Ads**
  - [ ] Target "Frequent Travelers"
  - [ ] Target "Digital Nomads"
  - [ ] Budget: $500/month initial
  - [ ] Creative: "Don't pay $4,000 for Japan..."
  
- [ ] **Google Ads**
  - [ ] Target "mistake fares"
  - [ ] Target "cheap flights"
  - [ ] Budget: $300/month initial

### Email Marketing
- [ ] **Weekly Newsletter**
  - [ ] Subject: "This Week's Mistake Fares"
  - [ ] List recent deals
  - [ ] Travel tips
  - [ ] Send Monday 9am
  
- [ ] **Segmentation**
  - [ ] By region interest (Asia, Europe, etc.)
  - [ ] By cabin class (economy, business)
  - [ ] By purchase history

## Growth Phase (Month 2+)

### Automation
- [ ] **Auto-Publish**
  - [ ] Enable `ENABLE_AUTO_PUBLISH=true`
  - [ ] Set confidence threshold
  - [ ] Manual review for high-value deals only
  
- [ ] **Scale Scanner**
  - [ ] Add 50 more origin airports
  - [ ] Reduce scan interval to 30 minutes
  - [ ] Implement parallel scanning

### Features
- [ ] **User Accounts**
  - [ ] Allow users to save preferences
  - [ ] Deal alerts by region
  - [ ] Purchase history
  
- [ ] **Mobile App**
  - [ ] React Native app
  - [ ] Push notifications
  - [ ] In-app purchase
  
- [ ] **Premium Tier**
  - [ ] $29/month for unlimited unlocks
  - [ ] Early access to deals
  - [ ] Priority support

### Metrics Tracking
- [ ] Set up analytics dashboard
- [ ] Track key metrics:
  - [ ] Monthly visitors
  - [ ] Conversion rate
  - [ ] Average unlock fee
  - [ ] Refund rate
  - [ ] Customer lifetime value
  - [ ] Churn rate

## Success Criteria

### Month 1
- ✅ 5+ deals published
- ✅ 50+ unlocks
- ✅ $350+ revenue
- ✅ <15% refund rate

### Month 3
- ✅ 10,000 monthly visitors
- ✅ 200+ unlocks
- ✅ $1,400+ revenue
- ✅ <10% refund rate
- ✅ 2%+ conversion rate

### Month 6
- ✅ 25,000 monthly visitors
- ✅ 500+ unlocks
- ✅ $3,500+ revenue
- ✅ Break even on marketing spend

## Emergency Procedures

### If Scanner Breaks
1. Check logs: `docker-compose logs scanner`
2. Verify API quotas not exceeded
3. Restart scanner: `docker-compose restart scanner`
4. Manual deal sourcing from FlyerTalk/SecretFlying

### If Airline Cancels Mass Bookings
1. Send immediate email to all affected customers
2. Process refunds automatically
3. Post transparency update on social media
4. Offer bonus credit for next deal

### If HubSpot Integration Fails
1. Switch to manual email delivery
2. Use Stripe direct for payments
3. Track unlocks in spreadsheet temporarily
4. Debug HubSpot API credentials

## Notes

- **Priority**: Speed is critical. Mistake fares last 2-48 hours.
- **Quality**: Only publish deals you'd book yourself.
- **Transparency**: Be upfront about risks (airline may cancel).
- **Customer Service**: Fast response to refund requests builds trust.

---

**Last Updated**: November 28, 2025  
**Next Review**: After soft launch (Week 4)
