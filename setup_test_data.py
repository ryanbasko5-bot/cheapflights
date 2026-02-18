"""
Quick Test Script - Verify FareGlitch Setup

This script:
1. Creates test subscribers (premium + free)
2. Creates test deals
3. Tests the authentication and deal filtering
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add src to path
sys.path.insert(0, '/workspaces/cheapflights')

from src.models.database import (
    Base, Deal, DealStatus, Subscriber, SubscriptionType
)
from src.utils.database import get_db_session, init_db
from src.utils.currency import get_currency_for_airport


def create_test_subscribers(db: Session):
    """Create test subscribers."""
    print("📱 Creating test subscribers...")
    
    # Check if already exist
    existing = db.query(Subscriber).filter(
        Subscriber.email.in_(["premium@test.com", "free@test.com"])
    ).all()
    
    if existing:
        print("  ⚠️  Test subscribers already exist. Skipping...")
        return existing
    
    # Premium member
    premium = Subscriber(
        phone_number="+61411111111",
        email="premium@test.com",
        subscription_type=SubscriptionType.SMS_MONTHLY,
        is_active=True,
        subscribed_at=datetime.now(),
        subscription_expires_at=datetime.now() + timedelta(days=30)
    )
    db.add(premium)
    print("  ✅ Created premium member: premium@test.com (+61411111111)")
    
    # Free member
    free = Subscriber(
        phone_number="+61422222222",
        email="free@test.com",
        subscription_type=SubscriptionType.FREE,
        is_active=True,
        subscribed_at=datetime.now()
    )
    db.add(free)
    print("  ✅ Created free member: free@test.com (+61422222222)")
    
    db.commit()
    return [premium, free]


def create_test_deals(db: Session):
    """Create test deals with different publish times."""
    print("\n✈️  Creating test deals...")
    
    # Check if already exist
    existing = db.query(Deal).filter(
        Deal.deal_number.in_(["TEST001", "TEST002", "TEST003"])
    ).all()
    
    if existing:
        print("  ⚠️  Test deals already exist. Updating publish times...")
        for deal in existing:
            db.delete(deal)
        db.commit()
    
    # Deal 1: Just published (premium only) - USD from NYC
    deal1 = Deal(
        deal_number="TEST001",
        origin="SYD",
        destination="LAX",
        route_description="Sydney to Los Angeles",
        normal_price=1800.00,
        mistake_price=680.00,
        savings_amount=1120.00,
        savings_percentage=62.2,
        currency=get_currency_for_airport("SYD"),  # AUD for Sydney
        cabin_class="economy",
        airline="Qantas",
        status=DealStatus.PUBLISHED,
        is_active=True,
        published_at=datetime.now(),  # Just now - PREMIUM ONLY
        expires_at=datetime.now() + timedelta(hours=24),
        teaser_headline="🔥 Sydney to LA for A$680!",
        teaser_description="Amazing mistake fare - usually A$1,800"
    )
    db.add(deal1)
    print("  ✅ TEST001: Sydney → LA (JUST PUBLISHED - Premium only)")
    
    # Deal 2: Published 30 minutes ago (still premium only) - GBP from London
    deal2 = Deal(
        deal_number="TEST002",
        origin="LHR",
        destination="BKK",
        route_description="London to Bangkok",
        normal_price=680.00,
        mistake_price=298.00,
        savings_amount=382.00,
        savings_percentage=56.2,
        currency=get_currency_for_airport("LHR"),  # GBP for London
        cabin_class="economy",
        airline="British Airways",
        status=DealStatus.PUBLISHED,
        is_active=True,
        published_at=datetime.now() - timedelta(minutes=30),  # 30 mins ago
        expires_at=datetime.now() + timedelta(hours=20),
        teaser_headline="🌴 London to Bangkok £298!",
        teaser_description="Incredible deal - save £382"
    )
    db.add(deal2)
    print("  ✅ TEST002: London → Bangkok (30 mins ago - Premium only)")
    
    # Deal 3: Published 2 hours ago (public access) - USD from NYC
    deal3 = Deal(
        deal_number="TEST003",
        origin="JFK",
        destination="TYO",
        route_description="New York to Tokyo",
        normal_price=1500.00,
        mistake_price=645.00,
        savings_amount=855.00,
        savings_percentage=57.0,
        currency=get_currency_for_airport("JFK"),  # USD for New York
        cabin_class="business",
        airline="ANA",
        status=DealStatus.PUBLISHED,
        is_active=True,
        published_at=datetime.now() - timedelta(hours=2),  # 2 hours ago - PUBLIC
        expires_at=datetime.now() + timedelta(hours=12),
        teaser_headline="✨ Business Class to Tokyo $645!",
        teaser_description="Business class mistake fare - save $855"
    )
    db.add(deal3)
    print("  ✅ TEST003: New York → Tokyo (2 hours ago - PUBLIC ACCESS)")
    
    db.commit()
    return [deal1, deal2, deal3]


def test_deal_filtering():
    """Test the deal filtering logic."""
    print("\n🧪 Testing deal filtering logic...")
    
    from src.api.auth import can_see_deal, is_premium_member
    
    db = next(get_db_session())
    
    # Get test data
    premium = db.query(Subscriber).filter(Subscriber.email == "premium@test.com").first()
    free_user = db.query(Subscriber).filter(Subscriber.email == "free@test.com").first()
    deals = db.query(Deal).filter(Deal.deal_number.in_(["TEST001", "TEST002", "TEST003"])).all()
    
    if not premium or not free_user or len(deals) != 3:
        print("  ❌ Test data not found. Run the script first to create it.")
        return
    
    print(f"\n  Premium member status: {is_premium_member(premium)}")
    print(f"  Free member status: {is_premium_member(free_user)}")
    
    print("\n  📊 Deal Visibility Test:")
    print("  " + "-" * 60)
    
    for deal in deals:
        hours_ago = (datetime.now() - deal.published_at).total_seconds() / 3600
        
        premium_can_see = can_see_deal(deal, premium)
        free_can_see = can_see_deal(deal, free_user)
        public_can_see = can_see_deal(deal, None)
        
        print(f"\n  {deal.deal_number}: {deal.origin} → {deal.destination}")
        print(f"    Published: {hours_ago:.1f} hours ago")
        print(f"    Premium member: {'✅ CAN SEE' if premium_can_see else '❌ CANNOT SEE'}")
        print(f"    Free member:    {'✅ CAN SEE' if free_can_see else '❌ CANNOT SEE'}")
        print(f"    Public (no auth): {'✅ CAN SEE' if public_can_see else '❌ CANNOT SEE'}")


def main():
    """Run all tests."""
    print("=" * 70)
    print("🚀 FareGlitch Test Setup")
    print("=" * 70)
    
    # Initialize database
    print("\n🗄️  Initializing database...")
    try:
        init_db()
        print("  ✅ Database initialized")
    except Exception as e:
        print(f"  ⚠️  Database already exists: {e}")
    
    # Get database session
    db = next(get_db_session())
    
    # Create test data
    subscribers = create_test_subscribers(db)
    deals = create_test_deals(db)
    
    # Test filtering
    test_deal_filtering()
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n📝 Test Credentials:")
    print("  Premium Member:")
    print("    Email: premium@test.com")
    print("    Phone: +61411111111")
    print("\n  Free Member:")
    print("    Email: free@test.com")
    print("    Phone: +61422222222")
    
    print("\n🌐 Next Steps:")
    print("  1. Start API: ./launch_api.sh")
    print("  2. Visit: http://localhost:8000/docs")
    print("  3. Test login with premium@test.com")
    print("  4. Check deals: GET /deals/active")
    print("  5. Open website: cd website && python -m http.server 8080")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
