from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.entities import Task
from ..models.enums import TaskStatus, TaskPriority


class TaskRepository(ABC):
    """Task repository interface."""
    
    @abstractmethod
    def create(self, task: Task) -> Task:
        """Create a new task."""
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        pass
    
    @abstractmethod
    def get_by_task_list_id(self, task_list_id: int) -> List[Task]:
        """Get all tasks for a specific task list."""
        pass
    
    @abstractmethod
    def get_by_assigned_user_id(self, user_id: int) -> List[Task]:
        """Get all tasks assigned to a specific user."""
        pass
    
    @abstractmethod
    def get_filtered_tasks(
        self, 
        task_list_id: int, 
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_user_id: Optional[int] = None
    ) -> List[Task]:
        """Get filtered tasks for a task list."""
        pass
    
    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update a task."""
        pass
    
    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task."""
        pass
    
    @abstractmethod
    def update_status(self, task_id: int, status: TaskStatus) -> Task:
        """Update task status."""
        pass
    
    @abstractmethod
    def assign_user(self, task_id: int, user_id: Optional[int]) -> Task:
        """Assign or unassign a user to a task."""
        pass
    
    @abstractmethod
    def exists_by_title_in_list(self, title: str, task_list_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if a task exists by title in a specific list."""
        pass 