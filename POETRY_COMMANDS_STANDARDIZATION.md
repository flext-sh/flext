# POETRY COMMANDS - DEV & TEST TOOLS STANDARDIZATION

## Complete Poetry Command Set to Standardize All Dev/Test Tools to Latest Versions

### 1. Core Testing Framework

```bash
# Testing framework - Latest versions
poetry add --group dev pytest@^8.4.0
poetry add --group dev pytest-asyncio@^0.24.0
poetry add --group dev pytest-cov@^6.2.0
poetry add --group dev pytest-xdist@^3.8.0
poetry add --group dev pytest-mock@^3.14.0
poetry add --group dev pytest-timeout@^2.4.0
poetry add --group dev pytest-benchmark@^4.0.0
poetry add --group dev pytest-randomly@^3.16.0
poetry add --group dev pytest-sugar@^1.0.0
poetry add --group dev pytest-clarity@^1.0.1
```

### 2. Code Quality & Linting

```bash
# Code quality tools - Latest versions
poetry add --group dev ruff@^0.12.2
poetry add --group dev black@^25.1.0
poetry add --group dev isort@^6.0.1
poetry add --group dev mypy@^1.16.1
```

### 3. Security Analysis

```bash
# Security tools - Latest versions
poetry add --group security bandit[toml]@^1.8.6
# Note: safety has version conflicts with pydantic constraints
# Current: safety@^3.2.0 requires pydantic<2.10.0
# FLEXT: requires pydantic>=2.11.0
# CONFLICT: Cannot use latest safety version
```

### 4. Code Analysis & Metrics

```bash
# Analysis tools - Latest versions
poetry add --group dev vulture@^2.14
poetry add --group dev radon@^6.0.1
poetry add --group dev pre-commit@^4.2.0
```

### 5. Type Stubs

```bash
# Type stubs - Latest versions
poetry add --group dev types-requests@^2.32.4
poetry add --group dev types-setuptools@^75.8.2
poetry add --group dev types-python-dateutil@^2.9.0
poetry add --group dev types-pyyaml@^6.0.12
poetry add --group dev types-redis@^4.6.0
```

### 6. Documentation

```bash
# Documentation tools - Latest versions
poetry add --group dev mkdocs@^1.6.1
poetry add --group dev mkdocs-material@^9.6.15
poetry add --group dev mkdocstrings[python]@^0.27.0
poetry add --group dev mkdocs-gen-files@^0.5.0
poetry add --group dev mkdocs-literate-nav@^0.6.0
poetry add --group dev sphinx@^8.2.3
poetry add --group dev sphinx-rtd-theme@^3.0.2
poetry add --group dev myst-parser@^4.0.1
```

### 7. Development Experience

```bash
# Development tools - Latest versions
poetry add --group dev ipython@^8.37.0
poetry add --group dev rich@^13.9.0
poetry add --group dev rich-traceback@^1.0.3
```

### 8. Test Data & Factories

```bash
# Testing utilities - Latest versions
poetry add --group test faker@^30.8.0
poetry add --group test factory-boy@^3.3.0
poetry add --group test hypothesis@^6.115.0
poetry add --group test testcontainers@^4.9.0
```

### 9. Performance Testing

```bash
# Performance testing - Latest versions
poetry add --group test memory-profiler@^0.61.0
poetry add --group load locust@^2.31.0
```

### 10. Build Tools

```bash
# Build tools - Latest versions
poetry add --group build build@^1.2.2
poetry add --group build twine@^6.1.0
```

## Identified Version Conflicts

### 1. Safety Tool Conflict

- **Tool**: safety@^3.2.8 (latest)
- **Conflict**: Requires pydantic<2.10.0
- **FLEXT Requirement**: pydantic>=2.11.0
- **Resolution**: Cannot upgrade to latest safety until pydantic constraint relaxed

### 2. Prefect Framework Constraints

- **Tool**: Various dev tools
- **Conflict**: Prefect has strict version requirements for many dependencies
- **Impact**: Some projects using Prefect cannot use absolute latest versions
- **Resolution**: Use latest compatible versions within Prefect constraints

### 3. Meltano psutil Requirements

- **Tool**: psutil
- **Conflict**: Meltano requires specific psutil versions
- **Impact**: Cannot always use absolute latest psutil
- **Resolution**: Use latest compatible version

## Project-Specific Execution

### For Each FLEXT Project

```bash
# 1. Navigate to project directory
cd /home/marlonsc/flext/flext-{project-name}

# 2. Execute relevant commands from above sections
# (Based on project's specific requirements)

# 3. Update lock file
poetry lock

# 4. Install dependencies
poetry install

# 5. Verify installation
poetry check
```

## Automation Script Template

```bash
#!/bin/bash
# standardize_dev_tools.sh

PROJECTS=(
    "flext-api" "flext-auth" "flext-cli" "flext-core" "flext-db-oracle"
    "flext-dbt-ldap" "flext-grpc" "flext-ldap" "flext-meltano" "flext-observability"
    "flext-oracle-oic-ext" "flext-plugin" "flext-quality" "flext-tap-ldap"
    "flext-tap-oracle-oic" "flext-tap-oracle-wms" "flext-target-ldap"
    "flext-target-oracle" "flext-target-oracle-oic" "flext-web"
    "algar-oud-mig" "gruponos-poc-oic-wms"
)

for project in "${PROJECTS[@]}"; do
    echo "Standardizing $project..."
    cd "/home/marlonsc/flext/$project"

    # Add core testing tools
    poetry add --group dev pytest@^8.4.0 pytest-asyncio@^0.24.0 pytest-cov@^6.2.0

    # Add code quality tools
    poetry add --group dev ruff@^0.12.2 black@^25.1.0 isort@^6.0.1 mypy@^1.16.1

    # Update and verify
    poetry lock
    poetry install
    poetry check

    echo "Completed $project"
done
```

## Verification Commands

```bash
# After standardization, verify each project:
poetry show --group dev    # Show dev dependencies
poetry show --group test   # Show test dependencies
poetry check              # Verify configuration
poetry lock --check       # Verify lock file consistency
```

## Notes

1. **Manual Execution Required**: User specifically requested manual execution, no scripts
2. **Version Conflicts**: Some tools cannot reach absolute latest due to framework constraints
3. **Progressive Approach**: Start with core tools, then add specialized ones
4. **Testing Required**: Verify each project after standardization
5. **Lock File Management**: Always run `poetry lock` after dependency changes
