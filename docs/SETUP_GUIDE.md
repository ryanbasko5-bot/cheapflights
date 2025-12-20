# FareGlitch Setup Guide

This guide will walk you through setting up the FareGlitch platform from scratch.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- API accounts:
  - Amadeus for Developers
  - Duffel (or Kiwi.com)
  - HubSpot Professional subscription
  - Slack workspace (for alerts)

## Week 1: API Setup and Scanner Development

### Step 1: Register for APIs

#### Amadeus for Developers
1. Go to https://developers.amadeus.com/register
2. Create a free account
3. Create a new app in the dashboard
4. Copy your **API Key** and **API Secret**
5. Start with **Test Environment** (5,000 free calls/month)

#### Duffel API
1. Go to https://duffel.com/signup
2. Create an account
3. Get your API token from the dashboard
4. Note: Duffel has generous free tier for testing

#### Alternative: Kiwi.com Tequila API
1. Go to https://tequila.kiwi.com/portal/getting-started
2. Request API access
3. Get your API key

### Step 2: Environment Setup

```bash
# Clone the repository
cd /workspaces/cheapflights

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Step 3: Configure Environment Variables

Edit `.env` with your API credentials:

```bash
# Amadeus
AMADEUS_API_KEY=your_actual_api_key
AMADEUS_API_SECRET=your_actual_secret
AMADEUS_ENV=test

# Duffel
DUFFEL_API_TOKEN=your_duffel_token

# HubSpot
HUBSPOT_API_KEY=your_hubspot_key
HUBSPOT_PORTAL_ID=your_portal_id

# Slack
SLACK_WEBHOOK_URL=your_slack_webhook
SLACK_CHANNEL=#fareglitch-alerts

# Database (for local development)
DATABASE_URL=postgresql://fareglitch:changeme@localhost:5432/fareglitch

# API Secret (generate a random string)
API_SECRET_KEY=$(openssl rand -hex 32)
```

### Step 4: Set Up Database

#### Option A: Docker (Recommended)
```bash
# Start PostgreSQL with Docker Compose
docker-compose up -d db

# Wait for database to be ready
sleep 10

# Initialize database
python -c "from src.utils.database import init_db; init_db()"
```

#### Option B: Local PostgreSQL
```bash
# Install PostgreSQL
# Ubuntu: sudo apt install postgresql
# Mac: brew install postgresql

# Create database
createdb fareglitch

# Initialize schema
python -c "from src.utils.database import init_db; init_db()"
```

### Step 5: Test Scanner

```bash
# Run scanner in test mode (won't send alerts or publish)
python -m src.scanner.main --test

# Check output for any errors
```

Expected output:
```
INFO - Starting scan of 25 origin airports...
INFO - Scanning routes from JFK...
INFO - Found 15 destinations from JFK
...
```

### Step 6: Configure Slack Alerts

1. Go to your Slack workspace
2. Create a channel: `#fareglitch-alerts`
3. Create an incoming webhook:
   - Go to https://api.slack.com/apps
   - Create New App → From scratch
   - Add "Incoming Webhooks" feature
   - Create webhook for `#fareglitch-alerts`
4. Add webhook URL to `.env`

### Step 7: Test Alert System

```bash
# Test Slack alerts
python -c "
from src.utils.alerts import AlertManager
import asyncio

async def test():
    alerts = AlertManager()
    await alerts.send_error_alert('Test alert from FareGlitch setup')

asyncio.run(test())
"
```

## Week 2: HubSpot Setup

### Step 8: Configure HubSpot Commerce Hub

1. **Enable Commerce Hub**:
   - Log into HubSpot
   - Go to Settings → Account Setup → Commerce Hub
   - Enable Commerce Hub (included in Professional)

2. **Create Custom Properties**:
   ```
   Contact Properties:
   - deal_unlock_timestamp (Date)
   - last_deal_unlocked (Single-line text)
   - total_deals_unlocked (Number)
   
   Product Properties:
   - deal_number (Single-line text)
   - deal_origin (Single-line text)
   - deal_destination (Single-line text)
   - deal_savings (Number)
   ```

3. **Set Up Payment Integration**:
   - Go to Commerce Hub → Payments
   - Connect Stripe account
   - Configure payment settings

### Step 9: Create Landing Page Template

1. Go to Marketing → Website → Templates
2. Create new template: "Deal Teaser Page"
3. Add modules:
   - Hero section with deal headline
   - Price comparison (crossed-out normal price)
   - Savings badge
   - "Unlock Details" CTA button
   - FAQ section
4. Use smart content to hide booking details
5. Embed payment link in CTA button

### Step 10: Create Email Templates

**Template 1: Deal Details Delivery**
```
Subject: CONFIDENTIAL: Your {{deal_number}} Flight Details

Hi there!

Thanks for unlocking {{deal_number}}! Here are your exclusive booking details:

🎯 Route: {{route_description}}
💰 Price: ${{mistake_price}} (Save ${{savings_amount}})
✈️ Airline: {{airline}}
📅 Travel Dates: {{travel_dates}}

🔗 BOOK NOW: {{booking_link}}

⚠️ IMPORTANT BOOKING TIPS:
1. Book immediately - mistake fares can be corrected within hours
2. Use incognito/private browsing
3. Clear cookies before searching
4. Book directly with airline when possible
5. Consider travel insurance

Questions? Reply to this email.

Happy travels!
The FareGlitch Team
```

**Template 2: Refund Confirmation**
```
Subject: Refund Processed - {{deal_number}}

We're sorry the airline canceled your fare for {{deal_number}}.

✅ Your ${{unlock_fee}} has been refunded
⏱️ Expect it in 5-7 business days

We'll notify you immediately when we find similar deals.
```

### Step 11: Create Workflows

#### Workflow 1: Deal Delivery
- **Trigger**: Contact property `deal_unlock_timestamp` is known
- **Actions**:
  1. Send "Deal Details Delivery" email (immediate)
  2. Add to list "Active Customers"
  3. Set lifecycle stage to "Customer"
  4. Wait 24 hours
  5. Send follow-up: "Did you book successfully?"

#### Workflow 2: Glitch Guarantee
- **Trigger**: Ticket created in "Refund Request" pipeline
- **Actions**:
  1. Send internal Slack notification
  2. Call webhook: `https://api.fareglitch.com/webhooks/process-refund`
  3. Wait for webhook response
  4. Send "Refund Confirmation" email
  5. Update ticket status to "Resolved"

## Week 3: Testing & Integration

### Step 12: Test Full Flow

```bash
# 1. Run scanner
python -m src.scanner.main --test --origins JFK LAX

# 2. Start API server
uvicorn src.api.main:app --reload

# 3. In another terminal, test API
curl http://localhost:8000/deals/active

# 4. Test unlock flow (with mock payment)
curl -X POST http://localhost:8000/deals/DEAL#001/unlock \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "payment_id": "test_payment_123"
  }'
```

### Step 13: Configure Webhooks

In HubSpot:
1. Go to Settings → Integrations → Webhooks
2. Create webhook subscriptions:
   - **Payment Success**: POST to `https://api.fareglitch.com/webhooks/hubspot/payment-success`
   - **Refund Request**: POST to `https://api.fareglitch.com/webhooks/hubspot/refund-request`

### Step 14: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Week 4: Soft Launch

### Step 15: Find Manual Deal

For your first test deal:
1. Visit FlyerTalk forums: https://www.flyertalk.com/forum/mileage-run-discussion-372/
2. Check SecretFlying: https://www.secretflying.com/
3. Find a confirmed mistake fare
4. Manually create deal in database:

```python
from src.models.database import Deal, DealStatus
from src.utils.database import get_db_session
from datetime import datetime, timedelta

db = next(get_db_session())

deal = Deal(
    deal_number="DEAL#001",
    origin="JFK",
    destination="NRT",
    route_description="New York to Tokyo",
    normal_price=2500.0,
    mistake_price=400.0,
    savings_amount=2100.0,
    savings_percentage=0.84,
    currency="USD",
    cabin_class="business",
    airline="ANA",
    status=DealStatus.VALIDATED,
    teaser_headline="Business Class Glitch: NYC to Tokyo",
    teaser_description="Fly ANA Business Class for 84% off",
    booking_link="https://www.google.com/flights/...",
    unlock_fee=7.0,
    expires_at=datetime.now() + timedelta(hours=48)
)

db.add(deal)
db.commit()
```

### Step 16: Publish First Deal

```bash
# Publish to HubSpot
curl -X POST http://localhost:8000/admin/deals/1/publish
```

### Step 17: Monitor & Iterate

- Watch Slack for alerts
- Monitor HubSpot workflows
- Check database for unlocks
- Gather user feedback
- Adjust pricing/messaging

## Production Deployment

### Option 1: Docker (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Scale scanner if needed
docker-compose up -d --scale scanner=2
```

### Option 2: Manual Deployment

```bash
# Set production environment
export AMADEUS_ENV=production

# Start API with gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Start scanner as background service
nohup python -m src.scanner.main --interval 3600 &
```

## Troubleshooting

### Scanner Issues
- **No anomalies found**: Adjust `PRICE_DROP_THRESHOLD` in `.env`
- **API rate limits**: Increase `SCAN_INTERVAL_SECONDS`
- **Database errors**: Check `DATABASE_URL` connection string

### HubSpot Issues
- **Workflow not triggering**: Check property mappings
- **Payment failed**: Verify Stripe integration
- **Email not sending**: Check email template active status

### API Issues
- **500 errors**: Check logs with `docker-compose logs api`
- **Database connection**: Verify PostgreSQL is running
- **CORS errors**: Update `allow_origins` in `src/api/main.py`

## Next Steps

1. **Marketing Setup**:
   - Create social media accounts
   - Design brand assets
   - Build landing page
   - Set up Facebook/Instagram ads

2. **Automation**:
   - Schedule scanner with cron
   - Set up monitoring (Sentry, Datadog)
   - Configure backups

3. **Scaling**:
   - Add more origin airports
   - Implement caching (Redis)
   - Set up CDN for static assets

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Run tests: `pytest tests/ -v`
- Review API docs: http://localhost:8000/docs
