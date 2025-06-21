"""Dependency injection for the application."""

from functools import lru_cache
from sqlalchemy.orm import Session

from .infrastructure.database.connection import SessionLocal
from .infrastructure.repositories.task_list_repository import SQLTaskListRepository
from .infrastructure.repositories.task_repository import SQLTaskRepository
from .application.use_cases.task_list import TaskListUseCases
from .application.use_cases.task import TaskUseCases


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_list_repository(db: Session) -> SQLTaskListRepository:
    """Get task list repository."""
    return SQLTaskListRepository(db)


def get_task_repository(db: Session) -> SQLTaskRepository:
    """Get task repository."""
    return SQLTaskRepository(db)


def get_task_list_use_cases(
    db: Session,
    task_list_repo: SQLTaskListRepository = None,
    task_repo: SQLTaskRepository = None
) -> TaskListUseCases:
    """Get task list use cases with dependency injection."""
    if task_list_repo is None:
        task_list_repo = get_task_list_repository(db)
    if task_repo is None:
        task_repo = get_task_repository(db)
    
    return TaskListUseCases(task_list_repo, task_repo)


def get_task_use_cases(
    db: Session,
    task_repo: SQLTaskRepository = None,
    task_list_repo: SQLTaskListRepository = None
) -> TaskUseCases:
    """Get task use cases with dependency injection."""
    if task_repo is None:
        task_repo = get_task_repository(db)
    if task_list_repo is None:
        task_list_repo = get_task_list_repository(db)
    
    return TaskUseCases(task_repo, task_list_repo) 