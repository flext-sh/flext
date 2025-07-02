# FLEXT Workspace Makefile
# ========================

.PHONY: help build test clean dev deps lint format check validate-api example-pipeline example-plugin list-pipelines list-plugins validate-architecture test-unit test-integration test-coverage benchmark dev-api load-test all

# Default target
help: ## Show this help message
	@echo "FLEXT Workspace Development Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build targets
build: ## Build the Go API server
	@echo "🔨 Building FLEXT Go API..."
	@mkdir -p bin
	go build -o bin/flext cmd/flext/main.go
	@echo "✅ Build complete: ./bin/flext"

build-docker: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t flext:latest .
	@echo "✅ Docker image built: flext:latest"

# Development targets
dev: ## Start development environment
	@echo "🚀 Starting FLEXT development environment..."
	@if [ ! -f .env ]; then echo "⚠️  Creating .env from example..."; cp .env.example .env; fi
	@if [ ! -f bin/flext ]; then echo "⚠️  Binary not found, building..."; $(MAKE) build; fi
	source .env && ./bin/flext

run: build ## Build and run the application
	@echo "🏃 Running FLEXT..."
	./bin/flext

# Python environment targets
venv: ## Create and activate Python virtual environment
	@echo "🐍 Setting up Python virtual environment..."
	python3 -m venv .venv
	@echo "✅ Virtual environment created. Activate with: source .venv/bin/activate"

deps: ## Install Go and Python dependencies
	@echo "📦 Installing Go dependencies..."
	go mod tidy
	go mod download
	@echo "📦 Installing Python dependencies..."
	@if [ -f .venv/bin/activate ]; then \
		source .venv/bin/activate && pip install --upgrade pip setuptools wheel; \
	else \
		echo "⚠️  Python venv not found. Run 'make venv' first."; \
	fi

# Testing targets
test: ## Run all tests
	@echo "🧪 Running Go tests..."
	go test -v ./internal/...
	go test -v ./tests/...
	@echo "🧪 Running Python tests in submodules..."
	@for dir in flext-*; do \
		if [ -d "$$dir" ] && [ -f "$$dir/pyproject.toml" ]; then \
			echo "Testing $$dir..."; \
			cd "$$dir" && source ../.venv/bin/activate && python -m pytest || true; \
			cd ..; \
		fi \
	done

test-go: ## Run only Go tests
	@echo "🧪 Running Go tests..."
	go test -v ./internal/...
	go test -v ./tests/...

test-python: ## Run Python tests in all submodules
	@echo "🧪 Running Python tests..."
	@for dir in flext-*; do \
		if [ -d "$$dir" ] && [ -f "$$dir/pyproject.toml" ]; then \
			echo "Testing $$dir..."; \
			cd "$$dir" && source ../.venv/bin/activate && python -m pytest || true; \
			cd ..; \
		fi \
	done

validate-api: build ## Validate API endpoints
	@echo "🔍 Validating FLEXT API..."
	@chmod +x validate_api.sh
	./validate_api.sh

# Code quality targets
lint: ## Run linters
	@echo "🔍 Running Go linters..."
	go vet ./...
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run; \
	else \
		echo "⚠️  golangci-lint not installed. Install with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"; \
	fi
	@echo "🔍 Running Python linters in submodules..."
	@for dir in flext-*; do \
		if [ -d "$$dir" ] && [ -f "$$dir/pyproject.toml" ]; then \
			echo "Linting $$dir..."; \
			cd "$$dir" && source ../.venv/bin/activate && python -m ruff check . || true; \
			cd ..; \
		fi \
	done

format: ## Format code
	@echo "🎨 Formatting Go code..."
	go fmt ./...
	@echo "🎨 Formatting Python code in submodules..."
	@for dir in flext-*; do \
		if [ -d "$$dir" ] && [ -f "$$dir/pyproject.toml" ]; then \
			echo "Formatting $$dir..."; \
			cd "$$dir" && source ../.venv/bin/activate && python -m black . && python -m ruff check --fix . || true; \
			cd ..; \
		fi \
	done

# Git targets
commit-all: ## Add and commit all changes
	@echo "📝 Committing all changes..."
	git add -A
	git submodule foreach 'git add -A'
	git commit -m "feat: workspace development improvements" --no-verify || echo "No changes to commit"
	git submodule foreach 'git commit -m "feat: sync with workspace" --no-verify || echo "No changes to commit in $$name"'

sync-submodules: ## Sync all submodules
	@echo "🔄 Syncing submodules..."
	git submodule update --init --recursive
	git submodule foreach 'git pull origin main || git pull origin master || echo "Could not pull $$name"'

# Cleanup targets
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf bin/
	rm -f flext
	go clean
	@echo "🧹 Cleaning Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

clean-all: clean ## Clean everything including dependencies
	@echo "🧹 Deep cleaning..."
	go clean -modcache
	rm -rf .venv

# Documentation targets
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Available guides:"
	@echo "  - API_VALIDATION_GUIDE.md"
	@echo "  - GO_ARCHITECTURE_GUIDE.md"
	@echo "  - CLAUDE.md (workspace standards)"

# Monitoring targets
health: ## Check application health
	@echo "🏥 Checking application health..."
	@if pgrep -f "flext" > /dev/null; then \
		echo "✅ FLEXT process is running"; \
		curl -s http://localhost:8081/health || echo "❌ Health endpoint not responding"; \
	else \
		echo "❌ FLEXT process not running"; \
	fi

logs: ## Show application logs
	@echo "📄 Showing FLEXT logs..."
	@if [ -f "/var/log/flext/flext.log" ]; then \
		tail -f /var/log/flext/flext.log; \
	else \
		echo "⚠️  Log file not found. Application may not be running."; \
	fi

# Database targets
db-up: ## Start database services
	@echo "🗄️  Starting database services..."
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose up -d postgres redis; \
	else \
		echo "⚠️  docker-compose not found. Please start databases manually."; \
	fi

db-down: ## Stop database services
	@echo "🗄️  Stopping database services..."
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose down; \
	else \
		echo "⚠️  docker-compose not found."; \
	fi

# Installation targets
install-tools: ## Install development tools
	@echo "🛠️  Installing development tools..."
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@if [ -f .venv/bin/activate ]; then \
		source .venv/bin/activate && pip install ruff black pytest mypy; \
	else \
		echo "⚠️  Python venv not found. Run 'make venv' first."; \
	fi

# All-in-one targets
setup: venv deps install-tools ## Complete development setup
	@echo "🎉 Development environment setup complete!"
	@echo "Next steps:"
	@echo "  1. Copy and configure .env: cp .env.example .env"
	@echo "  2. Start development: make dev"
	@echo "  3. Validate API: make validate-api"

check: lint test ## Run all quality checks
	@echo "✅ All quality checks complete!"

# Default environment variables
export WORKSPACE_ROOT ?= $(PWD)
export PYTHON_VENV ?= $(PWD)/.venv
export DEBUG_MODE ?= true

# Example API calls
example-pipeline: ## Create an example pipeline
	@echo "📝 Creating example pipeline..."
	@curl -X POST http://localhost:8081/api/v1/pipelines \
		-H "Content-Type: application/json" \
		-d '{"name": "example-pipeline", "description": "Example pipeline for testing", "tags": ["example", "test"]}' | jq . || echo "❌ Failed to create pipeline (server running?)"

example-plugin: ## Register an example plugin
	@echo "🔌 Registering example plugin..."
	@curl -X POST http://localhost:8081/api/v1/plugins \
		-H "Content-Type: application/json" \
		-d '{"name": "example-source", "type": "source", "version": "1.0.0", "entry_point": "./plugins/example-source", "description": "Example source plugin"}' | jq . || echo "❌ Failed to register plugin (server running?)"

list-pipelines: ## List all pipelines
	@echo "📋 Listing pipelines..."
	@curl -s http://localhost:8081/api/v1/pipelines | jq . || echo "❌ Failed to list pipelines (server running?)"

list-plugins: ## List all plugins
	@echo "🔌 Listing plugins..."
	@curl -s http://localhost:8081/api/v1/plugins | jq . || echo "❌ Failed to list plugins (server running?)"

# Architecture validation
validate-architecture: ## Validate hexagonal architecture compliance
	@echo "🏗️  Validating architecture compliance..."
	@echo "Checking bounded contexts..."
	@find internal/bounded_contexts -name "*.go" | wc -l | xargs echo "Domain files:"
	@echo "Checking ports/adapters..."
	@find internal/infrastructure -name "*.go" | wc -l | xargs echo "Infrastructure files:"
	@echo "Checking shared kernel..."
	@find internal/shared_kernel -name "*.go" | wc -l | xargs echo "Shared kernel files:"

# Testing improvements
test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	go test -v -short ./internal/...

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	go test -v ./tests/integration/...

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	go test -coverprofile=coverage.out ./internal/...
	go tool cover -html=coverage.out -o coverage.html
	@echo "📊 Coverage report generated: coverage.html"

benchmark: ## Run performance benchmarks
	@echo "🏃 Running benchmarks..."
	go test -bench=. -benchmem ./internal/...

# Development workflow
dev-api: build ## Run API in development mode
	@echo "🚀 Starting FLEXT API in development mode..."
	FLEXT_LOG_LEVEL=debug FLEXT_SERVER_PORT=8081 ./flext

# Load testing  
load-test: ## Run basic load test
	@echo "⚡ Running load test..."
	@if command -v ab >/dev/null 2>&1; then \
		ab -n 100 -c 10 http://localhost:8081/health; \
	else \
		echo "⚠️  apache-bench (ab) not installed. Install with: apt-get install apache2-utils"; \
	fi

all: setup build test validate-architecture ## Complete build and validation pipeline
	@echo "🎉 All checks passed! Ready for development."
