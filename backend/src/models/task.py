from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .user import User

class TaskBase(SQLModel):
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending")  # pending, in_progress, completed
    priority: str = Field(default="medium")  # low, medium, high
    user_id: uuid.UUID = Field(foreign_key="user.id")


class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationship with User
    user: "User" = Relationship(back_populates="tasks")  # type: ignore


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None