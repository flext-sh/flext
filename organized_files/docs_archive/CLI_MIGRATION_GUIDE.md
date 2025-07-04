# 🚀 CLI Migration Guide - From Scripts to Unified Interface

## Overview

This guide documents the migration from custom scripts to the unified FLX CLI interface, replacing scattered automation with organized, professional commands.

## ✅ Before (Custom Scripts)

```bash
# Quality management - scattered scripts
python achieve_100_percent_compliance.py
python fix_all_quality_issues.py
python fix_mypy_issues.py
python fix_final_syntax_errors.py
# ... 20+ different fix_*.py scripts

# Migration operations - project-specific scripts
cd algar-oud-mig
python analyze_hierarchy_errors.py
python create_missing_parents.py
python complete_groups_migration.py
python complete_production_validation.py

cd ../gruponos-meltano-native
python production_meltano_test.py
python validate_100_percent_real.py
```

## 🎯 After (Unified CLI)

```bash
# Quality management - organized interface
./flx quality check                    # Check all violations
./flx quality check --auto-fix         # Auto-fix when possible
./flx quality check --category E402    # Target specific violations
./flx quality compliance --target 95   # Systematic compliance

# Migration operations - project-agnostic interface
./flx migration status algar-oud       # Check status
./flx migration run algar-oud          # Execute migration
./flx migration run algar-oud --dry-run # Preview changes

./flx migration status gruponos        # GrupoNOS status
./flx migration run gruponos           # Execute GrupoNOS migration

# Development workflow - streamlined
./flx dev start                        # Start all services
./flx dev start --service api          # Start specific service
./flx dev test --coverage              # Run tests with coverage
./flx dev validate                     # Complete validation

# Workspace management - comprehensive
./flx workspace status                 # Overall status
./flx workspace build --clean          # Clean build
./flx workspace setup                  # Complete setup
```

## 📋 Command Mapping

### Quality Management

| Old Script | New Command | Description |
|------------|-------------|-------------|
| `achieve_100_percent_compliance.py` | `./flx quality compliance --target 100` | Systematic compliance |
| `fix_all_quality_issues.py` | `./flx quality check --auto-fix` | Auto-fix violations |
| `fix_mypy_issues.py` | `./flx quality check --category ANN` | Type annotation fixes |
| `fix_final_syntax_errors.py` | `./flx quality check --category E,F` | Syntax error fixes |

### Migration Operations

| Old Script | New Command | Description |
|------------|-------------|-------------|
| `analyze_hierarchy_errors.py` | `./flx migration run algar-oud` | ALGAR migration step 1 |
| `create_missing_parents.py` | `./flx migration run algar-oud` | ALGAR migration step 2 |
| `complete_groups_migration.py` | `./flx migration run algar-oud` | ALGAR migration step 3 |
| `production_meltano_test.py` | `./flx migration run gruponos` | GrupoNOS extraction |
| `validate_100_percent_real.py` | `./flx migration run gruponos` | GrupoNOS validation |

### Development Workflow

| Old Approach | New Command | Description |
|-------------|-------------|-------------|
| `make dev` | `./flx dev start` | Start development |
| `make test` | `./flx dev test` | Run tests |
| `make validate-api` | `./flx dev validate` | Validate setup |
| Manual status checks | `./flx workspace status` | Comprehensive status |

## 🏗️ Architecture Benefits

### Organization
- **Single Entry Point**: One `./flx` command for everything
- **Logical Grouping**: Commands organized by domain (quality, migration, dev)
- **Consistent Interface**: Same patterns across all operations
- **Help System**: Built-in help for every command

### Maintainability
- **Centralized Logic**: Common functionality in shared modules
- **DRY Principle**: No duplicate code across scripts
- **Type Safety**: Full type annotations throughout
- **Error Handling**: Consistent error reporting

### User Experience
- **Rich Output**: Beautiful terminal output with colors and progress
- **Debug Mode**: `--debug` flag for troubleshooting
- **Dry Run**: `--dry-run` for safe testing
- **Status Reporting**: Clear progress and status information

## 🔧 Implementation Details

### Module Structure

```
flxt/                          # Support modules
├── __init__.py               # Package init
├── quality.py                # Quality management (replaces fix_*.py)
├── migration.py              # Migration operations (replaces project scripts)
└── workspace.py              # Workspace management
```

### Quality Management Module

```python
class QualityManager:
    """Unified quality management to replace scattered scripts."""

    def check_all(self) -> Dict[str, int]:
        """Get comprehensive quality metrics."""

    def auto_fix(self, violations: List[Dict]) -> int:
        """Auto-fix violations when possible."""

class ComplianceManager:
    """Systematic compliance improvement."""

    def achieve_compliance(self, target: float):
        """Apply proven 'formiguinha' methodology."""
```

### Migration Management Module

```python
class AlgarMigration(BaseMigration):
    """ALGAR OUD migration - replaces all ALGAR scripts."""

    def execute(self):
        """Execute complete ALGAR migration pipeline."""

class GruponosMigration(BaseMigration):
    """GrupoNOS migration - replaces GrupoNOS scripts."""

    def execute(self):
        """Execute GrupoNOS migration pipeline."""
```

## 📊 Benefits Achieved

### For Users
- **Simplified Interface**: One command to learn instead of dozens
- **Consistent Experience**: Same patterns everywhere
- **Better Documentation**: Built-in help system
- **Error Recovery**: Better error messages and suggestions

### For Developers
- **Maintainability**: Centralized logic, easier to modify
- **Extensibility**: Easy to add new commands
- **Testing**: Modular structure enables better testing
- **Debugging**: Consistent debug patterns

### For Operations
- **Reliability**: Proven patterns consolidated
- **Monitoring**: Status commands for all operations
- **Automation**: Better scriptability for CI/CD
- **Consistency**: Same interface across environments

## 🎯 Usage Examples

### Quality Management Workflow

```bash
# Check current state
./flx quality check

# Get current compliance
./flx quality compliance

# Achieve 95% compliance systematically
./flx quality compliance --target 95

# Target specific issues
./flx quality check --category E402 --auto-fix
```

### Migration Workflow

```bash
# Check migration status
./flx migration status algar-oud

# Preview migration actions
./flx migration run algar-oud --dry-run

# Execute migration
./flx migration run algar-oud

# Check final status
./flx migration status algar-oud
```

### Development Workflow

```bash
# Complete workspace setup
./flx workspace setup

# Start development environment
./flx dev start

# Run tests with coverage
./flx dev test --coverage

# Check overall status
./flx workspace status

# Validate architecture
./flx dev validate
```

## 🔄 Migration Strategy

### Phase 1: Parallel Operation ✅ COMPLETE
- New CLI implemented alongside existing scripts
- All major functionality replicated
- Users can switch at their own pace

### Phase 2: Deprecation Notices (Next)
- Add deprecation warnings to old scripts
- Update documentation to recommend new CLI
- Provide migration assistance

### Phase 3: Script Removal (Future)
- Remove old scripts once adoption is complete
- Clean up repository structure
- Update CI/CD to use new CLI

## 📖 Getting Started

### Quick Start

```bash
# See available commands
./flx --help

# Get workspace overview
./flx info

# Check current status
./flx workspace status

# Start development
./flx dev start
```

### Common Workflows

```bash
# Quality improvement workflow
./flx quality check
./flx quality compliance --target 90
./flx quality check --auto-fix

# Migration workflow
./flx migration status algar-oud
./flx migration run algar-oud --dry-run
./flx migration run algar-oud

# Development workflow
./flx workspace setup
./flx dev start
./flx dev test
./flx dev validate
```

## 🎉 Success Metrics

- **Script Consolidation**: 20+ scripts → 1 unified CLI
- **User Experience**: Consistent interface across all operations
- **Maintainability**: Centralized logic with shared modules
- **Documentation**: Built-in help system
- **Error Handling**: Consistent error reporting and recovery

The migration from custom scripts to unified CLI represents a significant improvement in project organization, user experience, and maintainability.
