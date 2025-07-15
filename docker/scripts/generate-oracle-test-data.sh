#!/bin/bash
# Oracle Test Data Generator - Standalone Script
# Creates sample Oracle database tables and data for FLEXT testing

set -euo pipefail

# Configuration
ORACLE_HOST="${ORACLE_HOST:-oracle-db}"
ORACLE_PORT="${ORACLE_PORT:-1521}"
ORACLE_SERVICE_NAME="${ORACLE_SERVICE_NAME:-FLEXT_PDB}"
ORACLE_USERNAME="${ORACLE_USERNAME:-FLEXT_USER}"
ORACLE_PASSWORD="${ORACLE_PASSWORD:-FlextTest123!}"
ORACLE_SCHEMA="${ORACLE_SCHEMA:-FLEXT_TEST}"

# Test data configuration
SAMPLE_SIZE="${SAMPLE_SIZE:-10000}"
CREATE_INDEXES="${CREATE_INDEXES:-true}"
CREATE_SEQUENCES="${CREATE_SEQUENCES:-true}"

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

# Create Oracle test tables
create_test_tables() {
	log_info "Creating Oracle test tables..."

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
    
    -- Create comprehensive test tables
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
    
    COMMIT;
    EXIT;
EOF

	if [ $? -eq 0 ]; then
		log_success "Oracle test tables created successfully"
	else
		log_error "Failed to create Oracle test tables"
		return 1
	fi
}

# Create Oracle sequences
create_sequences() {
	if [ "${CREATE_SEQUENCES}" != "true" ]; then
		log_info "Skipping sequence creation"
		return 0
	fi

	log_info "Creating Oracle sequences..."

	cat <<EOF | sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}"
    -- Drop existing sequences
    BEGIN
        EXECUTE IMMEDIATE 'DROP SEQUENCE flext_test_customers_seq';
        EXCEPTION WHEN OTHERS THEN NULL;
    END;
    /
    
    BEGIN
        EXECUTE IMMEDIATE 'DROP SEQUENCE flext_test_products_seq';
        EXCEPTION WHEN OTHERS THEN NULL;
    END;
    /
    
    BEGIN
        EXECUTE IMMEDIATE 'DROP SEQUENCE flext_test_orders_seq';
        EXCEPTION WHEN OTHERS THEN NULL;
    END;
    /
    
    -- Create sequences
    CREATE SEQUENCE flext_test_customers_seq START WITH 1 INCREMENT BY 1;
    CREATE SEQUENCE flext_test_products_seq START WITH 1 INCREMENT BY 1;
    CREATE SEQUENCE flext_test_orders_seq START WITH 1 INCREMENT BY 1;
    
    COMMIT;
    EXIT;
EOF

	if [ $? -eq 0 ]; then
		log_success "Oracle sequences created successfully"
	else
		log_warning "Failed to create some Oracle sequences"
	fi
}

# Create Oracle indexes
create_indexes() {
	if [ "${CREATE_INDEXES}" != "true" ]; then
		log_info "Skipping index creation"
		return 0
	fi

	log_info "Creating Oracle indexes..."

	cat <<EOF | sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}"
    -- Create indexes for better performance
    CREATE INDEX idx_customers_email ON flext_test_customers(email);
    CREATE INDEX idx_customers_created ON flext_test_customers(created_date);
    CREATE INDEX idx_customers_active ON flext_test_customers(is_active);
    
    CREATE INDEX idx_products_category ON flext_test_products(category);
    CREATE INDEX idx_products_available ON flext_test_products(is_available);
    CREATE INDEX idx_products_price ON flext_test_products(price);
    
    CREATE INDEX idx_orders_customer ON flext_test_orders(customer_id);
    CREATE INDEX idx_orders_product ON flext_test_orders(product_id);
    CREATE INDEX idx_orders_date ON flext_test_orders(order_date);
    CREATE INDEX idx_orders_status ON flext_test_orders(status);
    
    COMMIT;
    EXIT;
EOF

	if [ $? -eq 0 ]; then
		log_success "Oracle indexes created successfully"
	else
		log_warning "Failed to create some Oracle indexes"
	fi
}

# Generate sample data using Python
generate_sample_data() {
	log_info "Generating ${SAMPLE_SIZE} sample records..."

	python3 <<EOF
import oracledb
import random
import json
from datetime import datetime, timedelta

# Connect to Oracle
try:
    connection = oracledb.connect(
        user="${ORACLE_USERNAME}",
        password="${ORACLE_PASSWORD}",
        host="${ORACLE_HOST}",
        port=${ORACLE_PORT},
        service_name="${ORACLE_SERVICE_NAME}"
    )
    cursor = connection.cursor()
    print("Connected to Oracle successfully")
except Exception as e:
    print(f"Failed to connect to Oracle: {e}")
    exit(1)

# Generate customer data
print("Generating customer data...")
customers = []
for i in range(min(${SAMPLE_SIZE}, 10000)):
    customer_data = {
        'preferences': ['email', 'sms'] if random.choice([True, False]) else ['email'],
        'segment': random.choice(['premium', 'standard', 'basic']),
        'tags': random.sample(['loyal', 'new', 'vip', 'bulk'], random.randint(1, 3)),
        'registration_source': random.choice(['web', 'mobile', 'store', 'referral'])
    }
    
    try:
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
    except Exception as e:
        print(f"Error inserting customer {i + 1}: {e}")
        break

print(f"Generated {len(customers)} customers")

# Generate product data
print("Generating product data...")
products = []
categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty', 'Automotive', 'Toys']
for i in range(min(${SAMPLE_SIZE} // 10, 1000)):
    metadata = {
        'weight': round(random.uniform(0.1, 50.0), 2),
        'dimensions': {
            'length': round(random.uniform(1, 100), 1),
            'width': round(random.uniform(1, 100), 1),
            'height': round(random.uniform(1, 100), 1)
        },
        'features': random.sample(['waterproof', 'eco-friendly', 'premium', 'limited', 'bestseller'], random.randint(1, 3)),
        'brand': random.choice(['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE'])
    }
    
    try:
        cursor.execute("""
            INSERT INTO flext_test_products 
            (product_id, product_name, description, price, is_available, category, metadata)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
        """, (
            i + 1,
            f"Product {i + 1}",
            f"Description for product {i + 1} with various features and specifications for testing purposes.",
            round(random.uniform(9.99, 999.99), 2),
            random.choice([0, 1]),
            random.choice(categories),
            json.dumps(metadata)
        ))
        products.append(i + 1)
    except Exception as e:
        print(f"Error inserting product {i + 1}: {e}")
        break

print(f"Generated {len(products)} products")

# Generate order data
print("Generating order data...")
statuses = ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
orders_count = 0
for i in range(min(${SAMPLE_SIZE} // 2, 5000)):
    if not customers or not products:
        break
        
    customer_id = random.choice(customers)
    product_id = random.choice(products)
    quantity = random.randint(1, 5)
    
    try:
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
            f"Order notes for order {i + 1} - automated test data generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ))
        orders_count += 1
    except Exception as e:
        print(f"Error inserting order {i + 1}: {e}")
        break

print(f"Generated {orders_count} orders")

# Commit all changes
connection.commit()
cursor.close()
connection.close()
print("Sample data generation completed successfully")
EOF

	if [ $? -eq 0 ]; then
		log_success "Sample data generated successfully"
	else
		log_error "Failed to generate sample data"
		return 1
	fi
}

# Verify data was created
verify_data() {
	log_info "Verifying generated data..."

	local customer_count=$(echo "SELECT COUNT(*) FROM flext_test_customers;" |
		sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}" |
		grep -E "^[0-9]+$" | head -1)

	local product_count=$(echo "SELECT COUNT(*) FROM flext_test_products;" |
		sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}" |
		grep -E "^[0-9]+$" | head -1)

	local order_count=$(echo "SELECT COUNT(*) FROM flext_test_orders;" |
		sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}" |
		grep -E "^[0-9]+$" | head -1)

	log_info "Data verification results:"
	log_info "  Customers: ${customer_count:-0}"
	log_info "  Products: ${product_count:-0}"
	log_info "  Orders: ${order_count:-0}"

	if [ "${customer_count:-0}" -gt 0 ] && [ "${product_count:-0}" -gt 0 ] && [ "${order_count:-0}" -gt 0 ]; then
		log_success "All test data verified successfully"
		return 0
	else
		log_error "Data verification failed"
		return 1
	fi
}

# Main execution
main() {
	log_info "Starting Oracle test data generation"
	log_info "======================================"
	log_info "Target: ${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}"
	log_info "User: ${ORACLE_USERNAME}"
	log_info "Sample size: ${SAMPLE_SIZE}"

	# Execute steps
	create_test_tables || exit 1
	create_sequences
	create_indexes
	generate_sample_data || exit 1
	verify_data || exit 1

	log_success "Oracle test data generation completed successfully!"
}

# Handle script arguments
case "${1:-generate}" in
"generate")
	main
	;;
"tables")
	create_test_tables
	;;
"sequences")
	create_sequences
	;;
"indexes")
	create_indexes
	;;
"data")
	generate_sample_data
	;;
"verify")
	verify_data
	;;
*)
	echo "Usage: $0 {generate|tables|sequences|indexes|data|verify}"
	echo "  generate  - Complete test data generation (default)"
	echo "  tables    - Create test tables only"
	echo "  sequences - Create sequences only"
	echo "  indexes   - Create indexes only"
	echo "  data      - Generate sample data only"
	echo "  verify    - Verify generated data"
	exit 1
	;;
esac
