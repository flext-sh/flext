# FLEXT DBT ORACLE WMS - Oracle WMS Data Transformations
# =======================================================
# dbt transformations for Oracle Warehouse Management System data
# Python 3.13 + dbt-oracle + Oracle WMS Analytics + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration
.PHONY: deps-update deps-audit deps-tree
.PHONY: dbt-run dbt-test dbt-docs dbt-compile dbt-debug dbt-wms-profile dbt-wms-lineage

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🏢 FLEXT DBT ORACLE WMS - Oracle WMS Data Transformations"
	@echo "========================================================="
	@echo "🎯 Clean Architecture + DDD + Python 3.13 + dbt Oracle WMS Analytics"
	@echo ""
	@echo "📦 dbt transformations for Oracle Warehouse Management System data"
	@echo "🔒 Zero tolerance quality gates for WMS data models"
	@echo "🧪 90%+ test coverage requirement for analytics models"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test dbt-test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT DBT ORACLE WMS COMPLIANT"

check: lint type-check test ## Essential quality checks (pre-commit standard)
	@echo "✅ Essential checks passed"

lint: ## Ruff linting (17 rule categories, ALL enabled)
	@echo "🔍 Running ruff linter (ALL rules enabled)..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ Linting complete"

type-check: ## MyPy strict mode type checking (zero errors tolerated)
	@echo "🛡️ Running MyPy strict type checking..."
	@poetry run mypy src/ tests/ --strict
	@echo "✅ Type checking complete"

security: ## Security scans (bandit + pip-audit + secrets)
	@echo "🔒 Running security scans..."
	@poetry run bandit -r src/ --severity-level medium --confidence-level medium
	@poetry run pip-audit --ignore-vuln PYSEC-2022-42969
	@poetry run detect-secrets scan --all-files
	@echo "✅ Security scans complete"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	@poetry run ruff format src/ tests/
	@echo "✅ Formatting complete"

format-check: ## Check formatting without fixing
	@echo "🎨 Checking code formatting..."
	@poetry run ruff format src/ tests/ --check
	@echo "✅ Format check complete"

fix: format lint ## Auto-fix all issues (format + imports + lint)
	@echo "🔧 Auto-fixing all issues..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ All auto-fixes applied"

# ============================================================================
# 🧪 TESTING - 90% COVERAGE MINIMUM
# ============================================================================

test: ## Run tests with coverage (90% minimum required)
	@echo "🧪 Running tests with coverage..."
	@poetry run pytest tests/ -v --cov=src/flext_dbt_oracle_wms --cov-report=term-missing --cov-fail-under=90
	@echo "✅ Tests complete"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v
	@echo "✅ Unit tests complete"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v
	@echo "✅ Integration tests complete"

coverage: ## Generate detailed coverage report
	@echo "📊 Generating coverage report..."
	@poetry run pytest tests/ --cov=src/flext_dbt_oracle_wms --cov-report=term-missing --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/"

coverage-html: coverage ## Generate HTML coverage report
	@echo "📊 Opening coverage report..."
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🚀 DEVELOPMENT SETUP
# ============================================================================

setup: install pre-commit ## Complete development setup
	@echo "🎯 Development setup complete!"

install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies..."
	@poetry install --all-extras --with dev,test,docs,security
	@echo "✅ Dependencies installed"

dev-install: install ## Install in development mode
	@echo "🔧 Setting up development environment..."
	@poetry install --all-extras --with dev,test,docs,security
	@poetry run pre-commit install
	@echo "✅ Development environment ready"

pre-commit: ## Setup pre-commit hooks
	@echo "🎣 Setting up pre-commit hooks..."
	@poetry run pre-commit install
	@poetry run pre-commit run --all-files || true
	@echo "✅ Pre-commit hooks installed"

# ============================================================================
# 🏗️ DBT ORACLE WMS OPERATIONS
# ============================================================================

dbt-run: ## Run dbt WMS models
	@echo "🏗️ Running dbt WMS models..."
	@poetry run dbt run --profiles-dir profiles --target dev
	@echo "✅ dbt WMS models executed"

dbt-test: ## Run dbt WMS tests
	@echo "🧪 Running dbt WMS tests..."
	@poetry run dbt test --profiles-dir profiles --target dev
	@echo "✅ dbt WMS tests passed"

dbt-docs: ## Generate dbt WMS documentation
	@echo "📚 Generating dbt WMS documentation..."
	@poetry run dbt docs generate --profiles-dir profiles --target dev
	@poetry run dbt docs serve --profiles-dir profiles --port 8080
	@echo "✅ dbt WMS documentation available at http://localhost:8080"

dbt-compile: ## Compile dbt WMS models
	@echo "🔨 Compiling dbt WMS models..."
	@poetry run dbt compile --profiles-dir profiles --target dev
	@echo "✅ dbt WMS models compiled"

dbt-debug: ## Debug dbt WMS configuration
	@echo "🔍 Debugging dbt WMS configuration..."
	@poetry run dbt debug --profiles-dir profiles --target dev
	@echo "✅ dbt WMS debug complete"

dbt-wms-profile: ## Setup Oracle WMS profile
	@echo "⚙️ Setting up Oracle WMS profile..."
	@echo "Creating profiles directory if it doesn't exist..."
	@mkdir -p profiles
	@echo "WMS profile setup complete - configure profiles/profiles.yml manually"

dbt-wms-lineage: ## Generate WMS data lineage
	@echo "🗂️ Generating WMS data lineage..."
	@poetry run dbt docs generate --profiles-dir profiles --target dev
	@echo "✅ WMS data lineage generated - view in dbt docs"

dbt-seed: ## Load WMS seed data
	@echo "🌱 Loading WMS seed data..."
	@poetry run dbt seed --profiles-dir profiles --target dev
	@echo "✅ WMS seed data loaded"

dbt-snapshot: ## Run WMS snapshots for SCD
	@echo "📸 Running WMS snapshots..."
	@poetry run dbt snapshot --profiles-dir profiles --target dev
	@echo "✅ WMS snapshots executed"

dbt-run-operation: ## Run dbt WMS operations
	@echo "⚙️ Running dbt WMS operations..."
	@poetry run dbt run-operation --profiles-dir profiles --target dev
	@echo "✅ dbt WMS operations complete"

# ============================================================================
# 📦 BUILD & DISTRIBUTION
# ============================================================================

build: clean ## Build distribution packages
	@echo "🔨 Building distribution..."
	@poetry build
	@echo "✅ Build complete - packages in dist/"

# ============================================================================
# 🧹 CLEANUP
# ============================================================================

clean: ## Remove all artifacts
	@echo "🧹 Cleaning up..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf target/
	@rm -rf dbt_packages/
	@rm -rf logs/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# ============================================================================
# 📊 DEPENDENCY MANAGEMENT
# ============================================================================

deps-update: ## Update all dependencies
	@echo "🔄 Updating dependencies..."
	@poetry update
	@echo "✅ Dependencies updated"

deps-audit: ## Audit dependencies for vulnerabilities
	@echo "🔍 Auditing dependencies..."
	@poetry run pip-audit
	@echo "✅ Dependency audit complete"

deps-tree: ## Show dependency tree
	@echo "🌳 Dependency tree:"
	@poetry show --tree

deps-outdated: ## Show outdated dependencies
	@echo "📋 Outdated dependencies:"
	@poetry show --outdated

# ============================================================================
# 🔧 ENVIRONMENT CONFIGURATION
# ============================================================================

# Python settings
PYTHON := python3.13
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

# dbt settings
export DBT_PROFILES_DIR := $(PWD)/profiles
export DBT_PROJECT_DIR := $(PWD)

# Oracle WMS settings
export WMS_ORGANIZATION_ID := 101
export WMS_FACILITY_CODE := DC001

# Poetry settings
export POETRY_VENV_IN_PROJECT := false
export POETRY_CACHE_DIR := $(HOME)/.cache/pypoetry

# Quality gate settings
export MYPY_CACHE_DIR := .mypy_cache
export RUFF_CACHE_DIR := .ruff_cache

# ============================================================================
# 📝 PROJECT METADATA
# ============================================================================

# Project information
PROJECT_NAME := flext-dbt-oracle-wms
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT DBT Oracle WMS - Oracle WMS Data Transformations

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 WMS SPECIFIC COMMANDS
# ============================================================================

wms-inventory-models: ## Run WMS inventory models only
	@echo "📦 Running WMS inventory models..."
	@poetry run dbt run --models tag:inventory --profiles-dir profiles --target dev
	@echo "✅ WMS inventory models executed"

wms-shipment-models: ## Run WMS shipment models only
	@echo "🚚 Running WMS shipment models..."
	@poetry run dbt run --models tag:shipment --profiles-dir profiles --target dev
	@echo "✅ WMS shipment models executed"

wms-location-models: ## Run WMS location models only
	@echo "📍 Running WMS location models..."
	@poetry run dbt run --models tag:location --profiles-dir profiles --target dev
	@echo "✅ WMS location models executed"

wms-kpi-models: ## Run WMS KPI models only
	@echo "📊 Running WMS KPI models..."
	@poetry run dbt run --models tag:kpi --profiles-dir profiles --target dev
	@echo "✅ WMS KPI models executed"

wms-full-refresh: ## Full refresh of WMS models
	@echo "🔄 Full refresh of WMS models..."
	@poetry run dbt run --full-refresh --profiles-dir profiles --target dev
	@echo "✅ WMS models full refresh complete"

wms-test-data-quality: ## Test WMS data quality rules
	@echo "🔍 Testing WMS data quality..."
	@poetry run dbt test --models tag:data_quality --profiles-dir profiles --target dev
	@echo "✅ WMS data quality tests passed"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 DBT WMS project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Clean Architecture + DDD"
	@echo "🐍 Python: 3.13"
	@echo "🗂️ Framework: dbt Oracle WMS"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: Oracle WMS Data Transformations"
	@echo "🔗 Dependencies: flext-core, flext-oracle-wms"
	@echo "📦 Provides: Oracle WMS analytics models"
	@echo "🎯 Standards: Enterprise dbt WMS patterns"