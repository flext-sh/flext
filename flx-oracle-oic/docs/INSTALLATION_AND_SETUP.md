# Installation and Setup Guide

> **tap-oic Version**: 2.0
> **Last Updated**: June 15, 2025

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Authentication Setup](#authentication-setup)
5. [Initial Setup](#initial-setup)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 2GB RAM
- **Network**: HTTPS access to Oracle Cloud

### Oracle Integration Cloud Requirements

- **OIC Generation**: 3 (required for REST API access)
- **User Role**: Integration Developer or Administrator
- **API Access**: REST API enabled for your instance
- **Network**: Whitelisted IP addresses (if applicable)

### Python Dependencies

```bash
# Core dependencies
python >= 3.8
singer-python >= 6.0.0
requests >= 2.28.0
pydantic >= 2.0.0

# Optional dependencies
meltano >= 2.0.0  # For Meltano integration
boto3 >= 1.26.0   # For S3 state management
redis >= 4.5.0    # For Redis state management
```

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install tap-oic
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/tap-oic.git
cd tap-oic

# Install in development mode
pip install -e .
```

### Method 3: Install with Meltano

```bash
# Add to Meltano project
meltano add extractor tap-oic

# Or with custom repository
meltano add extractor tap-oic --from-ref https://github.com/your-org/tap-oic.git
```

### Method 4: Docker Installation

```dockerfile
FROM python:3.11-slim

RUN pip install tap-oic

# Copy configuration
COPY config.json /app/config.json
COPY catalog.json /app/catalog.json

WORKDIR /app

CMD ["tap-oic", "--config", "config.json", "--catalog", "catalog.json"]
```

## Configuration

### Configuration File Structure

Create a `config.json` file:

```json
{
  "instance_url": "https://your-instance.integration.ocp.oraclecloud.com",
  "username": "your.email@example.com",
  "password": "${OIC_PASSWORD}",
  "start_date": "2025-01-01T00:00:00Z",
  "api_version": "v1",
  "page_size": 100,
  "request_timeout": 300,
  "max_retries": 3,
  "retry_delay": 60,
  "selected_streams": [
    "integrations",
    "connections",
    "projects",
    "executions",
    "metrics"
  ],
  "state_backend": {
    "type": "file",
    "path": "./state.json"
  },
  "advanced": {
    "verify_ssl": true,
    "user_agent": "tap-oic/2.0",
    "compression": "gzip",
    "connection_pool_size": 10
  }
}
```

### Configuration Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `instance_url` | Yes | OIC instance URL | - |
| `username` | Yes | OIC username | - |
| `password` | Yes | OIC password | - |
| `start_date` | No | Start date for data extraction | 30 days ago |
| `api_version` | No | API version to use | "v1" |
| `page_size` | No | Records per page | 100 |
| `request_timeout` | No | Request timeout in seconds | 300 |
| `max_retries` | No | Maximum retry attempts | 3 |
| `retry_delay` | No | Delay between retries | 60 |
| `selected_streams` | No | Streams to extract | All available |
| `state_backend` | No | State storage configuration | File-based |
| `verify_ssl` | No | Verify SSL certificates | true |

### Environment Variables

You can use environment variables for sensitive data:

```bash
# Set environment variables
export OIC_INSTANCE_URL="https://your-instance.integration.ocp.oraclecloud.com"
export OIC_USERNAME="your.email@example.com"
export OIC_PASSWORD="your-password"

# Reference in config.json
{
  "instance_url": "${OIC_INSTANCE_URL}",
  "username": "${OIC_USERNAME}",
  "password": "${OIC_PASSWORD}"
}
```

## Authentication Setup

### Basic Authentication

The simplest authentication method:

```json
{
  "username": "your.email@example.com",
  "password": "your-password"
}
```

### OAuth 2.0 Authentication

For enhanced security:

```json
{
  "auth_type": "oauth2",
  "client_id": "your-client-id",
  "client_secret": "${OIC_CLIENT_SECRET}",
  "token_url": "https://identity.oraclecloud.com/oauth2/v1/token",
  "scope": "https://your-instance.integration.ocp.oraclecloud.com:443"
}
```

### API Key Authentication

If configured in OIC:

```json
{
  "auth_type": "api_key",
  "api_key": "${OIC_API_KEY}",
  "api_key_header": "X-API-Key"
}
```

### Certificate-Based Authentication

For enterprise deployments:

```json
{
  "auth_type": "certificate",
  "cert_file": "/path/to/client.crt",
  "key_file": "/path/to/client.key",
  "ca_bundle": "/path/to/ca-bundle.crt"
}
```

## Initial Setup

### Step 1: Verify OIC Access

```bash
# Test connection to OIC
curl -u username:password \
  https://your-instance.integration.ocp.oraclecloud.com/ic/api/integration/v1/integrations \
  -H "Accept: application/json"
```

### Step 2: Create Configuration

```bash
# Create config directory
mkdir tap-oic-config
cd tap-oic-config

# Create configuration file
cat > config.json << EOF
{
  "instance_url": "https://your-instance.integration.ocp.oraclecloud.com",
  "username": "your.email@example.com",
  "password": "${OIC_PASSWORD}",
  "start_date": "2025-01-01T00:00:00Z"
}
EOF
```

### Step 3: Discover Available Streams

```bash
# Run discovery
tap-oic --config config.json --discover > catalog.json

# View available streams
cat catalog.json | jq '.streams[].stream'
```

### Step 4: Select Streams

Edit `catalog.json` to enable desired streams:

```json
{
  "streams": [
    {
      "stream": "integrations",
      "tap_stream_id": "integrations",
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "inclusion": "available",
            "selected": true,
            "forced-replication-method": "INCREMENTAL",
            "replication-key": "modifiedTime"
          }
        }
      ]
    }
  ]
}
```

### Step 5: Run Initial Sync

```bash
# Test run (outputs to stdout)
tap-oic --config config.json --catalog catalog.json

# Production run (pipe to target)
tap-oic --config config.json --catalog catalog.json | target-postgres --config target-config.json
```

## Verification

### Verify Installation

```bash
# Check version
tap-oic --version

# Run help
tap-oic --help

# Test configuration
tap-oic --config config.json --validate
```

### Verify Connectivity

```python
#!/usr/bin/env python3
import json
from tap_oic import OICClient

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Test connection
client = OICClient(config)
try:
    integrations = client.get_integrations(limit=1)
    print(f"✓ Connected successfully! Found {integrations['totalResults']} integrations")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Verify Data Extraction

```bash
# Extract sample data
tap-oic --config config.json --catalog catalog.json --limit 10 > sample_output.jsonl

# Verify output
cat sample_output.jsonl | jq -c '. | select(.type == "RECORD") | .record' | head -5
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failed

```
Error: 401 Unauthorized
```

**Solution**:
- Verify username and password
- Check if account is locked
- Ensure user has API access permissions
- Try using environment variables for credentials

#### 2. SSL Certificate Error

```
Error: SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution**:
```json
{
  "advanced": {
    "verify_ssl": false
  }
}
```

Or install certificates:
```bash
pip install certifi
export SSL_CERT_FILE=$(python -m certifi)
```

#### 3. Connection Timeout

```
Error: Connection timeout after 300s
```

**Solution**:
```json
{
  "request_timeout": 600,
  "advanced": {
    "connection_pool_size": 20
  }
}
```

#### 4. Rate Limit Exceeded

```
Error: 429 Too Many Requests
```

**Solution**:
```json
{
  "page_size": 50,
  "retry_delay": 120,
  "max_retries": 5
}
```

#### 5. Memory Issues

```
Error: MemoryError
```

**Solution**:
- Reduce page_size
- Enable streaming mode
- Use state management for incremental sync

### Debug Mode

Enable detailed logging:

```bash
# Set log level
export SINGER_LOG_LEVEL=DEBUG

# Run with debug output
tap-oic --config config.json --catalog catalog.json --debug

# Save debug logs
tap-oic --config config.json --catalog catalog.json --debug 2> debug.log
```

### Getting Help

1. **Check logs**: Review debug output for detailed error messages
2. **Validate config**: Run `tap-oic --config config.json --validate`
3. **Test connectivity**: Use curl to test OIC API directly
4. **Community**: Join Singer Slack community
5. **Oracle Support**: Contact for OIC-specific issues

## Oracle Cloud Infrastructure (OCI) Deployment

### Overview

For enterprises using Oracle Cloud, tap-oic can be deployed on OCI using native services for enhanced security, scalability, and integration.

### Architecture on OCI

```
┌─────────────────────────────────────────────────────────────┐
│                     Oracle Cloud Infrastructure              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐  ┌─────────────────────────┐  │
│  │      OKE Cluster         │  │   Autonomous Database    │  │
│  │  ┌─────────────────┐    │  │  ┌─────────────────┐    │  │
│  │  │  tap-oic pods   │────┼──┼─▶│  Target Tables  │    │  │
│  │  └─────────────────┘    │  │  └─────────────────┘    │  │
│  │  ┌─────────────────┐    │  └─────────────────────────┘  │
│  │  │  Orchestrator   │    │                                │
│  │  └─────────────────┘    │  ┌─────────────────────────┐  │
│  └─────────────────────────┘  │    Object Storage       │  │
│                                │  ┌─────────────────┐    │  │
│  ┌─────────────────────────┐  │  │ Extracted Data  │    │  │
│  │     OCI Vault           │  │  │   Archives      │    │  │
│  │  ┌─────────────────┐    │  │  └─────────────────┘    │  │
│  │  │   Credentials   │    │  └─────────────────────────┘  │
│  │  └─────────────────┘    │                                │
│  └─────────────────────────┘  ┌─────────────────────────┐  │
│                                │    OIC Instance         │  │
│  ┌─────────────────────────┐  │  ┌─────────────────┐    │  │
│  │     OCI Monitoring      │  │  │  Source Data    │◀───┼──│
│  │  ┌─────────────────┐    │  │  └─────────────────┘    │  │
│  │  │    Metrics &    │    │  └─────────────────────────┘  │
│  │  │     Alarms      │    │                                │
│  │  └─────────────────┘    │                                │
│  └─────────────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

### Prerequisites

1. **OCI Account** with appropriate permissions
2. **OKE Cluster** (Oracle Kubernetes Engine) or **Container Instances**
3. **Autonomous Database** or **MySQL Database Service**
4. **Object Storage Bucket** for data archival
5. **OCI Vault** for credential management
6. **VCN** with appropriate security rules

### IAM Policies

```hcl
# Policy for tap-oic service
Allow dynamic-group tap-oic-dg to manage secrets in compartment id <compartment-ocid>
Allow dynamic-group tap-oic-dg to use autonomous-database in compartment id <compartment-ocid>
Allow dynamic-group tap-oic-dg to manage objects in compartment id <compartment-ocid>
Allow dynamic-group tap-oic-dg to read metrics in compartment id <compartment-ocid>
```

### Container Deployment

#### Build Container Image

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY tap_oic/ ./tap_oic/
COPY setup.py .
RUN pip install -e .

# Add OCI CLI for vault access
RUN pip install oci-cli

# Create non-root user
RUN useradd -m -u 1000 tapuser
USER tapuser

# Entry point
ENTRYPOINT ["tap-oic"]
```

#### Build and Push to OCIR

```bash
# Build image
docker build -t tap-oic:latest .

# Tag for OCIR
docker tag tap-oic:latest <region>.ocir.io/<tenancy>/tap-oic:latest

# Login to OCIR
docker login -u '<tenancy>/<username>' <region>.ocir.io

# Push image
docker push <region>.ocir.io/<tenancy>/tap-oic:latest
```

### Kubernetes Deployment (OKE)

#### Create Namespace and Secrets

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: data-pipeline
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: tap-oic-config
  namespace: data-pipeline
type: Opaque
stringData:
  config.json: |
    {
      "base_url": "${OIC_BASE_URL}",
      "oauth_client_id": "${OIC_CLIENT_ID}",
      "oauth_client_secret": "${OIC_CLIENT_SECRET}",
      "oauth_token_url": "${OIC_TOKEN_URL}"
    }
```

#### Deploy tap-oic

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tap-oic
  namespace: data-pipeline
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tap-oic
  template:
    metadata:
      labels:
        app: tap-oic
    spec:
      serviceAccountName: tap-oic-sa
      containers:
      - name: tap-oic
        image: <region>.ocir.io/<tenancy>/tap-oic:latest
        env:
        - name: OCI_RESOURCE_PRINCIPAL_VERSION
          value: "2.2"
        - name: OCI_RESOURCE_PRINCIPAL_REGION
          value: "us-ashburn-1"
        volumeMounts:
        - name: config
          mountPath: /config
          readOnly: true
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
      volumes:
      - name: config
        secret:
          secretName: tap-oic-config
```

#### Schedule Extraction with CronJob

```yaml
# cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: tap-oic-hourly
  namespace: data-pipeline
spec:
  schedule: "0 * * * *"  # Every hour
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: tap-oic-sa
          containers:
          - name: tap-oic
            image: <region>.ocir.io/<tenancy>/tap-oic:latest
            command:
            - /bin/bash
            - -c
            - |
              tap-oic --config /config/config.json \
                      --catalog /catalog/catalog.json \
                      --state /state/state.json | \
              target-oracle --config /config/target-config.json
          restartPolicy: OnFailure
```

### OCI Vault Integration

```python
# vault_integration.py
import oci
import json
import base64

def get_secret_from_vault(secret_id):
    """Retrieve secret from OCI Vault."""
    # Use Instance Principal authentication
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

    # Create client
    secrets_client = oci.secrets.SecretsClient(config={}, signer=signer)

    # Get secret
    response = secrets_client.get_secret_bundle(secret_id)

    # Decode secret
    secret_content = base64.b64decode(
        response.data.secret_bundle_content.content
    ).decode('utf-8')

    return json.loads(secret_content)

# Usage in tap-oic
def get_config():
    """Get configuration from OCI Vault."""
    secret_id = os.environ.get('OCI_SECRET_ID')
    if secret_id:
        return get_secret_from_vault(secret_id)
    else:
        # Fallback to file
        with open('/config/config.json') as f:
            return json.load(f)
```

### Autonomous Database Integration

```sql
-- Create schema for OIC data
CREATE USER oic_data IDENTIFIED BY <password>;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO oic_data;
GRANT UNLIMITED TABLESPACE TO oic_data;

-- Create tables
CREATE TABLE oic_data.integrations (
    id VARCHAR2(100) PRIMARY KEY,
    name VARCHAR2(255),
    status VARCHAR2(50),
    version VARCHAR2(20),
    pattern VARCHAR2(50),
    time_created TIMESTAMP,
    time_updated TIMESTAMP,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Object Storage Archive

```python
# archive_to_oci.py
import oci
from datetime import datetime

def archive_to_object_storage(data, bucket_name, namespace):
    """Archive extracted data to OCI Object Storage."""
    # Use Instance Principal
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    object_storage = oci.object_storage.ObjectStorageClient(
        config={},
        signer=signer
    )

    # Create object name with timestamp
    object_name = f"tap-oic/extracts/{datetime.utcnow().strftime('%Y/%m/%d/%H')}/data.jsonl"

    # Upload data
    object_storage.put_object(
        namespace_name=namespace,
        bucket_name=bucket_name,
        object_name=object_name,
        put_object_body=data
    )
```

### Cost Optimization

#### Use Flex Shapes

```yaml
nodePool:
  - name: tap-oic-pool
    size: 2
    shape: VM.Standard.E4.Flex
    shapeConfig:
      ocpus: 2
      memoryInGBs: 16
```

#### Autoscaling Configuration

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tap-oic-hpa
  namespace: data-pipeline
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tap-oic
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Next Steps

- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Architecture and best practices
- [Integration Generation](INTEGRATION_GENERATION.md) - Creating integrations programmatically
- [Meltano Integration](MELTANO_INTEGRATION.md) - Using with Meltano
- [Examples](EXAMPLES.md) - Code examples and use cases
- [OCI Best Practices](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengbestpractices.htm)
