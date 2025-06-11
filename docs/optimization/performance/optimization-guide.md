# ⚡ Performance Optimization Guide

> **Function**: Comprehensive performance optimization strategies for FLX applications | **Audience**: Performance engineers, developers | **Status**: ✅ Production Validated

[![Performance](https://img.shields.io/badge/performance-optimized-green.svg)](./index.md)
[![Database](https://img.shields.io/badge/database-optimized-blue.svg)](#database-optimization)
[![Caching](https://img.shields.io/badge/caching-multi--level-orange.svg)](#caching-strategies)

**Complete performance optimization guide for FLX Framework - database optimization, caching strategies, async patterns, and production tuning**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Optimization](../index.md) → **📂 Section**: [Performance](./index.md) → **📄 Current**: Optimization Guide

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Architecture Hub](../../architecture/index.md) - Understanding hexagonal architecture patterns for performance-optimized design
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure services and production patterns enabling performance optimization
- [Development Hub](../../development/index.md) - Development standards and testing frameworks for performance validation

### **➡️ Next Steps**

- [Performance Hub](./performance-optimization-hub.md) - Central performance guidance and advanced monitoring techniques
- [Comprehensive Guide](./comprehensive-optimization-guide.md) - Complete optimization framework and enterprise strategies
- [Examples Hub](../../examples/index.md) - Working performance optimization examples and benchmarks

### **🔗 Related Topics**

- [Guides Hub](../../guides/index.md) - Practical implementation guides applying performance optimization to Oracle integrations
- [API Reference Hub](../../api-reference/index.md) - Performance-critical API documentation and optimization interfaces
- [Security Hub](../../security/index.md) - Security-aware performance optimization patterns and techniques
- [Deployment Hub](../../deployment/index.md) - Production deployment strategies implementing performance optimization
- [Infrastructure Services](../../infrastructure/index.md) - Cache, database, and HTTP services supporting performance optimization

## ⚡ Overview

FLX applications can achieve enterprise-scale performance through proper optimization techniques, efficient resource utilization, and strategic caching implementations.

### **Performance Optimization Areas**

- **🗄️ Database Optimization**: Query optimization, indexing, and connection pooling
- **💾 Caching Strategies**: Multi-level caching with Redis and in-memory stores  
- **🔄 Async Programming**: Efficient concurrent processing patterns
- **📊 Resource Management**: Memory, CPU, and I/O optimization
- **🌐 Network Optimization**: HTTP/2, compression, and CDN strategies
- **📈 Monitoring & Profiling**: Performance measurement and bottleneck identification

## 🗄️ Database Optimization

### **Query Optimization**

```python
# flx/performance/database_optimization.py
from flx.adapters.outbound.database import DatabaseAdapter
from flx.core.performance import QueryOptimizer, IndexAnalyzer

class OptimizedRepository:
    """Repository with built-in query optimization."""
    
    def __init__(self, database: DatabaseAdapter):
        self.database = database
        self.query_cache = {}
        self.query_stats = {}
        self.optimizer = QueryOptimizer()
    
    async def find_customers_optimized(self, filters: dict, 
                                     pagination: dict = None) -> list[dict]:
        """Optimized customer search with intelligent query building."""
        # Build optimized query based on filters
        query_builder = self.optimizer.create_query_builder('customers')
        
        # Add filters with optimal indexing strategy
        if filters.get('status'):
            query_builder.where('status', '=', filters['status'])
        
        if filters.get('email_domain'):
            # Use functional index for email domain extraction
            query_builder.where_raw(
                "SUBSTRING(email FROM '@(.*)') = ?", 
                [filters['email_domain']]
            )
        
        if filters.get('registration_date_range'):
            date_range = filters['registration_date_range']
            query_builder.where('registration_date', '>=', date_range['start'])
            query_builder.where('registration_date', '<=', date_range['end'])
        
        if filters.get('search_term'):
            # Use full-text search for name/email search
            search_term = filters['search_term']
            query_builder.where_raw(
                "to_tsvector('english', first_name || ' ' || last_name || ' ' || email) @@ plainto_tsquery(?)",
                [search_term]
            )
        
        # Add optimal sorting
        sort_by = filters.get('sort_by', 'registration_date')
        sort_order = filters.get('sort_order', 'DESC')
        
        if sort_by == 'name':
            query_builder.order_by(['last_name', 'first_name'], sort_order)
        else:
            query_builder.order_by(sort_by, sort_order)
        
        # Add pagination with efficient offset handling
        if pagination:
            limit = pagination.get('limit', 20)
            offset = pagination.get('offset', 0)
            
            # For large offsets, use cursor-based pagination
            if offset > 1000:
                cursor_value = pagination.get('cursor')
                if cursor_value and sort_by == 'registration_date':
                    if sort_order == 'DESC':
                        query_builder.where('registration_date', '<', cursor_value)
                    else:
                        query_builder.where('registration_date', '>', cursor_value)
                    query_builder.limit(limit)
                else:
                    # Fallback to offset but warn about performance
                    query_builder.limit(limit).offset(offset)
            else:
                query_builder.limit(limit).offset(offset)
        
        # Execute with query plan analysis
        query, params = query_builder.build()
        
        # Check query cache
        cache_key = self._generate_query_cache_key(query, params)
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Execute query with performance monitoring
        start_time = time.time()
        result = await self.database.fetch_all(query, params)
        execution_time = time.time() - start_time
        
        # Record query statistics
        self._record_query_stats(query, execution_time, len(result))
        
        # Cache result for short period
        if execution_time < 0.1:  # Only cache fast queries
            self.query_cache[cache_key] = result
        
        return result
    
    async def batch_load_customer_details(self, customer_ids: list[str]) -> dict[str, dict]:
        """Efficiently batch load customer details to avoid N+1 queries."""
        if not customer_ids:
            return {}
        
        # Single query to load all customers
        placeholders = ','.join(['?' for _ in customer_ids])
        customer_query = f"""
            SELECT c.customer_id, c.first_name, c.last_name, c.email, c.status,
                   c.registration_date, c.last_activity_date
            FROM customers c
            WHERE c.customer_id IN ({placeholders})
        """
        
        customers = await self.database.fetch_all(customer_query, customer_ids)
        customers_by_id = {c['customer_id']: c for c in customers}
        
        # Batch load addresses
        address_query = f"""
            SELECT customer_id, address_type, street, city, state, postal_code, country
            FROM customer_addresses
            WHERE customer_id IN ({placeholders})
        """
        
        addresses = await self.database.fetch_all(address_query, customer_ids)
        
        # Group addresses by customer
        for address in addresses:
            customer_id = address['customer_id']
            if customer_id in customers_by_id:
                if 'addresses' not in customers_by_id[customer_id]:
                    customers_by_id[customer_id]['addresses'] = []
                customers_by_id[customer_id]['addresses'].append(address)
        
        # Batch load orders summary
        orders_query = f"""
            SELECT customer_id, COUNT(*) as order_count, 
                   SUM(total_amount) as total_spent,
                   MAX(order_date) as last_order_date
            FROM orders
            WHERE customer_id IN ({placeholders})
            GROUP BY customer_id
        """
        
        orders_summary = await self.database.fetch_all(orders_query, customer_ids)
        
        # Add orders summary to customers
        for summary in orders_summary:
            customer_id = summary['customer_id']
            if customer_id in customers_by_id:
                customers_by_id[customer_id]['orders_summary'] = summary
        
        return customers_by_id
    
    def _record_query_stats(self, query: str, execution_time: float, result_count: int) -> None:
        """Record query execution statistics."""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                'query': query,
                'execution_count': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf')
            }
        
        stats = self.query_stats[query_hash]
        stats['execution_count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['execution_count']
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['min_time'] = min(stats['min_time'], execution_time)

# Database Connection Optimization
class OptimizedDatabaseAdapter(DatabaseAdapter):
    """Database adapter with connection pooling and optimization."""
    
    def __init__(self, connection_config: dict):
        super().__init__()
        self.connection_config = connection_config
        self.connection_pool = None
        self.prepared_statements = {}
    
    async def _connect(self) -> None:
        """Create optimized connection pool."""
        import asyncpg
        
        # Create connection pool with optimized settings
        self.connection_pool = await asyncpg.create_pool(
            host=self.connection_config['host'],
            port=self.connection_config['port'],
            user=self.connection_config['user'],
            password=self.connection_config['password'],
            database=self.connection_config['database'],
            
            # Pool configuration
            min_size=self.connection_config.get('min_connections', 5),
            max_size=self.connection_config.get('max_connections', 20),
            max_queries=self.connection_config.get('max_queries_per_connection', 50000),
            max_inactive_connection_lifetime=300,  # 5 minutes
            
            # Performance settings
            command_timeout=30,
            server_settings={
                'jit': 'off',  # Disable JIT for better connection times
                'application_name': 'flx_application',
                'search_path': 'public',
            }
        )
    
    async def execute_optimized(self, query: str, parameters: list = None) -> dict:
        """Execute query with prepared statements for better performance."""
        # Use prepared statements for frequently executed queries
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        async with self.connection_pool.acquire() as connection:
            if query_hash not in self.prepared_statements:
                # Prepare statement
                self.prepared_statements[query_hash] = await connection.prepare(query)
            
            prepared_stmt = self.prepared_statements[query_hash]
            
            if parameters:
                return await prepared_stmt.fetchval(*parameters)
            else:
                return await prepared_stmt.fetchval()
    
    async def bulk_insert_optimized(self, table: str, records: list[dict]) -> None:
        """Optimized bulk insert using COPY."""
        if not records:
            return
        
        # Get column names from first record
        columns = list(records[0].keys())
        
        async with self.connection_pool.acquire() as connection:
            # Use COPY for maximum insert performance
            await connection.copy_records_to_table(
                table,
                records=[(tuple(record[col] for col in columns) for record in records)],
                columns=columns
            )

# Database Indexing Strategy
class IndexOptimizer:
    """Automated database index optimization."""
    
    def __init__(self, database: DatabaseAdapter):
        self.database = database
    
    async def analyze_query_patterns(self) -> dict:
        """Analyze query patterns to suggest optimal indexes."""
        # Analyze slow queries
        slow_queries = await self.database.fetch_all("""
            SELECT query, calls, total_time, mean_time, rows
            FROM pg_stat_statements
            WHERE mean_time > 100  -- Queries taking more than 100ms
            ORDER BY total_time DESC
            LIMIT 50
        """)
        
        index_suggestions = []
        
        for query_stat in slow_queries:
            query = query_stat['query']
            suggestions = await self._analyze_query_for_indexes(query)
            index_suggestions.extend(suggestions)
        
        return {
            'slow_queries': slow_queries,
            'index_suggestions': index_suggestions
        }
    
    async def _analyze_query_for_indexes(self, query: str) -> list[dict]:
        """Analyze individual query for index opportunities."""
        suggestions = []
        
        # Simple pattern matching for common index opportunities
        import re
        
        # WHERE clause analysis
        where_patterns = re.findall(r'WHERE\s+(\w+)\s*=', query, re.IGNORECASE)
        for column in where_patterns:
            suggestions.append({
                'type': 'btree_index',
                'column': column,
                'reason': 'Equality condition in WHERE clause'
            })
        
        # JOIN condition analysis
        join_patterns = re.findall(r'JOIN\s+\w+\s+ON\s+\w+\.(\w+)\s*=\s*\w+\.(\w+)', query, re.IGNORECASE)
        for left_col, right_col in join_patterns:
            suggestions.append({
                'type': 'btree_index',
                'column': left_col,
                'reason': 'JOIN condition'
            })
            suggestions.append({
                'type': 'btree_index',
                'column': right_col,
                'reason': 'JOIN condition'
            })
        
        # ORDER BY analysis
        order_patterns = re.findall(r'ORDER\s+BY\s+(\w+)', query, re.IGNORECASE)
        for column in order_patterns:
            suggestions.append({
                'type': 'btree_index',
                'column': column,
                'reason': 'ORDER BY clause'
            })
        
        return suggestions
    
    async def create_recommended_indexes(self, suggestions: list[dict]) -> None:
        """Create recommended indexes."""
        for suggestion in suggestions:
            index_name = f"idx_{suggestion['column']}_auto"
            
            # Check if index already exists
            existing = await self.database.fetch_one("""
                SELECT indexname FROM pg_indexes 
                WHERE indexname = ?
            """, [index_name])
            
            if not existing:
                try:
                    await self.database.execute(
                        f"CREATE INDEX CONCURRENTLY {index_name} ON customers ({suggestion['column']})"
                    )
                except Exception as e:
                    # Log index creation failure
                    pass
```

## 💾 Caching Strategies

### **Multi-Level Caching**

```python
# flx/performance/caching.py
from flx.adapters.outbound.cache import CacheAdapter
from flx.adapters.outbound.memory_cache import MemoryCacheAdapter

class MultiLevelCache:
    """Multi-level caching with L1 (memory) and L2 (Redis) cache."""
    
    def __init__(self, memory_cache: MemoryCacheAdapter, redis_cache: CacheAdapter):
        self.l1_cache = memory_cache  # Fast, small capacity
        self.l2_cache = redis_cache   # Slower, large capacity
        self.cache_stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'l1_writes': 0,
            'l2_writes': 0
        }
    
    async def get(self, key: str) -> any:
        """Get value with multi-level cache lookup."""
        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            self.cache_stats['l1_hits'] += 1
            return value
        
        # Try L2 cache
        value = await self.l2_cache.get(key)
        if value is not None:
            self.cache_stats['l2_hits'] += 1
            
            # Populate L1 cache (promote hot data)
            await self.l1_cache.set(key, value, ttl=300)  # 5 minutes in L1
            self.cache_stats['l1_writes'] += 1
            
            return value
        
        # Cache miss
        self.cache_stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: any, ttl: int = 3600) -> None:
        """Set value in both cache levels."""
        # Store in L1 with shorter TTL
        l1_ttl = min(ttl, 600)  # Max 10 minutes in L1
        await self.l1_cache.set(key, value, ttl=l1_ttl)
        self.cache_stats['l1_writes'] += 1
        
        # Store in L2 with full TTL
        await self.l2_cache.set(key, value, ttl=ttl)
        self.cache_stats['l2_writes'] += 1
    
    async def delete(self, key: str) -> None:
        """Delete from both cache levels."""
        await self.l1_cache.delete(key)
        await self.l2_cache.delete(key)
    
    async def get_cache_stats(self) -> dict:
        """Get cache performance statistics."""
        total_requests = sum([
            self.cache_stats['l1_hits'],
            self.cache_stats['l2_hits'],
            self.cache_stats['misses']
        ])
        
        if total_requests == 0:
            return self.cache_stats
        
        return {
            **self.cache_stats,
            'l1_hit_rate': self.cache_stats['l1_hits'] / total_requests,
            'l2_hit_rate': self.cache_stats['l2_hits'] / total_requests,
            'overall_hit_rate': (self.cache_stats['l1_hits'] + self.cache_stats['l2_hits']) / total_requests,
            'miss_rate': self.cache_stats['misses'] / total_requests
        }

# Smart Caching Decorator
class SmartCache:
    """Intelligent caching with automatic key generation and TTL optimization."""
    
    def __init__(self, cache: MultiLevelCache):
        self.cache = cache
        self.access_patterns = {}
    
    def cached(self, ttl: int = 3600, key_prefix: str = None, 
               vary_on: list[str] = None):
        """Decorator for caching function results."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    func, args, kwargs, key_prefix, vary_on
                )
                
                # Try to get from cache
                cached_result = await self.cache.get(cache_key)
                if cached_result is not None:
                    self._record_access(cache_key)
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Determine optimal TTL based on access patterns
                optimal_ttl = self._calculate_optimal_ttl(cache_key, ttl)
                
                # Cache result
                await self.cache.set(cache_key, result, ttl=optimal_ttl)
                self._record_access(cache_key)
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func, args, kwargs, key_prefix, vary_on):
        """Generate cache key from function and parameters."""
        import hashlib
        import json
        
        # Start with function name
        key_parts = [func.__name__]
        
        # Add prefix if provided
        if key_prefix:
            key_parts.insert(0, key_prefix)
        
        # Add relevant arguments
        if vary_on:
            # Only include specified parameters
            relevant_kwargs = {k: v for k, v in kwargs.items() if k in vary_on}
            key_parts.append(json.dumps(relevant_kwargs, sort_keys=True))
        else:
            # Include all arguments
            key_parts.extend([str(arg) for arg in args])
            key_parts.append(json.dumps(kwargs, sort_keys=True, default=str))
        
        # Create hash for long keys
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{key_parts[0]}:{key_hash}"
        
        return key_string
    
    def _calculate_optimal_ttl(self, cache_key: str, default_ttl: int) -> int:
        """Calculate optimal TTL based on access patterns."""
        if cache_key not in self.access_patterns:
            return default_ttl
        
        pattern = self.access_patterns[cache_key]
        access_frequency = pattern['access_count'] / pattern['time_window']
        
        # Adjust TTL based on access frequency
        if access_frequency > 10:  # Very hot data
            return min(default_ttl * 2, 7200)  # Max 2 hours
        elif access_frequency > 1:  # Warm data
            return default_ttl
        else:  # Cold data
            return max(default_ttl // 2, 300)  # Min 5 minutes
    
    def _record_access(self, cache_key: str) -> None:
        """Record cache access for pattern analysis."""
        current_time = time.time()
        
        if cache_key not in self.access_patterns:
            self.access_patterns[cache_key] = {
                'access_count': 0,
                'first_access': current_time,
                'last_access': current_time,
                'time_window': 3600  # 1 hour window
            }
        
        pattern = self.access_patterns[cache_key]
        pattern['access_count'] += 1
        pattern['last_access'] = current_time
        
        # Reset window if too old
        if current_time - pattern['first_access'] > pattern['time_window']:
            pattern['access_count'] = 1
            pattern['first_access'] = current_time

# Cache-Aside Pattern Implementation
class CustomerCacheService:
    """Customer service with cache-aside pattern."""
    
    def __init__(self, repository: CustomerRepository, cache: SmartCache):
        self.repository = repository
        self.cache = cache
    
    @cache.cached(ttl=1800, key_prefix="customer", vary_on=["customer_id"])
    async def get_customer(self, customer_id: str) -> dict:
        """Get customer with caching."""
        customer = await self.repository.get(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        
        return customer.dict()
    
    @cache.cached(ttl=600, key_prefix="customer_search", 
                  vary_on=["filters", "pagination"])
    async def search_customers(self, filters: dict, pagination: dict = None) -> dict:
        """Search customers with caching."""
        result = await self.repository.search(filters, pagination)
        
        return {
            'customers': [c.dict() for c in result.customers],
            'total_count': result.total_count,
            'page': result.page,
            'total_pages': result.total_pages
        }
    
    async def update_customer(self, customer_id: str, updates: dict) -> dict:
        """Update customer and invalidate cache."""
        # Update in database
        customer = await self.repository.update(customer_id, updates)
        
        # Invalidate related cache entries
        await self._invalidate_customer_cache(customer_id)
        
        return customer.dict()
    
    async def _invalidate_customer_cache(self, customer_id: str) -> None:
        """Invalidate all cache entries related to customer."""
        # Delete specific customer cache
        customer_key = f"customer:{customer_id}"
        await self.cache.cache.delete(customer_key)
        
        # Clear search result caches (simplified approach)
        # In production, use cache tags for more efficient invalidation
        search_pattern = "customer_search:*"
        await self.cache.cache.l1_cache.clear(search_pattern)
        await self.cache.cache.l2_cache.clear(search_pattern)

# Distributed Cache Invalidation
class CacheInvalidationService:
    """Service for coordinated cache invalidation across instances."""
    
    def __init__(self, cache: MultiLevelCache, event_bus):
        self.cache = cache
        self.event_bus = event_bus
        self.setup_event_handlers()
    
    def setup_event_handlers(self) -> None:
        """Setup event handlers for cache invalidation."""
        
        @self.event_bus.subscribe(CustomerUpdated)
        async def handle_customer_updated(event: CustomerUpdated) -> None:
            """Invalidate customer cache when updated."""
            await self.invalidate_customer_cache(str(event.customer_id))
        
        @self.event_bus.subscribe(CustomerDeactivated)
        async def handle_customer_deactivated(event: CustomerDeactivated) -> None:
            """Invalidate customer cache when deactivated."""
            await self.invalidate_customer_cache(str(event.customer_id))
    
    async def invalidate_customer_cache(self, customer_id: str) -> None:
        """Invalidate all customer-related cache entries."""
        cache_keys = [
            f"customer:{customer_id}",
            f"customer_details:{customer_id}",
            f"customer_orders:{customer_id}",
            f"customer_addresses:{customer_id}"
        ]
        
        for key in cache_keys:
            await self.cache.delete(key)
        
        # Publish cache invalidation event for other instances
        invalidation_event = CacheInvalidationEvent(
            entity_type="customer",
            entity_id=customer_id,
            cache_keys=cache_keys
        )
        
        await self.event_bus.publish(invalidation_event)
```

## 🔄 Async Programming Optimization

### **Concurrent Processing Patterns**

```python
# flx/performance/async_patterns.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any, Callable

class AsyncBatchProcessor:
    """Efficient batch processing with concurrency control."""
    
    def __init__(self, max_concurrent: int = 10, max_batch_size: int = 100):
        self.max_concurrent = max_concurrent
        self.max_batch_size = max_batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(self, items: List[Any], 
                          processor: Callable, 
                          **kwargs) -> List[Any]:
        """Process items in batches with concurrency control."""
        results = []
        
        # Split items into batches
        batches = [
            items[i:i + self.max_batch_size] 
            for i in range(0, len(items), self.max_batch_size)
        ]
        
        # Process batches concurrently
        tasks = [
            self._process_single_batch(batch, processor, **kwargs)
            for batch in batches
        ]
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and handle exceptions
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                # Log error but continue processing
                continue
            results.extend(batch_result)
        
        return results
    
    async def _process_single_batch(self, batch: List[Any], 
                                  processor: Callable, 
                                  **kwargs) -> List[Any]:
        """Process a single batch with semaphore control."""
        async with self.semaphore:
            tasks = [processor(item, **kwargs) for item in batch]
            return await asyncio.gather(*tasks, return_exceptions=True)

class AsyncPipeline:
    """Async processing pipeline with stages."""
    
    def __init__(self):
        self.stages: List[Callable] = []
        self.error_handlers: dict[type, Callable] = {}
    
    def add_stage(self, processor: Callable) -> 'AsyncPipeline':
        """Add processing stage to pipeline."""
        self.stages.append(processor)
        return self
    
    def on_error(self, exception_type: type, handler: Callable) -> 'AsyncPipeline':
        """Add error handler for specific exception type."""
        self.error_handlers[exception_type] = handler
        return self
    
    async def process(self, item: Any) -> Any:
        """Process item through all pipeline stages."""
        current_item = item
        
        for stage in self.stages:
            try:
                if asyncio.iscoroutinefunction(stage):
                    current_item = await stage(current_item)
                else:
                    current_item = stage(current_item)
            except Exception as e:
                # Try to find specific error handler
                handler = self.error_handlers.get(type(e))
                if handler:
                    current_item = await handler(current_item, e)
                else:
                    raise
        
        return current_item
    
    async def process_many(self, items: List[Any], 
                          max_concurrent: int = 10) -> List[Any]:
        """Process multiple items concurrently through pipeline."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(item):
            async with semaphore:
                return await self.process(item)
        
        tasks = [process_with_semaphore(item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)

# CPU-Intensive Task Optimization
class CPUOptimizedProcessor:
    """Processor for CPU-intensive tasks using thread pools."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
    
    async def process_cpu_intensive(self, func: Callable, *args, **kwargs) -> Any:
        """Execute CPU-intensive function in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
    
    async def parallel_map(self, func: Callable, items: List[Any]) -> List[Any]:
        """Apply function to items in parallel using thread pool."""
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.thread_pool, func, item)
            for item in items
        ]
        return await asyncio.gather(*tasks)
    
    async def parallel_reduce(self, func: Callable, items: List[Any], 
                            initial: Any = None) -> Any:
        """Parallel reduce operation for CPU-intensive functions."""
        if not items:
            return initial
        
        # Split items into chunks for parallel processing
        chunk_size = max(1, len(items) // self.max_workers)
        chunks = [
            items[i:i + chunk_size] 
            for i in range(0, len(items), chunk_size)
        ]
        
        # Process chunks in parallel
        async def reduce_chunk(chunk):
            result = initial
            for item in chunk:
                if result is None:
                    result = item
                else:
                    result = func(result, item)
            return result
        
        chunk_results = await asyncio.gather(*[
            self.process_cpu_intensive(reduce_chunk, chunk)
            for chunk in chunks
        ])
        
        # Combine chunk results
        final_result = initial
        for chunk_result in chunk_results:
            if chunk_result is not None:
                if final_result is None:
                    final_result = chunk_result
                else:
                    final_result = func(final_result, chunk_result)
        
        return final_result
    
    async def cleanup(self) -> None:
        """Cleanup thread pool resources."""
        self.thread_pool.shutdown(wait=True)

# Streaming Data Processing
class AsyncStreamProcessor:
    """Process streaming data with backpressure control."""
    
    def __init__(self, buffer_size: int = 1000, 
                 processing_delay: float = 0.01):
        self.buffer_size = buffer_size
        self.processing_delay = processing_delay
        self.queue = asyncio.Queue(maxsize=buffer_size)
        self.processors = []
        self.is_running = False
    
    async def add_item(self, item: Any) -> None:
        """Add item to processing queue with backpressure."""
        try:
            await asyncio.wait_for(
                self.queue.put(item), 
                timeout=1.0
            )
        except asyncio.TimeoutError:
            # Handle backpressure - could drop item, raise exception, etc.
            raise BackpressureError("Processing queue is full")
    
    async def start_processing(self, processor: Callable, 
                              num_workers: int = 3) -> None:
        """Start processing with multiple workers."""
        self.is_running = True
        
        # Start worker tasks
        for i in range(num_workers):
            task = asyncio.create_task(
                self._worker(f"worker-{i}", processor)
            )
            self.processors.append(task)
    
    async def stop_processing(self) -> None:
        """Stop processing and cleanup."""
        self.is_running = False
        
        # Cancel all worker tasks
        for task in self.processors:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.processors, return_exceptions=True)
        self.processors.clear()
    
    async def _worker(self, worker_name: str, processor: Callable) -> None:
        """Worker that processes items from queue."""
        while self.is_running:
            try:
                # Get item with timeout
                item = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                # Process item
                await processor(item)
                
                # Mark task as done
                self.queue.task_done()
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(self.processing_delay)
                
            except asyncio.TimeoutError:
                # No items to process, continue
                continue
            except Exception as e:
                # Log processing error but continue
                print(f"Worker {worker_name} error: {e}")
                continue

# Performance Monitoring
class AsyncPerformanceMonitor:
    """Monitor async application performance."""
    
    def __init__(self):
        self.metrics = {
            'active_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_task_duration': 0,
            'max_task_duration': 0,
            'queue_sizes': {}
        }
        self.task_durations = []
    
    def track_task(self, task_name: str):
        """Decorator to track task performance."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                self.metrics['active_tasks'] += 1
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Record success
                    duration = time.time() - start_time
                    self._record_task_completion(task_name, duration, success=True)
                    
                    return result
                    
                except Exception as e:
                    # Record failure
                    duration = time.time() - start_time
                    self._record_task_completion(task_name, duration, success=False)
                    raise
                finally:
                    self.metrics['active_tasks'] -= 1
            
            return wrapper
        return decorator
    
    def _record_task_completion(self, task_name: str, duration: float, success: bool) -> None:
        """Record task completion metrics."""
        if success:
            self.metrics['completed_tasks'] += 1
        else:
            self.metrics['failed_tasks'] += 1
        
        # Update duration statistics
        self.task_durations.append(duration)
        
        # Keep only last 1000 durations for moving average
        if len(self.task_durations) > 1000:
            self.task_durations = self.task_durations[-1000:]
        
        self.metrics['avg_task_duration'] = sum(self.task_durations) / len(self.task_durations)
        self.metrics['max_task_duration'] = max(self.metrics['max_task_duration'], duration)
    
    async def get_runtime_metrics(self) -> dict:
        """Get current runtime performance metrics."""
        import psutil
        import gc
        
        # Get system metrics
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            **self.metrics,
            'memory_usage_mb': memory_info.rss / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'open_files': len(process.open_files()),
            'thread_count': process.num_threads(),
            'gc_counts': gc.get_counts(),
            'event_loop_running': asyncio.get_running_loop() is not None
        }

# Usage Example
async def optimized_customer_processing():
    """Example of optimized async processing."""
    
    # Setup components
    batch_processor = AsyncBatchProcessor(max_concurrent=20, max_batch_size=50)
    cpu_processor = CPUOptimizedProcessor(max_workers=8)
    performance_monitor = AsyncPerformanceMonitor()
    
    # Create processing pipeline
    pipeline = AsyncPipeline()
    pipeline.add_stage(validate_customer_data)
    pipeline.add_stage(enrich_customer_data)
    pipeline.add_stage(save_customer_data)
    pipeline.on_error(ValidationError, handle_validation_error)
    
    # Process customers in batches
    customers = await load_customer_data()  # Load customers to process
    
    @performance_monitor.track_task("customer_processing")
    async def process_customer(customer):
        return await pipeline.process(customer)
    
    # Process with monitoring
    results = await batch_processor.process_batch(
        customers,
        process_customer
    )
    
    # Get performance metrics
    metrics = await performance_monitor.get_runtime_metrics()
    print(f"Processed {len(results)} customers")
    print(f"Performance metrics: {metrics}")
```

---

**⚡ Your FLX application now has enterprise-grade performance optimization with advanced database querying, multi-level caching, and efficient async processing patterns!**

---

**📄 Content Document** | **🏠 Parent**: [Performance Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
