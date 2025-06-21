"""Tests de integración para la API de tareas."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.domain.models.enums import TaskStatus, TaskPriority


@pytest.mark.integration
class TestTasksAPI:
    """Tests de integración para endpoints de tareas."""
    
    def test_create_task_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test crear tarea exitosamente."""
        # Arrange
        task_data = {
            "title": "New Task",
            "description": "A test task for integration testing",
            "task_list_id": sample_task_list.id,
            "priority": "medium"
        }
        
        # Act
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "A test task for integration testing"
        assert data["task_list_id"] == sample_task_list.id
        assert data["priority"] == "medium"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_with_assigned_user(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test crear tarea con usuario asignado."""
        # Arrange
        task_data = {
            "title": "Assigned Task",
            "description": "A task with assigned user",
            "task_list_id": sample_task_list.id,
            "priority": "high",
            "assigned_user_id": sample_user.id
        }
        
        # Act
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["assigned_user_id"] == sample_user.id
    
    def test_create_task_unauthorized(self, client: TestClient, sample_task_list):
        """Test crear tarea sin autenticación."""
        # Arrange
        task_data = {
            "title": "Unauthorized Task",
            "description": "This should fail",
            "task_list_id": sample_task_list.id,
            "priority": "medium"
        }
        
        # Act
        response = client.post("/api/v1/tasks/", json=task_data)
        
        # Assert
        assert response.status_code == 403
    
    def test_create_task_duplicate_title(self, client: TestClient, auth_headers, sample_task_list):
        """Test crear tarea con título duplicado en la misma lista."""
        # Arrange
        task_data = {
            "title": "Duplicate Task",
            "description": "First task",
            "task_list_id": sample_task_list.id,
            "priority": "medium"
        }
        
        # Crear primera tarea
        client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Act - Intentar crear segunda tarea con mismo título
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_get_tasks_by_list_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test obtener tareas por lista exitosamente."""
        # Arrange - Crear algunas tareas
        tasks_data = [
            {"title": "Task 1", "description": "First task", "task_list_id": sample_task_list.id, "priority": "low"},
            {"title": "Task 2", "description": "Second task", "task_list_id": sample_task_list.id, "priority": "medium"},
            {"title": "Task 3", "description": "Third task", "task_list_id": sample_task_list.id, "priority": "high"}
        ]
        
        for task_data in tasks_data:
            client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Act
        response = client.get(f"/api/v1/tasks/list/{sample_task_list.id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # Al menos las 3 que creamos
        
        # Verificar que nuestras tareas están en la respuesta
        task_titles = [item["title"] for item in data]
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles
        assert "Task 3" in task_titles
    
    def test_get_tasks_by_list_with_filters(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test obtener tareas con filtros."""
        # Arrange - Crear tareas con diferentes estados y prioridades
        tasks_data = [
            {"title": "High Priority Task", "description": "High priority", "task_list_id": sample_task_list.id, "priority": "high", "assigned_user_id": sample_user.id},
            {"title": "Medium Priority Task", "description": "Medium priority", "task_list_id": sample_task_list.id, "priority": "medium"},
            {"title": "Low Priority Task", "description": "Low priority", "task_list_id": sample_task_list.id, "priority": "low"}
        ]
        
        for task_data in tasks_data:
            client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Act - Filtrar por prioridad alta
        response = client.get(f"/api/v1/tasks/list/{sample_task_list.id}?priority=high", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(task["priority"] == "high" for task in data)
    
    def test_get_task_by_id_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test obtener tarea por ID exitosamente."""
        # Arrange - Crear tarea
        task_data = {"title": "Test Task", "description": "Test description", "task_list_id": sample_task_list.id, "priority": "medium"}
        create_response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        task_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert data["description"] == "Test description"
    
    def test_get_task_not_found(self, client: TestClient, auth_headers):
        """Test obtener tarea inexistente."""
        # Act
        response = client.get("/api/v1/tasks/999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_task_status_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test actualizar estado de tarea exitosamente."""
        # Arrange - Crear tarea
        task_data = {"title": "Task to Complete", "description": "Will be completed", "task_list_id": sample_task_list.id, "priority": "medium"}
        create_response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"status": "completed"}
        response = client.patch(f"/api/v1/tasks/{task_id}/status", json=update_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["id"] == task_id
    
    def test_assign_task_to_user_success(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test asignar tarea a usuario exitosamente."""
        # Arrange - Crear tarea sin asignar
        task_data = {"title": "Task to Assign", "description": "Will be assigned", "task_list_id": sample_task_list.id, "priority": "medium"}
        create_response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        task_id = create_response.json()["id"]
        
        # Act
        assign_data = {"user_id": sample_user.id}
        response = client.patch(f"/api/v1/tasks/{task_id}/assign", json=assign_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_user_id"] == sample_user.id
        assert data["id"] == task_id
    
    def test_delete_task_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test eliminar tarea exitosamente."""
        # Arrange - Crear tarea
        task_data = {"title": "Task to Delete", "description": "Will be deleted", "task_list_id": sample_task_list.id, "priority": "medium"}
        create_response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        task_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 204
        
        # Verificar que realmente se eliminó
        get_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_get_tasks_by_user_success(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test obtener tareas asignadas a un usuario."""
        # Arrange - Crear tareas asignadas al usuario
        tasks_data = [
            {"title": "User Task 1", "description": "First assigned task", "task_list_id": sample_task_list.id, "priority": "medium", "assigned_user_id": sample_user.id},
            {"title": "User Task 2", "description": "Second assigned task", "task_list_id": sample_task_list.id, "priority": "high", "assigned_user_id": sample_user.id}
        ]
        
        for task_data in tasks_data:
            client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Act
        response = client.get(f"/api/v1/tasks/user/{sample_user.id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Al menos las 2 que creamos
        
        # Verificar que todas las tareas están asignadas al usuario
        for task in data:
            assert task["assigned_user_id"] == sample_user.id 