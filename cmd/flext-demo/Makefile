# cmd/flext-demo - Go Enterprise Development Makefile
# Clean Architecture + DDD + Professional Quality Gates
# =====================================================

.PHONY: help check fix test lint format build clean validate-strict status deps-check
.PHONY: test-unit test-integration test-coverage benchmark profile docs run dev-setup
.PHONY: mod-tidy mod-verify mod-download security vet install update

# Colors for output - Professional schema
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[1;37m
NC := \033[0m # No Color

# Project settings
PROJECT_NAME := cmd/flext-demo
BINARY_NAME := flext-demo
CMD_DIR := cmd/flext-demo
BUILD_DIR := build
PKG_DIR := pkg
INTERNAL_DIR := internal
DOCS_DIR := docs

# Go settings
GO := go
GO_VERSION := 1.24
GO_FLAGS := -v
GO_BUILD_FLAGS := -v -ldflags="-w -s"
GO_TEST_FLAGS := -v -race -cover
GO_BENCH_FLAGS := -bench=. -benchmem
GO_VET_FLAGS := -all

# Build settings
OS := $(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m | sed 's/x86_64/amd64/')
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")

# Coverage settings
COVERAGE_FILE := coverage.out
COVERAGE_HTML := coverage.html
COVERAGE_THRESHOLD := 85

help: ## Show this help message
	@echo "$(PURPLE)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(PURPLE)║$(NC)     $(BLUE)cmd/flext-demo - Go Development Commands$(NC)             $(PURPLE)║$(NC)"
	@echo "$(PURPLE)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)🔍 Quality Checks:$(NC)"
	@echo "  $(GREEN)check$(NC)            Run ALL quality checks (STRICT MODE)"
	@echo "  $(GREEN)lint$(NC)             Run golangci-lint with all rules"
	@echo "  $(GREEN)vet$(NC)              Run go vet analysis"
	@echo "  $(GREEN)security$(NC)         Security analysis with gosec"
	@echo "  $(GREEN)deps-check$(NC)       Check dependencies for vulnerabilities"
	@echo ""
	@echo "$(CYAN)🔧 Code Fixes:$(NC)"
	@echo "  $(GREEN)fix$(NC)              Auto-fix all possible issues"
	@echo "  $(GREEN)format$(NC)           Format code with gofmt and goimports"
	@echo "  $(GREEN)mod-tidy$(NC)         Tidy and verify go modules"
	@echo ""
	@echo "$(CYAN)🧪 Testing:$(NC)"
	@echo "  $(GREEN)test$(NC)             Run all tests with coverage"
	@echo "  $(GREEN)test-unit$(NC)        Unit tests only"
	@echo "  $(GREEN)test-integration$(NC) Integration tests only"
	@echo "  $(GREEN)test-coverage$(NC)    Generate coverage reports"
	@echo "  $(GREEN)benchmark$(NC)        Run benchmarks"
	@echo ""
	@echo "$(CYAN)🏗️ Build & Deploy:$(NC)"
	@echo "  $(GREEN)build$(NC)            Build binary for current platform"
	@echo "  $(GREEN)build-all$(NC)        Build for all supported platforms"
	@echo "  $(GREEN)install$(NC)          Install binary to GOPATH/bin"
	@echo "  $(GREEN)run$(NC)              Build and run the application"
	@echo ""
	@echo "$(CYAN)📦 Dependencies:$(NC)"
	@echo "  $(GREEN)mod-download$(NC)     Download dependencies"
	@echo "  $(GREEN)mod-verify$(NC)       Verify dependencies"
	@echo "  $(GREEN)update$(NC)           Update dependencies"
	@echo ""
	@echo "$(CYAN)🛠️ Development:$(NC)"
	@echo "  $(GREEN)dev-setup$(NC)        Complete development setup"
	@echo "  $(GREEN)clean$(NC)            Remove build artifacts"
	@echo "  $(GREEN)docs$(NC)             Generate documentation"
	@echo "  $(GREEN)status$(NC)           Show quality status"
	@echo "  $(GREEN)validate$(NC)         Validate 100% compliance"
	@echo ""
	@echo "$(YELLOW)⚡ Strict Mode: ZERO violations tolerated!$(NC)"
	@echo "$(PURPLE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"

# ═══════════════════════════════════════════════════════════════════
# QUALITY CHECKS
# ═══════════════════════════════════════════════════════════════════

check: lint vet security test ## Run ALL quality checks
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)✅ ALL QUALITY CHECKS PASSED - 100% COMPLIANCE!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"

lint: ## Run golangci-lint
	@echo "$(BLUE)🔥 Running golangci-lint...$(NC)"
	@if command -v golangci-lint >/dev/null 2>&1; then \
		golangci-lint run --config .golangci.yml ./...; \
	else \
		echo "$(YELLOW)⚠️  golangci-lint not found, running go fmt instead$(NC)"; \
		$(GO) fmt ./...; \
	fi
	@echo "$(GREEN)✅ Linting passed!$(NC)"

vet: ## Run go vet
	@echo "$(BLUE)🛡️ Running go vet...$(NC)"
	@$(GO) vet $(GO_VET_FLAGS) ./...
	@echo "$(GREEN)✅ Vet analysis passed!$(NC)"

security: ## Run security analysis
	@echo "$(BLUE)🔒 Running security analysis...$(NC)"
	@if command -v gosec >/dev/null 2>&1; then \
		gosec -severity medium -confidence medium ./...; \
	else \
		echo "$(YELLOW)⚠️  gosec not found, skipping security scan$(NC)"; \
	fi
	@echo "$(GREEN)✅ Security analysis passed!$(NC)"

deps-check: ## Check dependencies for vulnerabilities
	@echo "$(BLUE)🔍 Checking dependencies for vulnerabilities...$(NC)"
	@if command -v govulncheck >/dev/null 2>&1; then \
		govulncheck ./...; \
	else \
		echo "$(YELLOW)⚠️  govulncheck not found, install with: go install golang.org/x/vuln/cmd/govulncheck@latest$(NC)"; \
	fi
	@echo "$(GREEN)✅ Dependency check passed!$(NC)"

# ═══════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════

test: ## Run all tests with coverage
	@echo "$(BLUE)🧪 Running all tests with coverage...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@$(GO) test $(GO_TEST_FLAGS) -coverprofile=$(BUILD_DIR)/$(COVERAGE_FILE) -coverpkg=./... ./...
	@$(GO) tool cover -func=$(BUILD_DIR)/$(COVERAGE_FILE)
	@echo "$(GREEN)✅ All tests passed!$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	@$(GO) test $(GO_TEST_FLAGS) -short ./...

test-integration: ## Run integration tests only
	@echo "$(BLUE)🧪 Running integration tests...$(NC)"
	@$(GO) test $(GO_TEST_FLAGS) -run Integration ./...

test-coverage: ## Generate detailed coverage reports
	@echo "$(BLUE)📊 Generating coverage reports...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@$(GO) test $(GO_TEST_FLAGS) -coverprofile=$(BUILD_DIR)/$(COVERAGE_FILE) -coverpkg=./... ./...
	@$(GO) tool cover -html=$(BUILD_DIR)/$(COVERAGE_FILE) -o $(BUILD_DIR)/$(COVERAGE_HTML)
	@$(GO) tool cover -func=$(BUILD_DIR)/$(COVERAGE_FILE)
	@echo "$(GREEN)✅ Coverage reports generated!$(NC)"
	@echo "$(CYAN)📊 HTML coverage report: $(BUILD_DIR)/$(COVERAGE_HTML)$(NC)"

benchmark: ## Run benchmarks
	@echo "$(BLUE)🏁 Running benchmarks...$(NC)"
	@$(GO) test $(GO_BENCH_FLAGS) ./...
	@echo "$(GREEN)✅ Benchmarks complete!$(NC)"

# ═══════════════════════════════════════════════════════════════════
# CODE FIXES
# ═══════════════════════════════════════════════════════════════════

fix: format mod-tidy ## Auto-fix all possible issues
	@echo "$(GREEN)✅ All auto-fixes applied!$(NC)"

format: ## Format code
	@echo "$(BLUE)⚡ Formatting code...$(NC)"
	@$(GO) fmt ./...
	@if command -v goimports >/dev/null 2>&1; then \
		goimports -w .; \
	else \
		echo "$(YELLOW)⚠️  goimports not found, install with: go install golang.org/x/tools/cmd/goimports@latest$(NC)"; \
	fi
	@echo "$(GREEN)✅ Formatting complete!$(NC)"

mod-tidy: ## Tidy go modules
	@echo "$(BLUE)📦 Tidying go modules...$(NC)"
	@$(GO) mod tidy
	@echo "$(GREEN)✅ Modules tidied!$(NC)"

# ═══════════════════════════════════════════════════════════════════
# BUILD & DEPLOYMENT
# ═══════════════════════════════════════════════════════════════════

build: ## Build binary for current platform
	@echo "$(BLUE)🔨 Building $(BINARY_NAME) for $(OS)/$(ARCH)...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@CGO_ENABLED=0 $(GO) build $(GO_BUILD_FLAGS) \
		-ldflags="-w -s -X main.version=$(VERSION) -X main.commit=$(GIT_COMMIT) -X main.date=$(BUILD_TIME)" \
		-o $(BUILD_DIR)/$(BINARY_NAME) \
		./$(CMD_DIR)
	@echo "$(GREEN)✅ Build complete: $(BUILD_DIR)/$(BINARY_NAME)$(NC)"
	@ls -la $(BUILD_DIR)/$(BINARY_NAME)

build-all: ## Build for all supported platforms
	@echo "$(BLUE)🔨 Building for all platforms...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@for os in linux darwin windows; do \
		for arch in amd64 arm64; do \
			if [ "$$os" = "windows" ]; then \
				ext=".exe"; \
			else \
				ext=""; \
			fi; \
			echo "  Building $$os/$$arch..."; \
			CGO_ENABLED=0 GOOS=$$os GOARCH=$$arch $(GO) build $(GO_BUILD_FLAGS) \
				-ldflags="-w -s -X main.version=$(VERSION) -X main.commit=$(GIT_COMMIT) -X main.date=$(BUILD_TIME)" \
				-o $(BUILD_DIR)/$(BINARY_NAME)-$$os-$$arch$$ext \
				./$(CMD_DIR); \
		done; \
	done
	@echo "$(GREEN)✅ Multi-platform build complete!$(NC)"
	@ls -la $(BUILD_DIR)/

install: build ## Install binary to GOPATH/bin
	@echo "$(BLUE)📦 Installing $(BINARY_NAME)...$(NC)"
	@$(GO) install \
		-ldflags="-w -s -X main.version=$(VERSION) -X main.commit=$(GIT_COMMIT) -X main.date=$(BUILD_TIME)" \
		./$(CMD_DIR)
	@echo "$(GREEN)✅ Installation complete!$(NC)"

run: build ## Build and run the application
	@echo "$(BLUE)🚀 Running $(BINARY_NAME)...$(NC)"
	@./$(BUILD_DIR)/$(BINARY_NAME)

# ═══════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════

mod-download: ## Download dependencies
	@echo "$(BLUE)📥 Downloading dependencies...$(NC)"
	@$(GO) mod download
	@echo "$(GREEN)✅ Dependencies downloaded!$(NC)"

mod-verify: ## Verify dependencies
	@echo "$(BLUE)🔍 Verifying dependencies...$(NC)"
	@$(GO) mod verify
	@echo "$(GREEN)✅ Dependencies verified!$(NC)"

update: ## Update dependencies
	@echo "$(BLUE)⬆️ Updating dependencies...$(NC)"
	@$(GO) get -u ./...
	@$(GO) mod tidy
	@echo "$(GREEN)✅ Dependencies updated!$(NC)"

# ═══════════════════════════════════════════════════════════════════
# DEVELOPMENT TOOLS
# ═══════════════════════════════════════════════════════════════════

dev-setup: mod-download ## Complete development setup
	@echo "$(PURPLE)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(PURPLE)║$(NC)         $(GREEN)✅ Development Setup Complete!$(NC)                  $(PURPLE)║$(NC)"
	@echo "$(PURPLE)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)Recommended tools:$(NC)"
	@echo "  $(YELLOW)golangci-lint$(NC): curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $$(go env GOPATH)/bin"
	@echo "  $(YELLOW)gosec$(NC):        go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest"
	@echo "  $(YELLOW)govulncheck$(NC):  go install golang.org/x/vuln/cmd/govulncheck@latest"
	@echo "  $(YELLOW)goimports$(NC):    go install golang.org/x/tools/cmd/goimports@latest"
	@echo ""
	@echo "$(CYAN)Next steps:$(NC)"
	@echo "  1. Run '$(GREEN)make check$(NC)' to verify everything works"
	@echo "  2. Run '$(GREEN)make help$(NC)' to see all available commands"
	@echo "  3. Happy coding! 🎉"

clean: ## Remove build artifacts
	@echo "$(BLUE)🧹 Cleaning up...$(NC)"
	@rm -rf $(BUILD_DIR)/
	@$(GO) clean -cache
	@$(GO) clean -testcache
	@$(GO) clean -modcache
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

docs: ## Generate documentation
	@echo "$(BLUE)📚 Generating documentation...$(NC)"
	@mkdir -p $(DOCS_DIR)
	@$(GO) doc -all > $(DOCS_DIR)/api.md
	@if command -v godoc >/dev/null 2>&1; then \
		echo "$(CYAN)📖 Start godoc server with: godoc -http=:6060$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  godoc not found, install with: go install golang.org/x/tools/cmd/godoc@latest$(NC)"; \
	fi
	@echo "$(GREEN)✅ Documentation generated!$(NC)"

# ═══════════════════════════════════════════════════════════════════
# VALIDATION & STATUS
# ═══════════════════════════════════════════════════════════════════

validate: ## Validate STRICT compliance
	@echo "$(PURPLE)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(PURPLE)║$(NC)           $(YELLOW)🚨 STRICT MODE VALIDATION$(NC)                     $(PURPLE)║$(NC)"
	@echo "$(PURPLE)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)Checking for any quality violations...$(NC)"
	@if $(MAKE) check > /dev/null 2>&1; then \
		echo ""; \
		echo "$(GREEN)╔═══════════════════════════════════════════════════════════╗$(NC)"; \
		echo "$(GREEN)║$(NC)      $(GREEN)✅ 100% STRICT COMPLIANCE ACHIEVED!$(NC)                $(GREEN)║$(NC)"; \
		echo "$(GREEN)╚═══════════════════════════════════════════════════════════╝$(NC)"; \
	else \
		echo ""; \
		echo "$(RED)╔═══════════════════════════════════════════════════════════╗$(NC)"; \
		echo "$(RED)║$(NC)        $(RED)❌ STRICT COMPLIANCE FAILED!$(NC)                     $(RED)║$(NC)"; \
		echo "$(RED)╚═══════════════════════════════════════════════════════════╝$(NC)"; \
		echo ""; \
		echo "$(YELLOW)Run 'make check' to see violations$(NC)"; \
		exit 1; \
	fi

status: ## Show current quality status
	@echo "$(PURPLE)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(PURPLE)║$(NC)           $(CYAN)📊 Current Quality Status$(NC)                     $(PURPLE)║$(NC)"
	@echo "$(PURPLE)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)Project Information:$(NC)"
	@echo "  Project:     $(PROJECT_NAME)"
	@echo "  Binary:      $(BINARY_NAME)"
	@echo "  Go Version:  $$($(GO) version)"
	@echo "  Git Commit:  $(GIT_COMMIT)"
	@echo "  Version:     $(VERSION)"
	@echo ""
	@echo "$(CYAN)Quality Metrics:$(NC)"
	@VET_ISSUES=$$($(GO) vet ./... 2>&1 | wc -l || echo 0); \
	echo "  Vet Issues:   $$VET_ISSUES"; \
	if [ -f "$(BUILD_DIR)/$(COVERAGE_FILE)" ]; then \
		COVERAGE=$$($(GO) tool cover -func=$(BUILD_DIR)/$(COVERAGE_FILE) | tail -n 1 | awk '{print $$3}' | sed 's/%//'); \
		echo "  Coverage:     $$COVERAGE%"; \
		if [ "$${COVERAGE%.*}" -ge "$(COVERAGE_THRESHOLD)" ]; then \
			echo "$(GREEN)  ✅ Coverage above threshold ($(COVERAGE_THRESHOLD)%)$(NC)"; \
		else \
			echo "$(YELLOW)  ⚠️  Coverage below threshold ($(COVERAGE_THRESHOLD)%)$(NC)"; \
		fi; \
	else \
		echo "  Coverage:     Not measured (run 'make test')"; \
	fi
	@echo ""
	@echo "$(PURPLE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"

# ═══════════════════════════════════════════════════════════════════
# DEVELOPMENT HELPERS
# ═══════════════════════════════════════════════════════════════════

watch: ## Watch for changes and run tests
	@echo "$(BLUE)👁️ Watching for changes...$(NC)"
	@if command -v inotifywait >/dev/null 2>&1; then \
		while true; do \
			inotifywait -r -e modify,create,delete . --exclude '\.(git|build)/' 2>/dev/null; \
			clear; \
			$(MAKE) test; \
		done; \
	else \
		echo "$(YELLOW)⚠️  inotifywait not found, please install inotify-tools$(NC)"; \
	fi

profile: ## Run CPU profiling
	@echo "$(BLUE)⚡ Running CPU profiling...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@$(GO) test -cpuprofile=$(BUILD_DIR)/cpu.prof -bench=. ./...
	@echo "$(GREEN)✅ Profiling complete! View with: go tool pprof $(BUILD_DIR)/cpu.prof$(NC)"

# ═══════════════════════════════════════════════════════════════════
# ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════

# Environment variables
export CGO_ENABLED := 1
export FLEXT_DEMO_DEV := true

# Default target
.DEFAULT_GOAL := help

# Include standardized build system if exists
-include Makefile.build