"""
Error handlers for authentication-related exceptions.
Provides consistent error responses for all authentication failure cases.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict, Any

from ..exceptions.auth_exceptions import (
    AuthException,
    TokenValidationException,
    UserNotFoundException,
    InsufficientPermissionsException,
    UserMismatchException,
    InvalidCredentialsException,
    AccountLockedException,
    RateLimitExceededException,
    TokenTypeException,
    TokenFormatException
)


async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
    """
    Handle AuthException and subclasses.

    Args:
        request: The incoming request
        exc: The AuthException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Authentication error"),
            "code": exc.detail.get("code", "AUTH_ERROR") if isinstance(exc.detail, dict) else "AUTH_ERROR",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def token_validation_exception_handler(request: Request, exc: TokenValidationException) -> JSONResponse:
    """
    Handle TokenValidationException.

    Args:
        request: The incoming request
        exc: The TokenValidationException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Token validation failed"),
            "code": exc.detail.get("code", "TOKEN_VALIDATION_FAILED") if isinstance(exc.detail, dict) else "TOKEN_VALIDATION_FAILED",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def user_not_found_exception_handler(request: Request, exc: UserNotFoundException) -> JSONResponse:
    """
    Handle UserNotFoundException.

    Args:
        request: The incoming request
        exc: The UserNotFoundException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "User not found"),
            "code": exc.detail.get("code", "USER_NOT_FOUND") if isinstance(exc.detail, dict) else "USER_NOT_FOUND",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def insufficient_permissions_exception_handler(request: Request, exc: InsufficientPermissionsException) -> JSONResponse:
    """
    Handle InsufficientPermissionsException.

    Args:
        request: The incoming request
        exc: The InsufficientPermissionsException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Insufficient permissions"),
            "code": exc.detail.get("code", "INSUFFICIENT_PERMISSIONS") if isinstance(exc.detail, dict) else "INSUFFICIENT_PERMISSIONS",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def user_mismatch_exception_handler(request: Request, exc: UserMismatchException) -> JSONResponse:
    """
    Handle UserMismatchException.

    Args:
        request: The incoming request
        exc: The UserMismatchException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "User ID mismatch"),
            "code": exc.detail.get("code", "USER_MISMATCH") if isinstance(exc.detail, dict) else "USER_MISMATCH",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentialsException) -> JSONResponse:
    """
    Handle InvalidCredentialsException.

    Args:
        request: The incoming request
        exc: The InvalidCredentialsException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Invalid credentials"),
            "code": exc.detail.get("code", "INVALID_CREDENTIALS") if isinstance(exc.detail, dict) else "INVALID_CREDENTIALS",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def account_locked_exception_handler(request: Request, exc: AccountLockedException) -> JSONResponse:
    """
    Handle AccountLockedException.

    Args:
        request: The incoming request
        exc: The AccountLockedException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Account is locked"),
            "code": exc.detail.get("code", "ACCOUNT_LOCKED") if isinstance(exc.detail, dict) else "ACCOUNT_LOCKED",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def rate_limit_exceeded_exception_handler(request: Request, exc: RateLimitExceededException) -> JSONResponse:
    """
    Handle RateLimitExceededException.

    Args:
        request: The incoming request
        exc: The RateLimitExceededException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Rate limit exceeded"),
            "code": exc.detail.get("code", "RATE_LIMIT_EXCEEDED") if isinstance(exc.detail, dict) else "RATE_LIMIT_EXCEEDED",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


async def token_type_exception_handler(request: Request, exc: TokenTypeException) -> JSONResponse:
    """
    Handle TokenTypeException.

    Args:
        request: The incoming request
        exc: The TokenTypeException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Unsupported token type"),
            "code": exc.detail.get("code", "UNSUPPORTED_TOKEN_TYPE") if isinstance(exc.detail, dict) else "UNSUPPORTED_TOKEN_TYPE",
            "timestamp": _get_current_timestamp(),

            "path": str(request.url)
        }
    )


async def token_format_exception_handler(request: Request, exc: TokenFormatException) -> JSONResponse:
    """
    Handle TokenFormatException.

    Args:
        request: The incoming request
        exc: The TokenFormatException that was raised

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Invalid token format"),
            "code": exc.detail.get("code", "INVALID_TOKEN_FORMAT") if isinstance(exc.detail, dict) else "INVALID_TOKEN_FORMAT",
            "timestamp": _get_current_timestamp(),
            "path": str(request.url)
        }
    )


def _get_current_timestamp() -> str:
    """
    Get the current timestamp in ISO format.

    Returns:
        Current timestamp as ISO formatted string
    """
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"


def register_auth_error_handlers(app):
    """
    Register all authentication error handlers with the FastAPI app.

    Args:
        app: The FastAPI application instance
    """
    app.add_exception_handler(AuthException, auth_exception_handler)
    app.add_exception_handler(TokenValidationException, token_validation_exception_handler)
    app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)
    app.add_exception_handler(InsufficientPermissionsException, insufficient_permissions_exception_handler)
    app.add_exception_handler(UserMismatchException, user_mismatch_exception_handler)
    app.add_exception_handler(InvalidCredentialsException, invalid_credentials_exception_handler)
    app.add_exception_handler(AccountLockedException, account_locked_exception_handler)
    app.add_exception_handler(RateLimitExceededException, rate_limit_exceeded_exception_handler)
    app.add_exception_handler(TokenTypeException, token_type_exception_handler)
    app.add_exception_handler(TokenFormatException, token_format_exception_handler)

    return app