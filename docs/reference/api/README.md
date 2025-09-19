# FLEXT API Documentation

**Version**: 0.9.9 RC | **Status**: 1.0.0 Release Preparation | **Python**: 3.13+

## Overview

Complete API documentation for the FLEXT ecosystem preparing for **flext-core 1.0.0 stable release**, including REST endpoints, contracts, and integration guidelines with guaranteed API stability.

## API Documentation

### [API Contracts](./contracts.md)

Service integration contracts between FLEXT Control Panel and FlexCore Runtime.

### OpenAPI Specifications

Machine-readable API specifications (coming soon).

## API Overview

### REST Endpoints

- **Base URL**: `http://localhost:8081/api/v1`
- **Authentication**: Bearer token
- **Content-Type**: `application/json`

### Core Resources

- `/pipelines` - Pipeline management
- `/taps` - Data source connectors
- `/targets` - Data destination connectors
- `/transformations` - Data transformations
- `/executions` - Pipeline executions

### Health & Monitoring

- `/health` - Service health check
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe

---

See [Architecture](../architecture/README.md) for system design details.
