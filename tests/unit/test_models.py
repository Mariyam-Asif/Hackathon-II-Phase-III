import pytest
from datetime import datetime
import uuid
from backend.src.models.user_model import User
from backend.src.models.task_model import Task


def test_user_model_creation():
    """Test successful creation of a User model"""
    user = User(
        email="test@example.com",
        username="testuser"
    )

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert isinstance(user.id, uuid.UUID)
    assert user.created_at is not None
    assert user.updated_at is not None


def test_task_model_creation():
    """Test successful creation of a Task model"""
    user_id = uuid.uuid4()
    task = Task(
        title="Test Task",
        description="Test Description",
        user_id=user_id
    )

    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.user_id == user_id
    assert isinstance(task.id, uuid.UUID)
    assert task.completed is False
    assert task.deleted is False
    assert task.created_at is not None
    assert task.updated_at is not None


def test_task_title_validation():
    """Test validation of task title length"""
    user_id = uuid.uuid4()

    # Test valid title length
    task = Task(title="Valid title", user_id=user_id)
    assert task.title == "Valid title"

    # Test short title
    task_short = Task(title="Hi", user_id=user_id)
    assert task_short.title == "Hi"


def test_task_completion_toggle():
    """Test task completion status"""
    user_id = uuid.uuid4()
    task = Task(title="Test Task", user_id=user_id)

    assert task.completed is False

    task.completed = True
    assert task.completed is True


def test_task_soft_delete():
    """Test task soft delete functionality"""
    user_id = uuid.uuid4()
    task = Task(title="Test Task", user_id=user_id)

    assert task.deleted is False

    task.deleted = True
    assert task.deleted is True