#!/bin/bash
# Start FLEXT monitoring stack

echo "🚀 Starting FLEXT Monitoring Stack"
echo "=================================="

# Check dependencies
echo "📋 Checking dependencies..."

if ! command -v docker &>/dev/null; then
	echo "❌ Docker not found. Please install Docker first."
	exit 1
fi

if ! command -v docker-compose &>/dev/null; then
	echo "❌ Docker Compose not found. Please install Docker Compose first."
	exit 1
fi

echo "✅ Dependencies OK"

# Start monitoring services
echo "🐳 Starting monitoring containers..."
cd /home/marlonsc/flext/monitoring

docker-compose -f docker-compose.monitoring.yml up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

services=("prometheus:9090" "grafana:3000" "node-exporter:9100" "alertmanager:9093")

for service in "${services[@]}"; do
	name="${service%%:*}"
	port="${service##*:}"

	if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" | grep -q "200\|302"; then
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
echo "  • Grafana: http://localhost:3000 (REDACTED_LDAP_BIND_PASSWORD/flext-REDACTED_LDAP_BIND_PASSWORD-staging)"
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
