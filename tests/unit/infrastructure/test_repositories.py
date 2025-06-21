"""Tests unitarios para repositorios de infraestructura."""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from app.infrastructure.repositories.user_repository import SQLUserRepository
from app.infrastructure.repositories.task_repository import SQLTaskRepository
from app.infrastructure.repositories.task_list_repository import SQLTaskListRepository
from app.infrastructure.models.user import UserModel
from app.infrastructure.models.task import TaskModel
from app.infrastructure.models.task_list import TaskListModel
from app.domain.models.entities import User, Task, TaskList
from app.domain.models.enums import UserStatus, TaskStatus, TaskPriority


@pytest.mark.unit
class TestSQLUserRepository:
    """Tests para SQLUserRepository."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.mock_session = Mock()
        self.repository = SQLUserRepository(self.mock_session)
    
    def test_repository_initialization(self):
        """Test inicialización del repositorio."""
        # Assert
        assert self.repository.db == self.mock_session
        assert hasattr(self.repository, 'create')
        assert hasattr(self.repository, 'get_by_id')
        assert hasattr(self.repository, 'get_by_username')
        assert hasattr(self.repository, 'get_by_email')
        assert hasattr(self.repository, 'get_all')
        assert hasattr(self.repository, 'update')
        assert hasattr(self.repository, 'delete')
        assert hasattr(self.repository, 'exists_by_username')
        assert hasattr(self.repository, 'exists_by_email')
    
    def test_repository_has_required_methods(self):
        """Test que el repositorio tiene todos los métodos requeridos."""
        # Assert - Métodos básicos CRUD
        assert callable(getattr(self.repository, 'create', None))
        assert callable(getattr(self.repository, 'get_by_id', None))
        assert callable(getattr(self.repository, 'get_all', None))
        assert callable(getattr(self.repository, 'update', None))
        assert callable(getattr(self.repository, 'delete', None))
        
        # Métodos específicos de User
        assert callable(getattr(self.repository, 'get_by_username', None))
        assert callable(getattr(self.repository, 'get_by_email', None))
        assert callable(getattr(self.repository, 'exists_by_username', None))
        assert callable(getattr(self.repository, 'exists_by_email', None))


@pytest.mark.unit
class TestSQLTaskListRepository:
    """Tests para SQLTaskListRepository."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.mock_session = Mock()
        self.repository = SQLTaskListRepository(self.mock_session)
    
    def test_repository_initialization(self):
        """Test inicialización del repositorio."""
        # Assert
        assert self.repository.db == self.mock_session
        assert hasattr(self.repository, 'create')
        assert hasattr(self.repository, 'get_by_id')
        assert hasattr(self.repository, 'get_all')
        assert hasattr(self.repository, 'update')
        assert hasattr(self.repository, 'delete')
        assert hasattr(self.repository, 'exists_by_name')
    
    def test_repository_has_required_methods(self):
        """Test que el repositorio tiene todos los métodos requeridos."""
        # Assert - Métodos básicos CRUD
        assert callable(getattr(self.repository, 'create', None))
        assert callable(getattr(self.repository, 'get_by_id', None))
        assert callable(getattr(self.repository, 'get_all', None))
        assert callable(getattr(self.repository, 'update', None))
        assert callable(getattr(self.repository, 'delete', None))
        
        # Métodos específicos de TaskList
        assert callable(getattr(self.repository, 'exists_by_name', None)) 