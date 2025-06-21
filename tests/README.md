# 🧪 Suite de Tests - Crehana Backend Test

Esta suite de tests proporciona cobertura completa para la aplicación FastAPI con Clean Architecture.

## 📁 Estructura de Tests

```
tests/
├── conftest.py                     # Configuración global y fixtures
├── unit/                          # Tests unitarios
│   ├── domain/
│   │   └── test_entities.py       # Tests de entidades del dominio
│   ├── application/
│   │   ├── test_user_use_cases.py # Tests de casos de uso de usuarios
│   │   └── test_task_use_cases.py # Tests de casos de uso de tareas
│   ├── infrastructure/
│   │   └── test_repositories.py   # Tests de repositorios
│   └── auth/
│       ├── test_jwt_handler.py     # Tests de JWT
│       └── test_password_handler.py # Tests de passwords
├── integration/                   # Tests de integración
│   ├── api/
│   │   ├── test_auth_api.py       # Tests de API de autenticación
│   │   ├── test_users_api.py      # Tests de API de usuarios
│   │   ├── test_tasks_api.py      # Tests de API de tareas
│   │   └── test_task_lists_api.py # Tests de API de listas
│   └── repositories/
│       └── test_sql_repositories.py # Tests de repositorios SQL
└── README.md                      # Esta documentación
```

## 🏷️ Marcadores de Tests

Los tests están organizados con marcadores para facilitar la ejecución selectiva:

- `@pytest.mark.unit` - Tests unitarios (rápidos, sin dependencias externas)
- `@pytest.mark.integration` - Tests de integración (con base de datos y APIs)
- `@pytest.mark.slow` - Tests que tardan más tiempo

## 🐳 Ejecutar Tests con Docker

### Todos los Tests

```bash
docker-compose -f docker-compose.test.yml up test
```

### Solo Tests Unitarios

```bash
docker-compose -f docker-compose.test.yml up test-unit
```

### Solo Tests de Integración

```bash
docker-compose -f docker-compose.test.yml up test-integration
```

### Con Reporte de Cobertura

```bash
docker-compose -f docker-compose.test.yml up test-coverage
```

### Modo Watch (desarrollo)

```bash
docker-compose -f docker-compose.test.yml up test-watch
```

## 🔧 Ejecutar Tests Localmente

### Prerequisitos

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Comandos de Ejecución

#### Todos los tests

```bash
pytest -v
```

#### Solo tests unitarios

```bash
pytest tests/unit/ -v -m unit
```

#### Solo tests de integración

```bash
pytest tests/integration/ -v -m integration
```

#### Con cobertura de código

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

#### Tests específicos

```bash
# Un archivo específico
pytest tests/unit/domain/test_entities.py -v

# Una clase específica
pytest tests/unit/domain/test_entities.py::TestUser -v

# Un test específico
pytest tests/unit/domain/test_entities.py::TestUser::test_create_user_valid_data -v
```

#### Filtros adicionales

```bash
# Excluir tests lentos
pytest -v -m "not slow"

# Solo tests que fallan
pytest --lf

# Tests con palabra clave
pytest -k "user" -v
```

## 📊 Reportes de Cobertura

Los reportes de cobertura se generan en:

- **Terminal**: Muestra porcentaje y líneas faltantes
- **HTML**: `htmlcov/index.html` - Reporte interactivo detallado

### Objetivos de Cobertura

- **Mínimo**: 80% de cobertura general
- **Objetivo**: 90%+ en lógica de negocio (domain/application)
- **Crítico**: 100% en funciones de seguridad (auth)

## 🔍 Fixtures Disponibles

### Base de Datos

- `db_session` - Sesión de base de datos limpia para cada test
- `client` - Cliente de pruebas FastAPI con DB de test

### Autenticación

- `auth_token` - Token JWT válido
- `auth_headers` - Headers de autorización listos para usar

### Datos de Prueba

- `sample_user` - Usuario de prueba creado en DB
- `sample_task_list` - Lista de tareas de prueba
- `sample_user_data` - Datos para crear usuarios
- `sample_task_data` - Datos para crear tareas

### Servicios Mock

- `mock_email_service` - Servicio de email simulado

## 🚨 Buenas Prácticas

### Estructura de Tests

```python
def test_feature_success(self, fixture1, fixture2):
    """Test descripción clara del comportamiento esperado."""
    # Arrange - Preparar datos
    data = {"key": "value"}

    # Act - Ejecutar acción
    result = service.method(data)

    # Assert - Verificar resultado
    assert result.status == "success"
    assert result.data == expected_data
```

### Naming Convention

- `test_<feature>_success` - Caso exitoso
- `test_<feature>_failure` - Caso de fallo
- `test_<feature>_edge_case` - Casos límite
- `test_<feature>_invalid_data` - Datos inválidos

### Assertions

```python
# Específicas y descriptivas
assert user.username == "expected_username"
assert response.status_code == 201
assert "error_message" in response.json()["detail"]

# Para listas y objetos
assert len(users) == 3
assert user.id in [u.id for u in users]
```

## 🐛 Debugging Tests

### Información detallada

```bash
pytest -v --tb=long
```

### Parar en primer fallo

```bash
pytest -x
```

### Ejecutar test específico con debug

```bash
pytest tests/unit/domain/test_entities.py::TestUser::test_create_user_valid_data -v -s
```

### Ver salida de print

```bash
pytest -s
```

## 📈 Métricas de Calidad

### Cobertura por Módulo

- **Domain**: 95%+ (lógica de negocio crítica)
- **Application**: 90%+ (casos de uso)
- **Infrastructure**: 85%+ (repositorios y servicios)
- **API**: 80%+ (endpoints y validaciones)
- **Auth**: 100% (seguridad crítica)

### Tipos de Tests

- **Unitarios**: ~70% del total (rápidos, aislados)
- **Integración**: ~30% del total (E2E, realistas)

### Performance

- **Tests unitarios**: < 1 segundo cada uno
- **Tests integración**: < 5 segundos cada uno
- **Suite completa**: < 2 minutos

## 🔄 CI/CD Integration

Los tests están configurados para ejecutarse automáticamente en:

- **Pre-commit**: Tests unitarios rápidos
- **Pull Request**: Suite completa + cobertura
- **Deploy**: Tests de integración críticos

### Variables de Entorno para CI

```bash
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=test-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
PYTHONPATH=/app
```
