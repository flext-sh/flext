# Workspace-specific custom targets (never overwritten by sync).
#
# done-check — AGENTS.md §0 R12 / §13 Production-Readiness & Real-User QA.
# Invoked by the Stop hook (~/.agents/hooks/quality-gate.sh, 90s timeout). It must
# be FAST and SCOPED TO THIS SESSION'S COMMITTED WORK — never a whole-workspace or
# fleet gate (§13.4: scope of claim = scope of evidence). It verifies only the
# Python files this branch committed ahead of its upstream (origin/<branch>), so
# other lanes' uncommitted/untracked changes never pollute or brick it. Green when
# nothing is committed-ahead.

.PHONY: done-check workspace-docs-audit waza full-check

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
