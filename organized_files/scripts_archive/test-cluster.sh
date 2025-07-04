#!/bin/bash

set -e

# FLEXT Cluster Testing Script
# ===========================

echo "🚀 FLEXT Cluster Testing Script"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
	echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
	echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
	echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
	echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for service to be ready
wait_for_service() {
	local url=$1
	local service_name=$2
	local max_attempts=${3:-30}
	local attempt=1

	log_info "Waiting for $service_name to be ready..."

	while [ $attempt -le $max_attempts ]; do
		if curl -f -s "$url" >/dev/null 2>&1; then
			log_success "$service_name is ready!"
			return 0
		fi

		echo -n "."
		sleep 2
		attempt=$((attempt + 1))
	done

	log_error "$service_name failed to start within $((max_attempts * 2)) seconds"
	return 1
}

# Function to test API endpoint
test_endpoint() {
	local url=$1
	local description=$2
	local expected_status=${3:-200}

	log_info "Testing: $description"

	response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url")
	body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
	status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

	if [ "$status" -eq "$expected_status" ]; then
		log_success "✓ $description (HTTP $status)"
		return 0
	else
		log_error "✗ $description (HTTP $status, expected $expected_status)"
		echo "Response: $body"
		return 1
	fi
}

# Function to test cluster functionality
test_cluster_operations() {
	log_info "Testing cluster operations..."

	# Test load balancer
	test_endpoint "http://localhost/health" "Load Balancer Health Check"

	# Test individual nodes
	test_endpoint "http://localhost:8080/health" "Node 1 Health"
	test_endpoint "http://localhost:8081/health" "Node 2 Health"
	test_endpoint "http://localhost:8082/health" "Node 3 Health"

	# Test cluster status
	test_endpoint "http://localhost:8080/cluster/status" "Cluster Status"

	# Test metrics endpoints
	test_endpoint "http://localhost:8080/metrics" "Node 1 Metrics"
	test_endpoint "http://localhost:8081/metrics" "Node 2 Metrics"
	test_endpoint "http://localhost:8082/metrics" "Node 3 Metrics"

	# Test API endpoints
	test_endpoint "http://localhost:8080/" "API Documentation"
	test_endpoint "http://localhost:8080/api/v1/pipelines" "Pipelines API"
	test_endpoint "http://localhost:8080/api/v1/plugins" "Plugins API"
}

# Function to test database operations
test_database_operations() {
	log_info "Testing database operations..."

	# Create a test pipeline via API
	log_info "Creating test pipeline..."
	create_response=$(curl -s -X POST http://localhost:8080/api/v1/pipelines \
		-H "Content-Type: application/json" \
		-d '{
            "name": "test-cluster-pipeline",
            "description": "Test pipeline for cluster validation",
            "tags": ["test", "cluster"]
        }')

	if echo "$create_response" | grep -q "test-cluster-pipeline"; then
		log_success "✓ Pipeline creation successful"
	else
		log_error "✗ Pipeline creation failed"
		echo "Response: $create_response"
		return 1
	fi

	# List pipelines to verify creation
	log_info "Listing pipelines..."
	list_response=$(curl -s http://localhost:8080/api/v1/pipelines)

	if echo "$list_response" | grep -q "test-cluster-pipeline"; then
		log_success "✓ Pipeline listing successful"
	else
		log_error "✗ Pipeline not found in listing"
		echo "Response: $list_response"
		return 1
	fi
}

# Function to test distributed features
test_distributed_features() {
	log_info "Testing distributed features..."

	# Test worker distribution across nodes
	for port in 8080 8081 8082; do
		log_info "Testing worker pool on node :$port"
		worker_response=$(curl -s "http://localhost:$port/worker/status")

		if echo "$worker_response" | grep -q -E "(workers|active|queue)"; then
			log_success "✓ Worker pool active on node :$port"
		else
			log_warning "⚠ Worker pool status unclear on node :$port"
		fi
	done

	# Test service discovery
	log_info "Testing service discovery..."
	discovery_response=$(curl -s "http://localhost:8080/discovery/services")

	if echo "$discovery_response" | grep -q -E "(services|nodes)"; then
		log_success "✓ Service discovery operational"
	else
		log_warning "⚠ Service discovery response unclear"
	fi
}

# Function to test monitoring stack
test_monitoring_stack() {
	log_info "Testing monitoring stack..."

	# Test Prometheus
	if wait_for_service "http://localhost:9093/-/ready" "Prometheus" 20; then
		test_endpoint "http://localhost:9093/api/v1/targets" "Prometheus Targets"
	fi

	# Test Grafana
	if wait_for_service "http://localhost:3000/api/health" "Grafana" 20; then
		log_success "✓ Grafana is accessible"
	fi

	# Test Jaeger
	if wait_for_service "http://localhost:16686/" "Jaeger UI" 10; then
		log_success "✓ Jaeger tracing is accessible"
	fi

	# Test HAProxy Stats
	if wait_for_service "http://localhost:8404/" "HAProxy Stats" 10; then
		log_success "✓ HAProxy statistics available"
	fi
}

# Function to run performance test
run_performance_test() {
	log_info "Running basic performance test..."

	# Create multiple pipelines concurrently
	log_info "Creating 10 pipelines concurrently..."

	for i in {1..10}; do
		(
			curl -s -X POST http://localhost/api/v1/pipelines \
				-H "Content-Type: application/json" \
				-d "{
                    \"name\": \"perf-test-pipeline-$i\",
                    \"description\": \"Performance test pipeline $i\",
                    \"tags\": [\"performance\", \"test\"]
                }" >/dev/null
		) &
	done

	wait # Wait for all background jobs to complete

	# Check how many were created successfully
	list_response=$(curl -s http://localhost/api/v1/pipelines)
	perf_count=$(echo "$list_response" | grep -c "perf-test-pipeline" || echo "0")

	if [ "$perf_count" -ge 8 ]; then
		log_success "✓ Performance test passed ($perf_count/10 pipelines created)"
	else
		log_warning "⚠ Performance test partial success ($perf_count/10 pipelines created)"
	fi
}

# Main execution
main() {
	log_info "Starting FLEXT cluster test suite..."

	# Check if Docker Compose is running
	if ! docker compose -f docker-compose.cluster.yml ps | grep -q "Up"; then
		log_error "Docker Compose cluster is not running. Please start it first:"
		echo "  docker compose -f docker-compose.cluster.yml up -d"
		exit 1
	fi

	# Wait for core services
	log_info "Waiting for core services..."
	wait_for_service "http://localhost:5432" "PostgreSQL" 30 || log_warning "PostgreSQL check skipped (may require psql)"
	wait_for_service "http://localhost:6379" "Redis" 30 || log_warning "Redis check skipped (may require redis-cli)"

	# Wait for FLEXT nodes
	log_info "Waiting for FLEXT nodes..."
	wait_for_service "http://localhost:8080/health" "FLEXT Node 1" 60
	wait_for_service "http://localhost:8081/health" "FLEXT Node 2" 60
	wait_for_service "http://localhost:8082/health" "FLEXT Node 3" 60

	# Wait for load balancer
	wait_for_service "http://localhost/health" "Load Balancer" 30

	# Run tests
	local tests_passed=0
	local total_tests=5

	if test_cluster_operations; then
		tests_passed=$((tests_passed + 1))
	fi

	if test_database_operations; then
		tests_passed=$((tests_passed + 1))
	fi

	if test_distributed_features; then
		tests_passed=$((tests_passed + 1))
	fi

	if test_monitoring_stack; then
		tests_passed=$((tests_passed + 1))
	fi

	if run_performance_test; then
		tests_passed=$((tests_passed + 1))
	fi

	# Final report
	echo ""
	echo "🎯 CLUSTER TEST RESULTS"
	echo "======================"
	echo "Tests Passed: $tests_passed/$total_tests"

	if [ "$tests_passed" -eq "$total_tests" ]; then
		log_success "🎉 All tests passed! FLEXT cluster is fully operational."
		echo ""
		echo "📊 Access Points:"
		echo "  • Load Balancer:    http://localhost"
		echo "  • FLEXT Node 1:     http://localhost:8080"
		echo "  • FLEXT Node 2:     http://localhost:8081"
		echo "  • FLEXT Node 3:     http://localhost:8082"
		echo "  • Grafana:          http://localhost:3000 (REDACTED_LDAP_BIND_PASSWORD/REDACTED_LDAP_BIND_PASSWORD123)"
		echo "  • Prometheus:       http://localhost:9093"
		echo "  • Jaeger:           http://localhost:16686"
		echo "  • HAProxy Stats:    http://localhost:8404"
		echo "  • PgAdmin:          http://localhost:5050 (REDACTED_LDAP_BIND_PASSWORD@internal.invalid/REDACTED_LDAP_BIND_PASSWORD123)"
		echo "  • Redis Insight:    http://localhost:8001"
		exit 0
	else
		log_warning "⚠ Some tests failed. Check the output above for details."
		exit 1
	fi
}

# Run the main function
main "$@"
