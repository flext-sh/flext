#!/usr/bin/env python3
"""Standalone REST API server demonstrating CLI-to-HTTP exposure."""

import asyncio
import inspect
import sys
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "flx" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "examples"))

# Import plugin directly to register commands

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    sys.exit(1)

# Import only what we need from FLX
from flx.adapters.inbound.fire_cli import _command_groups, _dynamic_commands


class CommandRequest(BaseModel):
    """Request model for command execution."""

    parameters: dict[str, Any] = Field(default_factory=dict)


class CommandResponse(BaseModel):
    """Response model for command results."""

    success: bool
    data: Any
    error: str | None = None
    execution_time_ms: float


def create_standalone_api() -> FastAPI:
    """Create standalone REST API without full FLX imports."""

    app = FastAPI(
        title="FLX Framework REST API Demo",
        description="Demonstration of CLI commands exposed via REST API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    async def execute_plugin_command(command_func: Any, **kwargs) -> CommandResponse:
        """Execute a plugin command and return structured response."""
        import time

        start_time = time.time()

        try:
            if inspect.iscoroutinefunction(command_func):
                result = await command_func(**kwargs)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: command_func(**kwargs)
                )

            execution_time = (time.time() - start_time) * 1000

            return CommandResponse(
                success=True, data=result, execution_time_ms=execution_time
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return CommandResponse(
                success=False, data=None, error=str(e), execution_time_ms=execution_time
            )

    @app.get("/")
    async def root() -> dict[str, Any]:
        """Root endpoint."""
        return {
            "message": "FLX Framework REST API Demo",
            "docs": "/docs",
            "available_plugins": list(_command_groups.keys()),
            "dynamic_commands": list(_dynamic_commands.keys()),
        }

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check."""
        return {"status": "healthy", "service": "flx-rest-api-demo"}

    # Plugin command routes
    @app.get("/api/v1/database/status")
    async def database_status() -> Any:
        """Get database status."""
        if "database" in _command_groups:
            db_class = _command_groups["database"]
            db_instance = db_class()
            return await execute_plugin_command(db_instance.status)
        raise HTTPException(status_code=404, detail="Database plugin not found")

    @app.post("/api/v1/database/backup")
    async def database_backup(request: CommandRequest) -> Any:
        """Create database backup."""
        if "database" in _command_groups:
            db_class = _command_groups["database"]
            db_instance = db_class()

            path = request.parameters.get("path")
            compress = request.parameters.get("compress", True)

            if not path:
                raise HTTPException(status_code=400, detail="path parameter required")

            return await execute_plugin_command(
                db_instance.backup, path=path, compress=compress
            )
        raise HTTPException(status_code=404, detail="Database plugin not found")

    @app.post("/api/v1/database/restore")
    async def database_restore(request: CommandRequest) -> Any:
        """Restore database from backup."""
        if "database" in _command_groups:
            db_class = _command_groups["database"]
            db_instance = db_class()

            backup_path = request.parameters.get("backup_path")
            force = request.parameters.get("force", False)

            if not backup_path:
                raise HTTPException(
                    status_code=400, detail="backup_path parameter required"
                )

            return await execute_plugin_command(
                db_instance.restore, backup_path=backup_path, force=force
            )
        raise HTTPException(status_code=404, detail="Database plugin not found")

    @app.get("/api/v1/monitoring/alerts")
    async def monitoring_alerts(severity: str = Query("all")) -> Any:
        """Get monitoring alerts."""
        if "monitoring" in _command_groups:
            mon_class = _command_groups["monitoring"]
            mon_instance = mon_class()
            return await execute_plugin_command(mon_instance.alerts, severity=severity)
        raise HTTPException(status_code=404, detail="Monitoring plugin not found")

    @app.get("/api/v1/monitoring/metrics")
    async def monitoring_metrics(
        component: str = Query("all"), duration: str = Query("1h")
    ) -> Any:
        """Get monitoring metrics."""
        if "monitoring" in _command_groups:
            mon_class = _command_groups["monitoring"]
            mon_instance = mon_class()
            return await execute_plugin_command(
                mon_instance.metrics, component=component, duration=duration
            )
        raise HTTPException(status_code=404, detail="Monitoring plugin not found")

    @app.get("/api/v1/monitoring/health-check")
    async def monitoring_health_check() -> Any:
        """Run health check."""
        if "monitoring" in _command_groups:
            mon_class = _command_groups["monitoring"]
            mon_instance = mon_class()
            return await execute_plugin_command(mon_instance.health_check)
        raise HTTPException(status_code=404, detail="Monitoring plugin not found")

    @app.post("/api/v1/system-report")
    async def system_report(request: CommandRequest) -> Any:
        """Generate system report."""
        if "system-report" in _dynamic_commands:
            func = _dynamic_commands["system-report"]
            format_type = request.parameters.get("format", "json")
            output = request.parameters.get("output")
            return await execute_plugin_command(func, format=format_type, output=output)
        raise HTTPException(status_code=404, detail="System report command not found")

    @app.get("/api/v1/info")
    async def api_info() -> dict[str, Any]:
        """Get API information."""
        return {
            "name": "FLX Framework REST API Demo",
            "version": "1.0.0",
            "description": "Demonstration of CLI commands exposed via REST API",
            "available_endpoints": [
                "GET /",
                "GET /health",
                "GET /api/v1/info",
                "GET /api/v1/database/status",
                "POST /api/v1/database/backup",
                "POST /api/v1/database/restore",
                "GET /api/v1/monitoring/alerts",
                "GET /api/v1/monitoring/metrics",
                "GET /api/v1/monitoring/health-check",
                "POST /api/v1/system-report",
            ],
            "plugin_commands": list(_command_groups.keys()),
            "dynamic_commands": list(_dynamic_commands.keys()),
        }

    return app


def main() -> None:
    """Main function to run the server."""

    app = create_standalone_api()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")


if __name__ == "__main__":
    main()
