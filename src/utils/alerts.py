"""
Alert Management System

Sends notifications via Slack, Email, and SMS when deals are found.
"""
import logging
from typing import Optional, Dict, Any
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx

from src.config import settings
from src.models.database import Deal

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages all alert notifications for detected deals."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.slack_webhook = settings.slack_webhook_url
        self.email_configured = all([
            settings.smtp_user,
            settings.smtp_password,
            settings.alert_email_to
        ])
        
    async def send_deal_alert(self, deal: Deal) -> bool:
        """
        Send alert about a new validated deal.
        
        Args:
            deal: Deal object to alert about
            
        Returns:
            True if any alert was sent successfully
        """
        success = False
        
        # Try Slack first
        if self.slack_webhook:
            try:
                await self._send_slack_alert(deal)
                success = True
            except Exception as e:
                logger.error(f"Slack alert failed: {e}")
                
        # Send email backup
        if self.email_configured:
            try:
                self._send_email_alert(deal)
                success = True
            except Exception as e:
                logger.error(f"Email alert failed: {e}")
                
        if not success:
            logger.warning("No alerts configured or all failed!")
            
        return success
        
    async def _send_slack_alert(self, deal: Deal):
        """Send Slack notification."""
        # Build rich Slack message
        message = {
            "text": f"🚨 NEW MISTAKE FARE DETECTED: {deal.deal_number}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🎯 {deal.teaser_headline}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Route:*\n{deal.route_description}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Deal Number:*\n{deal.deal_number}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Normal Price:*\n${deal.normal_price:.0f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Mistake Price:*\n${deal.mistake_price:.0f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Savings:*\n${deal.savings_amount:.0f} ({deal.savings_percentage*100:.0f}% off)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:*\n{deal.status}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Cabin Class:* {deal.cabin_class or 'Unknown'}\n*Airline:* {deal.airline or 'Unknown'}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Approve & Publish"
                            },
                            "style": "primary",
                            "value": f"approve_{deal.id}"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "❌ Reject"
                            },
                            "style": "danger",
                            "value": f"reject_{deal.id}"
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.slack_webhook,
                json=message,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Slack API error: {response.status_code}")
                
        logger.info(f"Slack alert sent for {deal.deal_number}")
        
    def _send_email_alert(self, deal: Deal):
        """Send email notification."""
        subject = f"🚨 New Mistake Fare: {deal.route_description} ({deal.savings_percentage*100:.0f}% off)"
        
        # HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #FF4444; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .deal-box {{ border: 2px solid #FF4444; padding: 15px; margin: 10px 0; }}
                .price {{ font-size: 24px; font-weight: bold; color: #FF4444; }}
                .savings {{ font-size: 18px; color: #00AA00; }}
                .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Mistake Fare Detected</h1>
                <h2>{deal.deal_number}</h2>
            </div>
            <div class="content">
                <div class="deal-box">
                    <h2>{deal.teaser_headline}</h2>
                    <p><strong>Route:</strong> {deal.route_description}</p>
                    <p><strong>Origin:</strong> {deal.origin} → <strong>Destination:</strong> {deal.destination}</p>
                    <p class="price">Mistake Price: ${deal.mistake_price:.0f}</p>
                    <p>Normal Price: <strike>${deal.normal_price:.0f}</strike></p>
                    <p class="savings">💰 Save ${deal.savings_amount:.0f} ({deal.savings_percentage*100:.0f}% off)</p>
                    
                    <p><strong>Cabin Class:</strong> {deal.cabin_class or 'Unknown'}</p>
                    <p><strong>Airline:</strong> {deal.airline or 'Unknown'}</p>
                    <p><strong>Status:</strong> {deal.status}</p>
                    
                    <p><strong>Detected:</strong> {deal.detected_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h3>Next Steps:</h3>
                <ol>
                    <li>Review the deal details above</li>
                    <li>Check HubSpot for additional validation</li>
                    <li>Approve and publish if legitimate</li>
                    <li>Monitor for airline cancellations</li>
                </ol>
                
                <p><em>This is an automated alert from FareGlitch Scanner.</em></p>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.smtp_user
        msg['To'] = settings.alert_email_to
        
        # Attach HTML
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send via SMTP
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email alert sent for {deal.deal_number}")
            
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            raise
            
    async def send_publish_confirmation(self, deal: Deal, hubspot_url: str):
        """Send confirmation that deal was published to HubSpot."""
        if not self.slack_webhook:
            return
            
        message = {
            "text": f"✅ Deal Published: {deal.deal_number}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Deal {deal.deal_number} is now live!*\n{deal.teaser_headline}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{hubspot_url}|View in HubSpot>"
                    }
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(self.slack_webhook, json=message)
            
    async def send_error_alert(self, error_msg: str, details: Optional[Dict[str, Any]] = None):
        """Send alert about system errors."""
        if not self.slack_webhook:
            logger.error(f"ERROR ALERT (no Slack): {error_msg}")
            return
            
        message = {
            "text": f"❌ FareGlitch Error: {error_msg}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ System Error"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:* {error_msg}"
                    }
                }
            ]
        }
        
        if details:
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{json.dumps(details, indent=2)}```"
                }
            })
            
        async with httpx.AsyncClient() as client:
            await client.post(self.slack_webhook, json=message)
