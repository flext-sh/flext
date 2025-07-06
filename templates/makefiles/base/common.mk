# ═══════════════════════════════════════════════════════════════════════════
# FLEXT COMMON MAKEFILE TEMPLATE - BASE LAYER
# ═══════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Shared foundation for all FLEXT subproject Makefiles
# Usage: include $(FLEXT_ROOT)/templates/makefiles/base/common.mk
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
#  WORKSPACE DETECTION AND COORDINATION
# ═══════════════════════════════════════════════════════════════════════════

# Auto-detect FLEXT workspace root
FLEXT_ROOT ?= $(shell if [ -f "../Makefile" ] && grep -q "FLEXT Enhanced Workspace" "../Makefile" 2>/dev/null; then echo "$(CURDIR)/.."; elif [ -f "../../Makefile" ] && grep -q "FLEXT Enhanced Workspace" "../../Makefile" 2>/dev/null; then echo "$(CURDIR)/../.."; else echo ""; fi)

# Workspace coordination mode
ifneq ($(FLEXT_ROOT),)
    FLEXT_COORDINATED := true
    FLEXT_WORKSPACE_VENV := $(FLEXT_ROOT)/.venv
    FLEXT_WORKSPACE_PYTHON := $(FLEXT_WORKSPACE_VENV)/bin/python
else
    FLEXT_COORDINATED := false
    FLEXT_WORKSPACE_VENV :=
    FLEXT_WORKSPACE_PYTHON :=
endif

# ═══════════════════════════════════════════════════════════════════════════
#  PROJECT IDENTIFICATION
# ═══════════════════════════════════════════════════════════════════════════

# Auto-detect project name from directory
PROJECT_NAME := $(notdir $(CURDIR))
PROJECT_ROOT := $(CURDIR)
PROJECT_TYPE ?= python

# Project paths (configurable by individual projects)
SRC_DIR ?= src
TESTS_DIR ?= tests
DOCS_DIR ?= docs
REPORTS_DIR ?= reports
BUILD_DIR ?= build
DIST_DIR ?= dist

# ═══════════════════════════════════════════════════════════════════════════
#  PYTHON ENVIRONMENT DETECTION
# ═══════════════════════════════════════════════════════════════════════════

# Python detection with fallbacks
PYTHON_DEFAULT := $(shell which python3.13 2>/dev/null || which python3.12 2>/dev/null || which python3.11 2>/dev/null || which python3 2>/dev/null || which python 2>/dev/null)

# Use workspace Python if available, otherwise system Python
ifeq ($(FLEXT_COORDINATED),true)
    ifneq ($(wildcard $(FLEXT_WORKSPACE_PYTHON)),)
        PYTHON := $(FLEXT_WORKSPACE_PYTHON)
        PIP := $(FLEXT_WORKSPACE_VENV)/bin/pip
        POETRY := $(FLEXT_WORKSPACE_VENV)/bin/poetry
        PYTEST := $(FLEXT_WORKSPACE_VENV)/bin/pytest
    else
        PYTHON := $(PYTHON_DEFAULT)
        PIP := $(shell which pip3 2>/dev/null || which pip 2>/dev/null)
        POETRY := $(shell which poetry 2>/dev/null)
        PYTEST := $(shell which pytest 2>/dev/null)
    endif
else
    PYTHON := $(PYTHON_DEFAULT)
    PIP := $(shell which pip3 2>/dev/null || which pip 2>/dev/null)
    POETRY := $(shell which poetry 2>/dev/null)
    PYTEST := $(shell which pytest 2>/dev/null)
endif

# ═══════════════════════════════════════════════════════════════════════════
#  STANDARD SHELL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

# ═══════════════════════════════════════════════════════════════════════════
#  COLOR DEFINITIONS (STANDARDIZED)
# ═══════════════════════════════════════════════════════════════════════════

# Check if NO_COLOR environment variable is set
ifneq ($(NO_COLOR),)
    BOLD    :=
    RED     :=
    GREEN   :=
    YELLOW  :=
    BLUE    :=
    MAGENTA :=
    CYAN    :=
    WHITE   :=
    RESET   :=
else
    BOLD    := \033[1m
    RED     := \033[31m
    GREEN   := \033[32m
    YELLOW  := \033[33m
    BLUE    := \033[34m
    MAGENTA := \033[35m
    CYAN    := \033[36m
    WHITE   := \033[37m
    RESET   := \033[0m
endif

# ═══════════════════════════════════════════════════════════════════════════
#  STANDARD UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

# Logging functions
define log_info
	@echo "$(CYAN)ℹ $(1)$(RESET)"
endef

define log_success
	@echo "$(GREEN)✓ $(1)$(RESET)"
endef

define log_warning
	@echo "$(YELLOW)⚠ $(1)$(RESET)"
endef

define log_error
	@echo "$(RED)✗ $(1)$(RESET)"
endef

define log_section
	@echo ""
	@echo "$(BOLD)$(BLUE)══════════════════[ $(1) ]═══════════════════$(RESET)"
endef

# Project detection function
define check_project_file
	@test -f $(1) || ($(call log_error,Missing required file: $(1)) && exit 1)
endef

# Directory creation function
define ensure_dir
	@mkdir -p $(1)
endef

# Python version check function
define check_python_version
	@$(PYTHON) -c "import sys; assert sys.version_info >= (3, 11), f'Python 3.11+ required, got {sys.version}'" || ($(call log_error,Python 3.11+ required) && exit 1)
endef

# ═══════════════════════════════════════════════════════════════════════════
#  WORKSPACE COORDINATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

# Check if running in coordinated mode
define check_coordination
	$(if $(FLEXT_COORDINATED),$(call log_info,Running in FLEXT coordinated mode),$(call log_info,Running in standalone mode))
endef

# Workspace coordination for installation
define install_with_coordination
	$(if $(FLEXT_COORDINATED), \
		$(call log_info,Installing via workspace coordination) && \
		cd $(FLEXT_ROOT) && $(MAKE) project-install PROJECT=$(PROJECT_NAME), \
		$(call log_info,Installing in standalone mode) && \
		$(call standalone_install) \
	)
endef

# Standalone installation fallback
define standalone_install
	$(if $(POETRY), \
		$(POETRY) install, \
		$(if $(wildcard pyproject.toml), \
			$(PIP) install -e ., \
			$(if $(wildcard requirements.txt), \
				$(PIP) install -r requirements.txt, \
				$(call log_warning,No installation method found) \
			) \
		) \
	)
endef

# ═══════════════════════════════════════════════════════════════════════════
#  STANDARD CLEANUP PATTERNS
# ═══════════════════════════════════════════════════════════════════════════

# Cache directories to clean
CACHE_DIRS := __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage .tox
BUILD_DIRS := build dist *.egg-info
TEMP_FILES := *.pyc *.pyo *.orig *.bak *.tmp

# Standard cleanup function
define cleanup_python_artifacts
	$(call log_section,Cleaning Python artifacts)
	@find . -type d \( $(foreach dir,$(CACHE_DIRS),-name "$(dir)" -o) -false \) -exec rm -rf {} + 2>/dev/null || true
	@find . -type d \( $(foreach dir,$(BUILD_DIRS),-name "$(dir)" -o) -false \) -exec rm -rf {} + 2>/dev/null || true
	@find . \( $(foreach file,$(TEMP_FILES),-name "$(file)" -o) -false \) -delete 2>/dev/null || true
	$(call log_success,Python artifacts cleaned)
endef

# ═══════════════════════════════════════════════════════════════════════════
#  STANDARD HELP SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

# Default help target
.DEFAULT_GOAL := help

help: ## Show this help message with categorized commands
	@echo "$(BOLD)$(CYAN)🔧 $(PROJECT_NAME) - FLEXT Subproject$(RESET)"
	@echo "$(CYAN)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)Project Information:$(RESET)"
	@echo "  Name: $(PROJECT_NAME)"
	@echo "  Type: $(PROJECT_TYPE)"
	@echo "  Root: $(PROJECT_ROOT)"
	@echo "  Coordinated: $(if $(FLEXT_COORDINATED),$(GREEN)Yes$(RESET),$(YELLOW)No$(RESET))"
	@if [ "$(FLEXT_COORDINATED)" = "true" ]; then \
		echo "  Workspace: $(FLEXT_ROOT)"; \
		echo "  Python: $(PYTHON)"; \
	fi
	@echo ""
	@echo "$(BOLD)$(GREEN)📦 Installation & Setup:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(install|setup|init)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-25s$(RESET) %s\n", $$1, $$2}' || echo "  No installation commands available"
	@echo ""
	@echo "$(BOLD)$(BLUE)🧪 Development & Testing:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(test|lint|format|check|dev)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' || echo "  No development commands available"
	@echo ""
	@echo "$(BOLD)$(MAGENTA)🏗️ Build & Deploy:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(build|deploy|release|publish)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(MAGENTA)%-25s$(RESET) %s\n", $$1, $$2}' || echo "  No build commands available"
	@echo ""
	@echo "$(BOLD)$(RED)🧹 Cleanup & Maintenance:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(clean|reset|purge)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(RED)%-25s$(RESET) %s\n", $$1, $$2}' || echo "  No cleanup commands available"
	@echo ""
	@if [ "$(FLEXT_COORDINATED)" = "true" ]; then \
		echo "$(BOLD)$(YELLOW)🔗 Workspace Integration:$(RESET)"; \
		echo "  Run '$(BOLD)make -C $(FLEXT_ROOT) help$(RESET)' for workspace commands"; \
		echo ""; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  STANDARD VALIDATION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

validate-environment: ## Validate development environment
	$(call log_section,Validating Environment)
	$(call check_python_version)
	@test -n "$(PYTHON)" || ($(call log_error,Python not found) && exit 1)
	$(call log_info,Python: $(PYTHON))
	@$(PYTHON) --version
	$(if $(wildcard pyproject.toml),$(call check_project_file,pyproject.toml))
	$(if $(wildcard requirements.txt),$(call check_project_file,requirements.txt))
	$(call log_success,Environment validation complete)

validate-project: ## Validate project structure
	$(call log_section,Validating Project Structure)
	$(call log_info,Project: $(PROJECT_NAME))
	$(call log_info,Type: $(PROJECT_TYPE))
	@test -d "$(SRC_DIR)" || $(call log_warning,Source directory $(SRC_DIR) not found)
	@test -d "$(TESTS_DIR)" || $(call log_warning,Tests directory $(TESTS_DIR) not found)
	$(call log_success,Project structure validation complete)

validate: validate-environment validate-project ## Run all validation checks
	$(call log_success,All validations passed)

# ═══════════════════════════════════════════════════════════════════════════
#  STANDARD PHONY TARGETS
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: help validate validate-environment validate-project

# ═══════════════════════════════════════════════════════════════════════════
#  EXPORT STANDARD VARIABLES
# ═══════════════════════════════════════════════════════════════════════════

export PROJECT_NAME
export PROJECT_ROOT
export PROJECT_TYPE
export FLEXT_ROOT
export FLEXT_COORDINATED
export PYTHON
export PIP
export POETRY
export PYTEST
