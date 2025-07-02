#!/bin/bash
set -e

echo "🔥 FLEXT-MELTANO STRESS TESTING & PERFORMANCE VALIDATION"
echo "======================================================="

# Configuration
SERVER_URL="http://localhost:8081"
CONCURRENT_CONNECTIONS=20
REQUESTS_PER_CONNECTION=50
TOTAL_REQUESTS=$((CONCURRENT_CONNECTIONS * REQUESTS_PER_CONNECTION))
TEST_DURATION_SECONDS=300 # 5 minutes
LOG_FILE="./stress-test.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Performance thresholds
MAX_RESPONSE_TIME_MS=5000 # 5 seconds max response time
MIN_SUCCESS_RATE=95       # 95% minimum success rate
MAX_MEMORY_MB=500         # 500MB max memory usage
MAX_CPU_PERCENT=80        # 80% max CPU usage

# Logging function
log() {
	echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
	echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
	echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
	echo -e "${YELLOW}⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

info() {
	echo -e "${PURPLE}📊 $1${NC}" | tee -a "$LOG_FILE"
}

# Check dependencies
check_dependencies() {
	log "Checking dependencies..."

	command -v curl >/dev/null 2>&1 || {
		error "curl is required but not installed"
		exit 1
	}
	command -v jq >/dev/null 2>&1 || {
		error "jq is required but not installed"
		exit 1
	}
	command -v bc >/dev/null 2>&1 || {
		error "bc is required but not installed"
		exit 1
	}

	# Check if ab (Apache Bench) is available
	if command -v ab >/dev/null 2>&1; then
		AB_AVAILABLE=true
		success "Apache Bench (ab) available for load testing"
	else
		AB_AVAILABLE=false
		warning "Apache Bench (ab) not available, using curl for load testing"
	fi

	success "All dependencies available"
}

# Test server health
test_server_health() {
	log "Testing server health before stress test..."
	local response=$(curl -s -w "%{http_code}" "$SERVER_URL/health" -o /dev/null)

	if [ "$response" = "200" ]; then
		success "Server is healthy"
		return 0
	else
		error "Server health check failed (HTTP $response)"
		return 1
	fi
}

# Get baseline performance metrics
get_baseline_metrics() {
	log "Getting baseline performance metrics..."

	# Test single request latency
	local start_time=$(date +%s.%N)
	curl -s "$SERVER_URL/api/v1/meltano/health" >/dev/null
	local end_time=$(date +%s.%N)
	local baseline_latency=$(echo "($end_time - $start_time) * 1000" | bc)

	# Get process pool stats
	local pool_stats=$(curl -s "$SERVER_URL/api/v1/meltano/stats" | jq -r '.process_pool')
	local max_concurrent=$(echo "$pool_stats" | jq -r '.max_concurrent')

	info "Baseline latency: ${baseline_latency}ms"
	info "Max concurrent processes: $max_concurrent"

	echo "$baseline_latency" >/tmp/baseline_latency
	echo "$max_concurrent" >/tmp/max_concurrent
}

# Load test with Apache Bench
load_test_with_ab() {
	log "Starting Apache Bench load test..."

	local results_file="/tmp/ab_results.txt"

	# Run Apache Bench
	ab -n $TOTAL_REQUESTS -c $CONCURRENT_CONNECTIONS -l \
		-r "$SERVER_URL/api/v1/meltano/health" >"$results_file" 2>&1

	# Parse results
	local requests_per_second=$(grep "Requests per second" "$results_file" | awk '{print $4}')
	local mean_time=$(grep "Time per request.*mean" "$results_file" | head -1 | awk '{print $4}')
	local failed_requests=$(grep "Failed requests" "$results_file" | awk '{print $3}')
	local success_rate=$(echo "scale=2; (($TOTAL_REQUESTS - $failed_requests) * 100) / $TOTAL_REQUESTS" | bc)

	info "Apache Bench Results:"
	info "  Requests per second: $requests_per_second"
	info "  Mean response time: ${mean_time}ms"
	info "  Failed requests: $failed_requests"
	info "  Success rate: ${success_rate}%"

	# Store results for validation
	echo "$requests_per_second" >/tmp/rps
	echo "$mean_time" >/tmp/mean_time
	echo "$success_rate" >/tmp/success_rate
}

# Load test with curl (fallback)
load_test_with_curl() {
	log "Starting curl-based load test..."

	local results_dir="/tmp/curl_results"
	mkdir -p "$results_dir"

	# Function to run concurrent requests
	run_concurrent_requests() {
		local connection_id=$1
		local success_count=0
		local total_time=0

		for ((i = 1; i <= REQUESTS_PER_CONNECTION; i++)); do
			local start_time=$(date +%s.%N)
			local response=$(curl -s -w "%{http_code}" "$SERVER_URL/api/v1/meltano/health" -o /dev/null 2>/dev/null)
			local end_time=$(date +%s.%N)
			local request_time=$(echo "($end_time - $start_time) * 1000" | bc)

			if [ "$response" = "200" ]; then
				((success_count++))
			fi

			total_time=$(echo "$total_time + $request_time" | bc)
		done

		echo "$success_count $total_time" >"$results_dir/connection_$connection_id"
	}

	# Start concurrent connections
	log "Launching $CONCURRENT_CONNECTIONS concurrent connections..."
	for ((c = 1; c <= CONCURRENT_CONNECTIONS; c++)); do
		run_concurrent_requests $c &
	done

	# Wait for all connections to complete
	wait

	# Aggregate results
	local total_successful=0
	local total_time=0

	for ((c = 1; c <= CONCURRENT_CONNECTIONS; c++)); do
		if [ -f "$results_dir/connection_$c" ]; then
			local result=$(cat "$results_dir/connection_$c")
			local success=$(echo "$result" | awk '{print $1}')
			local time=$(echo "$result" | awk '{print $2}')

			total_successful=$((total_successful + success))
			total_time=$(echo "$total_time + $time" | bc)
		fi
	done

	local success_rate=$(echo "scale=2; ($total_successful * 100) / $TOTAL_REQUESTS" | bc)
	local mean_time=$(echo "scale=2; $total_time / $TOTAL_REQUESTS" | bc)
	local rps=$(echo "scale=2; $TOTAL_REQUESTS / ($total_time / 1000)" | bc)

	info "Curl Load Test Results:"
	info "  Total requests: $TOTAL_REQUESTS"
	info "  Successful requests: $total_successful"
	info "  Success rate: ${success_rate}%"
	info "  Mean response time: ${mean_time}ms"
	info "  Requests per second: $rps"

	# Store results for validation
	echo "$rps" >/tmp/rps
	echo "$mean_time" >/tmp/mean_time
	echo "$success_rate" >/tmp/success_rate

	# Cleanup
	rm -rf "$results_dir"
}

# Test process pool behavior under load
test_process_pool_under_load() {
	log "Testing process pool behavior under load..."

	# Function to make concurrent Meltano operations
	make_meltano_request() {
		local operation=$1
		case $operation in
		"health")
			curl -s "$SERVER_URL/api/v1/meltano/health" >/dev/null
			;;
		"stats")
			curl -s "$SERVER_URL/api/v1/meltano/stats" >/dev/null
			;;
		"state")
			curl -s "$SERVER_URL/api/v1/meltano/state/stats" >/dev/null
			;;
		esac
	}

	# Launch multiple operations simultaneously
	local max_concurrent=$(cat /tmp/max_concurrent)
	local operations=("health" "stats" "state")

	log "Launching $((max_concurrent * 2)) concurrent operations to test pool limits..."

	for ((i = 1; i <= max_concurrent * 2; i++)); do
		local operation=${operations[$((i % 3))]}
		make_meltano_request "$operation" &
		sleep 0.1 # Small delay to stagger requests
	done

	# Monitor process pool during load
	for ((i = 1; i <= 10; i++)); do
		local stats=$(curl -s "$SERVER_URL/api/v1/meltano/stats" 2>/dev/null || echo '{}')
		local active=$(echo "$stats" | jq -r '.process_pool.active_processes // 0')
		local available=$(echo "$stats" | jq -r '.process_pool.available_slots // 0')

		info "Pool status [$i]: Active=$active, Available=$available"
		sleep 1
	done

	# Wait for all background jobs
	wait

	success "Process pool test completed"
}

# Memory and CPU monitoring
monitor_resource_usage() {
	log "Monitoring resource usage during stress test..."

	local monitoring_file="/tmp/resource_monitor.log"
	local server_pid=$(pgrep -f "flext-server" | head -1)

	if [ -z "$server_pid" ]; then
		warning "Could not find FLEXT server process for monitoring"
		return
	fi

	# Monitor for 60 seconds during peak load
	for ((i = 1; i <= 60; i++)); do
		# Get memory usage (RSS in KB)
		local memory_kb=$(ps -o rss= -p "$server_pid" 2>/dev/null || echo "0")
		local memory_mb=$(echo "scale=2; $memory_kb / 1024" | bc)

		# Get CPU usage
		local cpu_percent=$(ps -o %cpu= -p "$server_pid" 2>/dev/null || echo "0")

		echo "$(date '+%H:%M:%S') Memory: ${memory_mb}MB CPU: ${cpu_percent}%" >>"$monitoring_file"

		sleep 1
	done

	# Calculate averages and peaks
	local avg_memory=$(awk '{sum+=$3} END {print sum/NR}' "$monitoring_file" 2>/dev/null || echo "0")
	local peak_memory=$(awk '{if($3>max) max=$3} END {print max}' "$monitoring_file" 2>/dev/null || echo "0")
	local avg_cpu=$(awk '{sum+=$5} END {print sum/NR}' "$monitoring_file" 2>/dev/null || echo "0")
	local peak_cpu=$(awk '{if($5>max) max=$5} END {print max}' "$monitoring_file" 2>/dev/null || echo "0")

	info "Resource Usage Summary:"
	info "  Average Memory: ${avg_memory}MB"
	info "  Peak Memory: ${peak_memory}MB"
	info "  Average CPU: ${avg_cpu}%"
	info "  Peak CPU: ${peak_cpu}%"

	# Store for validation
	echo "$peak_memory" >/tmp/peak_memory
	echo "$peak_cpu" >/tmp/peak_cpu
}

# Test error handling under stress
test_error_handling() {
	log "Testing error handling under stress..."

	# Make invalid requests to test error handling
	local error_endpoints=(
		"/api/v1/meltano/invalid_endpoint"
		"/api/v1/meltano/projects/nonexistent/plugins"
		"/api/v1/meltano/projects/test/executions/invalid_id"
	)

	for endpoint in "${error_endpoints[@]}"; do
		local response=$(curl -s -w "%{http_code}" "$SERVER_URL$endpoint" -o /dev/null)
		info "Error endpoint $endpoint returned HTTP $response"
	done

	# Test with malformed JSON
	local response=$(curl -s -w "%{http_code}" \
		-X POST \
		-H "Content-Type: application/json" \
		-d '{"invalid": json}' \
		"$SERVER_URL/api/v1/meltano/projects" \
		-o /dev/null)

	info "Malformed JSON request returned HTTP $response"

	success "Error handling test completed"
}

# Validate performance against thresholds
validate_performance() {
	log "Validating performance against thresholds..."

	local failed_validations=0

	# Validate response time
	if [ -f "/tmp/mean_time" ]; then
		local mean_time=$(cat /tmp/mean_time)
		local mean_time_int=$(echo "$mean_time" | cut -d'.' -f1)

		if [ "$mean_time_int" -le "$MAX_RESPONSE_TIME_MS" ]; then
			success "Response time validation passed: ${mean_time}ms <= ${MAX_RESPONSE_TIME_MS}ms"
		else
			error "Response time validation failed: ${mean_time}ms > ${MAX_RESPONSE_TIME_MS}ms"
			((failed_validations++))
		fi
	fi

	# Validate success rate
	if [ -f "/tmp/success_rate" ]; then
		local success_rate=$(cat /tmp/success_rate)
		local success_rate_int=$(echo "$success_rate" | cut -d'.' -f1)

		if [ "$success_rate_int" -ge "$MIN_SUCCESS_RATE" ]; then
			success "Success rate validation passed: ${success_rate}% >= ${MIN_SUCCESS_RATE}%"
		else
			error "Success rate validation failed: ${success_rate}% < ${MIN_SUCCESS_RATE}%"
			((failed_validations++))
		fi
	fi

	# Validate memory usage
	if [ -f "/tmp/peak_memory" ]; then
		local peak_memory=$(cat /tmp/peak_memory)
		local peak_memory_int=$(echo "$peak_memory" | cut -d'.' -f1)

		if [ "$peak_memory_int" -le "$MAX_MEMORY_MB" ]; then
			success "Memory usage validation passed: ${peak_memory}MB <= ${MAX_MEMORY_MB}MB"
		else
			error "Memory usage validation failed: ${peak_memory}MB > ${MAX_MEMORY_MB}MB"
			((failed_validations++))
		fi
	fi

	# Validate CPU usage
	if [ -f "/tmp/peak_cpu" ]; then
		local peak_cpu=$(cat /tmp/peak_cpu)
		local peak_cpu_int=$(echo "$peak_cpu" | cut -d'.' -f1)

		if [ "$peak_cpu_int" -le "$MAX_CPU_PERCENT" ]; then
			success "CPU usage validation passed: ${peak_cpu}% <= ${MAX_CPU_PERCENT}%"
		else
			error "CPU usage validation failed: ${peak_cpu}% > ${MAX_CPU_PERCENT}%"
			((failed_validations++))
		fi
	fi

	return $failed_validations
}

# Cleanup function
cleanup() {
	log "Cleaning up stress test artifacts..."
	rm -f /tmp/baseline_latency /tmp/max_concurrent /tmp/rps /tmp/mean_time /tmp/success_rate
	rm -f /tmp/peak_memory /tmp/peak_cpu /tmp/ab_results.txt /tmp/resource_monitor.log
	success "Cleanup completed"
}

# Main stress test execution
main() {
	echo "Starting stress testing at $(date)"
	echo >"$LOG_FILE" # Clear log file

	# Check dependencies
	check_dependencies

	# Test server health
	if ! test_server_health; then
		error "Server is not running. Please start the FLEXT server first."
		exit 1
	fi

	# Get baseline metrics
	get_baseline_metrics

	info "STRESS TEST CONFIGURATION:"
	info "  Server URL: $SERVER_URL"
	info "  Concurrent connections: $CONCURRENT_CONNECTIONS"
	info "  Requests per connection: $REQUESTS_PER_CONNECTION"
	info "  Total requests: $TOTAL_REQUESTS"
	info "  Performance thresholds:"
	info "    Max response time: ${MAX_RESPONSE_TIME_MS}ms"
	info "    Min success rate: ${MIN_SUCCESS_RATE}%"
	info "    Max memory usage: ${MAX_MEMORY_MB}MB"
	info "    Max CPU usage: ${MAX_CPU_PERCENT}%"
	echo

	# Start resource monitoring in background
	monitor_resource_usage &
	local monitor_pid=$!

	# Run load test
	if [ "$AB_AVAILABLE" = true ]; then
		load_test_with_ab
	else
		load_test_with_curl
	fi

	# Test process pool behavior
	test_process_pool_under_load

	# Test error handling
	test_error_handling

	# Wait for resource monitoring to complete
	wait $monitor_pid 2>/dev/null || true

	echo
	log "STRESS TESTING COMPLETED"
	echo "========================"

	# Validate performance
	if validate_performance; then
		success "🎉 ALL PERFORMANCE VALIDATIONS PASSED!"
		echo
		info "STRESS TEST SUMMARY:"
		if [ -f "/tmp/rps" ]; then
			info "  Requests per second: $(cat /tmp/rps)"
		fi
		if [ -f "/tmp/mean_time" ]; then
			info "  Mean response time: $(cat /tmp/mean_time)ms"
		fi
		if [ -f "/tmp/success_rate" ]; then
			info "  Success rate: $(cat /tmp/success_rate)%"
		fi
		if [ -f "/tmp/peak_memory" ]; then
			info "  Peak memory usage: $(cat /tmp/peak_memory)MB"
		fi
		if [ -f "/tmp/peak_cpu" ]; then
			info "  Peak CPU usage: $(cat /tmp/peak_cpu)%"
		fi

		success "FLEXT-Meltano integration is ready for production workloads!"
		exit 0
	else
		local failed_count=$?
		error "Performance validation failed ($failed_count failures)"
		warning "Review the performance thresholds and optimize the system"
		exit 1
	fi
}

# Trap for cleanup on script exit
trap cleanup EXIT

# Run main function
main "$@"
