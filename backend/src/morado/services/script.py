"""Service layer for Layer 2: Test Script management.

This module provides business logic for managing test scripts and their execution.
"""

from typing import Any

from sqlalchemy.orm import Session

from morado.models.script import ScriptParameter, ScriptType, TestScript
from morado.repositories.script import ScriptParameterRepository, TestScriptRepository


class TestScriptService:
    """Service for managing test scripts.

    Provides business logic for creating, updating, executing, and debugging scripts.

    Example:
        >>> service = TestScriptService()
        >>> script = service.create_script(
        ...     session,
        ...     name="Login Test",
        ...     api_definition_id=1,
        ...     script_type=ScriptType.MAIN
        ... )
    """

    def __init__(self):
        """Initialize TestScript service."""
        self.repository = TestScriptRepository()
        self.parameter_repository = ScriptParameterRepository()

    def create_script(  # noqa: PLR0913
        self,
        session: Session,
        name: str,
        api_definition_id: int,
        description: str | None = None,
        script_type: ScriptType = ScriptType.MAIN,
        execution_order: int = 0,
        variables: dict | None = None,
        assertions: list | None = None,
        validators: dict | None = None,
        pre_script: str | None = None,
        post_script: str | None = None,
        extract_variables: dict | None = None,
        output_variables: list | None = None,
        debug_mode: bool = False,
        retry_count: int = 0,
        retry_interval: float = 1.0,
        timeout_override: int | None = None,
        tags: list[str] | None = None,
        created_by: int | None = None,
        **kwargs: Any
    ) -> TestScript:
        """Create a new test script.

        Args:
            session: Database session
            name: Script name
            api_definition_id: API definition ID
            description: Script description
            script_type: Script type (setup/main/teardown/utility)
            execution_order: Execution order
            variables: Script-level variables
            assertions: Assertion list
            validators: Validator configuration
            pre_script: Pre-execution script code
            post_script: Post-execution script code
            extract_variables: Variable extraction configuration
            output_variables: Output variable list
            debug_mode: Enable debug mode
            retry_count: Number of retries
            retry_interval: Retry interval in seconds
            timeout_override: Timeout override in seconds
            tags: Tags for categorization
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created TestScript instance
        """
        script = self.repository.create(
            session,
            name=name,
            description=description,
            api_definition_id=api_definition_id,
            script_type=script_type,
            execution_order=execution_order,
            variables=variables,
            assertions=assertions,
            validators=validators,
            pre_script=pre_script,
            post_script=post_script,
            extract_variables=extract_variables,
            output_variables=output_variables,
            debug_mode=debug_mode,
            retry_count=retry_count,
            retry_interval=retry_interval,
            timeout_override=timeout_override,
            tags=tags,
            created_by=created_by,
            **kwargs
        )

        session.commit()
        return script

    def get_script(
        self,
        session: Session,
        script_id: int,
        with_relations: bool = False
    ) -> TestScript | None:
        """Get script by ID.

        Args:
            session: Database session
            script_id: Script ID
            with_relations: Whether to load related API definition and parameters

        Returns:
            TestScript instance or None if not found
        """
        if with_relations:
            return self.repository.get_with_relations(session, script_id)
        else:
            return self.repository.get_by_id(session, script_id)

    def get_script_by_uuid(self, session: Session, uuid: str) -> TestScript | None:
        """Get script by UUID.

        Args:
            session: Database session
            uuid: Script UUID

        Returns:
            TestScript instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_scripts(
        self,
        session: Session,
        api_definition_id: int | None = None,
        script_type: ScriptType | None = None,
        tags: list[str] | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestScript]:
        """List scripts with optional filtering.

        Args:
            session: Database session
            api_definition_id: Filter by API definition ID
            script_type: Filter by script type
            tags: Filter by tags
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances
        """
        if api_definition_id:
            return self.repository.get_by_api_definition(
                session, api_definition_id, skip, limit
            )
        elif script_type:
            return self.repository.get_by_type(session, script_type, skip, limit)
        elif tags:
            return self.repository.get_by_tags(session, tags, skip, limit)
        else:
            return self.repository.get_all(session, skip, limit)

    def search_scripts(
        self,
        session: Session,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestScript]:
        """Search scripts by name.

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances
        """
        return self.repository.search_by_name(session, name, skip, limit)

    def update_script(
        self,
        session: Session,
        script_id: int,
        **kwargs: Any
    ) -> TestScript | None:
        """Update script.

        Args:
            session: Database session
            script_id: Script ID
            **kwargs: Fields to update

        Returns:
            Updated TestScript instance or None if not found
        """
        script = self.repository.get_by_id(session, script_id)
        if not script:
            return None

        updated_script = self.repository.update(session, script, **kwargs)
        session.commit()
        return updated_script

    def delete_script(self, session: Session, script_id: int) -> bool:
        """Delete script.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete_by_id(session, script_id)
        if result:
            session.commit()
        return result

    def add_parameter(  # noqa: PLR0913
        self,
        session: Session,
        script_id: int,
        name: str,
        parameter_type: str,
        description: str | None = None,
        default_value: str | None = None,
        is_required: bool = False,
        validation_rules: dict | None = None,
        order: int = 0,
        group: str | None = None,
        is_sensitive: bool = False
    ) -> ScriptParameter:
        """Add parameter to script.

        Args:
            session: Database session
            script_id: Script ID
            name: Parameter name
            parameter_type: Parameter type
            description: Parameter description
            default_value: Default value
            is_required: Whether parameter is required
            validation_rules: Validation rules
            order: Display order
            group: Parameter group
            is_sensitive: Whether parameter is sensitive

        Returns:
            Created ScriptParameter instance
        """
        parameter = self.parameter_repository.create(
            session,
            script_id=script_id,
            name=name,
            description=description,
            parameter_type=parameter_type,
            default_value=default_value,
            is_required=is_required,
            validation_rules=validation_rules,
            order=order,
            group=group,
            is_sensitive=is_sensitive
        )

        session.commit()
        return parameter

    def get_script_parameters(
        self,
        session: Session,
        script_id: int,
        required_only: bool = False
    ) -> list[ScriptParameter]:
        """Get script parameters.

        Args:
            session: Database session
            script_id: Script ID
            required_only: Whether to return only required parameters

        Returns:
            List of ScriptParameter instances
        """
        if required_only:
            return self.parameter_repository.get_required_parameters(session, script_id)
        else:
            return self.parameter_repository.get_by_script(session, script_id)

    def update_parameter(
        self,
        session: Session,
        parameter_id: int,
        **kwargs: Any
    ) -> ScriptParameter | None:
        """Update script parameter.

        Args:
            session: Database session
            parameter_id: Parameter ID
            **kwargs: Fields to update

        Returns:
            Updated ScriptParameter instance or None if not found
        """
        parameter = self.parameter_repository.get_by_id(session, parameter_id)
        if not parameter:
            return None

        updated_parameter = self.parameter_repository.update(session, parameter, **kwargs)
        session.commit()
        return updated_parameter

    def delete_parameter(self, session: Session, parameter_id: int) -> bool:
        """Delete script parameter.

        Args:
            session: Database session
            parameter_id: Parameter ID

        Returns:
            True if deleted, False if not found
        """
        result = self.parameter_repository.delete_by_id(session, parameter_id)
        if result:
            session.commit()
        return result

    def enable_debug_mode(self, session: Session, script_id: int) -> TestScript | None:
        """Enable debug mode for script.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            Updated TestScript instance or None if not found
        """
        return self.update_script(session, script_id, debug_mode=True)

    def disable_debug_mode(self, session: Session, script_id: int) -> TestScript | None:
        """Disable debug mode for script.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            Updated TestScript instance or None if not found
        """
        return self.update_script(session, script_id, debug_mode=False)

    def validate_script_parameters(
        self,
        session: Session,
        script_id: int,
        parameters: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate script parameters.

        Args:
            session: Database session
            script_id: Script ID
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        script_params = self.get_script_parameters(session, script_id)
        errors = []

        # Check required parameters
        required_params = {p.name for p in script_params if p.is_required}
        missing_params = required_params - set(parameters.keys())
        if missing_params:
            errors.append(f"Missing required parameters: {', '.join(missing_params)}")

        # Validate parameter types and rules
        for param in script_params:
            if param.name in parameters:
                # Type validation would go here
                # Validation rules would be applied here
                pass

        return len(errors) == 0, errors

    def get_script_execution_config(
        self,
        session: Session,
        script_id: int
    ) -> dict[str, Any] | None:
        """Get complete script execution configuration.

        This method returns all information needed to execute a script,
        including API definition, parameters, assertions, etc.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            Dictionary with complete execution configuration or None if not found
        """
        script = self.repository.get_with_relations(session, script_id)
        if not script:
            return None

        return {
            'script': {
                'id': script.id,
                'uuid': script.uuid,
                'name': script.name,
                'description': script.description,
                'script_type': script.script_type,
                'execution_order': script.execution_order,
                'variables': script.variables,
                'assertions': script.assertions,
                'validators': script.validators,
                'pre_script': script.pre_script,
                'post_script': script.post_script,
                'extract_variables': script.extract_variables,
                'output_variables': script.output_variables,
                'debug_mode': script.debug_mode,
                'retry_count': script.retry_count,
                'retry_interval': script.retry_interval,
                'timeout_override': script.timeout_override
            },
            'api_definition': {
                'id': script.api_definition.id,
                'name': script.api_definition.name,
                'method': script.api_definition.method,
                'path': script.api_definition.path,
                'base_url': script.api_definition.base_url,
                'timeout': script.api_definition.timeout
            },
            'parameters': [
                {
                    'name': p.name,
                    'type': p.parameter_type,
                    'default_value': p.default_value,
                    'is_required': p.is_required,
                    'validation_rules': p.validation_rules,
                    'is_sensitive': p.is_sensitive
                }
                for p in script.parameters
            ]
        }
