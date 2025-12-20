"""
SMS Alert System using Sinch

The core monetization: Users PAY for SMS alerts, not unlock fees.
Instagram post goes live 1 hour AFTER paying subscribers receive SMS.
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from clx.xms import Client
from clx.xms.exceptions import ApiException

from src.config import settings
from src.models.database import Deal

logger = logging.getLogger(__name__)


class SMSAlertManager:
    """
    SMS alert system for instant deal notifications.
    
    Business Model:
    1. User pays $5 to subscribe to alerts
    2. When deal found, SMS sent IMMEDIATELY to subscribers
    3. 1 hour later, deal posted to Instagram (free tier sees it then)
    4. We sell TIME and EXCLUSIVITY, not the data itself
    """
    
    def __init__(self):
        """Initialize Sinch client."""
        if not all([
            settings.sinch_service_plan_id,
            settings.sinch_api_token,
            settings.sinch_phone_number
        ]):
            logger.warning("Sinch not configured. SMS alerts disabled.")
            self.client = None
        else:
            self.client = Client(
                service_plan_id=settings.sinch_service_plan_id,
                token=settings.sinch_api_token
            )
            self.from_number = settings.sinch_phone_number
            
    def send_instant_alert(
        self,
        phone_number: str,
        deal: Deal
    ) -> bool:
        """
        Send instant SMS alert to a paying subscriber.
        
        Args:
            phone_number: Subscriber's phone number (E.164 format)
            deal: Deal object
            
        Returns:
            True if sent successfully
        """
        if not self.client:
            logger.error("Cannot send SMS - Sinch not configured")
            return False
            
        try:
            # Craft urgent, actionable message
            message = self._format_sms_message(deal)
            
            # Send SMS via Sinch
            batch = self.client.create_batch_mt(
                sender=self.from_number,
                recipients=[phone_number],
                body=message
            )
            
            logger.info(f"📱 SMS sent to {phone_number}: {batch.batch_id}")
            return True
            
        except ApiException as e:
            logger.error(f"Sinch error: {e}")
            return False
            
    def send_bulk_alerts(
        self,
        phone_numbers: List[str],
        deal: Deal
    ) -> dict:
        """
        Send SMS alerts to multiple subscribers simultaneously.
        
        Args:
            phone_numbers: List of subscriber phone numbers
            deal: Deal to alert about
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {
            "sent": 0,
            "failed": 0,
            "errors": []
        }
        
        for phone in phone_numbers:
            success = self.send_instant_alert(phone, deal)
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(phone)
                
        logger.info(
            f"Bulk SMS complete: {results['sent']} sent, "
            f"{results['failed']} failed"
        )
        
        return results
        
    def _format_sms_message(self, deal: Deal) -> str:
        """
        Format urgent, actionable SMS message.
        
        SMS should be:
        - Under 160 characters (single segment)
        - Urgent tone
        - Clear action
        - Booking link included
        """
        savings_pct = int(deal.savings_percentage * 100)
        
        # Keep it under 160 chars for single SMS billing
        message = (
            f"🚨 ERROR FARE ALERT\n"
            f"{deal.origin}→{deal.destination}\n"
            f"${int(deal.mistake_price)} (Normally ${int(deal.normal_price)})\n"
            f"SAVE {savings_pct}%\n"
            f"BOOK NOW: {deal.booking_link}\n"
            f"⚠️ Expires in 48hrs"
        )
        
        return message
        
    def schedule_instagram_post(self, deal: Deal, delay_hours: int = 1):
        """
        Schedule Instagram post for 1 hour AFTER SMS alerts sent.
        
        This creates exclusivity - paying subscribers get it first,
        free Instagram followers see it later.
        
        Args:
            deal: Deal to post
            delay_hours: Hours to wait before posting (default: 1)
        """
        from datetime import datetime, timedelta
        
        post_time = datetime.now() + timedelta(hours=delay_hours)
        
        logger.info(
            f"📸 Instagram post scheduled for {post_time.strftime('%H:%M')} "
            f"({delay_hours}hr after SMS)"
        )
        
        # In production, this would use Celery or similar for scheduling
        # For now, we'll just log it and handle manually
        
        return {
            "deal_number": deal.deal_number,
            "post_scheduled_for": post_time.isoformat(),
            "instagram_caption": self._format_instagram_caption(deal)
        }
        
    def _format_instagram_caption(self, deal: Deal) -> str:
        """Format Instagram post caption."""
        savings_pct = int(deal.savings_percentage * 100)
        
        caption = f"""
🚨 ERROR FARE ALERT

{deal.route_description}
💰 ${int(deal.mistake_price)} (Normally ${int(deal.normal_price)})
✈️ {deal.airline or 'Major Carrier'}
🛋️ {deal.cabin_class or 'Economy'} Class
📉 SAVE {savings_pct}%

⚠️ EXPIRES IN 48 HOURS

Want alerts 1 HOUR BEFORE we post here?
💬 DM "ALERTS" to subscribe

Link in bio 🔗

#errorfare #mistakefare #cheapflights #traveldeals #flighthacks #{deal.origin.lower()} #{deal.destination.lower()}
"""
        return caption.strip()


class SubscriberManager:
    """
    Manages paid SMS alert subscribers.
    
    Subscription Model:
    - $5/month for unlimited SMS alerts
    - OR $2 per alert (pay-as-you-go)
    """
    
    def __init__(self, db_session):
        """Initialize with database session."""
        self.db = db_session
        
    def get_active_subscribers(self) -> List[dict]:
        """
        Get all active SMS subscribers.
        
        Returns:
            List of subscriber dicts with phone numbers
        """
        # This would query a Subscribers table
        # For now, returning mock data for illustration
        
        query = """
        SELECT phone_number, subscription_type
        FROM subscribers
        WHERE is_active = true
        AND (
            subscription_expires_at > NOW()
            OR subscription_type = 'pay_per_alert'
        )
        """
        
        # In production, execute this query
        # subscribers = self.db.execute(query).fetchall()
        
        return []
        
    def charge_pay_per_alert(self, subscriber_id: int, amount: float = 2.00) -> bool:
        """
        Charge pay-per-alert subscriber.
        
        Args:
            subscriber_id: Subscriber ID
            amount: Amount to charge (default: $2)
            
        Returns:
            True if charged successfully
        """
        # This would integrate with Stripe API
        # to charge the subscriber's saved payment method
        
        logger.info(f"Charging subscriber {subscriber_id}: ${amount}")
        return True


# Example Usage in Scanner
def alert_subscribers_on_deal_found(deal: Deal, db_session):
    """
    Called when scanner finds a validated deal.
    
    Workflow:
    1. Get active subscribers
    2. Send SMS to all subscribers IMMEDIATELY
    3. Schedule Instagram post for +1 hour
    4. Log all sends for billing
    """
    sms_manager = SMSAlertManager()
    subscriber_manager = SubscriberManager(db_session)
    
    # Get active subscribers
    subscribers = subscriber_manager.get_active_subscribers()
    
    if not subscribers:
        logger.warning("No active subscribers to alert")
        return
        
    # Extract phone numbers
    phone_numbers = [s["phone_number"] for s in subscribers]
    
    # Send bulk SMS alerts
    results = sms_manager.send_bulk_alerts(phone_numbers, deal)
    
    logger.info(
        f"📱 Alerted {results['sent']} subscribers about {deal.deal_number}"
    )
    
    # Schedule Instagram post for 1 hour later
    instagram_post = sms_manager.schedule_instagram_post(
        deal,
        delay_hours=settings.instagram_delay_hours
    )
    
    logger.info(
        f"📸 Instagram post scheduled: {instagram_post['post_scheduled_for']}"
    )
    
    # Charge pay-per-alert subscribers
    for subscriber in subscribers:
        if subscriber.get("subscription_type") == "pay_per_alert":
            subscriber_manager.charge_pay_per_alert(subscriber["id"])
