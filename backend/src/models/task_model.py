from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user_model import User

class Task(SQLModel, table=True):
    """
    Task model representing a user's to-do item with properties like title (max 100 chars),
    description (optional), completion status, deletion status, and timestamps
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(nullable=False, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    deleted: bool = Field(default=False)  # For soft delete
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship with User
    user: "User" = Relationship(back_populates="tasks")  # type: ignore

    # Indexes will be handled by the index=True parameter on user_id
    # Additional indexes can be added if needed

    # Update updated_at field before each update
    def __setattr__(self, name, value):
        if name == 'updated_at':
            super().__setattr__('updated_at', datetime.utcnow())
        elif name == 'title':
            # Ensure title constraints
            if len(value) < 1 or len(value) > 100:
                raise ValueError("Title must be between 1 and 100 characters")
        super().__setattr__(name, value)