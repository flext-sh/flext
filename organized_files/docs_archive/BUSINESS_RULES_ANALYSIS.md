# Business Rules Analysis - Oracle WMS Singer Implementation

This document analyzes the business rules and critical functionality implemented across three Oracle WMS Singer projects that must be preserved in the modernized Singer SDK implementation.

## 1. client-b-meltano-native Project

### Core Business Rules

#### 1.1 Type Mapping Rules (type_mapping_rules.py)
- **Centralized Oracle Type Conversion**:
  - Metadata-first approach: WMS metadata types have priority over pattern matching
  - Field pattern matching for consistent DDL generation
  - Special handling for Oracle-specific types (VARCHAR2, NUMBER, TIMESTAMP)
  - Complex field patterns like `*_set` fields always get VARCHAR2(4000 CHAR)

```python
# Priority order for type conversion:
1. WMS metadata type (from API describe endpoint)
2. Field name patterns (e.g., *_id → NUMBER, *_key → VARCHAR2)
3. Sample value inference (last resort)
```

#### 1.2 Table Creation Rules (table_creator.py)
- **Field Ordering Requirements**:
  1. Primary key field first (prioritize simple 'id' over complex ones)
  2. Regular fields (sorted, excluding audit/system fields)
  3. Complex foreign key fields (_ID_KEY, _ID_URL)
  4. Mandatory audit fields (CREATE_USER, CREATE_TS, MOD_USER, MOD_TS)
  5. TK_DATE field (always last)

- **Oracle-specific DDL Generation**:
  - Composite primary key: (ID, MOD_TS)
  - Collation: USING_NLS_COMP for VARCHAR2 fields
  - Performance indexes on _ID, _KEY, and _TS fields
  - Schema discovery via WMS API is mandatory (no fallback schemas)

#### 1.3 Connection Management (connection_manager.py)
- **SSL/TCPS Connection Handling**:
  - Primary: TCPS protocol with SSL
  - Fallback: TCP protocol if TCPS fails
  - Automatic port adjustment (1522 → 1521)
  - Retry logic with configurable attempts and delays
  - Connection pooling support

### Data Transformation Rules

1. **Schema Discovery Priority**:
   - API describe endpoint → sample data → pattern inference
   - Never use hardcoded schemas

2. **Null Handling**:
   - All fields nullable except: ID, MOD_TS, TK_DATE
   - Empty strings → NULL for numeric types

3. **Boolean Conversion**:
   - Oracle NUMBER(1,0) for boolean storage
   - String values: "true"/"1"/"yes" → 1, others → 0

## 2. flext-target-oracle Project

### Core Business Rules

#### 2.1 High-Performance Sink Implementation (sinks.py)
- **Lazy Connection Pattern**:
  - No database connection until first batch arrives
  - Reduces resource usage and startup time

- **Custom Table Creation**:
  - Bypasses Singer SDK's SQLAlchemy table creation
  - Uses unified type mapping rules from client-b project
  - Maintains exact field ordering as table_creator.py

- **URL Field Filtering**:
  - Automatically excludes URL fields from schema and data
  - Filters: _URL, _ID_URL, _ID_KEY, _ID_ID suffixes

- **Load Method Support**:
  - `append-only`: Default, adds records
  - `overwrite`: Truncates table before insert
  - `upsert`: Uses Oracle MERGE for updates

- **Batch Processing**:
  - Configurable batch sizes (default 50,000 rows)
  - Parallel processing with thread pools
  - Direct path inserts with APPEND_VALUES hint

#### 2.2 Performance Optimizations
- **Oracle-specific Features**:
  - Compression (BASIC/ADVANCED)
  - Parallel DML operations
  - In-Memory column store
  - Result cache for read-heavy workloads
  - NOLOGGING for bulk operations

- **Statistics and Monitoring**:
  - Comprehensive batch tracking
  - Row count verification after operations
  - Performance metrics (records/second, processing time)
  - Failure tracking and reporting

#### 2.3 Historical Versioning
- Optional versioning with MOD_TS as version key
- Composite primary keys for historical tracking

## 3. flext-tap-oracle-wms Project

### Core Business Rules

#### 3.1 Dynamic Stream Implementation (streams.py)
- **HATEOAS Pagination**:
  - Follows next_page URLs automatically
  - Cursor-based pagination (page_mode: "sequenced")
  - Handles pagination token parsing and validation

- **Incremental Sync Logic**:
  ```
  WITH STATE: filter mod_ts >= (last_mod_ts - overlap_minutes)
  NO STATE: filter mod_ts >= (current_time - lookback_minutes)
  Default overlap: 5 minutes for data consistency
  ```

- **Full Table Sync Logic**:
  ```
  1. Start from highest ID (ORDER BY id DESC)
  2. Save lowest ID from each batch as bookmark
  3. Next sync: filter id < bookmark
  4. Continue until ID = 0
  ```

- **Request Parameter Validation**:
  - Parameter key length limits (50 chars)
  - Alphanumeric validation for security
  - Query parameter sanitization

#### 3.2 Schema Discovery (discovery.py)
- **Metadata-First Pattern**:
  1. API describe endpoint for base schema
  2. Sample data for complex object detection
  3. Pattern-based inference as fallback

- **Complex Object Flattening**:
  - FK Objects (id/key/url triplets) → separate fields
  - SET Objects → count, total, filter_params fields
  - Arrays → indexed fields or JSON storage
  - Configurable flattening depth and thresholds

- **Enhanced Sampling Strategy**:
  ```python
  # Get diverse samples to ensure all field patterns discovered
  - Initial samples (first page)
  - Samples from different orderings (id, -id, mod_ts, -mod_ts)
  - Combine unique field patterns
  ```

- **Auto-Discovery of Missing Fields**:
  - Detects fields in data not present in schema
  - Automatically adds with inferred types
  - Logs warnings for schema extensions

#### 3.3 Type Mapping (type_mapping.py)
- **Centralized Type Conversion**:
  - Shared with client-b project for consistency
  - Metadata types → Singer types → Oracle DDL
  - Pattern-based fallbacks for undocumented fields

### Authentication and Security

1. **WMS Authentication**:
   - Bearer token support
   - Basic auth fallback
   - Automatic token refresh
   - Auth headers injection

2. **SSL Configuration**:
   - Custom CA certificate support
   - SSL verification toggle
   - Certificate validation

### Error Handling Patterns

1. **Retriable vs Fatal Errors**:
   - 401/403/404: Fatal (stop extraction)
   - 429: Retriable with Retry-After
   - 500-599: Retriable (server errors)
   - JSON parse errors: Retriable

2. **Circuit Breaker Pattern**:
   - Prevents cascade failures
   - Configurable thresholds
   - Automatic recovery

## Critical Business Logic to Preserve

### 1. Data Consistency Rules
- **Incremental Sync Overlap**: Always subtract 5 minutes from last sync time
- **Timestamp Normalization**: All timestamps must have timezone (UTC default)
- **Null Handling**: Empty strings → NULL for numeric types

### 2. Oracle-Specific Requirements
- **Table Naming**: Schema.TABLE_NAME format with proper quoting
- **Field Ordering**: Must match exact order from table_creator.py
- **Composite Keys**: (ID, MOD_TS) for all tables
- **Audit Fields**: Always add CREATE_*, MOD_*, TK_DATE fields

### 3. Performance Requirements
- **Batch Sizes**: 50,000 rows default, configurable
- **Connection Pooling**: Reuse connections across batches
- **Parallel Processing**: Thread pools for large datasets
- **Direct Path Loading**: APPEND_VALUES hint for bulk inserts

### 4. Data Transformation Rules
- **FK Object Flattening**: Extract id/key fields, skip URL
- **SET Object Handling**: Extract count and metadata
- **Boolean Conversion**: String/int → Oracle NUMBER(1,0)
- **Large Text Fields**: VARCHAR2(4000) limit, CLOB for larger

### 5. Error Recovery
- **Bookmark Management**: Save progress after each successful batch
- **Transaction Boundaries**: Commit per batch, not per record
- **Verification Queries**: COUNT(*) after operations
- **Failure Tracking**: Detailed logging of failed batches

## Migration Considerations

When modernizing to Singer SDK, ensure:

1. **Preserve Type Mapping Logic**: Use centralized type_mapping_rules.py
2. **Maintain Field Ordering**: Critical for Oracle DDL compatibility
3. **Keep Lazy Connection**: Don't connect until data arrives
4. **Honor Flattening Rules**: Complex objects must flatten consistently
5. **Implement Verification**: Post-operation row counts
6. **Support All Load Methods**: append-only, overwrite, upsert
7. **Handle Oracle Limits**: 30-char identifiers, 4000-char VARCHAR2
8. **Preserve Performance**: Batch processing, parallel options

## Configuration Preservation

Key configuration options that must be maintained:

```yaml
# Connection
- default_target_schema
- max_identifier_length (30 for older Oracle)
- ssl_server_dn_match
- connection_timeout

# Performance
- batch_size_rows (default: 50000)
- parallel_threads (default: 8)
- use_direct_path
- compression_type

# Behavior
- load_method (append-only/overwrite/upsert)
- enable_historical_versioning
- force_full_table (for tap)
- incremental_overlap_minutes

# Flattening
- enable_flattening
- flatten_id_based_objects
- max_flatten_depth
```
