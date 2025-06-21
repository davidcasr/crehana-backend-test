# Task Management API | Desafio Técnico Backend en Crehana

Una API completa de gestión de tareas desarrollada con FastAPI, siguiendo los principios de Clean Architecture. Permite crear, gestionar y organizar listas de tareas con funcionalidades avanzadas de filtrado y estadísticas de completitud.

## 🚀 Características

- ✅ **Gestión completa de listas de tareas**: Crear, leer, actualizar y eliminar listas
- ✅ **Gestión de tareas**: CRUD completo con filtros avanzados por estado y prioridad
- ✅ **Estadísticas en tiempo real**: Porcentaje de completitud automático
- ✅ **Filtrado inteligente**: Por estado (pending, in_progress, completed, cancelled) y prioridad (low, medium, high, urgent)
- ✅ **Validaciones de negocio**: Títulos únicos, fechas válidas, y más
- ✅ **Clean Architecture**: Separación clara de capas (Domain, Application, Infrastructure)
- ✅ **Base de datos PostgreSQL**: Con SQLAlchemy ORM
- ✅ **Documentación automática**: Swagger/OpenAPI integrado
- ✅ **Containerización**: Docker y Docker Compose incluidos

## 🏗️ Arquitectura

El proyecto sigue los principios de **Clean Architecture** con las siguientes capas:

```
app/
├── domain/                 # Capa de Dominio
│   ├── models/            # Entidades y Enums
│   ├── repositories.py    # Interfaces de repositorios
│   └── exceptions.py      # Excepciones de dominio
├── application/           # Capa de Aplicación
│   ├── dtos.py           # DTOs de entrada y salida
│   └── use_cases/        # Casos de uso (lógica de negocio)
├── infrastructure/        # Capa de Infraestructura
│   ├── database/         # Configuración de base de datos
│   ├── models/           # Modelos SQLAlchemy
│   └── repositories/     # Implementaciones de repositorios
└── api/                  # Capa de Presentación
    ├── task_lists.py     # Endpoints de listas de tareas
    └── tasks.py          # Endpoints de tareas
```

## 🛠️ Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para Python
- **PostgreSQL**: Base de datos relacional
- **Pydantic**: Validación de datos y serialización
- **Uvicorn**: Servidor ASGI
- **Docker**: Containerización
- **Pytest**: Framework de testing

## 📋 Prerrequisitos

- Python 3.11+
- PostgreSQL 13+ (para desarrollo local)
- Docker y Docker Compose (para ejecución containerizada)

## ⚙️ Configuración del Entorno Local

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd crehana-backend-test
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` basado en `env.example`:

```bash
cp env.example .env
```

Edita el archivo `.env` con tus configuraciones:

```env
# Base de datos
DATABASE_URL=postgresql://postgres:password@localhost:5432/fastapi_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fastapi_db
DB_USER=postgres
DB_PASSWORD=password
```

### 5. Configurar PostgreSQL

Asegúrate de tener PostgreSQL ejecutándose y crea la base de datos:

```sql
CREATE DATABASE fastapi_db;
```

### 6. Ejecutar la aplicación

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La aplicación estará disponible en:

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Ejecución con Docker

### Opción 1: Docker Compose (Recomendado)

```bash
# Ejecutar en modo desarrollo
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Opción 2: Docker manual

```bash
# Construir la imagen
docker build -t task-management-api .

# Ejecutar el contenedor (asegúrate de tener PostgreSQL ejecutándose)
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/fastapi_db \
  task-management-api
```

### Servicios incluidos en Docker Compose

- **app**: API de FastAPI (puerto 8000)
- **db**: PostgreSQL 13 (puerto 5432)

## 🧪 Ejecutar las Pruebas

### Configuración de pruebas

Las pruebas utilizan una base de datos SQLite en memoria para mayor velocidad.

### Ejecutar todas las pruebas

```bash
# Con pytest
pytest

# Con coverage
pytest --cov=app tests/

# Ejecutar pruebas específicas
pytest tests/test_api.py

# Ejecutar con output detallado
pytest -v tests/
```

### Ejecutar pruebas en Docker

```bash
# Ejecutar pruebas dentro del contenedor
docker-compose exec app pytest

# Ejecutar con coverage
docker-compose exec app pytest --cov=app tests/
```

## 🔧 Desarrollo

### Estructura del proyecto

```
├── app/
│   ├── api/              # Routers y endpoints
│   ├── application/      # DTOs y casos de uso
│   ├── domain/          # Entidades y lógica de dominio
│   ├── infrastructure/  # Implementaciones técnicas
│   ├── dependencies.py  # Inyección de dependencias
│   └── main.py         # Punto de entrada
├── tests/              # Pruebas
├── docker-compose.yml  # Configuración Docker
├── Dockerfile         # Imagen Docker
├── requirements.txt   # Dependencias Python
└── pytest.ini       # Configuración de pruebas
```

### Comandos útiles

```bash
# Formatear código
black app/ tests/

# Linting
flake8 app/ tests/

# Actualizar dependencias
pip freeze > requirements.txt

# Ejecutar en modo debug
uvicorn app.main:app --reload --log-level debug
```

## 🚀 Deployment

### Variables de entorno para producción

```env
DEBUG=False
DATABASE_URL=postgresql://user:password@production-host:5432/production_db
API_HOST=0.0.0.0
API_PORT=8000
```

## 📚 Documentación

Para más información, consulta la [documentación interactiva](http://localhost:8000/docs) cuando la aplicación esté ejecutándose.

Made with ❤️ by @davidcasr
