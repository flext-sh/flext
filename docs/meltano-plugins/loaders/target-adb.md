# target-oracle

This Meltano loader for Oracle Database (including Oracle Autonomous Database) allows loading data into Oracle tables from any Meltano/Singer extractor.

## Features

- Efficient data loading to Oracle Database (on-premise and cloud)
- Complete Oracle Autonomous Database support
- Automatic table creation when they don't exist
- Insert, update, merge (upsert) and complete replacement operations
- Bulk loading optimization using SQL*Loader or Direct Path Insert
- Support for data type transformations and column mapping

## Requirements

- Python 3.8 or higher
- Oracle Client driver (cx_Oracle) or python-oracledb
- Access to Oracle Database (19c, 21c) or Oracle Autonomous Database
- Wallet for Oracle Autonomous Database connection (if applicable)
- CREATE TABLE, INSERT, UPDATE, DELETE privileges on the database

## Installation

```bash
# Via pip
pip install target-oracle

# Via Meltano
meltano add loader target-oracle
```

### Oracle Driver Installation

Oracle drivers are required for database connection:

#### Using python-oracledb (recommended)

```bash
pip install oracledb
```

#### Using cx_Oracle (legacy mode)

```bash
pip install cx_Oracle
```

For Thick Client mode (cx_Oracle), you also need to install Oracle Instant Client.

## Configuration

### Basic Configuration

```yaml
# meltano.yml
plugins:
  loaders:
    - name: target-oracle
      variant: custom
      pip_url: target-oracle
      config:
        host: localhost
        port: 1521
        user: username
        password: password
        service_name: ORCLPDB1
        default_target_schema: WMSSTAGE
```

### Oracle Autonomous Database Configuration

```yaml
# meltano.yml for Autonomous DB
plugins:
  loaders:
    - name: target-oracle
      variant: custom
      pip_url: target-oracle
      config:
        connection_type: autonomous
        host: adb.sa-saopaulo-1.oraclecloud.com
        port: 1522
        user: ADMIN
        password: your_password
        service_name: dbname_low
        wallet_location: /path/to/wallet.zip
        wallet_password: wallet_password
        default_target_schema: WMSSTAGE
```

### Advanced Configuration

```yaml
# Complete config.json
{
  "connection_type": "normal",  # normal, autonomous
  "host": "localhost",
  "port": 1521,
  "user": "username",
  "password": "password",
  "service_name": "ORCLPDB1",
  "sid": null,  # Alternative to service_name if needed
  "wallet_location": null,  # For Autonomous DB
  "wallet_password": null,  # For Autonomous DB
  "default_target_schema": "WMSSTAGE",
  "table_prefix": "",  # Optional: prefix for all tables
  "table_suffix": "_STAGE",  # Optional: suffix for all tables
  "schema_mapping": {
    "tap_schema": "target_schema"
  },
  "add_metadata_columns": true,
  "metadata_columns": {
    "LOADED_AT": "TIMESTAMP",
    "BATCH_ID": "VARCHAR2(50)"
  },
  "batch_size_rows": 100000,
  "flush_all_streams": false,
  "parallelism": 4,
  "data_flattening_max_level": 0,
  "primary_key_required": false,
  "validate_records": true,
  "compression": "NONE",  # NONE, BASIC, LOW, MEDIUM, HIGH
  "hard_delete": false,
  "load_method": "append",  # append, upsert, insert, overwrite
  "table_cache_size": 20,
  "driver_type": "thin",  # thin, thick
  "use_direct_path": false,  # Use Direct Path for fast loading
  "use_sqlldr": false,  # Use SQL*Loader for very large loads
  "sqlldr_path": "sqlldr",
  "commit_every": 1000
}
```

## Loading Configuration

### Loading Methods

The loader supports several loading methods:

#### Append (Default)

Adds new records to existing table:

```yaml
config:
  load_method: append
```

#### Upsert

Inserts new records or updates existing ones based on primary key:

```yaml
config:
  load_method: upsert
```

#### Insert

Only inserts records, ignoring those that already exist:

```yaml
config:
  load_method: insert
```

#### Overwrite

Replaces entire table with each load:

```yaml
config:
  load_method: overwrite
```

### Bulk Loading

For high-volume loads, there are two options:

#### Direct Path Insert

Faster loading that bypasses some triggers and constraints:

```yaml
config:
  use_direct_path: true
```

#### SQL*Loader

Uses SQL*Loader tool for extremely large loads:

```yaml
config:
  use_sqlldr: true
  sqlldr_path: "/path/to/sqlldr"  # Path to sqlldr
```

## Mapping and Transformation

### Mapping of Schema

To load data from a source schema to a destination schema:

```yaml
config:
  schema_mapping:
    "source_schema": "WMSSTAGE"
```

### Metadata Columns

Add metadata columns to each table:

```yaml
config:
  add_metadata_columns: true
  metadata_columns:
    "LOADED_AT": "TIMESTAMP"
    "BATCH_ID": "VARCHAR2(50)"
```

## Example with Meltano

### Basic Pipeline

```bash
# Extract data from WMS and load into Oracle Database
meltano elt tap-wms target-oracle --job-id=wms_to_oracle
```

### Configuration with Scheduling

```yaml
# meltano.yml
schedules:
  - name: wms_daily_sync
    extractor: tap-wms
    loader: target-oracle
    interval: '@daily'
    start_date: 2023-01-01
```

## Development

This plugin was developed using the [Meltano SDK](https://sdk.meltano.com/) to ensure compatibility and follow best practices for loader construction.

### Code Structure

```
target_oracle/
├── __init__.py
├── connection.py     # Oracle connection management
├── sinks.py          # Data collector implementation
├── converter.py      # Type conversion and formatting
└── target.py         # Main loader class
```

## Troubleshooting

### Connection Errors with Autonomous Database

If encountering issues with the wallet:

1. Verify that the wallet.zip file is accessible to the Meltano user
2. Ensure that the wallet password is correct
3. Confirm that the used service_name is correct (we recommend using the_low profile for integration)

### Performance Issues

For high-volume loads:

1. Increase `batch_size_rows` for faster loading
2. Enable `use_direct_path: true` for faster insertion
3. For extremely large volumes, configure `use_sqlldr: true`
4. Adjust `parallelism` according to the number of available CPUs

```yaml
config:
  batch_size_rows: 250000
  use_direct_path: true
  parallelism: 8
```

### Permission Errors

If encountering permission errors:

1. Verify that the user has the necessary privileges (CREATE TABLE, INSERT, etc.)
2. Ensure that the destination schema exists and the user has access to it
3. If using Direct Path Insert, the user needs additional privileges like ALTER SESSION

### Data Type Issues

If encountering issues with type conversion:

```yaml
config:
  type_mapping:
    "string": "VARCHAR2(4000)"
    "integer": "NUMBER(38)"
    "number": "NUMBER"
    "boolean": "NUMBER(1)"
    "object": "CLOB"
    "array": "CLOB"
```
