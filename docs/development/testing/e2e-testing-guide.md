# End-to-End Tests

This directory contains end-to-end tests for the FLX framework.

## Test Files

- `test_logging_e2e.py` - End-to-end tests for the logging system

## Purpose

E2E tests verify:

- Complete user workflows
- System behavior from external perspective
- Full stack integration
- Real-world usage scenarios
- Performance and reliability

## Testing Strategy

E2E tests simulate real usage:

- No mocking of external systems
- Complete request/response cycles
- Multi-step user journeys
- Error scenarios and recovery
- Performance benchmarks

## Running Tests

```bash
# Run all E2E tests
pytest tests/e2e/

# Run with extended timeout
pytest tests/e2e/ --timeout=300
```

## Note

E2E tests may require external services to be running. Check test documentation for specific requirements.
