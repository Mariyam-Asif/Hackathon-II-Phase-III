from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)
    name: Optional[str] = Field(default=None)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with Task
    tasks: List["Task"] = Relationship(back_populates="user")  # type: ignore
    # Relationship with Conversation
    conversations: List["Conversation"] = Relationship(back_populates="user", cascade_delete=True)  # type: ignore

    # Update updated_at field before each update
    def __setattr__(self, name, value):
        if name == 'updated_at':
            super().__setattr__('updated_at', datetime.utcnow())
        super().__setattr__(name, value)


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime