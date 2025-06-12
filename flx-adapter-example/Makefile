###############################################################################
#  FLX Adapter Example - Project Makefile
#  Includes standard targets and adds project-specific commands
###############################################################################

# Include the standard Makefile
include Makefile.standard

# ═══════════════════════════[ PROJECT SPECIFIC ]═══════════════════════════════
# Adapter Example specific targets

.PHONY: example-basic example-advanced example-test adapter-scaffold

example-basic: ## Run basic adapter example
	$(call msg,"Running basic adapter example")
	@$(PYTHON) examples/basic_usage.py
	$(call success,"Basic example completed")

example-advanced: ## Run advanced adapter example
	$(call msg,"Running advanced adapter example")
	@if [ -f "examples/advanced_usage.py" ]; then \
		$(PYTHON) examples/advanced_usage.py; \
	else \
		$(warn,"Advanced example not yet implemented"); \
	fi
	$(call success,"Advanced example completed")

example-test: ## Test adapter functionality
	$(call msg,"Testing adapter functionality")
	@$(PYTHON) -c "from flx_adapter_example import ExampleAdapter; adapter = ExampleAdapter(); print('✓ Adapter instantiated successfully')"
	$(call success,"Adapter test completed")

adapter-scaffold: ## Generate new adapter from template
	$(call msg,"Generating adapter scaffold")
	@echo "Enter adapter name (e.g., my-service):"
	@read -r ADAPTER_NAME; \
	if [ -n "$$ADAPTER_NAME" ]; then \
		mkdir -p "../flx-adapter-$$ADAPTER_NAME"; \
		cp -r . "../flx-adapter-$$ADAPTER_NAME/"; \
		echo "✓ Created new adapter project: flx-adapter-$$ADAPTER_NAME"; \
	else \
		echo "❌ Adapter name required"; \
	fi
	$(call success,"Scaffold generation completed")

# Override the cli target
cli: ## Show adapter example help
	$(call msg,"FLX Adapter Example")
	@echo "This is a template project for creating FLX adapters."
	@echo ""
	@echo "Available examples:"
	@echo "  make example-basic    - Run basic adapter example"
	@echo "  make example-advanced - Run advanced adapter example"
	@echo ""
	@echo "To create a new adapter:"
	@echo "  make adapter-scaffold - Generate new adapter from this template"

# Add custom help section
help-adapter: ## Show adapter-specific commands
	@echo ""
	@echo "$(C_YELLOW)Adapter Example Targets:$(C_RESET)"
	@grep -E '^(example|adapter)-[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(C_GREEN)%-20s$(C_RESET) %s\n", $$1, $$2}'