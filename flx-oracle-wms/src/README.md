# 📦 FLX Oracle WMS - Source Implementation

> **Module**: Oracle Warehouse Management System (WMS) orchestration source implementation with advanced pipeline management | **Audience**: Supply Chain Engineers, Warehouse Operations, Integration Architects | **Status**: Production Ready

## 📋 **Overview**

Complete source implementation for Oracle Warehouse Management System integration and orchestration, providing comprehensive inventory management, advanced pipeline orchestration, and real-time monitoring capabilities for enterprise warehouse operations.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Oracle WMS](../README.md) → **📂 Current**: Source Implementation

---

## 🎯 **Module Purpose**

This module implements enterprise-grade Oracle WMS integration patterns, providing sophisticated orchestration capabilities, pipeline management, real-time monitoring, and comprehensive inventory synchronization for large-scale warehouse operations.

### **Key Capabilities**

- **Advanced Orchestration** - Complex warehouse operation orchestration
- **Pipeline Management** - Sophisticated data pipeline coordination
- **Real-time Monitoring** - Comprehensive warehouse operation monitoring
- **Inventory Synchronization** - Real-time inventory data management
- **Configuration Management** - Enterprise-grade configuration handling
- **CLI Interface** - Command-line tools for warehouse operations

---

## 📁 **Module Structure**

```
src/flx_oracle_wms/
├── __init__.py              # Public API exports
├── __main__.py              # CLI entry point
├── cli.py                   # Command-line interface
├── config.py                # Configuration management
├── monitoring.py            # Operation monitoring
├── orchestrator.py          # Basic orchestration engine
├── orchestrator_advanced.py # Advanced orchestration patterns
├── pipelines/               # Data pipeline modules
│   ├── __init__.py
│   └── inventory_sync.py    # Inventory synchronization pipeline
└── utils/                   # Utility modules
```

---

## 🔧 **Core Components**

### **1. CLI Interface (cli.py)**

Comprehensive command-line interface for WMS operations:

```python
class WMSOperationsCLI:
    """Command-line interface for WMS operations."""

    def __init__(self, config: WMSConfig):
        self.config = config
        self.orchestrator = WMSOrchestrator(config)
        self.monitor = WMSMonitor(config)

    def inventory_sync(
        self,
        location: str = None,
        item_filter: str = None
    ) -> SyncResult:
        """Synchronize inventory data."""

    def process_receipts(self, receipt_ids: List[str]) -> ProcessingResult:
        """Process warehouse receipts."""

    def execute_picks(self, pick_batch_id: str) -> ExecutionResult:
        """Execute pick operations."""

    def monitor_operations(self, duration: int = 3600) -> MonitoringReport:
        """Monitor warehouse operations."""

    def health_check(self) -> HealthStatus:
        """Check WMS system health."""
```

### **2. Configuration Management (config.py)**

Enterprise WMS configuration:

```python
class WMSConfig(BaseSettings):
    """Oracle WMS configuration with comprehensive validation."""

    # WMS API settings
    wms_base_url: HttpUrl
    wms_username: str
    wms_password: SecretStr
    wms_facility_id: str

    # Authentication settings
    auth_type: AuthType = AuthType.BASIC
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[SecretStr] = None

    # Performance settings
    batch_size: int = Field(default=1000, ge=1, le=10000)
    max_concurrent_requests: int = Field(default=10, ge=1, le=50)
    request_timeout: int = Field(default=60, ge=1, le=300)

    # Orchestration settings
    enable_auto_retry: bool = True
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=5, ge=1, le=60)

    # Monitoring settings
    enable_real_time_monitoring: bool = True
    monitoring_interval: int = Field(default=30, ge=5, le=300)
    alert_thresholds: AlertThresholds = Field(default_factory=AlertThresholds)

    class Config:
        env_prefix = "WMS_"
        env_file = ".env"
```

### **3. Basic Orchestrator (orchestrator.py)**

Core orchestration engine:

```python
class WMSOrchestrator:
    """Core WMS operation orchestrator."""

    def __init__(self, config: WMSConfig):
        self.config = config
        self.monitor = WMSMonitor(config)
        self.pipeline_manager = PipelineManager(config)

    async def orchestrate_inventory_cycle(
        self,
        locations: List[str]
    ) -> OrchestrationResult:
        """Orchestrate complete inventory cycle."""

    async def orchestrate_receiving_process(
        self,
        receipt_ids: List[str]
    ) -> ReceivingResult:
        """Orchestrate receiving process workflow."""

    async def orchestrate_picking_process(
        self,
        order_ids: List[str]
    ) -> PickingResult:
        """Orchestrate picking process workflow."""

    async def orchestrate_shipping_process(
        self,
        shipment_ids: List[str]
    ) -> ShippingResult:
        """Orchestrate shipping process workflow."""
```

### **4. Advanced Orchestrator (orchestrator_advanced.py)**

Sophisticated orchestration patterns:

```python
class AdvancedWMSOrchestrator:
    """Advanced WMS orchestration with complex patterns."""

    async def orchestrate_multi_facility_sync(
        self,
        facilities: List[FacilityConfig]
    ) -> MultiFacilityResult:
        """Orchestrate multi-facility synchronization."""

    async def orchestrate_demand_driven_replenishment(
        self,
        demand_forecast: DemandForecast
    ) -> ReplenishmentResult:
        """Orchestrate demand-driven replenishment."""

    async def orchestrate_wave_planning(
        self,
        wave_criteria: WaveCriteria
    ) -> WavePlanningResult:
        """Orchestrate wave planning optimization."""

    async def orchestrate_cross_docking(
        self,
        cross_dock_orders: List[CrossDockOrder]
    ) -> CrossDockingResult:
        """Orchestrate cross-docking operations."""

    async def orchestrate_yard_management(
        self,
        yard_config: YardConfig
    ) -> YardManagementResult:
        """Orchestrate yard management operations."""
```

### **5. Monitoring System (monitoring.py)**

Comprehensive warehouse operation monitoring:

```python
class WMSMonitor:
    """Monitor WMS operations and performance."""

    async def monitor_inventory_accuracy(
        self,
        locations: List[str] = None
    ) -> InventoryAccuracyReport:
        """Monitor inventory accuracy metrics."""

    async def monitor_throughput_metrics(
        self,
        time_range: TimeRange
    ) -> ThroughputReport:
        """Monitor warehouse throughput metrics."""

    async def monitor_labor_efficiency(
        self,
        shift_info: ShiftInfo
    ) -> LaborEfficiencyReport:
        """Monitor labor efficiency metrics."""

    async def monitor_equipment_utilization(self) -> EquipmentUtilizationReport:
        """Monitor equipment utilization."""

    async def monitor_order_fulfillment_rates(
        self,
        time_range: TimeRange
    ) -> FulfillmentReport:
        """Monitor order fulfillment rates."""

    async def detect_anomalies(
        self,
        metrics: List[Metric],
        threshold: float = 2.0
    ) -> List[Anomaly]:
        """Detect operational anomalies."""

    async def generate_real_time_dashboard(self) -> DashboardData:
        """Generate real-time dashboard data."""
```

---

## 🚀 **Pipeline Management (pipelines/)**

### **Inventory Synchronization Pipeline (inventory_sync.py)**

Sophisticated inventory synchronization:

```python
class InventorySyncPipeline:
    """Advanced inventory synchronization pipeline."""

    async def execute_full_sync(
        self,
        sync_config: InventorySyncConfig
    ) -> SyncResult:
        """Execute complete inventory synchronization."""

    async def execute_incremental_sync(
        self,
        last_sync_timestamp: datetime
    ) -> IncrementalSyncResult:
        """Execute incremental inventory sync."""

    async def sync_location_inventory(
        self,
        location_id: str,
        item_filters: List[ItemFilter] = None
    ) -> LocationSyncResult:
        """Synchronize inventory for specific location."""

    async def sync_item_availability(
        self,
        item_ids: List[str]
    ) -> AvailabilitySyncResult:
        """Synchronize item availability across locations."""

    async def validate_sync_integrity(
        self,
        sync_result: SyncResult
    ) -> IntegrityValidation:
        """Validate synchronization data integrity."""

    async def reconcile_discrepancies(
        self,
        discrepancies: List[InventoryDiscrepancy]
    ) -> ReconciliationResult:
        """Reconcile inventory discrepancies."""
```

---

## 🔄 **Orchestration Workflows**

### **Complete Receiving Workflow**

```python
async def complete_receiving_workflow(
    orchestrator: AdvancedWMSOrchestrator,
    receipt_number: str
) -> ReceivingWorkflowResult:
    """Complete receiving workflow orchestration."""

    try:
        # 1. Validate receipt
        receipt = await orchestrator.validate_receipt(receipt_number)

        # 2. Check dock availability
        dock_assignment = await orchestrator.assign_receiving_dock(receipt)

        # 3. Generate receiving tasks
        receiving_tasks = await orchestrator.generate_receiving_tasks(receipt)

        # 4. Execute receiving tasks
        task_results = []
        for task in receiving_tasks:
            result = await orchestrator.execute_receiving_task(task)
            task_results.append(result)

        # 5. Update inventory
        inventory_update = await orchestrator.update_inventory_from_receipt(
            receipt, task_results
        )

        # 6. Generate putaway tasks
        putaway_tasks = await orchestrator.generate_putaway_tasks(
            received_items=inventory_update.received_items
        )

        # 7. Execute putaway workflow
        putaway_result = await orchestrator.execute_putaway_workflow(putaway_tasks)

        # 8. Close receipt
        closure_result = await orchestrator.close_receipt(receipt_number)

        return ReceivingWorkflowResult(
            receipt_number=receipt_number,
            tasks_completed=len(task_results),
            inventory_updated=inventory_update,
            putaway_completed=putaway_result,
            status=WorkflowStatus.COMPLETED
        )

    except Exception as e:
        await orchestrator.handle_receiving_error(receipt_number, e)
        raise
```

### **Wave Planning and Execution Workflow**

```python
async def wave_planning_execution_workflow(
    orchestrator: AdvancedWMSOrchestrator,
    wave_criteria: WaveCriteria
) -> WaveExecutionResult:
    """Complete wave planning and execution workflow."""

    # 1. Analyze orders for wave
    order_analysis = await orchestrator.analyze_orders_for_wave(wave_criteria)

    # 2. Optimize wave plan
    wave_plan = await orchestrator.optimize_wave_plan(
        orders=order_analysis.eligible_orders,
        optimization_criteria=wave_criteria.optimization_goals
    )

    # 3. Allocate inventory
    allocation_result = await orchestrator.allocate_inventory_for_wave(
        wave_plan.planned_picks
    )

    # 4. Generate pick tasks
    pick_tasks = await orchestrator.generate_optimized_pick_tasks(
        allocations=allocation_result.allocations,
        routing_strategy=wave_criteria.routing_strategy
    )

    # 5. Execute picking workflow
    picking_result = await orchestrator.execute_picking_workflow(pick_tasks)

    # 6. Stage for shipping
    staging_result = await orchestrator.stage_picked_orders(
        picked_orders=picking_result.completed_picks
    )

    # 7. Generate shipping documentation
    shipping_docs = await orchestrator.generate_shipping_documentation(
        staged_orders=staging_result.staged_orders
    )

    return WaveExecutionResult(
        wave_id=wave_plan.wave_id,
        orders_processed=len(order_analysis.eligible_orders),
        pick_efficiency=picking_result.efficiency_metrics,
        shipping_ready=len(staging_result.staged_orders),
        total_processing_time=datetime.utcnow() - wave_plan.start_time
    )
```

### **Real-time Monitoring Workflow**

```python
async def real_time_monitoring_workflow(monitor: WMSMonitor):
    """Continuous real-time monitoring workflow."""

    while True:
        try:
            # 1. Collect current metrics
            inventory_metrics = await monitor.monitor_inventory_accuracy()
            throughput_metrics = await monitor.monitor_throughput_metrics(
                TimeRange.last_hour()
            )
            labor_metrics = await monitor.monitor_labor_efficiency(
                ShiftInfo.current_shift()
            )
            equipment_metrics = await monitor.monitor_equipment_utilization()

            # 2. Detect anomalies
            all_metrics = [
                inventory_metrics.accuracy_rate,
                throughput_metrics.orders_per_hour,
                labor_metrics.efficiency_percentage,
                equipment_metrics.utilization_rate
            ]

            anomalies = await monitor.detect_anomalies(all_metrics)

            # 3. Generate alerts for anomalies
            for anomaly in anomalies:
                await send_alert(anomaly)

            # 4. Update real-time dashboard
            dashboard_data = await monitor.generate_real_time_dashboard()
            await update_dashboard(dashboard_data)

            # 5. Log metrics for historical analysis
            await log_metrics_to_database({
                "inventory": inventory_metrics,
                "throughput": throughput_metrics,
                "labor": labor_metrics,
                "equipment": equipment_metrics
            })

        except Exception as e:
            await handle_monitoring_error(e)

        await asyncio.sleep(30)  # Monitor every 30 seconds
```

---

## 📊 **Data Models**

### **Orchestration Models**

```python
@dataclass
class OrchestrationResult:
    """Result of orchestration operation."""

    operation_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: OrchestrationStatus
    steps_completed: int
    total_steps: int
    metrics: OrchestrationMetrics
    errors: List[OrchestrationError]

@dataclass
class WavePlanningResult:
    """Wave planning optimization result."""

    wave_id: str
    planned_orders: List[PlannedOrder]
    estimated_completion_time: datetime
    resource_requirements: ResourceRequirements
    efficiency_score: float
    optimization_metrics: OptimizationMetrics
```

### **Monitoring Models**

```python
@dataclass
class InventoryAccuracyReport:
    """Inventory accuracy monitoring report."""

    location_id: str
    total_items_counted: int
    accurate_items: int
    accuracy_rate: float
    discrepancies: List[InventoryDiscrepancy]
    last_cycle_count: datetime

@dataclass
class ThroughputReport:
    """Warehouse throughput monitoring report."""

    time_range: TimeRange
    orders_processed: int
    orders_per_hour: float
    lines_picked: int
    lines_per_hour: float
    efficiency_trend: TrendDirection
    bottlenecks: List[ThroughputBottleneck]
```

### **Pipeline Models**

```python
@dataclass
class InventorySyncConfig:
    """Inventory synchronization configuration."""

    sync_type: SyncType
    locations: List[str]
    item_filters: List[ItemFilter]
    batch_size: int
    enable_validation: bool
    reconcile_discrepancies: bool
    notification_settings: NotificationSettings

@dataclass
class SyncResult:
    """Inventory synchronization result."""

    sync_id: str
    start_time: datetime
    end_time: datetime
    items_processed: int
    items_updated: int
    discrepancies_found: int
    discrepancies_resolved: int
    validation_results: ValidationResults
```

---

## 🧪 **Testing Strategies**

### **Orchestration Testing**

```python
@pytest.mark.asyncio
async def test_receiving_workflow_orchestration():
    """Test complete receiving workflow orchestration."""
    # Setup
    config = WMSConfig(
        wms_base_url="https://test-wms.oracle.com",
        wms_username="test_user",
        wms_password="test_password",
        wms_facility_id="FACILITY_001"
    )

    orchestrator = AdvancedWMSOrchestrator(config)

    # Mock receipt data
    receipt_number = "RCP-12345"

    # Execute workflow
    result = await complete_receiving_workflow(orchestrator, receipt_number)

    # Verify results
    assert result.status == WorkflowStatus.COMPLETED
    assert result.tasks_completed > 0
    assert result.inventory_updated is not None
```

### **Pipeline Testing**

```python
@pytest.mark.asyncio
async def test_inventory_sync_pipeline():
    """Test inventory synchronization pipeline."""
    config = InventorySyncConfig(
        sync_type=SyncType.INCREMENTAL,
        locations=["LOC-001", "LOC-002"],
        batch_size=100,
        enable_validation=True
    )

    pipeline = InventorySyncPipeline()

    # Execute sync
    result = await pipeline.execute_incremental_sync(
        datetime.utcnow() - timedelta(hours=1)
    )

    # Verify results
    assert result.items_processed > 0
    assert result.validation_results.passed
```

### **Monitoring Testing**

```python
@pytest.mark.asyncio
async def test_real_time_monitoring():
    """Test real-time monitoring capabilities."""
    monitor = WMSMonitor(test_config)

    # Test inventory accuracy monitoring
    accuracy_report = await monitor.monitor_inventory_accuracy(["LOC-001"])
    assert accuracy_report.accuracy_rate >= 0.0
    assert accuracy_report.accuracy_rate <= 1.0

    # Test anomaly detection
    test_metrics = [0.95, 0.97, 0.96, 0.45]  # Last value is anomaly
    anomalies = await monitor.detect_anomalies(test_metrics, threshold=2.0)
    assert len(anomalies) > 0
```

---

## 🔗 **Integration Patterns**

### **FLX Framework Integration**

```python
class WMSPlugin:
    """FLX plugin for Oracle WMS integration."""

    def __init__(self, config: WMSConfig):
        self.config = config
        self.orchestrator = AdvancedWMSOrchestrator(config)
        self.monitor = WMSMonitor(config)

    async def initialize(self) -> None:
        """Initialize WMS plugin."""
        await self.orchestrator.validate_connection()
        await self.monitor.start_monitoring()

    def get_orchestration_service(self) -> OrchestrationService:
        """Get orchestration service."""
        return OrchestrationService(self.orchestrator)

    def get_monitoring_service(self) -> MonitoringService:
        """Get monitoring service."""
        return MonitoringService(self.monitor)
```

### **CLI Integration**

```bash
# Execute inventory sync
flx-oracle-wms inventory-sync --location LOC-001 --incremental

# Process receipts
flx-oracle-wms process-receipts --receipt-ids RCP-001,RCP-002

# Monitor operations
flx-oracle-wms monitor-operations --duration 3600 --real-time

# Execute wave planning
flx-oracle-wms wave-planning --criteria wave-config.json

# Health check
flx-oracle-wms health-check --detailed
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete WMS component documentation
- [Configuration Guide](../docs/configuration.md) - WMS connection setup
- [Orchestration Guide](../docs/orchestration.md) - Advanced orchestration patterns

### **Related Components**

- [TAP Oracle WMS](../../tap-oracle-wms/README.md) - WMS data extraction
- [Target Oracle WMS](../../target-oracle-wms/README.md) - WMS data loading
- [FLX HTTP Oracle WMS](../../flx-http-oracle-wms/README.md) - HTTP client

### **External References**

- [Oracle WMS Cloud Documentation](https://docs.oracle.com/en/cloud/saas/applications/24a/fawms/) - WMS reference
- [WMS REST API Reference](https://docs.oracle.com/en/cloud/saas/applications/24a/fawms/api-warehouse-management/) - API reference
- [Supply Chain Management Best Practices](https://www.oracle.com/scm/) - SCM best practices

---

**📂 Module**: Source Implementation | **🏠 Component**: [FLX Oracle WMS](../README.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-19
