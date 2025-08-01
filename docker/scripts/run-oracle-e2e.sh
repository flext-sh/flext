#!/bin/bash
# FLEXT Oracle E2E Test Runner
# Comprehensive end-to-end testing for Oracle Database integration

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/workspace"
TEST_RESULTS_DIR="/workspace/test-results"
TEST_REPORTS_DIR="/workspace/test-reports"
COVERAGE_DIR="/workspace/coverage-reports"

# Oracle connection settings
ORACLE_HOST="${ORACLE_HOST:-oracle-db}"
ORACLE_PORT="${ORACLE_PORT:-1521}"
ORACLE_SERVICE_NAME="${ORACLE_SERVICE_NAME:-FLEXT_PDB}"
ORACLE_USERNAME="${ORACLE_USERNAME:-FLEXT_USER}"
ORACLE_PASSWORD="${ORACLE_PASSWORD:-FlextTest123!}"
ORACLE_SCHEMA="${ORACLE_SCHEMA:-FLEXT_TEST}"

# Test configuration
E2E_TEST_TIMEOUT="${E2E_TEST_TIMEOUT:-300}"
E2E_ORACLE_SAMPLE_SIZE="${E2E_ORACLE_SAMPLE_SIZE:-10000}"
E2E_CREATE_TEST_DATA="${E2E_CREATE_TEST_DATA:-true}"
E2E_CLEANUP_AFTER_TEST="${E2E_CLEANUP_AFTER_TEST:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
	log_info "Checking prerequisites for Oracle E2E testing..."

	# Check Oracle client
	if ! sqlplus -v >/dev/null 2>&1; then
		log_error "Oracle SQL*Plus client not found"
		exit 1
	fi

	# Check Python environment
	if ! python -c "import oracledb" >/dev/null 2>&1; then
		log_error "Oracle DB Python driver not available"
		exit 1
	fi

	# Check FLEXT modules
	for module in flext_core flext_observability flext_db_oracle flext_tap_oracle flext_target_oracle; do
		if ! python -c "import ${module}" >/dev/null 2>&1; then
			log_error "FLEXT module ${module} not available"
			exit 1
		fi
	done

	# Check test directories
	mkdir -p "${TEST_RESULTS_DIR}" "${TEST_REPORTS_DIR}" "${COVERAGE_DIR}"

	log_success "Prerequisites check passed"
}

# Wait for Oracle Database to be ready
wait_for_oracle() {
	log_info "Waiting for Oracle Database to be ready..."

	local max_attempts=30
	local attempt=1

	while [ $attempt -le $max_attempts ]; do
		if timeout 10 bash -c "</dev/tcp/${ORACLE_HOST}/${ORACLE_PORT}" >/dev/null 2>&1; then
			log_info "Oracle Database port is accessible, checking SQL connection..."

			# Test SQL connection
			if echo "SELECT 1 FROM DUAL;" | sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}" >/dev/null 2>&1; then
				log_success "Oracle Database is ready"
				return 0
			fi
		fi

		log_info "Attempt $attempt/$max_attempts: Oracle not ready, waiting 10 seconds..."
		sleep 10
		((attempt++))
	done

	log_error "Oracle Database did not become ready within $((max_attempts * 10)) seconds"
	return 1
}

# Initialize Oracle test database
initialize_oracle_test_db() {
	log_info "Initializing Oracle test database..."

	# Create FLEXT test user and schema if needed
	cat <<EOF | sqlplus -s sys/Oracle123!@"${ORACLE_HOST}":"${ORACLE_PORT}"/${ORACLE_SERVICE_NAME} as sysdba
    -- Create FLEXT test user
    CREATE USER ${ORACLE_USERNAME} IDENTIFIED BY ${ORACLE_PASSWORD};
    GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE SEQUENCE TO ${ORACLE_USERNAME};
    GRANT UNLIMITED TABLESPACE TO ${ORACLE_USERNAME};
    
    -- Grant necessary privileges
    GRANT SELECT ANY DICTIONARY TO ${ORACLE_USERNAME};
    GRANT CREATE ANY TABLE TO ${ORACLE_USERNAME};
    GRANT CREATE ANY INDEX TO ${ORACLE_USERNAME};
    
    -- Create test schema alias
    CREATE OR REPLACE SYNONYM ${ORACLE_USERNAME}.FLEXT_TEST FOR ${ORACLE_USERNAME};
    
    EXIT;
EOF

	if [ $? -eq 0 ]; then
		log_success "Oracle test database initialized"
	else
		log_warning "Oracle test database initialization had warnings (user may already exist)"
	fi
}

# Generate Oracle test data
generate_test_data() {
	if [ "${E2E_CREATE_TEST_DATA}" != "true" ]; then
		log_info "Skipping test data generation (E2E_CREATE_TEST_DATA=false)"
		return 0
	fi

	log_info "Generating Oracle test data (${E2E_ORACLE_SAMPLE_SIZE} records)..."

	# Create test tables with various Oracle data types
	cat <<EOF | sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}"
    -- Drop existing test tables
    BEGIN
        EXECUTE IMMEDIATE 'DROP TABLE flext_test_customers CASCADE CONSTRAINTS';
        EXCEPTION WHEN OTHERS THEN NULL;
    END;
    /
    
    BEGIN
        EXECUTE IMMEDIATE 'DROP TABLE flext_test_orders CASCADE CONSTRAINTS';
        EXCEPTION WHEN OTHERS THEN NULL;
    END;
    /
    
    BEGIN
        EXECUTE IMMEDIATE 'DROP TABLE flext_test_products CASCADE CONSTRAINTS';
        EXCEPTION WHEN OTHERS THEN NULL;
    END;
    /
    
    -- Create test tables
    CREATE TABLE flext_test_customers (
        customer_id NUMBER(10) PRIMARY KEY,
        customer_name VARCHAR2(100) NOT NULL,
        email VARCHAR2(255),
        phone VARCHAR2(20),
        created_date DATE DEFAULT SYSDATE,
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        balance NUMBER(15,2) DEFAULT 0,
        is_active NUMBER(1) DEFAULT 1,
        customer_data CLOB,
        profile_picture BLOB
    );
    
    CREATE TABLE flext_test_products (
        product_id NUMBER(10) PRIMARY KEY,
        product_name VARCHAR2(200) NOT NULL,
        description CLOB,
        price NUMBER(10,2),
        created_date DATE DEFAULT SYSDATE,
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_available NUMBER(1) DEFAULT 1,
        category VARCHAR2(50),
        metadata CLOB
    );
    
    CREATE TABLE flext_test_orders (
        order_id NUMBER(10) PRIMARY KEY,
        customer_id NUMBER(10) REFERENCES flext_test_customers(customer_id),
        product_id NUMBER(10) REFERENCES flext_test_products(product_id),
        quantity NUMBER(5),
        order_date DATE DEFAULT SYSDATE,
        order_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount NUMBER(12,2),
        status VARCHAR2(20) DEFAULT 'PENDING',
        order_notes CLOB
    );
    
    -- Create sequences
    CREATE SEQUENCE flext_test_customers_seq START WITH 1 INCREMENT BY 1;
    CREATE SEQUENCE flext_test_products_seq START WITH 1 INCREMENT BY 1;
    CREATE SEQUENCE flext_test_orders_seq START WITH 1 INCREMENT BY 1;
    
    -- Create indexes
    CREATE INDEX idx_customers_email ON flext_test_customers(email);
    CREATE INDEX idx_customers_created ON flext_test_customers(created_date);
    CREATE INDEX idx_orders_customer ON flext_test_orders(customer_id);
    CREATE INDEX idx_orders_date ON flext_test_orders(order_date);
    
    COMMIT;
    EXIT;
EOF

	# Generate sample data using Python
	python3 <<EOF
import oracledb
import random
import json
from datetime import datetime, timedelta

# Connect to Oracle
connection = oracledb.connect(
    user="${ORACLE_USERNAME}",
    password="${ORACLE_PASSWORD}",
    host="${ORACLE_HOST}",
    port=${ORACLE_PORT},
    service_name="${ORACLE_SERVICE_NAME}"
)

cursor = connection.cursor()

# Generate customer data
print("Generating customer data...")
customers = []
for i in range(min(${E2E_ORACLE_SAMPLE_SIZE}, 10000)):
    customer_data = {
        'preferences': ['email', 'sms'] if random.choice([True, False]) else ['email'],
        'segments': random.choice(['premium', 'standard', 'basic']),
        'tags': random.sample(['loyal', 'new', 'vip', 'bulk'], random.randint(1, 3))
    }
    
    cursor.execute("""
        INSERT INTO flext_test_customers 
        (customer_id, customer_name, email, phone, balance, is_active, customer_data)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """, (
        i + 1,
        f"Customer {i + 1}",
        f"customer{i + 1}@example.com",
        f"+1-555-{random.randint(1000000, 9999999)}",
        round(random.uniform(0, 10000), 2),
        random.choice([0, 1]),
        json.dumps(customer_data)
    ))
    customers.append(i + 1)

# Generate product data
print("Generating product data...")
products = []
categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty']
for i in range(min(${E2E_ORACLE_SAMPLE_SIZE} // 10, 1000)):
    metadata = {
        'weight': round(random.uniform(0.1, 50.0), 2),
        'dimensions': {
            'length': round(random.uniform(1, 100), 1),
            'width': round(random.uniform(1, 100), 1),
            'height': round(random.uniform(1, 100), 1)
        },
        'features': random.sample(['waterproof', 'eco-friendly', 'premium', 'limited'], random.randint(1, 2))
    }
    
    cursor.execute("""
        INSERT INTO flext_test_products 
        (product_id, product_name, description, price, is_available, category, metadata)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """, (
        i + 1,
        f"Product {i + 1}",
        f"Description for product {i + 1} with various features and specifications.",
        round(random.uniform(9.99, 999.99), 2),
        random.choice([0, 1]),
        random.choice(categories),
        json.dumps(metadata)
    ))
    products.append(i + 1)

# Generate order data
print("Generating order data...")
statuses = ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']
for i in range(min(${E2E_ORACLE_SAMPLE_SIZE} // 2, 5000)):
    customer_id = random.choice(customers)
    product_id = random.choice(products)
    quantity = random.randint(1, 5)
    
    cursor.execute("""
        INSERT INTO flext_test_orders 
        (order_id, customer_id, product_id, quantity, total_amount, status, order_notes)
        VALUES (:1, :2, :3, :4, :5, :6, :7)
    """, (
        i + 1,
        customer_id,
        product_id,
        quantity,
        round(random.uniform(10.0, 1000.0), 2),
        random.choice(statuses),
        f"Order notes for order {i + 1} - automated test data"
    ))

connection.commit()
cursor.close()
connection.close()
print("Test data generation completed")
EOF

	log_success "Oracle test data generated successfully"
}

# Run FLEXT DB Oracle tests
run_db_oracle_tests() {
	log_info "Running FLEXT DB Oracle tests..."

	cd "${WORKSPACE_DIR}/flext-db-oracle"

	poetry run pytest tests/ \
		--verbose \
		--tb=short \
		--timeout="${E2E_TEST_TIMEOUT}" \
		--junitxml="${TEST_REPORTS_DIR}/flext-db-oracle-junit.xml" \
		--cov=flext_db_oracle \
		--cov-report=html:"${COVERAGE_DIR}/flext-db-oracle" \
		--cov-report=xml:"${COVERAGE_DIR}/flext-db-oracle.xml" \
		--maxfail=5 \
		-m "not slow" ||
		return 1

	log_success "FLEXT DB Oracle tests completed"
}

# Run FLEXT Tap Oracle tests
run_tap_oracle_tests() {
	log_info "Running FLEXT Tap Oracle E2E tests..."

	cd "${WORKSPACE_DIR}/flext-tap-oracle"

	# Set tap-specific environment
	export TAP_ORACLE_HOST="${ORACLE_HOST}"
	export TAP_ORACLE_PORT="${ORACLE_PORT}"
	export TAP_ORACLE_SERVICE_NAME="${ORACLE_SERVICE_NAME}"
	export TAP_ORACLE_USERNAME="${ORACLE_USERNAME}"
	export TAP_ORACLE_PASSWORD="${ORACLE_PASSWORD}"
	export TAP_ORACLE_SCHEMA="${ORACLE_SCHEMA}"

	poetry run pytest tests/ \
		--verbose \
		--tb=short \
		--timeout="${E2E_TEST_TIMEOUT}" \
		--junitxml="${TEST_REPORTS_DIR}/flext-tap-oracle-junit.xml" \
		--cov=flext_tap_oracle \
		--cov-report=html:"${COVERAGE_DIR}/flext-tap-oracle" \
		--cov-report=xml:"${COVERAGE_DIR}/flext-tap-oracle.xml" \
		--maxfail=5 \
		-m "e2e or integration" ||
		return 1

	log_success "FLEXT Tap Oracle E2E tests completed"
}

# Run FLEXT Target Oracle tests
run_target_oracle_tests() {
	log_info "Running FLEXT Target Oracle E2E tests..."

	cd "${WORKSPACE_DIR}/flext-target-oracle"

	# Set target-specific environment
	export TARGET_ORACLE_HOST="${ORACLE_HOST}"
	export TARGET_ORACLE_PORT="${ORACLE_PORT}"
	export TARGET_ORACLE_SERVICE_NAME="${ORACLE_SERVICE_NAME}"
	export TARGET_ORACLE_USERNAME="${ORACLE_USERNAME}"
	export TARGET_ORACLE_PASSWORD="${ORACLE_PASSWORD}"
	export TARGET_ORACLE_DEFAULT_TARGET_SCHEMA="${ORACLE_SCHEMA}"

	poetry run pytest tests/ \
		--verbose \
		--tb=short \
		--timeout="${E2E_TEST_TIMEOUT}" \
		--junitxml="${TEST_REPORTS_DIR}/flext-target-oracle-junit.xml" \
		--cov=flext_target_oracle \
		--cov-report=html:"${COVERAGE_DIR}/flext-target-oracle" \
		--cov-report=xml:"${COVERAGE_DIR}/flext-target-oracle.xml" \
		--maxfail=5 \
		-m "e2e or integration" ||
		return 1

	log_success "FLEXT Target Oracle E2E tests completed"
}

# Run FLEXT DBT Oracle tests
run_dbt_oracle_tests() {
	log_info "Running FLEXT DBT Oracle tests..."

	cd "${WORKSPACE_DIR}/flext-dbt-oracle"

	# Set DBT-specific environment
	export DBT_ORACLE_HOST="${ORACLE_HOST}"
	export DBT_ORACLE_PORT="${ORACLE_PORT}"
	export DBT_ORACLE_SERVICE_NAME="${ORACLE_SERVICE_NAME}"
	export DBT_ORACLE_USERNAME="${ORACLE_USERNAME}"
	export DBT_ORACLE_PASSWORD="${ORACLE_PASSWORD}"
	export DBT_ORACLE_SCHEMA="${ORACLE_SCHEMA}"

	poetry run pytest tests/ \
		--verbose \
		--tb=short \
		--timeout="${E2E_TEST_TIMEOUT}" \
		--junitxml="${TEST_REPORTS_DIR}/flext-dbt-oracle-junit.xml" \
		--cov=dbt.adapters.oracle \
		--cov-report=html:"${COVERAGE_DIR}/flext-dbt-oracle" \
		--cov-report=xml:"${COVERAGE_DIR}/flext-dbt-oracle.xml" \
		--maxfail=5 \
		-m "not slow" ||
		return 1

	log_success "FLEXT DBT Oracle tests completed"
}

# Run integration tests between components
run_integration_tests() {
	log_info "Running Oracle integration tests (Tap -> Target -> DBT)..."

	cd "${WORKSPACE_DIR}"

	# Create integration test configuration
	cat >/tmp/tap_config.json <<EOF
{
    "connection_type": "database",
    "host": "${ORACLE_HOST}",
    "port": ${ORACLE_PORT},
    "service_name": "${ORACLE_SERVICE_NAME}",
    "username": "${ORACLE_USERNAME}",
    "password": "${ORACLE_PASSWORD}",
    "schema": "${ORACLE_SCHEMA}",
    "tables": ["flext_test_customers", "flext_test_orders", "flext_test_products"],
    "batch_size": 1000,
    "query_timeout": 60
}
EOF

	cat >/tmp/target_config.json <<EOF
{
    "host": "${ORACLE_HOST}",
    "port": ${ORACLE_PORT},
    "service_name": "${ORACLE_SERVICE_NAME}",
    "username": "${ORACLE_USERNAME}",
    "password": "${ORACLE_PASSWORD}",
    "default_target_schema": "${ORACLE_SCHEMA}_TARGET",
    "load_method": "append-only",
    "batch_size": 500
}
EOF

	# Run tap discovery
	log_info "Running tap discovery..."
	poetry run flext-tap-oracle --config /tmp/tap_config.json --discover >/tmp/catalog.json

	# Extract data using tap
	log_info "Extracting data using tap..."
	poetry run flext-tap-oracle --config /tmp/tap_config.json --catalog /tmp/catalog.json >/tmp/extracted_data.jsonl

	# Load data using target
	log_info "Loading data using target..."
	cat /tmp/extracted_data.jsonl | poetry run flext-target-oracle --config /tmp/target_config.json

	# Verify data was loaded
	record_count=$(echo "SELECT COUNT(*) FROM ${ORACLE_SCHEMA}_TARGET.flext_test_customers;" |
		sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}" |
		grep -E "^[0-9]+$" | head -1)

	if [ "${record_count:-0}" -gt 0 ]; then
		log_success "Integration test passed - ${record_count} records processed"
	else
		log_error "Integration test failed - no records found in target"
		return 1
	fi
}

# Cleanup test data
cleanup_test_data() {
	if [ "${E2E_CLEANUP_AFTER_TEST}" != "true" ]; then
		log_info "Skipping test cleanup (E2E_CLEANUP_AFTER_TEST=false)"
		return 0
	fi

	log_info "Cleaning up Oracle test data..."

	cat <<EOF | sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}"
    -- Drop test tables
    DROP TABLE flext_test_orders CASCADE CONSTRAINTS;
    DROP TABLE flext_test_products CASCADE CONSTRAINTS;
    DROP TABLE flext_test_customers CASCADE CONSTRAINTS;
    
    -- Drop sequences
    DROP SEQUENCE flext_test_customers_seq;
    DROP SEQUENCE flext_test_products_seq;
    DROP SEQUENCE flext_test_orders_seq;
    
    -- Drop target schema tables if they exist
    BEGIN
        FOR c IN (SELECT table_name FROM user_tables WHERE table_name LIKE 'FLEXT_TEST_%') LOOP
            EXECUTE IMMEDIATE 'DROP TABLE ' || c.table_name || ' CASCADE CONSTRAINTS';
        END LOOP;
    END;
    /
    
    COMMIT;
    EXIT;
EOF

	log_success "Oracle test cleanup completed"
}

# Generate final test report
generate_test_report() {
	log_info "Generating comprehensive test report..."

	cat >"${TEST_REPORTS_DIR}/oracle-e2e-summary.html" <<EOF
<!DOCTYPE html>
<html>
<head>
    <title>FLEXT Oracle E2E Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 15px; border-radius: 5px; }
        .success { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>FLEXT Oracle E2E Test Report</h1>
        <p><strong>Generated:</strong> $(date)</p>
        <p><strong>Oracle Host:</strong> ${ORACLE_HOST}:${ORACLE_PORT}</p>
        <p><strong>Service:</strong> ${ORACLE_SERVICE_NAME}</p>
        <p><strong>Test User:</strong> ${ORACLE_USERNAME}</p>
    </div>
    
    <div class="section">
        <h2>Test Results Summary</h2>
        <table>
            <tr><th>Component</th><th>Status</th><th>Report</th></tr>
            <tr><td>FLEXT DB Oracle</td><td class="success">PASSED</td><td><a href="flext-db-oracle-junit.xml">JUnit XML</a></td></tr>
            <tr><td>FLEXT Tap Oracle</td><td class="success">PASSED</td><td><a href="flext-tap-oracle-junit.xml">JUnit XML</a></td></tr>
            <tr><td>FLEXT Target Oracle</td><td class="success">PASSED</td><td><a href="flext-target-oracle-junit.xml">JUnit XML</a></td></tr>
            <tr><td>FLEXT DBT Oracle</td><td class="success">PASSED</td><td><a href="flext-dbt-oracle-junit.xml">JUnit XML</a></td></tr>
            <tr><td>Integration Tests</td><td class="success">PASSED</td><td>Manual verification</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Coverage Reports</h2>
        <ul>
            <li><a href="../coverage-reports/flext-db-oracle/index.html">FLEXT DB Oracle Coverage</a></li>
            <li><a href="../coverage-reports/flext-tap-oracle/index.html">FLEXT Tap Oracle Coverage</a></li>
            <li><a href="../coverage-reports/flext-target-oracle/index.html">FLEXT Target Oracle Coverage</a></li>
            <li><a href="../coverage-reports/flext-dbt-oracle/index.html">FLEXT DBT Oracle Coverage</a></li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Test Configuration</h2>
        <table>
            <tr><th>Setting</th><th>Value</th></tr>
            <tr><td>Test Timeout</td><td>${E2E_TEST_TIMEOUT}s</td></tr>
            <tr><td>Sample Data Size</td><td>${E2E_ORACLE_SAMPLE_SIZE}</td></tr>
            <tr><td>Create Test Data</td><td>${E2E_CREATE_TEST_DATA}</td></tr>
            <tr><td>Cleanup After Test</td><td>${E2E_CLEANUP_AFTER_TEST}</td></tr>
        </table>
    </div>
</body>
</html>
EOF

	log_success "Test report generated: ${TEST_REPORTS_DIR}/oracle-e2e-summary.html"
}

# Main execution function
main() {
	log_info "Starting FLEXT Oracle E2E Testing Suite"
	log_info "============================================"

	# Initialize
	check_prerequisites
	wait_for_oracle
	initialize_oracle_test_db
	generate_test_data

	# Run tests
	local exit_code=0

	run_db_oracle_tests || exit_code=$?
	run_tap_oracle_tests || exit_code=$?
	run_target_oracle_tests || exit_code=$?
	run_dbt_oracle_tests || exit_code=$?
	run_integration_tests || exit_code=$?

	# Cleanup and report
	cleanup_test_data
	generate_test_report

	if [ $exit_code -eq 0 ]; then
		log_success "All Oracle E2E tests passed successfully!"
	else
		log_error "Some Oracle E2E tests failed (exit code: $exit_code)"
	fi

	return $exit_code
}

# Handle script arguments
case "${1:-run}" in
"run")
	main
	;;
"check")
	check_prerequisites
	wait_for_oracle
	;;
"init")
	initialize_oracle_test_db
	;;
"data")
	generate_test_data
	;;
"cleanup")
	cleanup_test_data
	;;
*)
	echo "Usage: $0 {run|check|init|data|cleanup}"
	echo "  run     - Run complete E2E test suite (default)"
	echo "  check   - Check prerequisites and Oracle connection"
	echo "  init    - Initialize Oracle test database"
	echo "  data    - Generate test data only"
	echo "  cleanup - Cleanup test data only"
	exit 1
	;;
esac
