###############################################################################
#  Standard Makefile Template for PyAuto Subprojects
#  Version: 1.0.0
#  
#  This is a self-contained Makefile template that does not depend on the
#  parent pyauto repository. Copy this to your project and customize as needed.
###############################################################################

# ─────────────────────────[ Configuration ]─────────────────────────────────
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ─────────────────────────[ Project Info ]──────────────────────────────────
PROJECT_NAME := $(notdir $(CURDIR))
SRC_DIR      := src
TESTS_DIR    := tests
DOCS_DIR     := docs

# ─────────────────────────[ Python Tools ]──────────────────────────────────
# Check if Poetry is available, otherwise use pip
ifeq ($(shell which poetry 2>/dev/null),)
    PYTHON := python
    PIP := pip
    USE_POETRY := false
else
    POETRY := poetry
    PYTHON := $(POETRY) run python
    USE_POETRY := true
endif

# ─────────────────────────[ Colors ]─────────────────────────────────────────
ifneq ($(shell tput colors 2>/dev/null),)
    C_RESET  := $(shell tput sgr0)
    C_BLUE   := $(shell tput setaf 4)
    C_GREEN  := $(shell tput setaf 2)
    C_YELLOW := $(shell tput setaf 3)
    C_RED    := $(shell tput setaf 1)
    C_CYAN   := $(shell tput setaf 6)
    C_MAGENTA:= $(shell tput setaf 5)
else
    C_RESET  :=
    C_BLUE   :=
    C_GREEN  :=
    C_YELLOW :=
    C_RED    :=
    C_CYAN   :=
    C_MAGENTA:=
endif

# ─────────────────────────[ Helpers ]────────────────────────────────────────
define msg
	@printf '$(C_BLUE)→ %s$(C_RESET)\n' "$(1)"
endef

define success
	@printf '$(C_GREEN)✓ %s$(C_RESET)\n' "$(1)"
endef

define warn
	@printf '$(C_YELLOW)⚠ %s$(C_RESET)\n' "$(1)"
endef

define error
	@printf '$(C_RED)✗ %s$(C_RESET)\n' "$(1)"
endef

# ─────────────────────────[ Default Target ]────────────────────────────────
.DEFAULT_GOAL := help

# ─────────────────────────[ Phony Targets ]─────────────────────────────────
.PHONY: help install install-dev clean test lint lint-fix format type-check \
        build check check-all update test-unit test-integration test-cov

# ═══════════════════════════[ HELP ]═══════════════════════════════════════
help: ## Show this help message
	@echo "$(C_CYAN)╔══════════════════════════════════════════════════════════════╗$(C_RESET)"
	@echo "$(C_CYAN)║                  $(PROJECT_NAME) Makefile                      ║$(C_RESET)"
	@echo "$(C_CYAN)╚══════════════════════════════════════════════════════════════╝$(C_RESET)"
	@echo ""
	@echo "$(C_YELLOW)Available targets:$(C_RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(C_GREEN)%-20s$(C_RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# ═══════════════════════════[ SETUP ]═══════════════════════════════════════
install: ## Install dependencies
	$(call msg,"Installing $(PROJECT_NAME) dependencies")
ifeq ($(USE_POETRY),true)
	$(POETRY) install --no-dev
else
	$(PIP) install -e .
endif
	$(call success,"Dependencies installed")

install-dev: ## Install development dependencies
	$(call msg,"Installing $(PROJECT_NAME) development dependencies")
ifeq ($(USE_POETRY),true)
	$(POETRY) install
else
	$(PIP) install -e ".[dev]"
endif
	$(call success,"Development environment ready")

clean: ## Clean build artifacts and caches
	$(call msg,"Cleaning $(PROJECT_NAME)")
	@find . \( \
		-name "__pycache__" \
		-o -name "*.py[cod]" \
		-o -name ".pytest_cache" \
		-o -name ".mypy_cache" \
		-o -name ".ruff_cache" \
		-o -name ".coverage*" \
		-o -name "htmlcov" \
		-o -name "dist" \
		-o -name "build" \
		-o -name "*.egg-info" \
	\) -exec rm -rf {} + 2>/dev/null || true
	@mkdir -p reports
	$(call success,"Cleanup complete")

# ═══════════════════════════[ TESTING ]═══════════════════════════════════
test: ## Run all tests
	$(call msg,"Running $(PROJECT_NAME) tests")
	$(PYTHON) -m pytest $(TESTS_DIR)/ -v --tb=short
	$(call success,"Tests completed")

test-unit: ## Run unit tests
	$(call msg,"Running unit tests")
	@if [ -d "$(TESTS_DIR)/unit" ]; then \
		$(PYTHON) -m pytest $(TESTS_DIR)/unit -v --tb=short; \
	else \
		$(warn,"No unit tests directory found"); \
	fi

test-integration: ## Run integration tests
	$(call msg,"Running integration tests")
	@if [ -d "$(TESTS_DIR)/integration" ]; then \
		$(PYTHON) -m pytest $(TESTS_DIR)/integration -v --tb=short; \
	else \
		$(warn,"No integration tests directory found"); \
	fi

test-cov: ## Run tests with coverage
	$(call msg,"Running tests with coverage")
	$(PYTHON) -m pytest $(TESTS_DIR)/ --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	$(call success,"Coverage report generated")

# ═══════════════════════════[ CODE QUALITY ]═══════════════════════════════
lint: ## Run linting
	$(call msg,"Running linting")
ifeq ($(USE_POETRY),true)
	$(POETRY) run ruff check .
else
	ruff check .
endif
	$(call success,"Linting completed")

lint-fix: ## Run linting with auto-fix
	$(call msg,"Running linting with auto-fix")
ifeq ($(USE_POETRY),true)
	$(POETRY) run ruff check . --fix
else
	ruff check . --fix
endif
	$(call success,"Linting with auto-fix completed")

format: ## Format code
	$(call msg,"Formatting code")
ifeq ($(USE_POETRY),true)
	$(POETRY) run black .
	$(POETRY) run isort .
else
	black .
	isort .
endif
	$(call success,"Code formatted")

type-check: ## Run type checking
	$(call msg,"Running type checking")
ifeq ($(USE_POETRY),true)
	$(POETRY) run mypy $(SRC_DIR)
else
	mypy $(SRC_DIR)
endif
	$(call success,"Type checking completed")

# ═══════════════════════════[ BUILD ]═══════════════════════════════════════
build: clean ## Build package
	$(call msg,"Building $(PROJECT_NAME)")
ifeq ($(USE_POETRY),true)
	$(POETRY) build
else
	$(PYTHON) -m build
endif
	$(call success,"Build completed")

# ═══════════════════════════[ UTILITIES ]═══════════════════════════════════
check: lint type-check test ## Run all checks
	$(call success,"All checks passed")

check-all: lint-fix format type-check test ## Run all checks with auto-fixes
	$(call success,"All checks completed with fixes")

update: ## Update dependencies
	$(call msg,"Updating dependencies")
ifeq ($(USE_POETRY),true)
	$(POETRY) update
else
	$(PIP) install --upgrade -e ".[dev]"
endif
	$(call success,"Dependencies updated")