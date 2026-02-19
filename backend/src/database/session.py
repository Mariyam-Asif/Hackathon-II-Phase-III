from sqlmodel import Session
from database.database import engine

def get_session():
    """
    Generator that yields a database session
    This function should be used as a dependency in FastAPI routes
    """
    with Session(engine) as session:
        yield session