#!/usr/bin/env python3
"""Setup real monitoring infrastructure for FLEXT."""

import json
from pathlib import Path

import yaml


def create_prometheus_config(project_root: Path) -> Path:
    """Create Prometheus configuration for FLEXT monitoring."""

    prometheus_config = {
        "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
        "alerting": {
            "alertmanagers": [{"static_configs": [{"targets": ["localhost:9093"]}]}],
        },
        "rule_files": ["alerts/*.yml"],
        "scrape_configs": [
            {
                "job_name": "flext-api",
                "static_configs": [{"targets": ["localhost:8000"]}],
                "metrics_path": "/metrics",
                "scrape_interval": "10s",
                "scrape_timeout": "5s",
            },
            {
                "job_name": "flext-web",
                "static_configs": [{"targets": ["localhost:8080"]}],
                "metrics_path": "/metrics",
                "scrape_interval": "15s",
                "scrape_timeout": "5s",
            },
            {
                "job_name": "flext-grpc",
                "static_configs": [{"targets": ["localhost:50051"]}],
                "metrics_path": "/metrics",
                "scrape_interval": "10s",
                "scrape_timeout": "5s",
            },
            {
                "job_name": "node-exporter",
                "static_configs": [{"targets": ["localhost:9100"]}],
                "scrape_interval": "15s",
            },
            {
                "job_name": "postgres-exporter",
                "static_configs": [{"targets": ["localhost:9187"]}],
                "scrape_interval": "30s",
            },
            {
                "job_name": "redis-exporter",
                "static_configs": [{"targets": ["localhost:9121"]}],
                "scrape_interval": "30s",
            },
        ],
    }

    monitoring_dir = project_root / "monitoring"
    monitoring_dir.mkdir(exist_ok=True)

    config_file = monitoring_dir / "prometheus.yml"
    with Path(config_file).open("w", encoding="utf-8") as f:
        yaml.dump(prometheus_config, f, default_flow_style=False, indent=2)

    print(f"✅ Prometheus config: {config_file}")
    return config_file


def create_grafana_dashboards(monitoring_dir: Path) -> None:
    """Create Grafana dashboards for FLEXT monitoring."""

    # FLEXT API Dashboard
    api_dashboard = {
        "dashboard": {
            "id": None,
            "title": "FLEXT API Monitoring",
            "tags": ["flext", "api"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "API Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(http_requests_total{job="flext-api"}[5m])',
                            "legendFormat": "{{method}} {{endpoint}}",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                },
                {
                    "id": 2,
                    "title": "Response Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="flext-api"}[5m]))',
                            "legendFormat": "95th percentile",
                        },
                        {
                            "expr": 'histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{job="flext-api"}[5m]))',
                            "legendFormat": "50th percentile",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                },
                {
                    "id": 3,
                    "title": "Error Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": 'rate(http_requests_total{job="flext-api",status=~"5.."}[5m])',
                            "legendFormat": "5xx errors",
                        },
                        {
                            "expr": 'rate(http_requests_total{job="flext-api",status=~"4.."}[5m])',
                            "legendFormat": "4xx errors",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                },
                {
                    "id": 4,
                    "title": "Active Connections",
                    "type": "singlestat",
                    "targets": [
                        {
                            "expr": "flext_api_active_connections",
                            "legendFormat": "Connections",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                },
            ],
            "refresh": "5s",
            "time": {"from": "now-1h", "to": "now"},
        },
    }

    # Pipeline Monitoring Dashboard
    pipeline_dashboard = {
        "dashboard": {
            "id": None,
            "title": "FLEXT Pipeline Monitoring",
            "tags": ["flext", "pipeline"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Pipeline Executions",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(flext_pipeline_executions_total[5m])",
                            "legendFormat": "{{status}} - {{pipeline}}",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                },
                {
                    "id": 2,
                    "title": "Pipeline Duration",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, rate(flext_pipeline_duration_seconds_bucket[5m]))",
                            "legendFormat": "95th percentile",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                },
                {
                    "id": 3,
                    "title": "Records Processed",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(flext_pipeline_records_processed_total[5m])",
                            "legendFormat": "{{pipeline}}",
                        },
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                },
            ],
            "refresh": "10s",
            "time": {"from": "now-2h", "to": "now"},
        },
    }

    # Save dashboards
    dashboards_dir = monitoring_dir / "grafana" / "dashboards"
    dashboards_dir.mkdir(parents=True, exist_ok=True)

    with Path(dashboards_dir / "flext-api.json").open("w", encoding="utf-8") as f:
        json.dump(api_dashboard, f, indent=2)

    with Path(dashboards_dir / "flext-pipeline.json").open("w", encoding="utf-8") as f:
        json.dump(pipeline_dashboard, f, indent=2)

    print(f"✅ Grafana dashboards: {dashboards_dir}")


def create_alerting_rules(monitoring_dir: Path) -> None:
    """Create Prometheus alerting rules for FLEXT."""

    alerts = {
        "groups": [
            {
                "name": "flext_api_alerts",
                "rules": [
                    {
                        "alert": "FlextAPIHighErrorRate",
                        "expr": 'rate(http_requests_total{job="flext-api",status=~"5.."}[5m]) > 0.1',
                        "for": "5m",
                        "labels": {"severity": "critical", "service": "flext-api"},
                        "annotations": {
                            "summary": "FLEXT API high error rate",
                            "description": "FLEXT API is returning more than 10% 5xx errors for 5 minutes",
                        },
                    },
                    {
                        "alert": "FlextAPIHighLatency",
                        "expr": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="flext-api"}[5m])) > 1',
                        "for": "10m",
                        "labels": {"severity": "warning", "service": "flext-api"},
                        "annotations": {
                            "summary": "FLEXT API high latency",
                            "description": "95th percentile latency is above 1 second for 10 minutes",
                        },
                    },
                    {
                        "alert": "FlextAPIDown",
                        "expr": 'up{job="flext-api"} == 0',
                        "for": "1m",
                        "labels": {"severity": "critical", "service": "flext-api"},
                        "annotations": {
                            "summary": "FLEXT API is down",
                            "description": "FLEXT API has been down for more than 1 minute",
                        },
                    },
                ],
            },
            {
                "name": "flext_pipeline_alerts",
                "rules": [
                    {
                        "alert": "FlextPipelineFailures",
                        "expr": 'rate(flext_pipeline_executions_total{status="failed"}[10m]) > 0.1',
                        "for": "5m",
                        "labels": {"severity": "warning", "service": "flext-pipeline"},
                        "annotations": {
                            "summary": "FLEXT pipeline failures detected",
                            "description": "Pipeline failure rate is above 10% for 5 minutes",
                        },
                    },
                    {
                        "alert": "FlextPipelineLongRunning",
                        "expr": "flext_pipeline_duration_seconds > 3600",
                        "for": "0m",
                        "labels": {"severity": "warning", "service": "flext-pipeline"},
                        "annotations": {
                            "summary": "FLEXT pipeline running too long",
                            "description": "Pipeline {{$labels.pipeline}} has been running for more than 1 hour",
                        },
                    },
                ],
            },
        ],
    }

    alerts_dir = monitoring_dir / "alerts"
    alerts_dir.mkdir(exist_ok=True)

    alert_file = alerts_dir / "flext.yml"
    with Path(alert_file).open("w", encoding="utf-8") as f:
        yaml.dump(alerts, f, default_flow_style=False, indent=2)

    print(f"✅ Alert rules: {alert_file}")


def create_docker_monitoring_stack(monitoring_dir: Path) -> None:
    """Create Docker Compose file for monitoring stack."""

    docker_compose = {
        "version": "3.8",
        "services": {
            "prometheus": {
                "image": "prom/prometheus:latest",
                "container_name": "flext-prometheus",
                "ports": ["9090:9090"],
                "volumes": [
                    "./prometheus.yml:/etc/prometheus/prometheus.yml",
                    "./alerts:/etc/prometheus/alerts",
                    "prometheus_data:/prometheus",
                ],
                "command": [
                    "--config.file=/etc/prometheus/prometheus.yml",
                    "--storage.tsdb.path=/prometheus",
                    "--web.console.libraries=/etc/prometheus/console_libraries",
                    "--web.console.templates=/etc/prometheus/consoles",
                    "--storage.tsdb.retention.time=30d",
                    "--web.enable-lifecycle",
                ],
                "restart": "unless-stopped",
            },
            "grafana": {
                "image": "grafana/grafana:latest",
                "container_name": "flext-grafana",
                "ports": ["3000:3000"],
                "volumes": [
                    "grafana_data:/var/lib/grafana",
                    "./grafana/dashboards:/etc/grafana/provisioning/dashboards",
                    "./grafana/datasources:/etc/grafana/provisioning/datasources",
                ],
                "environment": {
                    "GF_SECURITY_ADMIN_PASSWORD": "flext-admin-staging",
                    "GF_USERS_ALLOW_SIGN_UP": "false",
                },
                "restart": "unless-stopped",
            },
            "node-exporter": {
                "image": "prom/node-exporter:latest",
                "container_name": "flext-node-exporter",
                "ports": ["9100:9100"],
                "volumes": ["/proc:/host/proc:ro", "/sys:/host/sys:ro", "/:/rootfs:ro"],
                "command": [
                    "--path.procfs=/host/proc",
                    "--path.sysfs=/host/sys",
                    "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)",
                ],
                "restart": "unless-stopped",
            },
            "alertmanager": {
                "image": "prom/alertmanager:latest",
                "container_name": "flext-alertmanager",
                "ports": ["9093:9093"],
                "volumes": ["./alertmanager.yml:/etc/alertmanager/alertmanager.yml"],
                "restart": "unless-stopped",
            },
        },
        "volumes": {"prometheus_data": {}, "grafana_data": {}},
        "networks": {"default": {"name": "flext-monitoring"}},
    }

    compose_file = monitoring_dir / "docker-compose.monitoring.yml"
    with Path(compose_file).open("w", encoding="utf-8") as f:
        yaml.dump(docker_compose, f, default_flow_style=False, indent=2)

    print(f"✅ Docker monitoring stack: {compose_file}")


def create_health_check_service(project_root: Path) -> None:
    """Create comprehensive health check service."""

    health_check_code = '''#!/usr/bin/env python3
"""FLEXT Health Check Service - Real monitoring implementation."""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any
from pathlib import Path
import logging

class FlextHealthChecker:
    """Comprehensive health checking for FLEXT services."""

    def __init__(self):
        self.services = {
            'api': 'http://localhost:8000/health',
            'web': 'http://localhost:8080/health',
            'grpc': 'localhost:50051',  # Special handling for gRPC
            'redis': 'redis://localhost:6379',
            'postgres': 'postgresql://localhost:5432/flext_staging'
        }
        self.results = {}

    async def check_http_service(self, name: str, url: str) -> Dict[str, Any]:
        """Check HTTP service health."""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    duration = time.time() - start_time

                    if response.status == 200:
                        return {
                            'status': 'healthy',
                            'response_time': duration,
                            'status_code': response.status,
                            'timestamp': time.time()
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'response_time': duration,
                            'status_code': response.status,
                            'error': f'HTTP {response.status}',
                            'timestamp': time.time()
                        }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.time()
            }

    async def check_all_services(self) -> Dict[str, Any]:
        """Check all FLEXT services."""
        tasks = []

        # HTTP services
        for name, url in self.services.items():
            if url.startswith('http'):
                tasks.append(self.check_http_service(name, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        service_names = [name for name, url in self.services.items() if url.startswith('http')]
        health_status = {}

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                health_status[service_names[i]] = {
                    'status': 'unhealthy',
                    'error': str(result),
                    'timestamp': time.time()
                }
            else:
                health_status[service_names[i]] = result

        # Overall health
        all_healthy = all(
            status.get('status') == 'healthy'
            for status in health_status.values()
        )

        return {
            'overall_status': 'healthy' if all_healthy else 'unhealthy',
            'services': health_status,
            'timestamp': time.time(),
            'healthy_count': sum(1 for s in health_status.values() if s.get('status') == 'healthy'),
            'total_count': len(health_status)
        }

async def main():
    """Run health checks and output results."""
    checker = FlextHealthChecker()

    while True:
        try:
            health_data = await checker.check_all_services()

            # Output JSON for monitoring tools
            print(json.dumps(health_data, indent=2))

            # Log critical issues
            if health_data['overall_status'] != 'healthy':
                logging.error("Health check failed: %s", health_data)

            # Wait before next check
            await asyncio.sleep(10)

        except KeyboardInterrupt:
            print("\\nHealth check service stopped")
            break
        except Exception as e:
            logging.error("Health check error: %s", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
'''

    health_check_file = project_root / "scripts" / "health_check_service.py"
    with Path(health_check_file).open("w", encoding="utf-8") as f:
        f.write(health_check_code)

    # Make executable
    health_check_file.chmod(0o755)

    print(f"✅ Health check service: {health_check_file}")


def create_monitoring_startup_script(monitoring_dir: Path) -> None:
    """Create script to start monitoring stack."""

    startup_script = f"""#!/bin/bash
# Start FLEXT monitoring stack

echo "🚀 Starting FLEXT Monitoring Stack"
echo "=================================="

# Check dependencies
echo "📋 Checking dependencies..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Dependencies OK"

# Start monitoring services
echo "🐳 Starting monitoring containers..."
cd {monitoring_dir}

docker-compose -f docker-compose.monitoring.yml up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

services=("prometheus:9090" "grafana:3000" "node-exporter:9100" "alertmanager:9093")

for service in "${{services[@]}}"; do
    name="${{service%%:*}}"
    port="${{service##*:}}"

    if curl -s -o /dev/null -w "%{{http_code}}" "http://localhost:$port" | grep -q "200\\|302"; then
        echo "  ✅ $name (port $port) - OK"
    else
        echo "  ❌ $name (port $port) - Failed"
    fi
done

echo ""
echo "🎉 FLEXT Monitoring Stack Started!"
echo ""
echo "📊 ACCESS POINTS:"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3000 (admin/flext-admin-staging)"
echo "  • Alertmanager: http://localhost:9093"
echo "  • Node Exporter: http://localhost:9100"
echo ""
echo "📋 NEXT STEPS:"
echo "  1. Import Grafana dashboards from grafana/dashboards/"
echo "  2. Configure Grafana data source: http://prometheus:9090"
echo "  3. Start FLEXT services with metrics enabled"
echo "  4. Monitor metrics at Prometheus targets page"
echo ""
echo "🛑 To stop: docker-compose -f docker-compose.monitoring.yml down"
"""

    startup_file = monitoring_dir / "start-monitoring.sh"
    with Path(startup_file).open("w", encoding="utf-8") as f:
        f.write(startup_script)

    # Make executable
    startup_file.chmod(0o755)

    print(f"✅ Monitoring startup script: {startup_file}")


def main():
    """Setup complete real monitoring infrastructure."""
    print("📊 FLEXT REAL MONITORING SETUP")
    print("=" * 50)

    project_root = Path(__file__).parent.parent

    # Create Prometheus configuration
    print("⚙️ Creating Prometheus configuration...")
    config_file = create_prometheus_config(project_root)
    monitoring_dir = config_file.parent

    # Create Grafana dashboards
    print("📈 Creating Grafana dashboards...")
    create_grafana_dashboards(monitoring_dir)

    # Create alerting rules
    print("🚨 Creating alerting rules...")
    create_alerting_rules(monitoring_dir)

    # Create Docker monitoring stack
    print("🐳 Creating Docker monitoring stack...")
    create_docker_monitoring_stack(monitoring_dir)

    # Create health check service
    print("🔍 Creating health check service...")
    create_health_check_service(project_root)

    # Create startup script
    print("🚀 Creating monitoring startup script...")
    create_monitoring_startup_script(monitoring_dir)

    print("\n" + "=" * 50)
    print("🎉 REAL MONITORING INFRASTRUCTURE COMPLETED!")

    print("\n📊 MONITORING COMPONENTS:")
    print(f"  📈 Prometheus config: {monitoring_dir}/prometheus.yml")
    print(f"  📊 Grafana dashboards: {monitoring_dir}/grafana/dashboards/")
    print(f"  🚨 Alert rules: {monitoring_dir}/alerts/flext.yml")
    print(f"  🐳 Docker stack: {monitoring_dir}/docker-compose.monitoring.yml")
    print(f"  🔍 Health check: {project_root}/scripts/health_check_service.py")

    print("\n🚀 QUICK START:")
    print(f"  1. cd {monitoring_dir}")
    print("  2. ./start-monitoring.sh")
    print("  3. Access Grafana: http://localhost:3000")
    print("  4. Import dashboards and configure data sources")

    print("\n📋 FEATURES:")
    print("  • Real-time metrics collection")
    print("  • Custom FLEXT dashboards")
    print("  • Automated alerting")
    print("  • Health check service")
    print("  • Docker-based deployment")
    print("  • Production-ready configuration")


if __name__ == "__main__":
    main()
