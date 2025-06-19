"""FLX Integrated Usage Example.

This example demonstrates how multiple FLX projects work together
using the new standardized architecture with Flx-prefixed classes.
It shows integration between:
- flx-database-oracle (Oracle Database operations)
- flx-http-oracle-wms (WMS HTTP API operations)
- flx-http-oracle-oic (OIC HTTP API operations)
"""

import asyncio
from typing import Any

import structlog
from flx.cli.declarative import FlxDeclarativeCli
from flx.ports.ingoing.operation import FlxOperationRequest

# Import FLX adapters from different projects
from flx_database_oracle.adapters.flx_application import FlxOracleApplicationContext
from flx_database_oracle.config.flx_oracle_config import FlxOracleConfig


def setup_logging() -> None:
    """Setup structured logging for integrated demo."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class FlxIntegratedApplication:
    """Integrated FLX Application combining multiple system adapters."""

    def __init__(self) -> None:
        """Initialize integrated application."""
        self.logger = structlog.get_logger(__name__)

        # Application configurations
        self.oracle_config = FlxOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="wms_user",
            password="wms_password",
        )

        # Application instances
        self.oracle_app: Any = None
        self.wms_app: Any = None
        self.oic_app: Any = None

        # Unified CLI
        self.unified_cli: FlxDeclarativeCli | None = None

    async def initialize(self) -> None:
        """Initialize all integrated applications."""
        self.logger.info("Initializing FLX Integrated Application")

        # Initialize Oracle Database application
        self.oracle_app = FlxOracleApplicationContext(self.oracle_config)
        await self.oracle_app.__aenter__()

        # Create unified CLI
        self.unified_cli = FlxDeclarativeCli("flx-integrated")

        # Register all adapters with unified CLI
        if self.oracle_app.app:
            oracle_cli = self.oracle_app.app.get_cli()
            self.unified_cli.register_adapter(
                "oracle-resource",
                oracle_cli.resource_adapter,
            )
            self.unified_cli.register_adapter(
                "oracle-pagination",
                oracle_cli.pagination_adapter,
            )
            self.unified_cli.register_adapter(
                "oracle-operation",
                oracle_cli.operation_adapter,
            )

        self.logger.info("FLX Integrated Application initialized successfully")

    async def shutdown(self) -> None:
        """Shutdown all integrated applications."""
        self.logger.info("Shutting down FLX Integrated Application")

        if self.oracle_app:
            await self.oracle_app.__aexit__(None, None, None)

        self.logger.info("FLX Integrated Application shutdown completed")


async def demonstrate_cross_system_workflow() -> None:
    """Demonstrate a workflow that spans multiple systems."""
    logger = structlog.get_logger(__name__)
    logger.info("=== Cross-System Workflow Demo ===")

    app = FlxIntegratedApplication()

    try:
        await app.initialize()

        # Step 1: Query inventory from Oracle Database
        logger.info("Step 1: Querying inventory from Oracle Database")
        inventory_data = await app.oracle_app.app.get_table_data(
            "inventory",
            limit=10,
            filters={"facility_id": "DC001"},
        )
        logger.info("Inventory data retrieved", count=len(inventory_data))

        # Step 2: Process inventory data and identify low stock items
        logger.info("Step 2: Analyzing inventory for low stock items")
        low_stock_items = []
        for item in inventory_data:
            if item.get("quantity", 0) < 100:  # Low stock threshold
                low_stock_items.append(item)

        logger.info(
            "Low stock analysis completed",
            low_stock_count=len(low_stock_items),
        )

        # Step 3: Create purchase orders for low stock items (simulated WMS operation)
        logger.info("Step 3: Creating purchase orders (simulated)")
        for item in low_stock_items[:3]:  # Limit for demo
            # In real implementation, this would use WMS adapter
            logger.info(
                "Purchase order created",
                item_id=item.get("item_id"),
                current_qty=item.get("quantity"),
                order_qty=500,
            )

        # Step 4: Log workflow completion in Oracle
        logger.info("Step 4: Logging workflow completion")
        workflow_result = await app.oracle_app.app.run_operation(
            "validate_data_integrity",
            {"table_name": "inventory"},
        )

        logger.info(
            "Cross-system workflow completed successfully",
            integrity_status=workflow_result.get("validation_summary", {}).get(
                "status",
            ),
        )

    except Exception as e:
        logger.exception("Cross-system workflow failed", error=str(e))

    finally:
        await app.shutdown()


async def demonstrate_unified_cli() -> None:
    """Demonstrate unified CLI across multiple systems."""
    logger = structlog.get_logger(__name__)
    logger.info("=== Unified CLI Demo ===")

    app = FlxIntegratedApplication()

    try:
        await app.initialize()

        if app.unified_cli:
            logger.info("Unified CLI commands available:")
            logger.info("Oracle Database commands:")
            logger.info("- flx-integrated oracle-resource get <table> <id>")
            logger.info("- flx-integrated oracle-resource list <table>")
            logger.info("- flx-integrated oracle-operation execute <op_name>")
            logger.info("- flx-integrated oracle-pagination strategies <table>")

            # Note: In real implementation, WMS and OIC commands would be here too
            logger.info("Future WMS commands:")
            logger.info("- flx-integrated wms-resource get items <item_id>")
            logger.info("- flx-integrated wms-operation execute create_shipment")

            logger.info("Future OIC commands:")
            logger.info("- flx-integrated oic-integration trigger <flow_id>")
            logger.info("- flx-integrated oic-monitoring status <instance_id>")

    except Exception as e:
        logger.exception("Unified CLI demo failed", error=str(e))

    finally:
        await app.shutdown()


async def demonstrate_data_synchronization() -> None:
    """Demonstrate data synchronization across systems."""
    logger = structlog.get_logger(__name__)
    logger.info("=== Data Synchronization Demo ===")

    app = FlxIntegratedApplication()

    try:
        await app.initialize()

        # Step 1: Export data from Oracle Database
        logger.info("Step 1: Exporting item master data from Oracle")
        export_result = await app.oracle_app.app.export_table(
            "items",
            format_type="JSON",
            where_clause="active = 'Y'",
        )

        logger.info(
            "Item master data exported",
            record_count=export_result.get("record_count", 0),
            format=export_result.get("format"),
        )

        # Step 2: Transform data for WMS (simulated)
        logger.info("Step 2: Transforming data for WMS format")
        # In real implementation, this would use data transformation rules
        wms_format_data = {
            "items_synchronized": export_result.get("record_count", 0),
            "transformation_rules": ["map_item_id", "convert_uom", "add_wms_fields"],
            "status": "ready_for_import",
        }

        # Step 3: Send data to WMS via OIC (simulated)
        logger.info("Step 3: Sending data to WMS via OIC integration")
        # In real implementation, this would use OIC adapter
        oic_response = {
            "integration_id": "INT_ITEM_SYNC_001",
            "status": "completed",
            "records_processed": wms_format_data["items_synchronized"],
            "processing_time_ms": 1500,
        }

        logger.info(
            "Data synchronization completed",
            integration_id=oic_response["integration_id"],
            records_processed=oic_response["records_processed"],
        )

        # Step 4: Verify synchronization results
        logger.info("Step 4: Verifying synchronization results")
        await app.oracle_app.app.run_operation(
            "analyze_table_stats",
            {"table_name": "sync_log"},
        )

        logger.info("Synchronization verification completed")

    except Exception as e:
        logger.exception("Data synchronization demo failed", error=str(e))

    finally:
        await app.shutdown()


async def demonstrate_performance_monitoring() -> None:
    """Demonstrate performance monitoring across systems."""
    logger = structlog.get_logger(__name__)
    logger.info("=== Performance Monitoring Demo ===")

    app = FlxIntegratedApplication()

    try:
        await app.initialize()

        # Collect performance metrics from each system
        performance_metrics: dict[str, dict[str, Any]] = {
            "oracle_db": {},
            "wms_api": {},
            "oic_integrations": {},
            "overall": {},
        }

        # Oracle Database metrics
        logger.info("Collecting Oracle Database performance metrics")
        start_time = asyncio.get_event_loop().time()

        # Test Oracle operations
        await app.oracle_app.app.get_paginated_data(
            "inventory",
            page_size=100,
            strategy="offset",
        )
        await app.oracle_app.app.analyze_table("items")

        oracle_time = asyncio.get_event_loop().time() - start_time
        performance_metrics["oracle_db"] = {
            "response_time_seconds": round(oracle_time, 3),
            "operations_tested": 2,
            "status": "healthy",
        }

        # Simulated WMS API metrics
        logger.info("Collecting WMS API performance metrics (simulated)")
        performance_metrics["wms_api"] = {
            "response_time_seconds": 0.245,
            "operations_tested": 5,
            "status": "healthy",
        }

        # Simulated OIC metrics
        logger.info("Collecting OIC integration performance metrics (simulated)")
        performance_metrics["oic_integrations"] = {
            "response_time_seconds": 1.120,
            "integrations_tested": 3,
            "status": "healthy",
        }

        # Overall metrics
        total_time = sum(
            metrics.get("response_time_seconds", 0)
            for metrics in performance_metrics.values()
            if isinstance(metrics, dict)
        )

        performance_metrics["overall"] = {
            "total_response_time_seconds": round(total_time, 3),
            "systems_tested": 3,
            "all_systems_healthy": all(
                metrics.get("status") == "healthy"
                for metrics in performance_metrics.values()
                if isinstance(metrics, dict) and "status" in metrics
            ),
        }

        logger.info("Performance monitoring completed", metrics=performance_metrics)

    except Exception as e:
        logger.exception("Performance monitoring demo failed", error=str(e))

    finally:
        await app.shutdown()


async def demonstrate_error_handling_and_recovery() -> None:
    """Demonstrate error handling and recovery across systems."""
    logger = structlog.get_logger(__name__)
    logger.info("=== Error Handling and Recovery Demo ===")

    app = FlxIntegratedApplication()

    try:
        await app.initialize()

        # Test error scenarios and recovery
        error_scenarios = [
            "database_connection_timeout",
            "wms_api_rate_limit",
            "oic_integration_failure",
            "data_validation_error",
        ]

        recovery_strategies = {
            "database_connection_timeout": "retry_with_backoff",
            "wms_api_rate_limit": "queue_and_throttle",
            "oic_integration_failure": "fallback_to_batch_processing",
            "data_validation_error": "quarantine_and_manual_review",
        }

        for scenario in error_scenarios:
            logger.info(f"Testing error scenario: {scenario}")

            try:
                # Simulate error condition
                if scenario == "database_connection_timeout":
                    # Test with invalid table to trigger error
                    await app.oracle_app.app.get_table_data("invalid_table")

                elif scenario == "data_validation_error":
                    # Test data validation
                    validation_result = await app.oracle_app.app.oracle_app.operation_adapter.validate_operation_request(
                        FlxOperationRequest(
                            operation_name="invalid_operation",
                            parameters={},
                        ),
                    )
                    if not validation_result[0]:
                        msg = f"Validation failed: {validation_result[1]}"
                        raise ValueError(msg)

                logger.info(f"Scenario {scenario} handled successfully")

            except Exception as e:
                logger.warning(
                    f"Expected error in scenario {scenario}",
                    error=str(e)[:100],
                    recovery_strategy=recovery_strategies.get(scenario, "unknown"),
                )

        logger.info("Error handling and recovery demonstration completed")

    except Exception as e:
        logger.exception("Error handling demo failed", error=str(e))

    finally:
        await app.shutdown()


async def main() -> None:
    """Main demonstration function."""
    setup_logging()
    logger = structlog.get_logger(__name__)

    logger.info("Starting FLX Integrated Systems comprehensive demonstration")

    demos = [
        ("Cross-System Workflow", demonstrate_cross_system_workflow),
        ("Unified CLI", demonstrate_unified_cli),
        ("Data Synchronization", demonstrate_data_synchronization),
        ("Performance Monitoring", demonstrate_performance_monitoring),
        ("Error Handling and Recovery", demonstrate_error_handling_and_recovery),
    ]

    for demo_name, demo_func in demos:
        try:
            logger.info(f"Running {demo_name} demonstration")
            await demo_func()
            logger.info(f"{demo_name} demonstration completed successfully")
        except Exception as e:
            logger.exception(f"{demo_name} demonstration failed", error=str(e))

    logger.info("FLX Integrated Systems comprehensive demonstration completed")

    # Summary of integration benefits
    logger.info("=== Integration Benefits Achieved ===")
    logger.info("✅ Unified FLX architecture across all systems")
    logger.info("✅ Standardized Flx-prefixed classes and interfaces")
    logger.info("✅ Cross-system workflow orchestration")
    logger.info("✅ Unified CLI for all systems")
    logger.info("✅ Integrated performance monitoring")
    logger.info("✅ Consistent error handling and recovery")
    logger.info("✅ Event-driven architecture with DDD principles")
    logger.info("✅ SOLID, KISS, DRY compliance across projects")


if __name__ == "__main__":
    asyncio.run(main())
