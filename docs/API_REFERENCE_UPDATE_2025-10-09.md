# FLEXT API Reference Update

**Generated:** 2025-10-09  
**Version:** 0.9.0  
**Status:** ✅ PRODUCTION READY

---

## 📊 API Overview

### Core Framework APIs

#### flext-core

**Foundation library providing core patterns and abstractions**

```python
from flext_core import (
    FlextResult,      # Railway-oriented error handling
    FlextContainer,   # Dependency injection container
    FlextModels,      # Unified domain models
    FlextLogger,      # Structured logging
    FlextConfig,      # Configuration management
)

# Railway-oriented programming
def process_data(data: dict) -> FlextResult[ProcessedData]:
    return (
        validate(data)
        .flat_map(transform)
        .map(enrich)
        .map_error(handle_error)
    )

# Dependency injection
container = FlextContainer.get_global()
container.register("database", DatabaseService())
db_result = container.get("database")
```

#### flext-api

**REST API framework with OpenAPI support**

```python
from flext_api import FlextApi, FlextApiModels

# API models
class UserRequest(FlextApiModels.Request):
    name: str
    email: str

class UserResponse(FlextApiModels.Response):
    user_id: str
    created_at: datetime

# API implementation
api = FlextApi()

@api.post("/users")
async def create_user(request: UserRequest) -> FlextResult[UserResponse]:
    return (
        validate_user_data(request)
        .flat_map(save_user)
        .map(format_response)
    )
```

#### flext-auth

**Authentication and authorization services**

```python
from flext_auth import FlextAuth, FlextAuthModels

# Auth models
class LoginRequest(FlextAuthModels.Request):
    username: str
    password: str

class TokenResponse(FlextAuthModels.Response):
    access_token: str
    refresh_token: str
    expires_in: int

# Auth implementation
auth = FlextAuth()

@auth.login
async def authenticate(request: LoginRequest) -> FlextResult[TokenResponse]:
    return (
        validate_credentials(request)
        .flat_map(generate_tokens)
        .map(format_token_response)
    )
```

### Data Integration APIs

#### flext-ldif

**RFC-compliant LDIF processing and migration**

```python
from flext_ldif import FlextLdif, FlextLdifModels

# LDIF models
class LdifEntry(FlextLdifModels.Entry):
    dn: str
    attributes: dict[str, FlextTypes.StringList]
    changetype: str = "add"

class LdifParseResult(FlextLdifModels.ParseResult):
    entries: list[LdifEntry]
    errors: FlextTypes.StringList

# LDIF processing
ldif = FlextLdif()

def parse_ldif_file(file_path: str) -> FlextResult[LdifParseResult]:
    return (
        read_file(file_path)
        .flat_map(ldif.parse)
        .map(validate_entries)
    )
```

#### flext-ldap

**LDAP client operations and management**

```python
from flext_ldap import FlextLdap, FlextLdapModels

# LDAP models
class LdapConnection(FlextLdapModels.Connection):
    host: str
    port: int
    bind_dn: str
    bind_password: str

class LdapSearchResult(FlextLdapModels.SearchResult):
    entries: list[dict[str, object]]
    total_count: int

# LDAP operations
ldap = FlextLdap()

def search_users(connection: LdapConnection) -> FlextResult[LdapSearchResult]:
    return (
        ldap.connect(connection)
        .flat_map(lambda conn: ldap.search(conn, "ou=users,dc=example,dc=com"))
        .map(format_search_results)
    )
```

#### flext-oracle

**Oracle database integration**

```python
from flext_oracle import FlextOracle, FlextOracleModels

# Oracle models
class OracleConnection(FlextOracleModels.Connection):
    host: str
    port: int
    service_name: str
    username: str
    password: str

class QueryResult(FlextOracleModels.QueryResult):
    rows: list[dict[str, object]]
    column_names: FlextTypes.StringList
    row_count: int

# Oracle operations
oracle = FlextOracle()

def execute_query(connection: OracleConnection, query: str) -> FlextResult[QueryResult]:
    return (
        oracle.connect(connection)
        .flat_map(lambda conn: oracle.execute(conn, query))
        .map(format_query_results)
    )
```

### Singer Platform APIs

#### Taps (Data Extraction)

**Extract data from various sources**

```python
from flext_tap_ldap import FlextTapLdap
from flext_tap_oracle import FlextTapOracle

# LDAP Tap
ldap_tap = FlextTapLdap()
ldap_tap.configure({
    "host": "ldap.example.com",
    "port": 389,
    "base_dn": "dc=example,dc=com"
})

# Oracle Tap
oracle_tap = FlextTapOracle()
oracle_tap.configure({
    "host": "oracle.example.com",
    "port": 1521,
    "service_name": "XE"
})

# Extract data
def extract_all_data() -> FlextResult[list[dict]]:
    return (
        ldap_tap.extract()
        .flat_map(lambda ldap_data: oracle_tap.extract().map(lambda oracle_data: ldap_data + oracle_data))
    )
```

#### Targets (Data Loading)

**Load data into various destinations**

```python
from flext_target_ldap import FlextTargetLdap
from flext_target_oracle import FlextTargetOracle

# LDAP Target
ldap_target = FlextTargetLdap()
ldap_target.configure({
    "host": "ldap.example.com",
    "port": 389,
    "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com"
})

# Oracle Target
oracle_target = FlextTargetOracle()
oracle_target.configure({
    "host": "oracle.example.com",
    "port": 1521,
    "service_name": "XE"
})

# Load data
def load_data(records: list[dict]) -> FlextResult[LoadResult]:
    return (
        ldap_target.load(records)
        .flat_map(lambda ldap_result: oracle_target.load(records).map(lambda oracle_result: combine_results(ldap_result, oracle_result)))
    )
```

### DBT Transformations

**Data transformation and modeling**

```python
from flext_dbt_ldap import FlextDbtLdap
from flext_dbt_oracle import FlextDbtOracle

# DBT models
class LdapUserModel(FlextDbtLdap.Model):
    user_id: str
    username: str
    email: str
    department: str

class OracleUserModel(FlextDbtOracle.Model):
    user_id: str
    full_name: str
    email_address: str
    org_unit: str

# Transform data
def transform_user_data() -> FlextResult[list[dict]]:
    return (
        extract_ldap_users()
        .flat_map(lambda users: transform_ldap_to_oracle(users))
        .map(validate_transformed_data)
    )
```

---

## 🔧 Configuration APIs

### Environment Configuration

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

# Configuration management
config = FlextConfig()

# Database configuration
db_config = config.get_database_config()
# Returns: FlextResult[DatabaseConfig]

# LDAP configuration
ldap_config = config.get_ldap_config()
# Returns: FlextResult[LdapConfig]

# API configuration
api_config = config.get_api_config()
# Returns: FlextResult[ApiConfig]
```

### Service Configuration

```python
# Service registration
container = FlextContainer.get_global()

# Register services
container.register("database", DatabaseService())
container.register("ldap", LdapService())
container.register("oracle", OracleService())

# Register factories
container.register_factory("logger", create_logger)
container.register_factory("config", create_config)

# Retrieve services
db_result = container.get("database")
if db_result.is_success:
    db_service = db_result.unwrap()
```

---

## 🚀 Advanced Features

### Error Handling Patterns

```python
# Railway-oriented programming
def complex_operation(data: dict) -> FlextResult[ProcessedData]:
    return (
        validate_input(data)
        .flat_map(authenticate_user)
        .flat_map(process_business_logic)
        .flat_map(save_to_database)
        .flat_map(send_notification)
        .map(format_response)
        .map_error(handle_errors)
    )

# Error handling
def handle_errors(error: str) -> str:
    logger.error(f"Operation failed: {error}")
    return f"Processing failed: {error}"
```

### Logging and Monitoring

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

# Structured logging
logger = FlextLogger.get_logger(__name__)

def process_with_logging(data: dict) -> FlextResult[ProcessedData]:
    logger.info("Starting data processing", extra={"data_size": len(data)})

    result = process_data(data)

    if result.is_success:
        logger.info("Data processing completed successfully")
    else:
        logger.error("Data processing failed", extra={"error": result.error})

    return result
```

### Testing Patterns

```python
import pytest
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

def test_data_processing():
    # Test success case
    data = {"name": "test", "email": "test@example.com"}
    result = process_data(data)

    assert result.is_success
    assert result.unwrap().name == "test"

    # Test error case
    invalid_data = {}
    result = process_data(invalid_data)

    assert not result.is_success
    assert "required" in result.error.lower()
```

---

## 📈 Performance Considerations

### Async Operations

```python
import asyncio
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

async def async_data_processing(data: list[dict]) -> FlextResult[list[ProcessedData]]:
    # Process data concurrently
    tasks = [process_single_item(item) for item in data]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle results
    processed_data = []
    errors = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
        elif result.is_success:
            processed_data.append(result.unwrap())
        else:
            errors.append(result.error)

    if errors:
        return FlextResult[list[ProcessedData]].fail(f"Processing errors: {errors}")

    return FlextResult[list[ProcessedData]].ok(processed_data)
```

### Caching

```python
from flext_core import FlextCache

# Cache configuration
cache = FlextCache(ttl=3600)  # 1 hour TTL

def get_cached_data(key: str) -> FlextResult[dict]:
    # Check cache first
    cached_result = cache.get(key)
    if cached_result.is_success:
        return cached_result

    # Fetch from source
    data_result = fetch_from_source(key)
    if data_result.is_success:
        # Cache the result
        cache.set(key, data_result.unwrap())

    return data_result
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors

```python
# ❌ WRONG - Internal module imports
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

# ✅ CORRECT - Root module imports
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities
```

#### 2. Type Safety Issues

```python
# ❌ WRONG - Missing type annotations
def process_data(data):
    return transform(data)

# ✅ CORRECT - Complete type annotations
def process_data(data: dict[str, object]) -> FlextResult[ProcessedData]:
    return transform(data)
```

#### 3. Error Handling

```python
# ❌ WRONG - Exception-based
def process_data(data: dict) -> ProcessedData:
    if not data:
        raise ValueError("Data required")
    return transform(data)

# ✅ CORRECT - Railway-oriented
def process_data(data: dict) -> FlextResult[ProcessedData]:
    if not data:
        return FlextResult[ProcessedData].fail("Data required")
    return transform(data)
```

### Debugging Tips

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use FlextLogger for structured logging
logger = FlextLogger.get_logger(__name__)
logger.debug("Processing data", extra={"data": data})

# Check FlextResult details
result = process_data(data)
if not result.is_success:
    logger.error(f"Processing failed: {result.error}")
    logger.debug(f"Error details: {result.error_details}")
```

---

## 📚 Additional Resources

### Documentation

- **Main README:** [README.md](../../README.md)
- **Implementation Status:** [IMPLEMENTATION_STATUS_2025-10-09.md](IMPLEMENTATION_STATUS_2025-10-09.md)
- **Architecture Guide:** [docs/architecture/](../architecture/)
- **Getting Started:** [docs/guides/getting-started.md](../guides/getting-started.md)

### Examples

- **Basic Usage:** [examples/basic_usage.py](../../examples/)
- **Advanced Patterns:** [examples/advanced_patterns.py](../../examples/)
- **Integration Examples:** [examples/integrations/](../../examples/)

### Support

- **Issues:** Create GitHub issue with appropriate label
- **Questions:** Check CLAUDE.md for guidance
- **Development:** Follow established patterns and practices

---

**API Reference Generated By:** FLEXT Documentation System  
**Last Updated:** 2025-10-09  
**Version:** 0.9.0
