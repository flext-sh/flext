# FLEXT DBT Oracle Adapter

Modern Oracle Database adapter for DBT using flext-db-oracle foundation.

## Features

- Enterprise-grade Oracle Database connectivity
- Modern DBT adapter patterns
- Zero code duplication with FLEXT ecosystem
- Comprehensive error handling and logging
- Full type safety with Python 3.13

## Configuration

Configure your `profiles.yml`:

```yaml
oracle_db:
  target: dev
  outputs:
    dev:
      type: oracle
      host: your-oracle-host
      port: 1521
      username: your-username
      password: your-password
      service_name: your-service
      schema: your-schema
```

## Installation

```bash
poetry install
```

## Quality Checks

```bash
make check  # Run all quality gates
make lint   # Linting only
make test   # Testing only
```
