from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.entities import TaskList


class TaskListRepository(ABC):
    """Task list repository interface."""

    @abstractmethod
    def create(self, task_list: TaskList) -> TaskList:
        """Create a new task list."""
        pass

    @abstractmethod
    def get_by_id(self, task_list_id: int) -> Optional[TaskList]:
        """Get a task list by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[TaskList]:
        """Get all task lists."""
        pass

    @abstractmethod
    def update(self, task_list: TaskList) -> TaskList:
        """Update a task list."""
        pass

    @abstractmethod
    def delete(self, task_list_id: int) -> bool:
        """Delete a task list."""
        pass

    @abstractmethod
    def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a task list exists by name."""
        pass
