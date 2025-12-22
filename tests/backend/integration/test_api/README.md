# API Integration Tests

This directory contains comprehensive integration tests for the Morado four-layer architecture API.

## Test Files

### test_header_api.py
Tests for Header management endpoints (Layer 1):
- Create, read, update, delete operations
- List and search functionality
- Filtering by scope and project
- Activation/deactivation
- Header reusability across API definitions

### test_body_api.py
Tests for Body management endpoints (Layer 1):
- Create, read, update, delete operations
- List and search functionality
- Filtering by body type and scope
- Body reusability across API definitions

### test_api_definition.py
Tests for API Definition endpoints (Layer 1):
- Reference mode (using header_id and body_id)
- Inline mode (using inline bodies)
- Full API definition retrieval with all components
- Filtering and searching
- Both combination modes

### test_four_layer_integration.py
Comprehensive integration tests covering all four layers:
- Complete workflow from Layer 1 to Layer 4
- Component nesting functionality
- Test cases with scripts and components
- Parameter override chain
- Header and body reuse across layers
- Error handling for missing references
- Cascade operations

### test_error_responses.py
Tests for API error handling:
- 404 Not Found responses
- Validation errors
- Missing required fields
- Invalid JSON format
- Invalid query parameters
- Consistent error response format

## Known Issues

### 1. Reserved Keyword Conflict
The API uses `scope` as a query parameter name, which conflicts with Litestar's reserved keywords. This causes the following error:

```
ImproperlyConfiguredException: Reserved kwargs (scope, request, socket, body, cookies, query, state, headers, data) cannot be used for dependencies and parameter arguments.
```

**Resolution needed**: Rename the `scope` parameter to something like `header_scope` or `component_scope` in:
- `backend/src/morado/api/v1/header.py`
- `backend/src/morado/api/v1/body.py`
- `backend/src/morado/models/api_component.py` (HeaderScope enum)

### 2. Schema Mismatch
The `PaginatedResponse` schema expects `page`, `page_size`, and `total_pages`, but the API endpoints use `skip` and `limit`. This causes type checking errors.

**Resolution needed**: Either:
- Update all ListResponse schemas to use skip/limit instead of page/page_size
- Update all API endpoints to use page/page_size instead of skip/limit
- Create a separate OffsetPaginatedResponse schema for skip/limit pagination

## Running the Tests

Once the above issues are resolved, run the tests with:

```bash
# Set PYTHONPATH
$env:PYTHONPATH="backend/src"

# Run all integration tests
uv run pytest tests/backend/integration/test_api/ -v

# Run specific test file
uv run pytest tests/backend/integration/test_api/test_header_api.py -v

# Run specific test
uv run pytest tests/backend/integration/test_api/test_header_api.py::TestHeaderAPI::test_create_header -v
```

## Test Coverage

The integration tests cover:
- ✅ Four-layer architecture (Header/Body/API Definition, Scripts, Components, Test Cases)
- ✅ CRUD operations for all entities
- ✅ Header and Body reusability
- ✅ API Definition two combination modes (reference and inline)
- ✅ Script creation and execution
- ✅ Component nesting
- ✅ Test case with scripts and components
- ✅ Parameter override chain
- ✅ Error response formats
- ✅ Validation errors
- ✅ 404 Not Found errors
- ✅ Cascade operations

## Next Steps

1. Fix the reserved keyword conflict by renaming `scope` parameter
2. Resolve the schema mismatch for pagination
3. Run the full test suite to verify all tests pass
4. Add authentication/authorization tests once auth is implemented
5. Add performance tests for large datasets
