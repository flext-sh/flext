"""
FLX Core Daemon implementation.

This is the main daemon process that manages all FLX operations, providing
gRPC interface, event processing, and integration with Meltano.
"""

import asyncio
import signal
import sys
from concurrent import futures
from typing import Optional

import grpc
import structlog
import uvloop
from grpc_reflection.v1alpha import reflection
from prometheus_client import start_http_server

# Conditional imports to avoid circular dependencies
try:
    from flx.config import settings
except ImportError:
    settings = None

try:
    from flx.engine.meltano_wrapper import MeltanoEngine
except ImportError:
    MeltanoEngine = None

try:
    from flx.events.event_bus import EventBus
except ImportError:
    EventBus = None

try:
    from flx.grpc.proto import flx_pb2, flx_pb2_grpc
except ImportError:
    flx_pb2 = None
    flx_pb2_grpc = None

try:
    from flx.grpc.server import FlxGrpcServer
except ImportError:
    FlxGrpcServer = None

try:
    from flx.monitoring.health import HealthChecker
except ImportError:
    HealthChecker = None

try:
    from flx.monitoring.metrics import MetricsCollector
except ImportError:
    MetricsCollector = None

try:
    from flx.monitoring.tracing import setup_tracing
except ImportError:
    setup_tracing = None

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        (
            structlog.dev.ConsoleRenderer()
            if settings.debug
            else structlog.processors.JSONRenderer()
        ),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class FlxDaemon:
    """Main FLX daemon coordinating all services."""

    def __init__(self) -> None:
        """Initialize daemon components."""
        self.logger = logger.bind(component="daemon")
        self.event_bus = EventBus()
        self.meltano_engine = MeltanoEngine(settings.meltano_project_root)
        self.metrics = MetricsCollector()
        self.health_checker = HealthChecker()
        self.grpc_server: Optional[grpc.aio.Server] = None
        self._shutdown_event = asyncio.Event()
        self._tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        """Start the daemon and all services."""
        self.logger.info("Starting FLX daemon", version=settings.environment)

        try:
            # Setup tracing if enabled
            if settings.tracing_enabled:
                setup_tracing(settings)

            # Start metrics server
            self._start_metrics_server()

            # Initialize components
            await self._initialize_components()

            # Start gRPC server
            await self._start_grpc_server()

            # Register signal handlers
            self._register_signal_handlers()

            # Start background tasks
            self._start_background_tasks()

            self.logger.info(
                "FLX daemon started successfully",
                grpc_port=settings.grpc_port,
                metrics_port=settings.metrics_port,
            )

            # Wait for shutdown signal
            await self._shutdown_event.wait()

        except Exception as e:
            self.logger.error("Failed to start daemon", error=str(e))
            raise
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Gracefully shutdown the daemon."""
        self.logger.info("Shutting down FLX daemon")

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)

        # Stop gRPC server
        if self.grpc_server:
            await self.grpc_server.stop(grace=5)

        # Cleanup components
        await self._cleanup_components()

        self.logger.info("FLX daemon shutdown complete")

    def _start_metrics_server(self) -> None:
        """Start Prometheus metrics server."""
        start_http_server(settings.metrics_port)
        self.logger.info("Metrics server started", port=settings.metrics_port)

    async def _initialize_components(self) -> None:
        """Initialize all daemon components."""
        self.logger.info("Initializing components")

        # Initialize event bus
        await self.event_bus.start()

        # Initialize Meltano engine
        await self.meltano_engine.initialize()

        # Initialize health checker
        await self.health_checker.initialize()

        self.logger.info("Components initialized successfully")

    async def _cleanup_components(self) -> None:
        """Cleanup all daemon components."""
        self.logger.info("Cleaning up components")

        await self.event_bus.stop()
        await self.meltano_engine.cleanup()
        await self.health_checker.cleanup()

        self.logger.info("Components cleaned up successfully")

    async def _start_grpc_server(self) -> None:
        """Start the gRPC server."""
        self.logger.info("Starting gRPC server", port=settings.grpc_port)

        # Create server with interceptors
        interceptors = self._get_grpc_interceptors()
        self.grpc_server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=settings.grpc_max_workers),
            interceptors=interceptors,
            options=[
                ("grpc.max_send_message_length", settings.grpc_max_message_length),
                ("grpc.max_receive_message_length", settings.grpc_max_message_length),
                ("grpc.keepalive_time_ms", 10000),
                ("grpc.keepalive_timeout_ms", 5000),
                ("grpc.keepalive_permit_without_calls", True),
                ("grpc.http2.max_pings_without_data", 0),
                ("grpc.http2.min_time_between_pings_ms", 10000),
            ],
        )

        # Add service implementation
        service = FlxGrpcServer(
            daemon=self,
            event_bus=self.event_bus,
            meltano_engine=self.meltano_engine,
            health_checker=self.health_checker,
        )
        flx_pb2_grpc.add_FlxServiceServicer_to_server(service, self.grpc_server)

        # Enable reflection for debugging
        SERVICE_NAMES = (
            flx_pb2.DESCRIPTOR.services_by_name["FlxService"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, self.grpc_server)

        # Start server
        listen_addr = f"[::]:{settings.grpc_port}"
        self.grpc_server.add_insecure_port(listen_addr)
        await self.grpc_server.start()

        self.logger.info("gRPC server started", address=listen_addr)

    def _get_grpc_interceptors(self) -> list[grpc.aio.ServerInterceptor]:
        """Get gRPC server interceptors."""
        interceptors = []

        # Add monitoring interceptor if available
        try:
            from flx.grpc.interceptors import MetricsInterceptor, TracingInterceptor

            interceptors.append(MetricsInterceptor())
        except ImportError:
            pass

        if settings and settings.tracing_enabled:
            try:
                from flx.grpc.interceptors import TracingInterceptor

                interceptors.append(TracingInterceptor())
            except ImportError:
                pass

        return interceptors

    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._handle_signal)

        self.logger.info("Signal handlers registered")

    def _handle_signal(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        self.logger.info("Received shutdown signal", signal=signum)
        self._shutdown_event.set()

    def _start_background_tasks(self) -> None:
        """Start background tasks."""
        self._tasks.append(asyncio.create_task(self._health_check_loop()))
        self._tasks.append(asyncio.create_task(self._metrics_collection_loop()))

        self.logger.info("Background tasks started", count=len(self._tasks))

    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while not self._shutdown_event.is_set():
            try:
                await self.health_checker.check_all()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Health check failed", error=str(e))
                await asyncio.sleep(60)  # Back off on error

    async def _metrics_collection_loop(self) -> None:
        """Periodic metrics collection loop."""
        while not self._shutdown_event.is_set():
            try:
                await self.metrics.collect_system_metrics()
                await asyncio.sleep(10)  # Collect every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Metrics collection failed", error=str(e))
                await asyncio.sleep(30)  # Back off on error


async def async_main() -> None:
    """Main entry point."""
    # Use uvloop for better performance
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Create and start daemon
    daemon = FlxDaemon()
    await daemon.start()


def main() -> None:
    """Run the daemon."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Daemon interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Daemon failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
