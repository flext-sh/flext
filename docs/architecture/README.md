# FLEXT Architecture

**Version**: 0.9.0-dev | **Status**: Under Development | **Last Updated**: 2025-08-05

## Overview

FLEXT implements a dual-service distributed architecture with Clean Architecture principles, Domain-Driven Design, CQRS, and Event Sourcing patterns. This section covers the core architectural decisions and current implementation status.

## Architecture Documentation

### [Overview](./overview.md)

**Primary Document**: Complete system architecture, service status, and development roadmap.

### [Clean Architecture](./clean-architecture.md)

**Implementation Guide**: Detailed Clean Architecture patterns with Go code examples.

### [FlexCore Current State](./flexcore-current-state.md)

**Current Reality**: Honest assessment of FlexCore's architectural compliance and critical issues.

### [Python-Go Integration](./python-go-integration.md)

**Integration Patterns**: Cross-language integration patterns and communication protocols.

## Key Concepts

### Architectural Principles

- **Clean Architecture**: Separation of concerns with clear boundaries
- **Domain-Driven Design**: Business domain modeling
- **CQRS**: Command/Query Responsibility Segregation
- **Event Sourcing**: Immutable event log for state reconstruction
- **Microservices**: Loosely coupled, independently deployable services

### Technology Stack

- **Go 1.24+**: Control plane implementation
- **Python 3.13+**: Data processing (Singer, Meltano, DBT)
- **PostgreSQL 15**: Primary data store
- **Redis 7**: Caching and message broker
- **Docker**: Containerization

### System Components

```
┌─────────────────────────────────────────────┐
│              FLEXT Control Panel            │
│              (Go - Port 8081)               │
│  ┌─────────────┬─────────────┬─────────────┐ │
│  │   API       │  Service    │  Plugin     │ │
│  │  Gateway    │ Discovery   │ Management  │ │
│  └─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│              FlexCore Runtime               │
│              (Go - Port 8080)               │
│  ┌─────────────┬─────────────┬─────────────┐ │
│  │ Workflow    │  Resource   │  Event      │ │
│  │ Execution   │ Management  │  Sourcing   │ │
│  └─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│            Python Ecosystem                 │
│            (33 Projects)                    │
│  ┌─────────────┬─────────────┬─────────────┐ │
│  │ Foundation  │ Integration │ Processing  │ │
│  │ Libraries   │ Services    │ Libraries   │ │
│  └─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────┘
```

## Integration Patterns

### Service Communication

- **gRPC**: High-performance service-to-service communication
- **HTTP/REST**: External API exposure
- **Event Streaming**: hronous event processing

### Data Flow

- **ETL Pipelines**: Extract, Transform, Load workflows
- **Stream Processing**: Real-time data processing
- **Batch Processing**: Large-scale data operations

### Deployment

- **Docker Containers**: Isolated service deployment
- **Kubernetes**: Orchestration and scaling
- **Service Mesh**: Inter-service communication

## Quality Standards

### Performance

- **Response Time**: < 100ms for API calls
- **Throughput**: 1000+ concurrent requests
- **Availability**: 99.9% uptime

### Security

- **Authentication**: JWT-based token system
- **Authorization**: Role-based access control
- **Encryption**: TLS for all communications

### Monitoring

- **Metrics**: Prometheus-based monitoring
- **Logging**: Structured logging with correlation IDs
- **Tracing**: Distributed tracing with OpenTelemetry

---

See [Patterns](../patterns/README.md) for implementation patterns.
