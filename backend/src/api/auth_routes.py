"""
API routes for authentication endpoints including registration and login.
Integrates with Better Auth for user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session
from typing import Dict
import uuid

from ..models.auth_models import (
    UserRegistrationRequest,
    UserLoginRequest,
    UserAuthResponse,
    AuthTokenRequest,
    AuthTokenResponse
)
from ..auth.auth_handler import create_access_token
from ..database.session import get_session
from ..models.user_model import User
from ..exceptions.auth_exceptions import InvalidCredentialsException, UserNotFoundException
from ..services.user_service import UserService
from ..auth.jwt_utils import verify_better_auth_token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserAuthResponse)
async def register_user(
    user_data: UserRegistrationRequest,
    db: Session = Depends(get_session)
):
    """
    Register a new user through the system.
    NOTE: In a real Better Auth integration, this would typically be handled
    by the Better Auth frontend, but we're providing an API endpoint for
    integration purposes.
    """
    try:
        # Create user service instance
        user_service = UserService(db)

        # Check if user already exists
        existing_user = user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Create new user
        user = user_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password  # This will be hashed in the service
        )

        # Create access token for the new user
        token_data = {"sub": str(user.id), "email": user.email, "username": user.username}
        access_token = create_access_token(token_data)

        return UserAuthResponse(
            user_id=str(user.id),
            email=user.email,
            username=user.username,
            access_token=access_token
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=UserAuthResponse)
async def login_user(
    login_data: UserLoginRequest,
    db: Session = Depends(get_session)
):
    """
    Authenticate user and return access token.
    """
    try:
        user_service = UserService(db)

        # Check if user exists first
        existing_user = user_service.get_user_by_email(login_data.email)
        if not existing_user:
            raise UserNotFoundException(detail={
                "error": "No account found with this email. Please register first.",
                "code": "USER_NOT_REGISTERED"
            })

        # Verify user credentials if user exists
        user = user_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise InvalidCredentialsException(detail="Invalid password for this email address")

        # Create access token
        token_data = {"sub": str(user.id), "email": user.email, "username": user.username}
        access_token = create_access_token(token_data)

        return UserAuthResponse(
            user_id=str(user.id),
            email=user.email,
            username=user.username,
            access_token=access_token,
            token_type="bearer"
        )

    except (InvalidCredentialsException, UserNotFoundException):
        raise
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/validate-token", response_model=AuthTokenResponse)
async def validate_token(
    token_request: AuthTokenRequest
):
    """
    Validate a JWT token and return information about its validity.
    """
    token_data = verify_better_auth_token(token_request.token)

    if token_data:
        return AuthTokenResponse(
            valid=True,
            user_id=token_data.user_id,
            expires_at=None,  # Would need to convert timestamp to datetime if needed
            error=None
        )
    else:
        return AuthTokenResponse(
            valid=False,
            user_id=None,
            expires_at=None,
            error="Invalid or expired token"
        )


@router.post("/logout")
async def logout_user():
    """
    Logout endpoint (stateless - no server-side session to clear).
    """
    # In a stateless JWT system, logout is typically handled on the client side
    # by simply discarding the token. Server-side session management is not used.
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=Dict)
async def get_current_user_profile(
    current_user_id: str = Depends(lambda: "test-user-id")  # Placeholder until we integrate deps properly
):
    """
    Get the profile of the currently authenticated user.
    """
    # In a real implementation, this would fetch user data from the database
    # based on the current user ID extracted from the token
    return {
        "user_id": current_user_id,
        "message": "User profile endpoint - would return user details from database"
    }