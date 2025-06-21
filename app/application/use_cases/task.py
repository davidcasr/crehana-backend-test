from datetime import datetime
from typing import List, Optional

from ...domain.models.entities import Task
from ...domain.models.enums import TaskStatus, TaskPriority
from ...domain.repositories import TaskRepository, TaskListRepository
from ...domain.exceptions import (
    TaskListNotFoundException,
    TaskNotFoundException,
    TaskTitleAlreadyExistsException,
    InvalidDueDateException,
)


class TaskUseCases:
    """Use cases for task management."""

    def __init__(
        self, task_repository: TaskRepository, task_list_repository: TaskListRepository
    ):
        self.task_repository = task_repository
        self.task_list_repository = task_list_repository

    def create_task(
        self,
        task_list_id: int,
        title: str,
        description: str = None,
        status: TaskStatus = TaskStatus.PENDING,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: datetime = None,
    ) -> Task:
        """Create a new task in a task list."""
        # Business validation: check if task list exists
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise TaskListNotFoundException(
                f"Task list with ID {task_list_id} not found"
            )

        # Business validation: check if title already exists in the same list
        if self.task_repository.exists_by_title_in_list(title, task_list_id):
            raise TaskTitleAlreadyExistsException(
                f"Task with title '{title}' already exists in this list"
            )

        # Business validation: check due date
        if due_date:
            # Handle timezone-aware vs timezone-naive datetime comparison
            due_date_naive = (
                due_date.replace(tzinfo=None) if due_date.tzinfo else due_date
            )
            if due_date_naive < datetime.utcnow():
                raise InvalidDueDateException("Due date cannot be in the past")

        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            task_list_id=task_list_id,
            created_at=datetime.utcnow(),
        )

        created_task = self.task_repository.create(task)
        return created_task

    def get_task_by_id(self, task_id: int) -> Task:
        """Get a task entity by ID."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(f"Task with ID {task_id} not found")
        return task

    def get_filtered_tasks(
        self,
        task_list_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[Task]:
        """Get all tasks for a task list with optional filters."""
        # Business validation: check if task list exists
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise TaskListNotFoundException(
                f"Task list with ID {task_list_id} not found"
            )

        # Get tasks with filters
        if status or priority:
            tasks = self.task_repository.get_filtered_tasks(
                task_list_id, status=status, priority=priority
            )
        else:
            tasks = self.task_repository.get_by_task_list_id(task_list_id)

        return tasks

    def update_task(
        self,
        task_id: int,
        title: str = None,
        description: str = None,
        status: TaskStatus = None,
        priority: TaskPriority = None,
        due_date: datetime = None,
    ) -> Task:
        """Update a task."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(f"Task with ID {task_id} not found")

        # Business validation: check if new title already exists in the same list
        if title and title != task.title:
            if self.task_repository.exists_by_title_in_list(
                title, task.task_list_id, exclude_id=task_id
            ):
                raise TaskTitleAlreadyExistsException(
                    f"Task with title '{title}' already exists in this list"
                )

        # Business validation: check due date
        if due_date:
            # Handle timezone-aware vs timezone-naive datetime comparison
            due_date_naive = (
                due_date.replace(tzinfo=None) if due_date.tzinfo else due_date
            )
            if due_date_naive < datetime.utcnow():
                raise InvalidDueDateException("Due date cannot be in the past")

        # Update fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date

        task.updated_at = datetime.utcnow()

        updated_task = self.task_repository.update(task)
        return updated_task

    def update_task_status(self, task_id: int, status: TaskStatus) -> Task:
        """Update task status."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(f"Task with ID {task_id} not found")

        updated_task = self.task_repository.update_status(task_id, status)
        return updated_task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(f"Task with ID {task_id} not found")

        return self.task_repository.delete(task_id)

    def get_tasks_with_stats(
        self,
        task_list_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> dict:
        """Get tasks for a task list with completion statistics."""
        from ...domain.models.enums import TaskStatus as StatusEnum

        # Business validation: check if task list exists
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise TaskListNotFoundException(
                f"Task list with ID {task_list_id} not found"
            )

        # Get filtered tasks
        if status or priority:
            filtered_tasks = self.task_repository.get_filtered_tasks(
                task_list_id, status=status, priority=priority
            )
        else:
            filtered_tasks = self.task_repository.get_by_task_list_id(task_list_id)

        # Get ALL tasks for completion percentage calculation
        all_tasks = self.task_repository.get_by_task_list_id(task_list_id)

        # Calculate completion percentage based on ALL tasks, not filtered ones
        total_tasks = len(all_tasks)
        completed_tasks = len(
            [task for task in all_tasks if task.status == StatusEnum.COMPLETED]
        )
        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )

        return {
            "task_list": task_list,
            "tasks": filtered_tasks,
            "completion_percentage": completion_percentage,
        }
