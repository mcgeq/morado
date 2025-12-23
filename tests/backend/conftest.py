"""Pytest configuration and fixtures for backend tests."""

import sys
from pathlib import Path

import pytest

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from morado.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    """Create a new database session for a test."""
    session_local = sessionmaker(bind=engine)
    session = session_local()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def db_session(session):
    """Alias for session fixture for compatibility."""
    return session
