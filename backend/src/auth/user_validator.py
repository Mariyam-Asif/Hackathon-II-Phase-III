"""
User validation utilities for Better Auth integration.
Validates user identity and authentication status.
"""
from typing import Optional
from sqlmodel import Session, select
import uuid

from backend.src.models.user_model import User
from backend.src.auth.jwt_utils import verify_better_auth_token, TokenData
from backend.src.exceptions.auth_exceptions import (
    UserNotFoundException,
    TokenValidationException,
    UserMismatchException
)


class UserValidator:
    """
    Class for validating user identity and authentication status.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the user validator with a database session.

        Args:
            db_session: The database session to use for validation
        """
        self.db = db_session

    def validate_user_from_token(self, token: str) -> User:
        """
        Validate a user based on their JWT token.

        Args:
            token: The JWT token to validate

        Returns:
            User object if valid, raises exception if invalid

        Raises:
            TokenValidationException: If the token is invalid
            UserNotFoundException: If the user in the token doesn't exist
        """
        # Verify the token
        token_data = verify_better_auth_token(token)
        if not token_data:
            raise TokenValidationException(detail="Invalid or expired token")

        # Get user from database
        user = self.get_user_by_id(uuid.UUID(token_data.user_id))
        if not user:
            raise UserNotFoundException(detail=f"User with ID {token_data.user_id} not found")

        # Check if user is active
        if user.deleted:
            raise UserNotFoundException(detail="User account is deactivated")

        return user

    def validate_user_access(self, token: str, required_user_id: str) -> bool:
        """
        Validate that the user in the token has access to the required user ID.

        Args:
            token: The JWT token to validate
            required_user_id: The user ID that access is required for

        Returns:
            True if access is granted, raises exception if not

        Raises:
            UserMismatchException: If the token user ID doesn't match the required user ID
            TokenValidationException: If the token is invalid
        """
        token_data = verify_better_auth_token(token)
        if not token_data:
            raise TokenValidationException(detail="Invalid or expired token")

        # Compare user IDs
        token_user_id = uuid.UUID(token_data.user_id)
        required_uuid = uuid.UUID(required_user_id)

        if token_user_id != required_uuid:
            raise UserMismatchException(
                detail=f"Access denied: token user ID ({token_user_id}) does not match required user ID ({required_uuid})"
            )

        return True

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieve a user by their ID from the database.

        Args:
            user_id: The UUID of the user to retrieve

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        user = self.db.exec(statement).first()
        return user

    def is_user_active(self, user: User) -> bool:
        """
        Check if a user is active (not deleted).

        Args:
            user: The user to check

        Returns:
            True if active, False otherwise
        """
        return not user.deleted

    def validate_token_user_identity(self, token: str, expected_email: str = None) -> TokenData:
        """
        Validate the identity of the user in the token.

        Args:
            token: The JWT token to validate
            expected_email: Optional email to verify against

        Returns:
            TokenData object if valid

        Raises:
            TokenValidationException: If the token is invalid
        """
        token_data = verify_better_auth_token(token)
        if not token_data:
            raise TokenValidationException(detail="Invalid or expired token")

        # If an expected email is provided, we'd need to validate it against the database
        if expected_email:
            user = self.get_user_by_id(uuid.UUID(token_data.user_id))
            if not user or user.email != expected_email:
                raise TokenValidationException(detail="Token user does not match expected email")

        return token_data

    def validate_user_permissions(self, token: str, required_permission: str = None) -> bool:
        """
        Validate that the user has required permissions.

        Args:
            token: The JWT token to validate
            required_permission: Optional permission to check for

        Returns:
            True if user has required permissions, False otherwise
        """
        # For now, we'll just validate that the user is authenticated
        # In a more complex system, we would check user roles/permissions
        try:
            self.validate_user_from_token(token)

            # If a specific permission is required, we would check it here
            # For now, just return True for authenticated users
            if required_permission:
                # Placeholder: implement permission checking logic
                # This would typically check user roles or permissions in the database
                pass

            return True
        except (TokenValidationException, UserNotFoundException):
            return False