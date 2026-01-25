"""
Custom exception classes for authentication-related errors in Better Auth integration.
Provides specific exception types for different authentication failure scenarios.
"""
from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception class."""
    def __init__(self, detail: str = "Authentication error", headers: dict = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class TokenValidationException(AuthException):
    """Exception raised when token validation fails."""
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class UserNotFoundException(AuthException):
    """Exception raised when the user associated with a token is not found."""
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail)


class InsufficientPermissionsException(HTTPException):
    """Exception raised when a user lacks required permissions for an action."""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class UserMismatchException(HTTPException):
    """Exception raised when the user in the token doesn't match the requested resource."""
    def __init__(self, detail: str = "User ID in token does not match requested resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class InvalidCredentialsException(AuthException):
    """Exception raised when provided credentials are invalid."""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AccountLockedException(AuthException):
    """Exception raised when an account is locked or disabled."""
    def __init__(self, detail: str = "Account is locked or disabled"):
        super().__init__(detail=detail)


class RateLimitExceededException(HTTPException):
    """Exception raised when authentication attempts exceed rate limits."""
    def __init__(self, detail: str = "Rate limit exceeded for authentication attempts"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )


class TokenTypeException(AuthException):
    """Exception raised when the token type is not supported."""
    def __init__(self, detail: str = "Unsupported token type"):
        super().__init__(detail=detail)


class TokenFormatException(AuthException):
    """Exception raised when the token format is invalid."""
    def __init__(self, detail: str = "Invalid token format"):
        super().__init__(detail=detail)