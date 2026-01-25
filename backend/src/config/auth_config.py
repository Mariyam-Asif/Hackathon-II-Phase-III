"""
Authentication configuration module for Better Auth integration.
This module handles configuration settings for JWT validation and authentication.
"""

import os
from typing import Optional
from datetime import timedelta


class AuthConfig:
    """Configuration class for authentication settings."""

    # Better Auth settings
    BETTER_AUTH_SECRET: str = os.getenv(
        "BETTER_AUTH_SECRET",
        "fallback_secret_key_for_development"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Token expiration settings
    JWT_EXPIRATION_DELTA: int = int(
        os.getenv("JWT_EXPIRATION_DELTA", "604800")  # 7 days in seconds
    )

    @classmethod
    def get_token_expiration_delta(cls) -> timedelta:
        """Get the token expiration as a timedelta object."""
        return timedelta(seconds=cls.JWT_EXPIRATION_DELTA)


# Create a singleton instance of the configuration
auth_config = AuthConfig()


def get_auth_config() -> AuthConfig:
    """Get the authentication configuration instance."""
    return auth_config