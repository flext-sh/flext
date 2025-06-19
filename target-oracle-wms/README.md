# 📥 Target Oracle WMS - Enterprise Data Loading & Business Logic Processing

> **Function**: Production-grade Singer target for Oracle WMS data loading with KPI calculation and alerting | **Audience**: Data Engineers, Business Analysts | **Status**: Production Ready

[![Singer](https://img.shields.io/badge/singer-target-blue.svg)](https://www.singer.io/)
[![Oracle](https://img.shields.io/badge/oracle-WMS-red.svg)](https://www.oracle.com/cx/retail/warehouse-management/)
[![Meltano](https://img.shields.io/badge/meltano-compatible-green.svg)](https://meltano.com/)
[![Python](https://img.shields.io/badge/python-3.9%2B-orange.svg)](https://www.python.org/)

Enterprise Singer target that processes warehouse data streams, calculates business KPIs, generates alerts, and loads data to multiple destinations including Oracle WMS.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../README.md) → **📂 Current**: Target Oracle WMS

---

## 🎯 **Core Purpose**

This Singer target provides enterprise-grade data loading and business logic processing for warehouse management data. It receives streams from any Singer tap, applies sophisticated business transformations, and delivers insights through KPIs, alerts, and reports.

### **Key Capabilities**

- **Business Logic Processing**: Real-time KPI calculation and alerting
- **Multi-Destination Loading**: Files, databases, and WMS API
- **Stream-Specific Intelligence**: Specialized handling per data type
- **Enterprise Scalability**: Batch processing for millions of records
- **Business Insights**: Automated reporting and analytics

### **Production Features**

- **Transaction Management**: ACID compliance for data integrity
- **Error Recovery**: Automatic retry with dead letter queues
- **Performance Monitoring**: Built-in metrics and logging
- **Data Validation**: Schema enforcement and quality checks

---

## 🚀 **Quick Start**

### **Installation**

```bash
# Install via pip (recommended for production)
pip install target-oracle-wms

# Install via Meltano
meltano add loader target-oracle-wms

# Install from source
git clone https://github.com/datacosmos-br/target-oracle-wms
cd target-oracle-wms
poetry install
```

### **Basic Configuration**

```json
{
  "base_url": "https://wms.company.com",
  "username": "data_loader",
  "password": "secure_password",
  "enable_kpi_calculation": true,
  "enable_alerts": true,
  "expiry_alert_days": 30,
  "output_path": "./output",
  "output_format": "json",
  "batch_size": 1000
}
```

### **Running the Target**

```bash
# Basic usage with tap
tap-oracle-wms --config tap_config.json | \
  target-oracle-wms --config target_config.json

# With state management
tap-oracle-wms --config tap_config.json --state state.json | \
  target-oracle-wms --config target_config.json | \
  tail -1 > state.json

# Test with sample data
echo '{"type":"RECORD","stream":"inventory","record":{"sku":"TEST-001","quantity":100}}' | \
  target-oracle-wms --config config.json
```

---

## 🏗️ **Architecture**

### **Data Processing Pipeline**

```
┌─────────────────────────────────────────┐
│          Singer Tap (Any)               │
│        (Data Source System)             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Singer Protocol                  │
│      (JSON Lines Input)                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       Target Oracle WMS                 │
│    (Business Logic Processor)           │
├─────────────────────────────────────────┤
│ • Stream Router                         │
│ • Business Logic Engine                 │
│ • KPI Calculator                        │
│ • Alert Generator                       │
│ • Data Validator                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Specialized Sinks                  │
├─────────────────────────────────────────┤
│ • InventorySink    • OrderSink          │
│ • WarehouseSink    • GenericWMSSink     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Destinations                    │
├─────────────────────────────────────────┤
│ • Files (JSON/CSV/Parquet)              │
│ • Database (PostgreSQL/Oracle)          │
│ • Oracle WMS API                        │
│ • Analytics Platform                    │
└─────────────────────────────────────────┘
```

### **Component Structure**

```
target-oracle-wms/
├── src/target_oracle_wms/
│   ├── __init__.py          # Package initialization
│   ├── target.py            # Main target class
│   ├── client.py            # WMS API client
│   ├── sinks/               # Specialized sinks
│   │   ├── inventory.py     # Inventory processing
│   │   ├── order.py         # Order processing
│   │   ├── warehouse.py     # Warehouse operations
│   │   └── generic.py       # Generic WMS sink
│   ├── processors/          # Business logic
│   │   ├── kpi.py          # KPI calculations
│   │   ├── alerts.py       # Alert generation
│   │   └── reports.py      # Report creation
│   ├── outputs/            # Output handlers
│   │   ├── file.py         # File outputs
│   │   ├── database.py     # Database outputs
│   │   └── api.py          # API outputs
│   └── utils/              # Utilities
├── tests/                   # Test suite
├── examples/                # Usage examples
└── meltano.yml             # Meltano config
```

---

## 🔧 **Core Features**

### **1. Stream-Specific Processing**

Intelligent routing based on stream type:

```python
# Automatic stream routing
STREAM_SINK_MAP = {
    "inventory": InventorySink,
    "lots": InventorySink,
    "locations": InventorySink,
    "cycle_counts": InventorySink,
    "orders": OrderSink,
    "order_lines": OrderSink,
    "shipments": OrderSink,
    "allocations": OrderSink,
    "tasks": WarehouseSink,
    "workers": WarehouseSink,
    "equipment": WarehouseSink,
    "zones": WarehouseSink,
}
```

### **2. Business Logic Processing**

#### **Inventory Management**

```json
{
  "kpis": {
    "total_inventory_value": 1250000.5,
    "inventory_turnover_ratio": 8.5,
    "stockout_rate": 2.1,
    "carrying_cost_percentage": 15.5,
    "abc_classification": {
      "a_items": 150,
      "b_items": 350,
      "c_items": 500
    }
  },
  "alerts": [
    { "type": "expiry", "severity": "high", "items": 25 },
    { "type": "low_stock", "severity": "medium", "items": 45 },
    { "type": "overstock", "severity": "low", "items": 12 }
  ]
}
```

#### **Order Processing**

```json
{
  "kpis": {
    "order_fulfillment_rate": 96.7,
    "perfect_order_rate": 92.3,
    "average_cycle_time": "4.5 hours",
    "backorder_rate": 3.2,
    "cost_per_order": 12.5
  },
  "trends": {
    "daily_orders": [150, 165, 142, 178, 195],
    "peak_hours": ["10-11", "14-15", "16-17"]
  }
}
```

### **3. Alert Generation**

Multi-level alert system:

```python
# Alert configuration
ALERT_RULES = {
    "inventory_expiry": {
        "critical": {"days": 7, "action": "immediate"},
        "warning": {"days": 30, "action": "notify"},
        "info": {"days": 60, "action": "report"}
    },
    "stock_levels": {
        "critical": {"threshold": 0.1, "action": "reorder"},
        "warning": {"threshold": 0.25, "action": "review"},
        "info": {"threshold": 0.5, "action": "monitor"}
    }
}
```

### **4. Output Formats**

Flexible output options:

```python
# File outputs
OUTPUT_FORMATS = {
    "json": JSONOutputHandler,
    "csv": CSVOutputHandler,
    "parquet": ParquetOutputHandler,
    "excel": ExcelOutputHandler
}

# Database outputs
DATABASE_SINKS = {
    "postgresql": PostgreSQLSink,
    "oracle": OracleSink,
    "mysql": MySQLSink,
    "snowflake": SnowflakeSink
}
```

### **5. Performance Features**

```json
{
  "performance": {
    "batch_size": 1000,
    "parallel_workers": 4,
    "memory_buffer_mb": 512,
    "compression": "gzip",
    "checkpoint_interval": 5000
  }
}
```

---

## 📊 **Business Logic Examples**

### **Inventory KPI Calculation**

```python
# examples/inventory_kpis.py
def calculate_inventory_kpis(records):
    """Calculate comprehensive inventory KPIs."""
    return {
        "total_value": sum(r["quantity"] * r["unit_cost"] for r in records),
        "turnover_ratio": calculate_turnover(records),
        "carrying_cost": calculate_carrying_cost(records),
        "stockout_risk": identify_stockout_risk(records),
        "excess_inventory": identify_excess_stock(records)
    }
```

### **Order Analytics**

```python
# examples/order_analytics.py
def analyze_order_performance(orders):
    """Analyze order fulfillment performance."""
    return {
        "fulfillment_metrics": {
            "on_time_rate": calculate_on_time_rate(orders),
            "perfect_order_rate": calculate_perfect_orders(orders),
            "cycle_time_analysis": analyze_cycle_times(orders)
        },
        "customer_insights": {
            "top_customers": identify_top_customers(orders),
            "order_patterns": analyze_order_patterns(orders),
            "seasonal_trends": detect_seasonal_trends(orders)
        }
    }
```

### **Warehouse Optimization**

```python
# examples/warehouse_optimization.py
def optimize_warehouse_operations(data):
    """Generate warehouse optimization insights."""
    return {
        "space_utilization": calculate_space_usage(data["locations"]),
        "pick_path_optimization": optimize_pick_paths(data["tasks"]),
        "worker_productivity": analyze_productivity(data["workers"]),
        "equipment_efficiency": track_equipment_usage(data["equipment"])
    }
```

---

## 🔐 **Security & Compliance**

### **Data Security**

- **Encryption**: TLS for transit, AES-256 for storage
- **Authentication**: OAuth2, API keys, mTLS
- **Audit Trail**: Complete data lineage tracking
- **PII Handling**: Automatic masking and tokenization

### **Compliance Features**

- **GDPR**: Right to erasure, data portability
- **SOX**: Financial data integrity controls
- **HIPAA**: Healthcare data protection (if applicable)
- **Industry Standards**: GS1, EDI compliance

---

## 🧪 **Testing**

### **Test Coverage**

- Unit Tests: 92%+ coverage
- Integration Tests: WMS API mocking
- End-to-End Tests: Full pipeline validation
- Performance Tests: Load testing scenarios

### **Running Tests**

```bash
# Unit tests
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# E2E tests
poetry run pytest tests/e2e

# All tests with coverage
poetry run pytest --cov=target_oracle_wms
```

---

## 📚 **Configuration Reference**

### **Required Settings**

| Setting    | Type   | Description      | Example                   |
| ---------- | ------ | ---------------- | ------------------------- |
| `base_url` | string | WMS API base URL | <https://wms.company.com> |
| `username` | string | WMS username     | data_loader               |
| `password` | string | WMS password     | secure_pass               |

### **Optional Settings**

| Setting                  | Type    | Description               | Default  |
| ------------------------ | ------- | ------------------------- | -------- |
| `timeout`                | integer | Request timeout (seconds) | 300      |
| `enable_kpi_calculation` | boolean | Calculate KPIs            | true     |
| `enable_alerts`          | boolean | Generate alerts           | true     |
| `expiry_alert_days`      | integer | Days before expiry        | 30       |
| `output_path`            | string  | Output directory          | ./output |
| `output_format`          | string  | File format               | json     |
| `batch_size`             | integer | Records per batch         | 1000     |
| `database_url`           | string  | Database connection       | -        |
| `enable_wms_updates`     | boolean | Update WMS                | false    |

---

## 🔗 **Integration Ecosystem**

### **Compatible Sources**

| Tap              | Purpose            | Status    |
| ---------------- | ------------------ | --------- |
| `tap-oracle-wms` | Primary WMS source | ✅ Tested |
| `tap-csv`        | File imports       | ✅ Tested |
| `tap-postgres`   | Database sync      | ✅ Tested |
| `tap-s3-csv`     | Cloud storage      | ✅ Tested |

### **PyAuto Integration**

| Component                                      | Integration    | Purpose             |
| ---------------------------------------------- | -------------- | ------------------- |
| [tap-oracle-wms](../tap-oracle-wms/)           | Primary source | WMS data extraction |
| [flx-oracle-wms](../flx-oracle-wms/)           | Orchestration  | Advanced workflows  |
| [flx-http-oracle-wms](../flx-http-oracle-wms/) | HTTP client    | API operations      |

### **Output Destinations**

| Destination | Format     | Purpose              |
| ----------- | ---------- | -------------------- |
| PostgreSQL  | Relational | Analytics warehouse  |
| Snowflake   | Cloud DW   | Enterprise analytics |
| S3/GCS      | Files      | Data lake storage    |
| Oracle WMS  | API        | Closed-loop updates  |

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Memory Issues with Large Batches**

   - **Symptom**: Out of memory errors
   - **Solution**: Reduce batch_size, increase memory_buffer_mb

2. **Slow Processing**

   - **Symptom**: Low throughput
   - **Solution**: Increase parallel_workers, optimize KPI calculations

3. **API Rate Limits**
   - **Symptom**: 429 errors from WMS
   - **Solution**: Implement backoff, reduce concurrent requests

### **Debug Mode**

```bash
# Enable debug logging
export TARGET_ORACLE_WMS_LOG_LEVEL=DEBUG

# Verbose output
target-oracle-wms --config config.json --debug

# Dry run mode
target-oracle-wms --config config.json --dry-run
```

---

## 🛠️ **CLI Reference**

```bash
# Basic processing
target-oracle-wms --config config.json

# With specific streams
target-oracle-wms --config config.json --streams inventory,orders

# Output to specific format
target-oracle-wms --config config.json --output-format parquet

# Database output
target-oracle-wms --config config.json --database-url postgresql://...

# Test mode
target-oracle-wms --config config.json --test

# Version info
target-oracle-wms --version
```

---

## 📖 **Advanced Usage**

### **Custom Business Logic**

```python
# custom_processor.py
from target_oracle_wms import TargetOracleWMS

class CustomWMSTarget(TargetOracleWMS):
    """Extended target with custom business logic."""

    def process_inventory_record(self, record):
        """Add custom inventory processing."""
        # Standard processing
        super().process_inventory_record(record)

        # Custom KPI
        record["custom_metric"] = self.calculate_custom_metric(record)

        # Custom alert
        if record["quantity"] < record["custom_threshold"]:
            self.generate_custom_alert(record)

        return record
```

### **Pipeline Integration**

```yaml
# meltano.yml
project_id: warehouse_analytics
environments:
  - name: prod
    config:
      plugins:
        loaders:
          - name: target-oracle-wms
            variant: datacosmos
            pip_url: target-oracle-wms
            config:
              base_url: ${WMS_BASE_URL}
              username: ${WMS_USERNAME}
              password: ${WMS_PASSWORD}
              enable_kpi_calculation: true
              output_format: parquet
              database_url: ${ANALYTICS_DB_URL}
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Singer Specification](https://hub.meltano.com/singer/spec) - Singer protocol specification
- [Oracle WMS API](https://docs.oracle.com/en/cloud/saas/warehouse-management/) - WMS API reference
- [Meltano Documentation](https://docs.meltano.com/) - Pipeline orchestration

### **Next Steps**

- [WMS Pipeline Guide](../docs/guides/wms-pipeline.md) - Complete pipeline setup
- [KPI Configuration](../docs/guides/kpi-setup.md) - Business logic customization
- [Production Deployment](../docs/deployment/target-deployment.md) - Production setup

### **Related Topics**

- [Singer Best Practices](../docs/patterns/singer.md) - Target patterns
- [Data Quality](../docs/patterns/data-quality.md) - Quality assurance
- [Business Intelligence](../docs/patterns/business-intelligence.md) - Analytics patterns

---

**📂 Component**: Target Oracle WMS | **🏠 Root**: [PyAuto Home](../README.md) | **Framework**: Singer SDK 0.39.0+ | **Updated**: 2025-06-19
