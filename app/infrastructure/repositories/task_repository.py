from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from ...domain.models.entities import Task
from ...domain.models.enums import TaskStatus, TaskPriority
from ...domain.repositories import TaskRepository
from ..models.task import TaskModel


class SQLTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, task: Task) -> Task:
        """Create a new task."""
        db_task = TaskModel(
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            due_date=task.due_date,
            task_list_id=task.task_list_id,
            assigned_user_id=task.assigned_user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)

        return self._to_domain(db_task)

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        return self._to_domain(db_task) if db_task else None

    def get_by_task_list_id(self, task_list_id: int) -> List[Task]:
        """Get all tasks for a specific task list."""
        db_tasks = (
            self.db.query(TaskModel)
            .filter(TaskModel.task_list_id == task_list_id)
            .all()
        )
        return [self._to_domain(db_task) for db_task in db_tasks]

    def get_by_assigned_user_id(self, user_id: int) -> List[Task]:
        """Get all tasks assigned to a specific user."""
        db_tasks = (
            self.db.query(TaskModel).filter(TaskModel.assigned_user_id == user_id).all()
        )
        return [self._to_domain(db_task) for db_task in db_tasks]

    def get_filtered_tasks(
        self,
        task_list_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_user_id: Optional[int] = None,
    ) -> List[Task]:
        """Get filtered tasks for a task list."""
        query = self.db.query(TaskModel).filter(TaskModel.task_list_id == task_list_id)

        if status:
            query = query.filter(TaskModel.status == status.value)

        if priority:
            query = query.filter(TaskModel.priority == priority.value)

        if assigned_user_id:
            query = query.filter(TaskModel.assigned_user_id == assigned_user_id)

        db_tasks = query.all()
        return [self._to_domain(db_task) for db_task in db_tasks]

    def update(self, task: Task) -> Task:
        """Update a task."""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task.id).first()
        if not db_task:
            raise ValueError(f"Task with id {task.id} not found")

        db_task.title = task.title
        db_task.description = task.description
        db_task.status = task.status.value
        db_task.priority = task.priority.value
        db_task.due_date = task.due_date
        db_task.assigned_user_id = task.assigned_user_id
        db_task.updated_at = task.updated_at

        self.db.commit()
        self.db.refresh(db_task)

        return self._to_domain(db_task)

    def delete(self, task_id: int) -> bool:
        """Delete a task."""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not db_task:
            return False

        self.db.delete(db_task)
        self.db.commit()
        return True

    def update_status(self, task_id: int, status: TaskStatus) -> Task:
        """Update task status."""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not db_task:
            raise ValueError(f"Task with id {task_id} not found")

        db_task.status = status.value
        db_task.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_task)

        return self._to_domain(db_task)

    def assign_user(self, task_id: int, user_id: Optional[int]) -> Task:
        """Assign or unassign a user to a task."""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not db_task:
            raise ValueError(f"Task with id {task_id} not found")

        db_task.assigned_user_id = user_id
        db_task.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_task)

        return self._to_domain(db_task)

    def exists_by_title_in_list(
        self, title: str, task_list_id: int, exclude_id: Optional[int] = None
    ) -> bool:
        """Check if a task exists by title in a specific list."""
        query = self.db.query(TaskModel).filter(
            TaskModel.title == title, TaskModel.task_list_id == task_list_id
        )

        if exclude_id:
            query = query.filter(TaskModel.id != exclude_id)

        return query.first() is not None

    def _to_domain(self, db_task: TaskModel) -> Task:
        """Convert TaskModel to Task domain entity."""
        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=TaskStatus(db_task.status),
            priority=TaskPriority(db_task.priority),
            due_date=db_task.due_date,
            task_list_id=db_task.task_list_id,
            assigned_user_id=db_task.assigned_user_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
        )
