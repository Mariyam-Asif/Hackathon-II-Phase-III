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
    current_user: str = Depends(get_current_user)
):
    """
    Create a new task for the specified user
    """
    try:
        # Verify user access
        verify_user_access(user_id, current_user)

        # Convert user_id to UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(error="Invalid user ID format").dict()
            )

        # Create task instance
        task = Task(
            title=task_create.title,
            description=task_create.description,
            priority=task_create.priority or 'medium',
            status='pending',
            user_id=user_uuid,
            deleted=False,
            completed=False
        )

        # Add to database
        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Successfully created task {task.id} for user {user_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        # Log the full traceback for debugging
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
    current_user: str = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    completed: bool = Query(None)
):
    """
    Retrieve all tasks for the specified user
    """
    try:
        # Verify user access
        verify_user_access(user_id, current_user)

        # Convert user_id to UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(error="Invalid user ID format").dict()
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
    current_user: str = Depends(get_current_user)
):
    """
    Retrieve a specific task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user
    if task.user_id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to access this task").dict()
        )

    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Update a specific task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user
    if task.user_id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to update this task").dict()
        )

    # Update task fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)

    # Commit changes
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def update_task_completion(
    user_id: str,
    task_id: str,
    task_complete_update: TaskCompleteUpdate,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Toggle or set the completion status of a specific task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user
    if task.user_id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to update this task").dict()
        )

    # Update completion status
    if task_complete_update.completed is not None:
        if task_complete_update.completed:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
        else:
            # If setting to not completed, change status to pending
            task.status = "pending"
            task.completed_at = None

    # Commit changes
    db.add(task)
    db.commit()
    db.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: str,
    task_id: str,
    db: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Delete a specific task for the specified user
    """
    # Verify user access
    verify_user_access(user_id, current_user)

    # Convert IDs to UUIDs
    try:
        user_uuid = uuid.UUID(user_id)
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="Invalid ID format").dict()
        )

    # Get task from database
    task = db.get(Task, task_uuid)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error="Task not found").dict()
        )

    # Verify task belongs to user
    if task.user_id != user_uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(error="Not authorized to delete this task").dict()
        )

    # Perform hard delete
    db.delete(task)
    db.commit()

    return