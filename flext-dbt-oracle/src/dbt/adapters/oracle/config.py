"""Configuration management for the DBT Oracle Adapter using flext-core patterns.

This module provides comprehensive configuration handling with validation,
type safety, and enterprise features using standardized flext-core patterns.
Enhanced to fully utilize flext-infrastructure.databases.flext-db-oracle
parameterization and modern typing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from flext_core.config.base import BaseConfig
from flext_core.domain.constants import (
    Environments,
    FlextFramework,
    LogLevels,
)
from flext_db_oracle import OracleConfig
from flext_observability.logging import get_logger

# Use flext-core configuration patterns
from pydantic import ConfigDict, Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings

# Import DBT Oracle adapter-specific constants with flext-core integration
from .constants import DBTOracleAdapterConstants

if TYPE_CHECKING:
    # Import types from the types module where they're defined
    from .types import (
        NonEmptyStr,
        Port,
        PositiveInt,
        TimeoutSeconds,
    )

logger = get_logger(__name__)


# ==============================================================================
# CONSTANTS - Imported from dedicated constants.py for maximum flext-core integration
# ==============================================================================
# All DBT Oracle Adapter constants are now centralized in ./constants.py
# This eliminates duplication and ensures flext-core compliance


# ==============================================================================
# DBT ORACLE SETTINGS - Using flext-core BaseSettings patterns
# ==============================================================================


class DBTOracleSettings(BaseSettings):
    """Modern DBT Oracle Settings using flext-core BaseSettings patterns.

    Provides environment variable integration, validation, and dependency injection
    using standardized flext-core patterns for enterprise configuration management.
    """

    # Project identification
    project_name: str = Field(default="flext-data.dbt.flext-dbt-oracle")
    project_version: str = Field(default=FlextFramework.VERSION)
    environment: str = Field(default=Environments.DEVELOPMENT)

    # Oracle Database connection (environment variables)
    oracle_host: NonEmptyStr | None = Field(
        default=None,
        description="Oracle database host",
    )
    oracle_port: Port = Field(
        default=DBTOracleAdapterConstants.DEFAULT_PORT,
        description="Oracle database port",
    )
    oracle_service_name: NonEmptyStr | None = Field(
        default=DBTOracleAdapterConstants.DEFAULT_SERVICE_NAME,
        description="Oracle service name",
    )
    oracle_sid: NonEmptyStr | None = Field(
        default=None,
        description="Oracle SID",
    )
    oracle_username: NonEmptyStr | None = Field(
        default=None,
        description="Oracle username",
    )
    oracle_password: NonEmptyStr | None = Field(
        default=None,
        description="Oracle password",
    )
    oracle_protocol: NonEmptyStr = Field(
        default=DBTOracleAdapterConstants.DEFAULT_PROTOCOL,
        description="Oracle protocol",
    )

    # DBT-specific settings
    database: NonEmptyStr = Field(
        default=DBTOracleAdapterConstants.DEFAULT_DATABASE,
        description="DBT database name",
    )
    schema: NonEmptyStr = Field(
        default=DBTOracleAdapterConstants.DEFAULT_SCHEMA,
        description="DBT schema name",
    )
    materialization: str = Field(
        default=DBTOracleAdapterConstants.DEFAULT_MATERIALIZATION,
        description="Default materialization strategy",
    )

    # Performance settings
    pool_min_size: PositiveInt = Field(
        default=DBTOracleAdapterConstants.DEFAULT_POOL_MIN_SIZE,
        description="Connection pool minimum size",
    )
    pool_max_size: PositiveInt = Field(
        default=DBTOracleAdapterConstants.DEFAULT_POOL_MAX_SIZE,
        description="Connection pool maximum size",
    )
    query_timeout: TimeoutSeconds = Field(
        default=DBTOracleAdapterConstants.DEFAULT_QUERY_TIMEOUT,
        description="Query timeout in seconds",
    )

    # Logging
    log_level: str = Field(
        default=LogLevels.INFO,
        description="Default log level",
    )

    # Model configuration for environment variables
    model_config = ConfigDict(
        env_prefix="DBT_ORACLE_",
        env_file=".env",
        case_sensitive=False,
    )

    def to_dbt_config(self) -> DBTOracleConfig:
        """Convert settings to DBTOracleConfig.

        Returns:
            DBTOracleConfig instance with environment values

        """
        return DBTOracleConfig(
            host=self.oracle_host,
            port=self.oracle_port,
            service_name=self.oracle_service_name,
            sid=self.oracle_sid,
            username=self.oracle_username,
            password=self.oracle_password,
            protocol=self.oracle_protocol,
            database=self.database,
            schema=self.schema,
            materialization=self.materialization,
            pool_min_size=self.pool_min_size,
            pool_max_size=self.pool_max_size,
            query_timeout=self.query_timeout,
            log_level=self.log_level,
            project_name=self.project_name,
            project_version=self.project_version,
            environment=self.environment,
        )


class DBTOracleConfig(BaseConfig):
    """Configuration for the DBT Oracle Adapter with comprehensive validation.

    Supports Oracle connection configuration and DBT-specific settings with
    enterprise-grade configuration management, validation, secrets handling,
    and environment variable integration.
    """

    # Project identification using flext-core patterns
    project_name: str = Field(
        default="flext-data.dbt.flext-dbt-oracle",
        description="Project name",
    )
    project_version: str = Field(
        default=FlextFramework.VERSION,
        description="Project version",
    )
    environment: str = Field(
        default=Environments.DEVELOPMENT,
        description="Environment name",
    )

    # Oracle Database connection using flext-core types
    host: NonEmptyStr | None = Field(
        default=None,
        description="Oracle database host",
    )
    port: Port = Field(
        default=DBTOracleAdapterConstants.DEFAULT_PORT,
        description="Oracle database port",
    )
    service_name: NonEmptyStr | None = Field(
        default=DBTOracleAdapterConstants.DEFAULT_SERVICE_NAME,
        description="Oracle service name",
    )
    sid: NonEmptyStr | None = Field(
        default=None,
        description="Oracle SID (alternative to service_name)",
    )
    username: NonEmptyStr | None = Field(
        default=None,
        description="Oracle username",
    )
    password: NonEmptyStr | None = Field(
        default=None,
        description="Oracle password",
    )
    protocol: NonEmptyStr = Field(
        default=DBTOracleAdapterConstants.DEFAULT_PROTOCOL,
        description="Oracle protocol (tcp or tcps)",
    )

    # DBT-specific configuration using flext-core types
    database: NonEmptyStr = Field(
        default=DBTOracleAdapterConstants.DEFAULT_DATABASE,
        description="DBT database identifier",
    )
    schema: NonEmptyStr = Field(
        default=DBTOracleAdapterConstants.DEFAULT_SCHEMA,
        description="DBT default schema",
    )
    materialization: str = Field(
        default=DBTOracleAdapterConstants.DEFAULT_MATERIALIZATION,
        description="Default materialization strategy",
        pattern="^(table|view|incremental|snapshot)$",
    )

    # Connection pool configuration using flext-core types and constants
    pool_min_size: PositiveInt = Field(
        default=DBTOracleAdapterConstants.DEFAULT_POOL_MIN_SIZE,
        description="Connection pool minimum size",
        le=DBTOracleAdapterConstants.MAX_POOL_SIZE,
    )
    pool_max_size: PositiveInt = Field(
        default=DBTOracleAdapterConstants.DEFAULT_POOL_MAX_SIZE,
        description="Connection pool maximum size",
        le=DBTOracleAdapterConstants.MAX_POOL_SIZE,
    )
    pool_increment: PositiveInt = Field(
        default=DBTOracleAdapterConstants.DEFAULT_POOL_INCREMENT,
        description="Connection pool increment",
        le=DBTOracleAdapterConstants.MAX_POOL_INCREMENT,
    )
    query_timeout: TimeoutSeconds = Field(
        default=DBTOracleAdapterConstants.DEFAULT_QUERY_TIMEOUT,
        description="Query timeout in seconds",
        le=DBTOracleAdapterConstants.MAX_TIMEOUT,
    )
    fetch_size: PositiveInt = Field(
        default=DBTOracleAdapterConstants.DEFAULT_FETCH_SIZE,
        description="Default fetch size for queries",
    )
    connect_timeout: TimeoutSeconds = Field(
        default=DBTOracleAdapterConstants.DEFAULT_CONNECT_TIMEOUT,
        description="Connection timeout in seconds",
    )
    retry_attempts: PositiveInt = Field(
        default=DBTOracleAdapterConstants.DEFAULT_RETRY_ATTEMPTS,
        description="Number of retry attempts",
    )
    retry_delay: float = Field(
        default=DBTOracleAdapterConstants.DEFAULT_RETRY_DELAY,
        description="Retry delay in seconds",
        ge=0.1,
        le=10.0,
    )

    # Oracle-specific settings
    ssl_server_dn_match: bool = Field(
        default=DBTOracleAdapterConstants.DEFAULT_SSL_SERVER_DN_MATCH,
        description="Verify SSL server DN for secure connections",
    )
    nls_lang: NonEmptyStr | None = Field(
        default=None,
        description="Oracle NLS_LANG setting",
    )
    nls_date_format: NonEmptyStr = Field(
        default=DBTOracleAdapterConstants.DEFAULT_NLS_DATE_FORMAT,
        description="Oracle NLS_DATE_FORMAT setting",
    )
    search_path: NonEmptyStr | None = Field(
        default=None,
        description="DBT search path for schemas",
    )

    # Advanced configuration
    enable_metrics: bool = Field(
        default=True,
        description="Enable detailed metrics collection",
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

    # Configuration inherits from BaseConfig but customizes prefix
    model_config = ConfigDict(
        env_prefix="DBT_ORACLE_",
        case_sensitive=False,
        extra="forbid",  # Prevent unknown configuration keys
    )

    @field_validator("materialization")
    @classmethod
    def validate_materialization(cls, v: str) -> str:
        """Validate materialization strategy using constants."""
        if v not in DBTOracleAdapterConstants.VALID_MATERIALIZATIONS:
            msg = (
                f"Invalid materialization: {v}. Must be one of "
                f"{DBTOracleAdapterConstants.VALID_MATERIALIZATIONS}"
            )
            raise ValueError(msg)
        return v

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v: str) -> str:
        """Validate protocol using constants."""
        if v not in DBTOracleAdapterConstants.VALID_PROTOCOLS:
            msg = (
                f"Invalid protocol: {v}. Must be one of "
                f"{DBTOracleAdapterConstants.VALID_PROTOCOLS}"
            )
            raise ValueError(msg)
        return v

    @field_validator("host")
    @classmethod
    def validate_host_required(cls, v: str | None) -> str | None:
        """Validate host is provided."""
        if not v:
            msg = "Host is required"
            raise ValueError(msg)
        return v

    @field_validator("service_name")
    @classmethod
    def validate_service_name_or_sid(
        cls,
        v: str | None,
        info: ValidationInfo,
    ) -> str | None:
        """Validate either service_name or sid is provided."""
        if info.data:
            sid = info.data.get("sid")
            if not v and not sid:
                # Provide default service name for DBT
                return DBTOracleAdapterConstants.DEFAULT_SERVICE_NAME
        return v

    @field_validator("username")
    @classmethod
    def validate_username_required(cls, v: str | None) -> str | None:
        """Validate username is provided."""
        if not v:
            msg = "Username is required"
            raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def validate_password_required(cls, v: str | None) -> str | None:
        """Validate password is provided."""
        if not v:
            msg = "Password is required"
            raise ValueError(msg)
        return v

    @field_validator("pool_max_size")
    @classmethod
    def validate_pool_sizes(cls, v: int, info: ValidationInfo) -> int:
        """Validate pool max size is greater than min size."""
        if info.data:
            min_size = info.data.get("pool_min_size", 1)
            if v < min_size:
                msg = f"Pool max size ({v}) must be greater than min size ({min_size})"
                raise ValueError(
                    msg,
                )
        return v

    def get_connection_string(self) -> str:
        """Generate Oracle connection string for logging/display purposes.

        Returns:
            Connection string with masked password

        """
        if self.service_name:
            return f"oracle://{self.username}:***@{self.host}:{self.port}/{self.service_name}"
        return f"oracle://{self.username}:***@{self.host}:{self.port}:{self.sid}"

    def get_effective_schema(self) -> str:
        """Get the effective schema name.

        Returns:
            DBT schema name

        """
        return self.schema

    def get_database_identifier(self) -> str:
        """Get database identifier for flext-infrastructure.databases.flext-db-oracle.

        Returns:
            Database identifier (service_name, sid, or default)

        """
        return self.service_name or self.sid or "ORCL"

    def to_connection_config(self) -> dict[str, Any]:
        """Convert to connection configuration for flext-infrastructure.databases.flext-db-oracle.

        Convert to connection configuration for
        flext-infrastructure.databases.flext-db-oracle.

        Returns:
            Dictionary suitable for OracleConnection configuration

        """
        return {
            "host": self.host,
            "port": self.port,
            "service_name": self.service_name,
            "sid": self.sid,
            "username": self.username,
            "password": self.password,
            "protocol": self.protocol,
        }

    def to_oracle_config(self) -> OracleConfig:
        """Convert to modern flext-infrastructure.databases.flext-db-oracle OracleConfig.

        Convert to modern flext-infrastructure.databases.flext-db-oracle
        OracleConfig.

        Returns:
            OracleConfig instance with proper parameterization for DBT operations

        """
        return OracleConfig(
            host=self.host or "localhost",
            port=self.port,
            service_name=self.service_name,
            sid=self.sid,
            username=self.username or "oracle",
            password=self.password or "oracle",
            protocol=self.protocol,
            # Performance settings optimized for DBT analytical workloads
            pool_min_size=self.pool_min_size,
            pool_max_size=self.pool_max_size,
            pool_increment=self.pool_increment,
            query_timeout=int(self.query_timeout),
            fetch_size=self.fetch_size,
            connect_timeout=int(self.connect_timeout),
            retry_attempts=self.retry_attempts,
            retry_delay=self.retry_delay,
        )

    def get_performance_settings(self) -> dict[str, Any]:
        """Get performance-related settings.

        Returns:
            Dictionary of performance configuration

        """
        return {
            "pool_min_size": self.pool_min_size,
            "pool_max_size": self.pool_max_size,
            "pool_increment": self.pool_increment,
            "query_timeout": self.query_timeout,
            "fetch_size": self.fetch_size,
            "connect_timeout": self.connect_timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
        }

    def get_dbt_settings(self) -> dict[str, Any]:
        """Get DBT-specific settings.

        Returns:
            Dictionary of DBT configuration

        """
        return {
            "database": self.database,
            "schema": self.schema,
            "materialization": self.materialization,
            "search_path": self.search_path,
            "nls_lang": self.nls_lang,
            "nls_date_format": self.nls_date_format,
        }

    def validate_configuration(self) -> bool:
        """Perform comprehensive configuration validation for DBT Oracle Adapter.

        Returns:
            True if configuration is valid and complete

        Raises:
            ValueError: If configuration is invalid

        """
        try:
            # This will trigger all field validators
            self.__class__(**self.dict())

            # Validate DBT Oracle Adapter configuration completeness
            if not all([self.host, self.username, self.password]):
                self._raise_config_incomplete_error()

            # Validate either service_name or sid is provided
            if not self.service_name and not self.sid:
                # This is handled by the validator, but double-check
                self.service_name = DBTOracleAdapterConstants.DEFAULT_SERVICE_NAME

        except Exception:
            logger.exception("Configuration validation failed")
            raise
        else:
            logger.info("DBT Oracle Adapter configuration validation successful")
            return True

    def _raise_config_incomplete_error(self) -> None:
        """Raise error for incomplete DBT Oracle Adapter configuration."""
        msg = (
            "DBT Oracle Adapter configuration incomplete: host, username, and "
            "password are required"
        )
        raise ValueError(msg)


class OracleCredentialsConfig(DBTOracleConfig):
    """Configuration specifically for DBT credentials with additional validation.

    Extends DBTOracleConfig with DBT-specific credential requirements
    and compatibility features for the DBT framework.
    """

    # Additional DBT-required fields that may not be in base config
    type: str = Field(
        default="oracle",
        description="DBT adapter type",
        pattern="^oracle$",
    )

    # DBT credential aliases for compatibility
    _ALIASES: ClassVar[dict[str, str]] = {
        "dbname": "database",
        "pass": "password",
        "user": "username",
    }

    @property
    def unique_field(self) -> str:
        """Return unique identifier for connection.

        Returns:
            Host as unique identifier

        """
        return self.host or "unknown"

    def connection_keys(self) -> set[str]:
        """Return keys used for connection pooling.

        Returns:
            Set of keys that identify unique connections

        """
        return {
            "host",
            "port",
            "username",
            "password",
            "service_name",
            "sid",
            "protocol",
            "schema",
        }
