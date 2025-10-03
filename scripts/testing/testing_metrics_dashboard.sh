#!/bin/bash
# testing_metrics_dashboard.sh - Generate ecosystem-wide testing metrics dashboard
#
# Usage: ./scripts/testing_metrics_dashboard.sh [options]
# Options:
#   --output FORMAT     Output format: console, html, json, csv (default: console)
#   --save PATH         Save report to file (optional)
#   --projects LIST     Comma-separated list of specific projects to analyze
#   --detailed          Include detailed per-test metrics
#   --trends            Show coverage trends (requires historical data)
#   --benchmarks        Include performance benchmark results
#   --quiet             Minimal output, errors only
#
# Examples:
#   ./scripts/testing_metrics_dashboard.sh
#   ./scripts/testing_metrics_dashboard.sh --output html --save report.html
#   ./scripts/testing_metrics_dashboard.sh --projects "flext-core,flext-api" --detailed
#   ./scripts/testing_metrics_dashboard.sh --output json --benchmarks

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
REPORT_TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
DEFAULT_OUTPUT="console"

# Project categorization
CORE_PROJECTS=("flext-core" "flext-api" "flext-cli" "flext-auth")
INFRASTRUCTURE_PROJECTS=("flext-db-oracle" "flext-ldap" "flext-grpc" "flext-observability")
SINGER_PROJECTS=("flext-tap-oracle" "flext-tap-ldap" "flext-target-oracle" "flext-target-ldap")
DBT_PROJECTS=("flext-dbt-oracle" "flext-dbt-ldap" "flext-dbt-ldif")
ENTERPRISE_PROJECTS=("client-b-meltano-native" "client-a-oud-mig")

# Colors for console output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Flags
OUTPUT_FORMAT="$DEFAULT_OUTPUT"
SAVE_PATH=""
SPECIFIC_PROJECTS=""
DETAILED=false
TRENDS=false
BENCHMARKS=false
QUIET=false

# Function to log messages
log_info() {
	if [ "$QUIET" = false ]; then
		echo -e "${BLUE}📊 $1${NC}"
	fi
}

log_success() {
	if [ "$QUIET" = false ]; then
		echo -e "${GREEN}✅ $1${NC}"
	fi
}

log_warning() {
	if [ "$QUIET" = false ]; then
		echo -e "${YELLOW}⚠️  $1${NC}"
	fi
}

log_error() {
	echo -e "${RED}❌ $1${NC}" >&2
}

log_section() {
	if [ "$QUIET" = false ]; then
		echo -e "${WHITE}$1${NC}"
		echo -e "${WHITE}$(echo "$1" | sed 's/./=/g')${NC}"
	fi
}

# Function to show usage
usage() {
	echo "FLEXT Testing Metrics Dashboard"
	echo ""
	echo "Usage: $0 [options]"
	echo ""
	echo "Options:"
	echo "  --output FORMAT     Output format: console, html, json, csv (default: console)"
	echo "  --save PATH         Save report to file (optional)"
	echo "  --projects LIST     Comma-separated list of specific projects to analyze"
	echo "  --detailed          Include detailed per-test metrics"
	echo "  --trends            Show coverage trends (requires historical data)"
	echo "  --benchmarks        Include performance benchmark results"
	echo "  --quiet             Minimal output, errors only"
	echo "  --help              Show this help message"
	echo ""
	echo "Examples:"
	echo "  $0                                    # Generate console dashboard"
	echo "  $0 --output html --save report.html  # Generate HTML report"
	echo "  $0 --projects \"flext-core,flext-api\" # Analyze specific projects"
	echo "  $0 --detailed --benchmarks           # Detailed report with benchmarks"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
	case $1 in
	--output)
		OUTPUT_FORMAT="$2"
		shift 2
		;;
	--save)
		SAVE_PATH="$2"
		shift 2
		;;
	--projects)
		SPECIFIC_PROJECTS="$2"
		shift 2
		;;
	--detailed)
		DETAILED=true
		shift
		;;
	--trends)
		TRENDS=true
		shift
		;;
	--benchmarks)
		BENCHMARKS=true
		shift
		;;
	--quiet)
		QUIET=true
		shift
		;;
	--help)
		usage
		exit 0
		;;
	*)
		echo "Unknown option: $1"
		usage
		exit 1
		;;
	esac
done

# Validate output format
case $OUTPUT_FORMAT in
console | html | json | csv) ;;
*)
	log_error "Invalid output format: $OUTPUT_FORMAT. Use console, html, json, or csv."
	exit 1
	;;
esac

# Data structures for metrics
declare -A project_coverage
declare -A project_test_count
declare -A project_status
declare -A project_execution_time
declare -A project_failed_tests
declare -A project_categories

# Function to get project coverage
get_project_coverage() {
	local project=$1
	local project_path="$WORKSPACE_ROOT/$project"

	if [ ! -d "$project_path" ]; then
		echo "N/A"
		return
	fi

	cd "$project_path"

	# Try to get coverage from pytest
	if command -v poetry &>/dev/null && [ -f "pyproject.toml" ]; then
		coverage_output=$(poetry run pytest --cov=src --tb=no -q 2>/dev/null | grep "TOTAL" | awk '{print $4}' | sed 's/%//' || echo "")
		if [ -n "$coverage_output" ] && [ "$coverage_output" != "0" ]; then
			echo "$coverage_output"
		else
			echo "N/A"
		fi
	else
		echo "N/A"
	fi

	cd - >/dev/null
}

# Function to get test count and status
get_project_test_metrics() {
	local project=$1
	local project_path="$WORKSPACE_ROOT/$project"

	if [ ! -d "$project_path" ]; then
		echo "0,N/A,0,N/A"
		return
	fi

	cd "$project_path"

	if command -v poetry &>/dev/null && [ -f "pyproject.toml" ]; then
		# Run tests and capture output
		test_output=$(poetry run pytest --tb=no -q 2>/dev/null || echo "FAILED")

		if [ "$test_output" = "FAILED" ]; then
			echo "0,FAILED,0,N/A"
		else
			# Parse test results
			test_count=$(echo "$test_output" | grep -oE '[0-9]+ passed' | awk '{print $1}' || echo "0")
			failed_count=$(echo "$test_output" | grep -oE '[0-9]+ failed' | awk '{print $1}' || echo "0")

			# Determine status
			if [ "$failed_count" -gt 0 ]; then
				status="FAILED"
			elif [ "$test_count" -gt 0 ]; then
				status="PASSED"
			else
				status="NO_TESTS"
			fi

			# Get execution time if available
			exec_time=$(echo "$test_output" | grep -oE '[0-9]+\.[0-9]+s' | head -1 | sed 's/s//' || echo "N/A")

			echo "$test_count,$status,$failed_count,$exec_time"
		fi
	else
		echo "0,NO_POETRY,0,N/A"
	fi

	cd - >/dev/null
}

# Function to categorize project
categorize_project() {
	local project=$1

	if [[ " ${CORE_PROJECTS[@]} " =~ " ${project} " ]]; then
		echo "Core"
	elif [[ " ${INFRASTRUCTURE_PROJECTS[@]} " =~ " ${project} " ]]; then
		echo "Infrastructure"
	elif [[ " ${SINGER_PROJECTS[@]} " =~ " ${project} " ]]; then
		echo "Singer"
	elif [[ " ${DBT_PROJECTS[@]} " =~ " ${project} " ]]; then
		echo "DBT"
	elif [[ " ${ENTERPRISE_PROJECTS[@]} " =~ " ${project} " ]]; then
		echo "Enterprise"
	else
		echo "Other"
	fi
}

# Function to collect all metrics
collect_metrics() {
	log_info "Collecting testing metrics across FLEXT ecosystem..."

	cd "$WORKSPACE_ROOT"

	# Determine projects to analyze
	local projects_to_analyze=()

	if [ -n "$SPECIFIC_PROJECTS" ]; then
		IFS=',' read -ra projects_to_analyze <<<"$SPECIFIC_PROJECTS"
	else
		# Find all flext-* projects
		while IFS= read -r -d '' project; do
			project=$(basename "$project")
			projects_to_analyze+=("$project")
		done < <(find . -maxdepth 1 -name "flext-*" -type d -print0)

		# Add other known projects
		for other_project in "client-a-oud-mig" "client-b-meltano-native"; do
			if [ -d "$other_project" ]; then
				projects_to_analyze+=("$other_project")
			fi
		done
	fi

	log_info "Analyzing ${#projects_to_analyze[@]} projects..."

	# Collect metrics for each project
	for project in "${projects_to_analyze[@]}"; do
		if [ "$QUIET" = false ]; then
			echo -n "  📋 $project..."
		fi

		# Get coverage
		coverage=$(get_project_coverage "$project")
		project_coverage["$project"]="$coverage"

		# Get test metrics
		test_metrics=$(get_project_test_metrics "$project")
		IFS=',' read -r test_count status failed_count exec_time <<<"$test_metrics"

		project_test_count["$project"]="$test_count"
		project_status["$project"]="$status"
		project_execution_time["$project"]="$exec_time"
		project_failed_tests["$project"]="$failed_count"

		# Categorize project
		category=$(categorize_project "$project")
		project_categories["$project"]="$category"

		if [ "$QUIET" = false ]; then
			echo " Done"
		fi
	done

	log_success "Metrics collection completed"
}

# Function to generate console output
generate_console_output() {
	log_section "🧪 FLEXT ECOSYSTEM TESTING METRICS DASHBOARD"
	echo "Generated: $(date)"
	echo "Workspace: $WORKSPACE_ROOT"
	echo ""

	# Overall summary
	local total_projects=0
	local projects_with_tests=0
	local total_tests=0
	local total_failed=0
	local total_coverage=0
	local coverage_count=0

	for project in "${!project_coverage[@]}"; do
		((total_projects++))

		if [ "${project_test_count[$project]}" != "0" ]; then
			((projects_with_tests++))
			((total_tests += ${project_test_count[$project]}))
			((total_failed += ${project_failed_tests[$project]}))
		fi

		if [ "${project_coverage[$project]}" != "N/A" ]; then
			((total_coverage += ${project_coverage[$project]}))
			((coverage_count++))
		fi
	done

	local avg_coverage=0
	if [ $coverage_count -gt 0 ]; then
		avg_coverage=$((total_coverage / coverage_count))
	fi

	log_section "📊 ECOSYSTEM SUMMARY"
	printf "%-25s %s\n" "Total Projects:" "$total_projects"
	printf "%-25s %s\n" "Projects with Tests:" "$projects_with_tests"
	printf "%-25s %s\n" "Total Tests:" "$total_tests"
	printf "%-25s %s\n" "Failed Tests:" "$total_failed"
	printf "%-25s %s%%\n" "Average Coverage:" "$avg_coverage"
	echo ""

	# Project details
	log_section "🔍 PROJECT DETAILS"
	printf "%-25s %-12s %-8s %-8s %-10s %-8s %-12s\n" "Project" "Category" "Coverage" "Tests" "Failed" "Status" "Exec Time"
	printf "%-25s %-12s %-8s %-8s %-10s %-8s %-12s\n" "$(printf '%.0s-' {1..25})" "$(printf '%.0s-' {1..12})" "$(printf '%.0s-' {1..8})" "$(printf '%.0s-' {1..8})" "$(printf '%.0s-' {1..10})" "$(printf '%.0s-' {1..8})" "$(printf '%.0s-' {1..12})"

	for project in $(printf '%s\n' "${!project_coverage[@]}" | sort); do
		local coverage="${project_coverage[$project]}"
		local category="${project_categories[$project]}"
		local test_count="${project_test_count[$project]}"
		local failed_count="${project_failed_tests[$project]}"
		local status="${project_status[$project]}"
		local exec_time="${project_execution_time[$project]}"

		# Color coding for status
		local status_color=""
		case $status in
		"PASSED") status_color="${GREEN}" ;;
		"FAILED") status_color="${RED}" ;;
		"NO_TESTS") status_color="${YELLOW}" ;;
		*) status_color="${NC}" ;;
		esac

		printf "%-25s %-12s %-8s %-8s %-10s ${status_color}%-8s${NC} %-12s\n" \
			"$project" "$category" "${coverage}%" "$test_count" "$failed_count" "$status" "${exec_time}s"
	done
	echo ""

	# Category summary
	log_section "🏷️  CATEGORY BREAKDOWN"
	declare -A category_counts
	declare -A category_coverage
	declare -A category_coverage_count

	for project in "${!project_categories[@]}"; do
		local category="${project_categories[$project]}"
		((category_counts["$category"]++))

		if [ "${project_coverage[$project]}" != "N/A" ]; then
			local coverage="${project_coverage[$project]}"
			category_coverage["$category"]=$((${category_coverage["$category"]:-0} + coverage))
			((category_coverage_count["$category"]++))
		fi
	done

	printf "%-15s %-8s %-12s\n" "Category" "Projects" "Avg Coverage"
	printf "%-15s %-8s %-12s\n" "$(printf '%.0s-' {1..15})" "$(printf '%.0s-' {1..8})" "$(printf '%.0s-' {1..12})"

	for category in "Core" "Infrastructure" "Singer" "DBT" "Enterprise" "Other"; do
		if [ "${category_counts[$category]:-0}" -gt 0 ]; then
			local count="${category_counts[$category]}"
			local avg_cov="N/A"

			if [ "${category_coverage_count[$category]:-0}" -gt 0 ]; then
				avg_cov="$((${category_coverage[$category]} / ${category_coverage_count[$category]}))%"
			fi

			printf "%-15s %-8s %-12s\n" "$category" "$count" "$avg_cov"
		fi
	done
	echo ""

	# Quality assessment
	log_section "🎯 QUALITY ASSESSMENT"
	local excellent=0
	local good=0
	local needs_improvement=0
	local critical=0

	for project in "${!project_coverage[@]}"; do
		local coverage="${project_coverage[$project]}"
		local status="${project_status[$project]}"

		if [ "$coverage" != "N/A" ] && [ "$status" = "PASSED" ]; then
			if [ "$coverage" -ge 85 ]; then
				((excellent++))
			elif [ "$coverage" -ge 75 ]; then
				((good++))
			elif [ "$coverage" -ge 50 ]; then
				((needs_improvement++))
			else
				((critical++))
			fi
		else
			((critical++))
		fi
	done

	echo -e "${GREEN}🟢 Excellent (85%+):${NC} $excellent projects"
	echo -e "${BLUE}🔵 Good (75-84%):${NC} $good projects"
	echo -e "${YELLOW}🟡 Needs Improvement (50-74%):${NC} $needs_improvement projects"
	echo -e "${RED}🔴 Critical (<50% or failing):${NC} $critical projects"
	echo ""

	# Recommendations
	log_section "💡 RECOMMENDATIONS"

	if [ $critical -gt 0 ]; then
		echo "🔴 CRITICAL: $critical projects need immediate attention"
		echo "   - Fix failing tests"
		echo "   - Increase test coverage above 50%"
		echo ""
	fi

	if [ $needs_improvement -gt 0 ]; then
		echo "🟡 IMPROVEMENT: $needs_improvement projects should increase coverage to 75%+"
		echo ""
	fi

	local foundation_coverage="${project_coverage["flext-core"]:-N/A}"
	if [ "$foundation_coverage" != "N/A" ] && [ "$foundation_coverage" -lt 85 ]; then
		echo "⚠️  Foundation Library (flext-core): $foundation_coverage% coverage"
		echo "   - Target: 85% for v1.0.0 release"
		echo "   - Current: Proven $foundation_coverage% baseline"
		echo ""
	fi

	echo "📋 Use FLEXT_TESTING_STANDARDS.md for guidance on improving test quality"
	echo "🔧 Run ./scripts/testing_quality_gates.sh to validate standards compliance"
	echo ""
}

# Function to generate HTML output
generate_html_output() {
	cat <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLEXT Testing Metrics Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #2c3e50; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #3498db; }
        .metric-label { color: #7f8c8d; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #34495e; color: white; }
        .status-passed { color: #27ae60; font-weight: bold; }
        .status-failed { color: #e74c3c; font-weight: bold; }
        .status-no-tests { color: #f39c12; font-weight: bold; }
        .coverage-excellent { background-color: #d5e8d4; }
        .coverage-good { background-color: #fff2cc; }
        .coverage-poor { background-color: #f8cecc; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 FLEXT Testing Metrics Dashboard</h1>
        <p class="timestamp">Generated: DATE_PLACEHOLDER</p>

        <div class="summary">
            <div class="metric-card">
                <div class="metric-value">TOTAL_PROJECTS_PLACEHOLDER</div>
                <div class="metric-label">Total Projects</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">TOTAL_TESTS_PLACEHOLDER</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">AVG_COVERAGE_PLACEHOLDER%</div>
                <div class="metric-label">Average Coverage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">FAILED_TESTS_PLACEHOLDER</div>
                <div class="metric-label">Failed Tests</div>
            </div>
        </div>

        <h2>📊 Project Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Project</th>
                    <th>Category</th>
                    <th>Coverage</th>
                    <th>Tests</th>
                    <th>Failed</th>
                    <th>Status</th>
                    <th>Execution Time</th>
                </tr>
            </thead>
            <tbody>
                TABLE_ROWS_PLACEHOLDER
            </tbody>
        </table>

        <h2>🏷️ Category Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Projects</th>
                    <th>Average Coverage</th>
                </tr>
            </thead>
            <tbody>
                CATEGORY_ROWS_PLACEHOLDER
            </tbody>
        </table>

        <h2>💡 Recommendations</h2>
        <div id="recommendations">
            RECOMMENDATIONS_PLACEHOLDER
        </div>
    </div>
</body>
</html>
EOF
}

# Function to generate JSON output
generate_json_output() {
	echo "{"
	echo "  \"timestamp\": \"$(date -Iseconds)\","
	echo "  \"workspace\": \"$WORKSPACE_ROOT\","
	echo '  "projects": {'

	local first=true
	for project in $(printf '%s\n' "${!project_coverage[@]}" | sort); do
		if [ "$first" = false ]; then
			echo ","
		fi
		first=false

		echo "    \"$project\": {"
		echo "      \"category\": \"${project_categories[$project]}\","
		echo "      \"coverage\": \"${project_coverage[$project]}\","
		echo "      \"test_count\": ${project_test_count[$project]},"
		echo "      \"failed_tests\": ${project_failed_tests[$project]},"
		echo "      \"status\": \"${project_status[$project]}\","
		echo "      \"execution_time\": \"${project_execution_time[$project]}\""
		echo -n "    }"
	done

	echo ""
	echo "  }"
	echo "}"
}

# Function to generate CSV output
generate_csv_output() {
	echo "Project,Category,Coverage,Tests,Failed,Status,ExecutionTime"
	for project in $(printf '%s\n' "${!project_coverage[@]}" | sort); do
		echo "$project,${project_categories[$project]},${project_coverage[$project]},${project_test_count[$project]},${project_failed_tests[$project]},${project_status[$project]},${project_execution_time[$project]}"
	done
}

# Function to save output to file
save_output() {
	local content="$1"
	local file_path="$2"

	echo "$content" >"$file_path"
	log_success "Report saved to: $file_path"
}

# Main execution
main() {
	cd "$WORKSPACE_ROOT"

	# Collect metrics
	collect_metrics

	# Generate output based on format
	local output_content=""
	case $OUTPUT_FORMAT in
	console)
		generate_console_output
		;;
	html)
		output_content=$(generate_html_output)
		# Replace placeholders with actual data
		# This would require more complex data processing for full HTML generation
		echo "$output_content"
		;;
	json)
		output_content=$(generate_json_output)
		echo "$output_content"
		;;
	csv)
		output_content=$(generate_csv_output)
		echo "$output_content"
		;;
	esac

	# Save to file if requested
	if [ -n "$SAVE_PATH" ] && [ -n "$output_content" ]; then
		save_output "$output_content" "$SAVE_PATH"
	fi

	log_success "Testing metrics dashboard generation completed"
}

# Execute main function
main "$@"
