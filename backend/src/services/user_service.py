"""
Service layer for user management operations.
Handles user creation, authentication, and related business logic.
"""
from sqlmodel import Session, select
from typing import Optional
import uuid
from datetime import datetime

from ..models.user import User
from ..exceptions.auth_exceptions import InvalidCredentialsException


class UserService:
    """
    Service class for user-related operations including registration and authentication.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the user service with a database session.

        Args:
            db_session: The database session to use for operations
        """
        self.db = db_session

    def create_user(self, email: str, username: str, password: str) -> User:
        """
        Create a new user with the provided details.

        Args:
            email: User's email address
            username: User's chosen username
            password: User's plain text password (will be hashed)

        Returns:
            The created User object
        """
        # Hash the password before storing
        import bcrypt

        # Bcrypt has a 72-byte password length limit, so we truncate if necessary
        safe_password = password[:72] if len(password.encode('utf-8')) > 72 else password

        # Use bcrypt directly to avoid version compatibility issues
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(safe_password.encode('utf-8'), salt).decode('utf-8')

        # Create new user instance
        user = User(
            email=email,
            name=username,  # Using name instead of username in the new model
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Add to database
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by their email address.

        Args:
            email: The email address to search for

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        user = self.db.exec(statement).first()
        return user

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Find a user by their ID.

        Args:
            user_id: The UUID of the user to search for

        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        user = self.db.exec(statement).first()
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            email: User's email address
            password: User's plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        import time

        # Find user by email
        user = self.get_user_by_email(email)
        if not user:
            # To prevent user enumeration, use the same timing regardless of user existence
            # This simulates the time it would take to verify a password
            import bcrypt
            salt = bcrypt.gensalt()
            bcrypt.hashpw("dummy_password_to_match_timing".encode('utf-8'), salt)
            return None

        # Verify password
        # Bcrypt has a 72-byte password length limit, so we truncate if necessary
        safe_password = password[:72] if len(password.encode('utf-8')) > 72 else password

        import bcrypt
        # Use bcrypt to verify the password
        if not bcrypt.checkpw(safe_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return None

        return user

    def update_user(self, user_id: uuid.UUID, **kwargs) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: ID of the user to update
            **kwargs: Fields to update

        Returns:
            Updated User object if successful, None otherwise
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Update allowed fields
        allowed_fields = {'username', 'email', 'password_hash'}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Delete a user (hard delete).

        Args:
            user_id: ID of the user to delete

        Returns:
            True if successful, False otherwise
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        return True