# Workspace-specific custom targets (never overwritten by sync).
#
# done-check — AGENTS.md §0 R12 / §13 Production-Readiness & Real-User QA.
# Invoked by the Stop hook (~/.agents/hooks/quality-gate.sh, 90s timeout). It must
# be FAST and SCOPED TO THIS SESSION'S COMMITTED WORK — never a whole-workspace or
# fleet gate (§13.4: scope of claim = scope of evidence). It verifies only the
# Python files this branch committed ahead of its upstream (origin/<branch>), so
# other lanes' uncommitted/untracked changes never pollute or brick it. Green when
# nothing is committed-ahead.

.PHONY: done-check waza legacy-check legacy-val full-check legacy-boot legacy-build legacy-ship legacy-test legacy-clean

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

legacy-check: ## Legacy compatibility layer (prefer: make check WHAT=<new-what>)
	$(Q)echo "DEPRECATED: legacy-check keeps old check WHAT mappings; prefer make check WHAT=<what>."
	$(Q)case "$(WHAT)" in \
	"" | all | full) $(MAKE) --no-print-directory _check_default $(MAKE_SELECTION_ARGS) ;; \
	scan) $(MAKE) --no-print-directory _scan $(MAKE_SELECTION_ARGS) ;; \
	fmt) $(MAKE) --no-print-directory _fmt $(MAKE_SELECTION_ARGS) ;; \
	types) $(MAKE) --no-print-directory _types $(MAKE_SELECTION_ARGS) ;; \
	pyre) $(MAKE) --no-print-directory _pyre $(MAKE_SELECTION_ARGS) ;; \
	pol) $(MAKE) --no-print-directory _pol $(MAKE_SELECTION_ARGS) ;; \
	cqrs) $(MAKE) --no-print-directory _cqrs $(MAKE_SELECTION_ARGS) ;; \
	lint) $(MAKE) --no-print-directory _check_default $(MAKE_SELECTION_ARGS) ;; \
	pyrefly) $(MAKE) --no-print-directory _pyre $(MAKE_SELECTION_ARGS) ;; \
	loc-cap) $(MAKE) --no-print-directory _check_default CHECK_GATES=loc-cap $(MAKE_SELECTION_ARGS) ;; \
	boundary) $(MAKE) --no-print-directory _check_default CHECK_GATES=boundary $(MAKE_SELECTION_ARGS) ;; \
	coordination) $(MAKE) --no-print-directory _coordination $(MAKE_SELECTION_ARGS) ;; \
	*) echo "ERRO: invalid legacy check WHAT='$(WHAT)'"; \
	   echo "VALID legacy values: all|full|scan|fmt|types|pyre|pol|cqrs|lint|pyrefly|loc-cap|boundary|coordination"; \
	   exit 2 ;; \
	esac

legacy-val: ## Legacy validation dispatch (prefer: make val WHAT=<scope>).
	$(Q)echo "DEPRECATED: legacy-val keeps old scope names; prefer make val WHAT=<project|workspace|all>."
	$(Q)case "$(WHAT)" in \
	"" | project) $(MAKE) --no-print-directory _val_project $(MAKE_SELECTION_ARGS) ;; \
	workspace) $(MAKE) --no-print-directory _val_workspace $(MAKE_SELECTION_ARGS) ;; \
	all) $(MAKE) --no-print-directory _val_workspace $(MAKE_SELECTION_ARGS); $(MAKE) --no-print-directory _val_project $(MAKE_SELECTION_ARGS) ;; \
	*) echo "ERRO: invalid legacy val WHAT='$(WHAT)'"; \
	   echo "VALID legacy values: project|workspace|all (or empty=project)"; \
	   exit 2 ;; \
	esac

legacy-boot: ## Legacy boot dispatch (prefer: make boot WHAT=<action>).
	$(Q)echo "DEPRECATED: legacy-boot keeps old boot WHAT mappings; prefer make boot WHAT=<all|sync|stat|imp>."
	$(Q)case "$(WHAT)" in \
	"" | all | venv | submodules) $(MAKE) --no-print-directory _boot_default $(MAKE_SELECTION_ARGS) ;; \
	sync) $(MAKE) --no-print-directory _sync $(MAKE_SELECTION_ARGS) ;; \
	stat) $(MAKE) --no-print-directory _stat $(MAKE_SELECTION_ARGS) ;; \
	imp) $(MAKE) --no-print-directory _imp $(MAKE_SELECTION_ARGS) ;; \
	*) echo "ERRO: invalid legacy boot WHAT='$(WHAT)'"; \
	   echo "VALID legacy values: all|venv|submodules|sync|stat|imp (or empty=all)"; \
	   exit 2 ;; \
	esac

legacy-build: ## Legacy build dispatch (prefer: make build WHAT=<action>).
	$(Q)echo "DEPRECATED: legacy-build keeps old build WHAT mappings; prefer make build WHAT=<all|gen|mod|up|constraints|sync|docs|stubs>."
	$(Q)case "$(WHAT)" in \
	"" | all) $(MAKE) --no-print-directory _build_default $(MAKE_SELECTION_ARGS) ;; \
	gen) $(MAKE) --no-print-directory _gen $(MAKE_SELECTION_ARGS) ;; \
	mod) $(MAKE) --no-print-directory _mod $(MAKE_SELECTION_ARGS) ;; \
	up) $(MAKE) --no-print-directory _up $(MAKE_SELECTION_ARGS) ;; \
	constraints) $(MAKE) --no-print-directory _constraints $(MAKE_SELECTION_ARGS) ;; \
	sync) $(MAKE) --no-print-directory _sync $(MAKE_SELECTION_ARGS) ;; \
	docs) $(MAKE) --no-print-directory _docs $(MAKE_SELECTION_ARGS) ;; \
	stubs) $(MAKE) --no-print-directory _stubs $(MAKE_SELECTION_ARGS) ;; \
	*) echo "ERRO: invalid legacy build WHAT='$(WHAT)'"; \
	   echo "VALID legacy values: all|gen|mod|up|constraints|sync|docs|stubs (or empty=all)"; \
	   exit 2 ;; \
	esac

legacy-ship: ## Legacy ship dispatch (prefer: make ship WHAT=<action>).
	$(Q)echo "DEPRECATED: legacy-ship keeps old ship WHAT mappings; prefer make ship WHAT=<all|save|tag|push|pr|rel>."
	$(Q)case "$(WHAT)" in \
	"" | all | rel) $(MAKE) --no-print-directory _rel $(MAKE_SELECTION_ARGS) ;; \
	save) $(MAKE) --no-print-directory _save $(MAKE_SELECTION_ARGS) ;; \
	tag) $(MAKE) --no-print-directory _tag $(MAKE_SELECTION_ARGS) ;; \
	push) $(MAKE) --no-print-directory _push $(MAKE_SELECTION_ARGS) ;; \
	pr) $(MAKE) --no-print-directory _pr $(MAKE_SELECTION_ARGS) ;; \
	*) echo "ERRO: invalid legacy ship WHAT='$(WHAT)'"; \
	   echo "VALID legacy values: all|save|tag|push|pr|rel (or empty=all)"; \
	   exit 2 ;; \
	esac

legacy-test: ## Legacy test dispatch (prefer: make test WHAT=<action>).
	$(Q)echo "DEPRECATED: legacy-test keeps old test interface; prefer make test WHAT=all PROJECT=... MATCH=...."
	$(Q)$(MAKE) --no-print-directory _test_default $(MAKE_SELECTION_ARGS)

legacy-clean: ## Legacy clean dispatch (prefer: make clean WHAT=<action>).
	$(Q)echo "DEPRECATED: legacy-clean keeps old clean interface; prefer make clean WHAT=all."
	$(Q)$(MAKE) --no-print-directory _clean_default $(MAKE_SELECTION_ARGS)

full-check: ## Run legacy full check path with explicit timeout (use only when needed)
	$(Q)timeout_s=$${FULL_CHECK_TIMEOUT:-1200}; \
	if ! command -v timeout >/dev/null 2>&1; then \
		echo "WARN: timeout utility unavailable; running without timeout"; \
		$(MAKE) --no-print-directory legacy-check WHAT=full $(MAKE_SELECTION_ARGS); \
		code=$$?; \
		exit $$code; \
	else \
		timeout "$$timeout_s"s $(MAKE) --no-print-directory legacy-check WHAT=full $(MAKE_SELECTION_ARGS); \
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
