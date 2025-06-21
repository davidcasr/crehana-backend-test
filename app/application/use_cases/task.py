from datetime import datetime
from typing import List, Optional

from ...domain.exceptions import (
    EntityNotFoundException,
    InvalidDataException,
    DuplicateEntityException,
)
from ...domain.models.entities import Task
from ...domain.models.enums import TaskStatus, TaskPriority
from ...domain.repositories import TaskRepository, TaskListRepository, UserRepository


class TaskUseCases:
    """Use cases for task management."""

    def __init__(
        self,
        task_repository: TaskRepository,
        task_list_repository: TaskListRepository,
        user_repository: UserRepository,
    ):
        self.task_repository = task_repository
        self.task_list_repository = task_list_repository
        self.user_repository = user_repository

    def create_task(
        self,
        title: str,
        description: str,
        task_list_id: int,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        assigned_user_id: Optional[int] = None,
    ) -> Task:
        """Create a new task."""
        # Validate input
        if not title or len(title.strip()) < 1:
            raise InvalidDataException("Task title cannot be empty")

        if not description or len(description.strip()) < 1:
            raise InvalidDataException("Task description cannot be empty")

        if task_list_id <= 0:
            raise InvalidDataException("Task list ID must be positive")
   
        # Verify task list exists
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise EntityNotFoundException(f"Task list with id {task_list_id} not found")

        # Check for duplicate title in the same list
        if self.task_repository.exists_by_title_in_list(title.strip(), task_list_id):
            raise DuplicateEntityException(
                f"Task with title '{title}' already exists in this list"
            )

        # Verify assigned user exists if provided
        if assigned_user_id is not None:
            if assigned_user_id <= 0:
                raise InvalidDataException("Assigned user ID must be positive")
            
            user = self.user_repository.get_by_id(assigned_user_id)
            if not user:
                raise EntityNotFoundException(f"User with id {assigned_user_id} not found")

        # Create task entity
        now = datetime.utcnow()
        task = Task(
            title=title.strip(),
            description=description.strip(),
            task_list_id=task_list_id,
            status=TaskStatus.PENDING,
            priority=priority,
            due_date=due_date,
            assigned_user_id=assigned_user_id,
            created_at=now,
            updated_at=now,
        )

        return self.task_repository.create(task)

    def get_task_by_id(self, task_id: int) -> Task:
        """Get a task by ID."""
        if task_id <= 0:
            raise InvalidDataException("Task ID must be positive")

        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise EntityNotFoundException(f"Task with id {task_id} not found")

        return task

    def get_tasks_by_list_id(
        self,
        task_list_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_user_id: Optional[int] = None,
    ) -> List[Task]:
        """Get all tasks for a specific task list with optional filters."""
        if task_list_id <= 0:
            raise InvalidDataException("Task list ID must be positive")

        # Verify task list exists
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise EntityNotFoundException(f"Task list with id {task_list_id} not found")

        # Verify assigned user exists if provided
        if assigned_user_id is not None:
            if assigned_user_id <= 0:
                raise InvalidDataException("Assigned user ID must be positive")
            
            user = self.user_repository.get_by_id(assigned_user_id)
            if not user:
                raise EntityNotFoundException(f"User with id {assigned_user_id} not found")

        return self.task_repository.get_filtered_tasks(
            task_list_id, status, priority, assigned_user_id
        )

    def get_tasks_by_user_id(self, user_id: int) -> List[Task]:
        """Get all tasks assigned to a specific user."""
        if user_id <= 0:
            raise InvalidDataException("User ID must be positive")

        # Verify user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException(f"User with id {user_id} not found")

        return self.task_repository.get_by_assigned_user_id(user_id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        due_date: Optional[datetime] = None,
        assigned_user_id: Optional[int] = None,
    ) -> Task:
        """Update a task."""
        # Get existing task
        task = self.get_task_by_id(task_id)

        # Validate and set new values
        if title is not None:
            if len(title.strip()) < 1:
                raise InvalidDataException("Task title cannot be empty")
            
            # Check for duplicate title in the same list (excluding current task)
            if self.task_repository.exists_by_title_in_list(
                title.strip(), task.task_list_id, exclude_id=task_id
            ):
                raise DuplicateEntityException(
                    f"Task with title '{title}' already exists in this list"
                )
            
            task.title = title.strip()

        if description is not None:
            if len(description.strip()) < 1:
                raise InvalidDataException("Task description cannot be empty")
            
            task.description = description.strip()

        if priority is not None:
            task.priority = priority

        if due_date is not None:
            task.due_date = due_date

        # Handle assigned user
        if assigned_user_id is not None:
            if assigned_user_id <= 0:
                raise InvalidDataException("Assigned user ID must be positive")
            
            user = self.user_repository.get_by_id(assigned_user_id)
            if not user:
                raise EntityNotFoundException(f"User with id {assigned_user_id} not found")
            
            task.assigned_user_id = assigned_user_id

        task.updated_at = datetime.utcnow()

        return self.task_repository.update(task)

    def update_task_status(self, task_id: int, status: TaskStatus) -> Task:
        """Update task status."""
        # Verify task exists
        self.get_task_by_id(task_id)

        return self.task_repository.update_status(task_id, status)

    def assign_task_to_user(self, task_id: int, user_id: Optional[int]) -> Task:
        """Assign or unassign a task to a user."""
        # Verify task exists
        self.get_task_by_id(task_id)

        # Verify user exists if provided
        if user_id is not None:
            if user_id <= 0:
                raise InvalidDataException("User ID must be positive")
            
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise EntityNotFoundException(f"User with id {user_id} not found")

        return self.task_repository.assign_user(task_id, user_id)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        # Verify task exists
        self.get_task_by_id(task_id)

        return self.task_repository.delete(task_id)

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as completed."""
        return self.update_task_status(task_id, TaskStatus.COMPLETED)

    def reopen_task(self, task_id: int) -> Task:
        """Reopen a completed task."""
        return self.update_task_status(task_id, TaskStatus.PENDING)
