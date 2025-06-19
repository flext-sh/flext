# flx-oracle-wms

Unified Oracle WMS integration that orchestrates `tap-oracle-wms` and `target-oracle-wms` with advanced pipeline management, monitoring, and business logic.

## Overview

`flx-oracle-wms` provides a complete ETL solution for Oracle Warehouse Management System by:

- Orchestrating data extraction (tap) and loading (target)
- Managing complex pipelines with scheduling
- Monitoring pipeline health and performance
- Applying business logic and generating insights
- Providing a unified CLI for all operations

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│   Oracle WMS    │────▶│  tap-oracle-wms  │────▶│ target-oracle-wms │
│      API        │     │   (Extractor)    │     │    (Loader)       │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                 │                          │
                                 └──────────┬───────────────┘
                                            │
                                   ┌────────▼────────┐
                                   │ flx-oracle-wms  │
                                   │  (Orchestrator) │
                                   └─────────────────┘
                                            │
                        ┌───────────────────┼───────────────────┐
                        │                   │                   │
                 ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
                 │  Pipeline    │    │ Monitoring  │    │   Business   │
                 │ Management   │    │  & Metrics  │    │    Logic     │
                 └──────────────┘    └─────────────┘    └──────────────┘
```

## Features

### Pipeline Management

- **Pre-configured Pipelines**: Inventory sync, order processing, warehouse analytics
- **Custom Pipelines**: Define your own extraction and transformation workflows
- **Scheduling**: Cron-based scheduling for automated execution
- **Parallel Execution**: Run multiple pipelines concurrently with resource control

### Monitoring & Observability

- **Real-time Metrics**: Track pipeline performance, record counts, errors
- **Prometheus Integration**: Export metrics for external monitoring
- **Health Checks**: Automatic health monitoring of pipelines
- **Event Logging**: Detailed event tracking for debugging

### Business Intelligence

- **KPI Calculation**: Automatic calculation of key performance indicators
- **Alert Generation**: Multi-level alerts for inventory, orders, operations
- **Report Generation**: Automated reports with insights and recommendations
- **Trend Analysis**: Historical data analysis for pattern detection

### Advanced Features

- **State Management**: Incremental replication with automatic state tracking
- **Error Recovery**: Automatic retry with exponential backoff
- **Data Validation**: Schema validation and data quality checks
- **Transformation Engine**: Built-in transformations and custom processors

## Installation

```bash
# Install from PyPI
pip install flx-oracle-wms

# Development installation
git clone https://github.com/pyauto/flx-oracle-wms.git
cd flx-oracle-wms
poetry install
```

## Quick Start

### 1. Initialize Configuration

```bash
# Generate configuration templates
flx-oracle-wms init \
  --tap-config config/tap_config.json \
  --target-config config/target_config.json \
  --pipeline-config config/pipeline_config.json
```

### 2. Configure Connections

Edit the generated configuration files:

**tap_config.json** (extraction settings):

```json
{
  "base_url": "https://your-instance.oracle.com/wms/api/v1",
  "username": "your_username",
  "password": "your_password",
  "start_date": "2024-01-01T00:00:00Z"
}
```

**target_config.json** (loading and business logic):

```json
{
  "output_path": "./output",
  "output_format": "json",
  "enable_kpi_calculation": true,
  "enable_alerts": true
}
```

### 3. Discover Available Streams

```bash
# Discover and save catalog
flx-oracle-wms discover --tap-config config/tap_config.json
```

### 4. Run a Pipeline

```bash
# Run the default pipeline
flx-oracle-wms pipeline run --config config/pipeline_config.json

# Run a specific pipeline
flx-oracle-wms pipeline run --config config/pipeline_config.json --pipeline-name inventory_sync
```

## CLI Commands

### Core Commands

```bash
# Extract data only (tap)
flx-oracle-wms extract --tap-config tap.json --target-config target.json

# Load data only (target)
flx-oracle-wms load --config target.json < data.jsonl

# Discover streams
flx-oracle-wms discover --tap-config tap.json
```

### Pipeline Commands

```bash
# List available pipelines
flx-oracle-wms pipeline list --config pipeline.json

# Run pipeline
flx-oracle-wms pipeline run --config pipeline.json --pipeline-name inventory_sync

# Run all pipelines
flx-oracle-wms pipeline run --config pipeline.json
```

### Monitoring Commands

```bash
# Check pipeline status
flx-oracle-wms monitor status --pipeline-name inventory_sync

# View metrics
flx-oracle-wms monitor metrics --format table
flx-oracle-wms monitor metrics --format prometheus
```

## Pipeline Configuration

### Example Pipeline Configuration

```json
{
  "name": "Oracle WMS Integration",
  "tap_config_path": "./config/tap_config.json",
  "target_config_path": "./config/target_config.json",
  "state_path": "./state.json",
  "catalog_path": "./catalog.json",
  "pipelines": [
    {
      "name": "inventory_sync",
      "description": "Sync inventory with KPIs",
      "streams": ["inventory", "lots", "locations"],
      "schedule": "0 */6 * * *",
      "enabled": true,
      "target_config_override": {
        "enable_kpi_calculation": true,
        "expiry_alert_days": 30
      }
    },
    {
      "name": "order_processing",
      "description": "Process orders and shipments",
      "streams": ["orders", "order_lines", "shipments"],
      "schedule": "0 * * * *",
      "enabled": true
    }
  ],
  "monitoring": {
    "enabled": true,
    "metrics_port": 9090
  }
}
```

### Pre-configured Pipelines

#### 1. Inventory Sync Pipeline

- **Purpose**: Synchronize inventory data with business intelligence
- **Streams**: inventory, lots, locations, cycle_counts
- **Features**:
  - Expiry alerts (multi-level)
  - Low stock warnings
  - Cycle count variance analysis
  - Location utilization reports

#### 2. Order Processing Pipeline

- **Purpose**: Process orders and track fulfillment
- **Streams**: orders, order_lines, shipments, allocations
- **Features**:
  - Order fulfillment KPIs
  - Bottleneck detection
  - Customer performance analytics
  - On-time delivery tracking

#### 3. Warehouse Analytics Pipeline

- **Purpose**: Analyze warehouse operations
- **Streams**: tasks, workers, equipment, zones
- **Features**:
  - Worker productivity scoring
  - Equipment utilization analysis
  - Task performance metrics
  - Zone efficiency reports

## Advanced Usage

### Custom Transformations

```python
from flx_oracle_wms import WMSOrchestrator
from flx_oracle_wms.config import PipelineConfig

# Load configuration
config = PipelineConfig.parse_file("pipeline_config.json")

# Create orchestrator with custom transformations
orchestrator = WMSOrchestrator(config)

# Add custom transformation
def custom_transform(records):
    # Your transformation logic
    return transformed_records

orchestrator.add_transformation("inventory", custom_transform)

# Run pipeline
result = orchestrator.run_pipeline("inventory_sync")
```

### Programmatic Pipeline Execution

```python
import asyncio
from flx_oracle_wms import WMSOrchestrator
from flx_oracle_wms.config import PipelineConfig

async def run_pipelines():
    config = PipelineConfig.parse_file("config.json")
    orchestrator = WMSOrchestrator(config)

    # Run all pipelines concurrently
    results = await orchestrator.run_all_pipelines_async()

    for result in results:
        print(f"Pipeline: {result['pipeline']}")
        print(f"Status: {result['status']}")
        print(f"Records: {result.get('records_loaded', 0)}")

# Run
asyncio.run(run_pipelines())
```

### Monitoring Integration

```python
from flx_oracle_wms.monitoring import PipelineMonitor

# Create monitor
monitor = PipelineMonitor()

# Get pipeline status
status = monitor.get_pipeline_status("inventory_sync")
print(f"Last run: {status['last_run']}")
print(f"Success rate: {status['success_rate']:.2%}")

# Get metrics for Prometheus
metrics = monitor.get_prometheus_metrics()
```

## Development

### Running Tests

```bash
# All tests
make test

# Unit tests
make test-unit

# Integration tests
make test-integration
```

### Code Quality

```bash
# Format code
make format

# Lint
make lint

# Type checking
make type-check

# All checks
make quality
```

## Configuration Reference

### Pipeline Configuration Options

| Option                 | Type   | Description              | Default  |
| ---------------------- | ------ | ------------------------ | -------- |
| name                   | string | Integration name         | Required |
| tap_config_path        | string | Path to tap config       | Required |
| target_config_path     | string | Path to target config    | Required |
| state_path             | string | Path to state file       | Optional |
| catalog_path           | string | Path to catalog          | Optional |
| pipelines              | array  | Pipeline definitions     | []       |
| monitoring             | object | Monitoring config        | {}       |
| max_parallel_pipelines | int    | Max concurrent pipelines | 2        |
| retry_count            | int    | Retry attempts           | 3        |
| retry_delay            | int    | Retry delay (seconds)    | 60       |

## Best Practices

1. **State Management**: Always use state files for incremental replication
2. **Catalog Selection**: Use catalogs to select only needed streams
3. **Monitoring**: Enable monitoring for production pipelines
4. **Error Handling**: Configure appropriate retry policies
5. **Resource Control**: Limit parallel executions based on system capacity

## Troubleshooting

### Common Issues

1. **Pipeline Fails to Start**

   - Check tap and target are installed
   - Verify configuration file paths
   - Check Oracle WMS connectivity

2. **No Data Extracted**

   - Verify credentials and permissions
   - Check start_date in tap config
   - Review catalog stream selection

3. **Performance Issues**
   - Reduce page_size in tap config
   - Limit parallel pipeline execution
   - Enable incremental replication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Apache License 2.0
