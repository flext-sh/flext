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
DOCSTRING_MIN ?= 80
COMPLEXITY_MAX ?= 10
CORE_STACK ?= python
PYTEST_ARGS ?=
CHECK_GATES ?=
VALIDATE_GATES ?=
DOCS_PHASE ?= all
AUTO_ADJUST ?= 1

# === WORKSPACE/STANDALONE DETECTION ===
BASE_MK_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
GIT_TOPLEVEL := $(shell git rev-parse --show-toplevel 2>/dev/null)
SUPERPROJECT_ROOT := $(shell git rev-parse --show-superproject-working-tree 2>/dev/null)
PROJECT_ROOT := $(CURDIR)

ifeq ($(FLEXT_STANDALONE),1)
FLEXT_MODE := standalone
else ifneq ($(SUPERPROJECT_ROOT),)
FLEXT_MODE := workspace
else ifneq ($(and $(GIT_TOPLEVEL),$(wildcard $(BASE_MK_DIR)/.gitmodules),$(wildcard $(BASE_MK_DIR)/base.mk)),)
FLEXT_MODE := workspace
else
FLEXT_MODE := standalone
endif

ifeq ($(FLEXT_MODE),workspace)
WORKSPACE_ROOT := $(BASE_MK_DIR)
WORKSPACE_VENV := $(WORKSPACE_ROOT)/.venv
ifeq ($(wildcard $(WORKSPACE_VENV)),)
ACTIVE_VENV := $(PROJECT_ROOT)/.venv
export POETRY_VIRTUALENVS_PATH := $(PROJECT_ROOT)
export POETRY_VIRTUALENVS_IN_PROJECT := true
export POETRY_VIRTUALENVS_CREATE := true
else
ACTIVE_VENV := $(WORKSPACE_VENV)
export POETRY_VIRTUALENVS_PATH := $(WORKSPACE_ROOT)
export POETRY_VIRTUALENVS_IN_PROJECT := false
export POETRY_VIRTUALENVS_CREATE := false
endif
else
WORKSPACE_ROOT := $(PROJECT_ROOT)
ACTIVE_VENV := $(PROJECT_ROOT)/.venv
export POETRY_VIRTUALENVS_PATH := $(PROJECT_ROOT)
export POETRY_VIRTUALENVS_IN_PROJECT := true
export POETRY_VIRTUALENVS_CREATE := true
endif

export PYTHON_KEYRING_BACKEND := keyring.backends.null.Keyring

VENV_PYTHON := $(ACTIVE_VENV)/bin/python
VENV_ACTIVATE := source $(ACTIVE_VENV)/bin/activate
export VIRTUAL_ENV := $(ACTIVE_VENV)
export PATH := $(ACTIVE_VENV)/bin:$(PATH)

# Poetry command (uses workspace venv automatically)
POETRY := poetry

# Quality tool (flext-quality with fallback)
QUALITY_CMD ?= flext-quality
QUALITY_AVAILABLE := $(shell command -v $(QUALITY_CMD) 2>/dev/null)

# Export for subprocesses
export PROJECT_NAME PYTHON_VERSION
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

# === SIMPLE VERB SURFACE ===
.PHONY: help setup check security format docs docs-base docs-sync-scripts test validate clean _preflight
STANDARD_VERBS := setup check security format docs test validate clean
$(STANDARD_VERBS): _preflight

define ENFORCE_WORKSPACE_VENV
if [ "$(FLEXT_MODE)" = "workspace" ]; then \
	if [ -d "$(WORKSPACE_ROOT)/.venv" ]; then \
		if [ -d ".venv" ] && [ "$(CURDIR)" != "$(WORKSPACE_ROOT)" ]; then \
			echo "Enforcing workspace venv: removing local .venv in $(CURDIR)"; \
			rm -rf .venv; \
			if [ -d ".venv" ]; then \
				echo "ERROR: unable to remove local .venv in $(CURDIR)"; \
				exit 1; \
			fi; \
		fi; \
	elif [ "$(CURDIR)" = "$(WORKSPACE_ROOT)" ]; then \
		echo "ERROR: workspace .venv not found at $(ACTIVE_VENV). Run 'make setup' in workspace root."; \
		exit 1; \
	elif [ "$(filter setup,$(MAKECMDGOALS))" != "setup" ] && [ ! -d "$(ACTIVE_VENV)" ]; then \
		echo "ERROR: workspace .venv not found; fallback local .venv missing at $(ACTIVE_VENV). Run 'make setup' in $(PROJECT_NAME)."; \
		exit 1; \
	else \
		echo "INFO: workspace .venv not found; using project-local fallback in $(PROJECT_NAME)."; \
	fi; \
elif [ "$(filter setup,$(MAKECMDGOALS))" != "setup" ] && [ ! -d "$(ACTIVE_VENV)" ]; then \
	echo "ERROR: local .venv not found at $(ACTIVE_VENV). Run 'make setup' in $(PROJECT_NAME)."; \
	exit 1; \
fi
endef

define AUTO_ADJUST_PROJECT
if [ "$(AUTO_ADJUST)" = "1" ]; then \
	md_files=$$(find . -type f -name '*.md' ! -path './.git/*' ! -path './.reports/*' ! -path './reports/*' ! -path './.venv/*' ! -path './node_modules/*' ! -path './.flext-deps/*' ! -path './.mypy_cache/*' ! -path './.pytest_cache/*' ! -path './.ruff_cache/*' ! -path './dist/*' ! -path './build/*'); \
	if [ -n "$$md_files" ] && command -v mdformat >/dev/null 2>&1; then \
		printf '%s\n' "$$md_files" | xargs -r mdformat; \
	fi; \
	if [ -n "$$md_files" ] && command -v markdownlint >/dev/null 2>&1; then \
		md_config=""; \
		if [ -f "$(WORKSPACE_ROOT)/.markdownlint.json" ]; then \
			md_config="--config $(WORKSPACE_ROOT)/.markdownlint.json"; \
		elif [ -f ".markdownlint.json" ]; then \
			md_config="--config .markdownlint.json"; \
		fi; \
		markdownlint --fix $$md_config $$md_files || true; \
	fi; \
	if [ -f go.mod ] && command -v gofmt >/dev/null 2>&1; then \
		go_files=$$(find . -type f -name '*.go' ! -path './.git/*'); \
		if [ -n "$$go_files" ]; then \
			printf '%s\n' "$$go_files" | xargs -r gofmt -w; \
		fi; \
	fi; \
fi
endef

_preflight: ## Internal preflight for standardized verbs
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(AUTO_ADJUST_PROJECT)

help: ## Show commands
	$(Q)echo "$(PROJECT_NAME) - FLEXT Project"
	$(Q)echo ""
	$(Q)echo "Core verbs:"
	$(Q)echo "  setup      Install dependencies and hooks (with automatic md/go adjustment)"
	$(Q)echo "  check      Run the 8 lint gates"
	$(Q)echo "  security   Run all security checks"
	$(Q)echo "  format     Run all formatting (including automatic md/go adjustment)"
	$(Q)echo "  docs       Build docs"
	$(Q)echo "  test       Run pytest only"
	$(Q)echo "  validate   Run validate gates only (use FIX=1 to auto-fix first)"
	$(Q)echo "  clean      Clean build/test/type artifacts"

setup: ## Complete setup
	$(Q)if [ "$(CORE_STACK)" = "go" ]; then \
		go mod download; \
		go mod tidy; \
		exit 0; \
	fi
	$(Q)if [ -f "$(WORKSPACE_ROOT)/scripts/dependencies/sync_internal_deps.py" ]; then \
		python3 "$(WORKSPACE_ROOT)/scripts/dependencies/sync_internal_deps.py" --project-root "$(CURDIR)"; \
	fi
	$(Q)$(POETRY) lock
	$(Q)$(POETRY) install --all-extras --all-groups
	$(Q)$(POETRY) run pre-commit install

check: ## Run lint gates (CHECK_GATES=lint,format,pyrefly,mypy,pyright,security,markdown,go,type to select)
	$(Q)if [ "$(CORE_STACK)" = "go" ]; then \
		gates="$(CHECK_GATES)"; \
		if [ -n "$$gates" ]; then \
			for g in $$(echo "$$gates" | tr ',' ' '); do \
				case "$$g" in \
					lint|format|security|markdown|go|type) ;; \
					*) echo "ERROR: unknown CHECK_GATES value '$$g' (allowed: lint,format,security,markdown,go,type)"; exit 2;; \
				esac; \
			done; \
		else \
			gates="lint,format,security,markdown,go"; \
		fi; \
		gates=$$(echo "$$gates" | tr ',' ' ' | sed 's/\btype\b/go/g' | tr ' ' ','); \
		if echo "$$gates" | grep -qw lint; then \
			golangci-lint run || { echo "FAIL: lint"; exit 1; }; \
		fi; \
		if echo "$$gates" | grep -qw format; then \
			if [ -n "$$(find . -type f -name '*.go' ! -path './.git/*')" ]; then \
				gofmt_diff=$$(find . -type f -name '*.go' ! -path './.git/*' -print0 | xargs -0 gofmt -l); \
				if [ -n "$$gofmt_diff" ]; then \
					echo "FAIL: gofmt"; \
					printf '%s\n' "$$gofmt_diff"; \
					exit 1; \
				fi; \
			fi; \
		fi; \
		if echo "$$gates" | grep -qw security; then \
			gosec ./... || { echo "FAIL: security"; exit 1; }; \
		fi; \
		if echo "$$gates" | grep -qw markdown; then \
			md_files=$$(find . -type f -name '*.md' ! -path './.git/*' ! -path './.reports/*' ! -path './reports/*' ! -path './.venv/*' ! -path './node_modules/*' ! -path './.flext-deps/*' ! -path './.mypy_cache/*' ! -path './.pytest_cache/*' ! -path './.ruff_cache/*' ! -path './dist/*' ! -path './build/*'); \
			md_config=""; \
			if [ -f "$(WORKSPACE_ROOT)/.markdownlint.json" ]; then \
				md_config="--config $(WORKSPACE_ROOT)/.markdownlint.json"; \
			elif [ -f ".markdownlint.json" ]; then \
				md_config="--config .markdownlint.json"; \
			fi; \
			if [ -n "$$md_files" ]; then markdownlint $$md_config $$md_files || { echo "FAIL: markdown"; exit 1; }; fi; \
		fi; \
		if echo "$$gates" | grep -qw go; then \
			go vet ./... || { echo "FAIL: go"; exit 1; }; \
		fi; \
		exit 0; \
	fi
	$(Q)gates="$(CHECK_GATES)"; \
	if [ -n "$$gates" ]; then \
		for g in $$(echo "$$gates" | tr ',' ' '); do \
			case "$$g" in \
				lint|format|pyrefly|mypy|pyright|security|markdown|go|type) ;; \
				*) echo "ERROR: unknown CHECK_GATES value '$$g' (allowed: lint,format,pyrefly,mypy,pyright,security,markdown,go,type)"; exit 2;; \
			esac; \
		done; \
	else \
		gates="lint,format,pyrefly,mypy,pyright,security,markdown,go"; \
	fi; \
	gates=$$(echo "$$gates" | tr ',' ' ' | sed 's/\btype\b/pyrefly/g' | tr ' ' ','); \
	if [ -f "$(WORKSPACE_ROOT)/scripts/check/workspace_check.py" ]; then \
		project_key="$(PROJECT_NAME)"; \
		if [ "$(CURDIR)" = "$(WORKSPACE_ROOT)" ]; then \
			project_key="."; \
		fi; \
		if [ -f "$(WORKSPACE_ROOT)/scripts/check/fix_pyrefly_config.py" ]; then \
			$(POETRY) run python "$(WORKSPACE_ROOT)/scripts/check/fix_pyrefly_config.py" "$$project_key"; \
		fi; \
		$(POETRY) run python "$(WORKSPACE_ROOT)/scripts/check/workspace_check.py" --gates "$$gates" --reports-dir "$(CURDIR)/.reports/check" "$$project_key"; \
		exit $$?; \
	fi; \
	if echo "$$gates" | grep -qw lint; then \
		$(POETRY) run ruff check . --quiet || { echo "FAIL: lint"; exit 1; }; \
	fi; \
	if echo "$$gates" | grep -qw format; then \
		$(POETRY) run ruff format --check . --quiet || { echo "FAIL: format"; exit 1; }; \
	fi; \
	if echo "$$gates" | grep -qw pyrefly; then \
		$(POETRY) run pyrefly check $(SRC_DIR) --config pyproject.toml \
			--count-errors=0 --summarize-errors=1 --summary full || { echo "FAIL: pyrefly"; exit 1; }; \
	fi; \
	if echo "$$gates" | grep -qw mypy; then \
		$(POETRY) run mypy $(SRC_DIR) || { echo "FAIL: mypy"; exit 1; }; \
	fi; \
	if echo "$$gates" | grep -qw pyright; then \
		$(POETRY) run pyright $(SRC_DIR) || { echo "FAIL: pyright"; exit 1; }; \
	fi; \
	if echo "$$gates" | grep -qw security; then \
		$(POETRY) run bandit -r $(SRC_DIR) -q -ll || { echo "FAIL: security"; exit 1; }; \
	fi; \
	if echo "$$gates" | grep -qw markdown; then \
		md_files=$$(find . -type f -name '*.md' ! -path './.git/*' ! -path './.reports/*' ! -path './reports/*' ! -path './.venv/*' ! -path './node_modules/*' ! -path './.flext-deps/*' ! -path './.mypy_cache/*' ! -path './.pytest_cache/*' ! -path './.ruff_cache/*' ! -path './dist/*' ! -path './build/*'); \
		md_config=""; \
		if [ -f "$(WORKSPACE_ROOT)/.markdownlint.json" ]; then \
			md_config="--config $(WORKSPACE_ROOT)/.markdownlint.json"; \
		elif [ -f ".markdownlint.json" ]; then \
			md_config="--config .markdownlint.json"; \
		fi; \
		if [ -n "$$md_files" ]; then \
			markdownlint $$md_config $$md_files || { echo "FAIL: markdown"; exit 1; }; \
		fi; \
	fi; \
	if echo "$$gates" | grep -qw go; then \
		if [ -f go.mod ]; then \
			go vet ./... || { echo "FAIL: go"; exit 1; }; \
			if [ -n "$$(find . -type f -name '*.go' ! -path './.git/*')" ]; then \
				gofmt_diff=$$(find . -type f -name '*.go' ! -path './.git/*' -print0 | xargs -0 gofmt -l); \
				if [ -n "$$gofmt_diff" ]; then \
					echo "FAIL: gofmt"; \
					printf '%s\n' "$$gofmt_diff"; \
					exit 1; \
				fi; \
			fi; \
		fi; \
	fi

security: ## Run all security checks
	$(Q)if [ "$(CORE_STACK)" = "go" ]; then \
		gosec ./...; \
		exit 0; \
	fi
	$(Q)$(POETRY) run bandit -r $(SRC_DIR) -q -ll

format: ## Run all formatting
	$(Q)if [ "$(CORE_STACK)" = "go" ]; then \
		if [ -n "$$(find . -type f -name '*.go' ! -path './.git/*')" ]; then \
			find . -type f -name '*.go' ! -path './.git/*' -print0 | xargs -0 gofmt -w; \
			if command -v goimports >/dev/null 2>&1; then \
				find . -type f -name '*.go' ! -path './.git/*' -print0 | xargs -0 goimports -w; \
			fi; \
		fi; \
	fi
	$(Q)if [ "$(CORE_STACK)" != "go" ]; then $(POETRY) run ruff format . --quiet; fi
	$(Q)md_files=$$(find . -type f -name '*.md' ! -path './.git/*' ! -path './.reports/*' ! -path './reports/*' ! -path './.venv/*' ! -path './node_modules/*' ! -path './.flext-deps/*' ! -path './.mypy_cache/*' ! -path './.pytest_cache/*' ! -path './.ruff_cache/*' ! -path './dist/*' ! -path './build/*'); \
	md_config=""; \
	if [ -f "$(WORKSPACE_ROOT)/.markdownlint.json" ]; then \
		md_config="--config $(WORKSPACE_ROOT)/.markdownlint.json"; \
	elif [ -f ".markdownlint.json" ]; then \
		md_config="--config .markdownlint.json"; \
	fi; \
	if [ -n "$$md_files" ]; then \
		printf '%s\n' "$$md_files" | xargs -r mdformat; \
		markdownlint --fix $$md_config $$md_files || true; \
	fi
	$(Q)if [ -f go.mod ] && [ -n "$$(find . -type f -name '*.go' ! -path './.git/*')" ]; then \
		find . -type f -name '*.go' ! -path './.git/*' -print0 | xargs -0 gofmt -w; \
	fi

docs: ## Build docs
	$(Q)src="$(WORKSPACE_ROOT)/scripts/documentation"; \
	dst="$(CURDIR)/scripts/documentation"; \
	if [ "$(FLEXT_MODE)" = "workspace" ] && [ -d "$$src" ] && [ "$(CURDIR)" != "$(WORKSPACE_ROOT)" ]; then \
		mkdir -p "$$(dirname "$$dst")"; \
		rm -rf "$$dst"; \
		cp -a "$$src" "$$dst"; \
		echo "PROJECT=$(PROJECT_NAME) PHASE=sync RESULT=OK REASON=workspace-docs-scripts-synced"; \
	elif [ -d "$$dst" ]; then \
		echo "PROJECT=$(PROJECT_NAME) PHASE=sync RESULT=OK REASON=local-docs-scripts-present"; \
	else \
		echo "PROJECT=$(PROJECT_NAME) PHASE=sync RESULT=FAIL REASON=docs-scripts-missing"; \
		exit 1; \
	fi
	$(Q)if [ "$(DOCS_PHASE)" = "all" ]; then \
		phases="generate fix audit build validate"; \
		all_mode=1; \
	else \
		phases="$(DOCS_PHASE)"; \
		all_mode=0; \
	fi; \
	for phase in $$phases; do \
		case "$$phase" in \
			audit) script="scripts/documentation/audit.py"; extra="--strict 1" ;; \
			fix) script="scripts/documentation/fix.py"; extra="$(if $(filter 1,$(FIX)),--apply,)" ;; \
			build) script="scripts/documentation/build.py"; extra="" ;; \
			generate) script="scripts/documentation/generate.py"; extra="--apply" ;; \
			validate) script="scripts/documentation/validate.py"; extra="$(if $(filter 1,$(FIX)),--apply,)" ;; \
			*) echo "ERROR: invalid DOCS_PHASE=$$phase"; exit 2 ;; \
		esac; \
		if [ "$$phase" = "fix" ] && [ "$$all_mode" = "1" ]; then extra="--apply"; fi; \
		if [ ! -f "$$script" ]; then \
			echo "PROJECT=$(PROJECT_NAME) PHASE=$$phase RESULT=FAIL REASON=missing-script:$$script"; \
			exit 1; \
		fi; \
		cmd="python $$script --root . --output-dir .reports/docs"; \
		if [ -n "$$extra" ]; then cmd="$$cmd $$extra"; fi; \
		eval $$cmd || exit $$?; \
	done

test: ## Run pytest only
	$(Q)if [ "$(CORE_STACK)" = "go" ]; then \
		go test -v -race -coverprofile=coverage.out -covermode=atomic ./...; \
		go tool cover -func=coverage.out; \
		exit 0; \
	fi
	$(Q)$(POETRY) run pytest $(TESTS_DIR) \
		-p no:metadata \
		--cov --cov-report=term-missing:skip-covered \
		-q $(PYTEST_ARGS)

validate: ## Run validate gates (VALIDATE_GATES=complexity,docstring to select, FIX=1)
	$(Q)if [ "$(CORE_STACK)" = "go" ]; then \
		if [ "$(FIX)" = "1" ]; then \
			$(MAKE) format; \
		fi; \
		go mod verify; \
		exit 0; \
	fi
	$(Q)if [ -n "$(FIX)" ] && [ "$(FIX)" != "1" ]; then \
		echo "ERROR: FIX must be empty or 1, got '$(FIX)'"; \
		exit 1; \
	fi
	$(Q)if [ "$(FIX)" = "1" ]; then $(POETRY) run ruff check --fix . --quiet; fi
	$(Q)gates="$(VALIDATE_GATES)"; \
	if [ -n "$$gates" ]; then \
		for g in $$(echo "$$gates" | tr ',' ' '); do \
			case "$$g" in \
				complexity|docstring) ;; \
				*) echo "ERROR: unknown VALIDATE_GATES value '$$g' (allowed: complexity,docstring)"; exit 2;; \
			esac; \
		done; \
	else \
		gates="complexity,docstring"; \
	fi; \
	if echo "$$gates" | grep -qw complexity; then \
		$(POETRY) run radon cc $(SRC_DIR) -n E -a --total-average; \
		$(POETRY) run radon mi $(SRC_DIR) -n C -s --sort; \
	fi; \
	if echo "$$gates" | grep -qw docstring; then \
		$(POETRY) run interrogate $(SRC_DIR) --fail-under=$(DOCSTRING_MIN) --ignore-init-method --ignore-magic -q; \
	fi

clean: ## Clean artifacts
	$(Q)if [ "$(CORE_STACK)" = "go" ]; then \
		rm -f coverage.out coverage.html; \
		go clean; \
	fi
	$(Q)rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage* \
		.mypy_cache/ .pyrefly_cache/ .ruff_cache/ $(LINT_CACHE_DIR)/ \
		.pyright/ .pytype/ .pyrefly-report.json .pyrefly-output.txt
	$(Q)find . -type d -name __pycache__ -exec rm -rf {} +
	$(Q)find . -type f -name "*.pyc" -delete
