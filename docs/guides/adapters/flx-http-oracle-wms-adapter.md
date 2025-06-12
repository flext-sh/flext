# FLX HTTP Oracle WMS

Modern Python client for Oracle Warehouse Management System (WMS) operations, built on the FLX framework with PEP8 compliance.

## Features

- ✅ Pure Python implementation (no shell scripts)
- ✅ PEP8 compliant code style
- ✅ Automatic `.env` file loading
- ✅ Multiple output formats (table, json, yaml, csv)
- ✅ Async/await support
- ✅ Type hints throughout
- ✅ Comprehensive error handling

## Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install package
pip install -e .

# Install with development dependencies
pip install -e .[dev]
```

## Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` with your WMS credentials:

```ini
WMS_BASE_URL=https://your-wms-endpoint.com/services
WMS_USERNAME=your_username
WMS_PASSWORD=your_password
```

## Usage

### Command Line Interface

The CLI automatically loads `.env` files and uses table output by default:

```bash
# Show help
python -m flx_http_oracle_wms --help

# Discover WMS operations
python -m flx_http_oracle_wms discover

# Test connection
python -m flx_http_oracle_wms test-connection

# Execute operation
python -m flx_http_oracle_wms execute getStockCount '{"warehouse": "WH01"}'

# Show configuration
python -m flx_http_oracle_wms show-config

# Different output formats
python -m flx_http_oracle_wms --json api-info
python -m flx_http_oracle_wms --yaml discover
python -m flx_http_oracle_wms --csv show-config
```

### Python API

```python
from flx_http_oracle_wms import WmsService, WmsConfig

# Create service from environment
config = WmsConfig.from_env()
service = WmsService(config)

# Discover operations
operations = await service.discover_operations()

# Execute operation
result = await service.execute_operation(
    "getStockCount",
    {"warehouse": "WH01"}
)
```

## Development

All development tasks are managed through Python (no shell scripts):

```bash
# Run all tasks
python tasks.py

# Install dependencies
python tasks.py install

# Run tests
python tasks.py test

# Run tests with coverage
python tasks.py coverage

# Format code
python tasks.py format

# Run linter
python tasks.py lint

# Type checking
python tasks.py type-check

# Security scan
python tasks.py security

# Clean build artifacts
python tasks.py clean

# Build package
python tasks.py build

# Run pre-commit checks
python tasks.py pre-commit

# Serve documentation
python tasks.py docs
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_client.py

# Run with coverage
python -m pytest --cov

# Run tests in parallel
python -m pytest -n auto
```

### Code Quality

The project enforces PEP8 compliance:

```bash
# Check code style
python -m ruff check src tests

# Format code
python -m ruff format src tests

# Type checking
python -m mypy src

# Security audit
python -m bandit -r src
```

## Project Structure

```
flx_http_oracle_wms/
├── src/
│   └── flx_http_oracle_wms/
│       ├── __init__.py
│       ├── __main__.py      # CLI entry point
│       ├── cli.py           # CLI implementation
│       ├── client.py        # WMS client
│       ├── config.py        # Configuration
│       ├── entities.py      # Data models
│       └── service.py       # Business logic
├── tests/
│   └── test_*.py           # Test files
├── examples/
│   └── *.py                # Usage examples
├── tasks.py                # Development tasks
├── setup.py                # Setup configuration
├── pyproject.toml          # Project configuration
├── .env.example            # Environment template
└── README.md               # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `python tasks.py pre-commit`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
