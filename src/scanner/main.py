"""
Scanner Main Module

Orchestrates the scanning process:
1. Query Amadeus for price anomalies
2. Validate fares via Duffel
3. Send alerts for confirmed deals
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from src.config import settings
from src.models.database import Deal, ScanLog, DealStatus
from src.scanner.amadeus_client import PriceAnomalyDetector, MAJOR_HUBS
from src.validator.duffel_client import DuffelValidator
from src.utils.alerts import AlertManager
from src.utils.sms_alerts import SMSAlertManager, SubscriberManager
from src.utils.database import get_db_session

logging.basicConfig(
    level=logging.INFO if not settings.debug_mode else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FareGlitchScanner:
    """Main scanner orchestrator."""
    
    def __init__(self, db_session: Session):
        """
        Initialize scanner with database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.detector = PriceAnomalyDetector(db_session)
        self.validator = DuffelValidator()
        self.alerts = AlertManager()
        self.sms_alerts = SMSAlertManager()
        self.subscriber_mgr = SubscriberManager(db_session)
        
    async def run_scan(
        self,
        origins: List[str] = None,
        test_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a full scan cycle.
        
        Args:
            origins: List of origin airports to scan (default: MAJOR_HUBS)
            test_mode: If True, don't publish deals or send alerts
            
        Returns:
            Summary of scan results
        """
        origins = origins or MAJOR_HUBS
        scan_log = ScanLog(started_at=datetime.now())
        
        try:
            logger.info(f"🔍 Starting scan of {len(origins)} origin airports...")
            
            # Step 1: Detect price anomalies
            anomalies = await self.detector.scan_routes(origins)
            scan_log.routes_checked = len(origins)
            scan_log.anomalies_found = len(anomalies)
            
            logger.info(f"Found {len(anomalies)} potential anomalies")
            
            if not anomalies:
                logger.info("No anomalies detected in this scan")
                scan_log.status = "success"
                scan_log.completed_at = datetime.now()
                self.db.add(scan_log)
                self.db.commit()
                return {
                    "status": "success",
                    "anomalies_found": 0,
                    "deals_validated": 0,
                    "deals_published": 0
                }
            
            # Step 2: Validate each anomaly
            validated_deals = []
            for anomaly in anomalies:
                logger.info(f"Validating {anomaly['route']}...")
                
                is_valid = await self.validator.validate_fare(
                    origin=anomaly["origin"],
                    destination=anomaly["destination"],
                    expected_price=anomaly["current_price"],
                    departure_date=anomaly.get("departure_date")
                )
                
                if is_valid:
                    validated_deals.append(anomaly)
                    logger.info(f"✅ Validated: {anomaly['route']}")
                else:
                    logger.warning(f"❌ Could not validate: {anomaly['route']}")
                    
                # Small delay to avoid rate limiting
                await asyncio.sleep(2)
                
            scan_log.deals_validated = len(validated_deals)
            
            # Step 3: Create deal records and send SMS alerts
            published_count = 0
            for deal_data in validated_deals:
                deal = await self._create_deal(deal_data)
                
                if not test_mode:
                    # Send internal alert to founder
                    await self.alerts.send_deal_alert(deal)
                    
                    # INSTANT SMS ALERTS to paying subscribers
                    if settings.enable_sms_alerts:
                        subscribers = self.subscriber_mgr.get_active_subscribers()
                        if subscribers:
                            phone_numbers = [s["phone_number"] for s in subscribers]
                            results = self.sms_alerts.send_bulk_alerts(phone_numbers, deal)
                            logger.info(
                                f"📱 SMS ALERTS SENT: {results['sent']} subscribers notified "
                                f"for {deal.deal_number}"
                            )
                            
                            # Schedule Instagram post for 1 hour later
                            if settings.enable_instagram_posting:
                                instagram = self.sms_alerts.schedule_instagram_post(
                                    deal,
                                    delay_hours=settings.instagram_delay_hours
                                )
                                logger.info(
                                    f"📸 Instagram scheduled: "
                                    f"{instagram['post_scheduled_for']}"
                                )
                    
                    # Auto-publish to HubSpot if enabled
                    if settings.enable_auto_publish:
                        from src.hubspot.integration import HubSpotIntegration
                        hubspot = HubSpotIntegration()
                        await hubspot.publish_deal(deal)
                        published_count += 1
                        
                    # AUTO-UPDATE WEBSITE with new deal
                    try:
                        from src.hubspot.website_updater import auto_update_website
                        website_result = auto_update_website([deal])
                        if website_result.get("hubdb_updated"):
                            logger.info(f"🌐 Website updated with {deal.deal_number}")
                        if website_result.get("blog_posts_created"):
                            logger.info(f"📝 Blog post created for {deal.deal_number}")
                    except Exception as e:
                        logger.warning(f"Website update failed (non-critical): {e}")
                else:
                    logger.info(f"[TEST MODE] Would send SMS for: {deal.teaser_headline}")
                    
            scan_log.deals_published = published_count
            scan_log.status = "success"
            scan_log.completed_at = datetime.now()
            
            self.db.add(scan_log)
            self.db.commit()
            
            logger.info(
                f"✅ Scan complete: {len(anomalies)} anomalies, "
                f"{len(validated_deals)} validated, {published_count} published"
            )
            
            return {
                "status": "success",
                "anomalies_found": len(anomalies),
                "deals_validated": len(validated_deals),
                "deals_published": published_count,
                "deals": [self._deal_to_dict(d) for d in validated_deals]
            }
            
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            scan_log.status = "failed"
            scan_log.errors = str(e)
            scan_log.completed_at = datetime.now()
            self.db.add(scan_log)
            self.db.commit()
            raise
            
    async def _create_deal(self, anomaly_data: Dict[str, Any]) -> Deal:
        """
        Create a Deal record from validated anomaly data.
        
        Args:
            anomaly_data: Validated anomaly information
            
        Returns:
            Created Deal object
        """
        # Generate deal number
        last_deal = self.db.query(Deal).order_by(Deal.id.desc()).first()
        deal_num = (last_deal.id + 1) if last_deal else 1
        
        # Create teaser headline
        route_desc = f"{anomaly_data['origin']} to {anomaly_data['destination']}"
        savings_pct = int(anomaly_data['savings_percentage'] * 100)
        
        airline = anomaly_data.get("airline", "")
        cabin = anomaly_data.get("cabin_class", "economy")
        booking_link = anomaly_data.get("booking_link", "")

        deal = Deal(
            deal_number=f"DEAL#{deal_num:03d}",
            origin=anomaly_data["origin"],
            destination=anomaly_data["destination"],
            route_description=route_desc,
            normal_price=anomaly_data["historical_avg"],
            mistake_price=anomaly_data["current_price"],
            savings_amount=anomaly_data["savings_amount"],
            savings_percentage=anomaly_data["savings_percentage"],
            currency=anomaly_data["currency"],
            detected_at=datetime.now(),
            validated_at=datetime.now(),
            status=DealStatus.VALIDATED,
            teaser_headline=f"{'✈️ ' + airline + ' ' if airline else ''}Mistake Fare: {route_desc} ({savings_pct}% Off)",
            teaser_description=(
                f"Normally ${int(anomaly_data['historical_avg'])}, "
                f"now ${int(anomaly_data['current_price'])}"
                f"{' on ' + airline if airline else ''}"
                f" ({cabin})" if cabin else ""
            ),
            unlock_fee=settings.unlock_fee_default
        )
        
        self.db.add(deal)
        self.db.commit()
        self.db.refresh(deal)
        
        return deal
        
    def _deal_to_dict(self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Convert anomaly data to dictionary for response."""
        return {
            "route": anomaly["route"],
            "origin": anomaly["origin"],
            "destination": anomaly["destination"],
            "current_price": anomaly["current_price"],
            "normal_price": anomaly["historical_avg"],
            "savings": anomaly["savings_amount"],
            "savings_pct": f"{int(anomaly['savings_percentage'] * 100)}%",
            "currency": anomaly["currency"],
            "airline": anomaly.get("airline"),
            "cabin_class": anomaly.get("cabin_class"),
            "bookable": anomaly.get("bookable", False),
            "booking_link": anomaly.get("booking_link"),
            "departure_date": anomaly.get("departure_date"),
            "pct_below_median": anomaly.get("pct_below_median"),
        }


async def main():
    """Main entry point for scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FareGlitch Scanner")
    parser.add_argument("--test", action="store_true", help="Run in test mode (no alerts/publishing)")
    parser.add_argument("--interval", type=int, help="Run continuously with interval (seconds)")
    parser.add_argument("--origins", nargs="+", help="Specific origins to scan")
    
    args = parser.parse_args()
    
    if args.interval:
        logger.info(f"Running scanner every {args.interval} seconds (Ctrl+C to stop)")
        while True:
            try:
                db = next(get_db_session())
                scanner = FareGlitchScanner(db)
                await scanner.run_scan(origins=args.origins, test_mode=args.test)
                logger.info(f"Waiting {args.interval} seconds until next scan...")
                await asyncio.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Scanner stopped by user")
                break
            except Exception as e:
                logger.error(f"Scan error: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error
    else:
        # Single scan
        db = next(get_db_session())
        scanner = FareGlitchScanner(db)
        result = await scanner.run_scan(origins=args.origins, test_mode=args.test)
        
        logger.info("="*60)
        logger.info("SCAN RESULTS")
        logger.info("="*60)
        logger.info(f"Anomalies Found: {result['anomalies_found']}")
        logger.info(f"Deals Validated: {result['deals_validated']}")
        logger.info(f"Deals Published: {result['deals_published']}")
        
        if result.get('validated_deals'):
            logger.info("VALIDATED DEALS:")
            for deal in result['validated_deals']:
                logger.info(f"  • {deal['route']}: ${deal['current_price']} (Save {deal['savings_pct']})")


if __name__ == "__main__":
    asyncio.run(main())
