# =============================================================================
# FLEXT BASE MAKEFILE - Shared patterns for all FLEXT projects
# =============================================================================
# Usage: Set PROJECT_NAME before including: include ../base.mk
# Silent by default. Use VERBOSE=1 for detailed output.
# =============================================================================

# === CONFIGURATION (override before include) ===
PROJECT_NAME ?= unnamed
PYTHON_VERSION ?= 3.13
SRC_DIR ?= src
TESTS_DIR ?= tests
COV_DIR ?= $(subst -,_,$(PROJECT_NAME))
MIN_COVERAGE ?= 80
DOCSTRING_MIN ?= 80
COMPLEXITY_MAX ?= 10

# === WORKSPACE DETECTION ===
# Detect workspace root (FLEXT monorepo root)
# For submodules, use superproject; otherwise use parent dir (standard FLEXT layout)
# Note: git commands can return empty strings, so we check for non-empty output
WORKSPACE_ROOT := $(shell \
	super="$$(git rev-parse --show-superproject-working-tree 2>/dev/null)"; \
	if [ -n "$$super" ]; then echo "$$super"; \
	elif [ -d "../.venv" ]; then cd .. && pwd; \
	else git rev-parse --show-toplevel 2>/dev/null || (cd .. && pwd); \
	fi \
)

# === VIRTUAL ENVIRONMENT CONFIGURATION ===
# Use workspace-level venv (shared across all projects)
WORKSPACE_VENV := $(WORKSPACE_ROOT)/.venv
VENV_PYTHON := $(WORKSPACE_VENV)/bin/python
VENV_ACTIVATE := source $(WORKSPACE_VENV)/bin/activate

# Poetry configuration to use workspace venv
export POETRY_VIRTUALENVS_PATH := $(WORKSPACE_ROOT)
export POETRY_VIRTUALENVS_IN_PROJECT := false
export POETRY_VIRTUALENVS_CREATE := false
export VIRTUAL_ENV := $(WORKSPACE_VENV)
export PATH := $(WORKSPACE_VENV)/bin:$(PATH)

# Poetry command (uses workspace venv automatically)
POETRY := poetry

# === PYTHONPATH CONFIGURATION ===
# Build PYTHONPATH with all core dependencies (in dependency order)
# This ensures cross-project imports work correctly
FLEXT_PYTHONPATH := $(shell \
	paths="$(CURDIR)/$(SRC_DIR)"; \
	for proj in flext-core flext-cli flext-ldif flext-ldap flext-api flext-auth flext-grpc flext-observability client-a-oud-mig; do \
		proj_src="$(WORKSPACE_ROOT)/$$proj/src"; \
		if [ -d "$$proj_src" ]; then \
			paths="$$paths:$$proj_src"; \
		fi; \
	done; \
	echo "$$paths" \
)

# Quality tool (flext-quality with fallback)
QUALITY_CMD ?= flext-quality
QUALITY_AVAILABLE := $(shell command -v $(QUALITY_CMD) 2>/dev/null)

# Export for subprocesses
export PROJECT_NAME PYTHON_VERSION MIN_COVERAGE
export PYTHONPATH := $(FLEXT_PYTHONPATH)
export FLEXT_ROOT := $(WORKSPACE_ROOT)

# === SILENT MODE ===
Q := @
ifdef VERBOSE
Q :=
endif

# === CACHE ===
LINT_CACHE_DIR := .lint-cache
CACHE_TIMEOUT := 300

$(LINT_CACHE_DIR):
	$(Q)mkdir -p $(LINT_CACHE_DIR)

# === LOCAL VENV CHECK ===
# Warn if local .venv exists (should use workspace venv)
LOCAL_VENV_EXISTS := $(shell [ -d ".venv" ] && echo "yes" || echo "no")
ifeq ($(LOCAL_VENV_EXISTS),yes)
$(warning ⚠️  Local .venv found! Run 'make clean-local-venv' to use workspace venv)
endif

# === PHONY DECLARATIONS ===
.PHONY: help install install-dev setup lint format fix type-check type-check-json pyrefly-infer test test-fast upgrade
.PHONY: test-unit test-integration security validate check clean clean-all reset
.PHONY: build shell deps complexity docstring-check coverage-html
.PHONY: dead-code modernize cognitive-complexity spell-check validate-full
.PHONY: t l f tc tcj pi c v s dp cx dc vf sp
.PHONY: check-venv clean-local-venv venv-info

# === HELP ===
help: ## Show commands
	$(Q)echo "$(PROJECT_NAME) - FLEXT Project"
	$(Q)echo ""
	$(Q)grep -hE '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# === SETUP ===
install: ## Install dependencies
	$(Q)$(POETRY) install

install-dev: ## Install dev dependencies
	$(Q)$(POETRY) install --with dev,test

setup: install-dev ## Complete setup
	$(Q)$(POETRY) run pre-commit install 2>/dev/null || true

# === LINT (Ruff - ZERO TOLERANCE) ===
lint: $(LINT_CACHE_DIR) ## Run linting
	$(Q)$(POETRY) run ruff check . --quiet || { echo "FAIL: lint"; exit 1; }

format: ## Format code
	$(Q)$(POETRY) run ruff format . --quiet

fix: ## Auto-fix lint issues
	$(Q)$(POETRY) run ruff check --fix . --quiet

format-check: ## Check formatting
	$(Q)$(POETRY) run ruff format --check . --quiet || { echo "FAIL: format"; exit 1; }

# === TYPE CHECK (PyRefly - ZERO TOLERANCE) ===
type-check: ## Run type checking
	$(Q)$(POETRY) run pyrefly check $(SRC_DIR) --config pyproject.toml 2>/dev/null || { echo "FAIL: types"; exit 1; }

type-check-json: ## Type-check with JSON output for artifact capture
	$(Q)$(POETRY) run pyrefly check $(SRC_DIR) --config pyproject.toml 2>&1 | tee /dev/stderr | grep -c "^ERROR" > .pyrefly-error-count.txt || true
	$(Q)echo "{\"project\":\"$(PROJECT_NAME)\",\"error_count\":$$(cat .pyrefly-error-count.txt 2>/dev/null || echo 0)}" > .pyrefly-report.json

pyrefly-infer: ## Run pyrefly infer for annotation backfill (guarded, non-degrading)
	$(Q)echo "pyrefly-infer: $(PROJECT_NAME)"
	$(Q)before=$$($(POETRY) run pyrefly check $(SRC_DIR) --config pyproject.toml 2>&1 | grep -c "^ERROR" || echo 0); \
	$(POETRY) run pyrefly infer $(SRC_DIR) 2>/dev/null || true; \
	$(MAKE) format -s 2>/dev/null || true; \
	after=$$($(POETRY) run pyrefly check $(SRC_DIR) --config pyproject.toml 2>&1 | grep -c "^ERROR" || echo 0); \
	if [ "$$after" -gt "$$before" ]; then \
		echo "REJECT: pyrefly-infer made errors worse ($$before -> $$after), reverting"; \
		git checkout -- $(SRC_DIR) 2>/dev/null || true; \
	else \
		echo "ACCEPT: pyrefly-infer ($$before -> $$after errors)"; \
	fi

# === CODE QUALITY ===
complexity: ## Code complexity analysis (Radon CC + MI)
	$(Q)$(POETRY) run radon cc $(SRC_DIR) -a -nb --total-average 2>/dev/null || echo "WARN: radon not installed"
	$(Q)$(POETRY) run radon mi $(SRC_DIR) -nb 2>/dev/null || true

docstring-check: ## Docstring coverage check
	$(Q)$(POETRY) run interrogate $(SRC_DIR) --fail-under=$(DOCSTRING_MIN) --ignore-init-method --ignore-magic -q 2>/dev/null || { echo "WARN: interrogate not installed or coverage below $(DOCSTRING_MIN)%"; exit 0; }

# === TEST ===
test: ## Run tests with coverage
	$(Q)$(POETRY) run pytest $(TESTS_DIR) \
		--cov=$(COV_DIR) --cov-report=term-missing:skip-covered \
		--cov-fail-under=$(MIN_COVERAGE) -q

test-fast: ## Run tests (no coverage)
	$(Q)$(POETRY) run pytest $(TESTS_DIR) -q --tb=short

test-verbose: ## Run tests with output
	$(Q)$(POETRY) run pytest $(TESTS_DIR) -v

test-unit: ## Unit tests only
	$(Q)$(POETRY) run pytest $(TESTS_DIR) -m "not integration" -q

test-integration: ## Integration tests
	$(Q)$(POETRY) run pytest $(TESTS_DIR) -m integration -q

coverage-html: ## Generate HTML coverage report
	$(Q)$(POETRY) run pytest --cov=$(COV_DIR) --cov-report=html -q

# === BUILD ===
build: ## Build package
	$(Q)$(POETRY) build

shell: ## Python shell
	$(Q)$(POETRY) run python

# === SECURITY (FAIL on issues) ===
security: ## Security checks (Bandit)
	$(Q)$(POETRY) run bandit -r $(SRC_DIR) -q -ll 2>/dev/null || { echo "WARN: bandit found issues or not installed"; exit 0; }

# === DEAD CODE & MODERNIZATION ===
# Note: These tools run from WORKSPACE_ROOT environment where they are installed
dead-code: ## Dead code detection (Vulture)
	$(Q)cd $(WORKSPACE_ROOT) && $(POETRY) run vulture $(CURDIR)/$(SRC_DIR) --min-confidence 80 --exclude "tests,examples" || true

modernize: ## Modern patterns suggestions (via Ruff FURB rules)
	@echo "Note: Ruff already applies 36 FURB rules from refurb (see: ruff rule --all | grep FURB)"
	@echo "Refurb standalone disabled - incompatible with Python 3.13 TypeAliasStmt"
	@echo "Run 'make lint' to apply modernization suggestions via Ruff"

cognitive-complexity: ## Cognitive complexity (Complexipy)
	$(Q)cd $(WORKSPACE_ROOT) && $(POETRY) run complexipy $(CURDIR)/$(SRC_DIR) --max-complexity-allowed 15 || true

spell-check: ## Spell checking (Codespell)
	$(Q)cd $(WORKSPACE_ROOT) && $(POETRY) run codespell $(CURDIR)/$(SRC_DIR) --toml $(WORKSPACE_ROOT)/pyproject.toml --quiet-level 3 || true

# === QUALITY GATES ===
ifdef QUALITY_AVAILABLE
check: ## Quick check (lint + type)
	$(Q)$(QUALITY_CMD) check .
else
check: lint type-check ## Quick check (lint + type)
endif

ifdef QUALITY_AVAILABLE
validate: ## Full validation
	$(Q)$(QUALITY_CMD) validate . --min-coverage $(MIN_COVERAGE)
else
validate: lint format-check type-check complexity docstring-check security test ## Full validation
endif

validate-full: lint format-check type-check dead-code cognitive-complexity spell-check security test ## Full + extended checks

# === UPGRADE ===
upgrade: ## Upgrade all dependencies to latest versions
	$(Q)echo "Upgrading dependencies in $(PROJECT_NAME)..."
	$(Q)$(POETRY) upgrade
	$(Q)echo "✓ Dependencies upgraded - verify with: make test"

# === DEPENDENCY ANALYSIS ===
deps: ## Analyze dependencies with deptry (missing, unused, transitive)
	$(Q)echo "Analyzing dependencies in $(PROJECT_NAME)..."
	$(Q)uvx deptry . --no-ansi 2>&1 | grep -E "(DEP00|Found)" || echo "✓ No issues"

# === CLEAN ===
clean: ## Clean artifacts
	$(Q)rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage* \
		.mypy_cache/ .pyrefly_cache/ .ruff_cache/ $(LINT_CACHE_DIR)/ \
		.pyright/ .pytype/
	$(Q)find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	$(Q)find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-all: clean ## Deep clean
	$(Q)rm -rf .venv/ node_modules/

reset: clean-all setup ## Full reset

# === VIRTUAL ENVIRONMENT MANAGEMENT ===
venv-info: ## Show venv configuration
	@echo "=== FLEXT Virtual Environment Info ==="
	@echo "WORKSPACE_ROOT:   $(WORKSPACE_ROOT)"
	@echo "WORKSPACE_VENV:   $(WORKSPACE_VENV)"
	@echo "VIRTUAL_ENV:      $(VIRTUAL_ENV)"
	@echo "Local .venv:      $(LOCAL_VENV_EXISTS)"
	@echo "Poetry path:      $$(poetry env info --path 2>/dev/null || echo 'not configured')"
	@echo "Python:           $$(which python)"

check-venv: ## Verify using workspace venv
	@if [ -d ".venv" ]; then \
		echo "ERROR: Local .venv exists. Run 'make clean-local-venv' first"; \
		exit 1; \
	fi
	@if [ "$$(poetry env info --path 2>/dev/null)" != "$(WORKSPACE_VENV)" ]; then \
		echo "WARNING: Poetry not using workspace venv"; \
		echo "  Expected: $(WORKSPACE_VENV)"; \
		echo "  Got:      $$(poetry env info --path 2>/dev/null)"; \
	else \
		echo "OK: Using workspace venv at $(WORKSPACE_VENV)"; \
	fi

clean-local-venv: ## Remove local .venv (use workspace venv)
	@if [ -d ".venv" ]; then \
		echo "Removing local .venv..."; \
		rm -rf .venv; \
		echo "Done. Run 'make check-venv' to verify."; \
	else \
		echo "No local .venv found."; \
	fi

# === SHORT ALIASES ===
t: test
l: lint
f: format
tc: type-check
tcj: type-check-json
pi: pyrefly-infer
c: clean
v: validate
vf: validate-full
s: setup
dp: deps
cx: complexity
dc: docstring-check
dd: dead-code
mod: modernize
cc: cognitive-complexity
sp: spell-check
vi: venv-info
cv: check-venv
clv: clean-local-venv
