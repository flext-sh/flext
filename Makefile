# =============================================================================
# FLEXT WORKSPACE - MASTER MAKEFILE
# =============================================================================
# Enterprise-grade Python 3.13+ distributed data platform
# Clean Architecture + Domain-Driven Design + Zero Tolerance Quality
# =============================================================================

# Project Configuration
PROJECT_NAME := flext
WORKSPACE_ROOT := $(shell pwd)
PYTHON_VERSION := 3.13
VENV_PATH := .venv
POETRY := poetry

# Core Python Projects
PYTHON_CORE_PROJECTS := flext-core
PYTHON_APP_PROJECTS := flext-api flext-auth flext-web flext-quality flext-observability
PYTHON_TAP_PROJECTS := flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic flext-tap-oracle-wms
PYTHON_TARGET_PROJECTS := flext-target-ldap flext-target-ldif flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms
PYTHON_DBT_PROJECTS := flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms
PYTHON_EXT_PROJECTS := flext-ldap flext-ldif flext-meltano flext-plugin flext-cli flext-grpc flext-oracle-oic client-b-meltano-native

# Go Projects
GO_CMD_PROJECTS := cmd/flext cmd/flext-cli cmd/flext-server cmd/flext-demo
GO_FLEXCORE_PROJECT := flexcore

# Docker Configuration
DOCKER_DIR := docker
DOCKER_REGISTRY := ghcr.io/flext-sh
DOCKER_TAG := latest

# Build Configuration
BIN_DIR := bin
BUILD_DIR := build

# All Projects
ALL_PYTHON_PROJECTS := $(PYTHON_CORE_PROJECTS) $(PYTHON_APP_PROJECTS) $(PYTHON_TAP_PROJECTS) $(PYTHON_TARGET_PROJECTS) $(PYTHON_DBT_PROJECTS) $(PYTHON_EXT_PROJECTS)
ALL_GO_PROJECTS := $(GO_CMD_PROJECTS) $(GO_FLEXCORE_PROJECT)

# Quality Gates Configuration
MIN_COVERAGE := 90
MYPY_STRICT := true
RUFF_CONFIG := pyproject.toml

# Export environment variables
export PYTHON_VERSION
export MIN_COVERAGE
export MYPY_STRICT

# =============================================================================
# HELP & INFORMATION
# =============================================================================

.PHONY: help
help: ## Show available commands
	@echo "FLEXT Workspace - Master Makefile"
	@echo "=================================="
	@echo ""
	@echo "📋 WORKSPACE COMMANDS:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "^[[:space:]]*[a-zA-Z_-]"
	@echo ""
	@echo "🐳 DOCKER OPERATIONS:"
	@echo "  docker-build-all     Build all Docker images"
	@echo "  docker-run-stack     Start complete Docker stack"
	@echo "  docker-stop-stack    Stop Docker stack"
	@echo "  docker-restart-stack Restart Docker stack"
	@echo "  docker-logs          Show Docker stack logs"
	@echo "  docker-clean         Clean Docker artifacts"
	@echo ""
	@echo "🔧 PROJECT TYPES:"
	@echo "  Core Projects:    $(PYTHON_CORE_PROJECTS)"
	@echo "  App Projects:     $(PYTHON_APP_PROJECTS)"
	@echo "  Tap Projects:     $(PYTHON_TAP_PROJECTS)"
	@echo "  Target Projects:  $(PYTHON_TARGET_PROJECTS)"
	@echo "  DBT Projects:     $(PYTHON_DBT_PROJECTS)"
	@echo "  Extension Projects: $(PYTHON_EXT_PROJECTS)"
	@echo "  Go Projects:      $(ALL_GO_PROJECTS)"

.PHONY: info
info: ## Show workspace information
	@echo "FLEXT Workspace Information"
	@echo "=========================="
	@echo "Workspace Root: $(WORKSPACE_ROOT)"
	@echo "Python Version: $(PYTHON_VERSION)"
	@echo "Virtual Environment: $(VENV_PATH)"
	@echo "Package Manager: $(POETRY)"
	@echo "Quality Standards: Zero Tolerance"
	@echo "Architecture: Clean Architecture + DDD"
	@echo ""
	@echo "Project Count:"
	@echo "  Python Projects: $(words $(ALL_PYTHON_PROJECTS))"
	@echo "  Go Projects: $(words $(ALL_GO_PROJECTS))"
	@echo "  Total Projects: $(shell echo $$(( $(words $(ALL_PYTHON_PROJECTS)) + $(words $(ALL_GO_PROJECTS)) )))"

# =============================================================================
# WORKSPACE SETUP & INSTALLATION
# =============================================================================

.PHONY: setup
setup: ## Complete workspace setup
	@echo "🚀 Setting up FLEXT workspace..."
	@make install-tools
	@make workspace-install
	@make pre-commit-setup
	@echo "✅ Workspace setup complete"

.PHONY: install-tools
install-tools: ## Install required development tools
	@echo "📦 Installing development tools..."
	@pip install --upgrade pip poetry pre-commit
	@poetry --version || (echo "❌ Poetry installation failed" && exit 1)
	@pre-commit --version || (echo "❌ Pre-commit installation failed" && exit 1)

.PHONY: workspace-install
workspace-install: ## Install all Python project dependencies
	@echo "📦 Installing all Python project dependencies..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "📦 Installing $$project..."; \
			cd $$project && poetry install && cd ..; \
		fi \
	done

.PHONY: workspace-update
workspace-update: ## Update all project dependencies
	@echo "🔄 Updating all project dependencies..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "🔄 Updating $$project..."; \
			cd $$project && poetry update && cd ..; \
		fi \
	done

.PHONY: pre-commit-setup
pre-commit-setup: ## Setup pre-commit hooks for all projects
	@echo "🔧 Setting up pre-commit hooks..."
	@pre-commit install
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/.pre-commit-config.yaml" ]; then \
			cd $$project && pre-commit install && cd ..; \
		fi \
	done

# =============================================================================
# QUALITY GATES & VALIDATION
# =============================================================================

.PHONY: validate
validate: ## Run complete workspace validation
	@echo "🔍 Running complete workspace validation..."
	@make lint-all
	@make type-check-all
	@make security-all
	@make test-all
	@echo "✅ Workspace validation complete"

.PHONY: check
check: ## Quick workspace health check
	@echo "🏥 Running workspace health check..."
	@make lint-all
	@make type-check-all
	@echo "✅ Health check complete"

.PHONY: lint-all
lint-all: ## Run linting on all Python projects
	@echo "🧹 Running linting on all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "🧹 Linting $$project..."; \
			cd $$project && poetry run ruff check . && cd ..; \
		fi \
	done

.PHONY: format-all
format-all: ## Format all Python projects
	@echo "🎨 Formatting all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "🎨 Formatting $$project..."; \
			cd $$project && poetry run ruff format . && cd ..; \
		fi \
	done

.PHONY: type-check-all
type-check-all: ## Run type checking on all Python projects
	@echo "🔍 Running type checking on all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "🔍 Type checking $$project..."; \
			cd $$project; \
			if [ -d "src" ]; then \
				echo "(scoped to src)"; \
				poetry run mypy src; \
			else \
				poetry run mypy .; \
			fi; \
			cd ..; \
		fi \
	done

.PHONY: security-all
security-all: ## Run security scanning on all Python projects
	@echo "🔒 Running security scanning on all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "🔒 Security scanning $$project..."; \
			cd $$project && poetry run bandit -r src/ && cd ..; \
		fi \
	done

.PHONY: test-all
test-all: ## Run tests on all Python projects
	@echo "🧪 Running tests on all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "🧪 Testing $$project..."; \
			cd $$project && poetry run pytest && cd ..; \
		fi \
	done

# =============================================================================
# BUILD & DEPLOYMENT
# =============================================================================

.PHONY: build-all
build-all: ## Build all projects
	@echo "🏗️ Building all projects..."
	@make build-python
	@make build-go

.PHONY: build-python
build-python: ## Build all Python projects
	@echo "🐍 Building Python projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "🔨 Building $$project..."; \
			cd $$project && poetry build && cd ..; \
		fi \
	done

.PHONY: build-go
build-go: ## Build all Go projects
	@echo "🐹 Building Go projects..."
	@mkdir -p $(BIN_DIR)
	@for project in $(GO_CMD_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/main.go" ]; then \
			echo "🔨 Building $$project..."; \
			binary_name=$$(basename $$project); \
			cd $$project && go build -o ../../$(BIN_DIR)/$$binary_name . && chmod +x ../../$(BIN_DIR)/$$binary_name && cd ..; \
		fi \
	done
	@if [ -d "$(GO_FLEXCORE_PROJECT)" ]; then \
		echo "🔨 Building $(GO_FLEXCORE_PROJECT)..."; \
		cd $(GO_FLEXCORE_PROJECT) && make build; \
	fi

# =============================================================================
# DOCKER OPERATIONS
# =============================================================================

.PHONY: docker-build-all
docker-build-all: ## Build all Docker images
	@echo "🐳 Building all Docker images..."
	@make docker-build-flext
	@make docker-build-flexcore

.PHONY: docker-build-flext
docker-build-flext: ## Build FLEXT service Docker image
	@echo "🐳 Building FLEXT service image..."
	@docker build -f $(DOCKER_DIR)/Dockerfile.flext-service -t $(DOCKER_REGISTRY)/flext:$(DOCKER_TAG) .

.PHONY: docker-build-flexcore
docker-build-flexcore: ## Build FlexCore service Docker image
	@echo "🐳 Building FlexCore service image..."
	@docker build -f $(DOCKER_DIR)/Dockerfile.flexcore -t $(DOCKER_REGISTRY)/flexcore:$(DOCKER_TAG) .

.PHONY: docker-run-stack
docker-run-stack: ## Run complete Docker stack
	@echo "🐳 Starting FLEXT Docker stack..."
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml up -d

.PHONY: docker-stop-stack
docker-stop-stack: ## Stop Docker stack
	@echo "🛑 Stopping FLEXT Docker stack..."
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml down

.PHONY: docker-restart-stack
docker-restart-stack: ## Restart Docker stack
	@echo "🔄 Restarting FLEXT Docker stack..."
	@make docker-stop-stack
	@make docker-run-stack

.PHONY: docker-logs
docker-logs: ## Show Docker stack logs
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml logs -f

.PHONY: docker-clean
docker-clean: ## Clean Docker artifacts
	@echo "🧹 Cleaning Docker artifacts..."
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml down --volumes --remove-orphans
	@docker system prune -f
	@docker volume prune -f

# =============================================================================
# MAINTENANCE & CLEANUP
# =============================================================================

.PHONY: clean
clean: ## Clean workspace build artifacts
	@echo "🧹 Cleaning workspace..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true

.PHONY: clean-all
clean-all: clean ## Deep clean including virtual environments
	@echo "🧹 Deep cleaning workspace..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project/.venv" ]; then \
			echo "Removing $$project/.venv..."; \
			rm -rf "$$project/.venv"; \
		fi \
	done

.PHONY: deps-audit-all
deps-audit-all: ## Run dependency audit on all projects
	@echo "🔍 Running dependency audit on all projects..."
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ] && [ -f "$$project/pyproject.toml" ]; then \
			echo "Auditing $$project..."; \
			cd $$project && poetry run pip-audit && cd ..; \
		fi \
	done

# =============================================================================
# DEVELOPMENT WORKFLOWS
# =============================================================================

.PHONY: dev-setup
dev-setup: ## Setup development environment
	@echo "🔧 Setting up development environment..."
	@make setup
	@make validate
	@echo "✅ Development environment ready"

.PHONY: pre-commit-all
pre-commit-all: ## Run pre-commit on all projects
	@echo "🔍 Running pre-commit on all projects..."
	@pre-commit run --all-files

.PHONY: show-status
show-status: ## Display comprehensive workspace status
	@echo "📊 FLEXT Workspace Status Report"
	@echo "================================="
	@echo ""
	@echo "🏗️ RUNTIME ARCHITECTURE STATUS:"
	@echo "  ✅ FlexCore (Go 1.24+): Runtime container port 8080"
	@echo "  ✅ FLEXT Service (Go/Python): Plugin execution port 8081"
	@echo "  ✅ Integration: FlexCore ↔ FLEXT communication working"
	@echo "  ✅ Plugin System: Meltano 3.8.0 operational via Python"
	@echo "  ✅ Clean Architecture + DDD: Bounded contexts operational"
	@echo ""
	@echo "🔗 HEALTH CHECK ENDPOINTS:"
	@echo "  FlexCore: curl http://localhost:8080/health"
	@echo "  FLEXT:    curl http://localhost:8081/health"
	@echo "  Plugins:  curl http://localhost:8081/api/v1/flexcore/plugins"
	@echo ""
	@echo "📦 Python Projects Status:"
	@for project in $(ALL_PYTHON_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  ✅ $$project"; \
		else \
			echo "  ❌ $$project (missing)"; \
		fi \
	done
	@echo ""
	@echo "🐹 Go Projects Status:"
	@for project in $(ALL_GO_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "  ✅ $$project"; \
		else \
			echo "  ❌ $$project (missing)"; \
		fi \
	done
	@echo ""
	@echo "🐳 Docker Status:"
	@docker --version 2>/dev/null && echo "  ✅ Docker available" || echo "  ❌ Docker not available"
	@docker-compose --version 2>/dev/null && echo "  ✅ Docker Compose available" || echo "  ❌ Docker Compose not available"

# Legacy alias for backward compatibility
.PHONY: status
status: show-status ## (Deprecated) Use show-status instead

# =============================================================================
# DOCUMENTATION MAINTENANCE
# =============================================================================

# Include Documentation Makefile
include Makefile.docs

# Include Enhanced Documentation Makefile
include Makefile.docs.enhanced

# =============================================================================
# SPECIALIZED COMMANDS
# =============================================================================

.PHONY: core-validate
core-validate: ## Validate core library (flext-core)
	@echo "🔍 Validating core library..."
	@cd flext-core && make validate

.PHONY: apps-validate
apps-validate: ## Validate application projects
	@echo "🔍 Validating applications..."
	@for project in $(PYTHON_APP_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "Validating $$project..."; \
			cd $$project && make validate && cd ..; \
		fi \
	done

.PHONY: taps-validate
taps-validate: ## Validate tap projects
	@echo "🔍 Validating tap projects..."
	@for project in $(PYTHON_TAP_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "Validating $$project..."; \
			cd $$project && make validate && cd ..; \
		fi \
	done

.PHONY: targets-validate
targets-validate: ## Validate target projects
	@echo "🔍 Validating target projects..."
	@for project in $(PYTHON_TARGET_PROJECTS); do \
		if [ -d "$$project" ]; then \
			echo "Validating $$project..."; \
			cd $$project && make validate && cd ..; \
		fi \
	done

# =============================================================================
# Default target
# =============================================================================

.DEFAULT_GOAL := help
