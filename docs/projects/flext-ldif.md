# flext-ldif

**LDIF Processing Library** - RFC-compliant LDIF processing with enterprise patterns and server-specific quirks handling.

## Overview

flext-ldif is a comprehensive library for processing LDAP Data Interchange Format (LDIF) files with full RFC 2849/4512 compliance. It provides enterprise-grade features including server-specific quirks handling, migration pipelines, and seamless integration with the flext-core framework.

## Installation

```bash
pip install flext-ldif
```

## Quick Start

### Basic Usage

```python
from flext_ldif import FlextLdif

# Initialize the API
ldif = FlextLdif()

# Parse LDIF content
ldif_content = """dn: cn=test,dc=example,dc=com
cn: test
sn: user
objectClass: inetOrgPerson"""

result = ldif.parse(ldif_content)
if result.is_success:
    entries = result.unwrap()
    print(f"Parsed {len(entries)} entries")
```

### Writing LDIF Files

```python
from flext_ldif import FlextLdifModels

# Create entries using the models
entry = FlextLdifModels.Entry(
    dn="cn=newuser,dc=example,dc=com",
    attributes={
        "cn": ["newuser"],
        "sn": ["User"],
        "objectClass": ["inetOrgPerson"]
    }
)

# Write to LDIF format
write_result = ldif.write([entry])
if write_result.is_success:
    ldif_output = write_result.unwrap()
    print(ldif_output)
```

### Server Migration

```python
from pathlib import Path

# Migrate between LDAP servers
migration_result = ldif.migrate(
    input_dir=Path("data/oid"),
    output_dir=Path("data/oud"),
    from_server="oid",
    to_server="oud"
)

if migration_result.is_success:
    print("Migration completed successfully")
else:
    print(f"Migration failed: {migration_result.failure()}")
```

## Architecture

### Core Components

#### FlextLdif (Main Facade)

The primary API providing unified access to all LDIF operations:

```python
class FlextLdif:
    def parse(self, content: str) -> FlextResult[List[Entry], Exception]
    def write(self, entries: List[Entry]) -> FlextResult[str, Exception]
    def migrate(self, input_dir: Path, output_dir: Path, from_server: str, to_server: str) -> FlextResult[MigrationReport, Exception]
```

#### FlextLdifModels

Pydantic v2 models for type-safe LDIF data representation:

```python
from flext_ldif import FlextLdifModels

# Entry model with validation
entry = FlextLdifModels.Entry(
    dn="cn=user,dc=example,dc=com",
    attributes={
        "cn": ["user"],
        "objectClass": ["inetOrgPerson", "posixAccount"]
    }
)

# Schema models for validation
schema = FlextLdifModels.Schema(
    object_classes=[
        FlextLdifModels.ObjectClass(
            name="inetOrgPerson",
            attributes=["cn", "sn", "uid"]
        )
    ]
)
```

#### Server-Specific Quirks

Handling of server-specific LDIF format variations:

```python
# Register server-specific quirks
from flext_ldif import FlextLdifQuirksRegistry

quirks = FlextLdifQuirksRegistry()

# OID-specific handling
oid_quirks = quirks.get_quirks("oid")
oid_quirks.handle_attribute_wrapping("description", long_value)

# OpenLDAP-specific handling
openldap_quirks = quirks.get_quirks("openldap")
openldap_quirks.handle_schema_extensions(schema_entry)
```

## Migration Pipeline

### Migration Process

1. **Input Scanning**: Scan source directory for LDIF files
2. **Parsing**: Parse LDIF content with server-specific quirks
3. **Transformation**: Apply server-specific transformations
4. **Validation**: Validate entries against target schema
5. **Output Generation**: Generate LDIF files for target server

### Migration Configuration

```python
from flext_ldif import FlextLdifConfig

config = FlextLdifConfig(
    # Server-specific settings
    source_server="oid",
    target_server="oud",

    # Migration options
    preserve_oid_modifiers=True,
    handle_schema_extensions=True,
    validate_entries=True,

    # Performance settings
    batch_size=1000,
    parallel_processing=True
)
```

### Migration Report

```python
migration_result = ldif.migrate(input_dir, output_dir, "oid", "oud")

if migration_result.is_success:
    report = migration_result.unwrap()

    print(f"Processed {report.total_entries} entries")
    print(f"Successfully migrated {report.successful_entries}")
    print(f"Failed entries: {len(report.failed_entries)}")

    for failure in report.failed_entries:
        print(f"Failed: {failure.dn} - {failure.error}")
```

## RFC Compliance

### Supported RFCs

- **RFC 2849**: The LDAP Data Interchange Format (LDIF) - Technical Specification
- **RFC 4512**: Lightweight Directory Access Protocol (LDAP): Directory Information Models
- **RFC 4517**: LDAP: Syntaxes and Matching Rules
- **RFC 4519**: LDAP: Schema for User Applications

### Compliance Features

- **Strict Parsing**: Validates LDIF format according to RFC specifications
- **Schema Validation**: Validates entries against LDAP schema definitions
- **Attribute Syntax Checking**: Ensures attribute values conform to LDAP syntax rules
- **DN Validation**: Validates Distinguished Name format and structure

## Server-Specific Quirks

### Supported Servers

| Server                          | Version  | Status       | Key Features                            |
| ------------------------------- | -------- | ------------ | --------------------------------------- |
| Oracle Internet Directory (OID) | 11g, 12c | ✅ Supported | Modifier handling, schema extensions    |
| Oracle Unified Directory (OUD)  | 11g, 12c | ✅ Supported | Password policy, ACI handling           |
| OpenLDAP                        | 2.4+     | ✅ Supported | Schema checking, overlay support        |
| 389 Directory Server            | 1.4+     | ✅ Supported | Tombstone handling, replication         |
| Apache Directory Server         | 2.x      | ✅ Supported | Partition handling, interceptor support |
| Novell eDirectory               | 9.x      | ✅ Supported | NDS syntax, partition handling          |
| Tivoli Directory Server         | 6.x      | ✅ Supported | RACF integration, policy handling       |

### Quirk Categories

1. **Attribute Handling**: Server-specific attribute value formatting
2. **Schema Extensions**: Custom schema elements and validation rules
3. **Modifier Support**: Handling of operational attributes and modifiers
4. **Password Policies**: Server-specific password policy enforcement
5. **Access Control**: ACI and permission handling differences

## Advanced Features

### Custom Processors

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

# Create custom processor
def custom_validation(entry: dict) -> dict[str, object]:
    # Custom validation logic
    if 'uid' in entry.get('attributes', {}):
        uid = entry['attributes']['uid'][0]
        if not uid.isalnum():
            raise ValueError(f"Invalid UID: {uid}")
    return entry

# Register processor
processors = ldif.Processors.create_processor()
ldif.Processors.register_processor("custom_validation", custom_validation, processors)

# Use in batch processing
batch_result = ldif.Processors.process_entries_batch(
    "custom_validation",
    entries,
    processors
)
```

### Event Handling

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

# Subscribe to LDIF events
bus = FlextBus()
bus.subscribe(LdifEntryProcessedEvent, CustomHandler)
bus.subscribe(LdifMigrationCompletedEvent, NotificationHandler)

# Events are automatically emitted during processing
result = ldif.parse_with_events(ldif_content)  # Emits events for each entry
```

### Async Processing

```python
import asyncio
from flext_ldif import FlextLdifClient

async def process_ldif_async():
    client = FlextLdifClient()

    # Async parsing
    result = await client.parse_async(ldif_content)
    if result.is_success:
        entries = result.unwrap()

        # Async writing
        write_result = await client.write_async(entries)
        return write_result.unwrap()

# Run async processing
ldif_output = asyncio.run(process_ldif_async())
```

## Configuration

### Environment Configuration

```bash
# Set LDIF processing options
export FLEXT_LDIF_DEFAULT_ENCODING=utf-8
export FLEXT_LDIF_STRICT_VALIDATION=true
export FLEXT_LDIF_SERVER_QUIRKS_ENABLED=true
export FLEXT_LDIF_BATCH_SIZE=1000
```

### Programmatic Configuration

```python
from flext_ldif import FlextLdifConfig

config = FlextLdifConfig(
    default_encoding="utf-8",
    strict_validation=True,
    server_quirks_enabled=True,
    batch_size=1000,
    parallel_processing=True,
    preserve_modifiers=True,
    handle_schema_extensions=True
)

# Use configuration
ldif = FlextLdif(config=config)
```

## Error Handling

### Error Handling Best Practices

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

def safe_ldif_processing():
    # Use FlextResult for error handling
    result = ldif.parse(ldif_content)

    return result.map(
        success=lambda entries: process_entries(entries),
        failure=lambda error: handle_error(error)
    )

def handle_error(error: Exception) -> str:
    # Log error with context
    logger.error("LDIF processing failed",
                extra={
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "ldif_size": len(ldif_content)
                })

    # Return safe default or re-raise
    return "error_default_value"
```

## Performance Optimization

### Batch Processing

```python
# Process large LDIF files in batches
batch_size = 1000
total_entries = len(entries)

for i in range(0, total_entries, batch_size):
    batch = entries[i:i + batch_size]
    batch_result = ldif.process_batch(batch)

    if batch_result.is_failure:
        print(f"Batch {i//batch_size} failed: {batch_result.failure()}")
        break
```

### Parallel Processing

```python
# Enable parallel processing for better performance
config = FlextLdifConfig(parallel_processing=True, max_workers=4)
ldif = FlextLdif(config=config)

# Process multiple files in parallel
files = ["file1.ldif", "file2.ldif", "file3.ldif"]
results = await ldif.process_files_parallel(files)
```

### Memory Optimization

```python
# Process large files with streaming
def process_large_file(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        # Process line by line to minimize memory usage
        for line in f:
            if line.strip():  # Skip empty lines
                result = ldif.parse_line(line)
                # Process result
```

## Testing

### Unit Testing

```python
import pytest
from flext_ldif import FlextLdif

class TestLdifProcessing:
    def test_parse_valid_ldif(self):
        ldif = FlextLdif()

        ldif_content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

        result = ldif.parse(ldif_content)
        assert result.is_success

        entries = result.unwrap()
        assert len(entries) == 1
        assert entries[0].dn == "cn=test,dc=example,dc=com"

    def test_parse_invalid_ldif(self):
        ldif = FlextLdif()

        invalid_content = "invalid ldif content"
        result = ldif.parse(invalid_content)

        assert result.is_failure
        error = result.failure()
        assert isinstance(error, LdifParsingException)
```

### Integration Testing

```python
import pytest
from pathlib import Path
from flext_ldif import FlextLdif

class TestLdifIntegration:
    def test_server_migration(self):
        ldif = FlextLdif()

        # Create test data
        input_dir = Path("test_input")
        output_dir = Path("test_output")

        input_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)

        # Create sample LDIF file
        sample_ldif = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

        with open(input_dir / "test.ldif", 'w') as f:
            f.write(sample_ldif)

        # Run migration
        result = ldif.migrate(
            input_dir=input_dir,
            output_dir=output_dir,
            from_server="oid",
            to_server="oud"
        )

        assert result.is_success
        report = result.unwrap()
        assert report.successful_entries > 0
```

## Examples

### Complete Migration Example

```python
#!/usr/bin/env python3
"""
Complete LDIF migration example from OID to OUD
"""

from pathlib import Path
from flext_ldif import FlextLdif, FlextLdifConfig

def main():
    # Configure for migration
    config = FlextLdifConfig(
        source_server="oid",
        target_server="oud",
        preserve_oid_modifiers=True,
        handle_schema_extensions=True,
        parallel_processing=True,
        batch_size=1000
    )

    # Initialize API
    ldif = FlextLdif(config=config)

    # Define paths
    input_dir = Path("data/oid_export")
    output_dir = Path("data/oud_import")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Perform migration
    print("Starting LDIF migration...")
    migration_result = ldif.migrate(
        input_dir=input_dir,
        output_dir=output_dir,
        from_server="oid",
        to_server="oud"
    )

    if migration_result.is_success:
        report = migration_result.unwrap()
        print("✅ Migration completed successfully!")
        print(f"📊 Processed {report.total_entries} entries")
        print(f"✅ Successfully migrated {report.successful_entries} entries")
        print(f"❌ Failed entries: {len(report.failed_entries)}")

        if report.failed_entries:
            print("\n❌ Failed entries:")
            for failure in report.failed_entries[:5]:  # Show first 5
                print(f"  - {failure.dn}: {failure.error}")

    else:
        error = migration_result.failure()
        print(f"❌ Migration failed: {error}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
```

## Best Practices

### LDIF Processing Best Practices

1. **Always validate input**: Use strict validation for production environments
2. **Handle server differences**: Use appropriate quirks for source and target servers
3. **Batch large files**: Process large LDIF files in manageable batches
4. **Monitor performance**: Use built-in metrics for performance monitoring
5. **Error handling**: Implement comprehensive error handling and logging

### Migration Best Practices

1. **Test migrations**: Always test migrations in a staging environment first
2. **Backup data**: Ensure source data is backed up before migration
3. **Validate results**: Verify migrated data integrity after migration
4. **Monitor progress**: Use progress callbacks for long-running migrations
5. **Rollback plan**: Have a rollback plan in case of migration failures

## Troubleshooting

### Common Issues

#### Parsing Errors

- **Invalid LDIF format**: Ensure LDIF content follows RFC specifications
- **Encoding issues**: Use UTF-8 encoding for international characters
- **Malformed DNs**: Validate DN format before processing

#### Migration Issues

- **Server compatibility**: Verify source and target server compatibility
- **Schema differences**: Check schema compatibility between servers
- **Permission issues**: Ensure proper read/write permissions for directories

#### Performance Issues

- **Large files**: Use batch processing for files > 100MB
- **Memory usage**: Enable streaming for memory-constrained environments
- **Network timeouts**: Configure appropriate timeouts for network operations

## Support and Documentation

- 📖 [Full API Reference](../api-reference/README.md#flext-ldif)
- 🐛 [Issue Tracker](https://github.com/flext/flext-ldif/issues)
- 💬 [Discussions](https://github.com/flext/flext-ldif/discussions)
- 📧 Support: <dev@flext.com>

## License

MIT License - see LICENSE file for details.

---

_Part of the FLEXT ecosystem - Built for enterprise-grade LDIF processing and migration._
