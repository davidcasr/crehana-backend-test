"""Tests de integración para la API de listas de tareas."""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestTaskListsAPI:
    """Tests de integración para endpoints de listas de tareas."""
    
    def test_create_task_list_success(self, client: TestClient, auth_headers):
        """Test crear lista de tareas exitosamente."""
        # Arrange
        task_list_data = {
            "name": "My New Task List",
            "description": "A test task list for integration testing"
        }
        
        # Act
        response = client.post("/api/v1/task-lists/", json=task_list_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My New Task List"
        assert data["description"] == "A test task list for integration testing"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_list_unauthorized(self, client: TestClient):
        """Test crear lista de tareas sin autenticación."""
        # Arrange
        task_list_data = {
            "name": "Unauthorized List",
            "description": "This should fail"
        }
        
        # Act
        response = client.post("/api/v1/task-lists/", json=task_list_data)
        
        # Assert
        assert response.status_code == 403
    
    def test_create_task_list_duplicate_name(self, client: TestClient, auth_headers):
        """Test crear lista de tareas con nombre duplicado."""
        # Arrange
        task_list_data = {
            "name": "Duplicate List",
            "description": "First list"
        }
        
        # Crear primera lista
        client.post("/api/v1/task-lists/", json=task_list_data, headers=auth_headers)
        
        # Act - Intentar crear segunda lista con mismo nombre
        response = client.post("/api/v1/task-lists/", json=task_list_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_create_task_list_invalid_data(self, client: TestClient, auth_headers):
        """Test crear lista de tareas con datos inválidos."""
        # Arrange
        task_list_data = {
            "name": "",  # Nombre vacío
            "description": "x" * 1001  # Descripción muy larga
        }
        
        # Act
        response = client.post("/api/v1/task-lists/", json=task_list_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_get_all_task_lists_success(self, client: TestClient, auth_headers):
        """Test obtener todas las listas de tareas exitosamente."""
        # Arrange - Crear algunas listas
        lists_data = [
            {"name": "List 1", "description": "First list"},
            {"name": "List 2", "description": "Second list"},
            {"name": "List 3", "description": "Third list"}
        ]
        
        created_lists = []
        for list_data in lists_data:
            response = client.post("/api/v1/task-lists/", json=list_data, headers=auth_headers)
            created_lists.append(response.json())
        
        # Act
        response = client.get("/api/v1/task-lists/", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # Al menos las 3 que creamos
        
        # Verificar que nuestras listas están en la respuesta
        list_names = [item["name"] for item in data]
        assert "List 1" in list_names
        assert "List 2" in list_names
        assert "List 3" in list_names
    
    def test_get_all_task_lists_unauthorized(self, client: TestClient):
        """Test obtener listas sin autenticación."""
        # Act
        response = client.get("/api/v1/task-lists/")
        
        # Assert
        assert response.status_code == 403
    
    def test_get_task_list_by_id_success(self, client: TestClient, auth_headers):
        """Test obtener lista por ID exitosamente."""
        # Arrange - Crear lista
        task_list_data = {"name": "Test List", "description": "Test description"}
        create_response = client.post("/api/v1/task-lists/", json=task_list_data, headers=auth_headers)
        list_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/v1/task-lists/{list_id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == list_id
        assert data["name"] == "Test List"
        assert data["description"] == "Test description"
    
    def test_get_task_list_not_found(self, client: TestClient, auth_headers):
        """Test obtener lista inexistente."""
        # Act
        response = client.get("/api/v1/task-lists/999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_task_list_success(self, client: TestClient, auth_headers):
        """Test actualizar lista de tareas exitosamente."""
        # Arrange - Crear lista
        task_list_data = {"name": "Original List", "description": "Original description"}
        create_response = client.post("/api/v1/task-lists/", json=task_list_data, headers=auth_headers)
        list_id = create_response.json()["id"]
        
        # Act
        update_data = {
            "name": "Updated List",
            "description": "Updated description"
        }
        response = client.put(f"/api/v1/task-lists/{list_id}", json=update_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated List"
        assert data["description"] == "Updated description"
        assert data["id"] == list_id
    
    def test_update_task_list_duplicate_name(self, client: TestClient, auth_headers):
        """Test actualizar lista con nombre duplicado."""
        # Arrange - Crear dos listas
        list1_data = {"name": "List 1", "description": "First list"}
        list2_data = {"name": "List 2", "description": "Second list"}
        
        create_response1 = client.post("/api/v1/task-lists/", json=list1_data, headers=auth_headers)
        create_response2 = client.post("/api/v1/task-lists/", json=list2_data, headers=auth_headers)
        
        list2_id = create_response2.json()["id"]
        
        # Act - Intentar cambiar el nombre de List 2 a "List 1"
        update_data = {"name": "List 1", "description": "Updated description"}
        response = client.put(f"/api/v1/task-lists/{list2_id}", json=update_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_update_task_list_not_found(self, client: TestClient, auth_headers):
        """Test actualizar lista inexistente."""
        # Arrange
        update_data = {"name": "Updated List", "description": "Updated description"}
        
        # Act
        response = client.put("/api/v1/task-lists/999", json=update_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_task_list_success(self, client: TestClient, auth_headers):
        """Test eliminar lista de tareas exitosamente."""
        # Arrange - Crear lista
        task_list_data = {"name": "List to Delete", "description": "Will be deleted"}
        create_response = client.post("/api/v1/task-lists/", json=task_list_data, headers=auth_headers)
        list_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"/api/v1/task-lists/{list_id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 204
        
        # Verificar que realmente se eliminó
        get_response = client.get(f"/api/v1/task-lists/{list_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_task_list_not_found(self, client: TestClient, auth_headers):
        """Test eliminar lista inexistente."""
        # Act
        response = client.delete("/api/v1/task-lists/999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_task_list_unauthorized(self, client: TestClient, sample_task_list):
        """Test eliminar lista sin autenticación."""
        # Act
        response = client.delete(f"/api/v1/task-lists/{sample_task_list.id}")
        
        # Assert
        assert response.status_code == 403 