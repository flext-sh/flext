# tap-oracle-wms Performance Tuning Guide

Optimize tap-oracle-wms for maximum throughput and efficiency when extracting data from Oracle WMS Cloud.

## Performance Baseline

### Typical Performance Metrics

| Dataset Size | Pagination Mode | Page Size | Throughput | Time |
| ------------ | --------------- | --------- | ---------- | ---- |
| 10K records  | Offset          | 100       | 500 rec/s  | 20s  |
| 10K records  | Cursor          | 1000      | 2000 rec/s | 5s   |
| 100K records | Offset          | 100       | 300 rec/s  | 5.5m |
| 100K records | Cursor          | 1000      | 1800 rec/s | 56s  |
| 1M records   | Offset          | 100       | 150 rec/s  | 1.9h |
| 1M records   | Cursor          | 1000      | 1500 rec/s | 11m  |

## Key Performance Factors

### 1. Pagination Strategy

#### Use Cursor Pagination for Large Datasets

```json
{
  "pagination_mode": "cursor",
  "page_size": 1000
}
```

**Why it's faster:**

- No expensive count queries
- Consistent performance regardless of offset
- No duplicate/missed records
- Direct index access

#### When to Use Offset Pagination

Use offset pagination only when:

- Dataset is small (<10K records)
- Need to jump to specific pages
- Require total count information
- Testing/debugging

### 2. Optimal Page Size

#### Page Size Recommendations

| Entity Type                      | Characteristics            | Recommended Page Size |
| -------------------------------- | -------------------------- | --------------------- |
| Simple entities (item, location) | Few fields, small payload  | 1000-1250             |
| Medium entities (inventory)      | Moderate fields            | 500-1000              |
| Complex entities (order_hdr)     | Many fields, relationships | 200-500               |
| Large entities (shipment)        | Very large payload         | 100-200               |

#### Dynamic Page Size

```python
def get_optimal_page_size(entity_name: str, avg_record_size: int) -> int:
    """Calculate optimal page size based on entity characteristics."""
    # Target ~5MB per page for optimal network efficiency
    target_page_bytes = 5 * 1024 * 1024

    # Calculate records that fit in target size
    calculated_size = target_page_bytes // avg_record_size

    # Apply WMS limits
    return min(calculated_size, 1250)
```

### 3. Field Selection

#### Select Only Required Fields

```json
{
  "field_selection": {
    "inventory": ["id", "item_id", "location_id", "on_hand_qty"],
    "order_hdr": ["id", "order_nbr", "status", "order_date"]
  }
}
```

**Performance impact:**

- 70% reduction in payload size
- 2-3x faster extraction
- Lower memory usage

#### Avoid Expensive Fields

Fields to avoid unless necessary:

- Large text fields (notes, descriptions)
- Binary data (attachments)
- Computed fields
- Nested relationships

### 4. Parallel Processing

#### Stream Parallelization

```json
{
  "max_parallel_streams": 5,
  "stream_parallelization_strategy": "round_robin"
}
```

**Optimal parallel streams by system size:**

- Small WMS (< 100K records): 3 streams
- Medium WMS (100K - 1M records): 5 streams
- Large WMS (> 1M records): 8-10 streams

#### Request Parallelization

```json
{
  "max_parallel_requests": 10,
  "request_queue_size": 50
}
```

### 5. Connection Pooling

```json
{
  "connection_pool": {
    "size": 20,
    "max_overflow": 10,
    "timeout": 30,
    "recycle": 3600
  }
}
```

## Advanced Optimization Techniques

### 1. Incremental Extraction

#### Optimize Replication Key

```json
{
  "replication_key_optimization": {
    "prefer_indexed_keys": true,
    "replication_key_preference": [
      "update_ts", // Usually indexed
      "modify_ts", // Alternative
      "id" // Fallback
    ]
  }
}
```

#### Smart Lookback

```python
def calculate_lookback(entity_name: str, last_sync: datetime) -> int:
    """Calculate optimal lookback period."""
    hours_since_sync = (datetime.now() - last_sync).total_seconds() / 3600

    if hours_since_sync < 1:
        return 0  # No lookback needed
    elif hours_since_sync < 24:
        return 1  # 1 day lookback
    elif hours_since_sync < 168:  # 1 week
        return 3  # 3 days lookback
    else:
        return 7  # Full week lookback
```

### 2. Query Optimization

#### Filter at Source

```json
{
  "entity_filters": {
    "inventory": {
      "status": "ACTIVE",
      "on_hand_qty__gt": 0
    }
  }
}
```

#### Use Indexed Fields

Always filter/sort on indexed fields:

- Primary keys (id)
- Foreign keys (\*\_id)
- Status fields
- Date fields (_\_ts,_\_date)

### 3. Memory Management

#### Streaming Processing

```python
class StreamingProcessor:
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.buffer = []

    async def process_record(self, record: dict):
        """Process records in batches to manage memory."""
        self.buffer.append(record)

        if len(self.buffer) >= self.batch_size:
            await self.flush_buffer()

    async def flush_buffer(self):
        """Process and clear buffer."""
        if self.buffer:
            await self.write_records(self.buffer)
            self.buffer.clear()
```

#### Memory Limits

```json
{
  "memory_management": {
    "max_memory_mb": 1024,
    "gc_threshold": 0.8,
    "buffer_size": 10000
  }
}
```

### 4. Network Optimization

#### Compression

```json
{
  "http_compression": true,
  "accepted_encodings": ["gzip", "deflate", "br"]
}
```

#### Keep-Alive

```json
{
  "http_keep_alive": true,
  "keep_alive_timeout": 30,
  "max_keep_alive_connections": 10
}
```

#### DNS Caching

```python
import socket
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_dns_resolve(hostname: str) -> str:
    """Cache DNS lookups to reduce resolution time."""
    return socket.gethostbyname(hostname)
```

## Performance Monitoring

### 1. Built-in Metrics

Enable performance metrics:

```json
{
  "metrics": {
    "enabled": true,
    "include_entity_metrics": true,
    "include_http_metrics": true,
    "log_interval_seconds": 60
  }
}
```

Sample output:

```
2024-01-15 10:30:00 - METRICS - Entity: inventory
  Records extracted: 50000
  Throughput: 1250 records/sec
  API calls: 50
  Avg response time: 0.8s
  Memory usage: 256MB
```

### 2. Custom Performance Tracking

```python
import time
from contextlib import contextmanager

class PerformanceTracker:
    def __init__(self):
        self.metrics = {}

    @contextmanager
    def track(self, operation: str):
        """Track operation performance."""
        start = time.time()
        start_memory = self.get_memory_usage()

        yield

        duration = time.time() - start
        memory_delta = self.get_memory_usage() - start_memory

        self.record_metric(operation, duration, memory_delta)

    def record_metric(self, operation: str, duration: float, memory: int):
        """Record performance metric."""
        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append({
            "duration": duration,
            "memory": memory,
            "timestamp": time.time()
        })
```

### 3. Bottleneck Identification

```python
async def identify_bottlenecks():
    """Identify performance bottlenecks."""
    timings = {}

    # Test API response time
    start = time.time()
    await test_api_connection()
    timings["api_latency"] = time.time() - start

    # Test pagination performance
    start = time.time()
    await test_pagination_speed()
    timings["pagination"] = time.time() - start

    # Test data processing
    start = time.time()
    await test_data_processing()
    timings["processing"] = time.time() - start

    # Identify bottleneck
    bottleneck = max(timings, key=timings.get)
    print(f"Primary bottleneck: {bottleneck} ({timings[bottleneck]:.2f}s)")
```

## Entity-Specific Optimization

### High-Volume Entities

#### Inventory

```json
{
  "entity_optimization": {
    "inventory": {
      "pagination_mode": "cursor",
      "page_size": 1250,
      "fields": ["id", "item_id", "location_id", "on_hand_qty"],
      "parallel_partitions": {
        "enabled": true,
        "partition_by": "location_id",
        "partitions": 10
      }
    }
  }
}
```

#### Orders

```json
{
  "entity_optimization": {
    "order_hdr": {
      "pagination_mode": "cursor",
      "page_size": 500,
      "incremental_strategy": "modified_orders_only",
      "lookback_hours": 24
    }
  }
}
```

### Complex Relationships

#### Denormalization Strategy

```json
{
  "denormalization": {
    "order_dtl": {
      "include_related": ["item__code", "item__description"],
      "cache_related": true
    }
  }
}
```

## Caching Strategies

### 1. Entity Metadata Cache

```json
{
  "cache_configuration": {
    "entity_metadata_ttl": 86400,
    "schema_cache_ttl": 3600,
    "reference_data_ttl": 7200
  }
}
```

### 2. Reference Data Cache

```python
class ReferenceDataCache:
    """Cache for frequently accessed reference data."""

    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl

    async def get_or_fetch(self, entity: str, key: str):
        """Get from cache or fetch from API."""
        cache_key = f"{entity}:{key}"

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() < entry["expires"]:
                return entry["data"]

        # Fetch from API
        data = await fetch_entity_by_key(entity, key)
        self.cache[cache_key] = {
            "data": data,
            "expires": time.time() + self.ttl
        }
        return data
```

## Production Optimization Checklist

### Pre-Production

- [ ] Profile typical data volumes
- [ ] Identify largest entities
- [ ] Test pagination modes
- [ ] Optimize field selection
- [ ] Configure parallelization
- [ ] Set up monitoring

### Initial Load

- [ ] Use cursor pagination
- [ ] Maximize page size
- [ ] Enable parallel streams
- [ ] Disable unnecessary validations
- [ ] Monitor memory usage
- [ ] Use bulk export if available

### Ongoing Sync

- [ ] Enable incremental replication
- [ ] Optimize lookback window
- [ ] Use state management
- [ ] Monitor API rate limits
- [ ] Cache reference data
- [ ] Regular performance review

## Troubleshooting Performance Issues

### Slow Extraction

1. **Check pagination mode** - Switch to cursor
2. **Increase page size** - Up to 1250
3. **Enable parallelization** - 5-10 streams
4. **Reduce fields** - Select only needed
5. **Check network** - Latency, bandwidth

### High Memory Usage

1. **Reduce page size** - Smaller batches
2. **Enable streaming** - Process incrementally
3. **Clear caches** - Periodic cleanup
4. **Reduce parallelism** - Fewer concurrent operations

### API Rate Limits

1. **Check headers** - X-RateLimit-\*
2. **Implement backoff** - Exponential retry
3. **Reduce parallelism** - Fewer streams
4. **Spread schedule** - Off-peak hours

## Performance Testing

### Load Testing Script

```python
async def performance_test(entity: str, record_count: int):
    """Test extraction performance."""
    configs = [
        {"mode": "offset", "size": 100},
        {"mode": "offset", "size": 1000},
        {"mode": "cursor", "size": 100},
        {"mode": "cursor", "size": 1000}
    ]

    results = []
    for config in configs:
        start = time.time()
        records = await extract_records(
            entity,
            pagination_mode=config["mode"],
            page_size=config["size"],
            limit=record_count
        )
        duration = time.time() - start

        results.append({
            "config": config,
            "duration": duration,
            "throughput": record_count / duration
        })

    # Print results
    print(f"\nPerformance test results for {entity}:")
    for result in results:
        print(f"Mode: {result['config']['mode']}, "
              f"Size: {result['config']['size']}, "
              f"Throughput: {result['throughput']:.0f} rec/s")
```

## Best Practices Summary

1. **Always use cursor pagination** for datasets > 10K records
2. **Maximize page size** within reason (usually 500-1250)
3. **Select only required fields** to reduce payload
4. **Enable parallel processing** for multiple entities
5. **Monitor performance metrics** continuously
6. **Cache reference data** to reduce API calls
7. **Use incremental replication** for regular syncs
8. **Test performance** with production-like data
9. **Profile before optimizing** to identify bottlenecks
10. **Document optimizations** for team knowledge
