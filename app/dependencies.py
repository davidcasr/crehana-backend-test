"""Dependency injection for the application."""

from sqlalchemy.orm import Session
from fastapi import Depends

from .infrastructure.database.connection import get_db
from .infrastructure.repositories.task_list_repository import SQLTaskListRepository
from .infrastructure.repositories.task_repository import SQLTaskRepository
from .infrastructure.repositories.user_repository import SQLUserRepository
from .infrastructure.services.email_service import get_email_service, EmailService
from .application.use_cases.task_list import TaskListUseCases
from .application.use_cases.task import TaskUseCases
from .application.use_cases.user import UserUseCases


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
    task_list_repository: SQLTaskListRepository = Depends(get_task_list_repository),
) -> TaskListUseCases:
    """Get task list use cases with dependency injection."""
    return TaskListUseCases(task_list_repository)


def get_task_use_cases(
    task_repository: SQLTaskRepository = Depends(get_task_repository),
    task_list_repository: SQLTaskListRepository = Depends(get_task_list_repository),
    user_repository: SQLUserRepository = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
) -> TaskUseCases:
    """Get task use cases with dependency injection."""
    return TaskUseCases(
        task_repository, task_list_repository, user_repository, email_service
    )


def get_user_use_cases(
    user_repository: SQLUserRepository = Depends(get_user_repository),
) -> UserUseCases:
    """Get user use cases with dependency injection."""
    return UserUseCases(user_repository)
