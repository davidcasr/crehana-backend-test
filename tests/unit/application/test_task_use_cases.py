"""Tests unitarios para TaskUseCases."""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from app.application.use_cases.task import TaskUseCases
from app.domain.models.entities import Task, User
from app.domain.models.enums import TaskStatus, TaskPriority, UserStatus
from app.domain.exceptions import (
    EntityNotFoundException,
    InvalidDataException,
    DuplicateEntityException
)


@pytest.mark.unit
class TestTaskUseCases:
    """Tests para TaskUseCases."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.mock_task_repository = Mock()
        self.mock_task_list_repository = Mock()
        self.mock_user_repository = Mock()
        self.mock_email_service = Mock()
        
        self.task_use_cases = TaskUseCases(
            task_repository=self.mock_task_repository,
            task_list_repository=self.mock_task_list_repository,
            user_repository=self.mock_user_repository,
            email_service=self.mock_email_service
        )
        
        # Tarea de ejemplo
        self.sample_task = Task(
            id=1,
            title="Test Task",
            description="A test task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            assigned_user_id=None,
            due_date=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Usuario de ejemplo
        self.sample_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_create_task_success(self):
        """Test crear tarea exitosamente."""
        # Arrange
        self.mock_task_list_repository.get_by_id.return_value = Mock(id=1, name="Test List")
        self.mock_task_repository.exists_by_title_in_list.return_value = False
        self.mock_task_repository.create.return_value = self.sample_task
        
        # Act
        result = self.task_use_cases.create_task(
            title="Test Task",
            description="A test task",
            task_list_id=1,
            priority=TaskPriority.MEDIUM,
            due_date=None,
            assigned_user_id=None
        )
        
        # Assert
        assert result == self.sample_task
        self.mock_task_list_repository.get_by_id.assert_called_once_with(1)
        self.mock_task_repository.exists_by_title_in_list.assert_called_once_with("Test Task", 1)
        self.mock_task_repository.create.assert_called_once()
        self.mock_email_service.send_task_assignment_email.assert_not_called()
    
    def test_create_task_with_assigned_user(self):
        """Test crear tarea con usuario asignado."""
        # Arrange
        task_with_user = Task(
            id=1,
            title="Test Task",
            description="A test task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            assigned_user_id=1,
            due_date=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_task_list_repository.get_by_id.return_value = Mock(id=1, name="Test List")
        self.mock_task_repository.exists_by_title_in_list.return_value = False
        self.mock_user_repository.get_by_id.return_value = self.sample_user
        self.mock_task_repository.create.return_value = task_with_user
        
        # Act
        result = self.task_use_cases.create_task(
            title="Test Task",
            description="A test task",
            task_list_id=1,
            priority=TaskPriority.MEDIUM,
            due_date=None,
            assigned_user_id=1
        )
        
        # Assert
        assert result == task_with_user
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_email_service.send_task_assignment_email.assert_called_once()
    
    def test_create_task_duplicate_title(self):
        """Test crear tarea con título duplicado en la misma lista."""
        # Arrange
        self.mock_task_list_repository.get_by_id.return_value = Mock(id=1, name="Test List")
        self.mock_task_repository.exists_by_title_in_list.return_value = True
        
        # Act & Assert
        with pytest.raises(DuplicateEntityException, match="already exists in this list"):
            self.task_use_cases.create_task(
                title="Test Task",
                description="A test task",
                task_list_id=1,
                priority=TaskPriority.MEDIUM,
                due_date=None,
                assigned_user_id=None
            )
    
    def test_create_task_task_list_not_found(self):
        """Test crear tarea con lista inexistente."""
        # Arrange
        self.mock_task_list_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="Task list with id 999 not found"):
            self.task_use_cases.create_task(
                title="Test Task",
                description="A test task",
                task_list_id=999,
                priority=TaskPriority.MEDIUM,
                due_date=None,
                assigned_user_id=None
            )
    
    def test_create_task_assigned_user_not_found(self):
        """Test crear tarea con usuario asignado inexistente."""
        # Arrange
        self.mock_task_list_repository.get_by_id.return_value = Mock(id=1, name="Test List")
        self.mock_task_repository.exists_by_title_in_list.return_value = False
        self.mock_user_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="User with id 999 not found"):
            self.task_use_cases.create_task(
                title="Test Task",
                description="A test task",
                task_list_id=1,
                priority=TaskPriority.MEDIUM,
                due_date=None,
                assigned_user_id=999
            )
    
    def test_get_task_by_id_success(self):
        """Test obtener tarea por ID exitosamente."""
        # Arrange
        self.mock_task_repository.get_by_id.return_value = self.sample_task
        
        # Act
        result = self.task_use_cases.get_task_by_id(1)
        
        # Assert
        assert result == self.sample_task
        self.mock_task_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_task_by_id_not_found(self):
        """Test obtener tarea por ID no encontrada."""
        # Arrange
        self.mock_task_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="Task with id 999 not found"):
            self.task_use_cases.get_task_by_id(999)
    
    def test_get_tasks_by_list_id_success(self):
        """Test obtener tareas por lista exitosamente."""
        # Arrange
        tasks = [self.sample_task]
        self.mock_task_list_repository.get_by_id.return_value = Mock(id=1, name="Test List")
        self.mock_task_repository.get_filtered_tasks.return_value = tasks
        
        # Act
        result = self.task_use_cases.get_tasks_by_list_id(1)
        
        # Assert
        assert result == tasks
        self.mock_task_list_repository.get_by_id.assert_called_once_with(1)
        self.mock_task_repository.get_filtered_tasks.assert_called_once_with(
            1, None, None, None
        )
    
    def test_get_tasks_by_list_id_with_filters(self):
        """Test obtener tareas por lista con filtros."""
        # Arrange
        tasks = [self.sample_task]
        self.mock_task_list_repository.get_by_id.return_value = Mock(id=1, name="Test List")
        self.mock_user_repository.get_by_id.return_value = self.sample_user
        self.mock_task_repository.get_filtered_tasks.return_value = tasks
        
        # Act
        result = self.task_use_cases.get_tasks_by_list_id(
            task_list_id=1,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            assigned_user_id=1
        )
        
        # Assert
        assert result == tasks
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_task_repository.get_filtered_tasks.assert_called_once_with(
            1, TaskStatus.PENDING, TaskPriority.HIGH, 1
        )
    
    def test_get_tasks_by_user_id_success(self):
        """Test obtener tareas por usuario exitosamente."""
        # Arrange
        tasks = [self.sample_task]
        self.mock_user_repository.get_by_id.return_value = self.sample_user
        self.mock_task_repository.get_by_assigned_user_id.return_value = tasks
        
        # Act
        result = self.task_use_cases.get_tasks_by_user_id(1)
        
        # Assert
        assert result == tasks
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_task_repository.get_by_assigned_user_id.assert_called_once_with(1)
    
    def test_update_task_success(self):
        """Test actualizar tarea exitosamente."""
        # Arrange
        updated_task = Task(
            id=1,
            title="Updated Task",
            description="Updated description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            task_list_id=1,
            assigned_user_id=1,
            due_date=datetime.now() + timedelta(days=7),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_task_repository.get_by_id.return_value = self.sample_task
        self.mock_task_repository.exists_by_title_in_list.return_value = False
        self.mock_user_repository.get_by_id.return_value = self.sample_user
        self.mock_task_repository.update.return_value = updated_task
        
        # Act
        result = self.task_use_cases.update_task(
            task_id=1,
            title="Updated Task",
            description="Updated description",
            priority=TaskPriority.HIGH,
            due_date=datetime.now() + timedelta(days=7),
            assigned_user_id=1
        )
        
        # Assert
        assert result == updated_task
        self.mock_task_repository.get_by_id.assert_called_once_with(1)
        self.mock_task_repository.update.assert_called_once()
    
    def test_delete_task_success(self):
        """Test eliminar tarea exitosamente."""
        # Arrange
        self.mock_task_repository.get_by_id.return_value = self.sample_task
        self.mock_task_repository.delete.return_value = True
        
        # Act
        result = self.task_use_cases.delete_task(1)
        
        # Assert
        assert result is True
        self.mock_task_repository.get_by_id.assert_called_once_with(1)
        self.mock_task_repository.delete.assert_called_once_with(1)
    
    def test_delete_task_not_found(self):
        """Test eliminar tarea no encontrada."""
        # Arrange
        self.mock_task_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="Task with id 999 not found"):
            self.task_use_cases.delete_task(999) 