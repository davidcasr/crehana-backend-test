from datetime import datetime
from typing import List, Optional

from ...domain.exceptions import (
    EntityNotFoundException,
    InvalidDataException,
    DuplicateEntityException,
)
from ...domain.models.entities import User
from ...domain.models.enums import UserStatus
from ...domain.repositories import UserRepository


class UserUseCases:
    """Use cases for user management."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        status: UserStatus = UserStatus.ACTIVE,
    ) -> User:
        """Create a new user."""
        # Validate input
        if not username or len(username.strip()) < 3:
            raise InvalidDataException("Username must be at least 3 characters long")

        if not email or "@" not in email:
            raise InvalidDataException("Invalid email format")

        if not full_name or len(full_name.strip()) < 1:
            raise InvalidDataException("Full name cannot be empty")

        # Check for duplicates
        if self.user_repository.exists_by_username(username.strip()):
            raise DuplicateEntityException(f"User with username '{username}' already exists")

        if self.user_repository.exists_by_email(email.strip().lower()):
            raise DuplicateEntityException(f"User with email '{email}' already exists")

        # Create user entity
        now = datetime.utcnow()
        user = User(
            username=username.strip(),
            email=email.strip().lower(),
            full_name=full_name.strip(),
            status=status,
            created_at=now,
            updated_at=now,
        )

        return self.user_repository.create(user)

    def get_user_by_id(self, user_id: int) -> User:
        """Get a user by ID."""
        if user_id <= 0:
            raise InvalidDataException("User ID must be positive")

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException(f"User with id {user_id} not found")

        return user

    def get_user_by_username(self, username: str) -> User:
        """Get a user by username."""
        if not username or len(username.strip()) == 0:
            raise InvalidDataException("Username cannot be empty")

        user = self.user_repository.get_by_username(username.strip())
        if not user:
            raise EntityNotFoundException(f"User with username '{username}' not found")

        return user

    def get_user_by_email(self, email: str) -> User:
        """Get a user by email."""
        if not email or "@" not in email:
            raise InvalidDataException("Invalid email format")

        user = self.user_repository.get_by_email(email.strip().lower())
        if not user:
            raise EntityNotFoundException(f"User with email '{email}' not found")

        return user

    def get_all_users(self, status: Optional[UserStatus] = None) -> List[User]:
        """Get all users, optionally filtered by status."""
        return self.user_repository.get_all(status)

    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        status: Optional[UserStatus] = None,
    ) -> User:
        """Update a user."""
        # Get existing user
        user = self.get_user_by_id(user_id)

        # Validate and set new values
        if username is not None:
            if len(username.strip()) < 3:
                raise InvalidDataException("Username must be at least 3 characters long")
            
            if self.user_repository.exists_by_username(username.strip(), exclude_id=user_id):
                raise DuplicateEntityException(f"User with username '{username}' already exists")
            
            user.username = username.strip()

        if email is not None:
            if "@" not in email:
                raise InvalidDataException("Invalid email format")
            
            if self.user_repository.exists_by_email(email.strip().lower(), exclude_id=user_id):
                raise DuplicateEntityException(f"User with email '{email}' already exists")
            
            user.email = email.strip().lower()

        if full_name is not None:
            if len(full_name.strip()) < 1:
                raise InvalidDataException("Full name cannot be empty")
            
            user.full_name = full_name.strip()

        if status is not None:
            user.status = status

        user.updated_at = datetime.utcnow()

        return self.user_repository.update(user)

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        # Verify user exists
        self.get_user_by_id(user_id)

        # TODO: Here we should check if the user has assigned tasks
        # and decide how to handle them (reassign, unassign, etc.)
        # For now, we'll assume the database constraints will handle this

        return self.user_repository.delete(user_id)

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user instead of deleting."""
        return self.update_user(user_id, status=UserStatus.INACTIVE)

    def activate_user(self, user_id: int) -> User:
        """Activate a user."""
        return self.update_user(user_id, status=UserStatus.ACTIVE) 