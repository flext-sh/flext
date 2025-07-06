# ═══════════════════════════════════════════════════════════════════════════
# FLEXT PYTHON PROJECT TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Standard Python development workflow for FLEXT projects
# Usage: include $(FLEXT_ROOT)/templates/makefiles/python/python.mk
# Dependencies: templates/makefiles/base/common.mk
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
#  PYTHON PROJECT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Python project specific paths
PYTHON_SRC_DIR := $(SRC_DIR)/$(shell echo $(PROJECT_NAME) | tr '-' '_')
PYTHON_TESTS_DIR := $(TESTS_DIR)
COVERAGE_DIR := $(REPORTS_DIR)/coverage
COVERAGE_THRESHOLD ?= 85

# Python tools
RUFF := $(shell which ruff 2>/dev/null || echo "$(PIP) install ruff && ruff")
BLACK := $(shell which black 2>/dev/null || echo "$(PIP) install black && black")
MYPY := $(shell which mypy 2>/dev/null || echo "$(PIP) install mypy && mypy")
BANDIT := $(shell which bandit 2>/dev/null || echo "$(PIP) install bandit && bandit")
ISORT := $(shell which isort 2>/dev/null || echo "$(PIP) install isort && isort")

# ═══════════════════════════════════════════════════════════════════════════
#  INSTALLATION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

install: ## Install project dependencies
	$(call log_section,Installing Dependencies)
	$(call check_coordination)
	$(call install_with_coordination)
	$(call log_success,Installation complete)

install-dev: ## Install development dependencies
	$(call log_section,Installing Development Dependencies)
	$(call ensure_dir,$(REPORTS_DIR))
	$(if $(POETRY), \
		$(POETRY) install --with dev,test,security 2>/dev/null || $(POETRY) install, \
		$(if $(wildcard pyproject.toml), \
			$(PIP) install -e ".[dev,test,security]" 2>/dev/null || $(PIP) install -e ., \
			$(PIP) install -r requirements-dev.txt 2>/dev/null || $(PIP) install -r requirements.txt 2>/dev/null \
		) \
	)
	$(call log_success,Development dependencies installed)

install-minimal: ## Install only production dependencies
	$(call log_section,Installing Minimal Dependencies)
	$(if $(POETRY), \
		$(POETRY) install --only main, \
		$(if $(wildcard pyproject.toml), \
			$(PIP) install -e ., \
			$(PIP) install -r requirements.txt \
		) \
	)
	$(call log_success,Minimal installation complete)

update-deps: ## Update project dependencies to latest versions
	$(call log_section,Updating Dependencies)
	@if [ -f "poetry.lock" ]; then \
		echo "$(CYAN)ℹ Using Poetry for dependency management$(RESET)"; \
		$(POETRY) update && $(call log_success,Poetry dependencies updated); \
	elif [ -f "pyproject.toml" ] && grep -q "poetry" pyproject.toml; then \
		echo "$(CYAN)ℹ Poetry project detected$(RESET)"; \
		$(POETRY) install && $(call log_success,Poetry dependencies installed); \
	elif [ -f "pyproject.toml" ]; then \
		echo "$(CYAN)ℹ Using pip with pyproject.toml$(RESET)"; \
		$(PIP) install --upgrade pip && \
		$(PIP) install -e . --upgrade && \
		$(call log_success,pip dependencies updated); \
	elif [ -f "requirements.txt" ]; then \
		echo "$(CYAN)ℹ Using pip with requirements.txt$(RESET)"; \
		$(PIP) install --upgrade pip && \
		$(PIP) install -r requirements.txt --upgrade && \
		$(call log_success,requirements.txt updated); \
	else \
		$(call log_warning,No dependency management found); \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  TESTING TARGETS
# ═══════════════════════════════════════════════════════════════════════════

test: ## Run all tests with coverage
	$(call log_section,Running Tests)
	$(call ensure_dir,$(COVERAGE_DIR))
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) \
			--cov=$(PYTHON_SRC_DIR) \
			--cov-report=term-missing:skip-covered \
			--cov-report=html:$(COVERAGE_DIR) \
			--cov-report=xml:$(REPORTS_DIR)/coverage.xml \
			--cov-fail-under=$(COVERAGE_THRESHOLD) \
			--junitxml=$(REPORTS_DIR)/pytest.xml \
			-v; \
	else \
		$(call log_warning,No tests directory found at $(PYTHON_TESTS_DIR)); \
	fi
	$(call log_success,Tests completed)

test-unit: ## Run unit tests only
	$(call log_section,Running Unit Tests)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "not integration and not e2e" -v; \
	else \
		$(call log_warning,No tests directory found); \
	fi
	$(call log_success,Unit tests completed)

test-integration: ## Run integration tests only
	$(call log_section,Running Integration Tests)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "integration" -v; \
	else \
		$(call log_warning,No tests directory found); \
	fi
	$(call log_success,Integration tests completed)

test-fast: ## Run tests without coverage (fast)
	$(call log_section,Running Fast Tests)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -x --tb=short; \
	else \
		$(call log_warning,No tests directory found); \
	fi
	$(call log_success,Fast tests completed)

test-watch: ## Run tests in watch mode
	$(call log_section,Running Tests in Watch Mode)
	@if command -v ptw >/dev/null 2>&1; then \
		ptw --runner "$(PYTHON) -m pytest --tb=short"; \
	else \
		$(call log_warning,pytest-watch not installed. Install with: pip install pytest-watch); \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  CODE QUALITY TARGETS
# ═══════════════════════════════════════════════════════════════════════════

lint: ## Run linting checks
	$(call log_section,Running Linting)
	@if [ -d "$(PYTHON_SRC_DIR)" ] || [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m ruff check . --output-format=full; \
	else \
		$(call log_warning,No Python source files found); \
	fi
	$(call log_success,Linting completed)

lint-fix: ## Fix linting issues automatically
	$(call log_section,Fixing Linting Issues)
	@if [ -d "$(PYTHON_SRC_DIR)" ] || [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m ruff check . --fix; \
		$(call log_success,Linting fixes applied); \
	else \
		$(call log_warning,No Python source files found); \
	fi

format: ## Format code with black and isort
	$(call log_section,Formatting Code)
	@if [ -d "$(PYTHON_SRC_DIR)" ] || [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m black . 2>/dev/null || true; \
		$(PYTHON) -m isort . 2>/dev/null || true; \
		$(call log_success,Code formatting completed); \
	else \
		$(call log_warning,No Python source files found); \
	fi

format-check: ## Check code formatting without changes
	$(call log_section,Checking Code Format)
	@if [ -d "$(PYTHON_SRC_DIR)" ] || [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m black . --check; \
		$(PYTHON) -m isort . --check-only; \
	else \
		$(call log_warning,No Python source files found); \
	fi
	$(call log_success,Format check completed)

type-check: ## Run type checking with mypy
	$(call log_section,Running Type Checking)
	@if [ -d "$(PYTHON_SRC_DIR)" ]; then \
		$(PYTHON) -m mypy $(PYTHON_SRC_DIR) --strict --show-error-codes 2>/dev/null || \
		$(PYTHON) -m mypy $(PYTHON_SRC_DIR) 2>/dev/null || \
		$(call log_warning,MyPy not available or no type annotations); \
	else \
		$(call log_warning,No Python source directory found); \
	fi
	$(call log_success,Type checking completed)

security: ## Run security checks
	$(call log_section,Running Security Checks)
	$(call ensure_dir,$(REPORTS_DIR))
	@if [ -d "$(PYTHON_SRC_DIR)" ]; then \
		$(PYTHON) -m bandit -r $(PYTHON_SRC_DIR) -f json -o $(REPORTS_DIR)/security.json 2>/dev/null || true; \
		$(PYTHON) -m bandit -r $(PYTHON_SRC_DIR) 2>/dev/null || $(call log_warning,Bandit not available); \
	else \
		$(call log_warning,No Python source directory found); \
	fi
	@if command -v safety >/dev/null 2>&1; then \
		safety check --json --output $(REPORTS_DIR)/safety.json 2>/dev/null || true; \
	fi
	$(call log_success,Security checks completed)

quality: lint type-check security ## Run all quality checks
	$(call log_success,All quality checks completed)

quality-fix: lint-fix format ## Fix all auto-fixable quality issues
	$(call log_success,All quality fixes applied)

# ═══════════════════════════════════════════════════════════════════════════
#  BUILD AND PACKAGING TARGETS
# ═══════════════════════════════════════════════════════════════════════════

build: ## Build the package
	$(call log_section,Building Package)
	$(call ensure_dir,$(DIST_DIR))
	@if [ -f "pyproject.toml" ]; then \
		$(PYTHON) -m build . 2>/dev/null || \
		$(PYTHON) setup.py sdist bdist_wheel 2>/dev/null || \
		$(call log_warning,Build tools not available); \
	else \
		$(call log_warning,No pyproject.toml found); \
	fi
	$(call log_success,Package built)

build-check: ## Check if package can be built
	$(call log_section,Checking Package Build)
	@if [ -f "pyproject.toml" ]; then \
		$(POETRY) check 2>/dev/null || \
		$(PYTHON) -m build . --check 2>/dev/null || \
		$(call log_warning,Build check not available); \
	else \
		$(call log_warning,No pyproject.toml found); \
	fi
	$(call log_success,Build check completed)

# ═══════════════════════════════════════════════════════════════════════════
#  CLEANUP TARGETS
# ═══════════════════════════════════════════════════════════════════════════

clean: ## Clean build artifacts and cache
	$(call cleanup_python_artifacts)

clean-all: clean ## Clean everything including virtual environments
	$(call log_section,Deep Cleaning)
	@rm -rf .venv venv env 2>/dev/null || true
	@rm -rf node_modules 2>/dev/null || true
	$(call log_success,Deep cleaning completed)

clean-reports: ## Clean test and coverage reports
	$(call log_section,Cleaning Reports)
	@rm -rf $(REPORTS_DIR) 2>/dev/null || true
	$(call log_success,Reports cleaned)

# ═══════════════════════════════════════════════════════════════════════════
#  DEVELOPMENT WORKFLOW TARGETS
# ═══════════════════════════════════════════════════════════════════════════

dev-setup: install-dev ## Complete development setup
	$(call log_section,Setting Up Development Environment)
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install 2>/dev/null || true; \
		$(call log_success,Pre-commit hooks installed); \
	fi
	$(call log_success,Development environment ready)

dev-check: validate quality test ## Run all development checks
	$(call log_success,All development checks passed)

dev-fix: quality-fix ## Fix all auto-fixable development issues
	$(call log_success,All development issues fixed)

# ═══════════════════════════════════════════════════════════════════════════
#  CONTINUOUS INTEGRATION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

ci-install: install-minimal ## CI: Install dependencies
	$(call log_success,CI installation completed)

ci-test: test ## CI: Run tests
	$(call log_success,CI tests completed)

ci-quality: quality ## CI: Run quality checks
	$(call log_success,CI quality checks completed)

ci-build: build ## CI: Build package
	$(call log_success,CI build completed)

ci-all: ci-install ci-quality ci-test ci-build ## CI: Run complete pipeline
	$(call log_success,CI pipeline completed)

# ═══════════════════════════════════════════════════════════════════════════
#  PHONY TARGETS
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: install install-dev install-minimal update-deps
.PHONY: test test-unit test-integration test-fast test-watch
.PHONY: lint lint-fix format format-check type-check security quality quality-fix
.PHONY: build build-check
.PHONY: clean clean-all clean-reports
.PHONY: dev-setup dev-check dev-fix
.PHONY: ci-install ci-test ci-quality ci-build ci-all
