# Implementation Plan

- [x] 1. Refactor UUID Generator module





- [x] 1.1 Create UUIDConfig dataclass with validation


  - Implement dataclass with all configuration fields
  - Add to_dict() and from_dict() methods
  - Add validation for format, charset, and length
  - _Requirements: 3.1, 3.2, 8.1_

- [x] 1.2 Refactor UUIDGenerator class to be stateless

  - Remove any instance state
  - Make all methods static
  - Ensure no dependencies on logger module
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 1.3 Add UUID4 format support

  - Implement standard RFC 4122 UUID4 generation
  - Add uuid4() static method
  - _Requirements: 12.1_

- [x] 1.4 Add ULID-like format support

  - Implement timestamp-based sortable ID generation
  - Add ulid() static method
  - Ensure monotonic ordering within milliseconds
  - _Requirements: 12.2, 12.5_

- [ ]* 1.5 Write property test for UUID4 RFC compliance
  - **Property 15: UUID4 RFC compliance**
  - **Validates: Requirements 12.1**

- [ ]* 1.6 Write property test for ULID temporal ordering
  - **Property 16: ULID temporal ordering**
  - **Validates: Requirements 12.2**

- [ ]* 1.7 Write property test for timestamp-based ID monotonicity
  - **Property 17: Timestamp-based ID monotonicity**
  - **Validates: Requirements 12.5**

- [ ]* 1.8 Write unit tests for UUID generator
  - Test each format (alphanumeric, numeric, UUID4, ULID)
  - Test prefix/suffix application
  - Test length constraints
  - Test charset validation
  - _Requirements: 3.1, 3.2, 12.1, 12.2_

- [x] 2. Create Configuration Manager module





- [x] 2.1 Create configuration dataclasses


  - Implement LoggerConfig dataclass
  - Implement ProcessorConfig dataclass
  - Add to_dict(), from_dict(), and merge() methods
  - _Requirements: 1.1, 1.2, 2.5_

- [x] 2.2 Implement ConfigurationManager class

  - Implement load_from_file() for TOML/YAML
  - Implement load_from_env() for environment variables
  - Implement merge_configs() with precedence rules
  - Implement get_default_config()
  - _Requirements: 1.1, 1.2, 2.5_

- [x] 2.3 Add configuration file search logic

  - Search in order: env var, ./logging.toml, ./config/logging.toml, ~/.morado/logging.toml
  - Handle missing files gracefully
  - _Requirements: 1.1, 1.2, 9.5_

- [x] 2.4 Add configuration validation

  - Validate log levels
  - Validate output formats
  - Validate module patterns
  - Log warnings for invalid values, use defaults
  - _Requirements: 1.3, 1.4, 9.2_

- [ ]* 2.5 Write property test for configuration precedence
  - **Property 4: Programmatic configuration precedence**
  - **Validates: Requirements 2.2, 2.5**

- [ ]* 2.6 Write unit tests for configuration manager
  - Test TOML file loading
  - Test environment variable loading
  - Test configuration merging
  - Test default fallback
  - Test malformed file handling
  - _Requirements: 1.1, 1.2, 2.5, 9.2, 9.5_


- [x] 3. Create Context Manager module






- [x] 3.1 Implement context variables

  - Define _request_id_var, _user_id_var, _trace_id_var using contextvars
  - Ensure thread-safe and async-safe
  - _Requirements: 6.1, 6.2, 6.3, 10.5_



- [x] 3.2 Implement ContextManager class

  - Implement get/set methods for each context variable
  - Implement get_all_context() method
  - Implement clear_context() method
  - _Requirements: 6.1, 6.2, 6.3_




- [x] 3.3 Implement RequestContext dataclass

  - Create dataclass with request_id, user_id, trace_id, additional fields
  - Add to_dict() method for logging
  - _Requirements: 6.1, 6.2, 6.3_





- [x] 3.4 Implement request_scope context manager

  - Handle context variable setting and restoration
  - Auto-generate request_id if not provided
  - Support additional context fields

  - _Requirements: 6.1, 6.4, 7.1_

- [x] 3.5 Implement async_request_scope context manager

  - Async version of request_scope
  - Ensure proper async context isolation
  - _Requirements: 10.1, 10.2, 10.3_

- [ ]* 3.6 Write property test for context propagation
  - **Property 8: Context propagation**
  - **Validates: Requirements 6.1**

- [ ]* 3.7 Write property test for context restoration
  - **Property 9: Context restoration round-trip**
  - **Validates: Requirements 6.4**

- [ ]* 3.8 Write property test for async context isolation
  - **Property 13: Async context isolation**
  - **Validates: Requirements 10.2**

- [ ]* 3.9 Write unit tests for context manager
  - Test context get/set operations
  - Test context scope entry/exit
  - Test context restoration
  - Test async context isolation
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 10.1, 10.2_

- [ ] 4. Create Logger System module
- [ ] 4.1 Implement LoggerSystem class (singleton)
  - Implement singleton pattern with __new__
  - Add _instance, _configured, _config attributes
  - _Requirements: 1.1, 2.1_

- [ ] 4.2 Implement configure() method
  - Accept LoggerConfig, config_file path, and overrides
  - Load and merge configurations with precedence
  - Initialize structlog with configuration
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.5_

- [ ] 4.3 Implement _build_processor_chain() method
  - Build processor list from configuration
  - Include built-in processors (timestamp, level, etc.)
  - Add custom processors from config
  - Wrap with error handling
  - _Requirements: 1.5, 4.1, 4.2, 4.3, 4.4, 9.1_

- [ ] 4.4 Implement _get_renderer() method
  - Select renderer based on configuration format
  - Support console, JSON, structured formats
  - Wrap with error handling and fallback
  - _Requirements: 1.4, 5.1, 5.2, 5.4, 9.3_

- [ ] 4.5 Implement _inject_context_vars() processor
  - Extract context variables from ContextManager
  - Add to event_dict only if set (not None)
  - Handle errors gracefully
  - _Requirements: 6.1, 6.2, 6.3, 6.5, 9.4_

- [ ] 4.6 Implement get_logger() method
  - Create and return structlog BoundLogger
  - Apply module-specific log level if configured
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 4.7 Implement add_processor() method
  - Allow runtime addition of custom processors
  - Reconfigure structlog with new processor chain
  - _Requirements: 2.3, 4.1, 4.2_

- [ ] 4.8 Implement set_level() method
  - Set global or module-specific log level
  - Support pattern matching for modules
  - _Requirements: 2.2, 11.1, 11.4, 11.5_

- [ ]* 4.9 Write property test for configuration application
  - **Property 1: Configuration application consistency**
  - **Validates: Requirements 1.3**

- [ ]* 4.10 Write property test for renderer selection
  - **Property 2: Renderer selection correctness**
  - **Validates: Requirements 1.4**

- [ ]* 4.11 Write property test for processor execution order
  - **Property 3: Processor execution order**
  - **Validates: Requirements 1.5, 4.4**

- [ ]* 4.12 Write property test for custom processor execution
  - **Property 6: Custom processor execution**
  - **Validates: Requirements 4.2**

- [ ]* 4.13 Write property test for JSON output validity
  - **Property 7: JSON output validity**
  - **Validates: Requirements 5.4**

- [ ]* 4.14 Write property test for module-level configuration
  - **Property 14: Module-level log configuration**
  - **Validates: Requirements 11.1**

- [ ]* 4.15 Write unit tests for logger system
  - Test logger initialization
  - Test processor registration
  - Test renderer selection
  - Test module-level log levels
  - Test error handling (processor failures, renderer fallback)
  - _Requirements: 1.1, 1.4, 2.1, 4.2, 9.1, 9.3, 11.1_


- [x] 5. Create Decorators module






- [x] 5.1 Implement with_request_context decorator

  - Extract context from function arguments
  - Create request scope with extracted context
  - Auto-generate request_id if enabled
  - Support both sync and async functions
  - _Requirements: 7.1, 7.3_

- [x] 5.2 Implement async_with_request_context decorator

  - Async-specific version of with_request_context
  - Use async_request_scope internally
  - _Requirements: 10.1, 10.4_

- [x] 5.3 Implement log_execution decorator

  - Log function entry and exit
  - Optionally log arguments and return values
  - Handle exceptions and log them
  - _Requirements: General logging utility_

- [ ]* 5.4 Write unit tests for decorators
  - Test with_request_context with various argument patterns
  - Test async_with_request_context
  - Test log_execution
  - Test auto-generation of request_id
  - _Requirements: 7.1, 7.3, 10.1, 10.4_

- [x] 6. Integrate UUID Generator with Logger System




- [x] 6.1 Update request_scope to use UUID Generator


  - Import UUIDGenerator in context module
  - Use configured UUID format for auto-generation
  - Pass UUIDConfig from LoggerConfig
  - _Requirements: 7.1, 7.2, 8.2, 8.3_

- [x] 6.2 Update LoggerConfig to include request_id_config


  - Add request_id_config field of type UUIDConfig
  - Ensure proper serialization/deserialization
  - _Requirements: 7.2, 8.2, 8.4_

- [ ]* 6.3 Write property test for request ID auto-generation uniqueness
  - **Property 10: Request ID auto-generation uniqueness**
  - **Validates: Requirements 7.1**

- [ ]* 6.4 Write property test for request ID format compliance
  - **Property 11: Request ID format compliance**
  - **Validates: Requirements 7.2**

- [ ]* 6.5 Write property test for explicit request ID preservation
  - **Property 12: Explicit request ID preservation**
  - **Validates: Requirements 7.3**

- [ ]* 6.6 Write unit tests for UUID-logger integration
  - Test auto-generation with various UUID configs
  - Test explicit request_id usage
  - Test UUID format application
  - _Requirements: 7.1, 7.2, 7.3, 8.2_

- [x] 7. Create public API and update __init__ files






- [x] 7.1 Update src/morado/common/logger/__init__.py

  - Export get_logger, configure_logger
  - Export request_scope, async_request_scope
  - Export with_request_context, async_with_request_context
  - Export LoggerConfig, UUIDConfig
  - Export ContextManager for advanced usage
  - _Requirements: All_

- [x] 7.2 Update src/morado/common/utils/__init__.py


  - Export UUIDGenerator
  - Export UUIDConfig
  - Export convenience functions (uuid4, ulid, alphanumeric, numeric)
  - _Requirements: 3.1, 3.2_


- [x] 7.3 Add backward compatibility imports

  - Keep old imports working with deprecation warnings
  - Map old LoggerUtil to new LoggerSystem
  - _Requirements: Backward compatibility_

- [ ]* 7.4 Write integration tests
  - Test full workflow: configure -> log -> verify output
  - Test request scope with logging
  - Test async request scope with logging
  - Test configuration file loading end-to-end
  - _Requirements: All_

- [x] 8. Create example configuration file




- [x] 8.1 Create example logging.toml


  - Include all configuration options with comments
  - Provide examples for common scenarios
  - Document environment variable overrides
  - Place in docs/ directory
  - _Requirements: 1.1, 1.5, 2.5_

- [x] 9. Update documentation



- [x] 9.1 Create migration guide


  - Document import changes
  - Document API changes
  - Provide before/after code examples
  - _Requirements: Backward compatibility_



- [x] 9.2 Create configuration reference
  - Document all configuration options
  - Document environment variables
  - Document precedence rules
  - _Requirements: 1.1, 2.5_


- [x] 9.3 Create usage examples


  - Basic logging example
  - Request scope example
  - Async logging example
  - Custom processor example
  - Custom renderer example
  - _Requirements: All_

- [x] 10. Fix existing code and remove old implementation




- [x] 10.1 Fix import error in old log.py


  - Update import from utils.uuid_generator to morado.common.utils.uuid
  - Ensure old code still works during transition
  - _Requirements: Bug fix_


- [x] 10.2 Update main.py and other usage sites

  - Update imports to use new API
  - Test that application still works
  - _Requirements: Integration_

- [x] 10.3 Remove old log.py after migration


  - Ensure all code migrated to new API
  - Remove src/morado/common/logger/log.py
  - _Requirements: Cleanup_

- [x] 11. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
