# Scripts Automation and Organization Guide

> **Cross-References:**
>
> - [Development Standards](./standardization-plan.md) - Code quality and PEP8 standards
> - [Dependency Synchronization Guide](./dependency-synchronization-guide.md) - Package management
> - [Task Completion Report](./task-completion-report.md) - Progress tracking

## Overview

This guide covers the comprehensive script organization and automation capabilities in the PyAuto workspace. All scripts have been organized with command wrappers, documentation, and automation features.

## Script Organization Structure

### Directory Layout

```
/home/marlonsc/pyauto/scripts/
├── bin/                           # Symbolic links for easy access
│   ├── flx_project-manage        # → ../project_manage.py
│   ├── scaffold-manage           # → ../scaffold_manage.py
│   ├── git-manage               # → ../git_manage.py
│   ├── setup                    # Wrapper for project_manage.py setup
│   ├── status                   # Wrapper for project_manage.py status
│   ├── scaffold                 # Wrapper for scaffold_manage.py
│   ├── git-op                   # Wrapper for git_manage.py
│   ├── fix-longlines           # Wrapper for fix_long_lines.py
│   ├── update-packages         # Wrapper for update_packages.py
│   ├── document-scripts        # Wrapper for document_scripts.py
│   └── ...                     # Other utility wrappers
├── project_manage.py            # Project management operations
├── scaffold_manage.py           # Scaffold & template management
├── git_manage.py               # Git operations
├── fix_long_lines.py           # Fix long lines in Python files
├── update_packages.py          # Update or reinstall packages
├── update_lint_excludes.py     # Update lint exclusions
├── pep8_check.py              # Check PEP8 compliance
├── pep8_apply.py              # Apply PEP8 standards
├── document_scripts.py         # Document Python scripts
├── setup_scripts.sh           # Setup for core scripts
├── create_utility_wrappers.sh # Setup for utility scripts
├── README.md                  # Documentation for scripts directory
└── SCRIPTS_SUMMARY.md         # Generated summary of all scripts
```

## Available Commands

After sourcing `~/.bashrc`, you can use the following commands from anywhere in the workspace:

### Core Project Management Commands

#### `flx_project-manage` - Project Management Operations

```bash
# Project setup and management
flx_project-manage setup          # Complete workspace setup
flx_project-manage status         # Show project status
flx_project-manage build          # Build all projects
flx_project-manage test           # Run all tests
flx_project-manage clean          # Clean build artifacts
```

#### `scaffold-manage` - Template and Scaffold Management

```bash
# Scaffold operations
scaffold-manage create <name>     # Create new scaffold
scaffold-manage list              # List available scaffolds
scaffold-manage update <name>     # Update existing scaffold
scaffold                         # Shorthand command
```

#### `git-manage` - Git Operations

```bash
# Git workflow automation
git-manage status                 # Enhanced git status
git-manage sync                   # Sync with remote
git-manage cleanup                # Clean up branches
git-op                           # Shorthand command
```

### Development Utility Commands

#### `fix-longlines` - Code Formatting

```bash
# Fix long lines in Python files
fix-longlines src/               # Fix long lines in directory
fix-longlines --check           # Check without fixing
fix-longlines --max-length 88   # Custom line length
```

#### `update-packages` - Package Management

```bash
# Package management
update-packages                  # Update all packages
update-packages --project flx    # Update specific project
update-packages --dev           # Update dev dependencies only
```

#### `document-scripts` - Script Documentation

```bash
# Script documentation automation
document-scripts                 # Document all scripts
document-scripts --check        # Check documentation status
document-scripts --update       # Update existing docstrings
```

#### `pep8-check` - Code Quality

```bash
# PEP8 compliance checking
pep8-check src/                 # Check PEP8 compliance
pep8-check --fix               # Apply automatic fixes
pep8-check --report            # Generate compliance report
```

### Quick Access Commands

#### `setup` - Quick Workspace Setup

```bash
setup                          # Complete workspace setup
```

#### `status` - Project Status

```bash
status                         # Show project status
```

## Script Features

### 1. Automatic Documentation

All scripts include comprehensive docstrings and help systems:

```python
def main():
    """
    Main script function with detailed documentation.

    Features:
    - Automatic help generation
    - Command validation
    - Error handling
    - Progress reporting
    """
    pass
```

### 2. Command Wrappers

Each script has a corresponding wrapper in `bin/` for easy access:

```bash
#!/bin/bash
# Wrapper for fix_long_lines.py
exec python "$(dirname "$0")/../fix_long_lines.py" "$@"
```

### 3. Error Handling and Logging

All scripts implement consistent error handling:

```python
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_operation(func):
    """Decorator for safe script operations."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Operation failed: {e}")
            return False
    return wrapper
```

## Setup and Installation

### Initial Setup

1. **Execute setup script:**

   ```bash
   cd /home/marlonsc/pyauto/scripts
   ./setup_scripts.sh
   ```

2. **Create utility wrappers:**

   ```bash
   ./create_utility_wrappers.sh
   ```

3. **Source bashrc to add commands to PATH:**

   ```bash
   source ~/.bashrc
   ```

### Verification

Test that commands are available:

```bash
# Test core commands
status
git-op status
scaffold list

# Test utility commands
fix-longlines --help
document-scripts --check
pep8-check --help
```

## Script Functionality

### Project Management (`project_manage.py`)

**Purpose**: Centralized project management operations

**Features**:

- Complete workspace setup
- Multi-project build coordination
- Test execution across projects
- Dependency management
- Clean operations

**Usage Examples**:

```bash
# Complete setup
flx_project-manage setup

# Build specific project
flx_project-manage build --project flx

# Run tests with coverage
flx_project-manage test --coverage

# Clean all build artifacts
flx_project-manage clean --all
```

### Scaffold Management (`scaffold_manage.py`)

**Purpose**: Template and code generation management

**Features**:

- Create new project scaffolds
- Template management
- Code generation utilities
- Scaffold versioning

**Usage Examples**:

```bash
# Create new adapter scaffold
scaffold-manage create adapter --name oracle-wms

# List available templates
scaffold-manage list --templates

# Update existing scaffold
scaffold-manage update --name adapter --version 2.0
```

### Git Operations (`git_manage.py`)

**Purpose**: Enhanced git workflow automation

**Features**:

- Enhanced git status with project context
- Branch management
- Remote synchronization
- Cleanup operations

**Usage Examples**:

```bash
# Enhanced status across all projects
git-manage status --all

# Sync with remote repositories
git-manage sync --projects flx,dc-oracle-wms

# Clean up merged branches
git-manage cleanup --merged
```

### Code Quality Scripts

#### Long Line Fixer (`fix_long_lines.py`)

**Purpose**: Automatically fix long lines in Python code

**Features**:

- PEP8 line length compliance
- Intelligent line breaking
- Comment preservation
- Batch processing

**Usage Examples**:

```bash
# Fix long lines in directory
fix-longlines src/flx/

# Check without fixing
fix-longlines --check src/

# Custom line length
fix-longlines --max-length 120 src/
```

#### PEP8 Compliance (`pep8_check.py`, `pep8_apply.py`)

**Purpose**: Ensure PEP8 compliance across codebase

**Features**:

- Comprehensive PEP8 checking
- Automatic fixing capabilities
- Detailed reporting
- Integration with CI/CD

**Usage Examples**:

```bash
# Check PEP8 compliance
pep8-check src/ --report compliance_report.json

# Apply PEP8 fixes
pep8-apply src/ --aggressive

# Check specific rules
pep8-check --rules E501,W503 src/
```

### Documentation Scripts

#### Script Documenter (`document_scripts.py`)

**Purpose**: Automatic script documentation generation

**Features**:

- Docstring analysis and generation
- API documentation creation
- Cross-reference generation
- Documentation validation

**Usage Examples**:

```bash
# Document all scripts
document-scripts --all

# Check documentation status
document-scripts --check --verbose

# Update specific script documentation
document-scripts --script project_manage.py --update
```

## Integration with GitHub Workflows

### CI/CD Integration

Scripts are integrated with GitHub Actions workflows:

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.13"

      - name: Run PEP8 check
        run: |
          source scripts/bin/pep8-check
          pep8-check src/ --report pep8_report.json

      - name: Fix long lines
        run: |
          source scripts/bin/fix-longlines
          fix-longlines src/ --check
```

### Automated Documentation

Documentation generation is automated:

```yaml
# .github/workflows/documentation.yml
name: Documentation

on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate script documentation
        run: |
          source scripts/bin/document-scripts
          document-scripts --all --output docs/scripts/
```

## Best Practices

### 1. Script Development

**Follow established patterns:**

```python
#!/usr/bin/env python3
"""
Script description and purpose.

This script provides [functionality description].
"""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Script logic here

if __name__ == '__main__':
    main()
```

### 2. Command Wrapper Creation

**Create consistent wrappers:**

```bash
#!/bin/bash
# Wrapper for script_name.py
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
exec python "$SCRIPT_DIR/../script_name.py" "$@"
```

### 3. Documentation Standards

**Include comprehensive docstrings:**

```python
def process_files(directory: Path, pattern: str = "*.py") -> List[Path]:
    """
    Process files in directory matching pattern.

    Args:
        directory: Target directory to process
        pattern: File pattern to match (default: "*.py")

    Returns:
        List of processed file paths

    Raises:
        FileNotFoundError: If directory doesn't exist
        PermissionError: If directory isn't accessible
    """
    pass
```

## Troubleshooting

### Common Issues

#### Commands Not Found

```bash
# Verify PATH setup
echo $PATH | grep scripts/bin

# Re-source bashrc
source ~/.bashrc

# Check symlinks
ls -la scripts/bin/
```

#### Permission Issues

```bash
# Fix script permissions
chmod +x scripts/*.py
chmod +x scripts/bin/*

# Fix wrapper permissions
find scripts/bin -type f -exec chmod +x {} \;
```

#### Script Dependencies

```bash
# Install script dependencies
pip install -r scripts/requirements.txt

# Check Python path
which python
python --version
```

### Performance Optimization

#### Parallel Processing

Scripts support parallel execution:

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def process_files_parallel(files: List[Path]) -> List[bool]:
    """Process files in parallel."""
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results = list(executor.map(process_single_file, files))
    return results
```

#### Caching

Implement result caching for expensive operations:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def expensive_operation(data: str) -> str:
    """Cache results of expensive operations."""
    # Expensive computation here
    return result
```

## Migration from Legacy Scripts

### Legacy Script Analysis

To migrate from legacy scripts:

1. **Identify legacy scripts:**

   ```bash
   find . -name "*.py" -not -path "./scripts/*" -exec grep -l "#!/usr/bin/env python" {} \;
   ```

2. **Analyze script dependencies:**

   ```bash
   document-scripts --analyze-legacy --input-dir .
   ```

3. **Generate migration plan:**

   ```bash
   document-scripts --migration-plan legacy_scripts.json
   ```

### Modernization Process

1. **Update to modern Python patterns**
2. **Add proper argument parsing**
3. **Implement logging and error handling**
4. **Create command wrappers**
5. **Add to automated documentation**

## Related Documentation

### Development Workflow

- [Development Standards](./standardization-plan.md) - Code quality standards
- [Testing Strategies](./testing-strategies.md) - Testing approaches

### Automation

- [GitHub Workflows](./github-workflows.md) - CI/CD automation
- [Dependency Management](./dependency-synchronization-guide.md) - Package automation

### Quality Assurance

- [PEP8 Compliance Report](./reports/pep8-compliance-report.md) - Code quality metrics
- [Script Documentation](./reports/script-documentation-report.md) - Documentation coverage

---

**Organization Status**: ✅ Complete and Automated
**Command Availability**: All commands accessible via PATH
**Documentation**: Comprehensive and auto-generated
**Integration**: Full CI/CD workflow integration
