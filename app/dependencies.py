"""Dependency injection for the application."""

from functools import lru_cache
from sqlalchemy.orm import Session
from fastapi import Depends

from .infrastructure.database.connection import SessionLocal
from .infrastructure.repositories.task_list_repository import SQLTaskListRepository
from .infrastructure.repositories.task_repository import SQLTaskRepository
from .infrastructure.repositories.user_repository import SQLUserRepository
from .application.use_cases.task_list import TaskListUseCases
from .application.use_cases.task import TaskUseCases
from .application.use_cases.user import UserUseCases


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_list_repository(db: Session = Depends(get_db)) -> SQLTaskListRepository:
    """Get task list repository."""
    return SQLTaskListRepository(db)


def get_task_repository(db: Session = Depends(get_db)) -> SQLTaskRepository:
    """Get task repository."""
    return SQLTaskRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> SQLUserRepository:
    """Get user repository."""
    return SQLUserRepository(db)


def get_task_list_use_cases(
    task_list_repo: SQLTaskListRepository = Depends(get_task_list_repository),
    task_repo: SQLTaskRepository = Depends(get_task_repository),
) -> TaskListUseCases:
    """Get task list use cases with dependency injection."""
    return TaskListUseCases(task_list_repo, task_repo)


def get_task_use_cases(
    task_repo: SQLTaskRepository = Depends(get_task_repository),
    task_list_repo: SQLTaskListRepository = Depends(get_task_list_repository),
    user_repo: SQLUserRepository = Depends(get_user_repository),
) -> TaskUseCases:
    """Get task use cases with dependency injection."""
    return TaskUseCases(task_repo, task_list_repo, user_repo)


def get_user_use_cases(
    user_repo: SQLUserRepository = Depends(get_user_repository),
) -> UserUseCases:
    """Get user use cases with dependency injection."""
    return UserUseCases(user_repo)
