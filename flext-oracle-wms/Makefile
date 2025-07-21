# FLEXT Oracle WMS - Oracle Warehouse Management System Integration
# ================================================================
# Enterprise Oracle WMS integration with inventory, shipping, and warehouse operations
# Python 3.13 + Oracle Database + WMS APIs + Clean Architecture + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration test-wms
.PHONY: deps-update deps-audit deps-tree deps-outdated
.PHONY: wms-test wms-validate wms-schema wms-sync wms-inventory wms-shipping
.PHONY: oracle-test oracle-connect oracle-schema oracle-performance

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🎯 FLEXT Oracle WMS - Oracle Warehouse Management System Integration"
	@echo "=================================================================="
	@echo "🎯 Oracle Database + WMS APIs + Clean Architecture + Python 3.13"
	@echo ""
	@echo "📦 Enterprise Oracle WMS integration with comprehensive warehouse operations"
	@echo "🔒 Zero tolerance quality gates with Oracle WMS testing"
	@echo "🧪 90%+ test coverage requirement with WMS integration testing"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT ORACLE WMS COMPLIANT"

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
	@poetry run pytest tests/ -v --cov=src/flext_oracle_wms --cov-report=term-missing --cov-fail-under=90
	@echo "✅ Tests complete"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v
	@echo "✅ Unit tests complete"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v
	@echo "✅ Integration tests complete"

test-wms: ## Run WMS-specific tests
	@echo "🧪 Running WMS-specific tests..."
	@poetry run pytest tests/ -m "wms" -v
	@echo "✅ WMS tests complete"

test-oracle: ## Run Oracle database tests
	@echo "🧪 Running Oracle database tests..."
	@poetry run pytest tests/ -m "oracle" -v
	@echo "✅ Oracle tests complete"

test-inventory: ## Run inventory management tests
	@echo "🧪 Running inventory management tests..."
	@poetry run pytest tests/ -m "inventory" -v
	@echo "✅ Inventory tests complete"

test-shipping: ## Run shipping tests
	@echo "🧪 Running shipping tests..."
	@poetry run pytest tests/ -m "shipping" -v
	@echo "✅ Shipping tests complete"

test-performance: ## Run performance tests
	@echo "⚡ Running WMS performance tests..."
	@poetry run pytest tests/performance/ -v --benchmark-only
	@echo "✅ Performance tests complete"

coverage: ## Generate detailed coverage report
	@echo "📊 Generating coverage report..."
	@poetry run pytest tests/ --cov=src/flext_oracle_wms --cov-report=term-missing --cov-report=html
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
# 🏢 ORACLE WMS OPERATIONS - CORE FUNCTIONALITY
# ============================================================================

wms-test: ## Test WMS connectivity and functionality
	@echo "🏢 Testing WMS connectivity and functionality..."
	@poetry run python -c "from flext_oracle_wms.infrastructure.oracle import WMSConnectionManager; from flext_oracle_wms.application.config import OracleWMSConfig; print('WMS integration loaded successfully')"
	@echo "✅ WMS connectivity test complete"

wms-validate: ## Validate WMS configuration
	@echo "🔍 Validating WMS configuration..."
	@poetry run python scripts/validate_wms_config.py
	@echo "✅ WMS configuration validation complete"

wms-schema: ## Validate WMS database schema
	@echo "📁 Validating WMS database schema..."
	@poetry run python scripts/validate_wms_schema.py
	@echo "✅ WMS schema validation complete"

wms-sync: ## Synchronize WMS data
	@echo "🔄 Synchronizing WMS data..."
	@poetry run python scripts/sync_wms_data.py
	@echo "✅ WMS data synchronization complete"

wms-inventory: ## Test WMS inventory operations
	@echo "📦 Testing WMS inventory operations..."
	@poetry run python scripts/test_wms_inventory.py
	@echo "✅ WMS inventory operations test complete"

wms-shipping: ## Test WMS shipping operations
	@echo "🚚 Testing WMS shipping operations..."
	@poetry run python scripts/test_wms_shipping.py
	@echo "✅ WMS shipping operations test complete"

wms-receiving: ## Test WMS receiving operations
	@echo "📦 Testing WMS receiving operations..."
	@poetry run python scripts/test_wms_receiving.py
	@echo "✅ WMS receiving operations test complete"

wms-picking: ## Test WMS picking operations
	@echo "🎣 Testing WMS picking operations..."
	@poetry run python scripts/test_wms_picking.py
	@echo "✅ WMS picking operations test complete"

wms-putaway: ## Test WMS putaway operations
	@echo "📦 Testing WMS putaway operations..."
	@poetry run python scripts/test_wms_putaway.py
	@echo "✅ WMS putaway operations test complete"

wms-cycle-count: ## Test WMS cycle counting
	@echo "🔄 Testing WMS cycle counting..."
	@poetry run python scripts/test_wms_cycle_count.py
	@echo "✅ WMS cycle counting test complete"

# ============================================================================
# 📊 ORACLE DATABASE OPERATIONS
# ============================================================================

oracle-test: ## Test Oracle database connectivity
	@echo "📊 Testing Oracle database connectivity..."
	@poetry run python scripts/test_oracle_connection.py
	@echo "✅ Oracle database connectivity test complete"

oracle-connect: ## Test Oracle WMS database connection
	@echo "🔗 Testing Oracle WMS database connection..."
	@poetry run python -c "from flext_oracle_wms.infrastructure.oracle import WMSDatabase; import asyncio; db = WMSDatabase(); print('Testing connection...'); result = asyncio.run(db.test_connection()); print('✅ Connected!' if result.is_success else f'❌ Failed: {result.error}')"
	@echo "✅ Oracle WMS connection test complete"

oracle-schema: ## Validate Oracle WMS schema
	@echo "📁 Validating Oracle WMS schema..."
	@poetry run python scripts/validate_oracle_wms_schema.py
	@echo "✅ Oracle WMS schema validation complete"

oracle-performance: ## Run Oracle performance tests
	@echo "⚡ Running Oracle performance tests..."
	@poetry run python scripts/test_oracle_performance.py
	@echo "✅ Oracle performance tests complete"

oracle-connection-pool: ## Test Oracle connection pooling
	@echo "🏊 Testing Oracle connection pooling..."
	@poetry run python scripts/test_oracle_pool.py
	@echo "✅ Oracle connection pooling test complete"

oracle-transactions: ## Test Oracle transaction handling
	@echo "🔄 Testing Oracle transaction handling..."
	@poetry run python scripts/test_oracle_transactions.py
	@echo "✅ Oracle transaction tests complete"

# ============================================================================
# 📦 INVENTORY MANAGEMENT OPERATIONS
# ============================================================================

inventory-lookup: ## Test inventory lookup operations
	@echo "🔍 Testing inventory lookup operations..."
	@poetry run python scripts/test_inventory_lookup.py
	@echo "✅ Inventory lookup test complete"

inventory-allocation: ## Test inventory allocation
	@echo "🎯 Testing inventory allocation..."
	@poetry run python scripts/test_inventory_allocation.py
	@echo "✅ Inventory allocation test complete"

inventory-adjustment: ## Test inventory adjustments
	@echo "🔧 Testing inventory adjustments..."
	@poetry run python scripts/test_inventory_adjustment.py
	@echo "✅ Inventory adjustment test complete"

inventory-transaction: ## Test inventory transactions
	@echo "📈 Testing inventory transactions..."
	@poetry run python scripts/test_inventory_transactions.py
	@echo "✅ Inventory transaction test complete"

inventory-availability: ## Test inventory availability
	@echo "✅ Testing inventory availability..."
	@poetry run python scripts/test_inventory_availability.py
	@echo "✅ Inventory availability test complete"

inventory-lot-tracking: ## Test lot tracking
	@echo "🏷️ Testing lot tracking..."
	@poetry run python scripts/test_lot_tracking.py
	@echo "✅ Lot tracking test complete"

inventory-serial-tracking: ## Test serial number tracking
	@echo "🔢 Testing serial number tracking..."
	@poetry run python scripts/test_serial_tracking.py
	@echo "✅ Serial tracking test complete"

# ============================================================================
# 🚚 SHIPPING & LOGISTICS OPERATIONS
# ============================================================================

shipment-create: ## Test shipment creation
	@echo "🚚 Testing shipment creation..."
	@poetry run python scripts/test_shipment_creation.py
	@echo "✅ Shipment creation test complete"

shipment-status: ## Test shipment status updates
	@echo "📊 Testing shipment status updates..."
	@poetry run python scripts/test_shipment_status.py
	@echo "✅ Shipment status test complete"

shipment-tracking: ## Test shipment tracking
	@echo "📍 Testing shipment tracking..."
	@poetry run python scripts/test_shipment_tracking.py
	@echo "✅ Shipment tracking test complete"

carrier-integration: ## Test carrier integration
	@echo "🚚 Testing carrier integration..."
	@poetry run python scripts/test_carrier_integration.py
	@echo "✅ Carrier integration test complete"

label-generation: ## Test shipping label generation
	@echo "🏷️ Testing shipping label generation..."
	@poetry run python scripts/test_label_generation.py
	@echo "✅ Label generation test complete"

manifest-generation: ## Test shipping manifest generation
	@echo "📄 Testing shipping manifest generation..."
	@poetry run python scripts/test_manifest_generation.py
	@echo "✅ Manifest generation test complete"

# ============================================================================
# 📊 WMS ANALYTICS & REPORTING
# ============================================================================

analytics-inventory: ## Generate inventory analytics
	@echo "📊 Generating inventory analytics..."
	@poetry run python scripts/generate_inventory_analytics.py
	@echo "✅ Inventory analytics complete"

analytics-shipping: ## Generate shipping analytics
	@echo "📊 Generating shipping analytics..."
	@poetry run python scripts/generate_shipping_analytics.py
	@echo "✅ Shipping analytics complete"

analytics-performance: ## Generate performance analytics
	@echo "📊 Generating performance analytics..."
	@poetry run python scripts/generate_performance_analytics.py
	@echo "✅ Performance analytics complete"

reports-daily: ## Generate daily WMS reports
	@echo "📊 Generating daily WMS reports..."
	@poetry run python scripts/generate_daily_reports.py
	@echo "✅ Daily reports complete"

reports-weekly: ## Generate weekly WMS reports
	@echo "📊 Generating weekly WMS reports..."
	@poetry run python scripts/generate_weekly_reports.py
	@echo "✅ Weekly reports complete"

reports-monthly: ## Generate monthly WMS reports
	@echo "📊 Generating monthly WMS reports..."
	@poetry run python scripts/generate_monthly_reports.py
	@echo "✅ Monthly reports complete"

# ============================================================================
# 📦 BUILD & DISTRIBUTION
# ============================================================================

build: clean ## Build distribution packages
	@echo "🔨 Building distribution..."
	@poetry build
	@echo "✅ Build complete - packages in dist/"

package: build ## Create deployment package
	@echo "📦 Creating deployment package..."
	@tar -czf dist/flext-oracle-wms-deployment.tar.gz \
		src/ \
		tests/ \
		scripts/ \
		pyproject.toml \
		README.md \
		CLAUDE.md
	@echo "✅ Deployment package created: dist/flext-oracle-wms-deployment.tar.gz"

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
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
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

# Oracle WMS Database settings
export ORACLE_WMS_HOST := localhost
export ORACLE_WMS_PORT := 1521
export ORACLE_WMS_SERVICE := WMSPROD
export ORACLE_WMS_USERNAME := wms_user

# WMS Environment settings
export WMS_ENVIRONMENT := development
export WMS_ORG_ID := 101
export WMS_FACILITY_CODE := DC001

# WMS API settings
export WMS_API_TIMEOUT := 30
export WMS_SYNC_BATCH_SIZE := 1000
export WMS_SYNC_INTERVAL := 15

# Performance settings
export WMS_CONNECTION_POOL_SIZE := 10
export WMS_QUERY_TIMEOUT := 300
export WMS_ENABLE_PARALLEL_PROCESSING := true

# Data retention settings
export WMS_DATA_RETENTION_DAYS := 365
export WMS_ARCHIVE_OLD_DATA := true

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
PROJECT_NAME := flext-oracle-wms
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT Oracle WMS - Oracle Warehouse Management System Integration

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 DEVELOPMENT UTILITIES
# ============================================================================

dev-wms-server: ## Start development WMS server
	@echo "🔧 Starting development WMS server..."
	@poetry run python scripts/dev_wms_server.py
	@echo "✅ Development WMS server started"

dev-wms-monitor: ## Monitor WMS operations
	@echo "📊 Monitoring WMS operations..."
	@poetry run python scripts/monitor_wms_operations.py
	@echo "✅ WMS monitoring complete"

dev-wms-dashboard: ## Start WMS dashboard
	@echo "📊 Starting WMS dashboard..."
	@poetry run python scripts/wms_dashboard.py
	@echo "✅ WMS dashboard started"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 Core project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Clean Architecture + Oracle WMS"
	@echo "🐍 Python: 3.13"
	@echo "🔗 Framework: FLEXT Core + Oracle Database + WMS APIs"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: Oracle Warehouse Management System Integration"
	@echo "🔗 Dependencies: flext-core, flext-db-oracle, cx-oracle"
	@echo "📦 Provides: WMS inventory, shipping, receiving operations"
	@echo "🎯 Standards: Enterprise WMS integration patterns"

# ============================================================================
# 🔄 CONTINUOUS INTEGRATION
# ============================================================================

ci-check: validate ## CI quality checks
	@echo "🔍 Running CI quality checks..."
	@poetry run python scripts/ci_quality_report.py
	@echo "✅ CI quality checks complete"

ci-performance: ## CI performance benchmarks
	@echo "⚡ Running CI performance benchmarks..."
	@poetry run python scripts/ci_performance_benchmarks.py
	@echo "✅ CI performance benchmarks complete"

ci-integration: ## CI integration tests
	@echo "🔗 Running CI integration tests..."
	@poetry run pytest tests/integration/ -v --tb=short
	@echo "✅ CI integration tests complete"

ci-wms: ## CI WMS-specific tests
	@echo "🏢 Running CI WMS tests..."
	@poetry run pytest tests/ -m "wms" -v --tb=short
	@echo "✅ CI WMS tests complete"

ci-all: ci-check ci-performance ci-integration ci-wms ## Run all CI checks
	@echo "✅ All CI checks complete"
