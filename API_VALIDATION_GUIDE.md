# FLEXT API Validation Guide

## 🚀 API Testing and Validation

This guide provides comprehensive instructions for testing and validating the FLEXT API endpoints.

### Quick Start

```bash
# Make script executable
chmod +x validate_api.sh

# Run complete validation
./validate_api.sh
```

### API Endpoints Tested

#### 1. Health Check

- **Endpoint**: `GET /health`
- **Purpose**: Verify server is running
- **Expected**: `{"status": "ok"}`

#### 2. Root Endpoint

- **Endpoint**: `GET /`
- **Purpose**: API information and available endpoints
- **Expected**: JSON with API metadata

#### 3. Pipeline Management

- **Create**: `POST /api/v1/pipelines`
- **List**: `GET /api/v1/pipelines`
- **Get**: `GET /api/v1/pipelines/{id}`
- **Add Step**: `POST /api/v1/pipelines/{id}/steps`

#### 4. Plugin Management

- **Register**: `POST /api/v1/plugins`
- **List**: `GET /api/v1/plugins`
- **Get**: `GET /api/v1/plugins/{id}`

### Sample Requests

#### Create Pipeline

```json
{
  "name": "Pipeline de Teste",
  "description": "Pipeline para validação da API",
  "tags": ["test", "validation"]
}
```

#### Register Plugin

```json
{
  "name": "Plugin de Teste",
  "type": "source",
  "version": "1.0.0",
  "description": "Plugin para validação da API",
  "author": "FLEXT Team",
  "entry_point": "/usr/bin/test-plugin",
  "ports": [
    {
      "name": "input",
      "type": "source",
      "required": true,
      "description": "Porta de entrada"
    }
  ]
}
```

### Prerequisites

- `curl` command line tool
- `jq` for JSON formatting
- FLEXT binary compiled and executable

### Troubleshooting

#### Server Not Starting

```bash
# Check if port 8081 is available
lsof -i :8081

# Kill existing processes if needed
pkill -f flext
```

#### Dependencies Missing

```bash
# Install jq on Ubuntu/Debian
sudo apt-get install jq

# Install jq on macOS
brew install jq
```

### Manual Testing

You can also test endpoints manually:

```bash
# Start server
./flext &

# Test health
curl http://localhost:8081/health

# Test root
curl http://localhost:8081/

# Create pipeline
curl -X POST http://localhost:8081/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Pipeline", "description": "Test"}'
```

### Expected Validation Results

The validation script should complete all 10 tests successfully:

1. ✅ Health Check responds
2. ✅ Root endpoint provides API info
3. ✅ Pipeline creation returns valid ID
4. ✅ Plugin registration returns valid ID
5. ✅ Pipeline listing includes created pipeline
6. ✅ Plugin listing includes registered plugin
7. ✅ Pipeline retrieval by ID works
8. ✅ Plugin retrieval by ID works
9. ✅ Pipeline step addition works
10. ✅ Updated pipeline includes new step

All responses should be valid JSON with proper status codes (200/201).
