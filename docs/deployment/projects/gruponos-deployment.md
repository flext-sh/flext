# 🏢 Grupo NOS Deployment Guide - OIC-WMS Integration

> **Function**: Complete deployment procedures for Grupo NOS OIC-WMS integration | **Audience**: Project teams, DevOps engineers | **Status**: Production-Ready

[![Grupo NOS](https://img.shields.io/badge/project-grupo_nos-blue.svg)](../index.md)
[![OIC-WMS](https://img.shields.io/badge/integration-oracle_oic_wms-green.svg)](../../guides/oracle/index.md)
[![Production](https://img.shields.io/badge/deployment-production_ready-orange.svg)](../strategies/production-checklist.md)

**Complete deployment guide for Grupo NOS Oracle Integration Cloud (OIC) and Warehouse Management System (WMS) integration using FLX Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Section**: [Deployment](../index.md) → **📂 Hub**: [Projects](./index.md) → **📄 Current**: Grupo NOS Deployment

### **📍 Learning Path Position**

```
[Deployment Strategies](../strategies/index.md) → **[GRUPO NOS DEPLOYMENT]** → [Production Checklist](../strategies/production-checklist.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Project Deployment](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Oracle Integration**: [Oracle Guides](../../guides/oracle/index.md)

---

## Quick Start

The fastest way to get the integration running:

```bash
# 1. Clone and setup
git clone <repository-url>
cd project-gruponos-oic-wms

# 2. Run automated deployment
python scripts/deploy.py --dev

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Test installation
poetry run gn-wms-cli test
poetry run gn-wms-cli status
```

## Deployment Methods

### 1. Local Development Setup

**Prerequisites:**

- Python 3.13+
- Poetry 1.8+
- Git
- Oracle Wallet (for ADB access)

**Steps:**

```bash
# Install dependencies
poetry install --with dev

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Create required directories
mkdir -p logs output/{oic,wms,oic_executions} reports/{coverage,pytest}

# Run database setup
poetry run gn-wms-cli setup

# Test installation
poetry run gn-wms-cli test
make test
```

### 2. Docker Deployment

**Basic Docker:**

```bash
# Build image
docker build -t gruponos-oic-wms .

# Run container
docker run -d \
  --name gruponos-oic-wms \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/wallet:/app/wallet:ro \
  gruponos-oic-wms
```

**Docker Compose (Recommended):**

```bash
# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs gruponos-oic-wms

# Run CLI commands
docker-compose exec gruponos-oic-wms gn-wms-cli status
```

**Optional monitoring stack:**

```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access dashboards
# Grafana: http://localhost:3000 (admin/admin123)
# Prometheus: http://localhost:9090
```

### 3. Production Deployment

**Kubernetes (Recommended for production):**

```bash
# Create namespace
kubectl create namespace gruponos-oic-wms

# Create secrets
kubectl create secret generic gruponos-secrets \
  --from-env-file=.env \
  --namespace=gruponos-oic-wms

# Deploy application
kubectl apply -f k8s/ --namespace=gruponos-oic-wms

# Check status
kubectl get pods --namespace=gruponos-oic-wms
```

**System Service (Linux):**

```bash
# Install as system service
sudo cp deployment/gruponos-oic-wms.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gruponos-oic-wms
sudo systemctl start gruponos-oic-wms

# Check status
sudo systemctl status gruponos-oic-wms
```

## Configuration

### Environment Variables

Key configuration variables (see `.env.example` for complete list):

| Variable | Description | Required |
|----------|-------------|----------|
| `DB_HOST` | Oracle ADB hostname | Yes |
| `DB_USERNAME` | Database username | Yes |
| `DB_PASSWORD` | Database password | Yes |
| `DB_WALLET_PATH` | Oracle wallet directory | Yes |
| `WMS_URL` | WMS Cloud instance URL | Yes |
| `WMS_USERNAME` | WMS username | Yes |
| `WMS_PASSWORD` | WMS password | Yes |
| `OIC_BASE_URL` | OIC instance URL | Yes |
| `OIC_USERNAME` | OIC username | Yes |
| `OIC_PASSWORD` | OIC password | Yes |

### Oracle Wallet Setup

For Oracle Autonomous Database:

```bash
# Download wallet from Oracle Cloud Console
# Extract to /path/to/wallet
unzip Wallet_DatabaseName.zip -d /path/to/wallet

# Set environment variable
export DB_WALLET_PATH=/path/to/wallet

# Test connection
poetry run gn-wms-cli test --verbose
```

### SFTP Configuration

For batch file processing:

```bash
# Password authentication
SFTP_HOST=your-sftp-host.com
SFTP_USERNAME=username
SFTP_PASSWORD=password

# Or SSH key authentication
SFTP_PRIVATE_KEY_PATH=/path/to/private/key
```

## Operations

### CLI Commands

The flx_project provides a comprehensive CLI for operations:

```bash
# Database operations
gn-wms-cli setup              # Create database tables
gn-wms-cli test               # Test connections
gn-wms-cli status             # Show system status
gn-wms-cli check              # Check table structures
gn-wms-cli clear              # Clear test data

# Pipeline operations (via Meltano)
meltano run tap-wms target-oracle        # Extract WMS data
meltano run tap-sftp target-oracle       # Process SFTP files
meltano schedule run                      # Run scheduled pipelines
```

### Monitoring

**Health Checks:**

```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
gn-wms-cli test

# Pipeline status
meltano schedule list
```

**Logs:**

```bash
# Application logs
tail -f logs/gruponos-oic-wms.log

# Container logs
docker-compose logs -f gruponos-oic-wms

# Pipeline logs
tail -f logs/meltano.log
```

**Metrics (if enabled):**

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Grafana dashboards
open http://localhost:3000
```

### Maintenance

**Database Maintenance:**

```bash
# Check table status
gn-wms-cli check --audit --columns

# Clear test data
gn-wms-cli clear --dry-run  # Review first
gn-wms-cli clear

# Recreate tables
gn-wms-cli setup --force
```

**Pipeline Maintenance:**

```bash
# Clear pipeline state
meltano state clear

# Reset extractors
meltano invoke tap-wms --reset

# Reprocess failed batches
meltano run tap-wms target-oracle --full-refresh
```

## Troubleshooting

### Common Issues

**1. Database Connection Errors:**

```bash
# Check connectivity
gn-wms-cli test --verbose

# Verify wallet configuration
ls -la $DB_WALLET_PATH
cat $DB_WALLET_PATH/tnsnames.ora

# Test with sqlplus
sqlplus $DB_USERNAME/$DB_PASSWORD@$DB_SERVICE
```

**2. WMS API Issues:**

```bash
# Test WMS connectivity
curl -u $WMS_USERNAME:$WMS_PASSWORD $WMS_URL/api/health

# Check credentials
echo $WMS_USERNAME $WMS_PASSWORD

# Verify API version
poetry run python -c "
from gn_oic_wms_db.wms_client import WMSClient
client = WMSClient()
print(client.get_version())
"
```

**3. OIC Integration Issues:**

```bash
# Test OIC connectivity
curl -u $OIC_USERNAME:$OIC_PASSWORD $OIC_BASE_URL/ic/api/integration/v1/integrations

# Check integration status
poetry run python scripts/oic_extract_integration_metadata.py
```

**4. SFTP Issues:**

```bash
# Test SFTP connection
sftp -P $SFTP_PORT $SFTP_USERNAME@$SFTP_HOST

# Check file permissions
ls -la output/
```

### Debug Mode

Enable debug logging:

```bash
# Set environment
export LOG_LEVEL=DEBUG
export DEBUG_MODE=true

# Run with verbose output
gn-wms-cli --verbose status
```

### Performance Issues

**Memory:**

```bash
# Check memory usage
docker stats gruponos-oic-wms

# Adjust worker settings
export WORKER_PROCESSES=2
export MEMORY_LIMIT=512MB
```

**Database:**

```bash
# Check connection pool
gn-wms-cli status

# Adjust pool settings
export DB_POOL_MAX=5
export DB_POOL_MIN=1
```

## Security

### Credentials Management

**Production:** Use external secret management:

```bash
# Kubernetes secrets
kubectl create secret generic gruponos-secrets --from-env-file=.env

# Docker secrets
echo "password" | docker secret create db_password -

# HashiCorp Vault
vault kv put secret/gruponos db_password="secret"
```

**Development:** Use environment files:

```bash
# Separate environments
cp .env.example .env.dev
cp .env.example .env.prod
```

### SSL/TLS

Enable SSL verification:

```bash
export SSL_VERIFY=true
export SSL_CERT_PATH=/path/to/certificate.pem
```

### Network Security

**Firewall rules:**

```bash
# Allow Oracle ADB (port 1522)
sudo ufw allow out 1522

# Allow HTTPS (port 443)
sudo ufw allow out 443

# Allow SFTP (port 22)
sudo ufw allow out 22
```

**Docker networks:**

```bash
# Use custom bridge network
docker network create gruponos-network --driver bridge
```

## Backup and Recovery

### Database Backup

```bash
# Export data
poetry run python scripts/export_data.py --output backup_$(date +%Y%m%d).sql

# Import data
poetry run python scripts/import_data.py --input backup_20240101.sql
```

### Configuration Backup

```bash
# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ .env meltano.yml

# Restore configuration
tar -xzf config_backup_20240101.tar.gz
```

## Scaling

### Horizontal Scaling

**Multiple Workers:**

```bash
# Docker Compose
docker-compose up --scale gruponos-oic-wms=3

# Kubernetes
kubectl scale deployment gruponos-oic-wms --replicas=3
```

**Load Balancing:**

```yaml
# nginx.conf
upstream gruponos_backend {
    server gruponos-oic-wms-1:8000;
    server gruponos-oic-wms-2:8000;
    server gruponos-oic-wms-3:8000;
}
```

### Vertical Scaling

**Resource Limits:**

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2GB
      cpus: '2.0'
```

**Performance Tuning:**

```bash
export WORKER_PROCESSES=8
export WORKER_THREADS=16
export DB_POOL_MAX=20
```

## Support

### Documentation

- [README.md](README.md) - Project overview
- [API Documentation](docs/api.md) - API reference
- [Architecture](docs/architecture.md) - System design

### Logging

All operations are logged with structured logging:

```bash
# View logs
tail -f logs/gruponos-oic-wms.log | jq .

# Filter by level
tail -f logs/gruponos-oic-wms.log | jq 'select(.level=="ERROR")'

# Filter by component
tail -f logs/gruponos-oic-wms.log | jq 'select(.component=="wms")'
```

### Support Contacts

- **Technical Issues:** [technical-support@gruponos.com]
- **Integration Issues:** [integration-team@gruponos.com]
- **Emergency:** [on-call@gruponos.com]


---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Guides](../../guides/oracle/index.md) - Essential Oracle integration patterns and authentication setup
- [Production Checklist](../strategies/production-checklist.md) - General production readiness validation before project deployment
- [Infrastructure Hub](../../infrastructure/index.md) - Understanding production infrastructure services

### **Next Steps**

- [Security Hub](../../security/index.md) - Project-specific security implementation and Oracle authentication
- [Optimization Hub](../../optimization/index.md) - Performance optimization for Oracle integration workloads
- [Kubernetes Deployment](../strategies/kubernetes-deployment.md) - Container orchestration for Grupo NOS services

### **Related Topics**

- [Guides Hub](../../guides/index.md) - Oracle WMS and OIC integration detailed guides
- [Examples Hub](../../examples/index.md) - Oracle integration examples and automation templates
- [Migration Hub](../../migration/index.md) - Project migration strategies for framework upgrades
- [API Reference Hub](../../api-reference/index.md) - Oracle integration API configurations

---

**📂 Hub**: [Project Deployment](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
