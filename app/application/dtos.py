from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from ..domain.models.enums import TaskStatus, TaskPriority, UserStatus


# User DTOs
class UserCreateRequest(BaseModel):
    """Request DTO for creating a user."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., max_length=100, description="User email")
    full_name: str = Field(
        ..., min_length=1, max_length=100, description="User full name"
    )
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")


class UserUpdateRequest(BaseModel):
    """Request DTO for updating a user."""

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    email: Optional[str] = Field(None, max_length=100, description="User email")
    full_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="User full name"
    )
    status: Optional[UserStatus] = Field(None, description="User status")


class UserResponse(BaseModel):
    """Response DTO for user."""

    id: int
    username: str
    email: str
    full_name: str
    status: UserStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, user):
        """Create response from User entity."""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class TaskListCreateRequest(BaseModel):
    """Request DTO for creating a task list."""

    name: str = Field(..., min_length=1, max_length=100, description="Task list name")
    description: Optional[str] = Field(
        None, max_length=500, description="Task list description"
    )


class TaskListUpdateRequest(BaseModel):
    """Request DTO for updating a task list."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Task list name"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Task list description"
    )


class TaskListResponse(BaseModel):
    """Response DTO for task list."""

    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    task_count: int = 0

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, task_list):
        """Create response from TaskList entity."""
        return cls(
            id=task_list.id,
            name=task_list.name,
            description=task_list.description,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at,
            task_count=len(task_list.tasks) if task_list.tasks else 0,
        )


class TaskCreateRequest(BaseModel):
    """Request DTO for creating a task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")
    assigned_user_id: Optional[int] = Field(
        None, description="ID of the user assigned to this task"
    )


class TaskUpdateRequest(BaseModel):
    """Request DTO for updating a task."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Task title"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    status: Optional[TaskStatus] = Field(None, description="Task status")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    assigned_user_id: Optional[int] = Field(
        None, description="ID of the user assigned to this task"
    )


class TaskResponse(BaseModel):
    """Response DTO for task."""

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    task_list_id: int
    assigned_user_id: Optional[int]
    assigned_user: Optional[UserResponse] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, task, assigned_user=None):
        """Create response from Task entity."""
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            task_list_id=task.task_list_id,
            assigned_user_id=task.assigned_user_id,
            assigned_user=(
                UserResponse.from_entity(assigned_user) if assigned_user else None
            ),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TaskListWithStatsResponse(BaseModel):
    """Response DTO for task list with tasks and completion percentage."""

    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    tasks: List[TaskResponse]
    completion_percentage: float = Field(
        ..., ge=0, le=100, description="Completion percentage"
    )

    @classmethod
    def from_entity_and_stats(cls, task_list, completion_percentage: float):
        """Create response from TaskList entity and completion stats."""
        return cls(
            id=task_list.id,
            name=task_list.name,
            description=task_list.description,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at,
            tasks=[TaskResponse.from_entity(task) for task in task_list.tasks],
            completion_percentage=completion_percentage,
        )


class TaskFilterRequest(BaseModel):
    """Request DTO for filtering tasks."""

    status: Optional[TaskStatus] = Field(None, description="Filter by task status")
    priority: Optional[TaskPriority] = Field(
        None, description="Filter by task priority"
    )
    assigned_user_id: Optional[int] = Field(
        None, description="Filter by assigned user ID"
    )


class TaskStatusUpdateRequest(BaseModel):
    """Request DTO for updating task status."""

    status: TaskStatus = Field(..., description="New task status")


class TaskAssignmentRequest(BaseModel):
    """Request DTO for assigning/unassigning a user to a task."""

    assigned_user_id: Optional[int] = Field(
        None, description="ID of the user to assign (null to unassign)"
    )


class TasksWithStatsResponse(BaseModel):
    """Response DTO for tasks with task list info and completion percentage."""

    task_list_id: int
    task_list_name: str
    task_list_description: Optional[str]
    total_tasks: int
    completion_percentage: float = Field(
        ..., ge=0, le=100, description="Completion percentage"
    )
    tasks: List[TaskResponse]

    @classmethod
    def from_tasks_and_task_list(
        cls, tasks: List, task_list, completion_percentage: float
    ):
        """Create response from tasks list, task_list entity and completion stats."""
        return cls(
            task_list_id=task_list.id,
            task_list_name=task_list.name,
            task_list_description=task_list.description,
            total_tasks=len(tasks),
            completion_percentage=completion_percentage,
            tasks=[TaskResponse.from_entity(task) for task in tasks],
        )


# Authentication DTOs
class LoginRequest(BaseModel):
    """Request DTO for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=6, description="User password")


class LoginResponse(BaseModel):
    """Response DTO for user login."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")


class RegisterRequest(BaseModel):
    """Request DTO for user registration."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., max_length=100, description="User email")
    full_name: str = Field(
        ..., min_length=1, max_length=100, description="User full name"
    )
    password: str = Field(..., min_length=6, description="User password")


class ChangePasswordRequest(BaseModel):
    """Request DTO for changing password."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")
