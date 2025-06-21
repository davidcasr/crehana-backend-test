from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ...domain.models.entities import TaskList
from ...domain.repositories import TaskListRepository
from ..models.task_list import TaskListModel
from ..models.task import TaskModel


class SQLTaskListRepository(TaskListRepository):
    """SQLAlchemy implementation of TaskListRepository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, task_list: TaskList) -> TaskList:
        """Create a new task list."""
        db_task_list = TaskListModel(
            name=task_list.name,
            description=task_list.description,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at,
        )

        self.db.add(db_task_list)
        self.db.commit()
        self.db.refresh(db_task_list)

        return self._to_entity(db_task_list)

    def get_by_id(self, task_list_id: int) -> Optional[TaskList]:
        """Get a task list by ID."""
        db_task_list = (
            self.db.query(TaskListModel)
            .filter(TaskListModel.id == task_list_id)
            .first()
        )

        if not db_task_list:
            return None

        return self._to_entity(db_task_list)

    def get_all(self) -> List[TaskList]:
        """Get all task lists."""
        db_task_lists = self.db.query(TaskListModel).all()
        return [self._to_entity(db_task_list) for db_task_list in db_task_lists]

    def update(self, task_list: TaskList) -> TaskList:
        """Update a task list."""
        db_task_list = (
            self.db.query(TaskListModel)
            .filter(TaskListModel.id == task_list.id)
            .first()
        )

        if not db_task_list:
            raise ValueError(f"TaskList with id {task_list.id} not found")

        # Update fields
        db_task_list.name = task_list.name
        db_task_list.description = task_list.description
        db_task_list.updated_at = task_list.updated_at

        self.db.commit()
        self.db.refresh(db_task_list)

        return self._to_entity(db_task_list)

    def delete(self, task_list_id: int) -> bool:
        """Delete a task list."""
        db_task_list = (
            self.db.query(TaskListModel)
            .filter(TaskListModel.id == task_list_id)
            .first()
        )

        if not db_task_list:
            return False

        self.db.delete(db_task_list)
        self.db.commit()
        return True

    def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a task list exists by name."""
        query = self.db.query(TaskListModel).filter(TaskListModel.name == name)

        if exclude_id:
            query = query.filter(TaskListModel.id != exclude_id)

        return query.first() is not None

    def _to_entity(self, db_task_list: TaskListModel) -> TaskList:
        """Convert SQLAlchemy model to domain entity."""
        # Get task count
        task_count = (
            self.db.query(TaskModel)
            .filter(TaskModel.task_list_id == db_task_list.id)
            .count()
        )

        # Convert tasks if loaded
        tasks = []
        if hasattr(db_task_list, "tasks") and db_task_list.tasks:
            from .task_repository import SQLTaskRepository

            task_repo = SQLTaskRepository(self.db)
            tasks = [task_repo._to_domain(task) for task in db_task_list.tasks]

        return TaskList(
            id=db_task_list.id,
            name=db_task_list.name,
            description=db_task_list.description,
            created_at=db_task_list.created_at,
            updated_at=db_task_list.updated_at,
            tasks=tasks,
        )
