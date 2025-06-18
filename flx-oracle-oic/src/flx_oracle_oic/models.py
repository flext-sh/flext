"""Domain models for Oracle Integration Cloud using FLX base classes with zero redundancy."""

from typing import Any, ClassVar

from flx.core.base import (  # type: ignore[import-untyped]
    DomainObject,
    Identifiable,
    Timestamped,
)
from pydantic import Field

from .constants import (
    DEFAULT_PAGE_SIZE,
    ENV_PROD,
    FIELD_DESCRIPTION,
    FIELD_ENTITY_NAME,
    FIELD_ENTITY_TYPE,
    FIELD_IDENTIFIER,
    FIELD_NAME,
    FIELD_STATUS,
    FIELD_VERSION,
    STATUS_ACTIVE,
    TEST_INTEGRATION_DESC,
    TEST_INTEGRATION_ID,
    TEST_INTEGRATION_NAME,
)


class OicIntegration(DomainObject, Identifiable, Timestamped):  # type: ignore[misc]
    """Oracle Integration Cloud integration domain entity.

    Represents a complete integration configuration with validation,
    lifecycle tracking, and business rule enforcement.
    """

    name: str = Field(min_length=1, max_length=255)
    identifier: str = Field(min_length=1, max_length=100)
    version: str = Field(default="1.0.0")
    description: str = Field(default="")
    status: str = Field(default=STATUS_ACTIVE)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Type mapping for constants validation
    _type_mapping: ClassVar[dict[str, str]] = {
        FIELD_NAME: "name",
        FIELD_IDENTIFIER: "identifier",
        FIELD_VERSION: "version",
        FIELD_DESCRIPTION: "description",
        FIELD_STATUS: "status",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OicIntegration":
        """Create integration from dictionary with field mapping."""
        mapped_data = {}
        for const_key, field_name in cls._type_mapping.items():
            if const_key in data:
                mapped_data[field_name] = data[const_key]

        # Add remaining fields
        for key, value in data.items():
            if key not in cls._type_mapping and key not in mapped_data:
                mapped_data[key] = value

        return cls(**mapped_data)


class OicConnection(DomainObject, Identifiable, Timestamped):  # type: ignore[misc]
    """Oracle Integration Cloud connection domain entity."""

    name: str = Field(min_length=1, max_length=255)
    identifier: str = Field(min_length=1, max_length=100)
    connection_type: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    _type_mapping: ClassVar[dict[str, str]] = {
        FIELD_NAME: "name",
        FIELD_IDENTIFIER: "identifier",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OicConnection":
        """Create connection from dictionary with field mapping."""
        mapped_data = {}
        for const_key, field_name in cls._type_mapping.items():
            if const_key in data:
                mapped_data[field_name] = data[const_key]

        for key, value in data.items():
            if key not in cls._type_mapping and key not in mapped_data:
                mapped_data[key] = value

        return cls(**mapped_data)


class FlxOicMonitoringData(DomainObject, Timestamped):  # type: ignore[misc]
    """OIC monitoring data value object."""

    entity_name: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)
    metrics: dict[str, Any] = Field(default_factory=dict)

    _type_mapping: ClassVar[dict[str, str]] = {
        FIELD_ENTITY_NAME: "entity_name",
        FIELD_ENTITY_TYPE: "entity_type",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FlxOicMonitoringData":
        """Create monitoring data from dictionary with field mapping."""
        mapped_data = {}
        for const_key, field_name in cls._type_mapping.items():
            if const_key in data:
                mapped_data[field_name] = data[const_key]

        for key, value in data.items():
            if key not in cls._type_mapping and key not in mapped_data:
                mapped_data[key] = value

        return cls(**mapped_data)


# Test data factory functions
def create_test_integration() -> OicIntegration:
    """Create test integration with predefined constants."""
    return OicIntegration(
        name=TEST_INTEGRATION_NAME,
        identifier=TEST_INTEGRATION_ID,
        description=TEST_INTEGRATION_DESC,
        metadata={"env": ENV_PROD},
    )


def create_test_monitoring_data() -> FlxOicMonitoringData:
    """Create test monitoring data with predefined constants."""
    return FlxOicMonitoringData(
        entity_name="Test Entity",
        entity_type="integration",
        metrics={"count": DEFAULT_PAGE_SIZE},
    )
