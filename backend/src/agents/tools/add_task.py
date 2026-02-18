from typing import Dict, Any
from pydantic import BaseModel
from ...database.crud import create_task
from ...models.task import TaskCreate
from sqlmodel import Session
from ...database.session import get_session
import uuid


class AddTaskInput(BaseModel):
    title: str
    description: str = ""
    user_id: str  # Will be converted to UUID
    priority: str = "medium"


async def add_task_tool(input_data: AddTaskInput) -> Dict[str, Any]:
    """
    MCP tool to add a new task for a user.

    Args:
        input_data: Contains title, description, user_id, and priority

    Returns:
        Dictionary with success status and task information
    """
    try:
        # Convert user_id string to UUID
        user_uuid = uuid.UUID(input_data.user_id)

        # Create task data
        task_create = TaskCreate(
            title=input_data.title,
            description=input_data.description,
            user_id=user_uuid,
            priority=input_data.priority
        )

        # Get database session and create task
        # Since this is async, we'll use a session context
        for session in get_session():
            session: Session
            created_task = create_task(session, task_create)

            return {
                "success": True,
                "task_id": str(created_task.id),
                "title": created_task.title,
                "message": f"Task '{created_task.title}' has been added successfully."
            }

    except ValueError as e:
        # Invalid UUID format
        return {
            "success": False,
            "error": f"Invalid user ID format: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to add task: {str(e)}"
        }