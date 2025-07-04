# 🚀 FLEXT-MELTANO PRODUCTION DEPLOYMENT GUIDE

**Version**: 2.0.0
**Last Updated**: 2025-06-30
**Status**: Production Ready

---

## 📋 OVERVIEW

This guide provides comprehensive instructions for deploying the FLEXT-Meltano integration in production environments. The system features robust error handling, state persistence, process pooling, and enterprise-grade monitoring capabilities.

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    FLEXT PRODUCTION STACK                   │
├─────────────────────────────────────────────────────────────┤
│ Load Balancer (nginx/HAProxy)                              │
├─────────────────────────────────────────────────────────────┤
│ FLEXT API Server (Go)                                      │
│ ├── HTTP/REST API (Port 8081)                              │
│ ├── WebSocket (Real-time monitoring)                       │
│ ├── Meltano Integration Layer                              │
│ │   ├── Process Pool (Configurable concurrency)           │
│ │   ├── State Management (File-based persistence)         │
│ │   ├── Timeout & Retry Logic                             │
│ │   └── Auto-configuration Detection                      │
│ └── Database Layer (PostgreSQL/In-Memory)                  │
├─────────────────────────────────────────────────────────────┤
│ Python Environment                                         │
│ ├── Meltano 3.7.8+                                        │
│ ├── Singer Protocol Plugins                               │
│ └── Custom Bridge Module                                   │
├─────────────────────────────────────────────────────────────┤
│ Monitoring & Observability                                 │
│ ├── Prometheus (Metrics collection)                        │
│ ├── Grafana (Dashboards)                                   │
│ ├── Jaeger (Distributed tracing)                          │
│ └── Structured Logging (JSON)                              │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ SYSTEM REQUIREMENTS

### Minimum Requirements

- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 20GB SSD
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- **Network**: HTTP/HTTPS connectivity

### Recommended Production Requirements

- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 100GB+ SSD (for logs and state persistence)
- **OS**: Linux with systemd support
- **Network**: Load balancer + multiple instances

### Software Dependencies

- **Go**: 1.24+ (for building)
- **Python**: 3.9+ with pip
- **PostgreSQL**: 13+ (optional, can use in-memory)
- **Redis**: 6+ (for sessions/cache)
- **nginx/HAProxy**: For load balancing

## 📦 DEPLOYMENT OPTIONS

### Option 1: Docker Deployment (Recommended)

#### 1.1 Create Production Dockerfile

```dockerfile
# Multi-stage build for optimized production image
FROM golang:1.24-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o flext-server cmd/flext/*.go

# Production image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 flext
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Meltano
RUN pip install --no-cache-dir meltano>=3.2.0

# Copy application
COPY --from=builder /app/flext-server /usr/local/bin/
COPY python-meltano-bridge/ ./python-meltano-bridge/
COPY config/ ./config/

# Install bridge module
RUN pip install -e ./python-meltano-bridge/

# Set up directories
RUN mkdir -p /app/data /app/logs /app/state && \
    chown -R flext:flext /app

USER flext

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

EXPOSE 8081

# Environment variables
ENV ENVIRONMENT=production
ENV LOG_LEVEL=info
ENV ENABLE_METRICS=true
ENV DATABASE_ENABLED=false

CMD ["flext-server"]
```

#### 1.2 Docker Compose for Production

```yaml
version: "3.8"

services:
  flext-api:
    build: .
    container_name: flext-api
    restart: unless-stopped
    ports:
      - "8081:8081"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
      - DATABASE_ENABLED=true
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=flext
      - POSTGRES_USER=flext
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - REDIS_URL=redis://redis:6379
      - PYTHON_PATH=/usr/local/bin/python3
      - MELTANO_STATE_DIR=/app/state
      - MAX_CONCURRENT_PROCESSES=10
      - BRIDGE_TIMEOUT=60s
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./state:/app/state
    depends_on:
      - postgres
      - redis
    networks:
      - flext-network

  postgres:
    image: postgres:15
    container_name: flext-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=flext
      - POSTGRES_USER=flext
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - flext-network

  redis:
    image: redis:7-alpine
    container_name: flext-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - flext-network

  prometheus:
    image: prom/prometheus:latest
    container_name: flext-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - flext-network

  grafana:
    image: grafana/grafana:latest
    container_name: flext-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - flext-network

  nginx:
    image: nginx:alpine
    container_name: flext-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - flext-api
    networks:
      - flext-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  flext-network:
    driver: bridge
```

### Option 2: Native Deployment

#### 2.1 System Setup

```bash
# Create flext user
sudo useradd -m -s /bin/bash flext
sudo usermod -aG sudo flext

# Create directories
sudo mkdir -p /opt/flext/{bin,config,data,logs,state}
sudo chown -R flext:flext /opt/flext

# Install Go
wget https://go.dev/dl/go1.24.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.24.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc

# Install Python and dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

#### 2.2 Application Setup

```bash
# Switch to flext user
sudo su - flext

# Create Python virtual environment
python3 -m venv /opt/flext/.venv
source /opt/flext/.venv/bin/activate

# Install Meltano
pip install meltano>=3.2.0

# Build FLEXT server
cd /path/to/source
go build -o /opt/flext/bin/flext-server cmd/flext/*.go

# Install bridge module
cp -r python-meltano-bridge /opt/flext/
cd /opt/flext && pip install -e ./python-meltano-bridge/

# Copy configuration
cp -r config/* /opt/flext/config/
```

#### 2.3 Systemd Service

```ini
# /etc/systemd/system/flext.service
[Unit]
Description=FLEXT-Meltano Integration Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=flext
Group=flext
WorkingDirectory=/opt/flext
ExecStart=/opt/flext/bin/flext-server
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Environment
Environment=ENVIRONMENT=production
Environment=LOG_LEVEL=info
Environment=PYTHON_PATH=/opt/flext/.venv/bin/python3
Environment=MELTANO_STATE_DIR=/opt/flext/state
Environment=MAX_CONCURRENT_PROCESSES=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/flext

[Install]
WantedBy=multi-user.target
```

### Option 3: Kubernetes Deployment

#### 3.1 Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext-api
  labels:
    app: flext-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flext-api
  template:
    metadata:
      labels:
        app: flext-api
    spec:
      containers:
        - name: flext-api
          image: flext:latest
          ports:
            - containerPort: 8081
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: LOG_LEVEL
              value: "info"
            - name: DATABASE_ENABLED
              value: "true"
            - name: POSTGRES_HOST
              value: "flext-postgres"
            - name: MAX_CONCURRENT_PROCESSES
              value: "10"
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8081
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8081
            initialDelaySeconds: 5
            periodSeconds: 5
          volumeMounts:
            - name: state-storage
              mountPath: /app/state
      volumes:
        - name: state-storage
          persistentVolumeClaim:
            claimName: flext-state-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: flext-api-service
spec:
  selector:
    app: flext-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8081
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: flext-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.flext.your-domain.com
      secretName: flext-tls
  rules:
    - host: api.flext.your-domain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: flext-api-service
                port:
                  number: 80
```

## ⚙️ CONFIGURATION

### Environment Variables

| Variable                   | Description                              | Default           | Required            |
| -------------------------- | ---------------------------------------- | ----------------- | ------------------- |
| `ENVIRONMENT`              | Deployment environment                   | `development`     | No                  |
| `LOG_LEVEL`                | Logging level (debug, info, warn, error) | `info`            | No                  |
| `PYTHON_PATH`              | Python interpreter path                  | Auto-detected     | No                  |
| `MELTANO_PATH`             | Meltano executable path                  | Auto-detected     | No                  |
| `MELTANO_STATE_DIR`        | State persistence directory              | `./meltano_state` | No                  |
| `MAX_CONCURRENT_PROCESSES` | Max Python processes                     | `5`               | No                  |
| `BRIDGE_TIMEOUT`           | Python operation timeout                 | `30s`             | No                  |
| `MAX_RETRIES`              | Operation retry attempts                 | `3`               | No                  |
| `DATABASE_ENABLED`         | Enable PostgreSQL                        | `false`           | No                  |
| `POSTGRES_HOST`            | PostgreSQL host                          | `localhost`       | No                  |
| `POSTGRES_PORT`            | PostgreSQL port                          | `5432`            | No                  |
| `POSTGRES_DB`              | Database name                            | `flext`           | No                  |
| `POSTGRES_USER`            | Database user                            | `flext`           | No                  |
| `POSTGRES_PASSWORD`        | Database password                        | -                 | Yes (if DB enabled) |

### Production Configuration File

```yaml
# config/production.yaml
server:
  host: "0.0.0.0"
  port: 8081
  read_timeout: 30s
  write_timeout: 30s
  shutdown_timeout: 10s
  enable_cors: true

logging:
  level: "info"
  format: "json"
  output: "stdout"

database:
  enabled: true
  driver: "postgres"
  host: "${POSTGRES_HOST}"
  port: 5432
  database: "${POSTGRES_DB}"
  username: "${POSTGRES_USER}"
  password: "${POSTGRES_PASSWORD}"
  ssl_mode: "require"
  max_open_connections: 25
  max_idle_connections: 5

meltano:
  state_dir: "/app/state"
  bridge_timeout: "60s"
  max_concurrent: 10
  max_retries: 3
  retry_delay: "2s"

monitoring:
  enabled: true
  prometheus_enabled: true
  jaeger_enabled: true
  health_check_interval: "30s"

features:
  database_enabled: true
  websocket_enabled: true
  quality_system_enabled: true
```

## 🔒 SECURITY CONSIDERATIONS

### 1. Network Security

- Use HTTPS/TLS for all external communication
- Implement IP whitelisting for REDACTED_LDAP_BIND_PASSWORDistrative endpoints
- Use VPC/private networks for internal communication
- Regular security updates for all components

### 2. Authentication & Authorization

```bash
# Generate JWT secret
openssl rand -base64 32

# Set in environment
export JWT_SECRET="your-generated-secret"
```

### 3. File System Security

```bash
# Set proper permissions
chmod 750 /opt/flext
chmod 640 /opt/flext/config/*
chmod 755 /opt/flext/bin/*

# SELinux contexts (if applicable)
setsebool -P httpd_can_network_connect 1
```

## 📊 MONITORING & OBSERVABILITY

### 1. Health Checks

```bash
# Application health
curl http://localhost:8081/health

# Meltano service health
curl http://localhost:8081/api/v1/meltano/health

# Process pool status
curl http://localhost:8081/api/v1/meltano/stats

# State management status
curl http://localhost:8081/api/v1/meltano/state/stats
```

### 2. Prometheus Metrics

Key metrics to monitor:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `meltano_executions_total` - Total pipeline executions
- `meltano_execution_duration_seconds` - Pipeline execution time
- `meltano_process_pool_active` - Active Python processes
- `meltano_state_records_total` - Persisted state records

### 3. Grafana Dashboards

Import the provided dashboard JSON from `config/grafana/dashboards/flext-overview.json`:

- System Overview
- Request Rate & Latency
- Meltano Operations
- Process Pool Utilization
- Error Rate Monitoring
- State Management Statistics

### 4. Log Aggregation

Configure log shipping to your centralized logging system:

```yaml
# filebeat.yml example
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /opt/flext/logs/*.log
    fields:
      service: flext
      environment: production
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## 🚀 DEPLOYMENT PROCEDURES

### 1. Pre-deployment Checklist

- [ ] System requirements met
- [ ] Dependencies installed
- [ ] Configuration files prepared
- [ ] SSL certificates configured
- [ ] Database migrations ready
- [ ] Monitoring systems configured
- [ ] Backup procedures tested

### 2. Deployment Steps

```bash
# 1. Stop existing service
sudo systemctl stop flext

# 2. Backup current deployment
tar -czf flext-backup-$(date +%Y%m%d).tar.gz /opt/flext

# 3. Deploy new version
cp flext-server /opt/flext/bin/
cp -r config/* /opt/flext/config/

# 4. Update permissions
chown -R flext:flext /opt/flext

# 5. Start service
sudo systemctl start flext

# 6. Verify deployment
curl http://localhost:8081/health
```

### 3. Rolling Updates (Kubernetes)

```bash
# Update image
kubectl set image deployment/flext-api flext-api=flext:v2.0.1

# Monitor rollout
kubectl rollout status deployment/flext-api

# Rollback if needed
kubectl rollout undo deployment/flext-api
```

## 🔧 PERFORMANCE TUNING

### 1. Resource Allocation

| Component        | CPU                     | Memory            | Notes                              |
| ---------------- | ----------------------- | ----------------- | ---------------------------------- |
| FLEXT API        | 2-4 cores               | 2-4GB             | Scale based on concurrent users    |
| Python Processes | 1 core per 5 concurrent | 512MB per process | Configure MAX_CONCURRENT_PROCESSES |
| PostgreSQL       | 2-4 cores               | 4-8GB             | Depends on data volume             |
| Redis            | 1 core                  | 1-2GB             | For sessions and cache             |

### 2. Database Optimization

```sql
-- Recommended PostgreSQL settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### 3. Application Tuning

```bash
# Optimize Go runtime
export GOGC=100                    # GC percentage
export GOMAXPROCS=4               # Max OS threads

# Python optimization
export PYTHONUNBUFFERED=1         # Unbuffered output
export PYTHONDONTWRITEBYTECODE=1  # No .pyc files
```

## 📋 MAINTENANCE PROCEDURES

### 1. Regular Tasks

#### Daily

- Monitor system health
- Check error logs
- Verify backup completion

#### Weekly

- Review performance metrics
- Clean old log files
- Update security patches

#### Monthly

- Database maintenance
- Capacity planning review
- Security audit

### 2. Backup Procedures

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/flext"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application
tar -czf "$BACKUP_DIR/flext-app-$DATE.tar.gz" /opt/flext

# Backup database (if enabled)
pg_dump -h localhost -U flext flext > "$BACKUP_DIR/flext-db-$DATE.sql"

# Backup state data
tar -czf "$BACKUP_DIR/flext-state-$DATE.tar.gz" /opt/flext/state

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete
```

### 3. Disaster Recovery

```bash
#!/bin/bash
# restore.sh

BACKUP_DATE=$1
BACKUP_DIR="/backups/flext"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 YYYYMMDD_HHMMSS"
    exit 1
fi

# Stop service
sudo systemctl stop flext

# Restore application
tar -xzf "$BACKUP_DIR/flext-app-$BACKUP_DATE.tar.gz" -C /

# Restore database
psql -h localhost -U flext flext < "$BACKUP_DIR/flext-db-$BACKUP_DATE.sql"

# Restore state
tar -xzf "$BACKUP_DIR/flext-state-$BACKUP_DATE.tar.gz" -C /opt/flext/

# Fix permissions
chown -R flext:flext /opt/flext

# Start service
sudo systemctl start flext
```

## 🔍 TROUBLESHOOTING

### Common Issues

#### 1. Service Won't Start

```bash
# Check logs
journalctl -u flext -f

# Verify configuration
/opt/flext/bin/flext-server --config-check

# Check permissions
ls -la /opt/flext/
```

#### 2. High Memory Usage

```bash
# Monitor process pool
curl http://localhost:8081/api/v1/meltano/stats

# Reduce concurrent processes
export MAX_CONCURRENT_PROCESSES=3
sudo systemctl restart flext
```

#### 3. Database Connection Issues

```bash
# Test connection
psql -h localhost -U flext flext -c "SELECT version();"

# Check pool status
curl http://localhost:8081/health
```

#### 4. Python Environment Issues

```bash
# Verify Python path
which python3

# Check Meltano installation
meltano --version

# Test bridge module
python3 -c "import meltano_bridge; print('OK')"
```

### Log Analysis

```bash
# Error analysis
grep -i error /opt/flext/logs/flext.log | tail -20

# Performance analysis
grep "slow_request" /opt/flext/logs/flext.log

# State management issues
grep "state_manager" /opt/flext/logs/flext.log
```

## 🎯 VALIDATION & TESTING

### 1. Post-Deployment Tests

Run the comprehensive test suite:

```bash
# End-to-end functionality test
./scripts/test-end-to-end-pipeline.sh

# Performance validation
./scripts/stress-test.sh

# Security validation
./scripts/security-test.sh
```

### 2. Production Readiness Checklist

- [ ] All health checks passing
- [ ] Performance thresholds met
- [ ] Security scan completed
- [ ] Monitoring alerts configured
- [ ] Backup/restore tested
- [ ] Load balancer configured
- [ ] SSL certificates valid
- [ ] Documentation updated

## 📞 SUPPORT & MAINTENANCE

### Emergency Contacts

- **Operations Team**: <ops@yourcompany.com>
- **Development Team**: <dev@yourcompany.com>
- **Security Team**: <security@yourcompany.com>

### Escalation Procedures

1. **Level 1**: Restart service, check basic connectivity
2. **Level 2**: Review logs, check resource usage
3. **Level 3**: Contact development team
4. **Level 4**: Emergency rollback procedures

---

## 🎉 CONCLUSION

This deployment guide provides comprehensive instructions for running FLEXT-Meltano in production. The system is designed for high availability, scalability, and operational excellence.

**Key Production Features:**

- ✅ Auto-configuration and environment detection
- ✅ Robust error handling with timeout protection
- ✅ Process pooling for resource management
- ✅ State persistence for pipeline tracking
- ✅ Comprehensive monitoring and observability
- ✅ Security best practices implementation
- ✅ Horizontal scaling capabilities

For additional support or questions, refer to the project documentation or contact the development team.

**Happy Deploying! 🚀**
