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
.PHONY: codemod

# The codemod library is OWNED BY flext-infra (the tooling engine), never by
# the workspace root. The root only dispatches the verb into that owner.
# The library lives INSIDE the flext-infra package (src/flext_infra/codemod)
# so it travels in the wheel and an external consumer installing
# flext-infra from git resolves the same rules the workspace uses.
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
CODEMOD_ATTACHED := $(shell $(UV_RUN) python -c "$$CODEMOD_ATTACHED_PY" 2>/dev/null)
CODEMOD_SCOPE := $(if $(filter-out project all,$(SCOPE)),$(filter-out project all,$(SCOPE)),. $(WORKSPACE_MEMBERS) $(CODEMOD_ATTACHED))
CODEMOD_TARGETS := $(foreach d,$(CODEMOD_SCOPE),$(wildcard $(d)/src) $(wildcard $(d)/tests) $(wildcard $(d)/examples) $(wildcard $(d)/scripts))
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
	$(UV_RUN) python $(CODEMOD_CSV_RUNNER) --csv $(CODEMOD_CSV) --check $(CODEMOD_TARGETS) || true
else
	$(Q)echo "==> codemod DETECT$(if $(RULE), [rule=$(RULE)],): scanning scope (read-only)"; \
	for t in $(CODEMOD_TARGETS); do \
	  [ -d "$$t" ] || continue; \
	  ast-grep scan $(CODEMOD_RULEFLAG) "$$t" || true; \
	done
endif
endif
