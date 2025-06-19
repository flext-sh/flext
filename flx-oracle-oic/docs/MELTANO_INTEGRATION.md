# Meltano Integration Guide

> **tap-oic Version**: 2.0
> **Last Updated**: June 15, 2025
> **Meltano Version**: 2.x

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Advanced Features](#advanced-features)
5. [Scheduling and Orchestration](#scheduling-and-orchestration)
6. [Integration Management](#integration-management)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

Meltano is an open-source data integration platform that works seamlessly with tap-oic. This guide covers:

- Setting up tap-oic with Meltano
- Configuring pipelines for OIC data extraction and monitoring
- Managing OIC integrations through Meltano workflows
- Orchestrating complex data workflows

## Quick Start

### 1. Install Meltano

```bash
# Install Meltano
pip install meltano

# Create new project
meltano init my-oic-project
cd my-oic-project
```

### 2. Add tap-oic

```bash
# Add tap-oic from Meltano Hub
meltano add extractor tap-oic

# Or add from custom source
meltano add extractor tap-oic --from-ref https://github.com/your-org/tap-oic.git
```

### 3. Configure tap-oic

```bash
# OAuth2 is the recommended authentication method for OIC
meltano config tap-oic set base_url https://your-instance.integration.ocp.oraclecloud.com
meltano config tap-oic set auth_method oauth2
meltano config tap-oic set oauth_client_id your-client-id
meltano config tap-oic set --interactive oauth_client_secret
meltano config tap-oic set oauth_token_url https://idcs.identity.oraclecloud.com/oauth2/v1/token

# Or use environment variables
export TAP_OIC_BASE_URL="https://your-instance.integration.ocp.oraclecloud.com"
export TAP_OIC_AUTH_METHOD="oauth2"
export TAP_OIC_OAUTH_CLIENT_ID="your-client-id"
export TAP_OIC_OAUTH_CLIENT_SECRET="your-client-secret"
export TAP_OIC_OAUTH_TOKEN_URL="https://idcs.identity.oraclecloud.com/oauth2/v1/token"
```

### 4. Test Connection

```bash
# Test extraction
meltano invoke tap-oic --discover

# Run a test extraction
meltano run tap-oic target-jsonl
```

## Configuration

### Complete meltano.yml Example

```yaml
version: 1
default_environment: prod
project_id: oic-data-platform

environments:
  - name: prod
    config:
      tap-oic:
        base_url: ${OIC_PROD_URL}
        auth_method: oauth2
        oauth_client_id: ${OIC_PROD_CLIENT_ID}
        oauth_client_secret: ${OIC_PROD_CLIENT_SECRET}
        oauth_token_url: ${OIC_PROD_TOKEN_URL}
  - name: dev
    config:
      tap-oic:
        base_url: ${OIC_DEV_URL}
        auth_method: oauth2
        oauth_client_id: ${OIC_DEV_CLIENT_ID}
        oauth_client_secret: ${OIC_DEV_CLIENT_SECRET}
        oauth_token_url: ${OIC_DEV_TOKEN_URL}

plugins:
  extractors:
    - name: tap-oic
      namespace: tap_oic
      pip_url: tap-oic>=2.0.0
      executable: tap-oic
      capabilities:
        - catalog
        - discover
        - state
      config:
        start_date: "2025-01-01T00:00:00Z"
        page_size: 200
        request_timeout: 300
        max_retries: 3
      select:
        # Extract all integration data
        - integrations.*
        - connections.*
        - projects.*
        # Extract monitoring data
        - executions.*
        - metrics.*
        - errors.*
        # Exclude large message payloads
        - "!message_payloads.*"
      metadata:
        integrations:
          replication-method: INCREMENTAL
          replication-key: modifiedTime
        executions:
          replication-method: INCREMENTAL
          replication-key: startTime

  loaders:
    - name: target-postgres
      namespace: target_postgres
      pip_url: pipelinewise-target-postgres
      executable: target-postgres
      config:
        host: localhost
        port: 5432
        user: postgres
        password: ${POSTGRES_PASSWORD}
        dbname: oic_analytics
        default_target_schema: oic_raw

    - name: target-snowflake
      namespace: target_snowflake
      pip_url: pipelinewise-target-snowflake
      executable: target-snowflake
      config:
        account: ${SNOWFLAKE_ACCOUNT}
        dbname: OIC_ANALYTICS
        user: ${SNOWFLAKE_USER}
        password: ${SNOWFLAKE_PASSWORD}
        warehouse: COMPUTE_WH
        default_target_schema: OIC_RAW

  transformers:
    - name: dbt-postgres
      namespace: dbt_postgres
      pip_url: dbt-postgres~=1.7.0
      executable: dbt
      config:
        project_dir: transform
        profiles_dir: transform/profiles

schedules:
  - name: oic-hourly-sync
    interval: "@hourly"
    job: oic-to-warehouse

  - name: oic-daily-metrics
    interval: "0 2 * * *" # 2 AM daily
    job: oic-metrics-pipeline

jobs:
  - name: oic-to-warehouse
    tasks:
      - tap-oic target-postgres
      - dbt-postgres:run
      - dbt-postgres:test

  - name: oic-metrics-pipeline
    tasks:
      - tap-oic target-snowflake
      - run: python scripts/generate_metrics_report.py
      - run: python scripts/send_alerts.py

  - name: manage-oic-integrations
    tasks:
      - run: python scripts/import_integration_archives.py
      - tap-oic target-postgres # Extract to verify import
```

### Stream Selection

```yaml
# Select specific streams and fields
select:
  # Include all fields from integrations
  - integrations.*

  # Include specific fields from connections
  - connections.id
  - connections.name
  - connections.adapterType
  - connections.status

  # Include all execution data except large payloads
  - executions.*
  - "!executions.request_payload"
  - "!executions.response_payload"

  # Exclude entire streams
  - "!lookups.*"
  - "!certificates.*"
```

### Advanced Configuration

```yaml
config:
  # OAuth2 Authentication (Recommended)
  base_url: ${OIC_BASE_URL}
  auth_method: oauth2
  oauth_client_id: ${OIC_CLIENT_ID}
  oauth_client_secret: ${OIC_CLIENT_SECRET}
  oauth_token_url: ${OIC_TOKEN_URL}

  # Performance tuning
  page_size: 500
  request_timeout: 600
  max_retries: 5
  retry_delay: 60
  connection_pool_size: 20

  # Data filtering
  start_date: "2025-01-01T00:00:00Z"
  end_date: "2025-12-31T23:59:59Z"

  # State management
  state_backend:
    type: redis
    url: ${REDIS_URL}
    key_prefix: tap_oic_state

  # Advanced options
  verify_ssl: true
  user_agent: "Meltano/2.0 tap-oic/2.0"
  compression: gzip

  # Stream-specific options
  stream_options:
    executions:
      lookback_days: 7
      include_failed_only: false
    metrics:
      aggregation_interval: hourly
      include_zero_values: false
```

## Advanced Features

### 1. Custom Extractor Variants

Create variants for different use cases:

```yaml
plugins:
  extractors:
    # Full extraction variant
    - name: tap-oic
      variant: full
      config:
        page_size: 1000
      select:
        - "*.*" # Select everything

    # Monitoring-only variant
    - name: tap-oic
      variant: monitoring
      config:
        page_size: 500
      select:
        - executions.*
        - metrics.*
        - errors.*

    # Metadata-only variant
    - name: tap-oic
      variant: metadata
      select:
        - integrations.*
        - connections.*
        - projects.*
```

### 2. Multi-Environment Pipelines

```yaml
environments:
  - name: prod
    config:
      tap-oic:
        base_url: ${OIC_PROD_URL}
        oauth_client_id: ${OIC_PROD_CLIENT_ID}
      target-postgres:
        dbname: oic_prod

  - name: staging
    config:
      tap-oic:
        base_url: ${OIC_STAGING_URL}
        oauth_client_id: ${OIC_STAGING_CLIENT_ID}
      target-postgres:
        dbname: oic_staging

  - name: dev
    config:
      tap-oic:
        base_url: ${OIC_DEV_URL}
        oauth_client_id: ${OIC_DEV_CLIENT_ID}
        page_size: 100 # Smaller for dev
      target-postgres:
        dbname: oic_dev
# Run in specific environment
# meltano --environment=prod run tap-oic target-postgres
```

### 3. Dynamic Pipeline Generation

```python
# scripts/generate_dynamic_pipeline.py
import yaml
import os
from meltano.core.project import Project

def generate_pipeline_for_tenant(tenant_id, tenant_config):
    """Generate Meltano pipeline for specific tenant"""

    project = Project.find()

    # Add tenant-specific extractor
    extractor_config = {
        'name': f'tap-oic-{tenant_id}',
        'inherit_from': 'tap-oic',
        'config': {
            'base_url': tenant_config['oic_url'],
            'oauth_client_id': tenant_config['client_id'],
            'oauth_client_secret': os.environ[f'OIC_CLIENT_SECRET_{tenant_id.upper()}']
        },
        'select': tenant_config.get('streams', ['*.*'])
    }

    # Add to meltano.yml
    with open('meltano.yml', 'r') as f:
        meltano_config = yaml.safe_load(f)

    meltano_config['plugins']['extractors'].append(extractor_config)

    # Add job
    job = {
        'name': f'sync-{tenant_id}',
        'tasks': [
            f'tap-oic-{tenant_id} target-postgres',
            f'dbt-postgres:run --models +tag:{tenant_id}'
        ]
    }
    meltano_config['jobs'].append(job)

    # Save updated config
    with open('meltano.yml', 'w') as f:
        yaml.dump(meltano_config, f, default_flow_style=False)

    print(f"Generated pipeline for tenant: {tenant_id}")

# Usage
tenants = {
    'acme': {
        'oic_url': 'https://acme.integration.ocp.oraclecloud.com',
        'client_id': 'acme-client-id',
        'streams': ['integrations.*', 'executions.*']
    },
    'globex': {
        'oic_url': 'https://globex.integration.ocp.oraclecloud.com',
        'client_id': 'globex-client-id',
        'streams': ['*.*']
    }
}

for tenant_id, config in tenants.items():
    generate_pipeline_for_tenant(tenant_id, config)
```

## Scheduling and Orchestration

### 1. Basic Scheduling

```yaml
schedules:
  # Hourly sync of all data
  - name: hourly-sync
    interval: "@hourly"
    job: oic-to-warehouse

  # Daily metrics at 2 AM
  - name: daily-metrics
    interval: "0 2 * * *"
    job: metrics-pipeline

  # Every 15 minutes for real-time monitoring
  - name: realtime-monitoring
    interval: "*/15 * * * *"
    job: monitoring-sync

  # Weekly full refresh
  - name: weekly-full-refresh
    interval: "0 0 * * 0" # Sunday midnight
    job: full-refresh-pipeline
```

### 2. Complex Orchestration

```yaml
jobs:
# Sequential pipeline with dependencies
- name: complete-etl-pipeline
  tasks:
  # Extract from multiple sources
  - tap-oic target-postgres
  - tap-salesforce target-postgres
  - tap-mysql target-postgres

  # Transform all data
  - dbt-postgres:snapshot
  - dbt-postgres:run
  - dbt-postgres:test

  # Generate reports
  - run: python scripts/generate_executive_dashboard.py
  - run: python scripts/send_notifications.py

# Parallel extraction
- name: parallel-extraction
  tasks:
  - - tap-oic variant:monitoring target-postgres
    - tap-oic variant:metadata target-postgres
    - tap-oic variant:analytics target-postgres
  - dbt-postgres:run --models +tag:consolidated

# Conditional execution
- name: conditional-pipeline
  tasks:
  - tap-oic target-postgres
  - run: python scripts/check_data_quality.py
  - dbt-postgres:run
    if: $MELTANO_RUN_ID
  - run: python scripts/alert_on_failure.py
    if: failure
```

### 3. Airflow Integration

```python
# dags/meltano_oic_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'oic_data_pipeline',
    default_args=default_args,
    description='OIC Data Pipeline via Meltano',
    schedule_interval='@hourly',
    catchup=False
)

# Extract OIC data
extract_oic = BashOperator(
    task_id='extract_oic_data',
    bash_command='cd /opt/meltano && meltano run tap-oic target-postgres',
    dag=dag
)

# Run transformations
transform_data = BashOperator(
    task_id='transform_data',
    bash_command='cd /opt/meltano && meltano run dbt-postgres:run',
    dag=dag
)

# Import integration archives
import_integrations = BashOperator(
    task_id='import_integrations',
    bash_command='cd /opt/meltano && meltano run manage-oic-integrations',
    dag=dag
)

# Set dependencies
extract_oic >> transform_data >> import_integrations
```

## Integration Management

### 1. Import Integration Archives to OIC

```python
# scripts/import_integration_archives.py
"""
Import pre-built integration archives (.iar files) to OIC
"""

import os
import yaml
from tap_oic import OICManagementClient

def load_meltano_config():
    """Load Meltano configuration"""
    with open('meltano.yml') as f:
        return yaml.safe_load(f)

def import_integration_archives():
    """Import integration archives based on Meltano pipelines"""

    # Initialize OIC client
    oic_client = OICManagementClient({
        'base_url': os.environ['OIC_BASE_URL'],
        'auth_method': 'oauth2',
        'oauth_client_id': os.environ['OIC_CLIENT_ID'],
        'oauth_client_secret': os.environ['OIC_CLIENT_SECRET'],
        'oauth_token_url': os.environ['OIC_TOKEN_URL']
    })

    # Load Meltano config
    config = load_meltano_config()

    # Directory containing integration archives
    archives_dir = 'oic_integrations/'

    # Import archives for each Meltano job
    for job in config.get('jobs', []):
        archive_name = f"{job['name']}.iar"
        archive_path = os.path.join(archives_dir, archive_name)

        if os.path.exists(archive_path):
            print(f"Importing archive: {archive_name}")

            # Import the integration archive
            try:
                result = oic_client.import_integration_archive(archive_path)
                integration_id = result['id']
                print(f"Imported integration: {integration_id}")

                # Activate if configured
                if job.get('auto_activate', True):
                    oic_client.activate_integration(integration_id)
                    print(f"Activated integration: {integration_id}")

            except Exception as e:
                print(f"Failed to import {archive_name}: {e}")
        else:
            print(f"Archive not found: {archive_path}")
            print("Note: OIC integrations can be created via REST API or Visual Designer")

if __name__ == '__main__':
    import_integration_archives()
```

### 2. Sync Meltano and OIC Configurations

```python
# scripts/sync_meltano_oic.py
"""
Keep Meltano and OIC configurations in sync
"""

import yaml
from tap_oic import TapOIC, OICManagementClient

class MeltanoOICSync:
    """Synchronize Meltano and OIC configurations"""

    def __init__(self, meltano_config_path, oic_config):
        self.meltano_config_path = meltano_config_path
        self.tap = TapOIC(oic_config)
        self.mgmt_client = OICManagementClient(oic_config)

    def sync_from_oic_to_meltano(self):
        """Update Meltano config based on OIC integrations"""

        # Discover OIC streams
        catalog = self.tap.discover()

        # Load Meltano config
        with open(self.meltano_config_path) as f:
            meltano_config = yaml.safe_load(f)

        # Update tap-oic selection based on available streams
        tap_oic_config = next(
            e for e in meltano_config['plugins']['extractors']
            if e['name'] == 'tap-oic'
        )

        # Update select patterns
        tap_oic_config['select'] = [
            f"{stream['stream']}.*"
            for stream in catalog['streams']
        ]

        # Save updated config
        with open(self.meltano_config_path, 'w') as f:
            yaml.dump(meltano_config, f, default_flow_style=False)

        print(f"Updated Meltano config with {len(catalog['streams'])} streams")

    def export_integrations_for_meltano_jobs(self):
        """Export OIC integrations that correspond to Meltano jobs"""

        with open(self.meltano_config_path) as f:
            meltano_config = yaml.safe_load(f)

        exports_dir = 'oic_integrations/'
        os.makedirs(exports_dir, exist_ok=True)

        # Get all integrations from OIC
        integrations = self.mgmt_client.list_integrations()

        for job in meltano_config.get('jobs', []):
            # Find matching integration in OIC
            matching_integration = self._find_matching_integration(job, integrations)

            if matching_integration:
                # Export the integration
                export_path = os.path.join(exports_dir, f"{job['name']}.iar")
                self.mgmt_client.export_integration(
                    matching_integration['id'],
                    export_path
                )
                print(f"Exported integration for job {job['name']} to {export_path}")

    def _find_matching_integration(self, job, integrations):
        """Find OIC integration that matches Meltano job"""
        # Look for integration with similar name or description
        job_name = job['name'].replace('-', '_').upper()

        for integration in integrations:
            if job_name in integration['name'].upper():
                return integration

        return None

# Usage
sync = MeltanoOICSync('meltano.yml', {
    'base_url': os.environ['OIC_BASE_URL'],
    'auth_method': 'oauth2',
    'oauth_client_id': os.environ['OIC_CLIENT_ID'],
    'oauth_client_secret': os.environ['OIC_CLIENT_SECRET'],
    'oauth_token_url': os.environ['OIC_TOKEN_URL']
})

# Sync configuration from OIC to Meltano
sync.sync_from_oic_to_meltano()
```

## Best Practices

### 1. Environment Management

```bash
# .env file (git-ignored)
OIC_PROD_URL=https://prod.integration.ocp.oraclecloud.com
OIC_PROD_CLIENT_ID=prod-client-id
OIC_PROD_CLIENT_SECRET=secure-client-secret
OIC_PROD_TOKEN_URL=https://idcs.identity.oraclecloud.com/oauth2/v1/token

OIC_DEV_URL=https://dev.integration.ocp.oraclecloud.com
OIC_DEV_CLIENT_ID=dev-client-id
OIC_DEV_CLIENT_SECRET=dev-client-secret
OIC_DEV_TOKEN_URL=https://idcs.identity.oraclecloud.com/oauth2/v1/token

# Use different environments
meltano --environment=prod run tap-oic target-postgres
meltano --environment=dev run tap-oic target-jsonl
```

### 2. State Management

```yaml
# Enable state persistence
plugins:
  extractors:
    - name: tap-oic
      config:
        state_backend:
          type: s3
          bucket: meltano-state
          key_prefix: tap-oic/
          region: us-east-1
```

### 3. Error Handling

```yaml
jobs:
- name: resilient-pipeline
  tasks:
  # Main extraction with error handling
  - tap-oic target-postgres
    retry:
      times: 3
      delay: 300  # 5 minutes

  # Check data quality
  - run: python scripts/validate_data.py
    continue_on_failure: false

  # Transform only if validation passes
  - dbt-postgres:run

  # Always run cleanup
  - run: python scripts/cleanup.py
    always_run: true
```

### 4. Performance Optimization

```yaml
# Optimize for large datasets
config:
  # Increase page size for bulk extraction
  page_size: 1000

  # Enable streaming to reduce memory usage
  stream_results: true

  # Use connection pooling
  connection_pool_size: 20

  # Enable compression
  compression: gzip

# Parallel processing
jobs:
  - name: parallel-extraction
    tasks:
      # Run multiple variants in parallel
      - - tap-oic variant:integrations target-postgres
        - tap-oic variant:connections target-postgres
        - tap-oic variant:executions target-postgres
```

### 5. Monitoring and Alerting

```python
# scripts/monitor_pipeline.py
import os
from datetime import datetime, timedelta
import requests

def check_pipeline_health():
    """Monitor Meltano pipeline health"""

    # Check last successful run
    last_run = get_last_successful_run()

    if datetime.now() - last_run > timedelta(hours=2):
        send_alert("Pipeline hasn't run successfully in 2 hours")

    # Check data freshness
    latest_data = check_data_freshness()

    if datetime.now() - latest_data > timedelta(hours=4):
        send_alert("Data is stale - last update was 4 hours ago")

    # Check for errors
    error_count = get_error_count()

    if error_count > 10:
        send_alert(f"High error count: {error_count} errors in last hour")

def send_alert(message):
    """Send alert to Slack"""
    webhook_url = os.environ['SLACK_WEBHOOK_URL']

    requests.post(webhook_url, json={
        'text': f'🚨 Meltano Pipeline Alert: {message}'
    })
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

```bash
# Test authentication
meltano invoke tap-oic --config | jq .

# Check environment variables
meltano config tap-oic list

# Set config interactively
meltano config tap-oic set --interactive password
```

#### 2. State Management Issues

```bash
# Reset state
meltano state clear tap-oic

# View current state
meltano state get tap-oic

# Set specific state
meltano state set tap-oic '{"bookmarks": {"integrations": {"replication_key_value": "2025-01-01T00:00:00Z"}}}'
```

#### 3. Performance Problems

```bash
# Run with profiling
meltano --log-level=debug run tap-oic target-jsonl

# Test with limited records
meltano invoke tap-oic --config | head -100 | meltano invoke target-jsonl

# Check resource usage
meltano run tap-oic target-postgres --monitor
```

#### 4. Schema Mismatches

```bash
# Refresh catalog
meltano invoke tap-oic --discover > catalog.json

# Reset schema in target
meltano invoke target-postgres --drop-schema
meltano invoke target-postgres --create-schema
```

### Debug Commands

```bash
# Test tap configuration
meltano invoke tap-oic --config

# Discover available streams
meltano invoke tap-oic --discover | jq '.streams[].stream'

# Test specific stream
meltano invoke tap-oic --catalog catalog.json --state state.json | grep '"stream":"integrations"' | head -5

# Validate pipeline
meltano run --dry-run tap-oic target-postgres

# Check logs
tail -f logs/meltano.log

# Run with debugging
MELTANO_LOG_LEVEL=debug meltano run tap-oic target-postgres
```

## Summary

This guide covers comprehensive Meltano integration with tap-oic, including:

1. **Setup and Configuration** - Getting started with Meltano and tap-oic using OAuth2 authentication
2. **Advanced Features** - Multi-environment, variants, and dynamic pipelines
3. **Orchestration** - Scheduling and complex workflow management
4. **Integration Management** - Importing and managing OIC integration archives
5. **Best Practices** - Environment management, state handling, and monitoring
6. **Troubleshooting** - Common issues and debug techniques

Key Points:

- tap-oic is a Singer tap for extracting data from OIC, not for creating integrations
- OIC integrations can be created via REST API or Visual Designer, with .iar files for portability
- OAuth2 is the recommended authentication method for OIC
- Meltano provides excellent orchestration for OIC data extraction pipelines

For more information, refer to:

- [Meltano Documentation](https://docs.meltano.com)
- [tap-oic Documentation](README.md)
- [Singer Specification](https://hub.meltano.com/singer/spec)
