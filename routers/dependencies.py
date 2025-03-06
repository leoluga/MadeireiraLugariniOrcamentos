# routers/dependencies.py

from infrastructure.database import SessionLocal

def get_db():
    """
    Provide a database session (SQLAlchemy).
    This is a FastAPI dependency used in routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
