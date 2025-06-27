# internal.invalid.md - TARGET-ORACLE-ADVANCED PROJECT SPECIFICS

**Hierarquia**: **PROJECT-SPECIFIC**
**Projeto**: Target Oracle Advanced - Enterprise Oracle Database Loader
**Status**: DEVELOPMENT - Advanced Singer target in development
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
# Target Oracle Advanced specific configurations
export TARGET_ORACLE_HOST=oracle.enterprise.com
export TARGET_ORACLE_PORT=1521
export TARGET_ORACLE_SERVICE_NAME=ORCL
export TARGET_ORACLE_USER=target_advanced_user
export TARGET_ORACLE_PASSWORD=secure_oracle_password
export TARGET_ORACLE_DEFAULT_SCHEMA=DATAWAREHOUSE
export TARGET_ORACLE_BATCH_SIZE=50000
export TARGET_ORACLE_CONNECTION_POOL_SIZE=10
export TARGET_ORACLE_UPSERT_MODE=true
export TARGET_ORACLE_BULK_LOADING=true
export TARGET_ORACLE_PARALLEL_DEGREE=4
export TARGET_ORACLE_LOG_LEVEL=DEBUG
export TARGET_ORACLE_ENABLE_PERFORMANCE_LOGGING=false
```

---

## 🏗️ TARGET ORACLE ADVANCED ARCHITECTURE

### **Purpose & Role**

- **Enterprise Oracle Loader**: Modern Singer target for high-performance Oracle data loading
- **Advanced Loading Strategies**: Bulk loading, upsert operations, and parallel processing
- **FLX Framework Integration**: Hexagonal architecture with robust Oracle database connections
- **Performance Optimized**: Connection pooling, batch processing, and parallel loading
- **Modern Development Stack**: Python 3.13+, Singer SDK 0.45.0+, latest Oracle patterns

### **Core Advanced Components**

```python
# Target Oracle Advanced structure
src/target_oracle_advanced/
├── __init__.py          # Package initialization
├── __version__.py       # Version management
├── target.py            # Main Singer target implementation
└── sinks.py             # Advanced Oracle sinks (bulk, upsert, standard)
```

### **Enterprise Oracle Loading Features**

- **Multiple Loading Modes**: Standard insert, bulk loading, and upsert operations
- **Connection Pool Management**: Advanced Oracle connection pooling with lifecycle management
- **Parallel Loading**: Multi-threaded data loading with configurable parallelism
- **Advanced Data Types**: Full Oracle data type handling with modern type mapping
- **Performance Monitoring**: Built-in performance metrics and logging

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

# Singer target operations
target-oracle-advanced --config config.json < data.jsonl
target-oracle-advanced --config config.json --input data.jsonl
```

### **Oracle Loading Testing**

```bash
# Test Oracle connectivity and loading
echo '{"type": "RECORD", "record": {"id": 1, "name": "test"}}' | target-oracle-advanced --config config.json

# Test bulk loading mode
export TARGET_ORACLE_BULK_LOADING=true
target-oracle-advanced --config config.json --input large_dataset.jsonl

# Test upsert operations
export TARGET_ORACLE_UPSERT_MODE=true
target-oracle-advanced --config config.json --input update_data.jsonl
```

### **Performance Testing**

```bash
# Test with debug performance logging
export TARGET_ORACLE_ENABLE_PERFORMANCE_LOGGING=true
export TARGET_ORACLE_LOG_LEVEL=DEBUG
target-oracle-advanced --config config.json --input performance_test.jsonl

# Test parallel loading
export TARGET_ORACLE_PARALLEL_DEGREE=8
target-oracle-advanced --config config.json --input parallel_test.jsonl
```

---

## 🚨 PROJECT-SPECIFIC KNOWN ISSUES

### **Oracle Advanced Loading Challenges**

- **Connection Pool Scaling**: Complex connection pool management under high load
- **Large Transaction Handling**: Memory management for bulk loading operations
- **Oracle Lock Management**: Handling Oracle row and table locks during loading
- **Data Type Precision**: Oracle numeric precision and scale handling
- **Parallel Loading Conflicts**: Coordination of parallel loading threads

### **Singer SDK Advanced Considerations**

```python
# Oracle-specific Singer target advanced patterns
class OracleAdvancedTargetPatterns:
    """Advanced patterns for Oracle Singer target implementation."""

    def handle_bulk_loading_efficiently(self, records: list):
        """Implement high-performance bulk loading."""
        # Use Oracle's bulk insert capabilities
        bulk_size = min(len(records), self.config.batch_size)

        # Prepare bulk insert statement
        placeholders = ", ".join([":{}".format(i) for i in range(1, len(records[0]) + 1)])
        sql = f"INSERT INTO {self.table_name} VALUES ({placeholders})"

        # Execute bulk insert with optimal Oracle settings
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.setinputsizes(*self.get_oracle_input_sizes(records[0]))
            cursor.executemany(sql, [list(record.values()) for record in records])
            conn.commit()

    def implement_upsert_strategy(self, records: list):
        """Implement Oracle MERGE statement for upsert operations."""
        # Use Oracle MERGE for efficient upsert
        merge_sql = f"""
        MERGE INTO {self.table_name} target
        USING (
            SELECT {self.build_select_values(records)} FROM dual
        ) source ON ({self.build_join_condition()})
        WHEN MATCHED THEN
            UPDATE SET {self.build_update_clause()}
        WHEN NOT MATCHED THEN
            INSERT ({self.build_insert_columns()})
            VALUES ({self.build_insert_values()})
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(merge_sql, self.build_bind_parameters(records))
            conn.commit()

    def manage_oracle_connection_pool(self):
        """Advanced Oracle connection pool management."""
        # Configure Oracle connection pool for high throughput
        pool_config = {
            "min": 2,
            "max": self.config.connection_pool_size,
            "increment": 1,
            "timeout": 30,
            "getmode": oracledb.POOL_GETMODE_WAIT,
            "homogeneous": True,
            "ping_interval": 60
        }

        return oracledb.create_pool(
            user=self.config.user,
            password=self.config.password,
            dsn=self.build_dsn(),
            **pool_config
        )
```

### **Production Oracle Edge Cases**

```bash
# Common Oracle advanced loading issues
1. Connection Pool Exhaustion: Too many concurrent loading operations
2. Oracle Lock Timeouts: Long-running transactions causing locks
3. Memory Overflow: Large bulk operations exceeding available memory
4. Data Type Conversion: Complex Oracle type mappings failing
5. Parallel Loading Deadlocks: Multiple threads accessing same resources
```

---

## 🎯 PROJECT-SPECIFIC SUCCESS METRICS

### **Singer Protocol Advanced Compliance**

- **Loading Throughput**: >200,000 records/minute for bulk loading operations
- **Upsert Performance**: <2 seconds per 1000 record upsert operations
- **Memory Efficiency**: <1GB memory usage for unlimited data loading
- **Connection Pool Efficiency**: 95% connection pool utilization
- **Parallel Loading Scalability**: Linear performance scaling with thread count

### **Enterprise Oracle Loading Goals**

- **Database Compatibility**: Support for Oracle 19c, 21c, 23c databases
- **Loading Strategy Flexibility**: Support for insert, bulk, and upsert modes
- **Data Integrity**: 100% ACID compliance for all loading operations
- **Performance Optimization**: 20x performance improvement over basic Oracle targets
- **Production Reliability**: 99.9% successful loading rate for enterprise workloads

---

## 🔗 PROJECT-SPECIFIC INTEGRATIONS

### **Singer Ecosystem Advanced Integration**

- **Tap Compatibility**: Optimized for all Singer-compliant taps
- **Meltano Plugin**: Advanced Meltano Hub plugin with performance tuning
- **Schema Evolution**: Automatic table schema evolution and migration
- **State Management**: Advanced loading state tracking and recovery

### **PyAuto Ecosystem Integration**

- **flx-database-oracle**: Shared Oracle connection patterns and optimization
- **tap-oracle-advanced**: Perfect companion for round-trip Oracle operations
- **target-oracle-wms**: Specialized WMS version based on advanced patterns
- **oracledb-core-shared**: Shared Oracle database models and utilities

### **Enterprise Oracle Integration**

```python
# Production Oracle advanced target configuration
class ProductionOracleAdvancedTarget:
    """Production Oracle target configuration for enterprise loading."""

    # High-performance production configuration
    ENTERPRISE_CONFIG = {
        "host": "oracle-dw.enterprise.com",
        "port": 1521,
        "service_name": "DWPROD",
        "user": "target_oracle_advanced",
        "password": "${ORACLE_TARGET_PASSWORD}",

        # Performance optimizations
        "connection_pool_size": 20,
        "batch_size": 100000,
        "bulk_loading": True,
        "upsert_mode": True,
        "parallel_degree": 8,
        "connection_timeout": 120,

        # Advanced loading features
        "enable_partitioning": True,
        "partition_strategy": "hash",
        "enable_compression": True,
        "compression_level": "high",
        "enable_parallel_dml": True,

        # Enterprise schema configuration
        "default_schema": "DATAWAREHOUSE",
        "table_prefix": "STG_",
        "create_tables": True,
        "auto_evolve_schema": True,

        # Data quality and validation
        "enable_data_validation": True,
        "validation_rules": {
            "max_string_length": 4000,
            "date_format": "YYYY-MM-DD HH24:MI:SS",
            "numeric_precision": 38,
            "numeric_scale": 10
        },

        # Monitoring and logging
        "enable_performance_logging": True,
        "log_level": "INFO",
        "metrics_enabled": True,
        "export_metrics_port": 9091
    }
```

---

## 📊 PROJECT-SPECIFIC MONITORING

### **Oracle Advanced Target Metrics**

```python
# Key metrics for Oracle advanced target monitoring
TARGET_ORACLE_ADVANCED_METRICS = {
    "loading_throughput": "Records loaded per second",
    "connection_pool_utilization": "Percentage of pool connections in use",
    "bulk_operation_time": "Average bulk loading operation time",
    "upsert_operation_time": "Average upsert operation time",
    "memory_usage_efficiency": "Memory usage per loaded record",
    "parallel_loading_efficiency": "Parallel thread utilization rate",
}
```

### **Oracle Database Loading Health Monitoring**

```bash
# Comprehensive Oracle loading monitoring
target-oracle-advanced --config config.json --test-connection --detailed
target-oracle-advanced --config config.json --performance-test --records 100000
target-oracle-advanced --config config.json --validate-schema --target-table test_table
```

---

## 📋 PROJECT-SPECIFIC MAINTENANCE

### **Regular Maintenance Tasks**

- **Daily**: Monitor loading performance and connection pool health
- **Weekly**: Review loading strategies and optimize batch sizes
- **Monthly**: Update Oracle client libraries and test compatibility
- **Quarterly**: Performance benchmarking and loading strategy optimization

### **Singer SDK Advanced Updates**

```bash
# Keep Singer SDK and Oracle dependencies updated
pip install --upgrade singer-sdk oracledb sqlalchemy

# Validate Singer advanced compliance
singer-check-target --target target-oracle-advanced --config config.json
singer-validate-schema --schema target_schema.json
```

### **Emergency Procedures**

```bash
# Oracle advanced target emergency troubleshooting
1. Test Oracle connectivity: sqlplus user/password@host:port/service_name
2. Check connection pool: target-oracle-advanced --config config.json --pool-status
3. Test loading performance: target-oracle-advanced --config config.json --benchmark
4. Validate table schemas: target-oracle-advanced --config config.json --validate-tables
5. Reset connection pool: target-oracle-advanced --config config.json --reset-pool
```

---

**PROJECT SUMMARY**: Singer target avançado para Oracle Database com estratégias de loading otimizadas, processamento paralelo e integração completa com FLX framework para carregamento empresarial de dados.

**CRITICAL SUCCESS FACTOR**: Manter performance otimizada de loading e compatibilidade total com Singer SDK moderno, oferecendo carregamento Oracle enterprise com eficiência e confiabilidade máximas.

---

_Última Atualização: 2025-06-26_
_Próxima Revisão: Semanal durante desenvolvimento ativo_
_Status: DEVELOPMENT - Desenvolvimento ativo de funcionalidades avançadas Oracle_
