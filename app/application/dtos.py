from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from ..domain.models.enums import TaskStatus, TaskPriority


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
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")


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


class TaskResponse(BaseModel):
    """Response DTO for task."""

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    task_list_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_entity(cls, task):
        """Create response from Task entity."""
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            task_list_id=task.task_list_id,
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


class TaskStatusUpdateRequest(BaseModel):
    """Request DTO for updating task status."""

    status: TaskStatus = Field(..., description="New task status")


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
