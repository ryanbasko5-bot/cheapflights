#!/usr/bin/env python3
"""
Exhaustive Mistake Fare Scanner - Leaves no stone unturned
Scans 50 routes × 3 cabin classes × 5 date ranges = 750 searches
Uses Duffel API (unlimited test calls)
"""

import os
import sys
import time
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from integrations.duffel_client import DuffelClient
# Database saving optional - focus on finding deals
try:
    from models.deal import Deal
    from models.database import SessionLocal
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Top 50 global routes covering all continents and classes
ROUTES = [
    # USA Domestic (Premium routes with Business class demand)
    ("JFK", "LAX"), ("LAX", "JFK"),
    ("SFO", "JFK"), ("JFK", "SFO"),
    ("MIA", "LAX"), ("LAX", "MIA"),
    
    # Trans-Atlantic (High mistake fare potential)
    ("JFK", "LHR"), ("LHR", "JFK"),
    ("JFK", "CDG"), ("CDG", "JFK"),
    ("LAX", "LHR"), ("LHR", "LAX"),
    ("JFK", "FRA"), ("FRA", "JFK"),
    ("MIA", "MAD"), ("MAD", "MIA"),
    
    # Trans-Pacific (Business/First class premium routes)
    ("LAX", "HKG"), ("HKG", "LAX"),
    ("SFO", "HKG"), ("HKG", "SFO"),
    ("JFK", "NRT"), ("NRT", "JFK"),
    ("LAX", "SYD"), ("SYD", "LAX"),
    ("SFO", "SIN"), ("SIN", "SFO"),
    
    # Europe-Asia (Highest First class fares)
    ("LHR", "SIN"), ("SIN", "LHR"),
    ("LHR", "HKG"), ("HKG", "LHR"),
    ("FRA", "NRT"), ("NRT", "FRA"),
    ("CDG", "DXB"), ("DXB", "CDG"),
    
    # Australia Routes (Long-haul premium)
    ("SYD", "LHR"), ("LHR", "SYD"),
    ("SYD", "DPS"), ("DPS", "SYD"),
    ("SYD", "SIN"), ("SIN", "SYD"),
    
    # Middle East Hubs (Business class focus)
    ("LHR", "DXB"), ("DXB", "LHR"),
    ("JFK", "DOH"), ("DOH", "JFK"),
    
    # South America (Mistake fare goldmine)
    ("MIA", "GRU"), ("GRU", "MIA"),
    ("JFK", "GIG"), ("GIG", "JFK"),
]

# Cabin classes to scan
CABIN_CLASSES = ["economy", "business", "first"]

# Date ranges to check (days ahead)
DATE_RANGES = [30, 45, 60, 90, 120]

# Typical price multipliers for premium cabins
BUSINESS_MULTIPLIER = 3.5
FIRST_MULTIPLIER = 5.0

def get_cabin_multiplier(cabin_class):
    """Get price multiplier for cabin class"""
    if cabin_class == "business":
        return BUSINESS_MULTIPLIER
    elif cabin_class == "first":
        return FIRST_MULTIPLIER
    return 1.0

def search_all_routes():
    """Execute exhaustive search across all routes, cabins, and dates"""
    client = DuffelClient()
    
    if DB_AVAILABLE:
        db = SessionLocal()
    else:
        db = None
    
    all_deals = []
    total_searches = len(ROUTES) * len(CABIN_CLASSES) * len(DATE_RANGES)
    current_search = 0
    
    print(f"🚀 Starting exhaustive scan: {total_searches} searches")
    print(f"   Routes: {len(ROUTES)}")
    print(f"   Cabins: {CABIN_CLASSES}")
    print(f"   Date ranges: {DATE_RANGES} days\n")
    
    for origin, destination in ROUTES:
        route_name = f"{origin}→{destination}"
        
        # Collect economy prices across all dates for baseline
        economy_prices = []
        
        for cabin_class in CABIN_CLASSES:
            cabin_prices = []
            
            for days_ahead in DATE_RANGES:
                current_search += 
                departure_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                
                print(f"[{current_search}/{total_searches}] {route_name} {cabin_class.upper()} {departure_date}")
                
                try:
                    # Search with Duffel
                    offers = client.search_flights(
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date,
                        cabin_class=cabin_class
                    )
                    
                    if offers and len(offers) > 0:
                        # Get cheapest offer
                        cheapest = min(offers, key=lambda x: float(x['total_amount']))
                        price = Decimal(str(cheapest['total_amount']))
                        currency = cheapest['total_currency']
                        cabin_prices.append(price)
                        
                        # Store economy prices for baseline
                        if cabin_class == "economy":
                            economy_prices.append(price)
                        
                        print(f"  ✓ Found: {currency} {price:.2f}")
                    else:
                        print(f"  ✗ No flights")
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  ✗ Error: {str(e)[:50]}")
                    continue
            
            # After collecting all dates for this cabin, check for deals
            if cabin_prices:
                lowest_price = min(cabin_prices)
                
                # Calculate typical price
                if cabin_class == "economy":
                    if len(cabin_prices) >= 2:
                        typical_price = Decimal(str(statistics.median(cabin_prices)))
                    else:
                        typical_price = lowest_price * Decimal("1.2")
                else:
                    # For Business/First, use economy baseline with multiplier
                    if economy_prices:
                        economy_median = Decimal(str(statistics.median(economy_prices)))
                        multiplier = Decimal(str(get_cabin_multiplier(cabin_class)))
                        typical_price = economy_median * multiplier
                    else:
                        # Fallback if no economy data
                        typical_price = lowest_price * Decimal("1.3")
                
                # Calculate savings
                savings = typical_price - lowest_price
                if typical_price > 0:
                    savings_pct = (savings / typical_price) * 100
                else:
                    savings_pct = Decimal("0")
                
                # Only save deals with 25%+ discount
                if savings_pct >= 25:
                    deal_data = {
                        'route': route_name,
                        'origin': origin,
                        'destination': destination,
                        'cabin_class': cabin_class,
                        'price': lowest_price,
                        'typical_price': typical_price,
                        'currency': currency,
                        'savings_pct': float(savings_pct),
                        'savings_amount': float(savings),
                        'is_mistake_fare': savings_pct >= 50
                    }
                    all_deals.append(deal_data)
                    
                    if savings_pct >= 50:
                        print(f"  🔥 MISTAKE FARE! {savings_pct:.0f}% off")
                    else:
                        print(f"  💰 Good deal: {savings_pct:.0f}% off")
    
    # Sort by savings percentage
    all_deals.sort(key=lambda x: x['savings_pct'], reverse=True)
    
    # Print results
    print("\n" + "="*80)
    print(f"EXHAUSTIVE SCAN COMPLETE - Top 20 Deals")
    print("="*80 + "\n")
    
    if not all_deals:
        print("❌ No deals found meeting 25% threshold")
        return
    
    # Save top 20 to database
    saved_count = 0
    if db:
        for i, deal in enumerate(all_deals[:20], 1):
            try:
                # Create deal object
                db_deal = Deal(
                    origin=deal['origin'],
                    destination=deal['destination'],
                    price=deal['price'],
                    currency=deal['currency'],
                    departure_date=datetime.now() + timedelta(days=30),  # Approximate
                    airline="Multiple",
                    source="duffel_exhaustive",
                    typical_price=deal['typical_price'],
                    savings_percentage=Decimal(str(deal['savings_pct'])),
                    is_mistake_fare=deal['is_mistake_fare'],
                    expires_at=datetime.now() + timedelta(hours=6 if deal['is_mistake_fare'] else 24),
                    cabin_class=deal['cabin_class']
                )
                
                db.add(db_deal)
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving deal: {e}")
        
        # Commit all deals
        try:
            db.commit()
            print(f"✅ Saved {saved_count} deals to database")
        except Exception as e:
            db.rollback()
            print(f"❌ Error saving to database: {e}")
        finally:
            db.close()
    
    # Print top 20 deals
    for i, deal in enumerate(all_deals[:20], 1):
        try:
            # Print deal
            emoji = "🔥" if deal['is_mistake_fare'] else "💰"
            cabin_badge = f"[{deal['cabin_class'].upper()}]"
            print(f"{i:2d}. {emoji} {deal['route']} {cabin_badge}")
            print(f"    Price: {deal['currency']} {deal['price']:.2f}")
            print(f"    Typical: {deal['currency']} {deal['typical_price']:.2f}")
            print(f"    Savings: {deal['savings_pct']:.0f}% ({deal['currency']} {deal['savings_amount']:.2f})")
            if deal['is_mistake_fare']:
                print(f"    🚨 MISTAKE FARE - 50%+ DISCOUNT!")
            print()
            
        except Exception as e:
            print(f"Error displaying deal: {e}")
    
    # Close database if available
    if db:
        db.close()
    
    # Summary stats
    mistake_fares = sum(1 for d in all_deals if d['is_mistake_fare'])
    good_deals = len(all_deals) - mistake_fares
    
    print(f"\n📊 Summary:")
    print(f"   Total searches: {total_searches}")
    print(f"   Deals found: {len(all_deals)}")
    print(f"   Mistake fares (50%+): {mistake_fares}")
    print(f"   Good deals (25-49%): {good_deals}")
    print(f"   Success rate: {(len(all_deals)/total_searches)*100:.1f}%")

if __name__ == "__main__":
    search_all_routes()
