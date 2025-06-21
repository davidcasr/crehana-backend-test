from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ...domain.models.entities import User
from ...domain.models.enums import UserStatus
from ...domain.repositories import UserRepository
from ..models.user import UserModel


class SQLUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """Create a new user."""
        db_user = UserModel(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return self._to_domain(db_user)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_domain(db_user) if db_user else None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_domain(db_user) if db_user else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_domain(db_user) if db_user else None
    
    def get_all(self, status: Optional[UserStatus] = None) -> List[User]:
        """Get all users, optionally filtered by status."""
        query = self.db.query(UserModel)
        
        if status:
            query = query.filter(UserModel.status == status.value)
        
        db_users = query.all()
        return [self._to_domain(db_user) for db_user in db_users]
    
    def update(self, user: User) -> User:
        """Update a user."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        
        if not db_user:
            raise ValueError(f"User with id {user.id} not found")
        
        # Update fields
        db_user.username = user.username
        db_user.email = user.email
        db_user.full_name = user.full_name
        db_user.status = user.status.value
        db_user.updated_at = user.updated_at
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return self._to_domain(db_user)
    
    def delete(self, user_id: int) -> bool:
        """Delete a user."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    def exists_by_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a user exists by username."""
        query = self.db.query(UserModel).filter(UserModel.username == username)
        
        if exclude_id:
            query = query.filter(UserModel.id != exclude_id)
        
        return query.first() is not None
    
    def exists_by_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a user exists by email."""
        query = self.db.query(UserModel).filter(UserModel.email == email)
        
        if exclude_id:
            query = query.filter(UserModel.id != exclude_id)
        
        return query.first() is not None
    
    def _to_domain(self, db_user: UserModel) -> User:
        """Convert UserModel to User domain entity."""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        ) 