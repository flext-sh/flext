# FLEXT Integration Patterns

**Comprehensive guide to integration patterns and communication protocols across the FLEXT ecosystem**

**Version**: 0.9.0
**Last Updated**: 2025-08-02  
**Authority**: FLEXT Architecture Team  
**Scope**: All ecosystem integration patterns

---

## 🎯 Integration Overview

The FLEXT ecosystem employs multiple integration patterns to enable seamless communication between 32 interconnected projects while maintaining architectural boundaries and performance requirements.

### **Integration Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT INTEGRATION PATTERNS                   │
├─────────────────────────────────────────────────────────────────┤
│  🔄 SERVICE-TO-SERVICE INTEGRATION                             │
│  ├─ FlexCore ↔ FLEXT Service    # HTTP/gRPC + Events          │
│  ├─ Control Panel ↔ Services    # REST API + Message Bus      │
│  └─ Cross-Service Events        # Domain Event Broadcasting    │
├─────────────────────────────────────────────────────────────────┤
│  📚 LIBRARY INTEGRATION PATTERNS                               │
│  ├─ Foundation Layer            # FlextResult + DI Container   │
│  ├─ Infrastructure Libraries    # Shared Interfaces + Adapters │
│  ├─ Application Libraries       # Service Layer Integration    │
│  └─ Singer Plugin Integration   # Meltano Orchestration       │
├─────────────────────────────────────────────────────────────────┤
│  🌉 BRIDGE PATTERNS                                            │
│  ├─ Go-Python Bridge           # Process + IPC Communication   │
│  ├─ Meltano Integration        # Plugin System + CLI Bridge    │
│  └─ External System APIs       # REST/gRPC/Database Adapters   │
├─────────────────────────────────────────────────────────────────┤
│  📡 EVENT-DRIVEN COMMUNICATION                                 │
│  ├─ Domain Events              # Business Event Publishing     │
│  ├─ Integration Events         # Cross-Service Coordination    │
│  └─ System Events              # Infrastructure Notifications  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Service-to-Service Integration

### **FlexCore ↔ FLEXT Service Communication**

#### **HTTP REST Integration Pattern**

**Architecture:**

```
FlexCore (Go:8080) ←─── HTTP/JSON ────→ FLEXT Service (Go/Python:8081)
       │                                           │
       ├─ Plugin Management                       ├─ Meltano Orchestration
       ├─ Event Sourcing                          ├─ Singer Execution
       ├─ Performance Monitoring                  ├─ DBT Transformations
       └─ Distributed Coordination                └─ Python Bridge
```

**Communication Protocols:**

```go
// FlexCore → FLEXT Service: Plugin Execution Request
type PluginExecutionRequest struct {
    PluginID    string                 `json:"plugin_id"`
    Command     string                 `json:"command"`
    Args        []string               `json:"args"`
    Environment map[string]string      `json:"environment"`
    Timeout     time.Duration          `json:"timeout"`
    Context     map[string]interface{} `json:"context"`
}

// FLEXT Service → FlexCore: Execution Response
type PluginExecutionResponse struct {
    ExecutionID string                 `json:"execution_id"`
    Status      string                 `json:"status"`
    Output      string                 `json:"output"`
    Error       string                 `json:"error,omitempty"`
    Metrics     ExecutionMetrics       `json:"metrics"`
    Events      []DomainEvent          `json:"events"`
}

// Implementation Example
func (fc *FlexCore) ExecutePlugin(request PluginExecutionRequest) (*PluginExecutionResponse, error) {
    client := &http.Client{Timeout: request.Timeout}

    requestBody, _ := json.Marshal(request)
    resp, err := client.Post(
        "http://flext-service:8081/api/v1/plugins/execute",
        "application/json",
        bytes.NewBuffer(requestBody),
    )

    if err != nil {
        return nil, fmt.Errorf("plugin execution failed: %w", err)
    }

    var response PluginExecutionResponse
    return &response, json.NewDecoder(resp.Body).Decode(&response)
}
```

#### **gRPC High-Performance Integration**

```protobuf
// flext_integration.proto
syntax = "proto3";

package flext.integration.v1;

service FlextIntegrationService {
    // High-frequency plugin management
    rpc ExecutePlugin(PluginExecutionRequest) returns (PluginExecutionResponse);

    // Real-time event streaming
    rpc StreamEvents(EventStreamRequest) returns (stream DomainEvent);

    // Performance monitoring
    rpc GetMetrics(MetricsRequest) returns (MetricsResponse);

    // Health and status
    rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}

message PluginExecutionRequest {
    string plugin_id = 1;
    string command = 2;
    repeated string args = 3;
    map<string, string> environment = 4;
    int64 timeout_seconds = 5;
    google.protobuf.Struct context = 6;
}

message PluginExecutionResponse {
    string execution_id = 1;
    PluginStatus status = 2;
    string output = 3;
    string error = 4;
    ExecutionMetrics metrics = 5;
    repeated DomainEvent events = 6;
}
```

### **Event-Driven Service Coordination**

#### **Domain Event Pattern**

```go
// Cross-service domain events
type PipelineExecutionStarted struct {
    BaseEvent
    PipelineID   string            `json:"pipeline_id"`
    ExecutionID  string            `json:"execution_id"`
    ServiceID    string            `json:"service_id"`
    StartedBy    string            `json:"started_by"`
    StartedAt    time.Time         `json:"started_at"`
    Config       PipelineConfig    `json:"config"`
    Context      map[string]string `json:"context"`
}

type PipelineExecutionCompleted struct {
    BaseEvent
    PipelineID    string                 `json:"pipeline_id"`
    ExecutionID   string                 `json:"execution_id"`
    Status        string                 `json:"status"`
    CompletedAt   time.Time              `json:"completed_at"`
    Duration      time.Duration          `json:"duration"`
    RecordsCount  int64                  `json:"records_count"`
    ErrorCount    int64                  `json:"error_count"`
    Metrics       PipelineMetrics        `json:"metrics"`
}

// Event publishing across services
type CrossServiceEventBus struct {
    redisClient   *redis.Client
    httpClients   map[string]*http.Client
    subscribers   map[string][]EventHandler
}

func (bus *CrossServiceEventBus) PublishDomainEvent(event DomainEvent) error {
    // Publish to Redis for immediate subscribers
    eventData, _ := json.Marshal(event)
    if err := bus.redisClient.Publish(ctx, event.Type(), eventData).Err(); err != nil {
        return fmt.Errorf("failed to publish to Redis: %w", err)
    }

    // HTTP webhook notifications for external services
    for serviceID, client := range bus.httpClients {
        go func(id string, c *http.Client) {
            endpoint := fmt.Sprintf("http://%s/api/v1/events/%s", id, event.Type())
            req, _ := http.NewRequest("POST", endpoint, bytes.NewBuffer(eventData))
            req.Header.Set("Content-Type", "application/json")
            req.Header.Set("X-Event-Source", "flext-ecosystem")

            if _, err := c.Do(req); err != nil {
                log.Printf("Failed to notify service %s of event %s: %v", id, event.Type(), err)
            }
        }(serviceID, client)
    }

    return nil
}
```

---

## 📚 Library Integration Patterns

### **Foundation Layer Integration (flext-core)**

#### **FlextResult Pattern Integration**

```python
# Consistent error handling across all libraries
from flext_core import FlextResult, get_logger

logger = get_logger(__name__)

def library_operation(input_data: dict) -> FlextResult[ProcessedData]:
    """Example of FlextResult pattern usage in library integration."""
    try:
        # Validate input using another library
        validation_result = validate_with_another_library(input_data)
        if validation_result.is_failure:
            return validation_result  # Chain failure through

        # Process using infrastructure library
        processing_result = process_with_infrastructure_lib(validation_result.data)
        if processing_result.is_failure:
            logger.error("Processing failed", error=processing_result.error)
            return processing_result

        # Success case
        return FlextResult.ok(processing_result.data)

    except Exception as e:
        logger.exception("Unexpected error in library operation")
        return FlextResult.fail(
            error=f"Library operation failed: {e}",
            error_code="LIBRARY_OPERATION_ERROR",
            context={"input_data_keys": list(input_data.keys())}
        )

# Monadic composition across libraries
def complex_cross_library_operation(data: dict) -> FlextResult[FinalResult]:
    """Chain operations across multiple libraries using monadic composition."""
    return (
        flext_validation.validate_input(data)
        .flat_map(lambda valid_data: flext_db_oracle.fetch_related_data(valid_data))
        .flat_map(lambda enriched_data: flext_ldap.authenticate_user(enriched_data))
        .flat_map(lambda auth_data: flext_meltano.process_pipeline(auth_data))
        .map(lambda result: create_final_result(result))
    )
```

#### **Dependency Injection Container Integration**

```python
# Global container usage across libraries
from flext_core import get_flext_container, ServiceKey

# Service registration in library initialization
def configure_library_services() -> FlextResult[None]:
    """Configure services for cross-library integration."""
    container = get_flext_container()

    # Register library-specific services
    oracle_service_key = ServiceKey[OracleService]("oracle_service")
    ldap_service_key = ServiceKey[LdapService]("ldap_service")
    meltano_service_key = ServiceKey[MeltanoService]("meltano_service")

    container.register_typed(oracle_service_key, OracleService())
    container.register_typed(ldap_service_key, LdapService())
    container.register_typed(meltano_service_key, MeltanoService())

    # Register cross-library integration services
    integration_service = CrossLibraryIntegrationService(
        oracle_service=container.get_typed(oracle_service_key).unwrap(),
        ldap_service=container.get_typed(ldap_service_key).unwrap(),
        meltano_service=container.get_typed(meltano_service_key).unwrap()
    )

    container.register("integration_service", integration_service)
    return FlextResult.ok(None)

# Service usage in library operations
def library_service_operation(data: dict) -> FlextResult[ProcessedData]:
    """Use services from global container for cross-library operations."""
    container = get_flext_container()

    # Get services from container
    oracle_service_result = container.get_typed("oracle_service", OracleService)
    if oracle_service_result.is_failure:
        return FlextResult.fail("Oracle service not available")

    ldap_service_result = container.get_typed("ldap_service", LdapService)
    if ldap_service_result.is_failure:
        return FlextResult.fail("LDAP service not available")

    # Use services for integration
    oracle_service = oracle_service_result.data
    ldap_service = ldap_service_result.data

    # Coordinated operation across services
    return perform_coordinated_operation(oracle_service, ldap_service, data)
```

### **Infrastructure Library Integration**

#### **Shared Interface Pattern**

```python
# Common interfaces for infrastructure libraries
from flext_core import FlextResult
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic

T = TypeVar('T')

class DatabaseConnection(Protocol):
    """Common database connection interface."""

    def execute_query(self, query: str, params: dict) -> FlextResult[list[dict]]:
        """Execute database query with parameters."""
        ...

    def begin_transaction(self) -> FlextResult[TransactionContext]:
        """Begin database transaction."""
        ...

    def health_check(self) -> FlextResult[HealthStatus]:
        """Check database connection health."""
        ...

class DirectoryService(Protocol):
    """Common directory service interface."""

    def search(self, base_dn: str, filter: str) -> FlextResult[list[DirectoryEntry]]:
        """Search directory entries."""
        ...

    def authenticate(self, username: str, password: str) -> FlextResult[AuthResult]:
        """Authenticate user credentials."""
        ...

    def get_user_groups(self, username: str) -> FlextResult[list[str]]:
        """Get user group memberships."""
        ...

# Adapter implementations in infrastructure libraries
class OracleConnectionAdapter:
    """flext-db-oracle implementation of DatabaseConnection protocol."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    def execute_query(self, query: str, params: dict) -> FlextResult[list[dict]]:
        try:
            # Oracle-specific implementation
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = [dict(zip([d[0] for d in cursor.description], row))
                          for row in cursor.fetchall()]
                return FlextResult.ok(results)
        except Exception as e:
            return FlextResult.fail(f"Oracle query failed: {e}")

class LdapDirectoryAdapter:
    """flext-ldap implementation of DirectoryService protocol."""

    def __init__(self, server_uri: str, bind_dn: str, bind_password: str):
        self.server_uri = server_uri
        self.bind_dn = bind_dn
        self.bind_password = bind_password

    def search(self, base_dn: str, filter: str) -> FlextResult[list[DirectoryEntry]]:
        try:
            # LDAP-specific implementation
            conn = ldap.initialize(self.server_uri)
            conn.simple_bind_s(self.bind_dn, self.bind_password)
            result_data = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, filter)

            entries = [DirectoryEntry.from_ldap_result(dn, attrs)
                      for dn, attrs in result_data if dn is not None]
            return FlextResult.ok(entries)
        except Exception as e:
            return FlextResult.fail(f"LDAP search failed: {e}")
```

---

## 🌉 Bridge Patterns

### **Go-Python Integration Bridge**

#### **Process-Based Bridge Pattern**

```go
// Go service executing Python processes
type PythonBridge struct {
    pythonExecutable string
    workingDirectory string
    environment      map[string]string
    timeout          time.Duration
    logger           *logger.Logger
}

type PythonExecutionRequest struct {
    Script      string            `json:"script"`
    Arguments   []string          `json:"arguments"`
    Environment map[string]string `json:"environment"`
    Timeout     time.Duration     `json:"timeout"`
    WorkingDir  string            `json:"working_dir"`
}

type PythonExecutionResult struct {
    ExitCode     int               `json:"exit_code"`
    Stdout       string            `json:"stdout"`
    Stderr       string            `json:"stderr"`
    Duration     time.Duration     `json:"duration"`
    ProcessID    int               `json:"process_id"`
    Error        string            `json:"error,omitempty"`
}

func (pb *PythonBridge) ExecutePythonScript(req PythonExecutionRequest) (*PythonExecutionResult, error) {
    startTime := time.Now()

    // Prepare command
    cmd := exec.Command(pb.pythonExecutable, append([]string{req.Script}, req.Arguments...)...)
    cmd.Dir = req.WorkingDir
    cmd.Env = pb.buildEnvironment(req.Environment)

    // Set up output capture
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr

    // Execute with timeout
    ctx, cancel := context.WithTimeout(context.Background(), req.Timeout)
    defer cancel()

    if err := cmd.Start(); err != nil {
        return nil, fmt.Errorf("failed to start Python process: %w", err)
    }

    processID := cmd.Process.Pid
    pb.logger.Info("Started Python process", "pid", processID, "script", req.Script)

    // Wait for completion or timeout
    done := make(chan error, 1)
    go func() {
        done <- cmd.Wait()
    }()

    select {
    case err := <-done:
        duration := time.Since(startTime)

        result := &PythonExecutionResult{
            ProcessID: processID,
            Duration:  duration,
            Stdout:    stdout.String(),
            Stderr:    stderr.String(),
        }

        if err != nil {
            if exitError, ok := err.(*exec.ExitError); ok {
                result.ExitCode = exitError.ExitCode()
            } else {
                result.Error = err.Error()
            }
        }

        pb.logger.Info("Python process completed",
            "pid", processID,
            "duration", duration,
            "exit_code", result.ExitCode)

        return result, nil

    case <-ctx.Done():
        // Timeout occurred
        if err := cmd.Process.Kill(); err != nil {
            pb.logger.Error("Failed to kill timed-out Python process", "pid", processID, "error", err)
        }

        return &PythonExecutionResult{
            ProcessID: processID,
            Duration:  time.Since(startTime),
            ExitCode:  -1,
            Error:     "Python process timed out",
            Stderr:    stderr.String(),
        }, fmt.Errorf("Python process timed out after %v", req.Timeout)
    }
}

// High-level Meltano integration
func (pb *PythonBridge) ExecuteMeltanoPipeline(config MeltanoConfig) (*PipelineResult, error) {
    script := "scripts/run_meltano_pipeline.py"
    args := []string{
        "--config", config.ToJSON(),
        "--project-dir", config.ProjectDirectory,
        "--environment", config.Environment,
    }

    request := PythonExecutionRequest{
        Script:      script,
        Arguments:   args,
        Environment: config.Environment,
        Timeout:     config.Timeout,
        WorkingDir:  config.ProjectDirectory,
    }

    result, err := pb.ExecutePythonScript(request)
    if err != nil {
        return nil, fmt.Errorf("Meltano pipeline execution failed: %w", err)
    }

    if result.ExitCode != 0 {
        return nil, fmt.Errorf("Meltano pipeline failed with exit code %d: %s",
            result.ExitCode, result.Stderr)
    }

    // Parse Python output into Go structures
    var pipelineResult PipelineResult
    if err := json.Unmarshal([]byte(result.Stdout), &pipelineResult); err != nil {
        return nil, fmt.Errorf("failed to parse Meltano pipeline result: %w", err)
    }

    return &pipelineResult, nil
}
```

#### **IPC-Based Bridge Pattern**

```go
// Named pipe communication for high-frequency operations
type IPCPythonBridge struct {
    namedPipePath string
    connection    net.Conn
    encoder       *json.Encoder
    decoder       *json.Decoder
    mutex         sync.Mutex
}

type IPCRequest struct {
    ID       string      `json:"id"`
    Method   string      `json:"method"`
    Params   interface{} `json:"params"`
    Timeout  int         `json:"timeout"`
}

type IPCResponse struct {
    ID     string      `json:"id"`
    Result interface{} `json:"result,omitempty"`
    Error  string      `json:"error,omitempty"`
}

func (ipc *IPCPythonBridge) CallPythonMethod(method string, params interface{}) (interface{}, error) {
    ipc.mutex.Lock()
    defer ipc.mutex.Unlock()

    requestID := generateRequestID()
    request := IPCRequest{
        ID:      requestID,
        Method:  method,
        Params:  params,
        Timeout: 30,
    }

    // Send request
    if err := ipc.encoder.Encode(request); err != nil {
        return nil, fmt.Errorf("failed to send IPC request: %w", err)
    }

    // Read response
    var response IPCResponse
    if err := ipc.decoder.Decode(&response); err != nil {
        return nil, fmt.Errorf("failed to read IPC response: %w", err)
    }

    if response.ID != requestID {
        return nil, fmt.Errorf("IPC response ID mismatch: expected %s, got %s", requestID, response.ID)
    }

    if response.Error != "" {
        return nil, fmt.Errorf("Python method error: %s", response.Error)
    }

    return response.Result, nil
}
```

### **Meltano Plugin Integration Bridge**

#### **Plugin System Integration**

```python
# Python side: Meltano plugin bridge
from flext_meltano import FlextMeltanoPlugin, FlextMeltanoOrchestrator
from flext_core import FlextResult, get_logger

class FlextMeltanoBridge:
    """Bridge between Go services and Meltano plugin system."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.orchestrator = FlextMeltanoOrchestrator(project_root)
        self.logger = get_logger(__name__)

    def execute_tap(self, tap_name: str, config: dict) -> FlextResult[dict]:
        """Execute Singer tap through Meltano."""
        try:
            self.logger.info("Executing tap", tap_name=tap_name)

            # Configure tap
            config_result = self.orchestrator.configure_plugin(tap_name, config)
            if config_result.is_failure:
                return config_result

            # Execute tap
            execution_result = self.orchestrator.run_tap(tap_name)
            if execution_result.is_failure:
                return execution_result

            return FlextResult.ok({
                "tap_name": tap_name,
                "records_extracted": execution_result.data.get("records_count", 0),
                "execution_time": execution_result.data.get("duration", 0),
                "status": "completed"
            })

        except Exception as e:
            self.logger.exception("Tap execution failed", tap_name=tap_name)
            return FlextResult.fail(f"Tap execution error: {e}")

    def execute_target(self, target_name: str, config: dict, input_stream: str) -> FlextResult[dict]:
        """Execute Singer target through Meltano."""
        try:
            self.logger.info("Executing target", target_name=target_name)

            # Configure target
            config_result = self.orchestrator.configure_plugin(target_name, config)
            if config_result.is_failure:
                return config_result

            # Execute target with input stream
            execution_result = self.orchestrator.run_target(target_name, input_stream)
            if execution_result.is_failure:
                return execution_result

            return FlextResult.ok({
                "target_name": target_name,
                "records_loaded": execution_result.data.get("records_count", 0),
                "execution_time": execution_result.data.get("duration", 0),
                "status": "completed"
            })

        except Exception as e:
            self.logger.exception("Target execution failed", target_name=target_name)
            return FlextResult.fail(f"Target execution error: {e}")

    def execute_dbt_models(self, models: list[str], **kwargs) -> FlextResult[dict]:
        """Execute DBT models through Meltano."""
        try:
            self.logger.info("Executing DBT models", models=models)

            # Run DBT models
            execution_result = self.orchestrator.run_dbt_models(models, **kwargs)
            if execution_result.is_failure:
                return execution_result

            return FlextResult.ok({
                "models": models,
                "models_executed": len(models),
                "execution_time": execution_result.data.get("duration", 0),
                "status": "completed"
            })

        except Exception as e:
            self.logger.exception("DBT execution failed", models=models)
            return FlextResult.fail(f"DBT execution error: {e}")

# CLI bridge for Go service integration
def main():
    """CLI entry point for Go-Python bridge communication."""
    import sys
    import json

    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: bridge_script.py <method> <params_json>"}))
        sys.exit(1)

    method = sys.argv[1]
    params_json = sys.argv[2]

    try:
        params = json.loads(params_json)
        bridge = FlextMeltanoBridge(params.get("project_root", "."))

        if method == "execute_tap":
            result = bridge.execute_tap(params["tap_name"], params["config"])
        elif method == "execute_target":
            result = bridge.execute_target(params["target_name"], params["config"], params["input_stream"])
        elif method == "execute_dbt_models":
            result = bridge.execute_dbt_models(params["models"], **params.get("options", {}))
        else:
            result = FlextResult.fail(f"Unknown method: {method}")

        if result.is_success:
            print(json.dumps({"result": result.data}))
        else:
            print(json.dumps({"error": result.error}))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": f"Bridge execution error: {e}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📡 Event-Driven Communication

### **Domain Event Broadcasting**

#### **Event Schema and Types**

```go
// Core event types for cross-service communication
type EventType string

const (
    // Pipeline events
    PipelineCreatedEvent     EventType = "pipeline.created"
    PipelineStartedEvent     EventType = "pipeline.started"
    PipelineCompletedEvent   EventType = "pipeline.completed"
    PipelineFailedEvent      EventType = "pipeline.failed"

    // Data events
    DataExtractionStarted    EventType = "data.extraction.started"
    DataExtractionCompleted  EventType = "data.extraction.completed"
    DataTransformationStarted EventType = "data.transformation.started"
    DataLoadingCompleted     EventType = "data.loading.completed"

    // System events
    ServiceStartedEvent      EventType = "service.started"
    ServiceStoppedEvent      EventType = "service.stopped"
    ServiceHealthChanged     EventType = "service.health.changed"

    // Integration events
    PluginRegistered         EventType = "plugin.registered"
    PluginExecutionStarted   EventType = "plugin.execution.started"
    PluginExecutionCompleted EventType = "plugin.execution.completed"
)

// Base event structure
type BaseEvent struct {
    ID          string                 `json:"id"`
    Type        EventType              `json:"type"`
    Source      string                 `json:"source"`
    SpecVersion string                 `json:"spec_version"`
    Time        time.Time              `json:"time"`
    Subject     string                 `json:"subject"`
    Data        map[string]interface{} `json:"data"`
    Extensions  map[string]string      `json:"extensions,omitempty"`
}

// Specific event implementations
type PipelineExecutionEvent struct {
    BaseEvent
    PipelineID   string        `json:"pipeline_id"`
    ExecutionID  string        `json:"execution_id"`
    ServiceID    string        `json:"service_id"`
    UserID       string        `json:"user_id"`
    Status       string        `json:"status"`
    StartTime    time.Time     `json:"start_time"`
    EndTime      *time.Time    `json:"end_time,omitempty"`
    Duration     time.Duration `json:"duration"`
    RecordCount  int64         `json:"record_count"`
    ErrorCount   int64         `json:"error_count"`
    Config       interface{}   `json:"config"`
}
```

#### **Event Bus Implementation**

```go
// Multi-transport event bus for ecosystem communication
type FlextEventBus struct {
    redisClient    *redis.Client
    httpEndpoints  map[string]string
    grpcClients    map[string]FlextEventServiceClient
    localHandlers  map[EventType][]EventHandler
    logger         *logger.Logger
    metrics        *metrics.EventMetrics
}

type EventHandler interface {
    Handle(ctx context.Context, event BaseEvent) error
    EventTypes() []EventType
}

func (eb *FlextEventBus) PublishEvent(ctx context.Context, event BaseEvent) error {
    eb.logger.Info("Publishing event",
        "type", event.Type,
        "id", event.ID,
        "source", event.Source)

    // Record metrics
    eb.metrics.EventPublished(string(event.Type), event.Source)

    var publishErrors []error

    // 1. Publish to Redis for immediate local subscribers
    if err := eb.publishToRedis(ctx, event); err != nil {
        publishErrors = append(publishErrors, fmt.Errorf("Redis publish failed: %w", err))
    }

    // 2. Send to HTTP endpoints for REST-based services
    for serviceID, endpoint := range eb.httpEndpoints {
        if err := eb.publishToHTTP(ctx, event, serviceID, endpoint); err != nil {
            publishErrors = append(publishErrors, fmt.Errorf("HTTP publish to %s failed: %w", serviceID, err))
        }
    }

    // 3. Send to gRPC clients for high-performance services
    for serviceID, client := range eb.grpcClients {
        if err := eb.publishToGRPC(ctx, event, serviceID, client); err != nil {
            publishErrors = append(publishErrors, fmt.Errorf("gRPC publish to %s failed: %w", serviceID, err))
        }
    }

    // 4. Handle locally registered handlers
    if err := eb.handleLocalEvent(ctx, event); err != nil {
        publishErrors = append(publishErrors, fmt.Errorf("local handling failed: %w", err))
    }

    if len(publishErrors) > 0 {
        eb.logger.Error("Some event publications failed", "errors", publishErrors)
        // Don't return error - allow partial success
    }

    eb.metrics.EventPublishCompleted(string(event.Type), event.Source, len(publishErrors))
    return nil
}

func (eb *FlextEventBus) publishToRedis(ctx context.Context, event BaseEvent) error {
    eventData, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %w", err)
    }

    channel := fmt.Sprintf("flext.events.%s", event.Type)
    if err := eb.redisClient.Publish(ctx, channel, eventData).Err(); err != nil {
        return fmt.Errorf("Redis publish failed: %w", err)
    }

    return nil
}

func (eb *FlextEventBus) publishToHTTP(ctx context.Context, event BaseEvent, serviceID, endpoint string) error {
    eventData, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %w", err)
    }

    req, err := http.NewRequestWithContext(ctx, "POST",
        fmt.Sprintf("%s/api/v1/events", endpoint),
        bytes.NewBuffer(eventData))
    if err != nil {
        return fmt.Errorf("failed to create HTTP request: %w", err)
    }

    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-Event-Source", "flext-ecosystem")
    req.Header.Set("X-Event-Type", string(event.Type))

    client := &http.Client{Timeout: 5 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return fmt.Errorf("HTTP request failed: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        return fmt.Errorf("HTTP publish failed with status %d", resp.StatusCode)
    }

    return nil
}
```

### **Event Sourcing Integration**

#### **Event Store Pattern**

```go
// Event store for persistent event history
type FlextEventStore struct {
    db      *sql.DB
    cache   *redis.Client
    logger  *logger.Logger
}

type StoredEvent struct {
    ID            string                 `json:"id" db:"id"`
    StreamID      string                 `json:"stream_id" db:"stream_id"`
    EventType     EventType              `json:"event_type" db:"event_type"`
    EventData     map[string]interface{} `json:"event_data" db:"event_data"`
    Metadata      map[string]string      `json:"metadata" db:"metadata"`
    Version       int64                  `json:"version" db:"version"`
    CreatedAt     time.Time              `json:"created_at" db:"created_at"`
    CorrelationID string                 `json:"correlation_id" db:"correlation_id"`
}

func (es *FlextEventStore) AppendEvent(ctx context.Context, streamID string, event BaseEvent) error {
    tx, err := es.db.BeginTx(ctx, nil)
    if err != nil {
        return fmt.Errorf("failed to begin transaction: %w", err)
    }
    defer tx.Rollback()

    // Get current stream version
    var currentVersion int64
    err = tx.QueryRowContext(ctx,
        "SELECT COALESCE(MAX(version), 0) FROM events WHERE stream_id = $1",
        streamID).Scan(&currentVersion)
    if err != nil {
        return fmt.Errorf("failed to get current version: %w", err)
    }

    newVersion := currentVersion + 1

    // Insert new event
    storedEvent := StoredEvent{
        ID:            event.ID,
        StreamID:      streamID,
        EventType:     event.Type,
        EventData:     event.Data,
        Metadata:      event.Extensions,
        Version:       newVersion,
        CreatedAt:     event.Time,
        CorrelationID: getCorrelationID(ctx),
    }

    _, err = tx.ExecContext(ctx, `
        INSERT INTO events (id, stream_id, event_type, event_data, metadata, version, created_at, correlation_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
        storedEvent.ID, storedEvent.StreamID, storedEvent.EventType,
        storedEvent.EventData, storedEvent.Metadata, storedEvent.Version,
        storedEvent.CreatedAt, storedEvent.CorrelationID)
    if err != nil {
        return fmt.Errorf("failed to insert event: %w", err)
    }

    if err := tx.Commit(); err != nil {
        return fmt.Errorf("failed to commit transaction: %w", err)
    }

    // Invalidate cache
    cacheKey := fmt.Sprintf("stream:%s", streamID)
    es.cache.Del(ctx, cacheKey)

    es.logger.Info("Event appended to stream",
        "stream_id", streamID,
        "event_id", event.ID,
        "version", newVersion)

    return nil
}

func (es *FlextEventStore) GetEventStream(ctx context.Context, streamID string, fromVersion int64) ([]StoredEvent, error) {
    // Try cache first
    cacheKey := fmt.Sprintf("stream:%s:from:%d", streamID, fromVersion)
    cached, err := es.cache.Get(ctx, cacheKey).Result()
    if err == nil {
        var events []StoredEvent
        if err := json.Unmarshal([]byte(cached), &events); err == nil {
            return events, nil
        }
    }

    // Query database
    rows, err := es.db.QueryContext(ctx, `
        SELECT id, stream_id, event_type, event_data, metadata, version, created_at, correlation_id
        FROM events
        WHERE stream_id = $1 AND version >= $2
        ORDER BY version ASC`,
        streamID, fromVersion)
    if err != nil {
        return nil, fmt.Errorf("failed to query events: %w", err)
    }
    defer rows.Close()

    var events []StoredEvent
    for rows.Next() {
        var event StoredEvent
        err := rows.Scan(&event.ID, &event.StreamID, &event.EventType,
            &event.EventData, &event.Metadata, &event.Version,
            &event.CreatedAt, &event.CorrelationID)
        if err != nil {
            return nil, fmt.Errorf("failed to scan event: %w", err)
        }
        events = append(events, event)
    }

    // Cache results
    eventData, _ := json.Marshal(events)
    es.cache.Set(ctx, cacheKey, eventData, 5*time.Minute)

    return events, nil
}
```

---

## 🔧 Integration Testing Patterns

### **Cross-Service Integration Testing**

```go
// Integration test suite for cross-service communication
type IntegrationTestSuite struct {
    flexcoreClient    *FlexCoreClient
    flextServiceClient *FlextServiceClient
    eventBus          *FlextEventBus
    testDatabase      *sql.DB
    testRedis         *redis.Client
}

func (suite *IntegrationTestSuite) TestPipelineExecutionIntegration() {
    // Setup test pipeline
    pipelineConfig := PipelineConfig{
        Name:   "test-integration-pipeline",
        TapConfig: map[string]interface{}{
            "plugin_type": "extractors",
            "name":        "tap-oracle",
            "config": map[string]interface{}{
                "host":     "localhost",
                "port":     1521,
                "database": "testdb",
            },
        },
        TargetConfig: map[string]interface{}{
            "plugin_type": "loaders",
            "name":        "target-postgres",
            "config": map[string]interface{}{
                "host":     "localhost",
                "port":     5432,
                "database": "testdb",
            },
        },
    }

    // Test FlexCore → FLEXT Service communication
    executionRequest := PluginExecutionRequest{
        PluginID:    "meltano-pipeline",
        Command:     "run",
        Args:        []string{pipelineConfig.Name},
        Environment: map[string]string{"MELTANO_PROJECT_ROOT": "/tmp/test-project"},
        Timeout:     5 * time.Minute,
    }

    // Execute pipeline through FlexCore
    response, err := suite.flexcoreClient.ExecutePlugin(executionRequest)
    assert.NoError(suite.T(), err)
    assert.Equal(suite.T(), "completed", response.Status)

    // Verify events were published
    events := suite.eventBus.GetPublishedEvents(PipelineStartedEvent, PipelineCompletedEvent)
    assert.Len(suite.T(), events, 2)

    // Verify FLEXT Service processed the request
    execution, err := suite.flextServiceClient.GetExecution(response.ExecutionID)
    assert.NoError(suite.T(), err)
    assert.Equal(suite.T(), "completed", execution.Status)
    assert.Greater(suite.T(), execution.RecordsProcessed, int64(0))
}

func (suite *IntegrationTestSuite) TestEventDrivenCommunication() {
    // Setup event listeners
    eventReceived := make(chan BaseEvent, 1)
    handler := &TestEventHandler{
        eventChannel: eventReceived,
        eventTypes:   []EventType{PipelineCompletedEvent},
    }

    suite.eventBus.Subscribe(handler)

    // Trigger event from one service
    event := BaseEvent{
        ID:          uuid.New().String(),
        Type:        PipelineCompletedEvent,
        Source:      "flext-service",
        SpecVersion: "1.0",
        Time:        time.Now(),
        Subject:     "pipeline-123",
        Data: map[string]interface{}{
            "pipeline_id":     "pipeline-123",
            "execution_id":    "exec-456",
            "records_count":   1000,
            "duration":        "2m30s",
            "status":          "completed",
        },
    }

    err := suite.eventBus.PublishEvent(context.Background(), event)
    assert.NoError(suite.T(), err)

    // Verify event was received
    select {
    case receivedEvent := <-eventReceived:
        assert.Equal(suite.T(), event.ID, receivedEvent.ID)
        assert.Equal(suite.T(), event.Type, receivedEvent.Type)
        assert.Equal(suite.T(), "pipeline-123", receivedEvent.Subject)
    case <-time.After(5 * time.Second):
        suite.T().Fatal("Event not received within timeout")
    }
}
```

---

## 📊 Integration Monitoring and Observability

### **Cross-Service Tracing**

```go
// Distributed tracing across integration points
type IntegrationTracer struct {
    tracer opentracing.Tracer
    logger *logger.Logger
}

func (it *IntegrationTracer) TraceServiceCall(ctx context.Context, serviceName, operation string, fn func(context.Context) error) error {
    span, ctx := opentracing.StartSpanFromContext(ctx, fmt.Sprintf("%s.%s", serviceName, operation))
    defer span.Finish()

    span.SetTag("service.name", serviceName)
    span.SetTag("operation.name", operation)
    span.SetTag("integration.type", "service-to-service")

    startTime := time.Now()
    err := fn(ctx)
    duration := time.Since(startTime)

    span.SetTag("operation.duration", duration.String())

    if err != nil {
        span.SetTag("error", true)
        span.LogFields(
            log.String("error.message", err.Error()),
            log.String("error.type", fmt.Sprintf("%T", err)),
        )
        it.logger.Error("Service call failed",
            "service", serviceName,
            "operation", operation,
            "duration", duration,
            "error", err)
    } else {
        it.logger.Info("Service call completed",
            "service", serviceName,
            "operation", operation,
            "duration", duration)
    }

    return err
}

// Usage in integration code
func (fc *FlexCore) ExecutePluginWithTracing(ctx context.Context, request PluginExecutionRequest) (*PluginExecutionResponse, error) {
    var response *PluginExecutionResponse

    err := fc.tracer.TraceServiceCall(ctx, "flext-service", "execute-plugin", func(ctx context.Context) error {
        var err error
        response, err = fc.executePluginInternal(ctx, request)
        return err
    })

    return response, err
}
```

### **Integration Metrics**

```go
// Metrics collection for integration points
type IntegrationMetrics struct {
    serviceCallDuration    prometheus.HistogramVec
    serviceCallTotal       prometheus.CounterVec
    eventPublishDuration   prometheus.HistogramVec
    eventPublishTotal      prometheus.CounterVec
    bridgeCallDuration     prometheus.HistogramVec
    integrationErrors      prometheus.CounterVec
}

func NewIntegrationMetrics() *IntegrationMetrics {
    return &IntegrationMetrics{
        serviceCallDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name: "flext_service_call_duration_seconds",
                Help: "Duration of service-to-service calls",
            },
            []string{"source_service", "target_service", "operation"},
        ),
        serviceCallTotal: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "flext_service_call_total",
                Help: "Total number of service-to-service calls",
            },
            []string{"source_service", "target_service", "operation", "status"},
        ),
        eventPublishDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name: "flext_event_publish_duration_seconds",
                Help: "Duration of event publishing operations",
            },
            []string{"event_type", "transport"},
        ),
        bridgeCallDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name: "flext_bridge_call_duration_seconds",
                Help: "Duration of Go-Python bridge calls",
            },
            []string{"bridge_type", "method"},
        ),
    }
}

func (im *IntegrationMetrics) RecordServiceCall(sourceService, targetService, operation, status string, duration time.Duration) {
    im.serviceCallDuration.WithLabelValues(sourceService, targetService, operation).Observe(duration.Seconds())
    im.serviceCallTotal.WithLabelValues(sourceService, targetService, operation, status).Inc()
}

func (im *IntegrationMetrics) RecordEventPublish(eventType, transport string, duration time.Duration) {
    im.eventPublishDuration.WithLabelValues(eventType, transport).Observe(duration.Seconds())
}
```

---

**Integration Patterns Version**: 2.0.0  
**Last Updated**: 2025-08-02  
**Status**: PRODUCTION READY  
**Maintained By**: FLEXT Integration Team

This document serves as the **comprehensive reference** for all integration patterns used across the FLEXT ecosystem. All new integrations must follow these established patterns and be documented here.
