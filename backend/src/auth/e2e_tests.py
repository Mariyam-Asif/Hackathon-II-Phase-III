"""
End-to-end tests for all Better Auth user scenarios.
Tests the complete flow from registration to task management.
"""
import asyncio
import requests
import json
import uuid
from sqlmodel import Session, create_engine, select
from backend.src.models.user_model import User
from backend.src.models.task_model import Task
from backend.src.database.database import get_db_uri, create_db_and_tables
from backend.src.services.user_service import UserService
from backend.src.auth.jwt_utils import create_access_token
import pytest
import time


def test_user_registration_to_task_management():
    """
    End-to-end test: User registers, logs in, creates tasks, and manages them.
    """
    print("Running end-to-end test: User registration to task management...")

    # Create a test database session
    engine = create_engine(get_db_uri())
    create_db_and_tables()

    with Session(engine) as session:
        user_service = UserService(session)

        # Clean up any existing test user
        test_email = f"e2e_test_{uuid.uuid4()}@example.com"
        test_username = f"e2e_tester_{uuid.uuid4()}"
        test_password = "securepassword123"

        print("\n1. Testing user registration...")
        # Register a new user
        new_user = user_service.create_user(
            email=test_email,
            username=test_username,
            password=test_password
        )

        assert new_user.email == test_email
        assert new_user.username == test_username
        print(f"   ✓ User registered: {new_user.email}")

        print("\n2. Testing JWT token creation for registered user...")
        # Generate JWT token for the user
        token_data = {"sub": str(new_user.id), "email": new_user.email, "username": new_user.username}
        access_token = create_access_token(token_data)

        # Verify the token is valid
        from backend.src.auth.jwt_utils import verify_better_auth_token
        validated_token = verify_better_auth_token(access_token)
        assert validated_token is not None
        assert validated_token.user_id == str(new_user.id)
        print(f"   ✓ JWT token created and validated for user")

        print("\n3. Testing task creation for user...")
        # Create tasks for the user
        task_titles = ["E2E Test Task 1", "E2E Test Task 2", "E2E Test Task 3"]

        created_tasks = []
        for i, title in enumerate(task_titles):
            task = Task(
                title=title,
                description=f"Task {i+1} created during end-to-end test",
                user_id=new_user.id
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            created_tasks.append(task)

        print(f"   ✓ Created {len(created_tasks)} tasks for user")

        print("\n4. Testing task retrieval for user...")
        # Retrieve tasks for the user
        user_tasks = session.exec(select(Task).where(Task.user_id == new_user.id)).all()
        assert len(user_tasks) == 3
        assert all(task.user_id == new_user.id for task in user_tasks)
        print(f"   ✓ Retrieved {len(user_tasks)} tasks for user")

        print("\n5. Testing task update...")
        # Update a task
        task_to_update = created_tasks[0]
        original_title = task_to_update.title
        new_title = f"Updated - {original_title}"

        task_to_update.title = new_title
        task_to_update.completed = True
        session.add(task_to_update)
        session.commit()

        # Verify update
        updated_task = session.get(Task, task_to_update.id)
        assert updated_task.title == new_title
        assert updated_task.completed is True
        print(f"   ✓ Task updated successfully")

        print("\n6. Testing user access validation...")
        # Test that access validation works correctly
        from backend.src.api.deps import verify_user_access

        # This should work - same user ID
        try:
            result = verify_user_access(str(new_user.id), str(new_user.id))
            assert result == str(new_user.id)
            print(f"   ✓ Access validation successful for same user")
        except Exception as e:
            print(f"   ✗ Access validation failed: {e}")
            return False

        # Test with another user (should fail in real API scenario)
        print("\n7. Testing user isolation...")
        # Create another user to test isolation
        test_email2 = f"e2e_test2_{uuid.uuid4()}@example.com"
        test_username2 = f"e2e_tester2_{uuid.uuid4()}"
        test_password2 = "securepassword1234"

        user2 = user_service.create_user(
            email=test_email2,
            username=test_username2,
            password=test_password2
        )

        # Generate token for user2
        token_data2 = {"sub": str(user2.id)}
        token2 = create_access_token(token_data2)

        # In a real API scenario, trying to access user1's tasks with user2's token would fail
        # Here we test the validation logic
        from backend.src.exceptions.auth_exceptions import UserMismatchException
        try:
            verify_user_access(str(new_user.id), str(user2.id))
            print(f"   ✗ User isolation failed - user2 accessed user1's data")
            return False
        except UserMismatchException:
            print(f"   ✓ User isolation working - user2 correctly denied access to user1's data")

        print("\n8. Testing token validation...")
        # Test token validation with various scenarios
        # Valid token should work
        valid_check = verify_better_auth_token(access_token)
        assert valid_check is not None
        print(f"   ✓ Valid token validation successful")

        # Expired token should fail
        from datetime import timedelta
        expired_token = create_access_token(
            {"sub": str(new_user.id)},
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )
        expired_check = verify_better_auth_token(expired_token)
        assert expired_check is None
        print(f"   ✓ Expired token correctly rejected")

        print(f"\n✓ All end-to-end tests passed!")
        return True


def test_authentication_edge_cases():
    """
    End-to-end test: Authentication edge cases and error handling.
    """
    print("\nRunning end-to-end test: Authentication edge cases...")

    engine = create_engine(get_db_uri())
    create_db_and_tables()

    with Session(engine) as session:
        user_service = UserService(session)

        print("\n1. Testing registration with existing email...")
        # Clean up any existing test user
        test_email = f"edge_test_{uuid.uuid4()}@example.com"
        test_username = f"edge_tester_{uuid.uuid4()}"
        test_password = "securepassword123"

        # Register first user
        first_user = user_service.create_user(
            email=test_email,
            username=test_username,
            password=test_password
        )

        # Try to register with same email (should fail)
        try:
            duplicate_user = user_service.create_user(
                email=test_email,  # Same email as first user
                username=f"duplicate_{test_username}",
                password="differentpassword123"
            )
            print(f"   ✗ Duplicate email registration should have failed")
            return False
        except Exception:
            # This is expected behavior - user already exists
            print(f"   ✓ Duplicate email registration correctly prevented")

        print("\n2. Testing login with wrong password...")
        # Try to authenticate with wrong password
        wrong_auth = user_service.authenticate_user(test_email, "wrongpassword")
        assert wrong_auth is None
        print(f"   ✓ Wrong password correctly rejected")

        print("\n3. Testing login with non-existent user...")
        # Try to authenticate with non-existent user
        non_existent_auth = user_service.authenticate_user("nonexistent@example.com", "password")
        assert non_existent_auth is None
        print(f"   ✓ Non-existent user login correctly rejected")

        print("\n4. Testing token with non-existent user ID...")
        # Create a token with a fake user ID
        fake_user_id = str(uuid.uuid4())
        fake_token_data = {"sub": fake_user_id}
        fake_token = create_access_token(fake_token_data)

        # The token itself should be valid, but if we had to look up the user in the DB for authorization,
        # it would fail (this is handled in real API calls)
        token_validation = verify_better_auth_token(fake_token)
        assert token_validation is not None
        assert token_validation.user_id == fake_user_id
        print(f"   ✓ Token with non-existent user ID validates but user lookup would fail")

        print(f"\n✓ All edge case tests passed!")
        return True


def test_complete_workflow_simulation():
    """
    End-to-end test: Simulate a complete user workflow.
    """
    print("\nRunning end-to-end test: Complete user workflow simulation...")

    engine = create_engine(get_db_uri())
    create_db_and_tables()

    with Session(engine) as session:
        user_service = UserService(session)

        # Create a user
        test_email = f"workflow_test_{uuid.uuid4()}@example.com"
        test_username = f"workflow_tester_{uuid.uuid4()}"
        test_password = "securepassword123"

        print("\n1. User registration...")
        user = user_service.create_user(
            email=test_email,
            username=test_username,
            password=test_password
        )
        assert user is not None
        print(f"   ✓ User registered")

        print("\n2. User authentication...")
        authenticated_user = user_service.authenticate_user(test_email, test_password)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        print(f"   ✓ User authenticated")

        print("\n3. JWT token generation...")
        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)
        token_validation = verify_better_auth_token(access_token)
        assert token_validation is not None
        print(f"   ✓ JWT token generated and validated")

        print("\n4. Task management operations...")
        # Create multiple tasks
        tasks_data = [
            {"title": "Task 1", "description": "First task"},
            {"title": "Task 2", "description": "Second task"},
            {"title": "Task 3", "description": "Third task"}
        ]

        created_tasks = []
        for task_data in tasks_data:
            task = Task(
                title=task_data["title"],
                description=task_data["description"],
                user_id=user.id
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            created_tasks.append(task)

        assert len(created_tasks) == 3
        print(f"   ✓ Created {len(created_tasks)} tasks")

        # Update a task
        task_to_update = created_tasks[1]
        task_to_update.title = "Updated Task 2"
        task_to_update.completed = True
        session.add(task_to_update)
        session.commit()

        # Verify update
        updated_task = session.get(Task, task_to_update.id)
        assert updated_task.title == "Updated Task 2"
        assert updated_task.completed is True
        print(f"   ✓ Task updated")

        # Retrieve all tasks for user
        user_tasks = session.exec(select(Task).where(Task.user_id == user.id)).all()
        assert len(user_tasks) == 3
        print(f"   ✓ Retrieved all tasks for user")

        # Mark another task as complete
        task_to_complete = created_tasks[0]
        task_to_complete.completed = True
        session.add(task_to_complete)
        session.commit()

        # Verify completion
        completed_task = session.get(Task, task_to_complete.id)
        assert completed_task.completed is True
        print(f"   ✓ Task marked as complete")

        print(f"\n✓ Complete workflow simulation passed!")
        return True


def run_all_e2e_tests():
    """
    Run all end-to-end tests.
    """
    print("Running end-to-end tests for Better Auth integration...\n")

    tests = [
        ("User registration to task management", test_user_registration_to_task_management),
        ("Authentication edge cases", test_authentication_edge_cases),
        ("Complete workflow simulation", test_complete_workflow_simulation),
    ]

    all_passed = True
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = test_func()
            if result:
                print(f"✓ {test_name} passed\n")
            else:
                print(f"✗ {test_name} failed\n")
                all_passed = False
        except Exception as e:
            print(f"✗ {test_name} raised exception: {str(e)}\n")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    success = run_all_e2e_tests()

    if success:
        print("🎉 All end-to-end tests passed!")
    else:
        print("❌ Some end-to-end tests failed!")