# FareGlitch API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.fareglitch.com`

## Authentication

Most endpoints are public. Admin endpoints (marked with 🔒) require authentication.

---

## Endpoints

### Health Check

#### `GET /`

Check API status.

**Response:**
```json
{
  "status": "online",
  "service": "FareGlitch API",
  "version": "1.0.0"
}
```

---

### Deal Endpoints

#### `GET /deals/active`

Get list of active deal teasers (public information only).

**Query Parameters:**
- `limit` (optional): Maximum results (default: 10, max: 50)

**Response:**
```json
[
  {
    "deal_number": "DEAL#001",
    "route_description": "NYC to Tokyo",
    "teaser_headline": "Business Class Glitch: NYC to Tokyo",
    "teaser_description": "Save 77%",
    "normal_price": 2000.0,
    "mistake_price": 450.0,
    "savings_amount": 1550.0,
    "savings_percentage": 0.775,
    "currency": "USD",
    "cabin_class": "business",
    "unlock_fee": 7.0,
    "expires_at": "2025-11-30T10:00:00"
  }
]
```

---

#### `GET /deals/{deal_number}`

Get teaser for a specific deal.

**Path Parameters:**
- `deal_number`: Deal identifier (e.g., "DEAL#001")

**Response:**
```json
{
  "deal_number": "DEAL#001",
  "route_description": "NYC to Tokyo",
  "teaser_headline": "Business Class Glitch",
  "normal_price": 2000.0,
  "mistake_price": 450.0,
  "unlock_fee": 7.0
}
```

**Errors:**
- `404`: Deal not found
- `410`: Deal expired or no longer available

---

#### `POST /deals/{deal_number}/unlock`

Unlock full deal details after payment.

**Path Parameters:**
- `deal_number`: Deal identifier

**Request Body:**
```json
{
  "email": "user@example.com",
  "payment_id": "pay_xxxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "deal_number": "DEAL#001",
  "route_description": "NYC to Tokyo",
  "origin": "JFK",
  "destination": "NRT",
  "normal_price": 2000.0,
  "mistake_price": 450.0,
  "airline": "ANA",
  "cabin_class": "business",
  "booking_link": "https://www.google.com/flights/...",
  "booking_instructions": "Book directly on ANA website...",
  "specific_dates": "{...}",
  "travel_dates_start": "2025-12-15T00:00:00",
  "travel_dates_end": "2026-02-28T00:00:00"
}
```

**Errors:**
- `404`: Deal not found
- `410`: Deal expired

---

#### `GET /deals/{deal_number}/stats`

Get deal statistics and analytics.

**Response:**
```json
{
  "deal_number": "DEAL#001",
  "total_unlocks": 143,
  "total_revenue": 1001.0,
  "status": "published",
  "published_at": "2025-11-28T12:00:00",
  "expires_at": "2025-11-30T12:00:00",
  "hubspot_analytics": {
    "product_id": "123456",
    "conversion_rate": 0.023
  }
}
```

---

### Refund Endpoints

#### `POST /refunds/request`

Request refund under Glitch Guarantee.

**Request Body:**
```json
{
  "email": "user@example.com",
  "deal_number": "DEAL#001",
  "reason": "Airline canceled my booking"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Refund processed"
}
```

**Errors:**
- `404`: Deal or unlock record not found
- `400`: Already refunded or outside 48-hour window
- `500`: Refund processing failed

---

### Webhook Endpoints

#### `POST /webhooks/hubspot/payment-success`

HubSpot webhook for successful payments.

**Request Body:**
```json
{
  "deal_number": "DEAL#001",
  "email": "user@example.com",
  "payment_id": "pay_xxxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "status": "success",
  "deal": { /* full deal object */ }
}
```

---

#### `POST /webhooks/hubspot/refund-request`

HubSpot webhook for refund requests.

**Request Body:**
```json
{
  "email": "user@example.com",
  "deal_number": "DEAL#001",
  "reason": "Airline canceled fare"
}
```

---

### Admin Endpoints 🔒

#### `POST /admin/deals/{deal_id}/publish`

Manually publish a deal to HubSpot.

**Path Parameters:**
- `deal_id`: Numeric deal ID

**Response:**
```json
{
  "status": "success",
  "deal_number": "DEAL#001",
  "hubspot_data": {
    "product_id": "123456",
    "payment_link": "https://buy.fareglitch.com/...",
    "landing_page_url": "https://fareglitch.com/deals/deal-001"
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request
- `404`: Not found
- `410`: Gone (deal expired)
- `500`: Internal server error

---

## Rate Limiting

- Public endpoints: 100 requests/minute
- Webhook endpoints: No limit (trusted sources)
- Admin endpoints: 1000 requests/minute

---

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation.

Visit `/redoc` for alternative ReDoc documentation.

---

## Examples

### Get Active Deals
```bash
curl http://localhost:8000/deals/active?limit=5
```

### Get Specific Deal
```bash
curl http://localhost:8000/deals/DEAL#001
```

### Unlock Deal (after payment)
```bash
curl -X POST http://localhost:8000/deals/DEAL#001/unlock \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "payment_id": "pay_xxxxxxxxxxxxx"
  }'
```

### Request Refund
```bash
curl -X POST http://localhost:8000/refunds/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "deal_number": "DEAL#001",
    "reason": "Airline canceled booking"
  }'
```
