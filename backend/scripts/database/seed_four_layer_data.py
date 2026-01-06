"""Seed test data for the four-layer architecture.

This script creates sample data for all layers:
- Layer 1: Headers, Bodies, API Definitions
- Layer 2: Test Scripts, Script Parameters
- Layer 3: Test Components, Component Scripts
- Layer 4: Test Cases, Test Case Scripts, Test Case Components
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import tomli
import argparse

# Set encoding environment variables
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Import all models
from morado.models.user import User, UserRole
from morado.models.api_component import Header, Body, ApiDefinition, HeaderScope, BodyType, HttpMethod
from morado.models.script import TestScript, ScriptParameter, ScriptType, ParameterType
from morado.models.component import TestComponent, ComponentScript, ComponentType, ExecutionMode
from morado.models.test_case import TestCase, TestCaseScript, TestCaseComponent, TestCasePriority, TestCaseStatus
from morado.common.utils.uuid import generate_uuid


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
        print(f"   Using DATABASE_URL from environment variable")
        # Convert postgresql:// to postgresql+psycopg:// if needed
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return db_url
    
    # Priority 2: Config file
    config_path = Path(__file__).parent.parent.parent / "config" / f"{environment}.toml"
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                config = tomli.load(f)
                db_url = config.get("database_url")
                if db_url:
                    print(f"   Using database_url from {config_path.name}")
                    # Convert postgresql:// to postgresql+psycopg:// if needed
                    if db_url.startswith("postgresql://"):
                        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
                    return db_url
        except Exception as e:
            print(f"   Warning: Failed to read config file: {e}")
    
    # Priority 3: Default fallback
    print(f"   Using default database URL (fallback)")
    return "postgresql+psycopg://postgres:postgres@localhost:5432/morado"


def create_sample_user(session: Session) -> User:
    """Create a sample user."""
    user = User(
        uuid=generate_uuid(),
        username="admin",
        email="admin@morado.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqKqQqKq",  # password: admin123
        full_name="系统管理员",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True
    )
    session.add(user)
    session.flush()
    return user


def create_sample_headers(session: Session, user: User) -> list[Header]:
    """Create sample Header components."""
    headers = [
        Header(
            uuid=generate_uuid(),
            name="认证Header",
            description="包含Bearer Token的认证Header",
            headers={
                "Authorization": "Bearer ${token}",
                "X-API-Key": "${api_key}"
            },
            scope=HeaderScope.GLOBAL,
            is_active=True,
            version="1.0.0",
            tags=["auth", "security"],
            created_by=user.id
        ),
        Header(
            uuid=generate_uuid(),
            name="JSON Content-Type",
            description="JSON格式的Content-Type Header",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            scope=HeaderScope.GLOBAL,
            is_active=True,
            version="1.0.0",
            tags=["json", "content-type"],
            created_by=user.id
        ),
        Header(
            uuid=generate_uuid(),
            name="XML Content-Type",
            description="XML格式的Content-Type Header",
            headers={
                "Content-Type": "application/xml",
                "Accept": "application/xml"
            },
            scope=HeaderScope.GLOBAL,
            is_active=True,
            version="1.0.0",
            tags=["xml", "content-type"],
            created_by=user.id
        )
    ]
    
    for header in headers:
        session.add(header)
    session.flush()
    return headers


def create_sample_bodies(session: Session, user: User) -> list[Body]:
    """Create sample Body components."""
    bodies = [
        Body(
            uuid=generate_uuid(),
            name="用户信息Body",
            description="用户基本信息的请求/响应体",
            body_type=BodyType.BOTH,
            content_type="application/json",
            body_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["name", "email"]
            },
            example_data={
                "name": "张三",
                "age": 25,
                "email": "zhangsan@example.com"
            },
            scope=HeaderScope.GLOBAL,
            is_active=True,
            version="1.0.0",
            tags=["user", "profile"],
            created_by=user.id
        ),
        Body(
            uuid=generate_uuid(),
            name="订单信息Body",
            description="订单信息的请求/响应体",
            body_type=BodyType.BOTH,
            content_type="application/json",
            body_schema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "product_name": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "price": {"type": "number"}
                },
                "required": ["order_id", "product_name", "quantity", "price"]
            },
            example_data={
                "order_id": "ORD-2024-001",
                "product_name": "测试产品",
                "quantity": 2,
                "price": 99.99
            },
            scope=HeaderScope.GLOBAL,
            is_active=True,
            version="1.0.0",
            tags=["order", "commerce"],
            created_by=user.id
        ),
        Body(
            uuid=generate_uuid(),
            name="登录请求Body",
            description="用户登录请求体",
            body_type=BodyType.REQUEST,
            content_type="application/json",
            body_schema={
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            },
            example_data={
                "username": "testuser",
                "password": "Test@123"
            },
            scope=HeaderScope.GLOBAL,
            is_active=True,
            version="1.0.0",
            tags=["auth", "login"],
            created_by=user.id
        )
    ]
    
    for body in bodies:
        session.add(body)
    session.flush()
    return bodies


def create_sample_api_definitions(session: Session, user: User, headers: list[Header], bodies: list[Body]) -> list[ApiDefinition]:
    """Create sample API Definitions."""
    api_defs = [
        # 方式1：引用Header和Body组件
        ApiDefinition(
            uuid=generate_uuid(),
            name="获取用户信息",
            description="根据用户ID获取用户详细信息",
            method=HttpMethod.GET,
            path="/api/users/{id}",
            base_url="https://api.example.com",
            header_id=headers[0].id,  # 认证Header
            response_body_id=bodies[0].id,  # 用户信息Body
            path_parameters={"id": {"type": "integer", "description": "用户ID"}},
            timeout=30,
            is_active=True,
            version="1.0.0",
            tags=["user", "get"],
            created_by=user.id
        ),
        # 方式2：引用Header + 内联Body
        ApiDefinition(
            uuid=generate_uuid(),
            name="创建用户",
            description="创建新用户",
            method=HttpMethod.POST,
            path="/api/users",
            base_url="https://api.example.com",
            header_id=headers[1].id,  # JSON Content-Type
            inline_request_body={
                "name": "李四",
                "age": 30,
                "email": "lisi@example.com"
            },
            inline_response_body={
                "id": 123,
                "name": "李四",
                "created_at": "2024-12-24T10:00:00Z"
            },
            timeout=30,
            is_active=True,
            version="1.0.0",
            tags=["user", "create"],
            created_by=user.id
        ),
        ApiDefinition(
            uuid=generate_uuid(),
            name="用户登录",
            description="用户登录接口",
            method=HttpMethod.POST,
            path="/api/auth/login",
            base_url="https://api.example.com",
            header_id=headers[1].id,  # JSON Content-Type
            request_body_id=bodies[2].id,  # 登录请求Body
            inline_response_body={
                "token": "${auth_token}",
                "user_id": "${user_id}",
                "expires_in": 3600
            },
            timeout=30,
            is_active=True,
            version="1.0.0",
            tags=["auth", "login"],
            created_by=user.id
        ),
        ApiDefinition(
            uuid=generate_uuid(),
            name="获取订单列表",
            description="获取用户的订单列表",
            method=HttpMethod.GET,
            path="/api/orders",
            base_url="https://api.example.com",
            header_id=headers[0].id,  # 认证Header
            query_parameters={
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 10}
            },
            inline_response_body={
                "total": 100,
                "page": 1,
                "page_size": 10,
                "items": []
            },
            timeout=30,
            is_active=True,
            version="1.0.0",
            tags=["order", "list"],
            created_by=user.id
        )
    ]
    
    for api_def in api_defs:
        session.add(api_def)
    session.flush()
    return api_defs


def create_sample_scripts(session: Session, user: User, api_defs: list[ApiDefinition]) -> list[TestScript]:
    """Create sample Test Scripts."""
    scripts = [
        TestScript(
            uuid=generate_uuid(),
            name="测试用户登录",
            description="验证用户登录功能",
            api_definition_id=api_defs[2].id,  # 用户登录API
            script_type=ScriptType.MAIN,
            execution_order=1,
            variables={
                "username": "testuser",
                "password": "Test@123"
            },
            assertions=[
                {
                    "type": "status_code",
                    "expected": 200,
                    "message": "登录应该返回200状态码"
                },
                {
                    "type": "json_path",
                    "path": "$.token",
                    "assertion": "exists",
                    "message": "响应应该包含token"
                }
            ],
            extract_variables={
                "auth_token": "$.token",
                "user_id": "$.user_id"
            },
            output_variables=["auth_token", "user_id"],
            debug_mode=False,
            retry_count=0,
            retry_interval=1.0,
            is_active=True,
            version="1.0.0",
            tags=["auth", "login"],
            created_by=user.id
        ),
        TestScript(
            uuid=generate_uuid(),
            name="获取用户信息",
            description="使用登录后的token获取用户信息",
            api_definition_id=api_defs[0].id,  # 获取用户信息API
            script_type=ScriptType.MAIN,
            execution_order=2,
            variables={
                "user_id": "${user_id}",
                "token": "${auth_token}"
            },
            assertions=[
                {
                    "type": "status_code",
                    "expected": 200,
                    "message": "应该成功获取用户信息"
                },
                {
                    "type": "json_path",
                    "path": "$.name",
                    "assertion": "exists",
                    "message": "响应应该包含用户名"
                }
            ],
            debug_mode=False,
            retry_count=0,
            retry_interval=1.0,
            is_active=True,
            version="1.0.0",
            tags=["user", "get"],
            created_by=user.id
        ),
        TestScript(
            uuid=generate_uuid(),
            name="创建新用户",
            description="创建一个新用户",
            api_definition_id=api_defs[1].id,  # 创建用户API
            script_type=ScriptType.MAIN,
            execution_order=1,
            variables={
                "name": "测试用户${timestamp}",
                "age": 25,
                "email": "test${random_int}@example.com"
            },
            assertions=[
                {
                    "type": "status_code",
                    "expected": 201,
                    "message": "创建用户应该返回201状态码"
                }
            ],
            extract_variables={
                "new_user_id": "$.id"
            },
            output_variables=["new_user_id"],
            debug_mode=False,
            retry_count=0,
            retry_interval=1.0,
            is_active=True,
            version="1.0.0",
            tags=["user", "create"],
            created_by=user.id
        ),
        TestScript(
            uuid=generate_uuid(),
            name="准备测试环境",
            description="前置脚本：准备测试数据",
            api_definition_id=api_defs[1].id,  # 创建用户API
            script_type=ScriptType.SETUP,
            execution_order=0,
            variables={
                "test_data_prefix": "test_"
            },
            debug_mode=False,
            retry_count=0,
            retry_interval=1.0,
            is_active=True,
            version="1.0.0",
            tags=["setup"],
            created_by=user.id
        )
    ]
    
    for script in scripts:
        session.add(script)
    session.flush()
    
    # Add script parameters
    params = [
        ScriptParameter(
            uuid=generate_uuid(),
            script_id=scripts[0].id,
            name="username",
            description="用户名",
            parameter_type=ParameterType.STRING,
            default_value="testuser",
            is_required=True,
            validation_rules={
                "min_length": 3,
                "max_length": 50,
                "pattern": "^[a-zA-Z0-9_]+$"
            },
            order=1,
            is_sensitive=False
        ),
        ScriptParameter(
            uuid=generate_uuid(),
            script_id=scripts[0].id,
            name="password",
            description="密码",
            parameter_type=ParameterType.STRING,
            is_required=True,
            is_sensitive=True,
            order=2
        )
    ]
    
    for param in params:
        session.add(param)
    session.flush()
    
    return scripts


def create_sample_components(session: Session, user: User, scripts: list[TestScript]) -> list[TestComponent]:
    """Create sample Test Components."""
    components = [
        TestComponent(
            uuid=generate_uuid(),
            name="用户登录流程",
            description="包含登录和获取用户信息的完整流程",
            component_type=ComponentType.SIMPLE,
            execution_mode=ExecutionMode.SEQUENTIAL,
            shared_variables={
                "base_url": "https://api.example.com",
                "timeout": 30
            },
            timeout=300,
            retry_count=0,
            continue_on_failure=False,
            is_active=True,
            version="1.0.0",
            tags=["auth", "user"],
            created_by=user.id
        ),
        TestComponent(
            uuid=generate_uuid(),
            name="用户管理完整测试",
            description="包含创建用户、登录、获取信息的完整测试",
            component_type=ComponentType.COMPOSITE,
            execution_mode=ExecutionMode.SEQUENTIAL,
            shared_variables={
                "test_env": "staging"
            },
            timeout=600,
            retry_count=0,
            continue_on_failure=False,
            is_active=True,
            version="1.0.0",
            tags=["user", "integration"],
            created_by=user.id
        )
    ]
    
    for component in components:
        session.add(component)
    session.flush()
    
    # Create nested component (child of second component)
    nested_component = TestComponent(
        uuid=generate_uuid(),
        name="登录子流程",
        description="嵌套在用户管理测试中的登录子流程",
        component_type=ComponentType.SIMPLE,
        execution_mode=ExecutionMode.SEQUENTIAL,
        parent_component_id=components[1].id,  # 父组件
        shared_variables={},
        timeout=300,
        retry_count=0,
        continue_on_failure=False,
        is_active=True,
        version="1.0.0",
        tags=["auth", "nested"],
        created_by=user.id
    )
    session.add(nested_component)
    session.flush()
    components.append(nested_component)
    
    # Add scripts to components
    component_scripts = [
        ComponentScript(
            component_id=components[0].id,
            script_id=scripts[0].id,  # 测试用户登录
            execution_order=1,
            is_enabled=True,
            script_parameters={
                "username": "component_user",
                "password": "Component@123"
            },
            description="登录脚本"
        ),
        ComponentScript(
            component_id=components[0].id,
            script_id=scripts[1].id,  # 获取用户信息
            execution_order=2,
            is_enabled=True,
            description="获取用户信息脚本"
        ),
        ComponentScript(
            component_id=components[1].id,
            script_id=scripts[3].id,  # 准备测试环境
            execution_order=0,
            is_enabled=True,
            description="前置脚本"
        ),
        ComponentScript(
            component_id=components[1].id,
            script_id=scripts[2].id,  # 创建新用户
            execution_order=1,
            is_enabled=True,
            description="创建用户脚本"
        )
    ]
    
    for cs in component_scripts:
        session.add(cs)
    session.flush()
    
    return components


def create_sample_test_cases(session: Session, user: User, scripts: list[TestScript], components: list[TestComponent]) -> list[TestCase]:
    """Create sample Test Cases."""
    test_cases = [
        TestCase(
            uuid=generate_uuid(),
            name="用户注册登录完整流程测试",
            description="测试用户从注册到登录的完整流程",
            priority=TestCasePriority.HIGH,
            status=TestCaseStatus.ACTIVE,
            category="用户管理",
            tags=["user", "auth", "integration"],
            preconditions="系统正常运行，数据库可访问",
            postconditions="测试数据已清理",
            execution_order="sequential",
            timeout=300,
            retry_count=0,
            continue_on_failure=False,
            test_data={
                "username": "test_user_001",
                "password": "Test@123",
                "email": "test001@example.com"
            },
            environment="test",
            version="1.0.0",
            is_automated=True,
            created_by=user.id
        ),
        TestCase(
            uuid=generate_uuid(),
            name="用户信息查询测试",
            description="测试用户信息查询功能",
            priority=TestCasePriority.MEDIUM,
            status=TestCaseStatus.ACTIVE,
            category="用户管理",
            tags=["user", "query"],
            execution_order="sequential",
            timeout=300,
            retry_count=0,
            continue_on_failure=False,
            test_data={
                "user_id": 123
            },
            environment="test",
            version="1.0.0",
            is_automated=True,
            created_by=user.id
        ),
        TestCase(
            uuid=generate_uuid(),
            name="组件嵌套测试",
            description="测试组件嵌套功能",
            priority=TestCasePriority.HIGH,
            status=TestCaseStatus.ACTIVE,
            category="系统测试",
            tags=["component", "nested"],
            execution_order="sequential",
            timeout=600,
            retry_count=0,
            continue_on_failure=False,
            environment="test",
            version="1.0.0",
            is_automated=True,
            created_by=user.id
        )
    ]
    
    for test_case in test_cases:
        session.add(test_case)
    session.flush()
    
    # Add scripts and components to test cases
    test_case_scripts = [
        TestCaseScript(
            test_case_id=test_cases[0].id,
            script_id=scripts[2].id,  # 创建新用户
            execution_order=1,
            is_enabled=True,
            script_parameters={
                "name": "测试用户",
                "email": "test@example.com"
            },
            description="创建测试用户"
        ),
        TestCaseScript(
            test_case_id=test_cases[0].id,
            script_id=scripts[0].id,  # 测试用户登录
            execution_order=2,
            is_enabled=True,
            description="登录测试"
        ),
        TestCaseScript(
            test_case_id=test_cases[1].id,
            script_id=scripts[1].id,  # 获取用户信息
            execution_order=1,
            is_enabled=True,
            description="查询用户信息"
        )
    ]
    
    test_case_components = [
        TestCaseComponent(
            test_case_id=test_cases[0].id,
            component_id=components[0].id,  # 用户登录流程
            execution_order=3,
            is_enabled=True,
            component_parameters={
                "base_url": "https://test.example.com"
            },
            description="执行登录流程组件"
        ),
        TestCaseComponent(
            test_case_id=test_cases[2].id,
            component_id=components[1].id,  # 用户管理完整测试（包含嵌套组件）
            execution_order=1,
            is_enabled=True,
            description="执行包含嵌套组件的测试"
        )
    ]
    
    for tcs in test_case_scripts:
        session.add(tcs)
    
    for tcc in test_case_components:
        session.add(tcc)
    
    session.flush()
    
    return test_cases


def seed_data(environment: str = "development"):
    """Seed all test data.
    
    Args:
        environment: Environment name (development, testing, production)
    """
    print(f"Seeding data for environment: {environment}")
    print("="*60)
    
    # Get database URL
    database_url = get_database_url(environment)
    
    # Mask password in display
    display_url = database_url
    if "@" in display_url:
        parts = display_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split("://")[1]
            user = user_pass.split(":")[0]
            display_url = display_url.replace(user_pass, f"{user}:****")
    
    print(f"Connecting to database: {display_url}")
    
    engine = create_engine(database_url, echo=False)
    
    with Session(engine) as session:
        print("\n1. Creating sample user...")
        user = create_sample_user(session)
        print(f"   ✓ Created user: {user.username}")
        
        print("\n2. Creating sample Headers (Layer 1)...")
        headers = create_sample_headers(session, user)
        print(f"   ✓ Created {len(headers)} headers")
        
        print("\n3. Creating sample Bodies (Layer 1)...")
        bodies = create_sample_bodies(session, user)
        print(f"   ✓ Created {len(bodies)} bodies")
        
        print("\n4. Creating sample API Definitions (Layer 1)...")
        api_defs = create_sample_api_definitions(session, user, headers, bodies)
        print(f"   ✓ Created {len(api_defs)} API definitions")
        
        print("\n5. Creating sample Test Scripts (Layer 2)...")
        scripts = create_sample_scripts(session, user, api_defs)
        print(f"   ✓ Created {len(scripts)} test scripts")
        
        print("\n6. Creating sample Test Components (Layer 3)...")
        components = create_sample_components(session, user, scripts)
        print(f"   ✓ Created {len(components)} test components (including nested)")
        
        print("\n7. Creating sample Test Cases (Layer 4)...")
        test_cases = create_sample_test_cases(session, user, scripts, components)
        print(f"   ✓ Created {len(test_cases)} test cases")
        
        print("\n8. Committing all changes...")
        session.commit()
        print("   ✓ All data committed successfully!")
        
        print("\n" + "="*60)
        print("✓ Test data seeding completed successfully!")
        print("="*60)
        print("\nSummary:")
        print(f"  - Users: 1")
        print(f"  - Headers: {len(headers)}")
        print(f"  - Bodies: {len(bodies)}")
        print(f"  - API Definitions: {len(api_defs)}")
        print(f"  - Test Scripts: {len(scripts)}")
        print(f"  - Test Components: {len(components)}")
        print(f"  - Test Cases: {len(test_cases)}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Seed test data for the four-layer architecture"
    )
    parser.add_argument(
        "--env",
        "--environment",
        dest="environment",
        choices=["development", "testing", "production"],
        default="development",
        help="Environment to seed data for (default: development)"
    )
    
    args = parser.parse_args()
    
    try:
        seed_data(environment=args.environment)
    except Exception as e:
        print(f"\n✗ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
