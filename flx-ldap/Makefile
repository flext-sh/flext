.PHONY: help install install-dev test test-unit test-integration test-e2e lint format format-check type-check security clean build publish docs serve-docs docker-test docker-clean pre-commit all

# Configuration
PYTHON := python
POETRY := poetry
SOURCE_DIR := src
TEST_DIR := tests
PACKAGE_NAME := flx_ldap

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

install-all: ## Install all dependencies and extras
	@echo "$(BLUE)Installing all dependencies...$(RESET)"
	$(POETRY) install --with dev,e2e --extras all

# Testing targets
test: test-unit test-integration ## Run all tests
	@echo "$(GREEN)All tests completed!$(RESET)"

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/unit -v --cov=$(SOURCE_DIR)/$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html --cov-report=xml

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/integration -v --cov=$(SOURCE_DIR)/$(PACKAGE_NAME) --cov-append --cov-report=term-missing

test-e2e: ## Run E2E tests with Docker
	@echo "$(BLUE)Running E2E tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/e2e -v --tb=short

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR) -v --cov=$(SOURCE_DIR)/$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=90

# Code quality targets
lint: ## Run linting (ruff + additional checks)
	@echo "$(BLUE)Running linter...$(RESET)"
	$(POETRY) run ruff check $(SOURCE_DIR) $(TEST_DIR)
	$(POETRY) run ruff format --check $(SOURCE_DIR) $(TEST_DIR)

format: ## Format code with ruff and black
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(POETRY) run ruff format $(SOURCE_DIR) $(TEST_DIR)
	$(POETRY) run ruff check --fix $(SOURCE_DIR) $(TEST_DIR)

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	$(POETRY) run ruff format --check $(SOURCE_DIR) $(TEST_DIR)

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(RESET)"
	$(POETRY) run mypy $(SOURCE_DIR)

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	$(POETRY) run bandit -r $(SOURCE_DIR) -f json -o bandit-report.json || true
	$(POETRY) run safety check

# flx-ldap specific targets
extract: ## Run LDAP data extraction
	@echo "$(BLUE)Running LDAP extraction...$(RESET)"
	$(POETRY) run flx-ldap extract --config config.json

transform: ## Run dbt transformations
	@echo "$(BLUE)Running transformations...$(RESET)"
	$(POETRY) run flx-ldap transform --config config.json

load: ## Run data loading to target LDAP
	@echo "$(BLUE)Running data loading...$(RESET)"
	$(POETRY) run flx-ldap load --config config.json

sync: ## Run complete sync pipeline
	@echo "$(BLUE)Running complete sync pipeline...$(RESET)"
	$(POETRY) run flx-ldap sync --config config.json

migrate: ## Run LDAP migration with comparison
	@echo "$(BLUE)Running LDAP migration...$(RESET)"
	$(POETRY) run flx-ldap migrate --config config.json

validate: ## Validate configuration and components
	@echo "$(BLUE)Validating configuration...$(RESET)"
	$(POETRY) run flx-ldap validate --config config.json

status: ## Show pipeline status
	@echo "$(BLUE)Checking pipeline status...$(RESET)"
	$(POETRY) run flx-ldap status --config config.json

# Pipeline workflow targets
pipeline-extract: extract ## Run extraction pipeline
	@echo "$(GREEN)Extraction pipeline completed!$(RESET)"

pipeline-transform: transform ## Run transformation pipeline
	@echo "$(GREEN)Transformation pipeline completed!$(RESET)"

pipeline-load: load ## Run loading pipeline
	@echo "$(GREEN)Loading pipeline completed!$(RESET)"

pipeline-full: sync ## Run full pipeline
	@echo "$(GREEN)Full pipeline completed!$(RESET)"

# Development targets
clean: ## Clean build artifacts and cache
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
	rm -rf data/
	rm -rf output/
	rm -rf logs/
	rm -rf state/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build package
	@echo "$(BLUE)Building package...$(RESET)"
	$(POETRY) build

publish: ## Publish package to PyPI
	@echo "$(BLUE)Publishing package...$(RESET)"
	$(POETRY) publish

publish-test: ## Publish package to Test PyPI
	@echo "$(BLUE)Publishing package to Test PyPI...$(RESET)"
	$(POETRY) publish --repository testpypi

# Docker targets
docker-test: ## Run tests in Docker environment
	@echo "$(BLUE)Starting Docker test environment...$(RESET)"
	docker-compose -f docker-compose.yml up -d
	@echo "$(YELLOW)Waiting for services to be ready...$(RESET)"
	sleep 20
	$(POETRY) run pytest $(TEST_DIR)/e2e -v
	docker-compose -f docker-compose.yml down -v

docker-clean: ## Clean Docker environment
	@echo "$(BLUE)Cleaning Docker environment...$(RESET)"
	docker-compose -f docker-compose.yml down -v --remove-orphans
	docker system prune -f

docker-logs: ## Show Docker container logs
	@echo "$(BLUE)Showing Docker logs...$(RESET)"
	docker-compose -f docker-compose.yml logs

# Pre-commit and CI targets
pre-commit: format lint type-check security test-unit ## Run pre-commit checks
	@echo "$(GREEN)Pre-commit checks completed!$(RESET)"

ci: install-dev pre-commit test-coverage ## Run CI pipeline
	@echo "$(GREEN)CI pipeline completed!$(RESET)"

# Convenience targets
all: clean install-all pre-commit test build ## Run complete development cycle
	@echo "$(GREEN)Complete development cycle finished!$(RESET)"

check: lint type-check security ## Run all code quality checks
	@echo "$(GREEN)Code quality checks completed!$(RESET)"

dev-setup: install-all ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	$(POETRY) install --with dev,e2e --extras all
	@echo "$(GREEN)Development environment ready!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Copy config.example.json to config.json and update with your settings"
	@echo "  2. Run 'make validate' to test your configuration"
	@echo "  3. Run 'make test' to ensure everything works"
	@echo "  4. Run 'make sync' to test the full pipeline"

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
	@echo "Package: $(PACKAGE_NAME)"
	@echo "Source: $(SOURCE_DIR)"
	@echo "Tests: $(TEST_DIR)"

debug-config: ## Debug configuration
	@echo "$(BLUE)Configuration Debug:$(RESET)"
	$(POETRY) run flx-ldap validate --config config.json --debug

# Monitoring and observability
monitor: ## Monitor pipeline execution
	@echo "$(BLUE)Starting pipeline monitoring...$(RESET)"
	$(POETRY) run flx-ldap monitor --config config.json

logs: ## Show pipeline logs
	@echo "$(BLUE)Showing pipeline logs...$(RESET)"
	$(POETRY) run flx-ldap logs --config config.json

metrics: ## Show pipeline metrics
	@echo "$(BLUE)Showing pipeline metrics...$(RESET)"
	$(POETRY) run flx-ldap metrics --config config.json

# Configuration management
example-config: ## Create example configuration file
	@echo "$(BLUE)Creating example configuration...$(RESET)"
	@cat > config.example.json << 'EOF'
{
  "tap": {
    "host": "source-ldap.example.com",
    "port": 389,
    "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=com",
    "password": "source_password",
    "base_dn": "dc=source,dc=com",
    "use_ssl": false,
    "user_filter": "(&(objectClass=inetOrgPerson)(employeeType=active))",
    "group_filter": "(objectClass=groupOfNames)"
  },
  "target": {
    "host": "target-ldap.example.com",
    "port": 389,
    "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=com",
    "password": "target_password",
    "base_dn": "dc=target,dc=com",
    "use_ssl": false,
    "validate_records": true,
    "dn_templates": {
      "users": "uid={uid},ou=users,ou=migrated,{base_dn}",
      "groups": "cn={cn},ou=groups,{base_dn}"
    }
  },
  "dbt": {
    "project_dir": "./dbt_project",
    "profiles_dir": "./profiles",
    "target": "prod"
  },
  "migration": {
    "comparison_enabled": true,
    "dry_run": false,
    "batch_size": 100
  },
  "output_path": "./data",
  "log_level": "INFO"
}
EOF
	@echo "$(GREEN)Example configuration created: config.example.json$(RESET)"

validate-config: ## Validate current configuration
	@echo "$(BLUE)Validating configuration...$(RESET)"
	@if [ ! -f "config.json" ]; then \
		echo "$(RED)Error: config.json not found. Run 'make example-config' first.$(RESET)"; \
		exit 1; \
	fi
	$(POETRY) run flx-ldap validate --config config.json

# Backup and restore
backup: ## Create backup of current state
	@echo "$(BLUE)Creating backup...$(RESET)"
	$(POETRY) run flx-ldap backup --config config.json

restore: ## Restore from backup
	@echo "$(BLUE)Restoring from backup...$(RESET)"
	$(POETRY) run flx-ldap restore --config config.json

# Performance testing
perf-test: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/performance -v --tb=short

load-test: ## Run load testing
	@echo "$(BLUE)Running load tests...$(RESET)"
	$(POETRY) run flx-ldap load-test --config config.json

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	$(POETRY) run sphinx-build -b html docs docs/_build/html

serve-docs: docs ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(RESET)"
	cd docs/_build/html && $(PYTHON) -m http.server 8000
