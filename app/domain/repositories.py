from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .models.entities import TaskList, Task
from .models.enums import TaskStatus, TaskPriority


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
    def get_filtered_tasks(
        self, 
        task_list_id: int, 
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
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
    def exists_by_title_in_list(self, title: str, task_list_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if a task exists by title in a specific list."""
        pass 