# FLEXT WORKSPACE - Master Makefile - Python 3.13 Enterprise Standards
# ====================================================================
# Comprehensive multi-project coordination with zero-tolerance quality gates
# Updated: 2025-01-06 | Python 3.13 | Bleeding-edge tooling | Clean Architecture | DDD

.PHONY: help install test clean lint format build docs dev security type-check pre-commit
.PHONY: workspace-* project-* all-* setup-* check-*

# Default target
help: ## Show this help message
	@echo "🚀 FLEXT WORKSPACE - Master Coordinator"
	@echo "======================================="
	@echo "🏗️  Multi-project enterprise workspace with 20+ Python projects"
	@echo "🎯 Clean Architecture + DDD + Python 3.13 + Poetry"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# Core Projects
CORE_PROJECTS := flext-core
API_PROJECTS := flext-api flext-auth flext-grpc flext-web
CLI_PROJECTS := flext-cli
DATA_PROJECTS := flext-tap-ldap flext-tap-oracle-oic flext-tap-oracle-wms \
	flext-target-ldap flext-target-oracle flext-target-oracle-oic flext-dbt-ldap
INFRA_PROJECTS := flext-observability flext-quality flext-plugin flext-meltano \
	flext-ldap flext-db-oracle flext-meltano-bridge
EXTENSION_PROJECTS := flext-oracle-oic-ext
PROJECT_APPS := client-a-oud-mig client-b-poc-oic-wms client-b-meltano-native

ALL_PROJECTS := $(CORE_PROJECTS) $(API_PROJECTS) $(CLI_PROJECTS) $(DATA_PROJECTS) $(INFRA_PROJECTS) $(EXTENSION_PROJECTS) $(PROJECT_APPS)

# ============================================================================
# 🚀 WORKSPACE MANAGEMENT
# ============================================================================

workspace-setup: ## Complete workspace setup
	@echo "🎯 Setting up FLEXT enterprise workspace..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "📦 Setting up $$project..."; \
			cd "$$project" && $(MAKE) install-dev && cd ..; \
		fi; \
	done
	@echo "✅ Workspace setup complete!"

workspace-install: ## Install all project dependencies
	@echo "📦 Installing dependencies for all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "⚡ Installing $$project..."; \
			cd "$$project" && poetry install --all-extras && cd ..; \
		fi; \
	done
	@echo "✅ All dependencies installed!"

workspace-update: ## Update all project dependencies
	@echo "🔄 Updating dependencies for all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔄 Updating $$project..."; \
			cd "$$project" && poetry update && cd ..; \
		fi; \
	done
	@echo "✅ All dependencies updated!"

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

type-check-all: ## Type check all projects
	@echo "🎯 Type checking all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🎯 Type checking $$project..."; \
			cd "$$project" && $(MAKE) type-check && cd ..; \
		fi; \
	done
	@echo "✅ All type checking complete!"

security-all: ## Security check all projects
	@echo "🔒 Security checking all projects..."
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "🔒 Security checking $$project..."; \
			cd "$$project" && $(MAKE) security && cd ..; \
		fi; \
	done
	@echo "✅ All security checks complete!"

check-all: lint-all type-check-all security-all test-all ## Run all quality checks
	@echo "✅ All quality checks complete for entire workspace!"

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
	@echo "========================"
	@echo "🏗️  Total Projects: $(words $(ALL_PROJECTS))"
	@echo "🎯 Core Projects: $(CORE_PROJECTS)"
	@echo "🚀 API Projects: $(API_PROJECTS)"
	@echo "🗂️  Data Projects: $(DATA_PROJECTS)"
	@echo "🔧 Infrastructure: $(INFRA_PROJECTS)"
	@echo "📱 Applications: $(PROJECT_APPS)"
	@echo ""
	@echo "🔍 Project Status:"
	@for project in $(ALL_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  ✅ $$project (exists)"; \
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

clean-workspace: workspace-clean ## Clean entire workspace
	@echo "🧹 Cleaning workspace..."
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
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
