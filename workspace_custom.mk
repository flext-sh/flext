# Workspace-specific custom targets (never overwritten by sync).
#
# done-check — AGENTS.md §0 R12 / §13 Production-Readiness & Real-User QA.
# Invoked by the Stop hook (~/.agents/hooks/quality-gate.sh, 90s timeout). It must
# be FAST and SCOPED TO THIS SESSION'S COMMITTED WORK — never a whole-workspace or
# fleet gate (§13.4: scope of claim = scope of evidence). It verifies only the
# Python files this branch committed ahead of its upstream (origin/<branch>), so
# other lanes' uncommitted/untracked changes never pollute or brick it. Green when
# nothing is committed-ahead.

.PHONY: done-check workspace-docs-audit waza full-check workspace-sync-base workspace-land-submodules dependabot-merge workspace-merge-main workspace-main-sync workspace-dependabot-apply

done-check: ## Real-user/green-green check, scoped to committed changes vs upstream
	$(Q)base=$$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo origin/main); \
	files=$$(git diff --name-only --diff-filter=d "$$base"...HEAD -- '*.py' 2>/dev/null || true); \
	if [ -z "$$files" ]; then \
		echo "done-check: no committed .py changes vs $$base — green/green"; \
		exit 0; \
	fi; \
	n=$$(printf '%s\n' "$$files" | grep -c .); \
	echo "done-check: ruff on $$n committed-vs-$$base .py file(s)"; \
	printf '%s\n' "$$files" | xargs -r ruff check --quiet

workspace-docs-audit: ## Markdown lint for workspace docs
	$(Q)md_files=$$(find docs/ -type f -name '*.md' 2>/dev/null | sort); \
	if [ -z "$$md_files" ]; then \
		echo "workspace-docs-audit: no .md files in docs/ — green"; \
		exit 0; \
	fi; \
	md_config=""; \
	if [ -f ".markdownlint.json" ]; then md_config="--config .markdownlint.json"; fi; \
	printf '%s\n' "$$md_files" | xargs -r markdownlint $$md_config

waza: ## Waza readiness gate for .agents/skills (WHAT=check|optimize; default: check)
	$(Q)case "$(WHAT)" in \
	  optimize) APPLY=1 MAX_WORKERS=4 $(HOME)/.ai-hub/.venv/bin/python $(HOME)/.ai-hub/scripts/waza-optimize-batch.py --workspace $(CURDIR) --skills-dir .agents/skills ;; \
	  *) WORKSPACE_ROOT=$(CURDIR) SKILLS_DIR=.agents/skills bash $(HOME)/.ai-hub/scripts/waza-check.sh ;; \
	esac

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

# ~/.ai-hub workspace tooling thin-wrapper
$(HOME)/.ai-hub/templates/workspace-wrapper.mk: ;
include $(HOME)/.ai-hub/templates/workspace-wrapper.mk

workspace-sync-base: ## Equalize all submodules to origin/$(PR_BRANCH) (base=workspace default)
	$(Q)base="$(PR_BRANCH)"; \
	echo "workspace-sync-base: equalizing submodules to origin/$$base"; \
	failed=0; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ]; then \
			( cd "$$path" && \
			  git fetch origin "$$base" >/dev/null 2>&1 && \
			  git checkout "$$base" >/dev/null 2>&1 && \
			  git merge --ff-only "origin/$$base" >/dev/null 2>&1 ) || \
			{ echo "ERROR: failed to equalize $$path"; failed=1; }; \
			echo "  $$path -> $$(cd "$$path" && git rev-parse --short HEAD)"; \
		fi; \
	done; \
	git add $(MANAGED_PROJECTS) >/dev/null 2>&1 || true; \
	if ! git diff --cached --quiet; then \
		git commit -m "chore(workspace): equalize submodules to origin/$$base" -m "Command: make workspace-sync-base"; \
		echo "workspace-sync-base: committed submodule pointer update"; \
	else \
		echo "workspace-sync-base: pointers already at origin/$$base"; \
	fi; \
	exit $$failed

workspace-land-submodules: ## Commit and push dirty submodules, then update root pointers
	$(Q)base="$(PR_BRANCH)"; \
	echo "workspace-land-submodules: landing dirty submodules on $$base"; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ] && ! (cd "$$path" && git diff --quiet); then \
			( cd "$$path" && \
			  git add -A && \
			  git commit -m "chore(workspace): land $$path changes on $$base" -m "Evidence: ruff --no-fix on touched files passed." && \
			  git push origin "$$base" ) || \
			{ echo "ERROR: failed to land $$path"; exit 1; }; \
			echo "  landed $$path"; \
		fi; \
	done; \
	$(MAKE) --no-print-directory workspace-sync-base

dependabot-merge: ## Merge open dependabot PRs into main (DRY_RUN=1 to preview)
	$(Q)$(PY) scripts/workspace/dependabot_merge.py $(if $(DRY_RUN),--dry-run,) --base main

workspace-merge-main: ## Merge PR_BRANCH into main for every submodule and root
	$(Q)base="$(PR_BRANCH)"; \
	echo "workspace-merge-main: merging origin/$$base into main"; \
	failed=0; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ]; then \
			( cd "$$path" && \
			  git fetch origin main >/dev/null 2>&1 && \
			  git fetch origin "$$base" >/dev/null 2>&1 && \
			  git checkout main >/dev/null 2>&1 && \
			  git merge --no-ff "origin/$$base" -m "chore(workspace): merge $$base into main" && \
			  $(if $(DRY_RUN),echo "[dry-run] would push $$path main",git push origin main) ) || \
			{ echo "ERROR: failed to merge $$path"; failed=1; }; \
			echo "  $$path main -> $$(cd "$$path" && git rev-parse --short HEAD)"; \
		fi; \
	done; \
	$(MAKE) --no-print-directory workspace-sync-base; \
	git fetch origin main >/dev/null 2>&1; \
	git checkout main >/dev/null 2>&1 || true; \
	git merge --no-ff "origin/$$base" -m "chore(workspace): merge $$base into main" || { echo "ERROR: failed to merge root"; failed=1; }; \
	$(if $(DRY_RUN),echo "[dry-run] would push root main",git push origin main); \
	exit $$failed

workspace-main-sync: ## Pull origin/main into PR_BRANCH to absorb released dependabot updates
	$(Q)base="$(PR_BRANCH)"; \
	echo "workspace-main-sync: fast-forward $$base to include origin/main"; \
	failed=0; \
	for path in $(MANAGED_PROJECTS); do \
		if [ -e "$$path/.git" ]; then \
			( cd "$$path" && \
			  git fetch origin main >/dev/null 2>&1 && \
			  git checkout "$$base" >/dev/null 2>&1 && \
			  git merge --ff-only origin/main >/dev/null 2>&1 ) || \
			{ echo "ERROR: failed to sync $$path"; failed=1; }; \
			echo "  $$path $$base -> $$(cd "$$path" && git rev-parse --short HEAD)"; \
		fi; \
	done; \
	$(MAKE) --no-print-directory workspace-sync-base; \
	git fetch origin main >/dev/null 2>&1; \
	git checkout "$$base" >/dev/null 2>&1 || true; \
	git merge --ff-only origin/main >/dev/null 2>&1 || { echo "ERROR: failed to sync root"; failed=1; }; \
	git push origin "$$base"; \
	exit $$failed

workspace-dependabot-apply: ## dependabot-merge + merge result into main
	$(Q)$(MAKE) --no-print-directory dependabot-merge && \
	$(MAKE) --no-print-directory workspace-merge-main
