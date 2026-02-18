"""
Unit Tests for HubSpot Integration

Tests HubSpot API interactions and workflow triggers.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
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
    async def test_create_product(self, hubspot, sample_deal):
        """Test creating a HubSpot product."""
        pytest.skip("HubSpot API integration test - requires live API or complex mocking")
        
    @pytest.mark.asyncio
    async def test_record_unlock(self, hubspot, sample_deal):
        """Test recording a deal unlock."""
        pytest.skip("HubSpot API integration test - requires live API or complex mocking")
        
    @pytest.mark.asyncio
    async def test_process_refund(self, hubspot):
        """Test processing a refund."""
        pytest.skip("HubSpot API integration test - requires live API")


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
