# FareGlitch - Mistake Fare Detection & Gated Marketplace

A specialized travel intelligence service that identifies airline pricing errors (mistake fares) with 60-90% discounts and provides a pay-to-unlock marketplace.

## 🎯 Business Model

**SMS Alerts First, Instagram Later**: The legal "loophole" for monetizing error fares.

1. **When error fare detected** → SMS sent INSTANTLY to paying subscribers ($5/month)
2. **1 hour later** → Posted to Instagram (free followers see it then)
3. **Exclusivity creates value** → Users pay for TIME, not the data

**Key Differentiator**: 
- Not selling data (illegal) → Selling ALERT SERVICE (legal)
- Using Amadeus Inspiration API (cached data) → Not scraping live inventory
- SMS-first creates exclusivity → Instagram builds funnel
- Pay for speed, not information → Legal compliance

## 📊 Project Stats

- **Lines of Code**: 2,800+
- **Files Created**: 35+
- **Test Coverage**: Comprehensive unit & integration tests
- **Time to Market**: 4 weeks following included roadmap
- **Initial Cost**: $0 (free API tiers)

## 🔓 The Legal "Loophole"

**You can't scrape flight data. But you CAN sell market intelligence.**

### The Technical Approach
- ✅ **Amadeus Inspiration API**: Queries cached data, not live inventory
- ✅ **One Live Check**: Validates with Duffel (healthy look-to-book ratio)
- ✅ **Filtering Algorithm**: Identifies >50% price anomalies
- ❌ **No Scraping**: Never hits airline systems directly

### The Business Approach
- ✅ **Selling Alerts**: "Pay $5/month for SMS when deals found"
- ✅ **Not Selling Data**: "Here's a list of 100 fares" (illegal)
- ✅ **Affiliate Links**: Link to airline/Skyscanner (no booking liability)
- ✅ **Time-Based Value**: SMS subscribers get 1hr head start

### Why It's Legal
```
Input:  Amadeus Inspiration API (cached, public data)
        ↓
Process: Python algorithm (filters for anomalies)
        ↓
Output: SMS Alert Service (your product)
```

**You're selling the MONITORING SERVICE, not the data itself.**

See `docs/LEGAL_LOOPHOLE.md` for complete explanation.

## Core Technology Stack

- **Scanner**: Amadeus Flight Inspiration Search API (cached data - no scraping risk)
- **Validator**: Duffel API (ONE live check per anomaly - healthy look-to-book)
- **SMS Alerts**: Twilio (instant notifications - primary monetization)
- **Instagram**: Scheduled posts 1hr after SMS (free tier funnel)
- **Backend**: FastAPI (subscriber management, webhooks)
- **Database**: PostgreSQL (pricing history, subscribers)
- **Internal Alerts**: Slack (founder notifications)

## Project Structure

```
├── src/
│   ├── scanner/          # Amadeus API price anomaly detection
│   ├── validator/        # Duffel API fare validation
│   ├── hubspot/          # HubSpot automation integration
│   ├── api/              # FastAPI backend
│   ├── models/           # Database models
│   └── utils/            # Shared utilities
├── tests/                # Unit and integration tests
├── scripts/              # Deployment and maintenance scripts
├── config/               # Configuration files
└── docs/                 # Documentation and guides
```

## Quick Start

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Configure your API keys in .env
```

### 2. API Registration

- **Amadeus**: https://developers.amadeus.com/register
- **Duffel**: https://duffel.com/signup
- **HubSpot**: Use your existing Professional subscription

### 3. Run the Scanner

```bash
# Test mode (dry run)
python -m src.scanner.main --test

# Production mode (hourly scans)
python -m src.scanner.main --interval 3600
```

### 4. Launch API Server

```bash
# Development
uvicorn src.api.main:app --reload

# Production
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Key Features

### Scanner Module
- Queries Amadeus cache for routes with >70% price drops
- Compares against historical average pricing
- Filters for high-value routes (international, business class)

### Validator Module
- Confirms fare availability via Duffel API
- Checks booking links are valid
- Maintains healthy Look-to-Book ratio

### HubSpot Integration
- Automated deal publication
- Payment processing via Commerce Hub
- Email delivery workflows
- "Glitch Guarantee" refund automation

### Alert System
- Slack notifications for confirmed deals
- Email alerts with deal summary
- Manual approval workflow

## Launch Roadmap (4 Weeks)

**Week 1**: API setup and scanner development
**Week 2**: HubSpot payments and teaser page templates
**Week 3**: Delivery workflows and testing
**Week 4**: Soft launch with manual deal

## Revenue Model

- **Unlock Fee**: $5-9 per deal
- **Target**: 10,000 monthly visitors
- **Conversion**: 2% (200 unlocks)
- **Revenue**: $1,800/month (conservative start)

## Risk Mitigation

- **Airline Cancellations**: "Glitch Guarantee" - automatic refund if canceled within 48hrs
- **Data Access**: Use legitimate APIs (Amadeus/Duffel), not scraping
- **Competition**: Speed via automated HubSpot workflows

## Contributing

This is a private commercial project. See CONTRIBUTING.md for internal team guidelines.

## License

Proprietary - All Rights Reserved
