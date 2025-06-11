# OUD Automation Usage Examples

This directory contains practical examples of how to use the Oracle Unified Directory (OUD) automation library.

## Available Examples

The `import_full_dump.py` example demonstrates how to use the Python API to import a complete dump file (15_full_dump.ldif) to an OUD instance.

### Basic Usage

```python
from oud_automation import OudClient

# Create OUD client
client = OudClient(
    host="localhost",
    port=1389,
    bind_dn="cn=Directory Manager",
    password="password"
)

# Import LDIF file
result = client.import_ldif("path/to/15_full_dump.ldif")
print(f"Import result: {result}")
```

### Advanced Configuration

```python
from oud_automation import OudClient, OudConfig

# Configure OUD connection
config = OudConfig(
    host="oud-server.example.com",
    port=1636,
    use_ssl=True,
    bind_dn="cn=Directory Manager",
    password="secure_password",
    timeout=30
)

# Create client with configuration
client = OudClient(config)

# Import with options
result = client.import_ldif(
    ldif_path="dumps/15_full_dump.ldif",
    skip_schema_check=True,
    continue_on_error=False,
    verbose=True
)
```

### Batch Operations

```python
from oud_automation import OudBatchOperations

# Initialize batch operations
batch = OudBatchOperations(client)

# Add multiple entries
entries = [
    {
        "dn": "uid=user1,ou=people,dc=example,dc=com",
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "cn": "User One",
            "sn": "One",
            "uid": "user1"
        }
    },
    {
        "dn": "uid=user2,ou=people,dc=example,dc=com", 
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "cn": "User Two", 
            "sn": "Two",
            "uid": "user2"
        }
    }
]

# Execute batch import
result = batch.add_entries(entries)
print(f"Batch import completed: {result}")
```

### Error Handling

```python
from oud_automation import OudClient, OudError, OudConnectionError

try:
    client = OudClient(config)
    result = client.import_ldif("invalid_file.ldif")
except OudConnectionError as e:
    print(f"Connection failed: {e}")
except OudError as e:
    print(f"OUD operation failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Monitoring and Logging

```python
import logging
from oud_automation import OudClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create client with logging
client = OudClient(config, logger=logger)

# Operations will be logged
client.import_ldif("data.ldif")
```

## File Structure

```
examples/
├── import_full_dump.py      # Main import example
├── batch_operations.py      # Batch processing example
├── error_handling.py        # Error handling patterns
├── configuration.py         # Advanced configuration
└── data/
    ├── 15_full_dump.ldif    # Sample dump file
    └── sample_entries.ldif  # Sample entries
```

## Running Examples

```bash
# Install dependencies
poetry install

# Run basic import example
poetry run python examples/import_full_dump.py

# Run with custom configuration
OUD_HOST=server.example.com poetry run python examples/import_full_dump.py

# Run batch operations
poetry run python examples/batch_operations.py
```

## Environment Variables

```bash
# OUD connection settings
export OUD_HOST=localhost
export OUD_PORT=1389
export OUD_BIND_DN="cn=Directory Manager"
export OUD_PASSWORD=password
export OUD_USE_SSL=false

# Operation settings
export OUD_TIMEOUT=30
export OUD_RETRY_COUNT=3
export DEBUG=true
```

## Best Practices

### 1. Connection Management

```python
# Use context managers for automatic cleanup
with OudClient(config) as client:
    result = client.import_ldif("data.ldif")
# Connection automatically closed
```

### 2. Validation

```python
# Validate LDIF before import
from oud_automation import validate_ldif

validation_result = validate_ldif("data.ldif")
if validation_result.is_valid:
    client.import_ldif("data.ldif")
else:
    print(f"Validation errors: {validation_result.errors}")
```

### 3. Performance Optimization

```python
# Configure for large imports
config = OudConfig(
    host="oud-server",
    port=1389,
    batch_size=1000,      # Process in batches
    max_connections=5,    # Connection pooling
    timeout=300          # Longer timeout for large operations
)
```

## Testing

```bash
# Run all tests
poetry run pytest tests/

# Run specific test
poetry run pytest tests/test_import.py

# Run with coverage
poetry run pytest --cov=oud_automation tests/
```

## Performance Considerations

- Use batch operations for multiple entries
- Configure appropriate timeouts for large imports
- Monitor memory usage during large operations
- Use connection pooling for concurrent operations

## Security Notes

- Store credentials in environment variables
- Use SSL/TLS for production connections  
- Validate LDIF files before import
- Implement proper error handling and logging
