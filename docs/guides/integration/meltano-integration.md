# FLX-Meltano Integration Guide - Integration Guides

> **Function**: Complete integration with Meltano for data pipeline orchestration | **Audience**: Data engineers, integration developers | **Status**: ✅ VALIDATED

[![Integration](https://img.shields.io/badge/integration-meltano-blue.svg)](./index.md)
[![Meltano](https://img.shields.io/badge/meltano-native-orange.svg)](https://meltano.com)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-green.svg)](../../index.md)

**Complete integration with Meltano enabling native plugin usage, workflow orchestration, and Airflow integration**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Integration**: [Integration Guides](./index.md) → **📄 Current**: Meltano Integration

### **📍 Learning Path Position**

```
[Integration Overview](./index.md) → **[Meltano Integration]** → [Data Pipeline Patterns](../data-patterns/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Integration Guides](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Meltano](../../../flx/src/flx/integrations/meltano/)
- **🔗 Related**: [Architecture Evolution](../../architecture/flx-2.0-architecture.md), [Meltano Plugins](../../meltano-plugins/index.md)

---

## 📋 **Overview**

The FLX framework now includes complete integration with Meltano, allowing you to use all Meltano plugins (tap-_, target-_, etc.) as native FLX adapters with full workflow orchestration, state management, and Airflow integration.

## Key Features

### 🔌 **Native Plugin Integration**

- Use any Meltano plugin as a native FLX adapter
- Full support for extractors (tap-_), loaders (target-_), transformers (dbt), and utilities
- Automatic plugin discovery from Meltano Hub
- Plugin configuration management through FLX interfaces

### 🔄 **Workflow Orchestration**

- Create and manage ELT/ETL workflows
- Schedule workflows with cron expressions
- Environment-specific configurations (dev, staging, prod)
- Dry-run capabilities for testing

### 💾 **State Management**

- Persistent state across pipeline runs
- Multiple state backends (systemdb, S3, Redis, etc.)
- State merging and copying operations
- Singer state format support

### ✈️ **Airflow Integration**

- Automatic DAG generation from workflows
- Deploy workflows to Airflow
- Schedule management through Airflow
- Monitor workflow execution

### 🏗️ **Hexagonal Architecture**

- Clean separation between domain and infrastructure
- Port/Adapter pattern implementation
- SOLID principles compliance
- Enterprise-grade patterns

## Quick Start

### Basic Usage

```python
from flx.adapters.outbound.meltano_factory import MeltanoAdapterFactory

# Create adapter with development configuration
adapter = MeltanoAdapterFactory.create_adapter(
    project_root="/path/to/meltano/project",
    config_template="development",
)

# Connect and initialize
await adapter.connect()

# Discover available plugins
plugins = await adapter.discover_plugins(plugin_type="extractors")
print(f"Found {len(plugins)} extractors")

# Install a plugin
from flx.ports.outbound.meltano_plugins import MeltanoPluginConfig

plugin_config = MeltanoPluginConfig(
    name="tap-postgres",
    plugin_type="extractors",
    namespace="tap_postgres",
    settings={
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "password",
        "dbname": "source_db",
    }
)

await adapter.install_plugin(plugin_config)
```

### Complete Pipeline Setup

```python
# Setup complete pipeline with template
adapter = await MeltanoAdapterFactory.setup_complete_pipeline(
    project_root="/path/to/project",
    plugin_template="postgres_to_snowflake",  # Pre-configured template
    config_template="production",
    install_plugins=True,
    create_workflow=True,
)

# Run ELT pipeline
result = await adapter.run_elt_pipeline(
    extractor="tap-postgres",
    loader="target-snowflake",
    transformer="dbt-snowflake",
    state_id="daily-pipeline",
)

print(f"Pipeline {'succeeded' if result['success'] else 'failed'}")
```

### Workflow Creation and Scheduling

```python
from flx.ports.outbound.meltano_plugins import MeltanoWorkflowConfig

# Create workflow
workflow_config = MeltanoWorkflowConfig(
    name="daily_sales_pipeline",
    extractors=["tap-salesforce", "tap-postgres"],
    loaders=["target-snowflake"],
    transformers=["dbt-snowflake"],
    orchestrator="airflow",
    schedule="0 2 * * *",  # Daily at 2 AM
    environment="prod",
    state_backend="s3",
)

await adapter.create_workflow(workflow_config)

# Deploy to Airflow
await adapter.deploy_to_airflow(
    workflow_name="daily_sales_pipeline",
    airflow_config={
        "dags_directory": "/opt/airflow/dags",
        "webserver_host": "localhost",
        "webserver_port": 8080,
    }
)

# Schedule workflow
await adapter.schedule_workflow(
    workflow_name="daily_sales_pipeline",
    schedule="0 2 * * *",
    orchestrator="airflow",
)
```

### State Management

```python
# Set state for pipeline resumption
state_data = {
    "singer_state": {
        "bookmarks": {
            "users": {
                "replication_key": "updated_at",
                "replication_key_value": "2023-01-01T00:00:00Z"
            }
        }
    }
}

await adapter.set_state("postgres-to-snowflake", state_data)

# Retrieve state
state = await adapter.get_state("postgres-to-snowflake")
if state:
    print(f"Last updated: {state.last_updated}")

# List all states
states = await adapter.list_states()
print(f"Available states: {states}")
```

## Configuration Templates

### Available Templates

```python
templates = MeltanoAdapterFactory.get_available_templates()

# Configuration templates
print("Config Templates:")
for name, config in templates["config_templates"].items():
    print(f"  - {name}: {config['state_backend']} backend")

# Plugin templates
print("Plugin Templates:")
for name, config in templates["plugin_templates"].items():
    print(f"  - {name}: {config['description']}")
```

### Configuration Templates

- **development**: Local development with systemdb backend
- **production**: Production-ready with S3 backend and extended timeouts
- **data_lake**: Optimized for large data transfers with extended timeouts
- **real_time**: Optimized for streaming with Redis backend

### Plugin Templates

- **postgres_to_snowflake**: PostgreSQL → Snowflake pipeline
- **mysql_to_bigquery**: MySQL → BigQuery pipeline
- **salesforce_to_warehouse**: Salesforce → Data warehouse
- **api_to_lake**: REST APIs → Data lake
- **files_to_warehouse**: Files → Data warehouse

## Environment Configuration

```bash
# Environment variables
export MELTANO_PROJECT_ROOT="/path/to/project"
export MELTANO_CONFIG_TEMPLATE="production"
export MELTANO_STATE_BACKEND="s3"
export MELTANO_TIMEOUT="600"
export AIRFLOW_DAGS_DIRECTORY="/opt/airflow/dags"

# Create adapter from environment
adapter = MeltanoAdapterFactory.create_from_environment()
```

## CRUD Interface

The Meltano adapter implements the standard FLX CRUD interface:

```python
# Plugin management via CRUD
await adapter.set("plugin:tap-postgres", {"host": "new-host"})
config = await adapter.get("plugin:tap-postgres")
exists = await adapter.exists("plugin:tap-postgres")
await adapter.delete("plugin:tap-postgres")

# State management via CRUD
await adapter.set("state:pipeline-1", state_data)
state = await adapter.get("state:pipeline-1")
await adapter.delete("state:pipeline-1")

# Workflow management via CRUD
await adapter.set("workflow:daily-pipeline", workflow_config)
workflow = await adapter.get("workflow:daily-pipeline")
```

## Advanced Features

### Custom Plugin Installation

```python
# Install plugin with specific variant and configuration
plugin_config = MeltanoPluginConfig(
    name="tap-github",
    plugin_type="extractors",
    namespace="tap_github",
    variant="meltanolabs",  # Specific variant
    settings={
        "repositories": ["owner/repo1", "owner/repo2"],
        "auth_token": "your_token",
    },
    env={
        "GITHUB_API_URL": "https://api.github.com",
    }
)

await adapter.install_plugin(plugin_config)
```

### Plugin Testing

```python
# Test plugin configuration
test_result = await adapter.test_plugin("tap-postgres")
if test_result["test_passed"]:
    print("✅ Plugin test passed")
else:
    print(f"❌ Plugin test failed: {test_result['errors']}")
```

### Batch Operations

```python
# Install multiple plugins
plugins = [
    MeltanoPluginConfig(name="tap-postgres", plugin_type="extractors", ...),
    MeltanoPluginConfig(name="target-snowflake", plugin_type="loaders", ...),
    MeltanoPluginConfig(name="dbt-snowflake", plugin_type="transformers", ...),
]

for plugin in plugins:
    await adapter.install_plugin(plugin)
    print(f"✅ Installed {plugin.name}")
```

## Error Handling

```python
from flx.core.exceptions import (
    ConfigurationError,
    ConnectionError,
    OperationError,
)

try:
    await adapter.install_plugin(plugin_config)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
except OperationError as e:
    print(f"Operation error: {e}")
```

## Monitoring and Observability

```python
# Health check
health = await adapter.health_check()
print(f"Status: {health['status']}")
print(f"Meltano version: {health['meltano_version']}")

# System information
info = await adapter.get_system_info()
print(f"System info: {info['system_info']}")

# Plugin execution with monitoring
result = await adapter.execute_plugin(
    plugin_name="tap-postgres",
    command="discover",
)
print(f"Execution time: {result['execution_time']}s")
```

## Best Practices

### 1. **Project Organization**

```
meltano_projects/
├── dev/
│   ├── meltano.yml
│   └── workflows/
├── staging/
│   ├── meltano.yml
│   └── workflows/
└── prod/
    ├── meltano.yml
    └── workflows/
```

### 2. **Configuration Management**

- Use environment variables for sensitive data
- Separate configurations per environment
- Version control your workflows and configurations

### 3. **State Management**

- Use consistent state IDs across environments
- Regular state backups for production
- Monitor state growth and cleanup old states

### 4. **Error Recovery**

- Implement retry logic for transient failures
- Use circuit breaker patterns for external services
- Monitor pipeline health and set up alerts

### 5. **Performance Optimization**

- Use appropriate batch sizes for data transfers
- Configure timeouts based on data volume
- Monitor resource usage and scale accordingly

## Integration with Existing FLX Components

### With Database Adapters

```python
from flx.adapters.outbound.database import DatabaseAdapter

# Use with existing database adapters
db_adapter = DatabaseAdapter(config)
meltano_adapter = MeltanoAdapterFactory.create_adapter(project_root)

# Coordinate between adapters in application services
```

### With CLI Interface

```python
from flx.adapters.inbound.cli import CliAdapter

# Expose Meltano functionality through FLX CLI
cli_adapter = CliAdapter()
# Register Meltano commands with CLI adapter
```

### With Application Services

```python
from flx.application import ApplicationService

class DataPipelineService(ApplicationService):
    def __init__(self, meltano_adapter: MeltanoAdapter):
        self.meltano = meltano_adapter

    async def run_daily_pipeline(self):
        result = await self.meltano.run_elt_pipeline(
            extractor="tap-postgres",
            loader="target-snowflake",
            state_id="daily-pipeline"
        )
        return result
```

## Troubleshooting

### Common Issues

1. **Meltano not found**

   ```bash
   # Install Meltano
   pip install meltano

   # Or specify path
   export MELTANO_EXECUTABLE="/path/to/meltano"
   ```

2. **Plugin installation fails**

   ```python
   # Check plugin availability
   plugins = await adapter.discover_plugins(search_term="postgres")

   # Verify plugin name and variant
   plugin_config = MeltanoPluginConfig(
       name="pipelinewise-tap-postgres",  # Full name
       variant="transferwise",  # Specific variant
       ...
   )
   ```

3. **State backend issues**

   ```python
   # Verify state backend configuration
   health = await adapter.health_check()
   print(health["project_status"])

   # Test state operations
   await adapter.set_state("test", {"test": True})
   ```

4. **Airflow deployment issues**

   ```python
   # Verify Airflow configuration
   airflow_config = {
       "dags_directory": "/correct/path/to/dags",
       "webserver_host": "localhost",
       "webserver_port": 8080,
   }
   ```

## Examples Repository

Complete examples are available in:

- `examples/flx_meltano_integration_example.py` - Comprehensive usage examples
- `flx/tests/test_meltano_integration.py` - Test cases and patterns

## API Reference

### Ports

- `MeltanoUnifiedPort` - Complete Meltano functionality
- `MeltanoPluginManagerPort` - Plugin management
- `MeltanoPluginExecutorPort` - Plugin execution
- `MeltanoStateManagerPort` - State management
- `MeltanoWorkflowOrchestratorPort` - Workflow orchestration
- `MeltanoAirflowIntegrationPort` - Airflow integration

### Adapters

- `MeltanoAdapter` - Main adapter implementation
- `MeltanoAdapterFactory` - Factory for creating adapters

### Models

- `MeltanoPluginConfig` - Plugin configuration
- `MeltanoPluginState` - Plugin state
- `MeltanoWorkflowConfig` - Workflow configuration
- `MeltanoAdapterConfig` - Adapter configuration

This integration brings the full power of the Meltano ecosystem into the FLX framework while maintaining clean architecture principles and enterprise-grade reliability.

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Integration Overview](./index.md) - Understanding integration patterns and strategies
- [Architecture Overview](../../architecture/index.md) - FLX hexagonal architecture fundamentals
- [Getting Started](../../getting-started/index.md) - FLX Framework installation and setup

### **Next Steps**

- [Data Pipeline Patterns](../data-patterns/index.md) - Advanced data pipeline implementation patterns
- [Workflow Orchestration](../orchestration/index.md) - Workflow orchestration strategies
- [Meltano Plugins](../../meltano-plugins/index.md) - Complete Meltano plugin ecosystem

### **Related Topics**

- [Architecture Evolution](../../architecture/flx-2.0-architecture.md) - FLX 2.0 Meltano-powered architecture
- [API Reference](../../api-reference/meltano/index.md) - Complete Meltano integration API
- [Performance Optimization](../../optimization/meltano/index.md) - Meltano performance tuning

---

## 🆘 **Troubleshooting**

### **Common Issues**

For Meltano integration issues:

1. Verify Meltano installation and plugin availability
2. Check project configuration and environment setup
3. Test adapter connectivity and plugin functionality
4. Review state management and workflow orchestration

### **Additional Resources**

- [Meltano Documentation](https://docs.meltano.com/) - Official Meltano documentation
- [Integration Examples](../../examples/meltano/index.md) - Working Meltano integration examples
- [Support Resources](../../getting-started/support.md) - Getting help with integration issues

---

**📂 Hub**: [Integration Guides](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-19
