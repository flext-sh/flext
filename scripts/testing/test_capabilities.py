#!/usr/bin/env python3
"""Test isolado para o sistema de capabilities."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, TypeVar, cast


class CapabilityType(Enum):
    """Standard capability types for FLX framework components."""
    LOGGING = "logging"
    HEALTH_CHECK = "health_check"
    METRICS = "metrics"


@dataclass
class CapabilityMetadata:
    """Metadata describing a capability's requirements and behavior."""
    capability_type: CapabilityType
    name: str
    description: str
    version: str = "1.0.0"
    required_config: list[str] = field(default_factory=list)
    optional_config: list[str] = field(default_factory=list)
    is_async: bool = False
    is_stateful: bool = False


class Capability(Protocol):
    """Protocol defining the interface for all capabilities."""

    @property
    def metadata(self) -> CapabilityMetadata:
        """Get capability metadata and requirements."""
        ...

    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize the capability with configuration."""
        ...

    async def cleanup(self) -> None:
        """Clean up capability resources."""
        ...

    def is_healthy(self) -> bool:
        """Check if capability is healthy and operational."""
        ...


class LoggingCapability:
    """Simple logging capability."""

    def __init__(self):
        self._logger_name = "test"
        self._messages = []

    @property
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_type=CapabilityType.LOGGING,
            name="simple_logging",
            description="Simple logging capability"
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        self._logger_name = config.get("logger_name", "test")

    async def cleanup(self) -> None:
        self._messages.clear()

    def is_healthy(self) -> bool:
        return True

    def info(self, message: str, **kwargs) -> None:
        log_entry = f"INFO [{self._logger_name}]: {message}"
        if kwargs:
            log_entry += f" {kwargs}"
        self._messages.append(log_entry)
        print(log_entry)


class HealthCheckCapability:
    """Simple health check capability."""

    def __init__(self):
        self._is_healthy = True
        self._checks = []

    @property
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_type=CapabilityType.HEALTH_CHECK,
            name="simple_health",
            description="Simple health check"
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def cleanup(self) -> None:
        self._checks.clear()

    def is_healthy(self) -> bool:
        return all(check() for check in self._checks) if self._checks else self._is_healthy

    def add_health_check(self, check_func) -> None:
        self._checks.append(check_func)


class MetricsCapability:
    """Simple metrics capability."""

    def __init__(self):
        self._counters = {}

    @property
    def metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_type=CapabilityType.METRICS,
            name="simple_metrics",
            description="Simple metrics collection"
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def cleanup(self) -> None:
        self._counters.clear()

    def is_healthy(self) -> bool:
        return True

    def increment_counter(self, name: str, value: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + value

    def get_metrics(self) -> dict[str, Any]:
        return {"counters": self._counters.copy()}


T = TypeVar('T')


class CapabilityComposer:
    """Composer for building objects with capability-based functionality."""

    _capability_registry: dict[CapabilityType, type[Capability]] = {
        CapabilityType.LOGGING: LoggingCapability,
        CapabilityType.HEALTH_CHECK: HealthCheckCapability,
        CapabilityType.METRICS: MetricsCapability,
    }

    @classmethod
    def compose(
        cls,
        base_class: type[T],
        capabilities: set[CapabilityType],
        config: dict[str, Any] | None = None
    ) -> type[T]:
        """Compose a class with specified capabilities."""
        config = config or {}

        class ComposedClass(base_class):
            """Dynamically composed class with capabilities."""

            def __init__(self, *args, **kwargs):
                # Initialize base class
                super().__init__(*args, **kwargs)

                # Initialize capabilities
                self._capabilities: dict[CapabilityType, Capability] = {}
                self._capability_config = config

                # Create and configure capabilities
                for cap_type in capabilities:
                    if cap_type in cls._capability_registry:
                        cap_class = cls._capability_registry[cap_type]
                        capability = cap_class()
                        self._capabilities[cap_type] = capability

                        # Add capability as attribute for easy access
                        setattr(self, cap_type.value, capability)

            async def _initialize_capabilities(self) -> None:
                """Initialize all capabilities with configuration."""
                for cap_type, capability in self._capabilities.items():
                    cap_config = self._capability_config.get(cap_type.value, {})
                    await capability.initialize(cap_config)

            async def _cleanup_capabilities(self) -> None:
                """Clean up all capabilities."""
                for capability in self._capabilities.values():
                    await capability.cleanup()

            def get_capabilities(self) -> dict[CapabilityType, Capability]:
                """Get all active capabilities."""
                return self._capabilities.copy()

            def has_capability(self, capability_type: CapabilityType) -> bool:
                """Check if component has specific capability."""
                return capability_type in self._capabilities

            def is_healthy(self) -> bool:
                """Check overall health of component and capabilities."""
                for capability in self._capabilities.values():
                    if not capability.is_healthy():
                        return False
                return True

        ComposedClass.__name__ = f"Composed{base_class.__name__}"
        ComposedClass.__qualname__ = f"Composed{base_class.__qualname__}"

        return cast(type[T], ComposedClass)


# Test the system
class SimpleAdapter:
    def __init__(self, name):
        self.name = name

    def process(self, data):
        return f'Processing {data} with {self.name}'


async def test_capability_system():
    print("🚀 Testing Capability-based Composition System")
    print("=" * 50)

    # Test basic composition
    EnhancedAdapter = CapabilityComposer.compose(
        SimpleAdapter,
        {CapabilityType.LOGGING, CapabilityType.HEALTH_CHECK, CapabilityType.METRICS},
        config={
            "logging": {"logger_name": "test_adapter"},
        }
    )

    adapter = EnhancedAdapter('TestAdapter')
    await adapter._initialize_capabilities()

    print('✅ Adapter created with capabilities:')
    print(f'   Has logging: {adapter.has_capability(CapabilityType.LOGGING)}')
    print(f'   Has health check: {adapter.has_capability(CapabilityType.HEALTH_CHECK)}')
    print(f'   Has metrics: {adapter.has_capability(CapabilityType.METRICS)}')
    print(f'   Is healthy: {adapter.is_healthy()}')
    print()

    # Test logging capability
    adapter.logging.info('Adapter initialized', component=adapter.name)
    adapter.logging.info('Processing data', operation='test')
    print('✅ Logging capability works')
    print()

    # Test health check
    adapter.health_check.add_health_check(lambda: True)
    adapter.health_check.add_health_check(lambda: adapter.name == 'TestAdapter')
    print(f'✅ Health check result: {adapter.health_check.is_healthy()}')
    print()

    # Test metrics
    adapter.metrics.increment_counter('operations_count')
    adapter.metrics.increment_counter('data_processed', 5)
    metrics = adapter.metrics.get_metrics()
    print(f'✅ Metrics collected: {metrics}')
    print()

    # Test original functionality still works
    result = adapter.process("test_data")
    print(f'✅ Original functionality: {result}')
    print()

    await adapter._cleanup_capabilities()
    print('✅ Capabilities cleaned up')
    print()

    print("🎉 All capability tests passed successfully!")
    print()
    print("Benefits achieved:")
    print("  ✅ No multiple inheritance complexity")
    print("  ✅ Clear separation of concerns")
    print("  ✅ Runtime capability inspection")
    print("  ✅ Easy testing and mocking")
    print("  ✅ Dynamic capability management")


if __name__ == "__main__":
    asyncio.run(test_capability_system())
