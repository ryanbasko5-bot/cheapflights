"""
HubSpot Integration Module

Handles all HubSpot automation:
- Publishing deals to HubSpot CMS/Landing Pages
- Creating products for unlock fees
- Setting up payment links
- Configuring workflows for deal delivery
- Processing payments and refunds
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from hubspot import HubSpot
from hubspot.crm.products import SimplePublicObjectInput, ApiException

from src.config import settings
from src.models.database import Deal, DealUnlock, DealStatus

logger = logging.getLogger(__name__)


class HubSpotIntegration:
    """Main HubSpot integration class."""
    
    def __init__(self):
        """Initialize HubSpot client."""
        self.client = HubSpot(access_token=settings.hubspot_api_key)
        self.portal_id = settings.hubspot_portal_id
        
    async def publish_deal(self, deal: Deal) -> Dict[str, Any]:
        """
        Publish a deal to HubSpot.
        
        Creates:
        1. Product for unlock fee
        2. Payment link
        3. Landing page (teaser)
        4. Workflow for delivery
        
        Args:
            deal: Deal object to publish
            
        Returns:
            Dictionary with HubSpot IDs and URLs
        """
        try:
            logger.info(f"Publishing {deal.deal_number} to HubSpot...")
            
            # Step 1: Create product
            product = await self._create_product(deal)
            deal.hubspot_product_id = product["id"]
            
            # Step 2: Create payment link
            payment_link = await self._create_payment_link(deal, product["id"])
            
            # Step 3: Create landing page (if using HubSpot CMS)
            # For now, we'll use external page and just track the URL
            landing_page_url = f"https://fareglitch.com/deals/{deal.deal_number.lower()}"
            deal.hubspot_page_url = landing_page_url
            
            # Step 4: Set up workflow (one-time setup, reusable)
            # Workflows are typically created manually in HubSpot UI
            # But we can trigger them via API
            
            # Update deal status
            deal.status = DealStatus.PUBLISHED
            deal.published_at = datetime.now()
            deal.expires_at = datetime.now() + timedelta(hours=settings.deal_expiry_hours)
            
            logger.info(f"✅ {deal.deal_number} published successfully")
            
            return {
                "product_id": product["id"],
                "payment_link": payment_link,
                "landing_page_url": landing_page_url
            }
            
        except Exception as e:
            logger.error(f"Failed to publish deal: {e}", exc_info=True)
            raise
            
    async def _create_product(self, deal: Deal) -> Dict[str, Any]:
        """
        Create a HubSpot product for the deal unlock.
        
        Args:
            deal: Deal object
            
        Returns:
            Created product data
        """
        product_name = f"{deal.deal_number} Unlock"
        
        properties = {
            "name": product_name,
            "description": deal.teaser_description,
            "price": str(deal.unlock_fee),
            "hs_sku": deal.deal_number,
            "hs_product_type": "Digital Product",
            # Custom properties (need to be created in HubSpot first)
            "deal_origin": deal.origin,
            "deal_destination": deal.destination,
            "deal_savings": str(deal.savings_amount),
            "deal_number": deal.deal_number
        }
        
        try:
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = self.client.crm.products.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
            
            logger.info(f"Created HubSpot product: {api_response.id}")
            return api_response.to_dict()
            
        except ApiException as e:
            logger.error(f"Product creation failed: {e}")
            raise
            
    async def _create_payment_link(self, deal: Deal, product_id: str) -> str:
        """
        Create a HubSpot payment link for the unlock fee.
        
        Note: HubSpot Commerce Hub payment links are typically created via UI.
        This method would use HubSpot's Commerce API if available,
        or you can integrate with Stripe directly.
        
        Args:
            deal: Deal object
            product_id: HubSpot product ID
            
        Returns:
            Payment link URL
        """
        # For HubSpot Commerce Hub, payment links are created through the UI
        # and then retrieved via API, or you can use the Checkout API
        
        # Alternative: Use Stripe directly
        # payment_link = await self._create_stripe_payment_link(deal, product_id)
        
        # For now, return a placeholder that would be created manually
        payment_link = f"https://buy.fareglitch.com/{deal.deal_number.lower()}"
        
        logger.info(f"Payment link: {payment_link}")
        return payment_link
        
    async def create_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        properties: Optional[Dict] = None
    ) -> str:
        """
        Create or update a HubSpot contact.
        
        Args:
            email: Contact email
            first_name: Optional first name
            last_name: Optional last name
            properties: Additional custom properties
            
        Returns:
            HubSpot contact ID
        """
        contact_properties = {
            "email": email
        }
        
        if first_name:
            contact_properties["firstname"] = first_name
        if last_name:
            contact_properties["lastname"] = last_name
            
        if properties:
            contact_properties.update(properties)
            
        try:
            simple_public_object_input = SimplePublicObjectInput(properties=contact_properties)
            api_response = self.client.crm.contacts.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
            
            return api_response.id
            
        except ApiException as e:
            # Contact might already exist
            if "CONTACT_EXISTS" in str(e):
                # Get existing contact
                contact = self.client.crm.contacts.basic_api.get_by_id(email)
                return contact.id
            else:
                logger.error(f"Contact creation failed: {e}")
                raise
                
    async def record_unlock(self, deal: Deal, email: str, payment_id: str) -> DealUnlock:
        """
        Record a deal unlock in both HubSpot and local database.
        
        Args:
            deal: Deal that was unlocked
            email: User email
            payment_id: HubSpot payment/order ID
            
        Returns:
            DealUnlock record
        """
        # Create/update contact in HubSpot
        contact_id = await self.create_contact(
            email=email,
            properties={
                "last_deal_unlocked": deal.deal_number,
                "total_deals_unlocked": "1"  # Would increment in real implementation
            }
        )
        
        # Create unlock record
        unlock = DealUnlock(
            deal_id=deal.id,
            email=email,
            hubspot_contact_id=contact_id,
            unlock_fee_paid=deal.unlock_fee,
            payment_id=payment_id,
            payment_status="succeeded",
            unlocked_at=datetime.now()
        )
        
        # Update deal stats
        deal.total_unlocks += 1
        deal.total_revenue += deal.unlock_fee
        
        logger.info(f"Recorded unlock for {deal.deal_number} by {email}")
        return unlock
        
    async def trigger_delivery_workflow(self, deal: Deal, contact_id: str):
        """
        Trigger the HubSpot workflow to deliver deal details.
        
        The workflow should:
        1. Send email with booking link
        2. Add contact to interest-based list
        3. Set up follow-up sequences
        
        Args:
            deal: Deal to deliver
            contact_id: HubSpot contact ID
        """
        # Workflows are typically triggered by:
        # - Contact property changes
        # - Deal stage changes
        # - Form submissions
        # - API events
        
        # For this implementation, we'll use contact property update
        # to trigger the workflow
        
        try:
            properties = {
                "deal_to_deliver": deal.deal_number,
                "deal_unlock_timestamp": datetime.now().isoformat()
            }
            
            self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input=SimplePublicObjectInput(properties=properties)
            )
            
            logger.info(f"Triggered delivery workflow for {deal.deal_number}")
            
        except Exception as e:
            logger.error(f"Workflow trigger failed: {e}")
            raise
            
    async def process_refund(
        self,
        unlock: DealUnlock,
        reason: str = "Airline canceled fare"
    ) -> bool:
        """
        Process a refund for the Glitch Guarantee.
        
        Args:
            unlock: DealUnlock record to refund
            reason: Reason for refund
            
        Returns:
            True if successful
        """
        try:
            # In real implementation, this would call HubSpot Commerce API
            # or Stripe API to process actual refund
            
            unlock.refund_requested = True
            unlock.refund_reason = reason
            unlock.refunded_at = datetime.now()
            unlock.payment_status = "refunded"
            
            # Update contact with refund info
            if unlock.hubspot_contact_id:
                properties = {
                    "last_refund_date": datetime.now().isoformat(),
                    "last_refund_reason": reason
                }
                
                self.client.crm.contacts.basic_api.update(
                    contact_id=unlock.hubspot_contact_id,
                    simple_public_object_input=SimplePublicObjectInput(properties=properties)
                )
                
            logger.info(f"Processed refund for unlock {unlock.id}")
            return True
            
        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            return False
            
    async def add_to_list(self, contact_id: str, list_id: str):
        """
        Add contact to a static list (e.g., "Interested in Asia").
        
        Args:
            contact_id: HubSpot contact ID
            list_id: HubSpot list ID
        """
        try:
            # Use HubSpot Lists API
            # This is typically done via workflows in HubSpot UI
            pass
        except Exception as e:
            logger.error(f"Failed to add contact to list: {e}")
            
    def get_deal_analytics(self, deal: Deal) -> Dict[str, Any]:
        """
        Get analytics for a deal from HubSpot.
        
        Args:
            deal: Deal to get analytics for
            
        Returns:
            Analytics data
        """
        try:
            # Get product data
            product = self.client.crm.products.basic_api.get_by_id(
                product_id=deal.hubspot_product_id
            )
            
            # In real implementation, would also get:
            # - Page views from CMS
            # - Email open rates
            # - Conversion rates
            
            return {
                "product_id": product.id,
                "total_unlocks": deal.total_unlocks,
                "total_revenue": deal.total_revenue,
                "conversion_rate": 0.0  # Would calculate from page views
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {}


class WorkflowTemplates:
    """
    Templates for HubSpot workflows.
    
    These would be created manually in HubSpot UI, but documented here.
    """
    
    DEAL_DELIVERY_WORKFLOW = {
        "name": "Deal Delivery Workflow",
        "description": "Automatically delivers deal details after payment",
        "trigger": {
            "type": "contact_property_change",
            "property": "deal_unlock_timestamp"
        },
        "actions": [
            {
                "type": "send_email",
                "delay": "0",
                "email_name": "Deal Details Delivery",
                "subject": "CONFIDENTIAL: Your Flight Details Inside",
                "personalization_tokens": [
                    "deal_number",
                    "booking_link",
                    "specific_dates",
                    "booking_instructions"
                ]
            },
            {
                "type": "add_to_list",
                "list_name": "Active Deal Buyers"
            },
            {
                "type": "set_property",
                "property": "lifecycle_stage",
                "value": "customer"
            }
        ]
    }
    
    GLITCH_GUARANTEE_WORKFLOW = {
        "name": "Glitch Guarantee Refund",
        "description": "Processes refund requests for canceled fares",
        "trigger": {
            "type": "ticket_created",
            "pipeline": "Support",
            "stage": "Refund Request"
        },
        "actions": [
            {
                "type": "webhook",
                "url": "https://api.fareglitch.com/webhooks/process-refund",
                "method": "POST"
            },
            {
                "type": "send_email",
                "email_name": "Refund Confirmation",
                "subject": "Your Glitch Guarantee Refund"
            }
        ]
    }
