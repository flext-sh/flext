# Tests Directory

This directory contains test scripts and utilities for tap-oic development and validation.

## Files

### `test_tap_oic_complete.py`

Comprehensive test suite that validates the complete tap-oic functionality.

**Usage:**

```bash
python tests/test_tap_oic_complete.py
```

**What it tests:**

- Tap structure validation
- Import functionality
- Configuration generation from .env
- Stream discovery process
- Basic data extraction
- Authentication handling
- Error handling for test environments

**Features:**

- Uses TapOICTester class for organized testing
- Validates all required source files
- Generates configuration from environment
- Tests OAuth2 authentication flow
- Handles 401 errors gracefully in test environments
- Provides detailed test output and summaries

### `test_tap_oic.py`

Basic unit tests for tap-oic core functionality.

### `test_production.py`

Production environment testing script.

**Usage:**

```bash
python tests/test_production.py
```

**Features:**

- Tests against real Oracle OIC instances
- Validates production authentication
- Tests all stream types
- Performance monitoring
- Error handling validation

### `test_production_full.py`

Extended production testing with comprehensive coverage.

### `test_validation.py`

Configuration and input validation tests.

**Features:**

- Config schema validation
- Environment variable validation
- Authentication parameter validation
- Stream selection validation

### `debug_auth.py`

Authentication debugging and troubleshooting utility.

**Usage:**

```bash
python tests/debug_auth.py
```

**Features:**

- OAuth2 token acquisition testing
- IDCS endpoint validation
- Scope and audience debugging
- Token introspection
- Authentication error analysis

## Running Tests

### Unit Tests

```bash
# Run all unit tests
poetry run pytest tests/

# Run specific test file
poetry run pytest tests/test_tap_oic.py

# Run with coverage
poetry run pytest tests/ --cov=tap_oic
```

### Integration Tests

```bash
# Complete integration test
python tests/test_tap_oic_complete.py

# Production testing (requires valid credentials)
python tests/test_production.py
```

### Test Categories

- **Unit Tests**: Basic functionality and imports
- **Integration Tests**: End-to-end tap functionality
- **Production Tests**: Real Oracle OIC environment testing
- **Debug Tests**: Authentication and configuration troubleshooting

## Test Requirements

### Environment Setup

1. Valid `.env` file with Oracle OIC credentials
2. Poetry environment with all dependencies
3. Network access to Oracle OIC instances (for production tests)

### Credentials Required

- `OIC_IDCS_CLIENT_ID`: IDCS application client ID
- `OIC_IDCS_CLIENT_SECRET`: IDCS application client secret
- `OIC_IDCS_URL`: IDCS base URL
- `OIC_IDCS_CLIENT_AUD`: Client audience URL
- `OIC_INSTANCE_ID`: Oracle OIC instance identifier

## Test Output

Tests generate various artifacts:

- `config.json`: Generated configuration for testing
- `catalog.json`: Discovered streams catalog
- `test_catalog.json`: Modified catalog for testing
- `tap_output.json`: Sample extraction output

These files are automatically cleaned up or can be regenerated as needed.
