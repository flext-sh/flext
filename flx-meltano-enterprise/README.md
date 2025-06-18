# FLX Enterprise Data Platform

Enterprise-grade data platform built on top of Meltano, providing advanced features for production data pipelines.

## 🚀 Features

- **Daemon Architecture**: Core daemon with gRPC for high-performance communication
- **Multiple Interfaces**: Django Web UI, FastAPI REST API, Click CLI
- **Enterprise Patterns**: Circuit breaker, retry policies, bulkhead isolation
- **Production Ready**: Docker, Kubernetes, monitoring, observability
- **Meltano Integration**: Leverages Meltano for ELT orchestration
- **Multi-tenancy**: Organization-based isolation
- **Security**: JWT authentication, RBAC, audit trails

## 📋 Requirements

- Python 3.13+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose
- Kubernetes (for production deployment)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd flx-meltano-enterprise
cp .env.example .env
# Edit .env with your configuration
```

### 2. Install Dependencies

```bash
make dev-install
```

### 3. Start Services

```bash
# Start infrastructure services
docker-compose up -d postgres redis rabbitmq minio

# Run migrations
make migrate

# Start development servers (each in separate terminal)
make daemon  # Core daemon
make web     # Django web UI
make api     # FastAPI REST API
```

### 4. Access Services

- Web UI: http://localhost:8080
- REST API: http://localhost:8081/api/docs
- gRPC: localhost:50051
- Metrics: http://localhost:8000/metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FLX Enterprise Platform                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐      │
│  │ Django  │  │ FastAPI  │  │ Click  │  │ gRPC/WS  │      │
│  │ Web UI  │  │ REST API │  │  CLI   │  │ Clients  │      │
│  └────┬────┘  └────┬─────┘  └───┬────┘  └────┬─────┘      │
│       └────────────┴────────────┴─────────────┘            │
│                           │                                 │
│                    ┌──────┴──────┐                         │
│                    │ Core Daemon │                         │
│                    └──────┬──────┘                         │
│                           │                                 │
│                    ┌──────┴──────┐                         │
│                    │   Meltano   │                         │
│                    └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
flx-meltano-enterprise/
├── flx_core/          # Core daemon implementation
├── flx_web/           # Django web interface
├── flx_api/           # FastAPI REST API
├── flx_cli/           # Click CLI client
├── flx_extensions/    # Meltano extensions
├── deployments/       # Docker & Kubernetes configs
├── tests/             # Test suites
└── docs/              # Documentation
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test suites
make test-unit
make test-integration
make test-e2e

# Generate coverage report
make coverage
```

## 🚀 Deployment

### Docker

```bash
# Build images
make docker-build

# Start services
make docker-up

# View logs
make docker-logs
```

### Kubernetes

```bash
# Deploy with Helm
make k8s-deploy

# Check status
make k8s-status
```

## 📊 Monitoring

- **Metrics**: Prometheus metrics at `/metrics`
- **Tracing**: OpenTelemetry integration
- **Logs**: Structured logging with correlation IDs
- **Health Checks**: `/health` and `/ready` endpoints

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Multi-tenancy support
- Audit logging
- Secret management

## 🤝 Contributing

1. Follow Python 3.13+ best practices
2. Maintain >90% test coverage
3. Run `make check-all` before committing
4. Use conventional commits

## 📝 License

MIT License - see LICENSE file for details
