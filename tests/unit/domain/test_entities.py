"""
Tests unitarios para las entidades del dominio.
"""
import pytest
from datetime import datetime, timedelta
from app.domain.models.entities import User, TaskList, Task
from app.domain.models.enums import UserStatus, TaskStatus, TaskPriority
from app.domain.exceptions import InvalidDataException


@pytest.mark.unit
class TestUser:
    """Tests para la entidad User."""
    
    def test_create_user_valid_data(self):
        """Test crear usuario con datos válidos."""
        # Arrange & Act
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.ACTIVE,
            password_hash="hashed_password",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Assert
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.status == UserStatus.ACTIVE
        assert user.password_hash == "hashed_password"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_is_active_property(self):
        """Test propiedad is_active del usuario."""
        # Arrange
        active_user = User(
            id=1,
            username="activeuser",
            email="active@example.com",
            full_name="Active User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        inactive_user = User(
            id=2,
            username="inactiveuser",
            email="inactive@example.com",
            full_name="Inactive User",
            status=UserStatus.INACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act & Assert
        assert active_user.is_active is True
        assert inactive_user.is_active is False
    
    def test_user_without_password_hash(self):
        """Test crear usuario sin password hash."""
        # Arrange & Act
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Assert
        assert user.password_hash is None
    
    def test_user_string_representation(self):
        """Test representación string del usuario."""
        # Arrange
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        result = str(user)
        
        # Assert
        assert "testuser" in result


@pytest.mark.unit
class TestTaskList:
    """Tests para la entidad TaskList."""
    
    def test_create_task_list_valid_data(self):
        """Test crear lista de tareas con datos válidos."""
        # Arrange & Act
        task_list = TaskList(
            id=1,
            name="Test List",
            description="A test task list",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Assert
        assert task_list.id == 1
        assert task_list.name == "Test List"
        assert task_list.description == "A test task list"
        assert isinstance(task_list.created_at, datetime)
        assert isinstance(task_list.updated_at, datetime)
    
    def test_task_list_without_description(self):
        """Test crear lista de tareas sin descripción."""
        # Arrange & Act
        task_list = TaskList(
            id=1,
            name="Test List",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Assert
        assert task_list.description is None
    
    def test_task_list_string_representation(self):
        """Test representación string de la lista de tareas."""
        # Arrange
        task_list = TaskList(
            id=1,
            name="Test List",
            description="A test task list",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        result = str(task_list)
        
        # Assert
        assert "Test List" in result


@pytest.mark.unit
class TestTask:
    """Tests para la entidad Task."""
    
    def test_create_task_valid_data(self):
        """Test crear tarea con datos válidos."""
        # Arrange & Act
        task = Task(
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
        
        # Assert
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "A test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.task_list_id == 1
        assert task.assigned_user_id is None
        assert task.due_date is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
    
    def test_task_is_completed_property(self):
        """Test propiedad is_completed de la tarea."""
        # Arrange
        pending_task = Task(
            id=1,
            title="Pending Task",
            description="A pending task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        completed_task = Task(
            id=2,
            title="Completed Task",
            description="A completed task",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act & Assert
        assert pending_task.is_completed is False
        assert completed_task.is_completed is True
    
    def test_task_is_overdue_property(self):
        """Test propiedad is_overdue de la tarea."""
        # Arrange
        past_due_date = datetime.now() - timedelta(days=1)
        future_due_date = datetime.now() + timedelta(days=1)
        
        overdue_task = Task(
            id=1,
            title="Overdue Task",
            description="An overdue task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            due_date=past_due_date,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        not_overdue_task = Task(
            id=2,
            title="Not Overdue Task",
            description="A task not overdue",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            due_date=future_due_date,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        no_due_date_task = Task(
            id=3,
            title="No Due Date Task",
            description="A task without due date",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            due_date=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act & Assert
        assert overdue_task.is_overdue is True
        assert not_overdue_task.is_overdue is False
        assert no_due_date_task.is_overdue is False
    
    def test_task_with_assigned_user(self):
        """Test crear tarea con usuario asignado."""
        # Arrange & Act
        task = Task(
            id=1,
            title="Assigned Task",
            description="A task with assigned user",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            task_list_id=1,
            assigned_user_id=123,
            due_date=datetime.now() + timedelta(days=7),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Assert
        assert task.assigned_user_id == 123
        assert task.due_date is not None
    
    def test_task_string_representation(self):
        """Test representación string de la tarea."""
        # Arrange
        task = Task(
            id=1,
            title="Test Task",
            description="A test task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            task_list_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act
        result = str(task)
        
        # Assert
        assert "Test Task" in result 