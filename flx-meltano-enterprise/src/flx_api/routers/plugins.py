"""
Plugin management endpoints.
"""

from typing import List, Optional
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies


import grpc
from fastapi import APIRouter, Depends, HTTPException, status
from flx_api.dependencies import check_rate_limit, get_current_user, get_grpc_stub
from flx_api.models.plugin import PluginInstallRequest, PluginResponse

# Lazy imports to avoid circular dependencies
flx_pb2 = lazy_import('flx.grpc.proto', 'flx_pb2')
flx_pb2_grpc = lazy_import('flx.grpc.proto', 'flx_pb2_grpc')

router = APIRouter()


@router.get("/", response_model=List[PluginResponse])
async def list_plugins(
    plugin_type: Optional[str] = None,
    installed_only: bool = False,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: None = Depends(check_rate_limit),
):
    """List available plugins."""
    try:
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

        return [
            PluginResponse(
                name=p.name,
                type=p.type.name.replace("PLUGIN_TYPE_", "").lower(),
                variant=p.variant,
                version=p.version,
                description=p.description,
                installed=p.installed,
                installed_at=(
                    p.installed_at.ToDatetime() if p.HasField("installed_at") else None
                ),
            )
            for p in response.plugins
        ]

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.post("/install", response_model=PluginResponse)
async def install_plugin(
    plugin_data: PluginInstallRequest,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: dict = Depends(get_current_user),
):
    """Install a plugin."""
    try:
        type_map = {
            "extractor": flx_pb2.PLUGIN_TYPE_EXTRACTOR,
            "loader": flx_pb2.PLUGIN_TYPE_LOADER,
            "transformer": flx_pb2.PLUGIN_TYPE_TRANSFORMER,
            "orchestrator": flx_pb2.PLUGIN_TYPE_ORCHESTRATOR,
            "utility": flx_pb2.PLUGIN_TYPE_UTILITY,
        }

        request = flx_pb2.InstallPluginRequest(
            name=plugin_data.name,
            type=type_map[plugin_data.type],
            variant=plugin_data.variant or "",
        )

        plugin = await stub.InstallPlugin(request)

        return PluginResponse(
            name=plugin.name,
            type=plugin.type.name.replace("PLUGIN_TYPE_", "").lower(),
            variant=plugin.variant,
            version=plugin.version,
            description=plugin.description,
            installed=plugin.installed,
        )

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.delete(
    "/uninstall/{plugin_type}/{plugin_name}", status_code=status.HTTP_204_NO_CONTENT
)
async def uninstall_plugin(
    plugin_type: str,
    plugin_name: str,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: dict = Depends(get_current_user),
):
    """Uninstall a plugin."""
    try:
        type_map = {
            "extractor": flx_pb2.PLUGIN_TYPE_EXTRACTOR,
            "loader": flx_pb2.PLUGIN_TYPE_LOADER,
            "transformer": flx_pb2.PLUGIN_TYPE_TRANSFORMER,
            "orchestrator": flx_pb2.PLUGIN_TYPE_ORCHESTRATOR,
            "utility": flx_pb2.PLUGIN_TYPE_UTILITY,
        }

        if plugin_type not in type_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plugin type: {plugin_type}",
            )

        request = flx_pb2.UninstallPluginRequest(
            name=plugin_name,
            type=type_map[plugin_type],
        )

        await stub.UninstallPlugin(request)

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )
