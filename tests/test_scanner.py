"""
Unit Tests for FareGlitch Scanner

Tests the core functionality of the price anomaly detection system.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock

from src.scanner.amadeus_client import AmadeusScanner, PriceAnomalyDetector
from src.models.database import Deal, PriceHistory, DealStatus
from src.config import settings


class TestAmadeusScanner:
    """Test Amadeus API client."""
    
    @pytest.fixture
    def scanner(self):
        """Create scanner instance."""
        return AmadeusScanner()
        
    @patch('src.scanner.amadeus_client.Client')
    def test_search_cheapest_destinations(self, mock_client_class, scanner):
        """Test searching for cheapest destinations."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.data = [
            {
                "type": "flight-destination",
                "origin": "JFK",
                "destination": "NRT",
                "departureDate": "2025-12-01",
                "returnDate": "2025-12-08",
                "price": {"total": "450", "currency": "USD"}
            }
        ]
        
        # Setup mock client
        mock_client = MagicMock()
        mock_client.shopping.flight_destinations.get.return_value = mock_response
        scanner.client = mock_client
        
        results = scanner.search_inspiration("JFK")
        
        assert len(results) == 1
        assert results[0]["origin"] == "JFK"
        assert results[0]["destination"] == "NRT"
        assert results[0]["price"] == 450.0


class TestPriceAnomalyDetector:
    """Test price anomaly detection logic."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()
        
    @pytest.fixture
    def detector(self, mock_db):
        """Create detector instance."""
        return PriceAnomalyDetector(mock_db)
        
    @pytest.mark.asyncio
    async def test_detect_anomaly_with_savings(self, detector, mock_db):
        """Test detecting a valid price anomaly."""
        # Mock historical price
        mock_db.query.return_value.filter.return_value.scalar.return_value = 2000.0
        
        dest_data = {
            "origin": "JFK",
            "destination": "NRT",
            "price": 450.0,
            "currency": "USD",
            "departure_date": "2025-12-01",
            "return_date": "2025-12-08"
        }
        
        anomaly = await detector._check_for_anomaly(
            dest_data,
            min_savings=300,
            threshold=0.70
        )
        
        assert anomaly is not None
        assert anomaly["savings_amount"] == 1550.0
        assert anomaly["savings_percentage"] >= 0.70
        
    @pytest.mark.asyncio
    async def test_no_anomaly_small_savings(self, detector, mock_db):
        """Test that small savings don't trigger anomaly."""
        # Mock historical price
        mock_db.query.return_value.filter.return_value.scalar.return_value = 500.0
        
        dest_data = {
            "origin": "JFK",
            "destination": "NRT",
            "price": 450.0,
            "currency": "USD"
        }
        
        anomaly = await detector._check_for_anomaly(
            dest_data,
            min_savings=300,  # Requires $300 savings
            threshold=0.70
        )
        
        # Only $50 savings, should not trigger
        assert anomaly is None


class TestDealCreation:
    """Test deal record creation."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.query.return_value.order_by.return_value.first.return_value = None
        return db
        
    @pytest.mark.asyncio
    async def test_create_deal_from_anomaly(self, mock_db):
        """Test creating a Deal from anomaly data."""
        from src.scanner.main import FareGlitchScanner
        
        scanner = FareGlitchScanner(mock_db)
        
        anomaly_data = {
            "origin": "JFK",
            "destination": "NRT",
            "route": "JFK to NRT",
            "current_price": 450.0,
            "historical_avg": 2000.0,
            "savings_amount": 1550.0,
            "savings_percentage": 0.775,
            "currency": "USD"
        }
        
        deal = await scanner._create_deal(anomaly_data)
        
        assert deal.deal_number == "DEAL#001"
        assert deal.origin == "JFK"
        assert deal.destination == "NRT"
        assert deal.mistake_price == 450.0
        assert deal.normal_price == 2000.0
        assert deal.status == DealStatus.VALIDATED


@pytest.fixture
def sample_deal():
    """Create a sample deal for testing."""
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
        status=DealStatus.VALIDATED,
        unlock_fee=7.0,
        teaser_headline="Mistake Fare: JFK to NRT (77% Off)",
        teaser_description="Normally $2000, now $450"
    )
