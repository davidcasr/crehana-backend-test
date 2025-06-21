from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..application.dtos import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
    TaskAssignmentRequest,
    TasksWithStatsResponse,
    UserResponse,
)
from ..application.use_cases.task import TaskUseCases
from ..application.use_cases.task_list import TaskListUseCases
from ..application.use_cases.user import UserUseCases
from ..dependencies import (
    get_task_use_cases,
    get_task_list_use_cases,
    get_user_use_cases,
)
from ..domain.exceptions import (
    EntityNotFoundException,
    InvalidDataException,
    DuplicateEntityException,
)
from ..domain.models.enums import TaskStatus, TaskPriority
from ..domain.models.entities import User
from ..auth.dependencies import get_current_user

# Router original para rutas anidadas bajo task-lists
router = APIRouter(prefix="/task-lists", tags=["Tasks"])

# Router adicional para rutas directas de tasks (para tests)
tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ===== ROUTER ORIGINAL (task-lists anidado) =====

@router.post(
    "/{task_list_id}/tasks/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_list_id: int,
    request: TaskCreateRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
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
    - **assigned_user_id**: ID of the user to assign this task to (optional)

    **Business Rules:**
    - Task title must be unique within the task list
    - Due date cannot be in the past
    - Task list must exist
    - Assigned user must exist (if provided)
    """
    try:
        # Get assigned user if provided (for response)
        assigned_user = None
        if request.assigned_user_id:
            assigned_user = user_use_cases.get_user_by_id(request.assigned_user_id)

        task_entity = task_use_cases.create_task(
            title=request.title,
            description=request.description,
            task_list_id=task_list_id,
            priority=request.priority,
            due_date=request.due_date,
            assigned_user_id=request.assigned_user_id,
        )
        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateEntityException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ===== ROUTER ADICIONAL (rutas directas para tests) =====

@tasks_router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_direct(
    request: TaskCreateRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Create a new task (direct endpoint for API consistency)."""
    try:
        # Validate that task_list_id is provided for direct endpoint
        if request.task_list_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="task_list_id is required for direct task creation"
            )

        # Get assigned user if provided (for response)
        assigned_user = None
        if request.assigned_user_id:
            assigned_user = user_use_cases.get_user_by_id(request.assigned_user_id)

        task_entity = task_use_cases.create_task(
            title=request.title,
            description=request.description,
            task_list_id=request.task_list_id,
            priority=request.priority,
            due_date=request.due_date,
            assigned_user_id=request.assigned_user_id,
        )
        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateEntityException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@tasks_router.get("/list/{task_list_id}", response_model=List[TaskResponse])
def get_tasks_by_list_direct(
    task_list_id: int,
    task_status: Optional[TaskStatus] = Query(
        None,
        alias="status",
        description="Filter by task status",
    ),
    priority: Optional[TaskPriority] = Query(
        None,
        description="Filter by task priority",
    ),
    assigned_user_id: Optional[int] = Query(
        None,
        description="Filter by assigned user ID",
    ),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Get tasks by task list ID (direct endpoint)."""
    try:
        tasks = task_use_cases.get_tasks_by_list_id(
            task_list_id=task_list_id,
            status=task_status,
            priority=priority,
            assigned_user_id=assigned_user_id,
        )

        # Get assigned users for tasks that have them
        tasks_with_users = []
        for task in tasks:
            assigned_user = None
            if task.assigned_user_id:
                try:
                    assigned_user = user_use_cases.get_user_by_id(task.assigned_user_id)
                except EntityNotFoundException:
                    pass
            tasks_with_users.append(TaskResponse.from_entity(task, assigned_user))

        return tasks_with_users

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@tasks_router.get("/{task_id}", response_model=TaskResponse)
def get_task_direct(
    task_id: int,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Get task by ID (direct endpoint)."""
    try:
        task = task_use_cases.get_task_by_id(task_id)
        
        # Get assigned user if exists
        assigned_user = None
        if task.assigned_user_id:
            try:
                assigned_user = user_use_cases.get_user_by_id(task.assigned_user_id)
            except EntityNotFoundException:
                pass

        return TaskResponse.from_entity(task, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@tasks_router.put("/{task_id}", response_model=TaskResponse)
def update_task_direct(
    task_id: int,
    request: TaskUpdateRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Update task (direct endpoint)."""
    try:
        # Get assigned user if provided
        assigned_user = None
        if request.assigned_user_id:
            assigned_user = user_use_cases.get_user_by_id(request.assigned_user_id)

        task_entity = task_use_cases.update_task(
            task_id=task_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            status=request.status,
            due_date=request.due_date,
            assigned_user_id=request.assigned_user_id,
        )
        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateEntityException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@tasks_router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status_direct(
    task_id: int,
    request: TaskStatusUpdateRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Update task status (direct endpoint)."""
    try:
        task_entity = task_use_cases.update_task_status(task_id, request.status)
        
        # Get assigned user if exists
        assigned_user = None
        if task_entity.assigned_user_id:
            try:
                assigned_user = user_use_cases.get_user_by_id(task_entity.assigned_user_id)
            except EntityNotFoundException:
                pass

        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@tasks_router.patch("/{task_id}/assign", response_model=TaskResponse)
def assign_task_to_user_direct(
    task_id: int,
    request: TaskAssignmentRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Assign task to user (direct endpoint)."""
    try:
        # Get user_id from either field (user_id takes precedence for tests)
        user_id = request.user_id if request.user_id is not None else request.assigned_user_id
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id or assigned_user_id is required"
            )
        
        # Get the user first to ensure they exist
        assigned_user = user_use_cases.get_user_by_id(user_id)
        
        task_entity = task_use_cases.assign_task_to_user(task_id, user_id)
        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_direct(
    task_id: int,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Delete task (direct endpoint)."""
    try:
        task_use_cases.delete_task(task_id)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@tasks_router.get("/user/{user_id}", response_model=List[TaskResponse])
def get_tasks_by_user_direct(
    user_id: int,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Get tasks assigned to a specific user (direct endpoint)."""
    try:
        # Verify user exists
        assigned_user = user_use_cases.get_user_by_id(user_id)
        
        tasks = task_use_cases.get_tasks_by_user_id(user_id)
        return [TaskResponse.from_entity(task, assigned_user) for task in tasks]

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


# ===== RESTO DEL ROUTER ORIGINAL (continúa igual) =====

@router.get("/{task_list_id}/tasks/", response_model=TasksWithStatsResponse)
def get_tasks_by_list(
    task_list_id: int,
    task_status: Optional[TaskStatus] = Query(
        None,
        alias="status",
        description="Filter by task status. Available values: pending, in_progress, completed, cancelled",
    ),
    priority: Optional[TaskPriority] = Query(
        None,
        description="Filter by task priority. Available values: low, medium, high, urgent",
    ),
    assigned_user_id: Optional[int] = Query(
        None,
        description="Filter by assigned user ID",
    ),
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    task_list_use_cases: TaskListUseCases = Depends(get_task_list_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
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

    - **assigned_user_id**: Filter tasks by assigned user ID (optional)

    **Note:** The completion percentage is calculated based on ALL tasks in the list,
    not just the filtered results.
    """
    try:
        # Get task list information
        task_list = task_list_use_cases.get_task_list_by_id(task_list_id)

        # Get filtered tasks
        tasks = task_use_cases.get_tasks_by_list_id(
            task_list_id=task_list_id,
            status=task_status,
            priority=priority,
            assigned_user_id=assigned_user_id,
        )

        # Get all tasks for completion percentage calculation
        all_tasks = task_use_cases.get_tasks_by_list_id(task_list_id)
        total_tasks = len(all_tasks)
        completed_tasks = len(
            [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        )
        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )

        # Get assigned users for tasks that have them
        tasks_with_users = []
        for task in tasks:
            assigned_user = None
            if task.assigned_user_id:
                try:
                    assigned_user = user_use_cases.get_user_by_id(task.assigned_user_id)
                except EntityNotFoundException:
                    # User might have been deleted, continue without user info
                    pass
            tasks_with_users.append(TaskResponse.from_entity(task, assigned_user))

        # Create custom response with user information
        response_data = TasksWithStatsResponse.from_tasks_and_task_list(
            tasks=tasks,
            task_list=task_list,
            completion_percentage=completion_percentage,
        )

        # Replace tasks with ones that include user information
        response_data.tasks = tasks_with_users

        return response_data

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{task_list_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_list_id: int,
    task_id: int,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Get a task by ID including assigned user information."""
    try:
        task_entity = task_use_cases.get_task_by_id(task_id)

        # Verify the task belongs to the specified task list
        if task_entity.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found in task list {task_list_id}",
            )

        # Get assigned user if exists
        assigned_user = None
        if task_entity.assigned_user_id:
            try:
                assigned_user = user_use_cases.get_user_by_id(
                    task_entity.assigned_user_id
                )
            except EntityNotFoundException:
                # User might have been deleted, continue without user info
                pass

        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{task_list_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_list_id: int,
    task_id: int,
    request: TaskUpdateRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
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
    - **assigned_user_id**: ID of the user to assign this task to (use null to unassign)

    **Business Rules:**
    - Task must exist and belong to the specified task list
    - New title must be unique within the task list (if provided)
    - Due date cannot be in the past (if provided)
    - Assigned user must exist (if provided and not null)
    """
    try:
        # First verify the task exists and belongs to the task list
        existing_task = task_use_cases.get_task_by_id(task_id)
        if existing_task.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found in task list {task_list_id}",
            )

        task_entity = task_use_cases.update_task(
            task_id=task_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            due_date=request.due_date,
            assigned_user_id=request.assigned_user_id,
        )

        # Get assigned user if exists
        assigned_user = None
        if task_entity.assigned_user_id:
            try:
                assigned_user = user_use_cases.get_user_by_id(
                    task_entity.assigned_user_id
                )
            except EntityNotFoundException:
                pass

        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateEntityException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/{task_list_id}/tasks/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_list_id: int,
    task_id: int,
    request: TaskStatusUpdateRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
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
        # First verify the task exists and belongs to the task list
        existing_task = task_use_cases.get_task_by_id(task_id)
        if existing_task.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found in task list {task_list_id}",
            )

        task_entity = task_use_cases.update_task_status(task_id, request.status)

        # Get assigned user if exists
        assigned_user = None
        if task_entity.assigned_user_id:
            try:
                assigned_user = user_use_cases.get_user_by_id(
                    task_entity.assigned_user_id
                )
            except EntityNotFoundException:
                pass

        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/{task_list_id}/tasks/{task_id}/assign", response_model=TaskResponse)
def assign_task_to_user(
    task_list_id: int,
    task_id: int,
    request: TaskAssignmentRequest,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """
    Assign or unassign a task to a user.

    **Request Body Fields:**
    - **assigned_user_id**: ID of the user to assign (use null to unassign)

    **Business Rules:**
    - Task must exist and belong to the specified task list
    - User must exist (if assigning)
    """
    try:
        # First verify the task exists and belongs to the task list
        existing_task = task_use_cases.get_task_by_id(task_id)
        if existing_task.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found in task list {task_list_id}",
            )

        task_entity = task_use_cases.assign_task_to_user(
            task_id, request.assigned_user_id
        )

        # Get assigned user if exists
        assigned_user = None
        if task_entity.assigned_user_id:
            try:
                assigned_user = user_use_cases.get_user_by_id(
                    task_entity.assigned_user_id
                )
            except EntityNotFoundException:
                pass

        return TaskResponse.from_entity(task_entity, assigned_user)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete(
    "/{task_list_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
    task_list_id: int,
    task_id: int,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    current_user: User = Depends(get_current_user),
):
    """Delete a task."""
    try:
        # First verify the task exists and belongs to the task list
        existing_task = task_use_cases.get_task_by_id(task_id)
        if existing_task.task_list_id != task_list_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found in task list {task_list_id}",
            )

        task_use_cases.delete_task(task_id)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Additional endpoint to get all tasks assigned to a specific user across all task lists
@router.get("/users/{user_id}/tasks", response_model=List[TaskResponse])
def get_tasks_by_user(
    user_id: int,
    task_use_cases: TaskUseCases = Depends(get_task_use_cases),
    user_use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: User = Depends(get_current_user),
):
    """
    Get all tasks assigned to a specific user across all task lists.

    **Path Parameters:**
    - **user_id**: ID of the user whose tasks to retrieve

    **Business Rules:**
    - User must exist
    """
    try:
        # Verify user exists
        user = user_use_cases.get_user_by_id(user_id)

        tasks = task_use_cases.get_tasks_by_user_id(user_id)
        return [TaskResponse.from_entity(task, user) for task in tasks]

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
