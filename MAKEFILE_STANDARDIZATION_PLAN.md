# FLEXT WORKSPACE - MAKEFILE STANDARDIZATION PLAN

**Status**: Implementation Plan Created
**Date**: 2025-07-12
**Objective**: Standardize `make check` commands across all 23 FLEXT projects

## 📊 CURRENT STATE ANALYSIS

### Projects WITH check targets: 20/25
- **Simple checks (lint + type-check)**: 4 projects
- **Comprehensive checks (+ security + test)**: 10 projects  
- **Extended checks (+ coverage + complexity)**: 3 projects
- **Quality-gate alias**: 3 projects

### Projects WITHOUT check targets: 5/25
- algar-oud-mig (root)
- flexcore
- flext-db-oracle
- flext-tap-oracle-wms
- Workspace root Makefile

## 🎯 STANDARDIZATION STRATEGY

### Tier 1: BASELINE STANDARD (All Projects)
Every project MUST have these targets:

```makefile
.PHONY: lint type-check test check

lint: ## Run code linting
	@echo "🔍 Running linting..."
	@ruff check src/ tests/ --output-format=concise

type-check: ## Run type checking
	@echo "🔍 Running type checking..."
	@mypy src/$(PACKAGE_NAME)/ --no-error-summary

test: ## Run tests
	@echo "🧪 Running tests..."
	@pytest tests/ -v --tb=short

check: lint type-check test ## Run all code quality checks
	@echo "✅ All quality checks passed!"
```

### Tier 2: PRODUCTION STANDARD (Python Services)
For production-ready services, add security:

```makefile
.PHONY: security

security: ## Run security scanning
	@echo "🔒 Running security scan..."
	@bandit -r src/ -ll -i

check: lint type-check security test ## Run all quality checks
```

### Tier 3: CRITICAL STANDARD (Core/Auth/API)
For critical infrastructure, add strict quality gates:

```makefile
.PHONY: format-check coverage quality-gate

format-check: ## Check code formatting
	@echo "📝 Checking formatting..."
	@black --check --diff .
	@isort --check-only .

coverage: ## Run tests with coverage
	@echo "📊 Running tests with coverage..."
	@pytest tests/ --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-fail-under=80

quality-gate: format-check lint type-check security coverage ## Run ALL quality gates (strict)
	@echo "🚀 All quality gates passed!"

check: quality-gate ## Alias for quality-gate
```

## 🔧 IMPLEMENTATION PLAN

### Phase 1: Add Missing Basics (IMMEDIATE)
Add Tier 1 `check` targets to these 5 projects:
1. ✅ algar-oud-mig (root)
2. ✅ flexcore  
3. ✅ flext-db-oracle
4. ✅ flext-tap-oracle-wms
5. ✅ Workspace root (special case - orchestration)

### Phase 2: Upgrade Simple to Comprehensive (WEEK 1)
Upgrade these 4 projects from Tier 1 to Tier 2:
1. flext-auth → Add security target
2. flext-api → Add security target
3. flext-cli → Add security target
4. flext-meltano → Add security target

### Phase 3: Standardize Commands (WEEK 2)
Ensure all projects use consistent commands:
- Replace `|| true` with proper error handling
- Use consistent output formats
- Reference pyproject.toml for configuration
- Standardize pytest flags

### Phase 4: Add Quality Gates (WEEK 3)
For critical projects, implement Tier 3:
1. flext-auth (security critical)
2. flext-api (gateway critical)
3. flext-grpc (service critical)

## 📝 STANDARD MAKEFILE TEMPLATE

```makefile
# === Variables ===
PACKAGE_NAME := flext_example
PYTHON := python
PYTEST := pytest
RUFF := ruff
MYPY := mypy
BLACK := black
ISORT := isort
BANDIT := bandit

# === Quality Targets ===
.PHONY: lint
lint: ## Run code linting
	@echo "🔍 Running linting..."
	@$(RUFF) check src/ tests/ --output-format=concise

.PHONY: type-check
type-check: ## Run type checking
	@echo "🔍 Running type checking..."
	@$(MYPY) src/$(PACKAGE_NAME)/ --no-error-summary

.PHONY: security
security: ## Run security scanning
	@echo "🔒 Running security scan..."
	@$(BANDIT) -r src/ -ll -i

.PHONY: test
test: ## Run tests
	@echo "🧪 Running tests..."
	@$(PYTEST) tests/ -v --tb=short

.PHONY: check
check: lint type-check security test ## Run all code quality checks
	@echo "✅ All quality checks passed!"

# === Development Targets ===
.PHONY: format
format: ## Format code
	@echo "📝 Formatting code..."
	@$(BLACK) .
	@$(ISORT) .
	@$(RUFF) check --fix .

.PHONY: clean
clean: ## Clean build artifacts
	@echo "🧹 Cleaning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/
```

## 🚀 WORKSPACE ROOT MAKEFILE

The workspace root should orchestrate all projects:

```makefile
.PHONY: check-all
check-all: ## Run quality checks on all projects
	@echo "🔍 Running quality checks on all FLEXT projects..."
	@for project in $(PYTHON_PROJECTS); do \
		echo "\n📦 Checking $$project..."; \
		$(MAKE) -C $$project check || exit 1; \
	done
	@echo "\n✅ All projects passed quality checks!"
```

## 📊 SUCCESS METRICS

- **Week 1**: All 25 projects have `make check` target
- **Week 2**: All projects use standardized commands
- **Week 3**: Critical projects have strict quality gates
- **Month 1**: 0 projects fail `make check-all`
- **Month 2**: All projects pass with 0 warnings

## 🔄 MAINTENANCE

1. **Regular Reviews**: Monthly review of Makefile standards
2. **Tool Updates**: Keep quality tools versions synchronized
3. **New Projects**: Must use standard template from day 1
4. **CI Integration**: `make check` must pass in CI/CD

---

**Next Step**: Implement Phase 1 - Add missing basics to 5 projects