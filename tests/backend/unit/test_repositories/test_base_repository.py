"""Unit tests for BaseRepository.

Tests basic CRUD operations provided by the base repository class.
"""

import pytest
from morado.models.base import Base
from morado.repositories.base import BaseRepository
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


# Test model for repository testing
class TestModel(Base):
    """Simple test model for repository testing."""

    __tablename__ = "test_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)


@pytest.fixture
def test_repo():
    """Create a test repository instance."""
    return BaseRepository(TestModel)


@pytest.fixture
def sample_data(session):
    """Create sample test data."""
    items = [
        TestModel(uuid="uuid-1", name="Item 1", value=10, is_active=True),
        TestModel(uuid="uuid-2", name="Item 2", value=20, is_active=True),
        TestModel(uuid="uuid-3", name="Item 3", value=30, is_active=False),
    ]
    for item in items:
        session.add(item)
    session.commit()
    return items


class TestBaseRepositoryCreate:
    """Test create operations."""

    def test_create_basic(self, session, test_repo):
        """Test creating a basic record."""
        item = test_repo.create(session, uuid="test-uuid", name="Test Item", value=100)

        assert item.id is not None
        assert item.uuid == "test-uuid"
        assert item.name == "Test Item"
        assert item.value == 100
        assert item.is_active is True

    def test_create_with_defaults(self, session, test_repo):
        """Test creating a record with default values."""
        item = test_repo.create(session, uuid="test-uuid", name="Test Item")

        assert item.value == 0
        assert item.is_active is True

    def test_create_multiple(self, session, test_repo):
        """Test creating multiple records."""
        item1 = test_repo.create(session, uuid="uuid-1", name="Item 1")
        item2 = test_repo.create(session, uuid="uuid-2", name="Item 2")

        assert item1.id != item2.id
        assert item1.uuid != item2.uuid


class TestBaseRepositoryRead:
    """Test read operations."""

    def test_get_by_id_exists(self, session, test_repo, sample_data):
        """Test getting a record by ID when it exists."""
        item = test_repo.get_by_id(session, sample_data[0].id)

        assert item is not None
        assert item.id == sample_data[0].id
        assert item.name == "Item 1"

    def test_get_by_id_not_exists(self, session, test_repo):
        """Test getting a record by ID when it doesn't exist."""
        item = test_repo.get_by_id(session, 999)

        assert item is None

    def test_get_by_uuid_exists(self, session, test_repo, sample_data):
        """Test getting a record by UUID when it exists."""
        item = test_repo.get_by_uuid(session, "uuid-1")

        assert item is not None
        assert item.uuid == "uuid-1"
        assert item.name == "Item 1"

    def test_get_by_uuid_not_exists(self, session, test_repo):
        """Test getting a record by UUID when it doesn't exist."""
        item = test_repo.get_by_uuid(session, "nonexistent-uuid")

        assert item is None

    def test_get_all_no_filters(self, session, test_repo, sample_data):
        """Test getting all records without filters."""
        items = test_repo.get_all(session)

        assert len(items) == 3
        assert items[0].name == "Item 1"
        assert items[1].name == "Item 2"
        assert items[2].name == "Item 3"

    def test_get_all_with_filters(self, session, test_repo, sample_data):
        """Test getting records with filters."""
        items = test_repo.get_all(session, filters={"is_active": True})

        assert len(items) == 2
        assert all(item.is_active for item in items)

    def test_get_all_with_pagination(self, session, test_repo, sample_data):
        """Test getting records with pagination."""
        items = test_repo.get_all(session, skip=1, limit=1)

        assert len(items) == 1
        assert items[0].name == "Item 2"

    def test_count_no_filters(self, session, test_repo, sample_data):
        """Test counting all records."""
        count = test_repo.count(session)

        assert count == 3

    def test_count_with_filters(self, session, test_repo, sample_data):
        """Test counting records with filters."""
        count = test_repo.count(session, filters={"is_active": True})

        assert count == 2


class TestBaseRepositoryUpdate:
    """Test update operations."""

    def test_update_single_field(self, session, test_repo, sample_data):
        """Test updating a single field."""
        item = sample_data[0]
        updated = test_repo.update(session, item, name="Updated Name")

        assert updated.id == item.id
        assert updated.name == "Updated Name"
        assert updated.value == 10  # Unchanged

    def test_update_multiple_fields(self, session, test_repo, sample_data):
        """Test updating multiple fields."""
        item = sample_data[0]
        updated = test_repo.update(session, item, name="New Name", value=999)

        assert updated.name == "New Name"
        assert updated.value == 999

    def test_update_nonexistent_field(self, session, test_repo, sample_data):
        """Test updating with a nonexistent field (should be ignored)."""
        item = sample_data[0]
        original_name = item.name
        updated = test_repo.update(session, item, nonexistent_field="value")

        assert updated.name == original_name
        assert not hasattr(updated, "nonexistent_field")


class TestBaseRepositoryDelete:
    """Test delete operations."""

    def test_delete_by_instance(self, session, test_repo, sample_data):
        """Test deleting a record by instance."""
        item = sample_data[0]
        item_id = item.id

        test_repo.delete(session, item)
        session.commit()

        deleted_item = test_repo.get_by_id(session, item_id)
        assert deleted_item is None

    def test_delete_by_id_exists(self, session, test_repo, sample_data):
        """Test deleting a record by ID when it exists."""
        item_id = sample_data[0].id

        result = test_repo.delete_by_id(session, item_id)
        session.commit()

        assert result is True
        deleted_item = test_repo.get_by_id(session, item_id)
        assert deleted_item is None

    def test_delete_by_id_not_exists(self, session, test_repo):
        """Test deleting a record by ID when it doesn't exist."""
        result = test_repo.delete_by_id(session, 999)

        assert result is False


class TestBaseRepositoryTransactions:
    """Test transaction handling."""

    def test_create_rollback(self, session, test_repo):
        """Test that rollback works after create."""
        test_repo.create(session, uuid="test-uuid", name="Test Item")
        session.rollback()

        items = test_repo.get_all(session)
        assert len(items) == 0

    def test_update_rollback(self, session, test_repo, sample_data):
        """Test that rollback works after update."""
        item = sample_data[0]
        original_name = item.name

        test_repo.update(session, item, name="Updated Name")
        session.rollback()

        refreshed_item = test_repo.get_by_id(session, item.id)
        assert refreshed_item.name == original_name

    def test_delete_rollback(self, session, test_repo, sample_data):
        """Test that rollback works after delete."""
        item = sample_data[0]
        item_id = item.id

        test_repo.delete(session, item)
        session.rollback()

        restored_item = test_repo.get_by_id(session, item_id)
        assert restored_item is not None
