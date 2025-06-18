# target-oracle-wms

Singer target for Oracle Warehouse Management System (WMS) that handles data loading and business logic transformations.

## Overview

`target-oracle-wms` is a [Singer](https://singer.io) target that:
- Receives data from any Singer tap (especially `tap-oracle-wms`)
- Applies business logic transformations (KPIs, alerts, reports)
- Writes data to multiple destinations (files, database, WMS API)

## Features

- **Business Logic Processing**: Calculate KPIs, generate alerts, create reports
- **Multiple Output Formats**: JSON, CSV, Parquet
- **Flexible Destinations**: Files, databases, or back to WMS
- **Stream-Specific Processing**: Specialized handling for inventory, orders, and warehouse data
- **Batch Processing**: Efficient handling of large data volumes

## Installation

```bash
# Using pip
pip install target-oracle-wms

# Using poetry
poetry add target-oracle-wms

# Development installation
git clone https://github.com/pyauto/target-oracle-wms.git
cd target-oracle-wms
poetry install
```

## Configuration

Create a `config.json` file:

```json
{
  "base_url": "https://your-instance.oracle.com/wms/api/v1",
  "username": "your_username",
  "password": "your_password",
  "enable_kpi_calculation": true,
  "enable_alerts": true,
  "expiry_alert_days": 30,
  "output_path": "./output",
  "output_format": "json"
}
```

### Configuration Options

| Option | Type | Required | Description | Default |
|--------|------|----------|-------------|---------|
| base_url | string | Yes | Base URL for Oracle WMS API | - |
| username | string | Yes | WMS username | - |
| password | string | Yes | WMS password | - |
| timeout | integer | No | Request timeout in seconds | 300 |
| enable_kpi_calculation | boolean | No | Enable KPI calculations | true |
| enable_alerts | boolean | No | Enable alert generation | true |
| expiry_alert_days | integer | No | Days before expiry for alerts | 30 |
| output_path | string | No | Path for output files | ./output |
| output_format | string | No | Output format (json/csv/parquet) | json |
| database_url | string | No | Database URL for storing data | - |
| enable_wms_updates | boolean | No | Enable writing back to WMS | false |

## Usage

### Basic Usage

```bash
# Pipe data from tap to target
tap-oracle-wms --config tap_config.json | target-oracle-wms --config target_config.json
```

### With State Management

```bash
# Run with state for incremental replication
tap-oracle-wms --config tap_config.json --state state.json | \
  target-oracle-wms --config target_config.json | \
  tail -1 > state.json
```

### Programmatic Usage

```python
from target_oracle_wms import TargetOracleWMS

# Create target instance
target = TargetOracleWMS(config={
    "base_url": "https://wms.example.com/api/v1",
    "username": "user",
    "password": "pass",
    "enable_kpi_calculation": True
})

# Process messages
target.listen(file_input=sys.stdin)
```

## Business Logic Features

### Inventory Management
- **KPI Calculation**: Total value, turnover rates, stock levels
- **Expiry Alerts**: Multi-level alerts for expiring lots
- **Cycle Count Analysis**: Variance reports and accuracy metrics
- **Location Utilization**: Space usage and optimization reports

### Order Processing
- **Fulfillment KPIs**: Order cycle times, on-time delivery rates
- **Allocation Analysis**: Efficiency metrics and bottleneck detection
- **Customer Performance**: Customer-specific analytics
- **Trend Analysis**: Daily/weekly order patterns

### Warehouse Operations
- **Task Performance**: Productivity metrics, completion rates
- **Worker Analytics**: Individual and team productivity scores
- **Equipment Utilization**: Usage patterns and maintenance alerts
- **Zone Performance**: Area-specific efficiency metrics

## Output Examples

### Inventory KPI Report
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "metrics": {
    "total_inventory_value": 1250000.50,
    "total_items": 15000,
    "unique_skus": 500,
    "allocation_percentage": 75.5,
    "low_stock_items": 25
  },
  "alerts": {
    "expiring_soon": 10,
    "expired": 2,
    "low_stock": 25
  }
}
```

### Order Fulfillment Report
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "metrics": {
    "total_orders": 150,
    "completed_orders": 145,
    "fulfillment_rate": 96.7,
    "average_cycle_time_hours": 4.5,
    "on_time_delivery_rate": 94.2
  }
}
```

## Development

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration

# With coverage
make test-coverage
```

### Code Quality

```bash
# Format code
make format

# Lint
make lint

# Type checking
make type-check

# All quality checks
make quality
```

## Stream-Specific Sinks

The target automatically routes streams to specialized sinks:

- **InventorySink**: inventory, lots, locations, cycle_counts
- **OrderSink**: orders, order_lines, shipments, allocations
- **WarehouseSink**: tasks, workers, equipment, zones
- **GenericWMSSink**: All other streams

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

Apache License 2.0
