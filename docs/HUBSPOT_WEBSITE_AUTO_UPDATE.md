# 🌐 HubSpot Website Auto-Update Guide

## Overview

Your scanner now **automatically updates your HubSpot-hosted website** when new deals are found!

## How It Works

```
New Deal Found
     ↓
Send SMS to Subscribers (instant)
     ↓
Update HubDB Table (website database)
     ↓
Create Blog Post (optional)
     ↓
Website Shows Updated Deals (automatic!)
```

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Run Setup Script

```bash
python setup_hubspot_website.py
```

This creates a HubDB table in your HubSpot account to store deals.

### Step 2: Save Table ID

The script will give you a table ID. Add it to `.env`:

```bash
HUBSPOT_DEALS_TABLE_ID=12345678
```

### Step 3: Add Module to Website

**Option A: HubDB Module (Easiest)**
1. Edit your HubSpot page
2. Click "Add" → Search "HubDB"
3. Select the "FareGlitch Deals" table
4. Customize the display

**Option B: Custom HubL Module**
1. Design Manager → New Module
2. Add this HubL code:

```html
{% set table_id = YOUR_TABLE_ID %}
{% set deals = hubdb_table_rows(table_id, "&orderBy=-created_at&limit=10") %}

<div class="deals-grid">
  {% for row in deals %}
    {% if row.status == "active" %}
    <div class="deal-card">
      <div class="deal-header">
        <h3>{{ row.route }}</h3>
        <span class="badge">{{ row.savings_pct }}% OFF</span>
      </div>
      
      <div class="deal-pricing">
        <div class="old-price">${{ row.normal_price }}</div>
        <div class="new-price">${{ row.deal_price }}</div>
        <div class="savings">Save ${{ row.savings }}</div>
      </div>
      
      <div class="deal-meta">
        <p>{{ row.origin }} → {{ row.destination }}</p>
        <p class="expires">Expires: {{ row.expires_at|datetimeformat('%B %d, %Y') }}</p>
      </div>
      
      <a href="/subscribe" class="cta-button">Get Details</a>
    </div>
    {% endif %}
  {% endfor %}
</div>

<style>
.deals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 2rem;
}

.deal-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  backdrop-filter: blur(10px);
}

.deal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.badge {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
}

.old-price {
  text-decoration: line-through;
  opacity: 0.6;
  font-size: 1.2rem;
}

.new-price {
  font-size: 2.5rem;
  font-weight: bold;
  color: #10b981;
  margin: 0.5rem 0;
}

.savings {
  color: #f093fb;
  font-weight: 600;
  font-size: 1.2rem;
}

.cta-button {
  display: block;
  width: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 1rem;
  text-align: center;
  border-radius: 8px;
  text-decoration: none;
  margin-top: 1.5rem;
  font-weight: 600;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
</style>
```

---

## 📊 HubDB Table Structure

The auto-updater creates this table:

| Column | Type | Description |
|--------|------|-------------|
| `deal_number` | Text | DEAL#001, DEAL#002, etc. |
| `route` | Text | "JFK to Tokyo" |
| `origin` | Text | "JFK" |
| `destination` | Text | "NRT" |
| `normal_price` | Number | 2000 |
| `deal_price` | Number | 450 |
| `savings` | Number | 1550 |
| `savings_pct` | Number | 77 |
| `status` | Text | "active" or "expired" |
| `expires_at` | DateTime | When deal expires |
| `created_at` | DateTime | When deal was found |

---

## 🔧 Configuration

Add to your `.env` file:

```bash
# HubSpot Website Integration
HUBSPOT_API_KEY=pat-na1-your-key-here
HUBSPOT_PORTAL_ID=your-portal-id
HUBSPOT_DEALS_TABLE_ID=12345678  # From setup script

# Enable auto-updates
ENABLE_AUTO_PUBLISH=true
```

---

## 🧪 Testing

### Test the Integration:

```python
# test_website_update.py
from src.models.database import Deal, DealStatus
from src.hubspot.website_updater import auto_update_website
from datetime import datetime, timedelta

# Create a test deal
test_deal = Deal(
    deal_number="DEAL#999",
    origin="SYD",
    destination="BKK",
    route_description="Sydney to Bangkok",
    normal_price=850.0,
    mistake_price=360.0,
    savings_amount=490.0,
    savings_percentage=0.576,
    currency="AUD",
    status=DealStatus.PUBLISHED,
    detected_at=datetime.now(),
    expires_at=datetime.now() + timedelta(hours=48)
)

# Update website
result = auto_update_website([test_deal])

print("Website Update Result:")
print(f"  HubDB Updated: {result['hubdb_updated']}")
print(f"  Blog Posts Created: {result['blog_posts_created']}")
print(f"  Errors: {result['errors']}")
```

Run it:
```bash
python test_website_update.py
```

Then check your HubSpot:
1. Content → HubDB → View your table
2. Content → Blog → See new posts
3. Visit your website → See updated deals!

---

## 🎯 What Happens Automatically

When your scanner finds a new deal:

1. **SMS Sent** (instant) → Paying subscribers notified
2. **HubDB Updated** → Deal added to website database
3. **Blog Post Created** → New announcement published
4. **Website Refreshes** → Visitors see new deals

All automatic - **zero manual work**!

---

## 🔄 Alternative Methods

### Method 1: Blog Posts Only

If you don't want to use HubDB, just use blog posts:

```python
# In src/config.py
enable_hubdb_updates: bool = False
enable_blog_posts: bool = True
```

Deals will be published as blog posts that appear in your blog feed.

### Method 2: Custom API Endpoint

Create a custom endpoint that your website calls:

```python
# In your HubSpot page (JavaScript)
fetch('https://api.fareglitch.com/deals/active')
  .then(res => res.json())
  .then(deals => {
    // Update page with deals
    deals.forEach(deal => {
      // Render deal card
    });
  });
```

### Method 3: RSS Feed

Your scanner can generate an RSS feed that HubSpot imports:

```python
# In scanner
from src.utils.rss_generator import create_deals_feed

create_deals_feed(deals)  # Creates deals.xml
```

Then in HubSpot:
- Content → Blog → Import → RSS Feed
- Point to: https://yoursite.com/deals.xml

---

## 📱 Mobile App Integration

The same HubDB table can feed your mobile app:

```javascript
// In React Native app
const fetchDeals = async () => {
  const response = await fetch(
    `https://api.hubapi.com/cms/v3/hubdb/tables/${TABLE_ID}/rows`,
    {
      headers: { 'Authorization': `Bearer ${API_KEY}` }
    }
  );
  const data = await response.json();
  setDeals(data.results);
};
```

---

## 🚨 Troubleshooting

### "HubDB table not found"
- Run `python setup_hubspot_website.py` first
- Check `HUBSPOT_DEALS_TABLE_ID` in `.env`

### "Unauthorized" error
- Verify `HUBSPOT_API_KEY` is correct
- Check API key has "CMS" permissions

### Deals not showing on website
- Publish the HubDB table (Content → HubDB → Publish)
- Clear HubSpot cache (Content → Settings → Clear cache)
- Check module is pointed to correct table

### Blog posts not created
- Check API key has "Content" permissions
- Verify blog is set up in HubSpot

---

## 📚 Resources

- [HubDB Documentation](https://developers.hubspot.com/docs/cms/data/hubdb)
- [HubL Template Language](https://developers.hubspot.com/docs/cms/hubl)
- [HubSpot CMS API](https://developers.hubspot.com/docs/api/cms)

---

## ✅ Success!

Your website now updates automatically when deals are found! 🎉

**Flow**:
Scanner finds deal → SMS sent → Website updated → Blog post created → All automatic!
