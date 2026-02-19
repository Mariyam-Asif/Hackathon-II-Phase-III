"""
Authentication middleware for Better Auth integration.
Provides global authentication enforcement for protected endpoints.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional, Set
import time
import logging

from auth.jwt_utils import verify_better_auth_token
from auth.rate_limiter import get_auth_rate_limiter
from exceptions.auth_exceptions import TokenValidationException


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware that provides global authentication enforcement.
    Applies authentication checks to protected endpoints while allowing
    public endpoints to remain accessible.
    """

    def __init__(
        self,
        app,
        public_paths: Optional[Set[str]] = None,
        protected_paths: Optional[Set[str]] = None
    ):
        """
        Initialize the authentication middleware.

        Args:
            app: The FastAPI application
            public_paths: Set of paths that don't require authentication
            protected_paths: Set of paths that require authentication (if None, all except public are protected)
        """
        super().__init__(app)
        self.public_paths = public_paths or {
            "/docs", "/redoc", "/openapi.json", "/health", "/",
            "/auth/register", "/auth/login", "/auth/validate-token", "/auth/logout"
        }
        self.protected_paths = protected_paths
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and apply authentication checks.

        Args:
            request: The incoming request
            call_next: The next middleware/function in the chain

        Returns:
            The response from the next middleware/function
        """
        # Get the request path
        path = request.url.path

        # Log the request
        start_time = time.time()
        self.logger.info(f"Processing request: {request.method} {path}")

        # Allow OPTIONS requests (preflight) without authentication
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response

        # Check if this is a public path that doesn't require authentication
        if self._is_public_path(path):
            response = await call_next(request)
            return response

        # For protected paths, check for authentication
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            # No authorization header provided
            if self._is_protected_path(path):
                self.logger.warning(f"Unauthorized access attempt to {path} - no auth header")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Authorization header is required",
                        "code": "MISSING_AUTH_HEADER"
                    }
                )

        # Extract token from header
        try:
            scheme, token = auth_header.split(" ")
            if scheme.lower() != "bearer":
                self.logger.warning(f"Invalid auth scheme in request to {path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Authorization scheme must be Bearer",
                        "code": "INVALID_AUTH_SCHEME"
                    }
                )
        except ValueError:
            self.logger.warning(f"Invalid authorization header format in request to {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Invalid authorization header format",
                    "code": "INVALID_AUTH_FORMAT"
                }
            )

        # Verify the token
        token_data = verify_better_auth_token(token)
        if not token_data:
            self.logger.warning(f"Invalid or expired token in request to {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Invalid or expired token",
                    "code": "INVALID_TOKEN"
                }
            )

        # Add user info to request state for downstream handlers
        request.state.user_id = token_data.user_id

        # Continue with the request
        response = await call_next(request)

        # Log the response
        process_time = time.time() - start_time
        self.logger.info(f"Request {request.method} {path} completed in {process_time:.2f}s with status {response.status_code}")

        return response

    def _is_public_path(self, path: str) -> bool:
        """
        Check if a path is public (doesn't require authentication).

        Args:
            path: The request path

        Returns:
            True if the path is public, False otherwise
        """
        # Check exact matches first
        if path in self.public_paths:
            return True

        # Check for path prefixes (e.g., "/static/" matches "/static/file.css")
        for public_path in self.public_paths:
            if path.startswith(public_path + "/") or path == public_path:
                return True

        return False

    def _is_protected_path(self, path: str) -> bool:
        """
        Check if a path requires authentication.

        Args:
            path: The request path

        Returns:
            True if the path is protected, False otherwise
        """
        if self.protected_paths is not None:
            return path in self.protected_paths

        # If no protected paths are specified, all paths except public ones are protected
        return not self._is_public_path(path)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for authentication endpoints.
    Prevents brute force and abuse of auth endpoints.
    """

    def __init__(self, app):
        """
        Initialize the rate limiting middleware.

        Args:
            app: The FastAPI application
        """
        super().__init__(app)
        self.auth_rate_limiter = get_auth_rate_limiter()
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and apply rate limiting.

        Args:
            request: The incoming request
            call_next: The next middleware/function in the chain

        Returns:
            The response from the next middleware/function
        """
        path = request.url.path

        # Allow OPTIONS requests (preflight) without rate limiting
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response

        client_ip = self._get_client_ip(request)

        # Apply rate limiting to authentication endpoints
        if path.startswith("/auth/"):
            if path == "/auth/login":
                if not self.auth_rate_limiter.is_login_allowed(client_ip):
                    self.logger.warning(f"Rate limit exceeded for IP {client_ip} on login endpoint")
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "Rate limit exceeded for login attempts",
                            "code": "RATE_LIMIT_EXCEEDED"
                        }
                    )
            elif path == "/auth/register":
                if not self.auth_rate_limiter.is_registration_allowed(client_ip):
                    self.logger.warning(f"Rate limit exceeded for IP {client_ip} on registration endpoint")
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "Rate limit exceeded for registration attempts",
                            "code": "RATE_LIMIT_EXCEEDED"
                        }
                    )
            elif path == "/auth/validate-token":
                if not self.auth_rate_limiter.is_token_validation_allowed(client_ip):
                    self.logger.warning(f"Rate limit exceeded for IP {client_ip} on token validation endpoint")
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "Rate limit exceeded for token validation",
                            "code": "RATE_LIMIT_EXCEEDED"
                        }
                    )

        # Continue with the request
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Get the client IP address from the request.

        Args:
            request: The incoming request

        Returns:
            The client IP address
        """
        # Check for forwarded IP headers first (for use behind proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to client host
        return request.client.host if request.client else "unknown"


def get_auth_middleware():
    """
    Get the authentication middleware instance with default configuration.

    Returns:
        AuthMiddleware instance
    """
    return AuthMiddleware


def get_rate_limit_middleware():
    """
    Get the rate limiting middleware instance.

    Returns:
        RateLimitMiddleware instance
    """
    return RateLimitMiddleware