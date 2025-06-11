# PyAuto Scripts Overview

## Executive Summary

This document provides a comprehensive overview of automation scripts in the pyauto workspace, designed to streamline development workflows, maintain code quality, and manage project dependencies.

## Related Documentation

- [Development Workflow](./development-workflow.md) - Overall development processes
- [Dependency Synchronization](./dependency-synchronization.md) - Dependency management
- [Code Quality Standards](./code-quality-standards.md) - Quality enforcement

## Script Categories

### 📋 Code Quality & Formatting

#### `pep8_check.py`

**PEP 8 Compliance Checker**

Validates Python code files against PEP 8 standards through:

1. Formatting validation with Black
2. Import sorting validation with isort
3. Code linting with Ruff

```bash
python scripts/pep8_check.py [file_or_directory]
```

#### `pep8_apply.py`

**PEP 8 Compliance Formatter**

Automatically applies PEP 8 standards to Python code files:

1. Code formatting with Black
2. Import sorting with isort
3. Automatic issue fixing with Ruff

```bash
python scripts/pep8_apply.py [file_or_directory]
```

#### `fix_long_lines.py`

**Long Line Formatter**

Automatically detects and fixes lines exceeding maximum length by:

- Breaking long lines into multiple lines
- Using various formatting strategies
- Maintaining code readability

```bash
python scripts/fix_long_lines.py [file]
```

#### `update_lint_excludes.py`

**Lint Configuration Manager**

Updates `pyproject.toml` with exclusions for problematic files:

- Reads files with long line issues (E501)
- Updates per-file-ignores section
- Manages linting exceptions

```bash
python scripts/update_lint_excludes.py
```

### 📚 Documentation Management

#### `document_scripts.py`

**Script Documentation Generator**

Generates or improves documentation for Python scripts:

- Scans Python files for analysis
- Analyzes script content and purpose
- Adds or enhances docstrings automatically

```bash
python scripts/document_scripts.py [directory]
```

### 🔧 Project Management

#### `project_manage.py`

**Project Management Script**

Provides consolidated functionality for managing multiple Python projects:

- Project creation and initialization
- Cross-project operations
- Workspace management utilities

```bash
python scripts/project_manage.py [command] [options]
```

#### `scaffold_manage.py`

**Scaffold Management Script**

Manages FLX project templates and scaffolds:

- Template creation and management
- Project scaffolding
- Boilerplate generation

```bash
python scripts/scaffold_manage.py [template] [target]
```

#### `git_manage.py`

**Git Management Script**

Provides Git operations for the pyauto workspace:

- Automated commit workflows
- Branch management
- Repository maintenance

```bash
python scripts/git_manage.py [git_command] [options]
```

### 🌍 Environment Management

#### `setup_venv.sh`

**Virtual Environment Management**

Unified script for Python virtual environment management:

- Environment creation and verification
- Dependency installation
- Environment activation

```bash
bash scripts/setup_venv.sh [create|verify|install]
```

## Script Integration

### Makefile Integration

Most scripts are integrated with the main Makefile:

```bash
# Code quality
make lint                    # Run pep8_check.py
make format                  # Run pep8_apply.py
make fix-long-lines         # Run fix_long_lines.py

# Project management
make create-project         # Use scaffold_manage.py
make sync-dependencies      # Use dependency sync

# Environment
make setup-env              # Use setup_venv.sh
```

### CI/CD Integration

Scripts are designed for CI/CD pipeline integration:

```yaml
# Example GitHub Actions integration
- name: Check code quality
  run: python scripts/pep8_check.py src/

- name: Validate documentation
  run: python scripts/document_scripts.py --check

- name: Verify environment
  run: bash scripts/setup_venv.sh verify
```

## Usage Patterns

### Development Workflow

**Pre-commit checks:**

```bash
# Check code quality before commit
python scripts/pep8_check.py .
python scripts/fix_long_lines.py --check
```

**Code formatting:**

```bash
# Format code before pull request
python scripts/pep8_apply.py src/
python scripts/fix_long_lines.py src/
```

**Documentation updates:**

```bash
# Update script documentation
python scripts/document_scripts.py scripts/
```

### Project Maintenance

**New project setup:**

```bash
# Create new project from template
python scripts/scaffold_manage.py create new-project

# Setup environment
bash scripts/setup_venv.sh create
```

**Workspace maintenance:**

```bash
# Manage multiple projects
python scripts/project_manage.py status
python scripts/project_manage.py update-all
```

## Configuration

### Script Configuration Files

**pyproject.toml integration:**

```toml
[tool.ruff]
# Configuration managed by update_lint_excludes.py
per-file-ignores = {}

[tool.black]
# Configuration for pep8_apply.py
line-length = 88
```

**Environment variables:**

```bash
# Common script configuration
export PYAUTO_WORKSPACE=/path/to/pyauto
export PYAUTO_VENV_PATH=.venv
export PYAUTO_PYTHON_VERSION=3.13
```

### Custom Configuration

Scripts support configuration through:

- Command-line arguments
- Environment variables
- Configuration files (pyproject.toml, .env)
- Makefile variables

## Best Practices

### Script Usage

**Do's ✅**

- Run scripts from workspace root
- Use dry-run mode when available
- Check script help: `python script.py --help`
- Integrate with Makefile commands
- Use in CI/CD pipelines

**Don'ts ❌**

- Don't run destructive scripts without backup
- Don't ignore script warnings
- Don't modify scripts without testing
- Don't bypass code quality checks

### Development

**Script Development Guidelines:**

- Add comprehensive docstrings
- Include --help and --dry-run options
- Support configuration via environment variables
- Provide clear error messages
- Include logging for debugging

## Troubleshooting

### Common Issues

**Permission errors:**

```bash
chmod +x scripts/*.sh
```

**Virtual environment issues:**

```bash
bash scripts/setup_venv.sh create
source .venv/bin/activate
```

**Script import errors:**

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Debugging

**Enable verbose output:**

```bash
python scripts/script_name.py --verbose
```

**Check script dependencies:**

```bash
python scripts/script_name.py --check-deps
```

## Script Maintenance

### Regular Tasks

**Weekly:**

- Update script documentation
- Check for broken scripts
- Verify CI/CD integration

**Monthly:**

- Review script performance
- Update script dependencies
- Optimize slow-running scripts

**Quarterly:**

- Audit script security
- Update script templates
- Review script architecture

### Quality Assurance

**Script Testing:**

```bash
# Test script functionality
python -m pytest tests/scripts/

# Test script integration
make test-scripts
```

**Performance Monitoring:**

```bash
# Profile script performance
python -m cProfile scripts/script_name.py
```

## Future Enhancements

### Planned Improvements

- Enhanced error handling and recovery
- Better integration with IDEs
- Automated script testing
- Performance optimization
- Security hardening

### Integration Opportunities

- VS Code extension integration
- GitHub Actions marketplace
- Docker container support
- Cloud deployment automation

## See Also

- [Development Environment Setup](./development-environment.md) - Environment configuration
- [Code Quality Guidelines](./code-quality-standards.md) - Quality standards
- [Testing Strategy](./testing-strategy.md) - Testing automation
- [CI/CD Pipeline](./cicd-pipeline.md) - Continuous integration

---

**Last Updated**: January 2025  
**Status**: Production Ready  
**Location**: `scripts/`  
**Integration**: Makefile, CI/CD, Development Workflow
