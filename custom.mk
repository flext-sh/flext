# Plan collection belongs to generation; its configuration authorizes effects.
# Like the generated gen recipe, it names its profile destination, so a
# profiled `FLEXT_INFRA_PROFILE=1 make gen` captures this stage too.
.PHONY: pre-gen
pre-gen:
	@FLEXT_INFRA_PROFILE_OUTPUT="$(PROJECT_ROOT)/.reports/docs/collect.pstats" $(PROJECT_FLEXT_INFRA) docs collect \
		--repository-root "$(PROJECT_ROOT)" \
		--configuration "$(PROJECT_ROOT)/config/plan-collection.yaml"
