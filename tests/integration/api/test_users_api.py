"""Tests de integración para la API de usuarios."""
import pytest
from fastapi.testclient import TestClient
from app.domain.models.enums import UserStatus


@pytest.mark.integration
class TestUsersAPI:
    """Tests de integración para endpoints de usuarios."""
    
    def test_get_user_by_id_not_found(self, client: TestClient, auth_headers):
        """Test obtener usuario por ID no encontrado."""
        # Act
        response = client.get("/api/v1/users/999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_get_user_by_username_not_found(self, client: TestClient, auth_headers):
        """Test obtener usuario por username no encontrado."""
        # Act
        response = client.get("/api/v1/users/by-username/nonexistent", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_get_user_by_email_not_found(self, client: TestClient, auth_headers):
        """Test obtener usuario por email no encontrado."""
        # Act
        response = client.get("/api/v1/users/by-email/nonexistent@example.com", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_user_not_found(self, client: TestClient, auth_headers):
        """Test actualizar usuario no encontrado."""
        # Arrange
        update_data = {"full_name": "New Name"}
        
        # Act
        response = client.put("/api/v1/users/999", json=update_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_user_not_found(self, client: TestClient, auth_headers):
        """Test eliminar usuario no encontrado."""
        # Act
        response = client.delete("/api/v1/users/999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404 