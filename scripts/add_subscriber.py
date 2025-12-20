#!/usr/bin/env python3
"""
Quick script to add a subscriber to the database
Usage: python scripts/add_subscriber.py +61412345678 sms_monthly
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.database import engine, Base, Subscriber
from sqlalchemy.orm import Session


def add_subscriber(phone_number: str, subscription_type: str = "sms_monthly", regions: str = "oceania,asia"):
    """
    Add a new subscriber to the database
    
    Args:
        phone_number: Phone with country code (e.g., +61412345678)
        subscription_type: 'sms_monthly' or 'pay_per_alert'
        regions: Comma-separated regions (e.g., 'oceania,asia,europe')
    """
    # Initialize database if needed
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Check if already exists
        existing = session.query(Subscriber).filter_by(phone_number=phone_number).first()
        
        if existing:
            print(f"⚠️  Subscriber {phone_number} already exists!")
            print(f"   Status: {'Active' if existing.is_active else 'Inactive'}")
            print(f"   Type: {existing.subscription_type}")
            print(f"   Subscribed: {existing.subscribed_at}")
            
            response = input("\n   Update? (y/n): ")
            if response.lower() != 'y':
                return
            
            # Update existing
            existing.subscription_type = subscription_type
            existing.is_active = True
            existing.regions = regions
            
            if subscription_type == 'sms_monthly':
                existing.subscription_expires_at = datetime.now() + timedelta(days=30)
            
            session.commit()
            print(f"\n✅ Updated subscriber {phone_number}")
            
        else:
            # Create new subscriber
            subscriber = Subscriber(
                phone_number=phone_number,
                subscription_type=subscription_type,
                is_active=True,
                regions=regions,
                subscribed_at=datetime.now()
            )
            
            # Set expiry for monthly subscribers
            if subscription_type == 'sms_monthly':
                subscriber.subscription_expires_at = datetime.now() + timedelta(days=30)
            
            session.add(subscriber)
            session.commit()
            
            print(f"\n✅ Added new subscriber!")
            print(f"   Phone: {phone_number}")
            print(f"   Type: {subscription_type}")
            print(f"   Regions: {regions}")
            
            if subscription_type == 'sms_monthly':
                print(f"   Expires: {subscriber.subscription_expires_at.strftime('%Y-%m-%d')}")


def list_subscribers():
    """
    List all subscribers
    """
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        subscribers = session.query(Subscriber).all()
        
        if not subscribers:
            print("📭 No subscribers yet")
            return
        
        print(f"\n📊 Total Subscribers: {len(subscribers)}")
        print("="*80)
        
        active = [s for s in subscribers if s.is_active]
        inactive = [s for s in subscribers if not s.is_active]
        
        print(f"✅ Active: {len(active)}")
        print(f"❌ Inactive: {len(inactive)}")
        print("="*80 + "\n")
        
        for sub in subscribers:
            status = "✅" if sub.is_active else "❌"
            print(f"{status} {sub.phone_number}")
            print(f"   Type: {sub.subscription_type}")
            print(f"   Regions: {sub.regions}")
            print(f"   Subscribed: {sub.subscribed_at.strftime('%Y-%m-%d')}")
            
            if sub.subscription_expires_at:
                days_left = (sub.subscription_expires_at - datetime.now()).days
                print(f"   Expires: {sub.subscription_expires_at.strftime('%Y-%m-%d')} ({days_left} days left)")
            
            print(f"   Alerts received: {sub.total_alerts_received}")
            print()


def main():
    """
    Main CLI handler
    """
    if len(sys.argv) == 1:
        print("Usage:")
        print("  Add subscriber:  python scripts/add_subscriber.py +61412345678 sms_monthly")
        print("  List all:        python scripts/add_subscriber.py --list")
        print()
        print("Subscription types:")
        print("  - sms_monthly     ($5/month, unlimited alerts)")
        print("  - pay_per_alert   ($2 per alert)")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        list_subscribers()
        return
    
    phone_number = sys.argv[1]
    subscription_type = sys.argv[2] if len(sys.argv) > 2 else "sms_monthly"
    regions = sys.argv[3] if len(sys.argv) > 3 else "oceania,asia"
    
    # Validate phone number format
    if not phone_number.startswith('+'):
        print("❌ Phone number must include country code (e.g., +61412345678)")
        sys.exit(1)
    
    # Validate subscription type
    if subscription_type not in ['sms_monthly', 'pay_per_alert']:
        print("❌ Subscription type must be 'sms_monthly' or 'pay_per_alert'")
        sys.exit(1)
    
    add_subscriber(phone_number, subscription_type, regions)


if __name__ == "__main__":
    main()
