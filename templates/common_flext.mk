# =============================================================================
# FLEXT COMMON COORDINATION - INCLUDE FILE
# Shared functions and coordination with central workspace
# Use: include $(FLEXT_ROOT)/templates/common_flext.mk
# =============================================================================

# Workspace detection and configuration
FLEXT_ROOT ?= $(shell if [ -f "../Makefile" ] && grep -q "FLEXT Enhanced Workspace" "../Makefile" 2>/dev/null; then echo "$(CURDIR)/.."; else echo "$(CURDIR)"; fi)
CURRENT_PROJECT := $(notdir $(CURDIR))
WORKSPACE_MAKEFILE := $(FLEXT_ROOT)/Makefile

# Check if we're in FLEXT workspace (must have enhanced workspace Makefile)
WORKSPACE_AVAILABLE := $(shell test -f "$(WORKSPACE_MAKEFILE)" && grep -q "FLEXT Enhanced Workspace" "$(WORKSPACE_MAKEFILE)" 2>/dev/null && echo "true" || echo "false")

# Colors for consistent output across all submodules
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
BOLD := \033[1m
NC := \033[0m

# Python workspace configuration
ifeq ($(WORKSPACE_AVAILABLE),true)
    WORKSPACE_PYTHON := $(FLEXT_ROOT)/.venv/bin/python
    WORKSPACE_PIP := $(FLEXT_ROOT)/.venv/bin/pip
else
    WORKSPACE_PYTHON := python
    WORKSPACE_PIP := pip
endif

# =============================================================================
# WORKSPACE COORDINATION FUNCTIONS
# =============================================================================

# Function to call workspace coordination if available
define call-workspace
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "$(CYAN)🔗 [$(CURRENT_PROJECT)] Using workspace coordination...$(NC)"; \
		cd "$(FLEXT_ROOT)" && $(MAKE) $(1) PROJECT=$(CURRENT_PROJECT); \
	else \
		echo "$(YELLOW)⚠ [$(CURRENT_PROJECT)] Workspace not available, using local mode$(NC)"; \
		$(2); \
	fi
endef

# Function to install dependencies with workspace coordination
define install-with-workspace
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "$(CYAN)📦 [$(CURRENT_PROJECT)] Installing via workspace...$(NC)"; \
		cd "$(FLEXT_ROOT)" && $(MAKE) submodule-install-single PROJECT=$(CURRENT_PROJECT); \
		if [ -f "pyproject.toml" ]; then \
			$(WORKSPACE_PIP) install -e "." || echo "$(YELLOW)⚠ Local install failed$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)📦 [$(CURRENT_PROJECT)] Installing locally...$(NC)"; \
		$(1); \
	fi
endef

# Function to install dev dependencies with workspace coordination
define install-dev-with-workspace
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "$(CYAN)🛠️ [$(CURRENT_PROJECT)] Installing dev deps via workspace...$(NC)"; \
		cd "$(FLEXT_ROOT)" && $(MAKE) submodule-install-dev-single PROJECT=$(CURRENT_PROJECT); \
		if [ -f "pyproject.toml" ]; then \
			$(WORKSPACE_PIP) install -e ".[dev,test,security,build]" || echo "$(YELLOW)⚠ Local dev install failed$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)🛠️ [$(CURRENT_PROJECT)] Installing dev deps locally...$(NC)"; \
		$(1); \
	fi
endef

# Function to run tests with workspace coordination
define test-with-workspace
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "$(CYAN)🧪 [$(CURRENT_PROJECT)] Testing via workspace...$(NC)"; \
		cd "$(FLEXT_ROOT)" && $(MAKE) submodule-test-single PROJECT=$(CURRENT_PROJECT); \
	else \
		echo "$(YELLOW)🧪 [$(CURRENT_PROJECT)] Testing locally...$(NC)"; \
		$(1); \
	fi
endef

# Function to run linting with workspace coordination
define lint-with-workspace
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "$(CYAN)🔍 [$(CURRENT_PROJECT)] Linting via workspace...$(NC)"; \
		cd "$(FLEXT_ROOT)" && $(MAKE) submodule-lint-single PROJECT=$(CURRENT_PROJECT); \
	else \
		echo "$(YELLOW)🔍 [$(CURRENT_PROJECT)] Linting locally...$(NC)"; \
		$(1); \
	fi
endef

# Function to format code with workspace coordination
define format-with-workspace
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "$(CYAN)🎨 [$(CURRENT_PROJECT)] Formatting via workspace...$(NC)"; \
		cd "$(FLEXT_ROOT)" && $(MAKE) submodule-format-single PROJECT=$(CURRENT_PROJECT); \
	else \
		echo "$(YELLOW)🎨 [$(CURRENT_PROJECT)] Formatting locally...$(NC)"; \
		$(1); \
	fi
endef

# Function to clean with workspace coordination
define clean-with-workspace
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "$(CYAN)🧹 [$(CURRENT_PROJECT)] Cleaning via workspace...$(NC)"; \
		cd "$(FLEXT_ROOT)" && $(MAKE) submodule-clean-single PROJECT=$(CURRENT_PROJECT); \
	else \
		echo "$(YELLOW)🧹 [$(CURRENT_PROJECT)] Cleaning locally...$(NC)"; \
		$(1); \
	fi
endef

# =============================================================================
# REUSABLE DEPENDENCY MANAGEMENT
# =============================================================================

# Check if project uses Poetry or pip
USES_POETRY := $(shell test -f "pyproject.toml" && grep -q "poetry" "pyproject.toml" && echo "true" || echo "false")

# Function to validate dependencies and suggest reuse
define validate-dependencies
	@echo "$(BLUE)🔍 [$(CURRENT_PROJECT)] Checking dependency reuse...$(NC)"
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		cd "$(FLEXT_ROOT)" && $(MAKE) validate-dependencies-single PROJECT=$(CURRENT_PROJECT); \
	else \
		echo "$(YELLOW)⚠ Workspace not available for dependency validation$(NC)"; \
	fi
endef

# Function to ensure core dependencies are properly used
define ensure-core-deps
	@echo "$(BLUE)📋 [$(CURRENT_PROJECT)] Ensuring core dependencies...$(NC)"
	@case "$(CURRENT_PROJECT)" in \
		flext-*-oracle*) \
			if [ -f "pyproject.toml" ] && ! grep -q "flext-db-oracle" "pyproject.toml"; then \
				echo "$(YELLOW)💡 Consider adding flext-db-oracle dependency for Oracle functionality$(NC)"; \
			fi ;; \
		flext-tap-*|flext-target-*) \
			if [ -f "pyproject.toml" ] && ! grep -q "flext-core" "pyproject.toml"; then \
				echo "$(YELLOW)💡 Consider adding flext-core dependency for Singer functionality$(NC)"; \
			fi ;; \
		flext-auth*|flext-api*) \
			if [ -f "pyproject.toml" ] && ! grep -q "flext-core" "pyproject.toml"; then \
				echo "$(YELLOW)💡 Consider adding flext-core dependency for auth/API functionality$(NC)"; \
			fi ;; \
	esac
endef

# =============================================================================
# QUALITY ASSURANCE HELPERS
# =============================================================================

# Function to run comprehensive quality checks
define quality-check
	@echo "$(MAGENTA)🏆 [$(CURRENT_PROJECT)] Running quality checks...$(NC)"
	@$(call lint-with-workspace,$(1))
	@$(call validate-dependencies)
	@$(call ensure-core-deps)
	@echo "$(GREEN)✅ [$(CURRENT_PROJECT)] Quality checks complete$(NC)"
endef

# Function to run commit pipeline
define commit-pipeline
	@echo "$(BOLD)$(CYAN)🚀 [$(CURRENT_PROJECT)] Pre-commit pipeline...$(NC)"
	@$(call quality-check,$(1))
	@$(call test-with-workspace,$(2))
	@echo "$(BOLD)$(GREEN)✅ [$(CURRENT_PROJECT)] Ready for commit!$(NC)"
endef

# =============================================================================
# COMMON TARGET IMPLEMENTATIONS
# =============================================================================

# These targets can be used by including projects as fallbacks

.PHONY: workspace-status workspace-install workspace-install-dev workspace-test
.PHONY: workspace-lint workspace-format workspace-clean workspace-quality workspace-commit

workspace-status: ## Show workspace coordination status
	@echo "$(BOLD)$(BLUE)📊 [$(CURRENT_PROJECT)] Workspace Status$(NC)"
	@echo "Project: $(CURRENT_PROJECT)"
	@echo "FLEXT Root: $(FLEXT_ROOT)"
	@echo "Workspace Available: $(WORKSPACE_AVAILABLE)"
	@echo "Uses Poetry: $(USES_POETRY)"
	@if [ "$(WORKSPACE_AVAILABLE)" = "true" ]; then \
		echo "Python: $(WORKSPACE_PYTHON)"; \
		echo "Central Makefile: $(WORKSPACE_MAKEFILE)"; \
		echo "$(GREEN)✅ Workspace coordination enabled$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Running in standalone mode$(NC)"; \
	fi

workspace-install: ## Install with workspace coordination
	$(call install-with-workspace,pip install -e . 2>/dev/null || echo "No local package to install")

workspace-install-dev: ## Install dev dependencies with workspace coordination
	$(call install-dev-with-workspace,pip install -e ".[dev,test]" 2>/dev/null || echo "No dev dependencies")

workspace-test: ## Run tests with workspace coordination
	$(call test-with-workspace,python -m pytest tests/ -v || echo "No tests to run")

workspace-lint: ## Run linting with workspace coordination
	$(call lint-with-workspace,ruff check . || echo "Local linting not available")

workspace-format: ## Format code with workspace coordination
	$(call format-with-workspace,ruff format . || echo "Local formatting not available")

workspace-clean: ## Clean with workspace coordination
	$(call clean-with-workspace,rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/ || echo "Local clean")

workspace-quality: ## Run quality checks with workspace coordination
	$(call quality-check,ruff check .)

workspace-commit: ## Run commit pipeline with workspace coordination
	$(call commit-pipeline,ruff check .,python -m pytest tests/ -v)

# =============================================================================
# INFORMATION HELPERS
# =============================================================================

define workspace-help-header
	@echo "$(BOLD)$(CYAN)🔗 Workspace Coordination Available$(NC)"
	@echo "$(CYAN)  Use 'workspace-*' targets for coordinated operations$(NC)"
	@echo "$(CYAN)  Run 'make workspace-status' for coordination details$(NC)"
	@echo ""
endef

define standalone-help-header
	@echo "$(BOLD)$(YELLOW)⚠ Standalone Mode$(NC)"
	@echo "$(YELLOW)  FLEXT workspace not detected$(NC)"
	@echo "$(YELLOW)  Using local project operations only$(NC)"
	@echo ""
endef

# Exported variables for consistency
export FLEXT_ROOT
export CURRENT_PROJECT
export WORKSPACE_AVAILABLE
export WORKSPACE_PYTHON
export WORKSPACE_PIP
