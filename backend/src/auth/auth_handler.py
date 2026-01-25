from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the auth config
from ..config.auth_config import auth_config
from .jwt_utils import verify_better_auth_token, TokenData as BetterAuthTokenData

# JWT configuration - Use Better Auth settings
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", auth_config.BETTER_AUTH_SECRET)
ALGORITHM = os.getenv("JWT_ALGORITHM", auth_config.JWT_ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days in minutes

# Security scheme for API docs
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new JWT access token compatible with Better Auth standards
    """
    from .jwt_utils import create_access_token as create_better_auth_token
    # Use the utility function from jwt_utils which follows Better Auth standards
    token_data = {"sub": data.get("sub", data.get("user_id", ""))}
    token_data.update(data)
    return create_better_auth_token(token_data, expires_delta)

def verify_token(token: str) -> Optional[BetterAuthTokenData]:
    """
    Verify a Better Auth JWT token and return the token data if valid
    """
    return verify_better_auth_token(token)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current user from the Better Auth JWT token
    This will be used to verify that the user is authenticated
    """
    token = credentials.credentials
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Could not validate credentials from Better Auth token",
                "code": "INVALID_TOKEN"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Return the user_id from the verified token
    return token_data.user_id