# Oracle Unified Directory Automation Library

High-performance Python library for automating Oracle Unified Directory (OUD) operations using the `python-ldap` library.

## Performance Improvements

This library has been optimized for maximum performance when working with large LDIF files and performing bulk LDAP operations:

### Key Performance Features

1. **Direct python-ldap Usage**
   - Uses python-ldap API directly for all operations instead of subprocess calls
   - Eliminates overhead of spawning external processes for ldapsearch/ldapmodify
   - Provides better error handling and type safety

2. **Connection Pooling**
   - Maintains a pool of LDAP connections for parallel operations
   - Reuses existing connections to reduce connection setup/teardown overhead
   - Configurable pool size to match system capabilities

3. **Atomic Operations**
   - Groups operations by type (add, modify, delete) for bulk processing
   - Minimizes network round-trips for better throughput
   - Provides atomic transaction-like behavior when possible

4. **Batched Processing**
   - Processes entries in configurable batch sizes
   - Optimizes memory usage for large datasets
   - Provides progress tracking and statistics

5. **Memory Efficiency**
   - Uses iterators for large LDIF files to reduce memory footprint
   - Streams entries rather than loading everything into memory
   - Efficiently handles files of any size

6. **Parallel Processing**
   - Uses ThreadPoolExecutor for concurrent operations
   - Optimizes thread usage based on operation type and complexity
   - Intelligently distributes workload across workers

7. **Invalid Suffix Handling**
   - Detects entries with base DNs not defined in the server
   - Saves these entries to a separate file for later processing
   - Continues importing valid entries without failing the entire operation

## Usage

The library provides several key components:

- `LDAPConnection`: High-performance connection manager for direct LDAP operations
- `LDIFMerger`: Tool for merging and importing multiple LDIF files efficiently
- `LDIFEntry`: Object representation of LDAP entries with changetype support
- Various utility functions for processing LDIF content

Example:

```python
from oud_automation.ldap_utils import LDAPConnection
from oud_automation.ldif_merger import merge_ldif_files

# Connect to LDAP server (using environment variables or explicit credentials)
with LDAPConnection.from_env() as ldap_conn:
    # Perform bulk import of multiple LDIF files
    success, errors = merge_ldif_files(
        ldif_files=["file1.ldif", "file2.ldif"],
        ldap_connection=ldap_conn,
        max_workers=8,
        batch_size=200,
        ignore_errors=True,
        invalid_suffix_file="invalid_suffixes.ldif"  # Save entries with invalid suffixes
    )
    
    print(f"Import completed: {success} entries successfully processed, {errors} errors")
```

## Command-line Interface

The library provides a command-line interface for common operations:

```bash
# Upsert LDIF files, saving entries with invalid suffixes to a separate file
python -m oud_automation.cli upsert file1.ldif file2.ldif --invalid-suffix-file=invalid_suffixes.ldif

# Merge multiple LDIF files
python -m oud_automation.cli merge-ldif --input-files part1.ldif part2.ldif --output-file=merged.ldif --invalid-suffix-file=invalid_suffixes.ldif
```

## Environment Variables

The library uses the following environment variables for configuration:

- `LDAP_HOST`: LDAP server hostname (default: localhost)
- `LDAP_PORT`: LDAP server port (default: 3389)
- `LDAP_BIND_DN`: DN to bind as (default: cn=Directory Manager)
- `LDAP_PASSWORD`: Password for binding
- `LDAP_USE_SSL`: Use SSL connection (true/false)
- `LDAP_CONNECT_TIMEOUT`: Connection timeout in seconds

## Performance Tuning

For optimal performance:

1. Increase batch_size for operations with many similar entries
2. Adjust max_workers based on your CPU cores and network latency
3. Group similar operations together (separate adds from modifies)
4. For large LDIF files, use the ldif_splitter to break them into manageable chunks
5. Set appropriate connection timeouts for your network environment
6. Use the invalid_suffix_file option to handle entries with invalid base DNs

## OUD Automation Package

This package provides a set of tools for Oracle Unified Directory (OUD) automation, focusing on migration from Oracle Internet Directory (OID) to OUD.

## Architecture

The package is organized as follows:

- `commands/`: Click command groups for schema, LDIF, LDAP operations, export and migration
- `config.py`: Configuration management with environment variables and JSON files
- `init_config.py`: Configuration initialization tools
- `ldap_*.py`: LDAP utilities, connection management, and diff tools
- `ldif_*.py`: LDIF file parsing, modification, and validation
- `schema.py`: Schema management and comparison functions
- `schema_*.py`: Schema extraction, migration, and transformation

## Configuration System

The OUD Automation package uses a flexible configuration system that supports:

1. Environment variables
2. `.env` files
3. JSON configuration files
4. Command-line options

### Configuration Hierarchy

Configuration is loaded with the following priority (highest to lowest):

1. Command-line options
2. Environment variables
3. `.env` file values
4. JSON configuration files
5. Default values

### Configuration Files

The package uses three main configuration file types, all stored in the `config/` directory:

1. `connection_config.json`: LDAP connection settings for different endpoints
2. `schema_config.json`: Schema migration settings and mappings
3. `ldif_config.json`: LDIF transformation and import settings

### Using the Configuration Manager

The package provides a `ConfigManager` class for easy access to configuration in your code:

```python
from oud_automation.config import config_manager

# Get LDAP configuration
ldap_config = config_manager.get_ldap_config()

# Get source/target specific configuration
source_config = config_manager.get_ldap_config("source")
target_config = config_manager.get_ldap_config("target")

# Get schema or LDIF configuration
schema_config = config_manager.get_schema_config()
ldif_config = config_manager.get_ldif_config()
```

### Initializing Configuration

You can initialize the configuration using the CLI:

```bash
oud_automation init --output-dir config --env --host localhost --port 3389
```

This will create:

1. Default configuration files in the specified directory
2. A `.env` file with the specified values
3. Necessary directories for the flx_project

### Viewing Current Configuration

To view the current active configuration:

```bash
oud_automation config --show-all
```

Or view specific parts:

```bash
oud_automation config --show-ldap --endpoint source
oud_automation config --show-schema
oud_automation config --show-ldif
```

## Command Line Interface

The package provides a comprehensive CLI for all operations.

```bash
Usage: oud_automation [OPTIONS] COMMAND [ARGS]...

  Oracle Unified Directory (OUD) automation tools.

Options:
  --version              Show version and exit.
  -v, --verbose          Enable verbose output.
  -l, --log-file TEXT    Log file path.
  -c, --config-dir TEXT  Configuration directory.
  -e, --endpoint [ldap|source|target]
                         LDAP connection endpoint to use.
  --help                 Show this message and exit.

Commands:
  config     Show current configuration settings.
  export     Export operations for OUD/OID data.
  init       Initialize configuration files for OUD automation.
  ldap       LDAP operations for OUD/OID.
  ldif       LDIF file operations.
  migrate    Migration workflows from OID to OUD.
  schema     Schema management commands for OUD.
```

Use `--help` with any command to see specific options.

## Usage Examples

See the flx_project's main README for detailed usage examples.

## Uso de LDIF

```python
from oud_automation.ldif_processor import LDIFProcessor, LDIFEntry

# Ler um arquivo LDIF
processor = LDIFProcessor()
entries = processor.read_ldif('input.ldif')

# Processar um arquivo LDIF para compatibilidade com OUD
processor.process_file('input.ldif', 'output.ldif')

# Mesclar vários arquivos LDIF
processor.merge_ldif_files(['file1.ldif', 'file2.ldif'], 'merged.ldif')

# Dividir um arquivo LDIF grande
processor.split_ldif_file('large.ldif', 'output_dir/', max_entries=1000)

# Validar um arquivo LDIF
result = processor.validate_ldif('input.ldif')
```

## Processar schemas
