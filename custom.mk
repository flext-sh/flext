# Workspace source collection precedes the standard documentation lifecycle.
.PHONY: pre-docs
pre-docs:
	@$(PROJECT_FLEXT_INFRA) docs collect \
		--repository-root "$(PROJECT_ROOT)" \
		--configuration "$(PROJECT_ROOT)/config/plan-collection.yaml"
