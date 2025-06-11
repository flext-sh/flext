# 🏢 Oracle WMS Comprehensive Guide

> **Function**: Complete Oracle WMS operations, CLI, and integration patterns | **Audience**: WMS developers, integration engineers | **Status**: ✅ Production Ready

[![Oracle WMS](https://img.shields.io/badge/Oracle-WMS-blue.svg)](./index.md)
[![CLI](https://img.shields.io/badge/CLI-validated-green.svg)](./oracle-wms-cli-guide.md)
[![Integration](https://img.shields.io/badge/integration-patterns-orange.svg)](./oracle-wms-integration-validated.md)

**Complete Oracle Warehouse Management System operations guide with FLX Framework - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Section**: [Oracle](./index.md) → **📄 Current**: Oracle WMS Comprehensive Guide

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Getting Started Hub](../../getting-started/index.md) - Essential FLX Framework installation and setup before WMS integration
- [Oracle Hub](./index.md) - Understanding Oracle integration patterns and authentication fundamentals
- [Authentication Guide](../authentication/jwt-service-guide.md) - Required JWT and OAuth2 authentication setup for Oracle WMS access

### **➡️ Next Steps**

- [Oracle WMS CLI Guide](./oracle-wms-cli-guide.md) - Command-line interface operations and practical examples
- [Oracle WMS Integration Validated](./oracle-wms-integration-validated.md) - Production integration patterns and troubleshooting
- [Oracle WMS API Reference](./oracle-wms-complete-api-reference.md) - Complete API documentation for WMS operations

### **🔗 Related Implementation Topics**

- [**API Reference Documentation**](../../api-reference/core-api-reference.md) - Complete FLX Framework APIs and Oracle adapter class documentation for WMS integration
- [**Real-World Examples**](../../examples/oracle-integration-real-examples.md) - Production-verified Oracle WMS implementation code examples and patterns
- [**Testing WMS Integrations**](../../development/testing/hexagonal-testing-guide.md) - Comprehensive testing strategies for WMS operations within hexagonal architecture
- [**Production Infrastructure**](../../infrastructure/service-patterns.md) - Infrastructure service patterns and deployment strategies for Oracle WMS in production
- [**Security Implementation**](../../security/architecture/security-architecture.md) - Enterprise security patterns and authentication services for Oracle WMS access
- [**Performance Optimization**](../../optimization/performance/optimization-guide.md) - WMS performance tuning, connection optimization, and batch processing strategies

## Table of Contents

1. [Overview and Architecture](#overview-and-architecture)
2. [Installation and Configuration](#installation-and-configuration)
3. [CLI Operations and Commands](#cli-operations-and-commands)
4. [API Operations and Integration](#api-operations-and-integration)
5. [Database Administration](#database-REDACTED_LDAP_BIND_PASSWORDistration)
6. [Troubleshooting and Best Practices](#troubleshooting-and-best-practices)
7. [Performance Optimization](#performance-optimization)

## Overview and Architecture

Oracle WMS Cloud provides comprehensive warehouse management capabilities through multiple interfaces:

### Core Components

- **FLX HTTP Oracle WMS CLI**: High-performance CLI for WMS operations
- **GN WMS CLI**: Database REDACTED_LDAP_BIND_PASSWORDistration and configuration tool
- **Oracle WMS Cloud API**: RESTful integration endpoints
- **WMS Entity Models**: Type-safe Pydantic models for validation

### Key Features

- **Dynamic Discovery**: Automatically discover available entities and endpoints
- **Type-Safe Operations**: Runtime validation using Pydantic models  
- **High-Speed Extraction**: Paged extraction for large datasets
- **Multiple Formats**: Support for JSON, CSV, Excel, Parquet, YAML
- **Bulk Operations**: Process multiple operations in batches
- **Schema Management**: Validate and cache entity schemas

### Architecture Integration

- **Hexagonal Architecture**: Clean separation between domain logic and infrastructure
- **Adapter Pattern**: WMS operations as pluggable adapters
- **Event-Driven**: Support for real-time event processing
- **Domain-Driven Design**: Rich domain models for WMS entities

## Installation and Configuration

### Prerequisites

- Python 3.8 or higher
- Access to Oracle WMS Cloud v25A/25B or higher
- Valid WMS user credentials with integration permissions

### Installation Methods

#### Method 1: FLX Project Installation

```bash
# Install from the flx_project directory
pip install -e .

# Or install using poetry
poetry install
```

#### Method 2: GN WMS CLI Installation

```bash
# Install dependencies
poetry install

# Verify installation
poetry run gn-wms-cli --version
```

#### Method 3: Standalone Installation

```bash
# Install from PyPI (when available)
pip install flx-http-oracle-wms

# Or install from source
git clone <repository>
cd flx-http-oracle-wms
poetry install
```

### Environment Configuration

#### Core WMS Connection Settings

```bash
# Basic WMS Connection
export WMS_HOST="your-wms-host.com"
export WMS_PORT="443"
export WMS_USERNAME="your-username"
export WMS_PASSWORD="your-password"
export WMS_USE_SSL="true"
export WMS_TIMEOUT="30"
export WMS_MAX_RETRIES="3"

# Company and Facility Configuration
export WMS_COMPANY_CODE="YOURCO"
export WMS_FACILITY_CODE="WH1"
export WMS_DEFAULT_BATCH_SIZE="100"
```

#### Advanced Configuration

```bash
# Performance Tuning
export WMS_CONNECTION_POOL_SIZE="10"
export WMS_REQUEST_TIMEOUT="300"
export WMS_ENABLE_COMPRESSION="true"
export WMS_CACHE_SCHEMAS="true"

# Logging and Monitoring
export WMS_LOG_LEVEL="INFO"
export WMS_ENABLE_METRICS="true"
export WMS_TRACE_REQUESTS="false"

# Integration Settings
export WMS_ENABLE_WEBHOOKS="false"
export WMS_WEBHOOK_PORT="5000"
export WMS_SFTP_ENABLED="false"
```

#### Configuration Validation

```bash
# Validate configuration (GN WMS CLI)
poetry run gn-wms-cli config

# Show configuration with sensitive values
poetry run gn-wms-cli config --show-secrets

# Export configuration as JSON
poetry run gn-wms-cli config --format=json
```

## CLI Operations and Commands

### FLX HTTP Oracle WMS CLI

#### Core Entity Operations

##### Entity Discovery

```bash
# List all available entities
flx-http-oracle-wms entity-list

# Get entity details and schema
flx-http-oracle-wms entity-schema [entity_name]

# Discover entity capabilities
flx-http-oracle-wms entity-capabilities [entity_name]
```

##### Entity Queries

```bash
# Basic entity query
flx-http-oracle-wms entity-query [entity] [key] [company_code] [facility_code]

# Advanced queries with filtering
flx-http-oracle-wms entity-query orders ORD123 COMPANY01 WH1 --format=json

# Bulk entity extraction
flx-http-oracle-wms entity-extract orders --batch-size=500 --output=orders.json
```

##### Specialized WMS Operations

**Order Management**

```bash
# Query specific order
flx-http-oracle-wms entity-query order_hdr ORD12345 YOURCO WH1

# Extract order details
flx-http-oracle-wms entity-query order_dtl ORD12345 YOURCO WH1

# Bulk order extraction
flx-http-oracle-wms entity-extract order_hdr --batch-size=100 --format=csv
```

**Inventory Operations**

```bash
# Check item inventory
flx-http-oracle-wms entity-query items ITEM123 YOURCO WH1

# Location inquiry
flx-http-oracle-wms entity-query locations LOC-A-01 YOURCO WH1

# Allocation status
flx-http-oracle-wms entity-query allocations --filter="status=ALLOCATED"
```

**Facility Management**

```bash
# List facilities
flx-http-oracle-wms entity-query facilities

# LPN tracking
flx-http-oracle-wms entity-query lpns LPN123456 YOURCO WH1

# Location management
flx-http-oracle-wms entity-query locations --filter="zone=PICK"
```

#### Data Export and Formatting

**Output Formats**

```bash
# JSON output (default)
flx-http-oracle-wms entity-query orders ORD123 --format=json

# CSV export
flx-http-oracle-wms entity-extract orders --format=csv --output=orders.csv

# Excel export
flx-http-oracle-wms entity-extract items --format=excel --output=items.xlsx

# Parquet format (for analytics)
flx-http-oracle-wms entity-extract order_hdr --format=parquet --output=orders.parquet

# YAML format
flx-http-oracle-wms entity-query facilities --format=yaml
```

**Batch Operations**

```bash
# High-volume extraction with pagination
flx-http-oracle-wms entity-extract order_hdr \
  --batch-size=1000 \
  --max-pages=10 \
  --output=large_orders.json

# Parallel processing
flx-http-oracle-wms entity-extract orders \
  --parallel=4 \
  --batch-size=250 \
  --format=csv
```

### GN WMS CLI - Database Administration

#### Configuration Management

```bash
# Display current configuration
poetry run gn-wms-cli config

# Validate database connectivity
poetry run gn-wms-cli config --validate

# Test WMS API connection
poetry run gn-wms-cli config --test-connection
```

#### Database Operations

```bash
# Database status and health
poetry run gn-wms-cli db-status

# Schema validation
poetry run gn-wms-cli validate-schema

# Performance metrics
poetry run gn-wms-cli performance-metrics

# Connection pool monitoring
poetry run gn-wms-cli pool-status
```

#### Data Management

```bash
# Data validation
poetry run gn-wms-cli validate-data [table_name]

# Data synchronization status
poetry run gn-wms-cli sync-status

# Batch processing status
poetry run gn-wms-cli batch-status
```

## API Operations and Integration

### REST API Integration Patterns

#### Authentication

```python
from flx_http_oracle_wms import WMSClient

# Basic authentication
client = WMSClient(
    host="your-wms-host.com",
    username="your-username",
    password="your-password",
    company_code="YOURCO",
    facility_code="WH1"
)

# With advanced configuration
client = WMSClient(
    host="your-wms-host.com",
    username="your-username", 
    password="your-password",
    company_code="YOURCO",
    facility_code="WH1",
    timeout=60,
    max_retries=3,
    use_ssl=True,
    enable_compression=True
)
```

#### Entity Operations

```python
# Query single entity
order = await client.get_order("ORD12345")

# Query with parameters
items = await client.query_entity(
    entity="items",
    filters={"status": "ACTIVE"},
    limit=100
)

# Bulk operations
orders = await client.extract_entities(
    entity="order_hdr",
    batch_size=500,
    filters={"date_created": ">=2023-01-01"}
)
```

#### Advanced Integration Patterns

```python
# Hexagonal architecture integration
from flx.adapters.outbound.wms import WMSAdapter
from flx.core.entities import Order

class OrderService:
    def __init__(self, wms_adapter: WMSAdapter):
        self._wms_adapter = wms_adapter
    
    async def process_order(self, order_id: str) -> Order:
        # Domain logic with adapter
        wms_data = await self._wms_adapter.get_order(order_id)
        return Order.from_wms_data(wms_data)
```

### Error Handling and Resilience

#### Standard Error Patterns

```python
from flx_http_oracle_wms import WMSError, ConnectionError, AuthenticationError

try:
    result = await client.get_order("ORD123")
except AuthenticationError:
    # Handle authentication issues
    logger.error("WMS authentication failed")
except ConnectionError:
    # Handle network issues
    logger.error("WMS connection failed")
except WMSError as e:
    # Handle WMS-specific errors
    logger.error(f"WMS operation failed: {e}")
```

#### Retry and Circuit Breaker Patterns

```python
from flx.infrastructure.resilience import CircuitBreaker, RetryPolicy

# Configure resilience patterns
client = WMSClient(
    host="your-wms-host.com",
    retry_policy=RetryPolicy(
        max_attempts=3,
        backoff_factor=2,
        max_delay=60
    ),
    circuit_breaker=CircuitBreaker(
        failure_threshold=5,
        recovery_timeout=30
    )
)
```

## Database Administration

### Schema Management

#### Schema Validation

```bash
# Validate entity schemas
poetry run gn-wms-cli validate-schema --entity=orders

# Check schema compatibility
poetry run gn-wms-cli schema-compatibility --version=25A

# Export schema definitions
poetry run gn-wms-cli export-schema --output=schemas/
```

#### Database Maintenance

```bash
# Database health check
poetry run gn-wms-cli db-health

# Performance optimization
poetry run gn-wms-cli optimize-db

# Index management
poetry run gn-wms-cli manage-indexes --analyze
```

### Data Synchronization

#### Sync Operations

```bash
# Full synchronization
poetry run gn-wms-cli full-sync

# Incremental sync
poetry run gn-wms-cli incremental-sync --since="2023-01-01"

# Entity-specific sync
poetry run gn-wms-cli sync-entity orders --batch-size=1000
```

#### Monitoring and Alerting

```bash
# Sync status monitoring
poetry run gn-wms-cli sync-status --detailed

# Error analysis
poetry run gn-wms-cli analyze-errors --period=24h

# Performance metrics
poetry run gn-wms-cli metrics --export=json
```

## Troubleshooting and Best Practices

### Common Issues and Solutions

#### Authentication Problems

**Issue:** Authentication failures

```bash
# Symptoms
ERROR: Authentication failed for user 'username'

# Solutions
1. Verify credentials in environment variables
2. Check user permissions in WMS
3. Validate company/facility access
4. Test with basic auth first

# Debugging
poetry run gn-wms-cli config --show-secrets
flx-http-oracle-wms test-connection
```

#### Connection and Timeout Issues

**Issue:** Connection timeouts or network errors

```bash
# Symptoms
ERROR: Connection timeout after 30 seconds

# Solutions
1. Increase timeout values
export WMS_TIMEOUT="60"
export WMS_REQUEST_TIMEOUT="300"

2. Check network connectivity
curl -v https://your-wms-host.com/health

3. Verify SSL/TLS configuration
export WMS_USE_SSL="true"
export WMS_VERIFY_SSL="true"
```

#### Performance Issues

**Issue:** Slow extraction or high memory usage

```bash
# Solutions
1. Reduce batch sizes
export WMS_DEFAULT_BATCH_SIZE="50"

2. Enable compression
export WMS_ENABLE_COMPRESSION="true"

3. Use pagination for large datasets
flx-http-oracle-wms entity-extract orders \
  --batch-size=100 \
  --max-pages=10

4. Enable caching
export WMS_CACHE_SCHEMAS="true"
```

#### Data Quality Issues

**Issue:** Invalid or missing data

```bash
# Debugging
poetry run gn-wms-cli validate-data orders
poetry run gn-wms-cli schema-compatibility

# Solutions
1. Validate entity schemas before extraction
2. Use type-safe operations with Pydantic models
3. Implement data validation in processing pipeline
```

### Best Practices

#### Configuration Management

- Use environment variables for all configuration
- Store sensitive credentials securely (vault, secrets manager)
- Validate configuration before operations
- Use different configurations for dev/staging/prod

#### Error Handling

- Implement comprehensive error handling for all operations
- Use structured logging for debugging
- Implement retry logic with exponential backoff
- Monitor error rates and patterns

#### Performance Optimization

- Use appropriate batch sizes for your use case
- Enable compression for large data transfers
- Implement connection pooling for high-frequency operations
- Cache frequently accessed schemas and metadata

#### Security

- Use least-privilege access principles
- Rotate credentials regularly
- Enable SSL/TLS for all connections
- Implement audit logging for all operations

## Performance Optimization

### Batch Processing Optimization

#### Optimal Batch Sizes

```bash
# Small datasets (< 1000 records)
--batch-size=50

# Medium datasets (1000-10000 records)  
--batch-size=100

# Large datasets (> 10000 records)
--batch-size=500

# Very large datasets with parallel processing
--batch-size=250 --parallel=4
```

#### Memory Management

```bash
# Enable streaming for large datasets
flx-http-oracle-wms entity-extract orders \
  --stream=true \
  --batch-size=100 \
  --output-format=jsonl

# Use compression to reduce memory usage
export WMS_ENABLE_COMPRESSION="true"
export WMS_COMPRESSION_LEVEL="6"
```

### Network Optimization

#### Connection Pooling

```python
# Configure connection pool
client = WMSClient(
    host="your-wms-host.com",
    pool_size=10,
    pool_maxsize=20,
    pool_block=True
)
```

#### Request Optimization

```bash
# Optimize request timeouts
export WMS_CONNECTION_TIMEOUT="30"
export WMS_REQUEST_TIMEOUT="300"
export WMS_KEEP_ALIVE="true"

# Enable HTTP/2 if supported
export WMS_HTTP_VERSION="2.0"
```

### Monitoring and Metrics

#### Performance Monitoring

```bash
# Enable metrics collection
export WMS_ENABLE_METRICS="true"
export WMS_METRICS_PORT="9090"

# Monitor performance
poetry run gn-wms-cli metrics --real-time

# Export metrics
flx-http-oracle-wms metrics --export=prometheus
```

#### Alerting Configuration

```bash
# Configure alerting thresholds
export WMS_ALERT_ERROR_RATE="5%"
export WMS_ALERT_RESPONSE_TIME="2000ms"
export WMS_ALERT_CONNECTION_FAILURES="3"
```

## Advanced Integration Patterns

### Event-Driven Architecture

```python
# Webhook integration
from flx_http_oracle_wms import WebhookServer

webhook_server = WebhookServer(
    port=5000,
    endpoint="/wms-events",
    auth_required=True
)

@webhook_server.on_event("order_created")
async def handle_order_created(event_data):
    # Process order creation event
    order_id = event_data["order_id"]
    await process_new_order(order_id)
```

### Real-time Processing

```python
# Stream processing with asyncio
async def process_wms_stream():
    async for batch in client.stream_entities("orders"):
        await process_order_batch(batch)
        
# Background task processing
from flx.infrastructure.tasks import BackgroundTaskManager

task_manager = BackgroundTaskManager()
task_manager.schedule_task(
    "sync_orders",
    sync_wms_orders,
    interval=300  # Every 5 minutes
)
```

### Integration with Data Pipelines

```python
# Apache Airflow integration
from airflow import DAG
from flx_http_oracle_wms.airflow import WMSOperator

dag = DAG("wms_sync", schedule_interval="@hourly")

sync_orders = WMSOperator(
    task_id="sync_orders",
    entity="order_hdr",
    batch_size=500,
    output_format="parquet",
    dag=dag
)
```

## See Also

- **Architecture Documentation:**
  - [FLX HTTP Oracle WMS Adapter](./flx-http-oracle-wms-adapter.md) - Technical adapter implementation
  - [Hexagonal Architecture Guide](../architecture/UNIFIED_ARCHITECTURE_GUIDE.md) - Architecture patterns

- **Integration Guides:**
  - [Meltano Plugins Integration](./meltano-plugins-integration.md) - Data pipeline integration
  - [Oracle Integration API Guide](./oracle-integration-api-guide.md) - General Oracle API patterns

- **Authentication and Security:**
  - [Oracle OAuth2 Authentication Guide](./oracle-oauth2-authentication-guide.md) - Authentication setup
  - [Oracle Security Guide](./oracle-security-guide.md) - Security best practices

- **Development and Testing:**
  - [Testing Guide](./testing-guide.md) - Testing strategies and patterns
  - [Development Tools](./development-tools.md) - Development environment setup

- **Performance and Monitoring:**
  - [Performance Optimization Guide](../optimization/performance-optimization.md) - Performance tuning
  - [Monitoring and Observability](../monitoring/observability-guide.md) - Monitoring setup

---

**📄 Content Document** | **🏠 Parent**: [Oracle Guides Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
