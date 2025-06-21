# Decision Log - Task Management API

Este documento registra las decisiones técnicas clave tomadas durante el desarrollo del sistema de gestión de tareas.

## Tabla de Contenidos

- [Arquitectura General](#arquitectura-general)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura de Datos](#estructura-de-datos)
- [Autenticación y Autorización](#autenticación-y-autorización)
- [API Design](#api-design)
- [Testing Strategy](#testing-strategy)
- [Code Quality](#code-quality)
- [Infrastructure](#infrastructure)

---

## Arquitectura General

### ADR-001: Clean Architecture Pattern

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Contexto**: Necesitamos una arquitectura que permita escalabilidad, mantenibilidad y testabilidad.

**Decisión**: Implementar Clean Architecture con las siguientes capas:

- **Domain**: Entidades de negocio, enums y repositorios abstractos
- **Application**: Casos de uso y DTOs
- **Infrastructure**: Implementaciones concretas (DB, servicios externos)
- **API**: Controladores FastAPI

**Consecuencias**:

- ✅ Separación clara de responsabilidades
- ✅ Fácil testing con mocks
- ✅ Independencia de frameworks
- ❌ Mayor complejidad inicial
- ❌ Más archivos y estructura

---

## Stack Tecnológico

### ADR-002: FastAPI como Framework Web

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Contexto**: Necesitamos un framework moderno para API REST con documentación automática.

**Decisión**: FastAPI + Uvicorn

**Alternativas consideradas**:

- Django REST Framework
- Flask + Flask-RESTful

**Razones**:

- ✅ Documentación automática (OpenAPI/Swagger)
- ✅ Validación automática con Pydantic
- ✅ Async/await nativo
- ✅ Type hints integrados
- ✅ Alto rendimiento

### ADR-003: SQLAlchemy ORM

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Contexto**: Necesitamos un ORM robusto para manejo de base de datos.

**Decisión**: SQLAlchemy 2.0 con Core + ORM

**Alternativas consideradas**:

- Django ORM
- Tortoise ORM
- Raw SQL

**Razones**:

- ✅ Maduro y estable
- ✅ Soporte para múltiples bases de datos
- ✅ Migraciones con Alembic
- ✅ Lazy loading y optimizaciones

### ADR-004: PostgreSQL como Base de Datos

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Contexto**: Necesitamos una base de datos relacional robusta.

**Decisión**: PostgreSQL 15+

**Alternativas consideradas**:

- MySQL
- SQLite
- MongoDB

**Razones**:

- ✅ ACID compliance
- ✅ Tipos de datos avanzados (JSON, Arrays)
- ✅ Rendimiento excelente
- ✅ Extensibilidad

---

## Estructura de Datos

### ADR-005: Enums para Estados y Prioridades

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Contexto**: Necesitamos valores controlados para status y prioridades.

**Decisión**: Usar Python Enums + SQLAlchemy Enum

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
```

**Consecuencias**:

- ✅ Validación automática
- ✅ Documentación clara en API
- ✅ Type safety

### ADR-006: Relaciones de Base de Datos

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**:

- Users 1:N Tasks (assigned_user_id nullable)
- TaskLists 1:N Tasks (task_list_id required)
- Soft deletes para preservar historial

**Consecuencias**:

- ✅ Flexibilidad en asignaciones
- ✅ Historial preservado
- ✅ Integridad referencial

---

## Autenticación y Autorización

### ADR-007: JWT Authentication

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Contexto**: Necesitamos autenticación stateless para API REST.

**Decisión**: JWT con `python-jose` + `passlib[bcrypt]`

**Características**:

- Tokens con expiración configurable
- Passwords hasheadas con bcrypt
- Login por username o email
- Middleware de autenticación opcional/obligatorio

**Alternativas consideradas**:

- Session-based auth
- OAuth2
- API Keys

**Razones**:

- ✅ Stateless
- ✅ Escalable
- ✅ Compatible con SPAs
- ✅ Estándar de industria

### ADR-008: Password Security

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: bcrypt con salt automático

**Configuración**:

- Mínimo 6 caracteres
- Hash con bcrypt (cost factor por defecto)
- Validación en backend

---

## API Design

### ADR-009: RESTful API Design

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: Seguir principios REST con endpoints anidados y directos

**Estructura**:

```
/api/v1/
├── auth/           # Autenticación
├── users/          # Gestión usuarios
├── task-lists/     # Listas de tareas
└── tasks/          # Tareas individuales
```

**Consecuencias**:

- ✅ API predecible
- ✅ Fácil de documentar
- ✅ Estándar de industria

### ADR-010: Pydantic para Validación

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: DTOs con Pydantic para request/response

**Beneficios**:

- ✅ Validación automática
- ✅ Documentación OpenAPI
- ✅ Type safety
- ✅ Serialización JSON

---

## Testing Strategy

### ADR-011: Pytest + TestClient

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: pytest con FastAPI TestClient para tests de integración

**Estructura**:

```
tests/
├── unit/           # Tests unitarios
├── integration/    # Tests de integración
└── conftest.py     # Fixtures compartidas
```

### ADR-012: Database Testing

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: Base de datos en memoria para tests

**Implementación**:

- SQLite in-memory para tests unitarios
- PostgreSQL test container para integración
- Fixtures con datos de prueba

---

## Code Quality

### ADR-013: Type Hints

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: Type hints obligatorios en todo el código

**Herramientas**:

- mypy para verificación estática
- Pydantic para runtime validation

### ADR-014: Code Formatting

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: Black + isort + flake8

**Configuración**:

- Line length: 88 caracteres
- Import sorting automático
- Linting con flake8

---

## Infrastructure

### ADR-015: Docker Containerization

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: Docker para desarrollo y producción

**Estructura**:

- `Dockerfile` para producción
- `Dockerfile.test` para testing
- `docker-compose.yml` para desarrollo local
- Multi-stage builds para optimización

### ADR-016: Environment Configuration

**Fecha**: 2024-12-15  
**Estado**: Adoptado

**Decisión**: Variables de entorno para configuración

**Variables clave**:

```
DATABASE_URL
SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES
ENVIRONMENT
```

**Beneficios**:

- ✅ Configuración por ambiente
- ✅ Secretos seguros
- ✅ 12-factor app compliance
