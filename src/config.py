"""
FareGlitch Configuration Management

Loads environment variables and provides centralized config access.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Amadeus API
    amadeus_api_key: str
    amadeus_api_secret: str
    amadeus_env: str = "test"  # test or production
    
    # Duffel API
    duffel_api_token: Optional[str] = None
    
    # Kiwi API (Alternative)
    kiwi_api_key: Optional[str] = None
    
    # HubSpot
    hubspot_api_key: str
    hubspot_portal_id: str
    
    # Slack Notifications
    slack_webhook_url: Optional[str] = None
    slack_channel: str = "#fareglitch-alerts"
    
    # Email Notifications
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    alert_email_to: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./fareglitch.db"
    database_pool_size: int = 10
    
    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str
    
    # Scanner Configuration
    scan_interval_seconds: int = 3600  # 1 hour
    price_drop_threshold: float = 0.70  # 70% drop
    min_savings_amount: int = 300  # Minimum $300 savings
    
    # Deal Configuration (Alert Model)
    alert_fee: float = 5.00  # Pay to receive SMS alert
    instagram_delay_hours: int = 1  # Post to Instagram 1hr after SMS
    deal_expiry_hours: int = 48
    
    # SMS Configuration (Sinch)
    sinch_service_plan_id: Optional[str] = None
    sinch_api_token: Optional[str] = None
    sinch_phone_number: Optional[str] = None
    
    # Feature Flags
    enable_auto_publish: bool = False
    enable_sms_alerts: bool = True
    enable_instagram_posting: bool = True
    debug_mode: bool = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.amadeus_env == "production"


# Global settings instance
settings = Settings()


# Export for easy imports
__all__ = ["settings", "Settings"]
