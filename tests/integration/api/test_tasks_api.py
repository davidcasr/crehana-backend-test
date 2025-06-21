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
    
    def test_create_task_with_due_date(self, client: TestClient, auth_headers, sample_task_list):
        """Test crear tarea con fecha de vencimiento."""
        # Arrange
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Task with Due Date",
            "description": "Task with due date",
            "task_list_id": sample_task_list.id,
            "priority": "urgent",
            "due_date": future_date
        }
        
        # Act
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None
        assert data["priority"] == "urgent"
    
    def test_create_task_nonexistent_user(self, client: TestClient, auth_headers, sample_task_list):
        """Test crear tarea con usuario inexistente."""
        # Arrange
        task_data = {
            "title": "Task with bad user",
            "description": "Should fail",
            "task_list_id": sample_task_list.id,
            "priority": "medium",
            "assigned_user_id": 99999
        }
        
        # Act
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_create_task_nonexistent_task_list(self, client: TestClient, auth_headers):
        """Test crear tarea con lista inexistente."""
        # Arrange
        task_data = {
            "title": "Task with bad list",
            "description": "Should fail",
            "task_list_id": 99999,
            "priority": "medium"
        }
        
        # Act
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
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

    # ===== TESTS PARA ENDPOINTS ANIDADOS BAJO /task-lists =====
    
    def test_create_task_nested_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test crear tarea usando endpoint anidado bajo task-lists."""
        # Arrange
        task_data = {
            "title": "Nested Task",
            "description": "Task created via nested endpoint",
            "priority": "low"
        }
        
        # Act
        response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Nested Task"
        assert data["task_list_id"] == sample_task_list.id
    
    def test_create_task_nested_with_assigned_user(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test crear tarea anidada con usuario asignado."""
        # Arrange
        task_data = {
            "title": "Nested Assigned Task",
            "description": "Nested task with user",
            "priority": "high",
            "assigned_user_id": sample_user.id
        }
        
        # Act
        response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["assigned_user_id"] == sample_user.id
        assert data["assigned_user"]["username"] == sample_user.username
    
    def test_get_tasks_by_list_nested_with_stats(self, client: TestClient, auth_headers, sample_task_list):
        """Test obtener tareas con estadísticas usando endpoint anidado."""
        # Arrange - Crear tareas con diferentes estados
        tasks_data = [
            {"title": "Pending Task", "description": "A pending task", "priority": "medium"},
            {"title": "Completed Task", "description": "A completed task", "priority": "high"}
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
            assert response.status_code == 201, f"Failed to create task: {response.json()}"
            created_tasks.append(response.json())
        
        # Marcar una como completada
        status_response = client.patch(f"/api/v1/tasks/{created_tasks[1]['id']}/status", json={"status": "completed"}, headers=auth_headers)
        assert status_response.status_code == 200, f"Failed to update status: {status_response.json()}"
        
        # Act
        response = client.get(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        # El endpoint devuelve TasksWithStatsResponse que tiene completion_percentage en lugar de stats
        assert "completion_percentage" in data
        assert data["total_tasks"] >= 2
        assert len(data["tasks"]) >= 2
    
    def test_get_task_nested_not_found(self, client: TestClient, auth_headers, sample_task_list):
        """Test obtener tarea inexistente usando endpoint anidado."""
        # Act
        response = client.get(f"/api/v1/task-lists/{sample_task_list.id}/tasks/99999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_task_nested_not_found(self, client: TestClient, auth_headers, sample_task_list):
        """Test actualizar tarea inexistente usando endpoint anidado."""
        # Arrange
        update_data = {"title": "New Title"}
        
        # Act
        response = client.put(f"/api/v1/task-lists/{sample_task_list.id}/tasks/99999", json=update_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_assign_task_nested_success(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test asignar usuario a tarea usando endpoint anidado."""
        # Arrange
        task_data = {"title": "Assignment Task", "description": "Task for assignment", "priority": "medium"}
        create_response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        created_task = create_response.json()
        
        # Act
        response = client.patch(f"/api/v1/task-lists/{sample_task_list.id}/tasks/{created_task['id']}/assign", json={"assigned_user_id": sample_user.id}, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_user_id"] == sample_user.id
    
    def test_assign_task_nested_nonexistent_user(self, client: TestClient, auth_headers, sample_task_list):
        """Test asignar usuario inexistente a tarea usando endpoint anidado."""
        # Arrange
        task_data = {"title": "Bad Assignment Task", "description": "Task for bad assignment", "priority": "medium"}
        create_response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        created_task = create_response.json()
        
        # Act
        response = client.patch(f"/api/v1/task-lists/{sample_task_list.id}/tasks/{created_task['id']}/assign", json={"assigned_user_id": 99999}, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_task_nested_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test eliminar tarea usando endpoint anidado."""
        # Arrange
        task_data = {"title": "Delete Task", "description": "Task to be deleted", "priority": "medium"}
        create_response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        created_task = create_response.json()
        
        # Act
        response = client.delete(f"/api/v1/task-lists/{sample_task_list.id}/tasks/{created_task['id']}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 204
        
        # Verificar que la tarea fue eliminada
        get_response = client.get(f"/api/v1/task-lists/{sample_task_list.id}/tasks/{created_task['id']}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_task_nested_not_found(self, client: TestClient, auth_headers, sample_task_list):
        """Test eliminar tarea inexistente usando endpoint anidado."""
        # Act
        response = client.delete(f"/api/v1/task-lists/{sample_task_list.id}/tasks/99999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_get_tasks_by_user_nested(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test obtener tareas por usuario usando endpoint correcto."""
        # Arrange
        task_data = {"title": "User Task", "description": "Task assigned to user", "priority": "medium", "assigned_user_id": sample_user.id}
        create_response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        
        # Act - Usar el endpoint correcto
        response = client.get(f"/api/v1/tasks/user/{sample_user.id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)  # El endpoint devuelve una lista directa
        user_tasks = [task for task in data if task["assigned_user_id"] == sample_user.id]
        assert len(user_tasks) >= 1

    # ===== TESTS PARA ENDPOINTS DIRECTOS =====
    
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
    
    def test_get_tasks_by_list_with_status_filter(self, client: TestClient, auth_headers, sample_task_list):
        """Test obtener tareas filtradas por estado."""
        # Arrange
        tasks_data = [
            {"title": "Pending Task", "description": "A pending task", "priority": "medium"},
            {"title": "In Progress Task", "description": "A task in progress", "priority": "high"}
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            response = client.post(f"/api/v1/tasks/", json={**task_data, "task_list_id": sample_task_list.id}, headers=auth_headers)
            assert response.status_code == 201, f"Failed to create task: {response.json()}"
            created_tasks.append(response.json())
        
        # Cambiar el estado de una tarea
        status_response = client.patch(f"/api/v1/tasks/{created_tasks[1]['id']}/status", json={"status": "in_progress"}, headers=auth_headers)
        assert status_response.status_code == 200, f"Failed to update status: {status_response.json()}"
        
        # Act - Filtrar por estado "in_progress"
        response = client.get(f"/api/v1/task-lists/{sample_task_list.id}/tasks/?status=in_progress", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        in_progress_tasks = [task for task in data["tasks"] if task["status"] == "in_progress"]
        assert len(in_progress_tasks) >= 1
    
    def test_get_tasks_by_list_with_assigned_user_filter(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test obtener tareas filtradas por usuario asignado."""
        # Arrange
        tasks_data = [
            {"title": "Assigned Task", "description": "Task assigned to user", "priority": "medium", "assigned_user_id": sample_user.id},
            {"title": "Unassigned Task", "description": "Task without assignment", "priority": "low"}
        ]
        
        for task_data in tasks_data:
            response = client.post(f"/api/v1/tasks/", json={**task_data, "task_list_id": sample_task_list.id}, headers=auth_headers)
            assert response.status_code == 201, f"Failed to create task: {response.json()}"
        
        # Act - Filtrar por usuario asignado
        response = client.get(f"/api/v1/task-lists/{sample_task_list.id}/tasks/?assigned_user_id={sample_user.id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assigned_tasks = [task for task in data["tasks"] if task["assigned_user_id"] == sample_user.id]
        assert len(assigned_tasks) >= 1
    
    def test_get_task_by_id_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test obtener tarea por ID."""
        # Arrange
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
    
    def test_get_task_not_found(self, client: TestClient, auth_headers):
        """Test obtener tarea inexistente."""
        # Act
        response = client.get("/api/v1/tasks/99999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_task_status_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test actualizar estado de tarea."""
        # Arrange
        task_data = {"title": "Task to Complete", "description": "Will be completed", "task_list_id": sample_task_list.id, "priority": "medium"}
        create_response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        task_id = create_response.json()["id"]
        
        # Act
        response = client.patch(f"/api/v1/tasks/{task_id}/status", json={"status": "completed"}, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
    
    def test_update_task_status_not_found(self, client: TestClient, auth_headers):
        """Test actualizar estado de tarea inexistente."""
        # Act
        response = client.patch("/api/v1/tasks/99999/status", json={"status": "completed"}, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
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
    
    def test_assign_task_not_found(self, client: TestClient, auth_headers, sample_user):
        """Test asignar tarea inexistente."""
        # Act
        assign_data = {"user_id": sample_user.id}
        response = client.patch("/api/v1/tasks/99999/assign", json=assign_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_assign_task_nonexistent_user(self, client: TestClient, auth_headers, sample_task_list):
        """Test asignar usuario inexistente a tarea."""
        # Arrange
        task_data = {"title": "Task for bad assignment", "description": "Task for bad assignment test", "priority": "medium", "task_list_id": sample_task_list.id}
        create_response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        created_task = create_response.json()
        
        # Act
        response = client.patch(f"/api/v1/tasks/{created_task['id']}/assign", json={"assigned_user_id": 99999}, headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
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
    
    def test_delete_task_not_found(self, client: TestClient, auth_headers):
        """Test eliminar tarea inexistente."""
        # Act
        response = client.delete("/api/v1/tasks/99999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
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
    
    def test_get_tasks_by_user_not_found(self, client: TestClient, auth_headers):
        """Test obtener tareas de usuario inexistente."""
        # Act
        response = client.get("/api/v1/tasks/user/99999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404

    # ===== TESTS PARA CASOS DE ERROR Y VALIDACIÓN =====
    
    def test_create_task_invalid_priority(self, client: TestClient, auth_headers, sample_task_list):
        """Test crear tarea con prioridad inválida."""
        # Arrange
        task_data = {
            "title": "Task with bad priority",
            "task_list_id": sample_task_list.id,
            "priority": "invalid_priority"
        }
        
        # Act
        response = client.post("/api/v1/tasks/", json=task_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 422
    
    def test_get_tasks_by_list_not_found(self, client: TestClient, auth_headers):
        """Test obtener tareas de lista inexistente."""
        # Act
        response = client.get("/api/v1/tasks/list/99999", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_get_tasks_by_list_nested_not_found(self, client: TestClient, auth_headers):
        """Test obtener tareas de lista inexistente usando endpoint anidado."""
        # Act
        response = client.get("/api/v1/task-lists/99999/tasks/", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404

    # ===== TESTS PARA AUTENTICACIÓN =====
    
    def test_all_endpoints_require_authentication(self, client: TestClient, sample_task_list, sample_user):
        """Test que todos los endpoints requieren autenticación."""
        endpoints = [
            ("POST", "/api/v1/tasks/", {"title": "Test", "task_list_id": sample_task_list.id, "priority": "medium"}),
            ("GET", f"/api/v1/tasks/list/{sample_task_list.id}", None),
            ("GET", "/api/v1/tasks/1", None),
            ("PUT", "/api/v1/tasks/1", {"title": "Test"}),
            ("PATCH", "/api/v1/tasks/1/status", {"status": "completed"}),
            ("PATCH", "/api/v1/tasks/1/assign", {"user_id": sample_user.id}),
            ("DELETE", "/api/v1/tasks/1", None),
            ("GET", f"/api/v1/tasks/user/{sample_user.id}", None),
            ("POST", f"/api/v1/task-lists/{sample_task_list.id}/tasks/", {"title": "Test", "priority": "medium"}),
            ("GET", f"/api/v1/task-lists/{sample_task_list.id}/tasks/", None),
            ("GET", f"/api/v1/task-lists/{sample_task_list.id}/tasks/1", None),
            ("PUT", f"/api/v1/task-lists/{sample_task_list.id}/tasks/1", {"title": "Test"}),
            ("PATCH", f"/api/v1/task-lists/{sample_task_list.id}/tasks/1/status", {"status": "completed"}),
            ("PATCH", f"/api/v1/task-lists/{sample_task_list.id}/tasks/1/assign", {"user_id": sample_user.id}),
            ("DELETE", f"/api/v1/task-lists/{sample_task_list.id}/tasks/1", None),
            ("GET", f"/api/v1/task-lists/users/{sample_user.id}/tasks", None),
        ]
        
        for method, endpoint, data in endpoints:
            # Act
            if method == "POST":
                response = client.post(endpoint, json=data)
            elif method == "GET":
                response = client.get(endpoint)
            elif method == "PUT":
                response = client.put(endpoint, json=data)
            elif method == "PATCH":
                response = client.patch(endpoint, json=data)
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # Assert
            assert response.status_code == 403, f"Endpoint {method} {endpoint} should require authentication"

    def test_get_tasks_by_list_nested_with_filters(self, client: TestClient, auth_headers, sample_task_list, sample_user):
        """Test obtener tareas anidadas con filtros."""
        # Arrange
        tasks_data = [
            {"title": "High Priority Task", "description": "High priority task", "priority": "high", "assigned_user_id": sample_user.id},
            {"title": "Medium Priority Task", "description": "Medium priority task", "priority": "medium"},
            {"title": "Low Priority Task", "description": "Low priority task", "priority": "low"}
        ]
        
        for task_data in tasks_data:
            response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
            assert response.status_code == 201, f"Failed to create task: {response.json()}"
        
        # Act - Filtrar por prioridad alta
        response = client.get(f"/api/v1/task-lists/{sample_task_list.id}/tasks/?priority=high", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verificar que tenemos al menos una tarea de alta prioridad
        high_priority_tasks = [task for task in data["tasks"] if task["priority"] == "high"]
        assert len(high_priority_tasks) >= 1
    
    def test_get_task_nested_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test obtener tarea específica usando endpoint anidado."""
        # Arrange
        task_data = {"title": "Nested Task", "description": "Task for nested get test", "priority": "medium"}
        create_response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        created_task = create_response.json()
        
        # Act
        response = client.get(f"/api/v1/task-lists/{sample_task_list.id}/tasks/{created_task['id']}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Nested Task"
        assert data["id"] == created_task["id"]
    
    def test_update_task_nested_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test actualizar tarea usando endpoint anidado."""
        # Arrange
        task_data = {"title": "Original Task", "description": "Original task description", "priority": "low"}
        create_response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        created_task = create_response.json()
        
        update_data = {"title": "Updated Task", "priority": "high"}
        
        # Act
        response = client.put(f"/api/v1/task-lists/{sample_task_list.id}/tasks/{created_task['id']}", json=update_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["priority"] == "high"
    
    def test_update_task_status_nested_success(self, client: TestClient, auth_headers, sample_task_list):
        """Test actualizar estado de tarea usando endpoint anidado."""
        # Arrange
        task_data = {"title": "Status Task", "description": "Task for status update", "priority": "medium"}
        create_response = client.post(f"/api/v1/task-lists/{sample_task_list.id}/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 201, f"Failed to create task: {create_response.json()}"
        created_task = create_response.json()
        
        # Act
        response = client.patch(f"/api/v1/task-lists/{sample_task_list.id}/tasks/{created_task['id']}/status", json={"status": "in_progress"}, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress" 