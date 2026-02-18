# ⚠️ CRITICAL: Pricing Accuracy Guide

## THE PROBLEM

We were showing **FAKE** "normal prices" that don't match reality:
- Claimed: "Sydney → Bali normally A$900"
- **ACTUAL Google Flights**: A$402-$635

This destroys credibility and could be considered **false advertising**.

## THE SOLUTION

### Option 1: Manual Verification (RECOMMENDED for now)
Before creating ANY deal:

1. **Go to Google Flights** for the route
2. **Check prices for 5-10 different dates** (1-3 months out)
3. **Use the HIGHEST price you see** as "normal_price"
4. **Use the LOWEST price you see** as "deal_price"
5. **Only create deal if savings >20%**

Example:
```
Sydney → Bali checked on Google Flights:
- Feb 12: A$431
- Feb 18: A$444
- Mar 5:  A$593
- Mar 12: A$521
- Apr 3:  A$489

CONSERVATIVE approach:
- normal_price: A$635 (higher than max seen, to be safe)
- deal_price: A$431 (lowest currently available)
- savings: 32% (REAL, VERIFIABLE)
```

### Option 2: Use Amadeus Historical API (Future)
```python
# Get 30-day price history
response = amadeus.analytics.itinerary_price_metrics.get(
    originIataCode='SYD',
    destinationIataCode='DPS',
    departureDate='2025-02-12'
)

# Use quartile3 (75th percentile) as "normal"
normal_price = response.data[0]['priceMetrics'][0]['quartiles'][2]['amount']
```

### Option 3: Track Our Own Data
Build a `price_history` table:
```python
class PriceHistory(Base):
    route = Column(String)  # "SYD-DPS"
    price = Column(Float)
    currency = Column(String)
    recorded_at = Column(DateTime)
    source = Column(String)  # "amadeus", "google", "manual"
```

Then calculate 30-day average from OUR data.

## CURRENT WORKFLOW

Until automated:

1. **Find potential deal** (Amadeus API shows cheap price)
2. **Manually verify on Google Flights**
3. **Document prices seen**:
   ```
   Route: SYD → DPS
   Date checked: 2025-12-21
   Prices found: A$431, A$444, A$593
   Typical range: A$450-600
   Conservative "normal": A$635
   Current best: A$431
   Savings: 32%
   ```
4. **Create deal with DOCUMENTED prices**
5. **Keep screenshot** of Google Flights as proof

## RED FLAGS TO AVOID

❌ **NEVER do this:**
- Guess "normal price" based on distance
- Use outdated price data (>7 days old)
- Inflate "normal price" to make savings look bigger
- Compare to business class prices when showing economy

✅ **ALWAYS do this:**
- Check Google Flights same cabin class
- Use conservative estimates (round UP for normal price)
- Document where numbers come from
- Include date ranges in deal description
- Link to Google Flights so users can verify

## LEGAL PROTECTION

Add disclaimers:
- "Typical price based on recent searches"
- "Deal price verified available on [date]"
- "Prices subject to change"
- "Savings compared to average fares on this route"

## AUTOMATION PLAN

Phase 1 (Now): Manual verification
Phase 2 (Week 2): Amadeus historical data
Phase 3 (Month 2): Our own price tracking database
Phase 4 (Month 3): ML model to predict "normal" prices

## MISTAKE FARE STANDARDS

For mistake fares (>50% off), even STRICTER rules:
- Must verify airline hasn't pulled the fare
- Must screenshot the booking page
- Must note if fare class is restricted
- Must warn users "may not be honored"
- Must track if airline confirmed/canceled

## Example: Accurate Deal Creation

```python
# WRONG - Made up numbers
deal = Deal(
    normal_price=900,  # GUESSED!
    mistake_price=249,  # From Amadeus
    savings_percentage=72  # FALSE!
)

# RIGHT - Verified numbers
deal = Deal(
    normal_price=635,  # Verified on Google Flights 2025-12-21
    mistake_price=431,  # Currently available (checked same day)
    savings_percentage=32.1,  # ACCURATE!
    teaser_description="Fly for A$431 (typical: A$635 based on Dec 2025 searches)"
)
```

## Tracking Template

Create `price_verification_log.md`:
```markdown
## SYD → DPS (Sydney to Bali)
- **Date checked**: 2025-12-21
- **Prices found**: A$431, A$444, A$593, A$489
- **Range**: A$431-$593
- **Conservative normal**: A$635
- **Source**: Google Flights manual check
- **Deal created**: VD001
- **Savings claimed**: 32%
```

## NEVER FORGET

**Users will click the link and see the REAL prices on Google Flights.**

If our "normal price" is way higher than what they see, we lose ALL credibility.

**Better to show 20% savings that's REAL than 70% savings that's FAKE.**
