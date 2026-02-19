from typing import Dict, Any
from pydantic import BaseModel
from database.crud import get_task_by_id, update_task
from models.task import TaskUpdate
from sqlmodel import Session
from database.session import get_session
import uuid


class UpdateTaskInput(BaseModel):
    task_id: str  # Will be converted to UUID
    user_id: str  # Will be converted to UUID
    title: str = None
    description: str = None
    status: str = None
    priority: str = None


async def update_task_tool(input_data: UpdateTaskInput) -> Dict[str, Any]:
    """
    MCP tool to update a task for a user.

    Args:
        input_data: Contains task_id, user_id, and optional fields to update

    Returns:
        Dictionary with success status and updated task information
    """
    try:
        # Convert IDs to UUID
        task_uuid = uuid.UUID(input_data.task_id)
        user_uuid = uuid.UUID(input_data.user_id)

        # Prepare update data
        task_update = TaskUpdate(
            title=input_data.title,
            description=input_data.description,
            status=input_data.status,
            priority=input_data.priority
        )

        # Get database session and update task
        for session in get_session():
            session: Session
            # First check if task exists for this user
            existing_task = get_task_by_id(session, task_uuid, user_uuid)

            if not existing_task:
                return {
                    "success": False,
                    "error": "Task not found or user does not have permission to modify this task."
                }

            updated_task = update_task(session, task_uuid, user_uuid, task_update)

            if updated_task:
                return {
                    "success": True,
                    "task_id": str(updated_task.id),
                    "title": updated_task.title,
                    "message": f"Task '{updated_task.title}' has been updated successfully."
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update task."
                }

    except ValueError as e:
        # Invalid UUID format
        return {
            "success": False,
            "error": f"Invalid task ID or user ID format: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }