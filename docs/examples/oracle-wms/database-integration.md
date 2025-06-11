# GN WMS Database Integration

A complete solution for WMS (Warehouse Management System) to Oracle database integration using standardized operations layer architecture.

## 🏗️ Architecture Overview

This flx_project follows a layered architecture that promotes separation of concerns and maintainability:

```
┌─────────────────────┐
│    CLI Interface    │ ← gn-wms-cli commands
├─────────────────────┤
│  Business Logic     │ ← check_wms_tables.py, create_wms_tables.py, etc.
├─────────────────────┤
│ Operations Layer    │ ← Standardized operations (database, wms, pipeline)
├─────────────────────┤
│  Core Components    │ ← Configuration, logging, models
├─────────────────────┤
│ External Services   │ ← Oracle DB, WMS API, OIC integrations
└─────────────────────┘
```

### Key Principles

- **No Direct Database Access**: All database operations go through `operations.database.GnDatabaseManager`
- **Standardized Logging**: All modules use `core.logging_setup` for structured logging
- **Centralized Configuration**: All configuration through `core.config.get_config()`
- **Layered Operations**: Business logic uses operations layer, not direct clients

## 📁 Project Structure

```
src/gn_oic_wms_db/
├── core/                           # Core infrastructure
│   ├── config.py                   # Configuration management
│   ├── logging_setup.py            # Structured logging setup
│   └── models.py                   # Data models and schemas
├── operations/                     # Operations layer (standardized)
│   ├── database.py                 # GnDatabaseManager (Oracle operations)
│   ├── wms_integration.py          # GnWmsIntegration (WMS operations)
│   ├── pipeline.py                 # GnPipelineOrchestrator (ETL operations)
│   └── schema.py                   # Schema extraction and validation
├── cli.py                          # Main CLI interface (click-based)
├── config_validate.py              # Configuration validation operations
├── config_show.py                  # Configuration display operations
├── config_setup.py                 # Database setup operations
├── config_check.py                 # Table inspection and analysis
├── sync.py                         # Data synchronization and clearing
└── README.md                       # This file
```

## 🔧 Operations Layer

### Database Operations (`operations.database.GnDatabaseManager`)

The standardized database manager provides:

```python
from .operations.database import GnDatabaseManager

db_manager = GnDatabaseManager()

# Table operations
db_manager.create_wms_tables(force=False)
db_manager.clear_wms_data(confirm=True)
inspection = db_manager.inspect_wms_tables(table_pattern="WMS_%")

# Data quality
quality = db_manager.analyze_table_data_quality(table_name)
validation = db_manager.validate_table_constraints(table_name)

# Connection management
db_manager.test_connection()
db_manager.close()
```

### WMS Integration (`operations.wms_integration.GnWmsIntegration`)

Standardized WMS operations:

```python
from .operations.wms_integration import GnWmsIntegration

wms = GnWmsIntegration()
wms.test_connection()
data = wms.extract_data(resource="order_hdr", limit=100)
```

### Pipeline Operations (`operations.pipeline.GnPipelineOrchestrator`)

ETL pipeline management:

```python
from .operations.pipeline import GnPipelineOrchestrator

pipeline = GnPipelineOrchestrator()

# Full synchronization
results = pipeline.run_full_sync(
    table_name="WMS_ORDER_HDR",
    wms_resource="order_hdr",
    batch_size=1000,
    dry_run=False
)

# Incremental synchronization
results = pipeline.run_incremental_sync(
    table_name="WMS_ORDER_HDR", 
    wms_resource="order_hdr",
    batch_size=500
)
```

## 🚀 CLI Usage Guide

The CLI has been organized into **3 main command groups** with comprehensive table control and management:

### 1. Configuration (`config`)

The `config` command group handles configuration, setup, and table checking operations.

```bash
# Basic configuration display (default)
gn-wms-cli config

# Validate configuration and test connections
gn-wms-cli config validate

# Show detailed configuration
gn-wms-cli config show

# Show configuration with secrets
gn-wms-cli config show --show-secrets

# Output configuration as JSON
gn-wms-cli config show --json

# Setup everything (WMS + control tables)
gn-wms-cli config setup

# Setup only WMS tables
gn-wms-cli config setup --tables wms

# Setup only control tables
gn-wms-cli config setup --tables-control

# Force recreation of existing tables
gn-wms-cli config setup --force

# Check all WMS tables (basic inspection)
gn-wms-cli config check

# Check specific table (automatically adds WMS_ prefix)
gn-wms-cli config check --table order_hdr

# Data quality analysis
gn-wms-cli config check --table order_hdr --analysis quality

# Constraint validation
gn-wms-cli config check --table order_hdr --analysis constraints

# Schema validation
gn-wms-cli config check --table order_hdr --analysis schema

# Include column details
gn-wms-cli config check --columns

# Skip data samples
gn-wms-cli config check --no-data
```

### 2. Synchronization (`sync`)

The `sync` command group handles data synchronization and clearing operations.

```bash
# Synchronize all tables (incremental by default)
gn-wms-cli sync all

# Full synchronization of all tables
gn-wms-cli sync all --mode full

# Synchronize specific table
gn-wms-cli sync table order_hdr

# Full synchronization of specific table
gn-wms-cli sync table order_hdr --mode full

# Custom batch size
gn-wms-cli sync table order_hdr --batch-size 500

# Dry run (validate without changes)
gn-wms-cli sync table order_hdr --dry-run

# Clear all WMS data (requires force)
gn-wms-cli sync all --clear --force

# Clear specific table data
gn-wms-cli sync table order_hdr --clear --force

# Sync with verbose output
gn-wms-cli sync table order_hdr --verbose
```

### 3. Control and Management (`control`)

The `control` command group provides comprehensive table control and management using control tables for tracking, monitoring, and governance.

```bash
# Show comprehensive table status from control tables
gn-wms-cli control status

# Show detailed status with quality metrics
gn-wms-cli control status --detailed

# Export status as JSON
gn-wms-cli control status --json

# Show load history for all tables
gn-wms-cli control history

# Show load history for specific table
gn-wms-cli control history --table WMS_ORDER_HDR

# Show history for last 30 days with more records
gn-wms-cli control history --days 30 --limit 50

# Manually register a table in control system
gn-wms-cli control register WMS_CUSTOM_TABLE custom_resource

# Register with specific table type
gn-wms-cli control register WMS_AUDIT_LOG audit_log --table-type AUDIT

# Refresh record counts for all tables
gn-wms-cli control refresh

# Get comprehensive system statistics
gn-wms-cli control stats

# Cleanup old load history (30+ days)
gn-wms-cli control cleanup --force

# Cleanup with custom retention period
gn-wms-cli control cleanup --days 60 --force
```

### Available Tables

When using table-specific commands, use these simplified names:

- `order_hdr` → Maps to `WMS_ORDER_HDR`
- `order_dtl` → Maps to `WMS_ORDER_DTL`
- `allocation` → Maps to `WMS_ALLOCATION`

### Global Options

All commands support these global options:

```bash
--verbose     # Verbose output with detailed logging
--quiet       # Quiet output (minimal messages)
--help        # Show command help
```

## 📋 Command Examples

### Simple Operations

```bash
# Quick setup
gn-wms-cli config setup

# Basic table check
gn-wms-cli config check

# Simple sync
gn-wms-cli sync table order_hdr
```

### Complex Operations

```bash
# Advanced setup with force recreation
gn-wms-cli config setup --force --verbose

# Comprehensive table analysis
gn-wms-cli config check --table order_hdr --analysis quality --columns --verbose

# Full sync with custom batch size
gn-wms-cli sync table order_hdr --mode full --batch-size 2000 --verbose

# Targeted data clearing
gn-wms-cli sync table order_hdr --clear --force --verbose
```

### Configuration and Testing

```bash
# Basic configuration display
gn-wms-cli config

# Validate environment and test connections
gn-wms-cli config validate

# Display full configuration with secrets
gn-wms-cli config show --show-secrets --json
```

### Programmatic Usage

```python
# Configuration operations
from gn_oic_wms_db.config_validate import validate_configuration
from gn_oic_wms_db.config_show import show_configuration

# Validate environment
success = validate_configuration()
print(f"Configuration valid: {success}")

# Display configuration
show_configuration(show_secrets=False, json_output=True)

# Table operations using direct operations modules
from gn_oic_wms_db.operations.database import GnDatabaseManager

db_manager = GnDatabaseManager()
try:
    # Setup tables
    setup_result = db_manager.create_wms_tables(force=False)
    print(f"Created {len(setup_result['created'])} tables")
    
    # Inspect tables
    inspection_result = db_manager.inspect_wms_tables(
        table_pattern="WMS_%", show_columns=True, show_data=True
    )
    print(f"Found {len(inspection_result['tables'])} tables")
finally:
    db_manager.close()

# Data synchronization using pipeline operations
from gn_oic_wms_db.operations.pipeline import GnPipelineOrchestrator

pipeline = GnPipelineOrchestrator()
sync_result = pipeline.run_incremental_sync(
    table_name="WMS_ORDER_HDR",
    wms_resource="order_hdr",
    batch_size=1000
)
print(f"Synced {sync_result.get('records_extracted', 0)} records")

# High-level operations using auxiliary modules
from gn_oic_wms_db.config_check import check_all_tables
from gn_oic_wms_db.sync import sync_specific_table

# Check tables
result = check_all_tables(show_columns=True, show_data=True)
print(f"Tables checked: {result is not None}")

# Sync specific table
success, sync_result = sync_specific_table("order_hdr", mode="incremental")
print(f"Sync successful: {success}")

# Control and management operations
from gn_oic_wms_db.control_management import (
    show_tables_status, 
    show_load_history,
    refresh_table_counts,
    get_table_statistics
)

# Get comprehensive table status
success, status_result = show_tables_status(detailed=True, json_output=False)
if success:
    summary = status_result["summary"]
    print(f"Active tables: {summary['active_tables']}")
    print(f"Total records: {summary['total_records']:,}")

# Show recent load history
success, history = show_load_history(table_name="WMS_ORDER_HDR", days=7)
if success and history:
    last_load = history[0]
    print(f"Last load: {last_load['load_status']} - {last_load['records_loaded']} records")

# Refresh all table counts
success, refresh_result = refresh_table_counts()
if success:
    print(f"Refreshed {refresh_result['updated']} tables")

# Get system statistics
success, stats = get_table_statistics()
if success:
    loads = stats["loads_last_7_days"]
    if loads["total_loads"] > 0:
        success_rate = (loads["successful_loads"] / loads["total_loads"]) * 100
        print(f"Load success rate: {success_rate:.1f}%")

# Direct control table operations
from gn_oic_wms_db.operations.database import GnDatabaseManager

db_manager = GnDatabaseManager()
try:
    # Register a new table
    success = db_manager.register_table(
        table_name="WMS_CUSTOM_TABLE",
        wms_resource="custom_data",
        table_type="WMS"
    )
    print(f"Table registered: {success}")
    
    # Start load tracking
    load_id = db_manager.start_load_tracking(
        table_name="WMS_ORDER_HDR",
        wms_resource="order_hdr", 
        load_type="INCREMENTAL",
        batch_size=1000
    )
    print(f"Load tracking started: {load_id}")
    
    # Complete load tracking
    success = db_manager.complete_load_tracking(
        load_id=load_id,
        records_extracted=1500,
        records_loaded=1450,
        records_failed=50
    )
    print(f"Load tracking completed: {success}")
    
    # Get comprehensive status
    status = db_manager.get_tables_status()
    print(f"Found {len(status['tables'])} registered tables")
    
    # Get load history
    history = db_manager.get_load_history(days=30)
    print(f"Found {len(history)} load operations in last 30 days")
    
finally:
    db_manager.close()
```

## 🗃️ Database Schema

### WMS Tables

- **WMS_ORDER_HDR**: Order header information with full audit trail
- **WMS_ORDER_DTL**: Order line details with item and location data
- **WMS_ALLOCATION**: Allocation records with picking and location data

### Control Tables

- **WMS_TABLE_REGISTRY**: Central registry of all WMS tables with metadata
- **WMS_TABLE_STATUS**: Current status and metrics for each table  
- **WMS_LOAD_HISTORY**: Complete history of all load operations
- **WMS_LOAD_WATERMARK**: Watermarks for incremental loading
- **WMS_LOAD_ERRORS**: Error tracking and debugging information

### Standard Fields

All WMS tables include:

- **ID**: Primary key (NUMBER(18))
- **KEY**: Unique business identifier (VARCHAR2(255))
- **Audit Fields**: CREATED_DATE, UPDATED_DATE, CREATED_BY, UPDATED_BY
- **TK Fields**: TK_CREATE_DT, TK_UPDATE_DT, TK_DELETE_DT

## ⚙️ Configuration

Configuration is managed through environment variables and loaded via `core.config`:

```python
from .core.config import get_config

config = get_config()
print(f"Database: {config.database.host}:{config.database.port}")
print(f"WMS URL: {config.wms.base_url}")
print(f"Log Level: {config.logging.level}")
```

### Required Environment Variables

```bash
# Database Configuration
DB_HOST=oracle.example.com
DB_PORT=1521
DB_SERVICE_NAME=ORCL
DB_USERNAME=wms_user
DB_PASSWORD=secure_password

# WMS Configuration  
WMS_URL=https://wms.example.com/api
WMS_USERNAME=api_user
WMS_PASSWORD=api_password
WMS_TIMEOUT=30

# OIC Configuration (optional)
IDCS_URL=https://idcs.example.com
IDCS_CLIENT_ID=client_id
IDCS_CLIENT_SECRET=client_secret

# Logging Configuration
LOG_LEVEL=INFO
```

## 🔍 Monitoring and Logging

All operations use structured logging:

```python
from .core.logging_setup import get_logger

logger = get_logger(__name__)
logger.info("Operation completed successfully", 
           table="WMS_ORDER_HDR", 
           records_processed=1500)
```

Log levels and formats are configured through environment variables and CLI options.

## 🧪 Testing

```bash
# Test all connections
gn-wms-cli config validate

# Validate configuration
gn-wms-cli config show

# Dry run pipeline
gn-wms-cli sync table order_hdr --dry-run

# Check system health
gn-wms-cli config check --verbose
```

## 🔧 Maintenance

### Data Quality Monitoring

```bash
# Check data quality for specific table
gn-wms-cli config check --table order_hdr --analysis quality

# Check all tables with detailed output
gn-wms-cli config check --columns --verbose
```

### Constraint Validation

```bash
# Validate constraints for specific table
gn-wms-cli config check --table order_hdr --analysis constraints

# Validate schema
gn-wms-cli config check --table order_hdr --analysis schema
```

### Batch Operations

```bash
# Large dataset sync with custom batch size
gn-wms-cli sync table order_hdr --mode full --batch-size 5000

# Incremental sync with smaller batches
gn-wms-cli sync table order_dtl --batch-size 1000
```

## 🚨 Error Handling

The operations layer provides comprehensive error handling:

- **Database Errors**: Logged to WMS_LOAD_ERRORS table
- **Connection Issues**: Automatic retry with exponential backoff
- **Data Quality Issues**: Detailed reporting and alerting
- **Configuration Errors**: Validation with clear error messages

## 📈 Performance

- **Batch Processing**: Configurable batch sizes for large datasets
- **Connection Pooling**: Efficient database connection management
- **Incremental Sync**: Watermark-based incremental loading
- **Memory Management**: Streaming processing for large datasets

## 🔐 Security

- **Environment Variables**: No secrets in code
- **Password Masking**: Secure display of sensitive information
- **Connection Encryption**: SSL/TLS for all external connections
- **Audit Trail**: Complete tracking of all data changes

## 📊 Control Tables System

The system now uses comprehensive control tables for complete governance and tracking:

### Control Tables

1. **WMS_TABLE_REGISTRY**: Central registry of all WMS tables with metadata
2. **WMS_TABLE_STATUS**: Current status and metrics for each table  
3. **WMS_LOAD_HISTORY**: Complete history of all load operations
4. **WMS_LOAD_WATERMARK**: Watermarks for incremental loading
5. **WMS_LOAD_ERRORS**: Error tracking and debugging information

### Automatic Table Registration

When tables are created via `config setup`, they are automatically registered in the control system with:

- Table name and WMS resource mapping
- Schema version and table type
- Initial status and creation timestamp
- Activation status and record count tracking

### Load Tracking

Every sync operation is automatically tracked with:

- Start and end timestamps
- Records extracted, loaded, and failed counts
- Batch size and operation mode (full/incremental)
- Error messages and duration metrics
- Watermark management for incremental loads

### Status Management

Tables maintain real-time status information:

- Current record counts
- Last sync and check timestamps  
- Data quality scores
- Error counts and schema validation
- Load success/failure tracking
