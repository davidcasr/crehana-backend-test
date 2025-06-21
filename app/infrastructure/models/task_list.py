from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship

from ..database.base import Base


class TaskListModel(Base):
    """SQLAlchemy model for task lists."""

    __tablename__ = "task_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )

    # Relationship with tasks
    tasks = relationship(
        "TaskModel", back_populates="task_list", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TaskListModel(id={self.id}, name='{self.name}')>"
