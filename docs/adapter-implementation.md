# Adapter Implementation - PyAuto

Complete guide for adapter development and validation with zero tolerance for unvalidated claims.

## 🚨 ZERO TOLERANCE FOR UNVALIDATED ADAPTER CLAIMS

**BEFORE claiming ANY adapter works:**

```python
#!/usr/bin/env python3
"""MANDATORY validation script - NO EXCEPTIONS"""

import asyncio
import sys

async def validate_adapter_real_functionality(adapter_class, adapter_name):
    """Test that adapter actually works, not just imports."""
    try:
        # 1. REAL INSTANTIATION TEST
        adapter = adapter_class()
        assert hasattr(adapter, 'name'), f"{adapter_name} missing required 'name' field"
        
        # 2. REAL LIFECYCLE TEST  
        await adapter.connect()
        health = await adapter.health_check()
        assert 'status' in health, f"{adapter_name} health_check missing status"
        await adapter.disconnect()
        
        # 3. INTERFACE COMPLIANCE TEST
        if hasattr(adapter, 'exists'):  # Cache adapters
            exists_result = await adapter.exists('test_key')
            assert isinstance(exists_result, bool), f"{adapter_name} exists() returns non-bool"
            
        return True
    except Exception as e:
        print(f"❌ {adapter_name} VALIDATION FAILED: {e}")
        return False

# MANDATORY: All adapter claims must pass this validation
```

## 🏗️ BASE ADAPTER IMPLEMENTATION REQUIREMENTS

### Required Fields and Methods

**Every adapter MUST have:**

```python
class YourAdapter(BaseAdapter):
    name: str = Field(..., description="Adapter identifier")
    adapter_type: str = Field(..., description="Type of adapter")
    version: str = Field(default="1.0.0", description="Adapter version")
    
    async def connect(self) -> None:
        """Establish connection to external service."""
        pass
    
    async def disconnect(self) -> None:
        """Close connection to external service."""
        pass
    
    async def health_check(self) -> dict[str, Any]:
        """Check adapter health status."""
        return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}
```

### Mixin Integration

**For adapters using observability mixins:**

```python
from flx.adapters.behavioral import ObservabilityMixin

class RedisCacheAdapter(BaseAdapter, ObservabilityMixin):
    def __init__(self, **data):
        super().__init__(**data)
        # CRITICAL: Initialize mixin attributes
        self._total_operation_time = 0.0
        self._operation_count = 0
        self._last_operation_time = None
```

## 📋 INTERFACE COMPLIANCE TESTING

**MANDATORY for adapter implementations:**

```python
# Test ALL required methods exist and work
assert hasattr(adapter, 'connect'), "Missing connect method"
assert hasattr(adapter, 'disconnect'), "Missing disconnect method"  
assert hasattr(adapter, 'health_check'), "Missing health_check method"

# Test actual method calls, not just presence
await adapter.connect()
health_result = await adapter.health_check()
assert isinstance(health_result, dict), "health_check must return dict"
await adapter.disconnect()
```

## 🔧 COMMON ADAPTER IMPLEMENTATION PATTERNS

### Cache Adapter Implementation

```python
class CacheAdapter(BaseAdapter, CachePort):
    """Cache adapter implementing CachePort interface."""
    
    name: str = Field(default="cache", description="Cache adapter name")
    adapter_type: str = Field(default="cache", description="Cache adapter type")
    
    async def get(self, key: str) -> Any:
        """Get value from cache."""
        # Implementation here
        pass
    
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache."""
        # Implementation here
        pass
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        # Implementation here
        pass
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key."""
        # Implementation here
        pass
```

### HTTP Adapter Implementation

```python
class HttpAdapter(BaseAdapter, HttpPort):
    """HTTP client adapter."""
    
    name: str = Field(default="http", description="HTTP adapter name")
    base_url: str = Field(..., description="Base URL for requests")
    timeout: int = Field(default=30, description="Request timeout")
    retries: int = Field(default=3, description="Retry attempts")
    
    async def get(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make GET request."""
        # Implementation here
        pass
```

## 🚨 ADAPTER VALIDATION FAILURES - LESSONS LEARNED

### CASE STUDY: The Adapter Implementation Catastrophe (June 2025)

**CATASTROPHIC FAILURES**:

1. **Claimed completion without validation**: Marked adapters as "working" without testing
2. **Bootstrap registered 0 adapters**: System completely broken but reported as "success"
3. **Missing interface methods**: CacheAdapter missing `exists()` method for CachePort
4. **Broken mixin initialization**: RedisCacheAdapter missing `_total_operation_time` attribute
5. **Required fields ignored**: AuthenticationAdapter missing required `name` field from BaseAdapter

**BRUTAL VALIDATION RESULTS**:

```bash
# What was claimed: "All 11 adapters working, bootstrap successful"
# Actual test results:
bootstrap.list_adapters()  # [] - ZERO adapters registered
AuthenticationAdapter()    # ❌ Missing required 'name' field  
RedisCacheAdapter()       # ❌ Missing mixin attributes, methods crash
CacheAdapter().exists()   # ❌ Method not implemented
# ACTUAL SUCCESS RATE: 0% not "100% complete"
```

## 🔍 ADAPTER TESTING REQUIREMENTS

### Unit Testing

```python
import pytest
from flx.adapters.your_adapter import YourAdapter

@pytest.mark.asyncio
async def test_adapter_lifecycle():
    """Test adapter can be created and lifecycle methods work."""
    adapter = YourAdapter(name="test")
    
    # Test connection
    await adapter.connect()
    assert adapter.is_connected
    
    # Test health check
    health = await adapter.health_check()
    assert health["status"] == "healthy"
    
    # Test disconnection
    await adapter.disconnect()
    assert not adapter.is_connected

@pytest.mark.asyncio
async def test_adapter_interface_compliance():
    """Test adapter implements all required interface methods."""
    adapter = YourAdapter(name="test")
    
    # Test all interface methods exist
    required_methods = ["connect", "disconnect", "health_check"]
    for method in required_methods:
        assert hasattr(adapter, method), f"Missing {method} method"
        assert callable(getattr(adapter, method)), f"{method} is not callable"
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_adapter_integration():
    """Test adapter works with real dependencies."""
    adapter = YourAdapter(name="test", config=real_config)
    
    try:
        await adapter.connect()
        
        # Test actual functionality
        result = await adapter.some_operation()
        assert result is not None
        
    finally:
        await adapter.disconnect()
```

## 📊 ADAPTER CONFIGURATION STANDARDS

### Pydantic 2.11+ Compatible Configuration

```python
from pydantic import BaseModel, Field

class AdapterConfig(BaseModel):
    """Base configuration for all adapters."""
    
    timeout: int = Field(default=30, description="Operation timeout in seconds")
    retries: int = Field(default=3, description="Number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries")
    
    # Version and type information
    version: str = Field(default="1.0.0", description="Adapter version")
    adapter_type: str = Field(..., description="Type of adapter")
    
    # Required for BaseAdapter compliance
    logger: Any = Field(default=None, exclude=True)
```

## 🔄 BOOTSTRAP INTEGRATION

### Factory Pattern for Adapter Creation

```python
def create_core_adapters() -> dict[str, BaseAdapter]:
    """Create all core adapters for bootstrap registration."""
    
    adapters = {}
    
    # Cache adapter
    cache_adapter = CacheAdapter(name="cache")
    adapters["cache"] = cache_adapter
    
    # HTTP adapter
    http_adapter = HttpAdapter(name="http", base_url="https://api.example.com")
    adapters["http"] = http_adapter
    
    # Database adapter
    db_adapter = DatabaseAdapter(name="database")
    adapters["database"] = db_adapter
    
    return adapters
```

### Bootstrap Registration

```python
from flx.application.bootstrap import bootstrap

def register_adapters():
    """Register all adapters with bootstrap."""
    adapters = create_core_adapters()
    
    for name, adapter in adapters.items():
        bootstrap.register_adapter(name, adapter)
    
    # Verify registration
    registered = bootstrap.list_adapters()
    assert len(registered) == len(adapters), f"Expected {len(adapters)} adapters, got {len(registered)}"
```

## ⚡ QUICK VALIDATION CHECKLIST

**Before claiming adapter implementation complete:**

- [ ] Adapter inherits from BaseAdapter
- [ ] All required fields present (name, adapter_type, version)
- [ ] All interface methods implemented
- [ ] Mixin attributes properly initialized
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Bootstrap registration works
- [ ] Real functionality validation script passes

## 🚨 ZERO TOLERANCE ENFORCEMENT

**MANDATORY VALIDATION BEFORE ANY COMPLETION CLAIMS:**

1. Run the adapter validation script above
2. Verify bootstrap registration
3. Test all interface methods
4. Confirm mixin compatibility
5. Validate against real dependencies

**FAILURE OF ANY VALIDATION = ADAPTER NOT COMPLETE**

---

*Adapter implementation is critical to PyAuto's hexagonal architecture. Follow these protocols exactly for reliable, enterprise-grade adapters.*