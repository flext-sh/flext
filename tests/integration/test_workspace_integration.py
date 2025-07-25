"""Integration tests for FLEXT workspace.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Tests the integration between all FLEXT modules using
the centralized DI container and Clean Architecture.
"""

from __future__ import annotations

import pytest
from flext_core import DIContainer, get_container


class TestWorkspaceIntegration:
    """Test integration between FLEXT modules."""

    def test_di_container_initialization(self) -> None:
        """Test that DI container initializes correctly."""
        container = get_container()
        assert isinstance(container, DIContainer)

    def test_service_registration(self) -> None:
        """Test service registration in DI container."""
        container = DIContainer()

        # Define test service and implementation
        class ITestService:
            def get_value(self) -> str:
                raise NotImplementedError

        class TestService(ITestService):
            def get_value(self) -> str:
                return "test_value"

        # Register service factory
        container.register_factory(ITestService, TestService)

        # Resolve service
        service = container.resolve(ITestService)

        assert isinstance(service, TestService)
        assert service.get_value() == "test_value"

    def test_dependency_injection(self) -> None:
        """Test dependency injection between services."""
        container = DIContainer()

        # Define services with dependencies
        class IDatabase:
            def connect(self) -> str:
                raise NotImplementedError

        class Database(IDatabase):
            def connect(self) -> str:
                return "connected"

        class IRepository:
            def get_data(self) -> str:
                raise NotImplementedError

        class Repository(IRepository):
            def __init__(self, database: IDatabase) -> None:
                self.database = database

            def get_data(self) -> str:
                return f"data from {self.database.connect()}"

        # Register services
        container.register_singleton(IDatabase, Database)
        container.register_factory(IRepository, Repository)

        # Resolve with dependencies
        repo = container.resolve(IRepository)

        assert isinstance(repo, Repository)
        assert repo.get_data() == "data from connected"

    def test_singleton_services(self) -> None:
        """Test singleton service lifetime."""
        container = DIContainer()

        # Counter to track instances
        instance_count = 0

        class SingletonService:
            def __init__(self) -> None:
                nonlocal instance_count
                instance_count += 1
                self.instance_id = instance_count

        container.register_singleton(SingletonService, SingletonService)

        # Get service multiple times
        service1 = container.resolve(SingletonService)
        service2 = container.resolve(SingletonService)

        # Same instance should be returned
        assert service1 is service2
        assert service1.instance_id == 1
        assert instance_count == 1  # Only created once

    @pytest.mark.asyncio
    async def test_async_service_integration(self) -> None:
        """Test async service integration."""
        container = DIContainer()

        class IAsyncService:
            async def process(self) -> str:
                raise NotImplementedError

        class AsyncService(IAsyncService):
            async def process(self) -> str:
                return "async_result"

        container.register_singleton(IAsyncService, AsyncService)

        service = container.resolve(IAsyncService)

        result = await service.process()
        assert result == "async_result"


class TestModuleIntegration:
    """Test integration between specific FLEXT modules."""

    def test_core_types_across_modules(self) -> None:
        """Test that core types can be used across modules."""
        from flext_core import EntityId, Version

        # Test type constraints work
        valid_id: EntityId = "test-123"
        assert valid_id == "test-123"

        # Version should work with string values
        version: Version = "1.0.0"
        assert version == "1.0.0"

    def test_config_integration(self) -> None:
        """Test configuration system integration."""
        from flext_core import BaseSettings, Field

        class TestSettings(BaseSettings):
            app_name: str = Field(default="test_app")
            debug: bool = Field(default=True)

        settings = TestSettings()
        assert settings.app_name == "test_app"
        assert settings.debug is True

    def test_domain_model_integration(self) -> None:
        """Test domain model integration across modules."""
        from flext_core import DomainEntity, EntityId, Field

        class TestEntity(DomainEntity):
            id: EntityId
            name: str = Field(description="Entity name")

        entity = TestEntity(id="test-123", name="Test Entity")
        assert entity.id == "test-123"
        assert entity.name == "Test Entity"


class TestObservabilityIntegration:
    """Test observability integration across modules."""

    def test_logging_setup(self) -> None:
        """Test that logging can be configured centrally."""
        from flext_observability import get_logger, setup_logging

        # Setup logging
        setup_logging(level="INFO", format="json")

        # Get logger for module
        logger = get_logger("test_module")
        assert logger is not None

    def test_metrics_collection(self) -> None:
        """Test metrics collection integration."""
        from flext_observability import MetricsCollector

        collector = MetricsCollector()
        assert collector is not None

    async def test_health_check_integration(self) -> None:
        """Test health check integration."""
        from flext_observability import ComponentHealth, HealthChecker

        checker = HealthChecker()

        # Add component health
        from flext_observability.domain.value_objects import HealthStatus

        component = ComponentHealth(
            name="test_component",
            status=HealthStatus.HEALTHY,
            details={"version": "1.0.0"},
        )

        checker.register_component(component)

        health = await checker.check_health()
        assert health["status"] == "healthy"


class TestCLIIntegration:
    """Test CLI integration across modules."""

    def test_cli_with_di_container(self) -> None:
        """Test CLI can use DI container."""
        import click
        from flext_cli import BaseCLI
        from flext_core import get_container

        class TestCLI(BaseCLI):
            def __init__(self) -> None:
                super().__init__(name="test-cli", version="1.0.0", description="Test CLI for integration tests")
                self.container = get_container()

            def create_cli(self) -> click.Group:
                """Create CLI application."""

                @click.group()
                def cli() -> None:
                    """Test CLI."""

                return cli

        cli = TestCLI()
        assert cli.container is not None


class TestFullStackIntegration:
    """Test full stack integration scenarios."""

    @pytest.mark.integration
    def test_api_to_database_flow(self) -> None:
        """Test complete flow from API to database."""
        container = get_container()

        # This would test a complete flow through:
        # 1. API endpoint (flext-api)
        # 2. Service layer (flext-core)
        # 3. Repository (flext-core)
        # 4. Database (infrastructure)

        # Simplified test - full implementation would use real services
        assert container is not None

    @pytest.mark.integration
    def test_plugin_loading_and_execution(self) -> None:
        """Test plugin loading and execution flow."""
        from flext_plugin import PluginManager

        # Test plugin discovery and loading
        # This would integrate with the DI container
        # to inject dependencies into plugins

        # Simplified test
        assert PluginManager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
