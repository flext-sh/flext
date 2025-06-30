# Legacy Integrations Reference Guide

> **Related Documentation:**
>
> - [Integration Examples Patterns](./integration-examples-patterns.md) - Modern integration implementation patterns
> - [Oracle Platform Resources](./oracle-platform-resources.md) - Oracle documentation and specifications
> - [Development Tools](./development-tools.md) - Testing and validation tools
> - [Architecture Migration](../migration/hexagonal-architecture-migration.md) - Legacy to modern architecture migration

This guide contains reference material from previous integration implementations and historical examples that serve as patterns for understanding Oracle WMS and OIC integration flows.

## Content Categories

### Integration Archives (.iar files)

Historical Oracle Integration Cloud packages:

- **`CRIARORDERRTV_01.00.0000.iar.zip`** - Order creation integration flow
- **`INTEGRACAOEXPEDI_*.iar`** - Expedition and shipping integration flows
- **`OCWMS_OTM_Integration.par`** - WMS to Oracle Transportation Management integration

### Extracted Integration Projects

Legacy implementation examples:

- **Oracle WMS Integrations**: Complete implementation examples
- **OIC Flow Configurations**: Integration flow design patterns
- **Connection Configurations**: Oracle system connectivity patterns
- **Data Mapping Examples**: Field-level transformation specifications

### Specialized Industry Solutions

Domain-specific integration examples:

- **`oxxo.oracle.*.par.zip`** - OXXO retail-specific Oracle integrations
- **Voice Link Integrations**: Warehouse voice picking integrations
- **Common WMS Operations**: Standard warehouse management flows

## Critical Usage Guidelines

### ⚠️ IMPORTANT: Reference Only Status

These are **legacy implementations for reference purposes only**. Do not use directly in production.

### What TO Extract from Legacy Code ✅

1. **Integration Patterns**: Understanding of system communication flows
2. **Business Logic**: Oracle WMS process understanding
3. **Data Flow Concepts**: How information moves between systems
4. **Configuration Patterns**: Connection and setup approaches
5. **Error Handling Concepts**: Resilience and failure management patterns

### What NOT to Use Directly ❌

1. **Direct Code Implementation**: Outdated patterns and practices
2. **Security Configurations**: May not meet current security standards
3. **Hard-coded Values**: Environment-specific configurations
4. **Deprecated APIs**: Oracle may have discontinued older services
5. **Monolithic Architecture**: Violates hexagonal architecture principles

## Adaptation Strategy for FLEXT Framework

### 1. Pattern Extraction Process

#### Business Logic Separation

```python
# Legacy Pattern (Monolithic)
def process_order(order_data):
    # Mixed: validation, database, external API, business logic
    validate_order(order_data)
    save_to_db(order_data)
    call_oracle_wms(order_data)
    send_notification(order_data)

# FLEXT Pattern (Hexagonal)
class OrderProcessingService:  # Domain Service
    def __init__(self, order_repo: OrderRepositoryPort, wms_client: WmsClientPort):
        self._order_repo = order_repo
        self._wms_client = wms_client

    async def process_order(self, order: Order) -> OrderResult:
        # Pure business logic
        validated_order = order.validate_business_rules()
        await self._order_repo.save(validated_order)
        wms_result = await self._wms_client.submit_order(validated_order)
        return OrderResult(order=validated_order, wms_confirmation=wms_result)
```

#### Integration Flow Modernization

```python
# Legacy: Direct Oracle API calls scattered throughout code
def legacy_inventory_sync():
    oracle_client = OracleClient(url, user, password)  # Direct dependency
    data = oracle_client.get_inventory()  # Mixed concerns
    process_inventory(data)  # Business logic embedded

# FLX: Clean separation with ports and adapters
class InventorySyncService:  # Domain Service
    def __init__(self, inventory_port: InventoryPort):
        self._inventory_port = inventory_port  # Depends on abstraction

    async def sync_inventory(self) -> SyncResult:
        # Pure business logic
        current_inventory = await self._inventory_port.get_current_inventory()
        return self._apply_business_rules(current_inventory)

class OracleInventoryAdapter:  # Infrastructure Adapter
    async def get_current_inventory(self) -> list[InventoryItem]:
        # Oracle-specific implementation details
        raw_data = await self._oracle_service.fetch_inventory()
        return [self._map_to_domain(item) for item in raw_data]
```

### 2. Architecture Mapping Patterns

#### Legacy to Hexagonal Architecture Translation

| Legacy Pattern         | Hexagonal Architecture Component       | Implementation                                               |
| ---------------------- | -------------------------------------- | ------------------------------------------------------------ |
| **Integration Flows**  | Domain Services + Outbound Adapters    | Extract business logic to services, Oracle calls to adapters |
| **Connection Configs** | Outbound Port Implementations          | Configuration becomes adapter initialization                 |
| **Data Mappings**      | Domain Value Objects + Adapters        | Business models in domain, technical mapping in adapters     |
| **Error Handling**     | Adapter Resilience + Domain Exceptions | Technical errors in adapters, business errors in domain      |
| **Validation Logic**   | Domain Entities + Value Objects        | Business validation in domain objects                        |
| **Workflow Steps**     | Domain Services + Events               | Business workflows as services, coordination via events      |

### 3. Practical Migration Examples

#### Example 1: Order Processing Flow

**Legacy Approach:**

```xml
<!-- Legacy OIC Integration -->
<integration>
  <receive>OrderCreated</receive>
  <transform>OrderToWMSFormat</transform>
  <invoke>OracleWMSService</invoke>
  <response>WMSConfirmation</response>
</integration>
```

**FLEXT Approach:**

```python
# Domain Event
class OrderCreatedEvent(DomainEvent):
    order_id: str
    customer_id: str
    items: list[OrderItem]

# Domain Service
class OrderFulfillmentService:
    async def handle_order_created(self, event: OrderCreatedEvent) -> None:
        order = await self._order_repo.find_by_id(event.order_id)
        wms_request = self._create_wms_fulfillment_request(order)
        confirmation = await self._wms_client.submit_fulfillment(wms_request)
        await self._update_order_status(order, confirmation)

# Adapter Implementation
class OracleWmsAdapter:
    async def submit_fulfillment(self, request: WmsFulfillmentRequest) -> WmsConfirmation:
        oracle_format = self._map_to_oracle_format(request)
        response = await self._wms_service.create_fulfillment(oracle_format)
        return self._map_to_domain_confirmation(response)
```

#### Example 2: Inventory Synchronization

**Legacy Pattern (Embedded in Integration):**

```python
# Legacy: Mixed concerns
def sync_inventory_legacy():
    # Database connection
    db = connect_to_oracle_db()
    # Business logic mixed with data access
    inventory_items = db.execute("SELECT * FROM inventory WHERE status = 'ACTIVE'")
    for item in inventory_items:
        # WMS API call mixed with processing
        wms_item = convert_to_wms_format(item)
        wms_client.update_inventory(wms_item)
```

**FLEXT Pattern (Separated Concerns):**

```python
# Domain Service (Business Logic)
class InventorySynchronizationService:
    async def synchronize_active_inventory(self) -> SyncResult:
        active_items = await self._inventory_repo.find_active_items()
        sync_results = []

        for item in active_items:
            # Business rule: only sync items with sufficient quantity
            if item.quantity >= self._minimum_sync_quantity:
                result = await self._wms_client.update_inventory(item)
                sync_results.append(result)

        return SyncResult(items_synced=len(sync_results), results=sync_results)

# Repository Adapter (Data Access)
class OracleInventoryRepositoryAdapter:
    async def find_active_items(self) -> list[InventoryItem]:
        query = "SELECT * FROM inventory WHERE status = 'ACTIVE'"
        raw_data = await self._db_service.execute_query(query)
        return [self._map_to_domain_item(row) for row in raw_data]

# WMS Client Adapter (External System)
class OracleWmsClientAdapter:
    async def update_inventory(self, item: InventoryItem) -> UpdateResult:
        wms_format = self._map_to_wms_format(item)
        response = await self._wms_service.update_item(wms_format)
        return self._map_update_result(response)
```

## Data Mapping Migration Patterns

### Legacy Mapping Files

The reference directory contains Oracle WMS mapping specifications:

- **Receipt Advice Mappings**: ASN, Purchase Orders, RMA processing
- **Shipment Request Mappings**: Sales and Transfer Orders
- **Inventory Transaction Mappings**: Real-time inventory updates
- **Backorder Mappings**: Partial fulfillment handling

### Modern FLEXT Mapping Approach

```python
# Legacy: Procedural mapping functions
def map_oracle_to_wms_legacy(oracle_data):
    wms_data = {}
    wms_data['item_code'] = oracle_data.get('ITEM_ID')
    wms_data['quantity'] = int(oracle_data.get('QTY', 0))
    # ... more mapping logic
    return wms_data

# FLX: Domain-driven mapping with validation
class InventoryItemMapper:
    @staticmethod
    def from_oracle_format(oracle_data: dict) -> InventoryItem:
        return InventoryItem(
            item_code=ItemCode(value=oracle_data['ITEM_ID']),
            quantity=Quantity(value=oracle_data['QTY']),
            location=LocationCode(value=oracle_data['LOCATION_ID']),
            status=InventoryStatus.from_oracle_code(oracle_data['STATUS'])
        )

    @staticmethod
    def to_wms_format(item: InventoryItem) -> dict:
        return {
            'item_code': item.item_code.value,
            'quantity': item.quantity.value,
            'location': item.location.value,
            'status': item.status.to_wms_code()
        }
```

## Error Handling Evolution

### Legacy Error Handling

```python
# Legacy: Mixed error handling
def process_order_legacy(order_data):
    try:
        # Validation mixed with processing
        if not order_data.get('customer_id'):
            raise ValueError("Customer ID required")

        # Database operation
        save_order(order_data)

        # External API call
        wms_response = call_wms_api(order_data)
        if wms_response.status != 'SUCCESS':
            # Technical error handling mixed with business logic
            rollback_order(order_data)
            raise Exception("WMS processing failed")

    except Exception as e:
        # Generic error handling
        log_error(f"Order processing failed: {e}")
        raise
```

### FLEXT Error Handling Strategy

```python
# Domain Exceptions
class OrderValidationError(DomainException):
    """Business rule validation failed."""
    pass

class OrderFulfillmentError(DomainException):
    """Order cannot be fulfilled."""
    pass

# Adapter Error Mapping
class OracleWmsAdapter:
    async def submit_order(self, order: Order) -> FulfillmentResult:
        try:
            wms_request = self._map_to_wms_format(order)
            response = await self._wms_service.submit_order(wms_request)
            return self._map_fulfillment_result(response)

        except ConnectionError as e:
            # Infrastructure error -> Adapter exception
            raise WmsConnectionError("WMS service unavailable") from e
        except ValidationError as e:
            # Business rule violation -> Domain exception
            raise OrderValidationError(f"Order validation failed: {e}") from e
        except Exception as e:
            # Unknown error -> Generic adapter error
            raise WmsAdapterError(f"Unexpected WMS error: {e}") from e

# Domain Service Error Handling
class OrderProcessingService:
    async def process_order(self, order: Order) -> ProcessingResult:
        try:
            # Business validation
            order.validate_business_rules()  # May raise OrderValidationError

            # Delegate to infrastructure
            fulfillment = await self._wms_adapter.submit_order(order)

            # Record success
            await self._order_repo.mark_as_processing(order.order_id, fulfillment.id)
            return ProcessingResult.success(fulfillment)

        except OrderValidationError:
            # Business error - re-raise as-is
            raise
        except WmsConnectionError:
            # Infrastructure error - may retry or fail gracefully
            return ProcessingResult.retry_later("WMS temporarily unavailable")
        except Exception as e:
            # Unexpected error - log and fail
            logger.error(f"Unexpected error processing order {order.order_id}: {e}")
            raise OrderProcessingError("Internal processing error") from e
```

## Configuration Migration

### Legacy Configuration Patterns

```python
# Legacy: Hard-coded configuration
WMS_URL = "https://wms.company.com/api"
WMS_USER = "integration_user"
WMS_PASSWORD = "hardcoded_password"
TIMEOUT = 30

# Legacy: Environment-specific files
# config_prod.py, config_test.py, config_dev.py
```

### FLEXT Configuration Approach

```python
# Type-safe configuration with validation
class OracleWmsConfig(BaseConfig):
    url: HttpUrl
    username: str
    password: SecretStr
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    retry_attempts: int = Field(default=3, ge=1, le=10)
    enable_ssl_verification: bool = True

    class Config:
        env_prefix = "ORACLE_WMS_"

# Adapter configuration injection
class OracleWmsAdapter:
    def __init__(self, config: OracleWmsConfig):
        self._config = config
        self._client = None

    async def _connect(self):
        self._client = OracleWmsClient(
            url=str(self._config.url),
            username=self._config.username,
            password=self._config.password.get_secret_value(),
            timeout=self._config.timeout_seconds
        )
```

## Testing Strategy Migration

### Legacy Testing Challenges

- Monolithic code difficult to unit test
- Hard-coded dependencies prevent mocking
- Integration tests require full Oracle environment
- No clear separation between business and technical logic

### FLEXT Testing Approach

```python
# Unit Testing Domain Logic
def test_order_validation():
    order = Order(
        order_id="TEST123",
        customer_id="CUST001",
        items=[OrderItem(sku="ITEM001", quantity=5)]
    )

    # Test business rules without external dependencies
    assert order.is_valid()
    assert order.total_items == 5

# Integration Testing with Mocks
@pytest.mark.asyncio
async def test_order_processing_service():
    # Mock adapters
    mock_wms = AsyncMock(spec=WmsClientPort)
    mock_repo = AsyncMock(spec=OrderRepositoryPort)

    # Configure mock behavior
    mock_wms.submit_order.return_value = FulfillmentResult.success("WMS123")

    # Test service logic
    service = OrderProcessingService(mock_wms, mock_repo)
    result = await service.process_order(valid_order)

    # Verify behavior
    assert result.success
    mock_wms.submit_order.assert_called_once()
    mock_repo.mark_as_processing.assert_called_once()

# Contract Testing with Real Infrastructure
@pytest.mark.integration
async def test_oracle_wms_adapter_integration():
    # Use test Oracle environment
    config = OracleWmsConfig(
        url="https://test-wms.company.com",
        username="test_user",
        password="test_password"
    )

    adapter = OracleWmsAdapter(config)
    await adapter.connect()

    # Test real Oracle WMS interaction
    test_order = create_test_order()
    result = await adapter.submit_order(test_order)

    assert result.confirmation_id is not None
    await adapter.disconnect()
```

## Performance Considerations

### Legacy Performance Issues

- Synchronous processing blocks threads
- No connection pooling
- Repeated Oracle API authentication
- Large data sets processed in memory

### FLEXT Performance Optimizations

```python
# Asynchronous processing
class InventoryBatchProcessor:
    async def process_inventory_updates(self, updates: list[InventoryUpdate]) -> BatchResult:
        # Process updates concurrently
        tasks = [self._process_single_update(update) for update in updates]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]

        return BatchResult(successful=len(successful), failed=len(failed))

# Connection pooling in infrastructure
class OracleWmsService:
    def __init__(self, config: OracleWmsConfig):
        self._session_pool = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=config.max_connections,
                limit_per_host=config.max_connections_per_host
            ),
            timeout=aiohttp.ClientTimeout(total=config.timeout_seconds)
        )

# Streaming for large data sets
class InventoryStreamProcessor:
    async def stream_inventory_updates(self) -> AsyncIterator[InventoryUpdate]:
        async for batch in self._inventory_repo.stream_updates(batch_size=1000):
            for update in batch:
                yield update
```

## Security Enhancement

### Legacy Security Issues

- Hard-coded credentials
- No encryption for sensitive data
- Basic authentication patterns
- No audit logging

### FLEXT Security Improvements

```python
# Secure credential management
class SecureOracleWmsAdapter:
    def __init__(self, config: OracleWmsConfig, credential_manager: CredentialManager):
        self._config = config
        self._credentials = credential_manager

    async def _authenticate(self) -> str:
        # OAuth2 or JWT authentication
        token = await self._credentials.get_access_token(
            scope="wms:read wms:write",
            audience=str(self._config.url)
        )
        return token

# Audit logging
class AuditableWmsAdapter:
    async def submit_order(self, order: Order) -> FulfillmentResult:
        audit_context = AuditContext(
            user_id=self._current_user_id,
            operation="submit_order",
            resource_id=order.order_id,
            timestamp=datetime.utcnow()
        )

        try:
            result = await self._perform_wms_submission(order)
            await self._audit_logger.log_success(audit_context, result)
            return result
        except Exception as e:
            await self._audit_logger.log_failure(audit_context, e)
            raise
```

## Migration Checklist

### Phase 1: Analysis

- [ ] Identify business logic in legacy integrations
- [ ] Extract data flow patterns
- [ ] Document error scenarios
- [ ] Map external system dependencies

### Phase 2: Design

- [ ] Define domain entities and value objects
- [ ] Design port interfaces
- [ ] Plan adapter implementations
- [ ] Create configuration schemas

### Phase 3: Implementation

- [ ] Implement domain services
- [ ] Create adapter implementations
- [ ] Add comprehensive error handling
- [ ] Implement configuration management

### Phase 4: Testing

- [ ] Unit tests for domain logic
- [ ] Integration tests with mocks
- [ ] Contract tests with real systems
- [ ] Performance testing

### Phase 5: Deployment

- [ ] Secure credential management
- [ ] Monitoring and alerting
- [ ] Gradual rollout strategy
- [ ] Rollback procedures

## Metadata

- **Legacy Coverage**: Oracle WMS integrations 2020-2023
- **Oracle Versions**: Pre-24c (various versions)
- **Migration Status**: Patterns extracted, modern implementation recommended
- **Security Status**: Legacy patterns require security review
- **Performance**: Legacy synchronous patterns need async modernization

## See Also

- [Integration Examples Patterns](./integration-examples-patterns.md) - Modern implementation patterns
- [Oracle Platform Resources](./oracle-platform-resources.md) - Current Oracle documentation
- [Development Tools](./development-tools.md) - Testing and validation tools
- [Hexagonal Architecture Guide](../architecture/UNIFIED_ARCHITECTURE_GUIDE.md) - Architecture principles
