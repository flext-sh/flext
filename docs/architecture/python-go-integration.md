# Python-Go Integration Architecture

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-01-08

## Overview

FLEXT implements a hybrid Python-Go architecture where Go services orchestrate Python libraries through well-defined integration patterns. This document explains how the 33 Python projects work together with the Go control plane.

## Architecture Principles

### 1. Go as Control Plane

- **FLEXT Service (Go)**: Primary orchestration and control
- **FlexCore Runtime (Go)**: Distributed execution engine
- **Python Libraries**: Specialized data processing capabilities

### 2. Clear Separation of Concerns

- **Go**: Service orchestration, API management, workflow coordination
- **Python**: Data processing, ETL operations, domain-specific logic

### 3. Protocol-Based Integration

- **gRPC**: High-performance service-to-service communication
- **HTTP/REST**: External API exposure
- **Subprocess**: Direct Python execution from Go

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT CONTROL PLANE (Go)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐  │
│  │  FLEXT Service      │◄──►│  FlexCore Runtime               │  │
│  │  (Port 8081)        │    │  (Port 8080)                    │  │
│  │                     │    │                                 │  │
│  │ • API Gateway       │    │ • Workflow Execution            │  │
│  │ • Service Discovery │    │ • Plugin Management             │  │
│  │ • Configuration     │    │ • Resource Coordination         │  │
│  │ • Monitoring        │    │ • Event Sourcing                │  │
│  └─────────────────────┘    └─────────────────────────────────┘  │
│           │                              │                      │
│           └─────────── COORDINATION ─────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON ECOSYSTEM (33 Projects)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────┐  │
│  │ Foundation  │ Integration │ Processing  │   Extensions    │  │
│  │             │             │             │                 │  │
│  │ • flext-core│ • flext-api │ • flext-    │ • flext-tap-*   │  │
│  │ • flext-    │ • flext-auth│   meltano   │ • flext-target-*│  │
│  │   observa-  │ • flext-grpc│ • flext-    │ • flext-dbt-*   │  │
│  │   bility    │ • flext-web │   ldap      │ • flext-*-ext   │  │
│  │             │ • flext-cli │ • flext-    │                 │  │
│  │             │             │   ldif      │                 │  │
│  │             │             │ • flext-db- │                 │  │
│  │             │             │   oracle    │                 │  │
│  └─────────────┴─────────────┴─────────────┴─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Patterns

### 1. gRPC Service Integration

#### Go Service Definition

```go
// pkg/interfaces/grpc/python_service.go
type PythonService interface {
    ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error)
    ExtractData(ctx context.Context, req *ExtractRequest) (*ExtractResponse, error)
    TransformData(ctx context.Context, req *TransformRequest) (*TransformResponse, error)
    LoadData(ctx context.Context, req *LoadRequest) (*LoadResponse, error)
}

// pkg/adapters/grpc/python_adapter.go
type PythonAdapter struct {
    client     *grpc.Client
    logger     *logger.Logger
    config     *config.Config
}

func (a *PythonAdapter) ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error) {
    // 1. Validate request
    if err := a.validatePipelineRequest(req); err != nil {
        return nil, fmt.Errorf("invalid pipeline request: %w", err)
    }

    // 2. Call Python service via gRPC
    resp, err := a.client.ExecutePipeline(ctx, req)
    if err != nil {
        return nil, fmt.Errorf("pipeline execution failed: %w", err)
    }

    // 3. Transform response
    return a.transformPipelineResponse(resp), nil
}
```

#### Python Service Implementation

```python
# flext-grpc/src/flext_grpc/services/pipeline_service.py
from flext_core.result import FlextResult
from flext_meltano import MeltanoRunner
from flext_core.types import FlextTypes

class PipelineService:
    """gRPC service for pipeline execution."""

    def __init__(self, meltano_runner: MeltanoRunner):
        self._meltano_runner = meltano_runner

    async def execute_pipeline(
        self,
        pipeline_id: str,
        config: FlextTypes.Data.ConnectionConfig
    ) -> FlextResult[FlextTypes.Data.RecordBatch]:
        """Execute pipeline via Meltano."""
        try:
            result = await self._meltano_runner.run_pipeline(
                pipeline_id=pipeline_id,
                config=config
            )
            return FlextResult[None].ok(result)
        except Exception as e:
            return FlextResult[None].fail(f"Pipeline execution failed: {e}")
```

### 2. HTTP/REST API Integration

#### Go API Gateway

```go
// pkg/adapters/controllers/http/pipeline_controller.go
type PipelineController struct {
    pythonService PythonService
    logger        *logger.Logger
}

func (c *PipelineController) CreatePipeline(w http.ResponseWriter, r *http.Request) {
    // 1. Parse request
    var req CreatePipelineRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    // 2. Call Python service
    resp, err := c.pythonService.CreatePipeline(r.Context(), &req)
    if err != nil {
        c.logger.Error("Pipeline creation failed", "error", err)
        http.Error(w, "Internal server error", http.StatusInternalServerError)
        return
    }

    // 3. Return response
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp)
}
```

#### Python API Service

```python
# flext-api/src/flext_api/controllers/pipeline_controller.py
from fastapi import APIRouter, HTTPException
from flext_core.result import FlextResult
from flext_meltano import MeltanoManager

router = APIRouter()

@router.post("/pipelines")
async def create_pipeline(pipeline: PipelineCreate):
    """Create new pipeline."""
    manager = MeltanoManager()
    result = await manager.create_pipeline(pipeline)

    if result.is_failure:
        raise HTTPException(
            status_code=400,
            detail=result.error
        )

    return result.data
```

### 3. Subprocess Execution

#### Go Subprocess Manager

```go
// pkg/adapters/executors/python_executor.go
type PythonExecutor struct {
    config     *config.Config
    logger     *logger.Logger
    workDir    string
}

func (e *PythonExecutor) ExecuteScript(ctx context.Context, script string, args []string) (*ExecutionResult, error) {
    // 1. Prepare command
    cmd := exec.CommandContext(ctx, "python", append([]string{script}, args...)...)
    cmd.Dir = e.workDir
    cmd.Env = e.buildEnvironment()

    // 2. Capture output
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr

    // 3. Execute with timeout
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    err := cmd.Run()

    return &ExecutionResult{
        ExitCode: cmd.ProcessState.ExitCode(),
        Stdout:   stdout.String(),
        Stderr:   stderr.String(),
        Error:    err,
    }, nil
}
```

#### Python Script Execution

```python
# flext-meltano/src/flext_meltano/scripts/pipeline_runner.py
import sys
import json
from flext_core.result import FlextResult
from flext_meltano import MeltanoRunner

def main():
    """Execute pipeline from command line."""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Pipeline ID required"
        }))
        sys.exit(1)

    pipeline_id = sys.argv[1]
    config = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    runner = MeltanoRunner()
    result = runner.run_pipeline(pipeline_id, config)

    print(json.dumps({
        "success": result.success,
        "data": result.data if result.success else None,
        "error": result.error if not result.success else None
    }))

    sys.exit(0 if result.success else 1)

if __name__ == "__main__":
    main()
```

## Data Flow Patterns

### 1. Pipeline Execution Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Go API    │───►│  Python     │───►│  Python     │
│  Gateway    │    │  Service    │    │  Processing │
│             │    │             │    │             │
│ • Validate  │    │ • Parse     │    │ • Extract   │
│ • Route     │    │ • Transform │    │ • Transform │
│ • Monitor   │    │ • Execute   │    │ • Load      │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └─────── Response ──┴─────── Results ───┘
```

### 2. Error Handling Flow

```go
// Go error handling with Python integration
func (s *PipelineService) ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error) {
    // 1. Call Python service
    resp, err := s.pythonService.ExecutePipeline(ctx, req)
    if err != nil {
        // 2. Handle Python service errors
        s.logger.Error("Python service error",
            "error", err,
            "pipeline_id", req.PipelineID,
            "correlation_id", req.CorrelationID)

        // 3. Transform to Go error
        return nil, &PythonServiceError{
            Message: err.Error(),
            Code:    "PYTHON_SERVICE_ERROR",
            Context: map[string]interface{}{
                "pipeline_id": req.PipelineID,
            },
        }
    }

    // 4. Handle Python business errors
    if !resp.Success {
        return nil, &PipelineExecutionError{
            Message: resp.Error,
            Code:    resp.ErrorCode,
            Context: resp.Context,
        }
    }

    return resp, nil
}
```

```python
# Python error handling with Go integration
from flext_core.errors import FlextBusinessError, FlextTechnicalError
from flext_core.result import FlextResult

class PipelineExecutor:
    """Execute pipelines with proper error handling."""

    async def execute_pipeline(self, pipeline_id: str, config: dict) -> FlextResult[dict]:
        try:
            # 1. Validate pipeline
            validation_result = await self._validate_pipeline(pipeline_id)
            if validation_result.is_failure:
                return FlextResult[None].fail(
                    f"Pipeline validation failed: {validation_result.error}",
                    error_code="PIPELINE_VALIDATION_ERROR"
                )

            # 2. Execute pipeline
            result = await self._run_pipeline(pipeline_id, config)
            return FlextResult[None].ok(result)

        except FlextBusinessError as e:
            # 3. Business errors (user action required)
            return FlextResult[None].fail(
                str(e),
                error_code=e.error_code,
                correlation_id=e.correlation_id
            )
        except Exception as e:
            # 4. Technical errors (system issue)
            return FlextResult[None].fail(
                f"Technical error: {str(e)}",
                error_code="TECHNICAL_ERROR"
            )
```

## Configuration Management

### 1. Shared Configuration

```go
// Go configuration that includes Python settings
type Config struct {
    Server   ServerConfig   `yaml:"server"`
    Database DatabaseConfig `yaml:"database"`
    Python   PythonConfig   `yaml:"python"`
}

type PythonConfig struct {
    VirtualEnv    string            `yaml:"virtual_env"`
    Requirements  string            `yaml:"requirements"`
    Services      map[string]string `yaml:"services"`
    Timeout       time.Duration     `yaml:"timeout"`
    MaxWorkers    int               `yaml:"max_workers"`
}
```

```python
# Python configuration that integrates with Go
from flext_core.config import FlextConfigHierarchical

class PythonServiceConfig(FlextConfigHierarchical):
    """Configuration for Python services."""

    def __init__(self):
        super().__init__()

        # Register Go configuration provider
        self.register_provider(GoConfigProvider())
        self.register_provider(EnvironmentProvider("PYTHON_"))
        self.register_provider(ConfigFileProvider("python-config.yaml"))

    def get_service_url(self, service_name: str) -> str:
        """Get service URL from Go configuration."""
        return self.get_config(f"services.{service_name}").unwrap_or("")

    def get_timeout(self) -> int:
        """Get timeout from Go configuration."""
        return self.get_config("timeout").unwrap_or(30)
```

### 2. Environment Coordination

```bash
# Shared environment variables
export FLEXT_ENVIRONMENT=production
export FLEXT_LOG_LEVEL=info
export FLEXT_DATABASE_URL=postgresql://...
export FLEXT_REDIS_URL=redis://...

# Python-specific variables
export PYTHON_SERVICES_API_URL=http://localhost:8081/api/v1
export PYTHON_SERVICES_GRPC_URL=localhost:50051
export PYTHON_MAX_WORKERS=4
export PYTHON_TIMEOUT=30
```

## Monitoring and Observability

### 1. Distributed Tracing

```go
// Go tracing with Python correlation
func (s *PipelineService) ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error) {
    // 1. Create trace span
    span := trace.SpanFromContext(ctx)
    span.SetAttributes(
        attribute.String("pipeline.id", req.PipelineID),
        attribute.String("service.type", "go"),
    )

    // 2. Inject trace context for Python
    traceContext := make(map[string]string)
    trace.Inject(ctx, propagation.MapCarrier(traceContext))

    // 3. Add trace context to Python request
    req.TraceContext = traceContext

    // 4. Execute Python service
    resp, err := s.pythonService.ExecutePipeline(ctx, req)

    // 5. Record span attributes
    span.SetAttributes(
        attribute.Bool("success", err == nil),
        attribute.String("python.service", "pipeline"),
    )

    return resp, err
}
```

```python
# Python tracing with Go correlation
from flext_core.observability import get_tracer, get_logger

class PipelineService:
    """Service with distributed tracing."""

    def __init__(self):
        self.tracer = get_tracer()
        self.logger = get_logger()

    async def execute_pipeline(self, request: PipelineRequest) -> PipelineResponse:
        # 1. Extract trace context from Go
        context = self.tracer.extract_context(request.trace_context)

        # 2. Create span
        with self.tracer.start_span("python.pipeline.execute", context=context) as span:
            span.set_attribute("pipeline.id", request.pipeline_id)
            span.set_attribute("service.type", "python")

            # 3. Execute pipeline
            result = await self._execute_pipeline(request)

            # 4. Record results
            span.set_attribute("success", result.success)

            return result
```

### 2. Metrics Collection

```go
// Go metrics for Python integration
type PythonMetrics struct {
    pipelineExecutions    *prometheus.CounterVec
    pipelineDuration      *prometheus.HistogramVec
    pythonServiceErrors   *prometheus.CounterVec
}

func (m *PythonMetrics) RecordPipelineExecution(pipelineID string, duration time.Duration, success bool) {
    m.pipelineExecutions.WithLabelValues(pipelineID).Inc()
    m.pipelineDuration.WithLabelValues(pipelineID).Observe(duration.Seconds())

    if !success {
        m.pythonServiceErrors.WithLabelValues(pipelineID).Inc()
    }
}
```

```python
# Python metrics for Go integration
from flext_core.observability import get_metrics

class PipelineMetrics:
    """Metrics for pipeline execution."""

    def __init__(self):
        self.metrics = get_metrics()

    def record_execution(self, pipeline_id: str, duration: float, success: bool):
        """Record pipeline execution metrics."""
        self.metrics.increment(
            "python.pipeline.executions",
            tags={"pipeline_id": pipeline_id, "success": str(success)}
        )

        self.metrics.histogram(
            "python.pipeline.duration",
            value=duration,
            tags={"pipeline_id": pipeline_id}
        )
```

## Quality Standards

### 1. Integration Testing

```go
// Go integration tests with Python
func TestPipelineExecution_Integration(t *testing.T) {
    // 1. Start Python service
    pythonService := startPythonService(t)
    defer pythonService.Stop()

    // 2. Create Go service
    goService := NewPipelineService(pythonService)

    // 3. Execute test pipeline
    req := &PipelineRequest{
        PipelineID: "test-pipeline",
        Config:     map[string]interface{}{"test": true},
    }

    resp, err := goService.ExecutePipeline(context.Background(), req)

    // 4. Assert results
    assert.NoError(t, err)
    assert.True(t, resp.Success)
    assert.Equal(t, "test-pipeline", resp.PipelineID)
}
```

```python
# Python integration tests with Go
import pytest
from flext_core.testing import MockGoService

class TestPipelineIntegration:
    """Integration tests with Go service."""

    @pytest.fixture
    def go_service(self):
        """Mock Go service for testing."""
        return MockGoService()

    async def test_pipeline_execution(self, go_service):
        """Test pipeline execution with Go integration."""
        # 1. Setup pipeline
        pipeline_id = "test-pipeline"
        config = {"test": True}

        # 2. Execute pipeline
        result = await go_service.execute_pipeline(pipeline_id, config)

        # 3. Assert results
        assert result.success
        assert result.data["pipeline_id"] == pipeline_id
```

### 2. Error Handling Standards

- **Go Services**: Handle Python service failures gracefully
- **Python Services**: Return structured errors via FlextResult
- **Cross-Service**: Maintain correlation IDs for debugging
- **Monitoring**: Track success/failure rates across services

### 3. Performance Standards

- **Response Time**: Python services respond within 5 seconds
- **Throughput**: Support 100+ concurrent pipeline executions
- **Resource Usage**: Python processes use < 512MB RAM each
- **Availability**: 99.9% uptime for critical Python services

## Related Documentation

- [Service Architecture](./services.md) - Overall service design
- [Package Structure](./pkg-structure.md) - Go package organization
- [Service Coordination](../integration/service-coordination.md) - Service communication
- [Patterns](../patterns/README.md) - Integration patterns

---

**Python-Go Integration Architecture** - Comprehensive integration patterns that enable seamless collaboration between Go control plane and Python data processing ecosystem.
