.PHONY: help install dev-install lint type-check format test test-unit test-integration test-e2e coverage clean build docker-build docker-up docker-down k8s-deploy proto

# Variables
PYTHON := python3.13
POETRY := poetry
DOCKER_COMPOSE := docker-compose
KUBECTL := kubectl
HELM := helm

# Colors
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)FLX-Meltano Enterprise Platform$(NC)"
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(POETRY) install --no-dev --no-interaction --no-ansi

dev-install: ## Install all dependencies including dev
	$(POETRY) install --no-interaction --no-ansi
	$(POETRY) run pre-commit install

lint: ## Run linting checks
	@echo "$(BLUE)Running ruff...$(NC)"
	$(POETRY) run ruff check src/
	@echo "$(BLUE)Running black check...$(NC)"
	$(POETRY) run black --check src/
	@echo "$(BLUE)Running isort check...$(NC)"
	$(POETRY) run isort --check-only src/
	@echo "$(BLUE)Running bandit security check...$(NC)"
	$(POETRY) run bandit -r src/ -ll
	@echo "$(GREEN)✓ All linting checks passed!$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running mypy...$(NC)"
	$(POETRY) run mypy src/flx src/flx_api src/flx_cli src/flx_web --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking passed!$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Running black...$(NC)"
	$(POETRY) run black src/
	@echo "$(BLUE)Running isort...$(NC)"
	$(POETRY) run isort src/
	@echo "$(BLUE)Running ruff fix...$(NC)"
	$(POETRY) run ruff check --fix src/
	@echo "$(GREEN)✓ Code formatted!$(NC)"

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	$(POETRY) run pytest -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(POETRY) run pytest tests/unit -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(POETRY) run pytest tests/integration -v

test-e2e: ## Run end-to-end tests only
	@echo "$(BLUE)Running e2e tests...$(NC)"
	$(POETRY) run pytest tests/e2e -v

test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	$(POETRY) run pytest tests/performance -v --benchmark-only

coverage: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	$(POETRY) run pytest --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	@echo "$(GREEN)✓ Clean complete!$(NC)"

proto: ## Generate gRPC protocol buffers
	@echo "$(BLUE)Generating gRPC protocol buffers...$(NC)"
	$(POETRY) run python -m grpc_tools.protoc \
		-I./src/flx/grpc/proto \
		--python_out=./src/flx/grpc/proto \
		--grpc_python_out=./src/flx/grpc/proto \
		--mypy_out=./src/flx/grpc/proto \
		./src/flx/grpc/proto/*.proto
	@echo "$(GREEN)✓ Protocol buffers generated!$(NC)"

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(POETRY) build
	@echo "$(GREEN)✓ Build complete!$(NC)"

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml build
	@echo "$(GREEN)✓ Docker images built!$(NC)"

docker-up: ## Start Docker services
	@echo "$(BLUE)Starting Docker services...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml up -d
	@echo "$(GREEN)✓ Services started!$(NC)"

docker-down: ## Stop Docker services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml down
	@echo "$(GREEN)✓ Services stopped!$(NC)"

docker-logs: ## Show Docker logs
	$(DOCKER_COMPOSE) -f docker-compose.yml logs -f

k8s-deploy: ## Deploy to Kubernetes
	@echo "$(BLUE)Deploying to Kubernetes...$(NC)"
	$(HELM) upgrade --install flx-platform \
		./deployments/kubernetes/helm/flx-platform \
		--namespace flx \
		--create-namespace \
		--values ./deployments/kubernetes/helm/flx-platform/values.yaml
	@echo "$(GREEN)✓ Deployed to Kubernetes!$(NC)"

k8s-status: ## Check Kubernetes deployment status
	@echo "$(BLUE)Checking deployment status...$(NC)"
	$(KUBECTL) -n flx get all

migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	cd src && $(POETRY) run python -m flx_web.manage migrate
	@echo "$(GREEN)✓ Migrations complete!$(NC)"

dev-server: ## Start development servers
	@echo "$(BLUE)Starting development servers...$(NC)"
	@echo "$(YELLOW)Start each in a separate terminal:$(NC)"
	@echo "  make daemon    # Start core daemon"
	@echo "  make web       # Start Django web"
	@echo "  make api       # Start FastAPI"

daemon: ## Start FLX daemon
	$(POETRY) run python -m flx.daemon

web: ## Start Django development server
	cd src && $(POETRY) run python -m flx_web.manage runserver

api: ## Start FastAPI development server
	$(POETRY) run uvicorn flx_api.main:app --reload --host 0.0.0.0 --port 8000

cli-install: ## Install CLI globally
	$(POETRY) run pip install -e .
	@echo "$(GREEN)✓ FLX CLI installed! Try: flx --help$(NC)"

check-all: lint type-check test ## Run all checks (lint, type-check, test)
	@echo "$(GREEN)✓ All checks passed!$(NC)"

safety-check: ## Check for security vulnerabilities
	$(POETRY) run safety check
	@echo "$(GREEN)✓ No security vulnerabilities found!$(NC)"

update-deps: ## Update dependencies
	$(POETRY) update
	$(POETRY) run safety check
	@echo "$(GREEN)✓ Dependencies updated!$(NC)"

.DEFAULT_GOAL := help
