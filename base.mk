# =============================================================================
# FLEXT BASE MAKEFILE - Shared patterns for all FLEXT projects
# =============================================================================
# Usage: Set PROJECT_NAME before including: include ../base.mk
# Silent by default. Use VERBOSE=1 for detailed output.
# =============================================================================

# === CONFIGURATION (override before include) ===
PROJECT_NAME ?= unnamed
PYTHON_VERSION ?= 3.13
POETRY ?= poetry
SRC_DIR ?= src
TESTS_DIR ?= tests
COV_DIR ?= $(subst -,_,$(PROJECT_NAME))
MIN_COVERAGE ?= 80
DOCSTRING_MIN ?= 80
COMPLEXITY_MAX ?= 10

# Export for subprocesses
export PROJECT_NAME PYTHON_VERSION MIN_COVERAGE

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

# === PHONY DECLARATIONS ===
.PHONY: help install install-dev setup lint format fix type-check test test-fast upgrade
.PHONY: test-unit test-integration security validate check clean clean-all reset
.PHONY: build shell deps complexity docstring-check coverage-html
.PHONY: dead-code modernize cognitive-complexity validate-full
.PHONY: t l f tc c v s dp cx dc vf

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
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pyrefly check $(SRC_DIR) --config pyproject.toml 2>/dev/null || { echo "FAIL: types"; exit 1; }

# === CODE QUALITY ===
complexity: ## Code complexity analysis (Radon CC + MI)
	$(Q)$(POETRY) run radon cc $(SRC_DIR) -a -nb --total-average 2>/dev/null || echo "WARN: radon not installed"
	$(Q)$(POETRY) run radon mi $(SRC_DIR) -nb 2>/dev/null || true

docstring-check: ## Docstring coverage check
	$(Q)$(POETRY) run interrogate $(SRC_DIR) --fail-under=$(DOCSTRING_MIN) --ignore-init-method --ignore-magic -q 2>/dev/null || { echo "WARN: interrogate not installed or coverage below $(DOCSTRING_MIN)%"; exit 0; }

# === TEST ===
test: ## Run tests with coverage
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR) \
		--cov=$(COV_DIR) --cov-report=term-missing:skip-covered \
		--cov-fail-under=$(MIN_COVERAGE) -q

test-fast: ## Run tests (no coverage)
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR) -q --tb=short

test-verbose: ## Run tests with output
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR) -v

test-unit: ## Unit tests only
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR) -m "not integration" -q

test-integration: ## Integration tests
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR) -m integration -q

coverage-html: ## Generate HTML coverage report
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest --cov=$(COV_DIR) --cov-report=html -q

# === BUILD ===
build: ## Build package
	$(Q)$(POETRY) build

shell: ## Python shell
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run python

# === SECURITY (FAIL on issues) ===
security: ## Security checks (Bandit)
	$(Q)$(POETRY) run bandit -r $(SRC_DIR) -q -ll 2>/dev/null || { echo "WARN: bandit found issues or not installed"; exit 0; }

# === DEAD CODE & MODERNIZATION ===
dead-code: ## Dead code detection (Vulture)
	$(Q)$(POETRY) run vulture $(SRC_DIR) --min-confidence 80 --exclude "tests,examples" || true

modernize: ## Modern patterns suggestions (Refurb)
	$(Q)$(POETRY) run refurb $(SRC_DIR) --enable-all --quiet || true

cognitive-complexity: ## Cognitive complexity (Complexipy)
	$(Q)$(POETRY) run complexipy $(SRC_DIR) --max-complexity 15 || true

# === QUALITY GATES ===
validate: lint format-check type-check complexity docstring-check security test ## Full validation

validate-full: lint format-check type-check dead-code cognitive-complexity security test ## Full + dead code

check: lint type-check ## Quick check

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

# === SHORT ALIASES ===
t: test
l: lint
f: format
tc: type-check
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
