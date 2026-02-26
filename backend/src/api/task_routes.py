from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from sqlalchemy import func
from typing import List
from datetime import datetime
import uuid
from models.task import Task
from models.user import User
from schemas.task_schemas import (
    TaskCreate, TaskUpdate, TaskCompleteUpdate, TaskResponse, TaskListResponse
)
from schemas.response_schemas import ErrorResponse
from database.session import get_session
from auth.auth_handler import get_current_user
from api.deps import verify_user_access
from api.auth_deps import verify_user_access as new_verify_user_access
from exceptions.auth_exceptions import UserMismatchException

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: str,
    task_create: TaskCreate,
    db: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new task for the specified user
    """
    try:
        # Verify user access
        if str(current_user_id) != user_id:
            raise UserMismatchException(
                detail=f"Access denied: token user ID ({current_user_id}) does not match requested user ID ({user_id})"
            )

        # Convert user_id to UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid user ID format", "code": "INVALID_USER_ID_FORMAT"}
            )

        # Create task instance with explicit defaults
        now = datetime.utcnow()
        task = Task(
            id=uuid.uuid4(),
            title=task_create.title,
            description=task_create.description or "",
            priority=(task_create.priority or 'medium').lower(),
            status='pending',
            user_id=user_uuid,
            deleted=False,
            completed=False,
            created_at=now,
            updated_at=now
        )

        logger.info(f"Attempting to create task: {task.title} for user {user_id}")
        
        # Add to database
        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Successfully created task {task.id} for user {user_id}")
        return task
    except UserMismatchException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/tasks", response_model=TaskListResponse)
def get_tasks(
    user_id: str,
    db: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    completed: bool = Query(None)
):
    """
    Retrieve all tasks for the specified user
    """
    try:
        # Verify user access
        if str(current_user_id) != user_id:
            raise UserMismatchException(
                detail=f"Access denied: token user ID ({current_user_id}) does not match requested user ID ({user_id})"
            )

        # Convert user_id to UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid user ID format", "code": "INVALID_USER_ID_FORMAT"}
            )

        # Build query with filters (always filter out deleted tasks)
        query = select(Task).where(Task.user_id == user_uuid, Task.deleted == False)

        if completed is not None:
            if completed:
                query = query.where(Task.status == "completed")
            else:
                query = query.where(Task.status != "completed")

        # Count total
        count_query = select(func.count(Task.id)).where(Task.user_id == user_uuid, Task.deleted == False)
        if completed is not None:
            if completed:
                count_query = count_query.where(Task.status == "completed")
            else:
                count_query = count_query.where(Task.status != "completed")
        
        total = db.exec(count_query).one()

        # Apply pagination
        query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
        tasks = db.exec(query).all()

        return TaskListResponse(
            tasks=tasks,
            total=total,
            limit=limit,
            offset=offset
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tasks for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: str,
    task_id: str,
    db: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Retrieve a specific task for the specified user
    """
    try:
        # Verify user access
        if str(current_user_id) != user_id:
            raise UserMismatchException(
                detail=f"Access denied: token user ID ({current_user_id}) does not match requested user ID ({user_id})"
            )

        # Convert IDs to UUIDs
        try:
            user_uuid = uuid.UUID(user_id)
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid ID format", "code": "INVALID_ID_FORMAT"}
            )

        # Get task from database
        task = db.get(Task, task_uuid)

        if not task or task.deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found", "code": "TASK_NOT_FOUND"}
            )

        # Verify task belongs to user
        if task.user_id != user_uuid:
            raise UserMismatchException(
                detail="Not authorized to access this task"
            )

        return task
    except (HTTPException, UserMismatchException):
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Update a specific task for the specified user
    """
    try:
        # Verify user access
        if str(current_user_id) != user_id:
            raise UserMismatchException(
                detail=f"Access denied: token user ID ({current_user_id}) does not match requested user ID ({user_id})"
            )

        # Convert IDs to UUIDs
        try:
            user_uuid = uuid.UUID(user_id)
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid ID format", "code": "INVALID_ID_FORMAT"}
            )

        # Get task from database
        task = db.get(Task, task_uuid)

        if not task or task.deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found", "code": "TASK_NOT_FOUND"}
            )

        # Verify task belongs to user
        if task.user_id != user_uuid:
            raise UserMismatchException(
                detail="Not authorized to update this task"
            )

        # Update task fields
        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()

        # Commit changes
        db.add(task)
        db.commit()
        db.refresh(task)

        return task
    except (HTTPException, UserMismatchException):
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def update_task_completion(
    user_id: str,
    task_id: str,
    task_complete_update: TaskCompleteUpdate,
    db: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Toggle or set the completion status of a specific task for the specified user
    """
    try:
        # Verify user access
        if str(current_user_id) != user_id:
            raise UserMismatchException(
                detail=f"Access denied: token user ID ({current_user_id}) does not match requested user ID ({user_id})"
            )

        # Convert IDs to UUIDs
        try:
            user_uuid = uuid.UUID(user_id)
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid ID format", "code": "INVALID_ID_FORMAT"}
            )

        # Get task from database
        task = db.get(Task, task_uuid)

        if not task or task.deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found", "code": "TASK_NOT_FOUND"}
            )

        # Verify task belongs to user
        if task.user_id != user_uuid:
            raise UserMismatchException(
                detail="Not authorized to update this task"
            )

        # Update completion status
        if task_complete_update.completed is not None:
            if task_complete_update.completed:
                task.status = "completed"
                task.completed = True
                task.completed_at = datetime.utcnow()
            else:
                task.status = "pending"
                task.completed = False
                task.completed_at = None

        task.updated_at = datetime.utcnow()

        # Commit changes
        db.add(task)
        db.commit()
        db.refresh(task)

        return task
    except (HTTPException, UserMismatchException):
        raise
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: str,
    task_id: str,
    db: Session = Depends(get_session),
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete a specific task for the specified user (Soft delete)
    """
    try:
        # Verify user access
        if str(current_user_id) != user_id:
            raise UserMismatchException(
                detail=f"Access denied: token user ID ({current_user_id}) does not match requested user ID ({user_id})"
            )

        # Convert IDs to UUIDs
        try:
            user_uuid = uuid.UUID(user_id)
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid ID format", "code": "INVALID_ID_FORMAT"}
            )

        # Get task from database
        task = db.get(Task, task_uuid)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found", "code": "TASK_NOT_FOUND"}
            )

        # Verify task belongs to user
        if task.user_id != user_uuid:
            raise UserMismatchException(
                detail="Not authorized to delete this task"
            )

        # Perform soft delete
        task.deleted = True
        task.updated_at = datetime.utcnow()
        db.add(task)
        db.commit()

        return
    except (HTTPException, UserMismatchException):
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )