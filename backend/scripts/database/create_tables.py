"""Create all database tables.

This script creates all tables defined in the models using SQLAlchemy.
"""

import sys
import os
from pathlib import Path

# Set encoding environment variables before importing psycopg2
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine

# Import all models to register them with SQLAlchemy
from morado.models.base import Base
from morado.models.user import User
from morado.models.api_component import Header, Body, ApiDefinition
from morado.models.script import TestScript, ScriptParameter
from morado.models.component import TestComponent, ComponentScript
from morado.models.test_case import TestCase, TestCaseScript, TestCaseComponent
from morado.models.test_suite import TestSuite, TestSuiteCase
from morado.models.test_execution import TestExecution, ExecutionResult

# Database connection - update with your credentials
# Using psycopg (psycopg3) instead of psycopg2
DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/morado"

def create_all_tables():
    """Create all database tables."""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("\nCreating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("\n✓ All tables created successfully!")
    print("\nCreated tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    try:
        create_all_tables()
    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        sys.exit(1)
