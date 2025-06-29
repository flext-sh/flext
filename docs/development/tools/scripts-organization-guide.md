# Scripts Organization and Management Guide

> **Comprehensive guide for script organization, development, and maintenance across the FLX framework workspace**

This guide establishes the complete framework for managing Python scripts within the FLX workspace, implementing **[Development Standards](standardization-plan.md)** and following **[Architectural Consistency](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md)** principles.

## Overview

The scripts management system provides a centralized, consistent approach to managing all scripts across multiple Python projects in the workspace. This replaces the previous fragmented approach with comprehensive Python scripts that handle all functionality through command-line interfaces.

**Related Documentation**:

- **[Implementation Summary](reports/implementation-summary.md)** - Complete implementation report
- **[Testing Strategies](TESTING_HEXAGONAL_ARCHITECTURE.md)** - Testing methodologies
- **[Documentation Standards](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md)** - Framework conventions

## 📋 Fundamental Rules

**ALL scripts must be in appropriate `scripts/` folders** - this rule applies to:

- ✅ Production scripts
- ✅ Temporary scripts
- ✅ Testing scripts
- ✅ Support scripts
- ✅ Debugging scripts
- ✅ One-off/disposable scripts
- ✅ Automation prototypes

Following **[Infrastructure Architecture](../architecture/INFRASTRUCTURE_ARCHITECTURE.md)** separation patterns.

## 📁 Mandatory Directory Structure

```
workspace/
├── scripts/                    # Workspace scripts (cross-project)
│   ├── automation/            # General automation scripts
│   ├── maintenance/           # Maintenance scripts
│   ├── deployment/            # Deployment scripts
│   ├── testing/               # Workspace testing scripts
│   ├── temp/                  # Temporary scripts (workspace)
│   └── utils/                 # Shared utilities
│
├── project/scripts/           # Project-specific scripts
│   ├── build/                 # Project build scripts
│   ├── migration/             # Migration scripts
│   ├── data/                  # Data processing scripts
│   ├── temp/                  # Project temporary scripts
│   └── test/                  # Project-specific tests
│
└── project/src/package/cli/   # CLI modules integrated into code
```

## Core Management Scripts

### 1. Project Management: `project_manage.py`

Handles core project operations following **[Development Workflow](documentation-guide.md)**:

- Environment setup (venv, Poetry)
- Dependency management
- Testing, linting, and formatting
- Project standardization
- Status reporting

```bash
# Setup the workspace
./project_manage.py setup

# Install dependencies
./project_manage.py install [--dev]

# Test all projects
./project_manage.py test

# Format code
./project_manage.py format

# Show project status
./project_manage.py status
```

### 2. Scaffold Management: `scaffold_manage.py`

Manages project templates and scaffolding:

- Updating scaffold templates from existing projects
- Syncing projects with latest scaffold
- Propagating scaffold changes to all projects
- Creating new projects from templates

```bash
# Update scaffold from a project
./scaffold_manage.py update project_name

# Sync a project with scaffold
./scaffold_manage.py sync project_name [--direction s|p|b]

# Create a new project from scaffold
./scaffold_manage.py create new_project_name
```

### 3. Git Operations: `git_manage.py`

Provides Git operations for the workspace:

- Status checking and reporting
- Committing changes
- Fetching updates and pushing changes
- Branch operations

```bash
# Show git status
./git_manage.py status

# Commit changes
./git_manage.py commit [--message "Commit message"]

# Push changes
./git_manage.py push
```

### 4. Virtual Environment Management: `setup_venv.sh`

Unified script for managing the Python virtual environment:

- Creating and rebuilding the virtual environment
- Installing dependencies via Poetry
- Verifying and fixing the environment
- Checking for necessary tools

```bash
# Create virtual environment
./setup_venv.sh create

# Install development dependencies
./setup_venv.sh install-dev

# Rebuild the environment from scratch
./setup_venv.sh rebuild

# Show environment status
./setup_venv.sh status
```

## Code Quality Utilities

### 1. Code Standards: `flext_long_lines.py`, `pep8_check.py`, `pep8_apply.py`

Tools for enforcing **[Coding Standards](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md#code-example-standards)**:

- Fixing long lines that exceed PEP 8 limits
- Checking PEP 8 compliance
- Applying PEP 8 standards automatically

```bash
# Fix long lines
./flext_long_lines.py [--max-length=88] [--check] [--aggressive]

# Check PEP 8 compliance
./pep8_check.py [project_dir]

# Apply PEP 8 standards
./pep8_apply.py [project_dir]
```

### 2. Configuration: `update_lint_excludes.py`

Configuration management tools:

- Updating lint exclusions in pyproject.toml

```bash
# Update lint exclusions
./update_lint_excludes.py --input=excludes.txt --pyproject=pyproject.toml
```

### 3. Documentation: `document_scripts.py`

Tool for documenting Python scripts following **[Documentation Standards](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md#documentation-style-standards)**:

- Checking documentation status
- Adding missing docstrings
- Generating documentation summary

```bash
# Check documentation status
./document_scripts.py --check

# Update documentation
./document_scripts.py --update

# Generate documentation summary
./document_scripts.py
```

## 🏷️ Temporary Script Naming Conventions

### ✅ Correct Naming Patterns

```bash
scripts/temp/debug_issue_123.py           # Debug specific issue
scripts/temp/test_migration_rollback.py   # Rollback testing
scripts/temp/poc_new_integration.py       # Proof of concept
scripts/temp/benchmark_performance.py     # Temporary benchmark
scripts/temp/fix_data_corruption_456.py   # Specific fix
```

### ❌ Incorrect Patterns

```bash
debug.py                    # ❌ In root
test_something.py          # ❌ In project root
/tmp/script.py            # ❌ In system /tmp
./temp_script.py          # ❌ In current directory
```

## 🚀 Creating Temporary Scripts

### 1. Use the Template

Following **[Testing Best Practices](TESTING_HEXAGONAL_ARCHITECTURE.md#testing-best-practices)**:

```bash
# Copy the template
cp scripts/utils/temp_script_template.py scripts/temp/my_debug_script.py

# Edit and customize
vim scripts/temp/my_debug_script.py
```

### 2. Standard Template Structure

```python
#!/usr/bin/env python3
"""
TEMPORARY SCRIPT - Debug problem X

Created: 2024-01-15
Author: Your Name
Purpose: Investigate performance issue in integration Y
Ticket/Issue: https://github.com/company/project/issues/123

THIS IS A TEMPORARY SCRIPT:
- Should be removed after use
- Not for production
- Created for: Specific debug of ticket #123

SCHEDULED CLEANUP: 2024-02-15
"""

import sys
from pathlib import Path
import structlog

# Mandatory location validation
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from script_validation import validate_script_location

validate_script_location()

logger = structlog.get_logger(__name__)

def main():
    """Main script logic following architectural patterns."""
    logger.info("Starting debug of problem X")

    # Your logic here
    pass

    logger.info("Debug completed")

if __name__ == "__main__":
    main()
```

## 🔧 Makefile Integration Commands

### Location Verification

```bash
# Verifies all scripts are in correct folders
make check-script-locations

# Executes all script validations
make validate-scripts
```

### Automatic Cleanup

```bash
# Removes old temporary scripts (default: 30 days)
make cleanup-temp-scripts

# Simulates cleanup (doesn't remove, just shows)
make cleanup-temp-scripts-dry

# Sets custom maximum age
make cleanup-temp-scripts MAX_AGE=7
```

## 🛡️ Automatic Validation

All scripts must include this validation at the beginning:

```python
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from script_validation import validate_script_location

# Mandatory validation - fails if not in correct folder
validate_script_location()
```

## Setup and Installation

The scripts can be set up for easy access using setup scripts:

```bash
# Run the main setup script (for core scripts)
./setup_scripts.sh
```

This will:

1. Make all Python scripts executable
2. Create symbolic links in `scripts/bin/`
3. Add the bin directory to your PATH in `.bashrc`

## Available Commands

After setup, you can use these commands from anywhere in the workspace:

### Core Commands

- `project-manage` - Manage projects
- `scaffold-manage` - Manage scaffolds
- `git-manage` - Git operations
- `setup-venv` - Manage virtual environment
- `setup` - Setup the workspace
- `status` - Show project status
- `scaffold` - Manage scaffolds (shorthand)
- `git-op` - Git operations (shorthand)

### Utility Commands

- `fix-longlines` - Fix long lines in Python files
- `update-packages` - Update packages in virtualenv
- `update-lint-excludes` - Update lint excludes in pyproject.toml
- `pep8-check` - Check PEP 8 compliance
- `pep8-apply` - Apply PEP 8 standards
- `document-scripts` - Document Python scripts

## 📊 Script Categories

### Workspace Level (`scripts/`)

- **automation/**: General automation between projects
- **maintenance/**: Workspace maintenance
- **deployment/**: Deploy and CI/CD
- **testing/**: Workspace integration testing
- **temp/**: Workspace temporary scripts
- **utils/**: Shared utilities

### Project Level (`project/scripts/`)

- **build/**: Project-specific build scripts
- **migration/**: Data/schema migrations
- **data/**: Project data processing
- **temp/**: Project temporary scripts
- **test/**: Project-specific tests

## 🧹 Automatic Cleanup

Scripts in `temp/` folders are automatically cleaned after 30 days by default.

### Manual Control

```python
# In temporary script header, specify:
"""
SCHEDULED CLEANUP: 2024-02-15
"""

# The cleanup script will respect this date
```

### Automatic Execution

Cleanup can be scheduled via cron:

```bash
# Run cleanup daily at 3 AM
0 3 * * * cd /path/to/workspace && make cleanup-temp-scripts
```

## Benefits of the New Structure

1. **Simplified Makefile**: Root Makefile is much simpler, just calling these scripts
2. **Consistent Paths**: All scripts use absolute paths, preventing path-related issues
3. **Better Error Handling**: Python scripts provide improved error handling and logging
4. **Extensibility**: Easier to add new features as workspace grows
5. **Reduced Duplication**: Common functions consolidated instead of duplicated
6. **Standardized Documentation**: All scripts properly documented with consistent docstrings
7. **Convenient Access**: All scripts available as commands in PATH
8. **Architectural Compliance**: Follows **[Hexagonal Architecture](../architecture/INFRASTRUCTURE_ARCHITECTURE.md)** principles

## ⚠️ Important Warnings

1. **Never** create scripts in project or workspace root
2. **Always** use location validation
3. **Document** the purpose of temporary scripts
4. **Remove** scripts after use or leave for automatic cleanup
5. **Use** descriptive naming that indicates purpose
6. **Follow** **[Error Handling Standards](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md#error-handling-standards)**

## 🔍 Troubleshooting

### Location Error

```bash
ERROR: Script must be in a 'scripts/' folder
Current location: /workspace/my_script.py
Move to: /workspace/scripts/ or /workspace/project/scripts/
```

**Solution**: Move script to a valid `scripts/` folder.

### Script Not Found

If validation script cannot import `script_validation`:

```python
# Adjust path as needed
sys.path.append(str(Path(__file__).parent.parent / "utils"))
# or
sys.path.append(str(Path(__file__).parent / ".." / ".." / "scripts" / "utils"))
```

### Cleanup Not Working

Check if script has correct permissions:

```bash
chmod +x scripts/maintenance/cleanup_temp_scripts.py
```

## 📚 Practical Examples

### Performance Debug

```python
# scripts/temp/debug_slow_query_issue_456.py
"""Debug slow query - Issue #456"""

def main():
    """Investigate performance issues."""
    # Code to investigate performance
    pass
```

### Migration Test

```python
# project/scripts/temp/test_migration_rollback_v2.py
"""Test rollback of migration v2"""

def main():
    """Test migration rollback procedures."""
    # Code to test rollback
    pass
```

### Integration POC

```python
# scripts/temp/poc_new_api_integration.py
"""POC for new external API integration"""

def main():
    """Proof of concept implementation."""
    # Proof of concept code
    pass
```

## Directory Structure Reference

```
/home/marlonsc/pyauto/scripts/
├── bin/                       # Symbolic links for easy access
│   ├── project-manage         -> ../project_manage.py
│   ├── scaffold-manage        -> ../scaffold_manage.py
│   ├── git-manage             -> ../git_manage.py
│   ├── setup                  # Wrapper for project_manage.py setup
│   ├── status                 # Wrapper for project_manage.py status
│   ├── scaffold               # Wrapper for scaffold_manage.py
│   ├── git-op                 # Wrapper for git_manage.py
│   ├── fix-longlines          # Wrapper for fix_long_lines.py
│   └── ...                    # Other utility wrappers
├── project_manage.py          # Project management operations
├── scaffold_manage.py         # Scaffold & template management
├── git_manage.py              # Git operations
├── flext_long_lines.py          # Fix long lines in Python files
├── update_packages.py         # Update or reinstall packages
├── update_lint_excludes.py    # Update lint exclusions
├── pep8_check.py              # Check PEP 8 compliance
├── pep8_apply.py              # Apply PEP 8 standards
├── document_scripts.py        # Document Python scripts
├── setup_scripts.sh           # Setup for core scripts
├── create_utility_wrappers.sh # Setup for utility scripts
└── SCRIPTS_SUMMARY.md         # Generated summary of all scripts
```

## Maintenance

To add new functionality:

1. Extend the appropriate Python script
2. Add a new target to the Makefile if needed, just calling the Python script
3. Add a wrapper in `scripts/bin/` for easy command-line access
4. Document the new functionality following **[Documentation Standards](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md)**
5. Update this guide with new patterns

## Cross-References

### Related Documentation

- **[Implementation Summary](reports/implementation-summary.md)** - Complete implementation details
- **[Testing Strategies](TESTING_HEXAGONAL_ARCHITECTURE.md)** - Testing methodologies and patterns
- **[Development Standards](standardization-plan.md)** - Overall development approach
- **[Architectural Consistency](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md)** - Framework standards

### Configuration Files

- **Script Rules**: `.cursor/rules/scripts.mdc`
- **Validation Utils**: `scripts/utils/script_validation.py`
- **Cleanup System**: `scripts/maintenance/cleanup_temp_scripts.py`
- **Template**: `scripts/utils/temp_script_template.py`

### Integration Points

- **Makefile Integration**: Root workspace Makefile
- **Development Workflow**: Integration with **[Development Guide](documentation-guide.md)**
- **Quality Assurance**: Follows **[Testing Best Practices](TESTING_HEXAGONAL_ARCHITECTURE.md#testing-best-practices)**

---

For more information, consult:

- **[Implementation Summary](reports/implementation-summary.md)** - Complete implementation report
- **[Documentation Standards](../architecture/ARCHITECTURAL_CONSISTENCY_GUIDE.md)** - Framework conventions
- **[Testing Strategies](TESTING_HEXAGONAL_ARCHITECTURE.md)** - Testing methodologies

_This guide provides comprehensive coverage of script organization and management within the FLX framework workspace, ensuring consistency and maintainability across all development activities._
