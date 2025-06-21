from datetime import datetime
from typing import List, Optional

from ...domain.exceptions import (
    EntityNotFoundException,
    InvalidDataException,
    DuplicateEntityException,
)
from ...domain.models.entities import TaskList
from ...domain.repositories import TaskListRepository


class TaskListUseCases:
    """Use cases for task list management."""

    def __init__(self, task_list_repository: TaskListRepository):
        self.task_list_repository = task_list_repository

    def create_task_list(
        self, name: str, description: Optional[str] = None
    ) -> TaskList:
        """Create a new task list."""
        # Validate input
        if not name or len(name.strip()) < 1:
            raise InvalidDataException("Task list name cannot be empty")

        # Check for duplicate name
        if self.task_list_repository.exists_by_name(name.strip()):
            raise DuplicateEntityException(
                f"Task list with name '{name}' already exists"
            )

        # Create task list entity
        now = datetime.utcnow()
        task_list = TaskList(
            name=name.strip(),
            description=description.strip() if description else None,
            created_at=now,
            updated_at=now,
        )

        return self.task_list_repository.create(task_list)

    def get_task_list_by_id(self, task_list_id: int) -> TaskList:
        """Get a task list by ID."""
        if task_list_id <= 0:
            raise InvalidDataException("Task list ID must be positive")

        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise EntityNotFoundException(f"Task list with id {task_list_id} not found")

        return task_list

    def get_all_task_lists(self) -> List[TaskList]:
        """Get all task lists."""
        return self.task_list_repository.get_all()

    def update_task_list(
        self,
        task_list_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> TaskList:
        """Update a task list."""
        # Get existing task list
        task_list = self.get_task_list_by_id(task_list_id)

        # Validate and set new values
        if name is not None:
            if len(name.strip()) < 1:
                raise InvalidDataException("Task list name cannot be empty")

            # Check for duplicate name (excluding current task list)
            if self.task_list_repository.exists_by_name(
                name.strip(), exclude_id=task_list_id
            ):
                raise DuplicateEntityException(
                    f"Task list with name '{name}' already exists"
                )

            task_list.name = name.strip()

        if description is not None:
            task_list.description = description.strip() if description else None

        task_list.updated_at = datetime.utcnow()

        return self.task_list_repository.update(task_list)

    def delete_task_list(self, task_list_id: int) -> bool:
        """Delete a task list."""
        # Verify task list exists
        self.get_task_list_by_id(task_list_id)

        # TODO: Here we should check if the task list has tasks
        # and decide how to handle them (cascade delete, prevent deletion, etc.)
        # For now, we'll assume the database constraints will handle this

        return self.task_list_repository.delete(task_list_id)
