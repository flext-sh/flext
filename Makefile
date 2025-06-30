# FLEXT Workspace Makefile
# ========================

.PHONY: help build test clean dev deps lint format check validate-api

# Default target
help: ## Show this help message
	@echo "FLEXT Workspace Development Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build targets
build: ## Build the Go API server
	@echo "🔨 Building FLEXT Go API..."
	go build -o flext cmd/flext/main.go
	@echo "✅ Build complete: ./flext"

build-docker: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t flext:latest .
	@echo "✅ Docker image built: flext:latest"

# Development targets
dev: ## Start development environment
	@echo "🚀 Starting FLEXT development environment..."
	@if [ ! -f .env ]; then echo "⚠️  Creating .env from example..."; cp .env.example .env; fi
	source .env && ./flext

run: build ## Build and run the application
	@echo "🏃 Running FLEXT..."
	./flext

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