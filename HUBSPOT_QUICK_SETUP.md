# 🚀 Add Auto-Updating Deals to Your HubSpot Page

## Your Situation: Separate Pages Already Built ✅

You have individual pages in HubSpot. Perfect! You just need to **add one module** to show deals.

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Create the HubDB Table

Run this once:
```bash
python setup_hubspot_website.py
```

Save the table ID it gives you. Let's say it's: `12345678`

### Step 2: Add to Any Page

**Pick which page** you want deals on (probably your home page or deals page).

#### Option A: Rich Text Module (Easiest)

1. Open your page in HubSpot editor
2. Click **(+)** where you want deals to show
3. Choose **"Rich text"** module
4. Click the **</>** (source code) button in toolbar
5. Open: `hubspot-sections/RECENT-DEALS-AUTO-UPDATE-MODULE.html`
6. **Find line 17** - it says: `{% set table_id = "YOUR_TABLE_ID" %}`
7. **Replace** with: `{% set table_id = "12345678" %}` (your actual ID)
8. Copy the ENTIRE file
9. Paste into the source code editor
10. Save and publish

**Done!** Deals now auto-update on that page! 🎉

#### Option B: Create Reusable Module (Use on multiple pages)

1. Go to: **Design Manager** (Marketing → Files & Templates → Design Tools)
2. Click: **File** → **New File** → **Module**
3. Name it: `Recent Deals Auto`
4. Paste the code from `RECENT-DEALS-AUTO-UPDATE-MODULE.html`
5. Replace `YOUR_TABLE_ID` with your actual table ID
6. **Save and publish**

Now you can add "Recent Deals Auto" module to ANY page:
- Edit page → (+) Add → Search "Recent Deals Auto" → Done!

---

## 📍 Where to Add It

Add the module to:
- **Home page** - Show featured deals at the top
- **Deals page** - Full list of all active deals
- **Blog sidebar** - Small widget showing latest deals
- **Footer** - Quick preview in footer section

---

## 🎨 Customize the Look

The module is **fully styled** but you can change:

**Colors** (in the `<style>` section):
- Purple: `#667eea` → Change to your brand color
- Pink: `#f093fb` → Change to your accent color
- Dark background: `#0f172a` → Change to match your site

**Layout**:
```html
<!-- Line 26: Change grid columns -->
grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));

<!-- 2 columns only: -->
grid-template-columns: repeat(2, 1fr);

<!-- 3 columns: -->
grid-template-columns: repeat(3, 1fr);
```

**Number of deals shown**:
```html
<!-- Line 17: Change limit -->
{% set deals = hubdb_table_rows(table_id, "orderBy=-created_at&limit=6") %}

<!-- Show only 3: -->
limit=3

<!-- Show 12: -->
limit=12
```

---

## 🔄 How Auto-Update Works

```
Your Scanner Runs
     ↓
Finds new deal: SYD → BKK $399
     ↓
Sends SMS to subscribers
     ↓
Updates HubDB table (automatic)
     ↓
Your website refreshes (automatic)
     ↓
Visitors see new deal instantly!
```

**You don't touch anything** - it's fully automatic! ✨

---

## 📱 Example: Multiple Pages Setup

### Home Page
Add the module showing **3 featured deals**:
```html
{% set deals = hubdb_table_rows(table_id, "orderBy=-savings&limit=3") %}
```
(Shows biggest savings first)

### Deals Page
Add the module showing **all active deals**:
```html
{% set deals = hubdb_table_rows(table_id, "orderBy=-created_at&limit=20") %}
```
(Shows up to 20 newest deals)

### Sidebar Widget
Add a mini version showing **1 hot deal**:
```html
{% set deals = hubdb_table_rows(table_id, "orderBy=-savings_pct&limit=1") %}
```
(Shows best percentage discount)

---

## 🧪 Test It

1. **Add the module** to a test page
2. **Run your scanner**: `python find_deals.py`
3. **Check HubSpot**: Content → HubDB → See the deal
4. **Refresh your page**: Deal appears automatically!

---

## 🆘 Troubleshooting

### "Table not found" error
- Make sure you ran `python setup_hubspot_website.py`
- Check the table ID is correct (no quotes in the actual ID)
- Format should be: `{% set table_id = "12345678" %}`

### Deals don't show up
- In HubSpot: Content → HubDB → **Publish** the table
- Clear cache: Content → Settings → Performance → Clear cache
- Check deal status is "active" or "published"

### Module doesn't appear
- Make sure you're in **source code view** when pasting
- Check all `<div>` tags are closed properly
- Try refreshing the page editor

### Styling looks broken
- HubSpot might override styles
- Add `!important` to styles:
  ```css
  background: #0f172a !important;
  ```

---

## 💡 Pro Tips

1. **Test deals first**: Create a test deal manually in HubDB to verify display
2. **Match your brand**: Update colors to match your site theme
3. **Mobile first**: Module is responsive, but test on phone
4. **Add CTA button**: Link to your subscribe form
5. **Show scarcity**: Deals have expiry times to create urgency

---

## 📚 What's Included

The module shows:
- ✅ Route (SYD → BKK)
- ✅ Normal price vs Deal price
- ✅ Savings amount & percentage
- ✅ Expiry time
- ✅ "Get Details" CTA button
- ✅ Live status badge
- ✅ Auto-updates from HubDB

---

## ✅ Checklist

- [ ] Run `python setup_hubspot_website.py`
- [ ] Save table ID to `.env`
- [ ] Open `RECENT-DEALS-AUTO-UPDATE-MODULE.html`
- [ ] Replace `YOUR_TABLE_ID` with actual ID
- [ ] Copy entire file
- [ ] Open HubSpot page editor
- [ ] Add Rich Text module
- [ ] Paste code in source view
- [ ] Save and publish
- [ ] Test with `python find_deals.py`
- [ ] Check deals appear on site!

Done! Your deals now update automatically! 🎉
