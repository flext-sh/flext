"""This module provides comprehensive configuration handling with validation.

Type safety, and enterprise features using standardized flext-core patterns.
Enhanced to fully utilize flext-infrastructure.databases.flext-db-oracle
parameterization and modern typing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import ValidationInfo, field_validator, model_validator

# Use flext-core configuration patterns
from flext_core import (
    BaseSettings,
    Field,
    FlextFramework,
)
from flext_core.base import BaseComponentConfig
from flext_core.domain.constants import (
    ConfigDefaults,
    LogLevels,
)

# Import tap-specific constants with flext-core integration
from .constants import OracleTapConstants

# Define Oracle-specific type aliases for tap-oracle
# Oracle-specific types for this tap implementation
if TYPE_CHECKING:
    from flext_core.domain.types import EnvironmentLiteral

    # Use proper types for type checking
    NonEmptyStr = str
    OracleBatchSize = int
    OracleConnectionDict = dict[str, Any]
    OracleHost = str
    OraclePassword = str
    OraclePort = int
    OracleQueryTimeout = int
    OracleSchema = str
    OracleServiceName = str
    OracleSID = str
    OracleTapCompleteConfig = dict[str, Any]
    OracleUsername = str
    PositiveInt = int
    SingerParallelStreams = int
    SingerPrimaryKey = list[str]
    SingerReplicationKey = str
    SingerReplicationMethod = str
    SingerStreamName = str
    TableName = str
    TimeoutSeconds = int
else:
    # Use simple types at runtime to avoid import errors
    NonEmptyStr = str
    OracleBatchSize = int
    OracleConnectionDict = dict
    OracleHost = str
    OraclePassword = str
    OraclePort = int
    OracleQueryTimeout = int
    OracleSchema = str
    OracleServiceName = str
    OracleSID = str
    OracleTapCompleteConfig = dict
    OracleUsername = str
    PositiveInt = int
    SingerParallelStreams = int
    SingerPrimaryKey = list
    SingerReplicationKey = str
    SingerReplicationMethod = str
    SingerStreamName = str
    TableName = str
    TimeoutSeconds = int

from flext_db_oracle import OracleConfig
from flext_observability.logging import get_logger

logger = get_logger(__name__)


# ==============================================================================
# CONSTANTS - Imported from dedicated constants.py for maximum flext-core integration
# ==============================================================================
# All Oracle Tap constants are now centralized in ./constants.py
# This eliminates duplication and ensures flext-core compliance


# ==============================================================================
# ORACLE TAP SETTINGS - Using flext-core BaseSettings patterns
# ==============================================================================


class OracleTapSettings(BaseSettings):
    """Modern Oracle Tap Settings using flext-core BaseSettings patterns.

    Provides environment variable integration, validation, and dependency injection
    using standardized flext-core patterns for enterprise configuration management.
    """

    # Project identification
    project_name: str = Field(default="flext-data.taps.flext-tap-oracle")
    project_version: str = Field(default=FlextFramework.VERSION)
    environment: EnvironmentLiteral = Field(default="development")

    # Oracle Database connection (environment variables)
    oracle_host: OracleHost | None = Field(
        default=None,
        description="Oracle database host",
    )
    oracle_port: OraclePort = Field(default=1521, description="Oracle database port")
    oracle_service_name: OracleServiceName | None = Field(
        default=None,
        description="Oracle service name",
    )
    oracle_username: OracleUsername | None = Field(
        default=None,
        description="Oracle username",
    )
    oracle_password: OraclePassword | None = Field(
        default=None,
        description="Oracle password",
    )
    oracle_schema: OracleSchema | None = Field(
        default=None,
        description="Oracle schema name",
    )

    # Performance settings
    default_batch_size: OracleBatchSize = Field(
        default=ConfigDefaults.DEFAULT_BATCH_SIZE,
        description="Default batch size for extraction",
    )
    default_timeout: OracleQueryTimeout = Field(
        default=ConfigDefaults.DEFAULT_TIMEOUT,
        description="Default query timeout",
    )

    # Logging
    log_level: str = Field(default=LogLevels.INFO, description="Default log level")

    # Model configuration for environment variables
    class Config:
        """Model configuration for environment variables."""

        env_prefix = "TAP_ORACLE_"
        env_file = ".env"
        case_sensitive = False

    def to_tap_config(self) -> TapOracleConfig:
        """Convert settings to TapOracleConfig.

        Returns:
            TapOracleConfig instance with environment values

        """
        return TapOracleConfig(
            host=self.oracle_host,
            port=self.oracle_port,
            service_name=self.oracle_service_name,
            username=self.oracle_username,
            password=self.oracle_password,
            schema_name=self.oracle_schema,
            batch_size=self.default_batch_size,
            query_timeout=self.default_timeout,
            log_level=self.log_level,
            project_name=self.project_name,
            project_version=self.project_version,
            environment=self.environment,
        )


class Config(BaseComponentConfig):
    """Configuration for the Oracle Tap with comprehensive validation.

    Supports multiple Oracle connection types and provides enterprise-grade
    configuration management with validation, secrets handling, and
    environment variable integration.
    """

    # Connection type and basic settings
    connection_type: str = Field(
        default="database",
        description="Type of Oracle connection (database only)",
        pattern="^database$",
    )

    # Project identification using flext-core patterns
    project_name: str = Field(
        default="flext-data.taps.flext-tap-oracle",
        description="Project name",
    )
    project_version: str = Field(
        default=FlextFramework.VERSION,
        description="Project version",
    )
    environment: str = Field(
        default="development",
        description="Environment name",
    )

    # Oracle Database connection using standardized Oracle types
    host: OracleHost | None = Field(
        default=None,
        description="Oracle database host",
    )
    port: OraclePort = Field(
        default=1521,
        description="Oracle database port",
    )
    service_name: OracleServiceName | None = Field(
        default=None,
        description="Oracle service name",
    )
    sid: OracleSID | None = Field(
        default=None,
        description="Oracle SID (alternative to service_name)",
    )
    username: OracleUsername | None = Field(
        default=None,
        description="Oracle username",
    )
    password: OraclePassword | None = Field(
        default=None,
        description="Oracle password",
    )
    schema_name: OracleSchema | None = Field(
        default=None,
        description="Oracle schema name",
    )

    # Stream configuration using flext-core types
    tables: list[TableName] | None = Field(
        default=None,
        description="List of Oracle tables to extract",
    )
    exclude_tables: list[TableName] | None = Field(
        default_factory=list,
        description="List of tables to exclude from extraction",
    )
    table_pattern: NonEmptyStr | None = Field(
        default=None,
        description="Regex pattern for table names to include",
    )

    # Performance configuration using standardized Oracle batch size
    batch_size: OracleBatchSize = Field(
        default=OracleTapConstants.DEFAULT_BATCH_SIZE,
        description="Batch size for data extraction",
        le=OracleTapConstants.MAX_BATCH_SIZE,
    )
    max_parallel_streams: SingerParallelStreams = Field(
        default=OracleTapConstants.DEFAULT_PARALLEL_STREAMS,
        description="Maximum number of parallel streams",
        le=OracleTapConstants.MAX_PARALLEL_STREAMS,
    )
    connection_pool_size: PositiveInt = Field(
        default=OracleTapConstants.DEFAULT_CONNECTION_POOL_SIZE,
        description="Connection pool size",
        le=OracleTapConstants.MAX_CONNECTION_POOL_SIZE,
    )
    query_timeout: OracleQueryTimeout = Field(
        default=OracleTapConstants.DEFAULT_TIMEOUT,
        description="Query timeout in seconds",
        le=OracleTapConstants.MAX_TIMEOUT,
    )

    # Advanced configuration
    enable_circuit_breaker: bool = Field(
        default=True,
        description="Enable circuit breaker for resilience",
    )
    circuit_breaker_failures: PositiveInt = Field(
        default=OracleTapConstants.DEFAULT_CIRCUIT_BREAKER_FAILURES,
        description="Number of failures before circuit breaker opens",
        le=100,
    )
    circuit_breaker_timeout: TimeoutSeconds = Field(
        default=OracleTapConstants.DEFAULT_CIRCUIT_BREAKER_TIMEOUT,
        description="Circuit breaker timeout in seconds",
        le=OracleTapConstants.MAX_TIMEOUT,
    )
    enable_async: bool = Field(
        default=True,
        description="Enable async processing for performance",
    )
    enable_metrics: bool = Field(
        default=True,
        description="Enable detailed metrics collection",
    )

    # Schema flattening configuration
    enable_flattening: bool = Field(
        default=False,
        description="Enable schema flattening for complex Oracle data structures",
    )
    flattening_max_depth: PositiveInt = Field(
        default=OracleTapConstants.DEFAULT_FLATTENING_MAX_DEPTH,
        description="Maximum depth for schema flattening",
        le=10,
    )
    flattening_separator: NonEmptyStr = Field(
        default=OracleTapConstants.DEFAULT_FLATTENING_SEPARATOR,
        description="Separator for flattened field names",
        max_length=10,
    )

    # Logging and observability using flext-core constants
    log_level: str = Field(
        default=LogLevels.INFO,
        description="Logging level",
    )
    enable_sql_logging: bool = Field(
        default=False,
        description="Enable SQL query logging (can be verbose)",
    )

    # Security configuration
    ssl_mode: str = Field(
        default="prefer",
        description="SSL connection mode",
        pattern="^(disable|allow|prefer|require)$",
    )
    ssl_cert_path: NonEmptyStr | None = Field(
        default=None,
        description="Path to SSL certificate file",
    )
    ssl_key_path: NonEmptyStr | None = Field(
        default=None,
        description="Path to SSL private key file",
    )
    ssl_ca_path: NonEmptyStr | None = Field(
        default=None,
        description="Path to SSL CA certificate file",
    )

    # Configuration inherits from BaseConfig but customizes prefix
    class Config:
        """Model configuration for environment variables."""

        env_prefix = "TAP_ORACLE_"
        case_sensitive = False
        extra = "forbid"  # Prevent unknown configuration keys

    @field_validator("connection_type")
    @classmethod
    def validate_connection_type(cls, v: str) -> str:
        """Validate connection type using constants."""
        if v not in OracleTapConstants.VALID_CONNECTION_TYPES:
            msg = (
                f"Invalid connection type: {v}. "
                f"Valid types: {OracleTapConstants.VALID_CONNECTION_TYPES}"
            )
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_database_connection_fields(self) -> Any:
        """Validate required fields for database connections."""
        if self.connection_type in {"database", "hybrid"}:
            if not self.host:
                raise ValueError("Host is required for database connections")
            if not self.service_name:
                raise ValueError("Service name is required for database connections")
            if not self.username:
                raise ValueError("Username is required for database connections")
            if not self.password:
                raise ValueError("Password is required for database connections")
        return self

    @field_validator("host")
    @classmethod
    def validate_host_for_database(
        cls,
        v: str | None,
        info: ValidationInfo,
    ) -> str | None:
        """Validate host is provided for database connections."""
        if info.data:
            connection_type = info.data.get("connection_type")
            if connection_type in {"database", "hybrid"} and not v:
                msg = "Host is required for database connections"
                raise ValueError(msg)
        return v

    @field_validator("service_name")
    @classmethod
    def validate_service_name_for_database(
        cls,
        v: str | None,
        info: ValidationInfo,
    ) -> str | None:
        """Validate service_name is provided for database connections."""
        if info.data:
            connection_type = info.data.get("connection_type")
            if connection_type in {"database", "hybrid"} and not v:
                msg = "Service name is required for database connections"
                raise ValueError(msg)
        return v

    @field_validator("username")
    @classmethod
    def validate_username_for_database(
        cls,
        v: str | None,
        info: ValidationInfo,
    ) -> str | None:
        """Validate username is provided for database connections."""
        if info.data:
            connection_type = info.data.get("connection_type")
            if connection_type in {"database", "hybrid"} and not v:
                msg = "Username is required for database connections"
                raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def validate_password_for_database(
        cls,
        v: str | None,
        info: ValidationInfo,
    ) -> str | None:
        """Validate password is provided for database connections."""
        if info.data:
            connection_type = info.data.get("connection_type")
            if connection_type in {"database", "hybrid"} and not v:
                msg = "Password is required for database connections"
                raise ValueError(msg)
        return v

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        """Validate batch size is reasonable using constants."""
        if v < OracleTapConstants.MIN_BATCH_SIZE:
            logger.warning("Small batch size (%d) may impact performance", v)
        elif v > OracleTapConstants.MAX_BATCH_SIZE:
            logger.warning("Large batch size (%d) may cause memory issues", v)
        return v

    @field_validator("max_parallel_streams")
    @classmethod
    def validate_max_parallel_streams(cls, v: int, info: ValidationInfo) -> int:
        """Validate max parallel streams against connection pool size."""
        if info.data:
            pool_size = info.data.get("connection_pool_size", 5)
            if v > pool_size:
                logger.warning(
                    "max_parallel_streams (%d) exceeds connection_pool_size (%d)",
                    v,
                    pool_size,
                )
        return v

    @field_validator("tables")
    @classmethod
    def validate_tables(
        cls,
        v: list[str] | None,
        info: ValidationInfo,
    ) -> list[str] | None:
        """Validate tables configuration."""
        if info.data:
            connection_type = info.data.get("connection_type")
            if connection_type == "database" and v is not None and len(v) == 0:
                logger.warning("Empty tables list - will discover all tables in schema")
        return v

    def get_connection_string(self) -> str:
        """Generate Oracle connection string for logging/display purposes.

        Returns:
            Connection string with masked password

        """
        return (
            f"oracle://{self.username}:***@{self.host}:{self.port}/{self.service_name}"
        )

    def get_effective_schema(self) -> str:
        """Get the effective schema name.

        Returns:
            Schema name, defaulting to username if not specified

        """
        return self.schema_name or self.username or "UNKNOWN"

    def to_connection_config(self) -> OracleConnectionDict:
        """Convert to connection configuration using flext-core composite types.

        Returns:
            Oracle connection dictionary with type safety

        """
        return {
            "host": self.host,
            "port": self.port,
            "service_name": self.service_name,
            "username": self.username,
            "password": self.password,
            "schema": self.get_effective_schema(),
        }

    def to_complete_config(self) -> OracleTapCompleteConfig:
        """Convert to complete Oracle Tap configuration using composite types.

        Returns:
            Complete Oracle Tap configuration with all settings

        """
        return {
            "connection_type": self.connection_type,
            "project_name": self.project_name,
            "project_version": self.project_version,
            "environment": self.environment,
            "host": self.host,
            "port": self.port,
            "service_name": self.service_name,
            "sid": self.sid,
            "username": self.username,
            "password": self.password,
            "schema": self.schema_name,
            "tables": self.tables,
            "exclude_tables": self.exclude_tables,
            "table_pattern": self.table_pattern,
            "batch_size": self.batch_size,
            "max_parallel_streams": self.max_parallel_streams,
            "connection_pool_size": self.connection_pool_size,
            "query_timeout": self.query_timeout,
            "enable_circuit_breaker": self.enable_circuit_breaker,
            "circuit_breaker_failures": self.circuit_breaker_failures,
            "circuit_breaker_timeout": self.circuit_breaker_timeout,
            "enable_async": self.enable_async,
            "enable_metrics": self.enable_metrics,
            "enable_flattening": self.enable_flattening,
            "flattening_max_depth": self.flattening_max_depth,
            "flattening_separator": self.flattening_separator,
            "log_level": self.log_level,
            "enable_sql_logging": self.enable_sql_logging,
            "ssl_mode": self.ssl_mode,
        }

    def to_oracle_config(self) -> OracleConfig:
        """Convert to modern flext-infrastructure.databases.flext-db-oracle OracleConfig.

        Returns:
            OracleConfig instance with proper parameterization

        """
        return OracleConfig(
            host=self.host or "localhost",
            port=self.port,
            service_name=self.service_name,
            sid=self.sid,
            username=self.username or "oracle",
            password=self.password or "oracle",
            protocol="tcp",
            # Performance settings from tap config
            pool_min_size=max(1, self.connection_pool_size // 2),
            pool_max_size=self.connection_pool_size,
            pool_increment=1,
            query_timeout=int(self.query_timeout),
            fetch_size=self.batch_size,
            connect_timeout=30,
            retry_attempts=3 if self.enable_circuit_breaker else 0,
            retry_delay=1.0,
        )

    def get_performance_settings(self) -> dict[str, Any]:
        """Get performance-related settings.

        Returns:
            Dictionary of performance configuration

        """
        return {
            "batch_size": self.batch_size,
            "max_parallel_streams": self.max_parallel_streams,
            "connection_pool_size": self.connection_pool_size,
            "query_timeout": self.query_timeout,
            "enable_async": self.enable_async,
        }

    def get_circuit_breaker_settings(self) -> dict[str, Any]:
        """Get circuit breaker configuration.

        Returns:
            Dictionary of circuit breaker settings

        """
        return {
            "enabled": self.enable_circuit_breaker,
            "failure_threshold": self.circuit_breaker_failures,
            "timeout": self.circuit_breaker_timeout,
        }

    def validate_configuration(self) -> bool:
        """Perform comprehensive configuration validation for Oracle Database.

        Returns:
            True if configuration is valid and complete

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            # This will trigger all field validators
            self.__class__(**self.dict())

            # Validate Oracle Database configuration completeness
            if not all([self.host, self.service_name, self.username, self.password]):
                self._raise_config_incomplete_error()

        except Exception:
            logger.exception("Configuration validation failed")
            raise
        else:
            logger.info("Oracle Database configuration validation successful")
            return True

    def _raise_config_incomplete_error(self) -> None:
        """Raise error for incomplete Oracle Database configuration."""
        msg = (
            "Incomplete Oracle Database configuration: host, service_name, "
            "username, and password are required"
        )
        raise ValueError(msg)


# TapOracleConfig alias for backward compatibility
TapOracleConfig = Config

# CRITICAL: Rebuild models after all forward references are resolved
# This fixes Pydantic "not fully defined" errors at runtime
TapOracleConfig.model_rebuild()
# TapOracleStreamConfig.model_rebuild()  # Stream config handled by base Singer classes
