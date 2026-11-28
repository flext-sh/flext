# Plan collection feeds the generation that make check converges; its
# configuration authorizes effects. Like that generation, it runs only outside
# CI (ADR-037: CI converges nothing), and it names its profile destination, so a
# profiled `FLEXT_INFRA_PROFILE=1 make check` captures this stage too.
.PHONY: pre-check
pre-check:
	@$(if $(filter Y,$(CI)),:,FLEXT_INFRA_PROFILE_OUTPUT="$(PROJECT_ROOT)/.reports/docs/collect.pstats" $(PROJECT_FLEXT_INFRA) docs collect \
		--repository-root "$(PROJECT_ROOT)" \
		--configuration "$(PROJECT_ROOT)/config/plan-collection.yaml")
