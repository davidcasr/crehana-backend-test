from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship

from ...domain.models.enums import UserStatus
from ..database.base import Base


class UserModel(Base):
    """SQLAlchemy model for users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable para usuarios existentes
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Relationship with tasks
    assigned_tasks = relationship("TaskModel", back_populates="assigned_user")
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, username='{self.username}', email='{self.email}')>" 