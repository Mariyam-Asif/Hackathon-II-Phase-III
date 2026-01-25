"""
Rate limiting utilities for authentication endpoints.
Prevents abuse and brute force attacks on authentication endpoints.
"""
import time
from typing import Dict, Optional
from collections import defaultdict, deque
import threading


class RateLimiter:
    """
    Simple in-memory rate limiter for authentication endpoints.
    Tracks request counts per IP/user and enforces limits.
    """

    def __init__(self):
        # Store request times for each identifier
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if a request is allowed based on rate limits.

        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            window_start = now - window_seconds

            # Clean up old requests outside the window
            while self.requests[identifier] and self.requests[identifier][0] < window_start:
                self.requests[identifier].popleft()

            # Check if we're under the limit
            if len(self.requests[identifier]) < max_requests:
                # Add current request
                self.requests[identifier].append(now)
                return True

            return False

    def get_reset_time(
        self,
        identifier: str,
        window_seconds: int
    ) -> Optional[float]:
        """
        Get the time when the rate limit will reset for an identifier.

        Args:
            identifier: Unique identifier
            window_seconds: Time window in seconds

        Returns:
            Unix timestamp when rate limit will reset, or None if not limited
        """
        with self.lock:
            now = time.time()
            window_start = now - window_seconds

            # Clean up old requests
            while self.requests[identifier] and self.requests[identifier][0] < window_start:
                self.requests[identifier].popleft()

            if self.requests[identifier]:
                # Reset time is the oldest request time + window
                oldest_request = self.requests[identifier][0]
                return oldest_request + window_seconds

            return None


class AuthRateLimiter:
    """
    Specialized rate limiter for authentication endpoints.
    Provides different limits for different types of auth requests.
    """

    def __init__(self):
        self.global_limiter = RateLimiter()
        self.ip_limiter = RateLimiter()
        self.user_limiter = RateLimiter()

        # Default rate limits (more permissive for development)
        self.login_limits = {
            "max_requests": 20,      # 20 login attempts
            "window_seconds": 300   # per 5 minutes
        }

        self.global_limits = {
            "max_requests": 100,    # 100 auth-related requests
            "window_seconds": 3600  # per hour
        }

        self.ip_limits = {
            "max_requests": 20,     # 20 requests per IP
            "window_seconds": 60    # per minute
        }

    def is_login_allowed(self, ip_address: str, user_identifier: Optional[str] = None) -> bool:
        """
        Check if a login attempt is allowed.

        Args:
            ip_address: IP address of the request
            user_identifier: Optional user identifier (for user-specific limits)

        Returns:
            True if login is allowed, False otherwise
        """
        # Check global rate limit
        if not self.global_limiter.is_allowed("global_auth",
                                            self.global_limits["max_requests"],
                                            self.global_limits["window_seconds"]):
            return False

        # Check IP rate limit
        if not self.ip_limiter.is_allowed(ip_address,
                                        self.ip_limits["max_requests"],
                                        self.ip_limits["window_seconds"]):
            return False

        # Check user-specific rate limit if user_identifier provided
        if user_identifier:
            if not self.user_limiter.is_allowed(user_identifier,
                                              self.login_limits["max_requests"],
                                              self.login_limits["window_seconds"]):
                return False

        # Check IP-specific rate limit for login
        if not self.ip_limiter.is_allowed(f"login_{ip_address}",
                                        self.login_limits["max_requests"],
                                        self.login_limits["window_seconds"]):
            return False

        return True

    def is_registration_allowed(self, ip_address: str) -> bool:
        """
        Check if a registration attempt is allowed.

        Args:
            ip_address: IP address of the request

        Returns:
            True if registration is allowed, False otherwise
        """
        # Check global rate limit
        if not self.global_limiter.is_allowed("global_auth",
                                            self.global_limits["max_requests"],
                                            self.global_limits["window_seconds"]):
            return False

        # Check IP rate limit
        if not self.ip_limiter.is_allowed(ip_address,
                                        self.ip_limits["max_requests"],
                                        self.ip_limits["window_seconds"]):
            return False

        # Registration limits (more permissive for development)
        registration_limits = {
            "max_requests": 10,      # 10 registrations
            "window_seconds": 3600   # per hour per IP
        }

        if not self.ip_limiter.is_allowed(f"register_{ip_address}",
                                        registration_limits["max_requests"],
                                        registration_limits["window_seconds"]):
            return False

        return True

    def is_token_validation_allowed(self, ip_address: str) -> bool:
        """
        Check if a token validation request is allowed.

        Args:
            ip_address: IP address of the request

        Returns:
            True if token validation is allowed, False otherwise
        """
        # Check global rate limit
        if not self.global_limiter.is_allowed("global_auth",
                                            self.global_limits["max_requests"],
                                            self.global_limits["window_seconds"]):
            return False

        # Check IP rate limit
        if not self.ip_limiter.is_allowed(ip_address,
                                        self.ip_limits["max_requests"],
                                        self.ip_limits["window_seconds"]):
            return False

        # Token validation might have higher limits since it's less expensive
        token_validation_limits = {
            "max_requests": 60,     # 60 validations
            "window_seconds": 60    # per minute
        }

        if not self.ip_limiter.is_allowed(f"validate_{ip_address}",
                                        token_validation_limits["max_requests"],
                                        token_validation_limits["window_seconds"]):
            return False

        return True

    def get_rate_limit_info(self, identifier: str) -> Dict:
        """
        Get rate limit information for an identifier.

        Args:
            identifier: The identifier to check

        Returns:
            Dictionary with rate limit information
        """
        reset_time = self.global_limiter.get_reset_time(identifier, 3600)
        return {
            "limit": 100,
            "remaining": 100 - len(self.global_limiter.requests[identifier]),
            "reset_time": reset_time
        }


# Singleton instance
auth_rate_limiter = AuthRateLimiter()


def get_auth_rate_limiter() -> AuthRateLimiter:
    """
    Get the authentication rate limiter instance.

    Returns:
        AuthRateLimiter instance
    """
    return auth_rate_limiter