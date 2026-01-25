"""
Token management utilities for Better Auth integration.
Handles token refresh, validation, and lifecycle management.
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the auth config
from backend.src.config.auth_config import auth_config
from backend.src.auth.jwt_utils import TokenData, verify_better_auth_token


class TokenManager:
    """
    Class for managing JWT token lifecycle including refresh functionality.
    """

    def __init__(self):
        """
        Initialize the token manager with configuration.
        """
        self.secret_key = auth_config.BETTER_AUTH_SECRET
        self.algorithm = auth_config.JWT_ALGORITHM
        self.access_token_expire_seconds = auth_config.JWT_EXPIRATION_DELTA

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token for the user.

        Args:
            user_id: The user ID to associate with the refresh token

        Returns:
            Encoded refresh token string
        """
        # For refresh tokens, we might want a longer expiration
        # In a real implementation, refresh tokens would be stored in a database
        expire = datetime.utcnow() + timedelta(days=30)  # 30-day refresh token

        to_encode = {
            "sub": user_id,
            "type": "refresh",
            "exp": int(expire.timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate a new access token using a refresh token.

        Args:
            refresh_token: The refresh token to use for generating a new access token

        Returns:
            New access token string if refresh is successful, None otherwise
        """
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])

            # Verify this is a refresh token
            token_type = payload.get("type")
            if token_type != "refresh":
                return None

            # Check if refresh token is expired
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
                return None

            user_id = payload.get("sub")
            if not user_id:
                return None

            # Create new access token with the same user data
            new_access_token_data = {
                "sub": user_id,
                "type": "access"
            }

            # Use the standard access token creation from jwt_utils
            from backend.src.auth.jwt_utils import create_access_token as create_standard_token
            return create_standard_token(new_access_token_data)

        except JWTError:
            return None

    def validate_refresh_token(self, refresh_token: str) -> bool:
        """
        Validate if a refresh token is valid and not expired.

        Args:
            refresh_token: The refresh token to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])

            # Check if this is a refresh token
            token_type = payload.get("type")
            if token_type != "refresh":
                return False

            # Check if refresh token is expired
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
                return False

            # Verify user ID exists
            user_id = payload.get("sub")
            if not user_id:
                return False

            return True

        except JWTError:
            return False

    def rotate_tokens(self, refresh_token: str) -> Optional[tuple[str, str]]:
        """
        Rotate both refresh and access tokens.

        Args:
            refresh_token: The current refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token) if rotation is successful, None otherwise
        """
        if not self.validate_refresh_token(refresh_token):
            return None

        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")

            if not user_id:
                return None

            # Create new tokens
            new_access_token = self.create_access_token_for_user(user_id)
            new_refresh_token = self.create_refresh_token(user_id)

            return new_access_token, new_refresh_token

        except JWTError:
            return None

    def create_access_token_for_user(self, user_id: str) -> str:
        """
        Create an access token for a specific user.

        Args:
            user_id: The user ID to create an access token for

        Returns:
            Encoded access token string
        """
        from backend.src.auth.jwt_utils import create_access_token as create_standard_token
        return create_standard_token({"sub": user_id})

    def invalidate_token(self, token: str) -> bool:
        """
        Invalidate a token by adding it to a blacklist.
        NOTE: In a stateless JWT system, this would typically require a database
        to track blacklisted tokens. This is a simplified implementation.

        Args:
            token: The token to invalidate

        Returns:
            True if successfully invalidated, False otherwise
        """
        # In a real implementation, this would add the token to a blacklist database
        # For now, we'll just return True to indicate the concept
        # The actual implementation would involve storing the token's JTI in a database
        return True


# Singleton instance
token_manager = TokenManager()


def get_token_manager() -> TokenManager:
    """
    Get the token manager instance.

    Returns:
        TokenManager instance
    """
    return token_manager