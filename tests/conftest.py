"""
Pytest Configuration

Global fixtures and configuration for tests.
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base
from src.config import settings


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["AMADEUS_API_KEY"] = "test_key"
    os.environ["AMADEUS_API_SECRET"] = "test_secret"
    os.environ["HUBSPOT_API_KEY"] = "test_hubspot_key"
    os.environ["HUBSPOT_PORTAL_ID"] = "test_portal"
    os.environ["API_SECRET_KEY"] = "test_secret_key"
