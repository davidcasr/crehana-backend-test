"""Tests unitarios para UserUseCases."""
import pytest
from unittest.mock import Mock
from datetime import datetime
from app.application.use_cases.user import UserUseCases
from app.domain.models.entities import User
from app.domain.models.enums import UserStatus
from app.domain.exceptions import (
    EntityNotFoundException,
    InvalidDataException,
    DuplicateEntityException
)


@pytest.mark.unit
class TestUserUseCases:
    """Tests para UserUseCases."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.mock_repository = Mock()
        self.user_use_cases = UserUseCases(self.mock_repository)
        
        # Usuario de ejemplo
        self.sample_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.ACTIVE,
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_create_user_success(self):
        """Test crear usuario exitosamente."""
        # Arrange
        self.mock_repository.exists_by_username.return_value = False
        self.mock_repository.exists_by_email.return_value = False
        self.mock_repository.create.return_value = self.sample_user
        
        # Act
        result = self.user_use_cases.create_user(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed_password"
        )
        
        # Assert
        assert result == self.sample_user
        self.mock_repository.exists_by_username.assert_called_once_with("testuser")
        self.mock_repository.exists_by_email.assert_called_once_with("test@example.com")
        self.mock_repository.create.assert_called_once()
    
    def test_create_user_duplicate_username(self):
        """Test crear usuario con username duplicado."""
        # Arrange
        self.mock_repository.exists_by_username.return_value = True
        
        # Act & Assert
        with pytest.raises(DuplicateEntityException, match="User with username 'testuser' already exists"):
            self.user_use_cases.create_user(
                username="testuser",
                email="test@example.com",
                full_name="Test User"
            )
    
    def test_create_user_duplicate_email(self):
        """Test crear usuario con email duplicado."""
        # Arrange
        self.mock_repository.exists_by_username.return_value = False
        self.mock_repository.exists_by_email.return_value = True
        
        # Act & Assert
        with pytest.raises(DuplicateEntityException, match="User with email 'test@example.com' already exists"):
            self.user_use_cases.create_user(
                username="testuser",
                email="test@example.com",
                full_name="Test User"
            )
    
    def test_create_user_invalid_username(self):
        """Test crear usuario con username inválido."""
        # Act & Assert
        with pytest.raises(InvalidDataException, match="Username must be at least 3 characters long"):
            self.user_use_cases.create_user(
                username="ab",  # Muy corto
                email="test@example.com",
                full_name="Test User"
            )
    
    def test_create_user_invalid_email(self):
        """Test crear usuario con email inválido."""
        # Act & Assert
        with pytest.raises(InvalidDataException, match="Invalid email format"):
            self.user_use_cases.create_user(
                username="testuser",
                email="invalid-email",  # Sin @
                full_name="Test User"
            )
    
    def test_get_user_by_id_success(self):
        """Test obtener usuario por ID exitosamente."""
        # Arrange
        self.mock_repository.get_by_id.return_value = self.sample_user
        
        # Act
        result = self.user_use_cases.get_user_by_id(1)
        
        # Assert
        assert result == self.sample_user
        self.mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_user_by_id_not_found(self):
        """Test obtener usuario por ID no encontrado."""
        # Arrange
        self.mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="User with id 999 not found"):
            self.user_use_cases.get_user_by_id(999)
    
    def test_get_user_by_username_success(self):
        """Test obtener usuario por username exitosamente."""
        # Arrange
        self.mock_repository.get_by_username.return_value = self.sample_user
        
        # Act
        result = self.user_use_cases.get_user_by_username("testuser")
        
        # Assert
        assert result == self.sample_user
        self.mock_repository.get_by_username.assert_called_once_with("testuser")
    
    def test_get_user_by_username_not_found(self):
        """Test obtener usuario por username no encontrado."""
        # Arrange
        self.mock_repository.get_by_username.return_value = None
        
        # Act & Assert
        with pytest.raises(EntityNotFoundException, match="User with username 'nonexistent' not found"):
            self.user_use_cases.get_user_by_username("nonexistent")
    
    def test_get_all_users_success(self):
        """Test obtener todos los usuarios exitosamente."""
        # Arrange
        users = [self.sample_user]
        self.mock_repository.get_all.return_value = users
        
        # Act
        result = self.user_use_cases.get_all_users()
        
        # Assert
        assert result == users
        self.mock_repository.get_all.assert_called_once_with(None)
    
    def test_get_all_users_with_status_filter(self):
        """Test obtener usuarios con filtro de estado."""
        # Arrange
        users = [self.sample_user]
        self.mock_repository.get_all.return_value = users
        
        # Act
        result = self.user_use_cases.get_all_users(status=UserStatus.ACTIVE)
        
        # Assert
        assert result == users
        self.mock_repository.get_all.assert_called_once_with(UserStatus.ACTIVE)
    
    def test_update_user_success(self):
        """Test actualizar usuario exitosamente."""
        # Arrange
        updated_user = User(
            id=1,
            username="updateduser",
            email="updated@example.com",
            full_name="Updated User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_repository.get_by_id.return_value = self.sample_user
        self.mock_repository.exists_by_username.return_value = False
        self.mock_repository.exists_by_email.return_value = False
        self.mock_repository.update.return_value = updated_user
        
        # Act
        result = self.user_use_cases.update_user(
            user_id=1,
            username="updateduser",
            email="updated@example.com",
            full_name="Updated User"
        )
        
        # Assert
        assert result == updated_user
        self.mock_repository.get_by_id.assert_called_once_with(1)
        self.mock_repository.update.assert_called_once()
    
    def test_delete_user_success(self):
        """Test eliminar usuario exitosamente."""
        # Arrange
        self.mock_repository.get_by_id.return_value = self.sample_user
        self.mock_repository.delete.return_value = True
        
        # Act
        result = self.user_use_cases.delete_user(1)
        
        # Assert
        assert result is True
        self.mock_repository.get_by_id.assert_called_once_with(1)
        self.mock_repository.delete.assert_called_once_with(1)
    
    def test_deactivate_user_success(self):
        """Test desactivar usuario exitosamente."""
        # Arrange
        deactivated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.INACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_repository.get_by_id.return_value = self.sample_user
        self.mock_repository.exists_by_username.return_value = False
        self.mock_repository.exists_by_email.return_value = False
        self.mock_repository.update.return_value = deactivated_user
        
        # Act
        result = self.user_use_cases.deactivate_user(1)
        
        # Assert
        assert result == deactivated_user
        assert result.status == UserStatus.INACTIVE
    
    def test_activate_user_success(self):
        """Test activar usuario exitosamente."""
        # Arrange
        activated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_repository.get_by_id.return_value = self.sample_user
        self.mock_repository.exists_by_username.return_value = False
        self.mock_repository.exists_by_email.return_value = False
        self.mock_repository.update.return_value = activated_user
        
        # Act
        result = self.user_use_cases.activate_user(1)
        
        # Assert
        assert result == activated_user
        assert result.status == UserStatus.ACTIVE
    
    def test_authenticate_user_success(self):
        """Test autenticar usuario exitosamente."""
        # Arrange
        self.mock_repository.get_by_username.return_value = self.sample_user
        
        # Act
        result = self.user_use_cases.authenticate_user("testuser")
        
        # Assert
        assert result == self.sample_user
        self.mock_repository.get_by_username.assert_called_once_with("testuser")
    
    def test_authenticate_user_by_email_success(self):
        """Test autenticar usuario por email exitosamente."""
        # Arrange
        self.mock_repository.get_by_username.side_effect = EntityNotFoundException("Not found")
        self.mock_repository.get_by_email.return_value = self.sample_user
        
        # Act
        result = self.user_use_cases.authenticate_user("test@example.com")
        
        # Assert
        assert result == self.sample_user
        self.mock_repository.get_by_username.assert_called_once_with("test@example.com")
        self.mock_repository.get_by_email.assert_called_once_with("test@example.com")
    
    def test_authenticate_user_not_found(self):
        """Test autenticar usuario no encontrado."""
        # Arrange
        self.mock_repository.get_by_username.side_effect = EntityNotFoundException("Not found")
        self.mock_repository.get_by_email.side_effect = EntityNotFoundException("Not found")
        
        # Act
        result = self.user_use_cases.authenticate_user("nonexistent")
        
        # Assert
        assert result is None 