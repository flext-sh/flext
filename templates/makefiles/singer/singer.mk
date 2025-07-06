# ═══════════════════════════════════════════════════════════════════════════
# FLEXT SINGER PROJECT TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Singer tap/target specific targets for FLEXT projects
# Usage: include $(FLEXT_ROOT)/templates/makefiles/singer/singer.mk
# Dependencies: templates/makefiles/python/python.mk
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
#  SINGER PROJECT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Singer project type detection
SINGER_TYPE := $(shell echo $(PROJECT_NAME) | sed -E 's/^flext-//' | sed -E 's/^(tap|target)-.*$$/\1/')
SINGER_SOURCE := $(shell echo $(PROJECT_NAME) | sed -E 's/^flext-(tap|target)-//')

# Singer configuration
SINGER_CONFIG_FILE ?= config.json
SINGER_CATALOG_FILE ?= catalog.json
SINGER_STATE_FILE ?= state.json
SINGER_PROPERTIES_FILE ?= properties.json

# Singer directories
SINGER_CONFIG_DIR ?= configs
SINGER_SCHEMAS_DIR ?= schemas
SINGER_SAMPLES_DIR ?= samples

# Meltano integration
MELTANO_PROJECT_DIR ?= meltano_project
MELTANO_ENVIRONMENT ?= dev

# ═══════════════════════════════════════════════════════════════════════════
#  SINGER DISCOVERY AND CATALOG TARGETS
# ═══════════════════════════════════════════════════════════════════════════

discover: ## Discover schema and generate catalog
	$(call log_section,Running Singer Discovery)
	$(call ensure_dir,$(SINGER_SCHEMAS_DIR))
	@if [ "$(SINGER_TYPE)" = "tap" ]; then \
		if [ -f "$(SINGER_CONFIG_FILE)" ]; then \
			$(call log_info,Running discovery with config: $(SINGER_CONFIG_FILE)); \
			$(PYTHON) -m $(shell echo $(PROJECT_NAME) | tr '-' '_') \
				--config $(SINGER_CONFIG_FILE) \
				--discover > $(SINGER_CATALOG_FILE); \
			$(call log_success,Catalog generated: $(SINGER_CATALOG_FILE)); \
		else \
			$(call log_error,Config file not found: $(SINGER_CONFIG_FILE)); \
			exit 1; \
		fi; \
	else \
		$(call log_warning,Discovery only available for taps, not targets); \
	fi

catalog-validate: ## Validate Singer catalog
	$(call log_section,Validating Singer Catalog)
	@if [ -f "$(SINGER_CATALOG_FILE)" ]; then \
		$(call log_info,Validating catalog structure); \
		$(PYTHON) -c "import json; json.load(open('$(SINGER_CATALOG_FILE)'))" && \
		$(call log_success,Catalog is valid JSON); \
	else \
		$(call log_error,Catalog file not found: $(SINGER_CATALOG_FILE)); \
		exit 1; \
	fi

catalog-select: ## Select streams in catalog (interactive)
	$(call log_section,Selecting Catalog Streams)
	@if [ -f "$(SINGER_CATALOG_FILE)" ]; then \
		$(call log_info,Available streams:); \
		$(PYTHON) -c "import json; cat=json.load(open('$(SINGER_CATALOG_FILE)')); [print(f'  - {s[\"tap_stream_id\"]}') for s in cat.get('streams', [])]"; \
		echo ""; \
		$(call log_info,Edit $(SINGER_CATALOG_FILE) to select streams and replication methods); \
	else \
		$(call log_error,No catalog found. Run 'make discover' first); \
		exit 1; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  SINGER EXECUTION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

tap-run: ## Run tap extraction
	$(call log_section,Running Tap Extraction)
	@if [ "$(SINGER_TYPE)" = "tap" ]; then \
		if [ -f "$(SINGER_CONFIG_FILE)" ] && [ -f "$(SINGER_CATALOG_FILE)" ]; then \
			$(call log_info,Running tap with config and catalog); \
			$(PYTHON) -m $(shell echo $(PROJECT_NAME) | tr '-' '_') \
				--config $(SINGER_CONFIG_FILE) \
				--catalog $(SINGER_CATALOG_FILE) \
				$(if $(wildcard $(SINGER_STATE_FILE)),--state $(SINGER_STATE_FILE),); \
		else \
			$(call log_error,Required files missing. Need: $(SINGER_CONFIG_FILE), $(SINGER_CATALOG_FILE)); \
			exit 1; \
		fi; \
	else \
		$(call log_error,This is not a tap project); \
		exit 1; \
	fi

tap-test: ## Test tap connection
	$(call log_section,Testing Tap Connection)
	@if [ "$(SINGER_TYPE)" = "tap" ]; then \
		if [ -f "$(SINGER_CONFIG_FILE)" ]; then \
			$(call log_info,Testing connection with limited records); \
			timeout 30s $(PYTHON) -m $(shell echo $(PROJECT_NAME) | tr '-' '_') \
				--config $(SINGER_CONFIG_FILE) \
				$(if $(wildcard $(SINGER_CATALOG_FILE)),--catalog $(SINGER_CATALOG_FILE),--discover) \
				| head -20; \
			$(call log_success,Connection test completed); \
		else \
			$(call log_error,Config file not found: $(SINGER_CONFIG_FILE)); \
			exit 1; \
		fi; \
	else \
		$(call log_error,This is not a tap project); \
		exit 1; \
	fi

target-run: ## Run target loading
	$(call log_section,Running Target Loading)
	@if [ "$(SINGER_TYPE)" = "target" ]; then \
		if [ -f "$(SINGER_CONFIG_FILE)" ]; then \
			$(call log_info,Running target with config); \
			$(PYTHON) -m $(shell echo $(PROJECT_NAME) | tr '-' '_') \
				--config $(SINGER_CONFIG_FILE); \
		else \
			$(call log_error,Config file not found: $(SINGER_CONFIG_FILE)); \
			exit 1; \
		fi; \
	else \
		$(call log_error,This is not a target project); \
		exit 1; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  SINGER TESTING TARGETS
# ═══════════════════════════════════════════════════════════════════════════

test-singer: ## Run Singer protocol tests
	$(call log_section,Running Singer Protocol Tests)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "singer" -v; \
	else \
		$(call log_warning,No Singer tests found); \
	fi

test-connection: ## Test connection to data source
	$(call log_section,Testing Data Source Connection)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "connection" -v; \
	else \
		$(call log_warning,No connection tests found); \
	fi

test-schema: ## Test schema discovery
	$(call log_section,Testing Schema Discovery)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "schema" -v; \
	else \
		$(call log_warning,No schema tests found); \
	fi

test-extract: ## Test data extraction
	$(call log_section,Testing Data Extraction)
	@if [ -d "$(PYTHON_TESTS_DIR)" ]; then \
		$(PYTHON) -m pytest $(PYTHON_TESTS_DIR) -m "extract" -v; \
	else \
		$(call log_warning,No extraction tests found); \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  STATE MANAGEMENT TARGETS
# ═══════════════════════════════════════════════════════════════════════════

state-show: ## Show current state
	$(call log_section,Current State)
	@if [ -f "$(SINGER_STATE_FILE)" ]; then \
		$(call log_info,State file: $(SINGER_STATE_FILE)); \
		cat $(SINGER_STATE_FILE) | jq . 2>/dev/null || cat $(SINGER_STATE_FILE); \
	else \
		$(call log_info,No state file found); \
	fi

state-backup: ## Backup current state
	$(call log_section,Backing Up State)
	@if [ -f "$(SINGER_STATE_FILE)" ]; then \
		cp $(SINGER_STATE_FILE) $(SINGER_STATE_FILE).backup.$$(date +%Y%m%d_%H%M%S); \
		$(call log_success,State backed up); \
	else \
		$(call log_warning,No state file to backup); \
	fi

state-restore: ## Restore state from backup
	$(call log_section,Restoring State)
	@LATEST_BACKUP=$$(ls $(SINGER_STATE_FILE).backup.* 2>/dev/null | sort | tail -1); \
	if [ -n "$$LATEST_BACKUP" ]; then \
		cp "$$LATEST_BACKUP" $(SINGER_STATE_FILE); \
		$(call log_success,State restored from $$LATEST_BACKUP); \
	else \
		$(call log_error,No backup files found); \
		exit 1; \
	fi

state-clean: ## Remove old state backups
	$(call log_section,Cleaning Old State Backups)
	@rm -f $(SINGER_STATE_FILE).backup.* 2>/dev/null || true
	$(call log_success,Old state backups removed)

# ═══════════════════════════════════════════════════════════════════════════
#  MELTANO INTEGRATION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

meltano-init: ## Initialize Meltano project
	$(call log_section,Initializing Meltano Project)
	@if command -v meltano >/dev/null 2>&1; then \
		if [ ! -d "$(MELTANO_PROJECT_DIR)" ]; then \
			meltano init $(MELTANO_PROJECT_DIR); \
			$(call log_success,Meltano project initialized: $(MELTANO_PROJECT_DIR)); \
		else \
			$(call log_warning,Meltano project already exists); \
		fi; \
	else \
		$(call log_error,Meltano not installed. Install with: pip install meltano); \
		exit 1; \
	fi

meltano-add: ## Add this Singer project to Meltano
	$(call log_section,Adding to Meltano Project)
	@if [ -d "$(MELTANO_PROJECT_DIR)" ]; then \
		cd $(MELTANO_PROJECT_DIR); \
		if [ "$(SINGER_TYPE)" = "tap" ]; then \
			meltano add extractor $(PROJECT_NAME) --custom; \
		elif [ "$(SINGER_TYPE)" = "target" ]; then \
			meltano add loader $(PROJECT_NAME) --custom; \
		fi; \
		$(call log_success,Added to Meltano project); \
	else \
		$(call log_error,Meltano project not found. Run 'make meltano-init' first); \
		exit 1; \
	fi

meltano-test: ## Test with Meltano
	$(call log_section,Testing with Meltano)
	@if [ -d "$(MELTANO_PROJECT_DIR)" ]; then \
		cd $(MELTANO_PROJECT_DIR); \
		meltano invoke $(PROJECT_NAME) --discover 2>/dev/null || \
		meltano test $(PROJECT_NAME); \
		$(call log_success,Meltano test completed); \
	else \
		$(call log_error,Meltano project not found); \
		exit 1; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  SAMPLE DATA TARGETS
# ═══════════════════════════════════════════════════════════════════════════

samples-generate: ## Generate sample data
	$(call log_section,Generating Sample Data)
	$(call ensure_dir,$(SINGER_SAMPLES_DIR))
	@if [ "$(SINGER_TYPE)" = "tap" ] && [ -f "$(SINGER_CONFIG_FILE)" ]; then \
		$(call log_info,Generating sample records); \
		timeout 10s $(PYTHON) -m $(shell echo $(PROJECT_NAME) | tr '-' '_') \
			--config $(SINGER_CONFIG_FILE) \
			$(if $(wildcard $(SINGER_CATALOG_FILE)),--catalog $(SINGER_CATALOG_FILE),--discover) \
			> $(SINGER_SAMPLES_DIR)/sample_output.jsonl 2>/dev/null || true; \
		$(call log_success,Sample data generated in $(SINGER_SAMPLES_DIR)); \
	else \
		$(call log_warning,Sample generation only available for taps with config); \
	fi

samples-validate: ## Validate sample data format
	$(call log_section,Validating Sample Data)
	@if [ -f "$(SINGER_SAMPLES_DIR)/sample_output.jsonl" ]; then \
		$(call log_info,Checking Singer message format); \
		$(PYTHON) -c "import json; [json.loads(line) for line in open('$(SINGER_SAMPLES_DIR)/sample_output.jsonl')]" && \
		$(call log_success,Sample data format is valid); \
	else \
		$(call log_warning,No sample data found. Run 'make samples-generate' first); \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

config-template: ## Generate configuration template
	$(call log_section,Generating Configuration Template)
	$(call ensure_dir,$(SINGER_CONFIG_DIR))
	@$(call log_info,Creating config template: $(SINGER_CONFIG_DIR)/$(SINGER_CONFIG_FILE).template)
	@echo '{}' > $(SINGER_CONFIG_DIR)/$(SINGER_CONFIG_FILE).template
	$(call log_success,Configuration template created)

config-validate: ## Validate configuration
	$(call log_section,Validating Configuration)
	@if [ -f "$(SINGER_CONFIG_FILE)" ]; then \
		$(call log_info,Validating config JSON structure); \
		$(PYTHON) -c "import json; json.load(open('$(SINGER_CONFIG_FILE)'))" && \
		$(call log_success,Configuration is valid JSON); \
	else \
		$(call log_error,Config file not found: $(SINGER_CONFIG_FILE)); \
		exit 1; \
	fi

# ═══════════════════════════════════════════════════════════════════════════
#  COMPREHENSIVE SINGER WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════

singer-setup: config-template ## Complete Singer project setup
	$(call log_section,Singer Project Setup)
	$(call log_info,Project type: $(SINGER_TYPE))
	$(call log_info,Data source: $(SINGER_SOURCE))
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit $(SINGER_CONFIG_FILE) with your connection details"
	@if [ "$(SINGER_TYPE)" = "tap" ]; then \
		echo "2. Run 'make discover' to generate catalog"; \
		echo "3. Edit $(SINGER_CATALOG_FILE) to select streams"; \
		echo "4. Run 'make tap-test' to test extraction"; \
	else \
		echo "2. Run 'make target-run' to test loading"; \
	fi
	$(call log_success,Singer setup completed)

singer-workflow: ## Run complete Singer workflow
	$(call log_section,Running Singer Workflow)
	@if [ "$(SINGER_TYPE)" = "tap" ]; then \
		$(MAKE) config-validate && \
		$(MAKE) discover && \
		$(MAKE) catalog-validate && \
		$(MAKE) tap-test && \
		$(MAKE) samples-generate; \
	elif [ "$(SINGER_TYPE)" = "target" ]; then \
		$(MAKE) config-validate && \
		$(MAKE) target-run; \
	fi
	$(call log_success,Singer workflow completed)

# ═══════════════════════════════════════════════════════════════════════════
#  PHONY TARGETS
# ═══════════════════════════════════════════════════════════════════════════

.PHONY: discover catalog-validate catalog-select
.PHONY: tap-run tap-test target-run
.PHONY: test-singer test-connection test-schema test-extract
.PHONY: state-show state-backup state-restore state-clean
.PHONY: meltano-init meltano-add meltano-test
.PHONY: samples-generate samples-validate
.PHONY: config-template config-validate
.PHONY: singer-setup singer-workflow
