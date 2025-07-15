# FLEXT API Examples - Real Working Examples

**Last Updated**: 2025-07-13  
**Status**: PRODUCTION-READY  
**Coverage**: REST API + gRPC Service

---

## 🚀 REST API Examples

### 1. Health Check (Basic)

```bash
# GET /health
curl -X GET "http://localhost:8080/health" \
  -H "Accept: application/json"
```

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-07-13T10:30:00Z",
  "components": {
    "database": {
      "healthy": true,
      "message": "Connected"
    },
    "meltano": {
      "healthy": true,
      "message": "Available"
    }
  }
}
```

### 2. System Information

```bash
# GET /
curl -X GET "http://localhost:8080/" \
  -H "Accept: application/json"
```

**Response**:

```json
{
  "name": "FLEXT API",
  "version": "2.0.0",
  "environment": "production",
  "features": {
    "database_enabled": true,
    "websocket_enabled": true,
    "clean_architecture": true
  },
  "python_version": "3.13.5",
  "meltano_version": "3.5.6"
}
```

### 3. Pipeline Operations

#### Create Pipeline

```bash
# POST /api/v1/pipelines
curl -X POST "http://localhost:8080/api/v1/pipelines" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "name": "etl-postgres-data",
    "description": "Extract data from PostgreSQL and load to warehouse",
    "extractor": "tap-postgres",
    "loader": "target-postgres",
    "transform": "dbt",
    "config": {
      "source_db": "postgresql://user:pass@localhost:5432/source",
      "target_db": "postgresql://user:pass@localhost:5432/warehouse"
    },
    "schedule": "0 2 * * *"
  }'
```

**Response**:

```json
{
  "id": "pipeline-123e4567-e89b-12d3-a456-426614174000",
  "name": "etl-postgres-data",
  "description": "Extract data from PostgreSQL and load to warehouse",
  "extractor": "tap-postgres",
  "loader": "target-postgres",
  "transform": "dbt",
  "is_active": true,
  "created_at": "2025-07-13T10:30:00Z",
  "created_by": "api_user",
  "last_status": "created"
}
```

#### List Pipelines

```bash
# GET /api/v1/pipelines?limit=10&offset=0
curl -X GET "http://localhost:8080/api/v1/pipelines?limit=10&offset=0" \
  -H "Accept: application/json"
```

**Response**:

```json
{
  "pipelines": [
    {
      "id": "pipeline-123e4567-e89b-12d3-a456-426614174000",
      "name": "etl-postgres-data",
      "description": "Extract data from PostgreSQL and load to warehouse",
      "is_active": true,
      "last_status": "success",
      "last_run": "2025-07-13T02:00:00Z"
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

#### Run Pipeline

```bash
# POST /api/v1/pipelines/{id}/run
curl -X POST "http://localhost:8080/api/v1/pipelines/pipeline-123e4567-e89b-12d3-a456-426614174000/run" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "full_refresh": false,
    "env_vars": {
      "EXTRACT_MODE": "incremental",
      "LOG_LEVEL": "INFO"
    }
  }'
```

**Response**:

```json
{
  "execution_id": "exec-987fcdeb-51a2-43d1-b678-900123456789",
  "pipeline_id": "pipeline-123e4567-e89b-12d3-a456-426614174000",
  "status": "running",
  "started_at": "2025-07-13T10:35:00Z",
  "triggered_by": "api_user"
}
```

### 4. Plugin Management

#### List Available Plugins

```bash
# GET /api/v1/plugins?type=extractor&installed_only=false
curl -X GET "http://localhost:8080/api/v1/plugins?type=extractor&installed_only=false" \
  -H "Accept: application/json"
```

**Response**:

```json
{
  "plugins": [
    {
      "name": "tap-postgres",
      "type": "extractor",
      "variant": "meltanolabs",
      "version": "0.3.0",
      "description": "PostgreSQL extractor",
      "installed": true,
      "installed_at": "2025-07-10T14:20:00Z"
    },
    {
      "name": "tap-salesforce",
      "type": "extractor",
      "variant": "singer-io",
      "version": "1.5.2",
      "description": "Salesforce extractor",
      "installed": false
    }
  ],
  "total": 25
}
```

#### Install Plugin

```bash
# POST /api/v1/plugins/install
curl -X POST "http://localhost:8080/api/v1/plugins/install" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "name": "tap-salesforce",
    "type": "extractor",
    "variant": "singer-io"
  }'
```

**Response**:

```json
{
  "name": "tap-salesforce",
  "type": "extractor",
  "variant": "singer-io",
  "version": "1.5.2",
  "installed": true,
  "installed_at": "2025-07-13T10:40:00Z"
}
```

---

## 🔧 gRPC Service Examples

### 1. Health Check

```python
import grpc
from flext_grpc.proto import flext_pb2
from flext_grpc.proto import flext_pb2_grpc
from google.protobuf.empty_pb2 import Empty

# Connect to gRPC server
channel = grpc.insecure_channel('localhost:50051')
stub = flext_pb2_grpc.FlextServiceStub(channel)

# Health check
response = stub.HealthCheck(Empty())
print(f"Service healthy: {response.healthy}")
print(f"Components: {len(response.components)}")
```

### 2. System Stats

```python
# Get system statistics
response = stub.GetSystemStats(Empty())
print(f"Active pipelines: {response.active_pipelines}")
print(f"Total executions: {response.total_executions}")
print(f"Success rate: {response.success_rate:.2%}")
print(f"CPU usage: {response.cpu_usage:.1f}%")
print(f"Memory usage: {response.memory_usage:.1f}%")
```

### 3. Pipeline Operations

#### Create Pipeline

```python
from google.protobuf.struct_pb2 import Struct

# Create pipeline request
request = flext_pb2.CreatePipelineRequest(
    name="grpc-etl-pipeline",
    description="ETL pipeline created via gRPC",
    extractor="tap-postgres",
    loader="target-snowflake",
    transform="dbt",
    schedule="0 1 * * *"
)

# Add configuration
config_struct = Struct()
config_struct.update({
    "source_schema": "public",
    "target_schema": "analytics",
    "batch_size": 1000
})
request.config.CopyFrom(config_struct)

# Create pipeline
response = stub.CreatePipeline(request)
print(f"Created pipeline: {response.id}")
print(f"Pipeline name: {response.name}")
print(f"Is active: {response.is_active}")
```

#### List Pipelines

```python
# List pipelines with pagination
request = flext_pb2.ListPipelinesRequest(
    limit=5,
    offset=0,
    filter="active",
    sort_by="created_at",
    descending=True
)

response = stub.ListPipelines(request)
print(f"Found {response.total} pipelines")
for pipeline in response.pipelines:
    print(f"- {pipeline.name} ({pipeline.id})")
    print(f"  Status: {pipeline.last_status}")
    print(f"  Last run: {pipeline.last_run}")
```

#### Run Pipeline

```python
# Run pipeline with environment variables
env_vars = {"LOG_LEVEL": "DEBUG", "EXTRACT_MODE": "full"}

request = flext_pb2.RunPipelineRequest(
    pipeline_id="pipeline-123e4567-e89b-12d3-a456-426614174000",
    full_refresh=False,
    env_vars=env_vars
)

response = stub.RunPipeline(request)
print(f"Execution started: {response.id}")
print(f"Status: {response.status}")
print(f"Started at: {response.started_at}")
```

### 4. Execution Monitoring

#### Get Execution Status

```python
# Get execution details
request = flext_pb2.GetExecutionRequest(
    id="exec-987fcdeb-51a2-43d1-b678-900123456789"
)

response = stub.GetExecution(request)
print(f"Execution ID: {response.id}")
print(f"Pipeline ID: {response.pipeline_id}")
print(f"Status: {response.status}")
print(f"Duration: {response.duration_seconds}s")
print(f"Records processed: {response.records_processed}")

if response.error_message:
    print(f"Error: {response.error_message}")
```

#### Stream Execution Updates

```python
# Stream real-time execution updates
request = flext_pb2.StreamExecutionRequest(
    execution_id="exec-987fcdeb-51a2-43d1-b678-900123456789"
)

# Stream updates
for update in stub.StreamExecution(request):
    print(f"[{update.timestamp}] {update.type}: {update.message}")
    if update.type == "progress":
        print(f"Progress: {update.progress:.1%}")
    elif update.type == "complete":
        print(f"Final status: {update.status}")
        break
```

### 5. Meltano Integration

#### Initialize Meltano Project

```python
# Initialize new Meltano project
request = flext_pb2.InitializeMeltanoProjectRequest(
    project_name="data-pipeline-project",
    environment="production",
    force=False
)

response = stub.InitializeMeltanoProject(request)
print(f"Project: {response.name}")
print(f"Environment: {response.environment}")
print(f"Root path: {response.project_root}")
print(f"Initialized: {response.is_initialized}")
```

#### Run Meltano Pipeline

```python
from google.protobuf.struct_pb2 import Struct

# Define pipeline configuration
pipeline_config = Struct()
pipeline_config.update({
    "tap": "tap-postgres",
    "target": "target-snowflake",
    "select": ["users.*", "orders.*"],
    "state_backend": "s3"
})

# Run Meltano pipeline
request = flext_pb2.RunMeltanoPipelineRequest(
    project_name="data-pipeline-project",
    pipeline_definition=pipeline_config,
    environment="production",
    execution_mode=flext_pb2.MELTANO_EXECUTION_MODE_ASYNC,
    env_vars={"DBT_PROFILES_DIR": "/opt/dbt/profiles"}
)

response = stub.RunMeltanoPipeline(request)
print(f"Meltano execution ID: {response.execution_id}")
print(f"Pipeline: {response.pipeline_name}")
print(f"State: {response.state}")
print(f"Environment: {response.environment}")
```

### 6. Plugin Management via gRPC

#### List Available Plugins

```python
# List extractor plugins
request = flext_pb2.ListPluginsRequest(
    type=flext_pb2.PLUGIN_TYPE_EXTRACTOR,
    installed_only=False
)

response = stub.ListPlugins(request)
print(f"Found {response.total} extractor plugins")
for plugin in response.plugins:
    status = "✓ Installed" if plugin.installed else "○ Available"
    print(f"{status}: {plugin.name} ({plugin.variant}) v{plugin.version}")
```

#### Install Plugin

```python
# Install a new plugin
request = flext_pb2.InstallPluginRequest(
    name="tap-github",
    type=flext_pb2.PLUGIN_TYPE_EXTRACTOR,
    variant="meltanolabs"
)

response = stub.InstallPlugin(request)
print(f"Installed: {response.name}")
print(f"Version: {response.version}")
print(f"Installed at: {response.installed_at}")
```

---

## 🔒 Authentication Examples

### JWT Token Authentication (REST)

```bash
# 1. Get authentication token
TOKEN=$(curl -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure_password"}' \
  | jq -r '.access_token')

# 2. Use token in requests
curl -X GET "http://localhost:8080/api/v1/pipelines" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

### gRPC Authentication

```python
import grpc
from grpc import ssl_channel_credentials, access_token_call_credentials, composite_channel_credentials

# Setup authentication
access_token = "your_jwt_token_here"
call_credentials = access_token_call_credentials(access_token)
ssl_credentials = ssl_channel_credentials()
credentials = composite_channel_credentials(ssl_credentials, call_credentials)

# Create authenticated channel
channel = grpc.secure_channel('localhost:50051', credentials)
stub = flext_pb2_grpc.FlextServiceStub(channel)
```

---

## 📊 Advanced Examples

### 1. Batch Operations (gRPC)

```python
from google.protobuf.struct_pb2 import Struct

# Create batch operations
operations = []

# Operation 1: Create pipeline
op1_params = Struct()
op1_params.update({
    "name": "batch-pipeline-1",
    "extractor": "tap-csv",
    "loader": "target-postgres"
})

operations.append(flext_pb2.BatchOperation(
    operation_id="op-1",
    operation_type="create_pipeline",
    parameters=op1_params,
    priority=1
))

# Operation 2: Install plugin
op2_params = Struct()
op2_params.update({
    "name": "tap-mongodb",
    "type": "extractor",
    "variant": "z3z1k"
})

operations.append(flext_pb2.BatchOperation(
    operation_id="op-2",
    operation_type="install_plugin",
    parameters=op2_params,
    priority=2
))

# Execute batch
request = flext_pb2.BatchOperationsRequest(
    operations=operations,
    fail_fast=False,
    max_parallel=2,
    timeout_seconds=300
)

response = stub.BatchOperations(request)
print(f"Total operations: {response.total_operations}")
print(f"Successful: {response.successful_operations}")
print(f"Failed: {response.failed_operations}")

for result in response.results:
    status = "✓" if result.success else "✗"
    print(f"{status} {result.operation_id}: {result.duration_ms}ms")
```

### 2. Advanced Metrics (gRPC)

```python
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta

# Get advanced metrics for last 24 hours
start_time = Timestamp()
end_time = Timestamp()

start_time.FromDatetime(datetime.now() - timedelta(days=1))
end_time.FromDatetime(datetime.now())

request = flext_pb2.AdvancedMetricsRequest(
    metric_types=["system", "pipelines", "performance"],
    start_time=start_time,
    end_time=end_time,
    granularity="hour",
    include_predictions=True
)

response = stub.GetAdvancedMetrics(request)
print(f"Metrics generated at: {response.generated_at}")
print(f"Granularity: {response.granularity}")

for metric_name, metric_series in response.metrics.items():
    print(f"\n{metric_name} ({metric_series.unit}):")
    for point in metric_series.data_points[-5:]:  # Last 5 points
        print(f"  {point.timestamp}: {point.value}")
```

---

## 🛠️ Error Handling Examples

### REST API Error Responses

```json
{
  "error": {
    "code": "PIPELINE_NOT_FOUND",
    "message": "Pipeline with ID 'invalid-id' not found",
    "details": {
      "pipeline_id": "invalid-id",
      "suggestion": "Check the pipeline ID and try again"
    },
    "timestamp": "2025-07-13T10:45:00Z",
    "request_id": "req-12345"
  }
}
```

### gRPC Error Handling

```python
import grpc

try:
    response = stub.GetPipeline(flext_pb2.GetPipelineRequest(id="invalid-id"))
except grpc.RpcError as e:
    print(f"gRPC Error: {e.code()}")
    print(f"Details: {e.details()}")

    # Handle specific error codes
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print("Pipeline not found")
    elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
        print("Access denied")
    elif e.code() == grpc.StatusCode.UNAVAILABLE:
        print("Service unavailable - check connection")
```

---

## 🧪 Testing Examples

### Integration Test Script

```python
#!/usr/bin/env python3
"""FLEXT API Integration Test Script"""

import requests
import grpc
import time
from flext_grpc.proto import flext_pb2, flext_pb2_grpc
from google.protobuf.empty_pb2 import Empty

# Configuration
REST_BASE_URL = "http://localhost:8080"
GRPC_SERVER = "localhost:50051"

def test_rest_api():
    """Test REST API endpoints"""
    print("🧪 Testing REST API...")

    # Health check
    response = requests.get(f"{REST_BASE_URL}/health")
    assert response.status_code == 200
    print("✓ Health check passed")

    # System info
    response = requests.get(f"{REST_BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    print("✓ System info endpoint working")

    # List pipelines
    response = requests.get(f"{REST_BASE_URL}/api/v1/pipelines")
    assert response.status_code == 200
    print("✓ Pipeline listing working")

def test_grpc_api():
    """Test gRPC API"""
    print("🧪 Testing gRPC API...")

    channel = grpc.insecure_channel(GRPC_SERVER)
    stub = flext_pb2_grpc.FlextServiceStub(channel)

    # Health check
    response = stub.HealthCheck(Empty())
    assert response.healthy
    print("✓ gRPC health check passed")

    # System stats
    response = stub.GetSystemStats(Empty())
    assert response.active_pipelines >= 0
    print("✓ System stats working")

    # List pipelines
    request = flext_pb2.ListPipelinesRequest(limit=10)
    response = stub.ListPipelines(request)
    assert response.total >= 0
    print("✓ Pipeline listing via gRPC working")

if __name__ == "__main__":
    test_rest_api()
    test_grpc_api()
    print("🎉 All tests passed!")
```

---

## 📋 Quick Reference

### REST API Endpoints

| Method | Endpoint                     | Description        |
| ------ | ---------------------------- | ------------------ |
| `GET`  | `/health`                    | Health check       |
| `GET`  | `/`                          | System information |
| `GET`  | `/api/v1/pipelines`          | List pipelines     |
| `POST` | `/api/v1/pipelines`          | Create pipeline    |
| `GET`  | `/api/v1/pipelines/{id}`     | Get pipeline       |
| `POST` | `/api/v1/pipelines/{id}/run` | Run pipeline       |
| `GET`  | `/api/v1/executions`         | List executions    |
| `GET`  | `/api/v1/plugins`            | List plugins       |
| `POST` | `/api/v1/plugins/install`    | Install plugin     |

### gRPC Service Methods

| Service        | Method               | Description              |
| -------------- | -------------------- | ------------------------ |
| `FlextService` | `HealthCheck`        | Service health status    |
| `FlextService` | `GetSystemStats`     | System metrics           |
| `FlextService` | `ListPipelines`      | List all pipelines       |
| `FlextService` | `CreatePipeline`     | Create new pipeline      |
| `FlextService` | `RunPipeline`        | Execute pipeline         |
| `FlextService` | `StreamExecution`    | Stream execution updates |
| `FlextService` | `ListPlugins`        | List available plugins   |
| `FlextService` | `InstallPlugin`      | Install plugin           |
| `FlextService` | `RunMeltanoPipeline` | Execute Meltano pipeline |
| `FlextService` | `BatchOperations`    | Execute batch operations |

---

## 🔗 Related Resources

- [FLEXT gRPC Proto Definition](./flext-grpc/src/flext_grpc/proto/flext.proto)
- [REST API Server Implementation](./cmd/flext/main.go)
- [Clean Architecture Documentation](./docs/api-reference/comprehensive/)
- [Production Deployment Guide](./docs/deployment/)

---

**Status**: ✅ All examples tested and verified functional  
**Last Validated**: 2025-07-13  
**API Version**: 2.0.0
