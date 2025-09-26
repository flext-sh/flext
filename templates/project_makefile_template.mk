# FLEXT Project Makefile Template - Testing Section
# Copy these targets to your project's Makefile
#
# Usage:
# 1. Set these variables at the top of your Makefile:
#    PROJECT_NAME := your-project-name
#    PYTHON_VERSION := 3.13
#    POETRY := poetry
#    SRC_DIR := src
#    TESTS_DIR := tests
#    COV_DIR := your_package_name  # Same as src/your_package_name
#    MIN_COVERAGE := 75  # Adjust based on project type (see FLEXT_TESTING_STANDARDS.md)
#
# 2. Copy the testing targets below to your Makefile
# 3. Adjust MIN_COVERAGE based on your project type:
#    - Foundation (flext-core): 75% minimum, 85% target
#    - Core Infrastructure: 75-80%
#    - Enterprise Projects: 85-90%
#    - Singer/DBT Projects: 65-75%
#
# Version: 1.0.0
# Standards: FLEXT_TESTING_STANDARDS.md

# =============================================================================
# TESTING TARGETS (FLEXT STANDARD)
# =============================================================================

.PHONY: test
test: ## Run tests with coverage reporting
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(COV_DIR) --cov-report=term-missing --cov-fail-under=$(MIN_COVERAGE)

.PHONY: test-unit
test-unit: ## Run unit tests only (fast development feedback)
	$(POETRY) run pytest $(TESTS_DIR) -m "not integration" -v

.PHONY: test-integration
test-integration: ## Run integration tests only
	$(POETRY) run pytest $(TESTS_DIR) -m integration -v

.PHONY: test-fast
test-fast: ## Run tests without coverage (fastest execution)
	$(POETRY) run pytest $(TESTS_DIR) -v

.PHONY: test-smoke
test-smoke: ## Run smoke tests for basic validation
	$(POETRY) run pytest $(TESTS_DIR) -m smoke -v

.PHONY: test-slow
test-slow: ## Run slow tests (usually excluded)
	$(POETRY) run pytest $(TESTS_DIR) -m slow -v

.PHONY: test-performance
test-performance: ## Run performance and benchmark tests
	$(POETRY) run pytest $(TESTS_DIR) -m performance -v

.PHONY: test-parallel
test-parallel: ## Run tests in parallel (requires pytest-xdist)
	$(POETRY) run pytest $(TESTS_DIR) -n auto --cov=$(COV_DIR) --cov-report=term-missing

# =============================================================================
# COVERAGE REPORTING
# =============================================================================

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(COV_DIR) --cov-report=html
	@echo "Coverage report generated in htmlcov/"

.PHONY: coverage-xml
coverage-xml: ## Generate XML coverage report (for CI)
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(COV_DIR) --cov-report=xml

.PHONY: coverage-json
coverage-json: ## Generate JSON coverage report
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(COV_DIR) --cov-report=json

.PHONY: coverage-show
coverage-show: ## Show current coverage percentage
	@$(POETRY) run pytest $(TESTS_DIR) --cov=$(COV_DIR) --tb=no -q 2>/dev/null | grep "TOTAL" | awk '{print "Current coverage: " $$4}' || echo "Coverage data not available"

# =============================================================================
# PROJECT-SPECIFIC TEST TARGETS (CUSTOMIZE AS NEEDED)
# =============================================================================

# For Singer projects (uncomment if applicable):
# .PHONY: test-tap
# test-tap: ## Run Singer tap tests
# 	$(POETRY) run pytest $(TESTS_DIR) -m tap -v

# .PHONY: test-target
# test-target: ## Run Singer target tests
# 	$(POETRY) run pytest $(TESTS_DIR) -m target -v

# For DBT projects (uncomment if applicable):
# .PHONY: test-dbt
# test-dbt: ## Run DBT transformation tests
# 	$(POETRY) run pytest $(TESTS_DIR) -m dbt -v

# For API projects (uncomment if applicable):
# .PHONY: test-api
# test-api: ## Run API endpoint tests
# 	$(POETRY) run pytest $(TESTS_DIR) -m api -v

# For CLI projects (uncomment if applicable):
# .PHONY: test-cli
# test-cli: ## Run CLI interface tests
# 	$(POETRY) run pytest $(TESTS_DIR) -m cli -v

# For Oracle integration projects (uncomment if applicable):
# .PHONY: test-oracle
# test-oracle: ## Run Oracle database tests
# 	$(POETRY) run pytest $(TESTS_DIR) -m oracle -v

# =============================================================================
# TESTING UTILITIES
# =============================================================================

.PHONY: test-debug
test-debug: ## Run tests with debugging output
	$(POETRY) run pytest $(TESTS_DIR) -v -s --tb=long

.PHONY: test-failed
test-failed: ## Run only previously failed tests
	$(POETRY) run pytest $(TESTS_DIR) --lf -v

.PHONY: test-collect
test-collect: ## Show available tests without running them
	$(POETRY) run pytest $(TESTS_DIR) --collect-only

.PHONY: test-markers
test-markers: ## Show available test markers
	$(POETRY) run pytest --markers

.PHONY: test-fixtures
test-fixtures: ## Show available test fixtures
	$(POETRY) run pytest --fixtures

# =============================================================================
# QUALITY GATES INTEGRATION
# =============================================================================

.PHONY: validate
validate: lint type-check security test ## Run all quality gates including tests

.PHONY: check
check: lint type-check ## Quick health check (without tests)

.PHONY: test-quality
test-quality: ## Validate testing standards compliance
	@if [ -f "../scripts/testing_quality_gates.sh" ]; then \
		../scripts/testing_quality_gates.sh --project $(PROJECT_NAME); \
	else \
		echo "Testing quality gates script not found. Run from workspace root."; \
	fi

# =============================================================================
# CLEANUP
# =============================================================================

.PHONY: clean-test
clean-test: ## Clean test artifacts
	rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml coverage.json
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# =============================================================================
# HELP INTEGRATION
# =============================================================================

# Add this to your existing help target or create one:
.PHONY: help-test
help-test: ## Show testing-related commands
	@echo "Testing Commands:"
	@grep -E '^[a-zA-Z_-]*test[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""
	@echo "Coverage Commands:"
	@grep -E '^[a-zA-Z_-]*coverage[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'