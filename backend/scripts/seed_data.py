#!/usr/bin/env python
"""Test data seeding script.

This script seeds the database with test data for development and testing.
It wraps the detailed seed_four_layer_data.py script and provides a simpler
interface for common seeding operations.

Usage:
    # Seed data for development environment
    python backend/scripts/seed_data.py

    # Seed data for specific environment
    python backend/scripts/seed_data.py --env testing

    # Clear existing data before seeding
    python backend/scripts/seed_data.py --clear

    # Seed minimal data only
    python backend/scripts/seed_data.py --minimal

Requirements:
    - Database must be initialized (tables created)
    - PostgreSQL database must be running
"""

import argparse
import os
import sys
from pathlib import Path

# Set encoding environment variables before importing psycopg
os.environ["PGCLIENTENCODING"] = "UTF8"
os.environ["PYTHONIOENCODING"] = "utf-8"

# Add the src directory to the path
BACKEND_DIR = Path(__file__).parent.parent
SRC_DIR = BACKEND_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

import tomllib

from morado.common.utils.uuid import generate_uuid
from morado.models.api_component import (
    ApiDefinition,
    Body,
    BodyType,
    Header,
    HeaderScope,
    HttpMethod,
)
from morado.models.script import ScriptType, TestScript
from morado.models.test_case import (
    TestCase,
    TestCasePriority,
    TestCaseScript,
    TestCaseStatus,
)
from morado.models.test_suite import TestSuite, TestSuiteCase

# Import models
from morado.models.user import User, UserRole
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session


def get_database_url(environment: str = "development") -> str:
    """Get database URL from environment variable or config file.

    Priority:
    1. DATABASE_URL environment variable
    2. Config file (backend/config/{environment}.toml)
    3. Default fallback

    Args:
        environment: Environment name (development, testing, production)

    Returns:
        Database connection URL
    """
    # Priority 1: Environment variable
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        print("   Using DATABASE_URL from environment variable")
        if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return db_url

    # Priority 2: Config file
    config_path = BACKEND_DIR / "config" / f"{environment}.toml"
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
                db_url = config.get("database_url")
                if db_url:
                    print(f"   Using database_url from {config_path.name}")
                    if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
                        db_url = db_url.replace(
                            "postgresql://", "postgresql+psycopg://", 1
                        )
                    return db_url
        except Exception as e:
            print(f"   Warning: Failed to read config file: {e}")

    # Priority 3: Default fallback
    print("   Using default database URL (fallback)")
    return "postgresql+psycopg://postgres:postgres@localhost:5432/morado"


def mask_password(url: str) -> str:
    """Mask password in database URL for display."""
    if "@" in url:
        parts = url.split("@")
        if ":" in parts[0]:
            protocol_user = parts[0].rsplit(":", 1)
            if len(protocol_user) == 2:
                return f"{protocol_user[0]}:****@{parts[1]}"
    return url


def clear_all_data(session: Session) -> None:
    """Clear all data from the database.

    This clears data in the correct order to respect foreign key constraints.

    Args:
        session: SQLAlchemy session
    """
    print("\nClearing existing data...")

    # Clear in reverse order of dependencies
    tables_to_clear = [
        "test_suite_cases",
        "test_case_components",
        "test_case_scripts",
        "component_scripts",
        "script_parameters",
        "test_executions",
        "execution_results",
        "test_cases",
        "test_components",
        "test_scripts",
        "api_definitions",
        "bodies",
        "headers",
        "test_suites",
        "users",
    ]

    for table_name in tables_to_clear:
        try:
            session.execute(text(f"DELETE FROM {table_name}"))
            print(f"   ✓ Cleared {table_name}")
        except Exception as e:
            print(f"   ⚠ Could not clear {table_name}: {e}")

    session.commit()
    print("✓ All data cleared!")


def create_admin_user(session: Session) -> User:
    """Create an admin user.

    Args:
        session: SQLAlchemy session

    Returns:
        Created User instance
    """
    user = User(
        uuid=generate_uuid(),
        username="admin",
        email="admin@morado.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqKqQqKq",
        full_name="系统管理员",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True,
    )
    session.add(user)
    session.flush()
    return user


def create_test_user(session: Session) -> User:
    """Create a test user.

    Args:
        session: SQLAlchemy session

    Returns:
        Created User instance
    """
    user = User(
        uuid=generate_uuid(),
        username="tester",
        email="tester@morado.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqKqQqKq",
        full_name="测试用户",
        role=UserRole.TESTER,
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    session.flush()
    return user


def seed_minimal_data(session: Session) -> dict:
    """Seed minimal data for basic functionality.

    Creates:
    - 1 admin user
    - 1 header
    - 1 body
    - 1 API definition
    - 1 test script
    - 1 test case

    Args:
        session: SQLAlchemy session

    Returns:
        Dictionary with created entities
    """
    print("\nSeeding minimal data...")

    # Create admin user
    print("   Creating admin user...")
    admin = create_admin_user(session)

    # Create a basic header
    print("   Creating basic header...")
    header = Header(
        uuid=generate_uuid(),
        name="JSON Header",
        description="Standard JSON content type header",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        scope=HeaderScope.GLOBAL,
        is_active=True,
        version="1.0.0",
        tags=["json", "standard"],
        created_by=admin.id,
    )
    session.add(header)
    session.flush()

    # Create a basic body
    print("   Creating basic body...")
    body = Body(
        uuid=generate_uuid(),
        name="Sample Request Body",
        description="A sample request body for testing",
        body_type=BodyType.REQUEST,
        content_type="application/json",
        body_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
            },
        },
        example_data={"message": "Hello, World!"},
        scope=HeaderScope.GLOBAL,
        is_active=True,
        version="1.0.0",
        tags=["sample"],
        created_by=admin.id,
    )
    session.add(body)
    session.flush()

    # Create an API definition
    print("   Creating API definition...")
    api_def = ApiDefinition(
        uuid=generate_uuid(),
        name="Health Check API",
        description="Simple health check endpoint",
        method=HttpMethod.GET,
        path="/api/health",
        base_url="https://api.example.com",
        header_id=header.id,
        timeout=30,
        is_active=True,
        version="1.0.0",
        tags=["health", "monitoring"],
        created_by=admin.id,
    )
    session.add(api_def)
    session.flush()

    # Create a test script
    print("   Creating test script...")
    script = TestScript(
        uuid=generate_uuid(),
        name="Health Check Test",
        description="Verify health check endpoint returns 200",
        api_definition_id=api_def.id,
        script_type=ScriptType.MAIN,
        execution_order=1,
        assertions=[
            {
                "type": "status_code",
                "expected": 200,
                "message": "Health check should return 200",
            }
        ],
        debug_mode=False,
        retry_count=0,
        retry_interval=1.0,
        is_active=True,
        version="1.0.0",
        tags=["health"],
        created_by=admin.id,
    )
    session.add(script)
    session.flush()

    # Create a test case
    print("   Creating test case...")
    test_case = TestCase(
        uuid=generate_uuid(),
        name="Basic Health Check",
        description="Verify system health check functionality",
        priority=TestCasePriority.HIGH,
        status=TestCaseStatus.ACTIVE,
        category="System",
        tags=["health", "smoke"],
        execution_order="sequential",
        timeout=60,
        retry_count=0,
        continue_on_failure=False,
        environment="test",
        version="1.0.0",
        is_automated=True,
        created_by=admin.id,
    )
    session.add(test_case)
    session.flush()

    # Link script to test case
    test_case_script = TestCaseScript(
        test_case_id=test_case.id,
        script_id=script.id,
        execution_order=1,
        is_enabled=True,
        description="Execute health check",
    )
    session.add(test_case_script)
    session.flush()

    session.commit()

    return {
        "users": [admin],
        "headers": [header],
        "bodies": [body],
        "api_definitions": [api_def],
        "scripts": [script],
        "test_cases": [test_case],
    }


def seed_full_data(session: Session) -> dict:
    """Seed full test data for comprehensive testing.

    This imports and runs the detailed seed_four_layer_data module.

    Args:
        session: SQLAlchemy session

    Returns:
        Dictionary with created entities
    """
    print("\nSeeding full test data...")

    # Import the detailed seeding functions
    from scripts.database.seed_four_layer_data import (
        create_sample_api_definitions,
        create_sample_bodies,
        create_sample_components,
        create_sample_headers,
        create_sample_scripts,
        create_sample_test_cases,
        create_sample_user,
    )

    # Create all sample data
    print("   Creating sample user...")
    user = create_sample_user(session)

    print("   Creating sample headers...")
    headers = create_sample_headers(session, user)

    print("   Creating sample bodies...")
    bodies = create_sample_bodies(session, user)

    print("   Creating sample API definitions...")
    api_defs = create_sample_api_definitions(session, user, headers, bodies)

    print("   Creating sample scripts...")
    scripts = create_sample_scripts(session, user, api_defs)

    print("   Creating sample components...")
    components = create_sample_components(session, user, scripts)

    print("   Creating sample test cases...")
    test_cases = create_sample_test_cases(session, user, scripts, components)

    # Create a test suite
    print("   Creating test suite...")
    test_suite = TestSuite(
        uuid=generate_uuid(),
        name="用户管理测试套件",
        description="包含所有用户管理相关的测试用例",
        tags=["user", "management"],
        is_active=True,
        version="1.0.0",
        created_by=user.id,
    )
    session.add(test_suite)
    session.flush()

    # Add test cases to suite
    for i, tc in enumerate(test_cases):
        suite_case = TestSuiteCase(
            test_suite_id=test_suite.id,
            test_case_id=tc.id,
            execution_order=i + 1,
            is_enabled=True,
        )
        session.add(suite_case)

    session.commit()

    return {
        "users": [user],
        "headers": headers,
        "bodies": bodies,
        "api_definitions": api_defs,
        "scripts": scripts,
        "components": components,
        "test_cases": test_cases,
        "test_suites": [test_suite],
    }


def print_summary(data: dict) -> None:
    """Print a summary of seeded data.

    Args:
        data: Dictionary with created entities
    """
    print("\n" + "=" * 60)
    print("Seeding Summary")
    print("=" * 60)

    for key, items in data.items():
        if items:
            print(f"  {key.replace('_', ' ').title()}: {len(items)}")


def main():
    """Main entry point for data seeding."""
    parser = argparse.ArgumentParser(
        description="Seed test data into the Morado database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seed data for development environment
  python seed_data.py

  # Seed data for specific environment
  python seed_data.py --env testing

  # Clear existing data before seeding
  python seed_data.py --clear

  # Seed minimal data only
  python seed_data.py --minimal
        """,
    )

    parser.add_argument(
        "--env",
        "--environment",
        dest="environment",
        choices=["development", "testing", "production"],
        default="development",
        help="Environment to seed data for (default: development)",
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding",
    )

    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Seed minimal data only (1 of each entity type)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force seeding without confirmation for production",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Morado Test Data Seeding")
    print("=" * 60)
    print(f"\nEnvironment: {args.environment}")
    print(f"Mode: {'Minimal' if args.minimal else 'Full'}")
    print(f"Clear existing: {args.clear}")

    # Safety check for production
    if args.environment == "production" and not args.force:
        print("\n⚠️  WARNING: You are about to seed data in PRODUCTION!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Operation cancelled.")
            sys.exit(0)

    # Get database URL
    database_url = get_database_url(args.environment)
    print(f"\nDatabase URL: {mask_password(database_url)}")

    # Create engine and session
    print("\nConnecting to database...")
    try:
        engine = create_engine(database_url, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connection successful!")
    except OperationalError as e:
        print(f"\n✗ Failed to connect to database: {e}")
        sys.exit(1)

    # Seed data
    with Session(engine) as session:
        try:
            # Clear existing data if requested
            if args.clear:
                clear_all_data(session)

            # Seed data
            if args.minimal:
                data = seed_minimal_data(session)
            else:
                data = seed_full_data(session)

            # Print summary
            print_summary(data)

            print("\n" + "=" * 60)
            print("✓ Data seeding completed successfully!")
            print("=" * 60)

        except IntegrityError as e:
            session.rollback()
            print(f"\n✗ Data integrity error: {e}")
            print("\nTip: Use --clear to remove existing data before seeding")
            sys.exit(1)
        except Exception as e:
            session.rollback()
            print(f"\n✗ Error seeding data: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
