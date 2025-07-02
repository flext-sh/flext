#!/bin/bash

set -e

# FLEXT Cluster Deployment Script
# ===============================

echo "🚀 FLEXT Cluster Deployment"
echo "============================"

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

# Function to check prerequisites
check_prerequisites() {
	log_info "Checking prerequisites..."

	# Check Docker
	if ! command -v docker &>/dev/null; then
		log_error "Docker is not installed. Please install Docker first."
		exit 1
	fi

	# Check Docker Compose
	if ! command -v docker &>/dev/null || ! docker compose version &>/dev/null; then
		log_error "Docker Compose is not available. Please ensure Docker Compose is installed."
		exit 1
	fi

	# Check if port 80 is available
	if lsof -i :80 &>/dev/null; then
		log_warning "Port 80 is already in use. The load balancer may not start correctly."
	fi

	log_success "Prerequisites check passed"
}

# Function to build FLEXT image
build_flext_image() {
	log_info "Building FLEXT Docker image..."

	# Ensure we have the binary built
	if [ ! -f "bin/flext" ]; then
		log_info "Building FLEXT binary first..."
		go build -o bin/flext ./cmd/flext
	fi

	# Build Docker image
	docker build -f docker/Dockerfile.demo -t flext:latest .

	if [ $? -eq 0 ]; then
		log_success "FLEXT Docker image built successfully"
	else
		log_error "Failed to build FLEXT Docker image"
		exit 1
	fi
}

# Function to start the cluster
start_cluster() {
	log_info "Starting FLEXT cluster..."

	# Stop any existing cluster
	docker compose -f docker-compose.cluster.yml down 2>/dev/null || true

	# Start the cluster
	docker compose -f docker-compose.cluster.yml up -d

	if [ $? -eq 0 ]; then
		log_success "FLEXT cluster started successfully"
	else
		log_error "Failed to start FLEXT cluster"
		exit 1
	fi
}

# Function to wait for services
wait_for_services() {
	log_info "Waiting for services to be ready..."

	# Wait for PostgreSQL
	log_info "Waiting for PostgreSQL..."
	timeout=60
	while [ $timeout -gt 0 ]; do
		if docker compose -f docker-compose.cluster.yml exec -T postgres pg_isready -U flext -d flext_db 2>/dev/null; then
			log_success "PostgreSQL is ready"
			break
		fi
		sleep 2
		timeout=$((timeout - 2))
	done

	# Wait for Redis
	log_info "Waiting for Redis..."
	timeout=30
	while [ $timeout -gt 0 ]; do
		if docker compose -f docker-compose.cluster.yml exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
			log_success "Redis is ready"
			break
		fi
		sleep 2
		timeout=$((timeout - 2))
	done

	# Wait for FLEXT nodes
	log_info "Waiting for FLEXT nodes..."
	for port in 8080 8081 8082; do
		timeout=90
		while [ $timeout -gt 0 ]; do
			if curl -f -s "http://localhost:$port/health" >/dev/null 2>&1; then
				log_success "FLEXT node on port $port is ready"
				break
			fi
			sleep 3
			timeout=$((timeout - 3))
		done

		if [ $timeout -le 0 ]; then
			log_warning "FLEXT node on port $port may not be ready yet"
		fi
	done

	# Wait for load balancer
	log_info "Waiting for load balancer..."
	timeout=30
	while [ $timeout -gt 0 ]; do
		if curl -f -s "http://localhost/health" >/dev/null 2>&1; then
			log_success "Load balancer is ready"
			break
		fi
		sleep 2
		timeout=$((timeout - 2))
	done
}

# Function to show cluster status
show_cluster_status() {
	echo ""
	echo "🎯 FLEXT CLUSTER STATUS"
	echo "======================="

	# Show running containers
	echo ""
	echo "📦 Running Containers:"
	docker compose -f docker-compose.cluster.yml ps

	echo ""
	echo "🌐 Access Points:"
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

	echo ""
	echo "🔧 Management Commands:"
	echo "  • View logs:        docker compose -f docker-compose.cluster.yml logs -f"
	echo "  • Stop cluster:     docker compose -f docker-compose.cluster.yml down"
	echo "  • Test cluster:     ./test-cluster.sh"
	echo "  • Scale nodes:      docker compose -f docker-compose.cluster.yml up -d --scale flext-node-2=2"
}

# Function to run quick health check
quick_health_check() {
	log_info "Running quick health check..."

	# Test load balancer
	if curl -f -s "http://localhost/health" >/dev/null; then
		log_success "✓ Load balancer is responding"
	else
		log_warning "⚠ Load balancer is not responding"
	fi

	# Test cluster status
	cluster_response=$(curl -s "http://localhost:8080/cluster/status" 2>/dev/null || echo "")
	if echo "$cluster_response" | grep -q -E "(nodes|cluster)"; then
		log_success "✓ Cluster coordination is active"
	else
		log_warning "⚠ Cluster coordination may not be fully ready"
	fi

	# Test database connectivity (via API)
	pipelines_response=$(curl -s "http://localhost/api/v1/pipelines" 2>/dev/null || echo "")
	if echo "$pipelines_response" | grep -q -E "(\[\]|\[.*\])"; then
		log_success "✓ Database connectivity working"
	else
		log_warning "⚠ Database connectivity may have issues"
	fi
}

# Main execution
main() {
	local command=${1:-"start"}

	case $command in
	"start")
		check_prerequisites
		build_flext_image
		start_cluster
		wait_for_services
		quick_health_check
		show_cluster_status

		echo ""
		log_success "🎉 FLEXT cluster is running!"
		echo ""
		log_info "Run './test-cluster.sh' to perform comprehensive testing"
		;;

	"stop")
		log_info "Stopping FLEXT cluster..."
		docker compose -f docker-compose.cluster.yml down
		log_success "FLEXT cluster stopped"
		;;

	"restart")
		log_info "Restarting FLEXT cluster..."
		docker compose -f docker-compose.cluster.yml down
		sleep 2
		$0 start
		;;

	"status")
		show_cluster_status
		quick_health_check
		;;

	"logs")
		docker compose -f docker-compose.cluster.yml logs -f
		;;

	"build")
		build_flext_image
		;;

	*)
		echo "Usage: $0 {start|stop|restart|status|logs|build}"
		echo ""
		echo "Commands:"
		echo "  start    - Start the FLEXT cluster (default)"
		echo "  stop     - Stop the FLEXT cluster"
		echo "  restart  - Restart the FLEXT cluster"
		echo "  status   - Show cluster status"
		echo "  logs     - Show cluster logs"
		echo "  build    - Build FLEXT Docker image"
		exit 1
		;;
	esac
}

# Run the main function
main "$@"
