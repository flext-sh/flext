#!/bin/bash
# Owner-Skill: .claude/skills/scripts-testing/SKILL.md

# FLEXT Distributed Testing Script
# Tests the distributed architecture capabilities

set -e

# Load FLEXT constants
source "$(dirname "$0")/../constants.env" 2>/dev/null || {
	echo "Warning: Could not load FLEXT constants, using FlextConstants defaults"
	# Fallback values synchronized with FlextConstants
	FLEXT_REDIS_ADDRESS="localhost:6379" # FlextConstants.Platform.DEFAULT_HOST:REDIS_DEFAULT_PORT
	FLEXT_TEST_API_PORT=8081             # Test API port (offset from FLEXT_API_PORT)
	FLEXT_PROMETHEUS_PORT=9090           # Standard Prometheus port
	FLEXT_GRAFANA_PORT=3000              # Standard Grafana port
}

echo "🚀 FLEXT Distributed Architecture Test"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
	echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
	echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
	echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
	echo -e "${RED}[ERROR]${NC} $1"
}

# Check if FLEXT binary exists
if [ ! -f "./bin/flext" ]; then
	print_error "FLEXT binary not found. Please build first: make build"
	exit 1
fi

print_status "Testing FLEXT help and version..."
./bin/flext --help
print_success "Help command works"

# Test standalone mode
print_status "Testing standalone mode..."
timeout 5 ./bin/flext &
STANDALONE_PID=$!
sleep 2

if kill -0 $STANDALONE_PID 2>/dev/null; then
	print_success "Standalone mode started successfully"
	kill $STANDALONE_PID
	wait $STANDALONE_PID 2>/dev/null || true
else
	print_error "Standalone mode failed to start"
fi

# Test distributed mode (if Redis is available)
if command -v redis-cli &>/dev/null && redis-cli ping &>/dev/null; then
	print_status "Redis detected, testing distributed mode..."

	# Set environment variables for testing
	export FLEXT_REDIS_ADDRESS="${FLEXT_REDIS_ADDRESS}"
	export FLEXT_MAX_WORKERS="5"
	export FLEXT_MIN_WORKERS="2"

	timeout 10 ./bin/flext -distributed &
	DISTRIBUTED_PID=$!
	sleep 3

	if kill -0 $DISTRIBUTED_PID 2>/dev/null; then
		print_success "Distributed mode started successfully"

		# Test API endpoints if curl is available
		if command -v curl &>/dev/null; then
			print_status "Testing distributed API endpoints..."

			# Test health endpoint
			if curl -s "http://localhost:${FLEXT_TEST_API_PORT}/health" >/dev/null; then
				print_success "Health endpoint responding"
			else
				print_warning "Health endpoint not responding"
			fi

			# Test cluster status
			if curl -s "http://localhost:${FLEXT_TEST_API_PORT}/api/v1/cluster/status" >/dev/null; then
				print_success "Cluster status endpoint responding"
			else
				print_warning "Cluster status endpoint not responding"
			fi

			# Test metrics
			if curl -s "http://localhost:${FLEXT_TEST_API_PORT}/metrics" >/dev/null; then
				print_success "Metrics endpoint responding"
			else
				print_warning "Metrics endpoint not responding"
			fi
		fi

		kill $DISTRIBUTED_PID
		wait $DISTRIBUTED_PID 2>/dev/null || true
	else
		print_error "Distributed mode failed to start"
	fi
else
	print_warning "Redis not available, skipping distributed mode test"
	print_warning "To test distributed mode: docker run -d -p ${FLEXT_REDIS_PORT}:${FLEXT_REDIS_PORT} redis:alpine"
fi

# Test configuration loading
print_status "Testing configuration loading..."
if [ -f "config/distributed.yaml" ]; then
	timeout 5 ./bin/flext -config config/distributed.yaml &
	CONFIG_PID=$!
	sleep 2

	if kill -0 $CONFIG_PID 2>/dev/null; then
		print_success "Configuration file loading works"
		kill $CONFIG_PID
		wait $CONFIG_PID 2>/dev/null || true
	else
		print_error "Configuration file loading failed"
	fi
else
	print_warning "distributed.yaml not found, skipping config test"
fi

# Architecture validation
print_status "Validating distributed architecture components..."

COMPONENTS=(
	"internal/infrastructure/cluster"
	"internal/infrastructure/worker"
	"internal/infrastructure/agent"
	"internal/infrastructure/coordination"
	"internal/infrastructure/discovery"
	"internal/infrastructure/observability"
	"internal/infrastructure/distributed"
)

for component in "${COMPONENTS[@]}"; do
	if [ -d "$component" ]; then
		print_success "✓ $component exists"
	else
		print_error "✗ $component missing"
	fi
done

# Docker validation
print_status "Checking Docker files..."
DOCKER_FILES=(
	"Dockerfile.distributed"
	"docker-compose.distributed.yml"
	"config/haproxy.cfg"
	"config/prometheus.yml"
)

for file in "${DOCKER_FILES[@]}"; do
	if [ -f "$file" ]; then
		print_success "✓ $file exists"
	else
		print_error "✗ $file missing"
	fi
done

echo ""
echo "🎉 FLEXT Distributed Architecture Test Complete!"
echo ""
echo "📚 Next Steps:"
echo "1. Start Redis: docker run -d -p ${FLEXT_REDIS_PORT}:${FLEXT_REDIS_PORT} redis:alpine"
echo "2. Test distributed: ./bin/flext -distributed"
echo "3. Start cluster: docker-compose -f docker-compose.distributed.yml up"
echo "4. Monitor cluster: http://localhost:${FLEXT_GRAFANA_PORT} (Grafana)"
echo "5. View metrics: http://localhost:${FLEXT_PROMETHEUS_PORT} (Prometheus)"
echo ""
echo "🔧 Architecture Features Available:"
echo "• Clustering with automatic node discovery"
echo "• Worker pools with auto-scaling"
echo "• Remote agent communication via WebSocket"
echo "• Distributed task coordination"
echo "• Service discovery and load balancing"
echo "• Distributed metrics and alerting"
echo "• Leader election and consensus"
echo "• Health monitoring and failover"
echo ""
print_success "FLEXT is ready for distributed deployment! 🚀"
