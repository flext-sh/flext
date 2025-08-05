# FLEXT Docker Configuration

**Centralized Docker configuration for the FLEXT ecosystem**

## Container Architecture

### Production Services

- **Dockerfile.flext** - Main FLEXT service container (Go/Python hybrid)
- **Dockerfile.distributed** - Distributed cluster configuration  
- **Dockerfile.oracle-e2e** - Oracle integration testing
- **Dockerfile.e2e-test** - End-to-end testing container

### Development

- **docker-compose.yml** - Local development stack
- **docker-compose.cluster.yml** - Multi-node cluster testing
- **docker-compose.distributed.yml** - Distributed architecture

## Build Commands

```bash
# Build main FLEXT service
docker build -f docker/Dockerfile.flext -t flext:latest .

# Build distributed cluster
docker build -f docker/Dockerfile.distributed -t flext-distributed:latest .

# Run development stack  
docker-compose -f docker/docker-compose.yml up -d
```

## Configuration

All Docker configurations now centralized in `/docker` directory:

- Nginx reverse proxy configuration
- PostgreSQL initialization scripts  
- Prometheus monitoring setup
- Grafana dashboards

## Standardization

- Removed duplicate and test Dockerfiles
- Consolidated build patterns
- Unified environment variable naming
- Consistent health check implementations
