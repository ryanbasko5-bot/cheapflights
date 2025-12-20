# HubSpot Configuration Guide

## Overview

This guide details how to configure HubSpot Professional for FareGlitch's pay-to-unlock model.

## Custom Properties

### Contact Properties

Create these in HubSpot → Settings → Properties → Contact Properties:

| Property Name | Field Type | Description |
|--------------|------------|-------------|
| `deal_unlock_timestamp` | Date picker | When contact last unlocked a deal |
| `deal_to_deliver` | Single-line text | Deal number to deliver via workflow |
| `last_deal_unlocked` | Single-line text | Most recent deal number |
| `total_deals_unlocked` | Number | Count of all deals unlocked |
| `last_refund_date` | Date picker | Most recent refund date |
| `last_refund_reason` | Multi-line text | Reason for last refund |
| `favorite_regions` | Multiple checkboxes | Asia, Europe, Americas, etc. |

### Product Properties

Create these in HubSpot → Commerce Hub → Products → Properties:

| Property Name | Field Type | Description |
|--------------|------------|-------------|
| `deal_number` | Single-line text | Unique deal identifier (e.g., DEAL#001) |
| `deal_origin` | Single-line text | Origin airport code |
| `deal_destination` | Single-line text | Destination airport code |
| `deal_savings` | Number | Dollar amount saved |
| `deal_savings_pct` | Number | Percentage saved |

## Workflow Templates

### Workflow 1: Deal Delivery Automation

**Name**: Deal Delivery Workflow  
**Type**: Contact-based  
**Trigger**: When "deal_unlock_timestamp" is known (updated)

**Steps**:

1. **Delay**: None (immediate)
2. **Action**: Send email "Deal Details Delivery"
   - Subject: `CONFIDENTIAL: Your {{contact.deal_to_deliver}} Flight Details`
   - Template: Use email template created below
   
3. **Action**: Add to static list
   - List: "Active Deal Buyers"
   
4. **Action**: Set contact property
   - Property: `lifecyclestage`
   - Value: `customer`
   
5. **Action**: Set contact property
   - Property: `last_deal_unlocked`
   - Value: `{{contact.deal_to_deliver}}`
   
6. **Delay**: 24 hours

7. **Action**: Send email "Booking Follow-up"
   - Subject: "Did you book your {{contact.last_deal_unlocked}} flight?"
   - Ask for feedback and testimonial

### Workflow 2: Refund Processing

**Name**: Glitch Guarantee Refund  
**Type**: Ticket-based  
**Trigger**: Ticket created in "Support" pipeline, stage "Refund Request"

**Steps**:

1. **Action**: Send internal email notification
   - To: founder@fareglitch.com
   - Subject: "Refund Request: {{ticket.subject}}"
   
2. **Action**: Call webhook
   - URL: `https://api.fareglitch.com/webhooks/hubspot/refund-request`
   - Method: POST
   - Body:
   ```json
   {
     "email": "{{contact.email}}",
     "deal_number": "{{contact.last_deal_unlocked}}",
     "reason": "{{ticket.content}}"
   }
   ```
   
3. **Delay**: Wait for webhook response (max 5 minutes)

4. **Branch**: If webhook response = success
   - **Action**: Send email "Refund Confirmation"
   - **Action**: Update ticket stage to "Resolved"
   
5. **Branch**: If webhook fails
   - **Action**: Create task for manual review
   - **Action**: Send internal alert

### Workflow 3: Regional Interest Segmentation

**Name**: Auto-segment by Region Interest  
**Type**: Contact-based  
**Trigger**: "deal_to_deliver" is known

**Steps**:

1. **Branch**: If "deal_to_deliver" contains "NRT" or "HND" or "ICN"
   - Add to list: "Interested in Asia"
   
2. **Branch**: If "deal_to_deliver" contains "LHR" or "CDG" or "FRA"
   - Add to list: "Interested in Europe"
   
3. **Branch**: If cabin_class = "business" or "first"
   - Add to list: "Premium Cabin Buyers"

## Email Templates

### Template 1: Deal Details Delivery

**Name**: Deal Details Delivery  
**Subject**: CONFIDENTIAL: Your {{contact.deal_to_deliver}} Flight Details  
**From**: FareGlitch <deals@fareglitch.com>

**Body**:
```html
<h1>🎯 Your Exclusive Deal Details</h1>

<p>Hi {{contact.firstname|default("there")}}!</p>

<p>Thanks for unlocking <strong>{{contact.deal_to_deliver}}</strong>! Here are your exclusive booking details:</p>

<div style="background: #f5f5f5; padding: 20px; margin: 20px 0;">
  <h2>{{deal.route_description}}</h2>
  <p><strong>💰 Price:</strong> ${{deal.mistake_price}} <strike style="color: #999;">(Normally ${{deal.normal_price}})</strike></p>
  <p><strong>✈️ Airline:</strong> {{deal.airline}}</p>
  <p><strong>🛋️ Cabin:</strong> {{deal.cabin_class}}</p>
  <p><strong>📅 Travel Dates:</strong> {{deal.travel_dates_start}} - {{deal.travel_dates_end}}</p>
</div>

<div style="text-align: center; margin: 30px 0;">
  <a href="{{deal.booking_link}}" style="background: #FF4444; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
    🔗 BOOK NOW
  </a>
</div>

<h3>⚠️ CRITICAL BOOKING TIPS</h3>
<ol>
  <li><strong>Book IMMEDIATELY</strong> - Airlines can correct pricing errors within hours</li>
  <li><strong>Use incognito/private browsing</strong> - Prevents price increases from cookies</li>
  <li><strong>Clear browser cookies</strong> before searching</li>
  <li><strong>Book directly with airline</strong> when possible (lower cancellation risk)</li>
  <li><strong>Consider travel insurance</strong> - Protects your investment</li>
  <li><strong>Don't call the airline</strong> to ask about the price - just book online</li>
</ol>

<h3>🛡️ Glitch Guarantee</h3>
<p>If the airline cancels your booking within 48 hours, we'll refund your ${{deal.unlock_fee}} unlock fee. No questions asked.</p>

<p>Questions? Just reply to this email.</p>

<p>Happy travels!<br>
The FareGlitch Team</p>
```

### Template 2: Weekly Watchlist

**Name**: Weekly Deal Watchlist  
**Subject**: 🚨 This Week's Mistake Fares  
**Sent**: Weekly on Monday 9am

**Body**:
```html
<h1>🔥 Hot Deals This Week</h1>

<p>Hi {{contact.firstname}}!</p>

<p>We've detected <strong>{{total_deals}}</strong> mistake fares this week. Here's your personalized watchlist:</p>

<!-- Repeat for each deal -->
<div style="border: 2px solid #FF4444; padding: 15px; margin: 20px 0;">
  <h3>{{deal.teaser_headline}}</h3>
  <p>{{deal.route_description}}</p>
  <p><strong>Price:</strong> ${{deal.mistake_price}} <span style="color: green;">(Save {{deal.savings_percentage}}%)</span></p>
  <a href="https://fareglitch.com/deals/{{deal.deal_number}}" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none;">
    View Details (${{deal.unlock_fee}} to unlock)
  </a>
</div>

<p><em>These deals won't last long. First come, first served!</em></p>
```

## Landing Page Template

### Deal Teaser Page

**Structure**:

1. **Hero Section**
   - Headline: `{{page.headline}}`
   - Subheadline: Savings percentage
   - Visual: Map showing route

2. **Pricing Module**
   ```
   Normal Price: ${{page.normal_price}} [crossed out]
   Mistake Price: ${{page.mistake_price}} [large, red]
   You Save: ${{page.savings}} ({{page.savings_pct}}%)
   ```

3. **What's Included** (Vague)
   - Route description (e.g., "East Coast US to Japan")
   - Date range (e.g., "November - February")
   - Cabin class hint (e.g., "Premium Cabin")
   - Airline alliance (e.g., "Star Alliance Carrier")

4. **Unlock CTA**
   ```
   [Button: Unlock Full Details - ${{unlock_fee}}]
   ```

5. **Hidden Section** (Smart Content - shows after payment)
   - Specific airline
   - Exact dates available
   - Booking link
   - Step-by-step instructions

6. **FAQ Section**
   - What is a mistake fare?
   - Is this legal?
   - Will the airline cancel?
   - What's the Glitch Guarantee?

7. **Social Proof**
   - Testimonials module
   - "X people unlocked this deal"
   - Timer: "Expires in 47 hours"

## Payment Link Configuration

### HubSpot Commerce Setup

1. **Go to**: Commerce Hub → Payments → Configure

2. **Connect Stripe**:
   - Click "Connect Stripe Account"
   - Authorize HubSpot to access Stripe
   - Select account

3. **Create Payment Link Template**:
   - Name: "Deal Unlock Payment"
   - Type: "One-time payment"
   - Default amount: $7.00
   - Currency: USD
   - Success redirect: `/deal-unlocked?id={{deal_number}}`

4. **Embed in Landing Page**:
   ```html
   <a href="https://buy.stripe.com/{{payment_link_id}}?prefilled_email={{contact.email}}&client_reference_id={{deal_number}}">
     Unlock for ${{unlock_fee}}
   </a>
   ```

## Lists

Create these static lists:

| List Name | Purpose | Criteria |
|-----------|---------|----------|
| Active Deal Buyers | All paying customers | Has unlocked ≥1 deal |
| Interested in Asia | Retargeting | Unlocked Asian routes |
| Interested in Europe | Retargeting | Unlocked European routes |
| Premium Cabin Buyers | High-value segment | Unlocked business/first class |
| Refund Recipients | Service recovery | Received Glitch Guarantee refund |
| Weekly Watchlist Subscribers | Email marketing | Opted into weekly emails |

## Forms

### Refund Request Form

**Name**: Glitch Guarantee Refund  
**Redirect**: /refund-submitted

**Fields**:
1. Email (required)
2. Deal Number (dropdown - populated from their unlocks)
3. Booking Confirmation Number
4. Reason (multi-line text)
5. Airline Cancellation Screenshot (file upload)

**Actions**:
- Create ticket in "Refund Request" pipeline
- Trigger "Glitch Guarantee Refund" workflow
- Send confirmation email

## Reporting Dashboard

Create custom report with:

- Total unlocks (this week)
- Revenue (this week)
- Top performing deals
- Conversion rate (page views → unlocks)
- Refund rate
- Customer lifetime value

## Testing Checklist

- [ ] All custom properties created
- [ ] Workflows active and tested
- [ ] Email templates approved and active
- [ ] Landing page template published
- [ ] Payment links working
- [ ] Webhooks configured
- [ ] Forms submitting correctly
- [ ] Lists populating automatically
- [ ] Test full unlock flow end-to-end
- [ ] Test refund flow
- [ ] Verify email deliverability
