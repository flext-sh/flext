# FLEXT WORKSPACE - Master Makefile - Python 3.13 Enterprise Standards
# ====================================================================
# Comprehensive multi-project coordination with zero-tolerance quality gates
# Updated: 2025-01-06 | Python 3.13 | Bleeding-edge tooling | Clean Architecture | DDD

.PHONY: help install test clean lint format build docs dev security type-check pre-commit
.PHONY: workspace-* project-* all-* setup-* check-*
.PHONY: build-go test-go clean-go go-*

# Default target
help: ## Show this help message
	@echo "🚀 FLEXT WORKSPACE - Master Coordinator"
	@echo "======================================="
	@echo "🏗️  Multi-project enterprise workspace with 20+ Python projects + Go services"
	@echo "🎯 Clean Architecture + DDD + Python 3.13 + Go 1.24 + Poetry"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# FLEXT Framework Core Projects
CORE_PROJECTS := flext-core flext-api flext-auth flext-grpc flext-web flext-cli flext-plugin flext-observability flext-meltano

# Singer Integration Projects
TAP_PROJECTS := flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic flext-tap-oracle-wms
TARGET_PROJECTS := flext-target-ldap flext-target-ldif flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms

# dbt Adapter Projects
DBT_PROJECTS := flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms

# Extension Projects
EXTENSION_PROJECTS := flext-ldap flext-ldif flext-oracle-wms flext-quality flext-db-oracle flext-oracle-oic-ext

# Enterprise Application Projects
PROJECT_APPS := client-a-oud-mig client-b-meltano-native

# All Python Projects
ALL_PYTHON_PROJECTS := $(CORE_PROJECTS) $(TAP_PROJECTS) $(TARGET_PROJECTS) $(DBT_PROJECTS) $(EXTENSION_PROJECTS) $(PROJECT_APPS)

# Go Projects
GO_CORE_PROJECTS := flexcore
GO_COMMAND_PROJECTS := cmd/flext cmd/flext-cli cmd/flext-demo cmd/flext-server
ALL_GO_PROJECTS := $(GO_CORE_PROJECTS) $(GO_COMMAND_PROJECTS)

# Combined projects for workspace operations
ALL_PROJECTS := $(ALL_PYTHON_PROJECTS)

# API Projects (subset of core projects)
API_PROJECTS := flext-api flext-grpc flext-web

# Data Projects (Singer taps, targets, and dbt)
DATA_PROJECTS := $(TAP_PROJECTS) $(TARGET_PROJECTS) $(DBT_PROJECTS)

# Go Build Settings
GO_BUILD_DIR := build
GO := go
GO_FLAGS := -v
GO_TEST_FLAGS := -race -cover

# ============================================================================
# 🚀 WORKSPACE MANAGEMENT
# ============================================================================

workspace-setup: ## Complete workspace setup
	@echo "🎯 Setting up FLEXT enterprise workspace..."
	@echo "📦 Setting up Python projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  📦 Setting up $$project..."; \
			cd "$$project" && $(MAKE) dev-install && cd ..; \
		fi; \
	done
	@echo "🔨 Setting up Go projects..."
	@for project in $(GO_CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  🔨 Setting up $$project..."; \
			cd "$$project" && $(MAKE) dev-setup && cd ..; \
		fi; \
	done
	@echo "✅ Workspace setup complete!"

setup-dependencies: ## Install dependencies correctly (fixes known issues)
	@echo "🔧 Installing FLEXT dependencies with known fixes..."
	@bash scripts/setup_dependencies.sh
	@echo "✅ Dependencies setup complete!"

workspace-install: ## Install all project dependencies
	@echo "📦 Installing dependencies for all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "⚡ Installing $$project..."; \
			cd "$$project" && $(MAKE) install && cd ..; \
		fi; \
	done
	@for project in $(GO_CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "⚡ Installing $$project..."; \
			cd "$$project" && $(MAKE) mod-download && cd ..; \
		fi; \
	done
	@echo "✅ All dependencies installed!"

workspace-update: ## Update all project dependencies
	@echo "🔄 Updating dependencies for all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔄 Updating $$project..."; \
			cd "$$project" && $(MAKE) update && cd ..; \
		fi; \
	done
	@for project in $(GO_CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔄 Updating $$project..."; \
			cd "$$project" && $(MAKE) update && cd ..; \
		fi; \
	done
	@echo "✅ All dependencies updated!"

sync-deps: ## Synchronize dependencies across all projects with root pyproject.toml
	@echo "🔄 Synchronizing dependencies across all projects..."
	@python scripts/sync_dependencies.py
	@echo "✅ Dependencies synchronized!"

workspace-clean: ## Clean all projects
	@echo "🧹 Cleaning all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🧹 Cleaning $$project..."; \
			cd "$$project" && $(MAKE) clean && cd ..; \
		fi; \
	done
	@echo "✅ Workspace cleaned!"

# ============================================================================
# 🎯 UNIFIED BUILD SYSTEM - ENTERPRISE STANDARDS (Phase 2)
# ============================================================================

# Enhanced standardized commands for all projects
std-install: ## Standardized install - Install project dependencies  
	@echo "📦 STANDARD INSTALL: Installing project dependencies..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "📦 Installing $$project..."; \
			cd "$$project" && poetry install --all-extras && cd ..; \
		fi; \
	done
	@echo "✅ Standard install complete!"

std-test: ## Standardized test - Run comprehensive test suite
	@echo "🧪 STANDARD TEST: Running comprehensive test suite..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🧪 Testing $$project..."; \
			cd "$$project" && $(MAKE) test && cd ..; \
		fi; \
	done
	@echo "✅ Standard test complete!"

std-lint: ## Standardized lint - Run code quality checks
	@echo "🔍 STANDARD LINT: Running code quality checks..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔍 Linting $$project..."; \
			cd "$$project" && $(MAKE) lint && cd ..; \
		fi; \
	done
	@echo "✅ Standard lint complete!"

std-format: ## Standardized format - Auto-format code
	@echo "🎨 STANDARD FORMAT: Auto-formatting code..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🎨 Formatting $$project..."; \
			cd "$$project" && $(MAKE) format && cd ..; \
		fi; \
	done
	@echo "✅ Standard format complete!"

std-coverage: ## Standardized coverage - Generate coverage reports
	@echo "📊 STANDARD COVERAGE: Generating coverage reports..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "📊 Coverage for $$project..."; \
			cd "$$project" && $(MAKE) coverage && cd ..; \
		fi; \
	done
	@echo "✅ Standard coverage complete!"

std-docs: ## Standardized docs - Generate documentation
	@echo "📚 STANDARD DOCS: Generating documentation..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "📚 Docs for $$project..."; \
			cd "$$project" && $(MAKE) docs && cd ..; \
		fi; \
	done
	@echo "✅ Standard docs complete!"

std-build: ## Standardized build - Build all projects
	@echo "🏗️ STANDARD BUILD: Building all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🏗️ Building $$project..."; \
			cd "$$project" && $(MAKE) build && cd ..; \
		fi; \
	done
	@echo "✅ Standard build complete!"

std-check: ## Standardized check - Complete quality gate
	@echo "✅ STANDARD CHECK: Complete quality gate..."
	$(MAKE) std-lint
	$(MAKE) std-test
	$(MAKE) std-coverage
	@echo "✅ Standard check complete!"

validate-all-standards: ## Enterprise validation - Master plan compliance check
	@echo "🎯 VALIDATE ALL STANDARDS: Master plan compliance check..."
	@echo "============================================================"
	@echo "📊 Phase 2 Enhanced Code Standards Validation"
	@echo ""
	@echo "🔍 1. Code Quality Metrics:"
	$(MAKE) std-lint
	@echo ""
	@echo "🧪 2. Test Coverage Validation:"  
	$(MAKE) std-test
	@echo ""
	@echo "📊 3. Coverage Reports:"
	$(MAKE) std-coverage
	@echo ""
	@echo "🏗️ 4. Build Validation:"
	$(MAKE) std-build
	@echo ""
	@echo "📚 5. Documentation Validation:"
	$(MAKE) std-docs
	@echo ""
	@echo "✅ MASTER PLAN COMPLIANCE CHECK COMPLETE!"
	@echo "🎯 All Phase 2 Enhanced Code Standards validated successfully!"

# ============================================================================
# 🧪 TESTING & QUALITY  
# ============================================================================

test-core: ## Test only core projects
	@echo "🧪 Testing core projects..."
	@for project in $(CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🧪 Testing $$project..."; \
			cd "$$project" && $(MAKE) test && cd ..; \
		fi; \
	done

test-api: ## Test API projects
	@echo "🧪 Testing API projects..."
	@for project in $(API_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🧪 Testing $$project..."; \
			cd "$$project" && $(MAKE) test && cd ..; \
		fi; \
	done

test-data: ## Test data integration projects
	@echo "🧪 Testing data integration projects..."
	@for project in $(DATA_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🧪 Testing $$project..."; \
			cd "$$project" && $(MAKE) test && cd ..; \
		fi; \
	done

test-all: ## Test all projects
	@echo "🧪 Testing all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🧪 Testing $$project..."; \
			cd "$$project" && $(MAKE) test && cd ..; \
		fi; \
	done
	@echo "✅ All tests complete!"

# ============================================================================
# 🔍 CODE QUALITY
# ============================================================================

lint-all: ## Lint all projects
	@echo "🔍 Linting all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔍 Linting $$project..."; \
			cd "$$project" && $(MAKE) lint && cd ..; \
		fi; \
	done
	@echo "✅ All linting complete!"

format-all: ## Format all projects
	@echo "🎨 Formatting all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🎨 Formatting $$project..."; \
			cd "$$project" && $(MAKE) format && cd ..; \
		fi; \
	done
	@echo "✅ All formatting complete!"

type-check-legacy: ## Legacy type check (replaced by mypy-comprehensive)
	@echo "⚠️  Use 'make mypy-comprehensive' instead"
	@make mypy-comprehensive

security-all: ## Security check all projects
	@echo "🔒 Security checking all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔒 Security checking $$project..."; \
			cd "$$project" && $(MAKE) security && cd ..; \
		fi; \
	done
	@echo "✅ All security checks complete!"

check-all: ## Run quality checks on all projects
	@echo "🔍 Running quality checks on all FLEXT projects..."
	@failed=0; \
	echo "📦 Checking Python projects..."; \
	for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/Makefile" ]; then \
			echo "  📦 Checking $$project..."; \
			if ! (cd "$$project" && $(MAKE) check); then \
				echo "❌ $$project failed quality checks!"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	echo "🔨 Checking Go projects..."; \
	for project in $(GO_CORE_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/Makefile" ]; then \
			echo "  🔨 Checking $$project..."; \
			if ! (cd "$$project" && $(MAKE) check); then \
				echo "❌ $$project failed quality checks!"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -gt 0 ]; then \
		echo "\n❌ $$failed projects failed quality checks!"; \
		exit 1; \
	else \
		echo "\n✅ All projects passed quality checks!"; \
	fi

# ============================================================================
# 🏗️ BUILD & DEPLOYMENT
# ============================================================================

build-core: ## Build core projects
	@echo "🔨 Building core projects..."
	@for project in $(CORE_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔨 Building $$project..."; \
			cd "$$project" && $(MAKE) build && cd ..; \
		fi; \
	done

build-api: ## Build API projects
	@echo "🔨 Building API projects..."
	@for project in $(API_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔨 Building $$project..."; \
			cd "$$project" && $(MAKE) build && cd ..; \
		fi; \
	done

build-all: ## Build all projects
	@echo "🔨 Building all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔨 Building $$project..."; \
			cd "$$project" && $(MAKE) build && cd ..; \
		fi; \
	done
	@echo "✅ All builds complete!"

# ============================================================================
# 📊 WORKSPACE INFORMATION
# ============================================================================

workspace-status: ## Show workspace status
	@echo "📊 FLEXT Workspace Status"
	@echo "========================="
	@echo "🏗️  Total Python Projects: $(words $(ALL_PYTHON_PROJECTS))"
	@echo "🔨 Total Go Projects: $(words $(ALL_GO_PROJECTS))"
	@echo ""
	@echo "📦 FLEXT Framework Core: $(words $(CORE_PROJECTS)) projects"
	@echo "  $(CORE_PROJECTS)"
	@echo ""
	@echo "🎯 Singer Integration: $(words $(TAP_PROJECTS)) taps + $(words $(TARGET_PROJECTS)) targets"
	@echo "  Taps: $(TAP_PROJECTS)"
	@echo "  Targets: $(TARGET_PROJECTS)"
	@echo ""
	@echo "🗂️  dbt Adapters: $(words $(DBT_PROJECTS)) projects"
	@echo "  $(DBT_PROJECTS)"
	@echo ""
	@echo "🔧 Extensions: $(words $(EXTENSION_PROJECTS)) projects"
	@echo "  $(EXTENSION_PROJECTS)"
	@echo ""
	@echo "📱 Enterprise Apps: $(words $(PROJECT_APPS)) projects"
	@echo "  $(PROJECT_APPS)"
	@echo ""
	@echo "🔨 Go Projects: $(words $(ALL_GO_PROJECTS)) projects"
	@echo "  Core: $(GO_CORE_PROJECTS)"
	@echo "  Commands: $(GO_COMMAND_PROJECTS)"
	@echo ""
	@echo "🔍 Project Status:"
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  ✅ $$project (Python)"; \
		else \
			echo "  ❌ $$project (missing)"; \
		fi; \
	done
	@for project in $(ALL_GO_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  ✅ $$project (Go)"; \
		else \
			echo "  ❌ $$project (missing)"; \
		fi; \
	done

workspace-deps: ## Show workspace dependencies
	@echo "📦 Workspace Dependencies"
	@echo "========================"
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "📦 $$project dependencies:"; \
			cd "$$project" && poetry show --tree && cd ..; \
			echo ""; \
		fi; \
	done

# ============================================================================
# 🚀 DEVELOPMENT COMMANDS
# ============================================================================

dev-setup: workspace-setup ## Complete development setup
	@echo "🎯 Setting up development environment..."
	@poetry install --all-extras
	@echo "✅ Development setup complete!"

dev-core: ## Run core development
	@echo "🔧 Starting core development..."
	@cd flext-core && $(MAKE) dev

dev-api: ## Run API development
	@echo "🔧 Starting API development..."
	@cd flext-api && $(MAKE) dev

dev-all: ## Run all development services
	@echo "🔧 Starting all development services..."
	@echo "🚀 Use docker-compose for full stack development"
	@docker-compose -f docker-compose.yml up -d

# ============================================================================
# 🔧 GO BUILD SYSTEM
# ============================================================================

build-go: ## Build all Go binaries
	@echo "🔨 Building Go binaries..."
	@mkdir -p $(GO_BUILD_DIR)
	@for cmd in $(GO_COMMAND_PROJECTS); do \
		echo "  Building $$cmd..."; \
		$(GO) build $(GO_FLAGS) -o $(GO_BUILD_DIR)/$$(basename $$cmd) ./$$cmd || exit 1; \
	done
	@echo "✅ Go binaries built successfully!"
	@ls -la $(GO_BUILD_DIR)/

test-go: ## Run Go tests
	@echo "🧪 Running Go tests..."
	@$(GO) test $(GO_TEST_FLAGS) ./...
	@echo "✅ Go tests completed!"

clean-go: ## Clean Go build artifacts
	@echo "🧹 Cleaning Go build artifacts..."
	@rm -rf $(GO_BUILD_DIR)
	@$(GO) clean -cache
	@echo "✅ Go artifacts cleaned!"

go-mod-tidy: ## Tidy Go modules
	@echo "📦 Tidying Go modules..."
	@$(GO) mod tidy
	@echo "✅ Go modules tidied!"

go-mod-verify: ## Verify Go modules
	@echo "🔍 Verifying Go modules..."
	@$(GO) mod verify
	@echo "✅ Go modules verified!"

go-deps: ## Download Go dependencies
	@echo "📥 Downloading Go dependencies..."
	@$(GO) mod download
	@echo "✅ Go dependencies downloaded!"

# ============================================================================
# 🐳 DOCKER COMMANDS
# ============================================================================

docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	@docker-compose build

docker-up: ## Start Docker services
	@echo "🐳 Starting Docker services..."
	@docker-compose up -d

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	@docker-compose down

docker-logs: ## Show Docker logs
	@echo "🐳 Showing Docker logs..."
	@docker-compose logs -f

# ============================================================================
# 🧹 CLEANUP
# ============================================================================

# ============================================================================
# 🔍 MYPY TYPE CHECKING - PEP 518 Compliant
# ============================================================================

mypy-workspace: ## Run MyPy on workspace (PEP 518 compliant)
	@python scripts/mypy_analyzer.py --workspace

mypy-all-projects: ## Run MyPy on all individual projects
	@python scripts/mypy_analyzer.py --all-projects

mypy-project: ## Run MyPy on specific project (usage: make mypy-project PROJECT=flext-core)
	@if [ -z "$(PROJECT)" ]; then \
		echo "❌ Usage: make mypy-project PROJECT=<project-name>"; \
		exit 1; \
	fi
	@python scripts/mypy_analyzer.py --project="$(PROJECT)"

mypy-comprehensive: ## Comprehensive MyPy analysis (workspace + all projects)
	@python scripts/mypy_analyzer.py --comprehensive

mypy-stats-project: ## Show MyPy error statistics by project
	@python scripts/mypy_analyzer.py --stats-by-project

mypy-stats-type: ## Show MyPy error statistics by error type
	@python scripts/mypy_analyzer.py --stats-by-type

type-check: mypy-workspace ## Quick type check (workspace only)
type-check-all: mypy-comprehensive ## Full type check (workspace + all projects)
stats-project: mypy-stats-project ## Alias for project statistics
stats-type: mypy-stats-type ## Alias for error type statistics

clean-workspace: workspace-clean ## Clean entire workspace
	@echo "🧹 Cleaning workspace..."
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
	@echo "✅ Workspace cleaned!"

# ============================================================================
# 📚 DOCUMENTATION
# ============================================================================

docs-all: ## Generate all documentation
	@echo "📚 Generating documentation for all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "📚 Generating docs for $$project..."; \
			cd "$$project" && $(MAKE) docs && cd ..; \
		fi; \
	done
	@echo "✅ All documentation generated!"

# ============================================================================
# 🎯 QUICK COMMANDS
# ============================================================================

quick-test: test-core ## Quick test (core only)
	@echo "⚡ Quick test complete!"

quick-check: ## Quick quality check (core only)
	@echo "⚡ Quick quality check..."
	@cd flext-core && $(MAKE) check
	@echo "✅ Quick check complete!"

quick-format: ## Quick format (all projects)
	@echo "⚡ Quick format..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			cd "$$project" && $(MAKE) format && cd ..; \
		fi; \
	done
	@echo "✅ Quick format complete!"

# ============================================================================
# 🔧 MAINTENANCE
# ============================================================================

poetry-update-all: ## Update Poetry in all projects
	@echo "🔄 Updating Poetry in all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔄 Updating Poetry in $$project..."; \
			cd "$$project" && poetry self update && cd ..; \
		fi; \
	done
	@echo "✅ Poetry updated in all projects!"

pre-commit-all: ## Run pre-commit in all projects
	@echo "🎣 Running pre-commit in all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🎣 Pre-commit in $$project..."; \
			cd "$$project" && $(MAKE) pre-commit && cd ..; \
		fi; \
	done
	@echo "✅ Pre-commit complete in all projects!"

# Environment variables
export PYTHONPATH := $(PWD):$(PYTHONPATH)
export FLEXT_WORKSPACE := $(PWD)
export FLEXT_ENV := development

# ============================================================================
# 📜 SCRIPTS AUTOMATIZADOS - Sistema Integrado
# ============================================================================

# Inclui targets gerados automaticamente pelos scripts
-include scripts/core/Makefile.scripts

# Scripts principais
scripts: ## Lista todos os scripts disponíveis
	@python scripts/core/script_runner.py --list

scripts-help: ## Mostra ajuda detalhada dos scripts
	@python scripts/core/script_runner.py --help

scripts-generate: ## Regenera targets do Makefile para scripts
	@python scripts/core/script_runner.py --generate-makefile

# Atalhos para categorias principais
config-scripts: scripts-config ## Execute scripts de configuração
quality-scripts: scripts-quality ## Execute scripts de qualidade
deps-scripts: scripts-dependencies ## Execute scripts de dependências

# ============================================================================
# 🔍 DETECÇÃO DE CÓDIGO DUPLICADO
# ============================================================================

detect-duplicates: ## Detecta código duplicado no workspace Flext
	@echo "🔍 Detecting duplicate code in FLEXT workspace..."
	@python scripts/quality/detect_duplicates.py
	@echo "✅ Duplicate code detection complete!"

detect-duplicates-ci: ## Detecta código duplicado em modo CI/CD
	@echo "🔍 Detecting duplicate code (CI/CD mode)..."
	@python scripts/quality/detect_duplicates.py --ci-mode
	@echo "✅ CI/CD duplicate code check complete!"

detect-duplicates-report: ## Detecta código duplicado e gera relatório JSON
	@echo "🔍 Detecting duplicate code and generating report..."
	@python scripts/quality/detect_duplicates.py --output reports/duplicate_code_report.json
	@echo "✅ Duplicate code report generated!"

detect-duplicates-modules: ## Detecta código duplicado em módulos específicos
	@echo "🔍 Detecting duplicate code in specific modules..."
	@python scripts/quality/detect_duplicates.py --modules flext-core flext-ldap flext-grpc
	@echo "✅ Module-specific duplicate code detection complete!"

detect-duplicates-all: ## Detecta duplicação em todos os arquivos rastreáveis pelo git
	@echo "🔍 Detecting duplicates in all git-trackable files..."
	@python scripts/quality/detect_duplicates.py --all-files
	@echo "✅ All files duplicate detection complete!"

detect-duplicates-all-ci: ## Detecta duplicação em todos os arquivos (modo CI/CD)
	@echo "🔍 Detecting duplicates in all files (CI/CD mode)..."
	@python scripts/quality/detect_duplicates.py --all-files --ci-mode
	@echo "✅ All files CI/CD duplicate check complete!"

detect-duplicates-all-report: ## Detecta duplicação em todos os arquivos e gera relatório
	@echo "🔍 Detecting duplicates in all files and generating report..."
	@python scripts/quality/detect_duplicates.py --all-files --output reports/all_files_duplicate_report.json
	@echo "✅ All files duplicate report generated!"

duplicates: detect-duplicates ## Alias para detect-duplicates
duplicates-ci: detect-duplicates-ci ## Alias para detect-duplicates-ci
duplicates-report: detect-duplicates-report ## Alias para detect-duplicates-report
duplicates-all: detect-duplicates-all ## Alias para detect-duplicates-all
