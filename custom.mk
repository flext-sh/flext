# Workspace source collection precedes the standard documentation lifecycle.
.PHONY: pre-docs
pre-docs:
	@$(PROJECT_INFRA_RUN) "$(PROJECT_ROOT)/scripts/docs/collect_plans.py"

# CSV-driven symbol-rename engine (ported from 0.20.0-dev). One generic
# mechanism applies ANY `old,new` list in codemod/rules/refactor/*.csv across
# every project's src/ and tests/; a new rename campaign adds a CSV, never a
# new script or parallel rule. AST-aware code rewrite (ast-grep) plus a
# word-boundary text pass over comments/docstrings, longest-old-first so no
# short name shadows a longer one and re-running is a no-op.
#
#   make codemod RULE=cacophony            # detect only (read-only report)
#   make codemod RULE=cacophony APPLY=Y    # rewrite in place
CODEMOD_CSV_DIR := $(PROJECT_ROOT)/codemod/rules/refactor
CODEMOD_CSV_RUNNER := $(CODEMOD_CSV_DIR)/apply_renames.py
CODEMOD_TARGETS := $(wildcard $(PROJECT_ROOT)/src) $(wildcard $(PROJECT_ROOT)/tests) \
	$(foreach d,$(wildcard $(PROJECT_ROOT)/flext-*),$(wildcard $(d)/src) $(wildcard $(d)/tests))

.PHONY: codemod
codemod:
	@if [ -z "$(RULE)" ]; then \
		printf 'ERROR: RULE=<csv-id> required; available: %s\n' \
			"$$(cd "$(CODEMOD_CSV_DIR)" && ls *.csv | sed 's/\.csv$$//' | tr '\n' ' ')" >&2; \
		exit 2; \
	fi
	@csv="$(CODEMOD_CSV_DIR)/$(RULE).csv"; \
	if [ ! -f "$$csv" ]; then printf 'ERROR: no substitution list %s\n' "$$csv" >&2; exit 2; fi; \
	if [ "$(APPLY)" = "Y" ]; then \
		printf '==> codemod APPLY [csv=%s]\n' "$(RULE)"; \
		$(PROJECT_INFRA_RUN) "$(CODEMOD_CSV_RUNNER)" --csv "$$csv" --apply $(CODEMOD_TARGETS); \
	else \
		printf '==> codemod DETECT [csv=%s] (read-only)\n' "$(RULE)"; \
		$(PROJECT_INFRA_RUN) "$(CODEMOD_CSV_RUNNER)" --csv "$$csv" --check $(CODEMOD_TARGETS) || true; \
	fi

