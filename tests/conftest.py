# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from infrastructure.database import Base
from routers.dependencies import get_db  # Adjust if your get_db is elsewhere

# In-memory DB URL. Alternatively: "sqlite:///./test_db.sqlite"
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.sqlite"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """
    Yields a session tied to the test DB.
    """
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Creates and drops tables once per test session.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """
    A per-test fixture for direct DB access in repository/service tests.
    """
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """
    A TestClient that uses the overridden DB dependency.
    """
    # Override FastAPI's get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    # Return a test client that calls our FastAPI `app`
    return TestClient(app)
