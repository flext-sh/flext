# Workspace source collection precedes the standard documentation lifecycle.
.PHONY: pre-docs
pre-docs:
	@$(PROJECT_INFRA_RUN) "$(PROJECT_ROOT)/scripts/docs/collect_plans.py"
