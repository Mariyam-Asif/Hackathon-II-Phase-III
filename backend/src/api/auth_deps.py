"""
Authentication dependencies for API endpoints.
Provides dependency injection functions for authentication validation.
"""
from fastapi import Depends, HTTPException, status
from typing import Generator
from sqlmodel import Session
from ..auth.auth_handler import get_current_user
from ..database.session import get_session
from ..exceptions.auth_exceptions import UserMismatchException
import uuid


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session for authentication operations.
    """
    db = next(get_session())
    try:
        yield db
    finally:
        db.close()


def verify_user_access(user_id: str, current_user_id: str = Depends(get_current_user)):
    """
    Dependency to verify that the current user has access to the specified user_id.
    This ensures users can only access their own resources.

    Args:
        user_id: The user ID from the URL/path parameter
        current_user_id: The user ID extracted from the JWT token (via dependency)

    Raises:
        UserMismatchException: If the token user ID doesn't match the requested user ID
    """
    # Convert both to UUID objects to ensure they're properly formatted
    try:
        requested_user_id = uuid.UUID(user_id)
        current_user_uuid = uuid.UUID(current_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    if requested_user_id != current_user_uuid:
        raise UserMismatchException(
            detail=f"Access denied: token user ID ({current_user_uuid}) does not match requested user ID ({requested_user_id})"
        )

    return current_user_id


def require_authentication(current_user_id: str = Depends(get_current_user)):
    """
    Dependency to require authentication for an endpoint.
    Simply checks that a valid JWT token is present and returns the user ID.

    Args:
        current_user_id: The user ID extracted from the JWT token

    Returns:
        The authenticated user's ID
    """
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return current_user_id


def verify_admin_access(current_user_id: str = Depends(get_current_user)):
    """
    Dependency to verify that the current user has admin privileges.
    NOTE: This is a placeholder implementation. In a real system, you would
    check user roles/permissions in the database.

    Args:
        current_user_id: The user ID extracted from the JWT token

    Raises:
        HTTPException: If the user doesn't have admin privileges
    """
    # Placeholder: In a real implementation, check if user has admin role
    # For now, just return the user ID to allow access
    # You would typically query the database to check user permissions
    return current_user_id