# =============================================================================
# FLEXT Workspace Makefile - Auto-Discovery & Orchestration
# =============================================================================
# Usage: make [target] [VERBOSE=1] [PROJECT=name]
#
# Project Discovery:
#   - FLEXT projects: flext-* in .gitmodules + pyproject.toml
#   - External projects: pyproject.toml + uses flext-core + NOT in .gitmodules
# =============================================================================

SHELL := /usr/bin/bash
.DEFAULT_GOAL := help

WORKSPACE_VENV := $(CURDIR)/.venv
POETRY_ENV := VIRTUAL_ENV=$(WORKSPACE_VENV) PATH=$(WORKSPACE_VENV)/bin:$$PATH POETRY_VIRTUALENVS_CREATE=false POETRY_VIRTUALENVS_IN_PROJECT=false

# === SILENT MODE ===
Q := @
ifdef VERBOSE
Q :=
endif

# =============================================================================
# AUTO-DISCOVERY
# =============================================================================

# Discover flext-* submodules from .gitmodules that have pyproject.toml
FLEXT_PROJECTS := $(shell if [ -f .gitmodules ]; then \
	grep -E 'path = flext-' .gitmodules | \
	sed 's/.*path = //' | \
	while read p; do [ -f "$$p/pyproject.toml" ] && echo "$$p"; done | \
	tr '\n' ' '; \
fi)

# Discover external projects: have pyproject.toml, use flext-core, NOT in .gitmodules
EXTERNAL_PROJECTS := $(shell for dir in */; do \
	name=$${dir%/}; \
	[ -f "$$dir/pyproject.toml" ] || continue; \
	if [ -f .gitmodules ] && grep -q "path = $$name" .gitmodules; then continue; fi; \
	if grep -qE "flext-core|flext_core" "$$dir/pyproject.toml"; then echo "$$name"; fi; \
	done | tr '\n' ' ')

# All Python projects
ALL_PROJECTS := $(FLEXT_PROJECTS) $(EXTERNAL_PROJECTS)

# Project categories (for grouping)
CORE_PROJECTS := $(filter flext-core flext-cli flext-ldif flext-ldap,$(ALL_PROJECTS))
TAP_PROJECTS := $(filter flext-tap-%,$(ALL_PROJECTS))
TARGET_PROJECTS := $(filter flext-target-%,$(ALL_PROJECTS))
DBT_PROJECTS := $(filter flext-dbt-%,$(ALL_PROJECTS))
ORACLE_PROJECTS := $(filter flext-db-oracle flext-oracle-%,$(ALL_PROJECTS))

# =============================================================================
# HELP
# =============================================================================

.PHONY: help
help: ## Show available targets
	$(Q)echo "FLEXT Workspace - Auto-Discovery Makefile"
	$(Q)echo ""
	$(Q)echo "Discovered Projects:"
	$(Q)echo "  FLEXT: $(words $(FLEXT_PROJECTS)) projects"
	$(Q)echo "  External: $(words $(EXTERNAL_PROJECTS)) projects"
	$(Q)echo "  Total: $(words $(ALL_PROJECTS)) Python projects"
	$(Q)echo ""
	$(Q)grep -hE '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'
	$(Q)echo ""
	$(Q)echo "Options: VERBOSE=1, PROJECT=name"

.PHONY: discover
discover: ## Show all discovered projects
	$(Q)echo "=== FLEXT Submodule Projects ($(words $(FLEXT_PROJECTS))) ==="
	$(Q)for p in $(FLEXT_PROJECTS); do echo "  $$p"; done
	$(Q)echo ""
	$(Q)echo "=== External Projects ($(words $(EXTERNAL_PROJECTS))) ==="
	$(Q)for p in $(EXTERNAL_PROJECTS); do echo "  $$p"; done
	$(Q)echo ""
	$(Q)echo "=== Categories ==="
	$(Q)echo "  Core: $(CORE_PROJECTS)"
	$(Q)echo "  Taps: $(TAP_PROJECTS)"
	$(Q)echo "  Targets: $(TARGET_PROJECTS)"
	$(Q)echo "  DBT: $(DBT_PROJECTS)"
	$(Q)echo "  Oracle: $(ORACLE_PROJECTS)"

# =============================================================================
# SETUP & INSTALL
# =============================================================================

.PHONY: install setup

install: setup ## Alias for setup

setup: ## Complete workspace setup (idempotent)
	$(Q)python3.13 --version >/dev/null 2>&1 || { echo "ERROR: Python 3.13 required"; exit 1; }
	$(Q)[ -d ".venv" ] || { echo "🔧 Creating .venv with Python 3.13..."; python3.13 -m venv .venv; }
	$(Q)echo "🔒 Locking dependencies..."
	$(Q)poetry lock
	$(Q)echo "📦 Installing all dependencies via Poetry..."
	$(Q)poetry install --all-extras --all-groups
	$(Q)echo "✅ Setup complete"

# =============================================================================
# QUALITY GATES
# =============================================================================

.PHONY: lint format fix type-check test validate validate-scripts check preflight
.PHONY: quality-report check-clean
.PHONY: validate-fix
.PHONY: upgrade-all deps-all

lint: ## Lint all projects
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) lint
else
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			if $(POETRY_ENV) $(MAKE) -C $$proj lint -s; then \
				echo "✓ $$proj"; \
			else \
				echo "✗ $$proj"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then \
		echo "FAIL: lint ($$failed projects)"; \
		exit 1; \
	fi
endif

format: ## Format all projects
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) format
else
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			if ! $(POETRY_ENV) $(MAKE) -C $$proj format -s; then \
				echo "✗ $$proj"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then \
		echo "FAIL: format ($$failed projects)"; \
		exit 1; \
	fi
	$(Q)echo "Format complete"
endif

fix: ## Auto-fix lint issues
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) fix
else
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			if ! $(POETRY_ENV) $(MAKE) -C $$proj fix -s; then \
				echo "✗ $$proj"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then \
		echo "FAIL: fix ($$failed projects)"; \
		exit 1; \
	fi
	$(Q)echo "Fix complete"
endif

type-check: ## Type-check all projects
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) type-check
else
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			if $(POETRY_ENV) $(MAKE) -C $$proj type-check -s; then \
				echo "✓ $$proj"; \
			else \
				echo "✗ $$proj"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then \
		echo "FAIL: type-check ($$failed projects)"; \
		exit 1; \
	fi
endif

test: ## Test all projects
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) test
else
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			if $(POETRY_ENV) $(MAKE) -C $$proj test -s; then \
				echo "✓ $$proj"; \
			else \
				echo "✗ $$proj"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then \
		echo "FAIL: test ($$failed projects)"; \
		exit 1; \
	fi
endif

check: ## Quick check (lint + type-check)
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) check
else
	$(Q)$(MAKE) lint type-check
endif

validate-scripts: ## Validate scripts/ (ownership, syntax, structure)
	$(Q)echo "=== Scripts Validation (skill-driven) ==="
	$(Q)python scripts/core/skill_validate.py --all --mode strict
	$(Q)echo "=== Scripts Validation Complete ==="

validate: ## Full validation
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) validate
else
	$(Q)$(MAKE) preflight
	$(Q)$(MAKE) lint type-check test validate-scripts
endif

# --- Validate with report artifacts ---
REPORT_DIR := $(CURDIR)/.reports/validate
QUALITY_DIR := $(CURDIR)/.reports/quality
QUALITY_INCLUDE_TEST ?= 0
QUALITY_INCLUDE_SCRIPTS ?= 0

validate-report: ## Validate with machine-readable report artifacts
	$(Q)$(MAKE) preflight
	$(Q)mkdir -p $(REPORT_DIR)/type-check $(REPORT_DIR)/lint
	$(Q)echo '{"projects":[],"gates":[]}' > $(REPORT_DIR)/summary.json
	$(Q)for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			$(POETRY_ENV) $(MAKE) -C $$proj lint -s > $(REPORT_DIR)/lint/$$proj.txt 2>&1 && \
			lint_status="pass" || lint_status="fail"; \
			$(POETRY_ENV) $(MAKE) -C $$proj type-check -s > $(REPORT_DIR)/type-check/$$proj.txt 2>&1 && \
			tc_status="pass" || tc_status="fail"; \
			python3 -c "import json; \
				p='$(REPORT_DIR)/summary.json'; \
				d=json.load(open(p)); \
				d['projects'].append('$$proj'); \
				d['gates'].append({'project':'$$proj','lint':'$$lint_status','type_check':'$$tc_status', \
					'lint_artifact':'$(REPORT_DIR)/lint/$$proj.txt', \
					'type_check_artifact':'$(REPORT_DIR)/type-check/$$proj.txt'}); \
				json.dump(d,open(p,'w'),indent=2)"; \
		fi; \
	done
	$(Q)echo "Report written to $(REPORT_DIR)/summary.json"

quality-report: ## Clean quality report with actionable next steps
	$(Q)$(MAKE) preflight
	$(Q)mkdir -p $(QUALITY_DIR)/lint $(QUALITY_DIR)/type-check $(QUALITY_DIR)/test $(QUALITY_DIR)/scripts
	$(Q)lock_file="$(QUALITY_DIR)/.quality-report.lock"; \
	exec 9>"$$lock_file"; \
	if ! flock -n 9; then \
		echo "ERROR: another quality-report process is running"; \
		exit 3; \
	fi; \
	report="$(QUALITY_DIR)/summary.txt"; \
	echo "FLEXT Clean Quality Report" > "$$report"; \
	echo "Generated: $$(date -Iseconds)" >> "$$report"; \
	echo "" >> "$$report"; \
	echo "Mode:" >> "$$report"; \
	echo "  QUALITY_INCLUDE_TEST=$(QUALITY_INCLUDE_TEST)" >> "$$report"; \
	echo "  QUALITY_INCLUDE_SCRIPTS=$(QUALITY_INCLUDE_SCRIPTS)" >> "$$report"; \
	echo "" >> "$$report"; \
	echo "Per-project status:" >> "$$report"; \
	echo "-------------------" >> "$$report"; \
	total_projects=0; \
	ok_projects=0; \
	failed_projects=0; \
	failed_lint=0; \
	failed_type=0; \
	failed_test=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			total_projects=$$((total_projects + 1)); \
			lint_log="$(QUALITY_DIR)/lint/$$proj.txt"; \
			type_log="$(QUALITY_DIR)/type-check/$$proj.txt"; \
			test_log="$(QUALITY_DIR)/test/$$proj.txt"; \
			echo "[RUN] $$proj"; \
			$(POETRY_ENV) $(MAKE) -C "$$proj" lint -s > "$$lint_log" 2>&1; lint_status=$$?; \
			$(POETRY_ENV) $(MAKE) -C "$$proj" type-check -s > "$$type_log" 2>&1; type_status=$$?; \
			test_status=0; \
			if [ "$(QUALITY_INCLUDE_TEST)" = "1" ]; then \
				$(POETRY_ENV) $(MAKE) -C "$$proj" test -s > "$$test_log" 2>&1; test_status=$$?; \
			fi; \
			if [ $$lint_status -eq 0 ] && [ $$type_status -eq 0 ] && [ $$test_status -eq 0 ]; then \
				ok_projects=$$((ok_projects + 1)); \
				echo "[OK] $$proj" >> "$$report"; \
			else \
				failed_projects=$$((failed_projects + 1)); \
				echo "[FAIL] $$proj" >> "$$report"; \
				if [ $$lint_status -ne 0 ]; then \
					failed_lint=$$((failed_lint + 1)); \
					echo "  - TODO: make PROJECT=$$proj lint" >> "$$report"; \
					echo "    log: $$lint_log" >> "$$report"; \
				fi; \
				if [ $$type_status -ne 0 ]; then \
					failed_type=$$((failed_type + 1)); \
					echo "  - TODO: make PROJECT=$$proj type-check" >> "$$report"; \
					echo "    log: $$type_log" >> "$$report"; \
				fi; \
				if [ $$test_status -ne 0 ]; then \
					failed_test=$$((failed_test + 1)); \
					echo "  - TODO: make PROJECT=$$proj test" >> "$$report"; \
					echo "    log: $$test_log" >> "$$report"; \
				fi; \
			fi; \
		fi; \
	done; \
	scripts_status=0; \
	scripts_log="$(QUALITY_DIR)/scripts/validate-scripts.txt"; \
	if [ "$(QUALITY_INCLUDE_SCRIPTS)" = "1" ]; then \
		$(MAKE) validate-scripts -s > "$$scripts_log" 2>&1; scripts_status=$$?; \
	fi; \
	echo "" >> "$$report"; \
	echo "Global scripts validation:" >> "$$report"; \
	if [ "$(QUALITY_INCLUDE_SCRIPTS)" != "1" ]; then \
		echo "[SKIP] validate-scripts (set QUALITY_INCLUDE_SCRIPTS=1 to enable)" >> "$$report"; \
	elif [ $$scripts_status -eq 0 ]; then \
		echo "[OK] validate-scripts" >> "$$report"; \
	else \
		echo "[FAIL] validate-scripts" >> "$$report"; \
		echo "  - TODO: make validate-scripts" >> "$$report"; \
		echo "    log: $$scripts_log" >> "$$report"; \
	fi; \
	echo "" >> "$$report"; \
	echo "Summary:" >> "$$report"; \
	echo "  projects_total=$$total_projects" >> "$$report"; \
	echo "  projects_ok=$$ok_projects" >> "$$report"; \
	echo "  projects_failed=$$failed_projects" >> "$$report"; \
	echo "  lint_failed=$$failed_lint" >> "$$report"; \
	echo "  type_check_failed=$$failed_type" >> "$$report"; \
	echo "  test_failed=$$failed_test" >> "$$report"; \
	if [ "$(QUALITY_INCLUDE_SCRIPTS)" = "1" ] && [ $$scripts_status -ne 0 ]; then scripts_failed=1; else scripts_failed=0; fi; \
	echo "  scripts_failed=$$scripts_failed" >> "$$report"; \
	echo ""; \
	cat "$$report"; \
	echo ""; \
	echo "Quality report written to $(QUALITY_DIR)/summary.txt"; \
	if [ $$failed_projects -ne 0 ] || [ $$scripts_failed -ne 0 ]; then \
		exit 1; \
	fi

check-clean: quality-report ## Run clean report and fail on issues

# --- Validate-Fix: check + auto-fix + re-check (non-degrading, transactional) ---
validate-fix: ## Full validation with automatic fixes
	$(Q)$(MAKE) preflight
	$(Q)echo "=== FLEXT Validate-Fix Pipeline ==="
	$(Q)echo "Step 1/6: Baseline snapshot..."
	$(Q)$(MAKE) validate-report
	$(Q)rm -rf $(REPORT_DIR).baseline
	$(Q)cp -r $(REPORT_DIR) $(REPORT_DIR).baseline
	$(Q)echo "Step 2/6: Ruff auto-fix..."
	$(Q)$(MAKE) fix
	$(Q)echo "Step 3/6: Skill-driven auto-fix (ast-grep)..."
	$(Q)python scripts/core/skill_fix.py --all --apply
	$(Q)echo "Step 4/6: Typing stub supply chain..."
	$(Q)python scripts/core/stub_supply_chain.py --all --apply --idempotency-check
	$(Q)echo "Step 5/6: Pyrefly infer (annotation backfill)..."
	$(Q)failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			if ! $(POETRY_ENV) $(MAKE) -C $$proj pyrefly-infer -s; then \
				echo "✗ $$proj"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then \
		echo "FAIL: pyrefly-infer ($$failed projects)"; \
		exit 1; \
	fi
	$(Q)echo "Step 6/6: Format + re-validate..."
	$(Q)$(MAKE) format
	$(Q)$(MAKE) validate-report
	$(Q)echo "=== Validate-Fix Complete ==="
	$(Q)echo "Reports: $(REPORT_DIR)/summary.json"
	$(Q)if [ -d "$(REPORT_DIR).baseline" ]; then \
		echo "Baseline: $(REPORT_DIR).baseline/summary.json"; \
	fi

# =============================================================================
# DEPENDENCY UPGRADE
# =============================================================================

upgrade-all: ## Upgrade dependencies for all projects
	$(Q)$(MAKE) preflight
	$(Q)echo "=== Upgrading all $(words $(ALL_PROJECTS)) projects ===" && \
	upgraded=0; failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			printf "  [%2d/$(words $(ALL_PROJECTS))] %-25s ... " $$((upgraded + failed + 1)) "$$proj"; \
			if $(MAKE) -C $$proj upgrade -s 2>&1 | grep -q "ERROR\|FAIL"; then \
				echo "✗ FAILED"; \
				failed=$$((failed + 1)); \
			else \
				echo "✓"; \
				upgraded=$$((upgraded + 1)); \
			fi; \
		fi; \
	done; \
	echo ""; \
	echo "=== Upgrade Summary ==="; \
	echo "  Total:    $(words $(ALL_PROJECTS)) projects"; \
	echo "  Upgraded: $$upgraded"; \
	echo "  Failed:   $$failed"; \
	echo ""; \
	if [ $$failed -eq 0 ]; then \
		echo "✅ All projects upgraded successfully"; \
	else \
		echo "⚠️  $$failed projects failed - review output above"; \
		exit 1; \
	fi

# =============================================================================
# DEPENDENCY ANALYSIS
# =============================================================================

deps-all: ## Analyze dependencies for all projects with deptry
	$(Q)$(MAKE) preflight
	$(Q)echo "=== Analyzing dependencies in $(words $(ALL_PROJECTS)) projects ===" && \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			printf "  %-25s " "$$proj"; \
			$(MAKE) -C $$proj deps -s 2>&1 | tail -1; \
		fi; \
	done

# =============================================================================
# PROJECT GROUPS
# =============================================================================

.PHONY: core taps targets dbt oracle external

core: ## Validate core projects
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(CORE_PROJECTS); do \
		if $(POETRY_ENV) $(MAKE) -C $$proj validate -s; then echo "✓ $$proj"; else echo "✗ $$proj"; failed=$$((failed + 1)); fi; \
	done; \
	if [ $$failed -ne 0 ]; then echo "FAIL: core ($$failed projects)"; exit 1; fi

taps: ## Validate tap projects
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(TAP_PROJECTS); do \
		if $(POETRY_ENV) $(MAKE) -C $$proj validate -s; then echo "✓ $$proj"; else echo "✗ $$proj"; failed=$$((failed + 1)); fi; \
	done; \
	if [ $$failed -ne 0 ]; then echo "FAIL: taps ($$failed projects)"; exit 1; fi

targets: ## Validate target projects
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(TARGET_PROJECTS); do \
		if $(POETRY_ENV) $(MAKE) -C $$proj validate -s; then echo "✓ $$proj"; else echo "✗ $$proj"; failed=$$((failed + 1)); fi; \
	done; \
	if [ $$failed -ne 0 ]; then echo "FAIL: targets ($$failed projects)"; exit 1; fi

dbt: ## Validate dbt projects
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(DBT_PROJECTS); do \
		if $(POETRY_ENV) $(MAKE) -C $$proj validate -s; then echo "✓ $$proj"; else echo "✗ $$proj"; failed=$$((failed + 1)); fi; \
	done; \
	if [ $$failed -ne 0 ]; then echo "FAIL: dbt ($$failed projects)"; exit 1; fi

oracle: ## Validate Oracle projects
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(ORACLE_PROJECTS); do \
		if $(POETRY_ENV) $(MAKE) -C $$proj validate -s; then echo "✓ $$proj"; else echo "✗ $$proj"; failed=$$((failed + 1)); fi; \
	done; \
	if [ $$failed -ne 0 ]; then echo "FAIL: oracle ($$failed projects)"; exit 1; fi

external: ## Validate external projects
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(EXTERNAL_PROJECTS); do \
		if $(POETRY_ENV) $(MAKE) -C $$proj validate -s; then echo "✓ $$proj"; else echo "✗ $$proj"; failed=$$((failed + 1)); fi; \
	done; \
	if [ $$failed -ne 0 ]; then echo "FAIL: external ($$failed projects)"; exit 1; fi

# =============================================================================
# CLEANUP
# =============================================================================

.PHONY: clean clean-all

clean: ## Clean build artifacts
ifdef PROJECT
	$(Q)$(POETRY_ENV) $(MAKE) -C $(PROJECT) clean
else
	$(Q)$(MAKE) preflight
	$(Q)failed=0; \
	for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			if ! $(POETRY_ENV) $(MAKE) -C $$proj clean -s; then \
				echo "✗ $$proj"; \
				failed=$$((failed + 1)); \
			fi; \
		fi; \
	done; \
	if [ $$failed -ne 0 ]; then \
		echo "FAIL: clean ($$failed projects)"; \
		exit 1; \
	fi
endif
	$(Q)rm -rf .pytest_cache/ htmlcov/ .coverage* .mypy_cache/ .ruff_cache/

preflight: ## Enforce workspace preconditions before loops
	$(Q)if [ ! -d "$(WORKSPACE_VENV)" ]; then \
		echo "ERROR: workspace venv not found at $(WORKSPACE_VENV). Run 'make setup'."; \
		exit 1; \
	fi
	$(Q)local_venvs=$$(for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj/.venv" ]; then echo "$$proj/.venv"; fi; \
	done); \
	if [ -n "$$local_venvs" ]; then \
		echo "ERROR: project-local .venv directories detected (must use workspace .venv):"; \
		printf '%s\n' "$$local_venvs"; \
		echo "Run: for p in $(ALL_PROJECTS); do rm -rf \"\$$p/.venv\"; done"; \
		exit 1; \
	fi

clean-all: clean ## Deep clean
	$(Q)find . -maxdepth 2 -type d -name __pycache__ -exec rm -rf {} +
	$(Q)find . -maxdepth 2 -type d -name .pytest_cache -exec rm -rf {} +
	$(Q)find . -maxdepth 2 -type d -name "*.egg-info" -exec rm -rf {} +

# =============================================================================
# STATUS
# =============================================================================

.PHONY: status

status: ## Show project status
	$(Q)echo "=== FLEXT Projects ($(words $(FLEXT_PROJECTS))) ==="
	$(Q)for proj in $(FLEXT_PROJECTS); do \
		if [ -f "$$proj/Makefile" ] && grep -q "base.mk" "$$proj/Makefile"; then \
			echo "  ✓ $$proj (base.mk)"; \
		else \
			echo "  ○ $$proj"; \
		fi; \
	done
	$(Q)echo ""
	$(Q)echo "=== External Projects ($(words $(EXTERNAL_PROJECTS))) ==="
	$(Q)for proj in $(EXTERNAL_PROJECTS); do \
		if [ -f "$$proj/Makefile" ] && grep -q "base.mk" "$$proj/Makefile"; then \
			echo "  ✓ $$proj (base.mk)"; \
		else \
			echo "  ○ $$proj"; \
		fi; \
	done

# =============================================================================
# MONOREPO MANAGEMENT
# =============================================================================

.PHONY: add-project remove-project deploy release commit

add-project: ## Adicionar projeto externo (datacosmos-br, etc.)
	$(Q)bash scripts/add-project.sh

remove-project: ## Remover projeto externo (uso: make remove-project PROJECT=nome)
ifdef PROJECT
	$(Q)bash scripts/remove-project.sh $(PROJECT)
else
	$(Q)echo "Uso: make remove-project PROJECT=nome-do-projeto"
	$(Q)echo ""
	$(Q)echo "Projetos externos registrados:"
	$(Q)if [ -f .flext/external-projects.json ]; then \
		jq -r '.projects | keys[]' .flext/external-projects.json; \
	else \
		echo "  (nenhum)"; \
	fi
endif

deploy: ## Deploy pipeline com validacao
	$(Q)bash scripts/deploy.sh

release: ## Release automatizado com bump de versao
	$(Q)bash scripts/release.sh

commit: ## Commit inteligente (conventional commits)
	$(Q)bash scripts/commit.sh

# =============================================================================
# SHORT ALIASES
# =============================================================================

.PHONY: l f tc t c v vf vr vs qr qc d s dp ap rp si

l: lint
f: format
tc: type-check
t: test
c: check
v: validate
vf: validate-fix
vr: validate-report
vs: validate-scripts
qr: quality-report
qc: check-clean
d: discover
s: status
dp: deps-all
ap: add-project
rp: remove-project
si: setup-interactive
