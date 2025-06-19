# tap-oracle-db

This Meltano extractor for Oracle Database (including Oracle Autonomous Database) allows extracting data from tables, views, and custom SQL queries for use in data pipelines.

## Features

- Complete table and view extraction
- Support for custom SQL queries
- Incremental extraction based on timestamp columns or replication keys
- Support for Oracle Database on-premise and Oracle Autonomous Database
- Certification for Oracle Database 19c, 21c and Oracle Autonomous Database
- Batch size configuration for memory control

## Requirements

- Python 3.8 or higher
- Oracle Client driver (cx_Oracle) or python-oracledb
- Access to Oracle Database or Oracle Autonomous Database
- Wallet for Oracle Autonomous Database connection (if applicable)

## Installation

```bash
# Via pip
pip install tap-oracle-db

# Via Meltano
meltano add extractor tap-oracle-db
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

For Thick Client mode (cx_Oracle), you also need to install Oracle Instant Client:

```bash
# Debian/Ubuntu
apt-get install libaio1
mkdir -p /opt/oracle
wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip
unzip instantclient-basiclite-linuxx64.zip -d /opt/oracle
```

## Configuration

### Basic Configuration

```yaml
# meltano.yml
plugins:
  extractors:
    - name: tap-oracle-db
      variant: custom
      pip_url: tap-oracle-db
      config:
        host: localhost
        port: 1521
        user: username
        password: password
        service_name: ORCLPDB1
        driver_type: thin # Options: thin, thick
```

### Configuration for Oracle Autonomous Database

```yaml
# meltano.yml for Autonomous DB
plugins:
  extractors:
    - name: tap-oracle-db
      variant: custom
      pip_url: tap-oracle-db
      config:
        connection_type: autonomous
        host: adb.sa-saopaulo-1.oraclecloud.com
        port: 1522
        user: ADMIN
        password: your_password
        service_name: dbname_low
        wallet_location: /path/to/wallet.zip
        wallet_password: wallet_password
```

### Advanced Configuration

```yaml
# Complete config.json
{
  "connection_type": "normal", # normal, autonomous
  "host": "localhost",
  "port": 1521,
  "user": "username",
  "password": "password",
  "service_name": "ORCLPDB1",
  "sid": null, # Alternative to service_name if needed
  "driver_type": "thin", # thin, thick
  "wallet_location": null, # For Autonomous DB
  "wallet_password": null, # For Autonomous DB
  "include_schemas": ["WMSSTAGE"],
  "exclude_schemas": ["SYS", "SYSTEM"],
  "default_replication_method": "INCREMENTAL",
  "batch_size": 50000,
  "fetch_size": 10000,
  "connect_timeout": 60,
  "query_timeout": 3600,
  "use_logminer": false, # For CDC (experimental)
  "tables":
    [
      {
        "table_name": "ORDER_HDR_STAGE",
        "schema": "WMSSTAGE",
        "replication_method": "INCREMENTAL",
        "replication_key": "CREATED_AT",
      },
      {
        "table_name": "ORDER_DTL_STAGE",
        "schema": "WMSSTAGE",
        "replication_method": "INCREMENTAL",
        "replication_key": "CREATED_AT",
      },
      {
        "table_name": "ALLOC_STAGE",
        "schema": "WMSSTAGE",
        "replication_method": "INCREMENTAL",
        "replication_key": "ALLOC_TS",
      },
    ],
  "views": [{ "view_name": "VW_ORDER_COMPLETE", "schema": "WMSSTAGE" }],
  "select_queries":
    [
      {
        "name": "allocation_summary",
        "query": "SELECT order_nbr, SUM(alloc_qty) as total_allocated FROM WMSSTAGE.ALLOC_STAGE GROUP BY order_nbr",
        "replication_method": "FULL_TABLE",
      },
    ],
}
```

## Table Configuration

You can define which tables to extract and how to synchronize them:

### FULL_TABLE Replication

Extracts the entire table on each execution:

```yaml
tables:
  - table_name: ITEMS
    schema: WMSSTAGE
    replication_method: FULL_TABLE
```

### INCREMENTAL Replication

Extracts only new or modified records since last execution:

```yaml
tables:
  - table_name: ORDER_HDR_STAGE
    schema: WMSSTAGE
    replication_method: INCREMENTAL
    replication_key: CREATED_AT
```

### Custom SQL Queries

Allows executing SQL queries to extract data:

```yaml
select_queries:
  - name: active_orders
    query: "SELECT * FROM WMSSTAGE.ORDER_HDR_STAGE WHERE STATUS != 'CLOSED'"
    replication_method: FULL_TABLE
```

## Example with Meltano

### Basic Pipeline

```bash
# Extract all configured tables and load into target database
meltano elt tap-oracle-db target-postgres --job-id=oracle_sync
```

### Selective Extraction

```bash
# Extract only certain tables
meltano elt tap-oracle-db target-postgres --select="WMSSTAGE.ORDER_HDR_STAGE WMSSTAGE.ALLOC_STAGE"
```

### Configuration with Scheduling

```yaml
# meltano.yml
schedules:
  - name: oracle_daily_sync
    extractor: tap-oracle-db
    loader: target-postgres
    interval: "@daily"
    start_date: 2023-01-01
```

## Development

This plugin was developed using the [Meltano SDK](https://sdk.meltano.com/) to ensure compatibility and follow best practices for building extractors.

### Code Structure

```
tap_oracle_db/
├── __init__.py
├── connection.py    # Gerenciamento de conexão Oracle
├── streams.py       # Definição dos streams de dados
├── discovery.py     # Lógica de descoberta de schema
├── sync.py          # Lógica de sincronização
└── tap.py           # Classe principal do extrator
```

## Troubleshooting

### Connection Issues with Autonomous Database

If encountering issues with the wallet:

1. Verify that the wallet.zip file is accessible to the user running Meltano
2. Ensure that the wallet password is correct
3. Confirm that the service_name used is correct (we recommend using the_low profile for integration)

```yaml
config:
  connection_type: autonomous
  service_name: dbname_low # Use _low for integration workloads
```

### Performance Issues

For very large tables:

1. Increase the `batch_size` for faster extractions (if memory available)
2. Configure `replication_method: INCREMENTAL` whenever possible
3. Create indexes in the database for the column used as `replication_key`

```yaml
config:
  batch_size: 100000
  fetch_size: 20000 # Controls data blocks in memory
```

### Issues with Special Characters

If encountering issues with special characters:

```yaml
config:
  nls_lang: "AMERICAN_AMERICA.AL32UTF8"
  client_charset: "UTF8"
```

## Example Schema

### Example: ORDER_HDR_STAGE

```json
{
  "type": "object",
  "properties": {
    "ORDER_NBR": {
      "type": ["string"],
      "maxLength": 50
    },
    "COMPANY_CODE": {
      "type": ["string"],
      "maxLength": 20
    },
    "FACILITY_CODE": {
      "type": ["string"],
      "maxLength": 20
    },
    "ORDER_TYPE": {
      "type": ["string", "null"],
      "maxLength": 30
    },
    "ORDER_DATE": {
      "type": ["string", "null"],
      "format": "date-time"
    },
    "DESTINATION": {
      "type": ["string", "null"],
      "maxLength": 100
    },
    "STATUS": {
      "type": ["string", "null"],
      "maxLength": 20
    },
    "CREATED_AT": {
      "type": ["string", "null"],
      "format": "date-time"
    },
    "CREATED_BY": {
      "type": ["string", "null"],
      "maxLength": 30
    }
  }
}
```
