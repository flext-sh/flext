# API Contracts - FlexCore ↔ FLEXT Service Integration

**Version 0.9.9** | **Status: Production Ready** | **Integration Type: Core Service Coordination**

Comprehensive API contract documentation defining the integration patterns, communication protocols, and service coordination between FlexCore Runtime Container (port 8080) and FLEXT Service Data Integration Engine (port 8081).

## Overview

This document defines the **professional API contracts** for bidirectional communication between the two core services of the FLEXT ecosystem:

- **FlexCore Service** (Go): High-performance runtime container and plugin orchestration engine
- **FLEXT Service** (Go/Python): Data integration engine with Python ecosystem bridge

### **Integration Architecture**

```
┌─────────────────┐       HTTP/REST API        ┌─────────────────┐
│   FlexCore      │◄──────────────────────────►│  FLEXT Service  │
│   (Port 8080)   │       Plugin Execution      │   (Port 8081)   │
│                 │       State Coordination    │                 │
│ Go Runtime      │       Health Monitoring     │ Go/Python       │
│ Plugin Engine   │       Event Coordination    │ Data Engine     │
└─────────────────┘                             └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐                             ┌─────────────────┐
│  PostgreSQL     │◄────────Event Sourcing────►│  Redis          │
│  Event Store    │                             │  Coordination   │
│  (Port 5433)    │                             │  (Port 6380)    │
└─────────────────┘                             └─────────────────┘
```

## Service Discovery & Health Monitoring

### **FlexCore Health Endpoints**

#### **Basic Health Check**

```http
GET http://localhost:8080/health
Accept: application/json
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "flexcore",
  "version": "2.0.0",
  "timestamp": "2025-08-02T10:00:00Z",
  "uptime": "2h45m30s"
}
```

#### **Detailed Health with Dependencies**

```http
GET http://localhost:8080/health/dependencies
Accept: application/json
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "flexcore",
  "version": "2.0.0",
  "timestamp": "2025-08-02T10:00:00Z",
  "dependencies": {
    "postgresql": {
      "status": "healthy",
      "response_time": "5ms",
      "connection_pool": {
        "active": 8,
        "idle": 12,
        "max": 20
      }
    },
    "redis": {
      "status": "healthy",
      "response_time": "2ms",
      "memory_usage": "45MB"
    },
    "flext_service": {
      "status": "healthy",
      "url": "http://localhost:8081",
      "response_time": "15ms",
      "last_check": "2025-08-02T09:59:55Z"
    }
  },
  "plugins": {
    "loaded": 12,
    "active": 8,
    "failed": 0
  }
}
```

### **FLEXT Service Health Endpoints**

#### **Basic Health Check**

```http
GET http://localhost:8081/health
Accept: application/json
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "flext-service",
  "version": "2.0.0",
  "mode": "server",
  "timestamp": "2025-08-02T10:00:00Z",
  "uptime": "2h45m30s",
  "python_bridge": "operational"
}
```

#### **Detailed Health with Python Ecosystem**

```http
GET http://localhost:8081/health?detail=true
Accept: application/json
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "flext-service",
  "version": "2.0.0",
  "mode": "server",
  "timestamp": "2025-08-02T10:00:00Z",
  "dependencies": {
    "flexcore": {
      "status": "healthy",
      "url": "http://localhost:8080",
      "response_time": "12ms",
      "plugin_coordination": "active"
    },
    "postgresql": {
      "status": "healthy",
      "response_time": "6ms"
    },
    "redis": {
      "status": "healthy",
      "response_time": "3ms"
    }
  },
  "python_ecosystem": {
    "meltano": {
      "status": "operational",
      "version": "3.8.0",
      "projects": 4,
      "active_pipelines": 2
    },
    "singer_taps": {
      "available": 5,
      "operational": 5,
      "last_validated": "2025-08-02T09:55:00Z"
    },
    "singer_targets": {
      "available": 5,
      "operational": 5,
      "last_validated": "2025-08-02T09:55:00Z"
    },
    "dbt_projects": {
      "available": 4,
      "compiled": 4,
      "models": 47
    }
  }
}
```

## Plugin Execution Coordination

### **FlexCore → FLEXT Service: Plugin Execution**

#### **Execute FLEXT Service as Plugin**

```http
POST http://localhost:8080/api/v1/plugins/flext-service/execute
Content-Type: application/json
Authorization: Bearer {jwt_token}
```

**Request Body:**

```json
{
  "operation": "meltano_pipeline",
  "parameters": {
    "project_name": "data_integration",
    "pipeline_name": "extract_transform_load",
    "tap": "tap-oracle",
    "target": "target-postgres",
    "dbt_models": ["staging", "marts"],
    "environment": "production"
  },
  "configuration": {
    "timeout": 3600,
    "max_memory": "2GB",
    "parallel_jobs": 4,
    "retry_attempts": 3
  },
  "context": {
    "execution_id": "exec_001_20250802_100030",
    "correlation_id": "corr_abc123def456",
    "user_id": "system",
    "workspace": "main"
  }
}
```

**Response (202 Accepted):**

```json
{
  "status": "accepted",
  "execution_id": "exec_001_20250802_100030",
  "message": "FLEXT Service plugin execution started",
  "estimated_duration": "45m",
  "monitoring": {
    "status_url": "/api/v1/executions/exec_001_20250802_100030/status",
    "logs_url": "/api/v1/executions/exec_001_20250802_100030/logs",
    "metrics_url": "/api/v1/executions/exec_001_20250802_100030/metrics"
  }
}
```

#### **Query Execution Status**

```http
GET http://localhost:8080/api/v1/executions/exec_001_20250802_100030/status
Accept: application/json
```

**Response (200 OK):**

```json
{
  "execution_id": "exec_001_20250802_100030",
  "status": "running",
  "progress": {
    "current_step": "dbt_transformation",
    "completed_steps": ["tap_extraction", "data_validation"],
    "remaining_steps": ["target_loading", "quality_checks"],
    "percentage": 65
  },
  "performance": {
    "start_time": "2025-08-02T10:00:30Z",
    "elapsed_time": "28m15s",
    "estimated_remaining": "17m",
    "records_processed": 1250000,
    "processing_rate": "740 records/sec"
  },
  "resource_usage": {
    "cpu_percent": 45,
    "memory_mb": 1450,
    "disk_io_mb": 2340
  }
}
```

### **FLEXT Service → FlexCore: Plugin Registration**

#### **Register Python Plugins with FlexCore**

```http
POST http://localhost:8081/api/v1/flexcore/plugins/register
Content-Type: application/json
```

**Request Body:**

```json
{
  "plugins": [
    {
      "name": "meltano-orchestrator",
      "version": "2.0.0",
      "type": "orchestration",
      "capabilities": ["tap_execution", "target_loading", "dbt_transformation"],
      "resource_requirements": {
        "min_memory": "256MB",
        "max_memory": "4GB",
        "cpu_cores": 2,
        "disk_space": "1GB"
      },
      "endpoints": {
        "execute": "/api/v1/meltano/execute",
        "status": "/api/v1/meltano/status",
        "health": "/api/v1/meltano/health"
      }
    },
    {
      "name": "singer-tap-coordinator",
      "version": "2.0.0",
      "type": "extraction",
      "capabilities": ["oracle_tap", "ldap_tap", "wms_tap"],
      "resource_requirements": {
        "min_memory": "128MB",
        "max_memory": "2GB",
        "cpu_cores": 1,
        "disk_space": "500MB"
      },
      "endpoints": {
        "execute": "/api/v1/singer/taps/execute",
        "discover": "/api/v1/singer/taps/discover",
        "validate": "/api/v1/singer/taps/validate"
      }
    }
  ]
}
```

**Response (201 Created):**

```json
{
  "status": "registered",
  "message": "Plugins registered successfully with FlexCore",
  "registered_plugins": [
    {
      "name": "meltano-orchestrator",
      "plugin_id": "meltano_orch_001",
      "status": "active",
      "registration_time": "2025-08-02T10:01:00Z"
    },
    {
      "name": "singer-tap-coordinator",
      "plugin_id": "singer_tap_001",
      "status": "active",
      "registration_time": "2025-08-02T10:01:00Z"
    }
  ]
}
```

## Event Coordination & State Synchronization

### **Event Publishing: FlexCore → FLEXT Service**

#### **Pipeline State Changed Event**

```http
POST http://localhost:8081/api/v1/events/pipeline-state-changed
Content-Type: application/json
```

**Request Body:**

```json
{
  "event_type": "PipelineStateChanged",
  "event_id": "evt_pipeline_001_20250802_100130",
  "timestamp": "2025-08-02T10:01:30Z",
  "correlation_id": "corr_abc123def456",
  "aggregate_id": "pipeline_data_integration_001",
  "aggregate_version": 5,
  "payload": {
    "pipeline_id": "pipeline_data_integration_001",
    "previous_state": "configuring",
    "current_state": "running",
    "transition_reason": "manual_start",
    "user_id": "REDACTED_LDAP_BIND_PASSWORD_user",
    "configuration": {
      "tap": "tap-oracle",
      "target": "target-postgres",
      "dbt_models": ["staging", "marts"]
    }
  },
  "metadata": {
    "source_service": "flexcore",
    "environment": "production",
    "workspace": "main"
  }
}
```

**Response (200 OK):**

```json
{
  "status": "processed",
  "event_id": "evt_pipeline_001_20250802_100130",
  "message": "Pipeline state change event processed",
  "actions_taken": [
    "meltano_pipeline_synchronized",
    "resource_allocation_updated",
    "monitoring_enabled"
  ]
}
```

### **Event Publishing: FLEXT Service → FlexCore**

#### **Data Processing Completed Event**

```http
POST http://localhost:8080/api/v1/events/data-processing-completed
Content-Type: application/json
```

**Request Body:**

```json
{
  "event_type": "DataProcessingCompleted",
  "event_id": "evt_processing_001_20250802_104530",
  "timestamp": "2025-08-02T10:45:30Z",
  "correlation_id": "corr_abc123def456",
  "execution_id": "exec_001_20250802_100030",
  "payload": {
    "pipeline_id": "pipeline_data_integration_001",
    "processing_summary": {
      "records_extracted": 1500000,
      "records_transformed": 1498500,
      "records_loaded": 1498500,
      "data_quality_score": 99.9,
      "processing_time": "44m18s"
    },
    "outputs": {
      "target_tables": [
        "staging.customers",
        "staging.orders",
        "marts.customer_metrics"
      ],
      "data_freshness": "2025-08-02T10:45:00Z",
      "schema_version": "v2.1.0"
    },
    "quality_metrics": {
      "duplicate_records": 0,
      "null_values": 1500,
      "schema_violations": 0,
      "business_rule_failures": 0
    }
  }
}
```

**Response (200 OK):**

```json
{
  "status": "acknowledged",
  "event_id": "evt_processing_001_20250802_104530",
  "message": "Data processing completion acknowledged",
  "next_actions": [
    "pipeline_marked_completed",
    "resources_released",
    "success_metrics_recorded"
  ]
}
```

## Meltano/Singer/DBT Integration Contracts

### **Singer Tap Execution**

#### **Execute Singer Tap via FLEXT Service**

```http
POST http://localhost:8081/api/v1/singer/taps/execute
Content-Type: application/json
```

**Request Body:**

```json
{
  "tap_name": "tap-oracle",
  "configuration": {
    "host": "internal.invalid.company.com",
    "port": 1521,
    "database": "PROD",
    "username": "${ORACLE_USER}",
    "password": "${ORACLE_PASSWORD}",
    "service_name": "XEPDB1"
  },
  "catalog": {
    "streams": [
      {
        "tap_stream_id": "customers",
        "schema": {
          "type": "object",
          "properties": {
            "customer_id": { "type": "integer" },
            "name": { "type": "string" },
            "email": { "type": "string" },
            "created_at": { "type": "string", "format": "date-time" }
          }
        },
        "metadata": [
          {
            "breadcrumb": [],
            "metadata": {
              "replication-method": "INCREMENTAL",
              "replication-key": "updated_at",
              "selected": true
            }
          }
        ]
      }
    ]
  },
  "state": {
    "bookmarks": {
      "customers": {
        "replication_key": "updated_at",
        "replication_key_value": "2025-08-01T00:00:00Z"
      }
    }
  }
}
```

**Response (202 Accepted):**

```json
{
  "status": "started",
  "execution_id": "tap_exec_oracle_001_20250802_105000",
  "tap_name": "tap-oracle",
  "estimated_records": 50000,
  "monitoring": {
    "status_url": "/api/v1/singer/executions/tap_exec_oracle_001_20250802_105000/status",
    "output_url": "/api/v1/singer/executions/tap_exec_oracle_001_20250802_105000/output"
  }
}
```

### **DBT Model Execution**

#### **Execute DBT Models via FLEXT Service**

```http
POST http://localhost:8081/api/v1/dbt/run
Content-Type: application/json
```

**Request Body:**

```json
{
  "project_name": "data_warehouse",
  "models": ["staging.stg_customers", "marts.customer_metrics"],
  "configuration": {
    "threads": 4,
    "target": "production",
    "full_refresh": false,
    "vars": {
      "start_date": "2025-08-01",
      "end_date": "2025-08-02"
    }
  },
  "dependencies": {
    "wait_for_completion": true,
    "upstream_tasks": ["tap_oracle_customers"]
  }
}
```

**Response (202 Accepted):**

```json
{
  "status": "started",
  "execution_id": "dbt_exec_001_20250802_110000",
  "project_name": "data_warehouse",
  "models_scheduled": ["staging.stg_customers", "marts.customer_metrics"],
  "estimated_duration": "15m",
  "monitoring": {
    "status_url": "/api/v1/dbt/executions/dbt_exec_001_20250802_110000/status",
    "logs_url": "/api/v1/dbt/executions/dbt_exec_001_20250802_110000/logs"
  }
}
```

## Error Handling & Circuit Breaker Patterns

### **Service Error Responses**

#### **FlexCore Plugin Execution Error**

```http
POST http://localhost:8080/api/v1/plugins/flext-service/execute
```

**Response (503 Service Unavailable):**

```json
{
  "error": {
    "code": "PLUGIN_EXECUTION_FAILED",
    "message": "FLEXT Service plugin execution failed",
    "details": {
      "plugin_name": "flext-service",
      "execution_id": "exec_failed_001_20250802_111500",
      "failure_reason": "python_bridge_timeout",
      "retry_possible": true,
      "retry_after": "30s"
    },
    "context": {
      "correlation_id": "corr_xyz789abc123",
      "timestamp": "2025-08-02T11:15:30Z",
      "service": "flexcore"
    },
    "troubleshooting": {
      "check_python_environment": true,
      "verify_meltano_project": true,
      "review_logs_at": "/api/v1/executions/exec_failed_001_20250802_111500/logs"
    }
  }
}
```

#### **FLEXT Service Dependency Error**

```http
GET http://localhost:8081/health
```

**Response (503 Service Unavailable):**

```json
{
  "status": "unhealthy",
  "service": "flext-service",
  "timestamp": "2025-08-02T11:20:00Z",
  "error": {
    "code": "DEPENDENCY_FAILURE",
    "message": "Critical dependency unavailable",
    "failed_dependencies": [
      {
        "name": "meltano",
        "status": "unhealthy",
        "error": "virtual_environment_not_found",
        "last_success": "2025-08-02T10:45:00Z"
      }
    ]
  },
  "actions": {
    "circuit_breaker": "open",
    "fail_fast": true,
    "retry_after": "60s"
  }
}
```

### **Circuit Breaker Implementation**

#### **FlexCore Circuit Breaker Status**

```http
GET http://localhost:8080/api/v1/circuit-breakers/flext-service
Accept: application/json
```

**Response (200 OK):**

```json
{
  "circuit_breaker": "flext-service",
  "state": "half_open",
  "failure_count": 3,
  "failure_threshold": 5,
  "timeout": "30s",
  "last_failure": "2025-08-02T11:15:30Z",
  "next_attempt": "2025-08-02T11:16:00Z",
  "statistics": {
    "total_requests": 145,
    "successful_requests": 140,
    "failed_requests": 5,
    "success_rate": 96.55
  }
}
```

## Security & Authentication

### **JWT Authentication**

#### **Service-to-Service Authentication**

```http
POST http://localhost:8080/api/v1/auth/service-token
Content-Type: application/json
```

**Request Body:**

```json
{
  "service_name": "flext-service",
  "service_version": "2.0.0",
  "client_secret": "${FLEXT_SERVICE_SECRET}",
  "requested_scopes": ["plugin.execute", "events.publish", "health.read"]
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "plugin.execute events.publish health.read",
  "service": "flext-service"
}
```

### **Request Authentication Headers**

All authenticated requests must include:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Service-Name: flext-service
X-Service-Version: 2.0.0
X-Correlation-ID: corr_abc123def456
```

## Rate Limiting & Throttling

### **Rate Limit Headers**

All API responses include rate limiting information:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1659438000
X-RateLimit-Window: 3600
```

### **Rate Limit Exceeded Response**

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 60
```

**Response Body:**

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "details": {
      "limit": 1000,
      "window": "1h",
      "retry_after": "60s",
      "current_usage": 1000
    }
  }
}
```

## Monitoring & Observability

### **Prometheus Metrics Endpoints**

#### **FlexCore Metrics**

```http
GET http://localhost:8080/metrics
Accept: text/plain
```

**Response (200 OK):**

```prometheus
# HELP flexcore_requests_total Total number of HTTP requests
# TYPE flexcore_requests_total counter
flexcore_requests_total{method="GET",endpoint="/health",status="200"} 1540
flexcore_requests_total{method="POST",endpoint="/api/v1/plugins/execute",status="202"} 89

# HELP flexcore_plugin_executions_duration_seconds Plugin execution duration
# TYPE flexcore_plugin_executions_duration_seconds histogram
flexcore_plugin_executions_duration_seconds_bucket{plugin="flext-service",le="30"} 15
flexcore_plugin_executions_duration_seconds_bucket{plugin="flext-service",le="60"} 45
flexcore_plugin_executions_duration_seconds_bucket{plugin="flext-service",le="300"} 87

# HELP flexcore_active_plugins Currently active plugins
# TYPE flexcore_active_plugins gauge
flexcore_active_plugins{type="orchestration"} 3
flexcore_active_plugins{type="extraction"} 5
flexcore_active_plugins{type="loading"} 5
```

#### **FLEXT Service Metrics**

```http
GET http://localhost:8081/metrics
Accept: text/plain
```

**Response (200 OK):**

```prometheus
# HELP flext_service_requests_total Total number of HTTP requests
# TYPE flext_service_requests_total counter
flext_service_requests_total{method="GET",endpoint="/health",status="200"} 2340
flext_service_requests_total{method="POST",endpoint="/api/v1/meltano/execute",status="202"} 156

# HELP flext_service_meltano_pipelines_duration_seconds Meltano pipeline execution duration
# TYPE flext_service_meltano_pipelines_duration_seconds histogram
flext_service_meltano_pipelines_duration_seconds_bucket{pipeline="data_integration",le="300"} 12
flext_service_meltano_pipelines_duration_seconds_bucket{pipeline="data_integration",le="600"} 34
flext_service_meltano_pipelines_duration_seconds_bucket{pipeline="data_integration",le="1800"} 89

# HELP flext_service_python_bridge_calls_total Python bridge function calls
# TYPE flext_service_python_bridge_calls_total counter
flext_service_python_bridge_calls_total{function="meltano_run",status="success"} 234
flext_service_python_bridge_calls_total{function="singer_tap",status="success"} 145
```

## Data Contracts & Schema Validation

### **Singer Record Schema**

All Singer records exchanged between services follow this structure:

```json
{
  "type": "RECORD",
  "stream": "customers",
  "record": {
    "customer_id": 12345,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "created_at": "2025-08-02T10:00:00Z",
    "updated_at": "2025-08-02T10:30:00Z"
  },
  "time_extracted": "2025-08-02T10:30:15Z"
}
```

### **State Management Schema**

State information exchanged for incremental processing:

```json
{
  "bookmarks": {
    "customers": {
      "replication_key": "updated_at",
      "replication_key_value": "2025-08-02T10:30:00Z",
      "version": 1659438000
    },
    "orders": {
      "replication_key": "order_date",
      "replication_key_value": "2025-08-02T10:25:00Z",
      "version": 1659437700
    }
  }
}
```

## Testing & Validation

### **Contract Testing**

#### **Health Check Contract Test**

```bash
# FlexCore health endpoint test
curl -f http://localhost:8080/health | jq '.status' | grep -q "healthy"

# FLEXT Service health endpoint test
curl -f http://localhost:8081/health | jq '.status' | grep -q "healthy"

# Cross-service health validation
curl -f http://localhost:8080/health/dependencies | jq '.dependencies.flext_service.status' | grep -q "healthy"
```

#### **Plugin Execution Contract Test**

```bash
# Test plugin execution contract
curl -X POST http://localhost:8080/api/v1/plugins/flext-service/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -d '{"operation":"health_check","parameters":{}}' | \
  jq '.status' | grep -q "accepted"
```

### **Integration Testing Framework**

```bash
# Run complete integration test suite
make test-integration-contracts       # Test all API contracts
make test-service-coordination        # Test service coordination patterns
make test-error-handling             # Test error scenarios and circuit breakers
make test-authentication             # Test JWT authentication flows
make test-rate-limiting              # Test rate limiting implementation
```

## Version Compatibility Matrix

| FlexCore Version | FLEXT Service Version | API Version | Compatibility            |
| ---------------- | --------------------- | ----------- | ------------------------ |
| 2.0.0            | 2.0.0                 | v1          | ✅ Fully Compatible      |
| 2.0.x            | 2.0.x                 | v1          | ✅ Patch Compatible      |
| 2.1.x            | 2.0.x                 | v1          | ⚠️ Limited Compatibility |
| 3.0.x            | 2.x.x                 | v1          | ❌ Breaking Changes      |

## Deployment Configuration

### **Production Environment Variables**

```bash
# FlexCore Configuration
FLEXCORE_PORT=8080
FLEXCORE_ENVIRONMENT=production
FLEXCORE_FLEXT_SERVICE_URL=http://flext-service:8081
FLEXCORE_JWT_SECRET=${FLEXCORE_JWT_SECRET}

# FLEXT Service Configuration
FLEXT_MODE=server
FLEXT_SERVER_PORT=8081
FLEXT_ENVIRONMENT=production
FLEXT_FLEXCORE_URL=http://flexcore:8080
FLEXT_JWT_SECRET=${FLEXT_JWT_SECRET}

# Shared Configuration
POSTGRES_URL=postgresql://flext_user:${DB_PASSWORD}@postgres:5432/flext_prod
REDIS_URL=redis://redis:6379/0
FLEXT_ECOSYSTEM_SECRET=${ECOSYSTEM_SECRET}
```

### **Docker Compose Integration**

```yaml
version: "3.8"
services:
  flexcore:
    image: flext-sh/flexcore:2.0.0
    ports:
      - "8080:8080"
    environment:
      - FLEXCORE_FLEXT_SERVICE_URL=http://flext-service:8081
    depends_on:
      - postgres
      - redis

  flext-service:
    image: flext/service:2.0.0
    ports:
      - "8081:8081"
    environment:
      - FLEXT_FLEXCORE_URL=http://flexcore:8080
    depends_on:
      - postgres
      - redis
      - flexcore
```

---

**This API contract documentation ensures reliable, secure, and efficient communication between FlexCore and FLEXT Service, providing the foundation for professional data integration operations across the entire FLEXT ecosystem.**

**Navigation**: [FLEXT Hub](NAVIGATION.md) > Documentation > API Contracts
**Related Documentation**: [FlexCore CLAUDE.md](../flexcore/CLAUDE.md) | [FLEXT Service CLAUDE.md](../cmd/flext/CLAUDE.md)
**Version**: 2.0.0 | **Last Updated**: 2025-08-02
