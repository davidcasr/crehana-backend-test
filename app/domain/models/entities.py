from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .enums import TaskStatus, TaskPriority


class TaskList(BaseModel):
    """Task list entity."""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100, description="Task list name")
    description: Optional[str] = Field(None, max_length=500, description="Task list description")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tasks: Optional[List['Task']] = []

    class Config:
        from_attributes = True


class Task(BaseModel):
    """Task entity."""
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    due_date: Optional[datetime] = None
    task_list_id: int = Field(..., description="ID of the task list this task belongs to")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Update forward references
TaskList.model_rebuild()
Task.model_rebuild() 