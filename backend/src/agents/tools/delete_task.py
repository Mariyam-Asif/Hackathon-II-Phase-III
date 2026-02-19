from typing import Dict, Any
from pydantic import BaseModel
from database.crud import delete_task
from sqlmodel import Session
from database.session import get_session
import uuid


class DeleteTaskInput(BaseModel):
    task_id: str  # Will be converted to UUID
    user_id: str  # Will be converted to UUID


async def delete_task_tool(input_data: DeleteTaskInput) -> Dict[str, Any]:
    """
    MCP tool to delete a task for a user.

    Args:
        input_data: Contains task_id and user_id

    Returns:
        Dictionary with success status and task information
    """
    try:
        # Convert IDs to UUID
        task_uuid = uuid.UUID(input_data.task_id)
        user_uuid = uuid.UUID(input_data.user_id)

        # Get database session and delete task
        for session in get_session():
            session: Session
            success = delete_task(session, task_uuid, user_uuid)

            if success:
                return {
                    "success": True,
                    "task_id": input_data.task_id,
                    "message": "Task has been deleted successfully."
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found or user does not have permission to delete this task."
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
            "error": f"Failed to delete task: {str(e)}"
        }