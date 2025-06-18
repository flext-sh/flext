# Monitoring and Operations Guide

> **tap-oic Version**: 2.0
> **Last Updated**: June 15, 2025

## Table of Contents

1. [Monitoring Overview](#monitoring-overview)
2. [Performance Metrics](#performance-metrics)
3. [Operational Health](#operational-health)
4. [Troubleshooting](#troubleshooting)
5. [Performance Optimization](#performance-optimization)
6. [Alerting and Notifications](#alerting-and-notifications)
7. [Maintenance Operations](#maintenance-operations)
8. [Best Practices](#best-practices)

## Monitoring Overview

### Key Monitoring Areas

1. **Integration Performance**
   - Execution times
   - Success/failure rates
   - Throughput metrics
   - Resource utilization

2. **Data Quality**
   - Record counts
   - Validation errors
   - Transformation failures
   - Schema mismatches

3. **System Health**
   - API availability
   - Connection status
   - Queue depths
   - Memory usage

### Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Metrics    │  │    Logs      │  │   Traces     │    │
│  │  Collection  │  │  Aggregation │  │   Analysis   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                           │                                 │
│                    ┌──────────────┐                        │
│                    │  Dashboards  │                        │
│                    │   & Alerts   │                        │
│                    └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Performance Metrics

### Integration Metrics

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class IntegrationMetrics:
    """Track integration performance metrics"""

    integration_id: str
    timestamp: datetime
    execution_count: int
    success_count: int
    failure_count: int
    average_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    records_processed: int
    bytes_processed: int
    error_rate: float

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'integration_id': self.integration_id,
            'timestamp': self.timestamp.isoformat(),
            'metrics': {
                'executions': {
                    'total': self.execution_count,
                    'successful': self.success_count,
                    'failed': self.failure_count,
                    'success_rate': self.success_rate,
                    'error_rate': self.error_rate
                },
                'performance': {
                    'avg_duration_ms': self.average_duration_ms,
                    'min_duration_ms': self.min_duration_ms,
                    'max_duration_ms': self.max_duration_ms
                },
                'throughput': {
                    'records': self.records_processed,
                    'bytes': self.bytes_processed,
                    'records_per_second': self.records_processed / (self.average_duration_ms / 1000)
                }
            }
        }
```

### Collecting Metrics

```python
class MetricsCollector:
    """Collect and aggregate performance metrics"""

    def __init__(self, oic_client: OICClient):
        self.client = oic_client
        self.metrics_cache = {}

    def collect_integration_metrics(
        self,
        integration_id: str,
        period: str = '1h'
    ) -> IntegrationMetrics:
        """Collect metrics for a specific integration"""

        # Get metrics from OIC API
        response = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/metrics',
            params={'period': period}
        )

        # Parse and aggregate metrics
        metrics = IntegrationMetrics(
            integration_id=integration_id,
            timestamp=datetime.utcnow(),
            execution_count=response['summary']['totalExecutions'],
            success_count=response['summary']['successfulExecutions'],
            failure_count=response['summary']['failedExecutions'],
            average_duration_ms=response['summary']['averageExecutionTime'],
            min_duration_ms=response['summary']['minExecutionTime'],
            max_duration_ms=response['summary']['maxExecutionTime'],
            records_processed=response['summary'].get('recordsProcessed', 0),
            bytes_processed=response['summary'].get('bytesProcessed', 0),
            error_rate=response['summary']['errorRate']
        )

        # Cache metrics
        self.metrics_cache[integration_id] = metrics

        return metrics

    def collect_all_metrics(self) -> List[IntegrationMetrics]:
        """Collect metrics for all active integrations"""

        # Get all active integrations
        integrations = self.client.paginate(
            '/ic/api/integration/v1/integrations',
            params={'status': 'ACTIVE'}
        )

        metrics_list = []

        for integration in integrations:
            try:
                metrics = self.collect_integration_metrics(
                    integration['id']
                )
                metrics_list.append(metrics)
            except Exception as e:
                logger.error(f"Failed to collect metrics for {integration['id']}: {e}")

        return metrics_list
```

### Real-time Monitoring

```python
import asyncio
from typing import Callable

class RealtimeMonitor:
    """Monitor integrations in real-time"""

    def __init__(
        self,
        oic_client: OICClient,
        callback: Callable[[Dict], None]
    ):
        self.client = oic_client
        self.callback = callback
        self.running = False

    async def start(self, integration_ids: List[str], interval: int = 60):
        """Start real-time monitoring"""
        self.running = True

        while self.running:
            tasks = [
                self._monitor_integration(int_id)
                for int_id in integration_ids
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Monitoring error: {result}")
                else:
                    self.callback(result)

            await asyncio.sleep(interval)

    async def _monitor_integration(self, integration_id: str) -> Dict:
        """Monitor single integration"""

        # Get current executions
        executions = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
            params={'status': 'IN_PROGRESS'}
        )

        # Get recent errors
        errors = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/errors',
            params={'period': '5m'}
        )

        return {
            'integration_id': integration_id,
            'timestamp': datetime.utcnow().isoformat(),
            'active_executions': len(executions.get('items', [])),
            'recent_errors': len(errors.get('items', [])),
            'status': 'HEALTHY' if len(errors.get('items', [])) == 0 else 'DEGRADED'
        }

    def stop(self):
        """Stop monitoring"""
        self.running = False
```

## Operational Health

### Health Check Implementation

```python
class HealthChecker:
    """Comprehensive health checking for tap-oic"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.checks = [
            self.check_api_connectivity,
            self.check_authentication,
            self.check_rate_limits,
            self.check_integration_health,
            self.check_connection_health
        ]

    def run_health_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'HEALTHY',
            'checks': {}
        }

        for check in self.checks:
            check_name = check.__name__
            try:
                check_result = check()
                results['checks'][check_name] = check_result

                if check_result['status'] != 'HEALTHY':
                    results['overall_status'] = 'DEGRADED'

            except Exception as e:
                results['checks'][check_name] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
                results['overall_status'] = 'UNHEALTHY'

        return results

    def check_api_connectivity(self) -> Dict[str, Any]:
        """Check OIC API connectivity"""
        start_time = time.time()

        try:
            response = requests.get(
                f"{self.config['instance_url']}/ic/api/integration/v1/integrations",
                timeout=10
            )
            response.raise_for_status()

            return {
                'status': 'HEALTHY',
                'response_time_ms': (time.time() - start_time) * 1000,
                'api_version': response.headers.get('X-OIC-API-Version')
            }
        except Exception as e:
            return {
                'status': 'UNHEALTHY',
                'error': str(e)
            }

    def check_authentication(self) -> Dict[str, Any]:
        """Check authentication status"""
        try:
            client = OICClient(self.config)
            # Try to get user info
            user_info = client.request('GET', '/ic/api/integration/v1/user')

            return {
                'status': 'HEALTHY',
                'user': user_info.get('email'),
                'roles': user_info.get('roles', [])
            }
        except Exception as e:
            return {
                'status': 'UNHEALTHY',
                'error': 'Authentication failed'
            }

    def check_rate_limits(self) -> Dict[str, Any]:
        """Check current rate limit status"""
        try:
            client = OICClient(self.config)
            # Make a request to check rate limit headers
            response = client.session.get(
                f"{self.config['instance_url']}/ic/api/integration/v1/integrations?limit=1"
            )

            return {
                'status': 'HEALTHY',
                'rate_limit': response.headers.get('X-RateLimit-Limit', 'Unknown'),
                'remaining': response.headers.get('X-RateLimit-Remaining', 'Unknown'),
                'reset': response.headers.get('X-RateLimit-Reset', 'Unknown')
            }
        except Exception as e:
            return {
                'status': 'UNKNOWN',
                'error': str(e)
            }
```

### System Resource Monitoring

```python
import psutil
import resource

class ResourceMonitor:
    """Monitor system resource usage"""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 90.0,
            'disk_percent': 85.0
        }

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()

        # Disk usage
        disk = psutil.disk_usage('/')

        # Process-specific stats
        process = psutil.Process()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'status': 'OK' if cpu_percent < self.thresholds['cpu_percent'] else 'HIGH'
                },
                'memory': {
                    'percent': memory.percent,
                    'used_gb': memory.used / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'status': 'OK' if memory.percent < self.thresholds['memory_percent'] else 'HIGH'
                },
                'disk': {
                    'percent': disk.percent,
                    'used_gb': disk.used / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'status': 'OK' if disk.percent < self.thresholds['disk_percent'] else 'HIGH'
                }
            },
            'process': {
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / (1024**2),
                'threads': process.num_threads(),
                'open_files': len(process.open_files())
            }
        }
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Failures

```python
class AuthenticationTroubleshooter:
    """Diagnose and fix authentication issues"""

    def diagnose(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Diagnose authentication problems"""

        results = {
            'issue': 'Authentication Failure',
            'checks': [],
            'solutions': []
        }

        # Check 1: Credentials format
        if '@' not in config.get('username', ''):
            results['checks'].append({
                'check': 'Username format',
                'status': 'FAILED',
                'message': 'Username should be an email address'
            })
            results['solutions'].append(
                'Update username to full email format'
            )

        # Check 2: Password encoding
        try:
            config['password'].encode('utf-8')
            results['checks'].append({
                'check': 'Password encoding',
                'status': 'PASSED'
            })
        except Exception:
            results['checks'].append({
                'check': 'Password encoding',
                'status': 'FAILED',
                'message': 'Password contains invalid characters'
            })
            results['solutions'].append(
                'Ensure password uses only ASCII characters'
            )

        # Check 3: Network connectivity
        try:
            response = requests.get(
                config['instance_url'],
                timeout=5
            )
            results['checks'].append({
                'check': 'Network connectivity',
                'status': 'PASSED'
            })
        except Exception as e:
            results['checks'].append({
                'check': 'Network connectivity',
                'status': 'FAILED',
                'message': str(e)
            })
            results['solutions'].append(
                'Check network connection and firewall rules'
            )

        return results
```

#### 2. Performance Issues

```python
class PerformanceTroubleshooter:
    """Diagnose performance problems"""

    def analyze_slow_integration(
        self,
        integration_id: str,
        threshold_ms: float = 5000
    ) -> Dict[str, Any]:
        """Analyze why an integration is running slowly"""

        # Get execution details
        executions = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/executions',
            params={'limit': 100}
        )

        slow_activities = []
        bottlenecks = []

        for execution in executions.get('items', []):
            if execution['duration'] > threshold_ms:
                # Get activity breakdown
                activities = self.client.request(
                    'GET',
                    f'/ic/api/monitoring/v1/executions/{execution["id"]}/activities'
                )

                for activity in activities.get('items', []):
                    if activity['duration'] > threshold_ms * 0.2:  # 20% of total
                        slow_activities.append({
                            'name': activity['name'],
                            'type': activity['type'],
                            'duration_ms': activity['duration'],
                            'percentage': (activity['duration'] / execution['duration']) * 100
                        })

        # Analyze patterns
        activity_stats = {}
        for activity in slow_activities:
            name = activity['name']
            if name not in activity_stats:
                activity_stats[name] = []
            activity_stats[name].append(activity['duration_ms'])

        for name, durations in activity_stats.items():
            avg_duration = sum(durations) / len(durations)
            if avg_duration > threshold_ms * 0.3:
                bottlenecks.append({
                    'activity': name,
                    'avg_duration_ms': avg_duration,
                    'occurrences': len(durations)
                })

        return {
            'integration_id': integration_id,
            'analysis': {
                'slow_executions': len([e for e in executions['items'] if e['duration'] > threshold_ms]),
                'total_executions': len(executions['items']),
                'bottlenecks': sorted(bottlenecks, key=lambda x: x['avg_duration_ms'], reverse=True),
                'recommendations': self._get_performance_recommendations(bottlenecks)
            }
        }

    def _get_performance_recommendations(self, bottlenecks: List[Dict]) -> List[str]:
        """Generate performance recommendations"""

        recommendations = []

        for bottleneck in bottlenecks:
            activity = bottleneck['activity']

            if 'database' in activity.lower():
                recommendations.append(
                    f"Optimize database queries in {activity} - consider indexing or query optimization"
                )
            elif 'transform' in activity.lower():
                recommendations.append(
                    f"Review transformation logic in {activity} - consider simplifying mappings"
                )
            elif 'api' in activity.lower() or 'rest' in activity.lower():
                recommendations.append(
                    f"Check API response times for {activity} - consider caching or pagination"
                )

        return recommendations
```

#### 3. Data Quality Issues

```python
class DataQualityAnalyzer:
    """Analyze and report data quality issues"""

    def analyze_validation_errors(
        self,
        integration_id: str,
        time_period: str = '24h'
    ) -> Dict[str, Any]:
        """Analyze validation errors"""

        # Get error details
        errors = self.client.request(
            'GET',
            f'/ic/api/monitoring/v1/integrations/{integration_id}/errors',
            params={'period': time_period, 'type': 'VALIDATION'}
        )

        error_patterns = {}
        field_errors = {}

        for error in errors.get('items', []):
            # Extract error details
            error_type = error.get('errorType', 'UNKNOWN')
            field = error.get('field', 'UNKNOWN')

            if error_type not in error_patterns:
                error_patterns[error_type] = 0
            error_patterns[error_type] += 1

            if field != 'UNKNOWN':
                if field not in field_errors:
                    field_errors[field] = []
                field_errors[field].append(error.get('message'))

        return {
            'integration_id': integration_id,
            'period': time_period,
            'total_errors': len(errors.get('items', [])),
            'error_patterns': error_patterns,
            'field_errors': {
                field: {
                    'count': len(messages),
                    'sample_messages': list(set(messages))[:5]
                }
                for field, messages in field_errors.items()
            },
            'recommendations': self._get_data_quality_recommendations(error_patterns, field_errors)
        }
```

## Performance Optimization

### Optimization Strategies

#### 1. Connection Pooling Optimization

```python
class ConnectionPoolOptimizer:
    """Optimize connection pool settings"""

    def optimize_pool_size(
        self,
        current_config: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate optimal pool size based on metrics"""

        # Analyze connection usage patterns
        avg_concurrent_connections = metrics.get('avg_concurrent_connections', 5)
        peak_concurrent_connections = metrics.get('peak_concurrent_connections', 10)
        connection_wait_time = metrics.get('avg_connection_wait_ms', 0)

        # Calculate optimal pool size
        optimal_pool_size = int(peak_concurrent_connections * 1.2)  # 20% buffer
        optimal_max_size = int(peak_concurrent_connections * 1.5)   # 50% buffer

        # Recommend settings
        recommendations = {
            'pool_connections': max(10, optimal_pool_size),
            'pool_maxsize': max(20, optimal_max_size),
            'pool_block': connection_wait_time > 1000,  # Block if wait times are high
            'keepalive': True,
            'keepalive_interval': 30
        }

        return recommendations
```

#### 2. Batch Size Optimization

```python
class BatchSizeOptimizer:
    """Optimize batch sizes for better performance"""

    def calculate_optimal_batch_size(
        self,
        record_size_bytes: int,
        processing_time_per_record_ms: float,
        available_memory_mb: int = 1024
    ) -> int:
        """Calculate optimal batch size"""

        # Memory constraint
        max_batch_by_memory = (available_memory_mb * 1024 * 1024) // (record_size_bytes * 2)

        # Time constraint (aim for 1-5 second batches)
        target_batch_time_ms = 2000
        max_batch_by_time = int(target_batch_time_ms / processing_time_per_record_ms)

        # Network constraint (10MB payload limit)
        max_batch_by_network = (10 * 1024 * 1024) // record_size_bytes

        # Take minimum of all constraints
        optimal_batch = min(
            max_batch_by_memory,
            max_batch_by_time,
            max_batch_by_network,
            1000  # Hard upper limit
        )

        return max(10, optimal_batch)  # At least 10 records
```

#### 3. Caching Strategy

```python
from functools import lru_cache
import hashlib

class CacheOptimizer:
    """Implement intelligent caching strategies"""

    def __init__(self, cache_size_mb: int = 100):
        self.cache_size_mb = cache_size_mb
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }

    @lru_cache(maxsize=1000)
    def get_cached_integration(self, integration_id: str, ttl_hash: int) -> Dict:
        """Cache integration metadata"""
        self.cache_stats['misses'] += 1
        return self.client.get_integration(integration_id)

    def get_integration_with_cache(self, integration_id: str, ttl_seconds: int = 300) -> Dict:
        """Get integration with cache"""
        # Create TTL hash
        ttl_hash = int(time.time() // ttl_seconds)

        # Try cache first
        result = self.get_cached_integration(integration_id, ttl_hash)
        if result:
            self.cache_stats['hits'] += 1

        return result

    def get_cache_effectiveness(self) -> Dict[str, Any]:
        """Calculate cache effectiveness metrics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']

        return {
            'hit_rate': self.cache_stats['hits'] / total_requests if total_requests > 0 else 0,
            'miss_rate': self.cache_stats['misses'] / total_requests if total_requests > 0 else 0,
            'total_requests': total_requests,
            'cache_size_mb': self.cache_size_mb,
            'recommendations': self._get_cache_recommendations()
        }

    def _get_cache_recommendations(self) -> List[str]:
        """Generate cache optimization recommendations"""

        recommendations = []
        hit_rate = self.get_cache_effectiveness()['hit_rate']

        if hit_rate < 0.7:
            recommendations.append("Consider increasing cache TTL for better hit rate")
        if hit_rate > 0.95:
            recommendations.append("Cache is very effective, consider increasing size")
        if self.cache_stats['evictions'] > self.cache_stats['hits']:
            recommendations.append("High eviction rate - increase cache size")

        return recommendations
```

## Alerting and Notifications

### Alert Configuration

```python
from enum import Enum
from typing import List, Callable

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertRule:
    """Define alert rules"""

    def __init__(
        self,
        name: str,
        condition: Callable[[Dict], bool],
        severity: AlertSeverity,
        message_template: str
    ):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message_template = message_template

class AlertManager:
    """Manage alerts and notifications"""

    def __init__(self):
        self.rules = []
        self.channels = []

    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.rules.append(rule)

    def add_channel(self, channel: 'NotificationChannel'):
        """Add notification channel"""
        self.channels.append(channel)

    def evaluate_metrics(self, metrics: Dict[str, Any]):
        """Evaluate metrics against alert rules"""

        for rule in self.rules:
            if rule.condition(metrics):
                alert = {
                    'name': rule.name,
                    'severity': rule.severity.value,
                    'message': rule.message_template.format(**metrics),
                    'timestamp': datetime.utcnow().isoformat(),
                    'metrics': metrics
                }

                self._send_alert(alert)

    def _send_alert(self, alert: Dict[str, Any]):
        """Send alert to all configured channels"""

        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.__class__.__name__}: {e}")
```

### Notification Channels

```python
import smtplib
from email.mime.text import MIMEText
import requests

class NotificationChannel:
    """Base class for notification channels"""

    def send(self, alert: Dict[str, Any]):
        """Send alert notification"""
        raise NotImplementedError

class EmailChannel(NotificationChannel):
    """Email notification channel"""

    def __init__(self, smtp_config: Dict[str, Any], recipients: List[str]):
        self.smtp_config = smtp_config
        self.recipients = recipients

    def send(self, alert: Dict[str, Any]):
        """Send email alert"""

        msg = MIMEText(f"""
        Alert: {alert['name']}
        Severity: {alert['severity']}
        Time: {alert['timestamp']}

        {alert['message']}

        Metrics:
        {json.dumps(alert['metrics'], indent=2)}
        """)

        msg['Subject'] = f"[{alert['severity'].upper()}] {alert['name']}"
        msg['From'] = self.smtp_config['from_address']
        msg['To'] = ', '.join(self.recipients)

        with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
            if self.smtp_config.get('use_tls'):
                server.starttls()
            if self.smtp_config.get('username'):
                server.login(
                    self.smtp_config['username'],
                    self.smtp_config['password']
                )
            server.send_message(msg)

class SlackChannel(NotificationChannel):
    """Slack notification channel"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, alert: Dict[str, Any]):
        """Send Slack alert"""

        color_map = {
            'info': '#36a64f',
            'warning': '#ff9900',
            'error': '#ff0000',
            'critical': '#990000'
        }

        payload = {
            'attachments': [{
                'color': color_map.get(alert['severity'], '#000000'),
                'title': alert['name'],
                'text': alert['message'],
                'fields': [
                    {
                        'title': 'Severity',
                        'value': alert['severity'],
                        'short': True
                    },
                    {
                        'title': 'Time',
                        'value': alert['timestamp'],
                        'short': True
                    }
                ],
                'footer': 'tap-oic monitoring'
            }]
        }

        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
```

### Alert Rules Examples

```python
# Define common alert rules
def setup_default_alerts(alert_manager: AlertManager):
    """Setup default alert rules"""

    # High error rate alert
    alert_manager.add_rule(AlertRule(
        name="High Error Rate",
        condition=lambda m: m.get('error_rate', 0) > 0.05,
        severity=AlertSeverity.ERROR,
        message_template="Integration {integration_id} has error rate of {error_rate:.1%}"
    ))

    # Performance degradation alert
    alert_manager.add_rule(AlertRule(
        name="Performance Degradation",
        condition=lambda m: m.get('avg_duration_ms', 0) > 5000,
        severity=AlertSeverity.WARNING,
        message_template="Integration {integration_id} average duration is {avg_duration_ms}ms"
    ))

    # Integration failure alert
    alert_manager.add_rule(AlertRule(
        name="Integration Failed",
        condition=lambda m: m.get('status') == 'FAILED',
        severity=AlertSeverity.CRITICAL,
        message_template="Integration {integration_id} has failed: {error_message}"
    ))

    # Resource usage alert
    alert_manager.add_rule(AlertRule(
        name="High Resource Usage",
        condition=lambda m: m.get('cpu_percent', 0) > 90 or m.get('memory_percent', 0) > 90,
        severity=AlertSeverity.WARNING,
        message_template="High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%"
    ))
```

## Maintenance Operations

### Automated Maintenance

```python
class MaintenanceScheduler:
    """Schedule and execute maintenance operations"""

    def __init__(self, oic_client: OICClient):
        self.client = oic_client
        self.tasks = []

    def add_task(
        self,
        name: str,
        operation: Callable,
        schedule: str,  # Cron expression
        enabled: bool = True
    ):
        """Add maintenance task"""
        self.tasks.append({
            'name': name,
            'operation': operation,
            'schedule': schedule,
            'enabled': enabled,
            'last_run': None,
            'next_run': self._calculate_next_run(schedule)
        })

    def cleanup_old_executions(self, retention_days: int = 30):
        """Clean up old execution history"""

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Get all integrations
        integrations = list(self.client.paginate('/ic/api/integration/v1/integrations'))

        cleaned = 0
        for integration in integrations:
            # Get old executions
            executions = self.client.request(
                'GET',
                f'/ic/api/monitoring/v1/integrations/{integration["id"]}/executions',
                params={
                    'endTime': cutoff_date.isoformat(),
                    'limit': 1000
                }
            )

            # Archive or delete old executions
            for execution in executions.get('items', []):
                try:
                    self.client.request(
                        'DELETE',
                        f'/ic/api/monitoring/v1/executions/{execution["id"]}'
                    )
                    cleaned += 1
                except Exception as e:
                    logger.warning(f"Failed to clean execution {execution['id']}: {e}")

        return {'executions_cleaned': cleaned}

    def optimize_integrations(self):
        """Optimize integration configurations"""

        optimizations = []

        # Get all active integrations
        integrations = list(self.client.paginate(
            '/ic/api/integration/v1/integrations',
            params={'status': 'ACTIVE'}
        ))

        for integration in integrations:
            # Get performance metrics
            metrics = self.client.request(
                'GET',
                f'/ic/api/monitoring/v1/integrations/{integration["id"]}/metrics',
                params={'period': '7d'}
            )

            # Check if optimization needed
            if metrics['summary']['averageExecutionTime'] > 10000:  # >10 seconds
                optimization = {
                    'integration_id': integration['id'],
                    'current_avg_time': metrics['summary']['averageExecutionTime'],
                    'recommendations': []
                }

                # Add recommendations based on patterns
                if integration.get('pattern') == 'SCHEDULED_ORCHESTRATION':
                    optimization['recommendations'].append(
                        'Consider increasing batch size for better throughput'
                    )

                optimizations.append(optimization)

        return optimizations
```

### Backup and Recovery

```python
import zipfile
import json

class BackupManager:
    """Manage integration backups"""

    def __init__(self, oic_client: OICClient, backup_path: str):
        self.client = oic_client
        self.backup_path = backup_path

    def backup_all_integrations(self) -> str:
        """Backup all integrations to archive"""

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.backup_path}/oic_backup_{timestamp}.zip"

        with zipfile.ZipFile(backup_file, 'w') as zf:
            # Get all integrations
            integrations = list(self.client.paginate('/ic/api/integration/v1/integrations'))

            # Save integration list
            zf.writestr(
                'integrations.json',
                json.dumps(integrations, indent=2)
            )

            # Export each integration
            for integration in integrations:
                try:
                    # Get IAR file
                    iar_content = self.client.request_binary(
                        'GET',
                        f'/ic/api/integration/v1/integrations/{integration["id"]}/archive'
                    )

                    # Save to archive
                    zf.writestr(
                        f'integrations/{integration["identifier"]}.iar',
                        iar_content
                    )
                except Exception as e:
                    logger.error(f"Failed to backup {integration['id']}: {e}")

            # Backup connections
            connections = list(self.client.paginate('/ic/api/integration/v1/connections'))
            zf.writestr(
                'connections.json',
                json.dumps(connections, indent=2)
            )

            # Backup projects
            projects = list(self.client.paginate('/ic/api/projects/v1/projects'))
            zf.writestr(
                'projects.json',
                json.dumps(projects, indent=2)
            )

        return backup_file

    def restore_from_backup(self, backup_file: str, dry_run: bool = True) -> Dict[str, Any]:
        """Restore integrations from backup"""

        results = {
            'projects_restored': 0,
            'connections_restored': 0,
            'integrations_restored': 0,
            'errors': []
        }

        with zipfile.ZipFile(backup_file, 'r') as zf:
            # Restore projects first
            if 'projects.json' in zf.namelist():
                projects = json.loads(zf.read('projects.json'))
                for project in projects:
                    if not dry_run:
                        try:
                            self.client.create_project(project)
                            results['projects_restored'] += 1
                        except Exception as e:
                            results['errors'].append(f"Project {project['name']}: {e}")

            # Restore connections
            if 'connections.json' in zf.namelist():
                connections = json.loads(zf.read('connections.json'))
                for connection in connections:
                    if not dry_run:
                        try:
                            self.client.create_connection(connection)
                            results['connections_restored'] += 1
                        except Exception as e:
                            results['errors'].append(f"Connection {connection['name']}: {e}")

            # Restore integrations
            for filename in zf.namelist():
                if filename.startswith('integrations/') and filename.endswith('.iar'):
                    if not dry_run:
                        try:
                            iar_content = zf.read(filename)
                            self.client.import_integration(iar_content)
                            results['integrations_restored'] += 1
                        except Exception as e:
                            results['errors'].append(f"Integration {filename}: {e}")

        return results
```

## Best Practices

### 1. Monitoring Strategy

```python
# Comprehensive monitoring setup
monitoring_config = {
    'metrics': {
        'collection_interval': 60,  # seconds
        'retention_period': 30,     # days
        'aggregation_levels': ['1m', '5m', '1h', '1d']
    },
    'alerts': {
        'error_rate_threshold': 0.05,
        'response_time_threshold': 5000,
        'resource_usage_threshold': 80
    },
    'dashboards': {
        'refresh_interval': 30,
        'default_time_range': '6h'
    }
}
```

### 2. Performance Baselines

```python
class PerformanceBaseline:
    """Establish and track performance baselines"""

    def establish_baseline(
        self,
        integration_id: str,
        period_days: int = 7
    ) -> Dict[str, Any]:
        """Establish performance baseline"""

        # Collect historical metrics
        metrics = self.collect_historical_metrics(integration_id, period_days)

        # Calculate baselines
        baseline = {
            'integration_id': integration_id,
            'period': f'{period_days}d',
            'established': datetime.utcnow().isoformat(),
            'metrics': {
                'avg_duration_ms': {
                    'p50': self._percentile(metrics['durations'], 50),
                    'p90': self._percentile(metrics['durations'], 90),
                    'p99': self._percentile(metrics['durations'], 99)
                },
                'error_rate': {
                    'avg': sum(metrics['error_rates']) / len(metrics['error_rates']),
                    'max': max(metrics['error_rates'])
                },
                'throughput': {
                    'avg_records_per_hour': sum(metrics['records']) / (period_days * 24),
                    'peak_records_per_hour': max(metrics['hourly_records'])
                }
            }
        }

        return baseline
```

### 3. Incident Response

```python
class IncidentResponse:
    """Automated incident response procedures"""

    def __init__(self, oic_client: OICClient):
        self.client = oic_client
        self.runbooks = {}

    def register_runbook(
        self,
        incident_type: str,
        runbook: List[Callable]
    ):
        """Register incident response runbook"""
        self.runbooks[incident_type] = runbook

    def handle_incident(
        self,
        incident_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute incident response runbook"""

        if incident_type not in self.runbooks:
            return {'error': f'No runbook for incident type: {incident_type}'}

        results = {
            'incident_type': incident_type,
            'start_time': datetime.utcnow().isoformat(),
            'steps': []
        }

        for step in self.runbooks[incident_type]:
            step_name = step.__name__
            try:
                step_result = step(context)
                results['steps'].append({
                    'name': step_name,
                    'status': 'SUCCESS',
                    'result': step_result
                })
            except Exception as e:
                results['steps'].append({
                    'name': step_name,
                    'status': 'FAILED',
                    'error': str(e)
                })
                # Stop on failure
                break

        results['end_time'] = datetime.utcnow().isoformat()
        return results
```

## Summary

This monitoring and operations guide provides comprehensive strategies for:

1. **Real-time monitoring** of integration performance and health
2. **Troubleshooting** common issues with diagnostic tools
3. **Performance optimization** through intelligent resource management
4. **Alerting** with multi-channel notifications
5. **Maintenance** automation and backup strategies
6. **Incident response** procedures

Implement these practices to ensure reliable, performant operation of your OIC integrations.
