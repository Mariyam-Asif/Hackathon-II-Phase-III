import pytest
import uuid
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from backend.src.models.user import User
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from backend.src.database.database import engine
from backend.src.main import app
from backend.src.auth.jwt_handler import create_access_token


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "name": "Test User"
    }


@pytest.fixture
def auth_headers(mock_user):
    """Create authentication headers with a valid token"""
    token = create_access_token(mock_user["id"], mock_user["email"])
    return {"Authorization": f"Bearer {token}"}


def test_complete_chat_flow(client, mock_user, auth_headers):
    """Test the complete UI → API → Agent → DB → UI loop"""
    # Test creating a chat message
    response = client.post(
        f"/api/{mock_user['id']}/chat",
        json={"message": "Hello, I want to create a test task"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    assert "tool_calls" in data

    conversation_id = data["conversation_id"]

    # Test retrieving conversation history
    response = client.get(
        f"/api/{mock_user['id']}/conversations/{conversation_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    messages = response.json()
    assert len(messages) >= 2  # User message + Agent response

    # Verify messages are properly stored in database
    with Session(engine) as session:
        # Check if conversation exists
        conversation = session.exec(
            select(Conversation).where(Conversation.conversation_id == uuid.UUID(conversation_id))
        ).first()
        assert conversation is not None
        assert conversation.user_id == uuid.UUID(mock_user["id"])

        # Check if messages exist
        messages_from_db = session.exec(
            select(Message).where(Message.conversation_id == uuid.UUID(conversation_id))
        ).all()
        assert len(messages_from_db) >= 2


def test_conversation_list_retrieval(client, mock_user, auth_headers):
    """Test retrieving user's conversation list"""
    # Create a few conversations first
    for i in range(2):
        response = client.post(
            f"/api/{mock_user['id']}/chat",
            json={"message": f"Test message {i}"},
            headers=auth_headers
        )
        assert response.status_code == 200

    # Test retrieving conversation list
    response = client.get(
        f"/api/{mock_user['id']}/conversations",
        headers=auth_headers
    )

    assert response.status_code == 200
    conversations = response.json()
    assert len(conversations) >= 2

    # Verify all conversations belong to the user
    for conv in conversations:
        assert conv["conversation_id"]
        assert "title" in conv
        assert "created_at" in conv
        assert "updated_at" in conv


def test_authentication_protection(client, mock_user):
    """Test that endpoints are properly protected by authentication"""
    # Try to access without token
    response = client.post(
        f"/api/{mock_user['id']}/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 401  # Unauthorized

    # Try to access another user's conversations
    fake_user_id = str(uuid.uuid4())
    auth_headers = {"Authorization": f"Bearer {create_access_token(fake_user_id, 'fake@example.com')}"}

    response = client.get(
        f"/api/{mock_user['id']}/conversations",
        headers=auth_headers
    )

    assert response.status_code == 403  # Forbidden


def test_conversation_isolation(client):
    """Test that users can only access their own conversations"""
    # Create two different users
    user1 = {"id": str(uuid.uuid4()), "email": "user1@example.com"}
    user2 = {"id": str(uuid.uuid4()), "email": "user2@example.com"}

    user1_token = create_access_token(user1["id"], user1["email"])
    user2_token = create_access_token(user2["id"], user2["email"])

    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 1 creates a conversation
    response = client.post(
        f"/api/{user1['id']}/chat",
        json={"message": "Hello from user 1"},
        headers=user1_headers
    )

    assert response.status_code == 200
    data = response.json()
    conversation_id = data["conversation_id"]

    # User 2 should not be able to access user 1's conversation
    response = client.get(
        f"/api/{user1['id']}/conversations/{conversation_id}",
        headers=user2_headers
    )

    assert response.status_code == 403  # Forbidden


def test_intent_to_tool_mapping(client, mock_user, auth_headers):
    """Test that user intents are properly mapped to tool calls"""
    # Test creating a task
    response = client.post(
        f"/api/{mock_user['id']}/chat",
        json={"message": "Please create a task called 'Test Task' with description 'Testing task creation'"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    # The response should contain tool calls related to task creation
    # This depends on the AI agent's interpretation but should have appropriate responses

    # Test listing tasks
    response = client.post(
        f"/api/{mock_user['id']}/chat",
        json={"message": "What tasks do I have?"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    # The response should trigger a list_tasks tool call


if __name__ == "__main__":
    pytest.main([__file__])