"""
Comprehensive integration tests for the complete Better Auth flow.
Tests the entire authentication and authorization workflow.
"""
import asyncio
from sqlmodel import Session, create_engine, select
from backend.src.models.user_model import User
from backend.src.models.task_model import Task
from backend.src.services.user_service import UserService
from backend.src.auth.jwt_utils import create_access_token, verify_better_auth_token
from backend.src.database.database import get_db_uri, create_db_and_tables
from backend.src.api.deps import verify_user_access
from backend.src.exceptions.auth_exceptions import UserMismatchException
from backend.src.auth.token_manager import TokenManager
from backend.src.auth.rate_limiter import AuthRateLimiter
import pytest
import uuid


def test_complete_auth_flow():
    print("Testing complete Better Auth integration flow...")

    # Create a test database session
    engine = create_engine(get_db_uri())
    create_db_and_tables()  # Ensure tables exist

    with Session(engine) as session:
        # Create user service
        user_service = UserService(session)

        print("\n1. Testing user registration...")
        # Create test users
        test_email = "integration_test@example.com"
        test_username = "integration_tester"
        test_password = "securepassword123"

        # Clean up any existing test user
        existing_user = user_service.get_user_by_email(test_email)
        if existing_user:
            session.delete(existing_user)
            session.commit()

        # Register a new user
        new_user = user_service.create_user(
            email=test_email,
            username=test_username,
            password=test_password
        )

        assert new_user.email == test_email
        assert new_user.username == test_username
        print(f"   ✓ User registered: {new_user.email}")

        print("\n2. Testing user authentication...")
        # Authenticate the user
        authenticated_user = user_service.authenticate_user(test_email, test_password)
        assert authenticated_user is not None
        assert authenticated_user.id == new_user.id
        print(f"   ✓ User authenticated successfully")

        # Test failed authentication
        failed_auth = user_service.authenticate_user(test_email, "wrongpassword")
        assert failed_auth is None
        print(f"   ✓ Failed authentication correctly rejected")

        print("\n3. Testing JWT token generation and validation...")
        # Generate a JWT token
        token_data = {"sub": str(new_user.id), "email": new_user.email, "username": new_user.username}
        access_token = create_access_token(token_data)

        # Validate the token
        validated_token = verify_better_auth_token(access_token)
        assert validated_token is not None
        assert validated_token.user_id == str(new_user.id)
        print(f"   ✓ JWT token generated and validated")

        print("\n4. Testing user access verification...")
        # Test access verification
        try:
            # This should work - same user ID
            result = verify_user_access(str(new_user.id), str(new_user.id))
            assert result == str(new_user.id)
            print(f"   ✓ Access verification successful for same user")
        except Exception as e:
            print(f"   ✗ Access verification failed: {e}")
            return False

        print("\n5. Testing user isolation...")
        # Create another user to test isolation
        test_email2 = "integration_test2@example.com"
        test_username2 = "integration_tester2"
        test_password2 = "securepassword1234"

        user2 = user_service.create_user(
            email=test_email2,
            username=test_username2,
            password=test_password2
        )

        # Generate token for user2
        token_data2 = {"sub": str(user2.id)}
        token2 = create_access_token(token_data2)

        # Try to access user1's data with user2's token (should fail)
        try:
            from backend.src.api.deps import verify_user_access
            verify_user_access(str(new_user.id), str(user2.id))
            print(f"   ✗ User isolation failed - user2 accessed user1's data")
            return False
        except UserMismatchException:
            print(f"   ✓ User isolation working - user2 correctly denied access to user1's data")

        print("\n6. Testing token manager functionality...")
        # Test token refresh functionality
        token_manager = TokenManager()

        # Create a refresh token
        refresh_token = token_manager.create_refresh_token(str(new_user.id))
        assert refresh_token is not None

        # Validate refresh token
        is_valid = token_manager.validate_refresh_token(refresh_token)
        assert is_valid
        print(f"   ✓ Refresh token created and validated")

        # Use refresh token to get new access token
        new_access_token = token_manager.refresh_access_token(refresh_token)
        assert new_access_token is not None
        print(f"   ✓ New access token obtained via refresh")

        print("\n7. Testing rate limiting...")
        # Test rate limiting
        rate_limiter = AuthRateLimiter()

        # Test login rate limiting
        ip_address = "192.168.1.100"
        is_allowed = rate_limiter.is_login_allowed(ip_address)
        assert is_allowed  # Should be allowed initially
        print(f"   ✓ Rate limiting initialized")

        print("\n8. Testing task creation and access...")
        # Create a task for the user
        task = Task(
            title="Integration test task",
            description="Task created during integration test",
            user_id=new_user.id
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.user_id == new_user.id
        print(f"   ✓ Task created for user")

        # Verify the task belongs to the correct user
        user_tasks = session.exec(select(Task).where(Task.user_id == new_user.id)).all()
        assert len(user_tasks) == 1
        assert user_tasks[0].title == "Integration test task"
        print(f"   ✓ Task correctly associated with user")

        print(f"\n✓ All integration tests passed!")
        return True


def test_error_conditions():
    print("\nTesting error conditions...")

    engine = create_engine(get_db_uri())
    create_db_and_tables()

    with Session(engine) as session:
        user_service = UserService(session)

        print("\n1. Testing invalid token scenarios...")
        # Test with invalid tokens
        invalid_tokens = ["", "invalid.token", "not-a-jwt"]

        for token in invalid_tokens:
            result = verify_better_auth_token(token)
            assert result is None, f"Token '{token}' should be invalid"
        print(f"   ✓ Invalid tokens correctly rejected")

        print("\n2. Testing user validation edge cases...")
        # Test with non-existent user
        fake_user_id = str(uuid.uuid4())
        fake_token_data = {"sub": fake_user_id}
        fake_token = create_access_token(fake_token_data)

        # Token validates but user doesn't exist in DB (this is okay for token validation)
        token_result = verify_better_auth_token(fake_token)
        assert token_result is not None
        assert token_result.user_id == fake_user_id
        print(f"   ✓ Valid token with non-existent user handled correctly")

        print("\n3. Testing expired tokens...")
        # Test with expired token
        from datetime import timedelta
        expired_token = create_access_token(
            {"sub": str(uuid.uuid4())},
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )

        expired_result = verify_better_auth_token(expired_token)
        assert expired_result is None, "Expired token should be rejected"
        print(f"   ✓ Expired token correctly rejected")

        print(f"\n✓ All error condition tests passed!")
        return True


def run_all_integration_tests():
    print("Running comprehensive integration tests for Better Auth...\n")

    test1_result = test_complete_auth_flow()
    test2_result = test_error_conditions()

    return test1_result and test2_result


if __name__ == "__main__":
    success = run_all_integration_tests()

    if success:
        print(f"\n🎉 All integration tests passed!")
    else:
        print(f"\n❌ Some integration tests failed!")