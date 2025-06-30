# Dependency Synchronization Guide

> **Cross-References:**
>
> - [Development Standards](standardization-plan.md) - Code standards and tool configuration
> - [Scripts Organization](scripts-organization-guide.md) - Development scripts overview
> - [Installation Guide](../getting-started/installation.md) - Environment setup requirements

## Overview

This guide describes the comprehensive dependency synchronization system for maintaining consistent library versions across all projects in the FLEXT hexagonal architecture workspace.

## Objective

The script was created to solve the problem of inconsistent library versions between different projects in the workspace, which can cause issues such as:

- Library incompatibilities
- Difficulty keeping all projects updated
- Unexpected behaviors due to different versions of the same library

## How It Works

The `sync_dependencies.py` script can operate in two modes:

### 1. Standard Mode

In this mode, the script:

1. Reads the `pyproject.toml` file from the source project (default: `dc-api-x`)
2. Extracts all dependencies and their versions
3. Finds all `pyproject.toml` and `requirements.txt` files in all workspace projects
4. Updates library versions in found files to match those from the source project

### 2. Consolidation Mode

In this mode, the script:

1. Finds all `pyproject.toml` and `requirements.txt` files in all workspace projects
2. Extracts all dependencies and their versions from all projects
3. For each dependency, identifies the most recent version among all projects
4. Updates all projects to use the most recent version of each dependency

This mode is useful to ensure all projects are using the most recent versions available in the workspace.

## Usage

To run the script, simply execute:

```bash
python sync_dependencies.py [options]
```

### Available Options

- `--force`, `-f`: Forces update of all dependencies, even when versions are equal
- `--flext_project NAME`, `-p NAME`: Updates only a specific project (directory name)
- `--dry-run`, `-d`: Runs in simulation mode without making real changes
- `--consolidate`, `-c`: Activates consolidation mode (uses most recent versions from all projects)
- `--source NAME`, `-s NAME`: Specifies the source project for versions (default: dc-api-x)

### Examples

```bash
# Standard mode: uses dc-api-x as source
python sync_dependencies.py

# Consolidation mode: uses most recent versions from all projects
python sync_dependencies.py --consolidate

# Force update of all dependencies
python sync_dependencies.py --force

# Use another project as source
python sync_dependencies.py --source dc-oracle-wms

# Update only a specific project
python sync_dependencies.py --flext_project dc-oracle-wms

# Simulate update without making changes
python sync_dependencies.py --dry-run
```

The script will display information about:

- Dependencies found in source project or most recent versions collected
- Which files were found for updating
- Which dependencies were updated in each file
- Success or error confirmation for each processed file

## Supported Formats

The script supports the following dependency file formats:

1. **pyproject.toml** with Poetry format:

   ```toml
   [tool.poetry.dependencies]
   requests = "^2.32.3"
   ```

2. **pyproject.toml** with PEP 621 format:

   ```toml
   [project.dependencies]
   requests = "^2.32.3"
   ```

3. **requirements.txt**:

   ```
   requests>=2.32.3
   ```

## Makefile Integration

The script is integrated with the workspace Makefile, allowing execution through the command:

```bash
make sync-dependencies
```

To force update of all dependencies:

```bash
make sync-dependencies FORCE=true
```

To use consolidation mode:

```bash
make sync-dependencies CONSOLIDATE=true
```

To update only a specific project:

```bash
make sync-dependencies PROJECT=project-name
```

To use another project as source:

```bash
make sync-dependencies SOURCE=project-name
```

## Maintenance

To keep all projects with consistent versions:

1. Run the script in consolidation mode to ensure all projects are using the most recent versions
2. Verify that all projects continue working correctly after synchronization
3. Run the script periodically to maintain synchronization

## Notes

- The script doesn't add new dependencies to projects, only updates versions of existing dependencies
- Python version (`python = "^3.10"`) is not synchronized to avoid compatibility issues
- Dependencies with specific requirements (like extras) maintain their configurations, only the version is updated
- In consolidation mode, the algorithm tries to determine which is the most recent version, but there may be cases where comparison is not trivial

## Integration with FLEXT Framework

This dependency synchronization is particularly important for the FLEXT framework workspace because:

### **Multi-Project Architecture**

The FLEXT workspace contains multiple related projects:

- `flext/` - Core FLEXT framework
- `flext_http_oracle_oic/` - Oracle OIC integration
- `flext_http_oracle_wms/` - Oracle WMS integration
- `flext_database_oracle/` - Oracle database integration
- And many more...

### **Hexagonal Architecture Dependencies**

Each project in the workspace implements hexagonal architecture patterns and needs:

- Consistent versions of infrastructure libraries (HTTP clients, database adapters)
- Compatible versions of domain libraries (Pydantic, validation)
- Aligned versions of testing frameworks (pytest, coverage)

### **Example Workflow**

```bash
# 1. Sync all projects to latest versions
make sync-dependencies CONSOLIDATE=true

# 2. Verify the core framework works
cd flext && make test

# 3. Verify Oracle integrations work
cd flext-http-oracle-oic && make test
cd flext-http-oracle-wms && make test

# 4. Check for any compatibility issues
make test-all
```

### **Critical Dependencies**

The synchronization pays special attention to:

- **pydantic**: Core to all domain models
- **httpx**: HTTP client infrastructure
- **pytest**: Testing framework
- **mypy**: Type checking
- **ruff**: Code linting

## Related Documentation

- [Development Standardization Plan](standardization-plan.md) - Overall development standards
- [Scripts Organization Guide](scripts-organization-guide.md) - Development scripts overview
- [FLEXT Core API Reference](../api-reference/core-api-reference.md) - Framework dependencies

---

**Implementation Status**: ✅ Current and Active  
**Script Location**: `/scripts/sync_dependencies.py`  
**Last Updated**: January 2025  
**Maintained By**: FLEXT Development Team

---

This dependency synchronization is essential for maintaining the integrity of the FLEXT hexagonal architecture across all Oracle integration projects.
