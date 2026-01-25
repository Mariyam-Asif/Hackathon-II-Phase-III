from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .task_model import Task

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False, min_length=3, max_length=50)

class User(UserBase, table=True):
    """
    User model representing a registered user account with unique identifier that owns tasks
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False, min_length=3, max_length=50)
    password_hash: str = Field(nullable=False)  # Hashed password
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship with Task
    tasks: List["Task"] = Relationship(back_populates="user")  # type: ignore

    # Update updated_at field before each update
    def __setattr__(self, name, value):
        if name == 'updated_at':
            super().__setattr__('updated_at', datetime.utcnow())
        super().__setattr__(name, value)