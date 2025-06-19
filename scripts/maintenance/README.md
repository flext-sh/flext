# Maintenance Scripts Directory

Enterprise-grade maintenance tools for the PyAuto workspace following CLAUDE.md standards.

## Overview

This directory contains production-ready maintenance scripts for code quality, dependency management, and architecture compliance. All scripts follow ABSOLUTE ZERO TOLERANCE policies for errors and warnings.

## Main Components

### 🚀 unified_maintenance_system_v2.py (Tool-First Approach)

The primary enterprise maintenance system (v4.0.0) that prioritizes project tools:

**Features:**
- Runs project tools first (ruff, mypy, black, isort, etc.)
- Beautiful Rich console interface with progress tracking
- Dry-run, interactive, and auto modes
- Comprehensive reporting with timing metrics
- Custom fix modules for remaining issues

**Usage:**
```bash
# Dry run on entire workspace
python scripts/maintenance/unified_maintenance_system_v2.py

# Fix specific projects interactively
python scripts/maintenance/unified_maintenance_system_v2.py --projects flx --mode interactive

# Auto-fix everything
python scripts/maintenance/unified_maintenance_system_v2.py --mode auto

# Skip specific tools
python scripts/maintenance/unified_maintenance_system_v2.py --skip-tools mypy bandit
```

### 🔧 Custom Fix Modules (modules/)

Modular fix modules for issues that tools can't handle:

#### Available Modules:
- **type_annotations** - Add missing type hints to functions and variables
- **logging_patterns** - Fix f-strings in logging, replace print() statements
- **exception_handling** - Fix bare except, add exception chaining
- **asyncio_patterns** - Fix asyncio.run() in loops, time.sleep in async
- **docstrings** - Add missing docstrings (stub)
- **imports** - Fix import order and unused imports (stub)
- **security** - Fix security vulnerabilities (stub)
- **performance** - Optimize loops and data structures (stub)

**Run Custom Fixes:**
```bash
# List available modules
python scripts/maintenance/run_custom_fixes.py --list

# Run specific module in dry-run
python scripts/maintenance/run_custom_fixes.py type_annotations --target src/

# Apply fixes interactively
python scripts/maintenance/run_custom_fixes.py logging_patterns --target src/ --apply --interactive

# Run multiple modules
python scripts/maintenance/run_custom_fixes.py type_annotations logging_patterns --target . --apply
```

### 🚀 unified_maintenance_system.py (Legacy)

The primary enterprise maintenance system (v3.0.0) that combines all proven patterns:

**Features:**
- Modular plugin architecture
- Configuration-driven operations
- Parallel processing support
- Incremental fixing with rollback
- Comprehensive metrics and reporting
- Multi-project targeting

**Usage:**
```bash
# Basic usage - process entire workspace
python scripts/maintenance/unified_maintenance_system.py

# Target specific projects
python scripts/maintenance/unified_maintenance_system.py --projects flx target-oracle-wms

# Dry run mode
python scripts/maintenance/unified_maintenance_system.py --dry-run

# Use configuration file
python scripts/maintenance/unified_maintenance_system.py --config config/maintenance.yaml

# Parallel processing
python scripts/maintenance/unified_maintenance_system.py --mode parallel --workers 8
```

### 📋 Configuration

Create `config/maintenance.yaml`:

```yaml
# Target specific projects (empty = all)
target_projects: []

# Exclude patterns
exclude_patterns:
  - __pycache__
  - .venv
  - node_modules
  - archive

# Fix categories
fix_categories:
  type_annotations: true
  logging_patterns: true
  exception_handling: true
  asyncio_patterns: true
  docstring_formatting: true

# Safety settings
safety:
  validate_syntax: true
  max_changes_per_file: 50
  dry_run: false
  parallel_workers: 8

# Metrics
metrics:
  detailed_report: true
  metrics_file: reports/maintenance_metrics.json
```

## Fix Categories

### Syntax and Style
- **type_annotations**: Add missing type hints
- **logging_patterns**: Fix f-strings in logging, replace print()
- **exception_handling**: Fix bare except, add "from e"
- **unused_variables**: Add *_ for unused arguments
- **import_sorting**: Organize imports properly
- **string_quotes**: Standardize quote usage

### Code Quality
- **undefined_variables**: Fix undefined name errors
- **docstring_formatting**: Add missing docstrings
- **line_length**: Fix long lines
- **blank_lines**: Fix blank line violations
- **trailing_whitespace**: Remove trailing spaces
- **indentation**: Fix indentation errors

### Modern Python
- **f_string_conversion**: Convert .format() to f-strings
- **comprehension_optimization**: Optimize list/dict comprehensions
- **method_ordering**: Fix method order in classes
- **class_structure**: Ensure proper class structure
- **type_checking_imports**: Fix TYPE_CHECKING patterns

### Security
- **sql_injection_prevention**: Fix SQL injection risks
- **hardcoded_secrets**: Remove hardcoded passwords
- **assert_statements**: Fix assert usage
- **eval_usage**: Remove eval() calls

### Performance
- **loop_optimizations**: Optimize loops
- **dict_get_usage**: Use dict.get() properly
- **set_operations**: Optimize set operations
- **string_concatenation**: Fix string concatenation
- **asyncio_patterns**: Fix asyncio anti-patterns

### Enterprise Patterns
- **dependency_injection**: Implement DI patterns
- **hexagonal_architecture**: Ensure hexagonal compliance
- **ddd_patterns**: Apply DDD patterns
- **cqrs_compliance**: Ensure CQRS compliance

### Documentation
- **markdownlint_compliance**: Fix markdown issues
- **readme_coverage**: Ensure README.md in all folders
- **api_documentation**: Add API docs
- **code_examples**: Add usage examples

## Integration

### Makefile Integration

Add to your `Makefile`:

```makefile
# Run maintenance system
.PHONY: maintenance
maintenance:
	python scripts/maintenance/unified_maintenance_system.py

# Dry run for CI
.PHONY: maintenance-check
maintenance-check:
	python scripts/maintenance/unified_maintenance_system.py --dry-run

# Fix specific categories
.PHONY: fix-types
fix-types:
	python scripts/maintenance/unified_maintenance_system.py --categories type_annotations type_checking_imports

# Emergency fix
.PHONY: emergency-fix
emergency-fix:
	python scripts/maintenance/emergency_lint_fixer.py
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run maintenance checks
  run: |
    python scripts/maintenance/unified_maintenance_system.py --dry-run --metrics-file reports/maintenance.json

- name: Upload maintenance report
  uses: actions/upload-artifact@v3
  with:
    name: maintenance-report
    path: reports/maintenance.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: maintenance-check
      name: Maintenance System Check
      entry: python scripts/maintenance/unified_maintenance_system.py --dry-run --projects
      language: system
      files: \.py$
      pass_filenames: false
```

## Emergency Procedures

### 1. Massive Error Outbreak (>10k errors)

Use the emergency fixer for quick resolution:

```bash
python scripts/maintenance/emergency_lint_fixer.py
```

### 2. Broken Imports Across Workspace

```bash
# Fix import errors specifically
python scripts/maintenance/unified_maintenance_system.py \
  --categories undefined_variables type_checking_imports \
  --mode parallel --workers 16
```

### 3. Full Workspace Restoration

```bash
# Complete maintenance run
python scripts/maintenance/unified_maintenance_system.py \
  --mode parallel \
  --workers 16 \
  --metrics-file reports/full_restoration.json
```

## Best Practices

1. **Always run dry-run first**
   ```bash
   python scripts/maintenance/unified_maintenance_system.py --dry-run
   ```

2. **Target specific projects when possible**
   ```bash
   python scripts/maintenance/unified_maintenance_system.py --projects flx
   ```

3. **Use configuration files for repeatability**
   ```bash
   python scripts/maintenance/unified_maintenance_system.py --config config/myproject.yaml
   ```

4. **Monitor metrics for trends**
   ```bash
   # Generate detailed metrics
   python scripts/maintenance/unified_maintenance_system.py --metrics-file reports/metrics.json

   # Analyze trends
   python scripts/analysis/analyze_maintenance_metrics.py reports/metrics.json
   ```

5. **Incremental fixes for large codebases**
   ```bash
   # Fix one category at a time
   python scripts/maintenance/unified_maintenance_system.py --categories logging_patterns
   python scripts/maintenance/unified_maintenance_system.py --categories type_annotations
   ```

## Plugin Development

To add new fix categories:

1. Create a new plugin class inheriting from `MaintenancePlugin`
2. Implement required methods: `name`, `category`, `can_fix`, `fix`
3. Add to the plugin registry in `PluginRegistry._load_plugins()`
4. Add the category to `FixCategory` enum

Example:

```python
class MyCustomFixer(MaintenancePlugin):
    @property
    def name(self) -> str:
        return "My Custom Fixer"

    @property
    def category(self) -> FixCategory:
        return FixCategory.MY_CUSTOM_FIX

    def can_fix(self, file_path: Path, content: str) -> bool:
        return "pattern_to_fix" in content

    def fix(self, file_path: Path, content: str) -> Tuple[str, List[str]]:
        changes = []
        fixed = content.replace("pattern_to_fix", "fixed_pattern")
        changes.append("Fixed custom pattern")
        return fixed, changes
```

## Metrics and Reporting

The system generates comprehensive metrics:

```json
{
  "timestamp": "2024-12-19T10:30:00Z",
  "summary": {
    "total_files": 1523,
    "successful": 1520,
    "failed": 3,
    "total_changes": 4567,
    "duration": 45.23
  },
  "category_metrics": {
    "type_annotations": 1234,
    "logging_patterns": 567,
    "exception_handling": 234
  },
  "results": [...]
}
```

## Troubleshooting

### Common Issues

1. **"Permission denied" errors**
   - Ensure files are not locked by other processes
   - Run with appropriate permissions

2. **"Syntax error after fix"**
   - Enable syntax validation: `safety.validate_syntax: true`
   - Check the specific plugin that caused the issue

3. **Performance issues**
   - Reduce parallel workers if system is overloaded
   - Use incremental mode for large codebases

4. **Memory issues with parallel processing**
   - Reduce worker count: `--workers 4`
   - Use sequential mode: `--mode sequential`

### Debug Mode

Enable detailed logging:

```bash
python scripts/maintenance/unified_maintenance_system.py --log-level DEBUG
```

## Tool-First Workflow

The recommended workflow is:

1. **Run tools first** - Let professional tools handle what they can:
   ```bash
   python scripts/maintenance/unified_maintenance_system_v2.py --mode dry-run
   ```

2. **Review tool results** - See what needs manual intervention

3. **Run custom fixes** - For issues tools can't handle:
   ```bash
   python scripts/maintenance/run_custom_fixes.py type_annotations logging_patterns --target . --apply
   ```

4. **Verify results** - Run tools again to ensure compliance

## Module Architecture

Each custom fix module follows a standard interface:

```python
class CustomFixModule(ABC):
    def __init__(self, dry_run=True, interactive=False, verbose=False):
        """Initialize with mode settings."""

    def analyze(self, file_path, content) -> List[Issue]:
        """Analyze file and return issues found."""

    def apply_fixes(self, content, issues) -> str:
        """Apply fixes and return modified content."""

    def validate_fixes(self, original, fixed) -> bool:
        """Validate fixes maintain code integrity."""
```

## Version History

- **v4.0.0** - Tool-first approach with modular custom fixes
- **v3.0.0** - Unified system with plugin architecture
- **v2.0.0** - Advanced categorized fixes
- **v1.0.0** - Official PyAuto lint fixer

## License

Internal Enterprise Use - PyAuto DevOps Team
