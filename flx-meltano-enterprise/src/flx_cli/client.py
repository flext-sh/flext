"""
gRPC client for FLX CLI.
"""

from typing import Any, AsyncIterator, Dict, List, Optional

import grpc
from google.protobuf import empty_pb2

# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies



# Lazy imports to avoid circular dependencies
flx_pb2 = lazy_import("flx.grpc.proto", "flx_pb2")
flx_pb2_grpc = lazy_import("flx.grpc.proto", "flx_pb2_grpc")


class AuthInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Client interceptor for authentication."""

    def __init__(self, token: Optional[str]):
        self.token = token

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Add authentication token to requests."""
        if self.token:
            metadata = list(client_call_details.metadata or [])
            metadata.append(("authorization", f"Bearer {self.token}"))

            client_call_details = client_call_details._replace(metadata=metadata)

        return await continuation(client_call_details, request)


class FlxGrpcClient:
    """gRPC client for FLX daemon."""

    def __init__(self, host: str, port: int, token: Optional[str] = None):
        """Initialize client."""
        self.address = f"{host}:{port}"
        self.token = token
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[flx_pb2_grpc.FlxServiceStub] = None

    async def _get_channel(self) -> grpc.aio.Channel:
        """Get or create gRPC channel."""
        if not self._channel:
            interceptors = []
            if self.token:
                interceptors.append(AuthInterceptor(self.token))

            self._channel = grpc.aio.insecure_channel(
                self.address,
                options=[
                    ("grpc.max_receive_message_length", 100 * 1024 * 1024),
                    ("grpc.max_send_message_length", 100 * 1024 * 1024),
                    ("grpc.keepalive_time_ms", 10000),
                    ("grpc.keepalive_timeout_ms", 5000),
                ],
                interceptors=interceptors,
            )

        return self._channel

    async def _get_stub(self) -> flx_pb2_grpc.FlxServiceStub:
        """Get or create gRPC stub."""
        if not self._stub:
            channel = await self._get_channel()
            self._stub = flx_pb2_grpc.FlxServiceStub(channel)

        return self._stub

    async def close(self):
        """Close gRPC channel."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            self._stub = None

    # System methods

    async def get_system_info(self) -> flx_pb2.SystemInfo:
        """Get system information."""
        stub = await self._get_stub()
        return await stub.GetSystemInfo(empty_pb2.Empty())

    async def get_system_stats(self) -> flx_pb2.SystemStats:
        """Get system statistics."""
        stub = await self._get_stub()
        return await stub.GetSystemStats(empty_pb2.Empty())

    async def health_check(self) -> flx_pb2.HealthStatus:
        """Check system health."""
        stub = await self._get_stub()
        return await stub.HealthCheck(empty_pb2.Empty())

    # Pipeline methods

    async def list_pipelines(
        self,
        limit: int = 100,
        offset: int = 0,
        filter: Optional[str] = None,
    ) -> List[flx_pb2.Pipeline]:
        """List pipelines."""
        stub = await self._get_stub()

        request = flx_pb2.ListPipelinesRequest(
            limit=limit,
            offset=offset,
            filter=filter or "",
        )

        response = await stub.ListPipelines(request)
        return list(response.pipelines)

    async def get_pipeline(self, pipeline_id: str) -> flx_pb2.Pipeline:
        """Get pipeline by ID."""
        stub = await self._get_stub()

        request = flx_pb2.GetPipelineRequest(id=pipeline_id)
        return await stub.GetPipeline(request)

    async def create_pipeline(
        self,
        name: str,
        extractor: str,
        loader: str,
        transform: Optional[str] = None,
        description: Optional[str] = None,
        schedule: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> flx_pb2.Pipeline:
        """Create a new pipeline."""
        stub = await self._get_stub()

        request = flx_pb2.CreatePipelineRequest(
            name=name,
            extractor=extractor,
            loader=loader,
            transform=transform or "",
            description=description or "",
            schedule=schedule or "",
        )

        if config:
            request.config.update(config)

        return await stub.CreatePipeline(request)

    async def update_pipeline(
        self,
        pipeline_id: str,
        **kwargs,
    ) -> flx_pb2.Pipeline:
        """Update pipeline."""
        stub = await self._get_stub()

        request = flx_pb2.UpdatePipelineRequest(id=pipeline_id)

        # Set fields from kwargs
        for field, value in kwargs.items():
            if hasattr(request, field) and value is not None:
                setattr(request, field, value)

        return await stub.UpdatePipeline(request)

    async def delete_pipeline(self, pipeline_id: str) -> None:
        """Delete pipeline."""
        stub = await self._get_stub()

        request = flx_pb2.DeletePipelineRequest(id=pipeline_id)
        await stub.DeletePipeline(request)

    async def run_pipeline(
        self,
        pipeline_id: str,
        full_refresh: bool = False,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> flx_pb2.Execution:
        """Run a pipeline."""
        stub = await self._get_stub()

        request = flx_pb2.RunPipelineRequest(
            pipeline_id=pipeline_id,
            full_refresh=full_refresh,
            env_vars=env_vars or {},
        )

        return await stub.RunPipeline(request)

    # Execution methods

    async def get_execution(self, execution_id: str) -> flx_pb2.Execution:
        """Get execution details."""
        stub = await self._get_stub()

        request = flx_pb2.GetExecutionRequest(id=execution_id)
        return await stub.GetExecution(request)

    async def list_executions(
        self,
        pipeline_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[flx_pb2.Execution]:
        """List executions."""
        stub = await self._get_stub()

        request = flx_pb2.ListExecutionsRequest(
            pipeline_id=pipeline_id or "",
            limit=limit,
            offset=offset,
        )

        response = await stub.ListExecutions(request)
        return list(response.executions)

    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a running execution."""
        stub = await self._get_stub()

        request = flx_pb2.CancelExecutionRequest(id=execution_id)
        await stub.CancelExecution(request)

    async def stream_execution(
        self,
        execution_id: str,
    ) -> AsyncIterator[flx_pb2.ExecutionUpdate]:
        """Stream execution updates."""
        stub = await self._get_stub()

        request = flx_pb2.StreamExecutionRequest(execution_id=execution_id)

        async for update in stub.StreamExecution(request):
            yield update

    # Plugin methods

    async def list_plugins(
        self,
        plugin_type: Optional[str] = None,
        installed_only: bool = False,
    ) -> List[flx_pb2.Plugin]:
        """List plugins."""
        stub = await self._get_stub()

        type_map = {
            "extractor": flx_pb2.PLUGIN_TYPE_EXTRACTOR,
            "loader": flx_pb2.PLUGIN_TYPE_LOADER,
            "transformer": flx_pb2.PLUGIN_TYPE_TRANSFORMER,
            "orchestrator": flx_pb2.PLUGIN_TYPE_ORCHESTRATOR,
            "utility": flx_pb2.PLUGIN_TYPE_UTILITY,
        }

        request = flx_pb2.ListPluginsRequest(
            type=type_map.get(plugin_type, flx_pb2.PLUGIN_TYPE_UNSPECIFIED),
            installed_only=installed_only,
        )

        response = await stub.ListPlugins(request)
        return list(response.plugins)

    async def install_plugin(
        self,
        name: str,
        plugin_type: str,
        variant: Optional[str] = None,
    ) -> flx_pb2.Plugin:
        """Install a plugin."""
        stub = await self._get_stub()

        type_map = {
            "extractor": flx_pb2.PLUGIN_TYPE_EXTRACTOR,
            "loader": flx_pb2.PLUGIN_TYPE_LOADER,
            "transformer": flx_pb2.PLUGIN_TYPE_TRANSFORMER,
            "orchestrator": flx_pb2.PLUGIN_TYPE_ORCHESTRATOR,
            "utility": flx_pb2.PLUGIN_TYPE_UTILITY,
        }

        request = flx_pb2.InstallPluginRequest(
            name=name,
            type=type_map[plugin_type],
            variant=variant or "",
        )

        return await stub.InstallPlugin(request)

    async def uninstall_plugin(
        self,
        name: str,
        plugin_type: str,
    ) -> None:
        """Uninstall a plugin."""
        stub = await self._get_stub()

        type_map = {
            "extractor": flx_pb2.PLUGIN_TYPE_EXTRACTOR,
            "loader": flx_pb2.PLUGIN_TYPE_LOADER,
            "transformer": flx_pb2.PLUGIN_TYPE_TRANSFORMER,
            "orchestrator": flx_pb2.PLUGIN_TYPE_ORCHESTRATOR,
            "utility": flx_pb2.PLUGIN_TYPE_UTILITY,
        }

        request = flx_pb2.UninstallPluginRequest(
            name=name,
            type=type_map[plugin_type],
        )

        await stub.UninstallPlugin(request)

    # State methods

    async def get_state(self, state_id: str) -> Dict[str, Any]:
        """Get pipeline state."""
        stub = await self._get_stub()

        request = flx_pb2.GetStateRequest(id=state_id)
        response = await stub.GetState(request)

        # Convert protobuf Struct to dict
        return dict(response.data)

    async def set_state(self, state_id: str, state_data: Dict[str, Any]) -> None:
        """Set pipeline state."""
        stub = await self._get_stub()

        request = flx_pb2.SetStateRequest(id=state_id)
        request.data.update(state_data)

        await stub.SetState(request)

    async def clear_state(self, state_id: str) -> None:
        """Clear pipeline state."""
        stub = await self._get_stub()

        request = flx_pb2.ClearStateRequest(id=state_id)
        await stub.ClearState(request)
