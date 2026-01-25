import pytest
from datetime import datetime
import uuid
from backend.src.schemas.task_schemas import TaskCreate, TaskUpdate, TaskCompleteUpdate, TaskResponse


def test_task_create_schema_valid():
    """Test valid TaskCreate schema"""
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }
    task_create = TaskCreate(**task_data)

    assert task_create.title == "Test Task"
    assert task_create.description == "Test Description"


def test_task_create_schema_minimal():
    """Test TaskCreate schema with minimal data"""
    task_data = {
        "title": "Test Task"
    }
    task_create = TaskCreate(**task_data)

    assert task_create.title == "Test Task"
    assert task_create.description is None


def test_task_create_title_length_validation():
    """Test TaskCreate schema title length validation"""
    # Test title that's too long (over 100 chars)
    with pytest.raises(ValueError):
        TaskCreate(title="a" * 101)


def test_task_update_schema_partial():
    """Test TaskUpdate schema with partial data"""
    task_update = TaskUpdate(title="Updated Title")

    assert task_update.title == "Updated Title"
    assert task_update.description is None
    assert task_update.completed is None


def test_task_update_schema_full():
    """Test TaskUpdate schema with all fields"""
    task_update = TaskUpdate(
        title="Updated Title",
        description="Updated Description",
        completed=True
    )

    assert task_update.title == "Updated Title"
    assert task_update.description == "Updated Description"
    assert task_update.completed is True


def test_task_complete_update_schema():
    """Test TaskCompleteUpdate schema"""
    # Test with completed=True
    update_true = TaskCompleteUpdate(completed=True)
    assert update_true.completed is True

    # Test with completed=False
    update_false = TaskCompleteUpdate(completed=False)
    assert update_false.completed is False

    # Test with no value (None)
    update_none = TaskCompleteUpdate()
    assert update_none.completed is None


def test_task_response_schema():
    """Test TaskResponse schema"""
    task_response = TaskResponse(
        id=uuid.uuid4(),
        title="Test Task",
        description="Test Description",
        completed=False,
        deleted=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    assert isinstance(task_response.id, uuid.UUID)
    assert task_response.title == "Test Task"
    assert task_response.description == "Test Description"
    assert task_response.completed is False
    assert task_response.deleted is False
    assert isinstance(task_response.created_at, datetime)
    assert isinstance(task_response.updated_at, datetime)