# =============================================================================
# CMD-FLEXT-CLI - PROJECT MAKEFILE
# =============================================================================
# Enterprise Go CLI Application with Clean Architecture + DDD + Zero Tolerance Quality
# Go 1.21+ + Modern Build Tools + Professional Standards
# =============================================================================

# Project Configuration
PROJECT_NAME := cmd-flext-cli
PROJECT_TYPE := go-cli
GO_VERSION := 1.21
BINARY_NAME := flext-cli
SRC_DIR := .
TESTS_DIR := .
DOCS_DIR := docs

# Quality Gates Configuration
MIN_COVERAGE := 80
GO_LINT_CONFIG := .golangci.yml
BUILD_DIR := bin

# Export environment variables
export GO_VERSION
export MIN_COVERAGE
export BINARY_NAME

# =============================================================================
# HELP & INFORMATION
# =============================================================================

.PHONY: help
help: ## Show available commands
	@echo "$(PROJECT_NAME) - Go CLI Application"
	@echo "===================================="
	@echo ""
	@echo "📋 AVAILABLE COMMANDS:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-18s %s\\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🔧 PROJECT INFO:"
	@echo "  Type: $(PROJECT_TYPE)"
	@echo "  Go Version: $(GO_VERSION)"
	@echo "  Coverage: $(MIN_COVERAGE)%"
	@echo "  Binary: $(BINARY_NAME)"

.PHONY: info
info: ## Show project information
	@echo "Project Information"
	@echo "=================="
	@echo "Name: $(PROJECT_NAME)"
	@echo "Type: $(PROJECT_TYPE)"
	@echo "Go Version: $(GO_VERSION)"
	@echo "Binary Name: $(BINARY_NAME)"
	@echo "Source Directory: $(SRC_DIR)"
	@echo "Tests Directory: $(TESTS_DIR)"
	@echo "Quality Standards: Zero Tolerance"
	@echo "Architecture: Clean Architecture + DDD + Go"

# =============================================================================
# INSTALLATION & SETUP
# =============================================================================

.PHONY: setup
setup: ## Complete project setup
	@echo "🚀 Setting up $(PROJECT_NAME)..."
	@make deps-download
	@make mod-tidy
	@echo "✅ Setup complete"

.PHONY: deps-download
deps-download: ## Download Go dependencies
	@echo "📦 Downloading dependencies..."
	@go mod download

.PHONY: mod-tidy
mod-tidy: ## Tidy Go modules
	@echo "🔧 Tidying Go modules..."
	@go mod tidy

.PHONY: mod-verify
mod-verify: ## Verify Go modules
	@echo "🔍 Verifying Go modules..."
	@go mod verify

# =============================================================================
# QUALITY GATES & VALIDATION
# =============================================================================

.PHONY: validate
validate: ## Run complete validation (quality gate)
	@echo "🔍 Running complete validation for $(PROJECT_NAME)..."
	@make lint
	@make vet
	@make security
	@make test
	@make mod-verify
	@echo "✅ Validation complete"

.PHONY: check
check: ## Quick health check
	@echo "🏥 Running health check..."
	@make lint
	@make vet
	@echo "✅ Health check complete"

.PHONY: lint
lint: ## Run Go linting
	@echo "🧹 Running linting..."
	@golangci-lint run

.PHONY: format
format: ## Format Go code
	@echo "🎨 Formatting code..."
	@go fmt ./...
	@goimports -w .

.PHONY: format-check
format-check: ## Check Go code formatting
	@echo "🎨 Checking code formatting..."
	@test -z "$$(gofmt -l .)"

.PHONY: vet
vet: ## Run Go vet
	@echo "🔍 Running go vet..."
	@go vet ./...

.PHONY: security
security: ## Run security scanning
	@echo "🔒 Running security scanning..."
	@gosec ./...

.PHONY: fix
fix: ## Auto-fix code issues
	@echo "🔧 Auto-fixing code issues..."
	@make format
	@golangci-lint run --fix

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run all tests with coverage
	@echo "🧪 Running tests with coverage..."
	@go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
	@go tool cover -func=coverage.out

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@go test -v -short ./...

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@go test -v -run Integration ./...

.PHONY: test-race
test-race: ## Run tests with race detection
	@echo "🧪 Running tests with race detection..."
	@go test -v -race ./...

.PHONY: test-bench
test-bench: ## Run benchmark tests
	@echo "🧪 Running benchmark tests..."
	@go test -v -bench=. -benchmem ./...

.PHONY: coverage
coverage: ## Generate coverage report
	@echo "📊 Generating coverage report..."
	@go test -coverprofile=coverage.out ./...
	@go tool cover -html=coverage.out -o coverage.html

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report
	@echo "📊 Generating HTML coverage report..."
	@go test -coverprofile=coverage.out ./...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "📊 Coverage report: coverage.html"

# =============================================================================
# BUILD & DISTRIBUTION
# =============================================================================

.PHONY: build
build: ## Build the application
	@echo "🏗️ Building $(BINARY_NAME)..."
	@mkdir -p $(BUILD_DIR)
	@go build -o $(BUILD_DIR)/$(BINARY_NAME) .

.PHONY: build-release
build-release: ## Build release version
	@echo "🏗️ Building release version..."
	@mkdir -p $(BUILD_DIR)
	@go build -ldflags="-s -w" -o $(BUILD_DIR)/$(BINARY_NAME) .

.PHONY: build-all
build-all: ## Build for all platforms
	@echo "🏗️ Building for all platforms..."
	@mkdir -p $(BUILD_DIR)
	@GOOS=linux GOARCH=amd64 go build -o $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64 .
	@GOOS=darwin GOARCH=amd64 go build -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 .
	@GOOS=windows GOARCH=amd64 go build -o $(BUILD_DIR)/$(BINARY_NAME)-windows-amd64.exe .

.PHONY: install
install: ## Install the application
	@echo "📦 Installing $(BINARY_NAME)..."
	@go install .

# =============================================================================
# CLI OPERATIONS
# =============================================================================

.PHONY: run
run: ## Run the application
	@echo "🚀 Running $(BINARY_NAME)..."
	@go run .

.PHONY: cli-test
cli-test: ## Test CLI functionality
	@echo "🔍 Testing CLI functionality..."
	@go run . --version
	@go run . --help

.PHONY: cli-validate
cli-validate: ## Validate CLI commands
	@echo "🔍 Validating CLI commands..."
	@go run . validate

.PHONY: cli-performance
cli-performance: ## Run CLI performance tests
	@echo "⚡ Running CLI performance tests..."
	@go test -bench=BenchmarkCLI -benchmem ./...

# =============================================================================
# DOCUMENTATION
# =============================================================================

.PHONY: docs
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@godoc -http=:6060

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@godoc -http=:6060

# =============================================================================
# DEPENDENCY MANAGEMENT
# =============================================================================

.PHONY: deps-update
deps-update: ## Update dependencies
	@echo "🔄 Updating dependencies..."
	@go get -u ./...
	@go mod tidy

.PHONY: deps-check
deps-check: ## Check for dependency updates
	@echo "🔍 Checking for dependency updates..."
	@go list -u -m all

.PHONY: deps-audit
deps-audit: ## Audit dependencies for security
	@echo "🔍 Auditing dependencies..."
	@go list -json -deps ./... | nancy sleuth

# =============================================================================
# MAINTENANCE & CLEANUP
# =============================================================================

.PHONY: clean
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@rm -f coverage.out coverage.html
	@go clean

.PHONY: clean-all
clean-all: clean ## Deep clean including cache
	@echo "🧹 Deep cleaning..."
	@go clean -cache -modcache -testcache

.PHONY: reset
reset: clean-all ## Reset project to clean state
	@echo "🔄 Resetting project..."
	@make setup

# =============================================================================
# DIAGNOSTICS & TROUBLESHOOTING
# =============================================================================

.PHONY: diagnose
diagnose: ## Run project diagnostics
	@echo "🔬 Running project diagnostics..."
	@echo "Go version: $$(go version)"
	@echo "Project info:"
	@go list -m
	@echo "Environment:"
	@go env

.PHONY: doctor
doctor: ## Check project health
	@echo "👩‍⚕️ Checking project health..."
	@make diagnose
	@make check
	@echo "✅ Health check complete"

# =============================================================================
# CONVENIENCE ALIASES
# =============================================================================

.PHONY: t
t: test ## Alias for test

.PHONY: l
l: lint ## Alias for lint

.PHONY: f
f: format ## Alias for format

.PHONY: b
b: build ## Alias for build

.PHONY: c
c: clean ## Alias for clean

.PHONY: r
r: run ## Alias for run

.PHONY: v
v: validate ## Alias for validate

# =============================================================================
# Default target
# =============================================================================

.DEFAULT_GOAL := help