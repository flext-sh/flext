# =============================================================================
# FLEXT Workspace Makefile - Simple Verbs Only
# =============================================================================

SHELL := /usr/bin/bash
.DEFAULT_GOAL := help

WORKSPACE_VENV := $(CURDIR)/.venv
POETRY_ENV := VIRTUAL_ENV=$(WORKSPACE_VENV) PATH=$(WORKSPACE_VENV)/bin:$$PATH POETRY_VIRTUALENVS_CREATE=false POETRY_VIRTUALENVS_IN_PROJECT=false
ORCHESTRATOR := $(POETRY_ENV) python scripts/workspace_orchestrator.py
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
TAG ?=
BUMP ?=
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

Q := @
ifdef VERBOSE
Q :=
endif

# Project discovery: single source of truth via scripts/maintenance/_discover.py
FLEXT_PROJECTS := $(shell python3 scripts/maintenance/_discover.py --kind submodule --format makefile 2>/dev/null)
EXTERNAL_PROJECTS := $(shell python3 scripts/maintenance/_discover.py --kind external --format makefile 2>/dev/null)

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
	python3 scripts/sync.py --project-root "$$proj" --canonical-root "$(CURDIR)" >/dev/null || exit 1; \
done
endef

define AUTO_ADJUST_SELECTED_PROJECTS
for proj in $(SELECTED_PROJECTS); do \
	if [ -d "$$proj" ]; then \
		md_files=$$(find "$$proj" -type f -name '*.md' ! -path "$$proj/.git/*" ! -path "$$proj/.reports/*" ! -path "$$proj/reports/*" ! -path "$$proj/.venv/*" ! -path "$$proj/node_modules/*" ! -path "$$proj/.flext-deps/*" ! -path "$$proj/.mypy_cache/*" ! -path "$$proj/.pytest_cache/*" ! -path "$$proj/.ruff_cache/*" ! -path "$$proj/dist/*" ! -path "$$proj/build/*"); \
		md_config=""; \
		if [ -f ".markdownlint.json" ]; then md_config="--config .markdownlint.json"; fi; \
		if [ -n "$$md_files" ] && [ -x "$(WORKSPACE_VENV)/bin/mdformat" ]; then \
			mkdir -p .reports/workspace/preflight; \
			printf '%s\n' "$$md_files" | xargs -r $(WORKSPACE_VENV)/bin/mdformat 2>>.reports/workspace/preflight/mdformat.log || true; \
		fi; \
		if [ -n "$$md_files" ] && command -v markdownlint >/dev/null 2>&1; then \
			markdownlint --fix $$md_config $$md_files || true; \
		fi; \
		if [ -f "$$proj/go.mod" ] && command -v gofmt >/dev/null 2>&1; then \
			go_files=$$(find "$$proj" -type f -name '*.go' ! -path "$$proj/.git/*"); \
			if [ -n "$$go_files" ]; then \
				printf '%s\n' "$$go_files" | xargs -r gofmt -w; \
			fi; \
		fi; \
	fi; \
done
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

.PHONY: help setup upgrade build check security format docs test validate typings clean release release-ci pr

help: ## Show simple workspace verbs
	$(Q)echo "FLEXT Workspace"
	$(Q)echo ""
	$(Q)echo "Projects: $(words $(ALL_PROJECTS)) total"
	$(Q)echo "Selection: $(words $(SELECTED_PROJECTS)) selected"
	$(Q)echo ""
	$(Q)echo "Core verbs:"
	$(Q)echo "  setup      Install all projects into workspace .venv, then run validate VALIDATE_SCOPE=workspace"
	$(Q)echo "  upgrade    Upgrade deps + modernize + dependency report (.reports/dependencies/)"
	$(Q)echo "  build      Build/package all selected projects"
	$(Q)echo "  check      Run the 6 lint gates in all projects"
	$(Q)echo "  security   Run all security checks in all projects"
	$(Q)echo "  format     Run all formatting in all projects"
	$(Q)echo "  docs       Build docs in all projects"
	$(Q)echo "  test       Run tests only in all projects"
	$(Q)echo "  validate   Run validate gates (FIX=1 auto-fix, VALIDATE_SCOPE=workspace for repo-level)"
	$(Q)echo "  release    Interactive workspace release orchestration"
	$(Q)echo "  release-ci Non-interactive release run for CI/tag workflows"
	$(Q)echo "  pr         Manage PRs for selected projects"
	$(Q)echo "  typings    Stub supply-chain + typing report (PROJECT/PROJECTS to scope)"
	$(Q)echo "  clean      Clean all projects"
	$(Q)echo ""
	$(Q)echo "Selectors:"
	$(Q)echo "  PROJECT=<name>                          Single project"
	$(Q)echo "  PROJECTS=\"proj-a proj-b\"               Multi-project"
	$(Q)echo "  FAIL_FAST=1                              Stop on first project failure"
	$(Q)echo "  FIX=1                                    Auto-fix before validate"
	$(Q)echo "  PYTEST_ARGS=\"-k expr -x\"               Extra pytest args for test"
	$(Q)echo "  CHECK_GATES=lint,format,pyrefly,mypy,pyright,security,type    Select check gates (default: all)"
	$(Q)echo "  VALIDATE_GATES=complexity,docstring      Select validate gates (default: all)"
	$(Q)echo "  VALIDATE_SCOPE=project|workspace         Validate scope (default: project)"
	$(Q)echo "  DOCS_PHASE=audit|fix|build|generate|validate|all"
	$(Q)echo "  RELEASE_PHASE=validate,version,build,publish|all"
	$(Q)echo "  INTERACTIVE=1|0                          Release prompt mode"
	$(Q)echo "  DRY_RUN=1                                Print plan, do not tag/push"
	$(Q)echo "  PUSH=1                                   Push release commit/tag"
	$(Q)echo "  VERSION=<semver> TAG=v<semver> BUMP=patch Release controls"
	$(Q)echo "  CREATE_BRANCHES=1|0                      Create release branches in workspace + projects"
	$(Q)echo "  PR_ACTION=status|create|view|checks|merge|close"
	$(Q)echo "  PR_BASE=main PR_HEAD=<branch> PR_NUMBER=<id> PR_DRAFT=0|1"
	$(Q)echo "  PR_TITLE='title' PR_BODY='body' PR_MERGE_METHOD=squash|merge|rebase"
	$(Q)echo "  PR_AUTO=0|1 PR_DELETE_BRANCH=0|1"
	$(Q)echo "  DEPS_REPORT=0                            Skip dependency report after upgrade/typings"
	$(Q)echo ""
	$(Q)echo "Examples:"
	$(Q)echo "  make check PROJECT=flext-core"
	$(Q)echo "  make build"
	$(Q)echo "  make typings PROJECT=flext-api"
	$(Q)echo "  make check CHECK_GATES=lint,type"
	$(Q)echo "  make validate PROJECTS=\"flext-core flext-api\" FIX=1"
	$(Q)echo "  make test PROJECT=flext-api PYTEST_ARGS=\"-k unit\" FAIL_FAST=1"
	$(Q)echo "  make validate VALIDATE_SCOPE=workspace"
	$(Q)echo "  make release BUMP=minor"
	$(Q)echo "  make release-ci VERSION=0.11.0 TAG=v0.11.0 RELEASE_PHASE=all"
	$(Q)echo "  make pr PROJECT=flext-core PR_ACTION=status"
	$(Q)echo "  make pr PROJECT=flext-core PR_ACTION=create PR_TITLE='release: 0.11.0-dev'"
	$(Q)echo "  NOTE: External projects (not in .gitmodules) require manual clone."

setup: ## Install all projects into workspace .venv
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)python3.13 --version >/dev/null 2>&1 || { echo "ERROR: Python 3.13 required"; exit 1; }
	$(Q)echo "Initializing git submodules..."; \
	if [ -f .gitmodules ]; then \
		git submodule update --init --recursive 2>&1; \
		echo "Submodules initialized."; \
	fi
	$(Q)[ -d ".venv" ] || { echo "Creating .venv with Python 3.13..."; python3.13 -m venv .venv; }
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)echo "Enforcing Python 3.13 version guards..."; python3.13 scripts/maintenance/enforce_python_version.py || exit 1
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)echo "Modernizing pyproject.toml files..."; \
	$(POETRY_ENV) python scripts/dependencies/modernize_pyproject.py --skip-check 2>&1 | grep -E "^Phase|Total:|✓|No semantic" || true; \
	echo ""
	$(Q)total_steps=$$(( $(words $(SELECTED_PROJECTS)) + 1 )); \
	echo "Starting workspace setup for $$total_steps item(s) ($(words $(SELECTED_PROJECTS)) projects + root)"; \
	failed=0; installed=0; step=1; failed_projects=""; \
	for proj in $(SELECTED_PROJECTS); do \
		if [ -d "$$proj" ] && [ -f "$$proj/pyproject.toml" ]; then \
			log_file="/tmp/flext-setup-$$proj.log"; \
			start_ts=$$(date +%s); \
			printf "[%2d/%2d] setup %s\n" $$step $$total_steps "$$proj"; \
			if FLEXT_WORKSPACE_ROOT="$(CURDIR)" python scripts/dependencies/sync_internal_deps.py --project-root "$$proj" >>"$$log_file" 2>&1; then \
				:; \
			else \
				echo "          sync    ... failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "          lock    ... "; \
			if $(POETRY_ENV) poetry -C "$$proj" lock >"$$log_file" 2>&1; then \
				echo "ok"; \
			else \
				echo "failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "          install ... "; \
			if $(POETRY_ENV) poetry -C "$$proj" install --all-extras --all-groups >>"$$log_file" 2>&1; then \
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
	if ! FLEXT_WORKSPACE_ROOT="$(CURDIR)" python scripts/dependencies/sync_internal_deps.py --project-root . >"$$log_file" 2>&1; then \
		echo "          sync    ... failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	printf "          lock    ... "; \
	if poetry lock >"$$log_file" 2>&1; then \
		echo "ok"; \
		root_lock_ok=1; \
	else \
		echo "failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	if [ $$root_lock_ok -eq 1 ]; then \
		printf "          install ... "; \
		if poetry install --all-extras --all-groups >>"$$log_file" 2>&1; then \
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
		printf "          install ... skipped\n"; \
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
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)echo "Enforcing Python 3.13 version guards..."; python3.13 scripts/maintenance/enforce_python_version.py || exit 1
	$(Q)echo "Modernizing pyproject.toml files..."; \
	$(POETRY_ENV) python scripts/dependencies/modernize_pyproject.py --skip-check 2>&1 | grep -E "^Phase|Total:|✓|No semantic" || true; \
	echo ""
	$(Q)total_steps=$$(( $(words $(SELECTED_PROJECTS)) + 1 )); \
	echo "Upgrading Python dependencies for $(words $(SELECTED_PROJECTS)) project(s) + root"; \
	failed=0; upgraded=0; step=1; failed_projects=""; \
	for proj in $(SELECTED_PROJECTS); do \
		if [ -d "$$proj" ] && [ -f "$$proj/pyproject.toml" ]; then \
			log_file="/tmp/flext-upgrade-$$proj.log"; \
			start_ts=$$(date +%s); \
			printf "[%2d/%2d] upgrade %s\n" $$step $$total_steps "$$proj"; \
			if FLEXT_WORKSPACE_ROOT="$(CURDIR)" python scripts/dependencies/sync_internal_deps.py --project-root "$$proj" >>"$$log_file" 2>&1; then \
				:; \
			else \
				echo "          sync    ... failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "          update  ... "; \
			if $(POETRY_ENV) poetry -C "$$proj" update >"$$log_file" 2>&1; then \
				echo "ok"; \
			else \
				echo "failed"; \
				cat "$$log_file"; \
				failed=$$((failed + 1)); \
				failed_projects="$$failed_projects $$proj"; \
				step=$$((step + 1)); \
				continue; \
			fi; \
			printf "          install ... "; \
			if $(POETRY_ENV) poetry -C "$$proj" install --all-extras --all-groups >>"$$log_file" 2>&1; then \
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
	if ! FLEXT_WORKSPACE_ROOT="$(CURDIR)" python scripts/dependencies/sync_internal_deps.py --project-root . >"$$log_file" 2>&1; then \
		echo "          sync    ... failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	printf "          update  ... "; \
	if poetry update >"$$log_file" 2>&1; then \
		echo "ok"; \
		root_update_ok=1; \
	else \
		echo "failed"; \
		cat "$$log_file"; \
		failed=$$((failed + 1)); \
		failed_projects="$$failed_projects root"; \
	fi; \
	if [ $$root_update_ok -eq 1 ]; then \
		printf "          install ... "; \
		if poetry install --all-extras --all-groups >>"$$log_file" 2>&1; then \
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
		printf "          install ... skipped\n"; \
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
		$(POETRY_ENV) python scripts/dependencies/detect_runtime_dev_deps.py -q --no-fail || true; \
	fi
	$(Q)echo "Syncing GitHub workflow templates..."
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/github/sync_workflows.py --workspace-root "$(CURDIR)" --apply --prune --report .reports/workflows/sync.json

check: ## Run lint gates in all projects (CHECK_GATES=lint,format,pyrefly,mypy,pyright,security)
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(POETRY_ENV) python scripts/check/fix_pyrefly_config.py $(SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb check \
		$(if $(filter 1,$(FAIL_FAST)),--fail-fast) \
		$(if $(CHECK_GATES),--make-arg "CHECK_GATES=$(CHECK_GATES)") \
		$(SELECTED_PROJECTS)

build: ## Build/package all selected projects
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(ORCHESTRATOR) --verb build $(if $(filter 1,$(FAIL_FAST)),--fail-fast) $(SELECTED_PROJECTS)

release: ## Interactive workspace release orchestration
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)python scripts/release/run.py \
		--root "$(CURDIR)" \
		--phase "$(RELEASE_PHASE)" \
		--interactive "$(INTERACTIVE)" \
		--create-branches "$(CREATE_BRANCHES)" \
		--projects $(SELECTED_PROJECTS) \
		$(if $(DRY_RUN),--dry-run "$(DRY_RUN)",) \
		$(if $(PUSH),--push "$(PUSH)",) \
		$(if $(VERSION),--version "$(VERSION)",) \
		$(if $(TAG),--tag "$(TAG)",) \
		$(if $(BUMP),--bump "$(BUMP)",)

release-ci: ## Non-interactive release run for CI/tag workflows
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)python scripts/release/run.py \
		--root "$(CURDIR)" \
		--phase "$(RELEASE_PHASE)" \
		--interactive 0 \
		--create-branches 0 \
		--projects $(SELECTED_PROJECTS) \
		$(if $(DRY_RUN),--dry-run "$(DRY_RUN)",) \
		$(if $(PUSH),--push "$(PUSH)",) \
		$(if $(VERSION),--version "$(VERSION)",) \
		$(if $(TAG),--tag "$(TAG)",) \
		$(if $(BUMP),--bump "$(BUMP)",)

pr: ## Manage pull requests for selected projects
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(ORCHESTRATOR) --verb pr \
		$(if $(filter 1,$(FAIL_FAST)),--fail-fast) \
		--make-arg "PR_ACTION=$(PR_ACTION)" \
		--make-arg "PR_BASE=$(PR_BASE)" \
		$(if $(PR_HEAD),--make-arg "PR_HEAD=$(PR_HEAD)",) \
		$(if $(PR_NUMBER),--make-arg "PR_NUMBER=$(PR_NUMBER)",) \
		$(if $(PR_TITLE),--make-arg "PR_TITLE=$(PR_TITLE)",) \
		$(if $(PR_BODY),--make-arg "PR_BODY=$(PR_BODY)",) \
		--make-arg "PR_DRAFT=$(PR_DRAFT)" \
		--make-arg "PR_MERGE_METHOD=$(PR_MERGE_METHOD)" \
		--make-arg "PR_AUTO=$(PR_AUTO)" \
		--make-arg "PR_DELETE_BRANCH=$(PR_DELETE_BRANCH)" \
		$(SELECTED_PROJECTS)

security: ## Run all security checks in all projects
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb security $(if $(filter 1,$(FAIL_FAST)),--fail-fast) $(SELECTED_PROJECTS)

format: ## Run all formatting in all projects
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb format $(if $(filter 1,$(FAIL_FAST)),--fail-fast) $(SELECTED_PROJECTS)

docs: ## Run docs pipeline (DOCS_PHASE=audit|fix|build|generate|validate|all)
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
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(AUTO_SYNC_ALL_PROJECTS)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)mkdir -p .reports
	$(Q)echo "Running workspace validation (inventory + strict anti-drift gates)..."
	$(Q)python3.13 scripts/maintenance/enforce_python_version.py --check || exit 1
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/core/generate_scripts_inventory.py --root .
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/core/check_base_mk_sync.py
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/github/lint_workflows.py --root . --report .reports/workflows/actionlint.json
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/core/skill_validate.py --skill scripts-validation --mode strict
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/core/skill_validate.py --skill rules-github --mode strict
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/core/skill_validate.py --skill rules-docker --mode strict
	$(Q)$(WORKSPACE_VENV)/bin/python scripts/dependencies/modernize_pyproject.py --audit
	$(Q)if git grep -nE '/home/.*/flext|file:///home/.*/flext' -- . ':!Makefile' ':!scripts/doc_scripts_analysis.json' ':!scripts/doc_scripts_inventory.json'; then \
		echo "ERROR: absolute workspace paths detected in tracked sources/config"; \
		exit 1; \
	fi
else
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

typings: ## Run typings supply-chain (stub_supply_chain + dependency report with typings). Use PROJECT= or PROJECTS= to scope.
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(POETRY_ENV) python scripts/core/stub_supply_chain.py --apply --idempotency-check \
		$(if $(PROJECT),--project $(PROJECT),$(if $(PROJECTS),$(addprefix --project ,$(PROJECTS)),--all))
	$(Q)if [ "$(DEPS_REPORT)" != "0" ]; then \
		$(POETRY_ENV) python scripts/dependencies/detect_runtime_dev_deps.py --typings -q --no-fail || true; \
	fi

clean: ## Clean all projects
	$(Q)$(ENSURE_NO_PROJECT_CONFLICT)
	$(Q)$(ENFORCE_WORKSPACE_VENV)
	$(Q)$(ENSURE_SELECTED_PROJECTS)
	$(Q)$(ENSURE_PROJECTS_EXIST)
	$(Q)$(AUTO_ADJUST_SELECTED_PROJECTS)
	$(Q)$(ORCHESTRATOR) --verb clean $(if $(filter 1,$(FAIL_FAST)),--fail-fast) $(SELECTED_PROJECTS)
	$(Q)rm -rf .pytest_cache/ htmlcov/ .coverage* .mypy_cache/ .ruff_cache/
