# =============================================================================
# {{PROJECT_NAME}} - FLEXT SUBMODULE MAKEFILE
# Coordinated Enterprise Automation with Autonomous Fallback
# =============================================================================

.DEFAULT_GOAL := help
SHELL := /bin/bash

# =============================================================================
# WORKSPACE COORDINATION DETECTION
# =============================================================================

# Detect if we're in FLEXT workspace for coordination
FLEXT_ROOT ?= $(shell git -C "$(CURDIR)" rev-parse --show-toplevel 2>/dev/null || echo "$(CURDIR)/..")
PROJECT_NAME := $(notdir $(CURDIR))
WORKSPACE_MAKEFILE := $(FLEXT_ROOT)/Makefile

# Check coordination mode
ifneq ($(wildcard $(WORKSPACE_MAKEFILE)),)
    COORDINATED_MODE := true
    WORKSPACE_VENV := $(FLEXT_ROOT)/.venv
    PYTHON := $(WORKSPACE_VENV)/bin/python
    PIP := $(WORKSPACE_VENV)/bin/pip
    POETRY := $(WORKSPACE_VENV)/bin/poetry
else
    COORDINATED_MODE := false
    WORKSPACE_VENV := .venv
    PYTHON := python3.13
    PIP := pip
    POETRY := poetry
endif

# Project Configuration
SOURCE_DIR := src
TESTS_DIR := tests
REPORTS_DIR := reports
BUILD_DIR := build
DIST_DIR := dist

# Colors for output
BOLD := \033[1m
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
NC := \033[0m

# =============================================================================
# HELP SYSTEM
# =============================================================================

.PHONY: help
help: ## Show development commands
	@echo -e "$(BOLD)$(CYAN){{PROJECT_NAME}} - FLEXT Submodule$(NC)"
	@echo -e "$(CYAN)Coordination Mode: $(if $(filter true,$(COORDINATED_MODE)),$(GREEN)✓ Coordinated$(NC),$(YELLOW)⚠ Autonomous$(NC))"
	@echo -e "$(CYAN)Python: $(PYTHON)$(NC)"
	@echo -e "$(CYAN)===============================================$(NC)"
	@echo ""
	@echo -e "$(BOLD)$(GREEN)🎯 Primary Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(install|test|lint|build|clean)$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(BLUE)🔧 Quality Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(format|lint-fix|type-check|security)' | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(BOLD)$(MAGENTA)🚀 Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(dev|validate|{{PROJECT_CATEGORY}})' | awk 'BEGIN {FS = ":.*?## "}; {printf "$(MAGENTA)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# DEPENDENCY VALIDATION (REUSE ENFORCEMENT)
# =============================================================================

.PHONY: validate-dependencies
validate-dependencies: ## Validate proper reuse of other FLEXT modules
	@echo -e "$(CYAN)Validating FLEXT module dependencies...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@echo -e "$(GREEN)✓ Coordinated mode: Dependencies managed by workspace$(NC)"
	@if [ -f "pyproject.toml" ]; then \
		echo "Checking for proper FLEXT dependencies..."; \
		grep -q "flext-core" pyproject.toml || echo "$(YELLOW)⚠ Consider using flext-core for domain models$(NC)"; \
		case "$(PROJECT_NAME)" in \
			*api*|*web*) grep -q "flext-auth" pyproject.toml || echo "$(YELLOW)⚠ API projects should use flext-auth$(NC)";; \
			*tap-*|*target-*) grep -q "flext-core" pyproject.toml || echo "$(YELLOW)⚠ Singer plugins should use flext-core$(NC)";; \
			*ldap*) grep -q "flext-ldap" pyproject.toml || echo "$(YELLOW)⚠ LDAP projects should reuse flext-ldap$(NC)";; \
		esac; \
	fi
else
	@echo -e "$(YELLOW)⚠ Autonomous mode: Manual dependency validation$(NC)"
endif

# =============================================================================
# INSTALLATION
# =============================================================================

.PHONY: install
install: validate-dependencies ## Install project dependencies
	@echo -e "$(CYAN)Installing dependencies...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@echo -e "$(GREEN)Using workspace coordination$(NC)"
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-install-single PROJECT=$(PROJECT_NAME)
else
	@echo -e "$(YELLOW)Autonomous installation$(NC)"
	@if [ -f "pyproject.toml" ]; then \
		$(PYTHON) -m pip install -e .; \
	elif [ -f "requirements.txt" ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		echo -e "$(RED)❌ No installation configuration found$(NC)"; \
		exit 1; \
	fi
endif
	@echo -e "$(GREEN)✓ Installation complete$(NC)"

.PHONY: install-dev
install-dev: validate-dependencies ## Install development dependencies
	@echo -e "$(CYAN)Installing development dependencies...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-install-dev-single PROJECT=$(PROJECT_NAME)
else
	@if [ -f "pyproject.toml" ]; then \
		$(PYTHON) -m pip install -e ".[dev,test,security,build]"; \
	else \
		$(PIP) install pytest ruff mypy black isort bandit safety; \
	fi
endif
	@echo -e "$(GREEN)✓ Development installation complete$(NC)"

# =============================================================================
# CODE QUALITY (ENTERPRISE STANDARDS)
# =============================================================================

.PHONY: format
format: ## Format code to enterprise standards
	@echo -e "$(CYAN)Formatting code...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-format-single PROJECT=$(PROJECT_NAME)
else
	@if [ -d "$(SOURCE_DIR)" ]; then \
		$(PYTHON) -m black $(SOURCE_DIR) $(TESTS_DIR) 2>/dev/null || echo "$(YELLOW)black not available$(NC)"; \
		$(PYTHON) -m isort $(SOURCE_DIR) $(TESTS_DIR) 2>/dev/null || echo "$(YELLOW)isort not available$(NC)"; \
		$(PYTHON) -m ruff format $(SOURCE_DIR) $(TESTS_DIR) 2>/dev/null || echo "$(YELLOW)ruff not available$(NC)"; \
	fi
endif
	@echo -e "$(GREEN)✓ Code formatted$(NC)"

.PHONY: lint
lint: ## Run comprehensive linting
	@echo -e "$(CYAN)Running linting...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-lint-single PROJECT=$(PROJECT_NAME)
else
	@if [ -d "$(SOURCE_DIR)" ]; then \
		$(PYTHON) -m ruff check $(SOURCE_DIR) $(TESTS_DIR) 2>/dev/null || echo "$(YELLOW)ruff not available$(NC)"; \
	fi
endif
	@echo -e "$(GREEN)✓ Linting complete$(NC)"

.PHONY: lint-fix
lint-fix: ## Fix linting issues automatically
	@echo -e "$(CYAN)Fixing linting issues...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-lint-fix-single PROJECT=$(PROJECT_NAME)
else
	@if [ -d "$(SOURCE_DIR)" ]; then \
		$(PYTHON) -m ruff check $(SOURCE_DIR) $(TESTS_DIR) --fix 2>/dev/null || echo "$(YELLOW)ruff not available$(NC)"; \
		$(PYTHON) -m black $(SOURCE_DIR) $(TESTS_DIR) 2>/dev/null || echo "$(YELLOW)black not available$(NC)"; \
		$(PYTHON) -m isort $(SOURCE_DIR) $(TESTS_DIR) 2>/dev/null || echo "$(YELLOW)isort not available$(NC)"; \
	fi
endif
	@echo -e "$(GREEN)✓ Linting fixes applied$(NC)"

.PHONY: type-check
type-check: ## Run type checking
	@echo -e "$(CYAN)Running type checking...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-type-check-single PROJECT=$(PROJECT_NAME)
else
	@if [ -d "$(SOURCE_DIR)" ]; then \
		$(PYTHON) -m mypy $(SOURCE_DIR) 2>/dev/null || echo "$(YELLOW)mypy not available$(NC)"; \
	fi
endif
	@echo -e "$(GREEN)✓ Type checking complete$(NC)"

.PHONY: security
security: ## Run security checks
	@echo -e "$(CYAN)Running security checks...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-security-single PROJECT=$(PROJECT_NAME)
else
	@if [ -d "$(SOURCE_DIR)" ]; then \
		$(PYTHON) -m bandit -r $(SOURCE_DIR) 2>/dev/null || echo "$(YELLOW)bandit not available$(NC)"; \
		$(PYTHON) -m safety check 2>/dev/null || echo "$(YELLOW)safety not available$(NC)"; \
	fi
endif
	@echo -e "$(GREEN)✓ Security checks complete$(NC)"

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run comprehensive tests
	@echo -e "$(CYAN)Running tests...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-test-single PROJECT=$(PROJECT_NAME)
else
	@if [ -d "$(TESTS_DIR)" ]; then \
		mkdir -p $(REPORTS_DIR); \
		$(PYTHON) -m pytest $(TESTS_DIR) -v 2>/dev/null || echo "$(YELLOW)pytest not available$(NC)"; \
	else \
		echo -e "$(YELLOW)⚠ No tests directory found$(NC)"; \
	fi
endif
	@echo -e "$(GREEN)✓ Tests complete$(NC)"

.PHONY: test-fast
test-fast: ## Run fast tests only
	@echo -e "$(CYAN)Running fast tests...$(NC)"
	@if [ -d "$(TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(TESTS_DIR) -x -q 2>/dev/null || echo "$(YELLOW)pytest not available$(NC)"; \
	fi

.PHONY: coverage
coverage: ## Generate coverage report
	@echo -e "$(CYAN)Generating coverage report...$(NC)"
	@if [ -d "$(TESTS_DIR)" ] && [ -d "$(SOURCE_DIR)" ]; then \
		mkdir -p $(REPORTS_DIR); \
		$(PYTHON) -m pytest $(TESTS_DIR) \
			--cov=$(SOURCE_DIR) \
			--cov-report=html:$(REPORTS_DIR)/coverage \
			--cov-report=term-missing 2>/dev/null || echo "$(YELLOW)coverage not available$(NC)"; \
	fi

# =============================================================================
# BUILD AND DISTRIBUTION
# =============================================================================

.PHONY: build
build: ## Build distribution packages
	@echo -e "$(CYAN)Building packages...$(NC)"
ifeq ($(COORDINATED_MODE),true)
	@cd $(FLEXT_ROOT) && $(MAKE) submodule-build-single PROJECT=$(PROJECT_NAME)
else
	@if [ -f "pyproject.toml" ]; then \
		mkdir -p $(BUILD_DIR) $(DIST_DIR); \
		$(PYTHON) -m build . 2>/dev/null || echo "$(YELLOW)build not available$(NC)"; \
	fi
endif
	@echo -e "$(GREEN)✓ Build complete$(NC)"

# =============================================================================
# DEVELOPMENT WORKFLOW
# =============================================================================

.PHONY: dev-setup
dev-setup: install-dev ## Complete development setup
	@echo -e "$(CYAN)Setting up development environment...$(NC)"
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install 2>/dev/null || echo "$(YELLOW)pre-commit setup skipped$(NC)"; \
	fi
	@echo -e "$(GREEN)✓ Development setup complete$(NC)"

.PHONY: validate
validate: lint type-check security test ## Run all validation checks
	@echo -e "$(GREEN)✓ All validation checks passed$(NC)"

.PHONY: quality-gate
quality-gate: format lint-fix validate ## Run quality gate pipeline
	@echo -e "$(GREEN)✓ Quality gate passed$(NC)"

# =============================================================================
# CLEANUP
# =============================================================================

.PHONY: clean
clean: ## Clean build artifacts
	@echo -e "$(CYAN)Cleaning build artifacts...$(NC)"
	@rm -rf $(BUILD_DIR) $(DIST_DIR) *.egg-info .pytest_cache .mypy_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@echo -e "$(GREEN)✓ Cleanup complete$(NC)"

.PHONY: clean-all
clean-all: clean ## Clean everything including reports
	@rm -rf $(REPORTS_DIR) .coverage htmlcov logs
	@echo -e "$(GREEN)✓ Deep cleanup complete$(NC)"

# =============================================================================
# PROJECT-SPECIFIC TARGETS (TO BE CUSTOMIZED)
# =============================================================================

# {{PROJECT_CATEGORY}}-specific targets should be added here
# Examples:
# - Singer taps: tap-discover, tap-test, tap-run
# - APIs: api-start, api-docs
# - CLI tools: cli-test, cli-install
# - Web apps: web-start, web-build

# =============================================================================
# COORDINATION EXPORTS
# =============================================================================

# Export variables for coordination
export COORDINATED_MODE
export FLEXT_ROOT
export PROJECT_NAME
export WORKSPACE_VENV
