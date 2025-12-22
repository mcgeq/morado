"""Pytest configuration for integration tests."""

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from morado.api.v1.api_definition import ApiDefinitionController
from morado.api.v1.body import BodyController
from morado.api.v1.component import TestComponentController
from morado.api.v1.header import HeaderController
from morado.api.v1.script import TestScriptController
from morado.api.v1.test_case import TestCaseController
from morado.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
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
def session_factory(engine):
    """Create a session factory."""
    return sessionmaker(bind=engine)


@pytest.fixture
def db_session(session_factory):
    """Create a new database session for a test."""
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def provide_db_session(session_factory) -> Session:
    """Provide database session for dependency injection."""
    session = session_factory()
    try:
        return session
    finally:
        session.close()


@pytest.fixture
def app(session_factory):
    """Create a Litestar app for testing."""

    def session_dependency() -> Session:
        """Dependency that provides database session."""
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app = Litestar(
        route_handlers=[
            HeaderController,
            BodyController,
            ApiDefinitionController,
            TestScriptController,
            TestComponentController,
            TestCaseController,
        ],
        dependencies={
            "db_session": session_dependency,
        },
    )
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    with TestClient(app=app) as client:
        yield client
