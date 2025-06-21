from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..application.dtos import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
    TasksWithStatsResponse
)
from ..application.use_cases.task import TaskUseCases
from ..dependencies import get_db, get_task_use_cases
from ..domain.exceptions import (
    TaskListNotFoundException,
    TaskNotFoundException,
    TaskTitleAlreadyExistsException,
    InvalidDueDateException,
    ValidationError
)
from ..domain.models.enums import TaskStatus, TaskPriority

router = APIRouter(prefix="/task-lists", tags=["Tasks"])


@router.post("/{task_list_id}/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_list_id: int,
    request: TaskCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new task in a task list.
    
    **Request Body Fields:**
    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional, max 1000 characters)
    - **status**: Task status (optional, default: pending)
        - Available values: pending, in_progress, completed, cancelled
    - **priority**: Task priority (optional, default: medium)
        - Available values: low, medium, high, urgent
    - **due_date**: Task due date (optional, ISO 8601 format)
    
    **Business Rules:**
    - Task title must be unique within the task list
    - Due date cannot be in the past
    - Task list must exist
    """
    try:
        use_cases = get_task_use_cases(db)
        task_entity = use_cases.create_task(
            task_list_id=task_list_id,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            due_date=request.due_date
        )
        return TaskResponse.from_entity(task_entity)
    
    except TaskListNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TaskTitleAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidDueDateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{task_list_id}/tasks/", response_model=TasksWithStatsResponse)
def get_tasks_by_list(
    task_list_id: int,
    status: Optional[TaskStatus] = Query(
        None, 
        description="Filter by task status. Available values: pending, in_progress, completed, cancelled"
    ),
    priority: Optional[TaskPriority] = Query(
        None, 
        description="Filter by task priority. Available values: low, medium, high, urgent"
    ),
    db: Session = Depends(get_db)
):
    """
    Get all tasks for a task list with optional filters and completion statistics.
    
    This endpoint returns:
    - Task list information (ID, name, description)
    - Total number of tasks in the list
    - Completion percentage (based on all tasks in the list)
    - Filtered tasks based on the provided query parameters
    
    **Query Parameters:**
    - **status**: Filter tasks by status (optional)
        - `pending`: Tasks that haven't been started
        - `in_progress`: Tasks currently being worked on
        - `completed`: Tasks that have been finished
        - `cancelled`: Tasks that have been cancelled
    
    - **priority**: Filter tasks by priority level (optional)
        - `low`: Low priority tasks
        - `medium`: Medium priority tasks  
        - `high`: High priority tasks
        - `urgent`: Urgent priority tasks
    
    **Note:** The completion percentage is calculated based on ALL tasks in the list,
    not just the filtered results.
    """
    try:
        use_cases = get_task_use_cases(db)
        result = use_cases.get_tasks_with_stats(
            task_list_id=task_list_id,
            status=status,
            priority=priority
        )
        return TasksWithStatsResponse.from_tasks_and_task_list(
            tasks=result["tasks"],
            task_list=result["task_list"],
            completion_percentage=result["completion_percentage"]
        )
    
    except TaskListNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{task_list_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_list_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get a task by ID."""
    try:
        use_cases = get_task_use_cases(db)
        task_entity = use_cases.get_task_by_id(task_id)
        
        # Verify the task belongs to the specified task list
        if task_entity.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Task {task_id} not found in task list {task_list_id}"
            )
        
        return TaskResponse.from_entity(task_entity)
    
    except TaskNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{task_list_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_list_id: int,
    task_id: int,
    request: TaskUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update a task.
    
    **Request Body Fields (all optional):**
    - **title**: Task title (1-200 characters)
    - **description**: Task description (max 1000 characters)
    - **status**: Task status
        - Available values: pending, in_progress, completed, cancelled
    - **priority**: Task priority
        - Available values: low, medium, high, urgent
    - **due_date**: Task due date (ISO 8601 format)
    
    **Business Rules:**
    - Task must exist and belong to the specified task list
    - New title must be unique within the task list (if provided)
    - Due date cannot be in the past (if provided)
    """
    try:
        use_cases = get_task_use_cases(db)
        
        # First verify the task exists and belongs to the task list
        existing_task = use_cases.get_task_by_id(task_id)
        if existing_task.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Task {task_id} not found in task list {task_list_id}"
            )
        
        task_entity = use_cases.update_task(
            task_id=task_id,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            due_date=request.due_date
        )
        return TaskResponse.from_entity(task_entity)
    
    except TaskNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TaskTitleAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidDueDateException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{task_list_id}/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_list_id: int,
    task_id: int,
    request: TaskStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update task status.
    
    **Request Body Fields:**
    - **status**: New task status (required)
        - Available values: pending, in_progress, completed, cancelled
    
    **Business Rules:**
    - Task must exist and belong to the specified task list
    """
    try:
        use_cases = get_task_use_cases(db)
        
        # First verify the task exists and belongs to the task list
        existing_task = use_cases.get_task_by_id(task_id)
        if existing_task.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Task {task_id} not found in task list {task_list_id}"
            )
        
        task_entity = use_cases.update_task_status(task_id, request.status)
        return TaskResponse.from_entity(task_entity)
    
    except TaskNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{task_list_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_list_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """Delete a task."""
    try:
        use_cases = get_task_use_cases(db)
        
        # First verify the task exists and belongs to the task list
        existing_task = use_cases.get_task_by_id(task_id)
        if existing_task.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Task {task_id} not found in task list {task_list_id}"
            )
        
        use_cases.delete_task(task_id)
    
    except TaskNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 