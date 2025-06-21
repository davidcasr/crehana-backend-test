"""
Configuración global de pytest y fixtures compartidas.
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.main import app
from app.infrastructure.database.base import Base
from app.infrastructure.database.connection import get_db
from app.dependencies import (
    get_user_use_cases,
    get_task_use_cases,
    get_task_list_use_cases,
)
from app.application.use_cases.user import UserUseCases
from app.application.use_cases.task import TaskUseCases
from app.application.use_cases.task_list import TaskListUseCases
from app.infrastructure.repositories.user_repository import SQLUserRepository
from app.infrastructure.repositories.task_repository import SQLTaskRepository
from app.infrastructure.repositories.task_list_repository import SQLTaskListRepository
from app.infrastructure.services.email_service import MockEmailService
from app.auth.jwt_handler import create_access_token
from app.domain.models.entities import User
from app.domain.models.enums import UserStatus

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Crea una sesión de base de datos para cada test.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Limpiar todas las tablas después de cada test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """
    Cliente de pruebas de FastAPI con base de datos de prueba.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_email_service():
    """Mock del servicio de email."""
    return MockEmailService()


@pytest.fixture
def user_repository(db_session: Session):
    """Repository de usuarios para tests."""
    return SQLUserRepository(db_session)


@pytest.fixture
def task_repository(db_session: Session):
    """Repository de tareas para tests."""
    return SQLTaskRepository(db_session)


@pytest.fixture
def task_list_repository(db_session: Session):
    """Repository de listas de tareas para tests."""
    return SQLTaskListRepository(db_session)


@pytest.fixture
def user_use_cases(user_repository: SQLUserRepository):
    """Use cases de usuarios para tests."""
    return UserUseCases(user_repository)


@pytest.fixture
def task_use_cases(task_repository: SQLTaskRepository, task_list_repository: SQLTaskListRepository, user_repository: SQLUserRepository, mock_email_service):
    """Use cases de tareas para tests."""
    return TaskUseCases(task_repository, task_list_repository, user_repository, mock_email_service)


@pytest.fixture
def task_list_use_cases(task_list_repository: SQLTaskListRepository):
    """Use cases de listas de tareas para tests."""
    return TaskListUseCases(task_list_repository)


@pytest.fixture
def sample_user_data():
    """Datos de ejemplo para crear usuarios."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "status": UserStatus.ACTIVE,
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # secret
    }


@pytest.fixture
def sample_user(user_use_cases: UserUseCases, sample_user_data):
    """Usuario de ejemplo creado en la base de datos."""
    return user_use_cases.create_user(
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        full_name=sample_user_data["full_name"],
        status=sample_user_data["status"],
        password_hash=sample_user_data["password_hash"]
    )


@pytest.fixture
def auth_token(sample_user: User):
    """Token JWT válido para autenticación en tests."""
    return create_access_token(data={"sub": str(sample_user.id)})


@pytest.fixture
def auth_headers(auth_token: str):
    """Headers de autenticación para requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_task_list_data():
    """Datos de ejemplo para crear listas de tareas."""
    return {
        "name": "Test Task List",
        "description": "A test task list for testing purposes"
    }


@pytest.fixture
def sample_task_list(task_list_use_cases: TaskListUseCases, sample_task_list_data):
    """Lista de tareas de ejemplo creada en la base de datos."""
    return task_list_use_cases.create_task_list(
        name=sample_task_list_data["name"],
        description=sample_task_list_data["description"]
    )


@pytest.fixture
def sample_task_data():
    """Datos de ejemplo para crear tareas."""
    return {
        "title": "Test Task",
        "description": "A test task for testing purposes",
        "priority": "medium",
        "due_date": None
    } 