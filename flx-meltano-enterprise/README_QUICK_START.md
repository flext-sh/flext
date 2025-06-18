# FLX-Meltano Enterprise - Quick Start Guide

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install basic dependencies
pip install -r requirements-basic.txt

# Copy environment file
cp .env.example .env
```

### 2. Run Basic Tests

```bash
# Test imports and configuration
python test_basic.py

# Run interactive demo
python demo.py
```

### 3. Test Individual Components

#### CLI Test
```bash
# Test CLI functionality
python test_cli_simple.py --help
python test_cli_simple.py status
python test_cli_simple.py list
```

#### API Test
```bash
# Start test API server
python test_api_simple.py

# In another terminal:
curl http://localhost:8001/health
# Visit http://localhost:8001/docs for interactive API docs
```

## 📁 Project Structure

```
flx-meltano-enterprise/
├── src/
│   ├── flx/                 # Core daemon with gRPC
│   ├── flx_web/            # Django web interface
│   ├── flx_api/            # FastAPI REST API
│   ├── flx_cli/            # Click CLI
│   └── flx_extensions/     # Meltano extensions
├── tests/                  # Test suite
├── helm/                   # Kubernetes charts
├── deploy/                 # Deployment configs
├── test_basic.py          # Basic import test
├── test_cli_simple.py     # Simple CLI demo
├── test_api_simple.py     # Simple API demo
└── demo.py                # Interactive demo

```

## 🛠 Development

### Running Services

Each service can be run independently:

```bash
# Core daemon (when fully implemented)
make daemon

# Django web (when database is setup)
make web

# FastAPI
make api
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check
```

## 🔧 Full Installation (with Poetry)

For complete installation with all dependencies:

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install all dependencies
poetry install

# Run with Poetry
poetry run python test_basic.py
```

## 📊 Current Status

✅ **Working:**
- Basic project structure
- Core module imports
- Configuration system
- Simple CLI demo
- Simple API demo
- Docker configurations
- Kubernetes Helm charts

⚠️ **Requires Setup:**
- PostgreSQL database
- Redis cache
- Django migrations
- gRPC protobuf compilation
- Full daemon implementation

## 🎯 Next Steps

1. **Database Setup**: Start PostgreSQL and run migrations
2. **Start Services**: Run daemon, web, and API services
3. **Test Integration**: Verify all components work together
4. **Deploy**: Use Docker or Kubernetes for deployment

## 🐛 Troubleshooting

### Import Errors
Make sure you're in the virtual environment:
```bash
source .venv/bin/activate
```

### Database Connection
Start PostgreSQL with Docker:
```bash
docker run -d --name flx-postgres \
  -e POSTGRES_USER=flx \
  -e POSTGRES_PASSWORD=flx_secret \
  -e POSTGRES_DB=flx \
  -p 5432:5432 \
  postgres:16-alpine
```

### Port Conflicts
Default ports:
- gRPC: 50051
- Django: 8000
- FastAPI: 8001
- PostgreSQL: 5432
- Redis: 6379

Change in `.env` if needed.

## 📚 Documentation

See `IMPLEMENTATION_SUMMARY.md` for detailed architecture and design decisions.

---

**Note**: This is a demonstration of the FLX-Meltano Enterprise platform architecture. Some features require additional setup and configuration.
