#!/usr/bin/env python
"""Database initialization script.

This script initializes the database by:
1. Creating all tables defined in the models
2. Optionally running Alembic migrations
3. Optionally seeding initial data

Usage:
    # Create tables directly (development)
    python backend/scripts/init_db.py

    # Use Alembic migrations (recommended for production)
    python backend/scripts/init_db.py --migrate

    # Create tables and seed data
    python backend/scripts/init_db.py --seed

    # Full initialization with migrations and seed data
    python backend/scripts/init_db.py --migrate --seed

    # Specify environment
    python backend/scripts/init_db.py --env production

    # Drop and recreate tables (WARNING: destroys all data!)
    python backend/scripts/init_db.py --drop --force

Requirements:
    - PostgreSQL database must be running
    - Database credentials configured in environment or config file
"""

import argparse
import os
import subprocess
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

# Import all models to register them with SQLAlchemy
from morado.models.base import Base
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


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
        # Convert postgresql:// to postgresql+psycopg:// if needed
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
                    # Convert postgresql:// to postgresql+psycopg:// if needed
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


def test_connection(database_url: str) -> bool:
    """Test database connection.

    Args:
        database_url: Database connection URL

    Returns:
        True if connection successful, False otherwise
    """
    try:
        engine = create_engine(database_url, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except OperationalError as e:
        print(f"   Connection failed: {e}")
        return False


def create_tables(database_url: str, echo: bool = False) -> None:
    """Create all database tables.

    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL statements
    """
    print("\nCreating database tables...")
    engine = create_engine(database_url, echo=echo)

    try:
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")

        print("\nCreated tables:")
        for table_name in sorted(Base.metadata.tables.keys()):
            print(f"  - {table_name}")
    finally:
        engine.dispose()


def drop_tables(database_url: str, echo: bool = False) -> None:
    """Drop all database tables.

    WARNING: This will delete all data!

    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL statements
    """
    print("\nDropping all database tables...")
    engine = create_engine(database_url, echo=echo)

    try:
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped successfully!")
    finally:
        engine.dispose()


def run_migrations(direction: str = "upgrade", revision: str = "head") -> bool:
    """Run Alembic migrations.

    Args:
        direction: Migration direction ('upgrade' or 'downgrade')
        revision: Target revision (default: 'head' for upgrade)

    Returns:
        True if migrations successful, False otherwise
    """
    print(f"\nRunning Alembic migrations ({direction} to {revision})...")

    alembic_ini = BACKEND_DIR / "alembic.ini"
    if not alembic_ini.exists():
        print(f"   Error: alembic.ini not found at {alembic_ini}")
        return False

    try:
        result = subprocess.run(
            ["alembic", direction, revision],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print("✓ Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   Error running migrations: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print("   Error: alembic command not found. Install with: pip install alembic")
        return False


def seed_data(environment: str = "development") -> bool:
    """Seed initial data into the database.

    Args:
        environment: Environment name

    Returns:
        True if seeding successful, False otherwise
    """
    print("\nSeeding initial data...")

    seed_script = BACKEND_DIR / "scripts" / "database" / "seed_four_layer_data.py"
    if not seed_script.exists():
        # Try the wrapper script
        seed_script = BACKEND_DIR / "scripts" / "seed_data.py"
        if not seed_script.exists():
            print("   Error: Seed script not found")
            return False

    try:
        result = subprocess.run(
            [sys.executable, str(seed_script), "--env", environment],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"   Error seeding data: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def main():
    """Main entry point for database initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize the Morado database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create tables directly (development)
  python init_db.py

  # Use Alembic migrations (recommended for production)
  python init_db.py --migrate

  # Create tables and seed data
  python init_db.py --seed

  # Full initialization with migrations and seed data
  python init_db.py --migrate --seed

  # Specify environment
  python init_db.py --env production

  # Drop and recreate tables (WARNING: destroys all data!)
  python init_db.py --drop --force
        """,
    )

    parser.add_argument(
        "--env",
        "--environment",
        dest="environment",
        choices=["development", "testing", "production"],
        default="development",
        help="Environment to initialize (default: development)",
    )

    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Use Alembic migrations instead of direct table creation",
    )

    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed initial test data after table creation",
    )

    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (WARNING: destroys all data!)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force destructive operations without confirmation",
    )

    parser.add_argument(
        "--echo",
        action="store_true",
        help="Echo SQL statements (verbose mode)",
    )

    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Only test database connection, don't create tables",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Morado Database Initialization")
    print("=" * 60)
    print(f"\nEnvironment: {args.environment}")

    # Get database URL
    database_url = get_database_url(args.environment)
    print(f"Database URL: {mask_password(database_url)}")

    # Test connection
    print("\nTesting database connection...")
    if not test_connection(database_url):
        print("\n✗ Failed to connect to database")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is running")
        print("  2. Database exists")
        print("  3. Credentials are correct")
        sys.exit(1)
    print("✓ Database connection successful!")

    if args.test_connection:
        print("\n✓ Connection test completed")
        sys.exit(0)

    # Handle drop operation
    if args.drop:
        if not args.force:
            print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() != "yes":
                print("Operation cancelled.")
                sys.exit(0)
        drop_tables(database_url, echo=args.echo)

    # Create tables or run migrations
    if args.migrate:
        if not run_migrations():
            print("\n✗ Migration failed")
            sys.exit(1)
    else:
        create_tables(database_url, echo=args.echo)

    # Seed data if requested
    if args.seed:
        if not seed_data(args.environment):
            print("\n✗ Data seeding failed")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ Database initialization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
