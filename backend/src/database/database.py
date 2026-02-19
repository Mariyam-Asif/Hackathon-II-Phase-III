from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool, QueuePool
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if running in test mode
TESTING = os.getenv("TESTING", "").lower() == "true"

if TESTING:
    # Use in-memory SQLite for testing
    DATABASE_URL = "sqlite:///:memory:"
    # Create engine with static pool for SQLite in-memory
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite in-memory
        poolclass=StaticPool,  # Use static pool for in-memory SQLite
    )
else:
    # Get database URL from environment variable for production
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/todo_db")

    # Create engine with connection pooling for production
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections after 5 minutes
    )

def create_db_and_tables():
    """
    Create database tables if they don't exist
    This function should be called on application startup
    """
    # Import models to ensure they're registered with SQLModel metadata
    from models import user, task
    SQLModel.metadata.create_all(engine)