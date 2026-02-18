from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .message import Message

class ConversationBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: Optional[str] = Field(default=None)


class Conversation(ConversationBase, table=True):
    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")  # type: ignore
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)  # type: ignore


class ConversationCreate(ConversationBase):
    pass


class ConversationRead(ConversationBase):
    conversation_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConversationUpdate(SQLModel):
    title: Optional[str] = None