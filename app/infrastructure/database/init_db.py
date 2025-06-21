"""Database initialization module."""

import time
from .connection import create_tables, drop_tables, engine
from ..models import (
    TaskListModel,
    TaskModel,
    UserModel,
)  # Import models to register them


def init_database():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    print("Dropping all database tables...")
    drop_tables()
    print("Creating database tables...")
    create_tables()
    print("Database reset completed!")


def check_database_connection(max_retries=5, delay=2):
    """Check if database connection is working with retries."""
    for attempt in range(max_retries):
        try:
            from sqlalchemy import text

            # Try to execute a simple query
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            print("Database connection successful!")
            return True
        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All database connection attempts failed!")
                return False
    return False


if __name__ == "__main__":
    # Check connection first
    if check_database_connection():
        # Initialize database
        init_database()
    else:
        print("Cannot initialize database due to connection issues.")
