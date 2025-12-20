#!/usr/bin/env python3
"""
Manual deal creator script for testing.

Usage:
    python scripts/create_deal.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.models.database import Deal, DealStatus
from src.utils.database import get_db_session


def create_sample_deal():
    """Create a sample deal for testing."""
    
    print("Creating sample deal...")
    
    db = next(get_db_session())
    
    # Get next deal number
    last_deal = db.query(Deal).order_by(Deal.id.desc()).first()
    deal_num = (last_deal.id + 1) if last_deal else 1
    
    deal = Deal(
        deal_number=f"DEAL#{deal_num:03d}",
        origin="JFK",
        destination="NRT",
        route_description="New York (JFK) to Tokyo (NRT)",
        normal_price=2500.0,
        mistake_price=420.0,
        savings_amount=2080.0,
        savings_percentage=0.832,
        currency="USD",
        cabin_class="business",
        airline="ANA - All Nippon Airways",
        airline_alliance="Star Alliance",
        travel_dates_start=datetime.now() + timedelta(days=30),
        travel_dates_end=datetime.now() + timedelta(days=120),
        status=DealStatus.VALIDATED,
        is_active=True,
        booking_link="https://www.google.com/flights",
        booking_instructions="Book directly on ANA website. Use incognito mode. Clear cookies first.",
        specific_dates='{"ranges": ["2025-12-15 to 2025-12-22", "2026-01-10 to 2026-01-20"]}',
        teaser_headline="🚨 Business Class Glitch: NYC to Tokyo",
        teaser_description="Fly ANA Business Class for 83% off. Normally $2,500, now just $420!",
        unlock_fee=7.0,
        expires_at=datetime.now() + timedelta(hours=48)
    )
    
    db.add(deal)
    db.commit()
    db.refresh(deal)
    
    print(f"✅ Created {deal.deal_number}")
    print(f"   Route: {deal.route_description}")
    print(f"   Price: ${deal.mistake_price} (Save ${deal.savings_amount})")
    print(f"   Expires: {deal.expires_at}")
    
    return deal


if __name__ == "__main__":
    create_sample_deal()
