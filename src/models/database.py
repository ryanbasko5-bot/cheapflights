"""
Database Models for FareGlitch

Defines the data structure for deals, pricing history, and transactions.
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class DealStatus(str, Enum):
    """Deal lifecycle status."""
    DETECTED = "detected"  # Price anomaly found
    VALIDATED = "validated"  # Confirmed bookable
    PUBLISHED = "published"  # Live on platform
    EXPIRED = "expired"  # Past expiry time
    CANCELED = "canceled"  # Airline canceled fare


class Deal(Base):
    """Mistake fare deal."""
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_number = Column(String, unique=True, index=True)  # e.g., "DEAL#402"
    
    # Route Information
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    route_description = Column(String)  # e.g., "NYC to Tokyo"
    
    # Pricing
    normal_price = Column(Float, nullable=False)
    mistake_price = Column(Float, nullable=False)
    savings_amount = Column(Float, nullable=False)
    savings_percentage = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Flight Details
    cabin_class = Column(String)  # economy, premium_economy, business, first
    airline = Column(String)
    airline_alliance = Column(String)  # Star Alliance, OneWorld, SkyTeam
    
    # Dates
    travel_dates_start = Column(DateTime)
    travel_dates_end = Column(DateTime)
    detected_at = Column(DateTime, default=func.now())
    validated_at = Column(DateTime)
    published_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Status
    status = Column(String, default=DealStatus.DETECTED)
    is_active = Column(Boolean, default=True)
    
    # Booking Information (hidden until unlocked)
    booking_link = Column(Text)
    booking_instructions = Column(Text)
    specific_dates = Column(Text)  # JSON string of available date ranges
    
    # HubSpot Integration
    hubspot_product_id = Column(String)
    hubspot_page_url = Column(String)
    
    # Teaser Content (public)
    teaser_headline = Column(String)
    teaser_description = Column(Text)
    teaser_image_url = Column(String)
    
    # Metadata
    unlock_fee = Column(Float, default=7.00)
    total_unlocks = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Relationships
    unlocks = relationship("DealUnlock", back_populates="deal")
    pricing_history = relationship("PriceHistory", back_populates="deal")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_deal_status_active", "status", "is_active"),
        Index("idx_deal_route", "origin", "destination"),
        Index("idx_deal_dates", "travel_dates_start", "travel_dates_end"),
    )


class DealUnlock(Base):
    """Record of user unlocking a deal."""
    __tablename__ = "deal_unlocks"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    
    # User/Contact Information
    email = Column(String, index=True)
    hubspot_contact_id = Column(String)
    
    # Transaction
    unlock_fee_paid = Column(Float, nullable=False)
    payment_id = Column(String)  # HubSpot payment/order ID
    payment_status = Column(String)  # succeeded, refunded
    
    # Timestamps
    unlocked_at = Column(DateTime, default=func.now())
    refunded_at = Column(DateTime)
    
    # Glitch Guarantee
    refund_requested = Column(Boolean, default=False)
    refund_reason = Column(Text)
    
    # Relationships
    deal = relationship("Deal", back_populates="unlocks")
    
    __table_args__ = (
        Index("idx_unlock_email_deal", "email", "deal_id"),
    )


class PriceHistory(Base):
    """Historical pricing data for route analysis."""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    
    # Route
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    cabin_class = Column(String)
    
    # Price
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Source
    data_source = Column(String)  # amadeus, duffel, manual
    checked_at = Column(DateTime, default=func.now())
    
    # Relationships
    deal = relationship("Deal", back_populates="pricing_history")
    
    __table_args__ = (
        Index("idx_price_route", "origin", "destination", "checked_at"),
    )


class ScanLog(Base):
    """Log of scanner runs for monitoring."""
    __tablename__ = "scan_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    routes_checked = Column(Integer, default=0)
    anomalies_found = Column(Integer, default=0)
    deals_validated = Column(Integer, default=0)
    deals_published = Column(Integer, default=0)
    
    errors = Column(Text)
    status = Column(String)  # success, failed, partial
    
    __table_args__ = (
        Index("idx_scan_time", "started_at"),
    )


class SubscriptionType(str, Enum):
    """Subscription tier types."""
    FREE = "free"  # Instagram only
    SMS_MONTHLY = "sms_monthly"  # $5/month unlimited SMS
    PAY_PER_ALERT = "pay_per_alert"  # $2 per alert


class Subscriber(Base):
    """SMS alert subscriber - the core monetization."""
    __tablename__ = "subscribers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact Info
    phone_number = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, index=True)
    
    # Subscription Details
    subscription_type = Column(String, default=SubscriptionType.FREE)
    is_active = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=func.now())
    subscription_expires_at = Column(DateTime)
    
    # Payment Info
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    last_payment_date = Column(DateTime)
    
    # Preferences
    regions = Column(Text)  # JSON list: ["asia", "europe"]
    cabin_classes = Column(Text)  # JSON list: ["business", "first"]
    min_savings_percentage = Column(Float, default=0.50)  # 50%
    
    # Stats
    total_alerts_received = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    last_alert_sent_at = Column(DateTime)
    
    # Relationships
    alert_logs = relationship("AlertLog", back_populates="subscriber")
    
    __table_args__ = (
        Index("idx_subscriber_active", "is_active", "subscription_type"),
        Index("idx_subscriber_phone", "phone_number"),
    )


class AlertLog(Base):
    """Log of SMS alerts sent (for billing and analytics)."""
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    
    # SMS Details
    sent_at = Column(DateTime, default=func.now())
    twilio_message_sid = Column(String)
    phone_number = Column(String)
    
    # Billing
    charged_amount = Column(Float, default=0.0)  # $0 for monthly, $2 for pay-per-alert
    stripe_charge_id = Column(String)
    
    # Engagement
    booking_link_clicked = Column(Boolean, default=False)
    clicked_at = Column(DateTime)
    
    # Relationships
    subscriber = relationship("Subscriber", back_populates="alert_logs")
    
    __table_args__ = (
        Index("idx_alert_sent", "sent_at"),
        Index("idx_alert_subscriber", "subscriber_id", "sent_at"),
    )
