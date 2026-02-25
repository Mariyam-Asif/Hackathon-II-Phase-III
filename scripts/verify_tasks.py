import os
import sys
import uuid
from sqlmodel import Session, SQLModel, create_engine, select

# Add src to path
sys.path.insert(0, os.path.abspath("backend/src"))

# Import all models to resolve relationships
from models.user import User
from models.task import Task
from models.conversation import Conversation
from models.message import Message

# Use SQLite for local verification
engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

def verify_tasks():
    print("Verifying Task CRUD logic...")
    with Session(engine) as session:
        # 1. Create a user
        user = User(
            email="tasktest@example.com",
            name="Task Tester",
            hashed_password="fakehash"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"User created: {user.id}")

        # 2. Create a task
        new_task = Task(
            title="Verify Task",
            description="Testing task creation",
            priority="high",
            user_id=user.id
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        print(f"Task created: {new_task.id}, status: {new_task.status}")

        assert new_task.user_id == user.id
        assert new_task.status == "pending"

        # 3. List tasks
        statement = select(Task).where(Task.user_id == user.id)
        tasks = session.exec(statement).all()
        print(f"Total tasks for user: {len(tasks)}")
        assert len(tasks) == 1

if __name__ == "__main__":
    try:
        verify_tasks()
        print("\nTASK LOGIC VERIFIED!")
    except Exception as e:
        print(f"\nTASK VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
