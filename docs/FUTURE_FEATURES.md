# Future Feature Roadmap

**Status**: NOT IMPLEMENTED - Ideas for future development

---

## Feature 1: The "Deal Radar" (The Lead Magnet)

### Goal
Capture users with eye-catching low prices on a public dashboard.

### User Experience
A dashboard showing **"Top 50 Deals from Sydney right now"** - no login required, acts as the hook to get people onto your site.

### Technical Implementation

**API**: Amadeus Flight Inspiration Search

**Query Example**:
```python
# Flight Inspiration Search
params = {
    "origin": "SYD",
    "maxPrice": 800,
    # No specific dates - gets all cheap destinations
}

response = amadeus.shopping.flight_destinations.get(**params)
```

**Output Example**:
```json
[
  {"destination": "DPS", "price": 400, "departure_date": "2025-12-15"},
  {"destination": "NAN", "price": 550, "departure_date": "2025-12-20"},
  {"destination": "NRT", "price": 700, "departure_date": "2026-01-10"}
]
```

**Display on Site**:
```
🌏 TOP 50 DEALS FROM SYDNEY RIGHT NOW

🇮🇩 Bali          $400  →  Book Now
🇫🇯 Fiji          $550  →  Book Now
🇯🇵 Tokyo         $700  →  Book Now
🇹🇭 Bangkok       $450  →  Book Now
🇳🇿 Auckland      $320  →  Book Now
...
```

### Why This Works (The "Loophole")
- Uses **cached aggregated data** from Amadeus
- Very low quota cost
- Not live scraping individual airlines
- Perfect for public-facing "inspiration" content
- Acts as lead magnet before SMS subscription

### Monetization
- **Free Tier**: See the radar, click affiliate links
- **Conversion**: "Want these deals 1hr before we post them? SMS Alerts →"

---

## Feature 2: The "AI Audit" (The Value Add)

### Goal
Prevent **"Deal Anxiety"** - users see a $400 Bali flight but are scared to book because:
- Is this actually cheap?
- Is it a scam airline?
- Are the layovers terrible?

### User Experience
Next to each price, show an **"AI Grade"**:

```
🟢 Grade A (Buy Now)
   ↳ Historic low price
   ↳ Direct flight
   ↳ 95% confidence this is real
   
🟡 Grade B (Caution)
   ↳ Good price (20% below average)
   ↳ 8hr layover in Dubai
   ↳ Budget airline (no meals)
   
🔴 Grade C (Wait)
   ↳ Price dropping trend detected
   ↳ Better deals likely next week
   ↳ 60% confidence
```

### Technical Implementation

#### 2.1: Price Analysis API

**API**: Amadeus Flight Price Analysis

**Query**:
```python
# Check if $400 to Bali is actually cheap
response = amadeus.analytics.itinerary_price_metrics.get(
    originIataCode='SYD',
    destinationIataCode='DPS',
    departureDate='2025-12-15',
    currencyCode='AUD'
)

# Returns:
{
  "data": {
    "priceMetrics": [
      {
        "amount": "400.00",
        "quartileRanking": "MINIMUM"  # This is bottom 25%!
      }
    ]
  }
}
```

**Interpretation**:
- `MINIMUM` → 🟢 Grade A (Historic low)
- `MEDIUM` → 🟡 Grade B (Average)
- `MAXIMUM` → 🔴 Grade C (Overpriced)

#### 2.2: Flight Choice Prediction API

**API**: Amadeus Flight Choice Prediction

**Purpose**: Predict if humans would actually book this flight (filters out bad layovers, terrible airlines)

**Query**:
```python
# Is this flight actually good, or just cheap?
response = amadeus.shopping.flight_offers.prediction.post(
    flight_offers=[flight_offer_object]
)

# Returns:
{
  "data": [
    {
      "id": "1",
      "choiceProbability": "0.92"  # 92% chance humans choose this
    }
  ]
}
```

**Interpretation**:
- `> 0.80` → 🟢 Great flight (direct, good times, reputable airline)
- `0.50 - 0.80` → 🟡 Acceptable (long layover, budget airline)
- `< 0.50` → 🔴 Avoid (terrible connections, overnight layovers)

#### 2.3: Combined Grading Algorithm

```python
def calculate_ai_grade(origin, destination, price, flight_details):
    """
    Combines price analysis + choice prediction into single grade
    """
    # Step 1: Check historical price
    price_metrics = amadeus.analytics.itinerary_price_metrics.get(
        originIataCode=origin,
        destinationIataCode=destination,
        departureDate=flight_details['departure_date']
    )
    
    price_quartile = price_metrics['data']['priceMetrics'][0]['quartileRanking']
    
    # Step 2: Check if humans would book it
    choice_prediction = amadeus.shopping.flight_offers.prediction.post(
        flight_offers=[flight_details]
    )
    
    choice_probability = float(choice_prediction['data'][0]['choiceProbability'])
    
    # Step 3: Calculate grade
    if price_quartile == "MINIMUM" and choice_probability > 0.8:
        return {
            "grade": "A",
            "emoji": "🟢",
            "message": "BUY NOW - Historic low + Great flight",
            "confidence": 95
        }
    
    elif price_quartile in ["MINIMUM", "MEDIUM"] and choice_probability > 0.5:
        return {
            "grade": "B",
            "emoji": "🟡",
            "message": "CAUTION - Good price but check details",
            "confidence": 70
        }
    
    else:
        return {
            "grade": "C",
            "emoji": "🔴",
            "message": "WAIT - Better deals coming",
            "confidence": 40
        }
```

### Visual Display

```
SYD → DPS (Bali)
$400  🟢 Grade A

✅ Bottom 5% of historical prices
✅ 92% predicted booking probability
✅ Direct flight (Jetstar)
⚠️ Budget airline (no meals)

BOOK NOW: [Affiliate Link]
```

### Monetization Tiers

| Tier | Access | Price |
|------|--------|-------|
| **Free** | See prices only, no grades | $0 |
| **Smart Member** | AI Grades + Trend Alerts | $5/mo |
| **One-Off Audit** | "Grade this flight I found" | $2/audit |

---

## Feature 3: The "Smart Watchdog" (Retention)

### Goal
Keep users coming back. If they view a deal but don't book, let them "Watch" it and get alerts only when:
- Price drops further
- Price about to spike (book now!)

### User Experience

**User Action**:
```
User sees: "SYD → Tokyo $700"
User clicks: "👁️ Watch This Deal"
```

**System Action**:
```python
# Add to watchlist
watchlist = Watchlist(
    user_id=user.id,
    origin="SYD",
    destination="NRT",
    current_price=700,
    alert_threshold_drop=50,  # Alert if drops by $50
    alert_threshold_spike=10  # Alert if about to rise $10
)
db.add(watchlist)
```

### Technical Implementation

#### 3.1: Flight Price Prediction API

**API**: Amadeus Flight Price Analysis (Time Series)

**Purpose**: Predict if price will go up or down in next 7 days

**Query**:
```python
# Will this Tokyo flight get cheaper?
response = amadeus.analytics.itinerary_price_metrics.get(
    originIataCode='SYD',
    destinationIataCode='NRT',
    departureDate='2026-01-10'
)

# Check trend
if response['data']['priceMetrics'][0]['quartileRanking'] == 'MINIMUM':
    trend = "RISING_SOON"  # Price at bottom, likely to go up
else:
    trend = "STABLE"
```

**Note**: Amadeus doesn't provide explicit "will rise/fall" predictions, but you can infer:
- If price is at `MINIMUM` quartile → Likely to rise (book now)
- If price is at `MAXIMUM` quartile → Likely to fall (wait)

#### 3.2: Watchdog Monitoring Script

```python
# Run this as cron job every 6 hours
def check_watchlists():
    watched_deals = db.query(Watchlist).filter(
        Watchlist.is_active == True
    ).all()
    
    for watch in watched_deals:
        # Check current price
        current_offers = amadeus.shopping.flight_offers_search.get(
            originLocationCode=watch.origin,
            destinationLocationCode=watch.destination,
            departureDate=watch.departure_date,
            adults=1
        )
        
        new_price = float(current_offers['data'][0]['price']['total'])
        price_change = watch.current_price - new_price
        
        # Price dropped significantly?
        if price_change >= watch.alert_threshold_drop:
            send_email(
                to=watch.user.email,
                subject=f"🚨 {watch.destination} dropped by ${price_change}!",
                body=f"Was ${watch.current_price}, now ${new_price}"
            )
            
            # Update watchlist
            watch.current_price = new_price
            watch.last_alerted_at = datetime.now()
        
        # Check if price about to spike
        price_metrics = amadeus.analytics.itinerary_price_metrics.get(
            originIataCode=watch.origin,
            destinationIataCode=watch.destination,
            departureDate=watch.departure_date
        )
        
        if price_metrics['data']['priceMetrics'][0]['quartileRanking'] == 'MINIMUM':
            # Price at historic low, likely to rise
            send_email(
                to=watch.user.email,
                subject=f"⚠️ {watch.destination} price rising soon!",
                body=f"Current price ${new_price} is at historic low. Book now!"
            )
        
        db.commit()
```

### Email Alert Examples

**Price Drop Alert**:
```
Subject: 🚨 Tokyo dropped by $50!

Hey Ryan,

Great news! The flight you're watching just got cheaper:

SYD → Tokyo (NRT)
Was: $700
Now: $650
You Save: $50

This is now in the bottom 10% of historical prices.

[BOOK NOW] [Stop Watching]
```

**Price Spike Warning**:
```
Subject: ⚠️ Tokyo price rising soon!

Hey Ryan,

Our AI detects the flight you're watching is about to get expensive:

SYD → Tokyo (NRT)
Current: $650
Predicted next week: $750+

This is a historic low. Book now before it rises!

[BOOK NOW] [Stop Watching]
```

### Database Schema

```sql
CREATE TABLE watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    origin VARCHAR(3) NOT NULL,
    destination VARCHAR(3) NOT NULL,
    departure_date DATE NOT NULL,
    current_price DECIMAL(10,2),
    alert_threshold_drop DECIMAL(10,2) DEFAULT 50.00,
    alert_threshold_spike DECIMAL(10,2) DEFAULT 10.00,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_alerted_at TIMESTAMP,
    alerts_sent INTEGER DEFAULT 0
);
```

---

## Visual Architecture (The Full Flow)

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: INSPIRATION (Broad Search)                    │
│  API: Flight Inspiration Search                         │
│  Input: "SYD, Max $800"                                 │
│  Output: 200 destinations                               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: FILTER (Remove Trash)                        │
│  Python Script                                          │
│  Rules: Remove 2+ stops, bad airlines, ghost fares     │
│  Output: 50 "candidates"                               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: INTELLIGENCE (AI Grading)                    │
│  API: Price Analysis + Choice Prediction               │
│  Output: Each deal gets A/B/C grade + confidence       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 4: PRESENTATION (User Dashboard)                │
│  Website: "Top 50 Deals from Sydney"                   │
│  Display: Price + AI Grade + Affiliate Link            │
└─────────────────────────────────────────────────────────┘
```

---

## Monetization Strategy (The Hybrid Model)

| Tier | What User Gets | How You Make Money | Price |
|------|---------------|-------------------|-------|
| **Free User** | Access to "The Radar" (raw list of cheap flights)<br>Standard affiliate links | Affiliate commission (Skyscanner/Kayak) when they click | $0 |
| **Smart Member** | ✅ AI Grades (See if it's a "Good Deal")<br>✅ Trend Alerts ("Price dropping soon")<br>✅ Zero Ghost Fares (Live verification)<br>✅ Watchdog alerts | Subscription revenue (recurring monthly) | **$5/mo** |
| **One-Off Audit** | "Paste a flight you found on Google.<br>Our AI will grade it." | Micro-transactions | **$2/audit** |

### Revenue Projections

**Scenario**: 10,000 monthly visitors

```
Free Users (80%):    8,000 users
  - Affiliate clicks: 800 (10% CTR)
  - Revenue @$5/click: $4,000/mo

Smart Members (3%):  300 users
  - Subscription revenue: $1,500/mo

One-Off Audits (2%): 200 users
  - Audit revenue: $400/mo

Total Monthly Revenue: $5,900
```

---

## Technical Implementation (Golden Script)

### The Complete Flow

```python
import amadeus
from datetime import datetime, timedelta

class DealRadarWithAI:
    """
    Combines Inspiration API (find deals) with Analysis APIs (grade them)
    """
    
    def __init__(self):
        self.amadeus = amadeus.Client(
            client_id='YOUR_API_KEY',
            client_secret='YOUR_API_SECRET'
        )
    
    def find_and_grade_deals(self, origin: str, max_price: int):
        """
        Step 1: Find cheap destinations (Inspiration API)
        Step 2: Grade each deal (Analysis APIs)
        """
        print(f"🔍 Searching for deals from {origin} under ${max_price}...")
        
        # STEP 1: Get inspiration (cached data)
        inspiration = self.amadeus.shopping.flight_destinations.get(
            origin=origin,
            maxPrice=max_price
        )
        
        candidates = inspiration.data
        print(f"✅ Found {len(candidates)} destinations\n")
        
        graded_deals = []
        
        for candidate in candidates[:10]:  # Grade top 10
            destination = candidate['destination']
            price = float(candidate['price']['total'])
            departure_date = candidate['departureDate']
            
            print(f"📊 Analyzing {origin} → {destination} (${price})...")
            
            # STEP 2: Grade the deal
            grade = self._grade_deal(origin, destination, departure_date, price)
            
            graded_deals.append({
                "origin": origin,
                "destination": destination,
                "price": price,
                "departure_date": departure_date,
                "grade": grade
            })
            
            print(f"   {grade['emoji']} Grade {grade['grade']}: {grade['message']}\n")
        
        return graded_deals
    
    def _grade_deal(self, origin: str, destination: str, date: str, price: float):
        """
        Combine price analysis + choice prediction into single grade
        """
        try:
            # Check 1: Is this price historically good?
            price_metrics = self.amadeus.analytics.itinerary_price_metrics.get(
                originIataCode=origin,
                destinationIataCode=destination,
                departureDate=date,
                currencyCode='AUD'
            )
            
            quartile = price_metrics.data[0]['priceMetrics'][0]['quartileRanking']
            
            # Check 2: Would humans actually book this?
            # (Requires full flight offer, simplified here)
            choice_probability = 0.85  # Mock value
            
            # Grade logic
            if quartile == "MINIMUM" and choice_probability > 0.8:
                return {
                    "grade": "A",
                    "emoji": "🟢",
                    "message": "BUY NOW - Historic low + Great flight",
                    "confidence": 95
                }
            elif quartile in ["MINIMUM", "MEDIUM"]:
                return {
                    "grade": "B",
                    "emoji": "🟡",
                    "message": "CAUTION - Good price, check details",
                    "confidence": 70
                }
            else:
                return {
                    "grade": "C",
                    "emoji": "🔴",
                    "message": "WAIT - Better deals likely",
                    "confidence": 40
                }
        
        except Exception as e:
            return {
                "grade": "?",
                "emoji": "⚪",
                "message": "Unable to grade",
                "confidence": 0
            }
    
    def generate_dashboard(self, graded_deals):
        """
        Output HTML/JSON for dashboard display
        """
        print("\n" + "="*60)
        print("🌏 TOP DEALS FROM SYDNEY (AI GRADED)")
        print("="*60 + "\n")
        
        for deal in sorted(graded_deals, key=lambda x: x['grade']['grade']):
            print(f"{deal['grade']['emoji']} Grade {deal['grade']['grade']} | "
                  f"{deal['origin']} → {deal['destination']}")
            print(f"   ${deal['price']} | {deal['departure_date']}")
            print(f"   {deal['grade']['message']}")
            print(f"   Confidence: {deal['grade']['confidence']}%\n")


# USAGE
if __name__ == "__main__":
    radar = DealRadarWithAI()
    
    # Find and grade deals from Sydney under $800
    deals = radar.find_and_grade_deals(origin="SYD", max_price=800)
    
    # Display on dashboard
    radar.generate_dashboard(deals)
```

### Expected Output

```
🔍 Searching for deals from SYD under $800...
✅ Found 47 destinations

📊 Analyzing SYD → DPS ($400)...
   🟢 Grade A: BUY NOW - Historic low + Great flight

📊 Analyzing SYD → NRT ($700)...
   🟡 Grade B: CAUTION - Good price, check details

📊 Analyzing SYD → LAX ($750)...
   🔴 Grade C: WAIT - Better deals likely

============================================================
🌏 TOP DEALS FROM SYDNEY (AI GRADED)
============================================================

🟢 Grade A | SYD → DPS
   $400 | 2025-12-15
   BUY NOW - Historic low + Great flight
   Confidence: 95%

🟡 Grade B | SYD → NRT
   $700 | 2026-01-10
   CAUTION - Good price, check details
   Confidence: 70%

🔴 Grade C | SYD → LAX
   $750 | 2025-12-20
   WAIT - Better deals likely
   Confidence: 40%
```

---

## Implementation Priority (When Ready)

### Phase 1: Deal Radar (Easy, High Impact)
- **Effort**: 1-2 days
- **APIs**: Flight Inspiration Search only
- **Value**: Lead magnet, drives traffic
- **Revenue**: Affiliate commissions

### Phase 2: AI Grading (Medium, High Value)
- **Effort**: 1 week
- **APIs**: Price Analysis + Choice Prediction
- **Value**: Differentiation, justifies subscription
- **Revenue**: $5/mo subscriptions

### Phase 3: Smart Watchdog (Hard, Retention)
- **Effort**: 2 weeks
- **APIs**: Price Analysis (time series) + cron jobs
- **Value**: User retention, repeat visits
- **Revenue**: Reduced churn, higher LTV

---

## Key Takeaways

1. **Feature 1 (Radar)**: Uses cached data, low cost, perfect lead magnet
2. **Feature 2 (AI Audit)**: Differentiates you from Skyscanner/Google Flights
3. **Feature 3 (Watchdog)**: Keeps users coming back, reduces churn

**The Moat**: It's not just finding cheap flights (Skyscanner does that). It's **telling users if they should actually book it** (AI grading) and **alerting them at the perfect time** (watchdog).

**Not Implemented Yet** - Ideas for when you're ready to scale beyond SMS alerts! 🚀
