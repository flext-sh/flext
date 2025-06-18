# tap-oic Examples

> **Version**: 2.0
> **Last Updated**: June 15, 2025

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Data Extraction Examples](#data-extraction-examples)
3. [Integration Creation Examples](#integration-creation-examples)
4. [Integration Management Examples](#integration-management-examples)
5. [Monitoring Examples](#monitoring-examples)
6. [Advanced Extraction Scenarios](#advanced-extraction-scenarios)
7. [Complete Workflows](#complete-workflows)

## Basic Examples

### 1. Simple Data Extraction

```python
#!/usr/bin/env python3
"""
Basic example of extracting integration data from OIC
"""

import json
from tap_oic import TapOIC

# Configuration using OAuth2 (OIC's preferred authentication)
config = {
    "base_url": "https://your-instance.integration.ocp.oraclecloud.com",
    "auth_method": "oauth2",
    "oauth_client_id": "your-client-id",
    "oauth_client_secret": "your-client-secret",
    "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token",
    "start_date": "2025-01-01T00:00:00Z"
}

# Create tap instance
tap = TapOIC(config)

# Discover available streams
catalog = tap.discover_catalog()
print(f"Available streams: {[s.tap_stream_id for s in catalog.streams]}")

# Select core streams (known to work)
for stream in catalog.streams:
    if stream.tap_stream_id in ['integrations', 'connections', 'packages']:
        stream.metadata[0]['metadata']['selected'] = True

# Run sync
tap.sync(catalog)
```

### 2. Command Line Usage

```bash
# Basic extraction to stdout
tap-oic --config config.json --catalog catalog.json

# Pipe to a Singer target
tap-oic --config config.json --catalog catalog.json | target-postgres --config target-config.json

# Save to file for analysis
tap-oic --config config.json --catalog catalog.json > oic-data.jsonl

# Run discovery to see available streams
tap-oic --config config.json --discover > catalog.json

# Extract with state for incremental sync
tap-oic --config config.json --catalog catalog.json --state state.json
```

### 3. Configuration with Environment Variables

```python
import os
import json

# config.json with environment variables for OAuth2
config = {
    "base_url": "${OIC_BASE_URL}",
    "auth_method": "oauth2",
    "oauth_client_id": "${OIC_CLIENT_ID}",
    "oauth_client_secret": "${OIC_CLIENT_SECRET}",
    "oauth_token_url": "${OIC_TOKEN_URL}",
    "start_date": "2025-01-01T00:00:00Z",
    "page_size": 100,
    "request_timeout": 300,
    "include_monitoring": False,  # Set to True if monitoring endpoints are available
    "include_extended": False    # Set to True for extended streams
}

# Set environment variables
os.environ['OIC_BASE_URL'] = "https://your-instance.integration.ocp.oraclecloud.com"
os.environ['OIC_CLIENT_ID'] = "your-oauth-client-id"
os.environ['OIC_CLIENT_SECRET'] = "your-oauth-client-secret"
os.environ['OIC_TOKEN_URL'] = "https://idcs.identity.oraclecloud.com/oauth2/v1/token"

# Save configuration
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## Data Extraction Examples

### 1. Extract Integration Metrics

```python
from tap_oic import OICClient
from datetime import datetime, timedelta

# Initialize client
client = OICClient({
    "instance_url": "https://your-instance.integration.ocp.oraclecloud.com",
    "username": "your.email@example.com",
    "password": "your-password"
})

# Get all active integrations
integrations = list(client.paginate(
    '/ic/api/integration/v1/integrations',
    params={'status': 'ACTIVE'}
))

# Collect metrics for each integration
metrics_data = []

for integration in integrations:
    # Get 24-hour metrics
    metrics = client.request(
        'GET',
        f'/ic/api/monitoring/v1/integrations/{integration["id"]}/metrics',
        params={
            'period': '24h',
            'interval': '1h'
        }
    )

    metrics_data.append({
        'integration_id': integration['id'],
        'integration_name': integration['name'],
        'metrics': metrics['summary'],
        'time_series': metrics.get('timeSeries', [])
    })

# Process metrics
for data in metrics_data:
    print(f"\nIntegration: {data['integration_name']}")
    print(f"Total Executions: {data['metrics']['totalExecutions']}")
    if data['metrics']['totalExecutions'] > 0:
        success_rate = (data['metrics']['successfulExecutions'] / data['metrics']['totalExecutions'] * 100)
        print(f"Success Rate: {success_rate:.1f}%")
    print(f"Average Duration: {data['metrics']['averageExecutionTime']}ms")
```

### 2. Extract Execution History with Filters

```python
from datetime import datetime, timedelta

def extract_failed_executions(client, integration_id, days_back=7):
    """Extract failed executions for analysis"""

    start_date = datetime.utcnow() - timedelta(days=days_back)

    failed_executions = []

    # Get failed executions
    executions = client.paginate(
        f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
        params={
            'status': 'FAILED',
            'startTime': start_date.isoformat() + 'Z',
            'limit': 100
        }
    )

    for execution in executions:
        # Get detailed error information
        errors = client.request(
            'GET',
            f'/ic/api/monitoring/v1/executions/{execution["id"]}/errors'
        )

        failed_executions.append({
            'execution_id': execution['id'],
            'integration_id': integration_id,
            'start_time': execution['startTime'],
            'end_time': execution['endTime'],
            'duration_ms': execution['duration'],
            'error_count': len(errors.get('items', [])),
            'errors': errors.get('items', [])
        })

    return failed_executions

# Example usage
integration_id = "CUSTOMER_SYNC|01.00.0000"
failures = extract_failed_executions(client, integration_id)

# Analyze failure patterns
error_types = {}
for failure in failures:
    for error in failure['errors']:
        error_type = error.get('errorCode', 'UNKNOWN')
        if error_type not in error_types:
            error_types[error_type] = 0
        error_types[error_type] += 1

print(f"Failure Analysis for {integration_id}:")
for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {error_type}: {count} occurrences")
```

### 3. Extract Connection Health Status

```python
def check_all_connections_health(client):
    """Check health status of all connections"""

    connections = list(client.paginate('/ic/api/integration/v1/connections'))

    health_report = {
        'timestamp': datetime.utcnow().isoformat(),
        'total_connections': len(connections),
        'healthy': 0,
        'unhealthy': 0,
        'untested': 0,
        'details': []
    }

    for connection in connections:
        # Test connection
        try:
            test_result = client.request(
                'POST',
                f'/ic/api/integration/v1/connections/{connection["id"]}/test'
            )

            status = test_result.get('status', 'UNKNOWN')

            if status == 'SUCCESS':
                health_report['healthy'] += 1
            else:
                health_report['unhealthy'] += 1

            health_report['details'].append({
                'connection_id': connection['id'],
                'connection_name': connection['name'],
                'adapter_type': connection['adapterType'],
                'status': status,
                'response_time_ms': test_result.get('responseTime', 0),
                'message': test_result.get('message', '')
            })

        except Exception as e:
            health_report['untested'] += 1
            health_report['details'].append({
                'connection_id': connection['id'],
                'connection_name': connection['name'],
                'adapter_type': connection['adapterType'],
                'status': 'ERROR',
                'error': str(e)
            })

    return health_report

# Run health check
health_report = check_all_connections_health(client)

print(f"Connection Health Report - {health_report['timestamp']}")
print(f"Total: {health_report['total_connections']}")
print(f"Healthy: {health_report['healthy']}")
print(f"Unhealthy: {health_report['unhealthy']}")
print(f"Untested: {health_report['untested']}")
```

## Integration Creation Examples

### 1. Create a Database to REST Integration

```python
from tap_oic.utils.oic_api_client import OICAPIClient
import json

# Initialize client
client = OICAPIClient({
    "base_url": "https://your-instance.integration.ocp.oraclecloud.com",
    "auth_method": "oauth2",
    "oauth_client_id": "your-client-id",
    "oauth_client_secret": "your-client-secret",
    "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token"
})

# First, create the database connection
db_connection = {
    "name": "Customer Database Connection",
    "identifier": "CUSTOMER_DB_CONN",
    "description": "Connection to customer database",
    "adapterType": "oracle-db-adapter",
    "projectId": "CUSTOMER_PROJECT",
    "connectionProperties": {
        "host": "prod-db.example.com",
        "port": 1521,
        "serviceName": "CUSTDB",
        "databaseSchema": "SALES",
        "security": {
            "authenticationType": "USERNAME_PASSWORD",
            "username": "${DB_USERNAME}",
            "password": "${DB_PASSWORD}",
            "useSSL": True
        }
    }
}

# Create database connection
db_conn_response = client.request(
    'POST',
    '/ic/api/integration/v1/connections',
    json=db_connection
)
print(f"Created database connection: {db_conn_response['id']}")

# Create REST API connection
rest_connection = {
    "name": "Customer API Connection",
    "identifier": "CUSTOMER_API_CONN",
    "description": "Connection to customer REST API",
    "adapterType": "rest-adapter",
    "projectId": "CUSTOMER_PROJECT",
    "connectionProperties": {
        "baseUrl": "https://api.example.com",
        "security": {
            "authenticationType": "OAUTH2",
            "clientId": "${API_CLIENT_ID}",
            "clientSecret": "${API_CLIENT_SECRET}",
            "tokenUrl": "https://auth.example.com/oauth/token"
        },
        "requestHeaders": {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    }
}

# Create REST connection
rest_conn_response = client.request(
    'POST',
    '/ic/api/integration/v1/connections',
    json=rest_connection
)
print(f"Created REST connection: {rest_conn_response['id']}")

# Create the integration
integration = {
    "name": "Customer Data Sync",
    "identifier": "CUSTOMER_DATA_SYNC",
    "version": "01.00.0000",
    "description": "Synchronizes customer data from database to REST API",
    "pattern": "SCHEDULED_ORCHESTRATION",
    "projectId": "CUSTOMER_PROJECT",
    "configuration": {
        "logLevel": "INFO",
        "enableTracing": True,
        "errorHandling": {
            "retryCount": 3,
            "retryInterval": 60
        },
        "schedule": {
            "frequency": "HOURLY",
            "startTime": "2025-06-15T00:00:00Z",
            "timeZone": "UTC"
        }
    },
    "connections": [
        {
            "role": "SOURCE",
            "connectionId": db_conn_response['id'],
            "operations": [
                {
                    "operationType": "QUERY",
                    "query": """
                        SELECT
                            customer_id,
                            first_name,
                            last_name,
                            email,
                            phone,
                            created_date,
                            modified_date
                        FROM customers
                        WHERE modified_date > TO_TIMESTAMP(:lastSyncTime, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
                    """,
                    "parameters": {
                        "lastSyncTime": "${lastSyncTime}"
                    }
                }
            ]
        },
        {
            "role": "TARGET",
            "connectionId": rest_conn_response['id'],
            "operations": [
                {
                    "operationType": "POST",
                    "endpoint": "/v1/customers",
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
            ]
        }
    ],
    "transformations": [
        {
            "type": "FIELD_MAPPING",
            "mappings": [
                {
                    "source": "customer_id",
                    "target": "id"
                },
                {
                    "source": "first_name + ' ' + last_name",
                    "target": "full_name"
                },
                {
                    "source": "email",
                    "target": "email_address"
                },
                {
                    "source": "phone",
                    "target": "phone_number"
                }
            ]
        }
    ]
}

# Create the integration
integration_response = client.request(
    'POST',
    '/ic/api/integration/v1/integrations',
    json=integration
)

print(f"Created integration: {integration_response['id']}")
print(f"Integration status: {integration_response['status']}")

# Activate the integration
activate_response = client.request(
    'POST',
    f'/ic/api/integration/v1/integrations/{integration_response["id"]}/activate',
    json={
        "enablePayloadTracing": True,
        "payloadTracingLevel": "PRODUCTION"
    }
)

print(f"Integration activated successfully")
```

### 2. Create a File to Database Integration

```python
# Create file adapter connection
file_connection = {
    "name": "Customer Files Connection",
    "identifier": "CUSTOMER_FILES_CONN",
    "description": "Connection to customer data files",
    "adapterType": "file-adapter",
    "projectId": "CUSTOMER_PROJECT",
    "connectionProperties": {
        "fileLocation": "/shared/customer_data",
        "filePattern": "customers_*.csv",
        "encoding": "UTF-8",
        "delimiter": ",",
        "hasHeader": True,
        "security": {
            "authenticationType": "OS_AUTH"
        }
    }
}

file_conn_response = client.request(
    'POST',
    '/ic/api/integration/v1/connections',
    json=file_connection
)

# Create file-to-database integration
file_to_db_integration = {
    "name": "Customer File Import",
    "identifier": "CUSTOMER_FILE_IMPORT",
    "version": "01.00.0000",
    "description": "Import customer data from CSV files to database",
    "pattern": "FILE_DRIVEN_ORCHESTRATION",
    "projectId": "CUSTOMER_PROJECT",
    "connections": [
        {
            "role": "SOURCE",
            "connectionId": file_conn_response['id'],
            "operations": [
                {
                    "operationType": "READ",
                    "filePattern": "customers_*.csv",
                    "archivePattern": "processed/customers_*.csv"
                }
            ]
        },
        {
            "role": "TARGET",
            "connectionId": "CUSTOMER_DB_CONN",  # Use previously created connection
            "operations": [
                {
                    "operationType": "INSERT",
                    "table": "CUSTOMER_STAGING",
                    "batchSize": 1000
                }
            ]
        }
    ],
    "transformations": [
        {
            "type": "DATA_VALIDATION",
            "rules": [
                {
                    "field": "email",
                    "type": "EMAIL_FORMAT"
                },
                {
                    "field": "phone",
                    "type": "PHONE_FORMAT"
                }
            ]
        }
    ]
}

file_integration_response = client.request(
    'POST',
    '/ic/api/integration/v1/integrations',
    json=file_to_db_integration
)

print(f"Created file integration: {file_integration_response['id']}")
```

### 3. Create a Project and Organize Integrations

```python
# Create a project to organize integrations
project = {
    "name": "Customer Data Management",
    "identifier": "CUSTOMER_DATA_MGMT",
    "description": "Project for all customer data integrations",
    "version": "1.0",
    "configuration": {
        "enableVersionControl": True,
        "defaultEnvironment": "DEVELOPMENT",
        "deploymentStrategy": "ROLLING"
    },
    "metadata": {
        "businessUnit": "Sales",
        "criticality": "HIGH",
        "tags": ["customer", "sales", "data-sync"]
    }
}

project_response = client.request(
    'POST',
    '/ic/api/projects/v1/projects',
    json=project
)

print(f"Created project: {project_response['id']}")

# Create lookup table for country codes
lookup = {
    "name": "Country Code Mapping",
    "identifier": "COUNTRY_CODE_MAP",
    "description": "Maps country names to ISO codes",
    "projectId": project_response['id'],
    "columns": [
        {"name": "CountryName", "type": "STRING"},
        {"name": "ISOCode", "type": "STRING"}
    ],
    "data": [
        {"CountryName": "United States", "ISOCode": "US"},
        {"CountryName": "United Kingdom", "ISOCode": "GB"},
        {"CountryName": "Canada", "ISOCode": "CA"},
        {"CountryName": "Australia", "ISOCode": "AU"}
    ]
}

lookup_response = client.request(
    'POST',
    '/ic/api/integration/v1/lookups',
    json=lookup
)

print(f"Created lookup table: {lookup_response['id']}")
```

### 4. Create Integration with Error Handling and Monitoring

```python
# Create integration with comprehensive error handling
robust_integration = {
    "name": "Robust Customer Sync",
    "identifier": "ROBUST_CUSTOMER_SYNC",
    "version": "01.00.0000",
    "description": "Customer sync with comprehensive error handling",
    "pattern": "APP_DRIVEN_ORCHESTRATION",
    "projectId": "CUSTOMER_DATA_MGMT",
    "configuration": {
        "logLevel": "DEBUG",
        "enableTracing": True,
        "payloadTrace": True,
        "errorHandling": {
            "retryCount": 5,
            "retryInterval": 30,
            "retryBackoffMultiplier": 2.0,
            "maxRetryInterval": 300,
            "continueOnError": False,
            "errorQueue": "CUSTOMER_ERROR_QUEUE",
            "notificationEmail": "admin@example.com"
        },
        "monitoring": {
            "enableSLA": True,
            "slaThreshold": 5000,  # 5 seconds
            "enableAlerts": True,
            "alertThreshold": 0.95,  # 95% success rate
            "alertEmail": "ops@example.com"
        }
    },
    "connections": [
        {
            "role": "SOURCE",
            "connectionId": "CUSTOMER_DB_CONN",
            "operations": [
                {
                    "operationType": "QUERY",
                    "query": "SELECT * FROM customers WHERE status = 'ACTIVE'",
                    "timeout": 60000,
                    "maxRows": 10000
                }
            ]
        },
        {
            "role": "TARGET",
            "connectionId": "CUSTOMER_API_CONN",
            "operations": [
                {
                    "operationType": "POST",
                    "endpoint": "/v1/customers",
                    "timeout": 30000,
                    "retries": 3
                }
            ]
        }
    ],
    "transformations": [
        {
            "type": "DATA_ENRICHMENT",
            "operations": [
                {
                    "type": "LOOKUP",
                    "lookupTable": "COUNTRY_CODE_MAP",
                    "sourceField": "country",
                    "targetField": "country_code"
                },
                {
                    "type": "CALCULATE",
                    "expression": "CURRENT_TIMESTAMP",
                    "targetField": "sync_timestamp"
                }
            ]
        }
    ]
}

robust_response = client.request(
    'POST',
    '/ic/api/integration/v1/integrations',
    json=robust_integration
)

print(f"Created robust integration: {robust_response['id']}")

# Create schedule for the integration
schedule = {
    "name": "Hourly Customer Sync",
    "description": "Sync customers every hour during business hours",
    "frequency": "HOURLY",
    "startTime": "2025-06-15T08:00:00Z",
    "endTime": "2025-06-15T18:00:00Z",
    "timeZone": "America/New_York",
    "isActive": True,
    "parameters": [
        {"name": "batchSize", "value": "1000"},
        {"name": "enableValidation", "value": "true"}
    ]
}

schedule_response = client.request(
    'POST',
    f'/ic/api/integration/v1/integrations/{robust_response["id"]}/schedule',
    json=schedule
)

print(f"Created schedule: {schedule_response['id']}")
```

## Integration Management Examples

### 1. Import and Activate Integration Archive

```python
from tap_oic.utils.oic_api_client import OICAPIClient

# Initialize client
client = OICAPIClient({
    "base_url": "https://your-instance.integration.ocp.oraclecloud.com",
    "auth_method": "oauth2",
    "oauth_client_id": "your-client-id",
    "oauth_client_secret": "your-client-secret",
    "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token"
})

# Import integration archive
def import_and_activate_integration(iar_file_path):
    """Import .iar file and activate the integration"""

    # Import the archive
    with open(iar_file_path, 'rb') as f:
        files = {'file': (iar_file_path, f, 'application/octet-stream')}

        import_response = client.request(
            'POST',
            '/ic/api/integration/v1/integrations/archive',
            files=files
        )

    integration_id = import_response['id']
    print(f"Imported integration: {integration_id}")

    # Activate the integration
    activate_response = client.request(
        'POST',
        f'/ic/api/integration/v1/integrations/{integration_id}/activate',
        json={'enablePayloadTracing': False}
    )

    print(f"Activated integration: {integration_id}")
    return integration_id

# Example usage
integration_id = import_and_activate_integration('CUSTOMER_SYNC_01.00.0000.iar')
```

### 2. Clone and Modify Integration

```python
def clone_integration_for_environment(source_id, environment):
    """Clone integration for different environment"""

    # Clone the integration
    clone_response = client.request(
        'POST',
        f'/ic/api/integration/v1/integrations/{source_id}/clone',
        json={
            'name': f'Customer_Sync_{environment}',
            'identifier': f'CUSTOMER_SYNC_{environment.upper()}',
            'version': '01.00.0001'
        }
    )

    cloned_id = clone_response['id']
    print(f"Cloned integration: {cloned_id}")

    # Update environment-specific properties
    update_response = client.request(
        'PUT',
        f'/ic/api/integration/v1/integrations/{cloned_id}',
        json={
            'description': f'Customer sync for {environment} environment',
            'configuration': {
                'errorHandling': {
                    'retryCount': 5 if environment == 'PROD' else 3
                }
            }
        }
    )

    return cloned_id

# Clone for different environments
environments = ['DEV', 'TEST', 'PROD']
for env in environments:
    clone_integration_for_environment('CUSTOMER_SYNC|01.00.0000', env)
```

### 3. Export All Integrations for Backup

```python
import os
from datetime import datetime

def backup_all_integrations(backup_dir):
    """Export all integrations for backup"""

    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'oic_backup_{timestamp}')
    os.makedirs(backup_path, exist_ok=True)

    # Get all integrations
    integrations = client.request('GET', '/ic/api/integration/v1/integrations')

    backed_up = []
    for integration in integrations['items']:
        try:
            # Export integration
            response = client.request(
                'GET',
                f'/ic/api/integration/v1/integrations/{integration["id"]}/archive',
                stream=True
            )

            # Save to file
            filename = f"{integration['identifier']}_{integration['version']}.iar"
            filepath = os.path.join(backup_path, filename)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            backed_up.append({
                'integration': integration['id'],
                'file': filepath,
                'status': 'SUCCESS'
            })

            print(f"Backed up: {filename}")

        except Exception as e:
            backed_up.append({
                'integration': integration['id'],
                'status': 'FAILED',
                'error': str(e)
            })

    # Generate backup report
    report_path = os.path.join(backup_path, 'backup_report.json')
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total_integrations': len(integrations['items']),
            'backed_up': len([b for b in backed_up if b['status'] == 'SUCCESS']),
            'failed': len([b for b in backed_up if b['status'] == 'FAILED']),
            'details': backed_up
        }, f, indent=2)

    return backup_path

# Run backup
backup_location = backup_all_integrations('./oic_backups')
print(f"Backup completed: {backup_location}")
```

## Monitoring Examples

### 1. Real-time Integration Monitoring

```python
import time
from datetime import datetime, timedelta

def monitor_integration_realtime(client, integration_id, duration_minutes=60):
    """Monitor integration in real-time"""

    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)

    print(f"Monitoring {integration_id} for {duration_minutes} minutes...")
    print("-" * 60)

    while datetime.utcnow() < end_time:
        # Get recent executions
        executions = client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
            params={
                'limit': 5,
                'startTime': (datetime.utcnow() - timedelta(minutes=5)).isoformat() + 'Z'
            }
        )

        # Display execution status
        for execution in executions.get('items', []):
            status_icon = "✅" if execution['status'] == 'SUCCESS' else "❌"
            print(f"{status_icon} {execution['startTime']} - {execution['status']} - {execution['duration']}ms")

        # Get current metrics
        metrics = client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/metrics',
            params={'period': '1h'}
        )

        if metrics.get('summary'):
            summary = metrics['summary']
            success_rate = (summary['successfulExecutions'] / summary['totalExecutions'] * 100) if summary['totalExecutions'] > 0 else 0
            print(f"\nLast Hour: {summary['totalExecutions']} executions, {success_rate:.1f}% success rate")
            print(f"Average Duration: {summary['averageExecutionTime']}ms\n")

        # Wait before next check
        time.sleep(60)  # Check every minute

    print("Monitoring complete.")

# Example usage
monitor_integration_realtime(client, 'CUSTOMER_SYNC|01.00.0000', duration_minutes=30)
```

### 2. Performance Trend Analysis

```python
def analyze_integration_performance_trends(client, integration_id, days=30):
    """Analyze performance trends over time"""

    from datetime import datetime, timedelta
    import statistics

    start_date = datetime.utcnow() - timedelta(days=days)

    # Get all executions for the period
    all_executions = []
    offset = 0
    limit = 500

    while True:
        executions = client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
            params={
                'startTime': start_date.isoformat() + 'Z',
                'limit': limit,
                'offset': offset
            }
        )

        all_executions.extend(executions.get('items', []))

        if not executions.get('hasMore', False):
            break

        offset += limit

    # Group by day
    daily_stats = {}

    for execution in all_executions:
        date = execution['startTime'][:10]

        if date not in daily_stats:
            daily_stats[date] = {
                'durations': [],
                'successes': 0,
                'failures': 0
            }

        daily_stats[date]['durations'].append(execution['duration'])

        if execution['status'] == 'SUCCESS':
            daily_stats[date]['successes'] += 1
        else:
            daily_stats[date]['failures'] += 1

    # Calculate trends
    trends = []
    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        total = stats['successes'] + stats['failures']

        trends.append({
            'date': date,
            'total_executions': total,
            'success_rate': (stats['successes'] / total * 100) if total > 0 else 0,
            'avg_duration': statistics.mean(stats['durations']) if stats['durations'] else 0,
            'min_duration': min(stats['durations']) if stats['durations'] else 0,
            'max_duration': max(stats['durations']) if stats['durations'] else 0,
            'median_duration': statistics.median(stats['durations']) if stats['durations'] else 0
        })

    return trends

# Generate performance report
trends = analyze_integration_performance_trends(client, 'CUSTOMER_SYNC|01.00.0000')

# Plot trends (example with text output)
print(f"Performance Trends - Last {len(trends)} Days")
print("-" * 70)
print("Date       | Executions | Success % | Avg Duration | Min | Max | Median")
print("-" * 70)

for trend in trends[-7:]:  # Last 7 days
    print(f"{trend['date']} | {trend['total_executions']:10} | {trend['success_rate']:8.1f}% | "
          f"{trend['avg_duration']:12.0f} | {trend['min_duration']:3.0f} | {trend['max_duration']:6.0f} | {trend['median_duration']:6.0f}")
```

### 3. Automated Health Monitoring

```python
class IntegrationHealthMonitor:
    """Automated health monitoring for all integrations"""

    def __init__(self, client, alert_threshold=0.95):
        self.client = client
        self.alert_threshold = alert_threshold
        self.alerts = []

    def check_all_integrations(self):
        """Check health of all active integrations"""

        # Get all active integrations
        integrations = self.client.request(
            'GET',
            '/ic/api/integration/v1/integrations',
            params={'status': 'ACTIVE'}
        )

        health_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_integrations': len(integrations['items']),
            'healthy': 0,
            'warning': 0,
            'critical': 0,
            'details': []
        }

        for integration in integrations['items']:
            health = self.check_integration_health(integration['id'])

            health_report['details'].append(health)

            if health['status'] == 'HEALTHY':
                health_report['healthy'] += 1
            elif health['status'] == 'WARNING':
                health_report['warning'] += 1
            else:
                health_report['critical'] += 1
                self.send_alert(health)

        return health_report

    def check_integration_health(self, integration_id):
        """Check health of a single integration"""

        # Get recent metrics
        metrics = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/metrics',
            params={'period': '1h'}
        )

        summary = metrics.get('summary', {})
        total = summary.get('totalExecutions', 0)
        successful = summary.get('successfulExecutions', 0)

        if total == 0:
            status = 'WARNING'
            message = 'No recent executions'
            success_rate = 0
        else:
            success_rate = successful / total

            if success_rate >= self.alert_threshold:
                status = 'HEALTHY'
                message = 'Operating normally'
            elif success_rate >= 0.8:
                status = 'WARNING'
                message = f'Success rate below normal: {success_rate:.1%}'
            else:
                status = 'CRITICAL'
                message = f'Critical: Success rate {success_rate:.1%}'

        # Check for recent errors
        recent_errors = self.get_recent_errors(integration_id)

        return {
            'integration_id': integration_id,
            'status': status,
            'message': message,
            'success_rate': success_rate,
            'total_executions': total,
            'recent_errors': len(recent_errors),
            'last_checked': datetime.utcnow().isoformat()
        }

    def get_recent_errors(self, integration_id):
        """Get recent error details"""

        executions = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
            params={
                'status': 'FAILED',
                'limit': 10,
                'startTime': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
            }
        )

        return executions.get('items', [])

    def send_alert(self, health_info):
        """Send alert for critical integrations"""

        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'integration_id': health_info['integration_id'],
            'status': health_info['status'],
            'message': health_info['message'],
            'success_rate': health_info['success_rate']
        }

        self.alerts.append(alert)

        # In a real implementation, send email/slack/webhook
        print(f"🚨 ALERT: {health_info['integration_id']} - {health_info['message']}")

# Run health monitoring
monitor = IntegrationHealthMonitor(client)
health_report = monitor.check_all_integrations()

print(f"\nIntegration Health Report - {health_report['timestamp']}")
print(f"Total: {health_report['total_integrations']}")
print(f"✅ Healthy: {health_report['healthy']}")
print(f"⚠️  Warning: {health_report['warning']}")
print(f"❌ Critical: {health_report['critical']}")
```

## Advanced Extraction Scenarios

### 1. Parallel Stream Extraction

```python
import concurrent.futures
import threading
import time

class ParallelOICExtractor:
    """Extract multiple OIC streams in parallel"""

    def __init__(self, tap_config):
        self.tap = TapOIC(config=tap_config)
        self.results = {}
        self.lock = threading.Lock()

    def extract_stream(self, stream_name):
        """Extract a single stream"""

        start_time = time.time()
        records = []

        try:
            # Create catalog with only this stream selected
            catalog = self.tap.discover_catalog()
            for stream in catalog.streams:
                stream.metadata[0]['metadata']['selected'] = (
                    stream.tap_stream_id == stream_name
                )

            # Extract data
            for message in self.tap.sync(catalog):
                if message['type'] == 'RECORD' and message['stream'] == stream_name:
                    records.append(message['record'])

            duration = time.time() - start_time

            with self.lock:
                self.results[stream_name] = {
                    'status': 'SUCCESS',
                    'records': len(records),
                    'duration': duration,
                    'data': records
                }

            print(f"✅ {stream_name}: {len(records)} records in {duration:.2f}s")

        except Exception as e:
            with self.lock:
                self.results[stream_name] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'duration': time.time() - start_time
                }
            print(f"❌ {stream_name}: {e}")

    def extract_all_parallel(self, stream_names, max_workers=5):
        """Extract multiple streams in parallel"""

        print(f"Starting parallel extraction of {len(stream_names)} streams...")
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.extract_stream, stream)
                for stream in stream_names
            ]

            concurrent.futures.wait(futures)

        total_duration = time.time() - start_time
        total_records = sum(
            r['records'] for r in self.results.values()
            if r['status'] == 'SUCCESS'
        )

        print(f"\nExtraction complete:")
        print(f"Total time: {total_duration:.2f}s")
        print(f"Total records: {total_records}")
        print(f"Successful streams: {sum(1 for r in self.results.values() if r['status'] == 'SUCCESS')}")
        print(f"Failed streams: {sum(1 for r in self.results.values() if r['status'] == 'FAILED')}")

        return self.results

# Example usage
config = {
    "base_url": "https://your-instance.integration.ocp.oraclecloud.com",
    "auth_method": "oauth2",
    "oauth_client_id": "your-client-id",
    "oauth_client_secret": "your-client-secret",
    "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token"
}

extractor = ParallelOICExtractor(config)

# Extract core streams in parallel
results = extractor.extract_all_parallel([
    'integrations',
    'connections',
    'packages',
    'lookups',
    'libraries'
])
```

### 2. Incremental Data Extraction with State Management

```python
import json
from datetime import datetime, timedelta

class IncrementalOICExtractor:
    """Extract OIC data incrementally using state management"""

    def __init__(self, tap_config, state_file='oic_state.json'):
        self.tap = TapOIC(config=tap_config)
        self.state_file = state_file
        self.state = self.load_state()

    def load_state(self):
        """Load extraction state from file"""

        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_state(self):
        """Save extraction state to file"""

        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def extract_incremental(self, stream_name, key_property='lastUpdated'):
        """Extract only new/updated records since last sync"""

        last_sync = self.state.get(stream_name, {}).get('last_sync')

        if last_sync:
            print(f"Extracting {stream_name} since {last_sync}")
        else:
            print(f"First extraction of {stream_name}")

        # Configure catalog
        catalog = self.tap.discover_catalog()
        for stream in catalog.streams:
            if stream.tap_stream_id == stream_name:
                stream.metadata[0]['metadata']['selected'] = True
                stream.replication_key = key_property
                stream.replication_method = 'INCREMENTAL'
            else:
                stream.metadata[0]['metadata']['selected'] = False

        # Track extraction
        records = []
        max_timestamp = last_sync

        for message in self.tap.sync(catalog, state=self.state):
            if message['type'] == 'RECORD' and message['stream'] == stream_name:
                record = message['record']
                records.append(record)

                # Track maximum timestamp
                if key_property in record:
                    timestamp = record[key_property]
                    if not max_timestamp or timestamp > max_timestamp:
                        max_timestamp = timestamp

            elif message['type'] == 'STATE':
                # Update state from tap
                self.state = message['value']

        # Update state
        if max_timestamp:
            if stream_name not in self.state:
                self.state[stream_name] = {}
            self.state[stream_name]['last_sync'] = max_timestamp
            self.state[stream_name]['last_count'] = len(records)
            self.state[stream_name]['last_run'] = datetime.utcnow().isoformat()

        self.save_state()

        print(f"Extracted {len(records)} records from {stream_name}")
        return records

    def extract_all_incremental(self):
        """Extract all streams incrementally"""

        streams = [
            ('integrations', 'lastUpdated'),
            ('connections', 'lastModified'),
            ('packages', 'modifiedTime')
        ]

        all_records = {}

        for stream_name, key_property in streams:
            records = self.extract_incremental(stream_name, key_property)
            all_records[stream_name] = records

        return all_records

# Example usage
extractor = IncrementalOICExtractor(config)

# Run incremental extraction
while True:
    print(f"\n--- Extraction run at {datetime.now()} ---")

    results = extractor.extract_all_incremental()

    # Process new/updated records
    for stream, records in results.items():
        if records:
            print(f"Processing {len(records)} new/updated {stream}")
            # Send to target, trigger alerts, etc.

    # Wait before next run
    print("Waiting 5 minutes before next extraction...")
    time.sleep(300)
```

### 3. Data Quality Monitoring

```python
class OICDataQualityMonitor:
    """Monitor data quality in OIC extractions"""

    def __init__(self, tap_config):
        self.tap = TapOIC(config=tap_config)
        self.quality_rules = {}

    def add_quality_rule(self, stream, field, rule_type, params=None):
        """Add a data quality rule"""

        if stream not in self.quality_rules:
            self.quality_rules[stream] = []

        self.quality_rules[stream].append({
            'field': field,
            'type': rule_type,
            'params': params or {}
        })

    def check_quality(self, stream_name, records):
        """Check data quality for extracted records"""

        if stream_name not in self.quality_rules:
            return {'passed': True, 'issues': []}

        issues = []

        for rule in self.quality_rules[stream_name]:
            field = rule['field']
            rule_type = rule['type']
            params = rule['params']

            for i, record in enumerate(records):
                issue = None

                if rule_type == 'required' and field not in record:
                    issue = f"Missing required field '{field}'"

                elif rule_type == 'not_null' and record.get(field) is None:
                    issue = f"Null value in field '{field}'"

                elif rule_type == 'min_length' and field in record:
                    min_len = params.get('min', 1)
                    if len(str(record[field])) < min_len:
                        issue = f"Field '{field}' below minimum length {min_len}"

                elif rule_type == 'pattern' and field in record:
                    import re
                    pattern = params.get('pattern')
                    if pattern and not re.match(pattern, str(record[field])):
                        issue = f"Field '{field}' doesn't match pattern {pattern}"

                elif rule_type == 'enum' and field in record:
                    allowed = params.get('values', [])
                    if record[field] not in allowed:
                        issue = f"Field '{field}' has invalid value: {record[field]}"

                if issue:
                    issues.append({
                        'record_index': i,
                        'record_id': record.get('id', 'unknown'),
                        'field': field,
                        'issue': issue,
                        'value': record.get(field)
                    })

        return {
            'passed': len(issues) == 0,
            'total_records': len(records),
            'issues_count': len(issues),
            'issues': issues[:10]  # First 10 issues
        }

    def extract_and_validate(self):
        """Extract data and validate quality"""

        # Define quality rules
        self.add_quality_rule('integrations', 'id', 'required')
        self.add_quality_rule('integrations', 'name', 'not_null')
        self.add_quality_rule('integrations', 'identifier', 'pattern',
                             {'pattern': r'^[A-Z][A-Z0-9_]*$'})
        self.add_quality_rule('integrations', 'status', 'enum',
                             {'values': ['CONFIGURED', 'ACTIVE', 'INACTIVE', 'FAILED']})

        self.add_quality_rule('connections', 'id', 'required')
        self.add_quality_rule('connections', 'adapterType', 'not_null')
        self.add_quality_rule('connections', 'status', 'enum',
                             {'values': ['CONFIGURED', 'ACTIVE', 'FAILED']})

        # Extract and validate each stream
        quality_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'streams': {}
        }

        streams = ['integrations', 'connections', 'packages']

        for stream in streams:
            print(f"\nExtracting and validating {stream}...")

            # Extract data
            catalog = self.tap.discover_catalog()
            for s in catalog.streams:
                s.metadata[0]['metadata']['selected'] = (s.tap_stream_id == stream)

            records = []
            for message in self.tap.sync(catalog):
                if message['type'] == 'RECORD' and message['stream'] == stream:
                    records.append(message['record'])

            # Validate quality
            quality_result = self.check_quality(stream, records)

            quality_report['streams'][stream] = {
                'records_extracted': len(records),
                'quality_passed': quality_result['passed'],
                'issues_found': quality_result['issues_count'],
                'sample_issues': quality_result['issues']
            }

            if quality_result['passed']:
                print(f"✅ {stream}: All {len(records)} records passed quality checks")
            else:
                print(f"⚠️  {stream}: {quality_result['issues_count']} quality issues found")
                for issue in quality_result['issues'][:3]:
                    print(f"   - Record {issue['record_id']}: {issue['issue']}")

        return quality_report

# Example usage
monitor = OICDataQualityMonitor(config)
quality_report = monitor.extract_and_validate()

# Save quality report
with open('oic_quality_report.json', 'w') as f:
    json.dump(quality_report, f, indent=2)

print(f"\nQuality report saved to oic_quality_report.json")
```

## Complete Workflows

### 1. Production Data Pipeline with Meltano

```bash
# Complete production setup using Meltano

# 1. Install Meltano and tap-oic
pip install meltano
meltano init oic-data-pipeline
cd oic-data-pipeline

# 2. Add tap-oic
meltano add extractor tap-oic

# 3. Configure tap-oic
cat > meltano.yml << EOF
version: 1
project_id: oic-data-pipeline
environments:
  - name: dev
  - name: prod
extractors:
  - name: tap-oic
    pip_url: tap-oic
    config:
      base_url: \${OIC_BASE_URL}
      auth_method: oauth2
      oauth_client_id: \${OIC_CLIENT_ID}
      oauth_client_secret: \${OIC_CLIENT_SECRET}
      oauth_token_url: \${OIC_TOKEN_URL}
      start_date: '2025-01-01T00:00:00Z'
    select:
      - integrations.*
      - connections.*
      - packages.*
    metadata:
      integrations:
        replication-method: INCREMENTAL
        replication-key: lastUpdated
      connections:
        replication-method: INCREMENTAL
        replication-key: lastModified
loaders:
  - name: target-postgres
    pip_url: target-postgres
    config:
      host: \${PG_HOST}
      port: 5432
      user: \${PG_USER}
      password: \${PG_PASSWORD}
      dbname: oic_analytics
      schema: oic_data
EOF

# 4. Set environment variables
export OIC_BASE_URL="https://your-instance.integration.ocp.oraclecloud.com"
export OIC_CLIENT_ID="your-client-id"
export OIC_CLIENT_SECRET="your-client-secret"
export OIC_TOKEN_URL="https://idcs.identity.oraclecloud.com/oauth2/v1/token"
export PG_HOST="postgres.example.com"
export PG_USER="analytics_user"
export PG_PASSWORD="secure-password"

# 5. Run extraction
meltano run tap-oic target-postgres

# 6. Schedule regular extraction
meltano schedule add oic-daily --interval @daily
meltano job add oic-daily --tasks "tap-oic target-postgres"
```

### 2. Complete Python Application

```python
#!/usr/bin/env python3
"""
Complete OIC data extraction and monitoring application
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import schedule
import time

from tap_oic import TapOIC
from tap_oic.utils.oic_api_client import OICAPIClient


class OICDataPipeline:
    """Complete OIC data extraction and monitoring pipeline"""

    def __init__(self, config_file='config.json'):
        # Load configuration
        with open(config_file) as f:
            self.config = json.load(f)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('oic_pipeline.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.tap = TapOIC(config=self.config['tap_config'])
        self.client = OICAPIClient(self.config['tap_config'])
        self.state = self.load_state()

    def load_state(self):
        """Load pipeline state"""
        try:
            with open('pipeline_state.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'last_run': None,
                'streams': {},
                'metrics': {}
            }

    def save_state(self):
        """Save pipeline state"""
        with open('pipeline_state.json', 'w') as f:
            json.dump(self.state, f, indent=2)

    def extract_data(self):
        """Extract data from OIC"""
        self.logger.info("Starting data extraction...")

        # Discover and configure catalog
        catalog = self.tap.discover_catalog()

        # Select streams based on configuration
        for stream in catalog.streams:
            if stream.tap_stream_id in self.config.get('selected_streams', []):
                stream.metadata[0]['metadata']['selected'] = True

        # Track extraction results
        extraction_results = {
            'start_time': datetime.utcnow().isoformat(),
            'streams': {}
        }

        # Extract data
        for message in self.tap.sync(catalog, state=self.state.get('tap_state')):
            if message['type'] == 'RECORD':
                stream = message['stream']
                if stream not in extraction_results['streams']:
                    extraction_results['streams'][stream] = {
                        'records': 0,
                        'first_record_time': datetime.utcnow().isoformat()
                    }

                extraction_results['streams'][stream]['records'] += 1

                # Process record
                self.process_record(stream, message['record'])

            elif message['type'] == 'STATE':
                self.state['tap_state'] = message['value']

        extraction_results['end_time'] = datetime.utcnow().isoformat()

        # Update state
        self.state['last_run'] = datetime.utcnow().isoformat()
        self.state['last_extraction'] = extraction_results
        self.save_state()

        self.logger.info(f"Extraction complete: {extraction_results}")
        return extraction_results

    def process_record(self, stream: str, record: Dict[str, Any]):
        """Process extracted record"""
        # Implement your record processing logic here
        # Examples: Send to database, trigger alerts, update cache

        if stream == 'integrations':
            # Check for failed integrations
            if record.get('status') == 'FAILED':
                self.alert_failed_integration(record)

        elif stream == 'monitoring_instances':
            # Check for performance issues
            if record.get('duration', 0) > 10000:  # 10 seconds
                self.alert_slow_execution(record)

    def monitor_health(self):
        """Monitor OIC health"""
        self.logger.info("Running health monitoring...")

        health_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'integrations': {},
            'connections': {},
            'overall_status': 'HEALTHY'
        }

        # Check integration health
        integrations = self.client.request('GET', '/ic/api/integration/v1/integrations')

        for integration in integrations.get('items', []):
            if integration['status'] == 'ACTIVE':
                # Get recent metrics
                try:
                    metrics = self.client.request(
                        'GET',
                        f'/ic/api/monitoring/v1/integrations/{integration["id"]}/metrics',
                        params={'period': '1h'}
                    )

                    summary = metrics.get('summary', {})
                    total = summary.get('totalExecutions', 0)
                    successful = summary.get('successfulExecutions', 0)

                    health_status = 'HEALTHY'
                    if total > 0:
                        success_rate = successful / total
                        if success_rate < 0.95:
                            health_status = 'WARNING'
                        if success_rate < 0.80:
                            health_status = 'CRITICAL'
                            health_report['overall_status'] = 'CRITICAL'

                    health_report['integrations'][integration['id']] = {
                        'name': integration['name'],
                        'status': health_status,
                        'success_rate': success_rate if total > 0 else 1.0,
                        'executions': total
                    }

                except Exception as e:
                    self.logger.error(f"Failed to get metrics for {integration['id']}: {e}")

        # Check connection health
        connections = self.client.request('GET', '/ic/api/integration/v1/connections')

        for connection in connections.get('items', []):
            try:
                test_result = self.client.request(
                    'POST',
                    f'/ic/api/integration/v1/connections/{connection["id"]}/test'
                )

                health_report['connections'][connection['id']] = {
                    'name': connection['name'],
                    'type': connection['adapterType'],
                    'status': test_result.get('status', 'UNKNOWN')
                }

                if test_result.get('status') != 'SUCCESS':
                    health_report['overall_status'] = 'WARNING'

            except Exception as e:
                self.logger.error(f"Failed to test connection {connection['id']}: {e}")
                health_report['connections'][connection['id']] = {
                    'name': connection['name'],
                    'status': 'ERROR'
                }

        # Save health report
        self.state['last_health_check'] = health_report
        self.save_state()

        # Send alerts if needed
        if health_report['overall_status'] != 'HEALTHY':
            self.send_health_alert(health_report)

        return health_report

    def alert_failed_integration(self, integration: Dict[str, Any]):
        """Alert on failed integration"""
        self.logger.error(f"Integration failed: {integration['name']} ({integration['id']})")
        # Implement your alerting logic (email, Slack, PagerDuty, etc.)

    def alert_slow_execution(self, execution: Dict[str, Any]):
        """Alert on slow execution"""
        self.logger.warning(f"Slow execution detected: {execution['integrationId']} took {execution['duration']}ms")
        # Implement your alerting logic

    def send_health_alert(self, health_report: Dict[str, Any]):
        """Send health alert"""
        self.logger.error(f"Health check failed: {health_report['overall_status']}")
        # Implement your alerting logic

    def generate_report(self):
        """Generate daily report"""
        self.logger.info("Generating daily report...")

        report = {
            'date': datetime.utcnow().date().isoformat(),
            'extraction_summary': self.state.get('last_extraction', {}),
            'health_status': self.state.get('last_health_check', {}),
            'alerts_sent': self.state.get('alerts_today', 0)
        }

        # Save report
        report_file = f"reports/oic_report_{report['date']}.json"
        os.makedirs('reports', exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Report saved to {report_file}")
        return report

    def run_pipeline(self):
        """Run complete pipeline"""
        self.logger.info("Starting OIC data pipeline...")

        try:
            # Extract data
            extraction_results = self.extract_data()

            # Monitor health
            health_report = self.monitor_health()

            # Generate report
            if datetime.utcnow().hour == 8:  # Generate report at 8 AM
                self.generate_report()

            self.logger.info("Pipeline completed successfully")

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            # Send critical alert
            self.send_critical_alert(str(e))

    def send_critical_alert(self, error_message: str):
        """Send critical pipeline failure alert"""
        self.logger.critical(f"Pipeline critical failure: {error_message}")
        # Implement your critical alerting logic

    def schedule_pipeline(self):
        """Schedule pipeline runs"""
        # Run every 30 minutes
        schedule.every(30).minutes.do(self.run_pipeline)

        # Health check every 10 minutes
        schedule.every(10).minutes.do(self.monitor_health)

        # Daily report at 8 AM
        schedule.every().day.at("08:00").do(self.generate_report)

        self.logger.info("Pipeline scheduled. Starting scheduler...")

        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    # Configuration
    config = {
        "tap_config": {
            "base_url": os.environ.get("OIC_BASE_URL"),
            "auth_method": "oauth2",
            "oauth_client_id": os.environ.get("OIC_CLIENT_ID"),
            "oauth_client_secret": os.environ.get("OIC_CLIENT_SECRET"),
            "oauth_token_url": os.environ.get("OIC_TOKEN_URL"),
            "start_date": "2025-01-01T00:00:00Z"
        },
        "selected_streams": [
            "integrations",
            "connections",
            "packages",
            "monitoring_instances"
        ]
    }

    # Save configuration
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

    # Create and run pipeline
    pipeline = OICDataPipeline('config.json')

    # Run once immediately
    pipeline.run_pipeline()

    # Schedule future runs
    pipeline.schedule_pipeline()
```

## Summary

This examples guide demonstrates how to use tap-oic effectively for:

1. **Basic Extraction** - Simple data extraction from OIC
2. **Data Analysis** - Extracting and analyzing OIC metrics
3. **Integration Management** - Managing existing integrations via API
4. **Monitoring** - Real-time and automated health monitoring
5. **Advanced Scenarios** - Parallel extraction, incremental sync, data quality
6. **Complete Workflows** - Production-ready implementations

Oracle Integration Cloud provides comprehensive REST APIs for creating, managing, and monitoring integrations programmatically. Future versions of tap-oic will include integration generation capabilities to simplify this process.
