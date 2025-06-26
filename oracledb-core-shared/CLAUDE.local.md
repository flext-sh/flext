# CLAUDE.local.md - ORACLEDB-CORE-SHARED PROJECT SPECIFICS

**Hierarquia**: **PROJECT-SPECIFIC**
**Projeto**: Oracle Database Core Shared Library - Enterprise Oracle Utilities
**Status**: PLANNING - Comprehensive Oracle database utilities library
**Framework**: Python 3.13+ + Oracle Database + Shared Utilities + Enterprise Tools
**Última Atualização**: 2025-06-26

**Referência Global**: `/home/marlonsc/CLAUDE.md` → Universal principles
**Referência Workspace**: `../CLAUDE.md` → PyAuto workspace patterns
**Referência Cross-Workspace**: `/home/marlonsc/CLAUDE.local.md` → Cross-workspace issues

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
# Oracle Core Shared specific configurations
export ORACLE_SHARED_HOST=oracle.enterprise.com
export ORACLE_SHARED_PORT=1521
export ORACLE_SHARED_SERVICE_NAME=ORCL
export ORACLE_SHARED_USER=shared_lib_user
export ORACLE_SHARED_PASSWORD=secure_shared_password
export ORACLE_SHARED_POOL_SIZE=20
export ORACLE_SHARED_POOL_MIN=5
export ORACLE_SHARED_POOL_MAX=50
export ORACLE_SHARED_TIMEOUT=30
export ORACLE_SHARED_ENABLE_ANALYTICS=true
export ORACLE_SHARED_ENABLE_LEGACY=false
export ORACLE_SHARED_LOG_LEVEL=DEBUG
```

---

## 🏗️ ORACLEDB CORE SHARED ARCHITECTURE

### **Purpose & Role**
- **Enterprise Oracle Utilities**: Comprehensive shared library for Oracle database operations
- **Cross-Project Foundation**: Common Oracle functionality for all PyAuto Oracle projects
- **Schema Management Hub**: Advanced schema analysis, comparison, and migration tools
- **Performance Optimization Engine**: SQL analysis, execution plans, and optimization utilities
- **Data Operations Platform**: ETL, validation, and bulk operation utilities

### **Core Shared Components**
```python
# Oracle Core Shared library structure
src/oracledb_core_shared/
├── __init__.py          # Main exports and public API
├── connection/          # Connection management
│   ├── config.py        # Connection configuration
│   ├── pool.py          # Connection pooling
│   └── async_client.py  # Async Oracle client
├── schema/              # Schema management utilities
│   ├── analyzer.py      # Schema analysis and introspection
│   ├── comparator.py    # Schema comparison and diff
│   ├── ddl_generator.py # DDL generation utilities
│   └── migration.py     # Migration planning and execution
├── sql/                 # SQL tools and utilities
│   ├── parser.py        # SQL parsing and analysis
│   ├── optimizer.py     # Query optimization tools
│   ├── validator.py     # SQL validation utilities
│   └── execution_plan.py # Explain plan analysis
├── data/                # Data operations
│   ├── comparator.py    # Data comparison utilities
│   ├── bulk_ops.py      # Bulk operations (insert/update/delete)
│   ├── etl.py           # ETL utilities
│   └── validator.py     # Data validation tools
├── monitoring/          # Database monitoring
│   ├── health.py        # Health checks and diagnostics
│   ├── performance.py   # Performance monitoring
│   ├── space.py         # Space management utilities
│   └── index_analysis.py # Index analysis tools
└── utils/               # Shared utilities
    ├── logging.py       # Structured logging
    ├── security.py      # Security utilities
    └── exceptions.py    # Custom exceptions
```

### **Enterprise Oracle Features**
- **Modern Driver Support**: Uses latest oracledb driver with optional cx_Oracle legacy
- **Connection Pooling**: Enterprise-grade connection pool management
- **Async Operations**: Full async/await support for high-performance applications
- **Schema Intelligence**: Complete Oracle metadata extraction and analysis
- **Migration Tools**: Database migration planning and execution utilities

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
make test-integration  # Integration tests with Oracle
make test-performance  # Performance and load tests
make lint              # Code quality checks
make format            # Code formatting

# Library development operations
python -c "from oracledb_core_shared import OracleConnection; print('Import successful')"
python -c "from oracledb_core_shared.schema import SchemaAnalyzer; print('Schema tools available')"
```

### **Oracle Utilities Testing**
```bash
# Test connection management
python -c "
from oracledb_core_shared import ConnectionConfig, OracleConnection
config = ConnectionConfig.from_env()
async with OracleConnection(config) as conn:
    result = await conn.execute('SELECT 1 FROM dual')
    print('Connection test:', result.fetchone())
"

# Test schema analysis
python -c "
from oracledb_core_shared.schema import SchemaAnalyzer
analyzer = SchemaAnalyzer(connection)
tables = await analyzer.get_tables('HR')
print('Tables found:', len(tables))
"

# Test data comparison
python -c "
from oracledb_core_shared.data import DataComparator
comparator = DataComparator(source_conn, target_conn)
diff = await comparator.compare_table('HR', 'EMPLOYEES')
print('Differences:', diff.row_count_diff)
"
```

### **Performance and Load Testing**
```bash
# Test connection pool performance
python -c "
from oracledb_core_shared.connection import ConnectionPool
pool = ConnectionPool(config, min_size=5, max_size=50)
# Run concurrent connection tests
"

# Test bulk operations performance
python -c "
from oracledb_core_shared.data import BulkOperations
bulk_ops = BulkOperations(connection)
# Test bulk insert performance
"
```

---

## 🚨 PROJECT-SPECIFIC KNOWN ISSUES

### **Oracle Shared Library Challenges**
- **Driver Compatibility**: Managing transition from cx_Oracle to oracledb driver
- **Performance Optimization**: Balancing functionality with performance across all PyAuto projects
- **Schema Complexity**: Handling diverse Oracle schema patterns across enterprise environments
- **Version Compatibility**: Supporting multiple Oracle database versions (19c, 21c, 23c)
- **Memory Management**: Efficient memory usage for large-scale operations

### **Shared Library Design Considerations**
```python
# Oracle shared library patterns
class OracleSharedLibraryPatterns:
    """Production patterns for Oracle shared library."""

    def implement_connection_pool_management(self):
        """Advanced connection pool with health monitoring."""
        from oracledb_core_shared.connection import ConnectionPool

        # Configure enterprise connection pool
        pool_config = {
            "min_size": 5,
            "max_size": 50,
            "increment": 2,
            "timeout": 30,
            "ping_interval": 60,
            "session_pool": True,
            "homogeneous": True,
            "events": True  # Enable Oracle events
        }

        pool = ConnectionPool(self.config, **pool_config)

        # Health monitoring
        pool.add_health_check(self.validate_connection_health)
        pool.add_performance_monitor(self.monitor_pool_metrics)

        return pool

    def implement_schema_analysis_caching(self, schema_name: str):
        """Intelligent caching for schema metadata."""
        from oracledb_core_shared.schema import SchemaAnalyzer

        analyzer = SchemaAnalyzer(self.connection)

        # Check cache first
        cache_key = f"schema_metadata_{schema_name}_{self.get_db_version()}"
        cached_metadata = self.cache.get(cache_key)

        if cached_metadata and not self.schema_changed_since(cached_metadata.timestamp):
            return cached_metadata

        # Analyze schema and cache results
        schema_metadata = await analyzer.analyze_schema(schema_name)
        self.cache.set(cache_key, schema_metadata, timeout=3600)

        return schema_metadata

    def implement_cross_project_utilities(self):
        """Utilities shared across all PyAuto Oracle projects."""
        # Standard Oracle connection pattern
        def get_standard_connection(config_name: str):
            config = ConnectionConfig.from_pyauto_standard(config_name)
            return OracleConnection(config)

        # Standard schema comparison
        def compare_schemas_standard(source_schema: str, target_schema: str):
            comparator = SchemaComparator(self.connection)
            return comparator.compare_schemas(source_schema, target_schema)

        # Standard bulk operations
        def bulk_load_standard(table_name: str, data: list):
            bulk_ops = BulkOperations(self.connection)
            return bulk_ops.bulk_insert(table_name, data, batch_size=10000)

        return {
            "connection": get_standard_connection,
            "schema_compare": compare_schemas_standard,
            "bulk_load": bulk_load_standard
        }
```

### **Production Oracle Edge Cases**
```bash
# Common Oracle shared library issues
1. Connection Pool Exhaustion: High-demand scenarios overwhelming pool
2. Schema Lock Conflicts: Multiple projects accessing same schema metadata
3. Memory Leaks: Long-running analysis operations not releasing resources
4. Driver Migration Issues: Compatibility problems during cx_Oracle to oracledb transition
5. Performance Degradation: Shared utilities affecting individual project performance
```

---

## 🎯 PROJECT-SPECIFIC SUCCESS METRICS

### **Shared Library Performance Goals**
- **Connection Pool Efficiency**: 95% pool utilization with minimal wait times
- **Schema Analysis Speed**: <10 seconds for complete schema analysis (1000+ objects)
- **Data Comparison Performance**: >100,000 rows/minute comparison throughput
- **Memory Efficiency**: <500MB memory usage for large-scale operations
- **Cross-Project Compatibility**: 100% compatibility across all PyAuto Oracle projects

### **Enterprise Utility Goals**
- **Code Reuse**: 80% reduction in Oracle-specific code duplication across projects
- **Performance Consistency**: Standardized performance across all Oracle operations
- **Migration Support**: Complete Oracle database migration capabilities
- **Monitoring Coverage**: 100% coverage of critical Oracle database metrics
- **Documentation Quality**: Complete API documentation with examples

---

## 🔗 PROJECT-SPECIFIC INTEGRATIONS

### **PyAuto Ecosystem Integration**
- **flx-database-oracle**: Core database adapter using shared utilities
- **tap-oracle-advanced**: Uses shared connection and schema utilities
- **target-oracle-advanced**: Uses shared bulk operations and validation
- **tap-oracle-wms / target-oracle-wms**: Uses shared Oracle connectivity
- **All Oracle projects**: Foundation for Oracle operations across PyAuto

### **Enterprise Oracle Integration**
```python
# Production Oracle shared configuration
class ProductionOracleShared:
    """Production Oracle shared library configuration."""

    # Standard PyAuto Oracle configuration
    PYAUTO_ORACLE_STANDARDS = {
        "connection_defaults": {
            "pool_size": 20,
            "pool_min": 5,
            "pool_max": 50,
            "timeout": 30,
            "ping_interval": 60,
            "retry_count": 3,
            "retry_delay": 5
        },

        "schema_analysis_defaults": {
            "include_system_objects": False,
            "include_indexes": True,
            "include_constraints": True,
            "include_triggers": True,
            "cache_metadata": True,
            "cache_timeout": 3600
        },

        "data_operations_defaults": {
            "bulk_batch_size": 10000,
            "comparison_chunk_size": 50000,
            "validation_strict_mode": True,
            "enable_parallel_operations": True,
            "max_parallel_workers": 4
        },

        "monitoring_defaults": {
            "health_check_interval": 300,  # 5 minutes
            "performance_monitoring": True,
            "slow_query_threshold": 5.0,  # seconds
            "connection_leak_detection": True
        }
    }

    # Cross-project utility exports
    SHARED_UTILITIES = {
        "connection": "oracledb_core_shared.connection",
        "schema": "oracledb_core_shared.schema",
        "data": "oracledb_core_shared.data",
        "sql": "oracledb_core_shared.sql",
        "monitoring": "oracledb_core_shared.monitoring"
    }
```

---

## 📊 PROJECT-SPECIFIC MONITORING

### **Shared Library Metrics**
```python
# Key metrics for Oracle shared library monitoring
ORACLEDB_CORE_SHARED_METRICS = {
    "connection_pool_utilization": "Connection pool usage percentage",
    "schema_analysis_duration": "Time to complete schema analysis",
    "data_comparison_throughput": "Data comparison rate (rows/minute)",
    "bulk_operation_performance": "Bulk operation throughput (ops/second)",
    "memory_usage_efficiency": "Memory usage per operation",
    "cross_project_usage": "Usage statistics across PyAuto projects",
}
```

### **Oracle Database Health Monitoring**
```bash
# Comprehensive Oracle monitoring via shared library
python -c "
from oracledb_core_shared.monitoring import HealthChecker
health = HealthChecker(connection)
status = await health.comprehensive_health_check()
print('Database health:', status.overall_score)
"
```

---

## 📋 PROJECT-SPECIFIC MAINTENANCE

### **Regular Maintenance Tasks**
- **Daily**: Monitor connection pool health and cross-project usage statistics
- **Weekly**: Review shared utility performance and optimize common operations
- **Monthly**: Update Oracle driver and validate compatibility across all projects
- **Quarterly**: Performance optimization and shared library architecture review

### **Cross-Project Coordination**
```bash
# Coordinate updates across PyAuto Oracle projects
python scripts/update_shared_library.py --validate-all-projects
python scripts/test_cross_project_compatibility.py --comprehensive

# Monitor shared library usage
python scripts/analyze_shared_library_usage.py --generate-report
```

### **Emergency Procedures**
```bash
# Oracle shared library emergency troubleshooting
1. Test base connectivity: python -c "from oracledb_core_shared import test_connection; test_connection()"
2. Validate shared utilities: python -c "from oracledb_core_shared import validate_all_utilities; validate_all_utilities()"
3. Check cross-project compatibility: python scripts/emergency_compatibility_check.py
4. Reset connection pools: python -c "from oracledb_core_shared.connection import reset_all_pools; reset_all_pools()"
5. Clear shared caches: python -c "from oracledb_core_shared import clear_all_caches; clear_all_caches()"
```

---

**PROJECT SUMMARY**: Biblioteca compartilhada empresarial para Oracle Database com utilitários avançados de conexão, schema, análise SQL e operações de dados para fundação de todos os projetos Oracle do PyAuto.

**CRITICAL SUCCESS FACTOR**: Manter biblioteca shared robusta e eficiente que serve como fundação confiável para todos os projetos Oracle do PyAuto, garantindo consistência e performance enterprise.

---

*Última Atualização: 2025-06-26*
*Próxima Revisão: Semanal durante desenvolvimento da biblioteca*
*Status: PLANNING - Planejamento de biblioteca compartilhada abrangente*
