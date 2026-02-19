from typing import Dict, Any, List
from pydantic import BaseModel
from database.crud import get_tasks_by_user_id
from models.task import TaskRead
from sqlmodel import Session
from database.session import get_session
import uuid


class ListTasksInput(BaseModel):
    user_id: str  # Will be converted to UUID


async def list_tasks_tool(input_data: ListTasksInput) -> Dict[str, Any]:
    """
    MCP tool to list all tasks for a user.

    Args:
        input_data: Contains user_id

    Returns:
        Dictionary with success status and list of tasks
    """
    try:
        # Convert user_id string to UUID
        user_uuid = uuid.UUID(input_data.user_id)

        # Get database session and fetch tasks
        for session in get_session():
            session: Session
            tasks = get_tasks_by_user_id(session, user_uuid)

            # Convert tasks to readable format
            tasks_list = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                tasks_list.append(task_dict)

            return {
                "success": True,
                "tasks_count": len(tasks_list),
                "tasks": tasks_list,
                "message": f"Found {len(tasks_list)} tasks for user."
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
            "error": f"Failed to list tasks: {str(e)}"
        }