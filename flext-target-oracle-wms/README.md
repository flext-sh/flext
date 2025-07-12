# FLEXT Target Oracle WMS

Singer target for loading data into Oracle WMS (Warehouse Management System).

## Features

- **Oracle WMS Integration**: Native Oracle database connectivity optimized for WMS schemas
- **Singer Protocol**: Full compliance with Singer specification for data loading
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Connection Pooling**: Built-in connection pooling for high-throughput scenarios
- **Type Mapping**: Intelligent mapping of Singer types to Oracle data types
- **Metadata Tracking**: Optional Singer CDC metadata columns
- **Error Handling**: Robust error handling and logging

## Installation

```bash
poetry install
```

## Configuration

Create a `config.json` file with your Oracle WMS connection details:

```json
{
  "host": "oracle-wms.example.com",
  "port": 1521,
  "service_name": "WMSPROD",
  "user": "wms_user",
  "password": "your_password",
  "schema": "WMS",
  "batch_size": 1000,
  "add_record_metadata": true
}
```

## Usage

### As Singer Target

```bash
# Pipe data from a Singer tap
tap-something | target-oracle-wms --config config.json

# With state management
tap-something | target-oracle-wms --config config.json > state.json
```

### CLI Options

```bash
target-oracle-wms --help
```

## Configuration Options

| Option                | Type    | Default  | Description                     |
| --------------------- | ------- | -------- | ------------------------------- |
| `host`                | string  | required | Oracle database host            |
| `port`                | integer | 1521     | Oracle database port            |
| `service_name`        | string  | required | Oracle service name             |
| `user`                | string  | required | Database user                   |
| `password`            | string  | required | Database password               |
| `schema`              | string  | "WMS"    | Target schema name              |
| `batch_size`          | integer | 1000     | Records per batch               |
| `connection_timeout`  | integer | 30       | Connection timeout (seconds)    |
| `pool_size`           | integer | 5        | Connection pool size            |
| `add_record_metadata` | boolean | true     | Add Singer metadata columns     |
| `hard_delete`         | boolean | false    | Use hard deletes                |
| `validate_records`    | boolean | true     | Validate records before loading |

## Oracle WMS Features

### Table Creation

- Automatic table creation from Singer schema
- Oracle-optimized column types
- Proper handling of Oracle naming conventions (30-char limit)

### Data Type Mapping

- String → VARCHAR2(4000) or CLOB
- Integer → NUMBER(38)
- Number → NUMBER(38,10)
- Boolean → CHAR(1) with Y/N values
- DateTime → TIMESTAMP WITH TIME ZONE
- Arrays/Objects → CLOB with JSON serialization

### WMS-Specific Optimizations

- Connection pooling for high-volume loads
- Batch processing for optimal Oracle performance
- Proper transaction management
- Oracle-specific SQL generation

## Development

### Running Tests

```bash
poetry run pytest
```

### Type Checking

```bash
poetry run mypy src tests
```

### Code Quality

```bash
poetry run ruff check src tests
poetry run ruff format src tests
```

## License

FLEXT Enterprise License
