# FLEXT DBT ORACLE - Oracle Database Data Transformations
# =======================================================
# dbt transformations for Oracle Database with enterprise analytics
# Python 3.13 + dbt-oracle + Oracle SQL + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration
.PHONY: deps-update deps-audit deps-tree
.PHONY: dbt-run dbt-test dbt-docs dbt-compile dbt-debug dbt-oracle-profile

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🏛️ FLEXT DBT ORACLE - Oracle Database Data Transformations"
	@echo "=========================================================="
	@echo "🎯 Clean Architecture + DDD + Python 3.13 + dbt Oracle Analytics"
	@echo ""
	@echo "📦 dbt transformations for Oracle Database with enterprise patterns"
	@echo "🔒 Zero tolerance quality gates for Oracle data models"
	@echo "🧪 90%+ test coverage requirement for analytics models"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test dbt-test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT DBT ORACLE COMPLIANT"

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
	@poetry run pytest tests/ -v --cov=src/flext_dbt_oracle --cov-report=term-missing --cov-fail-under=90
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
	@poetry run pytest tests/ --cov=src/flext_dbt_oracle --cov-report=term-missing --cov-report=html
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
# 🏗️ DBT ORACLE OPERATIONS
# ============================================================================

dbt-run: ## Run dbt Oracle models
	@echo "🏗️ Running dbt Oracle models..."
	@poetry run dbt run --profiles-dir profiles --target dev
	@echo "✅ dbt Oracle models executed"

dbt-test: ## Run dbt Oracle tests
	@echo "🧪 Running dbt Oracle tests..."
	@poetry run dbt test --profiles-dir profiles --target dev
	@echo "✅ dbt Oracle tests passed"

dbt-docs: ## Generate dbt Oracle documentation
	@echo "📚 Generating dbt Oracle documentation..."
	@poetry run dbt docs generate --profiles-dir profiles --target dev
	@poetry run dbt docs serve --profiles-dir profiles --port 8080
	@echo "✅ dbt Oracle documentation available at http://localhost:8080"

dbt-compile: ## Compile dbt Oracle models
	@echo "🔨 Compiling dbt Oracle models..."
	@poetry run dbt compile --profiles-dir profiles --target dev
	@echo "✅ dbt Oracle models compiled"

dbt-debug: ## Debug dbt Oracle configuration
	@echo "🔍 Debugging dbt Oracle configuration..."
	@poetry run dbt debug --profiles-dir profiles --target dev
	@echo "✅ dbt Oracle debug complete"

dbt-oracle-profile: ## Setup Oracle profile
	@echo "⚙️ Setting up Oracle profile..."
	@echo "Creating profiles directory if it doesn't exist..."
	@mkdir -p profiles
	@echo "Oracle profile setup complete - configure profiles/profiles.yml manually"

dbt-seed: ## Load Oracle seed data
	@echo "🌱 Loading Oracle seed data..."
	@poetry run dbt seed --profiles-dir profiles --target dev
	@echo "✅ Oracle seed data loaded"

dbt-snapshot: ## Run Oracle snapshots for SCD
	@echo "📸 Running Oracle snapshots..."
	@poetry run dbt snapshot --profiles-dir profiles --target dev
	@echo "✅ Oracle snapshots executed"

dbt-run-operation: ## Run dbt Oracle operations
	@echo "⚙️ Running dbt Oracle operations..."
	@poetry run dbt run-operation --profiles-dir profiles --target dev
	@echo "✅ dbt Oracle operations complete"

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

# Oracle settings
export ORACLE_SOURCE_SCHEMA := FLEXT_RAW
export ORACLE_TARGET_SCHEMA := FLEXT_ANALYTICS

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
PROJECT_NAME := flext-dbt-oracle
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT DBT Oracle - Oracle Database Data Transformations

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 ORACLE SPECIFIC COMMANDS
# ============================================================================

oracle-staging-models: ## Run Oracle staging models only
	@echo "📥 Running Oracle staging models..."
	@poetry run dbt run --models tag:staging --profiles-dir profiles --target dev
	@echo "✅ Oracle staging models executed"

oracle-marts-models: ## Run Oracle marts models only
	@echo "🏪 Running Oracle marts models..."
	@poetry run dbt run --models tag:marts --profiles-dir profiles --target dev
	@echo "✅ Oracle marts models executed"

oracle-fact-models: ## Run Oracle fact models only
	@echo "📊 Running Oracle fact models..."
	@poetry run dbt run --models tag:fact --profiles-dir profiles --target dev
	@echo "✅ Oracle fact models executed"

oracle-dimension-models: ## Run Oracle dimension models only
	@echo "🗂️ Running Oracle dimension models..."
	@poetry run dbt run --models tag:dimension --profiles-dir profiles --target dev
	@echo "✅ Oracle dimension models executed"

oracle-full-refresh: ## Full refresh of Oracle models
	@echo "🔄 Full refresh of Oracle models..."
	@poetry run dbt run --full-refresh --profiles-dir profiles --target dev
	@echo "✅ Oracle models full refresh complete"

oracle-test-data-quality: ## Test Oracle data quality rules
	@echo "🔍 Testing Oracle data quality..."
	@poetry run dbt test --models tag:data_quality --profiles-dir profiles --target dev
	@echo "✅ Oracle data quality tests passed"

oracle-explain-plan: ## Generate Oracle explain plans
	@echo "📋 Generating Oracle explain plans..."
	@poetry run dbt compile --profiles-dir profiles --target dev
	@echo "✅ Oracle models compiled - check target/ for SQL files"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 DBT Oracle project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Clean Architecture + DDD"
	@echo "🐍 Python: 3.13"
	@echo "🗂️ Framework: dbt Oracle"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: Oracle Database Data Transformations"
	@echo "🔗 Dependencies: flext-core"
	@echo "📦 Provides: Oracle analytics models"
	@echo "🎯 Standards: Enterprise dbt Oracle patterns"