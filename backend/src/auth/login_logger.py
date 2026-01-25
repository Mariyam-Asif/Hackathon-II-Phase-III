"""
Login audit logging for Better Auth integration.
Records authentication events for security and compliance purposes.
"""
import logging
import json
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel


class AuthEventType(Enum):
    """Enumeration of authentication event types."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    REGISTRATION_SUCCESS = "registration_success"
    REGISTRATION_FAILURE = "registration_failure"


class AuthEvent(BaseModel):
    """Model representing an authentication event."""
    timestamp: str
    event_type: AuthEventType
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: dict = {}
    session_id: Optional[str] = None


class LoginAuditLogger:
    """Class for logging authentication events."""

    def __init__(self, logger_name: str = "auth_audit"):
        """
        Initialize the login audit logger.

        Args:
            logger_name: Name of the logger to use
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        # Prevent duplicate handlers if logger already exists
        if not self.logger.handlers:
            # Create a file handler for audit logs
            file_handler = logging.FileHandler('auth_audit.log')
            file_handler.setLevel(logging.INFO)

            # Create a formatter for audit logs
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)

            # Add handler to the logger
            self.logger.addHandler(file_handler)

    def log_event(
        self,
        event_type: AuthEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
        session_id: Optional[str] = None
    ):
        """
        Log an authentication event.

        Args:
            event_type: Type of authentication event
            user_id: ID of the user involved in the event
            ip_address: IP address of the request
            user_agent: User agent string of the request
            details: Additional details about the event
            session_id: Session ID if applicable
        """
        if details is None:
            details = {}

        event = AuthEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            session_id=session_id
        )

        # Log the event as JSON
        self.logger.info(json.dumps(event.dict()))

    def log_login_success(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """
        Log a successful login event.

        Args:
            user_id: ID of the user who logged in
            ip_address: IP address of the login request
            user_agent: User agent string of the login request
            session_id: Session ID for the login
        """
        self.log_event(
            event_type=AuthEventType.LOGIN_SUCCESS,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            details={"message": "User logged in successfully"}
        )

    def log_login_failure(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        reason: str = "Unknown reason"
    ):
        """
        Log a failed login event.

        Args:
            user_id: ID of the user who attempted to log in (if known)
            ip_address: IP address of the failed login attempt
            user_agent: User agent string of the failed login attempt
            reason: Reason for the login failure
        """
        self.log_event(
            event_type=AuthEventType.LOGIN_FAILURE,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "message": f"Login failed: {reason}",
                "reason": reason
            }
        )

    def log_logout(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """
        Log a logout event.

        Args:
            user_id: ID of the user who logged out
            ip_address: IP address of the logout request
            user_agent: User agent string of the logout request
            session_id: Session ID for the logout
        """
        self.log_event(
            event_type=AuthEventType.LOGOUT,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            details={"message": "User logged out"}
        )

    def log_token_issued(
        self,
        user_id: str,
        token_type: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log a token issuance event.

        Args:
            user_id: ID of the user for whom the token was issued
            token_type: Type of token issued (access, refresh, etc.)
            ip_address: IP address of the token request
            user_agent: User agent string of the token request
        """
        self.log_event(
            event_type=AuthEventType.TOKEN_ISSUED,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "message": f"{token_type} token issued",
                "token_type": token_type
            }
        )

    def log_token_refreshed(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log a token refresh event.

        Args:
            user_id: ID of the user whose token was refreshed
            ip_address: IP address of the refresh request
            user_agent: User agent string of the refresh request
        """
        self.log_event(
            event_type=AuthEventType.TOKEN_REFRESHED,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"message": "Token refreshed"}
        )

    def log_registration_success(
        self,
        user_id: str,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log a successful registration event.

        Args:
            user_id: ID of the newly registered user
            email: Email address of the new user
            ip_address: IP address of the registration request
            user_agent: User agent string of the registration request
        """
        self.log_event(
            event_type=AuthEventType.REGISTRATION_SUCCESS,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "message": "User registered successfully",
                "email": email
            }
        )

    def log_registration_failure(
        self,
        email: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        reason: str = "Unknown reason"
    ):
        """
        Log a failed registration event.

        Args:
            email: Email address that attempted registration
            ip_address: IP address of the registration request
            user_agent: User agent string of the registration request
            reason: Reason for the registration failure
        """
        self.log_event(
            event_type=AuthEventType.REGISTRATION_FAILURE,
            user_id=None,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "message": f"Registration failed: {reason}",
                "email": email,
                "reason": reason
            }
        )


# Singleton instance
login_audit_logger = LoginAuditLogger()


def get_login_audit_logger() -> LoginAuditLogger:
    """
    Get the login audit logger instance.

    Returns:
        LoginAuditLogger instance
    """
    return login_audit_logger