"""
Authentication-related models for Better Auth integration.
Contains models for authentication requests, responses, and validation.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class AuthTokenRequest(BaseModel):
    """Request model for authentication token validation."""
    token: str = Field(..., description="JWT token to validate")


class AuthTokenResponse(BaseModel):
    """Response model for authentication token validation."""
    valid: bool
    user_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None


class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=1, max_length=50, description="User's username")
    password: str = Field(..., min_length=8, description="User's password")


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserAuthResponse(BaseModel):
    """Response model for user authentication."""
    user_id: str
    email: EmailStr
    name: str
    access_token: str
    token_type: str = "bearer"


class BetterAuthTokenPayload(BaseModel):
    """Model representing the expected payload in Better Auth tokens."""
    sub: str = Field(..., description="Subject (user ID)")
    exp: Optional[int] = Field(None, description="Expiration timestamp")
    iat: Optional[int] = Field(None, description="Issued at timestamp")
    jti: Optional[str] = Field(None, description="JWT ID")
    aud: Optional[str] = Field(None, description="Audience")
    iss: Optional[str] = Field(None, description="Issuer")


class AuthValidationResult(BaseModel):
    """Model representing the result of authentication validation."""
    authenticated: bool
    user_id: Optional[str] = None
    error_message: Optional[str] = None
    token_valid: bool = False
    token_expired: bool = False
    user_exists: bool = False