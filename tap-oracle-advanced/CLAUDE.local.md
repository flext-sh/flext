# internal.invalid.md - TAP-ORACLE-ADVANCED PROJECT SPECIFICS

**Hierarquia**: **PROJECT-SPECIFIC**
**Projeto**: Tap Oracle Advanced - Enterprise Oracle Database Extractor
**Status**: DEVELOPMENT - Advanced Singer tap in development
**Framework**: Singer SDK 0.45.0+ + FLX Framework + Oracle Database 19c+
**Última Atualização**: 2025-06-26

**Referência Global**: `/home/marlonsc/CLAUDE.md` → Universal principles
**Referência Workspace**: `../CLAUDE.md` → PyAuto workspace patterns
**Referência Cross-Workspace**: `/home/marlonsc/internal.invalid.md` → Cross-workspace issues

---

## 🎯 PROJECT-SPECIFIC CONFIGURATION

### Virtual Environment Usage
```bash
# MANDATORY: Use workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate
# NOT project-specific venv
```

### Agent Coordination
```bash
# Read workspace coordination first
cat /home/marlonsc/pyauto/.token | tail -5
# Use project .token only for project-specific coordination
```

### Project-Specific Environment Variables
```bash
# Tap Oracle Advanced specific configurations
export TAP_ORACLE_HOST=oracle.enterprise.com
export TAP_ORACLE_PORT=1521
export TAP_ORACLE_SERVICE_NAME=ORCL
export TAP_ORACLE_USER=tap_advanced_user
export TAP_ORACLE_PASSWORD=secure_oracle_password
export TAP_ORACLE_DEFAULT_SCHEMA=SALES
export TAP_ORACLE_BATCH_SIZE=50000
export TAP_ORACLE_CONNECTION_POOL_SIZE=10
export TAP_ORACLE_CONNECTION_TIMEOUT=60
export TAP_ORACLE_COMMAND_TIMEOUT=600
export TAP_ORACLE_LOG_LEVEL=DEBUG
export TAP_ORACLE_ENABLE_SQL_LOGGING=false
```

---

## 🏗️ TAP ORACLE ADVANCED ARCHITECTURE

### **Purpose & Role**
- **Enterprise Oracle Extractor**: Modern Singer tap for high-performance Oracle data extraction
- **Advanced SQL Support**: Custom queries, complex joins, and aggregations as Singer streams
- **Performance Optimized**: Connection pooling, batch processing, and parallel query execution
- **FLX Framework Integration**: Hexagonal architecture with robust Oracle database connections
- **Modern Development Stack**: Python 3.13+, Singer SDK 0.45.0+, latest Oracle patterns

### **Core Advanced Components**
```python
# Tap Oracle Advanced structure
src/tap_oracle_advanced/
├── __init__.py          # Package initialization
├── __version__.py       # Version management
├── tap.py               # Main Singer tap implementation
└── client.py            # Advanced Oracle client with FLX integration
```

### **Enterprise Oracle Features**
- **Multiple Connection Types**: SID and Service Name support with connection pooling
- **Schema Discovery**: Dynamic table, view, and materialized view detection
- **Custom Query Streams**: SQL queries as configurable Singer streams
- **Advanced Data Types**: Full Oracle data type mapping with modern JSON Schema
- **Performance Optimization**: Cursor array fetching, bind variables, parallel queries

---

## 🔧 PROJECT-SPECIFIC TECHNICAL DETAILS

### **Development Commands**
```bash
# MANDATORY: Always from workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate

# Core development workflow
make install-dev       # Install development dependencies
make test              # Run comprehensive test suite
make test-unit         # Unit tests only
make test-integration  # Integration tests with Oracle database
make lint              # Code quality checks
make format            # Code formatting

# Singer tap operations
tap-oracle-advanced --config config.json --discover > catalog.json
tap-oracle-advanced --config config.json --catalog catalog.json
tap-oracle-advanced --config config.json --catalog catalog.json --state state.json
```

### **Oracle Connection Testing**
```bash
# Test Oracle connectivity
tap-oracle-advanced --config config.json --test

# Test with debug logging
export TAP_ORACLE_LOG_LEVEL=DEBUG
export TAP_ORACLE_ENABLE_SQL_LOGGING=true
tap-oracle-advanced --config config.json --discover

# Test performance with large datasets
tap-oracle-advanced --config config.json --catalog catalog.json --debug | head -1000
```

### **Advanced Oracle Integration Testing**
```bash
# Test custom query streams
cat > custom_config.json << 'EOF'
{
  "host": "oracle.test.com",
  "user": "test_user",
  "password": "test_password",
  "custom_queries": [
    {
      "name": "sales_summary",
      "sql": "SELECT DATE_TRUNC('day', order_date) as day, SUM(amount) as total FROM orders GROUP BY DATE_TRUNC('day', order_date)",
      "replication_method": "FULL_TABLE",
      "primary_keys": ["day"]
    }
  ]
}
EOF

tap-oracle-advanced --config custom_config.json --discover
```

---

## 🚨 PROJECT-SPECIFIC KNOWN ISSUES

### **Oracle Advanced Integration Challenges**
- **Connection Pool Management**: Complex connection lifecycle with Oracle Instant Client
- **Large Object Handling**: CLOB/BLOB streaming for memory-efficient processing
- **Oracle Data Type Complexity**: Advanced Oracle types requiring careful mapping
- **Performance Scaling**: Optimization needed for very large Oracle databases
- **Custom Query Validation**: Complex SQL query validation and error handling

### **Singer SDK Advanced Considerations**
```python
# Oracle-specific Singer advanced patterns
class OracleAdvancedSingerPatterns:
    """Advanced patterns for Oracle Singer implementation."""

    def handle_oracle_connection_pooling(self):
        """Manage Oracle connection pools efficiently."""
        # Advanced connection pool configuration
        pool_config = {
            "min_pool_size": 2,
            "max_pool_size": self.config.connection_pool_size,
            "increment": 1,
            "connection_timeout": self.config.connection_timeout,
            "session_pool": True,
            "homogeneous": True
        }

        # Handle connection recovery
        return oracledb.create_pool(
            user=self.config.user,
            password=self.config.password,
            dsn=self.build_dsn(),
            **pool_config
        )

    def stream_large_oracle_objects(self, cursor, batch_size: int):
        """Stream large Oracle objects efficiently."""
        # Configure cursor for large object handling
        cursor.arraysize = min(batch_size, 10000)
        cursor.prefetchrows = cursor.arraysize

        # Stream results to manage memory
        while True:
            rows = cursor.fetchmany(cursor.arraysize)
            if not rows:
                break

            for row in rows:
                # Handle CLOB/BLOB streaming
                yield self.process_large_objects(row)

    def execute_custom_query_stream(self, query_config: dict):
        """Execute custom SQL queries as Singer streams."""
        # Validate SQL query safety
        validated_sql = self.validate_custom_sql(query_config["sql"])

        # Execute with bind variable support
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(validated_sql, self.build_bind_variables())

            # Stream results as Singer records
            for record in self.stream_large_oracle_objects(cursor, self.config.batch_size):
                yield self.transform_to_singer_record(
                    record=record,
                    stream_name=query_config["name"],
                    schema=self.get_stream_schema(query_config["name"])
                )
```

### **Production Oracle Edge Cases**
```bash
# Common Oracle advanced extraction issues
1. Connection Pool Exhaustion: Too many concurrent connections
2. Large Table Memory Issues: Tables with millions of rows requiring streaming
3. Complex Data Type Mapping: Oracle-specific types like INTERVAL, UDT
4. Custom Query Performance: Complex SQL requiring optimization
5. Schema Permission Issues: Missing privileges for metadata queries
```

---

## 🎯 PROJECT-SPECIFIC SUCCESS METRICS

### **Singer Protocol Advanced Compliance**
- **Schema Discovery Performance**: <30 seconds discovery for 1000+ table schemas
- **Data Extraction Throughput**: >100,000 records/minute for large Oracle tables
- **Memory Efficiency**: <2GB memory usage for unlimited data extraction
- **Connection Pool Utilization**: 95% efficient connection pool usage
- **Custom Query Performance**: <5 seconds execution for complex analytical queries

### **Enterprise Oracle Integration Goals**
- **Database Compatibility**: Support for Oracle 19c, 21c, 23c databases
- **Schema Scalability**: Handle schemas with 10,000+ tables and views
- **Data Type Coverage**: 100% Oracle data type mapping accuracy
- **Performance Optimization**: 10x performance improvement over basic Oracle taps
- **Production Reliability**: 99.9% successful extraction rate for enterprise workloads

---

## 🔗 PROJECT-SPECIFIC INTEGRATIONS

### **Singer Ecosystem Advanced Integration**
- **Target Compatibility**: Optimized for all Singer-compliant targets
- **Meltano Plugin**: Advanced Meltano Hub plugin with custom configuration
- **Schema Evolution**: Automatic schema change detection and adaptation
- **State Management**: Advanced incremental sync with multiple replication strategies

### **PyAuto Ecosystem Integration**
- **flx-database-oracle**: Shared Oracle connection patterns and optimization
- **target-oracle-advanced**: Perfect companion for round-trip Oracle operations
- **tap-oracle-wms**: Specialized WMS version based on advanced patterns
- **oracledb-core-shared**: Shared Oracle database models and utilities

### **Enterprise Oracle Integration**
```python
# Production Oracle advanced configuration
class ProductionOracleAdvancedConfig:
    """Production Oracle configuration for enterprise databases."""

    # High-performance production configuration
    ENTERPRISE_CONFIG = {
        "host": "oracle-prod.enterprise.com",
        "port": 1521,
        "service_name": "PRODDB",
        "user": "tap_oracle_advanced",
        "password": "${ORACLE_TAP_PASSWORD}",

        # Performance optimizations
        "connection_pool_size": 20,
        "cursor_array_size": 10000,
        "batch_size": 100000,
        "connection_timeout": 120,
        "command_timeout": 1800,

        # Advanced features
        "use_binds_for_partition": True,
        "enable_parallel_query": True,
        "parallel_degree": 8,
        "use_singer_decimal": True,
        "use_date_datatype": True,

        # Enterprise schema configuration
        "default_schema": "SALES",
        "schema_filter": ["SALES", "INVENTORY", "FINANCE", "HR"],
        "table_filter": ["SALES_*", "PRODUCT_*", "CUSTOMER_*"],
        "exclude_tables": ["*_TEMP", "*_BACKUP", "*_LOG"],

        # Custom analytical queries
        "custom_queries": [
            {
                "name": "sales_analytics",
                "sql": """
                    SELECT
                        DATE_TRUNC('day', s.sale_date) as sale_day,
                        p.category,
                        SUM(s.amount) as total_sales,
                        COUNT(*) as transaction_count,
                        AVG(s.amount) as avg_transaction
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    WHERE s.sale_date >= :start_date
                    GROUP BY DATE_TRUNC('day', s.sale_date), p.category
                    ORDER BY sale_day, p.category
                """,
                "replication_method": "INCREMENTAL",
                "replication_key": "sale_day",
                "primary_keys": ["sale_day", "category"]
            }
        ]
    }
```

---

## 📊 PROJECT-SPECIFIC MONITORING

### **Oracle Advanced Tap Metrics**
```python
# Key metrics for Oracle advanced tap monitoring
TAP_ORACLE_ADVANCED_METRICS = {
    "extraction_throughput": "Records extracted per second",
    "connection_pool_utilization": "Percentage of pool connections in use",
    "query_execution_time": "Average SQL query execution time",
    "memory_usage_efficiency": "Memory usage per extracted record",
    "schema_discovery_performance": "Time to discover all schemas",
    "custom_query_success_rate": "Success rate of custom query execution",
}
```

### **Oracle Database Health Monitoring**
```bash
# Comprehensive Oracle monitoring
tap-oracle-advanced --config config.json --test --detailed
tap-oracle-advanced --config config.json --discover --validate-schema
tap-oracle-advanced --config config.json --performance-test --duration 60
```

---

## 📋 PROJECT-SPECIFIC MAINTENANCE

### **Regular Maintenance Tasks**
- **Daily**: Monitor extraction performance and connection pool health
- **Weekly**: Review custom query performance and optimize SQL
- **Monthly**: Update Oracle client libraries and test compatibility
- **Quarterly**: Performance benchmarking and optimization review

### **Singer SDK Advanced Updates**
```bash
# Keep Singer SDK and Oracle dependencies updated
pip install --upgrade singer-sdk oracledb

# Validate Singer advanced compliance
singer-check-tap --tap tap-oracle-advanced --config config.json
singer-validate-schema --schema advanced_schema.json
```

### **Emergency Procedures**
```bash
# Oracle advanced tap emergency troubleshooting
1. Test Oracle connectivity: sqlplus user/password@host:port/service_name
2. Check connection pool: tap-oracle-advanced --config config.json --pool-status
3. Enable debug logging: export TAP_ORACLE_LOG_LEVEL=DEBUG
4. Test custom queries: tap-oracle-advanced --config config.json --test-custom-queries
5. Reset connection pool: tap-oracle-advanced --config config.json --reset-pool
```

---

**PROJECT SUMMARY**: Singer tap avançado para Oracle Database com arquitetura moderna, suporte a queries customizadas, otimização de performance e integração completa com FLX framework para extração empresarial de dados.

**CRITICAL SUCCESS FACTOR**: Manter performance otimizada e compatibilidade total com Singer SDK moderno, oferecendo extração Oracle enterprise com eficiência e confiabilidade máximas.

---

*Última Atualização: 2025-06-26*
*Próxima Revisão: Semanal durante desenvolvimento ativo*
*Status: DEVELOPMENT - Desenvolvimento ativo de funcionalidades avançadas Oracle*
