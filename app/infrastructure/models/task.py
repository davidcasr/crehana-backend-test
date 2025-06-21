from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from ..database.base import Base
from ...domain.models.enums import TaskStatus, TaskPriority


class TaskModel(Base):
    """SQLAlchemy model for tasks."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True
    )
    priority = Column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False, index=True
    )
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )

    # Foreign key to task list
    task_list_id = Column(
        Integer, ForeignKey("task_lists.id"), nullable=False, index=True
    )
    
    # Foreign key to assigned user
    assigned_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )

    # Relationship with task list
    task_list = relationship("TaskListModel", back_populates="tasks")
    
    # Relationship with assigned user
    assigned_user = relationship("UserModel", back_populates="assigned_tasks")

    def __repr__(self):
        return (
            f"<TaskModel(id={self.id}, title='{self.title}', status='{self.status}')>"
        )
