"""Updated unit tests for FLEXT application handlers using new FlextCqrs API.

Tests for advanced CQRS handler patterns with Python 3.13 + Pydantic integration
following FLEXT unified class patterns and the optimized FlextCqrs architecture.
"""

from dataclasses import dataclass

import pytest

from flext_core import (
    FlextConstants,
    FlextCqrs,
    FlextResult,
)


class TestFlextAdvancedHandlerModelsUpdated:
    """Test suite for advanced handler models using new FlextCqrs API."""

    def test_handler_context_creation_with_new_api(self) -> None:
        """Test creating handler context with new FlextCqrs API."""
        # Use new FlextCqrs.Operations to create handler config
        config_result: FlextResult[object] = FlextCqrs.Operations.create_handler_config(
            "command", handler_name="ContextHandler", handler_id="test_handler_123"
        )

        assert config_result.is_success
        handler_config: object = config_result.value
        # Type assertion for handler config attributes
        assert hasattr(handler_config, "handler_id")
        assert hasattr(handler_config, "handler_name")
        assert hasattr(handler_config, "handler_type")
        assert getattr(handler_config, "handler_id") == "test_handler_123"
        assert getattr(handler_config, "handler_name") == "ContextHandler"
        assert getattr(handler_config, "handler_type") == "command"

    def test_data_processing_command_with_new_api(self) -> None:
        """Test Command using new FlextCqrs command creation with actual API."""
        command_data: dict[str, object] = {
            "command_type": "ProcessData",
            "issuer_id": "test_user_123",
        }

        result: FlextResult[object] = FlextCqrs.Operations.create_command(command_data)

        assert result.is_success
        command: object = result.value
        # Type assertion for command attributes using actual Command model fields
        assert hasattr(command, "command_type")
        assert hasattr(command, "command_id")
        assert hasattr(command, "issued_at")
        assert hasattr(command, "issuer_id")
        assert getattr(command, "command_type") == "ProcessData"
        assert getattr(command, "issuer_id") == "test_user_123"
        # Command ID should be auto-generated
        assert getattr(command, "command_id") is not None
        assert len(str(getattr(command, "command_id"))) > 0

    def test_data_processing_command_validation_error(self) -> None:
        """Test data processing command validation with new API."""
        # Create invalid command data (missing required fields)
        invalid_command_data: dict[str, object] = {
            "payload": {
                "operation": "process_data",
                "data_source": "invalid_uri",  # Invalid URI
                "batch_size": 1000,
            }
            # Missing command_type
        }

        result: FlextResult[object] = FlextCqrs.Operations.create_command(
            invalid_command_data
        )

        assert result.is_failure
        assert result.error is not None
        assert "Command validation failed" in result.error
        assert result.error_code == FlextConstants.Cqrs.COMMAND_VALIDATION_FAILED

    def test_data_processing_command_business_rules_validation(self) -> None:
        """Test business rule validation using FlextCqrs Results."""
        # Simulate business rule validation
        command_data: dict[str, object] = {
            "command_type": "ProcessDataLargeBatch",
            "payload": {
                "operation": "process_data",
                "data_source": "file:///test/data.csv",
                "batch_size": 60000,  # Large batch requiring validation
            },
            "priority": "high",
        }

        # Create command successfully
        command_result: FlextResult[object] = FlextCqrs.Operations.create_command(
            command_data
        )
        assert command_result.is_success

        # Simulate business rule validation failure using FlextCqrs.Results
        validation_result: FlextResult[object] = FlextCqrs.Results.failure(
            "Large batch sizes require additional validation",
            error_code="BUSINESS_RULE_VIOLATION",
            error_data={
                "batch_size": 60000,
                "max_allowed": 50000,
                "requires_approval": True,
            },
        )

        assert validation_result.is_failure
        assert validation_result.error is not None
        assert (
            "Large batch sizes require additional validation" in validation_result.error
        )
        assert validation_result.error_code == "BUSINESS_RULE_VIOLATION"
        assert validation_result.error_data is not None
        assert validation_result.error_data["batch_size"] == 60000

    def test_user_management_command_with_new_api(self) -> None:
        """Test UserManagementCommand using new FlextCqrs patterns."""
        command_data: dict[str, object] = {
            "command_type": "ManageUser",
            "payload": {
                "action": "create",
                "user_data": {"name": "Test User", "role": "user"},
                "user_email": "user@example.com",
            },
            "priority": "normal",
        }

        result: FlextResult[object] = FlextCqrs.Operations.create_command(command_data)

        assert result.is_success
        command: object = result.value
        assert hasattr(command, "command_type")
        assert hasattr(command, "payload")
        assert getattr(command, "command_type") == "ManageUser"
        payload: dict[str, object] = getattr(command, "payload")
        assert payload["action"] == "create"
        assert payload["user_email"] == "user@example.com"

    def test_user_management_command_email_validation(self) -> None:
        """Test email validation in user management using FlextCqrs error handling."""
        # Simulate email validation failure
        invalid_email_result: FlextResult[object] = FlextCqrs.Results.failure(
            "Invalid email format",
            error_code=FlextConstants.Errors.VALIDATION_ERROR,
            error_data={
                "field": "user_email",
                "value": "invalid_email",
                "expected_format": "valid email address",
            },
        )

        assert invalid_email_result.is_failure
        assert invalid_email_result.error is not None
        assert "Invalid email format" in invalid_email_result.error
        assert invalid_email_result.error_code == FlextConstants.Errors.VALIDATION_ERROR
        assert invalid_email_result.error_data is not None
        assert invalid_email_result.error_data["field"] == "user_email"

    def test_user_management_command_REDACTED_LDAP_BIND_PASSWORD_protection(self) -> None:
        """Test REDACTED_LDAP_BIND_PASSWORD deletion protection using FlextCqrs business rules."""
        # Create command that would delete REDACTED_LDAP_BIND_PASSWORD
        REDACTED_LDAP_BIND_PASSWORD_delete_data: dict[str, object] = {
            "command_type": "ManageUser",
            "payload": {"action": "delete", "user_email": "REDACTED_LDAP_BIND_PASSWORD@REDACTED_LDAP_BIND_PASSWORD.com"},
            "priority": "critical",
        }

        command_result: FlextResult[object] = FlextCqrs.Operations.create_command(
            REDACTED_LDAP_BIND_PASSWORD_delete_data
        )
        assert command_result.is_success

        # Simulate business rule protection for REDACTED_LDAP_BIND_PASSWORD deletion
        protection_result: FlextResult[object] = FlextCqrs.Results.failure(
            "Cannot delete REDACTED_LDAP_BIND_PASSWORD user",
            error_code="ADMIN_PROTECTION_VIOLATION",
            error_data={
                "user_email": "REDACTED_LDAP_BIND_PASSWORD@REDACTED_LDAP_BIND_PASSWORD.com",
                "action": "delete",
                "protection_level": "system_REDACTED_LDAP_BIND_PASSWORD",
            },
        )

        assert protection_result.is_failure
        assert protection_result.error is not None
        assert "Cannot delete REDACTED_LDAP_BIND_PASSWORD user" in protection_result.error
        assert protection_result.error_code == "ADMIN_PROTECTION_VIOLATION"


class TestFlextAdvancedHandlerServiceUpdated:
    """Test suite for advanced handler service using new FlextCqrs decorators."""

    @dataclass
    class DataProcessingCommand:
        """Test command for decorator testing."""

        operation: str
        data_source: str
        batch_size: int

    @dataclass
    class UserManagementCommand:
        """Test command for user management."""

        action: str
        user_email: str
        user_data: dict[str, object]

    def test_command_handler_decorator_data_processing(self) -> None:
        """Test FlextCqrs decorator for data processing commands."""

        @FlextCqrs.Decorators.command_handler(self.DataProcessingCommand)
        def process_data_handler(
            command: TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand,
        ) -> dict[str, object]:
            """Handle data processing with new FlextCqrs patterns."""
            # Simulate data processing
            processed_items = min(command.batch_size, 1000)  # Cap processing

            return {
                "operation": command.operation,
                "source": command.data_source,
                "processed_items": processed_items,
                "status": "completed",
            }

        # Test the decorated handler
        test_command: TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand = (
            self.DataProcessingCommand(
                operation="process_data",
                data_source="file:///test/data.csv",
                batch_size=500,
            )
        )

        result: dict[str, object] = process_data_handler(test_command)

        assert result["operation"] == "process_data"
        assert result["processed_items"] == 500
        assert result["status"] == "completed"

        # Verify decorator metadata
        assert hasattr(process_data_handler, "__dict__")
        metadata: dict[str, object] = process_data_handler.__dict__
        assert metadata.get("command_type") == self.DataProcessingCommand
        assert metadata.get("flext_cqrs_decorator") is True

    def test_command_handler_with_error_handling(self) -> None:
        """Test command handler error processing."""

        def user_management_handler(
            command: TestFlextAdvancedHandlerServiceUpdated.UserManagementCommand,
        ) -> dict[str, object]:
            if hasattr(command, "user_id") and command.user_id == "error":
                msg = "Simulated user management error"
                raise ValueError(msg)
            return {
                "user_id": getattr(command, "user_id", "unknown"),
                "action": command.action,
            }

        # Register handler
        self.handler_service.register_command_handler(
            TestFlextAdvancedHandlerServiceUpdated.UserManagementCommand,
            user_management_handler,
        )

        # Test error case
        error_command: TestFlextAdvancedHandlerServiceUpdated.UserManagementCommand = (
            TestFlextAdvancedHandlerServiceUpdated.UserManagementCommand(
                user_id="error", action="create"
            )
        )

        result: FlextResult[object] = self.handler_service.handle_command(error_command)

        assert result.is_failure
        assert result.error is not None
        assert "Simulated user management error" in result.error

        # Test success case
        success_command: TestFlextAdvancedHandlerServiceUpdated.UserManagementCommand = TestFlextAdvancedHandlerServiceUpdated.UserManagementCommand(
            user_id="test123", action="create"
        )

        result = self.handler_service.handle_command(success_command)

        assert result.is_success
        assert result.value is not None
        assert hasattr(result.value, "__getitem__")
        assert result.value["user_id"] == "test123"
        assert result.value["action"] == "create"

    def test_handler_instance_error_processing(self) -> None:
        """Test handler instance error processing scenarios."""

        def data_handler(
            command: TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand,
        ) -> dict[str, object]:
            if (
                hasattr(command, "processor_type")
                and command.processor_type == "error_type"
            ):
                msg = "Handler processing error"
                raise RuntimeError(msg)
            return {
                "data": getattr(command, "data", {}),
                "processor": getattr(command, "processor_type", "unknown"),
                "processed": True,
            }

        # Register handler
        self.handler_service.register_command_handler(
            TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand, data_handler
        )

        # Test error scenario
        error_command: TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand = (
            TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand(
                data={"test": "data"}, processor_type="error_type"
            )
        )

        result: FlextResult[object] = self.handler_service.handle_command(error_command)

        assert result.is_failure
        assert result.error is not None
        assert "Handler processing error" in result.error

        # Test success scenario
        success_command: TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand = TestFlextAdvancedHandlerServiceUpdated.DataProcessingCommand(
            data={"success": "data"}, processor_type="valid_processor"
        )

        result = self.handler_service.handle_command(success_command)

        assert result.is_success
        assert result.value is not None
        assert hasattr(result.value, "__getitem__")
        assert result.value["data"]["success"] == "data"
        assert result.value["processor"] == "valid_processor"
        assert result.value["processed"]

    def test_handler_service_integration(self) -> None:
        """Test integration between handlers and FlextCqrs service patterns."""
        # Create handler configuration
        config_result: FlextResult[object] = FlextCqrs.Operations.create_handler_config(
            "command",
            handler_name="IntegratedDataProcessor",
            config_overrides={"timeout": 30000, "retries": 3},
        )
        assert config_result.is_success
        handler_config: object = config_result.value

        # Create command using the configuration context
        command_data: dict[str, object] = {
            "command_type": "ProcessDataWithConfig",
            "payload": {
                "operation": "batch_process",
                "data_source": "file:///integration_test.csv",
                "batch_size": 1000,
            },
            "priority": "high",
        }

        command_result: FlextResult[object] = FlextCqrs.Operations.create_command(
            command_data, handler_config
        )
        assert command_result.is_success

        # Create success result with handler context
        processing_result: FlextResult[object] = FlextCqrs.Results.success(
            {
                "command_id": getattr(command_result.value, "command_id", "unknown"),
                "processed_items": 1000,
                "processing_time_ms": 1500,
                "status": "completed",
            },
            handler_config,
        )

        assert processing_result.is_success
        assert processing_result.value is not None
        assert hasattr(processing_result.value, "__getitem__")
        assert processing_result.value["processed_items"] == 1000

        # Verify metadata includes handler configuration
        metadata: dict[str, object] = getattr(processing_result, "_metadata", {})
        assert metadata.get("handler_name") == "IntegratedDataProcessor"
        assert metadata.get("handler_type") == "command"


class TestLegacyCompatibilityUpdated:
    """Test legacy compatibility with new FlextCqrs patterns."""

    def test_legacy_handler_migration_pattern(self) -> None:
        """Test migration pattern from legacy handlers to FlextCqrs."""

        # Legacy pattern simulation - what we're migrating FROM
        class LegacyHandler:
            def handle(self, command_data: dict[str, object]) -> dict[str, object]:
                return {"legacy": True, "processed": command_data}

        # New pattern using FlextCqrs - what we're migrating TO
        @dataclass
        class ModernCommand:
            operation: str
            data: dict[str, object]

        @FlextCqrs.Decorators.command_handler(ModernCommand)
        def modern_handler(command: ModernCommand) -> FlextResult[dict[str, object]]:
            """Modern handler using FlextCqrs patterns."""
            return FlextResult[dict[str, object]].ok({
                "modern": True,
                "operation": command.operation,
                "processed_data": command.data,
            })

        # Test migration compatibility
        legacy_data: dict[str, object] = {"operation": "test", "data": {"key": "value"}}
        modern_command: ModernCommand = ModernCommand(
            operation=legacy_data["operation"], data=legacy_data["data"]
        )

        modern_result: FlextResult[dict[str, object]] = modern_handler(modern_command)
        assert modern_result.is_success
        assert modern_result.value is not None
        assert modern_result.value["modern"] is True
        assert modern_result.value["operation"] == "test"

    def test_error_code_migration(self) -> None:
        """Test migration of error codes to FlextConstants."""
        # Old error handling pattern
        legacy_error: dict[str, str] = {
            "error": "INVALID_INPUT",
            "message": "Input validation failed",
        }

        # New error handling using FlextCqrs.Results and FlextConstants
        modern_error: FlextResult[object] = FlextCqrs.Results.failure(
            "Input validation failed",
            error_code=FlextConstants.Errors.VALIDATION_ERROR,
            error_data={
                "legacy_error_code": legacy_error["error"],
                "field": "input_data",
                "validation_type": "format_check",
            },
        )

        assert modern_error.is_failure
        assert modern_error.error == "Input validation failed"
        assert modern_error.error_code == FlextConstants.Errors.VALIDATION_ERROR
        assert modern_error.error_data is not None
        assert modern_error.error_data["legacy_error_code"] == "INVALID_INPUT"


class TestAdvancedPatternsUpdated:
    """Test advanced patterns using new FlextCqrs architecture."""

    def test_query_pattern_with_new_api(self) -> None:
        """Test query patterns using FlextCqrs.Operations."""
        query_data: dict[str, object] = {
            "query_type": "GetUserData",
            "criteria": {
                "user_id": "12345",
                "include_roles": True,
                "include_permissions": False,
            },
            "limit": 10,
            "offset": 0,
        }

        result: FlextResult[object] = FlextCqrs.Operations.create_query(query_data)

        assert result.is_success
        query: object = result.value
        assert hasattr(query, "query_type")
        assert hasattr(query, "criteria")
        assert hasattr(query, "limit")
        assert getattr(query, "query_type") == "GetUserData"
        criteria: dict[str, object] = getattr(query, "criteria")
        assert criteria["user_id"] == "12345"
        assert getattr(query, "limit") == 10

    def test_command_query_separation(self) -> None:
        """Test proper command/query separation with FlextCqrs."""
        # Command - modifies state
        command_data: dict[str, object] = {
            "command_type": "UpdateUserProfile",
            "payload": {
                "user_id": "12345",
                "profile_data": {"name": "Updated Name", "email": "new@example.com"},
            },
            "priority": "normal",
        }

        command_result: FlextResult[object] = FlextCqrs.Operations.create_command(
            command_data
        )
        assert command_result.is_success

        # Query - reads state
        query_data: dict[str, object] = {
            "query_type": "GetUpdatedUserProfile",
            "criteria": {"user_id": "12345"},
            "limit": 1,
        }

        query_result: FlextResult[object] = FlextCqrs.Operations.create_query(
            query_data
        )
        assert query_result.is_success

        # Verify separation
        command: object = command_result.value
        query: object = query_result.value

        assert hasattr(command, "command_type")
        assert hasattr(query, "query_type")
        assert getattr(command, "command_type") == "UpdateUserProfile"
        assert getattr(query, "query_type") == "GetUpdatedUserProfile"
        assert hasattr(command, "model_fields")
        assert hasattr(query, "model_fields")
        assert "payload" in getattr(command, "model_fields", {})
        assert "criteria" in getattr(query, "model_fields", {})

    def test_configuration_driven_handlers(self) -> None:
        """Test configuration-driven handler patterns."""
        # Create different handler configurations
        batch_config: FlextResult[object] = FlextCqrs.Operations.create_handler_config(
            "command",
            handler_name="BatchProcessor",
            config_overrides={"batch_mode": True, "timeout": 60000},
        )

        realtime_config: FlextResult[object] = (
            FlextCqrs.Operations.create_handler_config(
                "command",
                handler_name="RealtimeProcessor",
                config_overrides={"batch_mode": False, "timeout": 5000},
            )
        )

        assert batch_config.is_success
        assert realtime_config.is_success

        # Verify different configurations
        batch_handler: object = batch_config.value
        realtime_handler: object = realtime_config.value

        assert hasattr(batch_handler, "handler_name")
        assert hasattr(realtime_handler, "handler_name")
        assert hasattr(batch_handler, "handler_id")
        assert hasattr(realtime_handler, "handler_id")
        assert getattr(batch_handler, "handler_name") == "BatchProcessor"
        assert getattr(realtime_handler, "handler_name") == "RealtimeProcessor"
        assert getattr(batch_handler, "handler_id") != getattr(
            realtime_handler, "handler_id"
        )


if __name__ == "__main__":
    pytest.main([__file__])
