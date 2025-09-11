# =============================================================================
# FLEXT-DEMO - Go Demo Application
# =============================================================================
# Go demo application with Clean Architecture + DDD + Zero Tolerance Quality
# =============================================================================

# Project Configuration
PROJECT_NAME := flext-demo
BINARY_NAME := flext-demo
BUILD_DIR := bin
GO_VERSION := 1.24
MIN_COVERAGE := 80

# Export variables
export GO_VERSION MIN_COVERAGE BINARY_NAME

# =============================================================================
# HELP & INFORMATION
# =============================================================================

.PHONY: help
help: ## Show available commands
	@echo "FLEXT-DEMO - Go Demo Application"
	@echo "================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: info
info: ## Show project information
	@echo "Project: $(PROJECT_NAME)"
	@echo "Binary: $(BINARY_NAME)"
	@echo "Go Version: $(GO_VERSION)+"
	@echo "Coverage: $(MIN_COVERAGE)%"
	@echo "Architecture: Clean Architecture + DDD"

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
build: ## Build the demo application
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
install: ## Install demo to GOPATH
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
# DEMO OPERATIONS
# =============================================================================

.PHONY: run
run: ## Run the demo application
	@echo "🚀 Running $(BINARY_NAME)..."
	@go run .

.PHONY: demo-basic
demo-basic: ## Run basic demo
	@echo "🎬 Running basic demo..."
	@go run . --demo basic

.PHONY: demo-advanced
demo-advanced: ## Run advanced demo
	@echo "🎬 Running advanced demo..."
	@go run . --demo advanced

.PHONY: demo-interactive
demo-interactive: ## Run interactive demo
	@echo "🎬 Starting interactive demo..."
	@go run . --interactive

.PHONY: demo-all
demo-all: ## Run all demo scenarios
	@echo "🎬 Running all demos..."
	@make demo-basic
	@make demo-advanced
	@echo "✅ All demos complete"

.PHONY: demo-test
demo-test: ## Test demo functionality
	@echo "🧪 Testing demo features..."
	@go run . --test

.PHONY: demo-benchmark
demo-benchmark: ## Run demo benchmarks
	@echo "⚡ Running demo benchmarks..."
	@go test -bench=BenchmarkDemo -benchmem ./...

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

# =============================================================================

.PHONY: t l f b c r v d
t: test
l: lint
f: format
b: build
c: clean
r: run
v: validate
d: demo-all

.DEFAULT_GOAL := help
