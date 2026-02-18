"""
Authentication and Authorization for FareGlitch API

Handles member authentication and subscription verification.
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings
from src.models.database import Subscriber, SubscriptionType
from src.utils.database import get_db_session

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.api_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def generate_magic_link_token(email: str) -> str:
    """Generate a magic link token for passwordless login."""
    data = f"{email}:{datetime.utcnow().isoformat()}:{secrets.token_urlsafe(16)}"
    return hashlib.sha256(data.encode()).hexdigest()


async def get_current_subscriber(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> Subscriber:
    """Get current authenticated subscriber from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    subscriber = db.query(Subscriber).filter(
        Subscriber.phone_number == phone_number
    ).first()
    
    if subscriber is None:
        raise credentials_exception
    
    return subscriber


async def get_optional_subscriber(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db_session)
) -> Optional[Subscriber]:
    """Get subscriber if authenticated, otherwise return None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            return None
        
        subscriber = db.query(Subscriber).filter(
            Subscriber.phone_number == phone_number
        ).first()
        
        return subscriber
    except JWTError:
        return None


def is_premium_member(subscriber: Optional[Subscriber]) -> bool:
    """Check if subscriber has active premium membership."""
    if not subscriber:
        return False
    
    if not subscriber.is_active:
        return False
    
    # Check if subscription is active
    if subscriber.subscription_type != SubscriptionType.SMS_MONTHLY:
        return False
    
    # Check if subscription hasn't expired
    if subscriber.subscription_expires_at and subscriber.subscription_expires_at < datetime.now():
        return False
    
    return True


def can_see_deal(deal, subscriber: Optional[Subscriber]) -> bool:
    """
    Determine if a user can see a deal based on membership status.
    
    Rules:
    - Premium members ($5/month): See deals immediately
    - Non-members: See deals after 1 hour delay
    """
    # If premium member, they can see all published deals immediately
    if is_premium_member(subscriber):
        return True
    
    # For non-members, check if deal was published more than 1 hour ago
    if deal.published_at is None:
        return False
    
    hours_since_published = (datetime.now() - deal.published_at).total_seconds() / 3600
    
    # Non-members can only see deals after 1 hour
    return hours_since_published >= 1.0
