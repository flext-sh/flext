"""Test constants for FLEXT ecosystem.

Organized constants for testing various components, using namespaces for maximum reusability.
Structured by domain with cross-cutting constants for common test scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar


class TestConstants:
    """Centralized test constants organized by domain with maximum reusability."""

    # =========================================================================
    # CROSS-CUTTING CONSTANTS - Reusable across all domains
    # =========================================================================

    class Common:
        """Common constants used across all test domains."""

        # Status and State
        STATUS_OPERATIONAL = "operational"
        STATUS_ACTIVE = "active"
        STATUS_INACTIVE = "inactive"
        STATUS_PENDING = "pending"
        STATUS_COMPLETED = "completed"
        STATUS_FAILED = "failed"

        # Generic Identifiers
        ID_DEFAULT = "default_123"
        ID_TEST = "test_123"
        ID_INVALID = "invalid_id"

        # Generic Names
        NAME_DEFAULT = "Default Name"
        NAME_TEST = "Test Name"
        NAME_EMPTY = ""
        NAME_UNICODE = "测试名称 🚀"

        # Generic Values
        VALUE_DEFAULT = "default_value"
        VALUE_EMPTY = ""
        VALUE_NULL: object | None = None
        VALUE_TRUE = True
        VALUE_FALSE = False
        VALUE_ZERO = 0
        VALUE_NEGATIVE = -1
        VALUE_LARGE = 999999

        # Paths and URLs
        PATH_ROOT = "/"
        PATH_TEST = "/test"
        PATH_INVALID = "/invalid/path"
        URL_HTTP = "http://example.com"
        URL_HTTPS = "https://example.com"
        URL_INVALID = "not-a-url"

        # Time and Duration
        TIMEOUT_DEFAULT = 30
        TIMEOUT_ZERO = 0
        TIMEOUT_NEGATIVE = -1
        DURATION_SHORT = 1
        DURATION_LONG = 3600

        # Sizes and Limits
        SIZE_ZERO = 0
        SIZE_SMALL = 10
        SIZE_MEDIUM = 100
        SIZE_LARGE = 1000
        SIZE_HUGE = 10000

        # Generic Collections
        LIST_EMPTY: ClassVar[list[object]] = []
        LIST_SINGLE: ClassVar[list[str]] = ["item"]
        LIST_MULTIPLE: ClassVar[list[str]] = ["item1", "item2", "item3"]
        DICT_EMPTY: ClassVar[dict[str, object]] = {}
        DICT_SINGLE: ClassVar[dict[str, str]] = {"key": "value"}
        DICT_MULTIPLE: ClassVar[dict[str, str]] = {"key1": "value1", "key2": "value2"}

    class GenericData:
        """Generic test data structures."""

        # User-like data
        USER_DATA: ClassVar[dict[str, object]] = {
            "id": "default_123",
            "name": "Default Name",
            "email": "user@example.com",
            "active": True,
        }

        # Configuration data
        CONFIG_DATA: ClassVar[dict[str, object]] = {
            "debug": True,
            "timeout": 30,
            "enabled": True,
        }

        # API response data
        API_RESPONSE_SUCCESS: ClassVar[dict[str, object]] = {
            "status": "success",
            "data": {"key": "value"},
            "message": "Operation successful",
        }

        API_RESPONSE_ERROR: ClassVar[dict[str, object]] = {
            "status": "error",
            "error": "Operation failed",
            "message": "An error occurred",
        }

    # =========================================================================
    # CLI DOMAIN CONSTANTS
    # =========================================================================

    class Cli:
        """CLI-specific constants and data."""

        # Service information
        SERVICE_NAME = "flext-cli"
        SERVICE_STATUS = "operational"
        SERVICE_VERSION = "1.0.0"

        # Component status
        COMPONENT_AVAILABLE = "available"
        COMPONENT_UNAVAILABLE = "unavailable"
        COMPONENT_COUNT = 4  # config, formatters, core, prompts

        # Field names
        STATUS = "status"
        SERVICE = "service"
        TIMESTAMP = "timestamp"
        VERSION = "version"
        COMPONENTS = "components"

        # Command data
        COMMAND_TEST = "test_command"
        COMMAND_ARGS: ClassVar[list[str]] = ["arg1", "arg2"]
        COMMAND_OPTIONS: ClassVar[dict[str, object]] = {
            "verbose": True,
            "output": "json",
        }

        # Configuration paths
        CONFIG_PATH = "/tmp/test_config.json"
        CONFIG_INVALID_PATH = "/invalid/config/path"

    class CliPrompts:
        """Constants for CLI prompts testing."""

        # Messages
        TEST_MESSAGE = "Test message"
        CONFIRM_MESSAGE = "Continue?"
        EMPTY_MESSAGE = ""
        LONG_MESSAGE = "This is a very long test message to test edge cases"

        # Defaults
        DEFAULT_TRUE = True
        DEFAULT_FALSE = False
        DEFAULT_STRING = "default_value"
        DEFAULT_EMPTY = ""

        # Status types
        STATUS_INFO = "info"
        STATUS_SUCCESS = "success"
        STATUS_WARNING = "warning"
        STATUS_ERROR = "error"
        STATUS_CUSTOM = "custom"

        # Progress descriptions
        PROGRESS_DESC = "Processing items"
        PROGRESS_EMPTY = ""
        PROGRESS_LONG = "Very long progress description for testing"

        # Input values
        INPUT_YES = "y"
        INPUT_YES_CAPS = "YES"
        INPUT_NO = "n"
        INPUT_INVALID = "maybe"
        INPUT_EMPTY = ""
        INPUT_WHITESPACE = "   "
        INPUT_VALID = "user_input"
        INPUT_NUMERIC = "123"
        INPUT_SPECIAL = "!@#$%"

        # Error messages
        ERROR_DEFAULT_MISMATCH = "Default value mismatch"
        ERROR_EMPTY_NOT_ALLOWED = "Empty input is not allowed"
        ERROR_INVALID_CHOICE = "Invalid choice"
        ERROR_USER_CANCELLED = "User cancelled"
        ERROR_INPUT_ENDED = "Input stream ended"
        ERROR_GENERAL = "Test error"

        # Validation patterns
        PATTERN_EMAIL = r"^[^@]+@[^@]+\.[^@]+$"
        PATTERN_NUMERIC = r"^\d+$"
        PATTERN_ALPHANUMERIC = r"^[a-zA-Z0-9]+$"

        # Choices
        CHOICES_SIMPLE: ClassVar[list[str]] = ["option1", "option2", "option3"]
        CHOICES_EMPTY: ClassVar[list[str]] = []
        CHOICES_SINGLE: ClassVar[list[str]] = ["single"]
        CHOICES_DUPLICATE: ClassVar[list[str]] = ["same", "same", "different"]

        # Passwords
        PASSWORD_VALID = "validpassword123"
        PASSWORD_SHORT = "short"
        PASSWORD_EMPTY = ""

        # Statistics
        STATS_PROMPTS_EXECUTED = 5
        STATS_INTERACTIVE_TRUE = True
        STATS_TIMEOUT = 30

    # =========================================================================
    # API DOMAIN CONSTANTS
    # =========================================================================

    class Api:
        """API-specific constants and test data."""

        # URLs and endpoints
        BASE_URL = "https://example.com"
        ENDPOINT_TEST = "/test"
        ENDPOINT_INVALID = "/invalid"
        ENDPOINT_USERS = "/users"
        ENDPOINT_CONFIG = "/config"

        # HTTP methods
        METHOD_GET = "GET"
        METHOD_POST = "POST"
        METHOD_PUT = "PUT"
        METHOD_DELETE = "DELETE"
        METHOD_PATCH = "PATCH"

        # HTTP status codes
        STATUS_OK = 200
        STATUS_CREATED = 201
        STATUS_BAD_REQUEST = 400
        STATUS_UNAUTHORIZED = 401
        STATUS_NOT_FOUND = 404
        STATUS_INTERNAL_ERROR = 500

        # Content types
        CONTENT_TYPE_JSON = "application/json"
        CONTENT_TYPE_XML = "application/xml"
        CONTENT_TYPE_TEXT = "text/plain"

        # Headers
        HEADER_AUTH = "Authorization"
        HEADER_CONTENT_TYPE = "Content-Type"
        HEADER_USER_AGENT = "User-Agent"

        # Request/Response data
        REQUEST_DATA: ClassVar[dict[str, object]] = {
            "method": METHOD_GET,
            "url": ENDPOINT_TEST,
            "headers": {HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON},
            "data": {"key": "value"},
        }

        RESPONSE_SUCCESS: ClassVar[dict[str, object]] = {
            "status_code": STATUS_OK,
            "data": {"key": "value"},
            "headers": {HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON},
        }

        RESPONSE_ERROR: ClassVar[dict[str, object]] = {
            "status_code": STATUS_BAD_REQUEST,
            "error": "Bad Request",
            "message": "Invalid request data",
        }

    # =========================================================================
    # DATABASE DOMAIN CONSTANTS
    # =========================================================================

    class Database:
        """Database-specific constants and test data."""

        # Connection parameters
        HOST_DEFAULT = "localhost"
        PORT_DEFAULT = 5432
        USER_DEFAULT = "testuser"
        PASSWORD_DEFAULT = "testpass"
        DATABASE_DEFAULT = "testdb"

        # Connection strings
        CONNECTION_STRING_POSTGRES = f"postgresql://{USER_DEFAULT}:{PASSWORD_DEFAULT}@{HOST_DEFAULT}:{PORT_DEFAULT}/{DATABASE_DEFAULT}"
        CONNECTION_STRING_MYSQL = f"mysql://{USER_DEFAULT}:{PASSWORD_DEFAULT}@{HOST_DEFAULT}:{PORT_DEFAULT}/{DATABASE_DEFAULT}"
        CONNECTION_STRING_INVALID = "invalid://connection:string"

        # Table/Collection names
        TABLE_USERS = "users"
        TABLE_CONFIG = "config"
        TABLE_LOGS = "logs"

        # Query types
        QUERY_SELECT = "SELECT"
        QUERY_INSERT = "INSERT"
        QUERY_UPDATE = "UPDATE"
        QUERY_DELETE = "DELETE"

        # Sample data
        USER_RECORD: ClassVar[dict[str, object]] = {
            "id": "default_123",
            "name": "Default Name",
            "email": "user@example.com",
            "active": True,
            "created_at": "2023-01-01T00:00:00Z",
        }

        CONFIG_RECORD: ClassVar[dict[str, object]] = {
            "key": "test_key",
            "value": "default_value",
            "type": "string",
        }

    class ResultValues:
        """Common result values for testing."""

        SUCCESS_DATA_DICT: ClassVar[dict[str, str]] = {"key": "value"}
        SUCCESS_DATA_STRING = "success"
        SUCCESS_DATA_INT = 42
        SUCCESS_DATA_BOOL_TRUE = True
        SUCCESS_DATA_BOOL_FALSE = False
        SUCCESS_DATA_LIST: ClassVar[list[int]] = [1, 2, 3]
        SUCCESS_DATA_NONE_INVALID: ClassVar[object | None] = None  # Invalid for success

        ERROR_MESSAGE = "Test error message"
        ERROR_CODE = "TEST_ERROR"

    class EdgeCases:
        """Edge case constants."""

        MAX_LENGTH_MESSAGE = "A" * 1000
        MIN_LENGTH_MESSAGE = ""
        UNICODE_MESSAGE = "测试消息 🚀"
        SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        VERY_LONG_DEFAULT = "A" * 500
        VERY_SHORT_DEFAULT = "x"

        LARGE_CHOICES: ClassVar[list[str]] = [f"option_{i}" for i in range(100)]
        EMPTY_CHOICES: ClassVar[list[str]] = []

    class ValidationData:
        """Validation test data."""

        VALID_EMAILS: ClassVar[list[str]] = [
            "test@example.com",
            "user.name+tag@domain.co.uk",
        ]
        INVALID_EMAILS: ClassVar[list[str]] = [
            "invalid",
            "no-at-sign.com",
            "@internal.invalid",
            "",
        ]

        VALID_HOSTNAMES: ClassVar[list[str]] = [
            "example.com",
            "localhost",
            "sub.domain.org",
        ]
        INVALID_HOSTNAMES: ClassVar[list[str]] = [
            "invalid..hostname",
            ".starts.with.dot",
            "",
        ]

        VALID_NUMBERS: ClassVar[list[str]] = ["123", "0", "-456"]
        INVALID_NUMBERS: ClassVar[list[str]] = ["abc", "12.34", ""]

    # =========================================================================
    # FACTORY METHODS - Generate test cases from constants
    # =========================================================================

    @classmethod
    def get_prompt_test_cases(cls) -> list[dict[str, object]]:
        """Get comprehensive prompt test cases using organized constants."""
        return [
            {
                "message": cls.CliPrompts.TEST_MESSAGE,
                "default": cls.CliPrompts.DEFAULT_STRING,
                "expected_success": True,
                "expected_data": cls.CliPrompts.DEFAULT_STRING,
            },
            {
                "message": cls.CliPrompts.CONFIRM_MESSAGE,
                "default": cls.CliPrompts.DEFAULT_TRUE,
                "expected_success": True,
                "expected_data": cls.CliPrompts.DEFAULT_TRUE,
            },
            {
                "message": cls.CliPrompts.EMPTY_MESSAGE,
                "default": cls.CliPrompts.DEFAULT_EMPTY,
                "expected_success": True,
                "expected_data": cls.CliPrompts.DEFAULT_EMPTY,
            },
        ]

    @classmethod
    def get_cli_component_test_cases(cls) -> list[dict[str, object]]:
        """Get CLI component validation test cases."""
        return [
            {
                "component_name": "config",
                "expected_exists": True,
                "expected_type": object,  # Will be validated as not None
            },
            {
                "component_name": "core",
                "expected_exists": True,
                "expected_type": object,
            },
            {
                "component_name": "formatters",
                "expected_exists": True,
                "expected_type": object,
            },
            {
                "component_name": "prompts",
                "expected_exists": True,
                "expected_type": object,
            },
        ]

    @classmethod
    def get_api_endpoint_test_cases(cls) -> list[dict[str, object]]:
        """Get API endpoint test cases."""
        return [
            {
                "endpoint": cls.Api.ENDPOINT_TEST,
                "method": cls.Api.METHOD_GET,
                "expected_status": cls.Api.STATUS_OK,
            },
            {
                "endpoint": cls.Api.ENDPOINT_INVALID,
                "method": cls.Api.METHOD_GET,
                "expected_status": cls.Api.STATUS_NOT_FOUND,
            },
        ]

    @classmethod
    def get_database_connection_test_cases(cls) -> list[dict[str, object]]:
        """Get database connection test cases."""
        return [
            {
                "connection_string": cls.Database.CONNECTION_STRING_POSTGRES,
                "expected_valid": True,
            },
            {
                "connection_string": cls.Database.CONNECTION_STRING_INVALID,
                "expected_valid": False,
            },
        ]

    @classmethod
    def get_status_test_cases(cls) -> list[tuple[str, bool]]:
        """Get status test cases."""
        return [
            (cls.CliPrompts.STATUS_INFO, True),
            (cls.CliPrompts.STATUS_SUCCESS, True),
            (cls.CliPrompts.STATUS_WARNING, True),
            (cls.CliPrompts.STATUS_ERROR, True),
            (cls.CliPrompts.STATUS_CUSTOM, True),
        ]

    @classmethod
    def get_progress_test_cases(cls) -> list[tuple[str, object]]:
        """Get progress test cases."""
        return [
            (cls.CliPrompts.PROGRESS_DESC, cls.CliPrompts.PROGRESS_DESC),
            (cls.CliPrompts.PROGRESS_EMPTY, cls.CliPrompts.PROGRESS_EMPTY),
            (cls.CliPrompts.PROGRESS_LONG, cls.CliPrompts.PROGRESS_LONG),
        ]
