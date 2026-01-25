import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
import uuid
from backend.src.main import app
from backend.src.models.task_model import Task
from backend.src.models.user_model import User
from backend.src.schemas.task_schemas import TaskResponse


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


def test_successful_task_creation(client):
    """Test successful task creation with valid inputs"""
    # Mock user ID and token
    user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    # Test data
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }

    # Mock the authentication dependency
    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()
                mock_task = Task(
                    id=uuid.uuid4(),
                    title=task_data["title"],
                    description=task_data["description"],
                    user_id=uuid.uuid4()
                )
                mock_db.add.return_value = None
                mock_db.commit.return_value = None
                mock_db.refresh.return_value = None
                mock_db.get.return_value = mock_task
                mock_session.return_value.__enter__.return_value = mock_db

                response = client.post(
                    f"/api/{user_id}/tasks",
                    json=task_data,
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 201
                assert response.json()["title"] == "Test Task"
                assert response.json()["description"] == "Test Description"


def test_error_response_invalid_inputs(client):
    """Test error response for invalid inputs (missing title, title too long)"""
    user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    # Test missing title
    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            response = client.post(
                f"/api/{user_id}/tasks",
                json={"description": "Test Description"},
                headers={"Authorization": f"Bearer {mock_token}"}
            )

            assert response.status_code == 422  # Validation error

    # Test title too long
    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            response = client.post(
                f"/api/{user_id}/tasks",
                json={"title": "a" * 101},  # Title too long
                headers={"Authorization": f"Bearer {mock_token}"}
            )

            assert response.status_code == 422  # Validation error


def test_error_response_unauthorized_access(client):
    """Test error response for unauthorized access attempts"""
    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    # Test unauthorized access (user trying to create task for different user)
    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=other_user_id)

        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": f"Bearer {mock_token}"}
        )

        assert response.status_code == 403  # Forbidden


def test_successful_task_retrieval_multiple(client):
    """Test successful task retrieval for user with multiple tasks"""
    user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()

                # Create mock tasks
                mock_tasks = [
                    Task(id=uuid.uuid4(), title="Task 1", user_id=uuid.UUID(user_id)),
                    Task(id=uuid.uuid4(), title="Task 2", user_id=uuid.UUID(user_id))
                ]

                # Mock the query result
                mock_exec_result = MagicMock()
                mock_exec_result.all.return_value = mock_tasks
                mock_exec_result.count.return_value = 2

                mock_query = MagicMock()
                mock_query.offset.return_value = mock_query
                mock_query.limit.return_value = mock_exec_result

                mock_select = MagicMock(return_value=mock_query)
                with patch('backend.src.api.task_routes.select', mock_select):
                    mock_db.exec.return_value = mock_exec_result

                    mock_session.return_value.__enter__.return_value = mock_db

                    response = client.get(
                        f"/api/{user_id}/tasks",
                        headers={"Authorization": f"Bearer {mock_token}"}
                    )

                    assert response.status_code == 200
                    assert len(response.json()["tasks"]) == 2


def test_successful_empty_list_retrieval(client):
    """Test successful retrieval of empty list for user with no tasks"""
    user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()

                # Mock empty task list
                mock_exec_result = MagicMock()
                mock_exec_result.all.return_value = []
                mock_exec_result.count.return_value = 0

                mock_query = MagicMock()
                mock_query.offset.return_value = mock_query
                mock_query.limit.return_value = mock_exec_result

                mock_select = MagicMock(return_value=mock_query)
                with patch('backend.src.api.task_routes.select', mock_select):
                    mock_db.exec.return_value = mock_exec_result

                    mock_session.return_value.__enter__.return_value = mock_db

                    response = client.get(
                        f"/api/{user_id}/tasks",
                        headers={"Authorization": f"Bearer {mock_token}"}
                    )

                    assert response.status_code == 200
                    assert len(response.json()["tasks"]) == 0


def test_error_response_unauthorized_retrieval(client):
    """Test error response for unauthorized access attempts during retrieval"""
    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=other_user_id)

        response = client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {mock_token}"}
        )

        assert response.status_code == 403  # Forbidden


def test_successful_task_update(client):
    """Test successful task update with valid inputs"""
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()

                # Create mock task
                mock_task = Task(
                    id=uuid.UUID(task_id),
                    title="Original Task",
                    user_id=uuid.UUID(user_id)
                )

                mock_db.get.return_value = mock_task

                mock_session.return_value.__enter__.return_value = mock_db

                update_data = {
                    "title": "Updated Task Title",
                    "description": "Updated Description",
                    "completed": True
                }

                response = client.put(
                    f"/api/{user_id}/tasks/{task_id}",
                    json=update_data,
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 200
                assert response.json()["title"] == "Updated Task Title"


def test_error_response_unauthorized_update(client):
    """Test error response for unauthorized update attempts"""
    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=other_user_id)

        response = client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json={"title": "Updated Task"},
            headers={"Authorization": f"Bearer {mock_token}"}
        )

        assert response.status_code == 403  # Forbidden


def test_error_response_nonexistent_task_update(client):
    """Test error response for attempts to update non-existent tasks"""
    user_id = str(uuid.uuid4())
    nonexistent_task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()
                mock_db.get.return_value = None  # Task not found

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.put(
                    f"/api/{user_id}/tasks/{nonexistent_task_id}",
                    json={"title": "Updated Task"},
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 404  # Not Found


def test_successful_completion_status_update(client):
    """Test successful completion status update"""
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()

                # Create mock task
                mock_task = Task(
                    id=uuid.UUID(task_id),
                    title="Test Task",
                    user_id=uuid.UUID(user_id),
                    completed=False
                )

                mock_db.get.return_value = mock_task

                mock_session.return_value.__enter__.return_value = mock_db

                update_data = {"completed": True}

                response = client.patch(
                    f"/api/{user_id}/tasks/{task_id}/complete",
                    json=update_data,
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 200
                assert response.json()["completed"] is True


def test_error_response_unauthorized_completion_update(client):
    """Test error response for unauthorized completion update attempts"""
    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=other_user_id)

        response = client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            json={"completed": True},
            headers={"Authorization": f"Bearer {mock_token}"}
        )

        assert response.status_code == 403  # Forbidden


def test_error_response_nonexistent_task_completion(client):
    """Test error response for attempts to update non-existent tasks"""
    user_id = str(uuid.uuid4())
    nonexistent_task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()
                mock_db.get.return_value = None  # Task not found

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.patch(
                    f"/api/{user_id}/tasks/{nonexistent_task_id}/complete",
                    json={"completed": True},
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 404  # Not Found


def test_successful_soft_deletion(client):
    """Test successful soft deletion of task"""
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()

                # Create mock task
                mock_task = Task(
                    id=uuid.UUID(task_id),
                    title="Test Task",
                    user_id=uuid.UUID(user_id)
                )

                mock_db.get.return_value = mock_task

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.delete(
                    f"/api/{user_id}/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 204  # No Content


def test_error_response_unauthorized_deletion(client):
    """Test error response for unauthorized deletion attempts"""
    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=other_user_id)

        response = client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {mock_token}"}
        )

        assert response.status_code == 403  # Forbidden


def test_error_response_nonexistent_task_deletion(client):
    """Test error response for attempts to delete non-existent tasks"""
    user_id = str(uuid.uuid4())
    nonexistent_task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()
                mock_db.get.return_value = None  # Task not found

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.delete(
                    f"/api/{user_id}/tasks/{nonexistent_task_id}",
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 404  # Not Found


def test_successful_individual_task_retrieval(client):
    """Test successful retrieval of individual task"""
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()

                # Create mock task
                mock_task = Task(
                    id=uuid.UUID(task_id),
                    title="Test Task",
                    user_id=uuid.UUID(user_id)
                )

                mock_db.get.return_value = mock_task

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.get(
                    f"/api/{user_id}/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 200
                assert response.json()["title"] == "Test Task"


def test_error_response_unauthorized_individual_access(client):
    """Test error response for unauthorized access attempts to individual task"""
    user_id = str(uuid.uuid4())
    other_user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=other_user_id)

        response = client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {mock_token}"}
        )

        assert response.status_code == 403  # Forbidden


def test_error_response_nonexistent_task_access(client):
    """Test error response for attempts to access non-existent tasks"""
    user_id = str(uuid.uuid4())
    nonexistent_task_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()
                mock_db.get.return_value = None  # Task not found

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.get(
                    f"/api/{user_id}/tasks/{nonexistent_task_id}",
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                assert response.status_code == 404  # Not Found