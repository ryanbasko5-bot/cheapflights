"""
API Integration Tests

Tests FastAPI endpoints and webhook handlers.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.api.main import app
from src.models.database import Deal, DealUnlock, DealStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return Mock()


class TestDealEndpoints:
    """Test deal API endpoints."""
    
    def test_get_active_deals(self, client):
        """Test retrieving active deals."""
        with patch('src.api.main.get_db_session') as mock_get_db:
            # Mock database response
            mock_db = Mock()
            mock_deals = [
                Deal(
                    deal_number="DEAL#001",
                    route_description="JFK to NRT",
                    teaser_headline="Mistake Fare: JFK to NRT",
                    teaser_description="Save 77%",
                    normal_price=2000.0,
                    mistake_price=450.0,
                    savings_amount=1550.0,
                    savings_percentage=0.775,
                    currency="USD",
                    unlock_fee=7.0,
                    status=DealStatus.PUBLISHED,
                    is_active=True,
                    expires_at=datetime.now() + timedelta(hours=24)
                )
            ]
            
            mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_deals
            mock_get_db.return_value = iter([mock_db])
            
            response = client.get("/deals/active")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["deal_number"] == "DEAL#001"
            
    def test_get_deal_teaser(self, client):
        """Test retrieving a specific deal teaser."""
        with patch('src.api.main.get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_deal = Deal(
                deal_number="DEAL#001",
                route_description="JFK to NRT",
                teaser_headline="Mistake Fare",
                teaser_description="Save 77%",
                normal_price=2000.0,
                mistake_price=450.0,
                savings_amount=1550.0,
                savings_percentage=0.775,
                currency="USD",
                unlock_fee=7.0,
                status=DealStatus.PUBLISHED,
                is_active=True
            )
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_deal
            mock_get_db.return_value = iter([mock_db])
            
            response = client.get("/deals/DEAL#001")
            
            assert response.status_code == 200
            data = response.json()
            assert data["deal_number"] == "DEAL#001"
            
    def test_deal_not_found(self, client):
        """Test 404 for non-existent deal."""
        with patch('src.api.main.get_db_session') as mock_get_db:
            mock_db = Mock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_get_db.return_value = iter([mock_db])
            
            response = client.get("/deals/DEAL#999")
            
            assert response.status_code == 404


class TestUnlockEndpoint:
    """Test deal unlock functionality."""
    
    @pytest.mark.asyncio
    async def test_unlock_deal_success(self, client):
        """Test successful deal unlock."""
        with patch('src.api.main.get_db_session') as mock_get_db, \
             patch('src.api.main.HubSpotIntegration') as mock_hubspot:
            
            mock_db = Mock()
            mock_deal = Deal(
                id=1,
                deal_number="DEAL#001",
                status=DealStatus.PUBLISHED,
                is_active=True,
                unlock_fee=7.0
            )
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_deal
            mock_get_db.return_value = iter([mock_db])
            
            # Mock HubSpot integration
            mock_hs = Mock()
            mock_unlock = DealUnlock(
                deal_id=1,
                email="user@example.com",
                hubspot_contact_id="contact_123"
            )
            mock_hs.record_unlock.return_value = mock_unlock
            mock_hubspot.return_value = mock_hs
            
            response = client.post(
                "/deals/DEAL#001/unlock",
                json={
                    "email": "user@example.com",
                    "payment_id": "payment_456"
                }
            )
            
            assert response.status_code == 200


class TestRefundEndpoint:
    """Test refund request functionality."""
    
    @pytest.mark.asyncio
    async def test_request_refund_success(self, client):
        """Test successful refund request."""
        with patch('src.api.main.get_db_session') as mock_get_db, \
             patch('src.api.main.HubSpotIntegration') as mock_hubspot:
            
            mock_db = Mock()
            mock_deal = Deal(id=1, deal_number="DEAL#001")
            mock_unlock = DealUnlock(
                id=1,
                deal_id=1,
                email="user@example.com",
                payment_status="succeeded",
                unlocked_at=datetime.now() - timedelta(hours=1)
            )
            
            mock_db.query.return_value.filter.return_value.first.side_effect = [mock_deal, mock_unlock]
            mock_get_db.return_value = iter([mock_db])
            
            # Mock HubSpot refund
            mock_hs = Mock()
            mock_hs.process_refund.return_value = True
            mock_hubspot.return_value = mock_hs
            
            response = client.post(
                "/refunds/request",
                json={
                    "email": "user@example.com",
                    "deal_number": "DEAL#001",
                    "reason": "Airline canceled"
                }
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "success"


class TestWebhooks:
    """Test webhook endpoints."""
    
    def test_hubspot_payment_webhook(self, client):
        """Test HubSpot payment webhook."""
        with patch('src.api.main.unlock_deal') as mock_unlock:
            mock_unlock.return_value = Deal(deal_number="DEAL#001")
            
            response = client.post(
                "/webhooks/hubspot/payment-success",
                json={
                    "deal_number": "DEAL#001",
                    "email": "user@example.com",
                    "payment_id": "payment_456"
                }
            )
            
            assert response.status_code == 200
