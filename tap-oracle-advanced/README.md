# 🔄 TAP Oracle Advanced

> **Enterprise-grade Singer tap for Oracle databases using FLX framework and modern SDK patterns**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Singer SDK](https://img.shields.io/badge/singer--sdk-0.45.0+-blue.svg)](https://sdk.meltano.com/)
[![FLX Framework](https://img.shields.io/badge/flx--framework-integrated-green.svg)](../flx-database-oracle)
[![Oracle](https://img.shields.io/badge/oracle-19c%2B-red.svg)](https://www.oracle.com/database/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A modern, high-performance Singer tap for extracting data from Oracle databases, built with the latest Singer SDK patterns and integrated with the FLX framework for enterprise-grade reliability and performance.

## ✨ Features

### 🚀 **Modern Architecture**

- **Python 3.13+** with full type safety and modern syntax
- **Singer SDK 0.45.0+** with latest features and best practices
- **FLX Framework integration** for robust database connections
- **Hexagonal architecture** with clear separation of concerns

### 🔧 **Advanced Oracle Support**

- **Multiple connection types**: SID and Service Name support
- **Connection pooling** with configurable pool sizes
- **Advanced query optimization** with bind variables and array fetching
- **Schema discovery** with dynamic table and view detection
- **Custom SQL queries** as configurable streams

### ⚡ **High Performance**

- **Async/await patterns** throughout for optimal performance
- **Batch processing** with configurable batch sizes
- **Cursor array fetching** for efficient memory usage
- **Parallel query execution** support

### 🛡️ **Enterprise Ready**

- **Comprehensive error handling** with retry mechanisms
- **Structured logging** with contextual information
- **Production monitoring** with performance metrics
- **Security best practices** with credential protection

## 🛠️ Installation

### Prerequisites

- Python 3.13 or higher
- Oracle Database 19c or higher
- Oracle Instant Client (for oracledb driver)

### Install from PyPI (when published)

```bash
pip install tap-oracle-advanced
```

### Install from Source

```bash
git clone <repository-url>
cd tap-oracle-advanced
poetry install
```

### Development Installation

```bash
git clone <repository-url>
cd tap-oracle-advanced
poetry install --with dev,docs
pre-commit install
```

## 🚀 Quick Start

### 1. Create Configuration File

Create a `config.json` file with your Oracle connection details:

```json
{
  "host": "localhost",
  "port": 1521,
  "service_name": "XEPDB1",
  "user": "your_username",
  "password": "your_password",
  "default_schema": "HR",
  "batch_size": 10000,
  "connection_pool_size": 5
}
```

### 2. Discover Available Streams

```bash
tap-oracle-advanced --config config.json --discover > catalog.json
```

### 3. Run Full Extraction

```bash
tap-oracle-advanced --config config.json --catalog catalog.json
```

### 4. Run Incremental Extraction

```bash
tap-oracle-advanced --config config.json --catalog catalog.json --state state.json
```

## ⚙️ Configuration

### Required Settings

| Setting    | Type   | Description          |
| ---------- | ------ | -------------------- |
| `host`     | string | Oracle database host |
| `user`     | string | Database username    |
| `password` | string | Database password    |

### Connection Settings

| Setting                | Type    | Default | Description                              |
| ---------------------- | ------- | ------- | ---------------------------------------- |
| `port`                 | integer | 1521    | Database port                            |
| `sid`                  | string  | -       | Oracle SID (alternative to service_name) |
| `service_name`         | string  | -       | Oracle service name (alternative to sid) |
| `connection_pool_size` | integer | 5       | Maximum connections in pool              |
| `connection_timeout`   | integer | 30      | Connection timeout (seconds)             |
| `command_timeout`      | integer | 300     | SQL command timeout (seconds)            |

### Discovery and Filtering

| Setting          | Type   | Default | Description                  |
| ---------------- | ------ | ------- | ---------------------------- |
| `default_schema` | string | -       | Default schema for discovery |
| `schema_filter`  | array  | -       | Schemas to include           |
| `table_filter`   | array  | -       | Table patterns to include    |
| `exclude_tables` | array  | -       | Table patterns to exclude    |

### Performance Settings

| Setting                   | Type    | Default | Description        |
| ------------------------- | ------- | ------- | ------------------ |
| `batch_size`              | integer | 10000   | Records per batch  |
| `cursor_array_size`       | integer | 1000    | Cursor array size  |
| `use_binds_for_partition` | boolean | true    | Use bind variables |

### Advanced Configuration

<details>
<summary>Click to expand advanced settings</summary>

```json
{
  "host": "oracle.example.com",
  "port": 1521,
  "service_name": "ORCL",
  "user": "tap_user",
  "password": "secure_password",

  "default_schema": "SALES",
  "schema_filter": ["SALES", "INVENTORY"],
  "table_filter": ["SALES_*", "PRODUCT_*"],
  "exclude_tables": ["*_TEMP", "*_BACKUP"],

  "batch_size": 50000,
  "cursor_array_size": 2000,
  "connection_pool_size": 10,
  "connection_timeout": 60,
  "command_timeout": 600,

  "use_singer_decimal": true,
  "use_date_datatype": true,
  "incremental_strategy": "replication_key",

  "custom_queries": [
    {
      "name": "sales_summary",
      "sql": "SELECT DATE_TRUNC('day', order_date) as day, SUM(amount) as total FROM orders GROUP BY DATE_TRUNC('day', order_date)",
      "replication_method": "FULL_TABLE",
      "primary_keys": ["day"]
    }
  ],

  "log_level": "INFO",
  "enable_sql_logging": false
}
```

</details>

## 📊 Supported Streams

The tap automatically discovers:

### 🗂️ **Standard Streams**

- **Tables**: All user tables in specified schemas
- **Views**: All user views in specified schemas
- **Materialized Views**: All user materialized views

### 🔍 **Custom Query Streams**

- Configure custom SQL queries as streams
- Support for complex joins and aggregations
- Configurable replication methods

### 📈 **Stream Features**

- **Automatic schema detection** from Oracle metadata
- **Incremental sync support** with replication keys
- **Primary key detection** for upsert operations
- **Data type mapping** to Singer JSON Schema

## 🔄 Data Type Mapping

| Oracle Type     | Singer Type    | Notes                     |
| --------------- | -------------- | ------------------------- |
| VARCHAR2, CHAR  | string         | Full Unicode support      |
| NUMBER          | integer/number | Based on precision/scale  |
| DATE, TIMESTAMP | datetime       | ISO 8601 format           |
| CLOB, LONG      | string         | Streamed for large values |
| BLOB, RAW       | string         | Base64 encoded            |
| BOOLEAN (23c+)  | boolean        | Native boolean support    |

## 🧪 Testing

### Run Unit Tests

```bash
poetry run pytest
```

### Run Integration Tests

```bash
# Requires Oracle database connection
export TAP_ORACLE_TEST_HOST=localhost
export TAP_ORACLE_TEST_USER=test_user
export TAP_ORACLE_TEST_PASSWORD=test_password
poetry run pytest tests/integration/
```

### Run with Coverage

```bash
poetry run pytest --cov=tap_oracle_advanced --cov-report=html
```

## 📈 Performance Tuning

### Connection Optimization

```json
{
  "connection_pool_size": 10,
  "cursor_array_size": 5000,
  "batch_size": 50000
}
```

### Query Optimization

```json
{
  "use_binds_for_partition": true,
  "enable_parallel_query": true,
  "parallel_degree": 4
}
```

### Memory Management

```json
{
  "stream_buffer_size": 100000,
  "max_memory_usage": "2GB"
}
```

## 🐛 Troubleshooting

### Common Issues

#### Connection Errors

```bash
# Test connection
tap-oracle-advanced --config config.json --test

# Enable debug logging
export TAP_ORACLE_LOG_LEVEL=DEBUG
```

#### Performance Issues

```bash
# Monitor SQL execution
export TAP_ORACLE_ENABLE_SQL_LOGGING=true

# Reduce batch size
# Set "batch_size": 1000 in config
```

#### Schema Discovery Issues

```bash
# Check user permissions
SELECT * FROM USER_TAB_PRIVS WHERE PRIVILEGE LIKE '%SELECT%';

# Verify schema access
SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE OWNER = 'YOUR_SCHEMA';
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone <repository-url>
cd tap-oracle-advanced
poetry install --with dev,docs
pre-commit install
```

### Code Quality

```bash
# Linting and formatting
poetry run ruff check .
poetry run ruff format .

# Type checking
poetry run mypy .

# Security scanning
poetry run bandit -r src/
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[target-oracle-advanced](../target-oracle-advanced)** - Companion Singer target
- **[flx-database-oracle](../flx-database-oracle)** - FLX Oracle database adapter
- **[Singer SDK](https://sdk.meltano.com/)** - Singer SDK documentation
- **[Meltano](https://docs.meltano.com/)** - Data integration platform

## 📞 Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/pyauto/tap-oracle-advanced/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pyauto/tap-oracle-advanced/discussions)

---

**Built with ❤️ using Singer SDK and FLX Framework**
