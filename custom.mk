# Workspace-specific custom targets (never overwritten by sync).
#
# done-check — AGENTS.md §0 R12 / §13 Production-Readiness & Real-User QA.
# Invoked by the Stop hook (~/.agents/hooks/quality-gate.sh, 90s timeout). It must
# be FAST and SCOPED TO THIS SESSION'S COMMITTED WORK — never a whole-workspace or
# fleet gate (§13.4: scope of claim = scope of evidence). It verifies only the
# Python files this branch committed ahead of its upstream (origin/<branch>), so
# other lanes' uncommitted/untracked changes never pollute or brick it. Green when
# nothing is committed-ahead.

# SSOT for the workspace base branch. All equalization/merge targets use this.
WORKSPACE_BASE ?= 0.12.0-dev

.PHONY: done-check workspace-docs-audit full-check workspace-status \
        workspace-sync-base workspace-land-submodules dependabot-merge \
        workspace-merge-main workspace-main-sync workspace-dependabot-apply \
        workspace-check-changed workspace-fix-changed hooks post-boot

done-check: ## Real-user/green-green check, scoped to committed changes vs upstream
	$(Q)base=$$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo origin/main); \
	files=$$(git diff --name-only --diff-filter=d "$$base"...HEAD -- '*.py') || { echo "ERROR: git diff against $$base failed" >&2; exit 1; }; \
	if [ -z "$$files" ]; then \
		echo "done-check: no committed .py changes vs $$base — green/green"; \
		exit 0; \
	fi; \
	n=$$(printf '%s\n' "$$files" | grep -c .); \
	echo "done-check: ruff on $$n committed-vs-$$base .py file(s)"; \
	printf '%s\n' "$$files" | xargs -r ruff check --quiet

hooks: ## Install Beads git hooks + FLEXT agent-trailer guard (workspace root)
	$(Q)if [ "$${CI:-}" = "true" ]; then \
		echo "hooks: skipped in CI (no local commit hooks are needed)"; \
	else \
		bash .github/scripts/install-git-hooks.sh; \
	fi

# Auto-provision git hooks after every `make boot` (verb-hook seam).
post-boot: hooks ## Post-boot: ensure git hooks + agent-trailer guard are installed

workspace-docs-audit: ## Markdown lint for workspace docs
	$(Q)md_files=$$(find docs/ -type f -name '*.md' 2>/dev/null | sort); \
	if [ -z "$$md_files" ]; then \
		echo "workspace-docs-audit: no .md files in docs/ — green"; \
		exit 0; \
	fi; \
	md_config=""; \
	if [ -f ".markdownlint.json" ]; then md_config="--config .markdownlint.json"; fi; \
	printf '%s\n' "$$md_files" | xargs -r markdownlint $$md_config

full-check: ## Run canonical full check path with explicit timeout
	$(Q)timeout_s=$${FULL_CHECK_TIMEOUT:-1200}; \
	if ! command -v timeout >/dev/null 2>&1; then \
		echo "WARN: timeout utility unavailable; running without timeout"; \
		$(MAKE) --no-print-directory check WHAT=all $(MAKE_SELECTION_ARGS); \
		code=$$?; \
		exit $$code; \
	else \
		timeout "$$timeout_s"s $(MAKE) --no-print-directory check WHAT=all $(MAKE_SELECTION_ARGS); \
		code=$$?; \
		if [ "$$code" -eq 124 ]; then \
			echo "ERRO: full-check atingiu o timeout de $$timeout_s s"; \
			exit $$code; \
		fi; \
		exit $$code; \
	fi

# Internal helpers -----------------------------------------------------------

# Standardized commit message schema for workspace automation.
# All generated messages include a unique counter and a command tag to avoid
# repetition and to keep Beads/git history auditable.
WORKSPACE_COMMIT_COUNTER_FILE := .workspace-commit-counter

define workspace_next_counter
$(shell mkdir -p .workspace-state && (cat .workspace-state/commit-counter 2>/dev/null || echo 0) | awk '{printf "%04d", $$1+1}' > .workspace-state/commit-counter.tmp && mv .workspace-state/commit-counter.tmp .workspace-state/commit-counter && cat .workspace-state/commit-counter)
endef

# $(1)=verb (chore|merge|sync|land), $(2)=scope, $(3)=short summary, $(4)=command
workspace_commit_message = \
	$(1)(workspace): $(2) — $(3)\n\n\
	Counter: $(call workspace_next_counter)\n\
	Base: $(WORKSPACE_BASE)\n\
	Command: $(4)\n\
	Evidence: make $(4)

# Abort if a submodule has unstaged/uncommitted changes.
# Callers must pass the submodule path in $(1).
workspace_require_clean = \
	if ! git -C "$(1)" diff --quiet; then \
		echo "ERROR: $(1) has unstaged changes; commit or stash before $(2)"; \
		exit 1; \
	fi; \
	if ! git -C "$(1)" diff --cached --quiet; then \
		echo "ERROR: $(1) has staged but uncommitted changes; commit before $(2)"; \
		exit 1; \
	fi

workspace-status: ## Show workspace/submodule branch and dirty state
	$(Q)echo "workspace base: $(WORKSPACE_BASE)"; \
	echo "root branch:    $$(git rev-parse --abbrev-ref HEAD)"; \
	echo "root dirty:     $$(git diff --quiet && git diff --cached --quiet && echo clean || echo DIRTY)"; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ]; then \
			branch=$$(git -C "$$path" rev-parse --abbrev-ref HEAD); \
			dirty=$$(git -C "$$path" diff --quiet && git -C "$$path" diff --cached --quiet && echo clean || echo DIRTY); \
			ahead=$$(git -C "$$path" log --oneline origin/main..HEAD 2>/dev/null | wc -l); \
			printf "  %-36s %-20s ahead=%-4s %s\n" "$$path" "$$branch" "$$ahead" "$$dirty"; \
		fi; \
	done

# Helper: list FLEXT projects touched in the working tree (staged or unstaged).
# Returns a space-separated list of top-level project directory names.
workspace_changed_projects = \
	( git diff --name-only; \
	  git diff --cached --name-only; \
	  git submodule foreach --quiet 'if [ -n "$$(git status --porcelain)" ]; then echo $$name; fi' ) | \
	cut -d/ -f1 | \
	sort -u | \
	while read -r proj; do \
		[ -f "$$proj/pyproject.toml" ] && echo "$$proj"; \
	done

workspace-check-changed: ## Run `make check` only on projects with working-tree changes
	$(Q)projects=$$($(workspace_changed_projects)); \
	if [ -z "$$projects" ]; then \
		echo "workspace-check-changed: no FLEXT projects changed — green"; \
		exit 0; \
	fi; \
	echo "workspace-check-changed: checking $$projects"; \
	failed=0; \
	for proj in $$projects; do \
		( cd "$$proj" && $(MAKE) --no-print-directory check PROJECT="$$proj" ) || \
		{ echo "ERROR: check failed for $$proj"; failed=1; }; \
	done; \
	exit $$failed

workspace-fix-changed: ## Auto-fix ruff + enforcement issues on changed projects
	$(Q)projects=$$($(workspace_changed_projects)); \
	if [ -z "$$projects" ]; then \
		echo "workspace-fix-changed: no FLEXT projects changed — green"; \
		exit 0; \
	fi; \
	echo "workspace-fix-changed: fixing $$projects"; \
	failed=0; \
	for proj in $$projects; do \
		echo "  fixing $$proj"; \
		( cd "$$proj" && \
		  files=$$(git diff --name-only -- '*.py' && git diff --cached --name-only -- '*.py' | sort -u) && \
		  if [ -n "$$files" ]; then \
			  printf '%s\n' "$$files" | xargs -r ruff format && \
			  printf '%s\n' "$$files" | xargs -r ruff check --fix; \
		  fi ) || \
		{ echo "ERROR: ruff fix failed for $$proj"; failed=1; continue; }; \
		( cd "$$proj" && \
		  $(MAKE) --no-print-directory fix-enforcement APPLY=1 PROJECTS="$$proj" ) || \
		{ echo "WARN: enforcement fix left unresolved issues in $$proj (see above)"; }; \
	done; \
	exit $$failed

workspace-sync-base: ## Equalize all submodules to origin/$(WORKSPACE_BASE)
	$(Q)base="$(WORKSPACE_BASE)"; \
	echo "workspace-sync-base: equalizing submodules to origin/$$base"; \
	failed=0; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ]; then \
			$(call workspace_require_clean,$$path,workspace-sync-base) || { failed=1; continue; }; \
			( cd "$$path" && \
			  git fetch origin "$$base" >/dev/null 2>&1 && \
			  git checkout "$$base" >/dev/null 2>&1 && \
			  git merge --ff-only "origin/$$base" >/dev/null 2>&1 ) || \
			{ echo "ERROR: failed to equalize $$path"; failed=1; continue; }; \
			echo "  $$path -> $$(cd "$$path" && git rev-parse --short HEAD)"; \
		fi; \
	done; \
	git add $(MANAGED_PROJECTS) || { echo "ERROR: git add failed for $(MANAGED_PROJECTS)" >&2; exit 1; }; \
	if ! git diff --cached --quiet; then \
		msg=$$(printf '%s' "$(call workspace_commit_message,chore,equalize submodules,origin/$$base,workspace-sync-base)"); \
		git commit -m "$$msg"; \
		echo "workspace-sync-base: committed submodule pointer update"; \
	else \
		echo "workspace-sync-base: pointers already at origin/$$base"; \
	fi; \
	exit $$failed

workspace-land-submodules: ## Commit and push dirty submodules, then update root pointers
	$(Q)base="$(WORKSPACE_BASE)"; \
	echo "workspace-land-submodules: landing dirty submodules on $$base"; \
	failed=0; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ] && ! (git -C "$$path" diff --quiet && git -C "$$path" diff --cached --quiet); then \
			( cd "$$path" && \
			  files=$$(git diff --name-only && git diff --cached --name-only | sort -u) && \
			  if [ -z "$$files" ]; then echo "  $$path: nothing to land"; exit 0; fi && \
			  printf '%s\n' "$$files" | xargs -r ruff check --quiet && \
			  git add -A && \
			  msg=$$(printf '%s' "$(call workspace_commit_message,chore,$$path,land local changes,workspace-land-submodules)") && \
			  git commit -m "$$msg" && \
			  git push origin "$$base" ) || \
			{ echo "ERROR: failed to land $$path"; failed=1; continue; }; \
			echo "  landed $$path"; \
		fi; \
	done; \
	$(MAKE) --no-print-directory workspace-sync-base; \
	exit $$failed

dependabot-merge: ## Merge open dependabot PRs into main (DRY_RUN=1 to preview)
	$(Q)$(PY) scripts/workspace/dependabot_merge.py $(if $(DRY_RUN),--dry-run,) --base main

workspace-merge-main: ## Merge $(WORKSPACE_BASE) into main for every submodule and root
	$(Q)base="$(WORKSPACE_BASE)"; \
	echo "workspace-merge-main: merging origin/$$base into main"; \
	failed=0; \
	$(call workspace_require_clean,.,workspace-merge-main) || exit 1; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ]; then \
			$(call workspace_require_clean,$$path,workspace-merge-main) || { failed=1; continue; }; \
			( cd "$$path" && \
			  git fetch origin main >/dev/null 2>&1 && \
			  git fetch origin "$$base" >/dev/null 2>&1 && \
			  git checkout main >/dev/null 2>&1 && \
			  git merge --no-ff "origin/$$base" -m "$$(printf '%s' "$(call workspace_commit_message,merge,$$path,merge $$base into main,workspace-merge-main)")" && \
			  $(if $(DRY_RUN),echo "[dry-run] would push $$path main",git push origin main) ) || \
			{ echo "ERROR: failed to merge $$path"; failed=1; continue; }; \
			echo "  $$path main -> $$(cd "$$path" && git rev-parse --short HEAD)"; \
		fi; \
	done; \
	$(MAKE) --no-print-directory workspace-sync-base; \
	git fetch origin main >/dev/null 2>&1; \
	git checkout main >/dev/null 2>&1 || { echo "ERROR: cannot checkout main in root; refusing to merge into the wrong branch" >&2; exit 1; }; \
	git merge --no-ff "origin/$$base" -m "$$(printf '%s' "$(call workspace_commit_message,merge,root,merge $$base into main,workspace-merge-main)")" || { echo "ERROR: failed to merge root"; failed=1; }; \
	$(if $(DRY_RUN),echo "[dry-run] would push root main",git push origin main); \
	exit $$failed

workspace-main-sync: ## Pull origin/main into $(WORKSPACE_BASE) to absorb released updates
	$(Q)base="$(WORKSPACE_BASE)"; \
	echo "workspace-main-sync: fast-forward $$base to include origin/main"; \
	failed=0; \
	$(call workspace_require_clean,.,workspace-main-sync) || exit 1; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ]; then \
			$(call workspace_require_clean,$$path,workspace-main-sync) || { failed=1; continue; }; \
			( cd "$$path" && \
			  git fetch origin main >/dev/null 2>&1 && \
			  git checkout "$$base" >/dev/null 2>&1 && \
			  git merge --ff-only origin/main >/dev/null 2>&1 ) || \
			{ echo "ERROR: failed to sync $$path"; failed=1; continue; }; \
			echo "  $$path $$base -> $$(cd "$$path" && git rev-parse --short HEAD)"; \
		fi; \
	done; \
	$(MAKE) --no-print-directory workspace-sync-base; \
	git fetch origin main >/dev/null 2>&1; \
	git checkout "$$base" >/dev/null 2>&1 || { echo "ERROR: cannot checkout $$base in root; refusing to sync into the wrong branch" >&2; exit 1; }; \
	git merge --ff-only origin/main >/dev/null 2>&1 || { echo "ERROR: failed to sync root"; failed=1; }; \
	git push origin "$$base"; \
	exit $$failed

workspace-dependabot-apply: ## dependabot-merge + merge result into main
	$(Q)$(MAKE) --no-print-directory dependabot-merge && \
	$(MAKE) --no-print-directory workspace-merge-main

# =============================================================================
# ast-grep codemod library ([root]/codemod)
# =============================================================================
# ONE verb drives large-scale, mechanical refactors so corrections are never
# hand-applied file by file:
#   make codemod              DETECT (default): scan scope read-only, print fixes.
#   make codemod TEST=1       VALIDATE: run every rule against its test cases.
#   make codemod APPLY=Y      APPLY: rewrite scope in declared order.
#   make codemod RULE=<id>    Restrict to ONE rule ($(CODEMOD_HOME)/rules/**/<id>.{yml,csv}).
#   make codemod SCOPE=<dir>  Restrict to one project instead of the workspace.
#
# SCOPE is derived from the workspace manifest SSOT (WORKSPACE_MEMBERS) plus any
# sibling that declares `[tool.flext.workspace] attached = true` in its own
# pyproject. No consumer directory is ever named here: the engine stays generic.
# The codemod library is OWNED BY flext-infra (the tooling engine), never by
# the workspace root. The root only dispatches the verb into that owner.
# The library lives INSIDE the flext-infra package (src/flext_infra/codemod)
# so it travels in the wheel and an external consumer installing
# flext-infra from git resolves the same rules the workspace uses.
.PHONY: codemod

CODEMOD_HOME := flext-infra/src/flext_infra/codemod
CODEMOD_SGCONFIG := $(CODEMOD_HOME)/sgconfig.yml
# Sibling workspaces join the scope only by declaring themselves attached, via
# the same canonical discovery the engine uses (no directory name is hardcoded).
define CODEMOD_ATTACHED_PY
import pathlib, sys
try:
    from flext_infra import u
except ImportError:
    sys.exit(0)
roots = u.Infra.discover_external_workspace_roots(pathlib.Path.cwd())
print(" ".join(str(root) for root in roots))
endef
export CODEMOD_ATTACHED_PY
# Lazy `=` on purpose: `:=` is expanded while GNU Make PARSES the file, so an
# interpreter here is started by every invocation (`make help` included) and
# once more per sub-make the verb dispatcher spawns for hook probing. Deferring
# the expansion keeps the discovery identical but charges it only to the codemod
# recipe that actually reads these variables.
CODEMOD_ATTACHED = $(shell $(UV_RUN) python -c "$$CODEMOD_ATTACHED_PY" 2>/dev/null)
CODEMOD_SCOPE = $(if $(filter-out project all,$(SCOPE)),$(filter-out project all,$(SCOPE)),. $(WORKSPACE_MEMBERS) $(CODEMOD_ATTACHED))
CODEMOD_TARGETS = $(foreach d,$(CODEMOD_SCOPE),$(wildcard $(d)/src) $(wildcard $(d)/tests) $(wildcard $(d)/examples) $(wildcard $(d)/scripts))
CODEMOD_CSV := $(if $(RULE),$(firstword $(wildcard $(CODEMOD_HOME)/rules/*/$(RULE).csv $(CODEMOD_HOME)/rules/$(RULE).csv)),)
CODEMOD_CSV_RUNNER := $(CODEMOD_HOME)/rules/refactor/apply_renames.py
CODEMOD_RULEFILE := $(if $(RULE),$(firstword $(wildcard $(CODEMOD_HOME)/rules/*/$(RULE).yml $(CODEMOD_HOME)/rules/$(RULE).yml)),)
CODEMOD_RULEFLAG := $(if $(RULE),--rule $(CODEMOD_RULEFILE),--config $(CODEMOD_SGCONFIG))

codemod: ## Codemod library: DETECT (default) | TEST=1 validate | APPLY=Y rewrite | RULE=<id>
ifneq ($(RULE),)
ifeq ($(CODEMOD_CSV)$(CODEMOD_RULEFILE),)
	$(Q)echo "ERROR: RULE='$(RULE)' matches no $(CODEMOD_HOME)/rules/**/$(RULE).{csv,yml}"; exit 1
endif
endif
ifeq ($(APPLY),Y)
ifneq ($(CODEMOD_CSV),)
	$(Q)echo "==> codemod APPLY [csv=$(RULE)]: rewriting scope from substitution list"; \
	$(UV_RUN) python $(CODEMOD_CSV_RUNNER) --csv $(CODEMOD_CSV) --apply $(CODEMOD_TARGETS)
else
	$(Q)echo "==> codemod APPLY$(if $(RULE), [rule=$(RULE)],): rewriting scope in declared order"; \
	for t in $(CODEMOD_TARGETS); do \
	  [ -d "$$t" ] || continue; \
	  echo "    apply -> $$t"; \
	  ast-grep scan $(CODEMOD_RULEFLAG) --update-all "$$t" || exit 1; \
	done
endif
else ifeq ($(TEST),1)
	$(Q)echo "==> codemod TEST: validating rules against their test cases"; \
	cd $(CODEMOD_HOME) && ast-grep test --skip-snapshot-tests $(if $(RULE),--filter $(RULE),)
else
ifneq ($(CODEMOD_CSV),)
	$(Q)echo "==> codemod DETECT [csv=$(RULE)]: scanning scope (read-only)"; \
	$(UV_RUN) python $(CODEMOD_CSV_RUNNER) --csv $(CODEMOD_CSV) --check $(CODEMOD_TARGETS)
else
	$(Q)echo "==> codemod DETECT$(if $(RULE), [rule=$(RULE)],): scanning scope (read-only)"; \
	for t in $(CODEMOD_TARGETS); do \
	  [ -d "$$t" ] || continue; \
	  ast-grep scan $(CODEMOD_RULEFLAG) "$$t" || exit $$?; \
	done
endif
endif
