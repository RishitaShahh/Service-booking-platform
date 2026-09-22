"""Security utilities for password hashing and JWT token creation/verification."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed password string.

    Args:
        plain_password (str): Plain-text password provided during authentication.
        hashed_password (str): Stored bcrypt password hash.

    Returns:
        bool: True if password matches hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a bcrypt password hash from a plain-text password.

    Args:
        password (str): Plain-text password to hash.

    Returns:
        str: Hashed password string.
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    role: str,
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT access token containing subject, user ID, role, and expiration.

    Args:
        subject (str): User identifier (usually user email).
        role (str): Role assigned to the user ('customer' or 'provider').
        user_id (int): Database ID of the user.
        expires_delta (Optional[timedelta]): Custom token expiration duration.

    Returns:
        str: Encoded JWT token string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": subject,
        "role": role,
        "user_id": user_id,
        "exp": expire
    }
    encoded_jwt: str = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token string.

    Args:
        token (str): JWT token string.

    Returns:
        Optional[Dict[str, Any]]: Decoded payload claims if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
