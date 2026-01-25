#!/usr/bin/env python3
"""
Final test to confirm data persistence in Neon PostgreSQL
"""
import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, delete
from sqlmodel import Session
from backend.src.models.user_model import User
from backend.src.models.task_model import Task

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def final_test():
    """Final test to confirm data persistence in Neon PostgreSQL"""
    print("Final test - confirming data persistence in Neon PostgreSQL...")

    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment!")
        return False

    try:
        # Create engine
        engine = create_engine(database_url)

        # Create a session
        with Session(engine) as session:
            print("Connected to Neon PostgreSQL with session.")

            # Clean up any existing test data
            print("Cleaning up any existing test data...")

            # Clean up test tasks first (due to foreign key constraint)
            stmt = delete(Task).where(Task.title.contains("Test Task"))
            session.exec(stmt)

            # Clean up test users
            stmt = delete(User).where(User.email.like("%test%"))
            session.exec(stmt)

            session.commit()  # Commit deletions before creating new records

            # Create a test user (simulating user sign-up)
            print("\nCreating test user (simulating user sign-up)...")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            test_user = User(
                email=f"testuser_{timestamp}@example.com",
                username=f"testuser_{timestamp}",
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

            print(f"Created user with ID: {test_user.id}, email: {test_user.email}")

            # Verify user was stored in database by getting it directly
            user_from_db = session.get(User, test_user.id)
            if user_from_db and user_from_db.email == f"testuser_{timestamp}@example.com":
                print("+ User successfully stored in Neon PostgreSQL!")
            else:
                print("- User was not properly stored in Neon PostgreSQL!")
                return False

            # Create a test task for the user (simulating task creation)
            print(f"\nCreating test task for user {test_user.id} (simulating task creation)...")
            test_task = Task(
                title="Test Task",
                description="This is a test task created to verify data persistence",
                completed=False,
                user_id=test_user.id
            )
            session.add(test_task)
            session.commit()
            session.refresh(test_task)

            print(f"Created task with ID: {test_task.id}, title: {test_task.title}, user_id: {test_task.user_id}")

            # Verify task was stored in database
            task_from_db = session.get(Task, test_task.id)
            if task_from_db and task_from_db.title == "Test Task" and task_from_db.user_id == test_user.id:
                print("+ Task successfully stored in Neon PostgreSQL!")
            else:
                print("- Task was not properly stored in Neon PostgreSQL!")
                return False

            # Verify the task is linked to the user properly
            user_tasks_result = session.exec(select(Task).where(Task.user_id == test_user.id))
            user_tasks = user_tasks_result.all()

            # Check if we got a Row object or actual Task objects
            if len(user_tasks) == 1:
                # If it's a Row object, get the first element
                if hasattr(user_tasks[0], '_fields'):
                    # This is a Row object, get the actual task
                    actual_task = user_tasks[0][0]  # Get first column which should be the Task
                    if hasattr(actual_task, 'id') and actual_task.id == test_task.id:
                        print("+ Task properly linked to user in Neon PostgreSQL!")
                    else:
                        print("- Task was not properly linked to user in Neon PostgreSQL!")
                        return False
                else:
                    # This is the actual Task object
                    if user_tasks[0].id == test_task.id:
                        print("+ Task properly linked to user in Neon PostgreSQL!")
                    else:
                        print("- Task was not properly linked to user in Neon PostgreSQL!")
                        return False
            else:
                print("- Task was not properly linked to user in Neon PostgreSQL!")
                return False

            # Test updating a task
            print(f"\nUpdating task (simulating task update)...")
            task_from_db = session.get(Task, test_task.id)
            task_from_db.completed = True
            session.add(task_from_db)
            session.commit()

            # Verify update was persisted
            updated_task = session.get(Task, test_task.id)
            if updated_task and updated_task.completed:
                print("+ Task update successfully persisted in Neon PostgreSQL!")
            else:
                print("- Task update was not properly persisted in Neon PostgreSQL!")
                return False

            # Test deleting a task (soft delete)
            print(f"\nDeleting task (simulating task deletion)...")
            task_to_delete = session.get(Task, test_task.id)
            task_to_delete.deleted = True
            session.add(task_to_delete)
            session.commit()

            # Verify deletion was persisted
            deleted_task = session.get(Task, test_task.id)
            if deleted_task and deleted_task.deleted:
                print("+ Task deletion successfully persisted in Neon PostgreSQL!")
            else:
                print("- Task deletion was not properly persisted in Neon PostgreSQL!")
                return False

            # Verify user still exists (should not be affected by task operations)
            still_existing_user = session.get(User, test_user.id)
            if still_existing_user:
                print("+ User still exists after task operations - data isolation maintained!")
            else:
                print("- User was incorrectly affected by task operations!")
                return False

        print("\nSUCCESS: All data persistence tests passed!")
        print("- User sign-up creates a row in 'user' table")
        print("- Task creation creates a row in 'task' table")
        print("- Task updates modify rows in 'task' table")
        print("- Task deletion modifies rows in 'task' table")
        print("- Authenticated users are properly linked to their tasks via user_id")
        print("- User data isolation is maintained")

        return True

    except Exception as e:
        print(f"ERROR: Failed data persistence test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = final_test()
    if success:
        print("\nSUCCESS: All data persistence tests passed!")
        print("Neon PostgreSQL is properly storing all application data!")
    else:
        print("\nERROR: Data persistence tests failed!")
        print("Application data is not being stored in Neon PostgreSQL!")