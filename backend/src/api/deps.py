from typing import Generator
from sqlmodel import Session
from fastapi import Depends, HTTPException, status
from database.session import get_session
from auth.auth_handler import get_current_user
from exceptions.auth_exceptions import UserMismatchException
import uuid

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = next(get_session())
    try:
        yield db
    finally:
        db.close()

def verify_user_access(user_id: str, current_user_id: str = Depends(get_current_user)):
    """
    Dependency to verify that the current user has access to the specified user_id
    This ensures users can only access their own resources based on Better Auth standards
    """
    # Convert both to UUID objects to ensure they're properly formatted
    try:
        requested_user_id = uuid.UUID(user_id)
        current_user_uuid = uuid.UUID(current_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid user ID format",
                "code": "INVALID_USER_ID_FORMAT"
            }
        )

    if requested_user_id != current_user_uuid:
        raise UserMismatchException(
            detail=f"Access denied: token user ID ({current_user_uuid}) does not match requested user ID ({requested_user_id})"
        )

    return current_user_id