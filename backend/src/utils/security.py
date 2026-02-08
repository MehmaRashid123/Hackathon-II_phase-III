"""
Security utilities for password hashing and JWT token management.

This module provides cryptographic functions for secure password storage
and authentication token generation/verification.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import uuid
import hashlib

from src.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: Plain-text password to hash

    Returns:
        str: Bcrypt-hashed password (60 characters)

    Example:
        >>> hashed = hash_password("mySecurePassword123")
        >>> len(hashed)
        60
    """
    try:
        # Always handle bcrypt's 72 byte limit
        password_bytes = password.encode('utf-8')
        
        if len(password_bytes) > 72:
            # Use SHA256 for very long passwords
            password = hashlib.sha256(password_bytes).hexdigest()
        else:
            # Safely truncate to 72 bytes
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        return pwd_context.hash(password)
    except Exception as e:
        # Log error and re-raise with clear message
        print(f"❌ Password hashing error: {str(e)}")
        raise ValueError(f"Failed to hash password: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Args:
        plain_password: Plain-text password to verify
        hashed_password: Bcrypt hash to compare against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("myPassword123")
        >>> verify_password("myPassword123", hashed)
        True
        >>> verify_password("wrongPassword", hashed)
        False
    """
    try:
        # Always handle bcrypt's 72 byte limit
        password_bytes = plain_password.encode('utf-8')
        
        if len(password_bytes) > 72:
            # Use SHA256 for very long passwords
            plain_password = hashlib.sha256(password_bytes).hexdigest()
        else:
            # Safely truncate to 72 bytes
            plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
        
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Log error and return False (invalid password)
        print(f"❌ Password verification error: {str(e)}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token (e.g., {"sub": user_id})
        expires_delta: Token expiration time (defaults to 24 hours)

    Returns:
        str: Encoded JWT token

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> len(token) > 100
        True
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode.update({"exp": expire})

    # Encode JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        dict: Decoded token payload if valid, None otherwise

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> payload = verify_token(token)
        >>> payload["sub"]
        'user@example.com'
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
