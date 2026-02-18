from sqlmodel import Session, select
from typing import List, Optional
from ..models.user import User, UserCreate
from ..models.task import Task, TaskCreate, TaskUpdate
from ..models.conversation import Conversation, ConversationCreate
from ..models.message import Message, MessageCreate, MessageStatus, SenderType
import uuid
from datetime import datetime


def create_user(session: Session, user: UserCreate) -> User:
    """Create a new user in the database"""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(user.password)

    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get a user by ID"""
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()


def create_task(session: Session, task: TaskCreate) -> Task:
    """Create a new task in the database"""
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        user_id=task.user_id
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def get_tasks_by_user_id(session: Session, user_id: uuid.UUID) -> List[Task]:
    """Get all tasks for a specific user"""
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()


def get_task_by_id(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
    """Get a specific task by ID for a specific user (to ensure data isolation)"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    return session.exec(statement).first()


def update_task(session: Session, task_id: uuid.UUID, user_id: uuid.UUID, task_update: TaskUpdate) -> Optional[Task]:
    """Update a task for a specific user"""
    db_task = get_task_by_id(session, task_id, user_id)
    if db_task:
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        # If status is being updated to 'completed', set completed_at
        if hasattr(task_update, 'status') and task_update.status == 'completed':
            db_task.completed_at = datetime.utcnow()

        db_task.updated_at = datetime.utcnow()
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
    return db_task


def delete_task(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Delete a task for a specific user"""
    db_task = get_task_by_id(session, task_id, user_id)
    if db_task:
        session.delete(db_task)
        session.commit()
        return True
    return False


def complete_task(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
    """Mark a task as completed for a specific user"""
    db_task = get_task_by_id(session, task_id, user_id)
    if db_task:
        db_task.status = 'completed'
        db_task.completed_at = datetime.utcnow()
        db_task.updated_at = datetime.utcnow()
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
    return db_task


# Conversation CRUD operations
def create_conversation(session: Session, conversation: ConversationCreate) -> Conversation:
    """Create a new conversation in the database"""
    db_conversation = Conversation(
        user_id=conversation.user_id,
        title=conversation.title
    )
    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)
    return db_conversation


def get_conversation_by_id(session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Conversation]:
    """Get a specific conversation by ID for a specific user (to ensure data isolation)"""
    statement = select(Conversation).where(Conversation.conversation_id == conversation_id, Conversation.user_id == user_id)
    return session.exec(statement).first()


def get_conversations_by_user_id(session: Session, user_id: uuid.UUID) -> List[Conversation]:
    """Get all conversations for a specific user"""
    statement = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
    return session.exec(statement).all()


def update_conversation(session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, title: Optional[str] = None) -> Optional[Conversation]:
    """Update a conversation for a specific user"""
    db_conversation = get_conversation_by_id(session, conversation_id, user_id)
    if db_conversation:
        if title is not None:
            db_conversation.title = title
        db_conversation.updated_at = datetime.utcnow()
        session.add(db_conversation)
        session.commit()
        session.refresh(db_conversation)
    return db_conversation


def delete_conversation(session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Delete a conversation for a specific user"""
    db_conversation = get_conversation_by_id(session, conversation_id, user_id)
    if db_conversation:
        session.delete(db_conversation)
        session.commit()
        return True
    return False


# Message CRUD operations
def create_message(session: Session, message: MessageCreate) -> Message:
    """Create a new message in the database"""
    db_message = Message(
        conversation_id=message.conversation_id,
        sender_type=message.sender_type,
        content=message.content,
        status=message.status,
        parent_message_id=message.parent_message_id
    )
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    return db_message


def get_messages_by_conversation_id(session: Session, conversation_id: uuid.UUID) -> List[Message]:
    """Get all messages for a specific conversation"""
    statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc())
    return session.exec(statement).all()


def get_message_by_id(session: Session, message_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Message]:
    """Get a specific message by ID for a specific user (through conversation relationship)"""
    statement = select(Message).join(Conversation).where(
        Message.message_id == message_id,
        Conversation.user_id == user_id
    )
    return session.exec(statement).first()


def update_message(session: Session, message_id: uuid.UUID, user_id: uuid.UUID, content: Optional[str] = None, status: Optional[MessageStatus] = None) -> Optional[Message]:
    """Update a message for a specific user"""
    db_message = get_message_by_id(session, message_id, user_id)
    if db_message:
        if content is not None:
            db_message.content = content
        if status is not None:
            db_message.status = status
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
    return db_message


def delete_message(session: Session, message_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Delete a message for a specific user"""
    db_message = get_message_by_id(session, message_id, user_id)
    if db_message:
        session.delete(db_message)
        session.commit()
        return True
    return False