# Plan collection belongs to generation; its configuration authorizes effects.
.PHONY: pre-gen
pre-gen:
	@$(PROJECT_FLEXT_INFRA) docs collect \
		--repository-root "$(PROJECT_ROOT)" \
		--configuration "$(PROJECT_ROOT)/config/plan-collection.yaml"
