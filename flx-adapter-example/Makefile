###############################################################################
#  flx-adapter-example Makefile — PyAuto subproject
#  Author : Marlon Costa <marlon.costa@datacosmos.com.br>
#  License: MIT
###############################################################################

# ═══════════════════════════════════════════════════════════════════════════
#  INHERITED WORKSPACE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Detect if we're in a PyAuto workspace
PYAUTO_ROOT ?= $(shell git -C "$(CURDIR)" rev-parse --show-toplevel 2>/dev/null || echo "$(CURDIR)/..")
flx-adapter-example := $(notdir $(CURDIR))
WORKSPACE_MAKEFILE := $(PYAUTO_ROOT)/Makefile

# Check if we can inherit from workspace
ifneq ($(wildcard $(WORKSPACE_MAKEFILE)),)
    COORDINATED_MODE := true
    VENV_DIR := $(PYAUTO_ROOT)/.venv
    VENV_BIN := $(VENV_DIR)/bin
    PYTHON := $(VENV_BIN)/python
    POETRY := $(VENV_BIN)/poetry
else
    COORDINATED_MODE := false
    VENV_DIR := .venv
    VENV_BIN := $(VENV_DIR)/bin
    PYTHON := python3.13
    POETRY := poetry
endif

# ═══════════════════════════════════════════════════════════════════════════
#  PROJECT-SPECIFIC CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Project paths
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs
REPORTS_DIR := reports
LOGS_DIR := logs

# Cleanup patterns
CACHE_DIRS := __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov dist build
CACHE_FILES := *.pyc .coverage
CACHE_PATTERNS := *.egg-info

# Colors (simple compatibility)
ifneq ($(NO_COLOR),)
    BLUE    :=
    GREEN   :=
    YELLOW  :=
    RED     :=
    CYAN    :=
    NC      :=
    BOLD    :=
else
    BLUE    := \\033[0;34m
    GREEN   := \\033[0;32m
    YELLOW  := \\033[0;33m
    RED     := \\033[0;31m
    CYAN    := \\033[0;36m
    NC      := \\033[0m
    BOLD    := \\033[1m
endif

# ═══════════════════════════════════════════════════════════════════════════
#  MACROS
# ═══════════════════════════════════════════════════════════════════════════

define section
	@/bin/echo -e "\n$(BLUE)══════════════════[ $(1) ]═══════════════════$(NC)"
endef

define success
	@/bin/echo -e "$(GREEN)✓ $(1)$(NC)"
endef

define error
	@/bin/echo -e "$(RED)✗ $(1)$(NC)"
endef

define warning
	@/bin/echo -e "$(YELLOW)⚠ $(1)$(NC)"
endef

define info
	@/bin/echo -e "$(CYAN)ℹ $(1)$(NC)"
endef

define cleanup_artifacts
	@find . \( \
		$(foreach dir,$(CACHE_DIRS),-type d -name "$(dir)" -o) \
		$(foreach file,$(CACHE_FILES),-type f -name "$(file)" -o) \
		$(foreach pattern,$(CACHE_PATTERNS),-name "$(pattern)" -o) \
		-false \) \
		-exec rm -rf {} \; 2>/dev/null || true
endef

# ═══════════════════════════════════════════════════════════════════════════
#  TARGETS
# ═══════════════════════════════════════════════════════════════════════════

.DEFAULT_GOAL := status
.PHONY: help status

# ───────────────────────────────────────────────────────────────────────────
#  STATUS & INFORMATION
# ───────────────────────────────────────────────────────────────────────────

## status: Shows project status and configuration
status:
	$(call section,$(flx-adapter-example) Status)
	@echo "Project: $(BOLD)$(flx-adapter-example)$(NC)"
	@echo "PyAuto Root: $(PYAUTO_ROOT)"
	@echo "Coordinated Mode: $(if $(filter true,$(COORDINATED_MODE)),$(GREEN)Enabled$(NC),$(RED)Disabled$(NC))"
	@echo "Python: $(PYTHON)"
	@echo "Poetry: $(POETRY)"
	@echo "Virtual Env: $(VENV_DIR)"
	@echo "Source Directory: $(SRC_DIR)"
	@echo "Tests Directory: $(TESTS_DIR)"
	@if [ -f "pyproject.toml" ]; then \
		echo "Project Version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"; \
	fi
	@if [ "$(COORDINATED_MODE)" = "true" ]; then \
		echo "$(CYAN)ℹ Dependencies managed by workspace$(NC)"; \
	fi

# ───────────────────────────────────────────────────────────────────────────
#  DEPENDENCY MANAGEMENT
# ───────────────────────────────────────────────────────────────────────────

## install: Installs project dependencies
install:
ifeq ($(COORDINATED_MODE),true)
	$(call info,Installing via workspace coordination)
	@cd $(PYAUTO_ROOT) && $(MAKE) project-run PROJECT=$(flx-adapter-example) TARGET=install-local
else
	$(call section,Installing dependencies)
	@if [ ! -f poetry.lock ] || [ pyproject.toml -nt poetry.lock ]; then \
		$(POETRY) lock || true; \
	fi
	@$(POETRY) install --all-extras || $(POETRY) install || true
	$(call success,Dependencies installed)
endif

## install-local: Local installation (called by workspace)
install-local:
	$(call section,Installing $(flx-adapter-example) dependencies)
	@if [ ! -f poetry.lock ] || [ pyproject.toml -nt poetry.lock ]; then \
		$(POETRY) lock || true; \
	fi
	@$(POETRY) install --all-extras || $(POETRY) install || true
	$(call success,Local dependencies installed)

## update: Updates dependencies
update:
ifeq ($(COORDINATED_MODE),true)
	$(call info,Updates managed by workspace)
	@cd $(PYAUTO_ROOT) && $(MAKE) update PROJECT=$(flx-adapter-example)
else
	$(call section,Updating dependencies)
	@$(POETRY) update || true
	$(call success,Dependencies updated)
endif

# ───────────────────────────────────────────────────────────────────────────
#  DEVELOPMENT
# ───────────────────────────────────────────────────────────────────────────

## test: Runs tests with coverage
test:
	$(call section,Running tests for $(flx-adapter-example))
	@mkdir -p $(REPORTS_DIR)
	@$(PYTHON) -m pytest \
		$(if $(V),-v,) \
		$(if $(VERBOSE),--verbose,) \
		--cov=$(SRC_DIR) \
		--cov-report=term-missing:skip-covered \
		--cov-report=html:$(REPORTS_DIR)/coverage \
		--cov-report=xml:$(REPORTS_DIR)/coverage.xml \
		$(if $(JUNIT),--junitxml=$(REPORTS_DIR)/junit.xml,) \
		$(if $(FAILFAST),--exitfirst,) \
		$(if $(k),'-k $(k)',) \
		$(if $(m),'-m $(m)',) \
		$(TESTS_DIR) \
		$(PYTEST_ARGS)
	$(call success,Tests completed)

## test-fast: Runs tests without coverage
test-fast:
	$(call section,Running fast tests for $(flx-adapter-example))
	@$(PYTHON) -m pytest $(TESTS_DIR) -x $(PYTEST_ARGS)
	$(call success,Fast tests completed)

## lint: Runs linting checks
lint:
	$(call section,Linting $(flx-adapter-example))
	@$(PYTHON) -m ruff check .
	$(call success,Linting completed)

## lint-fix: Fixes linting issues automatically
lint-fix:
	$(call section,Auto-fixing lint issues for $(flx-adapter-example))
	@$(PYTHON) -m ruff check --fix . || true
	$(call success,Lint fixes applied)

## format: Formats code with Black and isort
format:
	$(call section,Formatting $(flx-adapter-example))
	@$(PYTHON) -m black . || true
	@$(PYTHON) -m isort . || true
	$(call success,Code formatted)

## type-check: Runs mypy type checking
type-check:
	$(call section,Type checking $(flx-adapter-example))
	@$(PYTHON) -m mypy $(SRC_DIR) || true
	$(call success,Type checking completed)

## quality: Runs all quality checks
quality: lint type-check
	$(call success,All quality checks completed)

## fix: Runs all automated fixes
fix: lint-fix format
	$(call success,All automated fixes applied)

# ───────────────────────────────────────────────────────────────────────────
#  BUILD & PACKAGING
# ───────────────────────────────────────────────────────────────────────────

## build: Builds the package
build:
	$(call section,Building $(flx-adapter-example))
	@$(PYTHON) -m build
	$(call success,Package built)

## build-check: Checks build without creating artifacts
build-check:
	$(call section,Checking build for $(flx-adapter-example))
	@$(POETRY) check
	$(call success,Build check completed)

# ───────────────────────────────────────────────────────────────────────────
#  CLEANUP
# ───────────────────────────────────────────────────────────────────────────

## clean: Removes build artifacts and cache
clean:
	$(call section,Cleaning $(flx-adapter-example))
	$(call cleanup_artifacts)
	$(call success,Cleanup completed)

## clean-all: Removes everything including virtual environment
clean-all: clean
	$(call section,Deep cleaning $(flx-adapter-example))
	@rm -rf $(VENV_DIR) || true
	@rm -f poetry.lock || true
	$(call success,Deep cleanup completed)

# ───────────────────────────────────────────────────────────────────────────
#  VALIDATION & REPORTS
# ───────────────────────────────────────────────────────────────────────────

## validate: Validates project structure and configuration
validate:
	$(call section,Validating $(flx-adapter-example))
	@echo "Checking pyproject.toml..."
	@$(POETRY) check
	@echo "Checking source structure..."
	@test -d $(SRC_DIR) || (echo "Missing src directory" && exit 1)
	@test -d $(TESTS_DIR) || (echo "Missing tests directory" && exit 1)
	@echo "Checking imports..."
	@$(PYTHON) -c "import sys; sys.path.insert(0, '$(SRC_DIR)'); import $(shell echo $(flx-adapter-example) | tr '-' '_')" || true
	$(call success,Validation completed)

## report: Generates project report
report:
	$(call section,Generating report for $(flx-adapter-example))
	@mkdir -p $(REPORTS_DIR)
	@echo "# $(flx-adapter-example) Report" > $(REPORTS_DIR)/report.md
	@echo "Generated: $$(date)" >> $(REPORTS_DIR)/report.md
	@echo "" >> $(REPORTS_DIR)/report.md
	@echo "## Status" >> $(REPORTS_DIR)/report.md
	@echo "- Coordinated Mode: $(COORDINATED_MODE)" >> $(REPORTS_DIR)/report.md
	@echo "- Python: $(PYTHON)" >> $(REPORTS_DIR)/report.md
	@if [ -f "pyproject.toml" ]; then \
		echo "- Version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)" >> $(REPORTS_DIR)/report.md; \
	fi
	$(call success,Report generated in $(REPORTS_DIR)/report.md)

# ───────────────────────────────────────────────────────────────────────────
#  WORKSPACE INTEGRATION
# ───────────────────────────────────────────────────────────────────────────

## workspace-test: Runs tests via workspace (if available)
workspace-test:
ifeq ($(COORDINATED_MODE),true)
	@cd $(PYAUTO_ROOT) && $(MAKE) test PROJECT=$(flx-adapter-example)
else
	$(call warning,Not in coordinated mode, running local tests)
	@$(MAKE) test
endif

## workspace-lint: Runs linting via workspace (if available)
workspace-lint:
ifeq ($(COORDINATED_MODE),true)
	@cd $(PYAUTO_ROOT) && $(MAKE) lint PROJECT=$(flx-adapter-example)
else
	$(call warning,Not in coordinated mode, running local lint)
	@$(MAKE) lint
endif

# ═══════════════════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════════════════

help:
	@echo "$(YELLOW)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║  $(flx-adapter-example) - PyAuto Subproject Makefile                 $(NC)"
	@echo "$(YELLOW)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BOLD)$(GREEN)Information:$(NC)"
	@echo "  status              Shows project status and configuration"
	@echo "  validate            Validates project structure and configuration"
	@echo "  report              Generates project report"
	@echo ""
	@echo "$(BOLD)$(GREEN)Dependencies:$(NC)"
	@echo "  install             Installs project dependencies"
	@echo "  update              Updates dependencies"
	@echo ""
	@echo "$(BOLD)$(GREEN)Development:$(NC)"
	@echo "  test                Runs tests with coverage"
	@echo "  test-fast           Runs tests without coverage"
	@echo "  lint                Runs linting checks"
	@echo "  lint-fix            Fixes linting issues automatically"
	@echo "  format              Formats code with Black and isort"
	@echo "  type-check          Runs mypy type checking"
	@echo "  quality             Runs all quality checks"
	@echo "  fix                 Runs all automated fixes"
	@echo ""
	@echo "$(BOLD)$(GREEN)Build & Package:$(NC)"
	@echo "  build               Builds the package"
	@echo "  build-check         Checks build without creating artifacts"
	@echo ""
	@echo "$(BOLD)$(GREEN)Cleanup:$(NC)"
	@echo "  clean               Removes build artifacts and cache"
	@echo "  clean-all           Removes everything including virtual environment"
	@echo ""
	@echo "$(BOLD)$(GREEN)Workspace Integration:$(NC)"
	@echo "  workspace-test      Runs tests via workspace (if available)"
	@echo "  workspace-lint      Runs linting via workspace (if available)"
	@echo ""
	@echo "$(CYAN)Coordinated Mode: $(if $(filter true,$(COORDINATED_MODE)),$(GREEN)Enabled$(NC),$(RED)Disabled$(NC))$(NC)"
	@echo "$(CYAN)PyAuto Root: $(PYAUTO_ROOT)$(NC)"