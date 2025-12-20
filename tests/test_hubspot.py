"""
Unit Tests for HubSpot Integration

Tests HubSpot API interactions and workflow triggers.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.hubspot.integration import HubSpotIntegration
from src.models.database import Deal, DealUnlock, DealStatus


class TestHubSpotIntegration:
    """Test HubSpot integration functionality."""
    
    @pytest.fixture
    def hubspot(self):
        """Create HubSpot integration instance."""
        return HubSpotIntegration()
        
    @pytest.fixture
    def sample_deal(self):
        """Create sample deal."""
        return Deal(
            id=1,
            deal_number="DEAL#001",
            origin="JFK",
            destination="NRT",
            route_description="JFK to NRT",
            normal_price=2000.0,
            mistake_price=450.0,
            savings_amount=1550.0,
            savings_percentage=0.775,
            currency="USD",
            unlock_fee=7.0,
            status=DealStatus.VALIDATED,
            teaser_headline="Mistake Fare: JFK to NRT",
            teaser_description="Save 77%"
        )
        
    @pytest.mark.asyncio
    @patch('src.hubspot.integration.HubSpot')
    async def test_create_product(self, mock_hubspot_client, hubspot, sample_deal):
        """Test creating a HubSpot product."""
        # Mock API response
        mock_product = Mock()
        mock_product.id = "123456"
        mock_product.to_dict.return_value = {"id": "123456", "name": "DEAL#001 Unlock"}
        
        hubspot.client.crm.products.basic_api.create.return_value = mock_product
        
        product = await hubspot._create_product(sample_deal)
        
        assert product["id"] == "123456"
        assert "DEAL#001" in product["name"]
        
    @pytest.mark.asyncio
    @patch('src.hubspot.integration.HubSpot')
    async def test_record_unlock(self, mock_hubspot_client, hubspot, sample_deal):
        """Test recording a deal unlock."""
        # Mock contact creation
        mock_contact = Mock()
        mock_contact.id = "contact_123"
        hubspot.client.crm.contacts.basic_api.create.return_value = mock_contact
        
        unlock = await hubspot.record_unlock(
            deal=sample_deal,
            email="user@example.com",
            payment_id="payment_456"
        )
        
        assert unlock.email == "user@example.com"
        assert unlock.payment_id == "payment_456"
        assert unlock.unlock_fee_paid == 7.0
        assert unlock.hubspot_contact_id == "contact_123"
        
    @pytest.mark.asyncio
    @patch('src.hubspot.integration.HubSpot')
    async def test_process_refund(self, mock_hubspot_client, hubspot):
        """Test processing a refund."""
        unlock = DealUnlock(
            id=1,
            deal_id=1,
            email="user@example.com",
            hubspot_contact_id="contact_123",
            unlock_fee_paid=7.0,
            payment_status="succeeded"
        )
        
        success = await hubspot.process_refund(unlock, "Airline canceled")
        
        assert success is True
        assert unlock.payment_status == "refunded"
        assert unlock.refund_reason == "Airline canceled"
        assert unlock.refunded_at is not None


class TestWorkflowTriggers:
    """Test HubSpot workflow triggering."""
    
    @pytest.mark.asyncio
    @patch('src.hubspot.integration.HubSpot')
    async def test_trigger_delivery_workflow(self, mock_hubspot_client):
        """Test triggering deal delivery workflow."""
        hubspot = HubSpotIntegration()
        
        deal = Deal(
            id=1,
            deal_number="DEAL#001",
            origin="JFK",
            destination="NRT"
        )
        
        await hubspot.trigger_delivery_workflow(deal, "contact_123")
        
        # Verify contact update was called
        hubspot.client.crm.contacts.basic_api.update.assert_called_once()
