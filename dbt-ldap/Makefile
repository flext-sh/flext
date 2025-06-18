.PHONY: help install install-dev test test-unit test-integration test-e2e dbt-deps dbt-compile dbt-run dbt-test dbt-docs dbt-clean lint format format-check type-check security clean build docker-test docker-clean pre-commit all

# Configuration
PYTHON := python
POETRY := poetry
DBT := dbt
SOURCE_DIR := models
TEST_DIR := tests
PACKAGE_NAME := dbt_ldap

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
help: ## Show this help message
	@echo "$(BLUE)Available targets:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Installation targets
install: ## Install package dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(POETRY) install

install-dev: ## Install package with development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(POETRY) install --with dev

install-e2e: ## Install package with E2E testing dependencies
	@echo "$(BLUE)Installing E2E testing dependencies...$(RESET)"
	$(POETRY) install --with dev,e2e

install-all: ## Install all dependencies
	@echo "$(BLUE)Installing all dependencies...$(RESET)"
	$(POETRY) install --with dev,e2e

# dbt specific targets
dbt-deps: ## Install dbt dependencies
	@echo "$(BLUE)Installing dbt dependencies...$(RESET)"
	$(POETRY) run $(DBT) deps

dbt-compile: ## Compile dbt models
	@echo "$(BLUE)Compiling dbt models...$(RESET)"
	$(POETRY) run $(DBT) compile

dbt-run: ## Run dbt models
	@echo "$(BLUE)Running dbt models...$(RESET)"
	$(POETRY) run $(DBT) run

dbt-test: ## Run dbt tests
	@echo "$(BLUE)Running dbt tests...$(RESET)"
	$(POETRY) run $(DBT) test

dbt-test-data: ## Run dbt tests with data validation
	@echo "$(BLUE)Running dbt data tests...$(RESET)"
	$(POETRY) run $(DBT) test --data

dbt-docs: ## Generate and serve dbt documentation
	@echo "$(BLUE)Generating dbt documentation...$(RESET)"
	$(POETRY) run $(DBT) docs generate
	$(POETRY) run $(DBT) docs serve

dbt-clean: ## Clean dbt artifacts
	@echo "$(BLUE)Cleaning dbt artifacts...$(RESET)"
	$(POETRY) run $(DBT) clean

dbt-debug: ## Debug dbt configuration
	@echo "$(BLUE)Debugging dbt configuration...$(RESET)"
	$(POETRY) run $(DBT) debug

dbt-lint: ## Lint dbt models with sqlfluff
	@echo "$(BLUE)Linting dbt models...$(RESET)"
	$(POETRY) run sqlfluff lint $(SOURCE_DIR)/ --dialect postgres

dbt-format: ## Format dbt models with sqlfluff
	@echo "$(BLUE)Formatting dbt models...$(RESET)"
	$(POETRY) run sqlfluff fix $(SOURCE_DIR)/ --dialect postgres

# dbt workflow targets
dbt-build: dbt-deps dbt-compile dbt-run dbt-test ## Full dbt build workflow
	@echo "$(GREEN)dbt build completed!$(RESET)"

dbt-refresh: dbt-clean dbt-deps dbt-compile ## Refresh dbt environment
	@echo "$(GREEN)dbt environment refreshed!$(RESET)"

# Specific model targets
dbt-run-staging: ## Run only staging models
	@echo "$(BLUE)Running staging models...$(RESET)"
	$(POETRY) run $(DBT) run --select staging

dbt-run-marts: ## Run only marts models
	@echo "$(BLUE)Running marts models...$(RESET)"
	$(POETRY) run $(DBT) run --select marts

dbt-test-staging: ## Test only staging models
	@echo "$(BLUE)Testing staging models...$(RESET)"
	$(POETRY) run $(DBT) test --select staging

dbt-test-marts: ## Test only marts models
	@echo "$(BLUE)Testing marts models...$(RESET)"
	$(POETRY) run $(DBT) test --select marts

# Testing targets (Python tests if applicable)
test: test-unit test-integration ## Run all Python tests
	@echo "$(GREEN)All tests completed!$(RESET)"

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(RESET)"
	@if [ -d "$(TEST_DIR)/unit" ]; then \
		$(POETRY) run pytest $(TEST_DIR)/unit -v --cov=$(SOURCE_DIR) --cov-report=term-missing --cov-report=html --cov-report=xml; \
	else \
		echo "$(YELLOW)No unit tests found$(RESET)"; \
	fi

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	@if [ -d "$(TEST_DIR)/integration" ]; then \
		$(POETRY) run pytest $(TEST_DIR)/integration -v; \
	else \
		echo "$(YELLOW)No integration tests found$(RESET)"; \
	fi

test-e2e: ## Run E2E tests with Docker
	@echo "$(BLUE)Running E2E tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/e2e -v --tb=short

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	@if [ -d "$(TEST_DIR)" ]; then \
		$(POETRY) run pytest $(TEST_DIR) -v --cov=$(SOURCE_DIR) --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=90; \
	else \
		echo "$(YELLOW)No tests found$(RESET)"; \
	fi

# Code quality targets (for Python code if applicable)
lint: dbt-lint ## Run linting
	@echo "$(BLUE)Running Python linter...$(RESET)"
	@if [ -d "$(TEST_DIR)" ] || [ -d "macros" ]; then \
		$(POETRY) run ruff check . || true; \
	fi

format: dbt-format ## Format code
	@echo "$(BLUE)Formatting code...$(RESET)"
	@if [ -d "$(TEST_DIR)" ] || [ -d "macros" ]; then \
		$(POETRY) run ruff format . || true; \
		$(POETRY) run ruff check --fix . || true; \
	fi

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	@if [ -d "$(TEST_DIR)" ] || [ -d "macros" ]; then \
		$(POETRY) run ruff format --check . || true; \
	fi

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(RESET)"
	@if [ -d "$(TEST_DIR)" ] || [ -d "macros" ]; then \
		$(POETRY) run mypy . || true; \
	fi

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	@if [ -d "$(TEST_DIR)" ] || [ -d "macros" ]; then \
		$(POETRY) run bandit -r . -f json -o bandit-report.json || true; \
		$(POETRY) run safety check; \
	fi

# Development targets
clean: dbt-clean ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -f coverage.xml
	rm -f bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: dbt-build ## Build dbt project
	@echo "$(GREEN)dbt project built!$(RESET)"

# Docker targets
docker-test: ## Run tests in Docker environment
	@echo "$(BLUE)Starting Docker test environment...$(RESET)"
	docker-compose -f docker-compose.yml up -d
	@echo "$(YELLOW)Waiting for services to be ready...$(RESET)"
	sleep 10
	$(POETRY) run $(DBT) debug
	$(POETRY) run $(DBT) run
	$(POETRY) run $(DBT) test
	$(POETRY) run pytest $(TEST_DIR)/e2e -v
	docker-compose -f docker-compose.yml down -v

docker-clean: ## Clean Docker environment
	@echo "$(BLUE)Cleaning Docker environment...$(RESET)"
	docker-compose -f docker-compose.yml down -v --remove-orphans
	docker system prune -f

# Pre-commit and CI targets
pre-commit: format lint dbt-compile dbt-test ## Run pre-commit checks
	@echo "$(GREEN)Pre-commit checks completed!$(RESET)"

ci: install-dev pre-commit test ## Run CI pipeline
	@echo "$(GREEN)CI pipeline completed!$(RESET)"

# Convenience targets
all: clean install-dev dbt-deps pre-commit dbt-build ## Run complete development cycle
	@echo "$(GREEN)Complete development cycle finished!$(RESET)"

check: lint dbt-test ## Run all code quality checks
	@echo "$(GREEN)Code quality checks completed!$(RESET)"

dev-setup: install-dev dbt-deps ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	$(POETRY) install --with dev,e2e
	$(POETRY) run $(DBT) deps
	@echo "$(GREEN)Development environment ready!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Update profiles.yml with your database connection settings"
	@echo "  2. Run 'make dbt-debug' to test your configuration"
	@echo "  3. Run 'make dbt-run' to build your models"
	@echo "  4. Run 'make dbt-test' to validate your data"

# Poetry specific targets
poetry-lock: ## Update poetry.lock file
	@echo "$(BLUE)Updating poetry.lock...$(RESET)"
	$(POETRY) lock

poetry-update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(POETRY) update

poetry-show: ## Show dependency tree
	@echo "$(BLUE)Dependency tree:$(RESET)"
	$(POETRY) show --tree

poetry-export: ## Export requirements.txt
	@echo "$(BLUE)Exporting requirements.txt...$(RESET)"
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

# Debug targets
debug-env: ## Show environment information
	@echo "$(BLUE)Environment Information:$(RESET)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Poetry: $$($(POETRY) --version)"
	@echo "dbt: $$($(POETRY) run $(DBT) --version)"
	@echo "Package: $(PACKAGE_NAME)"
	@echo "Models: $(SOURCE_DIR)"
	@echo "Tests: $(TEST_DIR)"

# Data pipeline targets
pipeline-staging: dbt-run-staging dbt-test-staging ## Run staging pipeline
	@echo "$(GREEN)Staging pipeline completed!$(RESET)"

pipeline-marts: dbt-run-marts dbt-test-marts ## Run marts pipeline
	@echo "$(GREEN)Marts pipeline completed!$(RESET)"

pipeline-full: dbt-run dbt-test ## Run full data pipeline
	@echo "$(GREEN)Full pipeline completed!$(RESET)"

# Profile management
create-profile: ## Create example profiles.yml
	@echo "$(BLUE)Creating example profiles.yml...$(RESET)"
	@mkdir -p ~/.dbt
	@cat > ~/.dbt/profiles.yml << 'EOF'
dbt_ldap:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: dbt_user
      password: dbt_password
      port: 5432
      dbname: dbt_ldap_dev
      schema: dbt_ldap
      threads: 4
      keepalives_idle: 0
    test:
      type: postgres
      host: localhost
      user: dbt_user
      password: dbt_password
      port: 5432
      dbname: dbt_ldap_test
      schema: dbt_ldap_test
      threads: 4
      keepalives_idle: 0
EOF
	@echo "$(GREEN)Example profiles.yml created in ~/.dbt/$(RESET)"
