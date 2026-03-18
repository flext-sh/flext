# =============================================================================
# FLEXT Workspace Makefile - Simple Verbs Only
# =============================================================================

SHELL := /usr/bin/bash
.DEFAULT_GOAL := help

WORKSPACE_VENV := $(CURDIR)/.venv

# Determine required python version from pyproject.toml and find matching executable
PYTHON_REQ_VERSION := $(shell awk -F'"' '/requires-python/ {match($$2, /3\.[0-9]+/); print substr($$2, RSTART, RLENGTH)}' pyproject.toml)
PYTHON_CMD := $(shell if command -v python$(PYTHON_REQ_VERSION) >/dev/null 2>&1; then echo python$(PYTHON_REQ_VERSION); elif command -v python3 >/dev/null 2>&1; then echo python3; else echo python; fi)

PY := $(WORKSPACE_VENV)/bin/python
POETRY_BIN := $(WORKSPACE_VENV)/bin/poetry
PIPX_BIN := $(WORKSPACE_VENV)/bin/pipx
UV_BIN := $(WORKSPACE_VENV)/bin/uv
POETRY_ENV := VIRTUAL_ENV=$(WORKSPACE_VENV) PATH=$(WORKSPACE_VENV)/bin:$$PATH POETRY_VIRTUALENVS_CREATE=false POETRY_VIRTUALENVS_IN_PROJECT=false
ORCHESTRATOR := $(POETRY_ENV) $(PY) -m flext_infra workspace orchestrate
PYTEST_ARGS ?=
VALIDATE_SCOPE ?= project
DOCS_PHASE ?= all
FAIL_FAST ?=
JOBS ?=
CHECK_GATES ?=
VALIDATE_GATES ?=
RELEASE_PHASE ?= all
INTERACTIVE ?= 1
DRY_RUN ?=
PUSH ?=
VERSION ?=
MESSAGE ?=
TAG ?=
BUMP ?=
RELEASE_DEV_SUFFIX ?= 0
RELEASE_NEXT_DEV ?= 0
RELEASE_NEXT_BUMP ?= minor
CREATE_BRANCHES ?= 1
PR_ACTION ?= status
PR_BASE ?= main
PR_HEAD ?=
PR_NUMBER ?=
PR_TITLE ?=
PR_BODY ?=
PR_DRAFT ?= 0
PR_MERGE_METHOD ?= squash
PR_AUTO ?= 0
PR_DELETE_BRANCH ?= 0
PR_CHECKS_STRICT ?= 0
PR_RELEASE_ON_MERGE ?= 1
PR_INCLUDE_ROOT ?= 1
PR_BRANCH ?= 0.11.0-dev
PR_CHECKPOINT ?= 1

Q := @
ifdef VERBOSE
Q :=
endif

# Project discovery: parse .gitmodules directly - no Python needed, works before venv exists.
# submodule paths: listed in .gitmodules path = <dir>
# external projects: git repos with Makefile+pyproject.toml that are NOT in .gitmodules
FLEXT_PROJECTS := $(shell \
	if [ -f .gitmodules ]; then \
		git config --file .gitmodules --get-regexp '\.path$$' 2>/dev/null \
			| awk '{print $$2}' | tr '\n' ' '; \
	fi)
EXTERNAL_PROJECTS := $(shell \
	submods=$$(git config --file .gitmodules --get-regexp '\.path$$' 2>/dev/null | awk '{print $$2}' | tr '\n' ' '); \
	for d in */; do d="$${d%/}"; \
		if [ -d "$$d/.git" ] && [ -f "$$d/Makefile" ] && [ -f "$$d/pyproject.toml" ]; then \
			if ! echo " $$submods " | grep -qF " $$d "; then \
				printf '%s ' "$$d"; \
			fi; \
		fi; \
	done)

ALL_PROJECTS := $(FLEXT_PROJECTS) $(EXTERNAL_PROJECTS)
SELECTED_PROJECTS := $(strip $(if $(PROJECT),$(PROJECT),$(if $(PROJECTS),$(PROJECTS),$(ALL_PROJECTS))))

define ENSURE_NO_PROJECT_CONFLICT
if [ -n "$(PROJECT)" ] && [ -n "$(PROJECTS)" ]; then \
	echo "ERROR: Cannot use PROJECT and PROJECTS together"; \
	echo "Use PROJECT=<name> or PROJECTS=\"proj-a proj-b\""; \
	exit 1; \
fi
endef

define VALIDATE_FIX_PARAM
if [ -n "$(FIX)" ] && [ "$(FIX)" != "1" ]; then \
	echo "ERROR: FIX must be empty or 1, got '$(FIX)'"; \
	exit 1; \
fi
endef

define ENSURE_SELECTED_PROJECTS
if [ -z "$(SELECTED_PROJECTS)" ]; then \
	echo "ERROR: no projects selected"; \
	echo "Use PROJECT=<name> or PROJECTS=\"proj-a proj-b\""; \
	exit 1; \
fi
endef

define ENSURE_PROJECTS_EXIST
for proj in $(SELECTED_PROJECTS); do \
	if [ ! -d "$$proj" ] || [ ! -f "$$proj/pyproject.toml" ]; then \
		echo "ERROR: invalid project '$$proj'"; \
		exit 1; \
	fi; \
done
endef

define AUTO_SYNC_ALL_PROJECTS
for proj in $(ALL_PROJECTS); do \
	$(PY) -m flext_infra workspace sync --workspace "$$proj" --canonical-root "$(CURDIR)" --apply >/dev/null || exit 1; \
done
endef

define AUTO_ADJUST_SELECTED_PROJECTS
endef

define ENFORCE_WORKSPACE_VENV
if [ ! -d "$(WORKSPACE_VENV)" ]; then \
	echo "ERROR: workspace venv not found at $(WORKSPACE_VENV). Run 'make setup'."; \
	exit 1; \
fi; \
local_venvs=$$(for proj in $(ALL_PROJECTS); do \
	if [ -d "$$proj/.venv" ]; then echo "$$proj/.venv"; fi; \
done); \
if [ -n "$$local_venvs" ]; then \
	echo "Enforcing workspace venv by removing project-local .venv directories:"; \
	printf '%s\n' "$$local_venvs"; \
	for venv_path in $$local_venvs; do rm -rf "$$venv_path"; done; \
	echo "Project-local .venv directories removed."; \
fi; \
residual_venvs=$$(for proj in $(ALL_PROJECTS); do \
	if [ -d "$$proj/.venv" ]; then echo "$$proj/.venv"; fi; \
done); \
if [ -n "$$residual_venvs" ]; then \
	echo "ERROR: unable to remove some project-local .venv directories:"; \
	printf '%s\n' "$$residual_venvs"; \
	exit 1; \
fi
endef

# Guard: ensure .venv exists before running any target (read-only, no side effects)
define REQUIRE_VENV
if [ ! -x "$(PY)" ]; then \
	echo ""; \
	echo "ERROR: workspace .venv not found ($(PY) missing)."; \
	echo "    Run 'make setup' first to create the environment."; \
	echo ""; \
	exit 1; \
fi
endef

# Preflight: validate required tools before any destructive step
define PREFLIGHT_CHECK
	echo "--- Preflight checks ---"; \
	ok=1; \
	if ! command -v git >/dev/null 2>&1; then \
		echo " MISSING: git — install via your OS package manager (apt/brew/winget)"; ok=0; \
	fi; \
	if [ -z "$(PYTHON_CMD)" ] || ! command -v $(PYTHON_CMD) >/dev/null 2>&1; then \
		echo " MISSING: Python $(PYTHON_REQ_VERSION) — please install from https://python.org"; ok=0; \
	else \
		py_minor=$$($(PYTHON_CMD) -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 0); \
		req_minor=$$(echo $(PYTHON_REQ_VERSION) | cut -d. -f2); \
		if [ "$$py_minor" -ne "$$req_minor" ] 2>/dev/null; then \
			echo " REQUIRES: Python $(PYTHON_REQ_VERSION), found 3.$$py_minor — please install Python $(PYTHON_REQ_VERSION)"; ok=0; \
		fi; \
	fi; \
	if [ "$$ok" -eq 0 ]; then \
		echo ""; echo "Fix the above requirements and re-run: make setup"; exit 1; \
	fi; \
	echo " OK: all required tools present"
endef

.PHONY: help setup upgrade modernize build check security format docs test validate typings clean release pr commit tag push codegen status

help: ## Show simple workspace verbs
	$(Q)echo "FLEXT Workspace"
	$(Q)echo ""
	$(Q)echo "Projects: $(words $(ALL_PROJECTS)) total"
	$(Q)echo "Selection: $(words $(SELECTED_PROJECTS)) selected"
	$(Q)echo ""
	$(Q)echo "Core verbs:"
	$(Q)echo " setup   Install all projects into workspace .venv, then run validate VALIDATE_SCOPE=workspace"
	$(Q)echo " upgrade  Upgrade deps + modernize + dependency report (.reports/dependencies/)"
	$(Q)echo " modernize Modernize pyproject.toml configs only (no lock/install)"
	$(Q)echo " build   Build/package all selected projects"
	$(Q)echo " check   Run the 6 lint gates in all projects"
	$(Q)echo " security  Run all security checks in all projects"
	$(Q)echo " format   Run all formatting in all projects"
	$(Q)echo " docs    Build docs in all projects"
	$(Q)echo " test    Run tests only in all projects"
	$(Q)echo " validate  Run validate gates (FIX=1 auto-fix, VALIDATE_SCOPE=workspace for repo-level)"
	$(Q)echo " release  Interactive workspace release orchestration"
	$(Q)echo " pr     Manage PRs for selected projects"
	$(Q)echo " typings  Stub supply-chain + typing report (PROJECT/PROJECTS to scope)"
	$(Q)echo " clean   Clean all projects"
	$(Q)echo ""
	$(Q)echo "Git workflow:"
	$(Q)echo " commit  Commit all changes in selected projects (MESSAGE=)"
	$(Q)echo " tag    Create git tags for selected projects (TAG=, DRY_RUN=1)"
	$(Q)echo " push   Push branches and tags for selected projects"
	$(Q)echo " codegen  Standardize __init__.py lazy imports (PEP 562)"
	$(Q)echo ""
	$(Q)echo "Selectors:"
	$(Q)echo " PROJECT=<name>             Single project"
	$(Q)echo " PROJECTS=\"proj-a proj-b\"        Multi-project"
	$(Q)echo " FAIL_FAST=1               Stop on first project failure"
	$(Q)echo " FIX=1                  Auto-fix before validate"
	$(Q)echo " PYTEST_ARGS=\"-k expr -x\"        Extra pytest args for test"
	$(Q)echo " CHECK_GATES=lint,format,pyrefly,mypy,pyright,security,type  Select check gates (default: all)"
	$(Q)echo " VALIDATE_GATES=complexity,docstring   Select validate gates (default: all)"
	$(Q)echo " VALIDATE_SCOPE=project|workspace     Validate scope (default: project)"
	$(Q)echo " DOCS_PHASE=audit|fix|build|generate|validate|all"
	$(Q)echo " RELEASE_PHASE=validate,version,build,publish|all"
	$(Q)echo " INTERACTIVE=1|0             Release prompt mode"
	$(Q)echo " DRY_RUN=1                Print plan, do not tag/push"
	$(Q)echo " PUSH=1                  Push release commit/tag"
	$(Q)echo " VERSION=<semver> TAG=v<semver> BUMP=patch Release controls"
	$(Q)echo " RELEASE_DEV_SUFFIX=0|1         Append -dev during release version phase"
	$(Q)echo " RELEASE_NEXT_DEV=0|1          After release, auto-bump to next <RELEASE_NEXT_BUMP>-dev"
	$(Q)echo " RELEASE_NEXT_BUMP=major|minor|patch   Next dev bump strategy (default: minor)"
	$(Q)echo " CREATE_BRANCHES=1|0           Create release branches in workspace + projects"
	$(Q)echo " PR_ACTION=status|create|view|checks|merge|close"
	$(Q)echo " PR_BASE=main PR_HEAD=<branch> PR_NUMBER=<id> PR_DRAFT=0|1"
	$(Q)echo " PR_TITLE='title' PR_BODY='body' PR_MERGE_METHOD=squash|merge|rebase"
	$(Q)echo " PR_AUTO=0|1 PR_DELETE_BRANCH=0|1"
	$(Q)echo " PR_CHECKS_STRICT=0|1          checks action strict failure toggle"
	$(Q)echo " PR_RELEASE_ON_MERGE=0|1         merge action: dispatch release workflow"
	$(Q)echo " PR_INCLUDE_ROOT=0|1           include root repo in workspace PR automation"
	$(Q)echo " PR_BRANCH=<name> PR_CHECKPOINT=0|1   normalize branch + checkpoint before action"
	$(Q)echo " DEPS_REPORT=0              Skip dependency report after upgrade/typings"
	$(Q)echo " MESSAGE='chore: ...'          Commit message for commit verb"
	$(Q)echo ""
	$(Q)echo "Examples:"
	$(Q)echo " make check PROJECT=flext-core"
	$(Q)echo " make build"
	$(Q)echo " make typings PROJECT=flext-api"
	$(Q)echo " make check CHECK_GATES=lint,type"
	$(Q)echo " make validate PROJECTS=\"flext-core flext-api\" FIX=1"
	$(Q)echo " make test PROJECT=flext-api PYTEST_ARGS=\"-k unit\" FAIL_FAST=1"
	$(Q)echo " make validate VALIDATE_SCOPE=workspace"
	$(Q)echo " make release BUMP=minor"
	$(Q)echo " make commit MESSAGE='chore: upgrade deps'"
	$(Q)echo " make tag"
	$(Q)echo " make tag TAG=v1.0.0"
	$(Q)echo " make push"
	$(Q)echo " make codegen PROJECT=flext-core"
	$(Q)echo " make pr PROJECT=flext-core PR_ACTION=status"
	$(Q)echo " make pr PROJECT=flext-core PR_ACTION=create PR_TITLE='release: 0.11.0-dev'"
	$(Q)echo " NOTE: External projects (not in .gitmodules) require manual clone."

setup: ## Install all projects into workspace .venv
	$(Q)$(PREFLIGHT_CHECK)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)if [ -f .gitmodules ]; then \
		echo "Initializing and updating submodules..."; \
		git submodule sync --recursive; \
		if ! git submodule update --init --recursive --jobs $${JOBS:-8}; then \
			echo "Submodule update with configured URLs failed. Retrying with HTTPS fallback..."; \
			while IFS=' ' read -r key url; do \
				name="$${key#submodule.}"; \
				name="$${name%.url}"; \
				if [[ "$$url" == git@github.com:* ]]; then \
					https_url="https://github.com/$${url#git@github.com:}"; \
					git config "submodule.$$name.url" "$$https_url"; \
				fi; \
			done < <(git config --file .gitmodules --get-regexp '^submodule\..*\.url$$'); \
			git submodule sync --recursive; \
			git submodule update --init --recursive --jobs $${JOBS:-8} || { \
				echo "ERROR: failed to update submodules"; \
				exit 1; \
			}; \
		fi; \
		echo "Submodules ready."; \
	fi
	$(Q)[ -d ".venv" ] || { \
		echo "Creating .venv..."; \
		$(PYTHON_CMD) -m venv .venv; \
		echo "Installing poetry, pipx, and uv inside .venv..."; \
		.venv/bin/pip install -U pip poetry pipx uv; \
	}
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)echo "Bootstrapping flext-core runtime dependencies..."; \
	$(POETRY_ENV) $(POETRY_BIN) -C flext-core install --only main --no-interaction || exit 1
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)echo "Enforcing Python version guards..."; $(PY) -m flext_infra maintenance || exit 1
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)echo "Modernizing pyproject.toml files..."; \
	$(POETRY_ENV) $(PY) -m flext_infra deps modernize --skip-check --apply 2>&1 | grep -E "^Phase|Total:|✓|No semantic" || true; \
	echo ""
	$(Q)echo "Syncing dependency paths to workspace mode..."; \
	$(PY) -m flext_infra deps path-sync --mode auto --apply 2>&1 | grep -E "^\[sync|changed|No changes" || true; \
	echo ""
	$(Q)total_steps=$$(( $(words $(SELECTED_PROJECTS)) + 1 )); \
	echo "Starting workspace setup for $$total_steps item(s) ($(words $(SELECTED_PROJECTS)) projects + root)"; \
	failed=0; installed=0; step=1; failed_projects=""; \
	for proj in $(SELECTED_PROJECTS); do \
		if [ -d "$$proj" ] && [ -f "$$proj/pyproject.toml" ]; then \
			log_file="/tmp/flext-setup-$$proj.log"; \
			start_ts=$$(date +%s); \
			printf "[%2d/%2d] setup %s\n" $$step $$total_steps "$$proj"; \
			if FLEXT_WORKSPACE_ROOT="$(CURDIR)" $(PY) -m flext_infra deps internal-sync --workspace "$$proj" >>"$$log_file" 2>&1; then \
				:; \
			else \
				echo "     sync  ... failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "     lock  ... "; \
			if $(POETRY_ENV) $(POETRY_BIN) -C "$$proj" lock >"$$log_file" 2>&1; then \
				echo "ok"; \
			else \
				echo "failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "     install ... "; \
			if $(POETRY_ENV) $(POETRY_BIN) -C "$$proj" install --all-extras --all-groups >>"$$log_file" 2>&1; then \
				elapsed=$$(( $$(date +%s) - start_ts )); \
				echo "ok ($${elapsed}s)"; \
				installed=$$((installed + 1)); \
			else \
				echo "failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
			fi; \
			rm -f "$$log_file"; \
			step=$$((step + 1)); \
		fi; \
	done; \
	log_file="/tmp/flext-setup-root.log"; \
	start_ts=$$(date +%s); \
	root_lock_ok=0; \
	printf "[%2d/%2d] setup %s\n" $$step $$total_steps "root"; \
	if ! FLEXT_WORKSPACE_ROOT="$(CURDIR)" $(PY) -m flext_infra deps internal-sync --workspace . >"$$log_file" 2>&1; then \
		echo "     sync  ... failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	printf "     lock  ... "; \
	if $(POETRY_ENV) $(POETRY_BIN) lock >"$$log_file" 2>&1; then \
		echo "ok"; \
		root_lock_ok=1; \
	else \
		echo "failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	if [ $$root_lock_ok -eq 1 ]; then \
		printf "     install ... "; \
		if $(POETRY_ENV) $(POETRY_BIN) install --all-extras --all-groups >>"$$log_file" 2>&1; then \
			elapsed=$$(( $$(date +%s) - start_ts )); \
			echo "ok ($${elapsed}s)"; \
			installed=$$((installed + 1)); \
		else \
			echo "failed"; \
			cat "$$log_file"; \
			failed=$$((failed + 1)); \
			failed_projects="$$failed_projects root"; \
		fi; \
	else \
		printf "     install ... skipped\n"; \
	fi; \
	rm -f "$$log_file"; \
	echo "Setup summary: Installed=$$installed Failed=$$failed Total=$$total_steps"; \
	if [ $$failed -ne 0 ]; then \
		echo "Failed projects:$$failed_projects"; \
		echo "FAIL: setup ($$failed projects)"; \
		exit 1; \
	fi; \
	echo "Validating workspace (validate VALIDATE_SCOPE=workspace)..."; \
	$(MAKE) validate VALIDATE_SCOPE=workspace || { echo "FAIL: setup validation"; exit 1; }

upgrade: ## Upgrade Python dependencies to latest via Poetry
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)echo "Enforcing Python version guards..."; $(PY) -m flext_infra maintenance || exit 1
	$(Q)echo "Modernizing pyproject.toml files..."; \
	$(POETRY_ENV) $(PY) -m flext_infra deps modernize --skip-check --apply 2>&1 | grep -E "^Phase|Total:|✓|No semantic" || true; \
	echo ""
	$(Q)echo "Syncing dependency paths to workspace mode..."; \
	$(PY) -m flext_infra deps path-sync --mode auto --apply 2>&1 | grep -E "^\[sync|changed|No changes" || true; \
	echo ""
	$(Q)total_steps=$$(( $(words $(SELECTED_PROJECTS)) + 1 )); \
	echo "Upgrading Python dependencies for $(words $(SELECTED_PROJECTS)) project(s) + root"; \
	failed=0; upgraded=0; step=1; failed_projects=""; \
	for proj in $(SELECTED_PROJECTS); do \
		if [ -d "$$proj" ] && [ -f "$$proj/pyproject.toml" ]; then \
			log_file="/tmp/flext-upgrade-$$proj.log"; \
			start_ts=$$(date +%s); \
			printf "[%2d/%2d] upgrade %s\n" $$step $$total_steps "$$proj"; \
			if FLEXT_WORKSPACE_ROOT="$(CURDIR)" $(PY) -m flext_infra deps internal-sync --workspace "$$proj" >>"$$log_file" 2>&1; then \
				:; \
			else \
				echo "     sync  ... failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "     lock  ... "; \
			if $(POETRY_ENV) $(POETRY_BIN) -C "$$proj" lock >"$$log_file" 2>&1; then \
				echo "ok"; \
			else \
				echo "failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "     update ... "; \
			if $(POETRY_ENV) $(POETRY_BIN) -C "$$proj" update >"$$log_file" 2>&1; then \
				echo "ok"; \
			else \
				echo "failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "     install ... "; \
			if $(POETRY_ENV) $(POETRY_BIN) -C "$$proj" install --all-extras --all-groups >>"$$log_file" 2>&1; then \
				elapsed=$$(( $$(date +%s) - start_ts )); \
				echo "ok ($${elapsed}s)"; \
				upgraded=$$((upgraded + 1)); \
			else \
				echo "failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
			fi; \
			rm -f "$$log_file"; \
			step=$$((step + 1)); \
		fi; \
	done; \
	log_file="/tmp/flext-upgrade-root.log"; \
	start_ts=$$(date +%s); \
	root_update_ok=0; \
	printf "[%2d/%2d] upgrade %s\n" $$step $$total_steps "root"; \
	if ! FLEXT_WORKSPACE_ROOT="$(CURDIR)" $(PY) -m flext_infra deps internal-sync --workspace . >"$$log_file" 2>&1; then \
		echo "     sync  ... failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	printf "     lock  ... "; \
	if $(POETRY_ENV) $(POETRY_BIN) lock >"$$log_file" 2>&1; then \
		echo "ok"; \
	else \
		echo "failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	printf "     update ... "; \
	if $(POETRY_ENV) $(POETRY_BIN) update >"$$log_file" 2>&1; then \
		echo "ok"; \
		root_update_ok=1; \
	else \
		echo "failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	if [ $$root_update_ok -eq 1 ]; then \
		printf "     install ... "; \
		if $(POETRY_ENV) $(POETRY_BIN) install --all-extras --all-groups >>"$$log_file" 2>&1; then \
			elapsed=$$(( $$(date +%s) - start_ts )); \
			echo "ok ($${elapsed}s)"; \
			upgraded=$$((upgraded + 1)); \
		else \
			echo "failed"; \
			cat "$$log_file"; \
			failed=$$((failed + 1)); \
			failed_projects="$$failed_projects root"; \
		fi; \
	else \
		printf "     install ... skipped\n"; \
	fi; \
	rm -f "$$log_file"; \
	echo "Upgrade summary: Upgraded=$$upgraded Failed=$$failed Total=$$total_steps"; \
	if [ $$failed -ne 0 ]; then \
		echo "Failed projects:$$failed_projects"; \
		echo "FAIL: upgrade ($$failed projects)"; \
		exit 1; \
	fi; \
	if [ "$(DEPS_REPORT)" != "0" ]; then \
		echo "Dependency report (deptry + pip check)..."; \
		$(POETRY_ENV) $(PY) -m flext_infra deps detect -q --no-fail || true; \
	fi
	$(Q)echo "Syncing GitHub workflow templates..."
	$(Q)$(PY) -m flext_infra github workflows --workspace-root "$(CURDIR)" --apply --prune --report .reports/workflows/sync.json

modernize: ## Modernize pyproject.toml files (standardize configs without lock/install)
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)echo "Modernizing pyproject.toml files..."; \
	$(POETRY_ENV) $(PY) -m flext_infra deps modernize --skip-check --apply 2>&1 | grep -E "^Phase|Total:|✓|No semantic" || true; \
	echo ""
	$(Q)echo "Syncing dependency paths to workspace mode..."; \
	$(PY) -m flext_infra deps path-sync --mode auto --apply 2>&1 | grep -E "^\[sync|changed|No changes" || true; \
	echo ""
	$(Q)echo "Formatting pyproject.toml files with taplo..."; \
	taplo format pyproject.toml */pyproject.toml 2>&1 | grep -vE '^\s*$$' || true; \
	echo ""
	$(Q)echo "Formatting Python files (ruff)..."
	$(Q)$(POETRY_ENV) ruff format . --quiet
	$(Q)echo "Modernization complete."

check: ## Run lint gates in all projects (CHECK_GATES=lint,format,pyrefly,mypy,pyright,security)
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb check \
		$(if $(filter 1,$(FAIL_FAST)),--fail-fast) \
		$(if $(CHECK_GATES),--make-arg "CHECK_GATES=$(CHECK_GATES)") \
		$(SELECTED_PROJECTS)

check-cqrs-compliance: ## Enforce strict CQRS/FlextModels patterns across ecosystem
	$(Q).github/scripts/check-cqrs-compliance.sh

build: ## Build/package all selected projects
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(ORCHESTRATOR) --verb build $(if $(filter 1,$(FAIL_FAST)),--fail-fast) $(SELECTED_PROJECTS)

release: ## Interactive workspace release orchestration
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(PY) -m flext_infra release \
		--workspace "$(CURDIR)" \
		--phase "$(RELEASE_PHASE)" \
		--interactive "$(INTERACTIVE)" \
		--next-bump "$(RELEASE_NEXT_BUMP)" \
		--create-branches "$(CREATE_BRANCHES)" \
		--projects $(SELECTED_PROJECTS) \
		$(if $(filter 1,$(RELEASE_DEV_SUFFIX)),--dev-suffix,) \
		$(if $(filter 1,$(RELEASE_NEXT_DEV)),--next-dev,) \
		$(if $(filter 1,$(DRY_RUN)),--dry-run,) \
		$(if $(filter 1,$(PUSH)),--push,) \
		$(if $(VERSION),--version "$(VERSION)",) \
		$(if $(TAG),--tag "$(TAG)",) \
		$(if $(BUMP),--bump "$(BUMP)",)

pr: ## Manage pull requests for selected projects
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(PY) -m flext_infra github pr-workspace \
		--workspace-root "$(CURDIR)" \
		$(foreach proj,$(SELECTED_PROJECTS),--project "$(proj)") \
		--include-root "$(PR_INCLUDE_ROOT)" \
		--branch "$(PR_BRANCH)" \
		--checkpoint "$(PR_CHECKPOINT)" \
		--fail-fast "$(if $(filter 1,$(FAIL_FAST)),1,0)" \
		--pr-action "$(PR_ACTION)" \
		--pr-base "$(PR_BASE)" \
		$(if $(PR_HEAD),--pr-head "$(PR_HEAD)",) \
		$(if $(PR_NUMBER),--pr-number "$(PR_NUMBER)",) \
		$(if $(PR_TITLE),--pr-title "$(PR_TITLE)",) \
		$(if $(PR_BODY),--pr-body "$(PR_BODY)",) \
		--pr-draft "$(PR_DRAFT)" \
		--pr-merge-method "$(PR_MERGE_METHOD)" \
		--pr-auto "$(PR_AUTO)" \
		--pr-delete-branch "$(PR_DELETE_BRANCH)" \
		--pr-checks-strict "$(PR_CHECKS_STRICT)" \
		--pr-release-on-merge "$(PR_RELEASE_ON_MERGE)"

security: ## Run all security checks in all projects
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb security $(if $(filter 1,$(FAIL_FAST)),--fail-fast) $(SELECTED_PROJECTS)

format: ## Run code formatting across all workspace projects (ruff/gofmt + markdownlint)
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)echo "Formatting Python files (ruff)..."
	$(Q)$(POETRY_ENV) ruff format . --quiet
	$(Q)go_files=$$(find . -type f -name '*.go' ! -path '*/.git/*' ! -path '*/vendor/*' ! -path '*/.venv/*'); \
	if [ -n "$$go_files" ]; then \
		echo "Formatting Go files (gofmt)..."; \
		printf '%s\n' "$$go_files" | xargs gofmt -w; \
		if command -v goimports >/dev/null 2>&1; then \
			printf '%s\n' "$$go_files" | xargs goimports -w; \
		fi; \
	fi
	$(Q)md_files=$$(git ls-files -- '*.md' ':!vendor/' && git ls-files --others --exclude-standard -- '*.md' ':!vendor/'); \
	if [ -n "$$md_files" ]; then \
		echo "Formatting Markdown files (markdownlint)..."; \
		md_config=""; \
		if [ -f ".markdownlint.json" ]; then \
			md_config="--config .markdownlint.json"; \
		fi; \
		echo "$$md_files" | xargs markdownlint --fix $$md_config 2>/dev/null || true; \
	fi
	$(Q)echo "Format complete."

docs: ## Run docs pipeline (DOCS_PHASE=audit|fix|build|generate|validate|all)
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(ORCHESTRATOR) --verb docs \
		$(if $(filter 1,$(FAIL_FAST)),--fail-fast) \
		--make-arg "DOCS_PHASE=$(DOCS_PHASE)" \
		$(if $(FIX),--make-arg "FIX=$(FIX)") \
		$(SELECTED_PROJECTS)

test: ## Run tests only in all projects
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb test \
		$(if $(filter 1,$(FAIL_FAST)),--fail-fast) \
		$(if $(PYTEST_ARGS),--make-arg "PYTEST_ARGS=$(PYTEST_ARGS)") \
		$(SELECTED_PROJECTS)

validate: ## Run validate gates (VALIDATE_SCOPE=project|workspace, FIX=1)
ifeq ($(VALIDATE_SCOPE),workspace)
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(AUTO_SYNC_ALL_PROJECTS)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)mkdir -p .reports
	$(Q)echo "Running workspace validation (inventory + strict anti-drift gates)..."
	$(Q)$(PY) -m flext_infra maintenance --check || exit 1
	$(Q)$(PY) -m flext_infra validate inventory --workspace .
	$(Q)$(PY) -m flext_infra validate basemk-validate
	$(Q)$(PY) -m flext_infra github lint --workspace . --report .reports/workflows/actionlint.json
	$(Q)$(PY) -m flext_infra validate skill-validate --skill scripts-validation --mode strict
	$(Q)$(PY) -m flext_infra validate skill-validate --skill rules-github --mode strict
	$(Q)$(PY) -m flext_infra validate skill-validate --skill rules-docker --mode strict
	$(Q)$(PY) -m flext_infra deps modernize --audit
	$(Q)if git grep -nE '/home/.*/flext|file:///home/.*/flext' -- . ':!Makefile'; then \
		echo "ERROR: absolute workspace paths detected in tracked sources/config"; \
		exit 1; \
	fi
else
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(VALIDATE_FIX_PARAM)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)if [ -z "$(FIX)" ]; then echo "INFO: run 'make validate FIX=1' to auto-fix before validate"; fi
	$(Q)$(ORCHESTRATOR) --verb validate \
		$(if $(filter 1,$(FAIL_FAST)),--fail-fast) \
		$(if $(FIX),--make-arg "FIX=$(FIX)") \
		$(if $(VALIDATE_GATES),--make-arg "VALIDATE_GATES=$(VALIDATE_GATES)") \
		$(SELECTED_PROJECTS)
endif

typings: ## Run typings supply-chain (stubgen + stub_supply_chain + dependency report). Use PROJECT= or PROJECTS= to scope.
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)echo "Regenerating typings/generated/ via stubgen (PEP 561 pre-check)..."
	$(Q)gen_dir="$(CURDIR)/typings/generated"; \
	tmp_dir=$$(mktemp -d); \
	packages=$$(find "$$gen_dir" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort); \
	ok=0; fail=0; skip=0; \
	if [ -n "$$packages" ]; then \
		for pkg in $$packages; do \
			pkg_mod=$$(echo "$$pkg" | tr '-' '_'); \
			if $(POETRY_ENV) $(PY) -c "import importlib.util,pathlib;s=importlib.util.find_spec('$$pkg_mod');exit(0 if s and s.origin and (pathlib.Path(s.origin).parent/'py.typed').exists() else 1)" 2>/dev/null; then \
				echo "  skip: $$pkg (ships py.typed)"; \
				skip=$$((skip + 1)); \
				continue; \
			fi; \
			types_dash=$$(echo "$$pkg_mod" | tr '_' '-'); \
			if $(POETRY_ENV) $(PY) -c "import importlib.metadata;importlib.metadata.version('types-$$types_dash')" 2>/dev/null; then \
				echo "  skip: $$pkg (types-$$types_dash installed)"; \
				skip=$$((skip + 1)); \
				continue; \
			fi; \
			if $(POETRY_ENV) $(PY) -m mypy.stubgen -p "$$pkg" -o "$$tmp_dir" --include-private --export-less -q 2>/dev/null; then \
				if [ -d "$$tmp_dir/$$pkg" ]; then \
					rm -rf "$$gen_dir/$$pkg"; \
					mv "$$tmp_dir/$$pkg" "$$gen_dir/$$pkg"; \
					ok=$$((ok + 1)); \
				fi; \
			else \
				fail=$$((fail + 1)); \
				echo "  warning: stubgen failed for $$pkg (keeping existing)"; \
			fi; \
		done; \
		echo "  stubgen: $$ok regenerated, $$skip skipped (typed), $$fail failed"; \
	else \
		echo "  no packages to regenerate"; \
	fi; \
	rm -rf "$$tmp_dir"
	$(Q)$(POETRY_ENV) $(PY) -m flext_infra validate stub-validate \
		$(if $(PROJECT),--project $(PROJECT),$(if $(PROJECTS),$(addprefix --project ,$(PROJECTS)),--all))
	$(Q)if [ "$(DEPS_REPORT)" != "0" ]; then \
		$(POETRY_ENV) $(PY) -m flext_infra deps detect --typings -q --no-fail || true; \
	fi

clean: ## Clean all projects
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb clean $(if $(filter 1,$(FAIL_FAST)),--fail-fast) $(SELECTED_PROJECTS)
	$(Q)rm -rf .pytest_cache/ htmlcov/ .coverage* .mypy_cache/ .ruff_cache/

commit: ## Commit all changes in selected projects (MESSAGE=)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)if [ -z "$(MESSAGE)" ]; then \
		echo "ERROR: MESSAGE is required. Usage: make commit MESSAGE='chore: your message'"; \
		exit 1; \
	fi
	$(Q)committed=0; skipped=0; failed=0; \
	for proj in $(SELECTED_PROJECTS); do \
		if [ -e "$$proj/.git" ]; then \
			changes=$$(cd "$$proj" && git status --porcelain 2>/dev/null | wc -l); \
			if [ "$$changes" -gt 0 ]; then \
				if (cd "$$proj" && git add -A && git commit -m "$(MESSAGE)") >/dev/null 2>&1; then \
					echo "  ✓ $$proj"; \
					committed=$$((committed + 1)); \
				else \
					echo "  ✗ $$proj (commit failed)"; \
					failed=$$((failed + 1)); \
				fi; \
			else \
				skipped=$$((skipped + 1)); \
			fi; \
		fi; \
	done; \
	root_changes=$$(git status --porcelain 2>/dev/null | wc -l); \
	if [ "$$root_changes" -gt 0 ]; then \
		if git add -A && git commit -m "$(MESSAGE)" >/dev/null 2>&1; then \
			echo "  ✓ root"; \
			committed=$$((committed + 1)); \
		else \
			echo "  ✗ root (commit failed)"; \
			failed=$$((failed + 1)); \
		fi; \
	fi; \
	echo "Commit: $$committed committed, $$skipped clean, $$failed failed"

status: ## Show git status for all workspace projects (submodules + external + root)
	$(Q)for proj in $(ALL_PROJECTS); do \
		if [ -e "$$proj/.git" ]; then \
			changes=$$(cd "$$proj" && git status --porcelain 2>/dev/null); \
			if [ -n "$$changes" ]; then \
				echo "── $$proj ──"; \
				(cd "$$proj" && git status --short); \
			else \
				echo "  ✓ $$proj (clean)"; \
			fi; \
		fi; \
	done; \
	root_changes=$$(git status --porcelain 2>/dev/null); \
	if [ -n "$$root_changes" ]; then \
		echo "── root ──"; \
		git status --short; \
	else \
		echo "  ✓ root (clean)"; \
	fi

tag: ## Create git tags for selected projects (TAG= optional, DRY_RUN=1)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)tagged=0; skipped=0; failed=0; \
	for proj in $(SELECTED_PROJECTS); do \
		if [ -e "$$proj/.git" ] && [ -f "$$proj/pyproject.toml" ]; then \
			ver=$$(grep '^version' "$$proj/pyproject.toml" | head -1 | awk -F'"' '{print $$2}'); \
			tag_name="$${TAG:-v$$ver}"; \
			existing=$$(cd "$$proj" && git tag -l "$$tag_name" 2>/dev/null); \
			if [ -n "$$existing" ]; then \
				echo "  - $$proj: $$tag_name (already exists)"; \
				skipped=$$((skipped + 1)); \
			else \
				if [ "$(DRY_RUN)" = "1" ]; then \
					echo "  ~ $$proj: $$tag_name (dry-run)"; \
					tagged=$$((tagged + 1)); \
				else \
					if (cd "$$proj" && git tag -a "$$tag_name" -m "release: $$tag_name") 2>/dev/null; then \
						echo "  ✓ $$proj: $$tag_name"; \
						tagged=$$((tagged + 1)); \
					else \
						echo "  ✗ $$proj: $$tag_name (failed)"; \
						failed=$$((failed + 1)); \
					fi; \
				fi; \
			fi; \
		fi; \
	done; \
	root_ver=$$(grep '^version' pyproject.toml | head -1 | awk -F'"' '{print $$2}'); \
	root_tag="$${TAG:-v$$root_ver}"; \
	existing=$$(git tag -l "$$root_tag" 2>/dev/null); \
	if [ -n "$$existing" ]; then \
		echo "  - root: $$root_tag (already exists)"; \
		skipped=$$((skipped + 1)); \
	else \
		if [ "$(DRY_RUN)" = "1" ]; then \
			echo "  ~ root: $$root_tag (dry-run)"; \
			tagged=$$((tagged + 1)); \
		else \
			if git tag -a "$$root_tag" -m "release: $$root_tag" 2>/dev/null; then \
				echo "  ✓ root: $$root_tag"; \
				tagged=$$((tagged + 1)); \
			else \
				echo "  ✗ root: $$root_tag (failed)"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	fi; \
	echo "Tag: $$tagged tagged, $$skipped skipped, $$failed failed"

push: ## Push branches and tags for selected projects
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)pushed=0; failed=0; \
	for proj in $(SELECTED_PROJECTS); do \
		if [ -e "$$proj/.git" ]; then \
			if [ "$(DRY_RUN)" = "1" ]; then \
				echo "  ~ $$proj (dry-run)"; \
				pushed=$$((pushed + 1)); \
			else \
				if (cd "$$proj" && git push && git push --tags) >/dev/null 2>&1; then \
					echo "  ✓ $$proj"; \
					pushed=$$((pushed + 1)); \
				else \
					echo "  ✗ $$proj"; \
					failed=$$((failed + 1)); \
				fi; \
			fi; \
		fi; \
	done; \
	if [ "$(DRY_RUN)" = "1" ]; then \
		echo "  ~ root (dry-run)"; \
		pushed=$$((pushed + 1)); \
	else \
		if git push && git push --tags 2>/dev/null; then \
			echo "  ✓ root"; \
			pushed=$$((pushed + 1)); \
		else \
			echo "  ✗ root"; \
			failed=$$((failed + 1)); \
		fi; \
	fi; \
	echo "Push: $$pushed pushed, $$failed failed"

codegen: ## Standardize __init__.py lazy imports (PEP 562)
	$(Q)$(REQUIRE_VENV)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)echo "Standardizing __init__.py lazy imports..."
	$(Q)PYTHONPATH="$(CURDIR)/flext-infra/src:$$PYTHONPATH" $(PY) -m flext_infra codegen lazy-init --workspace "$(CURDIR)"
	$(Q)echo "Formatting generated files (ruff)..."
	$(Q)$(POETRY_ENV) ruff format . --quiet
