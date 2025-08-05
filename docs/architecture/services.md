# FLEXT Service Architecture

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-01-08

## Overview

FLEXT implements a distributed service architecture with Go services orchestrating Python libraries through well-defined integration patterns. This document describes the service design, communication patterns, and coordination mechanisms.

## Service Architecture

### Core Services

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

## Service Responsibilities

### FLEXT Service (Go - Port 8081)

**Primary Control Plane**

- **API Gateway**: Route requests to appropriate services
- **Service Discovery**: Discover and register Python services
- **Configuration Management**: Centralized configuration for all services
- **Monitoring & Observability**: Collect metrics, logs, and traces
- **Authentication & Authorization**: JWT-based security
- **Plugin Management**: Manage Python plugin lifecycle

### FlexCore Runtime (Go - Port 8080)

**Distributed Execution Engine**

- **Workflow Execution**: Execute ETL pipelines and workflows
- **Resource Management**: Allocate and manage compute resources
- **Event Sourcing**: Maintain immutable event log
- **Plugin Orchestration**: Coordinate Python plugin execution
- **State Management**: Track workflow and pipeline states
- **Failover & Recovery**: Handle service failures gracefully

### Python Services

**Specialized Data Processing**

#### Foundation Services

- **flext-core**: Shared types, models, and utilities
- **flext-observability**: Logging, metrics, and tracing

#### Integration Services

- **flext-api**: REST API endpoints
- **flext-auth**: Authentication and authorization
- **flext-grpc**: gRPC service implementations
- **flext-web**: Web interface
- **flext-cli**: Command-line interface

#### Processing Services

- **flext-meltano**: Meltano orchestration
- **flext-ldap**: LDAP integration
- **flext-ldif**: LDIF processing
- **flext-db-oracle**: Oracle database integration

#### Extension Services

- **flext-tap-***: Data extraction plugins
- **flext-target-***: Data loading plugins
- **flext-dbt-***: Data transformation plugins
- **flext-*-ext**: Custom extensions

## Integration Patterns

### 1. gRPC Service Integration

High-performance service-to-service communication between Go and Python.

```go
// Go service calling Python via gRPC
type PythonService interface {
    ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error)
    ExtractData(ctx context.Context, req *ExtractRequest) (*ExtractResponse, error)
    TransformData(ctx context.Context, req *TransformRequest) (*TransformResponse, error)
    LoadData(ctx context.Context, req *LoadRequest) (*LoadResponse, error)
}
```

```python
# Python service implementing gRPC interface
class PipelineService:
    async def execute_pipeline(self, request: PipelineRequest) -> PipelineResponse:
        # Execute pipeline logic
        result = await self._run_pipeline(request.pipeline_id, request.config)
        return PipelineResponse(success=result.success, data=result.data)
```

### 2. HTTP/REST API Integration

External API exposure with Go as gateway to Python services.

```go
// Go API gateway routing to Python services
func (c *PipelineController) CreatePipeline(w http.ResponseWriter, r *http.Request) {
    // Parse request
    var req CreatePipelineRequest
    json.NewDecoder(r.Body).Decode(&req)
    
    // Call Python service
    resp, err := c.pythonService.CreatePipeline(r.Context(), &req)
    if err != nil {
        http.Error(w, "Service error", http.StatusInternalServerError)
        return
    }
    
    // Return response
    json.NewEncoder(w).Encode(resp)
}
```

### 3. Subprocess Execution

Direct Python script execution from Go for simple operations.

```go
// Go executing Python scripts
func (e *PythonExecutor) ExecuteScript(ctx context.Context, script string, args []string) (*ExecutionResult, error) {
    cmd := exec.CommandContext(ctx, "python", append([]string{script}, args...)...)
    cmd.Env = e.buildEnvironment()
    
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr
    
    err := cmd.Run()
    return &ExecutionResult{
        ExitCode: cmd.ProcessState.ExitCode(),
        Stdout:   stdout.String(),
        Stderr:   stderr.String(),
        Error:    err,
    }, nil
}
```

## Service Communication

### Request Flow

```
1. Client Request → Go API Gateway
2. Go Service → Python Service (gRPC/HTTP)
3. Python Service → Processing Logic
4. Python Service → Go Service (Response)
5. Go Service → Client (Response)
```

### Event Flow

```
1. Go Service → Event Bus (Pipeline Started)
2. Python Service → Event Bus (Processing Complete)
3. Go Service → Event Bus (Pipeline Finished)
4. Monitoring → Metrics & Logs
```

## Configuration Management

### Shared Configuration

```yaml
# flext-config.yaml
server:
  port: 8081
  host: "0.0.0.0"

python:
  services:
    api: "http://localhost:8000"
    grpc: "localhost:50051"
    meltano: "http://localhost:8001"
  timeout: 30
  max_workers: 4

database:
  url: "postgresql://user:pass@localhost:5432/flext"

redis:
  url: "redis://localhost:6379"
```

### Environment Variables

```bash
# Go services
export FLEXT_ENVIRONMENT=production
export FLEXT_LOG_LEVEL=info
export FLEXT_DATABASE_URL=postgresql://...

# Python services
export PYTHON_SERVICES_API_URL=http://localhost:8081/api/v1
export PYTHON_SERVICES_GRPC_URL=localhost:50051
export PYTHON_MAX_WORKERS=4
```

## Monitoring and Observability

### Distributed Tracing

```go
// Go tracing with Python correlation
func (s *PipelineService) ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error) {
    span := trace.SpanFromContext(ctx)
    span.SetAttributes(
        attribute.String("pipeline.id", req.PipelineID),
        attribute.String("service.type", "go"),
    )
    
    // Inject trace context for Python
    traceContext := make(map[string]string)
    trace.Inject(ctx, propagation.MapCarrier(traceContext))
    req.TraceContext = traceContext
    
    // Execute Python service
    resp, err := s.pythonService.ExecutePipeline(ctx, req)
    
    span.SetAttributes(
        attribute.Bool("success", err == nil),
        attribute.String("python.service", "pipeline"),
    )
    
    return resp, err
}
```

### Metrics Collection

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

## Quality Standards

### Performance Standards

- **Response Time**: < 100ms for API calls
- **Python Service Response**: < 5 seconds for data processing
- **Throughput**: 1000+ concurrent requests
- **Resource Usage**: < 512MB RAM per Python process

### Availability Standards

- **Go Services**: 99.9% uptime
- **Python Services**: 99.5% uptime
- **Failover Time**: < 30 seconds
- **Recovery Time**: < 5 minutes

### Error Handling

- **Go Services**: Graceful degradation
- **Python Services**: Structured error responses
- **Cross-Service**: Correlation IDs for debugging
- **Monitoring**: Real-time error tracking

## Deployment

### Container Architecture

```yaml
# docker-compose.yml
version: '3.8'
services:
  flext-service:
    image: flext/service:latest
    ports:
      - "8081:8081"
    environment:
      - FLEXT_ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
  
  flexcore-runtime:
    image: flext/flexcore:latest
    ports:
      - "8080:8080"
    environment:
      - FLEXT_ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
  
  python-api:
    image: flext/python-api:latest
    ports:
      - "8000:8000"
    environment:
      - PYTHON_SERVICES_API_URL=http://flext-service:8081/api/v1
```

### Service Discovery

```go
// Service discovery in Go
type ServiceRegistry struct {
    services map[string]*ServiceInfo
    mutex    sync.RWMutex
}

func (r *ServiceRegistry) RegisterService(name string, info *ServiceInfo) {
    r.mutex.Lock()
    defer r.mutex.Unlock()
    r.services[name] = info
}

func (r *ServiceRegistry) GetService(name string) (*ServiceInfo, bool) {
    r.mutex.RLock()
    defer r.mutex.RUnlock()
    info, exists := r.services[name]
    return info, exists
}
```

## Related Documentation

- [Python-Go Integration](./python-go-integration.md) - Detailed integration patterns
- [Service Coordination](../integration/service-coordination.md) - Service communication
- [Package Structure](./pkg-structure.md) - Go package organization
- [Patterns](../patterns/README.md) - Implementation patterns

---

**FLEXT Service Architecture** - Distributed service architecture with Go orchestration and Python data processing capabilities.
