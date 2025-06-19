"""
Pipeline management endpoints.
"""

from typing import List, Optional
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies


import grpc
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from flx_api.dependencies import check_rate_limit, get_current_user, get_grpc_stub
from flx_api.models.pipeline import (
    ExecutionResponse,
    PipelineCreate,
    PipelineResponse,
    PipelineUpdate,
    RunPipelineRequest,
)
from google.protobuf import struct_pb2

# Lazy imports to avoid circular dependencies
flx_pb2 = lazy_import('flx.grpc.proto', 'flx_pb2')
flx_pb2_grpc = lazy_import('flx.grpc.proto', 'flx_pb2_grpc')

router = APIRouter()


@router.get("/", response_model=List[PipelineResponse])
async def list_pipelines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filter: Optional[str] = None,
    sort_by: Optional[str] = None,
    descending: bool = False,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: None = Depends(check_rate_limit),
):
    """List all pipelines."""
    try:
        request = flx_pb2.ListPipelinesRequest(
            offset=skip,
            limit=limit,
            filter=filter or "",
            sort_by=sort_by or "",
            descending=descending,
        )

        response = await stub.ListPipelines(request)

        return [
            PipelineResponse(
                id=str(p.id),
                name=p.name,
                description=p.description,
                extractor=p.extractor,
                loader=p.loader,
                transform=p.transform,
                schedule=p.schedule,
                is_active=p.is_active,
                created_by=p.created_by,
                created_at=p.created_at.ToDatetime(),
                updated_at=p.updated_at.ToDatetime(),
                last_status=p.last_status.name if p.last_status else None,
                last_run=p.last_run.ToDatetime() if p.HasField("last_run") else None,
            )
            for p in response.pipelines
        ]

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: str,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: None = Depends(check_rate_limit),
):
    """Get a specific pipeline."""
    try:
        request = flx_pb2.GetPipelineRequest(id=pipeline_id)
        pipeline = await stub.GetPipeline(request)

        return PipelineResponse(
            id=str(pipeline.id),
            name=pipeline.name,
            description=pipeline.description,
            extractor=pipeline.extractor,
            loader=pipeline.loader,
            transform=pipeline.transform,
            schedule=pipeline.schedule,
            is_active=pipeline.is_active,
            created_by=pipeline.created_by,
            created_at=pipeline.created_at.ToDatetime(),
            updated_at=pipeline.updated_at.ToDatetime(),
            last_status=pipeline.last_status.name if pipeline.last_status else None,
            last_run=(
                pipeline.last_run.ToDatetime()
                if pipeline.HasField("last_run")
                else None
            ),
        )

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline {pipeline_id} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.post("/", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    background_tasks: BackgroundTasks,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    current_user: dict = Depends(get_current_user),
):
    """Create a new pipeline."""
    try:
        request = flx_pb2.CreatePipelineRequest(
            name=pipeline_data.name,
            description=pipeline_data.description or "",
            extractor=pipeline_data.extractor,
            loader=pipeline_data.loader,
            transform=pipeline_data.transform or "",
            schedule=pipeline_data.schedule or "",
        )

        if pipeline_data.config:
            config_struct = struct_pb2.Struct()
            config_struct.update(pipeline_data.config)
            request.config.CopyFrom(config_struct)

        pipeline = await stub.CreatePipeline(request)

        # TODO: Schedule plugin installation in background

        return PipelineResponse(
            id=str(pipeline.id),
            name=pipeline.name,
            description=pipeline.description,
            extractor=pipeline.extractor,
            loader=pipeline.loader,
            transform=pipeline.transform,
            schedule=pipeline.schedule,
            is_active=pipeline.is_active,
            created_by=current_user["id"],
            created_at=pipeline.created_at.ToDatetime(),
            updated_at=pipeline.updated_at.ToDatetime(),
        )

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: str,
    pipeline_data: PipelineUpdate,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: dict = Depends(get_current_user),
):
    """Update an existing pipeline."""
    try:
        request = flx_pb2.UpdatePipelineRequest(id=pipeline_id)

        if pipeline_data.name is not None:
            request.name = pipeline_data.name
        if pipeline_data.description is not None:
            request.description = pipeline_data.description
        if pipeline_data.extractor is not None:
            request.extractor = pipeline_data.extractor
        if pipeline_data.loader is not None:
            request.loader = pipeline_data.loader
        if pipeline_data.transform is not None:
            request.transform = pipeline_data.transform
        if pipeline_data.schedule is not None:
            request.schedule = pipeline_data.schedule
        if pipeline_data.is_active is not None:
            request.is_active = pipeline_data.is_active
        if pipeline_data.config is not None:
            config_struct = struct_pb2.Struct()
            config_struct.update(pipeline_data.config)
            request.config.CopyFrom(config_struct)

        pipeline = await stub.UpdatePipeline(request)

        return PipelineResponse(
            id=str(pipeline.id),
            name=pipeline.name,
            description=pipeline.description,
            extractor=pipeline.extractor,
            loader=pipeline.loader,
            transform=pipeline.transform,
            schedule=pipeline.schedule,
            is_active=pipeline.is_active,
            created_by=pipeline.created_by,
            created_at=pipeline.created_at.ToDatetime(),
            updated_at=pipeline.updated_at.ToDatetime(),
        )

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline {pipeline_id} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: str,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: dict = Depends(get_current_user),
):
    """Delete a pipeline."""
    try:
        request = flx_pb2.DeletePipelineRequest(id=pipeline_id)
        await stub.DeletePipeline(request)

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline {pipeline_id} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.post("/{pipeline_id}/run", response_model=ExecutionResponse)
async def run_pipeline(
    pipeline_id: str,
    run_request: RunPipelineRequest,
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    current_user: dict = Depends(get_current_user),
):
    """Run a pipeline."""
    try:
        request = flx_pb2.RunPipelineRequest(
            pipeline_id=pipeline_id,
            full_refresh=run_request.full_refresh,
            env_vars=run_request.env_vars or {},
        )

        execution = await stub.RunPipeline(request)

        return ExecutionResponse(
            id=str(execution.id),
            pipeline_id=execution.pipeline_id,
            status=execution.status.name,
            started_at=execution.started_at.ToDatetime(),
            triggered_by=current_user["id"],
        )

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline {pipeline_id} not found",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.get("/{pipeline_id}/executions", response_model=List[ExecutionResponse])
async def list_pipeline_executions(
    pipeline_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
    _: None = Depends(check_rate_limit),
):
    """List executions for a pipeline."""
    try:
        request = flx_pb2.ListExecutionsRequest(
            pipeline_id=pipeline_id,
            offset=skip,
            limit=limit,
        )

        response = await stub.ListExecutions(request)

        return [
            ExecutionResponse(
                id=str(e.id),
                pipeline_id=e.pipeline_id,
                status=e.status.name,
                started_at=e.started_at.ToDatetime(),
                finished_at=(
                    e.finished_at.ToDatetime() if e.HasField("finished_at") else None
                ),
                duration_seconds=e.duration_seconds if e.duration_seconds else None,
                error_message=e.error_message if e.error_message else None,
                records_processed=e.records_processed if e.records_processed else None,
                triggered_by=e.triggered_by,
            )
            for e in response.executions
        ]

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )
