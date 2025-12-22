"""Test relationships between API component models and other models."""

import sys

sys.path.insert(0, 'src')

from morado.common.utils.uuid import generate_uuid
from morado.models import ApiDefinition, Body, Header


def test_relationships():
    """Test that relationships are properly defined."""
    print("Testing model relationships...")

    # Test Header relationships
    h = Header(uuid=generate_uuid(), name='Test Header', headers={})
    assert hasattr(h, 'api_definitions'), "Header should have api_definitions relationship"
    assert hasattr(h, 'creator'), "Header should have creator relationship"
    print("✓ Header relationships verified")

    # Test Body relationships
    b = Body(uuid=generate_uuid(), name='Test Body', body_type='request')
    assert hasattr(b, 'api_definitions_request'), "Body should have api_definitions_request relationship"
    assert hasattr(b, 'api_definitions_response'), "Body should have api_definitions_response relationship"
    assert hasattr(b, 'creator'), "Body should have creator relationship"
    print("✓ Body relationships verified")

    # Test ApiDefinition relationships
    api = ApiDefinition(uuid=generate_uuid(), name='Test API', method='GET', path='/test')
    assert hasattr(api, 'header'), "ApiDefinition should have header relationship"
    assert hasattr(api, 'request_body'), "ApiDefinition should have request_body relationship"
    assert hasattr(api, 'response_body'), "ApiDefinition should have response_body relationship"
    assert hasattr(api, 'scripts'), "ApiDefinition should have scripts relationship"
    assert hasattr(api, 'creator'), "ApiDefinition should have creator relationship"
    print("✓ ApiDefinition relationships verified")

    print("\n✓ All relationships verified successfully!")


if __name__ == "__main__":
    test_relationships()
