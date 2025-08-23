# FLEXT Service ↔ FlexCore Distributed Coordination

**Version**: 0.9.0 | **Status**: Production Ready | **Last Updated**: 2025-01-08

## Overview

This document defines the comprehensive integration patterns and coordination mechanisms between **FLEXT Service (Control Panel - Port 8081)**, **FlexCore Runtime (Port 8080)**, and the **Python Ecosystem (33 Projects)** within the FLEXT distributed architecture.

## Architecture Overview

### Distributed Service Coordination Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐  │
│  │  FLEXT Service      │◄──►│  FlexCore Runtime               │  │
│  │  (Control Panel)    │    │  (Distributed Execution)       │  │
│  │  Port 8081          │    │  Port 8080                      │  │
│  │                     │    │                                 │  │
│  │ • API Gateway       │    │ • Workflow Execution            │  │
│  │ • Service Discovery │    │ • Plugin Management             │  │
│  │ • Configuration     │    │ • Resource Coordination         │  │
│  │ • Monitoring        │    │ • Event Sourcing                │  │
│  │ • Python Integration│    │ • Python Orchestration          │  │
│  └─────────────────────┘    └─────────────────────────────────┘  │
│           │                              │                      │
│           └─────────── COORDINATION ─────┘                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              Windmill Workflow Engine                       │  │
│  │            (Orchestration Layer)                            │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    PYTHON ECOSYSTEM                        │  │
│  │                  (33 Projects)                             │  │
│  │  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │  │
│  │  │ Foundation  │ Integration │ Processing  │ Extensions  │  │  │
│  │  │ • flext-core│ • flext-api │ • flext-    │ • flext-tap-*│  │  │
│  │  │ • flext-obs │ • flext-auth│   meltano   │ • flext-target-*│  │  │
│  │  │             │ • flext-grpc│ • flext-ldap│ • flext-dbt-*│  │  │
│  │  │             │ • flext-web │ • flext-ldif│ • flext-*-ext│  │  │
│  │  │             │ • flext-cli │ • flext-db- │             │  │  │
│  │  │             │             │   oracle    │             │  │  │
│  │  └─────────────┴─────────────┴─────────────┴─────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────┬───────────────┬───────────────┬─────────────┐  │
│  │   Meltano     │  Ray Runtime  │  Kubernetes   │   Future    │  │
│  │ (Production)  │   (Future)    │   (Future)    │  Runtimes   │  │
│  │ Singer/DBT    │  ML/Analytics │ Orchestration │ Extensible  │  │
│  └───────────────┴───────────────┴───────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Patterns

### 1. Service Discovery and Registration

#### **FLEXT Service → FlexCore Discovery**

```go
// FlexCore discovery and health monitoring
type FlexCoreDiscovery struct {
    client     *http.Client
    baseURL    string
    logger     *logger.Logger
    healthTicker *time.Ticker
}

func (d *FlexCoreDiscovery) DiscoverFlexCoreInstances() (*FlexCoreTopology, error) {
    // 1. Discover available FlexCore instances
    instances, err := d.discoverInstances()
    if err != nil {
        return nil, fmt.Errorf("FlexCore discovery failed: %w", err)
    }

    // 2. Validate instance health and capabilities
    var healthy []*FlexCoreInstance
    for _, instance := range instances {
        if health, err := d.checkInstanceHealth(instance); err == nil && health.Status == "healthy" {
            instance.Capabilities = health.Capabilities
            instance.Runtimes = health.AvailableRuntimes
            healthy = append(healthy, instance)
        }
    }

    // 3. Build coordination topology
    return &FlexCoreTopology{
        Instances:       healthy,
        LoadBalancer:    d.createLoadBalancer(healthy),
        FailoverChain:   d.createFailoverChain(healthy),
        LastUpdated:     time.Now(),
    }, nil
}

func (d *FlexCoreDiscovery) checkInstanceHealth(instance *FlexCoreInstance) (*HealthReport, error) {
    resp, err := d.client.Get(fmt.Sprintf("%s/api/v1/health?detail=true", instance.BaseURL))
    if err != nil {
        return nil, fmt.Errorf("health check failed: %w", err)
    }
    defer resp.Body.Close()

    var health HealthReport
    if err := json.NewDecoder(resp.Body).Decode(&health); err != nil {
        return nil, fmt.Errorf("health response decode failed: %w", err)
    }

    return &health, nil
}
```

#### **Python Service Registration**

```go
// Python service registration and management
type PythonServiceRegistry struct {
    services map[string]*PythonServiceInfo
    mutex    sync.RWMutex
    logger   *logger.Logger
}

type PythonServiceInfo struct {
    Name         string            `json:"name"`
    Type         string            `json:"type"`
    Endpoint     string            `json:"endpoint"`
    HealthURL    string            `json:"health_url"`
    Capabilities []string          `json:"capabilities"`
    Version      string            `json:"version"`
    Status       string            `json:"status"`
    LastSeen     time.Time         `json:"last_seen"`
    Metadata     map[string]string `json:"metadata"`
}

func (r *PythonServiceRegistry) RegisterPythonService(info *PythonServiceInfo) error {
    r.mutex.Lock()
    defer r.mutex.Unlock()

    // Validate service information
    if err := r.validateServiceInfo(info); err != nil {
        return fmt.Errorf("invalid service info: %w", err)
    }

    // Check if service is healthy
    if err := r.checkServiceHealth(info); err != nil {
        return fmt.Errorf("service health check failed: %w", err)
    }

    // Register service
    r.services[info.Name] = info
    r.logger.Info("Python service registered",
        "name", info.Name,
        "type", info.Type,
        "endpoint", info.Endpoint,
        "capabilities", info.Capabilities)

    return nil
}

func (r *PythonServiceRegistry) GetPythonService(name string) (*PythonServiceInfo, bool) {
    r.mutex.RLock()
    defer r.mutex.RUnlock()

    info, exists := r.services[name]
    return info, exists
}

func (r *PythonServiceRegistry) ListPythonServices() []*PythonServiceInfo {
    r.mutex.RLock()
    defer r.mutex.RUnlock()

    services := make([]*PythonServiceInfo, 0, len(r.services))
    for _, service := range r.services {
        services = append(services, service)
    }
    return services
}
```

### 2. Python Service Integration

#### **gRPC Integration Pattern**

```go
// Go service calling Python via gRPC
type PythonServiceClient struct {
    client     *grpc.ClientConn
    logger     *logger.Logger
    timeout    time.Duration
}

func (c *PythonServiceClient) ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error) {
    // 1. Create gRPC context with timeout
    ctx, cancel := context.WithTimeout(ctx, c.timeout)
    defer cancel()

    // 2. Call Python service
    client := pb.NewPipelineServiceClient(c.client)
    resp, err := client.ExecutePipeline(ctx, &pb.PipelineRequest{
        PipelineId: req.PipelineID,
        Config:     req.Config,
        TraceContext: req.TraceContext,
    })

    if err != nil {
        c.logger.Error("Python service call failed",
            "pipeline_id", req.PipelineID,
            "error", err.Error())
        return nil, fmt.Errorf("python service error: %w", err)
    }

    // 3. Transform response
    return &PipelineResponse{
        Success: resp.Success,
        Data:    resp.Data,
        Error:   resp.Error,
    }, nil
}
```

```python
# Python gRPC service implementation
import grpc
from concurrent import futures
from flext_core.result import FlextResult
from flext_meltano import MeltanoRunner

class PipelineService(pb.PipelineServiceServicer):
    """gRPC service for pipeline execution."""

    def __init__(self, meltano_runner: MeltanoRunner):
        self._meltano_runner = meltano_runner
        self._logger = get_logger()

    def ExecutePipeline(self, request, context):
        """Execute pipeline via gRPC."""
        try:
            # Extract trace context from Go
            trace_context = request.trace_context
            if trace_context:
                self._logger.info("Received trace context",
                    correlation_id=trace_context.get("correlation_id"))

            # Execute pipeline
            result = await self._meltano_runner.run_pipeline(
                pipeline_id=request.pipeline_id,
                config=request.config
            )

            return pb.PipelineResponse(
                success=result.success,
                data=result.data if result.success else None,
                error=result.error if not result.success else None
            )

        except Exception as e:
            self._logger.error("Pipeline execution failed",
                pipeline_id=request.pipeline_id,
                error=str(e))
            return pb.PipelineResponse(
                success=False,
                error=f"Pipeline execution failed: {str(e)}"
            )

def serve():
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb.add_PipelineServiceServicer_to_server(PipelineService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

#### **HTTP/REST Integration Pattern**

```go
// Go service calling Python via HTTP
type PythonHTTPClient struct {
    client  *http.Client
    baseURL string
    logger  *logger.Logger
}

func (c *PythonHTTPClient) ExecutePipeline(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error) {
    // 1. Prepare request
    payload := map[string]interface{}{
        "pipeline_id": req.PipelineID,
        "config":      req.Config,
        "trace_context": req.TraceContext,
    }

    jsonData, err := json.Marshal(payload)
    if err != nil {
        return nil, fmt.Errorf("failed to marshal request: %w", err)
    }

    // 2. Create HTTP request
    httpReq, err := http.NewRequestWithContext(ctx, "POST",
        fmt.Sprintf("%s/api/v1/pipelines/execute", c.baseURL),
        bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, fmt.Errorf("failed to create request: %w", err)
    }

    httpReq.Header.Set("Content-Type", "application/json")
    httpReq.Header.Set("Authorization", fmt.Sprintf("Bearer %s", req.AuthToken))

    // 3. Execute request
    resp, err := c.client.Do(httpReq)
    if err != nil {
        return nil, fmt.Errorf("http request failed: %w", err)
    }
    defer resp.Body.Close()

    // 4. Parse response
    var result PipelineResponse
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, fmt.Errorf("failed to decode response: %w", err)
    }

    return &result, nil
}
```

```python
# Python HTTP service implementation
from fastapi import FastAPI, HTTPException, Depends
from flext_core.result import FlextResult
from flext_meltano import MeltanoRunner

app = FastAPI(title="FLEXT Python API")

@app.post("/api/v1/pipelines/execute")
async def execute_pipeline(request: PipelineExecuteRequest):
    """Execute pipeline via HTTP."""
    try:
        # Validate request
        if not request.pipeline_id:
            raise HTTPException(status_code=400, detail="Pipeline ID required")

        # Execute pipeline
        runner = MeltanoRunner()
        result = await runner.run_pipeline(
            pipeline_id=request.pipeline_id,
            config=request.config
        )

        if result.is_failure:
            raise HTTPException(
                status_code=400,
                detail=result.error
            )

        return {
            "success": True,
            "data": result.data,
            "pipeline_id": request.pipeline_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
```

### 3. Subprocess Integration Pattern

#### **Go Subprocess Manager**

```go
// Go executing Python scripts directly
type PythonSubprocessManager struct {
    pythonPath string
    workDir    string
    logger     *logger.Logger
    timeout    time.Duration
}

func (m *PythonSubprocessManager) ExecuteScript(ctx context.Context, script string, args []string) (*ExecutionResult, error) {
    // 1. Prepare command
    cmd := exec.CommandContext(ctx, m.pythonPath, append([]string{script}, args...)...)
    cmd.Dir = m.workDir

    // 2. Set environment variables
    cmd.Env = m.buildEnvironment()

    // 3. Capture output
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr

    // 4. Execute with timeout
    ctx, cancel := context.WithTimeout(ctx, m.timeout)
    defer cancel()

    startTime := time.Now()
    err := cmd.Run()
    duration := time.Since(startTime)

    // 5. Build result
    result := &ExecutionResult{
        ExitCode: cmd.ProcessState.ExitCode(),
        Stdout:   stdout.String(),
        Stderr:   stderr.String(),
        Duration: duration,
        Error:    err,
    }

    // 6. Log execution
    m.logger.Info("Python script executed",
        "script", script,
        "args", args,
        "exit_code", result.ExitCode,
        "duration", duration,
        "success", err == nil)

    return result, nil
}

func (m *PythonSubprocessManager) ExecutePipeline(ctx context.Context, pipelineID string, config map[string]interface{}) (*PipelineResult, error) {
    // 1. Prepare pipeline execution script
    script := "flext_meltano/scripts/pipeline_runner.py"
    configJSON, err := json.Marshal(config)
    if err != nil {
        return nil, fmt.Errorf("failed to marshal config: %w", err)
    }

    // 2. Execute pipeline script
    result, err := m.ExecuteScript(ctx, script, []string{pipelineID, string(configJSON)})
    if err != nil {
        return nil, fmt.Errorf("pipeline execution failed: %w", err)
    }

    // 3. Parse result
    if result.ExitCode != 0 {
        return nil, fmt.Errorf("pipeline failed with exit code %d: %s",
            result.ExitCode, result.Stderr)
    }

    // 4. Parse JSON output
    var pipelineResult PipelineResult
    if err := json.Unmarshal([]byte(result.Stdout), &pipelineResult); err != nil {
        return nil, fmt.Errorf("failed to parse pipeline result: %w", err)
    }

    return &pipelineResult, nil
}
```

```python
# Python script for subprocess execution
#!/usr/bin/env python3
"""Pipeline execution script for subprocess integration."""

import sys
import json
import asyncio
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

    try:
        # Execute pipeline
        runner = MeltanoRunner()
        result = asyncio.run(runner.run_pipeline(pipeline_id, config))

        # Output result as JSON
        output = {
            "success": result.success,
            "data": result.data if result.success else None,
            "error": result.error if not result.success else None,
            "pipeline_id": pipeline_id
        }

        print(json.dumps(output))
        sys.exit(0 if result.success else 1)

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Pipeline execution failed: {str(e)}",
            "pipeline_id": pipeline_id
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Coordination Mechanisms

### 1. Event-Driven Coordination

```go
// Event-driven coordination between services
type EventCoordinator struct {
    eventBus    messaging.EventBus
    logger      *logger.Logger
    registry    *PythonServiceRegistry
}

func (c *EventCoordinator) HandlePipelineRequest(ctx context.Context, event *PipelineRequestEvent) error {
    // 1. Publish pipeline started event
    startedEvent := &PipelineStartedEvent{
        PipelineID: event.PipelineID,
        Timestamp:  time.Now(),
        UserID:     event.UserID,
    }
    if err := c.eventBus.Publish(ctx, startedEvent); err != nil {
        return fmt.Errorf("failed to publish started event: %w", err)
    }

    // 2. Route to appropriate Python service
    service, exists := c.registry.GetPythonService("meltano")
    if !exists {
        return fmt.Errorf("meltano service not available")
    }

    // 3. Execute pipeline
    result, err := c.executePipeline(ctx, service, event)
    if err != nil {
        // Publish failure event
        failureEvent := &PipelineFailedEvent{
            PipelineID: event.PipelineID,
            Error:      err.Error(),
            Timestamp:  time.Now(),
        }
        c.eventBus.Publish(ctx, failureEvent)
        return err
    }

    // 4. Publish completion event
    completionEvent := &PipelineCompletedEvent{
        PipelineID:     event.PipelineID,
        RecordsProcessed: result.RecordsProcessed,
        Duration:        result.Duration,
        Timestamp:       time.Now(),
    }
    return c.eventBus.Publish(ctx, completionEvent)
}
```

### 2. Health Monitoring and Failover

```go
// Health monitoring for Python services
type PythonServiceHealthMonitor struct {
    registry *PythonServiceRegistry
    logger   *logger.Logger
    interval time.Duration
}

func (m *PythonServiceHealthMonitor) StartMonitoring() {
    ticker := time.NewTicker(m.interval)
    go func() {
        for range ticker.C {
            m.checkAllServices()
        }
    }()
}

func (m *PythonServiceHealthMonitor) checkAllServices() {
    services := m.registry.ListPythonServices()

    for _, service := range services {
        go func(s *PythonServiceInfo) {
            if err := m.checkServiceHealth(s); err != nil {
                m.logger.Warn("Python service health check failed",
                    "service", s.Name,
                    "error", err.Error())

                // Mark service as unhealthy
                s.Status = "unhealthy"
                s.LastSeen = time.Now()

                // Trigger failover if needed
                m.triggerFailover(s)
            } else {
                // Mark service as healthy
                s.Status = "healthy"
                s.LastSeen = time.Now()
            }
        }(service)
    }
}

func (m *PythonServiceHealthMonitor) checkServiceHealth(service *PythonServiceInfo) error {
    client := &http.Client{Timeout: 5 * time.Second}

    resp, err := client.Get(service.HealthURL)
    if err != nil {
        return fmt.Errorf("health check request failed: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("health check returned status %d", resp.StatusCode)
    }

    return nil
}

func (m *PythonServiceHealthMonitor) triggerFailover(service *PythonServiceInfo) {
    // Find alternative service
    alternatives := m.findAlternativeServices(service)
    if len(alternatives) > 0 {
        m.logger.Info("Triggering failover",
            "from_service", service.Name,
            "to_service", alternatives[0].Name)

        // Update routing to use alternative service
        m.updateServiceRouting(service.Name, alternatives[0].Name)
    }
}
```

### 3. Load Balancing and Scaling

```go
// Load balancing for Python services
type PythonServiceLoadBalancer struct {
    services []*PythonServiceInfo
    strategy LoadBalancingStrategy
    mutex    sync.RWMutex
}

type LoadBalancingStrategy interface {
    SelectService(services []*PythonServiceInfo, request *PipelineRequest) *PythonServiceInfo
}

type RoundRobinStrategy struct {
    current int
    mutex   sync.Mutex
}

func (r *RoundRobinStrategy) SelectService(services []*PythonServiceInfo, request *PipelineRequest) *PythonServiceInfo {
    r.mutex.Lock()
    defer r.mutex.Unlock()

    if len(services) == 0 {
        return nil
    }

    service := services[r.current%len(services)]
    r.current++

    return service
}

type WeightedStrategy struct {
    weights map[string]int
}

func (w *WeightedStrategy) SelectService(services []*PythonServiceInfo, request *PipelineRequest) *PythonServiceInfo {
    if len(services) == 0 {
        return nil
    }

    // Calculate total weight
    totalWeight := 0
    for _, service := range services {
        weight := w.weights[service.Name]
        if weight == 0 {
            weight = 1 // Default weight
        }
        totalWeight += weight
    }

    // Select service based on weight
    random := rand.Intn(totalWeight)
    currentWeight := 0

    for _, service := range services {
        weight := w.weights[service.Name]
        if weight == 0 {
            weight = 1
        }
        currentWeight += weight

        if random < currentWeight {
            return service
        }
    }

    return services[0] // Fallback
}
```

## Configuration Management

### 1. Shared Configuration

```yaml
# flext-coordination.yaml
coordination:
  service_discovery:
    enabled: true
    interval: "30s"
    timeout: "10s"

  python_services:
    registration:
      enabled: true
      auto_discovery: true
      health_check_interval: "60s"

    load_balancing:
      strategy: "round_robin" # round_robin, weighted, least_connections
      health_check_timeout: "5s"
      failover_enabled: true

    scaling:
      auto_scaling: true
      min_instances: 1
      max_instances: 10
      scale_up_threshold: 0.8
      scale_down_threshold: 0.3

  event_coordination:
    enabled: true
    event_bus: "redis" # redis, kafka, nats
    event_store: "postgres"
    correlation_enabled: true

python_services:
  meltano:
    endpoint: "http://localhost:8001"
    health_url: "http://localhost:8001/health"
    capabilities: ["pipeline_execution", "data_extraction", "data_loading"]
    weight: 3

  api:
    endpoint: "http://localhost:8000"
    health_url: "http://localhost:8000/health"
    capabilities: ["rest_api", "authentication"]
    weight: 2

  grpc:
    endpoint: "localhost:50051"
    health_url: "http://localhost:50052/health"
    capabilities: ["grpc_service", "pipeline_execution"]
    weight: 2
```

### 2. Environment Variables

```bash
# Service coordination
export FLEXT_COORDINATION_ENABLED=true
export FLEXT_SERVICE_DISCOVERY_INTERVAL=30s
export FLEXT_HEALTH_CHECK_TIMEOUT=10s

# Python service configuration
export PYTHON_SERVICES_MELTANO_URL=http://localhost:8001
export PYTHON_SERVICES_API_URL=http://localhost:8000
export PYTHON_SERVICES_GRPC_URL=localhost:50051

# Load balancing
export FLEXT_LOAD_BALANCING_STRATEGY=round_robin
export FLEXT_FAILOVER_ENABLED=true
export FLEXT_AUTO_SCALING_ENABLED=true

# Event coordination
export FLEXT_EVENT_BUS_URL=redis://localhost:6379
export FLEXT_EVENT_STORE_URL=postgres://user:pass@localhost:5432/events
```

## Monitoring and Observability

### 1. Distributed Tracing

```go
// Distributed tracing across Go and Python services
func (c *Coordinator) ExecutePipelineWithTracing(ctx context.Context, req *PipelineRequest) (*PipelineResponse, error) {
    // 1. Create trace span
    span := trace.SpanFromContext(ctx)
    span.SetAttributes(
        attribute.String("pipeline.id", req.PipelineID),
        attribute.String("service.type", "go_coordinator"),
    )

    // 2. Inject trace context for Python
    traceContext := make(map[string]string)
    trace.Inject(ctx, propagation.MapCarrier(traceContext))

    // 3. Add trace context to request
    req.TraceContext = traceContext

    // 4. Execute pipeline with tracing
    result, err := c.executePipeline(ctx, req)

    // 5. Record span attributes
    span.SetAttributes(
        attribute.Bool("success", err == nil),
        attribute.String("python.service", "meltano"),
        attribute.Int64("records_processed", result.RecordsProcessed),
    )

    return result, err
}
```

### 2. Metrics Collection

```go
// Metrics for service coordination
type CoordinationMetrics struct {
    pipelineExecutions    *prometheus.CounterVec
    serviceHealthChecks   *prometheus.CounterVec
    loadBalancerRequests  *prometheus.CounterVec
    failoverEvents        *prometheus.CounterVec
    pythonServiceLatency  *prometheus.HistogramVec
}

func (m *CoordinationMetrics) RecordPipelineExecution(pipelineID string, serviceName string, success bool, duration time.Duration) {
    m.pipelineExecutions.WithLabelValues(pipelineID, serviceName, fmt.Sprintf("%t", success)).Inc()
    m.pythonServiceLatency.WithLabelValues(serviceName).Observe(duration.Seconds())
}

func (m *CoordinationMetrics) RecordServiceHealthCheck(serviceName string, healthy bool) {
    m.serviceHealthChecks.WithLabelValues(serviceName, fmt.Sprintf("%t", healthy)).Inc()
}

func (m *CoordinationMetrics) RecordLoadBalancerRequest(serviceName string, strategy string) {
    m.loadBalancerRequests.WithLabelValues(serviceName, strategy).Inc()
}

func (m *CoordinationMetrics) RecordFailoverEvent(fromService string, toService string) {
    m.failoverEvents.WithLabelValues(fromService, toService).Inc()
}
```

## Quality Standards

### 1. Performance Standards

- **Service Discovery**: < 5 seconds for new service registration
- **Health Checks**: < 2 seconds per service check
- **Load Balancing**: < 100ms for service selection
- **Failover**: < 30 seconds for automatic failover
- **Event Processing**: < 1 second for event propagation

### 2. Reliability Standards

- **Service Availability**: 99.9% uptime for critical services
- **Failover Success Rate**: 99.5% successful failovers
- **Event Delivery**: 99.99% event delivery guarantee
- **Data Consistency**: Eventual consistency with < 5 second lag

### 3. Monitoring Standards

- **Real-time Metrics**: All coordination metrics available in real-time
- **Alerting**: Automated alerts for service failures and performance degradation
- **Logging**: Structured logging with correlation IDs across all services
- **Tracing**: Distributed tracing with 100% coverage of service interactions

## Related Documentation

- [Python-Go Integration](../architecture/python-go-integration.md) - Detailed integration patterns
- [Service Architecture](../architecture/services.md) - Overall service design
- [Package Structure](../architecture/pkg-structure.md) - Go package organization
- [Patterns](../patterns/README.md) - Implementation patterns

---

**FLEXT Service ↔ FlexCore Distributed Coordination** - Comprehensive coordination patterns that enable seamless integration between Go control plane, FlexCore runtime, and Python ecosystem.
