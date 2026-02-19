"""
FastAPI Backend for FareGlitch

Provides:
- Public API for deal teasers
- Webhook endpoints for HubSpot
- Admin API for deal management
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import settings

# Initialize Sentry for production error tracking
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    if settings.is_production and getattr(settings, "sentry_dsn", None):
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            traces_sample_rate=0.2,
            environment=settings.amadeus_env,
        )
        logging.getLogger(__name__).info("Sentry initialized for production")
except ImportError:
    pass  # sentry-sdk not installed; skip
from src.models.database import Deal, DealUnlock, DealStatus, Subscriber, SubscriptionType
from src.utils.database import get_db_session, init_db
from src.hubspot.integration import HubSpotIntegration
from src.scanner.amadeus_client import PriceAnomalyDetector, MAJOR_HUBS, get_scan_batch
from src.validator.duffel_client import DuffelValidator
from src.api.auth import (
    get_current_subscriber,
    get_optional_subscriber,
    is_premium_member,
    can_see_deal,
    create_access_token,
    generate_magic_link_token
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    try:
        # Run DB init and validate required environment in production
        init_db()
        logger.info("Database initialized successfully")
        try:
            # Import local validator which loads .env and checks required vars
            from check_env import validate_env

            if settings.is_production:
                validate_env()
            else:
                # In non-production, just check but don't exit
                missing_req, missing_opt = validate_env(return_missing=True)
                if missing_req:
                    logger.warning(f"Missing required env vars (dev): {missing_req}")
        except Exception as e:
            logger.debug(f"Env validation skipped or failed: {e}")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    yield
    # Shutdown
    logger.info("Shutting down FareGlitch API")


# Initialize FastAPI app
app = FastAPI(
    title="FareGlitch API",
    description="Mistake fare detection and gated marketplace API",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Configure based on environment
# Development: Allow all origins for testing
# Production: Restrict to specific domains
ALLOWED_ORIGINS = {
    "production": [
        "https://fareglitch.com.au",
        "https://www.fareglitch.com.au",
        "https://api.fareglitch.com.au"
    ],
    "development": [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000"
    ],
    "test": ["*"]
}

# Get appropriate origins based on environment
cors_origins = ALLOWED_ORIGINS.get(
    settings.amadeus_env,
    ALLOWED_ORIGINS["development"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600  # Cache preflight requests for 1 hour
)


# Pydantic models for API
class DealTeaserResponse(BaseModel):
    """Public teaser information (no booking details)."""
    deal_number: str
    route_description: str
    teaser_headline: str
    teaser_description: str
    normal_price: float
    mistake_price: float
    savings_amount: float
    savings_percentage: float
    currency: str
    cabin_class: Optional[str]
    unlock_fee: float
    expires_at: Optional[datetime]
    published_at: Optional[datetime]
    origin: Optional[str]
    destination: Optional[str]
    booking_link: Optional[str] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request with email/phone."""
    email: EmailStr
    phone_number: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    subscriber: dict


class DealFullResponse(BaseModel):
    """Full deal information (after unlock)."""
    deal_number: str
    route_description: str
    origin: str
    destination: str
    normal_price: float
    mistake_price: float
    savings_amount: float
    cabin_class: Optional[str]
    airline: Optional[str]
    booking_link: Optional[str]
    booking_instructions: Optional[str]
    specific_dates: Optional[str]
    travel_dates_start: Optional[datetime]
    travel_dates_end: Optional[datetime]
    
    class Config:
        from_attributes = True


class UnlockDealRequest(BaseModel):
    """Request to unlock a deal."""
    email: EmailStr


class RefundRequest(BaseModel):
    """Request refund under Glitch Guarantee."""
    email: EmailStr
    deal_number: str
    reason: str


class SubscribeRequest(BaseModel):
    """Request to subscribe for $5/month SMS alerts."""
    email: EmailStr
    phone_number: str


# API Endpoints

@app.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    """API health check with rate limiting."""
    return {
        "status": "online",
        "service": "FareGlitch API",
        "version": "1.0.0"
    }


@app.get("/deals/active", response_model=List[DealTeaserResponse])
@limiter.limit("100/hour")
async def get_active_deals(
    request: Request,
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db_session),
    subscriber: Optional[Subscriber] = Depends(get_optional_subscriber)
):
    """
    Get list of active deal teasers.
    
    Rate limit: 100 requests per hour per IP.
    
    Returns public information only (no booking details).
    Premium members see all deals immediately.
    Non-members see deals after 1-hour delay.
    """
    # Query all active deals
    all_deals = db.query(Deal).filter(
        Deal.status == DealStatus.PUBLISHED,
        Deal.is_active == True
    ).order_by(Deal.published_at.desc()).all()
    
    # Filter out expired deals and apply membership visibility rules
    now = datetime.now()
    visible_deals = [
        deal for deal in all_deals
        if (not deal.expires_at or deal.expires_at > now) and can_see_deal(deal, subscriber)
    ]
    
    return visible_deals[:limit]


@app.get("/deals/live")
@limiter.limit("300/hour")
async def get_live_deals_for_website(
    request: Request,
    db: Session = Depends(get_db_session),
):
    """
    Public feed for HubSpot website — returns deals as simple JSON.

    This endpoint is called by JavaScript on fareglitch.com.au/home
    to display live deals without manual copy-paste.
    No auth required, but only shows teasers (no booking details).
    """
    all_deals = db.query(Deal).filter(
        Deal.status == DealStatus.PUBLISHED,
        Deal.is_active == True,
    ).order_by(Deal.published_at.desc()).limit(12).all()

    now = datetime.now()
    deals_out = []
    for d in all_deals:
        if d.expires_at and d.expires_at < now:
            continue
        deals_out.append({
            "deal_number": d.deal_number,
            "route": f"{d.origin} → {d.destination}",
            "headline": d.teaser_headline or f"{d.origin} to {d.destination}",
            "normal_price": d.normal_price,
            "glitch_price": d.mistake_price,
            "savings_pct": int(d.savings_percentage * 100),
            "cabin_class": d.cabin_class or "Economy",
            "airline": d.airline or "",
            "expires_at": d.expires_at.isoformat() if d.expires_at else None,
        })

    return {
        "deals": deals_out,
        "count": len(deals_out),
        "updated_at": datetime.utcnow().isoformat(),
    }


@app.post("/auth/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db_session)
):
    """
    Login endpoint - authenticate subscriber and return JWT token.
    
    For passwordless auth, we'll send a magic link to email/SMS.
    For now, just check if subscriber exists and return token.
    """
    # Find subscriber by email or phone
    subscriber = None
    if login_request.phone_number:
        subscriber = db.query(Subscriber).filter(
            Subscriber.phone_number == login_request.phone_number
        ).first()
    
    if not subscriber and login_request.email:
        subscriber = db.query(Subscriber).filter(
            Subscriber.email == login_request.email
        ).first()
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscriber not found. Please subscribe first."
        )
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": subscriber.phone_number}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "subscriber": {
            "id": subscriber.id,
            "email": subscriber.email,
            "phone_number": subscriber.phone_number,
            "subscription_type": subscriber.subscription_type,
            "is_premium": is_premium_member(subscriber)
        }
    }


@app.get("/auth/me")
async def get_current_user(
    subscriber: Subscriber = Depends(get_current_subscriber)
):
    """Get current authenticated subscriber info."""
    return {
        "id": subscriber.id,
        "email": subscriber.email,
        "phone_number": subscriber.phone_number,
        "subscription_type": subscriber.subscription_type,
        "is_premium": is_premium_member(subscriber),
        "subscribed_at": subscriber.subscribed_at,
        "total_alerts_received": subscriber.total_alerts_received
    }


# ----------------------------------------------------------------
# Subscription Endpoints ($5/month)
# ----------------------------------------------------------------

@app.post("/subscribe")
@limiter.limit("10/hour")
async def subscribe(
    request: Request,
    sub_request: SubscribeRequest,
    db: Session = Depends(get_db_session),
):
    """
    Start a $5/month subscription for SMS deal alerts.

    Flow:
    1. Creates or finds subscriber in DB
    2. Creates Stripe Checkout Session (subscription mode)
    3. Returns checkout URL → user pays on Stripe's page
    4. Stripe webhook activates the subscription
    """
    from src.payments.stripe_checkout import create_subscription_checkout

    # Normalise phone number (strip spaces, ensure +61)
    phone = sub_request.phone_number.strip().replace(" ", "")
    if phone.startswith("0"):
        phone = "+61" + phone[1:]
    elif not phone.startswith("+"):
        phone = "+61" + phone

    # Find or create subscriber
    subscriber = db.query(Subscriber).filter(
        (Subscriber.phone_number == phone) | (Subscriber.email == sub_request.email)
    ).first()

    if subscriber and subscriber.stripe_subscription_id and subscriber.is_active:
        return {
            "status": "already_subscribed",
            "message": "You're already subscribed! You'll get SMS alerts for every deal.",
        }

    if not subscriber:
        subscriber = Subscriber(
            phone_number=phone,
            email=sub_request.email,
            subscription_type=SubscriptionType.FREE,
            is_active=True,
        )
        db.add(subscriber)
        db.commit()

    checkout = create_subscription_checkout(
        email=sub_request.email,
        phone=phone,
    )

    return {
        "status": "checkout_created",
        "checkout_url": checkout["checkout_url"],
        "session_id": checkout["session_id"],
        "price": f"${settings.subscription_price_aud:.2f} AUD/month",
    }


@app.post("/unsubscribe")
async def unsubscribe(
    request: Request,
    email: EmailStr = Query(...),
    db: Session = Depends(get_db_session),
):
    """Cancel subscription at end of current billing period."""
    subscriber = db.query(Subscriber).filter(Subscriber.email == email).first()

    if not subscriber or not subscriber.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found")

    from src.payments.stripe_checkout import cancel_subscription

    result = cancel_subscription(subscriber.stripe_subscription_id)

    return {
        "status": "success",
        "message": "Subscription will cancel at end of billing period. You'll keep receiving alerts until then.",
        "cancel_at": result["cancel_at"],
    }


@app.get("/deals/{deal_number}", response_model=DealTeaserResponse)
async def get_deal_teaser(
    deal_number: str,
    db: Session = Depends(get_db_session)
):
    """
    Get teaser information for a specific deal.
    
    Returns public information only.
    """
    deal = db.query(Deal).filter(Deal.deal_number == deal_number.upper()).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    if not deal.is_active or deal.status != DealStatus.PUBLISHED:
        raise HTTPException(status_code=410, detail="Deal is no longer available")
        
    return deal


@app.post("/deals/{deal_number}/unlock", response_model=DealFullResponse)
async def unlock_deal(
    deal_number: str,
    unlock_request: UnlockDealRequest,
    db: Session = Depends(get_db_session)
):
    """
    Check if deal is already unlocked for this email.
    If yes → return full deal details.
    If no → return 402 with Stripe checkout URL.
    """
    deal = db.query(Deal).filter(Deal.deal_number == deal_number.upper()).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    if not deal.is_active or deal.status != DealStatus.PUBLISHED:
        raise HTTPException(status_code=410, detail="Deal is no longer available")
        
    # Check if already unlocked by this user
    existing_unlock = db.query(DealUnlock).filter(
        DealUnlock.deal_id == deal.id,
        DealUnlock.email == unlock_request.email
    ).first()
    
    if existing_unlock and existing_unlock.payment_status == "succeeded":
        # Already paid — return full deal
        return deal
    
    # Not yet paid — create Stripe Checkout session
    from src.payments.stripe_checkout import create_checkout_session
    
    checkout = create_checkout_session(
        deal_number=deal.deal_number,
        deal_headline=deal.teaser_headline or f"{deal.origin} → {deal.destination}",
        amount_aud=deal.unlock_fee,
        customer_email=unlock_request.email,
    )
    
    return JSONResponse(
        status_code=402,
        content={
            "message": "Payment required to unlock deal",
            "deal_number": deal.deal_number,
            "unlock_fee": deal.unlock_fee,
            "currency": "AUD",
            "checkout_url": checkout["checkout_url"],
            "session_id": checkout["session_id"],
        }
    )


async def _process_refund(refund_request: RefundRequest, db: Session):
    """
    Internal refund logic — shared by the public endpoint and HubSpot webhook.
    """
    deal = db.query(Deal).filter(Deal.deal_number == refund_request.deal_number.upper()).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    # Find unlock record
    unlock = db.query(DealUnlock).filter(
        DealUnlock.deal_id == deal.id,
        DealUnlock.email == refund_request.email
    ).first()
    
    if not unlock:
        raise HTTPException(status_code=404, detail="No unlock record found")
        
    if unlock.payment_status == "refunded":
        raise HTTPException(status_code=400, detail="Already refunded")
    
    if not unlock.payment_id:
        raise HTTPException(status_code=400, detail="No payment record to refund")
        
    # Check if within 48 hour window
    hours_since_unlock = (datetime.now() - unlock.unlocked_at).total_seconds() / 3600
    
    if hours_since_unlock > 48 and settings.enable_glitch_guarantee:
        raise HTTPException(
            status_code=400,
            detail="Refund window expired (48 hours)"
        )
        
    # Process refund via Stripe
    from src.payments.stripe_checkout import issue_refund
    
    try:
        refund_result = issue_refund(
            payment_intent_id=unlock.payment_id,
            reason="requested_by_customer",
        )
        
        unlock.payment_status = "refunded"
        unlock.refund_requested = True
        unlock.refund_reason = refund_request.reason
        unlock.refunded_at = datetime.now()
        
        deal.total_revenue -= unlock.unlock_fee_paid
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Refund processed via Glitch Guarantee",
            "refund_id": refund_result["refund_id"],
            "amount_refunded": refund_result["amount"],
        }
    except Exception as e:
        logger.error(f"Stripe refund failed: {e}")
        raise HTTPException(status_code=500, detail="Refund processing failed")


@app.post("/refunds/request")
async def request_refund(
    refund_request: RefundRequest,
    db: Session = Depends(get_db_session),
    subscriber: Subscriber = Depends(get_current_subscriber)
):
    """
    Request refund under Glitch Guarantee.
    
    Users can request refund if airline cancels the fare within 48 hours.
    Refund is processed automatically via Stripe.
    Requires JWT authentication — refund email must match authenticated user.
    """
    # Ensure the authenticated user matches the refund request email
    if subscriber.email != refund_request.email:
        raise HTTPException(
            status_code=403,
            detail="You can only request refunds for your own purchases"
        )
    return await _process_refund(refund_request, db)


@app.get("/deals/{deal_number}/stats")
async def get_deal_stats(
    deal_number: str,
    request: Request,
    db: Session = Depends(get_db_session)
):
    """
    Get statistics for a deal. Admin only — requires Authorization: Bearer <API_SECRET_KEY>.
    """
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {settings.api_secret_key}":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    deal = db.query(Deal).filter(Deal.deal_number == deal_number.upper()).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    hubspot = HubSpotIntegration()
    analytics = hubspot.get_deal_analytics(deal)
    
    return {
        "deal_number": deal.deal_number,
        "total_unlocks": deal.total_unlocks,
        "total_revenue": deal.total_revenue,
        "status": deal.status,
        "published_at": deal.published_at,
        "expires_at": deal.expires_at,
        "hubspot_analytics": analytics
    }


# Webhook Endpoints

@app.post("/webhooks/hubspot/payment-success")
async def hubspot_payment_webhook(
    request: Request,
    payload: dict,
    db: Session = Depends(get_db_session)
):
    """
    Webhook endpoint for HubSpot payment success.
    
    HubSpot will call this when a payment is completed.
    Requires Authorization: Bearer <API_SECRET_KEY> header.
    """
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {settings.api_secret_key}":
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    # Extract payment info from HubSpot webhook payload
    # Payload structure depends on HubSpot Commerce Hub configuration
    
    deal_number = payload.get("deal_number")
    email = payload.get("email")
    payment_id = payload.get("payment_id")
    
    if not all([deal_number, email, payment_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")
        
    # Process unlock (legacy HubSpot path)
    unlock_request = UnlockDealRequest(email=email)
    result = await unlock_deal(deal_number, unlock_request, db)
    
    return {"status": "success", "deal": result}


@app.post("/webhooks/hubspot/refund-request")
async def hubspot_refund_webhook(
    request: Request,
    payload: dict,
    db: Session = Depends(get_db_session)
):
    """
    Webhook endpoint for HubSpot refund requests.
    
    Triggered when support ticket is created for refund.
    Requires Authorization: Bearer <API_SECRET_KEY> header.
    """
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {settings.api_secret_key}":
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    email = payload.get("email")
    deal_number = payload.get("deal_number")
    reason = payload.get("reason", "Airline canceled fare")
    
    refund_request = RefundRequest(
        email=email,
        deal_number=deal_number,
        reason=reason
    )
    
    return await _process_refund(refund_request, db)


# Admin Endpoints (protected by API_SECRET_KEY)

@app.post("/admin/deals/{deal_id}/publish")
async def admin_publish_deal(
    deal_id: int,
    request: Request,
    db: Session = Depends(get_db_session)
):
    """
    Manually publish a deal to HubSpot.
    Requires Authorization: Bearer <API_SECRET_KEY>
    """
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {settings.api_secret_key}":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    hubspot = HubSpotIntegration()
    result = await hubspot.publish_deal(deal)
    
    db.commit()
    
    return {
        "status": "success",
        "deal_number": deal.deal_number,
        "hubspot_data": result
    }


# ----------------------------------------------------------------
# Stripe Payment Endpoints
# ----------------------------------------------------------------

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db_session)):
    """
    Stripe webhook — handles both subscriptions and one-off payments.

    Events handled:
    - checkout.session.completed → activate subscription or unlock deal
    - invoice.payment_succeeded → renew subscription
    - customer.subscription.deleted → deactivate subscriber
    - charge.refunded → record refund
    """
    from src.payments.stripe_checkout import process_webhook_event
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    event = process_webhook_event(payload, sig_header)
    
    if not event:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    data_object = event["data"]["object"]

    # ── CHECKOUT COMPLETED ─────────────────────────────────────────
    if event_type == "checkout.session.completed":
        metadata = data_object.get("metadata", {})
        checkout_type = metadata.get("type", "deal_unlock")

        # ── Subscription checkout ──
        if checkout_type == "subscription" or data_object.get("mode") == "subscription":
            email = metadata.get("email") or data_object.get("customer_email")
            phone = metadata.get("phone", "")
            stripe_customer_id = data_object.get("customer")
            stripe_subscription_id = data_object.get("subscription")

            if not email:
                logger.error(f"Subscription webhook missing email: {metadata}")
                return {"status": "error", "reason": "missing email"}

            # Find subscriber by phone or email
            subscriber = None
            if phone:
                subscriber = db.query(Subscriber).filter(
                    Subscriber.phone_number == phone
                ).first()
            if not subscriber:
                subscriber = db.query(Subscriber).filter(
                    Subscriber.email == email
                ).first()

            if not subscriber:
                subscriber = Subscriber(
                    phone_number=phone,
                    email=email,
                    subscription_type=SubscriptionType.FREE,
                    is_active=True,
                )
                db.add(subscriber)

            # Activate subscription
            subscriber.subscription_type = SubscriptionType.SMS_MONTHLY
            subscriber.stripe_customer_id = stripe_customer_id
            subscriber.stripe_subscription_id = stripe_subscription_id
            subscriber.is_active = True
            subscriber.last_payment_date = datetime.now()
            # Set expiry 35 days out (monthly + buffer)
            subscriber.subscription_expires_at = datetime.now() + timedelta(days=35)

            db.commit()

            logger.info(
                f"🎉 NEW SUBSCRIBER: {email} ({phone}) — "
                f"${settings.subscription_price_aud}/month"
            )

            # Sync to HubSpot CRM (non-blocking, best-effort)
            try:
                hubspot = HubSpotIntegration()
                hubspot.sync_subscriber(email=email, phone=phone, subscription_type="sms_monthly")
            except Exception as hs_err:
                logger.warning(f"HubSpot sync skipped: {hs_err}")

            return {"status": "subscription_activated", "email": email}

        # ── Deal unlock checkout (legacy) ──
        else:
            session = data_object
            if session.get("payment_status") != "paid":
                return {"status": "ignored", "reason": "not paid"}

            deal_number = metadata.get("deal_number")
            customer_email = metadata.get("customer_email")
            payment_intent = session.get("payment_intent")
            amount_paid = (session.get("amount_total", 0)) / 100

            if not deal_number or not customer_email:
                logger.error(f"Stripe webhook missing metadata: {metadata}")
                return {"status": "error", "reason": "missing metadata"}

            deal = db.query(Deal).filter(Deal.deal_number == deal_number).first()
            if not deal:
                logger.error(f"Stripe webhook: deal {deal_number} not found")
                return {"status": "error", "reason": "deal not found"}

            existing = db.query(DealUnlock).filter(
                DealUnlock.deal_id == deal.id,
                DealUnlock.email == customer_email,
            ).first()

            if existing:
                return {"status": "already_processed"}

            unlock = DealUnlock(
                deal_id=deal.id,
                email=customer_email,
                unlock_fee_paid=amount_paid,
                payment_id=payment_intent,
                payment_status="succeeded",
                unlocked_at=datetime.now(),
            )

            deal.total_unlocks += 1
            deal.total_revenue += amount_paid

            db.add(unlock)
            db.commit()

            logger.info(
                f"💰 PAYMENT: {customer_email} unlocked {deal_number} "
                f"(${amount_paid} AUD) — total revenue: ${deal.total_revenue}"
            )

            return {"status": "success", "deal_number": deal_number}

    # ── INVOICE PAID (subscription renewal) ────────────────────────
    elif event_type == "invoice.payment_succeeded":
        stripe_sub_id = data_object.get("subscription")
        if stripe_sub_id:
            subscriber = db.query(Subscriber).filter(
                Subscriber.stripe_subscription_id == stripe_sub_id
            ).first()
            if subscriber:
                subscriber.last_payment_date = datetime.now()
                subscriber.subscription_expires_at = datetime.now() + timedelta(days=35)
                subscriber.is_active = True
                db.commit()
                logger.info(f"🔄 Subscription renewed: {subscriber.email}")
        return {"status": "renewal_recorded"}

    # ── SUBSCRIPTION CANCELLED ─────────────────────────────────────
    elif event_type == "customer.subscription.deleted":
        stripe_sub_id = data_object.get("id")
        subscriber = db.query(Subscriber).filter(
            Subscriber.stripe_subscription_id == stripe_sub_id
        ).first()
        if subscriber:
            subscriber.subscription_type = SubscriptionType.FREE
            subscriber.is_active = False
            subscriber.stripe_subscription_id = None
            db.commit()
            logger.info(f"🚫 Subscription cancelled: {subscriber.email}")
        return {"status": "subscription_cancelled"}

    # ── REFUND ─────────────────────────────────────────────────────
    elif event_type == "charge.refunded":
        charge = data_object
        payment_intent = charge.get("payment_intent")
        
        if payment_intent:
            unlock = db.query(DealUnlock).filter(
                DealUnlock.payment_id == payment_intent
            ).first()
            
            if unlock:
                unlock.payment_status = "refunded"
                unlock.refunded_at = datetime.now()
                db.commit()
                logger.info(f"💸 Refund recorded for {payment_intent}")
        
        return {"status": "refund_recorded"}
    
    return {"status": "ignored", "event_type": event_type}


@app.get("/payment/success")
async def payment_success(
    session_id: str = Query(...),
    db: Session = Depends(get_db_session),
):
    """
    Success page after Stripe payment.
    Returns the full deal details.
    """
    from src.payments.stripe_checkout import get_session_details
    
    session = get_session_details(session_id)
    if not session or session["payment_status"] != "paid":
        raise HTTPException(status_code=400, detail="Payment not confirmed")
    
    deal = db.query(Deal).filter(
        Deal.deal_number == session["deal_number"]
    ).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return {
        "status": "unlocked",
        "deal_number": deal.deal_number,
        "route": f"{deal.origin} → {deal.destination}",
        "normal_price": deal.normal_price,
        "mistake_price": deal.mistake_price,
        "savings": f"{int(deal.savings_percentage * 100)}%",
        "airline": deal.airline,
        "cabin_class": deal.cabin_class,
        "booking_link": deal.booking_link,
        "booking_instructions": deal.booking_instructions,
        "specific_dates": deal.specific_dates,
        "glitch_guarantee": "48-hour refund if fare is cancelled",
    }


@app.get("/payment/cancelled")
async def payment_cancelled():
    """User cancelled the Stripe checkout."""
    return {
        "status": "cancelled",
        "message": "No worries — you weren't charged. The deal is still available if you change your mind.",
    }


# Health Check Endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db_session)):
    """
    Health check endpoint for monitoring.
    
    Returns:
        - status: healthy/unhealthy
        - timestamp: current UTC time
        - version: API version
        - database: database connection status
    """
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "database": f"error: {str(e)}"
            }
        )
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": db_status,
        "environment": settings.amadeus_env
    }


@app.get("/readiness")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    Simple check without database dependency.
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


# ----------------------------------------------------------------
# Scan endpoint — trigger a scan via API (protected by secret key)
# ----------------------------------------------------------------
@app.post("/admin/scan")
async def trigger_scan(
    request: Request,
    batch_size: int = Query(default=5, le=10, description="Airports per batch (max 10)"),
    db: Session = Depends(get_db_session),
):
    """
    Trigger a cost-conscious scan.

    - Rotates through airports in small batches (default 5)
    - Only hits expensive APIs when cheap APIs find candidates
    - Protected by API_SECRET_KEY in Authorization header

    Typical cost: ~5-15 API calls per scan (Inspiration is cached/free)
    """
    # Auth check — must provide the secret key
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {settings.api_secret_key}":
        raise HTTPException(status_code=403, detail="Invalid secret key")

    from src.scanner.main import FareGlitchScanner

    origins = get_scan_batch(batch_size)
    logger.info(f"🔍 Scan triggered for batch: {origins}")

    scanner = FareGlitchScanner(db)
    result = await scanner.run_scan(origins=origins)

    # Track API usage
    estimated_calls = len(origins) + (result.get("anomalies_found", 0) * 2)
    _log_api_usage(estimated_calls)

    return {
        "status": "scan_complete",
        "batch_scanned": origins,
        "batch_size": len(origins),
        "total_hubs": len(MAJOR_HUBS),
        "api_budget": {
            "calls_today": _api_calls_today,
            "daily_limit": DAILY_BUDGET,
            "calls_this_month": _api_calls_this_month,
            "monthly_limit": FREE_MONTHLY_LIMIT,
        },
        **result,
    }


@app.get("/admin/budget")
async def api_budget(request: Request):
    """Check Amadeus API call budget. Requires Authorization: Bearer <API_SECRET_KEY>."""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {settings.api_secret_key}":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    _track_api_budget()
    return {
        "calls_today": _api_calls_today,
        "daily_limit": DAILY_BUDGET,
        "calls_this_month": _api_calls_this_month,
        "monthly_limit": FREE_MONTHLY_LIMIT,
        "remaining_today": max(0, DAILY_BUDGET - _api_calls_today),
        "remaining_this_month": max(0, FREE_MONTHLY_LIMIT - _api_calls_this_month),
    }


# ----------------------------------------------------------------
# Background auto-scanner — scans ALL 26 airports every 3 hours
# Budget: $100 AUD/month ≈ 7,000 calls (2,000 free + ~5,000 paid)
# ----------------------------------------------------------------
_scanner_task = None

# Monthly API call budget tracking
_api_calls_this_month = 0
_api_month = None
FREE_MONTHLY_LIMIT = 7000  # 2,000 free + ~$100 AUD of paid calls
DAILY_BUDGET = 250  # 250/day × 30 = 7,500 (with buffer)
_api_calls_today = 0
_api_day = None


def _track_api_budget():
    """Reset daily/monthly counters and check if we're within budget."""
    global _api_calls_this_month, _api_month, _api_calls_today, _api_day

    now = datetime.utcnow()

    # Reset monthly counter on 1st of month
    if _api_month != now.month:
        _api_calls_this_month = 0
        _api_month = now.month
        logger.info(f"📊 Monthly API counter reset for month {now.month}")

    # Reset daily counter at midnight
    if _api_day != now.day:
        _api_calls_today = 0
        _api_day = now.day

    return _api_calls_today < DAILY_BUDGET and _api_calls_this_month < FREE_MONTHLY_LIMIT


def _log_api_usage(calls_made: int):
    """Record API calls used in this scan."""
    global _api_calls_this_month, _api_calls_today
    _api_calls_today += calls_made
    _api_calls_this_month += calls_made
    logger.info(
        f"📊 API budget: {_api_calls_today}/{DAILY_BUDGET} today, "
        f"{_api_calls_this_month}/{FREE_MONTHLY_LIMIT} this month"
    )


async def _auto_scan_loop():
    """
    Background loop: scans 7 airports every 6 hours (4x/day).
    All 26 airports covered every single day.

    COST BUDGET (staying within 2,000 free calls/month):
    ┌───────────────────────────────────────────────────┐
    │ 4 scans/day × 7 airports = 26 Inspiration calls  │
    │ Inspiration API = cached data (cheapest calls)    │
    │ Price Analysis = only if anomaly found (~rare)    │
    │ Offers Search = only if analysis confirms deal    │
    │                                                   │
    │ Typical day: 26-35 API calls                      │
    │ Busy day:    ~65 API calls (hard cap)             │
    │ Monthly:     ~900-1,200 calls (under 2,000 free)  │
    └───────────────────────────────────────────────────┘
    """
    import asyncio

    # Wait 2 minutes after startup before first scan
    await asyncio.sleep(120)

    while True:
        try:
            if not _track_api_budget():
                logger.warning(
                    f"⚠️ API budget exhausted — skipping scan. "
                    f"Today: {_api_calls_today}/{DAILY_BUDGET}, "
                    f"Month: {_api_calls_this_month}/{FREE_MONTHLY_LIMIT}"
                )
                await asyncio.sleep(6 * 60 * 60)
                continue

            from src.utils.database import get_db_session as get_db
            from src.scanner.main import FareGlitchScanner

            db = next(get_db())
            origins = get_scan_batch(7)  # 7 airports per batch
            logger.info(f"⏰ Auto-scan starting: {origins}")

            scanner = FareGlitchScanner(db)
            result = await scanner.run_scan(origins=origins)

            # Estimate API calls made:
            # 1 per origin (Inspiration) + 2 per anomaly (Analysis + Offers)
            estimated_calls = len(origins) + (result.get("anomalies_found", 0) * 2)
            _log_api_usage(estimated_calls)

            logger.info(
                f"⏰ Auto-scan done: {result.get('anomalies_found', 0)} anomalies, "
                f"{result.get('deals_validated', 0)} validated"
            )
        except Exception as e:
            logger.error(f"Auto-scan error: {e}", exc_info=True)

        # Wait 6 hours until next scan (4 scans/day)
        await asyncio.sleep(6 * 60 * 60)


@app.on_event("startup")
async def start_auto_scanner():
    """Start the background scanner if in production."""
    global _scanner_task
    if settings.is_production:
        import asyncio

        _scanner_task = asyncio.create_task(_auto_scan_loop())
        logger.info(
            "⏰ Auto-scanner: 7 airports per batch, every 6 hours (4x/day), "
            f"budget cap {DAILY_BUDGET}/day {FREE_MONTHLY_LIMIT}/month"
        )
    else:
        logger.info("⏰ Auto-scanner disabled (not in production mode)")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
