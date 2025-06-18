# Oracle WMS API Evolution & Versioning

## Version History

Oracle WMS Cloud follows a quarterly release cycle with continuous API improvements while maintaining backward compatibility.

### Release Timeline

| Version | Release Date | API Version | Major Changes |
|---------|--------------|-------------|---------------|
| 25B | April 2025 | v10 | Data Extract API, Enhanced IBLPN APIs, Async Processing |
| 25A | January 2025 | v10 | Performance improvements, Cursor pagination |
| 24C | October 2024 | v10 | OAuth 2.0 support, Bulk operations |
| 24B | July 2024 | v10 | Enhanced filtering, Field selection |
| 24A | April 2024 | v10 | API v10 release, Standardized responses |
| 23D | January 2024 | v9 | Legacy version (deprecated) |

## API Versioning Strategy

### URL-Based Versioning

Oracle WMS uses URL path versioning:

```
https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/
                                                              ^^^
                                                          API Version
```

### Version Lifecycle

1. **Active**: Current version, full support
2. **Deprecated**: Previous version, limited support (12 months)
3. **Sunset**: End of life, no support

Current status:

- **v10**: Active (since 24A)
- **v9**: Deprecated (sunset: January 2025)
- **v8**: Sunset (no longer available)

## Major Version Changes

### Version 10 (Current)

Released with WMS 24A, v10 introduced significant improvements:

#### Standardized Response Format

```json
{
  "results": [...],
  "result_count": 1000,
  "page_count": 10,
  "page_nbr": 1,
  "hasMore": true,
  "next_page": "...",
  "previous_page": "..."
}
```

#### Enhanced Error Responses

```json
{
  "error": "ValidationError",
  "message": "Detailed error message",
  "details": {
    "field": "status",
    "value": "INVALID",
    "allowed_values": ["ACTIVE", "INACTIVE"]
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### New Features in v10

- Cursor-based pagination
- Advanced filtering operators
- Field selection and aliasing
- Bulk operations
- Async processing
- Enhanced metadata discovery

### Version 9 (Deprecated)

Key differences from v10:

- Different response structure
- Limited filtering options
- No cursor pagination
- Basic error messages
- No bulk operations

Migration example:

```python
# v9 response
{
  "items": [...],
  "total": 1000,
  "page": 1,
  "hasNext": true
}

# v10 response
{
  "results": [...],
  "result_count": 1000,
  "page_nbr": 1,
  "hasMore": true
}
```

## Feature Evolution by Release

### 25B (Latest) - April 2025

#### Data Extract API

New endpoint for large-scale data extraction:

```http
POST /entity/{entity_name}/extract
```

Features:

- Asynchronous processing
- Object storage integration
- Compression support
- Progress tracking

#### Enhanced IBLPN APIs

- Additional query parameters
- Nested entity expansion
- Performance optimizations

#### Async Status API

```http
GET /async/status/{job_id}
```

Monitor long-running operations.

### 25A - January 2025

#### Cursor Pagination Enhancement

- Improved performance for large datasets
- Consistent iteration without duplicates
- No expensive count queries

#### Query Performance

- Optimized database queries
- Index improvements
- Response time reduction (30-50%)

### 24C - October 2024

#### OAuth 2.0 Support

- Client credentials flow
- JWT tokens
- Scope-based permissions
- IDCS integration

#### Bulk Operations

```http
POST /entity/{entity_name}/bulk
```

- Create/update multiple records
- Transaction support
- Error handling per record

### 24B - July 2024

#### Advanced Filtering

New operators added:

- `__regex`: Regular expression matching
- `__icontains`: Case-insensitive contains
- `__range`: Between two values
- Negation with `!` suffix

#### Field Selection

- Select specific fields: `?fields=id,code,description`
- Nested field access: `?fields=item_id__code`
- Performance improvement for large entities

### 24A - April 2024

#### API v10 Release

Complete API redesign:

- RESTful principles
- Consistent endpoints
- Standardized responses
- Comprehensive documentation

## Backward Compatibility

### Compatibility Promise

Oracle maintains backward compatibility within major versions:

- No breaking changes in minor releases
- Additive changes only
- Deprecation warnings provided
- Migration guides for major versions

### Breaking Changes

Breaking changes only occur between major versions:

- Response structure changes
- Endpoint path changes
- Authentication method changes
- Required parameter additions

### Deprecation Policy

1. **Announcement**: 6 months before deprecation
2. **Deprecation**: Feature marked deprecated, warnings issued
3. **Sunset**: Feature removed (minimum 12 months after deprecation)

Example deprecation header:

```http
X-WMS-Deprecated: true
X-WMS-Sunset-Date: 2025-01-31
X-WMS-Alternative: Use /lgfapi/v10/entity instead
```

## Version Detection

### API Version Discovery

```python
async def discover_api_version(base_url: str) -> str:
    """Discover supported API versions."""
    # Try versions in order of preference
    versions = ["v10", "v9", "v8"]

    for version in versions:
        try:
            url = f"{base_url}/wms/lgfapi/{version}/entity"
            response = await client.get(url)
            if response.status_code == 200:
                return version
        except:
            continue

    raise Exception("No supported API version found")
```

### Version Headers

Check version in response headers:

```http
X-WMS-API-Version: 10
X-WMS-Release: 25B
X-WMS-Build: 2025.04.15.001
```

### Feature Detection

```python
async def check_feature_support(feature: str) -> bool:
    """Check if a feature is supported."""
    feature_map = {
        "cursor_pagination": lambda: check_cursor_support(),
        "bulk_operations": lambda: check_endpoint_exists("/entity/item/bulk"),
        "oauth2": lambda: check_oauth_endpoint(),
        "data_extract": lambda: check_endpoint_exists("/entity/item/extract")
    }

    if feature in feature_map:
        return await feature_map[feature]()
    return False
```

## Migration Strategies

### Version Migration Checklist

When upgrading API versions:

1. **Test in non-production first**
2. **Update response parsing**
3. **Adjust error handling**
4. **Modify pagination logic**
5. **Update authentication if needed**
6. **Test all endpoints used**
7. **Monitor for deprecation warnings**

### Response Structure Migration

```python
class ResponseAdapter:
    """Adapt responses between API versions."""

    def __init__(self, api_version: str):
        self.api_version = api_version

    def normalize_list_response(self, response: dict) -> dict:
        """Normalize list responses across versions."""
        if self.api_version == "v9":
            return {
                "results": response.get("items", []),
                "result_count": response.get("total", 0),
                "page_nbr": response.get("page", 1),
                "hasMore": response.get("hasNext", False)
            }
        return response  # v10 is already normalized
```

### Endpoint Migration

```python
class EndpointMapper:
    """Map endpoints between API versions."""

    endpoint_map = {
        "v9": {
            "entities": "/api/entities",
            "describe": "/api/entities/{entity}/schema"
        },
        "v10": {
            "entities": "/entity",
            "describe": "/entity/{entity}/describe/"
        }
    }

    def get_endpoint(self, version: str, endpoint_type: str) -> str:
        return self.endpoint_map[version][endpoint_type]
```

## Future Roadmap

### Planned Features (Subject to Change)

#### 26A (Projected)

- GraphQL API support
- WebSocket subscriptions
- Enhanced webhooks
- Real-time events

#### Long-term Vision

- Event streaming
- AI-powered insights
- Predictive analytics APIs
- IoT integration

### API Design Principles Going Forward

1. **RESTful Design**: Continue REST best practices
2. **Backward Compatibility**: Maintain within major versions
3. **Performance First**: Optimize for large-scale operations
4. **Security**: Enhanced authentication and authorization
5. **Developer Experience**: Better documentation and tools

## Version-Specific Considerations

### Handling Multiple Versions

```python
class MultiVersionWMSClient:
    """Client supporting multiple API versions."""

    def __init__(self, base_url: str, preferred_version: str = "v10"):
        self.base_url = base_url
        self.version = self.detect_version()
        self.adapter = ResponseAdapter(self.version)

    async def get_entities(self):
        """Get entities with version adaptation."""
        endpoint = self.get_versioned_endpoint("entities")
        response = await self.client.get(endpoint)
        return self.adapter.normalize_list_response(response.json())
```

### Testing Across Versions

```python
@pytest.mark.parametrize("api_version", ["v9", "v10"])
async def test_entity_list(api_version):
    """Test entity listing across API versions."""
    client = WMSClient(api_version=api_version)
    entities = await client.list_entities()
    assert len(entities) > 0
    assert all("url" in entity for entity in entities.values())
```

## Best Practices

### 1. Version Pinning

Always specify the API version explicitly:

```python
# Good
base_url = "https://instance.wms.ocs.oraclecloud.com/tenant/wms/lgfapi/v10"

# Bad - relies on default version
base_url = "https://instance.wms.ocs.oraclecloud.com/tenant/wms/lgfapi"
```

### 2. Monitor Deprecations

```python
def check_deprecation_warnings(response):
    """Check for API deprecation warnings."""
    if "X-WMS-Deprecated" in response.headers:
        sunset_date = response.headers.get("X-WMS-Sunset-Date")
        alternative = response.headers.get("X-WMS-Alternative")
        logger.warning(
            f"API deprecation warning: "
            f"Sunset date: {sunset_date}, "
            f"Alternative: {alternative}"
        )
```

### 3. Graceful Degradation

```python
async def get_data_with_fallback(entity_name: str):
    """Try modern features with fallback to legacy."""
    # Try cursor pagination (v10)
    try:
        return await get_with_cursor_pagination(entity_name)
    except FeatureNotSupportedError:
        # Fall back to offset pagination
        return await get_with_offset_pagination(entity_name)
```

### 4. Version Documentation

Always document the API version used:

```python
class WMSConfig:
    """WMS configuration.

    Tested with:
    - Oracle WMS 25B
    - API version: v10
    - Last verified: 2025-04-15
    """
    api_version = "v10"
    min_wms_version = "24A"
```

This comprehensive guide ensures smooth operation across Oracle WMS versions and prepares for future API evolution.
