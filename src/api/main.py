"""
FastAPI Backend for FareGlitch

Provides:
- Public API for deal teasers
- Webhook endpoints for HubSpot
- Admin API for deal management
"""
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from src.config import settings
from src.models.database import Deal, DealUnlock, DealStatus
from src.utils.database import get_db_session, init_db
from src.hubspot.integration import HubSpotIntegration
from src.validator.duffel_client import DuffelValidator

# Initialize FastAPI app
app = FastAPI(
    title="FareGlitch API",
    description="Mistake fare detection and gated marketplace API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    
    class Config:
        from_attributes = True


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

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
        # Continue anyway - some endpoints don't need DB


@app.get("/")
async def root():
    """API health check."""
    return {
        "status": "online",
        "service": "FareGlitch API",
        "version": "1.0.0"
    }


@app.get("/deals/active", response_model=List[DealTeaserResponse])
async def get_active_deals(
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db_session)
):
    """
    Get list of active deal teasers.
    
    Returns public information only (no booking details).
    """
    deals = db.query(Deal).filter(
        Deal.status == DealStatus.PUBLISHED,
        Deal.is_active == True,
        Deal.expires_at > datetime.now()
    ).order_by(Deal.published_at.desc()).limit(limit).all()
    
    return deals


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
