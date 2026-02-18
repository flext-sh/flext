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

# === SILENT MODE ===
Q := @
ifdef VERBOSE
Q :=
endif

# =============================================================================
# AUTO-DISCOVERY
# =============================================================================

# Discover flext-* submodules from .gitmodules that have pyproject.toml
FLEXT_PROJECTS := $(shell grep -E 'path = flext-' .gitmodules 2>/dev/null | \
	sed 's/.*path = //' | \
	while read p; do [ -f "$$p/pyproject.toml" ] && echo "$$p"; done | \
	tr '\n' ' ')

# Discover external projects: have pyproject.toml, use flext-core, NOT in .gitmodules
EXTERNAL_PROJECTS := $(shell for dir in */; do \
	name=$${dir%/}; \
	[ -f "$$dir/pyproject.toml" ] || continue; \
	grep -q "path = $$name" .gitmodules 2>/dev/null && continue; \
	grep -qE "flext-core|flext_core" "$$dir/pyproject.toml" 2>/dev/null && echo "$$name"; \
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

.PHONY: lint format fix type-check test validate validate-scripts check
.PHONY: validate-fix
.PHONY: upgrade-all deps-all

lint: ## Lint all projects
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) lint
else
	$(Q)for proj in $(ALL_PROJECTS); do \
		[ -d "$$proj" ] && $(MAKE) -C $$proj lint -s 2>/dev/null && \
		echo "✓ $$proj" || echo "✗ $$proj"; \
	done
endif

format: ## Format all projects
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) format
else
	$(Q)for proj in $(ALL_PROJECTS); do \
		[ -d "$$proj" ] && $(MAKE) -C $$proj format -s 2>/dev/null || true; \
	done
	$(Q)echo "Format complete"
endif

fix: ## Auto-fix lint issues
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) fix
else
	$(Q)for proj in $(ALL_PROJECTS); do \
		[ -d "$$proj" ] && $(MAKE) -C $$proj fix -s 2>/dev/null || true; \
	done
	$(Q)echo "Fix complete"
endif

type-check: ## Type-check all projects
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) type-check
else
	$(Q)for proj in $(ALL_PROJECTS); do \
		[ -d "$$proj" ] && $(MAKE) -C $$proj type-check -s 2>/dev/null && \
		echo "✓ $$proj" || echo "✗ $$proj"; \
	done
endif

test: ## Test all projects
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) test
else
	$(Q)for proj in $(ALL_PROJECTS); do \
		[ -d "$$proj" ] && $(MAKE) -C $$proj test -s 2>/dev/null && \
		echo "✓ $$proj" || echo "✗ $$proj"; \
	done
endif

check: ## Quick check (lint + type-check)
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) check
else
	$(Q)$(MAKE) lint type-check
endif

validate-scripts: ## Validate scripts/ (ownership, syntax, structure)
	$(Q)echo "=== Scripts Validation (skill-driven) ==="
	$(Q)python scripts/core/skill_validate.py --all || true
	$(Q)echo "=== Scripts Validation Complete ==="

validate: ## Full validation
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) validate
else
	$(Q)$(MAKE) lint type-check test validate-scripts
endif

# --- Validate with report artifacts ---
REPORT_DIR := $(CURDIR)/.reports/validate

validate-report: ## Validate with machine-readable report artifacts
	$(Q)mkdir -p $(REPORT_DIR)/type-check $(REPORT_DIR)/lint
	$(Q)echo '{"projects":[],"gates":[]}' > $(REPORT_DIR)/summary.json
	$(Q)for proj in $(ALL_PROJECTS); do \
		if [ -d "$$proj" ]; then \
			$(MAKE) -C $$proj lint -s 2>&1 > $(REPORT_DIR)/lint/$$proj.txt && \
			lint_status="pass" || lint_status="fail"; \
			$(MAKE) -C $$proj type-check -s 2>&1 > $(REPORT_DIR)/type-check/$$proj.txt && \
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

# --- Validate-Fix: check + auto-fix + re-check (non-degrading, transactional) ---
validate-fix: ## Full validation with automatic fixes
	$(Q)echo "=== FLEXT Validate-Fix Pipeline ==="
	$(Q)echo "Step 1/6: Baseline snapshot..."
	$(Q)$(MAKE) validate-report
	$(Q)cp -r $(REPORT_DIR) $(REPORT_DIR).baseline 2>/dev/null || true
	$(Q)echo "Step 2/6: Ruff auto-fix..."
	$(Q)$(MAKE) fix
	$(Q)echo "Step 3/6: Skill-driven auto-fix (ast-grep)..."
	$(Q)python scripts/core/skill_fix.py --all --apply 2>/dev/null || echo "WARN: skill_fix.py returned non-zero"
	$(Q)echo "Step 4/6: Typing stub supply chain..."
	$(Q)if [ "$${STUB_SUPPLY_CHAIN:-1}" = "1" ] && [ -f scripts/core/stub_supply_chain.py ]; then \
		python scripts/core/stub_supply_chain.py --all --apply 2>/dev/null || echo "WARN: stub supply chain returned non-zero"; \
	fi
	$(Q)echo "Step 5/6: Pyrefly infer (annotation backfill)..."
	$(Q)if [ "$${PYREFLY_INFER:-1}" = "1" ]; then \
		for proj in $(ALL_PROJECTS); do \
			if [ -d "$$proj" ]; then \
				$(MAKE) -C $$proj pyrefly-infer -s 2>/dev/null || true; \
			fi; \
		done; \
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
	$(Q)for proj in $(CORE_PROJECTS); do \
		$(MAKE) -C $$proj validate -s 2>/dev/null && echo "✓ $$proj" || echo "✗ $$proj"; \
	done

taps: ## Validate tap projects
	$(Q)for proj in $(TAP_PROJECTS); do \
		$(MAKE) -C $$proj validate -s 2>/dev/null && echo "✓ $$proj" || echo "✗ $$proj"; \
	done

targets: ## Validate target projects
	$(Q)for proj in $(TARGET_PROJECTS); do \
		$(MAKE) -C $$proj validate -s 2>/dev/null && echo "✓ $$proj" || echo "✗ $$proj"; \
	done

dbt: ## Validate dbt projects
	$(Q)for proj in $(DBT_PROJECTS); do \
		$(MAKE) -C $$proj validate -s 2>/dev/null && echo "✓ $$proj" || echo "✗ $$proj"; \
	done

oracle: ## Validate Oracle projects
	$(Q)for proj in $(ORACLE_PROJECTS); do \
		$(MAKE) -C $$proj validate -s 2>/dev/null && echo "✓ $$proj" || echo "✗ $$proj"; \
	done

external: ## Validate external projects
	$(Q)for proj in $(EXTERNAL_PROJECTS); do \
		$(MAKE) -C $$proj validate -s 2>/dev/null && echo "✓ $$proj" || echo "✗ $$proj"; \
	done

# =============================================================================
# CLEANUP
# =============================================================================

.PHONY: clean clean-all

clean: ## Clean build artifacts
ifdef PROJECT
	$(Q)$(MAKE) -C $(PROJECT) clean
else
	$(Q)for proj in $(ALL_PROJECTS); do \
		[ -d "$$proj" ] && $(MAKE) -C $$proj clean -s 2>/dev/null || true; \
	done
endif
	$(Q)rm -rf .pytest_cache/ htmlcov/ .coverage* .mypy_cache/ .ruff_cache/

clean-all: clean ## Deep clean
	$(Q)find . -maxdepth 2 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	$(Q)find . -maxdepth 2 -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	$(Q)find . -maxdepth 2 -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# =============================================================================
# STATUS
# =============================================================================

.PHONY: status

status: ## Show project status
	$(Q)echo "=== FLEXT Projects ($(words $(FLEXT_PROJECTS))) ==="
	$(Q)for proj in $(FLEXT_PROJECTS); do \
		[ -f "$$proj/Makefile" ] && grep -q "base.mk" "$$proj/Makefile" && \
		echo "  ✓ $$proj (base.mk)" || echo "  ○ $$proj"; \
	done
	$(Q)echo ""
	$(Q)echo "=== External Projects ($(words $(EXTERNAL_PROJECTS))) ==="
	$(Q)for proj in $(EXTERNAL_PROJECTS); do \
		[ -f "$$proj/Makefile" ] && grep -q "base.mk" "$$proj/Makefile" && \
		echo "  ✓ $$proj (base.mk)" || echo "  ○ $$proj"; \
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
	$(Q)jq -r '.projects | keys[]' .flext/external-projects.json 2>/dev/null || echo "  (nenhum)"
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

# Update VSCode settings to exclude files not tracked by git
vscode-update:
	@echo "🔧 Updating VSCode settings for git exclusions..."
	@python scripts/update_vscode_git_exclusions.py
	@echo "✅ VSCode settings updated. Restart VSCode to apply changes."

.PHONY: l f tc t c v vf vr d s dp ap rp si vscode-update

l: lint
f: format
tc: type-check
t: test
c: check
v: validate
vf: validate-fix
vr: validate-report
vs: validate-scripts
d: discover
s: status
dp: deps-all
ap: add-project
rp: remove-project
si: setup-interactive
