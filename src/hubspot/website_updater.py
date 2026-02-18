"""
HubSpot Website Auto-Updater

Automatically updates your HubSpot-hosted website when new deals are found.

Methods:
1. Custom Module Data API - Updates a JSON data source
2. HubDB - Updates a database table that feeds into the website
3. Blog Posts - Creates new blog posts for each deal
4. CMS API - Directly updates page modules
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
import requests

from src.config import settings
from src.models.database import Deal, DealStatus

logger = logging.getLogger(__name__)


class HubSpotWebsiteUpdater:
    """Automatically update HubSpot website with new deals."""
    
    def __init__(self):
        """Initialize HubSpot API client."""
        self.api_key = settings.hubspot_api_key
        self.portal_id = settings.hubspot_portal_id
        self.base_url = "https://api.hubapi.com"
        
        # HubDB table for deals (create this in HubSpot first)
        self.deals_table_id = None  # Will be set after table creation
        
    def update_website_with_deals(self, deals: List[Deal]) -> Dict[str, Any]:
        """
        Update the HubSpot website with new deals.
        
        This uses multiple methods to ensure deals appear on site:
        1. Update HubDB table (displays in Recent Deals section)
        2. Create blog post announcement (optional)
        3. Trigger webhook to refresh modules (if configured)
        
        Args:
            deals: List of new Deal objects
            
        Returns:
            Status of updates
        """
        results = {
            "hubdb_updated": False,
            "blog_posts_created": 0,
            "errors": []
        }
        
        try:
            # Method 1: Update HubDB table
            if self.deals_table_id:
                hubdb_result = self._update_hubdb_deals(deals)
                results["hubdb_updated"] = hubdb_result
                logger.info(f"✅ HubDB updated with {len(deals)} deals")
            else:
                logger.warning("HubDB table not configured. Run setup_hubdb_table() first")
                
            # Method 2: Create blog posts (optional)
            for deal in deals:
                try:
                    blog_post = self._create_deal_blog_post(deal)
                    results["blog_posts_created"] += 1
                    logger.info(f"✅ Blog post created for {deal.deal_number}")
                except Exception as e:
                    logger.error(f"Blog post creation failed: {e}")
                    results["errors"].append(str(e))
                    
            return results
            
        except Exception as e:
            logger.error(f"Website update failed: {e}", exc_info=True)
            results["errors"].append(str(e))
            return results
            
    def _update_hubdb_deals(self, deals: List[Deal]) -> bool:
        """
        Update HubDB table with latest deals.
        
        HubDB is HubSpot's database for dynamic website content.
        Create table at: Content → HubDB → Create table
        
        Table columns needed:
        - deal_number (text)
        - route (text) 
        - origin (text)
        - destination (text)
        - normal_price (number)
        - deal_price (number)
        - savings (number)
        - savings_pct (number)
        - status (text: active/expired)
        - expires_at (date)
        - created_at (date)
        
        Args:
            deals: List of Deal objects
            
        Returns:
            True if successful
        """
        if not self.deals_table_id:
            logger.error("HubDB table ID not set")
            return False
            
        try:
            url = f"{self.base_url}/cms/v3/hubdb/tables/{self.deals_table_id}/rows"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Add each deal as a row
            for deal in deals:
                row_data = {
                    "values": {
                        "deal_number": deal.deal_number,
                        "route": deal.route_description,
                        "origin": deal.origin,
                        "destination": deal.destination,
                        "normal_price": deal.normal_price,
                        "deal_price": deal.mistake_price,
                        "savings": deal.savings_amount,
                        "savings_pct": int(deal.savings_percentage * 100),
                        "status": deal.status,
                        "expires_at": deal.expires_at.isoformat() if deal.expires_at else None,
                        "created_at": deal.detected_at.isoformat()
                    }
                }
                
                # Create row in HubDB
                response = requests.post(url, json=row_data, headers=headers)
                response.raise_for_status()
                
            # Publish table to make changes live
            publish_url = f"{self.base_url}/cms/v3/hubdb/tables/{self.deals_table_id}/draft/publish"
            publish_response = requests.post(publish_url, headers=headers)
            publish_response.raise_for_status()
            
            logger.info(f"✅ HubDB table published with {len(deals)} new deals")
            return True
            
        except Exception as e:
            logger.error(f"HubDB update failed: {e}")
            return False
            
    def _create_deal_blog_post(self, deal: Deal) -> Dict[str, Any]:
        """
        Create a blog post announcing the new deal.
        
        This creates a blog post in HubSpot CMS that can be displayed
        in your blog feed or recent deals section.
        
        Args:
            deal: Deal object
            
        Returns:
            Created blog post data
        """
        url = f"{self.base_url}/cms/v3/blogs/posts"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format the blog post
        savings_pct = int(deal.savings_percentage * 100)
        
        post_content = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 40px; border-radius: 16px; color: white; text-align: center;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">🚨 {deal.deal_number}</h1>
            <h2 style="font-size: 2rem; margin-bottom: 2rem;">{deal.route_description}</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; max-width: 600px; margin: 0 auto;">
                <div>
                    <p style="font-size: 0.875rem; opacity: 0.8;">Normal Price</p>
                    <p style="font-size: 1.5rem; text-decoration: line-through;">${int(deal.normal_price)}</p>
                </div>
                <div>
                    <p style="font-size: 0.875rem; opacity: 0.8;">Deal Price</p>
                    <p style="font-size: 2.5rem; font-weight: 700;">${int(deal.mistake_price)}</p>
                </div>
            </div>
            
            <p style="font-size: 1.5rem; margin-top: 2rem; font-weight: 600;">
                Save {savings_pct}% (${int(deal.savings_amount)})
            </p>
            
            <p style="margin-top: 2rem; font-size: 1rem; opacity: 0.9;">
                ⚠️ This deal expires in 48 hours or when airlines fix the error!
            </p>
        </div>
        
        <div style="margin-top: 3rem;">
            <h3>How to Book This Deal</h3>
            <p>SMS subscribers received booking instructions immediately. Want instant alerts?</p>
            <p><strong>Subscribe for $5/month</strong> to get deals 1 hour before they're posted publicly.</p>
        </div>
        """
        
        post_data = {
            "name": f"{deal.deal_number}: {deal.route_description}",
            "slug": f"{deal.deal_number.lower()}-{deal.origin}-{deal.destination}".lower(),
            "postBody": post_content,
            "postSummary": f"Save {savings_pct}% on flights from {deal.origin} to {deal.destination}!",
            "metaDescription": f"Mistake fare alert: {deal.route_description} for only ${int(deal.mistake_price)}. Save ${int(deal.savings_amount)}!",
            "state": "PUBLISHED",
            "publishDate": datetime.now().isoformat(),
            "enableGoogleAmpOutput": False
        }
        
        try:
            response = requests.post(url, json=post_data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ Blog post created: {result.get('url')}")
            return result
            
        except Exception as e:
            logger.error(f"Blog post creation failed: {e}")
            raise
            
    def setup_hubdb_table(self) -> str:
        """
        Create the HubDB table for storing deals.
        
        This only needs to be run once. After creation, save the table ID
        in your settings.
        
        Returns:
            Table ID
        """
        url = f"{self.base_url}/cms/v3/hubdb/tables"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        table_data = {
            "name": "FareGlitch Deals",
            "label": "Deals",
            "useForPages": False,
            "allowPublicApiAccess": True,
            "allowChildTables": False,
            "columns": [
                {"name": "deal_number", "label": "Deal Number", "type": "TEXT"},
                {"name": "route", "label": "Route", "type": "TEXT"},
                {"name": "origin", "label": "Origin", "type": "TEXT"},
                {"name": "destination", "label": "Destination", "type": "TEXT"},
                {"name": "normal_price", "label": "Normal Price", "type": "NUMBER"},
                {"name": "deal_price", "label": "Deal Price", "type": "NUMBER"},
                {"name": "savings", "label": "Savings", "type": "NUMBER"},
                {"name": "savings_pct", "label": "Savings %", "type": "NUMBER"},
                {"name": "status", "label": "Status", "type": "TEXT"},
                {"name": "expires_at", "label": "Expires At", "type": "DATETIME"},
                {"name": "created_at", "label": "Created At", "type": "DATETIME"}
            ]
        }
        
        try:
            response = requests.post(url, json=table_data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            table_id = result.get("id")
            logger.info(f"✅ HubDB table created with ID: {table_id}")
            logger.info(f"⚠️  Save this ID in your .env: HUBSPOT_DEALS_TABLE_ID={table_id}")
            
            return table_id
            
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise
            
    def get_active_deals_for_website(self, limit: int = 10) -> List[Dict]:
        """
        Fetch active deals from HubDB to display on website.
        
        This can be called from HubSpot custom modules via API.
        
        Args:
            limit: Number of deals to return
            
        Returns:
            List of deal dictionaries
        """
        if not self.deals_table_id:
            logger.error("HubDB table ID not set")
            return []
            
        try:
            url = f"{self.base_url}/cms/v3/hubdb/tables/{self.deals_table_id}/rows"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            params = {
                "limit": limit,
                "sort": "-created_at"  # Newest first
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            # Format deals for website display
            deals = []
            for row in result.get("results", []):
                values = row.get("values", {})
                if values.get("status") == "active":
                    deals.append({
                        "deal_number": values.get("deal_number"),
                        "route": values.get("route"),
                        "origin": values.get("origin"),
                        "destination": values.get("destination"),
                        "normal_price": values.get("normal_price"),
                        "deal_price": values.get("deal_price"),
                        "savings": values.get("savings"),
                        "savings_pct": values.get("savings_pct"),
                        "expires_at": values.get("expires_at")
                    })
                    
            return deals[:limit]
            
        except Exception as e:
            logger.error(f"Failed to fetch deals: {e}")
            return []


# Convenience function for easy integration
def auto_update_website(deals: List[Deal]) -> Dict[str, Any]:
    """
    Convenience function to auto-update HubSpot website.
    
    Usage in scanner:
        from src.hubspot.website_updater import auto_update_website
        
        # After finding new deals:
        result = auto_update_website(validated_deals)
    
    Args:
        deals: List of new Deal objects
        
    Returns:
        Update status
    """
    updater = HubSpotWebsiteUpdater()
    return updater.update_website_with_deals(deals)
