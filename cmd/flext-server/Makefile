# =============================================================================
# FLEXT-SERVER - Go HTTP Server Application
# =============================================================================
# Go server application with Clean Architecture + DDD + Zero Tolerance Quality
# =============================================================================

# Project Configuration
PROJECT_NAME := flext-server
BINARY_NAME := flext-server
BUILD_DIR := bin
GO_VERSION := 1.24
MIN_COVERAGE := 80

# Server Configuration
SERVER_PORT := 8080
SERVER_HOST := localhost
SERVER_ENV := development

# Export variables
export GO_VERSION MIN_COVERAGE BINARY_NAME SERVER_PORT SERVER_HOST SERVER_ENV

# =============================================================================
# HELP & INFORMATION
# =============================================================================

.PHONY: help
help: ## Show available commands
	@echo "FLEXT-SERVER - Go HTTP Server Application"
	@echo "========================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: info
info: ## Show project information
	@echo "Project: $(PROJECT_NAME)"
	@echo "Binary: $(BINARY_NAME)"
	@echo "Go Version: $(GO_VERSION)+"
	@echo "Coverage: $(MIN_COVERAGE)%"
	@echo "Architecture: Clean Architecture + DDD"
	@echo "Server: $(SERVER_HOST):$(SERVER_PORT)"

# =============================================================================
# DEPENDENCIES & SETUP
# =============================================================================

.PHONY: setup
setup: ## Complete project setup
	@echo "🚀 Setting up project..."
	@go mod download
	@go mod tidy
	@echo "✅ Setup complete"

.PHONY: deps
deps: ## Download dependencies
	@echo "📦 Downloading dependencies..."
	@go mod download

.PHONY: tidy
tidy: ## Tidy Go modules
	@echo "🔧 Tidying modules..."
	@go mod tidy

.PHONY: verify
verify: ## Verify Go modules
	@echo "🔍 Verifying modules..."
	@go mod verify

# =============================================================================
# BUILD & DISTRIBUTION
# =============================================================================

.PHONY: build
build: ## Build the server application
	@echo "🏗️ Building $(BINARY_NAME)..."
	@mkdir -p $(BUILD_DIR)
	@go build -o $(BUILD_DIR)/$(BINARY_NAME) .

.PHONY: build-release
build-release: ## Build optimized release
	@echo "🏗️ Building release..."
	@mkdir -p $(BUILD_DIR)
	@go build -ldflags="-s -w" -o $(BUILD_DIR)/$(BINARY_NAME) .

.PHONY: build-all
build-all: ## Build for multiple platforms
	@echo "🏗️ Building for all platforms..."
	@mkdir -p $(BUILD_DIR)
	@GOOS=linux GOARCH=amd64 go build -o $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64 .
	@GOOS=darwin GOARCH=amd64 go build -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 .
	@GOOS=windows GOARCH=amd64 go build -o $(BUILD_DIR)/$(BINARY_NAME)-windows.exe .

.PHONY: install
install: ## Install server to GOPATH
	@echo "📦 Installing $(BINARY_NAME)..."
	@go install .

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run all tests with coverage
	@echo "🧪 Running tests..."
	@go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
	@go tool cover -func=coverage.out

.PHONY: test-unit
test-unit: ## Run unit tests only
	@go test -v -short ./...

.PHONY: test-integration
test-integration: ## Run integration tests
	@go test -v -run Integration ./...

.PHONY: test-race
test-race: ## Run tests with race detection
	@go test -v -race ./...

.PHONY: bench
bench: ## Run benchmark tests
	@go test -v -bench=. -benchmem ./...

.PHONY: coverage
coverage: ## Generate HTML coverage report
	@go test -coverprofile=coverage.out ./...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "📊 Coverage report: coverage.html"

# =============================================================================
# QUALITY GATES
# =============================================================================

.PHONY: validate
validate: ## Complete validation (quality gate)
	@echo "🔍 Running validation..."
	@make lint
	@make vet
	@make security
	@make test
	@make verify
	@echo "✅ Validation complete"

.PHONY: check
check: ## Quick health check
	@echo "🏥 Health check..."
	@make lint
	@make vet

.PHONY: lint
lint: ## Run Go linting
	@echo "🧹 Linting..."
	@golangci-lint run

.PHONY: format
format: ## Format Go code
	@echo "🎨 Formatting..."
	@go fmt ./...
	@goimports -w .

.PHONY: format-check
format-check: ## Check code formatting
	@test -z "$$(gofmt -l .)"

.PHONY: vet
vet: ## Run go vet
	@echo "🔍 Running vet..."
	@go vet ./...

.PHONY: security
security: ## Security scanning
	@echo "🔒 Security scan..."
	@gosec ./...

.PHONY: fix
fix: ## Auto-fix issues
	@make format
	@golangci-lint run --fix

# =============================================================================
# SERVER OPERATIONS
# =============================================================================

.PHONY: run
run: ## Run the server in development
	@echo "🚀 Running $(BINARY_NAME)..."
	@go run .

.PHONY: serve
serve: build ## Start server (production)
	@echo "🌐 Starting server..."
	@./$(BUILD_DIR)/$(BINARY_NAME) -port=$(SERVER_PORT) -host=$(SERVER_HOST)

.PHONY: serve-dev
serve-dev: ## Start server (development)
	@echo "🛠️ Starting dev server..."
	@go run . -dev -port=$(SERVER_PORT) -host=$(SERVER_HOST)

.PHONY: serve-prod
serve-prod: build-release ## Start server (production)
	@echo "🏭 Starting production server..."
	@./$(BUILD_DIR)/$(BINARY_NAME) -prod -port=$(SERVER_PORT) -host=$(SERVER_HOST)

.PHONY: health-check
health-check: ## Check server health
	@echo "🏥 Checking server health..."
	@curl -f http://$(SERVER_HOST):$(SERVER_PORT)/health || echo "❌ Server not responding"

.PHONY: status
status: ## Get server status
	@echo "📊 Getting server status..."
	@curl -s http://$(SERVER_HOST):$(SERVER_PORT)/status || echo "❌ Status not available"

.PHONY: metrics
metrics: ## Get server metrics
	@echo "📊 Getting server metrics..."
	@curl -s http://$(SERVER_HOST):$(SERVER_PORT)/metrics || echo "❌ Metrics not available"

.PHONY: load-test
load-test: ## Run load tests
	@echo "🧪 Running load tests..."
	@go test -v -run LoadTest ./...

.PHONY: server-stop
server-stop: ## Stop running server
	@echo "🛑 Stopping server..."
	@pkill -f $(BINARY_NAME) || echo "Server not running"

# =============================================================================
# MAINTENANCE
# =============================================================================

.PHONY: clean
clean: ## Clean build artifacts
	@echo "🧹 Cleaning..."
	@rm -rf $(BUILD_DIR)
	@rm -f coverage.out coverage.html
	@go clean

.PHONY: clean-all
clean-all: clean ## Deep clean with cache
	@echo "🧹 Deep cleaning..."
	@go clean -cache -modcache -testcache

.PHONY: reset
reset: clean-all setup ## Reset to clean state

.PHONY: deps-update
deps-update: ## Update dependencies
	@echo "🔄 Updating deps..."
	@go get -u ./...
	@go mod tidy

.PHONY: deps-audit
deps-audit: ## Audit dependencies
	@echo "🔍 Auditing deps..."
	@go list -json -deps ./... | nancy sleuth

# =============================================================================
# DIAGNOSTICS
# =============================================================================

.PHONY: diagnose
diagnose: ## Project diagnostics
	@echo "🔬 Diagnostics..."
	@echo "Go: $$(go version)"
	@go list -m
	@go env GOOS GOARCH

.PHONY: doctor
doctor: ## Complete health check
	@make diagnose
	@make check

# =============================================================================
# ALIASES
# =============================================================================

.PHONY: t l f b c r v s h
t: test
l: lint
f: format
b: build
c: clean
r: run
v: validate
s: serve
h: health-check

.DEFAULT_GOAL := help