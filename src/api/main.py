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
        "https://fareglitch.com",
        "https://www.fareglitch.com",
        "https://api.fareglitch.com"
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
    payment_id: str  # HubSpot payment/order ID


class RefundRequest(BaseModel):
    """Request refund under Glitch Guarantee."""
    email: EmailStr
    deal_number: str
    reason: str


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
    Unlock a deal after payment.
    
    This endpoint is called by HubSpot webhook after successful payment.
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
    
    if existing_unlock:
        # Already unlocked, return details
        return deal
        
    # Record unlock
    hubspot = HubSpotIntegration()
    unlock = await hubspot.record_unlock(
        deal=deal,
        email=unlock_request.email,
        payment_id=unlock_request.payment_id
    )
    
    db.add(unlock)
    db.commit()
    
    # Trigger delivery workflow
    await hubspot.trigger_delivery_workflow(deal, unlock.hubspot_contact_id)
    
    return deal


@app.post("/refunds/request")
async def request_refund(
    refund_request: RefundRequest,
    db: Session = Depends(get_db_session)
):
    """
    Request refund under Glitch Guarantee.
    
    Users can request refund if airline cancels the fare within 48 hours.
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
        
    # Check if within 48 hour window
    hours_since_unlock = (datetime.now() - unlock.unlocked_at).total_seconds() / 3600
    
    if hours_since_unlock > 48 and settings.enable_glitch_guarantee:
        raise HTTPException(
            status_code=400,
            detail="Refund window expired (48 hours)"
        )
        
    # Process refund
    hubspot = HubSpotIntegration()
    success = await hubspot.process_refund(unlock, refund_request.reason)
    
    if success:
        db.commit()
        return {"status": "success", "message": "Refund processed"}
    else:
        raise HTTPException(status_code=500, detail="Refund processing failed")


@app.get("/deals/{deal_number}/stats")
async def get_deal_stats(
    deal_number: str,
    db: Session = Depends(get_db_session)
):
    """
    Get statistics for a deal (admin only in production).
    """
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
    payload: dict,
    db: Session = Depends(get_db_session)
):
    """
    Webhook endpoint for HubSpot payment success.
    
    HubSpot will call this when a payment is completed.
    """
    # Extract payment info from HubSpot webhook payload
    # Payload structure depends on HubSpot Commerce Hub configuration
    
    deal_number = payload.get("deal_number")
    email = payload.get("email")
    payment_id = payload.get("payment_id")
    
    if not all([deal_number, email, payment_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")
        
    # Process unlock
    unlock_request = UnlockDealRequest(email=email, payment_id=payment_id)
    result = await unlock_deal(deal_number, unlock_request, db)
    
    return {"status": "success", "deal": result}


@app.post("/webhooks/hubspot/refund-request")
async def hubspot_refund_webhook(
    payload: dict,
    db: Session = Depends(get_db_session)
):
    """
    Webhook endpoint for HubSpot refund requests.
    
    Triggered when support ticket is created for refund.
    """
    email = payload.get("email")
    deal_number = payload.get("deal_number")
    reason = payload.get("reason", "Airline canceled fare")
    
    refund_request = RefundRequest(
        email=email,
        deal_number=deal_number,
        reason=reason
    )
    
    return await request_refund(refund_request, db)


# Admin Endpoints (would be protected in production)

@app.post("/admin/deals/{deal_id}/publish")
async def admin_publish_deal(
    deal_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Manually publish a deal to HubSpot.
    """
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
