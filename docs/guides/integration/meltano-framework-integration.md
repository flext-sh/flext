# Meltano Framework Integration

> **Integrating Meltano's declarative code-first data integration engine with FLX framework**

## Overview

Meltano is a declarative code-first data integration engine that unlocks 600+ APIs and databases. When integrated with the FLX framework, it provides powerful capabilities for enterprise data pipelines while maintaining hexagonal architecture principles.

## What is Meltano?

Meltano eliminates the need to write, maintain, and scale custom API integrations. It provides:

- **Declarative Configuration**: Define your entire data pipeline in code
- **600+ Connectors**: Pre-built integrations for APIs and databases
- **Code-First Approach**: Version control your data pipelines
- **Production Ready**: Battle-tested in enterprise environments

## Integration with FLX Framework

### Adapter Pattern Implementation

```python
from flext.adapters.base import BaseAdapter
from meltano.core.project import Project
from typing import Dict, Any, List

class MeltanoAdapter(BaseAdapter):
    """FLX adapter for Meltano integration."""

    def __init__(self, project_dir: str):
        self.project = Project(project_dir)

    async def run_extraction(self, tap: str, target: str) -> bool:
        """Run Meltano ELT pipeline through FLX adapter."""
        try:
            result = await self.project.run([tap, target])
            return result.success
        except Exception as e:
            await self.handle_error(e)
            return False

    async def list_available_taps(self) -> List[str]:
        """List available extractors in Meltano project."""
        return [plugin.name for plugin in self.project.plugins.extractors()]

    async def list_available_targets(self) -> List[str]:
        """List available loaders in Meltano project."""
        return [plugin.name for plugin in self.project.plugins.loaders()]
```

### FLX Configuration Integration

```python
from flext.core.config import Config
from meltano.core.project_add_service import ProjectAddService

class FLXMeltanoConfig(Config):
    """FLX configuration for Meltano integration."""

    meltano_project_dir: str = "./meltano"
    auto_discover_plugins: bool = True
    plugin_install_timeout: int = 300

    async def setup_meltano_project(self):
        """Initialize Meltano project with FLX integration."""
        project = Project(self.meltano_project_dir)

        # Add common extractors
        add_service = ProjectAddService(project)
        await add_service.add(plugin_type="extractors", plugin_name="tap-postgres")
        await add_service.add(plugin_type="loaders", plugin_name="target-postgres")
```

## Project Structure

```
meltano/
├── meltano.yml                   # Meltano project configuration
├── plugins/                     # Custom plugins
│   ├── extractors/
│   ├── loaders/
│   └── transformers/
├── transform/                   # dbt transformations
├── notebooks/                  # Jupyter notebooks
└── orchestrate/                # Airflow DAGs
```

## Configuration Example

```yaml
# meltano.yml
version: 1
default_environment: dev
project_id: flext-meltano-integration

environments:
  - name: dev
  - name: staging
  - name: prod

plugins:
  extractors:
    - name: tap-postgres
      variant: meltanolabs
      pip_url: pipelinewise-tap-postgres
      config:
        host: localhost
        port: 5432
        user: postgres
        password: ${POSTGRES_PASSWORD}
        dbname: flext_data

  loaders:
    - name: target-postgres
      variant: meltanolabs
      pip_url: pipelinewise-target-postgres
      config:
        host: localhost
        port: 5432
        user: postgres
        password: ${POSTGRES_PASSWORD}
        dbname: flext_warehouse

  transforms:
    - name: dbt-postgres
      variant: dbt-labs
      pip_url: dbt-core~=1.0.0 dbt-postgres~=1.0.0
```

## Integration Patterns

### 1. ELT Pipeline with FLX

```python
from flext.core.application import Application
from flext.adapters.meltano import MeltanoAdapter

class DataPipelineApplication(Application):
    """FLX application with Meltano integration."""

    def __init__(self):
        super().__init__()
        self.meltano_adapter = MeltanoAdapter("./meltano")

    async def run_data_pipeline(self, source: str, destination: str):
        """Execute data pipeline using Meltano."""
        # Extract and Load
        success = await self.meltano_adapter.run_extraction(
            tap=f"tap-{source}",
            target=f"target-{destination}"
        )

        if success:
            # Transform using dbt
            await self.meltano_adapter.run_transform()

        return success
```

### 2. Custom Plugin Development

```python
from singer_sdk import Tap, Target
from flext.adapters.base import BaseAdapter

class FLXCustomTap(Tap):
    """Custom tap integrated with FLX framework."""

    name = "tap-flext-custom"

    def __init__(self, flext_adapter: BaseAdapter):
        super().__init__()
        self.flext_adapter = flext_adapter

    def discover_streams(self):
        """Discover streams using FLX adapter."""
        return self.flext_adapter.discover_entities()
```

### 3. Orchestration with FLX

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from flext.core.orchestration import TaskOrchestrator

def run_flext_meltano_pipeline(**context):
    """Airflow task for FLX-Meltano pipeline."""
    orchestrator = TaskOrchestrator()

    # Run Meltano pipeline through FLX
    result = await orchestrator.run_pipeline(
        pipeline_name="customer_data_sync",
        source="crm_api",
        destination="data_warehouse"
    )

    return result.success

dag = DAG(
    'flext_meltano_integration',
    schedule_interval='@daily',
    catchup=False
)

pipeline_task = PythonOperator(
    task_id='run_data_pipeline',
    python_callable=run_flext_meltano_pipeline,
    dag=dag
)
```

## Development Workflow

### 1. Setup Integration

```bash
# Initialize FLX project with Meltano
flext init --with-meltano

# Install Meltano
pip install meltano

# Initialize Meltano project
meltano init meltano_project
```

### 2. Add Plugins

```bash
# Add extractor
meltano add extractor tap-postgres

# Add loader
meltano add loader target-postgres

# Add transformer
meltano add transformer dbt-postgres
```

### 3. Configure with FLX

```bash
# Generate FLX configuration
flext config generate --meltano ./meltano

# Set environment variables
export MELTANO_PROJECT_ROOT=./meltano
export FLX_MELTANO_INTEGRATION=true
```

### 4. Run Pipeline

```bash
# Run through Meltano CLI
meltano run tap-postgres target-postgres

# Run through FLX CLI
flext pipeline run --meltano customer_sync

# Run with orchestration
flext orchestrate --dag meltano_daily_sync
```

## Monitoring and Observability

### Logging Integration

```python
from flext.core.logging import get_logger
from meltano.core.logging import configure_logging

# Configure unified logging
logger = get_logger(__name__)
configure_logging(level="INFO", format="structured")

# Log pipeline execution
logger.info("Starting Meltano pipeline", extra={
    "pipeline": "customer_sync",
    "extractor": "tap-postgres",
    "loader": "target-postgres"
})
```

### Metrics Collection

```python
from flext.core.metrics import MetricsCollector

metrics = MetricsCollector()

# Track pipeline metrics
metrics.track_pipeline_execution(
    pipeline_name="customer_sync",
    duration=pipeline_duration,
    records_processed=record_count,
    success=pipeline_success
)
```

## Best Practices

### 1. Environment Management

- Use separate Meltano environments for dev/staging/prod
- Integrate with FLX environment configuration
- Secure credential management through FLX adapters

### 2. Error Handling

- Implement FLX error handling patterns
- Use structured logging for debugging
- Set up alerting for pipeline failures

### 3. Performance Optimization

- Leverage FLX async capabilities
- Use incremental extraction where possible
- Implement proper resource management

## Related Documentation

- [Singer SDK Integration](singer-sdk-integration.md)
- [Meltano Plugins Integration](meltano-plugins-integration.md)
- [FLX Orchestration Guide](../architecture/orchestration-patterns.md)
- [Data Pipeline Architecture](../architecture/data-pipeline-patterns.md)

## External Resources

- [Meltano Documentation](https://docs.meltano.com/)
- [Meltano Hub](https://hub.meltano.com/)
- [Singer Specification](https://hub.meltano.com/singer/spec)
- [Meltano Contributing Guide](https://docs.meltano.com/contribute/)
