"""Initial migration: Create four-layer architecture tables

Revision ID: 001
Revises: 
Create Date: 2024-12-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the four-layer architecture."""
    
    # Create users table first (referenced by other tables)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'DEVELOPER', 'TESTER', 'VIEWER', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_uuid'), 'users', ['uuid'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # Layer 1: Create headers table
    op.create_table(
        'headers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('headers', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('scope', sa.Enum('GLOBAL', 'PROJECT', 'PRIVATE', name='headerscope'), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_headers_uuid'), 'headers', ['uuid'], unique=False)

    # Layer 1: Create bodies table
    op.create_table(
        'bodies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('body_type', sa.Enum('REQUEST', 'RESPONSE', 'BOTH', name='bodytype'), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('body_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('example_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('scope', sa.Enum('GLOBAL', 'PROJECT', 'PRIVATE', name='headerscope'), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_bodies_uuid'), 'bodies', ['uuid'], unique=False)

    # Layer 1: Create api_definitions table
    op.create_table(
        'api_definitions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('method', sa.Enum('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', name='httpmethod'), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('base_url', sa.String(length=500), nullable=True),
        sa.Column('header_id', sa.Integer(), nullable=True),
        sa.Column('request_body_id', sa.Integer(), nullable=True),
        sa.Column('response_body_id', sa.Integer(), nullable=True),
        sa.Column('inline_request_body', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('inline_response_body', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('query_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('path_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['header_id'], ['headers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['request_body_id'], ['bodies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['response_body_id'], ['bodies.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_api_definitions_uuid'), 'api_definitions', ['uuid'], unique=False)

    # Layer 2: Create test_scripts table
    op.create_table(
        'test_scripts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('api_definition_id', sa.Integer(), nullable=False),
        sa.Column('script_type', sa.Enum('SETUP', 'MAIN', 'TEARDOWN', 'UTILITY', name='scripttype'), nullable=False),
        sa.Column('execution_order', sa.Integer(), nullable=False),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('assertions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('validators', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('pre_script', sa.Text(), nullable=True),
        sa.Column('post_script', sa.Text(), nullable=True),
        sa.Column('extract_variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('debug_mode', sa.Boolean(), nullable=False),
        sa.Column('debug_breakpoints', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('retry_interval', sa.Float(), nullable=False),
        sa.Column('timeout_override', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['api_definition_id'], ['api_definitions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_test_scripts_uuid'), 'test_scripts', ['uuid'], unique=False)

    # Layer 2: Create script_parameters table
    op.create_table(
        'script_parameters',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parameter_type', sa.Enum('STRING', 'INTEGER', 'FLOAT', 'BOOLEAN', 'JSON', 'ARRAY', 'FILE', name='parametertype'), nullable=False),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('validation_rules', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('group', sa.String(length=100), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['script_id'], ['test_scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_script_parameters_uuid'), 'script_parameters', ['uuid'], unique=False)

    # Layer 3: Create test_components table
    op.create_table(
        'test_components',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('component_type', sa.Enum('SIMPLE', 'COMPOSITE', 'TEMPLATE', name='componenttype'), nullable=False),
        sa.Column('execution_mode', sa.Enum('SEQUENTIAL', 'PARALLEL', 'CONDITIONAL', name='executionmode'), nullable=False),
        sa.Column('parent_component_id', sa.Integer(), nullable=True),
        sa.Column('shared_variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('continue_on_failure', sa.Boolean(), nullable=False),
        sa.Column('execution_condition', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_component_id'], ['test_components.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_test_components_uuid'), 'test_components', ['uuid'], unique=False)

    # Layer 3: Create component_scripts association table
    op.create_table(
        'component_scripts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('execution_order', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('script_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('execution_condition', sa.Text(), nullable=True),
        sa.Column('skip_on_condition', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['component_id'], ['test_components.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['script_id'], ['test_scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Layer 4: Create test_cases table
    op.create_table(
        'test_cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='testcasepriority'), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'DEPRECATED', 'ARCHIVED', name='testcasestatus'), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('preconditions', sa.Text(), nullable=True),
        sa.Column('postconditions', sa.Text(), nullable=True),
        sa.Column('execution_order', sa.String(length=20), nullable=False),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('continue_on_failure', sa.Boolean(), nullable=False),
        sa.Column('test_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('environment', sa.String(length=20), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('is_automated', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_test_cases_uuid'), 'test_cases', ['uuid'], unique=False)

    # Layer 4: Create test_case_scripts association table
    op.create_table(
        'test_case_scripts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('execution_order', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('script_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['script_id'], ['test_scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Layer 4: Create test_case_components association table
    op.create_table(
        'test_case_components',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('execution_order', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('component_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['component_id'], ['test_components.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create test_suites table
    op.create_table(
        'test_suites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('execution_order', sa.String(length=20), nullable=False),
        sa.Column('parallel_execution', sa.Boolean(), nullable=False),
        sa.Column('continue_on_failure', sa.Boolean(), nullable=False),
        sa.Column('schedule_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_scheduled', sa.Boolean(), nullable=False),
        sa.Column('environment', sa.String(length=20), nullable=False),
        sa.Column('global_variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_test_suites_uuid'), 'test_suites', ['uuid'], unique=False)
    
    # Create test_suite_cases association table
    op.create_table(
        'test_suite_cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('test_suite_id', sa.Integer(), nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=False),
        sa.Column('execution_order', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('case_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['test_suite_id'], ['test_suites.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create test_executions table
    op.create_table(
        'test_executions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=50), nullable=False),
        sa.Column('test_case_id', sa.Integer(), nullable=True),
        sa.Column('test_suite_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'PASSED', 'FAILED', 'ERROR', 'SKIPPED', 'CANCELLED', name='executionstatus'), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('environment', sa.String(length=20), nullable=False),
        sa.Column('executor', sa.String(length=100), nullable=True),
        sa.Column('execution_parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_count', sa.Integer(), nullable=False),
        sa.Column('passed_count', sa.Integer(), nullable=False),
        sa.Column('failed_count', sa.Integer(), nullable=False),
        sa.Column('error_count', sa.Integer(), nullable=False),
        sa.Column('skipped_count', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['test_case_id'], ['test_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_suite_id'], ['test_suites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_test_executions_uuid'), 'test_executions', ['uuid'], unique=False)

    # Create execution_results table
    op.create_table(
        'execution_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=True),
        sa.Column('component_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'PASSED', 'FAILED', 'ERROR', 'SKIPPED', 'CANCELLED', name='executionstatus'), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('request_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('response_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('assertions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('screenshots', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['execution_id'], ['test_executions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['script_id'], ['test_scripts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['component_id'], ['test_components.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('execution_results')
    op.drop_table('test_executions')
    op.drop_table('test_suite_cases')
    op.drop_table('test_suites')
    op.drop_table('test_case_components')
    op.drop_table('test_case_scripts')
    op.drop_table('test_cases')
    op.drop_table('component_scripts')
    op.drop_table('test_components')
    op.drop_table('script_parameters')
    op.drop_table('test_scripts')
    op.drop_table('api_definitions')
    op.drop_table('bodies')
    op.drop_table('headers')
    op.drop_table('users')
