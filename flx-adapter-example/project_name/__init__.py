"""
A Python client library template with API client, configuration, and CLI tools.

This template provides a foundation for building API client libraries with
features like dynamic configuration, robust error handling, and CLI tools.
"""

__version__ = "0.1.0"

# Import core components
from .client import ApiClient, FlxResponse
from .config import Config, ConfigProfile, load_config_from_env
from .entity import Entity, EntityManager
from .exceptions import (
    ApiError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    RequestError,
    ResponseError,
    ValidationError,
)
from .models import BaseModel
from .pagination import PagedResponse, PageInfo, PaginatedIterator, paginate
from .schema import SchemaDefinition, SchemaExtractor, SchemaManager
from .utils.formatting import format_csv, format_json, format_table, format_text

# Import utilities
from .utils.logging import get_logger, setup_logger
from .utils.validation import (
    validate_date,
    validate_email,
    validate_enum_field,
    validate_min_max,
    validate_required_fields,
    validate_url,
    validate_uuid,
)


# Public API
__all__ = [
    # Core components
    "ApiClient",
    # Exceptions
    "ApiError",
    "AuthenticationError",
    "BaseModel",
    "Config",
    "ConfigProfile",
    "ConfigurationError",
    "ConnectionError",
    # Entity management
    "Entity",
    "EntityManager",
    "FlxResponse",
    # Pagination
    "PageInfo",
    "PagedResponse",
    "PaginatedIterator",
    "RequestError",
    "ResponseError",
    # Schema management
    "SchemaDefinition",
    "SchemaExtractor",
    "SchemaManager",
    "ValidationError",
    "format_csv",
    # Formatting utilities
    "format_json",
    "format_table",
    "format_text",
    "get_logger",
    # Configuration
    "load_config_from_env",
    "paginate",
    # Logging utilities
    "setup_logger",
    "validate_date",
    "validate_email",
    "validate_enum_field",
    "validate_min_max",
    "validate_required_fields",
    # Validation utilities
    "validate_url",
    "validate_uuid",
]

# Version info
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"
