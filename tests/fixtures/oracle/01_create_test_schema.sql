-- Oracle Test Schema Setup for FLEXT E2E Testing
-- Creates test data for Oracle Database tap/target/dbt validation

-- Connect to the pluggable database
ALTER SESSION SET CONTAINER = XEPDB1;

-- Create test schemas
CREATE USER flext_source IDENTIFIED BY flext_source_password DEFAULT TABLESPACE USERS;
CREATE USER flext_target IDENTIFIED BY flext_target_password DEFAULT TABLESPACE USERS;
CREATE USER flext_dbt IDENTIFIED BY flext_dbt_password DEFAULT TABLESPACE USERS;

-- Grant necessary privileges
GRANT CONNECT, RESOURCE, CREATE VIEW TO flext_source;
GRANT CONNECT, RESOURCE, CREATE VIEW TO flext_target;
GRANT CONNECT, RESOURCE, CREATE VIEW TO flext_dbt;

-- Grant DBA privileges for testing (not for production)
GRANT DBA TO flext_source;
GRANT DBA TO flext_target;
GRANT DBA TO flext_dbt;

-- Connect as source user to create test data
ALTER SESSION SET CURRENT_SCHEMA = flext_source;

-- Create test tables with various Oracle data types
CREATE TABLE customers (
    customer_id NUMBER PRIMARY KEY,
    customer_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(255) UNIQUE,
    phone VARCHAR2(20),
    address CLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active NUMBER(1) DEFAULT 1,
    credit_limit NUMBER(10,2),
    customer_metadata CLOB CHECK (customer_metadata IS JSON)
);

CREATE TABLE orders (
    order_id NUMBER PRIMARY KEY,
    customer_id NUMBER NOT NULL,
    order_date DATE DEFAULT SYSDATE,
    order_status VARCHAR2(20) DEFAULT 'PENDING',
    total_amount NUMBER(12,2) NOT NULL,
    order_details CLOB CHECK (order_details IS JSON),
    shipping_address CLOB,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE products (
    product_id NUMBER PRIMARY KEY,
    product_name VARCHAR2(200) NOT NULL,
    category VARCHAR2(50),
    price NUMBER(10,2),
    stock_quantity NUMBER DEFAULT 0,
    product_attributes CLOB CHECK (product_attributes IS JSON),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id NUMBER PRIMARY KEY,
    order_id NUMBER NOT NULL,
    product_id NUMBER NOT NULL,
    quantity NUMBER NOT NULL,
    unit_price NUMBER(10,2) NOT NULL,
    line_total NUMBER(12,2) GENERATED ALWAYS AS (quantity * unit_price),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create sequences for primary keys
CREATE SEQUENCE seq_customers START WITH 1000;
CREATE SEQUENCE seq_orders START WITH 2000;
CREATE SEQUENCE seq_products START WITH 3000;
CREATE SEQUENCE seq_order_items START WITH 4000;

-- Create test data
-- Insert customers with complex JSON metadata
INSERT INTO customers (
    customer_id, customer_name, email, phone, address, 
    credit_limit, customer_metadata
) VALUES (
    seq_customers.NEXTVAL,
    'Oracle Corp Test Customer',
    'test@oracle.com',
    '+1-555-0123',
    'Oracle Parkway, Redwood City, CA',
    50000.00,
    '{"preferences": {"newsletter": true, "marketing": false}, "tier": "enterprise", "tags": ["oracle", "database", "enterprise"]}'
);

INSERT INTO customers (
    customer_id, customer_name, email, phone, address, 
    credit_limit, customer_metadata
) VALUES (
    seq_customers.NEXTVAL,
    'FLEXT Integration Test',
    'flext@test.com',
    '+1-555-0456',
    '123 Integration St, Test City, TC',
    25000.00,
    '{"preferences": {"newsletter": false, "marketing": true}, "tier": "professional", "tags": ["flext", "singer", "integration"]}'
);

-- Insert products with complex attributes
INSERT INTO products (
    product_id, product_name, category, price, stock_quantity, product_attributes
) VALUES (
    seq_products.NEXTVAL,
    'Oracle Database Enterprise Edition',
    'Database Software',
    47500.00,
    100,
    '{"version": "23c", "features": ["RAC", "Partitioning", "Advanced Security"], "licensing": "per_processor", "support_level": "premier"}'
);

INSERT INTO products (
    product_id, product_name, category, price, stock_quantity, product_attributes
) VALUES (
    seq_products.NEXTVAL,
    'FLEXT Data Platform',
    'Data Integration',
    12000.00,
    50,
    '{"version": "0.7.0", "features": ["Singer SDK", "Oracle Integration", "DBT"], "licensing": "subscription", "support_level": "enterprise"}'
);

-- Insert orders with complex details
INSERT INTO orders (
    order_id, customer_id, order_status, total_amount, order_details, shipping_address
) VALUES (
    seq_orders.NEXTVAL,
    (SELECT customer_id FROM customers WHERE email = 'test@oracle.com'),
    'COMPLETED',
    47500.00,
    '{"payment_method": "wire_transfer", "discount_applied": 0, "tax_rate": 0.08, "currency": "USD", "order_priority": "high"}',
    '{"street": "Oracle Parkway", "city": "Redwood City", "state": "CA", "country": "USA", "postal_code": "94065"}'
);

INSERT INTO orders (
    order_id, customer_id, order_status, total_amount, order_details, shipping_address
) VALUES (
    seq_orders.NEXTVAL,
    (SELECT customer_id FROM customers WHERE email = 'flext@test.com'),
    'PROCESSING',
    12000.00,
    '{"payment_method": "credit_card", "discount_applied": 500, "tax_rate": 0.08, "currency": "USD", "order_priority": "normal"}',
    '{"street": "123 Integration St", "city": "Test City", "state": "TC", "country": "USA", "postal_code": "12345"}'
);

-- Insert order items
INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price)
SELECT 
    seq_order_items.NEXTVAL,
    o.order_id,
    p.product_id,
    1,
    p.price
FROM orders o, products p
WHERE o.order_status IN ('COMPLETED', 'PROCESSING');

-- Create views for complex testing
CREATE VIEW customer_order_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent,
    MAX(o.order_date) as last_order_date,
    JSON_OBJECT(
        'customer_tier' VALUE JSON_VALUE(c.customer_metadata, '$.tier'),
        'total_orders' VALUE COUNT(o.order_id),
        'total_spent' VALUE SUM(o.total_amount)
    ) as customer_summary
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.email, c.customer_metadata;

-- Create materialized view for performance testing
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT 
    TRUNC(o.order_date) as sale_date,
    COUNT(*) as order_count,
    SUM(o.total_amount) as daily_revenue,
    AVG(o.total_amount) as avg_order_value
FROM orders o
WHERE o.order_status = 'COMPLETED'
GROUP BY TRUNC(o.order_date);

-- Create indexes for performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_order_items_order ON order_items(order_id);

COMMIT;

-- Log completion
SELECT 'Oracle test schema setup completed successfully' as status FROM dual;