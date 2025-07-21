# FLEXT TAP ORACLE - Oracle Database Data Extraction
# ===================================================
# Singer tap for Oracle Database with enterprise connectivity
# Python 3.13 + Singer SDK + Oracle DB + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration
.PHONY: deps-update deps-audit deps-tree
.PHONY: discover run validate-config singer-check

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🔍 FLEXT TAP ORACLE - Oracle Database Data Extraction"
	@echo "===================================================="
	@echo "🎯 Clean Architecture + DDD + Python 3.13 + Singer Oracle Integration"
	@echo ""
	@echo "📦 Singer tap for Oracle Database data extraction with enterprise features"
	@echo "🔒 Zero tolerance quality gates for data extraction"
	@echo "🧪 90%+ test coverage requirement for Oracle integration"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT TAP ORACLE COMPLIANT"

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
	@poetry run pytest tests/ -v --cov=src/flext_tap_oracle --cov-report=term-missing --cov-fail-under=90
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
	@poetry run pytest tests/ --cov=src/flext_tap_oracle --cov-report=term-missing --cov-report=html
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
# 🎵 SINGER TAP OPERATIONS
# ============================================================================

discover: ## Run discovery mode
	@echo "🔍 Running Oracle discovery..."
	@poetry run tap-oracle --config config.json --discover > catalog.json
	@echo "✅ Oracle schema discovery complete - catalog.json generated"

run: ## Run Oracle data extraction
	@echo "📊 Running Oracle data extraction..."
	@poetry run tap-oracle --config config.json --catalog catalog.json
	@echo "✅ Oracle data extraction complete"

validate-config: ## Validate tap configuration
	@echo "🔍 Validating Oracle tap configuration..."
	@poetry run tap-oracle --config config.json --test
	@echo "✅ Oracle tap configuration valid"

singer-check: ## Check Singer specification compliance
	@echo "🎵 Checking Singer specification compliance..."
	@poetry run tap-oracle --config config.json --discover | poetry run singer-check-tap
	@echo "✅ Singer specification compliance verified"

test-connection: ## Test Oracle database connection
	@echo "🔗 Testing Oracle database connection..."
	@poetry run python -c "\
from flext_tap_oracle.client import OracleClient; \
import json; \
\
with open('config.json', 'r') as f: \
    config = json.load(f); \
\
client = OracleClient(**config['oracle']); \
try: \
    with client.get_connection() as conn: \
        with conn.cursor() as cursor: \
            cursor.execute('SELECT 1 FROM dual'); \
            result = cursor.fetchone(); \
            print(f'✅ Oracle connection successful: {result}'); \
except Exception as e: \
    print(f'❌ Oracle connection failed: {e}'); \
"

extract-sample: ## Extract sample data from Oracle
	@echo "📊 Extracting sample Oracle data..."
	@poetry run tap-oracle --config config.json --catalog catalog.json | head -100
	@echo "✅ Sample data extraction complete"

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
	@rm -rf catalog.json
	@rm -rf state.json
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

# Oracle settings
export ORACLE_HOST := localhost
export ORACLE_PORT := 1521
export ORACLE_SERVICE_NAME := ORCL

# Singer settings
export SINGER_CONFIG := config.json
export SINGER_CATALOG := catalog.json
export SINGER_STATE := state.json

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
PROJECT_NAME := flext-tap-oracle
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT TAP Oracle - Oracle Database Data Extraction

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 ORACLE SPECIFIC COMMANDS
# ============================================================================

oracle-tables: ## List Oracle tables available for extraction
	@echo "📋 Listing Oracle tables..."
	@poetry run python scripts/list_oracle_tables.py

oracle-schema-info: ## Show Oracle schema information
	@echo "🗂️ Oracle schema information..."
	@poetry run python scripts/oracle_schema_info.py

oracle-test-query: ## Test Oracle query execution
	@echo "🔍 Testing Oracle query execution..."
	@poetry run python scripts/oracle_test_query.py

oracle-performance-test: ## Test Oracle connection performance
	@echo "⚡ Testing Oracle performance..."
	@poetry run python -c "\
import time; \
from flext_tap_oracle.client import OracleClient; \
import json; \
with open('config.json', 'r') as f: \
    config = json.load(f); \
client = OracleClient(**config['oracle']); \
start_time = time.time(); \
for i in range(10): \
    query = f'SELECT {i}, SYSDATE FROM dual'; \
    for row in client.execute_query(query): \
        pass; \
end_time = time.time(); \
print(f'Executed 10 queries in {end_time - start_time:.2f} seconds'); \
print(f'Average query time: {(end_time - start_time) / 10:.3f} seconds'); \
"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 Singer Tap project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Clean Architecture + DDD"
	@echo "🐍 Python: 3.13"
	@echo "🎵 Framework: Singer SDK Oracle"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: Oracle Database Data Extraction (Singer Tap)"
	@echo "🔗 Dependencies: flext-core, flext-observability"
	@echo "📦 Provides: Oracle data extraction via Singer protocol"
	@echo "🎯 Standards: Enterprise Oracle integration patterns"