# FareGlitch - Quick Start Guide

## 🎯 What is FareGlitch?

FareGlitch is a mistake fare detection platform that finds airline pricing errors (60-90% discounts) and monetizes them through a pay-to-unlock model ($5-9 per deal) instead of subscriptions.

## 🚀 5-Minute Quickstart

### 1. Clone and Setup

```bash
cd /workspaces/cheapflights

# Run automated setup
./scripts/setup.sh

# This will:
# ✓ Check Python 3.11+
# ✓ Create virtual environment
# ✓ Install dependencies
# ✓ Copy .env template
# ✓ Start PostgreSQL (if Docker available)
```

### 2. Configure API Keys

Edit `.env` with your credentials:

```bash
# Get free API keys:
# - Amadeus: https://developers.amadeus.com/register
# - Duffel: https://duffel.com/signup
# - Slack: https://api.slack.com/messaging/webhooks

nano .env
```

Minimum required:
```env
AMADEUS_API_KEY=your_key_here
AMADEUS_API_SECRET=your_secret_here
HUBSPOT_API_KEY=your_hubspot_key
API_SECRET_KEY=$(openssl rand -hex 32)
```

### 3. Initialize Database

```bash
./scripts/init_db.sh

# Choose 'y' to load sample data for testing
```

### 4. Test the Scanner

```bash
# Activate virtual environment
source venv/bin/activate

# Run scanner in test mode
python -m src.scanner.main --test --origins JFK LAX

# Expected output:
# 🔍 Starting scan of 2 origin airports...
# INFO - Scanning routes from JFK...
# ✅ Scan complete
```

### 5. Start the API

```bash
# Terminal 1: Start API server
uvicorn src.api.main:app --reload

# Terminal 2: Test API
curl http://localhost:8000/deals/active

# View interactive docs
open http://localhost:8000/docs
```

## 📚 Key Concepts

### The Business Model

**Traditional Model (Going, Jack's Flight Club)**:
- Monthly subscription: $49/month
- Send all deals via email
- Low per-user revenue

**FareGlitch Model**:
- No subscription
- Pay per deal: $5-9 to unlock
- 10x higher revenue per deal
- Viral potential (social sharing)

### The Tech Stack

```
Amadeus API → Price Scanner → Anomaly Detector
                    ↓
            Duffel Validator
                    ↓
              Slack Alert
                    ↓
         Manual Approval (You)
                    ↓
         HubSpot Publication
                    ↓
         Landing Page + Payment
                    ↓
         Automated Email Delivery
```

### The Workflow

1. **Every hour**: Scanner queries Amadeus cached prices
2. **If >70% drop detected**: Validator confirms via Duffel
3. **If validated**: Slack alert sent to you
4. **You approve**: Deal published to HubSpot
5. **User finds deal**: Views teaser on landing page
6. **User pays $7**: HubSpot processes payment
7. **Instant delivery**: Workflow emails booking link
8. **If airline cancels**: Automatic refund (Glitch Guarantee)

## 🎓 Tutorial: Your First Deal

### Step 1: Create a Test Deal

```bash
python scripts/create_deal.py
```

Output:
```
✅ Created DEAL#001
   Route: New York (JFK) to Tokyo (NRT)
   Price: $420 (Save $2080)
   Expires: 2025-11-30 10:00:00
```

### Step 2: View via API

```bash
curl http://localhost:8000/deals/active | jq
```

### Step 3: Simulate Unlock

```bash
curl -X POST http://localhost:8000/deals/DEAL#001/unlock \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "payment_id": "test_payment_123"
  }' | jq
```

### Step 4: Check Database

```bash
psql -h localhost -U fareglitch -d fareglitch -c "SELECT deal_number, total_unlocks, total_revenue FROM deals;"
```

## 🔧 Development Workflow

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_scanner.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/
```

### Database Management

```bash
# Reset database
python -c "from src.models.database import Base; from src.utils.database import engine; Base.metadata.drop_all(engine)"
./scripts/init_db.sh

# Backup
pg_dump fareglitch > backup.sql

# Restore
psql fareglitch < backup.sql
```

## 🐳 Docker Deployment

### Local Development

```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up api

# View logs
docker-compose logs -f scanner

# Rebuild
docker-compose up --build
```

### Production Deployment

```bash
# Set production env
export AMADEUS_ENV=production

# Start detached
docker-compose up -d

# Scale scanner
docker-compose up -d --scale scanner=3

# Monitor
docker-compose ps
docker-compose logs -f
```

## 📊 Monitoring

### Check Scanner Status

```bash
# View recent scans
psql fareglitch -c "SELECT * FROM scan_logs ORDER BY started_at DESC LIMIT 5;"

# Check anomaly detection rate
psql fareglitch -c "SELECT AVG(anomalies_found) FROM scan_logs WHERE started_at > NOW() - INTERVAL '24 hours';"
```

### API Health

```bash
# Health check
curl http://localhost:8000/

# Check active deals
curl http://localhost:8000/deals/active | jq 'length'

# Monitor logs
tail -f logs/api.log
```

## 🆘 Troubleshooting

### Scanner Not Finding Deals

**Issue**: `anomalies_found: 0` in every scan

**Solutions**:
1. Lower threshold: `PRICE_DROP_THRESHOLD=0.50` (50% instead of 70%)
2. Lower minimum savings: `MIN_SAVINGS_AMOUNT=100`
3. Add more origins: Edit `MAJOR_HUBS` in `src/scanner/amadeus_client.py`
4. Check Amadeus API quota: Visit developer dashboard

### Database Connection Failed

**Issue**: `psycopg2.OperationalError: could not connect`

**Solutions**:
```bash
# Check PostgreSQL is running
docker-compose ps db

# Restart database
docker-compose restart db

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

### HubSpot Integration Issues

**Issue**: Deal not appearing in HubSpot after publish

**Solutions**:
1. Verify API key: Check HubSpot → Settings → Integrations → API Key
2. Check product was created: HubSpot → Commerce Hub → Products
3. View API logs: `docker-compose logs api | grep hubspot`

### Slack Alerts Not Working

**Issue**: No Slack notifications

**Solutions**:
1. Test webhook manually:
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test alert"}'
```
2. Check `.env` has correct webhook URL
3. Verify channel exists and bot has permissions

## 📈 Scaling Up

### Week 1-2: Manual Operation

- Run scanner every 6 hours manually
- Manually approve each deal
- Target: 1-2 deals/week

### Week 3-4: Semi-Automated

- Enable auto-publish: `ENABLE_AUTO_PUBLISH=true`
- Run scanner every 1 hour: `--interval 3600`
- Target: 5-10 deals/week

### Month 2+: Full Automation

- Deploy scanner to cloud (AWS/GCP)
- Set up monitoring (Sentry, Datadog)
- Add more origin airports (100+)
- Implement ML-based price prediction
- Target: 20-50 deals/week

## 🎯 Business Metrics

### Key Performance Indicators

Track these metrics:

```sql
-- Daily unlocks
SELECT DATE(unlocked_at), COUNT(*), SUM(unlock_fee_paid)
FROM deal_unlocks
GROUP BY DATE(unlocked_at)
ORDER BY DATE(unlocked_at) DESC;

-- Conversion rate
SELECT 
  deal_number,
  total_unlocks,
  -- Would need page view tracking for accurate conversion
  total_unlocks::float / NULLIF(page_views, 0) as conversion_rate
FROM deals;

-- Refund rate
SELECT 
  COUNT(*) FILTER (WHERE payment_status = 'refunded')::float / 
  COUNT(*) as refund_rate
FROM deal_unlocks;

-- Average deal value
SELECT AVG(unlock_fee_paid) FROM deal_unlocks;
```

### Target Metrics (Conservative)

- **Monthly Visitors**: 10,000
- **Conversion Rate**: 2%
- **Unlocks/Month**: 200
- **Avg Unlock Fee**: $7
- **Monthly Revenue**: $1,400
- **Refund Rate**: <10%

## 📞 Support

- **Documentation**: `/docs` folder
- **API Reference**: http://localhost:8000/docs
- **Issues**: Check logs first
- **Community**: (Would link to Discord/Slack)

## 🚦 Next Steps

1. ✅ Complete setup
2. ✅ Test scanner
3. 📋 Register for production APIs
4. 📋 Set up HubSpot workflows (see `docs/HUBSPOT_SETUP.md`)
5. 📋 Create landing page templates
6. 📋 Configure payment processing
7. 📋 Launch soft test with manual deal
8. 📋 Gather feedback and iterate
9. 📋 Scale to production

## 🎉 You're Ready!

The platform is now fully operational. Start by:

```bash
# Terminal 1: Run scanner
python -m src.scanner.main --interval 3600

# Terminal 2: Run API
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Monitor Slack for alerts!
```

Good luck building FareGlitch! 🚀✈️
