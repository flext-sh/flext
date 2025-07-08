# FLEXT Makefile System Documentation

# ===================================

## 🚀 Overview

The FLEXT workspace uses a **standardized Makefile system** that provides:

- **Unified commands** across all projects
- **Project-specific features** based on type
- **Workspace-level coordination**
- **Professional development workflow**

## 📁 Structure

```
flext/
├── Makefile                    # Master workspace coordinator
├── flext-core/Makefile         # Core foundation framework
├── flext-api/Makefile          # API service (with api-dev commands)
├── flext-tap-ldap/Makefile     # Data integration (with validate-schema)
└── scripts/
    └── standardize-makefiles.py # Makefile generation script
```

## 🎯 Usage Patterns

### Workspace Commands (Root Level)

```bash
# Development workflow
make workspace-setup          # Setup entire workspace
make dev-setup                # Quick development setup
make workspace-status         # Show project status

# Testing
make test-all                 # Test all projects
make test-core                # Test only core projects
make test-api                 # Test API projects
make test-data                # Test data integration projects

# Quality & Maintenance
make lint-all                 # Lint all projects
make format-all               # Format all projects
make type-check-all           # Type check all projects
make security-all             # Security check all projects
make check-all                # Run all quality checks

# Quick commands for development
make quick-test               # Quick test (core only)
make quick-check              # Quick quality check
make quick-format             # Quick format (all projects)

# Build & Documentation
make build-all                # Build all projects
make docs-all                 # Generate all documentation

# Maintenance
make workspace-clean          # Clean all projects
make workspace-update         # Update all dependencies
make poetry-update-all        # Update Poetry in all projects
```

### Individual Project Commands

```bash
# Basic workflow for any project
cd flext-core                 # or any project
make help                     # Show available commands
make install                  # Install dependencies
make test                     # Run tests
make lint                     # Run linting
make format                   # Format code
make build                    # Build package

# Development cycle
make dev-setup                # Setup development environment
make dev                      # Run in development mode
make dev-test                 # Quick test cycle

# Quality assurance
make check                    # Run all quality checks
make type-check               # Type checking
make security                 # Security analysis
make pre-commit               # Pre-commit hooks
```

## 🔧 Project-Specific Commands

### API Projects (flext-api, flext-auth, flext-grpc, flext-web)

```bash
make api-dev                  # Start API development server
make api-test                 # Test API endpoints (fast tests)
```

### CLI Projects (flext-cli)

```bash
make cli-install              # Install CLI globally
make cli-test                 # Test CLI commands
```

### Data Integration (flext-tap-*, flext-target-*)

```bash
make validate-schema          # Validate data schemas
make test-connection          # Test data source connection
```

## 📊 Project Types

| Type | Projects | Special Commands |
|------|----------|------------------|
| **core** | flext-core | Foundation framework commands |
| **api** | flext-api, flext-auth, flext-grpc, flext-web | `api-dev`, `api-test` |
| **cli** | flext-cli | `cli-install`, `cli-test` |
| **data** | flext-tap-*, flext-target-*, flext-dbt-* | `validate-schema`, `test-connection` |
| **infra** | flext-observability, flext-quality, etc. | Standard commands |
| **project** | client-a-oud-mig, client-b-* | Enterprise applications |

## 🔄 Development Workflow

### 1. Initial Setup

```bash
# Setup entire workspace
make workspace-setup

# Or setup individual project
cd flext-core
make dev-setup
```

### 2. Daily Development

```bash
# Format code before committing
make quick-format

# Run tests during development
make quick-test

# Full quality check before PR
make check-all
```

### 3. Before Committing

```bash
# Run pre-commit hooks
make pre-commit-all

# Full quality check
make check-all

# Build verification
make build-all
```

## 🎨 Customization

### Adding New Projects

1. **Create project structure**:

```bash
mkdir new-project
cd new-project
# Create pyproject.toml, src/, tests/
```

2. **Add to standardization script**:

```python
# In scripts/standardize-makefiles.py
PROJECT_TYPES = {
    'your_type': ['new-project'],
    # ...
}
```

3. **Generate Makefile**:

```bash
python scripts/standardize-makefiles.py
```

### Custom Commands

Add custom commands to individual project Makefiles:

```makefile
# In project/Makefile (after standard commands)

# Custom project commands
custom-command: ## Your custom command
	@echo "🔧 Running custom command..."
	# Your command here
```

## 🚨 Troubleshooting

### Common Issues

1. **Command not found**:

```bash
# Ensure Poetry is installed
make -C flext-core install

# Or use workspace command
make workspace-install
```

2. **Permission errors**:

```bash
# Make script executable
chmod +x scripts/standardize-makefiles.py
```

3. **Import errors in tests**:

```bash
# Verify PYTHONPATH is set correctly
cd project
export PYTHONPATH=src:$PYTHONPATH
make test
```

### Debugging

1. **Show detailed output**:

```bash
make test V=1               # Verbose mode
make lint --debug           # Debug mode
```

2. **Test individual project**:

```bash
cd problematic-project
make help                   # Check available commands
make install               # Reinstall dependencies
make test                  # Run tests
```

## 📈 Performance

### Parallel Execution

```bash
# Run tests in parallel (workspace level)
make -j4 test-all          # 4 parallel jobs

# Build all projects in parallel
make -j$(nproc) build-all  # Use all CPU cores
```

### Fast Commands

```bash
make quick-test            # Core tests only
make quick-check           # Essential quality checks
make dev-test              # Fast development tests
```

## 🔐 Best Practices

### 1. **Always use workspace commands** for multi-project operations

```bash
✅ make test-all           # Good
❌ for project in */; do cd $project && make test; done  # Bad
```

### 2. **Use project-specific commands** for focused work

```bash
cd flext-api
make api-dev               # Start API server
make api-test              # Test API endpoints
```

### 3. **Run quality checks** before committing

```bash
make check-all             # Full quality check
make quick-format          # Format code
```

### 4. **Use backups** when modifying Makefiles

```bash
# Backups are automatically created as Makefile.bak
ls flext-core/Makefile.bak # Backup of original
```

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Setup workspace | `make workspace-setup` |
| Test everything | `make test-all` |
| Format code | `make quick-format` |
| Quality check | `make check-all` |
| Build all | `make build-all` |
| Clean workspace | `make workspace-clean` |
| Show status | `make workspace-status` |
| Individual project help | `make -C project help` |

## 🔗 Integration

### With Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
make quick-format
make quick-check
```

### With CI/CD

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: make test-all

- name: Quality checks  
  run: make check-all

- name: Build packages
  run: make build-all
```

---

💡 **Tip**: Start with `make help` at any level to see available commands!
