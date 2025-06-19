# Integration Management Guide

> **tap-oic Version**: 2.0
> **Last Updated**: June 15, 2025

## Table of Contents

1. [Overview](#overview)
2. [Integration Design Process](#integration-design-process)
3. [Managing Existing Integrations](#managing-existing-integrations)
4. [Working with Integration Archives](#working-with-integration-archives)
5. [Connection Management](#connection-management)
6. [Deployment Strategies](#deployment-strategies)
7. [Monitoring and Operations](#monitoring-and-operations)
8. [Best Practices](#best-practices)

## Overview

This guide covers how to manage Oracle Integration Cloud (OIC) integrations using the REST API and tap-oic. While OIC requires using the Visual Designer to create new integrations, the REST API provides powerful capabilities for managing, deploying, and monitoring existing integrations.

### Key Capabilities

✅ **Import/Export** integration archives (.iar files)
✅ **Activate/Deactivate** existing integrations
✅ **Monitor** integration execution and performance
✅ **Update** integration properties and configurations
✅ **Clone** existing integrations as templates

## Integration Design Process

### Creating Integrations in OIC

Integrations can be created using either the OIC Visual Designer or REST API:

1. **Login to OIC Console**: Access your OIC instance via web browser
2. **Navigate to Integrations**: Click "Integrations" in the navigation menu
3. **Create New Integration**: Click "Create" and select a pattern
4. **Design the Flow**: Use the visual designer to add activities
5. **Configure Connections**: Select and configure adapter connections
6. **Add Mappings**: Create data transformations visually
7. **Test the Integration**: Use the built-in testing capabilities
8. **Export as Archive**: Save the integration as a .iar file

### Integration Patterns in Visual Designer

| Pattern                  | Use Case                    | Created Via     |
| ------------------------ | --------------------------- | --------------- |
| App Driven Orchestration | REST/SOAP triggered flows   | Visual Designer |
| Scheduled Orchestration  | Time-based batch processing | Visual Designer |
| Basic Routing            | Simple message routing      | Visual Designer |
| Publish to OIC           | Event publishing            | Visual Designer |
| Subscribe to OIC         | Event consumption           | Visual Designer |

## Managing Existing Integrations

### Importing Integration Archives

```python
import requests
from tap_oic import OICClient

# Initialize client
client = OICClient({
    'base_url': 'https://your-instance.integration.ocp.oraclecloud.com',
    'client_id': 'your-client-id',
    'client_secret': 'your-client-secret',
    'token_url': 'https://idcs.identity.oraclecloud.com/oauth2/v1/token'
})

# Import an integration archive
def import_integration(iar_file_path):
    """Import a pre-built integration archive"""

    with open(iar_file_path, 'rb') as f:
        files = {'file': (iar_file_path, f, 'application/octet-stream')}

        response = client.request(
            'POST',
            '/ic/api/integration/v1/integrations/archive',
            files=files
        )

    return response

# Example usage
result = import_integration('CUSTOMER_SYNC_01.00.0000.iar')
print(f"Imported integration: {result['id']}")
```

### Activating and Deactivating Integrations

```python
# Activate an integration
def activate_integration(integration_id, enable_tracing=False):
    """Activate an existing integration"""

    payload = {
        'enablePayloadTracing': enable_tracing,
        'payloadTracingLevel': 'PRODUCTION' if enable_tracing else 'NONE'
    }

    response = client.request(
        'POST',
        f'/ic/api/integration/v1/integrations/{integration_id}/activate',
        json=payload
    )

    return response

# Deactivate an integration
def deactivate_integration(integration_id):
    """Deactivate a running integration"""

    response = client.request(
        'POST',
        f'/ic/api/integration/v1/integrations/{integration_id}/deactivate'
    )

    return response

# Example usage
integration_id = 'CUSTOMER_SYNC|01.00.0000'
activate_integration(integration_id, enable_tracing=True)
```

### Cloning Integrations

```python
# Clone an existing integration
def clone_integration(source_id, new_name, new_identifier, new_version):
    """Create a copy of an existing integration"""

    payload = {
        'name': new_name,
        'identifier': new_identifier,
        'version': new_version
    }

    response = client.request(
        'POST',
        f'/ic/api/integration/v1/integrations/{source_id}/clone',
        json=payload
    )

    return response

# Example: Create multiple versions of an integration
source_integration = 'CUSTOMER_SYNC|01.00.0000'

# Clone for different environments
environments = ['DEV', 'TEST', 'PROD']

for env in environments:
    cloned = clone_integration(
        source_id=source_integration,
        new_name=f'Customer_Sync_{env}',
        new_identifier=f'CUSTOMER_SYNC_{env}',
        new_version='01.00.0001'
    )
    print(f"Created {env} version: {cloned['id']}")
```

## Working with Integration Archives

### Exporting Integrations

```python
# Export an integration as .iar file
def export_integration(integration_id, output_path):
    """Export integration archive for backup or migration"""

    response = client.request(
        'GET',
        f'/ic/api/integration/v1/integrations/{integration_id}/archive',
        stream=True
    )

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path

# Export all integrations for backup
integrations = client.request('GET', '/ic/api/integration/v1/integrations')

for integration in integrations['items']:
    filename = f"{integration['identifier']}_{integration['version']}.iar"
    export_integration(integration['id'], filename)
    print(f"Exported: {filename}")
```

### Batch Operations

```python
# Batch import integrations
def batch_import_integrations(iar_directory):
    """Import all .iar files from a directory"""

    import os
    import glob

    iar_files = glob.glob(os.path.join(iar_directory, '*.iar'))
    results = []

    for iar_file in iar_files:
        try:
            result = import_integration(iar_file)
            results.append({
                'file': iar_file,
                'status': 'SUCCESS',
                'integration_id': result['id']
            })
        except Exception as e:
            results.append({
                'file': iar_file,
                'status': 'FAILED',
                'error': str(e)
            })

    return results

# Import all integrations from backup
results = batch_import_integrations('./integration_backups/')
for result in results:
    print(f"{result['file']}: {result['status']}")
```

## Connection Management

### Updating Connection Properties

```python
# Update existing connection properties
def update_connection(connection_id, updates):
    """Update connection configuration"""

    response = client.request(
        'PUT',
        f'/ic/api/integration/v1/connections/{connection_id}',
        json=updates
    )

    return response

# Example: Update database connection
connection_updates = {
    'connectionProperties': {
        'host': 'new-mysql.example.com',
        'connectionPooling': {
            'maxSize': 50,
            'timeout': 60000
        }
    }
}

update_connection('MYSQL_PROD_DB', connection_updates)
```

### Testing Connections

```python
# Test all connections
def test_all_connections():
    """Test all configured connections"""

    connections = client.request('GET', '/ic/api/integration/v1/connections')
    results = []

    for conn in connections['items']:
        test_result = client.request(
            'POST',
            f'/ic/api/integration/v1/connections/{conn["id"]}/test'
        )

        results.append({
            'connection': conn['name'],
            'type': conn['adapterType'],
            'status': test_result['status'],
            'message': test_result.get('message', '')
        })

    return results

# Run connection tests
test_results = test_all_connections()
for result in test_results:
    print(f"{result['connection']} ({result['type']}): {result['status']}")
```

## Deployment Strategies

### Managing Integration Versions

```python
# Version management for integrations
class IntegrationVersionManager:
    """Manage multiple versions of integrations"""

    def __init__(self, client):
        self.client = client

    def list_versions(self, identifier):
        """List all versions of an integration"""

        integrations = self.client.request(
            'GET',
            '/ic/api/integration/v1/integrations',
            params={'q': f'identifier:{identifier}'}
        )

        versions = []
        for integration in integrations['items']:
            if integration['identifier'] == identifier:
                versions.append({
                    'version': integration['version'],
                    'status': integration['status'],
                    'modified': integration['lastModified']
                })

        return sorted(versions, key=lambda x: x['version'], reverse=True)

    def activate_version(self, identifier, version):
        """Activate a specific version"""

        integration_id = f"{identifier}|{version}"
        return activate_integration(integration_id)

    def rollback_to_version(self, identifier, target_version):
        """Rollback to a previous version"""

        # Deactivate current active version
        versions = self.list_versions(identifier)
        for v in versions:
            if v['status'] == 'ACTIVE':
                self.client.request(
                    'POST',
                    f'/ic/api/integration/v1/integrations/{identifier}|{v["version"]}/deactivate'
                )

        # Activate target version
        return self.activate_version(identifier, target_version)
```

### Environment-Based Deployment

```python
# Deploy same integration across environments
def deploy_to_environments(integration_archive, environments):
    """Deploy integration to multiple environments"""

    results = {}

    for env_name, env_config in environments.items():
        # Create environment-specific client
        env_client = OICClient(env_config)

        # Import integration
        import_result = import_integration_to_env(
            env_client,
            integration_archive,
            env_name
        )

        # Update environment-specific properties
        if env_name == 'PROD':
            # Enable extensive logging for production
            activate_integration(
                import_result['id'],
                enable_tracing=True
            )
        else:
            # Minimal logging for non-prod
            activate_integration(
                import_result['id'],
                enable_tracing=False
            )

        results[env_name] = import_result

    return results

# Example usage
environments = {
    'DEV': {
        'base_url': 'https://dev-oic.example.com',
        'client_id': 'dev-client-id',
        'client_secret': 'dev-secret'
    },
    'PROD': {
        'base_url': 'https://prod-oic.example.com',
        'client_id': 'prod-client-id',
        'client_secret': 'prod-secret'
    }
}

deploy_to_environments('CUSTOMER_SYNC.iar', environments)
```

## Monitoring and Operations

### Real-time Integration Monitoring

```python
# Monitor integration health in real-time
def monitor_integration_health(integration_id):
    """Monitor integration health and performance"""

    # Get current status
    integration = client.request(
        'GET',
        f'/ic/api/integration/v1/integrations/{integration_id}'
    )

    # Get recent executions
    executions = client.request(
        'GET',
        f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
        params={'limit': 10}
    )

    # Calculate health metrics
    recent_executions = executions['items']
    if recent_executions:
        success_count = sum(1 for e in recent_executions if e['status'] == 'SUCCESS')
        health_score = (success_count / len(recent_executions)) * 100
    else:
        health_score = 100  # No executions yet

    return {
        'integration_id': integration_id,
        'status': integration['status'],
        'health_score': health_score,
        'recent_failures': [e for e in recent_executions if e['status'] == 'FAILED']
    }
```

### Performance Analysis

```python
# Analyze integration performance trends
def analyze_performance_trends(integration_id, days=7):
    """Analyze performance trends over time"""

    from datetime import datetime, timedelta
    import statistics

    # Get executions for the period
    start_date = datetime.utcnow() - timedelta(days=days)

    executions = client.request(
        'GET',
        f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
        params={
            'startTime': start_date.isoformat() + 'Z',
            'limit': 1000
        }
    )

    # Group by day and calculate metrics
    daily_metrics = {}

    for execution in executions['items']:
        date = execution['startTime'][:10]  # YYYY-MM-DD

        if date not in daily_metrics:
            daily_metrics[date] = {
                'durations': [],
                'successes': 0,
                'failures': 0
            }

        daily_metrics[date]['durations'].append(execution['duration'])
        if execution['status'] == 'SUCCESS':
            daily_metrics[date]['successes'] += 1
        else:
            daily_metrics[date]['failures'] += 1

    # Calculate daily averages
    trends = []
    for date, metrics in sorted(daily_metrics.items()):
        trends.append({
            'date': date,
            'avg_duration': statistics.mean(metrics['durations']),
            'success_rate': metrics['successes'] / (metrics['successes'] + metrics['failures']) * 100,
            'total_executions': metrics['successes'] + metrics['failures']
        })

    return trends
```

### Automated Health Checks

```python
# Automated health check system
class IntegrationHealthChecker:
    """Automated health checking for integrations"""

    def __init__(self, client, alert_callback=None):
        self.client = client
        self.alert_callback = alert_callback

    def check_all_integrations(self):
        """Check health of all active integrations"""

        # Get all active integrations
        integrations = self.client.request(
            'GET',
            '/ic/api/integration/v1/integrations',
            params={'status': 'ACTIVE'}
        )

        health_report = []

        for integration in integrations['items']:
            health = self.check_integration_health(integration['id'])
            health_report.append(health)

            # Alert if unhealthy
            if health['status'] != 'HEALTHY' and self.alert_callback:
                self.alert_callback(health)

        return health_report

    def check_integration_health(self, integration_id):
        """Comprehensive health check for an integration"""

        checks = {
            'execution_check': self._check_recent_executions(integration_id),
            'performance_check': self._check_performance(integration_id),
            'error_rate_check': self._check_error_rate(integration_id),
            'connection_check': self._check_connections(integration_id)
        }

        # Determine overall health
        failed_checks = [k for k, v in checks.items() if not v['passed']]

        return {
            'integration_id': integration_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'HEALTHY' if not failed_checks else 'UNHEALTHY',
            'checks': checks,
            'failed_checks': failed_checks
        }

    def _check_recent_executions(self, integration_id):
        """Check if integration has recent executions"""

        executions = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
            params={'limit': 1}
        )

        if not executions['items']:
            return {'passed': False, 'message': 'No recent executions'}

        last_execution = executions['items'][0]
        hours_since = (datetime.utcnow() - datetime.fromisoformat(last_execution['endTime'].replace('Z', '+00:00'))).total_seconds() / 3600

        if hours_since > 24:
            return {'passed': False, 'message': f'No executions in {hours_since:.1f} hours'}

        return {'passed': True, 'message': 'Recent executions found'}
```

## Best Practices

### Integration Lifecycle Management

1. **Version Control**

   - Export all integrations as .iar files
   - Store in version control system
   - Use semantic versioning
   - Tag releases appropriately

2. **Testing Strategy**

   - Test integrations in Visual Designer first
   - Use non-production environments
   - Validate connections before activation
   - Monitor initial executions closely

3. **Deployment Best Practices**
   - Always backup before updates
   - Use blue-green deployment for critical integrations
   - Monitor metrics after deployment
   - Have rollback procedures ready

### Security Considerations

```python
# Secure credential management
def setup_secure_client():
    """Setup OIC client with secure credential management"""

    import os
    from getpass import getpass

    # Use environment variables or secure vault
    config = {
        'base_url': os.environ.get('OIC_BASE_URL'),
        'client_id': os.environ.get('OIC_CLIENT_ID'),
        'client_secret': os.environ.get('OIC_CLIENT_SECRET') or getpass('Client Secret: '),
        'token_url': os.environ.get('OIC_TOKEN_URL')
    }

    # Validate all required fields
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise ValueError(f"Missing required configuration: {missing}")

    return OICClient(config)
```

### Error Handling Patterns

```python
# Robust error handling for OIC operations
def safe_integration_operation(operation_func, *args, **kwargs):
    """Execute OIC operation with comprehensive error handling"""

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            return operation_func(*args, **kwargs)

        except HTTPError as e:
            if e.response.status_code == 401:
                # Re-authenticate
                client.refresh_token()
                continue
            elif e.response.status_code == 429:
                # Rate limited - wait and retry
                time.sleep(retry_delay * (attempt + 1))
                continue
            elif e.response.status_code >= 500:
                # Server error - may be temporary
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            raise

        except Exception as e:
            logger.error(f"Operation failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)
```

### Maintenance Automation

```python
# Automated maintenance tasks
class IntegrationMaintenance:
    """Automated maintenance for OIC integrations"""

    def __init__(self, client):
        self.client = client

    def cleanup_old_versions(self, keep_versions=3):
        """Clean up old integration versions"""

        # Group integrations by identifier
        integrations = self.client.request(
            'GET',
            '/ic/api/integration/v1/integrations'
        )

        grouped = {}
        for integration in integrations['items']:
            identifier = integration['identifier']
            if identifier not in grouped:
                grouped[identifier] = []
            grouped[identifier].append(integration)

        # Clean up old versions
        cleanup_report = []

        for identifier, versions in grouped.items():
            # Sort by version (newest first)
            versions.sort(key=lambda x: x['version'], reverse=True)

            # Keep only the specified number of versions
            if len(versions) > keep_versions:
                for old_version in versions[keep_versions:]:
                    if old_version['status'] != 'ACTIVE':
                        try:
                            # Export before deletion
                            export_integration(
                                old_version['id'],
                                f"archive/{identifier}_{old_version['version']}.iar"
                            )

                            # Delete old version
                            self.client.request(
                                'DELETE',
                                f'/ic/api/integration/v1/integrations/{old_version["id"]}'
                            )

                            cleanup_report.append({
                                'integration': f"{identifier}|{old_version['version']}",
                                'action': 'DELETED',
                                'archived': True
                            })
                        except Exception as e:
                            cleanup_report.append({
                                'integration': f"{identifier}|{old_version['version']}",
                                'action': 'FAILED',
                                'error': str(e)
                            })

        return cleanup_report

    def validate_all_connections(self):
        """Validate all connections are working"""

        connections = self.client.request(
            'GET',
            '/ic/api/integration/v1/connections'
        )

        validation_results = []

        for connection in connections['items']:
            result = self.client.request(
                'POST',
                f'/ic/api/integration/v1/connections/{connection["id"]}/test'
            )

            validation_results.append({
                'connection': connection['name'],
                'type': connection['adapterType'],
                'status': result['status'],
                'tested_at': datetime.utcnow().isoformat()
            })

        return validation_results
```

## Summary

This guide demonstrates how to effectively manage Oracle Integration Cloud integrations:

1. **Design integrations** using the OIC Visual Designer
2. **Import/Export** integration archives for deployment
3. **Manage versions** and environments systematically
4. **Monitor performance** and health continuously
5. **Automate maintenance** tasks for efficiency

### Key Takeaways

- Integrations can be created via REST API or Visual Designer
- REST API provides powerful management capabilities
- Proper version control and deployment strategies are essential
- Continuous monitoring ensures reliability
- Automation reduces operational overhead

For practical examples using tap-oic, see the [Examples](EXAMPLES.md) documentation.
