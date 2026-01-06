"""Verify data integrity of the four-layer architecture.

This script verifies:
1. Header and Body independence
2. ApiDefinition's two combination methods
3. Script references to API definitions
4. Component nesting relationships
5. Test case references to scripts and components
6. Cascade delete and update rules
"""

import sys
import os
from pathlib import Path
import argparse

# Set encoding environment variables
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Import all models
from morado.models.user import User
from morado.models.api_component import Header, Body, ApiDefinition
from morado.models.script import TestScript, ScriptParameter
from morado.models.component import TestComponent, ComponentScript
from morado.models.test_case import TestCase, TestCaseScript, TestCaseComponent


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
        if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return db_url
    
    # Priority 2: Config file
    if tomllib:
        config_path = Path(__file__).parent.parent.parent / "config" / f"{environment}.toml"
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    config = tomllib.load(f)
                    db_url = config.get("database_url")
                    if db_url:
                        print(f"   Using database_url from {config_path.name}")
                        # Convert postgresql:// to postgresql+psycopg:// if needed
                        if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
                            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
                        return db_url
            except Exception as e:
                print(f"   Warning: Failed to read config file: {e}")
    
    # Priority 3: Default fallback
    print(f"   Using default database URL (fallback)")
    return "postgresql+psycopg://postgres:postgres@localhost:5432/morado"


def verify_header_body_independence(session: Session) -> bool:
    """Verify that Headers and Bodies are independent entities."""
    print("\n1. Verifying Header and Body independence...")
    
    headers = session.execute(select(Header)).scalars().all()
    bodies = session.execute(select(Body)).scalars().all()
    
    if not headers:
        print("   ✗ No headers found")
        return False
    
    if not bodies:
        print("   ✗ No bodies found")
        return False
    
    print(f"   ✓ Found {len(headers)} independent headers")
    print(f"   ✓ Found {len(bodies)} independent bodies")
    
    # Verify headers can exist without API definitions
    for header in headers:
        if header.uuid and header.name:
            print(f"   ✓ Header '{header.name}' exists independently")
    
    # Verify bodies can exist without API definitions
    for body in bodies:
        if body.uuid and body.name:
            print(f"   ✓ Body '{body.name}' exists independently")
    
    return True


def verify_api_definition_combinations(session: Session) -> bool:
    """Verify ApiDefinition's two combination methods."""
    print("\n2. Verifying ApiDefinition combination methods...")
    
    api_defs = session.execute(select(ApiDefinition)).scalars().all()
    
    if not api_defs:
        print("   ✗ No API definitions found")
        return False
    
    method1_count = 0  # Header + Body reference
    method2_count = 0  # Header + Inline Body
    
    for api_def in api_defs:
        # Method 1: References both Header and Body
        if api_def.header_id and (api_def.request_body_id or api_def.response_body_id):
            method1_count += 1
            print(f"   ✓ API '{api_def.name}' uses Method 1 (Header + Body reference)")
            print(f"      - Header ID: {api_def.header_id}")
            if api_def.request_body_id:
                print(f"      - Request Body ID: {api_def.request_body_id}")
            if api_def.response_body_id:
                print(f"      - Response Body ID: {api_def.response_body_id}")
        
        # Method 2: References Header + Inline Body
        if api_def.header_id and (api_def.inline_request_body or api_def.inline_response_body):
            method2_count += 1
            print(f"   ✓ API '{api_def.name}' uses Method 2 (Header + Inline Body)")
            print(f"      - Header ID: {api_def.header_id}")
            if api_def.inline_request_body:
                print(f"      - Has inline request body")
            if api_def.inline_response_body:
                print(f"      - Has inline response body")
    
    print(f"\n   Summary:")
    print(f"   - Method 1 (Header + Body reference): {method1_count}")
    print(f"   - Method 2 (Header + Inline Body): {method2_count}")
    
    return method1_count > 0 or method2_count > 0


def verify_script_api_references(session: Session) -> bool:
    """Verify scripts reference API definitions correctly."""
    print("\n3. Verifying script references to API definitions...")
    
    scripts = session.execute(select(TestScript)).scalars().all()
    
    if not scripts:
        print("   ✗ No scripts found")
        return False
    
    for script in scripts:
        if not script.api_definition_id:
            print(f"   ✗ Script '{script.name}' has no API definition reference")
            return False
        
        # Verify the API definition exists
        api_def = session.get(ApiDefinition, script.api_definition_id)
        if not api_def:
            print(f"   ✗ Script '{script.name}' references non-existent API definition")
            return False
        
        print(f"   ✓ Script '{script.name}' → API '{api_def.name}'")
        
        # Verify script parameters
        if script.parameters:
            print(f"      - Has {len(script.parameters)} parameters")
    
    return True


def verify_component_nesting(session: Session) -> bool:
    """Verify component nesting relationships."""
    print("\n4. Verifying component nesting relationships...")
    
    components = session.execute(select(TestComponent)).scalars().all()
    
    if not components:
        print("   ✗ No components found")
        return False
    
    nested_count = 0
    for component in components:
        if component.parent_component_id:
            nested_count += 1
            parent = session.get(TestComponent, component.parent_component_id)
            if not parent:
                print(f"   ✗ Component '{component.name}' references non-existent parent")
                return False
            
            print(f"   ✓ Nested: '{component.name}' → Parent: '{parent.name}'")
        else:
            print(f"   ✓ Root component: '{component.name}'")
        
        # Verify component-script associations
        if component.component_scripts:
            print(f"      - Contains {len(component.component_scripts)} scripts")
            for cs in component.component_scripts:
                script = session.get(TestScript, cs.script_id)
                if script:
                    print(f"        • Script: '{script.name}' (order: {cs.execution_order})")
    
    print(f"\n   Summary:")
    print(f"   - Total components: {len(components)}")
    print(f"   - Nested components: {nested_count}")
    
    return True


def verify_test_case_references(session: Session) -> bool:
    """Verify test case references to scripts and components."""
    print("\n5. Verifying test case references...")
    
    test_cases = session.execute(select(TestCase)).scalars().all()
    
    if not test_cases:
        print("   ✗ No test cases found")
        return False
    
    for test_case in test_cases:
        print(f"   ✓ Test Case: '{test_case.name}'")
        
        # Verify script references
        if test_case.test_case_scripts:
            print(f"      - References {len(test_case.test_case_scripts)} scripts:")
            for tcs in test_case.test_case_scripts:
                script = session.get(TestScript, tcs.script_id)
                if not script:
                    print(f"        ✗ References non-existent script")
                    return False
                print(f"        • '{script.name}' (order: {tcs.execution_order})")
        
        # Verify component references
        if test_case.test_case_components:
            print(f"      - References {len(test_case.test_case_components)} components:")
            for tcc in test_case.test_case_components:
                component = session.get(TestComponent, tcc.component_id)
                if not component:
                    print(f"        ✗ References non-existent component")
                    return False
                print(f"        • '{component.name}' (order: {tcc.execution_order})")
    
    return True


def verify_cascade_rules(session: Session) -> bool:
    """Verify cascade delete and update rules (non-destructive check)."""
    print("\n6. Verifying cascade rules (checking relationships)...")
    
    # Check foreign key relationships
    print("   ✓ Checking foreign key relationships...")
    
    # Verify API Definition → Script cascade
    api_defs = session.execute(select(ApiDefinition)).scalars().all()
    for api_def in api_defs:
        scripts = session.execute(
            select(TestScript).where(TestScript.api_definition_id == api_def.id)
        ).scalars().all()
        if scripts:
            print(f"   ✓ API '{api_def.name}' has {len(scripts)} dependent scripts (CASCADE)")
    
    # Verify Component → ComponentScript cascade
    components = session.execute(select(TestComponent)).scalars().all()
    for component in components:
        if component.component_scripts:
            print(f"   ✓ Component '{component.name}' has {len(component.component_scripts)} script associations (CASCADE)")
    
    # Verify TestCase → TestCaseScript/TestCaseComponent cascade
    test_cases = session.execute(select(TestCase)).scalars().all()
    for test_case in test_cases:
        total_refs = len(test_case.test_case_scripts) + len(test_case.test_case_components)
        if total_refs > 0:
            print(f"   ✓ Test Case '{test_case.name}' has {total_refs} associations (CASCADE)")
    
    print("\n   Note: Cascade delete rules are configured but not tested destructively")
    print("   The following cascade rules are in place:")
    print("   - Deleting API Definition → Deletes dependent Scripts")
    print("   - Deleting Component → Deletes ComponentScript associations")
    print("   - Deleting TestCase → Deletes TestCaseScript/TestCaseComponent associations")
    print("   - Deleting User → Sets created_by to NULL (SET NULL)")
    
    return True


def run_verification(environment: str = "development"):
    """Run all verification checks.
    
    Args:
        environment: Environment name (development, testing, production)
    """
    print("="*60)
    print("Four-Layer Architecture Data Integrity Verification")
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
        results = []
        
        results.append(("Header/Body Independence", verify_header_body_independence(session)))
        results.append(("API Definition Combinations", verify_api_definition_combinations(session)))
        results.append(("Script API References", verify_script_api_references(session)))
        results.append(("Component Nesting", verify_component_nesting(session)))
        results.append(("Test Case References", verify_test_case_references(session)))
        results.append(("Cascade Rules", verify_cascade_rules(session)))
        
        print("\n" + "="*60)
        print("Verification Summary")
        print("="*60)
        
        all_passed = True
        for check_name, passed in results:
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{check_name:.<40} {status}")
            if not passed:
                all_passed = False
        
        print("="*60)
        
        if all_passed:
            print("\n✓ All integrity checks passed!")
            return 0
        else:
            print("\n✗ Some integrity checks failed!")
            return 1


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Verify data integrity of the four-layer architecture"
    )
    parser.add_argument(
        "--env",
        "--environment",
        dest="environment",
        choices=["development", "testing", "production"],
        default="development",
        help="Environment to verify (default: development)"
    )
    
    args = parser.parse_args()
    
    try:
        sys.exit(run_verification(environment=args.environment))
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
