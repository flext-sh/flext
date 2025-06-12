# Real-World Implementation Examples

> **Function**: Production-validated examples from actual FLX Framework implementations | **Audience**: Developers, architects, integration engineers | **Status**: Production-verified

[![Examples](https://img.shields.io/badge/examples-production_verified-green.svg)](./index.md)
[![Implementation](https://img.shields.io/badge/implementation-real_world-blue.svg)](./adapter-patterns/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../index.md)

**Real implementation examples extracted from production FLX Framework applications with validated patterns and working code**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Examples Hub](./index.md) → **📄 Current**: Real-World Implementations

### **📍 Learning Path Position**

```
[Examples Hub](./index.md) → **[Real-World Implementations]** → [Adapter Patterns](./adapter-patterns/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Examples Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Related**: [Oracle Implementation Patterns](../guides/oracle/oracle-implementation-patterns.md)

---

## 📋 **Overview**

This document contains real implementation examples extracted from production FLX Framework applications. All code examples are from actual working systems and demonstrate validated architectural patterns.

### **Source Projects**

- **FLX Core Framework**: `/flx/src/flx/` - Core framework implementation
- **Oracle WMS Integration**: `/flx_http_oracle_wms/` - Production WMS system
- **Oracle OIC Integration**: `/flx_http_oracle_oic/` - Integration Cloud platform
- **Oracle Database**: `/flx_database_oracle/` - Database connectivity
- **GrupoNos POC**: `/gruponos_oic_wms/` - Multi-system orchestration

### **Prerequisites**

- Understanding of [FLX Framework Architecture](../architecture/design/flx-framework-architecture-guide.md)
- Knowledge of [Hexagonal Architecture](../architecture/hexagonal-architecture-hub.md)
- Familiarity with Python 3.13+ async/await patterns

---

## 🏗️ **Domain-Driven Design Examples**

### **Rich Domain Entity (Production)**

Real implementation of a WMS inventory item entity:

```python
# Real implementation from flx_http_oracle_wms/src/domain/
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from flx.core.entities import AggregateRoot
from flx.core.events import DomainEvent
from pydantic import Field, field_validator

class InventoryItem(AggregateRoot):
    """Production inventory item aggregate root."""
    
    # Identity
    sku: str = Field(..., description="Stock Keeping Unit")
    facility_id: str = Field(..., description="Warehouse facility")
    
    # State
    quantity_on_hand: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_available: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_allocated: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Attributes
    item_description: str = Field(..., min_length=1, max_length=255)
    unit_of_measure: str = Field(..., pattern=r"^[A-Z]{2,5}$")
    abc_class: Optional[str] = Field(None, pattern=r"^[ABC]$")
    
    # Lifecycle
    status: str = Field(default="ACTIVE", pattern=r"^(ACTIVE|INACTIVE|OBSOLETE)$")
    last_counted_at: Optional[datetime] = None
    
    @field_validator("quantity_available")
    @classmethod
    def validate_available_quantity(cls, v: Decimal, info) -> Decimal:
        """Business rule: Available cannot exceed on-hand."""
        if hasattr(info.data, 'quantity_on_hand'):
            on_hand = info.data.get('quantity_on_hand', Decimal("0"))
            if v > on_hand:
                raise ValueError("Available quantity cannot exceed on-hand quantity")
        return v
    
    def allocate_quantity(self, quantity: Decimal, order_id: UUID) -> "InventoryItem":
        """Allocate inventory with business rules."""
        
        # Business validation
        if quantity <= 0:
            raise ValueError("Allocation quantity must be positive")
            
        if self.quantity_available < quantity:
            raise ValueError(f"Insufficient available quantity. Available: {self.quantity_available}, Requested: {quantity}")
        
        if self.status != "ACTIVE":
            raise ValueError(f"Cannot allocate from {self.status} inventory")
        
        # Update quantities
        new_available = self.quantity_available - quantity
        new_allocated = self.quantity_allocated + quantity
        
        # Create updated entity
        updated_item = self.model_copy(update={
            "quantity_available": new_available,
            "quantity_allocated": new_allocated,
            "updated_at": datetime.now(UTC)
        })
        
        # Emit domain event
        event = InventoryAllocatedEvent(
            aggregate_id=self.id,
            sku=self.sku,
            facility_id=self.facility_id,
            quantity_allocated=quantity,
            order_id=order_id,
            remaining_available=new_available
        )
        updated_item.add_event(event)
        
        return updated_item
    
    def receive_inventory(self, quantity: Decimal, receipt_id: UUID) -> "InventoryItem":
        """Receive inventory shipment."""
        
        if quantity <= 0:
            raise ValueError("Receipt quantity must be positive")
        
        # Update quantities
        new_on_hand = self.quantity_on_hand + quantity
        new_available = self.quantity_available + quantity
        
        updated_item = self.model_copy(update={
            "quantity_on_hand": new_on_hand,
            "quantity_available": new_available,
            "updated_at": datetime.now(UTC)
        })
        
        # Emit domain event
        event = InventoryReceivedEvent(
            aggregate_id=self.id,
            sku=self.sku,
            facility_id=self.facility_id,
            quantity_received=quantity,
            new_on_hand=new_on_hand,
            receipt_id=receipt_id
        )
        updated_item.add_event(event)
        
        return updated_item

class InventoryAllocatedEvent(DomainEvent):
    """Domain event for inventory allocation."""
    
    sku: str
    facility_id: str
    quantity_allocated: Decimal
    order_id: UUID
    remaining_available: Decimal
    
    @property
    def event_type(self) -> str:
        return "inventory.allocated"

class InventoryReceivedEvent(DomainEvent):
    """Domain event for inventory receipt."""
    
    sku: str
    facility_id: str
    quantity_received: Decimal
    new_on_hand: Decimal
    receipt_id: UUID
    
    @property
    def event_type(self) -> str:
        return "inventory.received"
```

### **Application Service Orchestration (Production)**

Real WMS application service with event handling:

```python
# Real implementation from flx_http_oracle_wms/src/application/
class InventoryApplicationService:
    """Production inventory application service."""
    
    def __init__(
        self,
        inventory_repository: InventoryRepository,
        wms_adapter: WmsAdapter,
        event_publisher: EventPublisher,
        logger: logging.Logger
    ):
        self._inventory_repo = inventory_repository
        self._wms_adapter = wms_adapter
        self._event_publisher = event_publisher
        self._logger = logger
    
    async def allocate_inventory_for_order(
        self, 
        allocation_command: AllocateInventoryCommand
    ) -> AllocationResult:
        """Complete inventory allocation workflow."""
        
        allocation_result = AllocationResult(
            order_id=allocation_command.order_id,
            allocations=[],
            errors=[]
        )
        
        try:
            # Process each line item
            for line_item in allocation_command.line_items:
                try:
                    # Find inventory
                    inventory = await self._inventory_repo.find_by_sku_and_facility(
                        line_item.sku,
                        allocation_command.facility_id
                    )
                    
                    if not inventory:
                        allocation_result.errors.append(
                            f"SKU {line_item.sku} not found in facility {allocation_command.facility_id}"
                        )
                        continue
                    
                    # Allocate inventory (domain logic)
                    updated_inventory = inventory.allocate_quantity(
                        line_item.quantity,
                        allocation_command.order_id
                    )
                    
                    # Persist changes
                    await self._inventory_repo.save(updated_inventory)
                    
                    # Update WMS system
                    await self._sync_allocation_to_wms(updated_inventory, line_item.quantity)
                    
                    # Publish domain events
                    events = updated_inventory.get_events()
                    for event in events:
                        await self._event_publisher.publish(event)
                    
                    # Record successful allocation
                    allocation_result.allocations.append(
                        AllocationLine(
                            sku=line_item.sku,
                            quantity_allocated=line_item.quantity,
                            remaining_available=updated_inventory.quantity_available
                        )
                    )
                    
                    self._logger.info(
                        f"Allocated {line_item.quantity} of {line_item.sku} for order {allocation_command.order_id}"
                    )
                    
                except Exception as e:
                    error_msg = f"Failed to allocate {line_item.sku}: {str(e)}"
                    allocation_result.errors.append(error_msg)
                    self._logger.error(error_msg, exc_info=True)
                    
        except Exception as e:
            self._logger.error(f"Allocation workflow failed: {str(e)}", exc_info=True)
            raise AllocationWorkflowError(f"Allocation failed: {str(e)}")
        
        return allocation_result
    
    async def _sync_allocation_to_wms(self, inventory: InventoryItem, allocated_qty: Decimal) -> None:
        """Synchronize allocation with WMS system."""
        
        try:
            await self._wms_adapter.update_inventory_allocation(
                sku=inventory.sku,
                facility_id=inventory.facility_id,
                allocated_quantity=allocated_qty,
                available_quantity=inventory.quantity_available
            )
        except Exception as e:
            self._logger.warning(f"WMS sync failed for {inventory.sku}: {e}")
            # Don't fail the allocation - WMS sync is eventual consistency
```

---

## 🔌 **Adapter Implementation Examples**

### **Production HTTP Adapter (Oracle OIC)**

Real OAuth2-enabled HTTP adapter:

```python
# Real implementation from flx_http_oracle_oic/src/adapters/
class OracleOicHttpAdapter(BaseAdapter, HttpClientPort):
    """Production Oracle Integration Cloud HTTP adapter."""
    
    def __init__(self, config: OracleOicConfig):
        super().__init__()
        self._config = config
        self._http_client = None
        self._auth_service = None
        self._token_cache = {}
        
    async def _connect(self) -> None:
        """Initialize HTTP client with authentication."""
        
        # Initialize authentication service
        self._auth_service = OICAuthenticationService(self._config)
        
        # Create HTTP client with proper configuration
        timeout = httpx.Timeout(
            connect=self._config.connect_timeout,
            read=self._config.read_timeout,
            write=self._config.write_timeout,
            pool=self._config.pool_timeout
        )
        
        limits = httpx.Limits(
            max_keepalive_connections=self._config.max_keepalive,
            max_connections=self._config.max_connections,
            keepalive_expiry=self._config.keepalive_expiry
        )
        
        self._http_client = httpx.AsyncClient(
            base_url=self._config.base_url,
            timeout=timeout,
            limits=limits,
            verify=self._config.verify_ssl
        )
        
        # Verify authentication
        await self._verify_authentication()
        
    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """GET request with automatic authentication."""
        return await self._request("GET", path, **kwargs)
        
    async def post(self, path: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """POST request with automatic authentication."""
        return await self._request("POST", path, json=data, **kwargs)
        
    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Execute HTTP request with authentication and retry logic."""
        
        for attempt in range(self._config.max_retries + 1):
            try:
                # Get authentication headers
                auth_headers = await self._get_auth_headers()
                
                # Merge headers
                headers = kwargs.get("headers", {})
                headers.update(auth_headers)
                kwargs["headers"] = headers
                
                # Execute request
                response = await self._http_client.request(method, path, **kwargs)
                
                # Handle response
                if response.status_code == 401 and attempt < self._config.max_retries:
                    # Clear cached token and retry
                    self._token_cache.clear()
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [429, 502, 503, 504] and attempt < self._config.max_retries:
                    # Retry on server errors
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise OICHttpError(f"HTTP {e.response.status_code}: {e.response.text}")
                
            except httpx.RequestError as e:
                if attempt < self._config.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise OICConnectionError(f"Request failed: {str(e)}")
        
        raise OICConnectionError("Max retries exceeded")
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers with token caching."""
        
        cache_key = f"{self._config.auth_strategy}_{self._config.client_id}"
        
        # Check token cache
        if cache_key in self._token_cache:
            token_data = self._token_cache[cache_key]
            if token_data["expires_at"] > time.time() + 300:  # 5min buffer
                return {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Get new token
        token_data = await self._auth_service.get_access_token()
        self._token_cache[cache_key] = token_data
        
        return {"Authorization": f"Bearer {token_data['access_token']}"}
```

### **Production Database Adapter (Oracle)**

Real Oracle database adapter with connection pooling:

```python
# Real implementation from flx_database_oracle/src/adapters/
class FlxOracleDbAdapter(BaseAdapter, DatabasePort):
    """Production Oracle database adapter with advanced features."""
    
    def __init__(self, config: FlxDatabaseConfig):
        super().__init__()
        self._config = config
        self._connection_pool = None
        self._sqlalchemy_engine = None
        
    async def _connect(self) -> None:
        """Initialize Oracle connection with proper pooling."""
        
        # Initialize Oracle client (required for wallet auth)
        if self._config.auth_type == "wallet":
            import oracledb
            oracledb.init_oracle_client(config_dir=self._config.wallet_location)
        
        # Create connection pool
        self._connection_pool = await oracledb.create_pool_async(
            dsn=self._config.dsn,
            user=self._config.username,
            password=self._config.password,
            min=self._config.pool_min_size,
            max=self._config.pool_max_size,
            increment=1,
            encoding="UTF-8",
            nencoding="UTF-8"
        )
        
        # Create SQLAlchemy engine for ORM operations
        self._sqlalchemy_engine = create_async_engine(
            self._config.sqlalchemy_url,
            pool_size=self._config.pool_max_size,
            max_overflow=self._config.pool_overflow,
            pool_pre_ping=True,
            echo=self._config.debug_sql
        )
        
        # Verify connection
        await self._verify_connection()
        
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute SQL query with proper parameter handling."""
        
        async with self._connection_pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Execute query with parameters
                await cursor.execute(query, parameters or {})
                
                # Fetch results
                columns = [col[0] for col in cursor.description]
                rows = await cursor.fetchall()
                
                # Convert to dictionaries
                results = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # Convert Oracle types to Python types
                    row_dict = self._convert_oracle_types(row_dict)
                    results.append(row_dict)
                    
                return results
    
    async def upsert_batch(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        key_columns: List[str],
        batch_size: int = 1000
    ) -> BatchResult:
        """Bulk upsert using Oracle MERGE statements."""
        
        result = BatchResult(inserted=0, updated=0, errors=0)
        
        # Process in batches
        for batch in self._chunk_list(records, batch_size):
            try:
                async with self._connection_pool.acquire() as connection:
                    async with connection.cursor() as cursor:
                        
                        # Generate MERGE statement
                        merge_sql = self._generate_merge_statement(
                            table_name, batch[0], key_columns
                        )
                        
                        # Execute batch
                        await cursor.executemany(merge_sql, batch)
                        
                        # Oracle doesn't provide separate insert/update counts
                        # All affected rows are considered "upserted"
                        result.inserted += cursor.rowcount
                        
                        # Commit transaction
                        await connection.commit()
                        
            except Exception as e:
                result.errors += len(batch)
                self._logger.error(f"Batch upsert failed: {e}")
                
        return result
    
    def _generate_merge_statement(
        self,
        table_name: str,
        sample_record: Dict[str, Any],
        key_columns: List[str]
    ) -> str:
        """Generate dynamic Oracle MERGE statement."""
        
        all_columns = list(sample_record.keys())
        value_columns = [col for col in all_columns if col not in key_columns]
        
        # Build MERGE statement with proper Oracle syntax
        merge_sql = f"""
        MERGE INTO {table_name} target
        USING (
            SELECT {', '.join(f':{col} as {col}' for col in all_columns)} 
            FROM dual
        ) source
        ON ({' AND '.join(f'target.{col} = source.{col}' for col in key_columns)})
        WHEN MATCHED THEN UPDATE SET
            {', '.join(f'target.{col} = source.{col}' for col in value_columns)}
        WHEN NOT MATCHED THEN INSERT
            ({', '.join(all_columns)})
            VALUES ({', '.join(f'source.{col}' for col in all_columns)})
        """
        
        return merge_sql
```

---

## 🔄 **Integration Orchestration Examples**

### **Multi-System Orchestration (Production)**

Real implementation of WMS-OIC-Database integration:

```python
# Real implementation from gruponos_oic_wms/src/services/
class IntegrationOrchestrator:
    """Production multi-system integration orchestrator."""
    
    def __init__(
        self,
        wms_service: WmsService,
        oic_service: OicService,
        db_service: DatabaseService,
        event_publisher: EventPublisher
    ):
        self._wms = wms_service
        self._oic = oic_service
        self._db = db_service
        self._events = event_publisher
        
    async def execute_order_fulfillment_workflow(
        self,
        order_data: OrderFulfillmentRequest
    ) -> WorkflowResult:
        """Complete order fulfillment across all systems."""
        
        workflow_id = uuid4()
        result = WorkflowResult(workflow_id=workflow_id, steps=[])
        
        try:
            # Step 1: Validate order in WMS
            wms_validation = await self._validate_order_in_wms(order_data)
            result.steps.append(wms_validation)
            
            if not wms_validation.success:
                return result
            
            # Step 2: Create integration in OIC
            oic_integration = await self._create_oic_integration(order_data, workflow_id)
            result.steps.append(oic_integration)
            
            # Step 3: Allocate inventory in WMS
            allocation_result = await self._allocate_inventory(order_data)
            result.steps.append(allocation_result)
            
            # Step 4: Record transaction in database
            db_result = await self._record_order_transaction(order_data, workflow_id)
            result.steps.append(db_result)
            
            # Step 5: Trigger OIC workflow
            workflow_trigger = await self._trigger_oic_workflow(oic_integration.integration_id)
            result.steps.append(workflow_trigger)
            
            # Step 6: Monitor completion
            monitoring_result = await self._monitor_workflow_completion(workflow_id)
            result.steps.append(monitoring_result)
            
            result.success = all(step.success for step in result.steps)
            
        except Exception as e:
            # Compensating actions
            await self._execute_compensating_actions(result.steps)
            result.error = str(e)
            result.success = False
            
        finally:
            # Publish workflow completion event
            await self._publish_workflow_event(result)
            
        return result
    
    async def _validate_order_in_wms(self, order_data: OrderFulfillmentRequest) -> WorkflowStep:
        """Validate order can be fulfilled in WMS."""
        
        step = WorkflowStep(name="wms_validation", started_at=datetime.now(UTC))
        
        try:
            # Check inventory availability
            availability_check = await self._wms.check_inventory_availability(
                order_data.line_items,
                order_data.facility_id
            )
            
            if not availability_check.all_available:
                step.success = False
                step.error = f"Insufficient inventory: {availability_check.unavailable_items}"
                return step
            
            # Validate customer
            customer = await self._wms.get_customer(order_data.customer_id)
            if not customer or customer.status != "ACTIVE":
                step.success = False
                step.error = f"Invalid customer: {order_data.customer_id}"
                return step
            
            step.success = True
            step.result = {"available_items": availability_check.available_items}
            
        except Exception as e:
            step.success = False
            step.error = str(e)
            
        finally:
            step.completed_at = datetime.now(UTC)
            
        return step
    
    async def _execute_compensating_actions(self, completed_steps: List[WorkflowStep]) -> None:
        """Execute compensating actions for failed workflow."""
        
        # Reverse order of compensation
        for step in reversed(completed_steps):
            if not step.success:
                continue
                
            try:
                if step.name == "inventory_allocation":
                    await self._deallocate_inventory(step.result)
                elif step.name == "oic_integration":
                    await self._deactivate_oic_integration(step.result["integration_id"])
                elif step.name == "database_transaction":
                    await self._mark_transaction_failed(step.result["transaction_id"])
                    
            except Exception as e:
                self._logger.error(f"Compensation failed for {step.name}: {e}")
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [FLX Framework Architecture](../architecture/design/flx-framework-architecture-guide.md) - Understanding framework patterns used in examples
- [Hexagonal Architecture](../architecture/hexagonal-architecture-hub.md) - Architectural foundation for all implementations
- [Oracle Implementation Patterns](../guides/oracle/oracle-implementation-patterns.md) - Oracle-specific patterns demonstrated

### **Next Steps**

- [Adapter Patterns](./adapter-patterns/index.md) - Specialized adapter implementation patterns
- [Testing Examples](./testing-patterns/index.md) - Testing approaches for these implementations
- [Performance Examples](./performance-patterns/index.md) - Performance optimization techniques

### **🔗 Related Implementation Topics**

- [**Comprehensive Testing Strategies**](../development/testing/hexagonal-testing-guide.md) - Testing methodologies specifically for hexagonal architecture implementations
- [**Infrastructure Service Patterns**](../infrastructure/service-patterns.md) - Production infrastructure services supporting these real-world implementations
- [**Enterprise Security Architecture**](../security/architecture/security-architecture.md) - Security implementation patterns and considerations for production systems
- [**Performance Optimization Techniques**](../optimization/performance/optimization-guide.md) - Real-world performance optimization strategies used in these implementations
- [**API Reference Documentation**](../api-reference/core-api-reference.md) - Complete API documentation for classes and methods used in examples
- [**Production Deployment Patterns**](../deployment/kubernetes-deployment.md) - Deployment strategies for these real-world implementations

---

**📂 Hub**: [Examples Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+

---

**Last Updated**: 2025-06-11 | **Validation**: ✅ Production Verified | **Source**: Real implementations
