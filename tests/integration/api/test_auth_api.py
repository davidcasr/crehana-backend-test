"""Tests de integración para la API de autenticación."""
import pytest
from fastapi.testclient import TestClient
from app.domain.models.entities import User


@pytest.mark.integration
class TestAuthAPI:
    """Tests de integración para endpoints de autenticación."""
    
    def test_register_user_success(self, client: TestClient):
        """Test registrar usuario exitosamente."""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "secure_password_123"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["status"] == "active"
        assert "password" not in data  # No debe devolver password
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_register_user_duplicate_username(self, client: TestClient, sample_user):
        """Test registrar usuario con username duplicado."""
        # Arrange
        user_data = {
            "username": sample_user.username,  # Username ya existe
            "email": "different@example.com",
            "full_name": "Different User",
            "password": "secure_password_123"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 409
        assert f"User with username '{sample_user.username}' already exists" in response.json()["detail"]
    
    def test_register_user_duplicate_email(self, client: TestClient, sample_user):
        """Test registrar usuario con email duplicado."""
        # Arrange
        user_data = {
            "username": "differentuser",
            "email": sample_user.email,  # Email ya existe
            "full_name": "Different User",
            "password": "secure_password_123"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 409
        assert f"User with email '{sample_user.email}' already exists" in response.json()["detail"]
    
    def test_register_user_invalid_data(self, client: TestClient):
        """Test registrar usuario con datos inválidos."""
        # Arrange
        user_data = {
            "username": "ab",  # Muy corto
            "email": "invalid-email",  # Email inválido
            "full_name": "",  # Vacío
            "password": "123"  # Muy corta
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, client: TestClient, sample_user):
        """Test login exitoso."""
        # Arrange
        login_data = {
            "username": sample_user.username,
            "password": "secret"  # Password del fixture
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    def test_login_with_email_success(self, client: TestClient, sample_user):
        """Test login con email exitoso."""
        # Arrange
        login_data = {
            "username": sample_user.email,  # Usar email en lugar de username
            "password": "secret"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, sample_user):
        """Test login con credenciales inválidas."""
        # Arrange
        login_data = {
            "username": sample_user.username,
            "password": "wrong_password"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        assert "Usuario o contraseña incorrectos" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login con usuario inexistente."""
        # Arrange
        login_data = {
            "username": "nonexistent",
            "password": "any_password"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        assert "Usuario o contraseña incorrectos" in response.json()["detail"]
    
    def test_login_form_success(self, client: TestClient, sample_user):
        """Test login form (compatible con Swagger UI)."""
        # Arrange
        form_data = {
            "username": sample_user.username,
            "password": "secret"
        }
        
        # Act
        response = client.post("/api/v1/auth/login-form", data=form_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_get_current_user_success(self, client: TestClient, auth_headers, sample_user):
        """Test obtener usuario actual con token válido."""
        # Act
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user.id
        assert data["username"] == sample_user.username
        assert data["email"] == sample_user.email
        assert data["full_name"] == sample_user.full_name
        assert data["status"] == sample_user.status.value
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test obtener usuario actual sin token."""
        # Act
        response = client.get("/api/v1/auth/me")
        
        # Assert
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test obtener usuario actual con token inválido."""
        # Arrange
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        # Act
        response = client.get("/api/v1/auth/me", headers=invalid_headers)
        
        # Assert
        assert response.status_code == 401
        assert "Token inválido" in response.json()["detail"]
    
    def test_change_password_success(self, client: TestClient, auth_headers):
        """Test cambiar contraseña exitosamente."""
        # Arrange
        password_data = {
            "current_password": "secret",
            "new_password": "new_secure_password_123"
        }
        
        # Act
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Contraseña actualizada exitosamente" in data["message"]
    
    def test_change_password_wrong_current(self, client: TestClient, auth_headers):
        """Test cambiar contraseña con contraseña actual incorrecta."""
        # Arrange
        password_data = {
            "current_password": "wrong_password",
            "new_password": "new_secure_password_123"
        }
        
        # Act
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 400
        assert "Contraseña actual incorrecta" in response.json()["detail"]
    
    def test_change_password_unauthorized(self, client: TestClient):
        """Test cambiar contraseña sin autenticación."""
        # Arrange
        password_data = {
            "current_password": "secret",
            "new_password": "new_secure_password_123"
        }
        
        # Act
        response = client.post("/api/v1/auth/change-password", json=password_data)
        
        # Assert
        assert response.status_code == 403
    
    def test_change_password_weak_password(self, client: TestClient, auth_headers):
        """Test cambiar contraseña con contraseña débil."""
        # Arrange
        password_data = {
            "current_password": "secret",
            "new_password": "123"  # Muy débil
        }
        
        # Act
        response = client.post("/api/v1/auth/change-password", json=password_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 422  # Validation error 