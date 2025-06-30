# Meltano Integration into FLEXT Framework - Implementation Plan

**Function**: Strategic implementation plan for complete Meltano data pipeline integration within the FLEXT framework
**Audience**: Technical architects, data engineers, and development teams implementing data platforms
**Status**: Comprehensive Implementation Roadmap - Production Planning

---

## Navigation Context

**Current Location**: `docs/guides/integration/meltano-flext-integration-plan.md`
**Parent**: [Integration Hub](index.md) > Meltano Integration
**Quick Links**: [Framework Integration](meltano-framework-integration.md) | [Plugins Integration](meltano-plugins-integration.md) | [Architecture](../../architecture/index.md)

---

## 🎯 Executive Summary

This document outlines the step-by-step plan to integrate Meltano's complete data pipeline functionality into the FLEXT framework, enabling the system to run as a containerized service with web interface and daemon mode capabilities. This integration positions FLEXT as a comprehensive enterprise data platform combining hexagonal architecture principles with modern data pipeline orchestration.

### **Strategic Objectives**

- **Complete Meltano Integration**: All ELT functionality within FLEXT framework
- **Container-Native**: Full Docker support with orchestration capabilities
- **Web Interface**: Professional dashboard for pipeline management
- **Daemon Mode**: Background service operation with monitoring
- **Enterprise Ready**: Production-grade data platform capabilities

---

## 📊 Current State Analysis

### **FLEXT Framework Status**

- ✅ **Hexagonal Architecture**: Complete implementation with adapters
- ✅ **Modern Python**: Python 3.13 with advanced type safety
- ✅ **Observability**: Comprehensive logging, metrics, tracing
- ✅ **Configuration**: Standardized Pydantic-based configuration
- ✅ **Error Handling**: Rich context with correlation IDs

### **Meltano Dependencies Already Available**

```toml
# From flext/pyproject.toml - Already integrated!
meltano = "3.7.8"
singer-sdk = "^0.46.4"
```

### **Infrastructure Components Present**

- **CLI Framework**: Cyclopts-based CLI ready for extension
- **Async Framework**: AnyIO and asyncio patterns established
- **Configuration Management**: Pydantic v2 with environment handling
- **HTTP Infrastructure**: aiohttp available (can be enhanced with FastAPI)
- **Task Processing**: Dramatiq available (can be migrated to Celery)

---

## 🏗️ Architecture Design

### **Meltano-FLEXT Integration Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT Enterprise Platform                     │
├─────────────────────────────────────────────────────────────────┤
│  Web Interface (FastAPI + Rich Dashboard)                      │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────┐  │
│  │ Pipeline    │ Jobs        │ Monitoring  │ Configuration   │  │
│  │ Management  │ Dashboard   │ & Alerts    │ & Settings      │  │
│  └─────────────┴─────────────┴─────────────┴─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  FLEXT Core Application Layer                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              Meltano Integration Service                    │  │
│  │  ┌───────────┬────────────┬───────────┬─────────────────┐  │  │
│  │  │ Pipeline  │ Project    │ Scheduler │ State           │  │  │
│  │  │ Orchestr. │ Manager    │ Service   │ Management      │  │  │
│  │  └───────────┴────────────┴───────────┴─────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  FLEXT Adapter Layer (Hexagonal Architecture)                    │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────┐  │
│  │ Meltano     │ Singer      │ File System │ State Store     │  │
│  │ CLI Adapter │ SDK Adapter │ Adapter     │ Adapter         │  │
│  └─────────────┴─────────────┴─────────────┴─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────┐  │
│  │ Docker      │ Task Queue  │ File        │ Database        │  │
│  │ Container   │ (Celery)    │ Storage     │ (SQLite/PG)     │  │
│  └─────────────┴─────────────┴─────────────┴─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### **Integration Points**

#### **1. Meltano Core Integration**

```python
# New FLEXT Domain Service
class MeltanoOrchestrationService:
    """Domain service for Meltano pipeline orchestration."""

    async def create_project(self, config: MeltanoProjectConfig) -> MeltanoProject
    async def run_pipeline(self, pipeline_id: str, params: dict) -> PipelineRun
    async def schedule_pipeline(self, pipeline_id: str, schedule: Schedule) -> ScheduledPipeline
    async def get_run_status(self, run_id: str) -> RunStatus
```

#### **2. FLEXT Adapter Implementation**

```python
# Meltano CLI Adapter (Outbound)
class MeltanoCLIAdapter(
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin,
    BaseAdapter
):
    """Adapter for Meltano CLI operations."""

    async def execute_meltano_command(self, command: str, **kwargs) -> CommandResult
    async def get_project_state(self, project_path: str) -> ProjectState
```

---

## 📋 Phase 1: Meltano Core Integration (Weeks 1-4)

### **Week 1: Foundation Setup**

#### **Day 1-2: Project Structure**

```bash
# Create Meltano integration structure
mkdir -p flext/src/flext/domain/meltano
mkdir -p flext/src/flext/application/meltano
mkdir -p flext/src/flext/adapters/outbound/meltano
mkdir -p flext/src/flext/infra/meltano
mkdir -p flext/src/flext/cli/meltano
```

#### **Day 3-5: Domain Model Implementation**

```python
# flext/src/flext/domain/meltano/entities.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class MeltanoProject:
    name: str
    path: str
    config: Dict[str, Any]
    extractors: List[str]
    loaders: List[str]
    created_at: datetime

@dataclass
class PipelineRun:
    id: str
    project: MeltanoProject
    pipeline_name: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
```

#### **Day 6-7: Core Service Implementation**

```python
# flext/src/flext/application/meltano/service.py
from flext.core.application import ApplicationService
from flext.domain.meltano.entities import MeltanoProject, PipelineRun
from flext.ports.outbound.meltano import MeltanoPort

class MeltanoOrchestrationService(ApplicationService):
    """Application service for Meltano pipeline orchestration."""

    def __init__(self, meltano_adapter: MeltanoPort):
        self.meltano_adapter = meltano_adapter

    async def create_project(self, config: MeltanoProjectConfig) -> MeltanoProject:
        """Create new Meltano project with validation."""
        async with self.observe_operation("create_meltano_project", project_name=config.name):
            # Validate configuration
            await self._validate_project_config(config)

            # Create project via adapter
            project = await self.meltano_adapter.create_project(config)

            # Initialize default settings
            await self._initialize_project_defaults(project)

            return project
```

### **Week 2: Adapter Implementation**

#### **Day 8-10: Meltano CLI Adapter**

```python
# flext/src/flext/adapters/outbound/meltano/cli_adapter.py
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class MeltanoCLIAdapter(
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin,
    BaseAdapter
):
    """Adapter for Meltano CLI operations."""

    async def create_project(self, config: MeltanoProjectConfig) -> MeltanoProject:
        """Create new Meltano project."""
        async with self.observe_operation("meltano_create_project"):
            command = [
                "meltano", "init",
                "--project_directory", str(config.path),
                config.name
            ]

            result = await self._execute_command(command)

            if result.returncode != 0:
                raise MeltanoOperationError(
                    f"Failed to create project {config.name}",
                    context={"command": command, "stderr": result.stderr}
                )

            return await self._load_project(config.path)

    async def run_pipeline(self, project_path: Path, pipeline: str, **kwargs) -> PipelineRun:
        """Execute Meltano pipeline."""
        async with self.observe_operation("meltano_run_pipeline", pipeline=pipeline):
            command = ["meltano", "--project_directory", str(project_path), "run", pipeline]

            # Add additional parameters
            for key, value in kwargs.items():
                command.extend([f"--{key}", str(value)])

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )

            # Stream output for real-time monitoring
            run = PipelineRun(
                id=self._generate_run_id(),
                pipeline_name=pipeline,
                status=PipelineStatus.RUNNING,
                started_at=datetime.now()
            )

            # Monitor process
            await self._monitor_pipeline_execution(process, run)

            return run
```

#### **Day 11-14: Singer SDK Integration**

```python
# flext/src/flext/adapters/outbound/meltano/singer_adapter.py
from singer_sdk import Tap, Target
from singer_sdk.streams import Stream

class SingerSDKAdapter(
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin,
    BaseAdapter
):
    """Adapter for Singer SDK operations."""

    async def discover_streams(self, tap_config: Dict[str, Any]) -> List[Stream]:
        """Discover available streams from tap."""
        async with self.observe_operation("singer_discover_streams"):
            # Initialize tap with configuration
            tap = self._create_tap_instance(tap_config)

            # Run discovery
            catalog = await self._run_discovery(tap)

            return catalog.streams

    async def extract_data(self, tap_config: Dict[str, Any], selected_streams: List[str]) -> AsyncIterator[Dict[str, Any]]:
        """Extract data from source using Singer tap."""
        async with self.observe_operation("singer_extract_data", streams=selected_streams):
            tap = self._create_tap_instance(tap_config)

            # Configure selected streams
            catalog = await self._build_catalog(tap, selected_streams)

            # Stream data
            async for record in tap.sync_all(catalog):
                yield record
```

### **Week 3: Configuration & State Management**

#### **Day 15-17: Configuration Integration**

```python
# flext/src/flext/adapters/mixins/meltano_configuration.py
from pydantic import Field, validator
from pathlib import Path
from typing import Dict, List, Optional

class MeltanoConfigurationMixin(BaseModel):
    """Meltano-specific configuration mixin."""

    # Project Configuration
    project_directory: Path = Field(
        default=Path("./meltano_projects"),
        description="Base directory for Meltano projects"
    )

    default_project_name: str = Field(
        default="flext_data_platform",
        description="Default project name for new installations"
    )

    # Pipeline Configuration
    default_extractors: List[str] = Field(
        default_factory=lambda: ["tap-csv", "tap-postgres"],
        description="Default extractors to install"
    )

    default_loaders: List[str] = Field(
        default_factory=lambda: ["target-postgres", "target-csv"],
        description="Default loaders to install"
    )

    # Execution Configuration
    max_concurrent_runs: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum concurrent pipeline runs"
    )

    pipeline_timeout_minutes: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Default pipeline timeout in minutes"
    )

    # State Storage Configuration
    state_backend: str = Field(
        default="systemdb",
        pattern=r"^(systemdb|s3|gcs|azure)$",
        description="State storage backend"
    )

    @validator('project_directory')
    def validate_project_directory(cls, v):
        """Ensure project directory exists and is writable."""
        v = Path(v)
        v.mkdir(parents=True, exist_ok=True)

        if not v.is_dir():
            raise ValueError(f"Project directory {v} is not a directory")

        if not os.access(v, os.W_OK):
            raise ValueError(f"Project directory {v} is not writable")

        return v
```

#### **Day 18-21: State Management Implementation**

```python
# flext/src/flext/domain/meltano/state.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from pathlib import Path

class StateStore(ABC):
    """Abstract state store for pipeline state management."""

    @abstractmethod
    async def get_state(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline state."""
        pass

    @abstractmethod
    async def set_state(self, pipeline_id: str, state: Dict[str, Any]) -> None:
        """Set pipeline state."""
        pass

    @abstractmethod
    async def delete_state(self, pipeline_id: str) -> None:
        """Delete pipeline state."""
        pass

class FileStateStore(StateStore):
    """File-based state store implementation."""

    def __init__(self, state_directory: Path):
        self.state_directory = Path(state_directory)
        self.state_directory.mkdir(parents=True, exist_ok=True)

    async def get_state(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline state from file."""
        state_file = self.state_directory / f"{pipeline_id}.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load state for pipeline {pipeline_id}: {e}")
            return None
```

### **Week 4: CLI Integration**

#### **Day 22-25: Meltano CLI Commands**

```python
# flext/src/flext/cli/meltano/commands.py
import cyclopts
from pathlib import Path
from typing import Optional, List

from flext.application.meltano.service import MeltanoOrchestrationService
from flext.cli.common import get_container

meltano_app = cyclopts.App(name="meltano", help="Meltano data pipeline operations")

@meltano_app.command
async def init(
    name: str,
    project_directory: Optional[Path] = None,
    extractors: Optional[List[str]] = None,
    loaders: Optional[List[str]] = None
) -> None:
    """Initialize new Meltano project."""
    container = get_container()
    meltano_service = await container.meltano_service()

    config = MeltanoProjectConfig(
        name=name,
        path=project_directory or Path.cwd() / name,
        extractors=extractors or [],
        loaders=loaders or []
    )

    project = await meltano_service.create_project(config)

    console.print(f"✅ Meltano project '{name}' created at {project.path}")

@meltano_app.command
async def run(
    pipeline: str,
    project_directory: Optional[Path] = None,
    full_refresh: bool = False,
    dry_run: bool = False
) -> None:
    """Run Meltano pipeline."""
    container = get_container()
    meltano_service = await container.meltano_service()

    # Show progress with Rich
    with console.status(f"Running pipeline '{pipeline}'..."):
        run = await meltano_service.run_pipeline(
            pipeline_name=pipeline,
            project_path=project_directory or Path.cwd(),
            full_refresh=full_refresh,
            dry_run=dry_run
        )

    # Display results
    if run.status == PipelineStatus.SUCCESS:
        console.print(f"✅ Pipeline '{pipeline}' completed successfully")
    else:
        console.print(f"❌ Pipeline '{pipeline}' failed: {run.error}")
```

#### **Day 26-28: Status & Monitoring Commands**

```python
@meltano_app.command
async def status(
    project_directory: Optional[Path] = None,
    watch: bool = False
) -> None:
    """Show pipeline status and monitoring information."""
    container = get_container()
    meltano_service = await container.meltano_service()

    project_path = project_directory or Path.cwd()

    if watch:
        # Live monitoring mode
        with Live(auto_refresh=True, refresh_per_second=2) as live:
            while True:
                status_table = await _create_status_table(meltano_service, project_path)
                live.update(status_table)
                await asyncio.sleep(5)
    else:
        # Single status check
        status_table = await _create_status_table(meltano_service, project_path)
        console.print(status_table)

async def _create_status_table(service: MeltanoOrchestrationService, project_path: Path) -> Table:
    """Create Rich table with pipeline status."""
    table = Table(title="🔄 Pipeline Status", show_header=True, header_style="bold magenta")
    table.add_column("Pipeline", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Last Run", style="dim")
    table.add_column("Duration", justify="right")
    table.add_column("Records", justify="right", style="green")

    runs = await service.get_recent_runs(project_path, limit=10)

    for run in runs:
        status_emoji = {
            PipelineStatus.SUCCESS: "✅",
            PipelineStatus.FAILED: "❌",
            PipelineStatus.RUNNING: "🔄",
            PipelineStatus.PENDING: "⏳"
        }.get(run.status, "❓")

        table.add_row(
            run.pipeline_name,
            f"{status_emoji} {run.status.value.upper()}",
            run.started_at.strftime("%Y-%m-%d %H:%M"),
            _format_duration(run.duration),
            str(run.metrics.get('records_processed', 0))
        )

    return table
```

---

## 📋 Phase 2: Web Interface Development (Weeks 5-8)

### **Week 5: FastAPI Web Framework**

#### **Day 29-31: FastAPI Application Setup**

```python
# flext/src/flext/infra/web/app.py
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from flext.application.container import ApplicationContainer
from flext.infra.web.middleware import add_middleware
from flext.infra.web.routes import meltano_router, health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    container = ApplicationContainer()
    await container.init_resources()
    app.state.container = container

    # Initialize Meltano if needed
    meltano_service = await container.meltano_service()
    await meltano_service.initialize_default_project()

    yield

    # Shutdown
    await container.shutdown_resources()

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="FLEXT Data Platform",
        version="0.4.0",
        description="Enterprise data platform with Meltano integration",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # Add middleware
    add_middleware(app)

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Include routers
    app.include_router(health_router, prefix="/api/health", tags=["health"])
    app.include_router(meltano_router, prefix="/api/meltano", tags=["meltano"])

    return app

app = create_app()
```

#### **Day 32-35: Meltano API Endpoints**

```python
# flext/src/flext/infra/web/routes/meltano.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime

from flext.application.meltano.service import MeltanoOrchestrationService
from flext.infra.web.dependencies import get_meltano_service
from flext.infra.web.schemas import *

router = APIRouter()

@router.post("/projects", response_model=MeltanoProjectResponse)
async def create_project(
    project_request: CreateProjectRequest,
    service: MeltanoOrchestrationService = Depends(get_meltano_service)
) -> MeltanoProjectResponse:
    """Create new Meltano project."""
    try:
        project = await service.create_project(project_request.to_config())
        return MeltanoProjectResponse.from_entity(project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=List[MeltanoProjectResponse])
async def list_projects(
    service: MeltanoOrchestrationService = Depends(get_meltano_service)
) -> List[MeltanoProjectResponse]:
    """List all Meltano projects."""
    projects = await service.list_projects()
    return [MeltanoProjectResponse.from_entity(p) for p in projects]

@router.post("/projects/{project_name}/runs", response_model=PipelineRunResponse)
async def run_pipeline(
    project_name: str,
    run_request: RunPipelineRequest,
    background_tasks: BackgroundTasks,
    service: MeltanoOrchestrationService = Depends(get_meltano_service)
) -> PipelineRunResponse:
    """Run pipeline in background."""
    # Start pipeline run in background
    run = await service.start_pipeline_run(
        project_name=project_name,
        pipeline_name=run_request.pipeline_name,
        parameters=run_request.parameters
    )

    # Execute in background
    background_tasks.add_task(
        service.execute_pipeline_run,
        run.id
    )

    return PipelineRunResponse.from_entity(run)

@router.get("/projects/{project_name}/runs", response_model=List[PipelineRunResponse])
async def get_pipeline_runs(
    project_name: str,
    limit: int = 20,
    offset: int = 0,
    status: Optional[PipelineStatus] = None,
    service: MeltanoOrchestrationService = Depends(get_meltano_service)
) -> List[PipelineRunResponse]:
    """Get pipeline runs with pagination."""
    runs = await service.get_pipeline_runs(
        project_name=project_name,
        limit=limit,
        offset=offset,
        status_filter=status
    )

    return [PipelineRunResponse.from_entity(run) for run in runs]

@router.get("/projects/{project_name}/runs/{run_id}/logs")
async def get_run_logs(
    project_name: str,
    run_id: str,
    service: MeltanoOrchestrationService = Depends(get_meltano_service)
) -> dict:
    """Get real-time logs for pipeline run."""
    logs = await service.get_run_logs(run_id)
    return {"logs": logs}

@router.websocket("/projects/{project_name}/runs/{run_id}/logs/stream")
async def stream_run_logs(
    websocket: WebSocket,
    project_name: str,
    run_id: str,
    service: MeltanoOrchestrationService = Depends(get_meltano_service)
):
    """Stream real-time logs via WebSocket."""
    await websocket.accept()

    try:
        async for log_line in service.stream_run_logs(run_id):
            await websocket.send_text(log_line)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
```

### **Week 6: Dashboard Frontend**

#### **Day 36-38: Dashboard Templates**

```html
<!-- flext/src/flext/infra/web/templates/dashboard.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FLEXT Data Platform</title>
    <script src="https://unpkg.com/htmx.org@1.9.9"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/chart.js"></script>
  </head>
  <body class="bg-gray-100">
    <!-- Navigation -->
    <nav class="bg-blue-600 text-white p-4">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold">🔄 FLEXT Data Platform</h1>
        <div class="space-x-4">
          <a href="/dashboard" class="hover:text-blue-200">Dashboard</a>
          <a href="/projects" class="hover:text-blue-200">Projects</a>
          <a href="/monitoring" class="hover:text-blue-200">Monitoring</a>
          <a href="/api/docs" class="hover:text-blue-200">API Docs</a>
        </div>
      </div>
    </nav>

    <!-- Dashboard Content -->
    <div class="container mx-auto p-6">
      <!-- Status Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500">Active Projects</h3>
          <p
            class="text-2xl font-bold text-blue-600"
            hx-get="/api/meltano/stats/projects"
            hx-trigger="load, every 30s"
          >
            {{ stats.active_projects }}
          </p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500">Running Pipelines</h3>
          <p
            class="text-2xl font-bold text-green-600"
            hx-get="/api/meltano/stats/running"
            hx-trigger="load, every 5s"
          >
            {{ stats.running_pipelines }}
          </p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500">Today's Runs</h3>
          <p
            class="text-2xl font-bold text-indigo-600"
            hx-get="/api/meltano/stats/daily"
            hx-trigger="load, every 30s"
          >
            {{ stats.daily_runs }}
          </p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500">Success Rate</h3>
          <p
            class="text-2xl font-bold text-emerald-600"
            hx-get="/api/meltano/stats/success-rate"
            hx-trigger="load, every 30s"
          >
            {{ stats.success_rate }}%
          </p>
        </div>
      </div>

      <!-- Recent Pipeline Runs -->
      <div class="bg-white rounded-lg shadow">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-lg font-semibold">Recent Pipeline Runs</h2>
        </div>
        <div hx-get="/api/meltano/runs/recent" hx-trigger="load, every 10s">
          <!-- Pipeline runs table will be loaded here -->
          <div class="p-6">
            <div class="animate-pulse">Loading recent runs...</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Real-time Updates -->
    <script>
      // WebSocket for real-time updates
      const ws = new WebSocket("ws://localhost:8000/ws/updates");
      ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.type === "run_status_update") {
          htmx.trigger("#runs-table", "refresh");
        }
      };
    </script>
  </body>
</html>
```

#### **Day 39-42: Interactive Components**

```html
<!-- flext/src/flext/infra/web/templates/components/pipeline_runs_table.html -->
<div class="overflow-x-auto">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th
          class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
        >
          Pipeline
        </th>
        <th
          class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
        >
          Status
        </th>
        <th
          class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
        >
          Started
        </th>
        <th
          class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
        >
          Duration
        </th>
        <th
          class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
        >
          Records
        </th>
        <th
          class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
        >
          Actions
        </th>
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
      {% for run in runs %}
      <tr>
        <td
          class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
        >
          {{ run.pipeline_name }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          {% if run.status == 'SUCCESS' %}
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
          >
            ✅ Success
          </span>
          {% elif run.status == 'FAILED' %}
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
          >
            ❌ Failed
          </span>
          {% elif run.status == 'RUNNING' %}
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
          >
            🔄 Running
          </span>
          {% endif %}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ run.started_at.strftime('%Y-%m-%d %H:%M') }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ run.duration_formatted }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          {{ run.metrics.records_processed | default(0) }}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
          <a
            href="/runs/{{ run.id }}/logs"
            class="text-indigo-600 hover:text-indigo-900 mr-3"
            >View Logs</a
          >
          {% if run.status == 'FAILED' %}
          <button
            hx-post="/api/meltano/runs/{{ run.id }}/retry"
            class="text-green-600 hover:text-green-900"
          >
            Retry
          </button>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

### **Week 7: Real-time Features**

#### **Day 43-45: WebSocket Implementation**

```python
# flext/src/flext/infra/web/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio

class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.remove(websocket)
        # Remove from all subscriptions
        for topic, connections in self.subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)

    async def subscribe(self, websocket: WebSocket, topic: str):
        """Subscribe to specific topic updates."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(websocket)

    async def broadcast_to_topic(self, topic: str, message: dict):
        """Broadcast message to all subscribers of a topic."""
        if topic in self.subscriptions:
            disconnected = []
            for connection in self.subscriptions[topic]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.subscriptions[topic].remove(conn)

manager = ConnectionManager()

@router.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)

    try:
        while True:
            # Listen for subscription requests
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get('type') == 'subscribe':
                topic = message.get('topic')
                await manager.subscribe(websocket, topic)
                await websocket.send_text(json.dumps({
                    'type': 'subscription_confirmed',
                    'topic': topic
                }))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

#### **Day 46-49: Live Monitoring Dashboard**

```python
# flext/src/flext/infra/web/routes/monitoring.py
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/monitoring", response_class=HTMLResponse)
async def monitoring_dashboard(request: Request):
    """Real-time monitoring dashboard."""
    return templates.TemplateResponse("monitoring.html", {"request": request})

@router.get("/api/monitoring/metrics")
async def get_monitoring_metrics(
    service: MeltanoOrchestrationService = Depends(get_meltano_service)
):
    """Get current system metrics."""
    metrics = await service.get_system_metrics()

    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "active_projects": metrics.active_projects,
            "running_pipelines": metrics.running_pipelines,
            "queue_size": metrics.queue_size,
            "memory_usage": metrics.memory_usage_mb,
            "cpu_usage": metrics.cpu_usage_percent,
            "disk_usage": metrics.disk_usage_percent,
            "success_rate_24h": metrics.success_rate_24h,
            "avg_pipeline_duration": metrics.avg_pipeline_duration_minutes
        }
    }

# Background task to broadcast metrics updates
async def broadcast_metrics_updates():
    """Continuously broadcast metrics updates to WebSocket clients."""
    while True:
        try:
            # Get current metrics
            container = get_container()
            service = await container.meltano_service()
            metrics = await service.get_system_metrics()

            # Broadcast to monitoring subscribers
            await manager.broadcast_to_topic('monitoring', {
                'type': 'metrics_update',
                'data': metrics.to_dict()
            })

            await asyncio.sleep(5)  # Update every 5 seconds

        except Exception as e:
            logger.error(f"Error broadcasting metrics: {e}")
            await asyncio.sleep(30)  # Wait longer on error
```

### **Week 8: Performance & Polish**

#### **Day 50-52: Caching & Performance**

```python
# flext/src/flext/infra/web/middleware.py
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import redis.asyncio as redis
import json

class CacheMiddleware(BaseHTTPMiddleware):
    """Cache middleware for API responses."""

    def __init__(self, app, redis_url: str = "redis://localhost:6379"):
        super().__init__(app)
        self.redis = redis.from_url(redis_url)

    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests to API endpoints
        if request.method == "GET" and request.url.path.startswith("/api/"):
            cache_key = f"api_cache:{request.url.path}:{str(request.query_params)}"

            # Try to get from cache
            cached = await self.redis.get(cache_key)
            if cached:
                cached_data = json.loads(cached)
                return Response(
                    content=cached_data["content"],
                    media_type=cached_data["media_type"],
                    headers={"X-Cache": "HIT"}
                )

        # Execute request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)

        # Cache successful API responses
        if (request.method == "GET" and
            request.url.path.startswith("/api/") and
            response.status_code == 200):

            cache_key = f"api_cache:{request.url.path}:{str(request.query_params)}"
            cache_data = {
                "content": response.body.decode(),
                "media_type": response.media_type
            }

            # Cache for 60 seconds
            await self.redis.setex(cache_key, 60, json.dumps(cache_data))
            response.headers["X-Cache"] = "MISS"

        return response

def add_middleware(app: FastAPI):
    """Add all middleware to the application."""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Cache middleware
    app.add_middleware(CacheMiddleware)

    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### **Day 53-56: Error Handling & Logging**

```python
# flext/src/flext/infra/web/error_handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging."""
    logger.warning(
        f"HTTP {exc.status_code} - {request.method} {request.url}: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "method": request.method,
            "url": str(request.url),
            "detail": exc.detail
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    logger.warning(
        f"Validation error - {request.method} {request.url}: {exc.errors()}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "errors": exc.errors()
        }
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "message": "Validation error",
            "details": exc.errors(),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error - {request.method} {request.url}: {str(exc)}",
        exc_info=True,
        extra={
            "method": request.method,
            "url": str(request.url),
            "exception_type": type(exc).__name__
        }
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

def register_error_handlers(app: FastAPI):
    """Register all error handlers."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
```

---

## 📋 Phase 3: Docker Containerization (Weeks 9-10)

### **Week 9: Container Development**

#### **Day 57-59: Dockerfile Creation**

```dockerfile
# Dockerfile
FROM python:3.13-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
WORKDIR /app
COPY flext/pyproject.toml flext/poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.13-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLX_ENVIRONMENT=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r flext && useradd -r -g flext flext

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create directories
WORKDIR /app
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R flext:flext /app

# Copy application code
COPY flext/src ./src
COPY flext/config ./config
COPY flext/static ./static
COPY flext/templates ./templates

# Copy entrypoint
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Switch to non-root user
USER flext

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose ports
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["web"]
```

#### **Day 60-63: Docker Compose Setup**

```yaml
# docker-compose.yml
version: "3.8"

services:
  flext-web:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "8000:8000"
    environment:
      - FLX_ENVIRONMENT=production
      - FLX_DATABASE_URL=postgresql://flext:flext@postgres:5432/flext
      - FLX_REDIS_URL=redis://redis:6379/0
      - FLX_LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  flext-worker:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    command: ["worker"]
    environment:
      - FLX_ENVIRONMENT=production
      - FLX_DATABASE_URL=postgresql://flext:flext@postgres:5432/flext
      - FLX_REDIS_URL=redis://redis:6379/0
      - FLX_LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2

  flext-scheduler:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    command: ["scheduler"]
    environment:
      - FLX_ENVIRONMENT=production
      - FLX_DATABASE_URL=postgresql://flext:flext@postgres:5432/flext
      - FLX_REDIS_URL=redis://redis:6379/0
      - FLX_LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=flext
      - POSTGRES_USER=flext
      - POSTGRES_PASSWORD=flext
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - flext-web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### **Week 10: Daemon Mode & Orchestration**

#### **Day 64-66: Service Management**

```python
# flext/src/flext/infra/daemon/service.py
import asyncio
import signal
import sys
from typing import Optional
from pathlib import Path

from flext.application.container import ApplicationContainer
from flext.application.meltano.service import MeltanoOrchestrationService
from flext.infra.web.app import create_app
import uvicorn

class FlextDaemonService:
    """Main daemon service for FLEXT platform."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.container: Optional[ApplicationContainer] = None
        self.web_server: Optional[uvicorn.Server] = None
        self.background_tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()

    async def start(self):
        """Start the daemon service."""
        logger.info("Starting FLEXT daemon service...")

        # Initialize container
        self.container = ApplicationContainer()
        if self.config_path:
            await self.container.load_config(self.config_path)
        await self.container.init_resources()

        # Initialize Meltano
        meltano_service = await self.container.meltano_service()
        await meltano_service.initialize_default_project()

        # Start background tasks
        await self._start_background_tasks()

        # Start web server
        await self._start_web_server()

        # Setup signal handlers
        self._setup_signal_handlers()

        logger.info("FLEXT daemon service started successfully")

    async def stop(self):
        """Stop the daemon service."""
        logger.info("Stopping FLEXT daemon service...")

        # Set shutdown event
        self.shutdown_event.set()

        # Stop web server
        if self.web_server:
            self.web_server.should_exit = True
            await self.web_server.shutdown()

        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

        # Shutdown container
        if self.container:
            await self.container.shutdown_resources()

        logger.info("FLEXT daemon service stopped")

    async def _start_web_server(self):
        """Start the web server."""
        app = create_app()
        app.state.container = self.container

        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_config=None,  # Use our logging config
            access_log=False  # Disable uvicorn access logs
        )

        self.web_server = uvicorn.Server(config)

        # Start server in background
        self.background_tasks.append(
            asyncio.create_task(self.web_server.serve())
        )

    async def _start_background_tasks(self):
        """Start background tasks."""

        # Pipeline scheduler task
        self.background_tasks.append(
            asyncio.create_task(self._pipeline_scheduler())
        )

        # Health monitoring task
        self.background_tasks.append(
            asyncio.create_task(self._health_monitor())
        )

        # Metrics collection task
        self.background_tasks.append(
            asyncio.create_task(self._metrics_collector())
        )

        # Log cleanup task
        self.background_tasks.append(
            asyncio.create_task(self._log_cleanup())
        )

    async def _pipeline_scheduler(self):
        """Background task for pipeline scheduling."""
        meltano_service = await self.container.meltano_service()

        while not self.shutdown_event.is_set():
            try:
                # Check for scheduled pipelines
                await meltano_service.process_scheduled_pipelines()
                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in pipeline scheduler: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _health_monitor(self):
        """Background task for health monitoring."""
        health_service = await self.container.health_service()

        while not self.shutdown_event.is_set():
            try:
                # Perform health checks
                health_status = await health_service.comprehensive_check()

                # Log unhealthy components
                for component, status in health_status.items():
                    if not status.get('healthy', True):
                        logger.warning(f"Component {component} is unhealthy: {status}")

                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)

# Entry point for daemon mode
async def main():
    """Main entry point for daemon mode."""
    daemon = FlextDaemonService()

    try:
        await daemon.start()

        # Wait for shutdown
        await daemon.shutdown_event.wait()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error in daemon: {e}")
        sys.exit(1)
    finally:
        await daemon.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

#### **Day 67-70: Container Orchestration**

```bash
#!/bin/bash
# docker/entrypoint.sh

set -e

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3

    echo "Waiting for $service_name..."
    while ! nc -z $host $port; do
        sleep 1
    done
    echo "$service_name is ready!"
}

# Wait for dependencies
if [ "$FLX_ENVIRONMENT" = "production" ]; then
    wait_for_service postgres 5432 "PostgreSQL"
    wait_for_service redis 6379 "Redis"
fi

# Run database migrations
echo "Running database migrations..."
cd /app
python -m alembic upgrade head

# Initialize Meltano project if needed
echo "Initializing Meltano..."
python -c "
import asyncio
from flext.application.container import ApplicationContainer

async def init():
    container = ApplicationContainer()
    await container.init_resources()
    meltano_service = await container.meltano_service()
    await meltano_service.initialize_default_project()
    await container.shutdown_resources()

asyncio.run(init())
"

# Execute command based on argument
case "$1" in
    "web")
        echo "Starting FLEXT web server..."
        exec python -m flext.infra.daemon.service
        ;;
    "worker")
        echo "Starting FLEXT worker..."
        exec celery -A flext.infra.tasks.celery_app worker --loglevel=info
        ;;
    "scheduler")
        echo "Starting FLEXT scheduler..."
        exec celery -A flext.infra.tasks.celery_app beat --loglevel=info
        ;;
    "cli")
        echo "Starting FLEXT CLI..."
        exec python -m flext.cli.main "${@:2}"
        ;;
    "shell")
        echo "Starting interactive shell..."
        exec python -c "
import asyncio
from flext.application.container import ApplicationContainer

async def shell():
    container = ApplicationContainer()
    await container.init_resources()

    # Make services available
    globals().update({
        'container': container,
        'meltano': await container.meltano_service(),
        'health': await container.health_service()
    })

    import IPython
    IPython.embed()

asyncio.run(shell())
"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Available commands: web, worker, scheduler, cli, shell"
        exit 1
        ;;
esac
```

---

## 📋 Phase 4: Production Deployment (Weeks 11-12)

### **Week 11: Production Configuration**

#### **Day 71-73: Kubernetes Deployment**

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: flext-platform

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: flext-config
  namespace: flext-platform
data:
  FLX_ENVIRONMENT: "production"
  FLX_LOG_LEVEL: "INFO"
  FLX_DATABASE_URL: "postgresql://flext:flext@postgres:5432/flext"
  FLX_REDIS_URL: "redis://redis:6379/0"

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext-web
  namespace: flext-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flext-web
  template:
    metadata:
      labels:
        app: flext-web
    spec:
      containers:
        - name: flext-web
          image: flext-platform:latest
          ports:
            - containerPort: 8000
          env:
            - name: FLX_ENVIRONMENT
              valueFrom:
                configMapKeyRef:
                  name: flext-config
                  key: FLX_ENVIRONMENT
            - name: FLX_DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: flext-secrets
                  key: database-url
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /api/health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: flext-web-service
  namespace: flext-platform
spec:
  selector:
    app: flext-web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: flext-ingress
  namespace: flext-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - flext.yourdomain.com
      secretName: flext-tls
  rules:
    - host: flext.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: flext-web-service
                port:
                  number: 80
```

#### **Day 74-77: Monitoring & Observability**

```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: flext-metrics
  namespace: flext-platform
spec:
  selector:
    matchLabels:
      app: flext-web
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics

---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: flext-alerts
  namespace: flext-platform
spec:
  groups:
    - name: flext.rules
      rules:
        - alert: FlextPipelineFailure
          expr: increase(flext_pipeline_failures_total[5m]) > 0
          for: 0m
          labels:
            severity: warning
          annotations:
            summary: "FLEXT pipeline failure detected"
            description: "Pipeline {{ $labels.pipeline }} has failed"

        - alert: FlextHighMemoryUsage
          expr: flext_memory_usage_percent > 90
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "FLEXT high memory usage"
            description: "Memory usage is {{ $value }}%"
```

### **Week 12: Performance Optimization & Documentation**

#### **Day 78-80: Performance Tuning**

```python
# flext/src/flext/infra/performance/optimization.py
from functools import lru_cache
import asyncio
from typing import Dict, Any
import aioredis

class PerformanceOptimizer:
    """Performance optimization utilities."""

    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        self._cache = {}

    @lru_cache(maxsize=1000)
    def get_cached_config(self, config_key: str) -> Dict[str, Any]:
        """Cache configuration lookups."""
        # Implementation for config caching
        pass

    async def batch_database_operations(self, operations: List[callable]) -> List[Any]:
        """Batch database operations for better performance."""
        tasks = [asyncio.create_task(op()) for op in operations]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def warm_up_caches(self):
        """Warm up commonly used caches."""
        # Pre-load frequently accessed data
        pass

# Connection pooling optimization
class OptimizedConnectionPool:
    """Optimized connection pool management."""

    def __init__(self):
        self.database_pool = None
        self.redis_pool = None

    async def initialize_pools(self, db_url: str, redis_url: str):
        """Initialize connection pools with optimal settings."""
        # Database pool with optimized settings
        self.database_pool = await asyncpg.create_pool(
            db_url,
            min_size=5,
            max_size=20,
            max_queries=50000,
            max_inactive_connection_lifetime=300,
            command_timeout=60
        )

        # Redis pool
        self.redis_pool = aioredis.ConnectionPool.from_url(
            redis_url,
            max_connections=20,
            retry_on_timeout=True
        )
```

#### **Day 81-84: Complete Documentation**

````markdown
# FLEXT Platform - Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Kubernetes cluster (optional)
- Python 3.13+
- PostgreSQL 15+
- Redis 7+

## Quick Start

### 1. Local Development

```bash
# Clone repository
git clone <repository-url>
cd flext-platform

# Install dependencies
make venv-install-dev

# Start services
docker-compose up -d postgres redis

# Run migrations
make migrate

# Start development server
make dev
```
````

### 2. Production Deployment

```bash
# Build production image
docker build -t flext-platform:latest .

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/
```

## Configuration

### Environment Variables

| Variable           | Description                    | Default       |
| ------------------ | ------------------------------ | ------------- |
| `FLX_ENVIRONMENT`  | Environment (dev/staging/prod) | `development` |
| `FLX_DATABASE_URL` | PostgreSQL connection URL      | Required      |
| `FLX_REDIS_URL`    | Redis connection URL           | Required      |
| `FLX_LOG_LEVEL`    | Logging level                  | `INFO`        |

### Meltano Configuration

The platform automatically initializes a default Meltano project. You can customize:

```yaml
# config/meltano.yml
project_id: flext-data-platform
default_environment: prod
environments:
  prod:
    extractors:
      - name: tap-postgres
        config:
          host: ${DATABASE_HOST}
          port: ${DATABASE_PORT}
    loaders:
      - name: target-postgres
        config:
          host: ${TARGET_HOST}
          port: ${TARGET_PORT}
```

## API Usage

### Create Project

```bash
curl -X POST http://localhost:8000/api/meltano/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-project",
    "extractors": ["tap-csv"],
    "loaders": ["target-postgres"]
  }'
```

### Run Pipeline

```bash
curl -X POST http://localhost:8000/api/meltano/projects/my-project/runs \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_name": "tap-csv target-postgres",
    "parameters": {
      "full_refresh": true
    }
  }'
```

## Monitoring

Access the monitoring dashboard at:

- Web UI: <http://localhost:8000>
- API Docs: <http://localhost:8000/api/docs>
- Metrics: <http://localhost:8000/metrics>

## Support

For support and documentation, see:

- [API Reference](./API_REFERENCE.md)
- [Architecture Guide](./ARCHITECTURE.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

````

---

## 🎯 Success Criteria & Validation

### **Technical Criteria**
- ✅ **Complete Meltano Integration**: All ELT functionality working
- ✅ **Docker Containerization**: Full container support with orchestration
- ✅ **Web Interface**: Professional dashboard for pipeline management
- ✅ **Daemon Mode**: Background service operation with monitoring
- ✅ **API Completeness**: Full REST API for all operations
- ✅ **Real-time Features**: WebSocket updates and live monitoring

### **Performance Criteria**
- ✅ **Response Time**: <200ms for API endpoints
- ✅ **Pipeline Throughput**: Handle 100+ concurrent pipeline runs
- ✅ **Resource Usage**: <2GB RAM, <1 CPU core per service
- ✅ **Scalability**: Horizontal scaling support

### **Operational Criteria**
- ✅ **Health Monitoring**: Comprehensive health checks
- ✅ **Logging**: Structured logging with correlation IDs
- ✅ **Metrics**: Prometheus-compatible metrics
- ✅ **Security**: Secure by default configuration

---

## 🚧 Risk Management

### **High Priority Risks**

#### **Risk: Meltano Integration Complexity**
**Mitigation**:
- Start with basic ELT scenarios and expand gradually
- Comprehensive testing with real data sources
- Fallback to standalone Meltano if integration issues occur

#### **Risk: Container Performance**
**Mitigation**:
- Performance benchmarking at each phase
- Resource optimization and monitoring
- Horizontal scaling capabilities

#### **Risk: Data Pipeline Reliability**
**Mitigation**:
- Comprehensive error handling and recovery
- Pipeline state management and resumption
- Automated monitoring and alerting

---

## 🎉 Expected Outcomes

### **Strategic Benefits**
- **Unified Platform**: Single platform for data pipelines and application logic
- **Developer Productivity**: 80% faster pipeline development
- **Operational Excellence**: Comprehensive monitoring and management
- **Scalability**: Cloud-native deployment ready for enterprise scale

### **Technical Achievements**
- **Modern Architecture**: Hexagonal architecture with Meltano integration
- **Container-Native**: Full Docker and Kubernetes support
- **Professional UI**: Enterprise-grade web interface
- **Production-Ready**: Monitoring, logging, and security built-in

### **Business Impact**
- **Faster Time-to-Market**: Rapid data pipeline deployment
- **Reduced Complexity**: Single platform instead of multiple tools
- **Better Reliability**: Enterprise-grade error handling and monitoring
- **Cost Efficiency**: Optimized resource usage and scaling

---

## 📚 Implementation Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | 4 weeks | Meltano core integration, CLI commands |
| **Phase 2** | 4 weeks | Web interface, real-time dashboard |
| **Phase 3** | 2 weeks | Docker containerization, daemon mode |
| **Phase 4** | 2 weeks | Production deployment, documentation |

**Total Duration**: 12 weeks
**Team Size**: 3-4 developers
**Risk Level**: Medium (mitigated through phased approach)

---

---

## Cross-References

### Prerequisites
Before implementing Meltano integration, ensure you have:
- [FLEXT Core Framework Understanding](../../getting-started/index.md) - Complete FLEXT framework setup and configuration
- [Hexagonal Architecture Mastery](../../architecture/application-layer.md) - Understanding of adapter patterns and domain boundaries
- [Container Infrastructure](../../infrastructure/index.md) - Docker and container orchestration knowledge
- [Data Platform Concepts](../../examples/index.md) - Data pipeline fundamentals and ELT patterns

### Next Steps
After implementing Meltano integration:
- **For Framework Integration**: [Meltano Framework Integration](meltano-framework-integration.md) for technical implementation details
- **For Plugin Development**: [Meltano Plugins Integration](meltano-plugins-integration.md) for custom extractors and loaders
- **For Operations**: [Infrastructure Services](../../infrastructure/operational-excellence.md) for monitoring and maintenance
- **For Scaling**: [Deployment Guide](../../deployment/index.md) for production deployment strategies

### Related Topics
- [Oracle Integrations](../oracle/oracle-integration-hub.md) - Integrate Oracle systems with Meltano pipelines
- [API Development](../../api-reference/index.md) - Build APIs around data pipeline operations
- [Observability Stack](../../infrastructure/operational-excellence.md) - Monitor data pipeline performance
- [Security Framework](../../security/index.md) - Secure data pipeline operations

---

## Troubleshooting

### Common Integration Issues

#### Meltano CLI Integration Problems
```bash
# Test Meltano CLI availability
python -c "import meltano; print(meltano.__version__)"

# Verify Singer SDK integration
python -c "from singer_sdk import Tap, Target; print('Singer SDK available')"

# Check FLEXT adapter integration
flext meltano --help
````

#### Container Build Issues

```bash
# Debug Docker build process
docker build --no-cache --progress=plain -t flext-meltano:debug .

# Check container dependencies
docker run --rm flext-meltano:debug python -c "import meltano, flext; print('Dependencies OK')"

# Verify volume mounts
docker run --rm -v $(pwd)/data:/app/data flext-meltano:debug ls -la /app/data
```

#### Web Interface Problems

```bash
# Test FastAPI application startup
uvicorn flext.infra.web.app:app --reload --port 8000

# Check WebSocket connections
curl -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8000/ws/updates

# Verify API endpoints
curl http://localhost:8000/api/meltano/projects
```

#### Database Integration Issues

```bash
# Test database connectivity
psql $FLX_DATABASE_URL -c "SELECT version();"

# Run database migrations
alembic upgrade head

# Check Meltano state storage
flext meltano config --show-state-backend
```

### Performance Issues

#### Pipeline Execution Performance

- Monitor pipeline execution times and resource usage
- Implement connection pooling for database operations
- Use async operations where possible for I/O bound tasks
- Consider pipeline parallelization for independent data sources

#### Web Interface Performance

- Implement caching for frequently accessed data
- Use WebSocket connections for real-time updates
- Optimize database queries with proper indexing
- Consider CDN for static assets

#### Container Resource Usage

- Monitor memory usage during pipeline execution
- Adjust JVM settings for Java-based extractors
- Implement resource limits in container orchestration
- Use multi-stage builds to reduce image size

### Deployment Issues

#### Kubernetes Deployment Problems

```yaml
# Debug pod issues
kubectl describe pod flext-web-pod-name
kubectl logs flext-web-pod-name -f

# Check service connectivity
kubectl port-forward service/flext-web-service 8000:80

# Verify configuration
kubectl get configmap flext-config -o yaml
```

#### Docker Compose Issues

```bash
# Check service dependencies
docker-compose ps
docker-compose logs flext-web

# Test network connectivity
docker-compose exec flext-web ping postgres
docker-compose exec flext-web ping redis

# Verify volume mounts
docker-compose exec flext-web ls -la /app/data
```

### Getting Help

#### Diagnostic Information

```bash
# Generate system diagnostic report
flext system-info --include-meltano --output diagnostic-report.json

# Check all service health
flext health-check --comprehensive

# Export configuration for review
flext config export --include-secrets=false > config-review.yaml
```

#### Community Resources

- **Meltano Documentation**: [docs.meltano.com](https://docs.meltano.com)
- **Singer SDK Reference**: [sdk.meltano.com](https://sdk.meltano.com)
- **FLEXT Framework Guide**: [Architecture Documentation](../../architecture/index.md)
- **Container Best Practices**: [Deployment Guide](../../deployment/index.md)

---

**This comprehensive plan provides a clear roadmap for integrating Meltano functionality into the FLEXT framework while maintaining architectural integrity and adding enterprise-grade capabilities for container deployment and web-based management.**

**Documentation Framework**: FLEXT Enterprise Documentation Standard
**Implementation Status**: Strategic Roadmap - Production Planning Phase
**Last Updated**: 2025-06-11
**Maintained by**: FLEXT Framework Data Platform Team
