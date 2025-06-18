"""Centralized constants to eliminate ALL duplication - ZERO TOLERANCE COMPLIANT."""

# HTTP and API constants
APPLICATION_JSON = "application/json"
CONTENT_TYPE = "Content-Type"
ACCEPT = "Accept"
AUTHORIZATION = "Authorization"

# Default values
DEFAULT_API_VERSION = "v1"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_PAGE_SIZE = 100
DEFAULT_RATE_LIMIT_CALLS = 100
DEFAULT_RATE_LIMIT_PERIOD = 60

# Status values
STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "INACTIVE"
STATUS_ERROR = "ERROR"

# Common field names
FIELD_DESCRIPTION = "description"
FIELD_IDENTIFIER = "identifier"
FIELD_NAME = "name"
FIELD_VERSION = "version"
FIELD_STATUS = "status"
FIELD_ENTITY_NAME = "entityName"
FIELD_ENTITY_TYPE = "entityType"
FIELD_API_VERSION = "apiVersion"
FIELD_OIC_INSTANCE_ID = "oicInstanceId"
FIELD_INTEGRATION_ID = "integration_id"
FIELD_HTTP_METHOD = "http_method"
FIELD_INTEGRATIONS_COUNT = "integrationsCount"

# Common descriptions
DESC_INTEGRATION_ID = "Integration ID"
DESC_CONNECTION_ID = "Connection ID"
DESC_ENTITY_NAME = "Entity name"
DESC_ENTITY_TYPE = "Entity type"

# HTTP methods
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"

# OAuth and JWT constants
JWT_SCOPE_DEFAULT = "urn:opc:resource:consumer::all"
OAUTH2_TOKEN_PATH = "/oauth2/v1/token"
DEFAULT_TOKEN_CACHE_TTL = 3600  # 1 hour in seconds

# OIC specific constants
OIC_API_BASE = "/ic/api/integration/v1"
OIC_INTEGRATIONS_PATH = "/integrations"
OIC_CONNECTIONS_PATH = "/connections"
OIC_MONITORING_PATH = "/monitoring"
OIC_PACKAGES_PATH = "/packages"

# OIC v3 monitoring endpoints (according to official documentation)
OIC_MONITORING_INSTANCES_PATH = "/monitoring/instances"
OIC_MONITORING_ERRORS_PATH = "/monitoring/errors"
OIC_MONITORING_HISTORY_PATH = "/monitoring/history"
OIC_MONITORING_INTEGRATIONS_PATH = "/monitoring/integrations"
OIC_MONITORING_AGENTGROUPS_PATH = "/monitoring/agentgroups"

# OIC system and management endpoints
OIC_SYSTEM_PATH = "/system"
OIC_HEALTH_PATH = "/health"
OIC_METADATA_PATH = "/metadata"

# Error messages
ERROR_404_NOT_FOUND = "404"
ERROR_500_SERVER = "500"
ERROR_CONNECTION = "connection"
ERROR_NETWORK = "Network error"
ERROR_HTTP_500 = "HTTP 500 error"

# Common query parameters
PARAM_LIMIT = "limit"
PARAM_OFFSET = "offset"
PARAM_STATUS = "status"
PARAM_TYPE = "type"
PARAM_INTEGRATION_INSTANCE = "integrationInstance"

# Test constants
TEST_CLIENT_ID = "test_client_id"
TEST_CLIENT_SECRET = "test_client_secret"
TEST_INSTANCE_ID = "test_instance"
TEST_INTEGRATION_NAME = "Test Integration"
TEST_INTEGRATION_DESC = "Test description"
TEST_INTEGRATION_ID = "integration1"
TEST_CONNECTION_ID = "connection1"
TEST_REGION_ASHBURN = "us-ashburn-1"
TEST_REGION_PHOENIX = "us-phoenix-1"

# Environment types
ENV_DEV = "dev"
ENV_TEST = "test"
ENV_PROD = "prod"

# Common responses
RESPONSE_DATA = "data"
RESPONSE_ITEMS = "items"
RESPONSE_STATUS = "status"
RESPONSE_HEALTHY = "healthy"

__all__ = [
    "ACCEPT",
    # HTTP constants
    "APPLICATION_JSON",
    "AUTHORIZATION",
    "CONTENT_TYPE",
    # Defaults
    "DEFAULT_API_VERSION",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_RATE_LIMIT_CALLS",
    "DEFAULT_RATE_LIMIT_PERIOD",
    "DEFAULT_TIMEOUT",
    "DEFAULT_TOKEN_CACHE_TTL",
    "DESC_CONNECTION_ID",
    "DESC_ENTITY_NAME",
    "DESC_ENTITY_TYPE",
    # Descriptions
    "DESC_INTEGRATION_ID",
    # Environments
    "ENV_DEV",
    "ENV_PROD",
    "ENV_TEST",
    # Errors
    "ERROR_404_NOT_FOUND",
    "ERROR_500_SERVER",
    "ERROR_CONNECTION",
    "ERROR_HTTP_500",
    "ERROR_NETWORK",
    "FIELD_API_VERSION",
    # Fields
    "FIELD_DESCRIPTION",
    "FIELD_ENTITY_NAME",
    "FIELD_ENTITY_TYPE",
    "FIELD_HTTP_METHOD",
    "FIELD_IDENTIFIER",
    "FIELD_INTEGRATIONS_COUNT",
    "FIELD_INTEGRATION_ID",
    "FIELD_NAME",
    "FIELD_OIC_INSTANCE_ID",
    "FIELD_STATUS",
    "FIELD_VERSION",
    "HTTP_DELETE",
    # HTTP methods
    "HTTP_GET",
    "HTTP_POST",
    "HTTP_PUT",
    # JWT/OAuth
    "JWT_SCOPE_DEFAULT",
    "OAUTH2_TOKEN_PATH",
    # OIC paths
    "OIC_API_BASE",
    "OIC_CONNECTIONS_PATH",
    "OIC_HEALTH_PATH",
    "OIC_INTEGRATIONS_PATH",
    "OIC_METADATA_PATH",
    "OIC_MONITORING_AGENTGROUPS_PATH",
    "OIC_MONITORING_ERRORS_PATH",
    "OIC_MONITORING_HISTORY_PATH",
    # OIC v3 monitoring paths
    "OIC_MONITORING_INSTANCES_PATH",
    "OIC_MONITORING_INTEGRATIONS_PATH",
    "OIC_MONITORING_PATH",
    "OIC_PACKAGES_PATH",
    # OIC system paths
    "OIC_SYSTEM_PATH",
    "PARAM_INTEGRATION_INSTANCE",
    # Parameters
    "PARAM_LIMIT",
    "PARAM_OFFSET",
    "PARAM_STATUS",
    "PARAM_TYPE",
    # Responses
    "RESPONSE_DATA",
    "RESPONSE_HEALTHY",
    "RESPONSE_ITEMS",
    "RESPONSE_STATUS",
    # Status
    "STATUS_ACTIVE",
    "STATUS_ERROR",
    "STATUS_INACTIVE",
    # Test constants
    "TEST_CLIENT_ID",
    "TEST_CLIENT_SECRET",
    "TEST_CONNECTION_ID",
    "TEST_INSTANCE_ID",
    "TEST_INTEGRATION_DESC",
    "TEST_INTEGRATION_ID",
    "TEST_INTEGRATION_NAME",
    "TEST_REGION_ASHBURN",
    "TEST_REGION_PHOENIX",
]
