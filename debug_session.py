#!/usr/bin/env python3
"""
Debug script to check session transaction handling
"""
import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlmodel import Session
from backend.src.models.user_model import User
from backend.src.models.task_model import Task

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

def debug_session_handling():
    """Debug session handling to understand the issue"""
    print("Debugging session handling...")

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
            from sqlalchemy import delete

            # Clean up test tasks first (due to foreign key constraint)
            stmt = delete(Task).where(Task.title.contains("Debug Test Task"))
            session.exec(stmt)

            # Clean up test users
            stmt = delete(User).where(User.email.like("%debug%"))
            session.exec(stmt)

            session.commit()  # Commit deletions before creating new records

            # Create a test user
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            test_user = User(
                email=f"debuguser_{timestamp}@example.com",
                username=f"debuguser_{timestamp}",
            )

            print(f"About to add user with email: {test_user.email}")
            session.add(test_user)
            print("Added user to session, about to commit")
            session.commit()
            print("Committed user, about to refresh")
            session.refresh(test_user)
            print(f"Refreshed user, ID: {test_user.id}")

            # Try to query the user using different methods
            print(f"\nTesting different ways to retrieve user with ID: {test_user.id}")

            # Method 1: session.get
            user1 = session.get(User, test_user.id)
            print(f"Method 1 (session.get): {user1.email if user1 else 'None'}")

            # Method 2: select query
            user2 = session.exec(select(User).where(User.id == test_user.id)).first()
            print(f"Method 2 (select query): {user2.email if user2 else 'None'}")

            # Method 3: direct query
            user3 = session.exec(select(User).where(User.email == test_user.email)).first()
            print(f"Method 3 (email query): {user3.email if user3 else 'None'}")

            # Let's also test with a new session to see if the issue is session-related
            print("\nTesting in a new session...")
            with Session(engine) as new_session:
                user_new = new_session.get(User, test_user.id)
                print(f"New session retrieval: {user_new.email if user_new else 'None'}")

                # Query all users to see what's available
                all_users = new_session.exec(select(User).where(User.email.like('%debug%'))).all()
                print(f"All debug users in new session: {len(all_users)}")
                for u in all_users:
                    print(f"  - {u.email} (ID: {u.id})")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_session_handling()