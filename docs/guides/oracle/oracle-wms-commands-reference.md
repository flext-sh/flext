# Oracle WMS Commands Reference Guide

**Date**: January 2025  
**Status**: Production Commands Guide  
**Version**: Complete CLI Reference

## 📋 Commands Index by Action Verbs

- [🔍 **LIST** - Discover and view](#-list---discover-and-view)
- [📝 **REGISTER** - Create and configure](#-register---create-and-configure)
- [🔄 **SYNCHRONIZE** - Transfer data](#-synchronize---transfer-data)
- [📊 **VERIFY** - Monitor status](#-verify---monitor-status)
- [🧹 **CLEAN** - Maintenance](#-clean---maintenance)
- [❌ **REMOVE** - Deregister](#-remove---deregister)

---

## 🔍 **LIST** - Discover and view

### List available WMS entities

```bash
# List all available entities (singular forms)
python -m src.gn_oic_wms_db.cli control entities list

# List with filter
python -m src.gn_oic_wms_db.cli control entities list --filter order

# List in JSON format
python -m src.gn_oic_wms_db.cli control entities list --json
```

### List configurations

```bash
# Show basic configuration
python -m src.gn_oic_wms_db.cli config

# Show detailed configuration
python -m src.gn_oic_wms_db.cli config show --detailed

# Show configuration with secrets
python -m src.gn_oic_wms_db.cli config show --secrets

# Show specific component
python -m src.gn_oic_wms_db.cli config show --component database
```

---

## 📝 **REGISTER** - Create and configure

### Register WMS entities

```bash
# Register a single entity
python -m src.gn_oic_wms_db.cli control entities register item

# Register multiple entities
python -m src.gn_oic_wms_db.cli control entities register item order allocation

# Register with dry-run (test without executing)
python -m src.gn_oic_wms_db.cli control entities register item --dry-run

# Register continuing on error
python -m src.gn_oic_wms_db.cli control entities register item order --continue-on-error
```

### Configure system

```bash
# Configure database tables
python -m src.gn_oic_wms_db.cli config setup

# Configure only WMS tables
python -m src.gn_oic_wms_db.cli config setup --tables wms

# Force table recreation
python -m src.gn_oic_wms_db.cli config setup --force

# Interactive configuration
python -m src.gn_oic_wms_db.cli config configure
```

---

## 🔄 **SYNCHRONIZE** - Transfer data

### Basic synchronization

```bash
# Synchronize all entities (incremental)
python -m src.gn_oic_wms_db.cli sync all

# Full synchronization (complete sync)
python -m src.gn_oic_wms_db.cli sync all --mode full

# Synchronize specific table
python -m src.gn_oic_wms_db.cli sync table item

# Dry-run (test without executing)
python -m src.gn_oic_wms_db.cli sync all --dry-run
```

### 🚀 Advanced synchronization (RECOMMENDED)

```bash
# Synchronization with threading and progress
python -m src.gn_oic_wms_db.cli sync enhanced

# Full sync with 8 threads
python -m src.gn_oic_wms_db.cli sync enhanced --full-sync --max-workers 8

# Synchronization with total comparison
python -m src.gn_oic_wms_db.cli sync enhanced --compare-totals

# Synchronization of specific entities
python -m src.gn_oic_wms_db.cli sync enhanced --tables item,order

# Dry-run of advanced synchronization
python -m src.gn_oic_wms_db.cli sync enhanced --dry-run --compare-totals
```

---

## 📊 **VERIFY** - Monitor status

### Check entity status

```bash
# Status of all registered entities
python -m src.gn_oic_wms_db.cli control entities status

# Status of specific entities
python -m src.gn_oic_wms_db.cli control entities status item order

# Detailed status
python -m src.gn_oic_wms_db.cli control entities status --detailed

# Status in JSON format
python -m src.gn_oic_wms_db.cli control entities status --json
```

### Check synchronization

```bash
# Synchronization status of a table
python -m src.gn_oic_wms_db.cli sync status item

# General status of tables
python -m src.gn_oic_wms_db.cli control status

# Detailed status with metrics
python -m src.gn_oic_wms_db.cli control status --detailed
```

### Check configuration

```bash
# Validate configuration
python -m src.gn_oic_wms_db.cli config validate

# Validate with details
python -m src.gn_oic_wms_db.cli config validate --verbose

# Validate specific component
python -m src.gn_oic_wms_db.cli config validate --component database

# Complete health check
python -m src.gn_oic_wms_db.cli config health
```

### Check integrity

```bash
# Complete entity check
python -m src.gn_oic_wms_db.cli control entities check item order

# Check in JSON format
python -m src.gn_oic_wms_db.cli control entities check item --json

# Check specific tables
python -m src.gn_oic_wms_db.cli config check --table WMS_ITEM

# Data quality analysis
python -m src.gn_oic_wms_db.cli config check --table WMS_ITEM --analysis quality
```

---

## 🧹 **CLEAN** - Maintenance

### Clean history

```bash
# Clean old history (30 days)
python -m src.gn_oic_wms_db.cli control cleanup --days 30 --force

# Clean specific history
python -m src.gn_oic_wms_db.cli control cleanup --days 7 --force
```

### Update counters

```bash
# Update record counters
python -m src.gn_oic_wms_db.cli control refresh
```

---

## ❌ **REMOVE** - Deregister

### Deregister entities

```bash
# Deregister entity (keep table)
python -m src.gn_oic_wms_db.cli control entities deregister item

# Deregister and remove table
python -m src.gn_oic_wms_db.cli control entities deregister item --drop-tables

# Force deregistration
python -m src.gn_oic_wms_db.cli control entities deregister item --force

# Dry-run deregistration
python -m src.gn_oic_wms_db.cli control entities deregister item --dry-run
```

---

## 🎯 **RECOMMENDED WORKFLOWS**

### 1. 🚀 Complete initial setup

```bash
# 1. Validate configuration
python -m src.gn_oic_wms_db.cli config validate --verbose

# 2. Configure tables
python -m src.gn_oic_wms_db.cli config setup

# 3. List available entities
python -m src.gn_oic_wms_db.cli control entities list

# 4. Register main entities
python -m src.gn_oic_wms_db.cli control entities register item order allocation order_dtl

# 5. Check status
python -m src.gn_oic_wms_db.cli control entities status --detailed
```

### 2. 🔄 Daily synchronization

```bash
# Incremental synchronization with threading
python -m src.gn_oic_wms_db.cli sync enhanced --compare-totals

# Check results
python -m src.gn_oic_wms_db.cli control status --detailed
```

### 3. 🔍 Problem diagnosis

```bash
# 1. General health check
python -m src.gn_oic_wms_db.cli config health

# 2. Check specific entities
python -m src.gn_oic_wms_db.cli control entities check item order

# 3. Check load history
python -m src.gn_oic_wms_db.cli control history --days 7

# 4. Quality analysis
python -m src.gn_oic_wms_db.cli config check --table WMS_ITEM --analysis quality
```

### 4. 🧹 Weekly maintenance

```bash
# 1. Update counters
python -m src.gn_oic_wms_db.cli control refresh

# 2. Clean old history
python -m src.gn_oic_wms_db.cli control cleanup --days 30 --force

# 3. Check statistics
python -m src.gn_oic_wms_db.cli control stats
```

---

## 🔧 **GLOBAL OPTIONS**

### Logging

```bash
# Verbose mode (detailed)
python -m src.gn_oic_wms_db.cli --verbose [command]

# Quiet mode (silent)
python -m src.gn_oic_wms_db.cli --quiet [command]
```

### Dry-run

```bash
# Test without executing (available in most commands)
python -m src.gn_oic_wms_db.cli [command] --dry-run
```

### Output formats

```bash
# JSON (available in status commands)
python -m src.gn_oic_wms_db.cli [command] --json

# Detailed
python -m src.gn_oic_wms_db.cli [command] --detailed
```

---

## 🚨 **EMERGENCY COMMANDS**

### Quick recovery

```bash
# 1. Check if system is working
python -m src.gn_oic_wms_db.cli config validate

# 2. Recreate tables if necessary
python -m src.gn_oic_wms_db.cli config setup --force

# 3. Re-register essential entities
python -m src.gn_oic_wms_db.cli control entities register item order allocation order_dtl --continue-on-error

# 4. Complete synchronization
python -m src.gn_oic_wms_db.cli sync enhanced --full-sync --max-workers 2
```

### Configuration backup

```bash
# Backup configuration
python -m src.gn_oic_wms_db.cli config backup

# Export configuration
python -m src.gn_oic_wms_db.cli config show --export config_backup.json
```

---

## 📈 **CONTINUOUS MONITORING**

### Daily monitoring script

```bash
#!/bin/bash
# daily_monitor.sh

echo "🔍 Daily WMS Monitoring - $(date)"
echo "=================================="

# Health check
python -m src.gn_oic_wms_db.cli config health

# Entity status
python -m src.gn_oic_wms_db.cli control entities status --detailed

# Incremental synchronization
python -m src.gn_oic_wms_db.cli sync enhanced --compare-totals

# Final statistics
python -m src.gn_oic_wms_db.cli control stats
```

---

## 🔗 **FLX Framework Integration**

### Programmatic usage

```python
from flext.adapters.oracle.wms import WMSCommandExecutor

# Initialize command executor
executor = WMSCommandExecutor(config_path="./config/wms.json")

# Execute entity registration
result = await executor.register_entities(["item", "order", "allocation"])

# Execute synchronization
sync_result = await executor.sync_enhanced(
    compare_totals=True,
    max_workers=4
)

# Get entity status
status = await executor.get_entity_status(detailed=True)
```

### Automated workflows

```python
from flext.adapters.oracle.wms import WMSWorkflowOrchestrator

# Initialize workflow orchestrator
orchestrator = WMSWorkflowOrchestrator()

# Execute daily maintenance workflow
daily_result = await orchestrator.execute_daily_workflow()

# Execute emergency recovery workflow
recovery_result = await orchestrator.execute_emergency_recovery()
```

---

## 📊 **Performance Monitoring**

### Resource monitoring

```bash
# Monitor memory usage during sync
python -m src.gn_oic_wms_db.cli sync enhanced --monitor-memory

# Monitor performance metrics
python -m src.gn_oic_wms_db.cli control performance --real-time

# Generate performance report
python -m src.gn_oic_wms_db.cli control performance --generate-report
```

### Optimization commands

```bash
# Optimize database performance
python -m src.gn_oic_wms_db.cli config optimize --component database

# Optimize synchronization settings
python -m src.gn_oic_wms_db.cli config optimize --component sync

# Auto-tune worker count
python -m src.gn_oic_wms_db.cli sync enhanced --auto-tune-workers
```

---

## ✅ **OPERATION VERIFICATION**

To verify everything is working:

```bash
# 1. Basic test
python -m src.gn_oic_wms_db.cli --help

# 2. Complete validation
python -m src.gn_oic_wms_db.cli config validate --verbose

# 3. List entities
python -m src.gn_oic_wms_db.cli control entities list

# 4. General status
python -m src.gn_oic_wms_db.cli control status
```

If all commands above work without errors, the system is operational! 🎉

## Related Documentation

- [Oracle WMS Integration Guide](oracle-wms-integration-guide.md)
- [Oracle WMS REST API Guide](oracle-wms-rest-api-guide.md)
- [Oracle WMS API Entities Reference](oracle-wms-api-entities-reference.md)
- [Oracle Integration API Guide](oracle-integration-api-guide.md)

This comprehensive command reference provides enterprise-grade WMS operations with complete CLI automation capabilities.
