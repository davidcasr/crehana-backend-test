"""Main FastAPI application module."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.database.init_db import init_database, check_database_connection
from .api import (
    task_lists_router,
    tasks_router,
    tasks_direct_router,
    users_router,
    auth_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    print("Starting Task Management API...")

    # Check database connection
    if check_database_connection():
        # Initialize database tables
        init_database()
        print("Database initialized successfully!")
    else:
        print("Warning: Database connection failed!")

    yield

    # Shutdown
    print("Shutting down Task Management API...")


# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="A comprehensive task management system with users, task lists and tasks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users_router, prefix="/api/v1")
app.include_router(task_lists_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(tasks_direct_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "message": "Welcome to Task Management API!",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    # Check database connectivity
    db_status = "connected" if check_database_connection() else "disconnected"

    return {"status": "healthy", "database": db_status, "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=debug, log_level="info")
