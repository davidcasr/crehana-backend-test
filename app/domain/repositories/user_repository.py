from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.entities import User
from ..models.enums import UserStatus


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