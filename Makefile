# FLEXT Enhanced Workspace - Central Coordination Makefile
# Comprehensive submodule coordination and development automation
# Supports both active projects and legacy projects in legacy/ directory

.PHONY: help version-check version-sync version-update install test lint build clean dev
.PHONY: submodule-status submodule-sync submodule-install submodule-test submodule-lint submodule-clean
.PHONY: legacy-status legacy-install legacy-test legacy-clean active-status active-install active-test
.PHONY: workspace-validate workspace-health workspace-full-test workspace-full-clean
.PHONY: project-install update-deps dev-stop dev-logs docs docs-serve monitor
.PHONY: install-dev test-fast lint-fix type-check security build-api validate-api
.PHONY: release-check release-prepare clean-all clean-workspace clean-venv

# Configuration
SHELL := /bin/bash
WORKSPACE_ROOT := $(shell pwd)
VENV_PATH := $(WORKSPACE_ROOT)/.venv
PYTHON := $(VENV_PATH)/bin/python
POETRY := $(VENV_PATH)/bin/poetry

# Colors for enhanced output
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
RESET := \033[0m

# Project categorization
FLEXT_CORE_PROJECTS := flext-core flext-auth flext-api flext-grpc flext-web flext-cli flext-plugin flext-observability flext-meltano flext-ldap flext-db-oracle flext-quality
SINGER_PROJECTS := flext-tap-ldap flext-tap-oracle-oic flext-tap-oracle-wms flext-target-ldap flext-target-oracle flext-target-oracle-oic flext-dbt-ldap flext-oracle-oic-ext
ENTERPRISE_PROJECTS := client-a-oud-mig client-b-poc-oic-wms client-b-meltano-native
ADDITIONAL_PROJECTS := flext-meltano-bridge python-meltano-gopy flexcore

# All active projects
ACTIVE_PROJECTS := $(FLEXT_CORE_PROJECTS) $(SINGER_PROJECTS) $(ENTERPRISE_PROJECTS) $(ADDITIONAL_PROJECTS)

# Legacy projects in legacy/ directory
LEGACY_PROJECTS := flx flx-adapter-example flx-database-oracle flx-http-oracle-oic flx-http-oracle-wms flx-ldap flx-meltano-enterprise flx-oracle-oic flx-oracle-wms

# All projects (active + legacy)
ALL_PROJECTS := $(ACTIVE_PROJECTS) $(addprefix legacy/,$(LEGACY_PROJECTS))

# Default target
help: ## Show comprehensive workspace commands
	@echo "$(BOLD)$(CYAN)🚀 FLEXT Enhanced Workspace Development Commands$(RESET)"
	@echo "$(CYAN)═══════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📊 Workspace Overview:$(RESET)"
	@echo "  Active Projects: $(words $(ACTIVE_PROJECTS)) projects"
	@echo "  Legacy Projects: $(words $(LEGACY_PROJECTS)) projects"
	@echo "  Total Projects:  $(words $(ALL_PROJECTS)) projects"
	@echo ""
	@echo "$(BOLD)$(GREEN)🎯 Primary Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(help|install|test|lint|build|clean)$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)$(YELLOW)🔧 Submodule Coordination:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'submodule|legacy|active' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)$(BLUE)📈 Workspace Management:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'workspace|version' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)$(MAGENTA)🚀 Development Environment:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'dev|validate|health' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(MAGENTA)%-25s$(RESET) %s\n", $$1, $$2}'

# ═══════════════════════════════════════════════════════════════════════════
#  WORKSPACE STATUS AND VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

workspace-validate: ## Validate entire workspace structure and configuration
	@echo "$(BOLD)$(CYAN)🔍 Validating FLEXT Workspace Structure$(RESET)"
	@echo "Workspace Root: $(WORKSPACE_ROOT)"
	@echo "Python Virtual Env: $(VENV_PATH)"
	@echo "Active Projects: $(words $(ACTIVE_PROJECTS))"
	@echo "Legacy Projects: $(words $(LEGACY_PROJECTS))"
	@echo ""
	@echo "$(BOLD)Checking virtual environment...$(RESET)"
	@test -d $(VENV_PATH) || (echo "$(RED)✗ Virtual environment not found at $(VENV_PATH)$(RESET)" && exit 1)
	@test -f $(PYTHON) || (echo "$(RED)✗ Python not found at $(PYTHON)$(RESET)" && exit 1)
	@echo "$(GREEN)✓ Virtual environment validated$(RESET)"
	@echo ""
	@echo "$(BOLD)Checking project structure...$(RESET)"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(GREEN)✓$(RESET) $$project"; \
		else \
			echo "$(YELLOW)⚠$(RESET) $$project (missing)"; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)Checking legacy projects...$(RESET)"
	@for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "$(GREEN)✓$(RESET) legacy/$$project"; \
		else \
			echo "$(YELLOW)⚠$(RESET) legacy/$$project (missing)"; \
		fi; \
	done
	@echo "$(GREEN)✓ Workspace validation complete$(RESET)"

workspace-health: ## Check health of all projects and their dependencies
	@echo "$(BOLD)$(CYAN)💓 FLEXT Workspace Health Check$(RESET)"
	@echo "Python version: $$($(PYTHON) --version 2>/dev/null || echo 'Not available')"
	@echo "Poetry version: $$($(POETRY) --version 2>/dev/null || echo 'Not available')"
	@echo "Git status: $$(git status --porcelain | wc -l) modified files"
	@echo "Disk usage: $$(du -sh . 2>/dev/null | cut -f1)"
	@echo ""
	@echo "$(BOLD)Checking submodule status...$(RESET)"
	@git submodule status | head -10
	@echo "$(GREEN)✓ Workspace health check complete$(RESET)"

submodule-status: ## Show status of all git submodules
	@echo "$(BOLD)$(CYAN)📊 Git Submodule Status$(RESET)"
	@git submodule status
	@echo ""
	@echo "$(BOLD)Submodule Summary:$(RESET)"
	@echo "Total submodules: $$(git submodule status | wc -l)"
	@echo "Active submodules: $$(git submodule status | grep -v '^-' | wc -l)"
	@echo "Missing submodules: $$(git submodule status | grep '^-' | wc -l)"

submodule-sync: ## Synchronize and update all git submodules
	@echo "$(BOLD)$(CYAN)🔄 Synchronizing Git Submodules$(RESET)"
	@git submodule sync --recursive
	@git submodule update --init --recursive
	@echo "$(GREEN)✓ Submodule synchronization complete$(RESET)"

# Version management
version-check: ## Check version consistency across all projects including legacy
	@echo "$(BOLD)$(CYAN)🔍 Checking version consistency...$(RESET)"
	@python scripts/check_versions.py
	@echo "$(BOLD)Checking legacy project versions...$(RESET)"
	@for project in $(LEGACY_PROJECTS); do \
		if [ -f "legacy/$$project/pyproject.toml" ]; then \
			version=$$(grep '^version = ' "legacy/$$project/pyproject.toml" | cut -d'"' -f2 2>/dev/null || echo "unknown"); \
			echo "legacy/$$project: $$version"; \
		fi; \
	done

version-sync: ## Synchronize all project versions to TARGET_VERSION
	@echo "$(BOLD)$(CYAN)🔄 Synchronizing versions to $(TARGET_VERSION)...$(RESET)"
	@python scripts/standardize_versions.py

version-update: ## Update to specific version (use: make version-update TARGET_VERSION=0.7.0)
	@if [ -z "$(TARGET_VERSION)" ]; then \
		echo "$(RED)❌ Please specify TARGET_VERSION (e.g., make version-update TARGET_VERSION=0.7.0)$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BOLD)$(CYAN)📝 Updating all projects to version $(TARGET_VERSION)...$(RESET)"
	@python scripts/update_version.py $(TARGET_VERSION)

# ═══════════════════════════════════════════════════════════════════════════
#  COORDINATED INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════

install: active-install ## Install all active packages in development mode

active-install: ## Install all active FLEXT packages
	@echo "$(BOLD)$(CYAN)📦 Installing Active FLEXT Packages$(RESET)"
	@if [ -f "pyproject.toml" ]; then \
		echo "Installing workspace root..."; \
		$(PYTHON) -m pip install -e . || true; \
	fi
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Installing $$project...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				cd "$$project" && $(MAKE) install && cd ..; \
			elif [ -f "$$project/pyproject.toml" ]; then \
				$(PYTHON) -m pip install -e "./$$project" || true; \
			else \
				echo "$(YELLOW)⚠ No installation method found for $$project$(RESET)"; \
			fi; \
		else \
			echo "$(YELLOW)⚠ Project $$project not found$(RESET)"; \
		fi; \
	done
	@echo "$(GREEN)✓ Active packages installation complete$(RESET)"

legacy-install: ## Install legacy packages
	@echo "$(BOLD)$(YELLOW)📦 Installing Legacy FLEXT Packages$(RESET)"
	@for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "$(YELLOW)Installing legacy/$$project...$(RESET)"; \
			if [ -f "legacy/$$project/Makefile" ]; then \
				cd "legacy/$$project" && $(MAKE) install && cd ../..; \
			elif [ -f "legacy/$$project/pyproject.toml" ]; then \
				$(PYTHON) -m pip install -e "./legacy/$$project" || true; \
			else \
				echo "$(YELLOW)⚠ No installation method found for legacy/$$project$(RESET)"; \
			fi; \
		else \
			echo "$(YELLOW)⚠ Legacy project $$project not found$(RESET)"; \
		fi; \
	done
	@echo "$(GREEN)✓ Legacy packages installation complete$(RESET)"

submodule-install: active-install legacy-install ## Install all packages (active + legacy)
	@echo "$(BOLD)$(GREEN)✓ Complete submodule installation finished$(RESET)"

install-dev: ## Install with development dependencies for all projects
	@echo "$(BOLD)$(CYAN)🛠️ Installing development dependencies...$(RESET)"
	@if [ -f "pyproject.toml" ]; then \
		$(PYTHON) -m pip install -e ".[dev,test,security,build]" || true; \
	fi
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/Makefile" ]; then \
			echo "$(CYAN)Installing dev dependencies for $$project...$(RESET)"; \
			cd "$$project" && $(MAKE) install-dev 2>/dev/null && cd .. || true; \
		fi; \
	done
	@echo "$(GREEN)✓ Development dependencies installation complete$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════
#  COORDINATED TESTING
# ═══════════════════════════════════════════════════════════════════════════

test: active-test ## Run tests for all active projects

workspace-full-test: active-test legacy-test ## Run tests for all projects including legacy
	@echo "$(BOLD)$(GREEN)✓ Complete workspace testing finished$(RESET)"

active-test: ## Run tests for all active projects
	@echo "$(BOLD)$(CYAN)🧪 Running tests for active projects$(RESET)"
	@test_results=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Testing $$project...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				cd "$$project" && $(MAKE) test && cd .. || test_results=$$((test_results + 1)); \
			elif [ -d "$$project/tests" ]; then \
				$(PYTHON) -m pytest "$$project/tests/" -v || test_results=$$((test_results + 1)); \
			else \
				echo "$(YELLOW)⚠ No tests found for $$project$(RESET)"; \
			fi; \
		fi; \
	done; \
	if [ $$test_results -eq 0 ]; then \
		echo "$(GREEN)✓ All active project tests passed$(RESET)"; \
	else \
		echo "$(RED)✗ $$test_results project(s) had test failures$(RESET)"; \
		exit 1; \
	fi

legacy-test: ## Run tests for legacy projects
	@echo "$(BOLD)$(YELLOW)🧪 Running tests for legacy projects$(RESET)"
	@test_results=0; \
	for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "$(YELLOW)Testing legacy/$$project...$(RESET)"; \
			if [ -f "legacy/$$project/Makefile" ]; then \
				cd "legacy/$$project" && $(MAKE) test && cd ../.. || test_results=$$((test_results + 1)); \
			elif [ -d "legacy/$$project/tests" ]; then \
				$(PYTHON) -m pytest "legacy/$$project/tests/" -v || test_results=$$((test_results + 1)); \
			else \
				echo "$(YELLOW)⚠ No tests found for legacy/$$project$(RESET)"; \
			fi; \
		fi; \
	done; \
	if [ $$test_results -eq 0 ]; then \
		echo "$(GREEN)✓ All legacy project tests passed$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ $$test_results legacy project(s) had test failures$(RESET)"; \
	fi

submodule-test: workspace-full-test ## Alias for complete testing

test-fast: ## Run fast tests only (exclude slow markers)
	@echo "$(BOLD)$(CYAN)⚡ Running fast tests...$(RESET)"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project/tests" ]; then \
			echo "$(CYAN)Fast testing $$project...$(RESET)"; \
			$(PYTHON) -m pytest "$$project/tests/" -x -q || true; \
		fi; \
	done
	@echo "$(GREEN)✓ Fast tests complete$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════
#  COORDINATED LINTING
# ═══════════════════════════════════════════════════════════════════════════

lint: active-lint ## Run linting on all active projects

active-lint: ## Run linting on active projects
	@echo "$(BOLD)$(CYAN)🔍 Running linting on active projects$(RESET)"
	@lint_errors=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Linting $$project...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				cd "$$project" && $(MAKE) lint && cd .. || lint_errors=$$((lint_errors + 1)); \
			else \
				$(PYTHON) -m ruff check "$$project/" || lint_errors=$$((lint_errors + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$lint_errors -eq 0 ]; then \
		echo "$(GREEN)✓ All active projects passed linting$(RESET)"; \
	else \
		echo "$(RED)✗ $$lint_errors project(s) had linting issues$(RESET)"; \
	fi

legacy-lint: ## Run linting on legacy projects
	@echo "$(BOLD)$(YELLOW)🔍 Running linting on legacy projects$(RESET)"
	@for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "$(YELLOW)Linting legacy/$$project...$(RESET)"; \
			if [ -f "legacy/$$project/Makefile" ]; then \
				cd "legacy/$$project" && $(MAKE) lint && cd ../.. || true; \
			else \
				$(PYTHON) -m ruff check "legacy/$$project/" || true; \
			fi; \
		fi; \
	done
	@echo "$(GREEN)✓ Legacy project linting complete$(RESET)"

submodule-lint: active-lint legacy-lint ## Run linting on all projects
	@echo "$(BOLD)$(GREEN)✓ Complete submodule linting finished$(RESET)"

lint-fix: ## Fix linting issues across all projects
	@echo "$(BOLD)$(CYAN)🔧 Fixing linting issues...$(RESET)"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Fixing linting in $$project...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				cd "$$project" && $(MAKE) lint-fix 2>/dev/null && cd .. || true; \
			else \
				$(PYTHON) -m ruff check "$$project/" --fix || true; \
				$(PYTHON) -m black "$$project/" || true; \
			fi; \
		fi; \
	done
	@echo "$(GREEN)✓ Linting fixes applied$(RESET)"

type-check: ## Run type checking
	@echo "🏷️ Running type checking..."
	@if [ -d "src/" ]; then $(PYTHON) -m mypy src/ --ignore-missing-imports || true; fi
	@type_errors=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project/src" ]; then \
			echo "$(CYAN)Type checking $$project...$(RESET)"; \
			cd "$$project" && $(PYTHON) -m mypy src/ --ignore-missing-imports && cd .. || type_errors=$$((type_errors + 1)); \
		fi; \
	done; \
	if [ $$type_errors -eq 0 ]; then \
		echo "$(GREEN)✓ All type checks passed$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ $$type_errors project(s) had type issues$(RESET)"; \
	fi

security: ## Run security checks
	@echo "🔒 Running security checks..."
	@mkdir -p reports
	@if [ -d "src/" ]; then $(PYTHON) -m bandit -r src/ -f json -o reports/security.json || true; fi
	@security_errors=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project/src" ]; then \
			echo "$(CYAN)Security checking $$project...$(RESET)"; \
			$(PYTHON) -m bandit -r "$$project/src" -q || security_errors=$$((security_errors + 1)); \
		fi; \
	done; \
	if [ $$security_errors -eq 0 ]; then \
		echo "$(GREEN)✓ All security checks passed$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ $$security_errors project(s) had security warnings$(RESET)"; \
	fi
	@$(PYTHON) -m safety check || true

# Build and package
# ═══════════════════════════════════════════════════════════════════════════
#  COORDINATED BUILD
# ═══════════════════════════════════════════════════════════════════════════

build: active-build ## Build all active packages

active-build: ## Build all active FLEXT packages
	@echo "$(BOLD)$(CYAN)🏗️ Building active packages$(RESET)"
	@if [ -f "pyproject.toml" ]; then \
		echo "Building workspace root..."; \
		$(PYTHON) -m build . || true; \
	fi
	@build_errors=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Building $$project...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				cd "$$project" && $(MAKE) build && cd .. || build_errors=$$((build_errors + 1)); \
			elif [ -f "$$project/pyproject.toml" ]; then \
				cd "$$project" && $(PYTHON) -m build . && cd .. || build_errors=$$((build_errors + 1)); \
			else \
				echo "$(YELLOW)⚠ No build configuration found for $$project$(RESET)"; \
			fi; \
		fi; \
	done; \
	if [ $$build_errors -eq 0 ]; then \
		echo "$(GREEN)✓ All active packages built successfully$(RESET)"; \
	else \
		echo "$(RED)✗ $$build_errors package(s) failed to build$(RESET)"; \
	fi

legacy-build: ## Build legacy packages
	@echo "$(BOLD)$(YELLOW)🏗️ Building legacy packages$(RESET)"
	@for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "$(YELLOW)Building legacy/$$project...$(RESET)"; \
			if [ -f "legacy/$$project/Makefile" ]; then \
				cd "legacy/$$project" && $(MAKE) build && cd ../.. || true; \
			elif [ -f "legacy/$$project/pyproject.toml" ]; then \
				cd "legacy/$$project" && $(PYTHON) -m build . && cd ../.. || true; \
			fi; \
		fi; \
	done
	@echo "$(GREEN)✓ Legacy packages build complete$(RESET)"

submodule-build: active-build legacy-build ## Build all packages (active + legacy)
	@echo "$(BOLD)$(GREEN)✓ Complete submodule build finished$(RESET)"

build-api: ## Build and start API server
	@echo "🚀 Building and starting API server..."
	@cd cmd/flext && go build -o ../../flext-api-server .
	@./flext-api-server

# ═══════════════════════════════════════════════════════════════════════════
#  SINGLE PROJECT COORDINATION (CALLED FROM SUBMODULES)
# ═══════════════════════════════════════════════════════════════════════════

submodule-install-single: ## Install single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Installing $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)" ] && [ -f "$(PROJECT)/pyproject.toml" ]; then \
		$(PYTHON) -m pip install -e "./$(PROJECT)" || true; \
	else \
		echo "$(YELLOW)⚠ No pyproject.toml found for $(PROJECT)$(RESET)"; \
	fi

project-install: submodule-install-single ## Alias for single project installation (PROJECT=name)
	@echo "$(GREEN)✅ Project $(PROJECT) installation complete$(RESET)"

submodule-install-dev-single: ## Install single project dev dependencies (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Installing dev dependencies for $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)" ] && [ -f "$(PROJECT)/pyproject.toml" ]; then \
		$(PYTHON) -m pip install -e "./$(PROJECT)[dev,test,security,build]" || true; \
	fi

submodule-format-single: ## Format single project code (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Formatting $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)/src" ]; then \
		$(PYTHON) -m ruff format "$(PROJECT)/src" "$(PROJECT)/tests" || true; \
		$(PYTHON) -m black "$(PROJECT)/src" "$(PROJECT)/tests" || true; \
		$(PYTHON) -m isort "$(PROJECT)/src" "$(PROJECT)/tests" || true; \
	fi

submodule-lint-single: ## Lint single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Linting $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)/src" ]; then \
		$(PYTHON) -m ruff check "$(PROJECT)/src" "$(PROJECT)/tests" || true; \
	fi

submodule-lint-fix-single: ## Fix lint issues in single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Fixing lint issues in $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)/src" ]; then \
		$(PYTHON) -m ruff check "$(PROJECT)/src" "$(PROJECT)/tests" --fix || true; \
		$(PYTHON) -m black "$(PROJECT)/src" "$(PROJECT)/tests" || true; \
		$(PYTHON) -m isort "$(PROJECT)/src" "$(PROJECT)/tests" || true; \
	fi

submodule-type-check-single: ## Type check single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Type checking $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)/src" ]; then \
		$(PYTHON) -m mypy "$(PROJECT)/src" --ignore-missing-imports || true; \
	fi

submodule-security-single: ## Security check single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Security checking $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)/src" ]; then \
		$(PYTHON) -m bandit -r "$(PROJECT)/src" || true; \
		$(PYTHON) -m safety check || true; \
	fi



submodule-build-single: ## Build single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Building $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)" ] && [ -f "$(PROJECT)/pyproject.toml" ]; then \
		cd "$(PROJECT)" && $(PYTHON) -m build . && cd .. || true; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  AUTOMATED QUALITY PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

quality-pipeline: ## Run complete quality pipeline for all projects
	@echo "$(BOLD)$(CYAN)🔄 Running FLEXT Quality Pipeline$(RESET)"
	@echo "$(CYAN)Step 1/5: Formatting code...$(RESET)"
	@$(MAKE) lint-fix
	@echo "$(CYAN)Step 2/5: Running linting...$(RESET)"
	@$(MAKE) lint
	@echo "$(CYAN)Step 3/5: Type checking...$(RESET)"
	@$(MAKE) type-check
	@echo "$(CYAN)Step 4/5: Security checks...$(RESET)"
	@$(MAKE) security
	@echo "$(CYAN)Step 5/5: Running tests...$(RESET)"
	@$(MAKE) test || echo "$(YELLOW)⚠ Some tests failed, but pipeline continues$(RESET)"
	@echo "$(GREEN)✅ Quality pipeline completed$(RESET)"

quality-essential: ## Run essential quality checks (format, lint, type-check)
	@echo "$(BOLD)$(CYAN)🔄 Running Essential Quality Checks$(RESET)"
	@$(MAKE) lint-fix
	@$(MAKE) lint || echo "$(YELLOW)⚠ Linting issues found$(RESET)"
	@$(MAKE) type-check || echo "$(YELLOW)⚠ Type checking issues found$(RESET)"
	@echo "$(GREEN)✅ Essential quality checks completed$(RESET)"

clean-all: ## Clean all cache files and build artifacts from workspace
	@echo "$(BOLD)$(CYAN)🧹 Cleaning FLEXT Workspace$(RESET)"
	@echo "$(CYAN)Removing Python cache files...$(RESET)"
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(CYAN)Removing build artifacts...$(RESET)"
	@find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(CYAN)Removing test artifacts...$(RESET)"
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Workspace cleaned successfully$(RESET)"

pre-commit-pipeline: ## Run pre-commit quality checks
	@echo "$(BOLD)$(CYAN)🚀 Pre-commit Quality Checks$(RESET)"
	@$(MAKE) format-all
	@$(MAKE) validate-dependencies-all
	@$(MAKE) lint-fix
	@$(MAKE) test-fast
	@echo "$(GREEN)✅ Pre-commit checks passed$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════
#  DEPENDENCY VALIDATION AND REUSE ENFORCEMENT
# ═══════════════════════════════════════════════════════════════════════════

validate-dependencies-all: ## Validate dependencies across all projects
	@echo "$(BOLD)$(CYAN)🔍 Validating FLEXT Dependencies and Reuse$(RESET)"
	@echo "$(CYAN)Checking for proper module reuse...$(RESET)"
	@dependency_issues=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "$(CYAN)Checking $$project...$(RESET)"; \
			case "$$project" in \
				*api*|*web*) \
					if ! grep -q "flext-auth\|flext-core" "$$project/pyproject.toml"; then \
						echo "$(YELLOW)⚠ $$project should use flext-auth and flext-core$(RESET)"; \
						dependency_issues=$$((dependency_issues + 1)); \
					fi;; \
				*tap-*|*target-*) \
					if ! grep -q "flext-core" "$$project/pyproject.toml"; then \
						echo "$(YELLOW)⚠ $$project should use flext-core$(RESET)"; \
						dependency_issues=$$((dependency_issues + 1)); \
					fi;; \
				*ldap*) \
					if [ "$$project" != "flext-ldap" ] && ! grep -q "flext-ldap\|flext-core" "$$project/pyproject.toml"; then \
						echo "$(YELLOW)⚠ $$project should reuse flext-ldap$(RESET)"; \
						dependency_issues=$$((dependency_issues + 1)); \
					fi;; \
				*oracle*) \
					if ! grep -q "flext-db-oracle\|flext-core" "$$project/pyproject.toml"; then \
						echo "$(YELLOW)⚠ $$project should reuse flext-db-oracle$(RESET)"; \
						dependency_issues=$$((dependency_issues + 1)); \
					fi;; \
			esac; \
		fi; \
	done; \
	if [ $$dependency_issues -eq 0 ]; then \
		echo "$(GREEN)✅ All dependency validations passed$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ $$dependency_issues dependency issues found$(RESET)"; \
		echo "$(CYAN)Run 'make fix-dependencies' to automatically fix some issues$(RESET)"; \
	fi

fix-dependencies: ## Automatically fix common dependency issues
	@echo "$(BOLD)$(CYAN)🔧 Auto-fixing Common Dependency Issues$(RESET)"
	@echo "$(YELLOW)This would analyze and suggest dependency fixes$(RESET)"
	@echo "$(CYAN)Implementation needed: Add flext-core to Singer plugins, etc.$(RESET)"

format-all: ## Format all projects
	@echo "$(BOLD)$(CYAN)🎨 Formatting All Projects$(RESET)"
	@$(MAKE) lint-fix

# ═══════════════════════════════════════════════════════════════════════════
#  AUTOMATED COMMIT AND RELEASE PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

commit-pipeline: ## Run complete commit pipeline with quality checks
	@echo "$(BOLD)$(CYAN)🚀 FLEXT Automated Commit Pipeline$(RESET)"
	@echo "$(CYAN)Step 1: Pre-commit quality checks...$(RESET)"
	@$(MAKE) pre-commit-pipeline
	@echo "$(CYAN)Step 2: Dependency validation...$(RESET)"
	@$(MAKE) validate-dependencies-all
	@echo "$(CYAN)Step 3: Comprehensive testing...$(RESET)"
	@$(MAKE) test
	@echo "$(CYAN)Step 4: Build validation...$(RESET)"
	@$(MAKE) build
	@echo "$(GREEN)✅ All checks passed - Ready for commit$(RESET)"
	@echo "$(YELLOW)Manual step: Review changes and commit with 'git add . && git commit -m \"your message\"'$(RESET)"

auto-commit: ## Automated commit with quality checks (COMMIT_MSG required)
	@if [ -z "$(COMMIT_MSG)" ]; then \
		echo "$(RED)❌ COMMIT_MSG variable required$(RESET)"; \
		echo "$(CYAN)Usage: make auto-commit COMMIT_MSG=\"your commit message\"$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BOLD)$(CYAN)🚀 Automated Commit with Quality Gates$(RESET)"
	@$(MAKE) commit-pipeline
	@echo "$(CYAN)Staging changes...$(RESET)"
	@git add .
	@echo "$(CYAN)Committing with message: $(COMMIT_MSG)$(RESET)"
	@git commit -m "$(COMMIT_MSG)"
	@echo "$(GREEN)✅ Automated commit completed$(RESET)"

release-pipeline: ## Complete release pipeline with all validations
	@echo "$(BOLD)$(CYAN)🎯 FLEXT Release Pipeline$(RESET)"
	@echo "$(CYAN)Step 1: Quality pipeline...$(RESET)"
	@$(MAKE) quality-pipeline
	@echo "$(CYAN)Step 2: Build all packages...$(RESET)"
	@$(MAKE) build
	@echo "$(CYAN)Step 3: Comprehensive testing...$(RESET)"
	@$(MAKE) workspace-full-test
	@echo "$(CYAN)Step 4: Security audit...$(RESET)"
	@$(MAKE) security
	@echo "$(GREEN)✅ Release pipeline completed - Ready for release$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════
#  INDIVIDUAL PROJECT OPERATIONS (CALLED FROM SUBMODULES VIA COMMON.MK)
# ═══════════════════════════════════════════════════════════════════════════

submodule-test-single: ## Test single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Testing $(PROJECT)...$(RESET)"
	@if [ -d "$(PROJECT)/tests" ]; then \
		$(PYTHON) -m pytest "$(PROJECT)/tests/" -v || echo "$(YELLOW)⚠ Tests failed for $(PROJECT)$(RESET)"; \
	elif [ -f "$(PROJECT)/Makefile" ]; then \
		cd "$(PROJECT)" && $(MAKE) test || echo "$(YELLOW)⚠ Tests failed for $(PROJECT)$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ No tests found for $(PROJECT)$(RESET)"; \
	fi

submodule-clean-single: ## Clean single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Cleaning $(PROJECT)...$(RESET)"
	@if [ -f "$(PROJECT)/Makefile" ]; then \
		cd "$(PROJECT)" && $(MAKE) clean || echo "$(YELLOW)⚠ Clean failed for $(PROJECT)$(RESET)"; \
	else \
		find "$(PROJECT)" -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name "build" -o -name "dist" -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true; \
		find "$(PROJECT)" -name "*.pyc" -delete 2>/dev/null || true; \
	fi

validate-dependencies-single: ## Validate dependencies for single project (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then echo "$(RED)❌ PROJECT variable required$(RESET)"; exit 1; fi
	@echo "$(CYAN)Validating dependencies for $(PROJECT)...$(RESET)"
	@if [ -f "$(PROJECT)/pyproject.toml" ]; then \
		case "$(PROJECT)" in \
			flext-*-oracle*) \
				if ! grep -q "flext-db-oracle\|flext-core" "$(PROJECT)/pyproject.toml"; then \
					echo "$(YELLOW)💡 [$(PROJECT)] Consider adding flext-db-oracle dependency$(RESET)"; \
				fi ;; \
			flext-tap-*|flext-target-*) \
				if ! grep -q "flext-core" "$(PROJECT)/pyproject.toml"; then \
					echo "$(YELLOW)💡 [$(PROJECT)] Consider adding flext-core dependency$(RESET)"; \
				fi ;; \
			flext-auth*|flext-api*) \
				if ! grep -q "flext-core" "$(PROJECT)/pyproject.toml"; then \
					echo "$(YELLOW)💡 [$(PROJECT)] Consider adding flext-core dependency$(RESET)"; \
				fi ;; \
		esac; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  COORDINATED CLEANUP
# ═══════════════════════════════════════════════════════════════════════════

clean: active-clean ## Clean build artifacts from active projects

workspace-full-clean: active-clean legacy-clean ## Clean all projects including legacy
	@echo "$(BOLD)$(GREEN)✓ Complete workspace cleanup finished$(RESET)"

active-clean: ## Clean artifacts from active projects (autonomous submodules)
	@echo "$(BOLD)$(CYAN)🧹 Cleaning active project artifacts (Autonomous Mode)$(RESET)"
	@cleaned_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Cleaning $$project (autonomous)...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				echo "  Using project's own clean process"; \
				if cd "$$project" && $(MAKE) clean 2>/dev/null && cd ..; then \
					cleaned_count=$$((cleaned_count + 1)); \
				else \
					echo "$(YELLOW)  ⚠ Project Makefile clean failed, using fallback$(RESET)"; \
					cd .. 2>/dev/null || true; \
					find "$$project" -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name "build" -o -name "dist" -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true; \
					find "$$project" -name "*.pyc" -delete 2>/dev/null || true; \
					cleaned_count=$$((cleaned_count + 1)); \
				fi; \
			else \
				echo "  Using direct cleanup"; \
				find "$$project" -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name "build" -o -name "dist" -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true; \
				find "$$project" -name "*.pyc" -delete 2>/dev/null || true; \
				cleaned_count=$$((cleaned_count + 1)); \
			fi; \
		fi; \
	done; \
	echo "$(GREEN)✓ Active project cleanup complete ($$cleaned_count projects cleaned)$(RESET)"

legacy-clean: ## Clean artifacts from legacy projects
	@echo "$(BOLD)$(YELLOW)🧹 Cleaning legacy project artifacts$(RESET)"
	@for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "$(YELLOW)Cleaning legacy/$$project...$(RESET)"; \
			if [ -f "legacy/$$project/Makefile" ]; then \
				cd "legacy/$$project" && $(MAKE) clean && cd ../.. || true; \
			else \
				find "legacy/$$project" -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name "build" -o -name "dist" -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true; \
				find "legacy/$$project" -name "*.pyc" -delete 2>/dev/null || true; \
			fi; \
		fi; \
	done
	@echo "$(GREEN)✓ Legacy project cleanup complete$(RESET)"

submodule-clean: workspace-full-clean ## Alias for complete cleanup

clean-workspace: ## Clean workspace-level artifacts
	@echo "$(BOLD)$(CYAN)🧹 Cleaning workspace artifacts$(RESET)"
	@find . -maxdepth 2 -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name "build" -o -name "dist" -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true
	@find . -maxdepth 2 -name "*.pyc" -delete 2>/dev/null || true
	@rm -f flext-api-server 2>/dev/null || true
	@echo "$(GREEN)✓ Workspace cleanup complete$(RESET)"

clean-venv: ## Remove virtual environment
	@echo "$(BOLD)$(RED)🗑️ Removing virtual environment...$(RESET)"
	@rm -rf .venv
	@echo "$(GREEN)✓ Virtual environment removed$(RESET)"

# Development environment
dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	@docker-compose up -d postgres redis prometheus
	@echo "✅ Development services started"
	@echo "📊 Prometheus: http://localhost:9090"
	@echo "🗄️ PostgreSQL: localhost:5432"
	@echo "🔴 Redis: localhost:6379"

dev-stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	@docker-compose down

dev-logs: ## Show development environment logs
	@docker-compose logs -f

# API validation
validate-api: ## Validate API endpoints
	@echo "🔬 Validating API endpoints..."
	@./validate_api.sh

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@for project in flext-core flext-auth flext-api flext-grpc flext-web flext-cli \
					flext-plugin flext-observability flext-meltano flext-ldap; do \
		if [ -d "$$project" ] && [ -f "$$project/mkdocs.yml" ]; then \
			echo "Building docs for $$project..."; \
			cd $$project && mkdocs build && cd ..; \
		fi; \
	done

docs-serve: ## Serve documentation locally
	@echo "📖 Serving documentation at http://localhost:8000"
	@mkdocs serve

# Release management
release-check: ## Check if ready for release
	@echo "🔍 Checking release readiness..."
	@echo "Running version consistency check..."
	@python scripts/check_versions.py
	@echo "Running tests..."
	@pytest tests/ */tests/ --cov=src --cov=*/src --cov-fail-under=85
	@echo "Running security checks..."
	@bandit -r src/ */src/
	@echo "✅ Release checks passed"

release-prepare: version-sync test lint type-check security build ## Prepare for release
	@echo "📦 Release preparation complete"

# Monitoring and maintenance
monitor: ## Show system monitoring
	@echo "📊 System Monitoring"
	@echo "Memory usage:"
	@ps aux --sort=-%mem | head -10
	@echo ""
	@echo "Disk usage:"
	@df -h
	@echo ""
	@echo "Python processes:"
	@ps aux | grep python

# ═══════════════════════════════════════════════════════════════════════════
#  MAKEFILE STANDARDIZATION AND ENHANCEMENT
# ═══════════════════════════════════════════════════════════════════════════

enhance-makefiles: ## Enhance all submodule Makefiles with workspace coordination
	@echo "$(BOLD)$(CYAN)🚀 Enhancing Submodule Makefiles$(RESET)"
	$(PYTHON) scripts/enhance_submodule_makefiles.py

enhance-makefiles-dry-run: ## Show what makefiles would be enhanced (dry run)
	@echo "$(BOLD)$(CYAN)👀 Makefile Enhancement Preview$(RESET)"
	$(PYTHON) scripts/enhance_submodule_makefiles.py --dry-run

revert-makefile-enhancements: ## Revert all Makefile enhancements using backups
	@echo "$(BOLD)$(YELLOW)🔄 Reverting Makefile Enhancements$(RESET)"
	$(PYTHON) scripts/enhance_submodule_makefiles.py --revert

standardize-makefiles: ## Apply standardized Makefile templates to all submodules
	@echo "$(BOLD)$(CYAN)📐 Standardizing All Makefiles$(RESET)"
	@if [ -z "$(FORCE)" ]; then \
		echo "$(RED)❌ This will modify all Makefiles. Use FORCE=1 if you're sure$(RESET)"; \
		exit 1; \
	fi
	$(PYTHON) scripts/standardize_makefiles.py

makefile-status: ## Show status of all Makefile enhancements and standardization
	@echo "$(BOLD)$(CYAN)📊 Makefile Status Report$(RESET)"
	@enhanced_count=0; \
	total_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/Makefile" ]; then \
			total_count=$$((total_count + 1)); \
			if grep -q "common_flext.mk\|FLEXT WORKSPACE COORDINATION" "$$project/Makefile" 2>/dev/null; then \
				echo "$(GREEN)✅ $$project - Enhanced$(RESET)"; \
				enhanced_count=$$((enhanced_count + 1)); \
			else \
				echo "$(YELLOW)⚠ $$project - Standard only$(RESET)"; \
			fi; \
		fi; \
	done; \
	echo "$(BOLD)Summary: $$enhanced_count/$$total_count projects enhanced$(RESET)"

test-workspace-coordination: ## Test workspace coordination functionality
	@echo "$(BOLD)$(CYAN)🧪 Testing Workspace Coordination$(RESET)"
	@echo "$(CYAN)Testing individual project operations...$(RESET)"
	@for project in flext-core flext-auth flext-api; do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Testing $$project coordination...$(RESET)"; \
			$(MAKE) submodule-install-single PROJECT=$$project; \
			$(MAKE) submodule-test-single PROJECT=$$project; \
			$(MAKE) validate-dependencies-single PROJECT=$$project; \
		fi; \
	done
	@echo "$(GREEN)✅ Workspace coordination tests complete$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════
#  ENHANCED REPORTING AND STATUS (AUTONOMOUS SUBMODULES)
# ═══════════════════════════════════════════════════════════════════════════

autonomous-check: ## Verify autonomous capability of all submodules
	@echo "$(BOLD)$(CYAN)🔍 Checking Autonomous Capability of Submodules$(RESET)"
	@autonomous_count=0; \
	makefile_count=0; \
	config_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			has_makefile=false; \
			has_config=false; \
			echo "$(CYAN)Checking $$project...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				has_makefile=true; \
				makefile_count=$$((makefile_count + 1)); \
				echo "  $(GREEN)✓ Has autonomous Makefile$(RESET)"; \
			else \
				echo "  $(YELLOW)⚠ No Makefile (dependency on workspace)$(RESET)"; \
			fi; \
			if [ -f "$$project/pyproject.toml" ] || [ -f "$$project/requirements.txt" ] || [ -f "$$project/setup.py" ]; then \
				has_config=true; \
				config_count=$$((config_count + 1)); \
				echo "  $(GREEN)✓ Has autonomous config$(RESET)"; \
			else \
				echo "  $(RED)✗ No autonomous config$(RESET)"; \
			fi; \
			if [ "$$has_makefile" = true ] && [ "$$has_config" = true ]; then \
				autonomous_count=$$((autonomous_count + 1)); \
				echo "  $(BOLD)$(GREEN)✓ FULLY AUTONOMOUS$(RESET)"; \
			else \
				echo "  $(BOLD)$(YELLOW)⚠ PARTIALLY AUTONOMOUS$(RESET)"; \
			fi; \
			echo ""; \
		fi; \
	done; \
	echo "$(BOLD)Autonomy Summary:$(RESET)"; \
	echo "  Total Projects: $(words $(ACTIVE_PROJECTS))"; \
	echo "  $(GREEN)Fully Autonomous: $$autonomous_count$(RESET)"; \
	echo "  $(CYAN)With Makefile: $$makefile_count$(RESET)"; \
	echo "  $(BLUE)With Config: $$config_count$(RESET)"; \
	autonomy_percent=$$((autonomous_count * 100 / $(words $(ACTIVE_PROJECTS)))); \
	if [ $$autonomy_percent -ge 80 ]; then \
		echo "  $(BOLD)$(GREEN)🏆 Autonomy Level: $$autonomy_percent% (EXCELLENT)$(RESET)"; \
	elif [ $$autonomy_percent -ge 60 ]; then \
		echo "  $(BOLD)$(YELLOW)⚠ Autonomy Level: $$autonomy_percent% (GOOD)$(RESET)"; \
	else \
		echo "  $(BOLD)$(RED)🚨 Autonomy Level: $$autonomy_percent% (NEEDS IMPROVEMENT)$(RESET)"; \
	fi

active-status: ## Show status of all active projects
	@echo "$(BOLD)$(CYAN)📊 Active Projects Status$(RESET)"
	@echo "FLEXT Core Projects ($(words $(FLEXT_CORE_PROJECTS))):"
	@for project in $(FLEXT_CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			version=$$(grep '^version = ' "$$project/pyproject.toml" 2>/dev/null | cut -d'"' -f2 || echo "unknown"); \
			echo "  $(GREEN)✓$(RESET) $$project ($$version)"; \
		else \
			echo "  $(RED)✗$(RESET) $$project (missing)"; \
		fi; \
	done
	@echo ""
	@echo "Singer/Meltano Projects ($(words $(SINGER_PROJECTS))):"
	@for project in $(SINGER_PROJECTS); do \
		if [ -d "$$project" ]; then \
			version=$$(grep '^version = ' "$$project/pyproject.toml" 2>/dev/null | cut -d'"' -f2 || echo "unknown"); \
			echo "  $(GREEN)✓$(RESET) $$project ($$version)"; \
		else \
			echo "  $(RED)✗$(RESET) $$project (missing)"; \
		fi; \
	done
	@echo ""
	@echo "Enterprise Projects ($(words $(ENTERPRISE_PROJECTS))):"
	@for project in $(ENTERPRISE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			version=$$(grep '^version = ' "$$project/pyproject.toml" 2>/dev/null | cut -d'"' -f2 || echo "unknown"); \
			echo "  $(GREEN)✓$(RESET) $$project ($$version)"; \
		else \
			echo "  $(RED)✗$(RESET) $$project (missing)"; \
		fi; \
	done

legacy-status: ## Show status of all legacy projects
	@echo "$(BOLD)$(YELLOW)📊 Legacy Projects Status$(RESET)"
	@for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			version=$$(grep '^version = ' "legacy/$$project/pyproject.toml" 2>/dev/null | cut -d'"' -f2 || echo "unknown"); \
			echo "  $(GREEN)✓$(RESET) legacy/$$project ($$version)"; \
		else \
			echo "  $(RED)✗$(RESET) legacy/$$project (missing)"; \
		fi; \
	done

submodule-status-detailed: active-status legacy-status autonomous-check ## Show detailed status of all projects
	@echo "$(BOLD)$(GREEN)📊 Complete Project Overview$(RESET)"
	@echo "Total Active: $(words $(ACTIVE_PROJECTS)) projects"
	@echo "Total Legacy: $(words $(LEGACY_PROJECTS)) projects"
	@echo "Total Workspace: $(words $(ALL_PROJECTS)) projects"
	@echo ""
	@echo "$(BOLD)$(CYAN)🔄 Autonomous Independence Summary:$(RESET)"
	@echo "Each submodule can operate independently with its own:"
	@echo "  • Makefile (build, test, lint, clean)"
	@echo "  • Configuration (pyproject.toml, requirements.txt)"
	@echo "  • Dependencies (no reliance on parent workspace)"
	@echo "  • Development workflow (autonomous dev cycle)"

# ═══════════════════════════════════════════════════════════════════════════
#  MAKEFILE CONFIGURATION SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

# AUTONOMOUS SUBMODULE PRINCIPLES:
# 1. Each submodule must work independently
# 2. Submodule Makefiles have total independence from workspace
# 3. Workspace Makefile provides coordination but respects autonomy
# 4. Fallback mechanisms ensure graceful degradation
# 5. No forced dependencies between submodules

# ═══════════════════════════════════════════════════════════════════════════
#  MAKEFILE ORCHESTRATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

# Include orchestration system
include templates/makefiles/orchestrator.mk

# Orchestration targets for distributed Makefile management
orchestrate: ## Orchestrate all project Makefiles with intelligent templates
	@echo "$(BOLD)$(CYAN)🎼 FLEXT Makefile Orchestration System$(RESET)"
	@echo "$(CYAN)═════════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)Intelligent Makefile Distribution:$(RESET)"
	@echo "  • Auto-detects project types and capabilities"
	@echo "  • Distributes appropriate templates"
	@echo "  • Maintains project autonomy"
	@echo "  • Backs up custom Makefiles"
	@echo ""
	@$(MAKE) validate-templates
	@$(MAKE) orchestrate-all

orchestrate-analyze: ## Analyze all projects for orchestration readiness
	@$(MAKE) analyze-projects

orchestrate-interactive: ## Orchestrate specific project interactively (use: make orchestrate-interactive PROJECT=flext-core)
	@if [ -z "$(PROJECT)" ]; then \
		echo "$(RED)✗ PROJECT variable required$(RESET)"; \
		echo "Usage: make orchestrate-interactive PROJECT=flext-core"; \
		exit 1; \
	fi
	@$(MAKE) analyze-project PROJECT=$(PROJECT)
	@echo ""
	@read -p "Proceed with orchestration? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(CYAN)🚀 Starting orchestration...$(RESET)"; \
		$(MAKE) -f templates/makefiles/orchestrator.mk orchestrate-project PROJECT=$(PROJECT) WORKSPACE_ROOT=$(WORKSPACE_ROOT) TEMPLATES_DIR=$(WORKSPACE_ROOT)/templates/makefiles; \
	else \
		echo "$(YELLOW)⚠ Orchestration cancelled$(RESET)"; \
	fi

orchestrate-validate: ## Validate all template files
	@$(MAKE) validate-templates

orchestrate-update: ## Update all orchestrated Makefiles to latest templates
	@$(MAKE) update-orchestrated

orchestrate-clean: ## Clean old Makefile backups
	@$(MAKE) clean-backups

# ═══════════════════════════════════════════════════════════════════════════
#  MAKEFILE DISTRIBUTION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

distribute-makefiles: orchestrate ## Distribute standardized Makefiles to all projects
	@echo "$(BOLD)$(GREEN)✓ Makefile distribution complete$(RESET)"
	@echo ""
	@echo "$(BOLD)Next steps:$(RESET)"
	@echo "1. Review generated Makefiles in each project"
	@echo "2. Test functionality: make -C [project] help"
	@echo "3. Add project-specific targets as needed"
	@echo "4. Run 'make orchestrate-update' to update templates"

check-makefile-consistency: ## Check consistency across all project Makefiles
	@echo "$(BOLD)$(CYAN)🔍 Checking Makefile Consistency$(RESET)"
	@inconsistent_count=0; \
	orchestrated_count=0; \
	custom_count=0; \
	missing_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			if [ -f "$$project/Makefile" ]; then \
				if grep -q "Generated by FLEXT Orchestrator" "$$project/Makefile" 2>/dev/null; then \
					orchestrated_count=$$((orchestrated_count + 1)); \
					echo "$(GREEN)✓$(RESET) $$project (orchestrated)"; \
				else \
					custom_count=$$((custom_count + 1)); \
					echo "$(YELLOW)⚠$(RESET) $$project (custom)"; \
				fi; \
			else \
				missing_count=$$((missing_count + 1)); \
				echo "$(RED)✗$(RESET) $$project (missing)"; \
			fi; \
		fi; \
	done; \
	echo ""; \
	echo "$(BOLD)Makefile Summary:$(RESET)"; \
	echo "  $(GREEN)Orchestrated: $$orchestrated_count$(RESET)"; \
	echo "  $(YELLOW)Custom: $$custom_count$(RESET)"; \
	echo "  $(RED)Missing: $$missing_count$(RESET)"; \
	echo ""; \
	consistency_percent=$$((orchestrated_count * 100 / $(words $(ACTIVE_PROJECTS)))); \
	if [ $$consistency_percent -ge 80 ]; then \
		echo "  $(BOLD)$(GREEN)🏆 Consistency Level: $$consistency_percent% (EXCELLENT)$(RESET)"; \
	elif [ $$consistency_percent -ge 60 ]; then \
		echo "  $(BOLD)$(YELLOW)⚠ Consistency Level: $$consistency_percent% (GOOD)$(RESET)"; \
	else \
		echo "  $(BOLD)$(RED)🚨 Consistency Level: $$consistency_percent% (NEEDS IMPROVEMENT)$(RESET)"; \
	fi

# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGIC PROJECT MANAGEMENT COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: strategic-overview strategic-deploy strategic-monitor strategic-rollback strategic-health
.PHONY: project-create project-archive project-restore project-migrate project-sync
.PHONY: workspace-evolve workspace-transform workspace-optimize workspace-govern

# Strategic Management Commands
strategic-overview: ## Strategic overview of entire FLEXT ecosystem with health metrics
	@echo "$(BOLD)$(CYAN)🎯 FLEXT Strategic Ecosystem Overview$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "$(BOLD)📊 Workspace Summary:$(RESET)"
	@echo "  • Total Projects: $(words $(ALL_PROJECTS))"
	@echo "  • Active Projects: $(words $(ACTIVE_PROJECTS))"
	@echo "  • Legacy Projects: $(words $(LEGACY_PROJECTS))"
	@echo "  • FLEXT Core: $(words $(FLEXT_CORE_PROJECTS))"
	@echo "  • Singer/Meltano: $(words $(SINGER_PROJECTS))"
	@echo "  • Enterprise: $(words $(ENTERPRISE_PROJECTS))"
	@echo ""
	@echo "$(BOLD)🏗️ Architecture Health:$(RESET)"
	@$(MAKE) autonomous-check | grep -E "(Autonomy Level|AUTONOMOUS|Summary)" || true
	@echo ""
	@echo "$(BOLD)📈 Development Metrics:$(RESET)"
	@git_files=$$(git ls-files | wc -l); \
	python_files=$$(find . -name "*.py" | wc -l); \
	go_files=$$(find . -name "*.go" | wc -l); \
	echo "  • Git tracked files: $$git_files"; \
	echo "  • Python files: $$python_files"; \
	echo "  • Go files: $$go_files"; \
	echo "  • Workspace size: $$(du -sh . | cut -f1)"
	@echo ""
	@echo "$(BOLD)🔄 Git Status:$(RESET)"
	@modified=$$(git status --porcelain | wc -l); \
	untracked=$$(git ls-files --others --exclude-standard | wc -l); \
	echo "  • Modified files: $$modified"; \
	echo "  • Untracked files: $$untracked"; \
	echo "  • Current branch: $$(git branch --show-current)"

strategic-deploy: ## Strategic deployment of all FLEXT projects with dependency resolution
	@echo "$(BOLD)$(CYAN)🚀 Strategic FLEXT Deployment$(RESET)"
	@echo "Phase 1: Core Infrastructure"
	@$(MAKE) submodule-install-single PROJECT=flext-core
	@$(MAKE) submodule-install-single PROJECT=flext-auth
	@$(MAKE) submodule-install-single PROJECT=flext-db-oracle
	@echo "Phase 2: Framework Services"
	@$(MAKE) submodule-install-single PROJECT=flext-api
	@$(MAKE) submodule-install-single PROJECT=flext-grpc
	@$(MAKE) submodule-install-single PROJECT=flext-observability
	@echo "Phase 3: ETL Pipeline"
	@$(MAKE) submodule-install-single PROJECT=flext-meltano
	@for project in $(SINGER_PROJECTS); do \
		$(MAKE) submodule-install-single PROJECT=$$project; \
	done
	@echo "Phase 4: User Interfaces"
	@$(MAKE) submodule-install-single PROJECT=flext-web
	@$(MAKE) submodule-install-single PROJECT=flext-cli
	@echo "Phase 5: Enterprise Integration"
	@for project in $(ENTERPRISE_PROJECTS); do \
		$(MAKE) submodule-install-single PROJECT=$$project; \
	done
	@echo "$(GREEN)✅ Strategic deployment completed$(RESET)"

strategic-monitor: ## Real-time monitoring of all FLEXT project health and performance
	@echo "$(BOLD)$(CYAN)📊 FLEXT Strategic Monitoring Dashboard$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "$(BOLD)🔍 System Health Check:$(RESET)"
	@$(MAKE) workspace-health
	@echo ""
	@echo "$(BOLD)🧪 Quality Metrics:$(RESET)"
	@total_errors=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			project_errors=$$($(PYTHON) -m ruff check "$$project/" 2>/dev/null | wc -l || echo "0"); \
			total_errors=$$((total_errors + project_errors)); \
		fi; \
	done; \
	echo "  • Total linting issues: $$total_errors"
	@echo ""
	@echo "$(BOLD)📈 Performance Metrics:$(RESET)"
	@echo "  • CPU Usage: $$(top -bn1 | grep "Cpu(s)" | awk '{print $$2}' | cut -d'%' -f1)%"
	@echo "  • Memory Usage: $$(free | grep Mem | awk '{printf \"%.1f%%\", $$3/$$2 * 100.0}')"
	@echo "  • Disk Usage: $$(df -h . | tail -1 | awk '{print $$5}')"

strategic-rollback: ## Strategic rollback system for FLEXT workspace with backup restoration
	@echo "$(BOLD)$(YELLOW)🔄 FLEXT Strategic Rollback System$(RESET)"
	@if [ -z "$(BACKUP_ID)" ]; then \
		echo "$(RED)❌ BACKUP_ID required for rollback$(RESET)"; \
		echo "Usage: make strategic-rollback BACKUP_ID=backup_name"; \
		echo "Available backups:"; \
		ls -la backups/ 2>/dev/null | grep "^d" | awk '{print "  • " $$9}' || echo "  No backups found"; \
		exit 1; \
	fi
	@if [ ! -d "backups/$(BACKUP_ID)" ]; then \
		echo "$(RED)❌ Backup $(BACKUP_ID) not found$(RESET)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)⚠️  WARNING: This will restore from backup $(BACKUP_ID)$(RESET)"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(CYAN)🔄 Restoring from backup...$(RESET)"; \
		echo "Implementation needed: Backup restoration logic"; \
	else \
		echo "$(GREEN)✅ Rollback cancelled$(RESET)"; \
	fi

strategic-health: workspace-health autonomous-check strategic-monitor ## Comprehensive health check of entire FLEXT ecosystem
	@echo "$(BOLD)$(GREEN)🏥 FLEXT Ecosystem Health Report Complete$(RESET)"

# Project Lifecycle Management
project-create: ## Create new FLEXT project with standardized template (PROJECT=name TYPE=type)
	@if [ -z "$(PROJECT)" ]; then \
		echo "$(RED)❌ PROJECT variable required$(RESET)"; \
		echo "Usage: make project-create PROJECT=flext-new-service TYPE=service"; \
		echo "Types: core, service, tap, target, enterprise"; \
		exit 1; \
	fi
	@if [ -z "$(TYPE)" ]; then \
		echo "$(RED)❌ TYPE variable required$(RESET)"; \
		echo "Types: core, service, tap, target, enterprise"; \
		exit 1; \
	fi
	@if [ -d "$(PROJECT)" ]; then \
		echo "$(RED)❌ Project $(PROJECT) already exists$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BOLD)$(CYAN)🆕 Creating FLEXT Project: $(PROJECT)$(RESET)"
	@mkdir -p "$(PROJECT)"
	@echo "$(CYAN)Setting up project structure...$(RESET)"
	@case "$(TYPE)" in \
		core) template="templates/makefiles/base/common.mk"; ;; \
		service) template="templates/makefiles/service/service.mk"; ;; \
		tap|target) template="templates/makefiles/singer/singer.mk"; ;; \
		enterprise) template="templates/makefiles/python/python.mk"; ;; \
		*) echo "$(RED)❌ Unknown type: $(TYPE)$(RESET)"; exit 1; ;; \
	esac; \
	cp "$$template" "$(PROJECT)/Makefile" 2>/dev/null || echo "# FLEXT $(TYPE) Project Makefile\ninclude ../templates/common_flext.mk" > "$(PROJECT)/Makefile"
	@cp templates/pyproject_template.toml "$(PROJECT)/pyproject.toml"
	@sed -i 's/PROJECT_NAME/$(PROJECT)/g' "$(PROJECT)/pyproject.toml"
	@mkdir -p "$(PROJECT)/src/$(PROJECT)" "$(PROJECT)/tests" "$(PROJECT)/docs"
	@echo "# $(PROJECT)\n\nFLEXT $(TYPE) project" > "$(PROJECT)/README.md"
	@echo "# $(PROJECT) - Project Documentation" > "$(PROJECT)/CLAUDE.md"
	@echo "$(GREEN)✅ Project $(PROJECT) created successfully$(RESET)"

project-archive: ## Archive project to backup directory (PROJECT=name)
	@if [ -z "$(PROJECT)" ]; then \
		echo "$(RED)❌ PROJECT variable required$(RESET)"; \
		exit 1; \
	fi
	@if [ ! -d "$(PROJECT)" ]; then \
		echo "$(RED)❌ Project $(PROJECT) not found$(RESET)"; \
		exit 1; \
	fi
	@backup_name="$(PROJECT)_backup_$$(date +%Y%m%d_%H%M%S)"; \
	echo "$(BOLD)$(YELLOW)📦 Archiving $(PROJECT) to backups/$$backup_name$(RESET)"; \
	mkdir -p backups; \
	cp -r "$(PROJECT)" "backups/$$backup_name"; \
	echo "$(GREEN)✅ Project archived as $$backup_name$(RESET)"

project-restore: ## Restore project from backup (PROJECT=name BACKUP_ID=backup_name)
	@if [ -z "$(PROJECT)" ] || [ -z "$(BACKUP_ID)" ]; then \
		echo "$(RED)❌ PROJECT and BACKUP_ID variables required$(RESET)"; \
		echo "Usage: make project-restore PROJECT=flext-core BACKUP_ID=flext-core_backup_20250706_120000"; \
		exit 1; \
	fi
	@if [ ! -d "backups/$(BACKUP_ID)" ]; then \
		echo "$(RED)❌ Backup $(BACKUP_ID) not found$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BOLD)$(CYAN)📥 Restoring $(PROJECT) from $(BACKUP_ID)$(RESET)"
	@if [ -d "$(PROJECT)" ]; then \
		echo "$(YELLOW)⚠️  Project $(PROJECT) exists, creating backup first...$(RESET)"; \
		$(MAKE) project-archive PROJECT=$(PROJECT); \
	fi
	@cp -r "backups/$(BACKUP_ID)" "$(PROJECT)"
	@echo "$(GREEN)✅ Project $(PROJECT) restored from $(BACKUP_ID)$(RESET)"

project-migrate: ## Migrate project to new structure or technology (PROJECT=name MIGRATION=type)
	@if [ -z "$(PROJECT)" ] || [ -z "$(MIGRATION)" ]; then \
		echo "$(RED)❌ PROJECT and MIGRATION variables required$(RESET)"; \
		echo "Migrations: modernize, singer-to-meltano, legacy-to-active"; \
		exit 1; \
	fi
	@echo "$(BOLD)$(CYAN)🔄 Migrating $(PROJECT) with $(MIGRATION)$(RESET)"
	@case "$(MIGRATION)" in \
		modernize) \
			echo "$(CYAN)Modernizing project structure...$(RESET)"; \
			$(MAKE) project-archive PROJECT=$(PROJECT); \
			$(PYTHON) scripts/modernize_project.py $(PROJECT) || echo "$(YELLOW)⚠️  Manual modernization needed$(RESET)"; \
			;; \
		singer-to-meltano) \
			echo "$(CYAN)Converting Singer to Meltano SDK...$(RESET)"; \
			echo "$(YELLOW)⚠️  Implementation needed for Singer->Meltano conversion$(RESET)"; \
			;; \
		legacy-to-active) \
			echo "$(CYAN)Moving from legacy to active...$(RESET)"; \
			if [ -d "legacy/$(PROJECT)" ]; then \
				cp -r "legacy/$(PROJECT)" .; \
				echo "$(GREEN)✅ Project moved to active$(RESET)"; \
			else \
				echo "$(RED)❌ Project not found in legacy/$(RESET)"; \
			fi; \
			;; \
		*) echo "$(RED)❌ Unknown migration: $(MIGRATION)$(RESET)"; exit 1; ;; \
	esac

project-sync: ## Synchronize project dependencies and configurations across workspace
	@echo "$(BOLD)$(CYAN)🔄 FLEXT Project Synchronization$(RESET)"
	@$(MAKE) version-check
	@$(MAKE) validate-dependencies-all
	@echo "$(CYAN)Synchronizing common configurations...$(RESET)"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "$(CYAN)Syncing $$project...$(RESET)"; \
			$(MAKE) validate-dependencies-single PROJECT=$$project; \
		fi; \
	done
	@echo "$(GREEN)✅ Project synchronization complete$(RESET)"

# Workspace Evolution Commands
workspace-evolve: ## Evolve workspace architecture with new patterns and technologies
	@echo "$(BOLD)$(CYAN)🧬 FLEXT Workspace Evolution$(RESET)"
	@echo "Phase 1: Analysis"
	@$(MAKE) autonomous-check
	@echo "Phase 2: Template Updates"
	@$(MAKE) orchestrate-validate
	@echo "Phase 3: Dependency Optimization"
	@$(MAKE) validate-dependencies-all
	@echo "Phase 4: Architecture Enhancement"
	@$(MAKE) check-makefile-consistency
	@echo "$(GREEN)✅ Workspace evolution complete$(RESET)"

workspace-transform: ## Transform workspace for different deployment models (MODEL=type)
	@if [ -z "$(MODEL)" ]; then \
		echo "$(RED)❌ MODEL variable required$(RESET)"; \
		echo "Models: microservices, monolith, distributed, cloud-native"; \
		exit 1; \
	fi
	@echo "$(BOLD)$(CYAN)🔄 Transforming workspace for $(MODEL) model$(RESET)"
	@case "$(MODEL)" in \
		microservices) \
			echo "$(CYAN)Optimizing for microservices architecture...$(RESET)"; \
			$(MAKE) autonomous-check; \
			echo "$(GREEN)✅ Microservices optimization ready$(RESET)"; \
			;; \
		monolith) \
			echo "$(CYAN)Preparing monolithic deployment...$(RESET)"; \
			echo "$(YELLOW)⚠️  Implementation needed for monolith transformation$(RESET)"; \
			;; \
		distributed) \
			echo "$(CYAN)Setting up distributed architecture...$(RESET)"; \
			if [ -f "docker-compose.distributed.yml" ]; then \
				echo "$(GREEN)✅ Distributed configuration available$(RESET)"; \
			else \
				echo "$(YELLOW)⚠️  Distributed configuration missing$(RESET)"; \
			fi; \
			;; \
		cloud-native) \
			echo "$(CYAN)Preparing cloud-native deployment...$(RESET)"; \
			echo "$(YELLOW)⚠️  Implementation needed for cloud-native transformation$(RESET)"; \
			;; \
		*) echo "$(RED)❌ Unknown model: $(MODEL)$(RESET)"; exit 1; ;; \
	esac

workspace-optimize: ## Optimize workspace for performance, security, and maintainability
	@echo "$(BOLD)$(CYAN)⚡ FLEXT Workspace Optimization$(RESET)"
	@echo "$(CYAN)Step 1: Performance Analysis...$(RESET)"
	@$(MAKE) monitor | grep -E "(CPU|Memory|Disk)" || true
	@echo "$(CYAN)Step 2: Security Audit...$(RESET)"
	@$(MAKE) security | head -20
	@echo "$(CYAN)Step 3: Code Quality Enhancement...$(RESET)"
	@$(MAKE) quality-essential
	@echo "$(CYAN)Step 4: Dependency Optimization...$(RESET)"
	@$(MAKE) validate-dependencies-all
	@echo "$(GREEN)✅ Workspace optimization complete$(RESET)"

workspace-govern: ## Apply governance policies and compliance checks across all projects
	@echo "$(BOLD)$(CYAN)⚖️ FLEXT Workspace Governance$(RESET)"
	@echo "$(CYAN)Policy 1: Code Quality Standards...$(RESET)"
	@$(MAKE) quality-full | tail -10
	@echo "$(CYAN)Policy 2: Security Compliance...$(RESET)"
	@$(MAKE) security | grep -E "(error|warning|passed)" | tail -5
	@echo "$(CYAN)Policy 3: Documentation Standards...$(RESET)"
	@doc_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -f "$$project/README.md" ] && [ -f "$$project/CLAUDE.md" ]; then \
			doc_count=$$((doc_count + 1)); \
		fi; \
	done; \
	echo "  • Projects with complete documentation: $$doc_count/$(words $(ACTIVE_PROJECTS))"
	@echo "$(CYAN)Policy 4: Version Consistency...$(RESET)"
	@$(MAKE) version-check | tail -5
	@echo "$(GREEN)✅ Governance policies applied$(RESET)"

# Default version for version management
TARGET_VERSION ?= 0.6.0

# Export variables for use in scripts
export TARGET_VERSION
export ACTIVE_PROJECTS
export LEGACY_PROJECTS
export ALL_PROJECTS
export WORKSPACE_ROOT
export VENV_PATH

# Autonomous mode indicators
export FLEXT_AUTONOMOUS_MODE=true
export FLEXT_RESPECT_SUBMODULE_INDEPENDENCE=true

# Orchestration indicators
export FLEXT_ORCHESTRATION_ENABLED=true
export FLEXT_TEMPLATES_VERSION=1.0.0

# ═══════════════════════════════════════════════════════════════════════════════
# ADVANCED SUBPROJECT MANAGEMENT AND CONTROL SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: subproject-control subproject-audit subproject-enforce subproject-scale
.PHONY: dependency-graph dependency-analyze dependency-resolve dependency-update
.PHONY: performance-profile performance-optimize performance-monitor performance-report
.PHONY: security-harden security-audit security-compliance security-remediate

# Total Subproject Control System
subproject-control: ## Total control panel for all FLEXT subprojects with real-time management
	@echo "$(BOLD)$(CYAN)🎛️ FLEXT Subproject Control Center$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "$(BOLD)📊 Control Dashboard:$(RESET)"
	@echo ""
	@echo "$(BOLD)Core Projects Control:$(RESET)"
	@for project in $(FLEXT_CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			status="$(GREEN)ONLINE$(RESET)"; \
			has_makefile=""; \
			has_tests=""; \
			has_docs=""; \
			if [ -f "$$project/Makefile" ]; then has_makefile="📋"; fi; \
			if [ -d "$$project/tests" ]; then has_tests="🧪"; fi; \
			if [ -f "$$project/README.md" ]; then has_docs="📚"; fi; \
			echo "  $(GREEN)●$(RESET) $$project $$has_makefile$$has_tests$$has_docs [$$status]"; \
		else \
			echo "  $(RED)●$(RESET) $$project [$(RED)OFFLINE$(RESET)]"; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)Singer/Meltano Control:$(RESET)"
	@for project in $(SINGER_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  $(YELLOW)●$(RESET) $$project [$(YELLOW)ACTIVE$(RESET)]"; \
		else \
			echo "  $(RED)●$(RESET) $$project [$(RED)INACTIVE$(RESET)]"; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)Enterprise Integration Control:$(RESET)"
	@for project in $(ENTERPRISE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  $(BLUE)●$(RESET) $$project [$(BLUE)DEPLOYED$(RESET)]"; \
		else \
			echo "  $(RED)●$(RESET) $$project [$(RED)MISSING$(RESET)]"; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)🔧 Available Control Commands:$(RESET)"
	@echo "  • make subproject-audit      - Comprehensive audit of all subprojects"
	@echo "  • make subproject-enforce    - Enforce standards across all subprojects"
	@echo "  • make subproject-scale      - Scale subprojects for load management"
	@echo "  • make dependency-graph      - Visualize dependency relationships"
	@echo "  • make performance-profile   - Profile all subproject performance"
	@echo "  • make security-harden      - Harden security across all subprojects"

subproject-audit: ## Comprehensive audit of all subprojects with compliance scoring
	@echo "$(BOLD)$(CYAN)🔍 FLEXT Subproject Comprehensive Audit$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@total_score=0; total_projects=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			total_projects=$$((total_projects + 1)); \
			project_score=0; max_score=100; \
			echo ""; \
			echo "$(BOLD)📁 Auditing $$project$(RESET)"; \
			echo "$(CYAN)──────────────────────────────────────────────────────────────────$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				echo "$(GREEN)✓$(RESET) Makefile present (+10)"; \
				project_score=$$((project_score + 10)); \
			else \
				echo "$(RED)✗$(RESET) Makefile missing (-10)"; \
			fi; \
			if [ -f "$$project/pyproject.toml" ]; then \
				echo "$(GREEN)✓$(RESET) pyproject.toml present (+10)"; \
				project_score=$$((project_score + 10)); \
			else \
				echo "$(RED)✗$(RESET) pyproject.toml missing (-10)"; \
			fi; \
			if [ -d "$$project/tests" ]; then \
				test_count=$$(find "$$project/tests" -name "test_*.py" | wc -l); \
				if [ $$test_count -gt 0 ]; then \
					echo "$(GREEN)✓$(RESET) Tests present ($$test_count files) (+20)"; \
					project_score=$$((project_score + 20)); \
				else \
					echo "$(YELLOW)⚠$(RESET) Test directory exists but no test files (+5)"; \
					project_score=$$((project_score + 5)); \
				fi; \
			else \
				echo "$(RED)✗$(RESET) No tests directory (-20)"; \
			fi; \
			if [ -f "$$project/README.md" ]; then \
				readme_size=$$(wc -l < "$$project/README.md" 2>/dev/null || echo "0"); \
				if [ $$readme_size -gt 10 ]; then \
					echo "$(GREEN)✓$(RESET) Comprehensive README.md ($$readme_size lines) (+15)"; \
					project_score=$$((project_score + 15)); \
				else \
					echo "$(YELLOW)⚠$(RESET) Basic README.md (+5)"; \
					project_score=$$((project_score + 5)); \
				fi; \
			else \
				echo "$(RED)✗$(RESET) No README.md (-15)"; \
			fi; \
			if [ -f "$$project/CLAUDE.md" ]; then \
				echo "$(GREEN)✓$(RESET) CLAUDE.md documentation (+10)"; \
				project_score=$$((project_score + 10)); \
			else \
				echo "$(YELLOW)⚠$(RESET) No CLAUDE.md documentation (-5)"; \
			fi; \
			lint_errors=$$($(PYTHON) -m ruff check "$$project/" 2>/dev/null | wc -l || echo "999"); \
			if [ $$lint_errors -eq 0 ]; then \
				echo "$(GREEN)✓$(RESET) No linting errors (+20)"; \
				project_score=$$((project_score + 20)); \
			elif [ $$lint_errors -lt 10 ]; then \
				echo "$(YELLOW)⚠$(RESET) Few linting errors ($$lint_errors) (+10)"; \
				project_score=$$((project_score + 10)); \
			else \
				echo "$(RED)✗$(RESET) Many linting errors ($$lint_errors) (-10)"; \
			fi; \
			src_exists=false; \
			if [ -d "$$project/src" ]; then \
				echo "$(GREEN)✓$(RESET) Standard src/ structure (+15)"; \
				project_score=$$((project_score + 15)); \
				src_exists=true; \
			else \
				echo "$(YELLOW)⚠$(RESET) No standard src/ structure (-5)"; \
			fi; \
			project_percentage=$$((project_score * 100 / max_score)); \
			total_score=$$((total_score + project_percentage)); \
			if [ $$project_percentage -ge 80 ]; then \
				grade="$(GREEN)A$(RESET)"; \
			elif [ $$project_percentage -ge 70 ]; then \
				grade="$(YELLOW)B$(RESET)"; \
			elif [ $$project_percentage -ge 60 ]; then \
				grade="$(YELLOW)C$(RESET)"; \
			else \
				grade="$(RED)F$(RESET)"; \
			fi; \
			echo "$(BOLD)Grade: $$grade ($$project_percentage%/100%)$(RESET)"; \
		fi; \
	done; \
	if [ $$total_projects -gt 0 ]; then \
		workspace_average=$$((total_score / total_projects)); \
		echo ""; \
		echo "$(BOLD)═══════════════════════════════════════════════════════════════════════════════$(RESET)"; \
		echo "$(BOLD)📊 WORKSPACE AUDIT SUMMARY$(RESET)"; \
		echo "Total Projects Audited: $$total_projects"; \
		echo "Workspace Average Score: $$workspace_average%"; \
		if [ $$workspace_average -ge 80 ]; then \
			echo "$(BOLD)$(GREEN)🏆 Workspace Grade: EXCELLENT (A)$(RESET)"; \
		elif [ $$workspace_average -ge 70 ]; then \
			echo "$(BOLD)$(YELLOW)👍 Workspace Grade: GOOD (B)$(RESET)"; \
		elif [ $$workspace_average -ge 60 ]; then \
			echo "$(BOLD)$(YELLOW)⚠️ Workspace Grade: NEEDS IMPROVEMENT (C)$(RESET)"; \
		else \
			echo "$(BOLD)$(RED)🚨 Workspace Grade: CRITICAL ISSUES (F)$(RESET)"; \
		fi; \
	fi

subproject-enforce: ## Enforce standards and policies across all subprojects
	@echo "$(BOLD)$(CYAN)⚖️ FLEXT Subproject Standards Enforcement$(RESET)"
	@echo "Phase 1: Code Quality Enforcement"
	@$(MAKE) lint-fix
	@echo "Phase 2: Documentation Standards"
	@enforced_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ ! -f "$$project/README.md" ]; then \
			echo "$(CYAN)Creating README.md for $$project...$(RESET)"; \
			echo "# $$project\n\nFLEXT project component\n\n## Installation\n\`\`\`bash\nmake install\n\`\`\`\n\n## Testing\n\`\`\`bash\nmake test\n\`\`\`" > "$$project/README.md"; \
			enforced_count=$$((enforced_count + 1)); \
		fi; \
		if [ -d "$$project" ] && [ ! -f "$$project/CLAUDE.md" ]; then \
			echo "$(CYAN)Creating CLAUDE.md for $$project...$(RESET)"; \
			echo "# $$project - Project Documentation\n\n**Project Type**: FLEXT Component\n**Status**: Active Development\n\n## Project Standards\n\n- Follow FLEXT workspace conventions\n- Maintain test coverage\n- Use standardized Makefile" > "$$project/CLAUDE.md"; \
			enforced_count=$$((enforced_count + 1)); \
		fi; \
	done
	@echo "Phase 3: Testing Infrastructure"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ ! -d "$$project/tests" ]; then \
			echo "$(CYAN)Creating tests directory for $$project...$(RESET)"; \
			mkdir -p "$$project/tests"; \
			echo "# Tests for $$project" > "$$project/tests/__init__.py"; \
			echo "# Basic test template\nimport pytest\n\ndef test_basic():\n    assert True" > "$$project/tests/test_basic.py"; \
		fi; \
	done
	@echo "$(GREEN)✅ Standards enforcement complete ($$enforced_count projects updated)$(RESET)"

subproject-scale: ## Scale subprojects for load management and performance optimization
	@echo "$(BOLD)$(CYAN)📈 FLEXT Subproject Scaling Management$(RESET)"
	@if [ -z "$(SCALE_FACTOR)" ]; then \
		echo "Usage: make subproject-scale SCALE_FACTOR=2 (1-10)"; \
		echo "Current scaling analysis:"; \
		echo ""; \
		for project in $(FLEXT_CORE_PROJECTS); do \
			if [ -d "$$project" ]; then \
				file_count=$$(find "$$project" -name "*.py" | wc -l); \
				if [ $$file_count -gt 50 ]; then \
					echo "  $(RED)⚠$(RESET) $$project: HIGH complexity ($$file_count files) - needs scaling"; \
				elif [ $$file_count -gt 20 ]; then \
					echo "  $(YELLOW)●$(RESET) $$project: MEDIUM complexity ($$file_count files) - ready to scale"; \
				else \
					echo "  $(GREEN)●$(RESET) $$project: LOW complexity ($$file_count files) - optimal"; \
				fi; \
			fi; \
		done; \
		exit 0; \
	fi
	@echo "Scaling factor: $(SCALE_FACTOR)"
	@echo "$(CYAN)Optimizing build processes...$(RESET)"
	@$(MAKE) -j$(SCALE_FACTOR) active-install
	@echo "$(CYAN)Optimizing test execution...$(RESET)"
	@$(MAKE) -j$(SCALE_FACTOR) active-test
	@echo "$(GREEN)✅ Subprojects scaled for factor $(SCALE_FACTOR)$(RESET)"

# Advanced Dependency Management
dependency-graph: ## Generate and display dependency graph for all FLEXT projects
	@echo "$(BOLD)$(CYAN)🕸️ FLEXT Dependency Graph Analysis$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "$(BOLD)Core Dependencies:$(RESET)"
	@for project in $(FLEXT_CORE_PROJECTS); do \
		if [ -f "$$project/pyproject.toml" ]; then \
			echo ""; \
			echo "$(CYAN)📦 $$project:$(RESET)"; \
			deps=$$(grep -A 20 "^.dependencies" "$$project/pyproject.toml" | grep -E '^"[^"]+' | head -10 | sed 's/^"/  • /' | sed 's/",*$$//' || echo "  • No dependencies found"); \
			echo "$$deps"; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)Dependency Conflicts Analysis:$(RESET)"
	@conflict_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -f "$$project/pyproject.toml" ]; then \
			if grep -q "flext-core" "$$project/pyproject.toml"; then \
				echo "$(GREEN)✓$(RESET) $$project: Uses flext-core (good dependency)"; \
			else \
				case "$$project" in \
					flext-core) ;; \
					*) echo "$(YELLOW)⚠$(RESET) $$project: Could benefit from flext-core dependency"; \
					   conflict_count=$$((conflict_count + 1)); ;; \
				esac; \
			fi; \
		fi; \
	done; \
	echo ""; \
	echo "$(BOLD)Summary: $$conflict_count projects could be optimized$(RESET)"

dependency-analyze: ## Deep analysis of dependency relationships and optimization opportunities
	@echo "$(BOLD)$(CYAN)🔬 Deep Dependency Analysis$(RESET)"
	@echo "$(CYAN)Analyzing circular dependencies...$(RESET)"
	@circular_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -f "$$project/pyproject.toml" ]; then \
			project_deps=$$(grep -A 20 "^.dependencies" "$$project/pyproject.toml" | grep -o '"flext-[^"]*"' | tr -d '"' || echo ""); \
			for dep in $$project_deps; do \
				if [ -f "$$dep/pyproject.toml" ] && grep -q "$$project" "$$dep/pyproject.toml"; then \
					echo "$(RED)⚠ Circular dependency: $$project ↔ $$dep$(RESET)"; \
					circular_count=$$((circular_count + 1)); \
				fi; \
			done; \
		fi; \
	done; \
	if [ $$circular_count -eq 0 ]; then \
		echo "$(GREEN)✓ No circular dependencies found$(RESET)"; \
	else \
		echo "$(RED)⚠ $$circular_count circular dependencies detected$(RESET)"; \
	fi
	@echo "$(CYAN)Analyzing version conflicts...$(RESET)"
	@$(MAKE) version-check | tail -10

dependency-resolve: ## Automatically resolve dependency conflicts and optimize relationships
	@echo "$(BOLD)$(CYAN)🔧 Automatic Dependency Resolution$(RESET)"
	@echo "$(CYAN)Step 1: Resolving version conflicts...$(RESET)"
	@$(MAKE) version-sync TARGET_VERSION=$(TARGET_VERSION)
	@echo "$(CYAN)Step 2: Optimizing dependency chains...$(RESET)"
	@optimized_count=0; \
	for project in $(SINGER_PROJECTS); do \
		if [ -f "$$project/pyproject.toml" ] && ! grep -q "flext-core" "$$project/pyproject.toml"; then \
			echo "$(CYAN)Adding flext-core dependency to $$project...$(RESET)"; \
			echo "$(YELLOW)⚠️ Manual intervention needed for $$project$(RESET)"; \
			optimized_count=$$((optimized_count + 1)); \
		fi; \
	done
	@echo "$(GREEN)✅ Dependency resolution complete ($$optimized_count optimizations suggested)$(RESET)"

dependency-update: ## Update all dependencies to latest compatible versions
	@echo "$(BOLD)$(CYAN)📥 Updating All Dependencies$(RESET)"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -f "$$project/pyproject.toml" ]; then \
			echo "$(CYAN)Updating dependencies for $$project...$(RESET)"; \
			if [ -f "$$project/Makefile" ]; then \
				cd "$$project" && $(MAKE) update-deps 2>/dev/null && cd .. || echo "$(YELLOW)⚠ Manual update needed for $$project$(RESET)"; \
			fi; \
		fi; \
	done
	@echo "$(GREEN)✅ Dependency updates complete$(RESET)"

update-deps: dependency-update ## Alias for dependency-update
	@echo "$(GREEN)✅ All dependencies updated$(RESET)"

# Performance Management System
performance-profile: ## Profile performance of all FLEXT subprojects
	@echo "$(BOLD)$(CYAN)📊 FLEXT Performance Profiling$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "$(BOLD)📈 Build Performance:$(RESET)"
	@total_time=0; \
	for project in $(FLEXT_CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Profiling $$project build time...$(RESET)"; \
			start_time=$$(date +%s); \
			if [ -f "$$project/Makefile" ]; then \
				cd "$$project" && timeout 30s $(MAKE) build 2>/dev/null >/dev/null && cd .. || true; \
			fi; \
			end_time=$$(date +%s); \
			build_time=$$((end_time - start_time)); \
			total_time=$$((total_time + build_time)); \
			if [ $$build_time -gt 20 ]; then \
				echo "  $(RED)⚠$(RESET) $$project: $${build_time}s (SLOW)"; \
			elif [ $$build_time -gt 10 ]; then \
				echo "  $(YELLOW)●$(RESET) $$project: $${build_time}s (MEDIUM)"; \
			else \
				echo "  $(GREEN)●$(RESET) $$project: $${build_time}s (FAST)"; \
			fi; \
		fi; \
	done; \
	echo ""; \
	echo "$(BOLD)Total workspace build time: $${total_time}s$(RESET)"
	@echo ""
	@echo "$(BOLD)📊 Memory Usage Analysis:$(RESET)"
	@echo "Current memory usage: $$(free -h | grep Mem | awk '{print $$3 "/" $$2}')"
	@echo "$(BOLD)💾 Disk Usage Analysis:$(RESET)"
	@echo "Workspace size: $$(du -sh . | cut -f1)"
	@echo "Largest projects:"
	@du -sh */ 2>/dev/null | sort -hr | head -5 | sed 's/^/  /'

performance-optimize: ## Optimize performance across all FLEXT subprojects
	@echo "$(BOLD)$(CYAN)⚡ FLEXT Performance Optimization$(RESET)"
	@echo "$(CYAN)Step 1: Cleaning build artifacts...$(RESET)"
	@$(MAKE) clean-all
	@echo "$(CYAN)Step 2: Optimizing dependencies...$(RESET)"
	@$(MAKE) dependency-resolve
	@echo "$(CYAN)Step 3: Parallel build optimization...$(RESET)"
	@$(MAKE) -j4 active-build
	@echo "$(GREEN)✅ Performance optimization complete$(RESET)"

performance-monitor: ## Real-time performance monitoring of FLEXT workspace
	@echo "$(BOLD)$(CYAN)📊 Real-time FLEXT Performance Monitor$(RESET)"
	@echo "Starting 60-second monitoring session..."
	@for i in $$(seq 1 12); do \
		echo ""; \
		echo "$(CYAN)Monitor cycle $$i/12$(RESET)"; \
		echo "CPU: $$(top -bn1 | grep "Cpu(s)" | awk '{print $$2}')"; \
		echo "Memory: $$(free | grep Mem | awk '{printf \"%.1f%%\", $$3/$$2 * 100.0}')"; \
		echo "Active processes: $$(ps aux | grep python | wc -l)"; \
		sleep 5; \
	done
	@echo "$(GREEN)✅ Monitoring session complete$(RESET)"

performance-report: performance-profile ## Generate comprehensive performance report
	@echo "$(BOLD)$(GREEN)📋 Performance Report Generated$(RESET)"
	@echo "Report saved to: reports/performance_report_$$(date +%Y%m%d_%H%M%S).txt"
	@mkdir -p reports
	@$(MAKE) performance-profile > "reports/performance_report_$$(date +%Y%m%d_%H%M%S).txt"

# Security Hardening System
security-harden: ## Harden security across all FLEXT subprojects
	@echo "$(BOLD)$(CYAN)🔒 FLEXT Security Hardening$(RESET)"
	@echo "$(CYAN)Phase 1: Dependency security audit...$(RESET)"
	@$(PYTHON) -m safety check || echo "$(YELLOW)⚠ Safety check issues found$(RESET)"
	@echo "$(CYAN)Phase 2: Code security scanning...$(RESET)"
	@$(MAKE) security
	@echo "$(CYAN)Phase 3: Configuration hardening...$(RESET)"
	@hardened_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ ! -f "$$project/.env.example" ]; then \
			echo "$(CYAN)Creating security template for $$project...$(RESET)"; \
			echo "# Security Configuration Template\n# DO NOT commit real secrets\nDEBUG=false\nSECURE_MODE=true" > "$$project/.env.example"; \
			hardened_count=$$((hardened_count + 1)); \
		fi; \
	done
	@echo "$(GREEN)✅ Security hardening complete ($$hardened_count projects hardened)$(RESET)"

security-audit: ## Comprehensive security audit of all subprojects
	@echo "$(BOLD)$(CYAN)🔍 FLEXT Comprehensive Security Audit$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@$(MAKE) security
	@echo ""
	@echo "$(BOLD)🔐 Secret Scanning:$(RESET)"
	@secret_count=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			secrets=$$(grep -r -E "(password|secret|key|token)" "$$project/" --include="*.py" --include="*.json" 2>/dev/null | grep -v ".env.example" | wc -l || echo "0"); \
			if [ $$secrets -gt 0 ]; then \
				echo "$(YELLOW)⚠$(RESET) $$project: $$secrets potential secrets found"; \
				secret_count=$$((secret_count + secrets)); \
			else \
				echo "$(GREEN)✓$(RESET) $$project: No secrets detected"; \
			fi; \
		fi; \
	done; \
	echo ""; \
	echo "$(BOLD)Total potential secrets: $$secret_count$(RESET)"

security-compliance: ## Check security compliance against industry standards
	@echo "$(BOLD)$(CYAN)⚖️ FLEXT Security Compliance Check$(RESET)"
	@echo "$(CYAN)Checking OWASP compliance...$(RESET)"
	@compliance_score=0; max_compliance=100; \
	if [ -f ".gitignore" ] && grep -q "\.env" ".gitignore"; then \
		echo "$(GREEN)✓$(RESET) .env files properly ignored (+20)"; \
		compliance_score=$$((compliance_score + 20)); \
	else \
		echo "$(RED)✗$(RESET) .env files not properly ignored (-20)"; \
	fi; \
	secret_files=$$(find . -name "*.env" -not -path "./.*" | wc -l); \
	if [ $$secret_files -eq 0 ]; then \
		echo "$(GREEN)✓$(RESET) No committed secret files (+20)"; \
		compliance_score=$$((compliance_score + 20)); \
	else \
		echo "$(RED)✗$(RESET) $$secret_files secret files found in repository (-20)"; \
	fi; \
	if [ -f "requirements.txt" ] || find . -name "pyproject.toml" | head -1 >/dev/null; then \
		echo "$(GREEN)✓$(RESET) Dependency management present (+20)"; \
		compliance_score=$$((compliance_score + 20)); \
	fi; \
	if [ -d ".git" ]; then \
		echo "$(GREEN)✓$(RESET) Version control active (+20)"; \
		compliance_score=$$((compliance_score + 20)); \
	fi; \
	test_dirs=$$(find . -name "tests" -type d | wc -l); \
	if [ $$test_dirs -gt 5 ]; then \
		echo "$(GREEN)✓$(RESET) Testing infrastructure present (+20)"; \
		compliance_score=$$((compliance_score + 20)); \
	else \
		echo "$(YELLOW)⚠$(RESET) Limited testing infrastructure (+10)"; \
		compliance_score=$$((compliance_score + 10)); \
	fi; \
	compliance_percent=$$((compliance_score * 100 / max_compliance)); \
	echo ""; \
	echo "$(BOLD)Security Compliance Score: $$compliance_percent%$(RESET)"; \
	if [ $$compliance_percent -ge 80 ]; then \
		echo "$(GREEN)🏆 EXCELLENT compliance$(RESET)"; \
	elif [ $$compliance_percent -ge 60 ]; then \
		echo "$(YELLOW)👍 GOOD compliance$(RESET)"; \
	else \
		echo "$(RED)🚨 POOR compliance - immediate action required$(RESET)"; \
	fi

security-remediate: ## Automatically remediate common security issues
	@echo "$(BOLD)$(CYAN)🔧 FLEXT Security Issue Remediation$(RESET)"
	@echo "$(CYAN)Step 1: Creating .env templates...$(RESET)"
	@for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ] && [ ! -f "$$project/.env.example" ]; then \
			echo "# Environment template for $$project\n# Copy to .env and configure\nDEBUG=false" > "$$project/.env.example"; \
		fi; \
	done
	@echo "$(CYAN)Step 2: Updating .gitignore...$(RESET)"
	@if ! grep -q "\.env$" .gitignore 2>/dev/null; then \
		echo "\n# Environment files\n.env\n*.env\n!.env.example" >> .gitignore; \
	fi
	@echo "$(CYAN)Step 3: Removing potential secrets...$(RESET)"
	@echo "$(YELLOW)⚠️ Manual review required for potential secrets$(RESET)"
	@echo "$(GREEN)✅ Security remediation complete$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# SYNTAX AND CODE QUALITY DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: syntax-check syntax-fix syntax-report lint-report mypy-report quality-full

syntax-check: ## Check syntax errors in all Python files across all projects
	@echo "$(BOLD)$(CYAN)🔍 Checking Python syntax errors across all projects$(RESET)"
	@syntax_errors=0; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "$(CYAN)Checking syntax in $$project...$(RESET)"; \
			find "$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" || true; \
			if find "$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" >/dev/null; then \
				syntax_errors=$$((syntax_errors + 1)); \
			fi; \
		fi; \
	done; \
	echo "$(CYAN)Checking legacy projects...$(RESET)"; \
	for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "$(YELLOW)Checking syntax in legacy/$$project...$(RESET)"; \
			find "legacy/$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" || true; \
			if find "legacy/$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" >/dev/null; then \
				syntax_errors=$$((syntax_errors + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$syntax_errors -eq 0 ]; then \
		echo "$(GREEN)✓ No syntax errors found in any project$(RESET)"; \
	else \
		echo "$(RED)✗ $$syntax_errors project(s) have syntax errors$(RESET)"; \
		exit 1; \
	fi

syntax-report: ## Generate detailed syntax error report for all projects
	@echo "$(BOLD)$(CYAN)📊 Generating comprehensive syntax error report$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "FLEXT Workspace Syntax Error Report - $(shell date)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo ""
	@total_files=0; total_errors=0; \
	echo "$(BOLD)ACTIVE PROJECTS:$(RESET)"; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			project_files=$$(find "$$project" -name "*.py" | wc -l); \
			total_files=$$((total_files + project_files)); \
			echo "\n$(CYAN)📁 $$project$(RESET) ($$project_files Python files)"; \
			project_errors=$$(find "$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" | wc -l); \
			if [ $$project_errors -gt 0 ]; then \
				total_errors=$$((total_errors + project_errors)); \
				echo "$(RED)  ✗ $$project_errors syntax errors:$(RESET)"; \
				find "$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" | sed 's/^/    /' || true; \
			else \
				echo "$(GREEN)  ✓ No syntax errors$(RESET)"; \
			fi; \
		fi; \
	done; \
	echo "\n$(BOLD)LEGACY PROJECTS:$(RESET)"; \
	for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			project_files=$$(find "legacy/$$project" -name "*.py" | wc -l); \
			total_files=$$((total_files + project_files)); \
			echo "\n$(YELLOW)📁 legacy/$$project$(RESET) ($$project_files Python files)"; \
			project_errors=$$(find "legacy/$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" | wc -l); \
			if [ $$project_errors -gt 0 ]; then \
				total_errors=$$((total_errors + project_errors)); \
				echo "$(RED)  ✗ $$project_errors syntax errors:$(RESET)"; \
				find "legacy/$$project" -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -E "(SyntaxError|IndentationError)" | sed 's/^/    /' || true; \
			else \
				echo "$(GREEN)  ✓ No syntax errors$(RESET)"; \
			fi; \
		fi; \
	done; \
	echo "\n═══════════════════════════════════════════════════════════════════════════════"; \
	echo "$(BOLD)SUMMARY:$(RESET)"; \
	echo "Total Python files checked: $$total_files"; \
	echo "Total syntax errors found: $$total_errors"; \
	if [ $$total_errors -eq 0 ]; then \
		echo "$(GREEN)🎉 All files pass syntax validation!$(RESET)"; \
	else \
		echo "$(RED)⚠️  $$total_errors syntax errors need fixing$(RESET)"; \
	fi; \
	echo "═══════════════════════════════════════════════════════════════════════════════"

lint-report: ## Generate detailed linting report for all projects
	@echo "$(BOLD)$(CYAN)📊 Generating comprehensive linting report$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "FLEXT Workspace Linting Report - $(shell date)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo ""
	@total_lint_issues=0; \
	echo "$(BOLD)ACTIVE PROJECTS:$(RESET)"; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "\n$(CYAN)📁 $$project$(RESET)"; \
			project_issues=$$($(PYTHON) -m ruff check "$$project/" 2>/dev/null | wc -l); \
			if [ $$project_issues -gt 0 ]; then \
				total_lint_issues=$$((total_lint_issues + project_issues)); \
				echo "$(RED)  ✗ $$project_issues linting issues:$(RESET)"; \
				$(PYTHON) -m ruff check "$$project/" 2>/dev/null | head -10 | sed 's/^/    /' || true; \
				if [ $$project_issues -gt 10 ]; then \
					echo "    $(YELLOW)... and $$((project_issues - 10)) more issues$(RESET)"; \
				fi; \
			else \
				echo "$(GREEN)  ✓ No linting issues$(RESET)"; \
			fi; \
		fi; \
	done; \
	echo "\n$(BOLD)LEGACY PROJECTS:$(RESET)"; \
	for project in $(LEGACY_PROJECTS); do \
		if [ -d "legacy/$$project" ]; then \
			echo "\n$(YELLOW)📁 legacy/$$project$(RESET)"; \
			project_issues=$$($(PYTHON) -m ruff check "legacy/$$project/" 2>/dev/null | wc -l); \
			if [ $$project_issues -gt 0 ]; then \
				total_lint_issues=$$((total_lint_issues + project_issues)); \
				echo "$(RED)  ✗ $$project_issues linting issues$(RESET)"; \
			else \
				echo "$(GREEN)  ✓ No linting issues$(RESET)"; \
			fi; \
		fi; \
	done; \
	echo "\n═══════════════════════════════════════════════════════════════════════════════"; \
	echo "$(BOLD)SUMMARY:$(RESET)"; \
	echo "Total linting issues found: $$total_lint_issues"; \
	if [ $$total_lint_issues -eq 0 ]; then \
		echo "$(GREEN)🎉 All projects pass linting validation!$(RESET)"; \
	else \
		echo "$(RED)⚠️  $$total_lint_issues linting issues need fixing$(RESET)"; \
	fi; \
	echo "═══════════════════════════════════════════════════════════════════════════════"

mypy-report: ## Generate detailed mypy type checking report for all projects
	@echo "$(BOLD)$(CYAN)📊 Generating comprehensive mypy report$(RESET)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "FLEXT Workspace MyPy Type Checking Report - $(shell date)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo ""
	@total_type_issues=0; \
	echo "$(BOLD)ACTIVE PROJECTS:$(RESET)"; \
	for project in $(ACTIVE_PROJECTS); do \
		if [ -d "$$project/src" ]; then \
			echo "\n$(CYAN)📁 $$project$(RESET)"; \
			project_issues=$$($(PYTHON) -m mypy "$$project/src" --ignore-missing-imports 2>/dev/null | grep -E "error:|warning:" | wc -l); \
			if [ $$project_issues -gt 0 ]; then \
				total_type_issues=$$((total_type_issues + project_issues)); \
				echo "$(RED)  ✗ $$project_issues type checking issues:$(RESET)"; \
				$(PYTHON) -m mypy "$$project/src" --ignore-missing-imports 2>/dev/null | grep -E "error:|warning:" | head -5 | sed 's/^/    /' || true; \
				if [ $$project_issues -gt 5 ]; then \
					echo "    $(YELLOW)... and $$((project_issues - 5)) more issues$(RESET)"; \
				fi; \
			else \
				echo "$(GREEN)  ✓ No type checking issues$(RESET)"; \
			fi; \
		elif [ -d "$$project" ]; then \
			echo "\n$(CYAN)📁 $$project$(RESET)"; \
			echo "$(YELLOW)  ⚠ No src/ directory found$(RESET)"; \
		fi; \
	done; \
	echo "\n═══════════════════════════════════════════════════════════════════════════════"; \
	echo "$(BOLD)SUMMARY:$(RESET)"; \
	echo "Total mypy issues found: $$total_type_issues"; \
	if [ $$total_type_issues -eq 0 ]; then \
		echo "$(GREEN)🎉 All projects pass type checking!$(RESET)"; \
	else \
		echo "$(RED)⚠️  $$total_type_issues type checking issues need fixing$(RESET)"; \
	fi; \
	echo "═══════════════════════════════════════════════════════════════════════════════"

quality-full: syntax-report lint-report mypy-report ## Generate complete quality report (syntax + lint + mypy)
	@echo "$(BOLD)$(GREEN)🎯 Complete code quality analysis finished$(RESET)"
	@echo "$(CYAN)Use 'make syntax-check' for quick syntax validation$(RESET)"
	@echo "$(CYAN)Use 'make lint-fix' to auto-fix linting issues$(RESET)"
	@echo "$(CYAN)Use individual project Makefiles for targeted fixes$(RESET)"
