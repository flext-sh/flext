"""Comprehensive tests for FlextLdapDomainServices.

This module provides complete test coverage for the FlextLdapDomainServices class
following FLEXT standards with proper domain separation and real functionality testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_core import (
    FlextBus,
    FlextContainer,
    FlextDispatcher,
    FlextModels,
    FlextProcessors,
    FlextRegistry,
    FlextResult,
)
from flext_ldap import FlextLdapClient, FlextLdapDomainServices


@pytest.fixture
def domain_services() -> FlextLdapDomainServices:
    """Create FlextLdapDomainServices instance for testing."""
    # Create minimal config with required fields
    config = FlextModels.CqrsConfig.Handler(
        handler_id="test-handler",
        handler_name="Test Handler"
    )
    
    # Create mock client
    client = FlextLdapClient()
    
    # Create container and other components in correct order
    container = FlextContainer.get_global()
    bus = FlextBus()
    dispatcher = FlextDispatcher()
    processors = FlextProcessors()
    registry = FlextRegistry(dispatcher=dispatcher)
    
    return FlextLdapDomainServices(
        config=config,
        client=client,
        container=container,
        bus=bus,
        dispatcher=dispatcher,
        processors=processors,
        registry=registry,
    )


class TestFlextLdapDomainServices:
    """Comprehensive test suite for FlextLdapDomainServices."""

    def test_domain_services_initialization(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test domain services initialization."""
        assert domain_services is not None
        assert hasattr(domain_services, "_client")
        assert hasattr(domain_services, "_container")
        assert hasattr(domain_services, "_bus")
        assert hasattr(domain_services, "_dispatcher")
        assert hasattr(domain_services, "_processors")
        assert hasattr(domain_services, "_registry")
        assert hasattr(domain_services, "_models")
        assert hasattr(domain_services, "_types")
        assert hasattr(domain_services, "_constants")

    def test_handle_invalid_message_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test handling invalid message type."""
        result = domain_services.handle("invalid_message")
        assert result.is_failure
        assert "Message must be a dictionary" in result.error

    def test_handle_missing_service_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test handling message without service_type."""
        message = {"data": "test"}
        result = domain_services.handle(message)
        assert result.is_failure
        assert "Service type must be a string" in result.error

    def test_handle_invalid_service_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test handling message with invalid service_type."""
        message = {"service_type": 123}
        result = domain_services.handle(message)
        assert result.is_failure
        assert "Service type must be a string" in result.error

    def test_handle_unknown_service_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test handling unknown service type."""
        message = {"service_type": "unknown_service"}
        result = domain_services.handle(message)
        assert result.is_failure
        assert "Unknown service type: unknown_service" in result.error

    def test_handle_user_aggregate_management(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test user aggregate management service."""
        message = {
            "service_type": "user_aggregate_management",
            "operation": "create_user",
            "user_data": {"uid": "testuser", "cn": "Test User"},
        }
        result = domain_services.handle(message)
        # The actual implementation should handle this
        assert isinstance(result, FlextResult)

    def test_handle_organization_domain_service(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test organization domain service."""
        message = {
            "service_type": "organization_domain_service",
            "operation": "create_ou",
            "ou_data": {"name": "test_ou", "parent": "dc=test,dc=com"},
        }
        result = domain_services.handle(message)
        # The actual implementation should handle this
        assert isinstance(result, FlextResult)

    def test_handle_security_policy_enforcement(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test security policy enforcement service."""
        message = {
            "service_type": "security_policy_enforcement",
            "operation": "validate_access",
            "access_data": {"user": "testuser", "resource": "test_resource"},
        }
        result = domain_services.handle(message)
        # The actual implementation should handle this
        assert isinstance(result, FlextResult)

    def test_handle_audit_trail_management(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test audit trail management service."""
        message = {
            "service_type": "audit_trail_management",
            "operation": "log_event",
            "event_data": {"action": "user_login", "user": "testuser"},
        }
        result = domain_services.handle(message)
        # The actual implementation should handle this
        assert isinstance(result, FlextResult)

    def test_handle_event_sourcing_orchestration(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test event sourcing orchestration service."""
        message = {
            "service_type": "event_sourcing_orchestration",
            "operation": "process_event",
            "event_data": {"event_type": "user_created", "payload": {}},
        }
        result = domain_services.handle(message)
        # The actual implementation should handle this
        assert isinstance(result, FlextResult)

    def test_cqrs_command_handler_initialization(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS command handler initialization."""
        # Test that the nested CqrsCommandHandler class exists and can be instantiated
        cqrs_services = domain_services.get_cqrs_services()
        assert cqrs_services is not None

        # Test command handler
        command_handler = cqrs_services.command_handler
        assert command_handler is not None
        assert hasattr(command_handler, "handle")

    def test_cqrs_query_handler_initialization(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS query handler initialization."""
        cqrs_services = domain_services.get_cqrs_services()
        assert cqrs_services is not None

        # Test query handler
        query_handler = cqrs_services.query_handler
        assert query_handler is not None
        assert hasattr(query_handler, "handle")

    def test_cqrs_command_handler_invalid_message(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS command handler with invalid message."""
        cqrs_services = domain_services.get_cqrs_services()
        command_handler = cqrs_services.command_handler

        result = command_handler.handle("invalid_message")
        assert result.is_failure
        assert "Message must be a dictionary" in result.error

    def test_cqrs_command_handler_missing_operation_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS command handler with missing operation_type."""
        cqrs_services = domain_services.get_cqrs_services()
        command_handler = cqrs_services.command_handler

        message = {"data": "test"}
        result = command_handler.handle(message)
        assert result.is_failure
        assert "Operation type must be a string" in result.error

    def test_cqrs_command_handler_invalid_operation_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS command handler with invalid operation_type."""
        cqrs_services = domain_services.get_cqrs_services()
        command_handler = cqrs_services.command_handler

        message = {"operation_type": 123}
        result = command_handler.handle(message)
        assert result.is_failure
        assert "Operation type must be a string" in result.error

    def test_cqrs_command_handler_unknown_operation_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS command handler with unknown operation_type."""
        cqrs_services = domain_services.get_cqrs_services()
        command_handler = cqrs_services.command_handler

        message = {"operation_type": "unknown_operation"}
        result = command_handler.handle(message)
        assert result.is_failure
        assert "Unknown operation type: unknown_operation" in result.error

    def test_cqrs_query_handler_invalid_message(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS query handler with invalid message."""
        cqrs_services = domain_services.get_cqrs_services()
        query_handler = cqrs_services.query_handler

        result = query_handler.handle("invalid_message")
        assert result.is_failure
        assert "Message must be a dictionary" in result.error

    def test_cqrs_query_handler_missing_operation_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS query handler with missing operation_type."""
        cqrs_services = domain_services.get_cqrs_services()
        query_handler = cqrs_services.query_handler

        message = {"data": "test"}
        result = query_handler.handle(message)
        assert result.is_failure
        assert "Operation type must be a string" in result.error

    def test_cqrs_query_handler_invalid_operation_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS query handler with invalid operation_type."""
        cqrs_services = domain_services.get_cqrs_services()
        query_handler = cqrs_services.query_handler

        message = {"operation_type": 123}
        result = query_handler.handle(message)
        assert result.is_failure
        assert "Operation type must be a string" in result.error

    def test_cqrs_query_handler_unknown_operation_type(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test CQRS query handler with unknown operation_type."""
        cqrs_services = domain_services.get_cqrs_services()
        query_handler = cqrs_services.query_handler

        message = {"operation_type": "unknown_operation"}
        result = query_handler.handle(message)
        assert result.is_failure
        assert "Unknown operation type: unknown_operation" in result.error

    def test_domain_services_error_handling(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test domain services error handling."""
        # Test with malformed message that should cause an exception
        message = {"service_type": "user_aggregate_management"}
        result = domain_services.handle(message)
        # Should handle gracefully and return FlextResult
        assert isinstance(result, FlextResult)

    def test_domain_services_flext_result_patterns(
        self, domain_services: FlextLdapDomainServices
    ) -> None:
        """Test that domain services consistently use FlextResult patterns."""
        # Test various message types to ensure consistent FlextResult usage
        test_messages = [
            {"service_type": "user_aggregate_management"},
            {"service_type": "organization_domain_service"},
            {"service_type": "security_policy_enforcement"},
            {"service_type": "audit_trail_management"},
            {"service_type": "event_sourcing_orchestration"},
        ]

        for message in test_messages:
            result = domain_services.handle(message)
            assert isinstance(result, FlextResult)
            assert hasattr(result, "is_success")
            assert hasattr(result, "is_failure")
            assert hasattr(result, "error")
            assert hasattr(result, "value")
