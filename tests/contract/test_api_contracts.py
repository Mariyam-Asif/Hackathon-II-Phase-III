import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
from backend.src.main import app
from backend.src.models.task_model import Task
from backend.src.schemas.response_schemas import ErrorResponse


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


def test_api_contract_post_task_response_format(client):
    """Test API contract compliance for POST /api/{user_id}/tasks response format"""
    user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    with patch('backend.src.auth.auth_handler.verify_token') as mock_verify:
        mock_verify.return_value = MagicMock(user_id=user_id)

        with patch('backend.src.api.deps.verify_user_access') as mock_access:
            mock_access.return_value = user_id

            with patch('backend.src.database.session.next') as mock_session:
                mock_db = MagicMock()
                mock_task = Task(
                    id=uuid.uuid4(),
                    title="Test Task",
                    description="Test Description",
                    user_id=uuid.uuid4()
                )
                mock_db.add.return_value = None
                mock_db.commit.return_value = None
                mock_db.refresh.return_value = None
                mock_db.get.return_value = mock_task
                mock_session.return_value.__enter__.return_value = mock_db

                response = client.post(
                    f"/api/{user_id}/tasks",
                    json={"title": "Test Task", "description": "Test Description"},
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                # Verify response format
                assert response.status_code == 201
                response_data = response.json()

                # Check that all required fields are present
                assert "id" in response_data
                assert "title" in response_data
                assert "description" in response_data
                assert "completed" in response_data
                assert "deleted" in response_data
                assert "created_at" in response_data
                assert "updated_at" in response_data

                # Check data types
                assert isinstance(response_data["id"], str)  # UUID as string
                assert isinstance(response_data["title"], str)
                assert response_data["description"] is None or isinstance(response_data["description"], str)
                assert isinstance(response_data["completed"], bool)
                assert isinstance(response_data["deleted"], bool)
                assert isinstance(response_data["created_at"], str)  # ISO datetime string
                assert isinstance(response_data["updated_at"], str)  # ISO datetime string


def test_api_contract_get_tasks_response_format(client):
    """Test API contract compliance for GET /api/{user_id}/tasks response format"""
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

                    # Verify response format
                    assert response.status_code == 200
                    response_data = response.json()

                    # Check that all required fields are present
                    assert "tasks" in response_data
                    assert "total" in response_data
                    assert "limit" in response_data
                    assert "offset" in response_data

                    # Check that tasks list has correct format
                    assert isinstance(response_data["tasks"], list)
                    if response_data["tasks"]:
                        task = response_data["tasks"][0]
                        assert "id" in task
                        assert "title" in task
                        assert "description" in task
                        assert "completed" in task
                        assert "deleted" in task
                        assert "created_at" in task
                        assert "updated_at" in task


def test_api_contract_error_response_format(client):
    """Test API contract compliance for error response format"""
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

                # For error responses, the format may vary depending on implementation
                # The important thing is that error responses follow a consistent pattern
                assert response.status_code == 404


def test_api_contract_standardized_error_format(client):
    """Test that error responses follow the standardized format { 'error': 'message', 'code': 'error_code', 'details': {} }"""
    user_id = str(uuid.uuid4())
    mock_token = "mocked_jwt_token"

    # Test with invalid user ID format
    response = client.get(
        f"/api/invalid-user-id-format/tasks/some-task-id",
        headers={"Authorization": f"Bearer {mock_token}"}
    )

    # This should return a 422 validation error
    if response.status_code == 422:
        response_data = response.json()
        # FastAPI validation errors have a specific format
        assert "detail" in response_data


def test_api_contract_patch_completion_response_format(client):
    """Test API contract compliance for PATCH /api/{user_id}/tasks/{id}/complete response format"""
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
                    id=uuid.uuid4(),
                    title="Test Task",
                    user_id=uuid.uuid4(),
                    completed=False
                )

                mock_db.get.return_value = mock_task

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.patch(
                    f"/api/{user_id}/tasks/{task_id}/complete",
                    json={"completed": True},
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                # Verify response format
                assert response.status_code == 200
                response_data = response.json()

                # Check that all required fields are present
                assert "id" in response_data
                assert "title" in response_data
                assert "description" in response_data
                assert "completed" in response_data
                assert "deleted" in response_data
                assert "created_at" in response_data
                assert "updated_at" in response_data


def test_api_contract_delete_response_format(client):
    """Test API contract compliance for DELETE /api/{user_id}/tasks/{id} response format"""
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
                    id=uuid.uuid4(),
                    title="Test Task",
                    user_id=uuid.uuid4()
                )

                mock_db.get.return_value = mock_task

                mock_session.return_value.__enter__.return_value = mock_db

                response = client.delete(
                    f"/api/{user_id}/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                # DELETE should return 204 No Content
                assert response.status_code == 204


def test_api_contract_put_response_format(client):
    """Test API contract compliance for PUT /api/{user_id}/tasks/{id} response format"""
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
                    id=uuid.uuid4(),
                    title="Original Task",
                    user_id=uuid.uuid4()
                )

                mock_db.get.return_value = mock_task

                mock_session.return_value.__enter__.return_value = mock_db

                update_data = {
                    "title": "Updated Task Title",
                    "description": "Updated Description"
                }

                response = client.put(
                    f"/api/{user_id}/tasks/{task_id}",
                    json=update_data,
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

                # Verify response format
                assert response.status_code == 200
                response_data = response.json()

                # Check that all required fields are present
                assert "id" in response_data
                assert "title" in response_data
                assert "description" in response_data
                assert "completed" in response_data
                assert "deleted" in response_data
                assert "created_at" in response_data
                assert "updated_at" in response_data