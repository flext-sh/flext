"""FLEXT Core Standards - Padronização Arquitetural Centralizada.

Este módulo centraliza todos os padrões arquiteturais do ecossistema FLEXT,
eliminando duplicação de código e garantindo consistência em todos os subprojetos.

PRINCÍPIOS DE PADRONIZAÇÃO:
1. Usar sempre FlextModel como base para modelos Pydantic
2. Usar FlextResult[T] para todas as operações que podem falhar
3. Imports diretos sem TYPE_CHECKING
4. Exportações centralizadas via __init__.py
5. Tipos centralizados no flext-core

Este arquivo serve como:
- Ponto central de refatoração
- Guia de migração para subprojetos
- Exemplo de padrões corretos
"""

from __future__ import annotations

from typing import Any, TypeVar

# Imports diretos do flext-core (sem TYPE_CHECKING)
from flext_core import (
    FlextConnectionError,
    FlextContainer,
    FlextEntity,
    FlextError,
    FlextModel,
    FlextResult,
    FlextValidationError,
    FlextValueObject,
    get_flext_container,
    get_logger,
)
from pydantic import ConfigDict, Field, field_validator

# Type variables centralizados
T = TypeVar("T")
TModel = TypeVar("TModel", bound=FlextModel)
TEntity = TypeVar("TEntity", bound=FlextEntity)
TValueObject = TypeVar("TValueObject", bound=FlextValueObject)

logger = get_logger(__name__)

# ============================================================================
# PADRÕES DE MODELOS CENTRALIZADOS
# ============================================================================


class FlextBaseConfigModel(FlextModel):
    """Modelo base para configurações usando padrões FLEXT."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        frozen=False,
    )


class FlextBaseEntityModel(FlextModel):
    """Modelo base para entidades usando padrões FLEXT."""

    id: str = Field(..., description="Entity unique identifier")
    created_at: str = Field(default_factory=lambda: "2025-01-01T00:00:00Z")
    updated_at: str = Field(default_factory=lambda: "2025-01-01T00:00:00Z")

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        use_enum_values=True,
    )


class FlextBaseValueObjectModel(FlextModel):
    """Modelo base para value objects usando padrões FLEXT."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,  # Value objects são imutáveis
        use_enum_values=True,
    )

# ============================================================================
# PADRÕES DE RESULT CENTRALIZADOS
# ============================================================================


class FlextStandardResult:
    """Padrões padronizados para FlextResult."""

    @staticmethod
    def success(data: T) -> FlextResult[T]:
        """Criar resultado de sucesso padronizado."""
        return FlextResult.ok(data)

    @staticmethod
    def failure(error_message: str, error_code: str | None = None) -> FlextResult[None]:
        """Criar resultado de falha padronizado."""
        return FlextResult.fail(error_message, error_code=error_code)

    @staticmethod
    def validation_error(field: str, message: str) -> FlextResult[None]:
        """Criar erro de validação padronizado."""
        return FlextResult.fail(f"Validation error in {field}: {message}")

# ============================================================================
# PADRÕES DE SERVICE CENTRALIZADOS
# ============================================================================


class FlextBaseService:
    """Classe base para todos os serviços do ecossistema FLEXT."""

    def __init__(self, container: FlextContainer | None = None) -> None:
        """Inicializar serviço com container de DI."""
        self.container = container or get_flext_container()
        self.logger = get_logger(self.__class__.__name__)

    def _handle_error(self, error: Exception, operation: str) -> FlextResult[None]:
        """Tratar erros de forma padronizada."""
        self.logger.error(f"Error in {operation}: {error}")
        return FlextResult.fail(f"Operation {operation} failed: {error!s}")

# ============================================================================
# PADRÕES DE CONFIGURAÇÃO CENTRALIZADOS
# ============================================================================


class FlextBaseConfig(FlextBaseConfigModel):
    """Configuração base padronizada para todos os subprojetos."""

    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of {valid_levels}"
            raise ValueError(msg)
        return v.upper()

# ============================================================================
# PADRÕES DE EXCEPTION CENTRALIZADOS
# ============================================================================


class FlextStandardErrors:
    """Padrões de erro padronizados para todo o ecossistema."""

    @staticmethod
    def configuration_error(message: str) -> FlextError:
        """Erro de configuração padronizado."""
        return FlextError(f"Configuration error: {message}")

    @staticmethod
    def validation_error(field: str, value: Any, expected: str) -> FlextValidationError:
        """Erro de validação padronizado."""
        return FlextValidationError(
            f"Validation failed for field '{field}': got {value}, expected {expected}"
        )

    @staticmethod
    def connection_error(service: str, details: str) -> FlextConnectionError:
        """Erro de conexão padronizado."""
        return FlextConnectionError(f"Connection to {service} failed: {details}")

# ============================================================================
# PADRÕES DE MIGRATION PARA LEGACY
# ============================================================================


class FlextLegacyCompat:
    """Compatibilidade com código legado durante migração."""

    @staticmethod
    def migrate_dict_to_model(data: dict[str, Any], model_class: type[TModel]) -> FlextResult[TModel]:
        """Migrar dict para modelo Pydantic de forma segura."""
        try:
            model = model_class(**data)
            return FlextResult.ok(model)
        except Exception as e:
            return FlextResult.fail(f"Failed to migrate dict to {model_class.__name__}: {e}")

    @staticmethod
    def handle_legacy_import(
        legacy_import_path: str,
        new_import_path: str,
        deprecation_message: str
    ) -> None:
        """Tratar imports legados com warnings."""
        import warnings
        warnings.warn(
            f"Import from {legacy_import_path} is deprecated. "
            f"Use {new_import_path} instead. {deprecation_message}",
            DeprecationWarning,
            stacklevel=3
        )

# ============================================================================
# EXAMPLE USAGE PATTERNS
# ============================================================================

# Exemplo de uso correto dos padrões:


class ExampleUserConfig(FlextBaseConfig):
    """Exemplo de configuração seguindo padrões FLEXT."""

    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=389, description="Server port")


class ExampleUserEntity(FlextBaseEntityModel):
    """Exemplo de entidade seguindo padrões FLEXT."""

    username: str = Field(..., description="User username")
    email: str = Field(..., description="User email")
    active: bool = Field(default=True, description="User is active")


class ExampleUserService(FlextBaseService):
    """Exemplo de serviço seguindo padrões FLEXT."""

    def create_user(self, username: str, email: str) -> FlextResult[ExampleUserEntity]:
        """Criar usuário seguindo padrões FLEXT."""
        try:
            if not username:
                return FlextStandardResult.validation_error("username", "Username is required")

            if not email or "@" not in email:
                return FlextStandardResult.validation_error("email", "Valid email is required")

            user = ExampleUserEntity(
                id=f"user_{username}",
                username=username,
                email=email
            )

            self.logger.info("User created successfully", username=username)
            return FlextStandardResult.success(user)

        except Exception as e:
            return self._handle_error(e, "create_user")

# ============================================================================
# EXPORT PATTERNS
# ============================================================================


__all__ = [
    # Examples
    "ExampleUserConfig",
    "ExampleUserEntity",
    "ExampleUserService",
    "FlextBaseConfig",
    # Base classes
    "FlextBaseConfigModel",
    "FlextBaseEntityModel",
    "FlextBaseService",
    "FlextBaseValueObjectModel",
    "FlextLegacyCompat",
    "FlextStandardErrors",
    # Utility classes
    "FlextStandardResult",
    # Type variables
    "T",
    "TEntity",
    "TModel",
    "TValueObject",
]
