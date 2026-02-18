from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
import uuid
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .conversation import Conversation

class SenderType(str, Enum):
    user = "user"
    agent = "agent"

class MessageStatus(str, Enum):
    sent = "sent"
    pending = "pending"
    error = "error"

class MessageBase(SQLModel):
    conversation_id: uuid.UUID = Field(foreign_key="conversation.conversation_id")
    sender_type: SenderType = Field(nullable=False)
    content: str = Field(nullable=False)
    status: MessageStatus = Field(default=MessageStatus.sent)


class Message(MessageBase, table=True):
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parent_message_id: Optional[uuid.UUID] = Field(default=None, foreign_key="message.message_id")

    # Relationship
    conversation: "Conversation" = Relationship(back_populates="messages")  # type: ignore


class MessageCreate(MessageBase):
    parent_message_id: Optional[uuid.UUID] = None


class MessageRead(MessageBase):
    message_id: uuid.UUID
    timestamp: datetime


class MessageUpdate(SQLModel):
    content: Optional[str] = None
    status: Optional[MessageStatus] = None