from datetime import datetime
from typing import List

from ...domain.models.entities import TaskList
from ...domain.repositories import TaskListRepository, TaskRepository
from ...domain.exceptions import (
    TaskListNotFoundException,
    TaskListNameAlreadyExistsException,
)


class TaskListUseCases:
    """Use cases for task list management."""

    def __init__(
        self, task_list_repository: TaskListRepository, task_repository: TaskRepository
    ):
        self.task_list_repository = task_list_repository
        self.task_repository = task_repository

    def create_task_list(self, name: str, description: str = None) -> TaskList:
        """Create a new task list."""
        # Business validation: check if name already exists
        if self.task_list_repository.exists_by_name(name):
            raise TaskListNameAlreadyExistsException(
                f"Task list with name '{name}' already exists"
            )

        task_list = TaskList(
            name=name, description=description, created_at=datetime.utcnow()
        )

        created_task_list = self.task_list_repository.create(task_list)
        return created_task_list

    def get_task_list(self, task_list_id: int) -> TaskList:
        """Get a task list by ID."""
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise TaskListNotFoundException(
                f"Task list with ID {task_list_id} not found"
            )

        return task_list

    def get_all_task_lists(self) -> List[TaskList]:
        """Get all task lists."""
        task_lists = self.task_list_repository.get_all()
        return task_lists

    def update_task_list(
        self, task_list_id: int, name: str = None, description: str = None
    ) -> TaskList:
        """Update a task list."""
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise TaskListNotFoundException(
                f"Task list with ID {task_list_id} not found"
            )

        # Business validation: check if new name already exists (excluding current task list)
        if name and name != task_list.name:
            if self.task_list_repository.exists_by_name(name, exclude_id=task_list_id):
                raise TaskListNameAlreadyExistsException(
                    f"Task list with name '{name}' already exists"
                )

        # Update fields
        if name is not None:
            task_list.name = name
        if description is not None:
            task_list.description = description

        task_list.updated_at = datetime.utcnow()

        updated_task_list = self.task_list_repository.update(task_list)
        return updated_task_list

    def delete_task_list(self, task_list_id: int) -> bool:
        """Delete a task list."""
        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise TaskListNotFoundException(
                f"Task list with ID {task_list_id} not found"
            )

        return self.task_list_repository.delete(task_list_id)

    def get_task_list_with_completion_stats(self, task_list_id: int) -> dict:
        """Get a task list with completion percentage."""
        from ...domain.models.enums import TaskStatus

        task_list = self.task_list_repository.get_by_id(task_list_id)
        if not task_list:
            raise TaskListNotFoundException(
                f"Task list with ID {task_list_id} not found"
            )

        # Get all tasks for this task list
        tasks = self.task_repository.get_by_task_list_id(task_list_id)

        # Calculate completion percentage
        total_tasks = len(tasks)
        completed_tasks = len(
            [task for task in tasks if task.status == TaskStatus.COMPLETED]
        )
        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )

        # Add tasks to task_list for response
        task_list.tasks = tasks

        return {"task_list": task_list, "completion_percentage": completion_percentage}
