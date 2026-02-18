from typing import Dict, Any
from pydantic import BaseModel
from ...database.crud import complete_task
from sqlmodel import Session
from ...database.session import get_session
import uuid


class CompleteTaskInput(BaseModel):
    task_id: str  # Will be converted to UUID
    user_id: str  # Will be converted to UUID


async def complete_task_tool(input_data: CompleteTaskInput) -> Dict[str, Any]:
    """
    MCP tool to mark a task as completed for a user.

    Args:
        input_data: Contains task_id and user_id

    Returns:
        Dictionary with success status and task information
    """
    try:
        # Convert IDs to UUID
        task_uuid = uuid.UUID(input_data.task_id)
        user_uuid = uuid.UUID(input_data.user_id)

        # Get database session and complete task
        for session in get_session():
            session: Session
            completed_task = complete_task(session, task_uuid, user_uuid)

            if completed_task:
                return {
                    "success": True,
                    "task_id": str(completed_task.id),
                    "title": completed_task.title,
                    "message": f"Task '{completed_task.title}' has been marked as completed."
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found or user does not have permission to modify this task."
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
            "error": f"Failed to complete task: {str(e)}"
        }