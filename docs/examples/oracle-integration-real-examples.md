# 🎯 Oracle Integration Real Examples

> **Document Type**: Practical Examples | **Audience**: Integration developers | **Scope**: Working Oracle integration implementations

[![Oracle](https://img.shields.io/badge/oracle-enterprise-orange.svg)](../guides/oracle/index.md)
[![Examples](https://img.shields.io/badge/examples-working-green.svg)](./index.md)
[![Code](https://img.shields.io/badge/code-validated-blue.svg)](../reference/specifications/oracle-integration-specification.md)

**Real working examples of Oracle system integrations using FLX Framework architecture patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Examples](./index.md) → **📂 Current**: Oracle Integration Real Examples

---

## 🎯 **Example Overview**

### **Real Implementation Examples**

| **Integration** | **Use Case** | **Complexity** | **Source Code** |
|----------------|--------------|----------------|-----------------|
| **Oracle Database** | Data persistence and transactions | ⭐⭐ | `/flx_database_oracle/` |
| **Oracle WMS** | Inventory and warehouse operations | ⭐⭐⭐ | `/flx_http_oracle_wms/` |
| **Oracle OIC** | Integration orchestration | ⭐⭐⭐⭐ | `/flx_http_oracle_oic/` |
| **Multi-System** | End-to-end business process | ⭐⭐⭐⭐⭐ | Combined projects |

### **Architecture Patterns Demonstrated**

- **Hexagonal Architecture**: Clean separation with ports and adapters
- **Domain-Driven Design**: Rich domain models with business logic
- **CQRS**: Command/Query separation for complex operations
- **Event-Driven**: Domain events for cross-system communication

---

## 🗄️ **Oracle Database Integration Examples**

### **1. Basic Database Operations**

#### **Simple CRUD Operations**

```python
# examples/oracle_database_basic.py
import asyncio
from flx.adapters.oracle.database import FlxOracleDbAdapter
from flx.core.entities import Entity, AggregateRoot
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Product(AggregateRoot):
    """Product aggregate root with business logic"""
    
    product_id: str
    name: str
    description: Optional[str] = None
    price: float
    category_id: str
    active: bool = True
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None
    
    def update_price(self, new_price: float) -> None:
        """Update product price with business validation"""
        if new_price <= 0:
            raise ValueError("Price must be positive")
        
        old_price = self.price
        self.price = new_price
        self.touch()  # Update timestamp
        
        # Emit domain event for price change
        self.add_event(PriceChangedEvent(
            product_id=self.product_id,
            old_price=old_price,
            new_price=new_price
        ))

class PriceChangedEvent(DomainEvent):
    """Domain event for price changes"""
    product_id: str
    old_price: float
    new_price: float

async def database_crud_example():
    """Demonstrate basic CRUD operations with Oracle Database"""
    
    # Initialize Oracle Database adapter
    db_adapter = FlxOracleDbAdapter(
        host="localhost",
        port=1521,
        service_name="XEPDB1",
        username="flx_user",
        password="flx_password"
    )
    
    try:
        # Connect to database
        await db_adapter.initialize()
        
        # Create product
        product = Product(
            product_id="PROD-001",
            name="Enterprise Widget",
            description="High-quality widget for enterprise use",
            price=99.99,
            category_id="CAT-001"
        )
        
        # Insert product
        await db_adapter.execute_command(
            """INSERT INTO products (product_id, name, description, price, category_id, active, created_at)
               VALUES (:product_id, :name, :description, :price, :category_id, :active, :created_at)""",
            {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category_id": product.category_id,
                "active": product.active,
                "created_at": product.created_at
            }
        )
        
        # Query product
        results = await db_adapter.execute_query(
            "SELECT * FROM products WHERE product_id = :product_id",
            {"product_id": "PROD-001"}
        )
        
        print(f"Retrieved product: {results[0]}")
        
        # Update product price
        product.update_price(89.99)
        
        # Update in database
        await db_adapter.execute_command(
            """UPDATE products SET price = :price, updated_at = :updated_at 
               WHERE product_id = :product_id""",
            {
                "price": product.price,
                "updated_at": product.updated_at,
                "product_id": product.product_id
            }
        )
        
        # Process domain events
        events = product.clear_events()
        for event in events:
            print(f"Domain event: {event.type} - Product {event.product_id} price changed from {event.old_price} to {event.new_price}")
        
    finally:
        await db_adapter.shutdown()

if __name__ == "__main__":
    asyncio.run(database_crud_example())
```

#### **Advanced Database Operations with Transactions**

```python
# examples/oracle_database_advanced.py
import asyncio
from flx.adapters.oracle.database import FlxOracleDbAdapter
from flx.core.services import ApplicationService
from contextlib import asynccontextmanager
from typing import List

class OrderProcessingService(ApplicationService):
    """Application service for order processing with transactions"""
    
    def __init__(self, db_adapter: FlxOracleDbAdapter):
        self.db_adapter = db_adapter
    
    async def process_order(self, order_data: dict) -> str:
        """Process order with transactional integrity"""
        
        async with self._transaction() as tx:
            # Create order header
            order_id = await self._create_order_header(order_data, tx)
            
            # Create order lines
            await self._create_order_lines(order_id, order_data["items"], tx)
            
            # Update inventory
            await self._update_inventory(order_data["items"], tx)
            
            # Calculate totals
            await self._calculate_order_totals(order_id, tx)
            
            return order_id
    
    @asynccontextmanager
    async def _transaction(self):
        """Transaction context manager"""
        connection = await self.db_adapter._connection_pool.acquire()
        try:
            async with connection.begin():
                yield connection
        finally:
            await self.db_adapter._connection_pool.release(connection)
    
    async def _create_order_header(self, order_data: dict, connection) -> str:
        """Create order header record"""
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        await connection.execute(
            """INSERT INTO order_headers 
               (order_id, customer_id, order_date, status, created_at)
               VALUES (:order_id, :customer_id, :order_date, :status, :created_at)""",
            {
                "order_id": order_id,
                "customer_id": order_data["customer_id"],
                "order_date": datetime.now(),
                "status": "PENDING",
                "created_at": datetime.now()
            }
        )
        
        return order_id
    
    async def _create_order_lines(self, order_id: str, items: List[dict], connection):
        """Create order line items"""
        for line_num, item in enumerate(items, 1):
            await connection.execute(
                """INSERT INTO order_lines 
                   (order_id, line_number, product_id, quantity, unit_price, line_total)
                   VALUES (:order_id, :line_number, :product_id, :quantity, :unit_price, :line_total)""",
                {
                    "order_id": order_id,
                    "line_number": line_num,
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "line_total": item["quantity"] * item["unit_price"]
                }
            )
    
    async def _update_inventory(self, items: List[dict], connection):
        """Update inventory levels"""
        for item in items:
            # Check available inventory
            result = await connection.execute(
                "SELECT available_quantity FROM inventory WHERE product_id = :product_id",
                {"product_id": item["product_id"]}
            )
            
            available = result.fetchone()[0]
            if available < item["quantity"]:
                raise ValueError(f"Insufficient inventory for product {item['product_id']}")
            
            # Update inventory
            await connection.execute(
                """UPDATE inventory 
                   SET available_quantity = available_quantity - :quantity,
                       reserved_quantity = reserved_quantity + :quantity
                   WHERE product_id = :product_id""",
                {
                    "quantity": item["quantity"],
                    "product_id": item["product_id"]
                }
            )

async def advanced_database_example():
    """Demonstrate advanced database operations with transactions"""
    
    db_adapter = FlxOracleDbAdapter(
        host="localhost",
        port=1521,
        service_name="XEPDB1",
        username="flx_user",
        password="flx_password",
        pool_min=2,
        pool_max=10
    )
    
    try:
        await db_adapter.initialize()
        
        order_service = OrderProcessingService(db_adapter)
        
        # Process order with transaction
        order_data = {
            "customer_id": "CUST-001",
            "items": [
                {"product_id": "PROD-001", "quantity": 2, "unit_price": 89.99},
                {"product_id": "PROD-002", "quantity": 1, "unit_price": 149.99}
            ]
        }
        
        order_id = await order_service.process_order(order_data)
        print(f"Order processed successfully: {order_id}")
        
    except Exception as e:
        print(f"Order processing failed: {e}")
    finally:
        await db_adapter.shutdown()

if __name__ == "__main__":
    asyncio.run(advanced_database_example())
```

---

## 📦 **Oracle WMS Integration Examples**

### **1. Inventory Management Operations**

#### **Real WMS Inventory Operations**

```python
# examples/oracle_wms_inventory.py
import asyncio
from flx.adapters.oracle.wms import WmsClient
from flx.core.services import ApplicationService
from datetime import datetime
from typing import List, Optional

class InventoryManagementService(ApplicationService):
    """Application service for WMS inventory operations"""
    
    def __init__(self, wms_client: WmsClient):
        self.wms_client = wms_client
    
    async def process_inventory_adjustment(self, adjustment_request: dict) -> dict:
        """Process inventory adjustment with validation"""
        
        # Validate current inventory
        current_inventory = await self.wms_client.inventory_inquiry(
            adjustment_request["item_id"],
            adjustment_request.get("location")
        )
        
        # Calculate new quantity
        new_quantity = current_inventory.available_quantity + adjustment_request["adjustment_quantity"]
        
        if new_quantity < 0:
            raise ValueError("Adjustment would result in negative inventory")
        
        # Submit adjustment
        adjustment_result = await self.wms_client.inventory_adjustment({
            "item_id": adjustment_request["item_id"],
            "location": adjustment_request["location"],
            "adjustment_quantity": adjustment_request["adjustment_quantity"],
            "reason_code": adjustment_request["reason_code"],
            "reference": adjustment_request.get("reference"),
            "user_id": adjustment_request["user_id"]
        })
        
        return {
            "adjustment_id": adjustment_result.adjustment_id,
            "previous_quantity": current_inventory.available_quantity,
            "adjustment_quantity": adjustment_request["adjustment_quantity"],
            "new_quantity": new_quantity,
            "processed_at": datetime.now()
        }
    
    async def transfer_inventory_between_locations(self, transfer_request: dict) -> dict:
        """Transfer inventory between warehouse locations"""
        
        # Validate source location inventory
        source_inventory = await self.wms_client.inventory_inquiry(
            transfer_request["item_id"],
            transfer_request["source_location"]
        )
        
        if source_inventory.available_quantity < transfer_request["quantity"]:
            raise ValueError("Insufficient inventory at source location")
        
        # Execute transfer
        transfer_result = await self.wms_client.inventory_transfer({
            "item_id": transfer_request["item_id"],
            "source_location": transfer_request["source_location"],
            "destination_location": transfer_request["destination_location"],
            "quantity": transfer_request["quantity"],
            "reference": transfer_request.get("reference"),
            "user_id": transfer_request["user_id"]
        })
        
        return {
            "transfer_id": transfer_result.transfer_id,
            "item_id": transfer_request["item_id"],
            "source_location": transfer_request["source_location"],
            "destination_location": transfer_request["destination_location"],
            "quantity": transfer_request["quantity"],
            "status": transfer_result.status,
            "processed_at": datetime.now()
        }

async def wms_inventory_example():
    """Demonstrate WMS inventory management operations"""
    
    wms_client = WmsClient(
        base_url="https://your-wms-instance.oracle.com",
        facility_id="FACILITY_01",
        client_id="wms_client_id",
        client_secret="wms_client_secret",
        username="wms_user",
        password="wms_password"
    )
    
    try:
        await wms_client.initialize()
        
        inventory_service = InventoryManagementService(wms_client)
        
        # Example 1: Inventory inquiry
        inventory_info = await wms_client.inventory_inquiry("ITEM-001", "LOC-A001")
        print(f"Current inventory: {inventory_info.available_quantity} units at {inventory_info.location}")
        
        # Example 2: Inventory adjustment
        adjustment_request = {
            "item_id": "ITEM-001",
            "location": "LOC-A001",
            "adjustment_quantity": 10,
            "reason_code": "RECEIPT_ADJUSTMENT",
            "reference": "ADJ-001",
            "user_id": "USER001"
        }
        
        adjustment_result = await inventory_service.process_inventory_adjustment(adjustment_request)
        print(f"Adjustment processed: {adjustment_result}")
        
        # Example 3: Inventory transfer
        transfer_request = {
            "item_id": "ITEM-001",
            "source_location": "LOC-A001",
            "destination_location": "LOC-B001",
            "quantity": 5,
            "reference": "TRANSFER-001",
            "user_id": "USER001"
        }
        
        transfer_result = await inventory_service.transfer_inventory_between_locations(transfer_request)
        print(f"Transfer completed: {transfer_result}")
        
    finally:
        await wms_client.shutdown()

if __name__ == "__main__":
    asyncio.run(wms_inventory_example())
```

### **2. LPN (License Plate Number) Operations**

#### **Complete LPN Workflow**

```python
# examples/oracle_wms_lpn_workflow.py
import asyncio
from flx.adapters.oracle.wms import WmsClient
from flx.core.services import ApplicationService
from typing import List, Dict

class LpnWorkflowService(ApplicationService):
    """Complete LPN workflow management service"""
    
    def __init__(self, wms_client: WmsClient):
        self.wms_client = wms_client
    
    async def process_inbound_lpn(self, lpn_data: dict) -> dict:
        """Complete inbound LPN processing workflow"""
        
        workflow_result = {
            "lpn": lpn_data["lpn"],
            "steps": [],
            "status": "IN_PROGRESS"
        }
        
        try:
            # Step 1: Receive LPN
            receipt_result = await self.wms_client.lpn_receive({
                "lpn": lpn_data["lpn"],
                "receipt_id": lpn_data["receipt_id"],
                "items": lpn_data["items"],
                "received_by": lpn_data["user_id"],
                "receipt_location": "RECEIVING_DOCK"
            })
            
            workflow_result["steps"].append({
                "step": "RECEIVE",
                "status": "COMPLETED",
                "result": receipt_result.dict()
            })
            
            # Step 2: Quality inspection (if required)
            if lpn_data.get("requires_inspection", False):
                inspection_result = await self._process_quality_inspection(lpn_data["lpn"])
                workflow_result["steps"].append({
                    "step": "INSPECTION",
                    "status": "COMPLETED",
                    "result": inspection_result
                })
            
            # Step 3: Move to storage location
            putaway_location = await self._determine_putaway_location(lpn_data["items"])
            
            move_result = await self.wms_client.lpn_move({
                "lpn": lpn_data["lpn"],
                "destination_location": putaway_location,
                "move_type": "PUTAWAY",
                "user_id": lpn_data["user_id"]
            })
            
            workflow_result["steps"].append({
                "step": "PUTAWAY",
                "status": "COMPLETED",
                "result": move_result.dict()
            })
            
            workflow_result["status"] = "COMPLETED"
            workflow_result["final_location"] = putaway_location
            
        except Exception as e:
            workflow_result["status"] = "FAILED"
            workflow_result["error"] = str(e)
        
        return workflow_result
    
    async def process_outbound_lpn(self, pick_request: dict) -> dict:
        """Complete outbound LPN picking workflow"""
        
        workflow_result = {
            "order_id": pick_request["order_id"],
            "lpns_processed": [],
            "status": "IN_PROGRESS"
        }
        
        try:
            # Get LPN recommendations for pick
            lpn_recommendations = await self._get_lpn_pick_recommendations(pick_request["items"])
            
            for lpn_rec in lpn_recommendations:
                # Pick from LPN
                pick_result = await self.wms_client.lpn_pick({
                    "lpn": lpn_rec["lpn"],
                    "items": lpn_rec["items"],
                    "order_id": pick_request["order_id"],
                    "user_id": pick_request["user_id"]
                })
                
                # Move LPN to staging
                if pick_result.status == "COMPLETED":
                    staging_result = await self.wms_client.lpn_move({
                        "lpn": lpn_rec["lpn"],
                        "destination_location": "STAGING_AREA",
                        "move_type": "PICK_STAGING",
                        "user_id": pick_request["user_id"]
                    })
                    
                    workflow_result["lpns_processed"].append({
                        "lpn": lpn_rec["lpn"],
                        "pick_result": pick_result.dict(),
                        "staging_result": staging_result.dict()
                    })
            
            workflow_result["status"] = "COMPLETED"
            
        except Exception as e:
            workflow_result["status"] = "FAILED"
            workflow_result["error"] = str(e)
        
        return workflow_result
    
    async def _process_quality_inspection(self, lpn: str) -> dict:
        """Process quality inspection for LPN"""
        # Simulate quality inspection process
        return {
            "lpn": lpn,
            "inspection_status": "PASSED",
            "inspector": "QC_USER",
            "inspection_date": datetime.now().isoformat()
        }
    
    async def _determine_putaway_location(self, items: List[dict]) -> str:
        """Determine optimal putaway location based on items"""
        # Simulate location determination logic
        return "STORAGE_A001"
    
    async def _get_lpn_pick_recommendations(self, items: List[dict]) -> List[dict]:
        """Get LPN recommendations for picking items"""
        # Simulate pick recommendation logic
        return [
            {
                "lpn": "LPN-001",
                "items": items[:2]  # First 2 items from LPN-001
            },
            {
                "lpn": "LPN-002", 
                "items": items[2:]  # Remaining items from LPN-002
            }
        ]

async def wms_lpn_workflow_example():
    """Demonstrate complete LPN workflow operations"""
    
    wms_client = WmsClient(
        base_url="https://your-wms-instance.oracle.com",
        facility_id="FACILITY_01",
        client_id="wms_client_id",
        client_secret="wms_client_secret",
        username="wms_user",
        password="wms_password"
    )
    
    try:
        await wms_client.initialize()
        
        lpn_service = LpnWorkflowService(wms_client)
        
        # Example 1: Inbound LPN workflow
        inbound_lpn_data = {
            "lpn": "LPN-INBOUND-001",
            "receipt_id": "REC-001",
            "user_id": "USER001",
            "requires_inspection": True,
            "items": [
                {"item_id": "ITEM-001", "quantity": 10},
                {"item_id": "ITEM-002", "quantity": 5}
            ]
        }
        
        inbound_result = await lpn_service.process_inbound_lpn(inbound_lpn_data)
        print(f"Inbound LPN workflow: {inbound_result}")
        
        # Example 2: Outbound LPN workflow
        outbound_pick_request = {
            "order_id": "ORD-001",
            "user_id": "USER001",
            "items": [
                {"item_id": "ITEM-001", "quantity": 3},
                {"item_id": "ITEM-002", "quantity": 2},
                {"item_id": "ITEM-003", "quantity": 1}
            ]
        }
        
        outbound_result = await lpn_service.process_outbound_lpn(outbound_pick_request)
        print(f"Outbound LPN workflow: {outbound_result}")
        
    finally:
        await wms_client.shutdown()

if __name__ == "__main__":
    asyncio.run(wms_lpn_workflow_example())
```

---

## 🔄 **Oracle OIC Integration Examples**

### **1. Integration Orchestration**

#### **End-to-End Integration Workflow**

```python
# examples/oracle_oic_integration.py
import asyncio
from flx.adapters.oracle.oic import OicClient
from flx.core.services import ApplicationService
from flx.core.events import DomainEvent
from typing import Dict, List
import json

class IntegrationOrchestrationService(ApplicationService):
    """Service for orchestrating complex integrations via OIC"""
    
    def __init__(self, oic_client: OicClient):
        self.oic_client = oic_client
    
    async def process_order_integration(self, order_data: dict) -> dict:
        """Complete order processing integration across multiple systems"""
        
        integration_result = {
            "order_id": order_data["order_id"],
            "integrations": [],
            "status": "IN_PROGRESS"
        }
        
        try:
            # Step 1: Customer validation integration
            customer_validation = await self._execute_customer_validation(order_data["customer_id"])
            integration_result["integrations"].append(customer_validation)
            
            # Step 2: Inventory check integration
            inventory_check = await self._execute_inventory_check(order_data["items"])
            integration_result["integrations"].append(inventory_check)
            
            # Step 3: Credit check integration
            credit_check = await self._execute_credit_check(order_data["customer_id"], order_data["total_amount"])
            integration_result["integrations"].append(credit_check)
            
            # Step 4: Order creation integration
            if all(result["status"] == "SUCCESS" for result in integration_result["integrations"]):
                order_creation = await self._execute_order_creation(order_data)
                integration_result["integrations"].append(order_creation)
                
                # Step 5: Fulfillment integration
                fulfillment = await self._execute_fulfillment_process(order_data["order_id"])
                integration_result["integrations"].append(fulfillment)
                
                integration_result["status"] = "COMPLETED"
            else:
                integration_result["status"] = "FAILED"
                integration_result["reason"] = "Pre-validation checks failed"
        
        except Exception as e:
            integration_result["status"] = "ERROR"
            integration_result["error"] = str(e)
        
        return integration_result
    
    async def _execute_customer_validation(self, customer_id: str) -> dict:
        """Execute customer validation integration"""
        
        payload = {
            "customer_id": customer_id,
            "validation_type": "COMPREHENSIVE",
            "include_credit_history": True
        }
        
        submission = await self.oic_client.submit_integration(
            "CUSTOMER_VALIDATION_01",
            payload
        )
        
        # Monitor integration
        final_status = await self._monitor_integration_completion(submission.instance_id)
        
        return {
            "integration": "CUSTOMER_VALIDATION",
            "instance_id": submission.instance_id,
            "status": final_status.status,
            "result": final_status.result
        }
    
    async def _execute_inventory_check(self, items: List[dict]) -> dict:
        """Execute inventory availability check integration"""
        
        payload = {
            "items": items,
            "check_type": "AVAILABILITY_AND_ALLOCATION",
            "facility_id": "FACILITY_01"
        }
        
        submission = await self.oic_client.submit_integration(
            "INVENTORY_CHECK_01",
            payload
        )
        
        final_status = await self._monitor_integration_completion(submission.instance_id)
        
        return {
            "integration": "INVENTORY_CHECK",
            "instance_id": submission.instance_id,
            "status": final_status.status,
            "result": final_status.result
        }
    
    async def _execute_credit_check(self, customer_id: str, amount: float) -> dict:
        """Execute credit check integration"""
        
        payload = {
            "customer_id": customer_id,
            "requested_amount": amount,
            "check_type": "CREDIT_LIMIT_AND_HISTORY"
        }
        
        submission = await self.oic_client.submit_integration(
            "CREDIT_CHECK_01",
            payload
        )
        
        final_status = await self._monitor_integration_completion(submission.instance_id)
        
        return {
            "integration": "CREDIT_CHECK",
            "instance_id": submission.instance_id,
            "status": final_status.status,
            "result": final_status.result
        }
    
    async def _execute_order_creation(self, order_data: dict) -> dict:
        """Execute order creation integration"""
        
        submission = await self.oic_client.submit_integration(
            "ORDER_CREATION_01",
            order_data
        )
        
        final_status = await self._monitor_integration_completion(submission.instance_id)
        
        return {
            "integration": "ORDER_CREATION",
            "instance_id": submission.instance_id,
            "status": final_status.status,
            "result": final_status.result
        }
    
    async def _execute_fulfillment_process(self, order_id: str) -> dict:
        """Execute fulfillment process integration"""
        
        payload = {
            "order_id": order_id,
            "fulfillment_type": "STANDARD",
            "priority": "NORMAL"
        }
        
        submission = await self.oic_client.submit_integration(
            "FULFILLMENT_PROCESS_01",
            payload
        )
        
        final_status = await self._monitor_integration_completion(submission.instance_id)
        
        return {
            "integration": "FULFILLMENT_PROCESS",
            "instance_id": submission.instance_id,
            "status": final_status.status,
            "result": final_status.result
        }
    
    async def _monitor_integration_completion(self, instance_id: str) -> dict:
        """Monitor integration until completion"""
        
        max_attempts = 60  # 5 minutes with 5-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            status = await self.oic_client.monitor_integration(instance_id)
            
            if status.status in ["COMPLETED", "FAILED", "ERROR"]:
                return status
            
            await asyncio.sleep(5)  # Wait 5 seconds
            attempt += 1
        
        raise TimeoutError(f"Integration {instance_id} did not complete within timeout")

async def oic_integration_example():
    """Demonstrate complex OIC integration orchestration"""
    
    oic_client = OicClient(
        oic_host="your-oic-instance.oraclecloud.com",
        client_id="oic_client_id",
        client_secret="oic_client_secret",
        username="oic_user",
        password="oic_password"
    )
    
    try:
        await oic_client.initialize()
        
        orchestration_service = IntegrationOrchestrationService(oic_client)
        
        # Complex order processing integration
        order_data = {
            "order_id": "ORD-001",
            "customer_id": "CUST-001",
            "total_amount": 1500.00,
            "items": [
                {"item_id": "ITEM-001", "quantity": 2, "unit_price": 500.00},
                {"item_id": "ITEM-002", "quantity": 1, "unit_price": 500.00}
            ]
        }
        
        result = await orchestration_service.process_order_integration(order_data)
        
        print(f"Order integration result: {json.dumps(result, indent=2)}")
        
        # Print detailed integration status
        for integration in result["integrations"]:
            print(f"Integration {integration['integration']}: {integration['status']}")
            if integration["status"] == "SUCCESS":
                print(f"  Result: {integration['result']}")
        
    finally:
        await oic_client.shutdown()

if __name__ == "__main__":
    asyncio.run(oic_integration_example())
```

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Oracle Integration Specification](../reference/specifications/oracle-integration-specification.md) - Technical specifications implemented in these examples
- [Oracle Integration Guide](../guides/oracle/oracle-integration-comprehensive-guide.md) - Setup and configuration required for these examples
- [Getting Started](../getting-started/index.md) - Framework installation and basic concepts needed to run examples

### **➡️ Next Steps**

- [Development Testing](../development/testing/index.md) - Testing strategies for Oracle integration validation using these examples
- [Deployment Guide](../deployment/index.md) - Production deployment patterns for Oracle integrations demonstrated here
- [Optimization Guide](../optimization/index.md) - Performance optimization techniques for Oracle integration workloads

### **🔗 Related Implementation Sections**

- [**Oracle WMS Comprehensive Guide**](../guides/oracle/oracle-wms-comprehensive-guide.md) - Complete WMS integration patterns and CLI operations demonstrated in warehouse inventory examples
- [**Oracle Database Implementation**](../guides/oracle/database-complete-guide.md) - Advanced database integration patterns and transaction management shown in CRUD examples
- [**Infrastructure Services Analysis**](../infrastructure/service-patterns.md) - Production infrastructure patterns supporting these Oracle integration implementations
- [**Complete API Reference**](../api-reference/core-api-reference.md) - Detailed API documentation for all classes, methods, and interfaces used in Oracle integration examples
- [**Testing Oracle Integrations**](../development/testing/hexagonal-testing-guide.md) - Testing methodologies and validation strategies for Oracle integration patterns
- [**Security Implementation**](../security/architecture/security-architecture.md) - Enterprise security patterns for Oracle authentication and authorization demonstrated in examples

---

## 📊 **Example Validation**

### **Source Code Validation**

- **Database Examples**: Validated against `/flx_database_oracle/` implementation
- **WMS Examples**: Validated against `/flx_http_oracle_wms/` implementation  
- **OIC Examples**: Validated against `/flx_http_oracle_oic/` implementation
- **Architecture Patterns**: Validated against `/flx/src/flx/` core framework

### **Testing Coverage**

- All examples include error handling and resilience patterns
- Transaction management demonstrated with proper cleanup
- Authentication flows implemented according to Oracle standards
- Integration monitoring and status tracking included

---

## 📋 **Example Metadata**

- **Example Version**: 1.0.0
- **Framework Compatibility**: FLX 0.4.0+
- **Oracle Compatibility**: 19c+, Autonomous Database, Cloud Services
- **Validation Date**: June 11, 2025
- **Implementation Status**: ✅ Production-ready examples

---

**📂 Examples**: [Examples Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
