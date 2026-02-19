"""
JWT token validation utility functions for Better Auth integration.
Provides reusable functions for validating JWT tokens issued by Better Auth.
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the auth config
from config.auth_config import auth_config


class TokenData(BaseModel):
    """Model representing decoded token data."""
    user_id: str
    exp: Optional[int] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token compatible with Better Auth standards.

    Args:
        data: Dictionary containing token payload data
        expires_delta: Optional timedelta for custom expiration

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=auth_config.JWT_EXPIRATION_DELTA)

    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, auth_config.BETTER_AUTH_SECRET, algorithm=auth_config.JWT_ALGORITHM)
    return encoded_jwt


def verify_better_auth_token(token: str) -> Optional[TokenData]:
    """
    Verify a Better Auth JWT token and return the token data if valid.

    Args:
        token: JWT token string to verify

    Returns:
        TokenData object if valid, None if invalid
    """
    # First check if the token has a valid JWT format
    if not is_valid_jwt_format(token):
        return None

    try:
        payload = jwt.decode(token, auth_config.BETTER_AUTH_SECRET, algorithms=[auth_config.JWT_ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        # Check if token is expired
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            if datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
                return None

        token_data = TokenData(user_id=user_id, exp=exp_timestamp)
        return token_data
    except JWTError:
        return None


def is_valid_jwt_format(token: str) -> bool:
    """
    Check if a token has a valid JWT format (header.payload.signature).

    Args:
        token: JWT token string to validate

    Returns:
        True if format is valid, False otherwise
    """
    if not token or not isinstance(token, str):
        return False

    # JWT has 3 parts separated by dots: header.payload.signature
    parts = token.split('.')
    if len(parts) != 3:
        return False

    # Each part should be non-empty
    for part in parts:
        if not part:
            return False

    # Basic check: each part should be base64url-safe
    import re
    base64_pattern = re.compile(r'^[A-Za-z0-9_-]*$')
    for part in parts:
        if not base64_pattern.match(part):
            return False

    return True


def decode_token_payload(token: str) -> Optional[dict]:
    """
    Decode JWT token payload without verifying signature (use carefully).

    Args:
        token: JWT token string to decode

    Returns:
        Decoded payload dictionary if valid format, None otherwise
    """
    # First check if the token has a valid JWT format
    if not is_valid_jwt_format(token):
        return None

    try:
        # Decode without verification to inspect payload
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError:
        return None


def is_token_expired(token_data: TokenData) -> bool:
    """
    Check if a token is expired based on its expiration timestamp.

    Args:
        token_data: TokenData object to check

    Returns:
        True if token is expired, False otherwise
    """
    if token_data.exp is None:
        return False

    return datetime.fromtimestamp(token_data.exp) < datetime.utcnow()


def validate_user_id_in_token(token: str, expected_user_id: str) -> bool:
    """
    Validate that the user ID in the token matches the expected user ID.

    Args:
        token: JWT token string to validate
        expected_user_id: Expected user ID to match

    Returns:
        True if user IDs match, False otherwise
    """
    token_data = verify_better_auth_token(token)
    if token_data is None:
        return False

    try:
        # Convert both to UUID objects to ensure they're properly formatted
        token_user_id = uuid.UUID(token_data.user_id)
        expected_uuid = uuid.UUID(expected_user_id)
        return token_user_id == expected_uuid
    except ValueError:
        # If either ID is not a valid UUID, return False
        return False