from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .models.entities import TaskList, Task, User
from .models.enums import TaskStatus, TaskPriority, UserStatus


class UserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        pass
    
    @abstractmethod
    def get_all(self, status: Optional[UserStatus] = None) -> List[User]:
        """Get all users, optionally filtered by status."""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Update a user."""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete a user."""
        pass
    
    @abstractmethod
    def exists_by_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a user exists by username."""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a user exists by email."""
        pass


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
