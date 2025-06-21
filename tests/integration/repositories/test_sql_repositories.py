"""Tests de integración para repositorios SQL."""
import pytest
from datetime import datetime
from app.infrastructure.repositories.user_repository import SQLUserRepository
from app.infrastructure.repositories.task_repository import SQLTaskRepository
from app.infrastructure.repositories.task_list_repository import SQLTaskListRepository
from app.domain.models.entities import User, Task, TaskList
from app.domain.models.enums import UserStatus, TaskStatus, TaskPriority


@pytest.mark.integration
class TestSQLUserRepositoryIntegration:
    """Tests de integración para SQLUserRepository."""
    
    def test_create_and_get_user(self, user_repository: SQLUserRepository):
        """Test crear y obtener usuario."""
        # Arrange
        user = User(
            username="integration_user",
            email="integration@example.com",
            full_name="Integration User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        created_user = user_repository.create(user)
        retrieved_user = user_repository.get_by_id(created_user.id)
        
        # Assert
        assert created_user.id is not None
        assert retrieved_user is not None
        assert retrieved_user.username == "integration_user"
        assert retrieved_user.email == "integration@example.com"
    
    def test_get_user_by_username(self, user_repository: SQLUserRepository):
        """Test obtener usuario por username."""
        # Arrange
        user = User(
            username="test_username",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        user_repository.create(user)
        
        # Act
        found_user = user_repository.get_by_username("test_username")
        
        # Assert
        assert found_user is not None
        assert found_user.username == "test_username"
    
    def test_get_user_by_email(self, user_repository: SQLUserRepository):
        """Test obtener usuario por email."""
        # Arrange
        user = User(
            username="email_test",
            email="email_test@example.com",
            full_name="Email Test User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        user_repository.create(user)
        
        # Act
        found_user = user_repository.get_by_email("email_test@example.com")
        
        # Assert
        assert found_user is not None
        assert found_user.email == "email_test@example.com"


@pytest.mark.integration
class TestSQLTaskListRepositoryIntegration:
    """Tests de integración para SQLTaskListRepository."""
    
    def test_create_and_get_task_list(self, task_list_repository: SQLTaskListRepository):
        """Test crear y obtener lista de tareas."""
        # Arrange
        task_list = TaskList(
            name="Integration Task List",
            description="A task list for integration testing",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        created_list = task_list_repository.create(task_list)
        retrieved_list = task_list_repository.get_by_id(created_list.id)
        
        # Assert
        assert created_list.id is not None
        assert retrieved_list is not None
        assert retrieved_list.name == "Integration Task List"
    
    def test_get_task_list_by_name(self, task_list_repository: SQLTaskListRepository):
        """Test verificar si existe lista por nombre."""
        # Arrange
        task_list = TaskList(
            name="Unique List Name",
            description="A unique task list",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        task_list_repository.create(task_list)
        
        # Act
        exists = task_list_repository.exists_by_name("Unique List Name")
        
        # Assert
        assert exists is True
        
        # Verificar que no existe un nombre diferente
        assert task_list_repository.exists_by_name("Non-existent Name") is False


@pytest.mark.integration
class TestSQLTaskRepositoryIntegration:
    """Tests de integración para SQLTaskRepository."""
    
    def test_create_and_get_task(self, task_repository: SQLTaskRepository, sample_task_list):
        """Test crear y obtener tarea."""
        # Arrange
        task = Task(
            title="Integration Task",
            description="A task for integration testing",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=sample_task_list.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        created_task = task_repository.create(task)
        retrieved_task = task_repository.get_by_id(created_task.id)
        
        # Assert
        assert created_task.id is not None
        assert retrieved_task is not None
        assert retrieved_task.title == "Integration Task"
        assert retrieved_task.task_list_id == sample_task_list.id 