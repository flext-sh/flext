###############################################################################
#  Root Makefile — pyauto workspace
#  Author : Marlon Costa <marlon.costa@datacosmos.com.br>
#  License: MIT
###############################################################################

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Paths
WORKSPACE_ROOT ?= $(shell git -C "$(CURDIR)" rev-parse --show-toplevel 2>/dev/null || \
                          echo "$(CURDIR)")
SCRIPTS_DIR    := $(WORKSPACE_ROOT)/scripts
LOGS_DIR       := $(WORKSPACE_ROOT)/logs
VENV_DIR       := $(WORKSPACE_ROOT)/.venv
VENV_BIN       := $(VENV_DIR)/bin
VENV_SCRIPT    := $(SCRIPTS_DIR)/utilities/setup_venv.sh

# Python Environment
PYTHON_VERSION := 3.13
PY             := python$(PYTHON_VERSION)
PYTHON         := $(PY)
POETRY         := poetry
PROJECT_RUNNER := $(SCRIPTS_DIR)/project_runner.sh

# Python Scripts
PROJECT_MANAGE := $(SCRIPTS_DIR)/core/project_manage.py
SCAFFOLD_MANAGE:= $(SCRIPTS_DIR)/core/scaffold_manage.py
GIT_MANAGE     := $(SCRIPTS_DIR)/core/git_manage.py

# Logging
TIMESTAMP      := $(shell date +"%Y%m%d_%H%M%S")
LOGFILE_DIR    := $(LOGS_DIR)/makefile
$(shell mkdir -p $(LOGFILE_DIR))

# Cleanup Patterns - Padrões para limpeza de artefatos
# Centraliza todos os padrões de limpeza em variáveis reutilizáveis
CACHE_DIRS     := __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov dist build
CACHE_FILES    := *.pyc .coverage
CACHE_PATTERNS := *.egg-info

# Project Detection - Melhorada para consistência com sync_dependencies.py
EXCLUDE_DIRS := reference docs logs scripts reports schemas temp_workflows junit src tests
EXCLUDE_DIRS_PATTERN := $(shell echo "$(EXCLUDE_DIRS)" | sed 's/ /|/g')
PROJECTS_DIR := $(WORKSPACE_ROOT)

define detect_projects
  $(shell find $(PROJECTS_DIR) \
    -mindepth 1 \
    -maxdepth 1 \
    -type d \
    -not -name ".*" \
    $(foreach dir,$(EXCLUDE_DIRS),-not -name "$(dir)") \
    -exec test -f {}/pyproject.toml \; \
    -print | \
    sort)
endef

PROJECTS := $(call detect_projects)
ALL_PROJECT_NAMES := $(notdir $(PROJECTS))
PROJECT_NAMES := $(if $(PROJECT),$(PROJECT),$(notdir $(PROJECTS)))
PROJECT ?=

# Colors - Compatível com bash simples
# Função para detectar suporte a cores
define check_color_support
$(shell if [ -t 1 ] && [ "$${TERM:-dumb}" != "dumb" ] && [ -z "$${NO_COLOR:-}" ]; then echo "1"; else echo "0"; fi)
endef

COLOR_SUPPORT := $(call check_color_support)

# Define cores usando uma abordagem mais simples
ifeq ($(COLOR_SUPPORT),1)
BLUE    := \\033[0;34m
GREEN   := \\033[0;32m
YELLOW  := \\033[0;33m
RED     := \\033[0;31m
CYAN    := \\033[0;36m
NC      := \\033[0m
BOLD    := \\033[1m
else
BLUE    :=
GREEN   :=
YELLOW  :=
RED     :=
CYAN    :=
NC      :=
BOLD    :=
endif

# ═══════════════════════════════════════════════════════════════════════════
#  MACROS
# ═══════════════════════════════════════════════════════════════════════════

define section
	@/bin/echo -e "\n$(BLUE)══════════════════[ $1 ]═══════════════════$(NC)"
endef

define success
	@/bin/echo -e "$(GREEN)✓ $1$(NC)"
endef

define error
	@/bin/echo -e "$(RED)✗ $1$(NC)"
endef

define warning
	@/bin/echo -e "$(YELLOW)⚠ $1$(NC)"
endef

define info
	@/bin/echo -e "$(CYAN)ℹ $1$(NC)"
endef

# Execute command for all projects
define run_for_projects
	@mkdir -p $(LOGFILE_DIR)/$(1)
	@/bin/echo -e "\n$(BLUE)══════════════════[ $(2) em $(if $(PROJECT),$(PROJECT),todos os projetos) ]═══════════════════$(NC)"
	@for proj in $(PROJECT_NAMES); do \
		/bin/echo -e "\n$(BLUE)══════════════════[ $(2) em $$proj ]═══════════════════$(NC)"; \
		$(PROJECT_RUNNER) \
			--flx_project $$proj \
			--log-dir $(LOGFILE_DIR)/$(1) \
			"$(3)"; \
	done
endef

# Execute single command with logging
define run_command
	@mkdir -p $(LOGFILE_DIR)/$(1)
	$(call section,$(2))
	@$(3)
	$(call success,$(2) completado com sucesso)
endef

# Require PROJECT variable
define require_project
	@if [ -z "$(PROJECT)" ]; then \
		$(call error,É necessário especificar um projeto: make $(1) PROJECT=nome_do_projeto); \
		exit 1; \
	fi
endef

# Require MODULE variable
define require_module
	@if [ -z "$(MODULE)" ]; then \
		$(call error,É necessário especificar um módulo: make $(1) PROJECT=$(PROJECT) MODULE=nome_do_módulo); \
		exit 1; \
	fi
endef

# Macro otimizado para limpeza completa
# Combina todos os padrões em um único comando find para melhor performance
define cleanup_artifacts
	@find . \( \
		$(foreach dir,$(CACHE_DIRS),-type d -name "$(dir)" -o) \
		$(foreach file,$(CACHE_FILES),-type f -name "$(file)" -o) \
		$(foreach pattern,$(CACHE_PATTERNS),-name "$(pattern)" -o) \
		-false \) \
		-exec rm -rf {} \; 2>/dev/null || true
endef

# ═══════════════════════════════════════════════════════════════════════════
#  TARGETS
# ═══════════════════════════════════════════════════════════════════════════

.DEFAULT_GOAL := install
.PHONY: help

# ───────────────────────────────────────────────────────────────────────────
#  VIRTUAL ENVIRONMENT
# ───────────────────────────────────────────────────────────────────────────

## venv-check: Verifica integridade do ambiente virtual
venv-check:
	@echo ">>> Verificando integridade do ambiente virtual..."
	@if ! bash $(VENV_SCRIPT) verify; then \
		echo ">>> Ambiente virtual precisa ser reconstruído"; \
		echo ">>> Iniciando reconstrução completa..."; \
		bash $(VENV_SCRIPT) rebuild; \
	fi

## venv-install: Instala dependências principais
venv-install: venv-check
	@bash $(VENV_SCRIPT) install

## venv-install-dev: Instala dependências de desenvolvimento
venv-install-dev: venv-check
	@bash $(VENV_SCRIPT) install-dev

## venv-setup: Configuração inicial completa do ambiente
venv-setup: venv-install-dev
	$(call section,Configurando ambiente de desenvolvimento)
	@bash $(VENV_SCRIPT) check-tools
	$(call success,Setup do ambiente virtual completo)

## venv-rebuild: Reconstrói ambiente virtual do zero
venv-rebuild:
	$(call section,Reconstruindo ambiente virtual)
	@bash $(VENV_SCRIPT) rebuild
	$(call success,Ambiente virtual reconstruído)

## venv-clean: Remove ambiente virtual
venv-clean:
	$(call section,Removendo ambiente virtual)
	@bash $(VENV_SCRIPT) clean
	$(call success,Ambiente virtual removido)

## venv-status: Mostra status do ambiente virtual
venv-status:
	$(call section,Status do ambiente virtual)
	@bash $(VENV_SCRIPT) status

# Aliases para compatibilidade
## install: Alias para venv-install
install: venv-install

## install-dev: Alias para venv-install-dev
install-dev: venv-install-dev

## setup: Alias para venv-setup
setup: venv-setup

# ───────────────────────────────────────────────────────────────────────────
#  CLEANUP
# ───────────────────────────────────────────────────────────────────────────

## clean: Limpa artefatos de build e cache
clean:
	$(call section,Limpando artefatos)
	$(call cleanup_artifacts)
	$(call success,Limpeza de artefatos completada)

# ───────────────────────────────────────────────────────────────────────────
#  STANDARDIZED PROJECT COORDINATION
# ───────────────────────────────────────────────────────────────────────────

# Define PYAUTO_ROOT for coordinated mode
export PYAUTO_ROOT := $(WORKSPACE_ROOT)

## project-run: Executa qualquer target em um projeto específico
project-run: venv-check
	@if [ -z "$(PROJECT)" ]; then \
		$(call error,"PROJECT não especificado. Use: make project-run PROJECT=nome TARGET=comando"); \
		exit 1; \
	elif [ -z "$(TARGET)" ]; then \
		$(call error,"TARGET não especificado. Use: make project-run PROJECT=nome TARGET=comando"); \
		exit 1; \
	else \
		$(call check_project_exists); \
		$(call section,"Executando $(TARGET) em $(PROJECT)"); \
		cd $(WORKSPACE_ROOT)/$(PROJECT) && \
		$(MAKE) $(TARGET) PYAUTO_ROOT=$(WORKSPACE_ROOT); \
	fi

## project-status: Mostra status de um projeto específico
project-status:
	@if [ -z "$(PROJECT)" ]; then \
		$(call section,"Status de todos os projetos"); \
		for proj in $(ALL_PROJECT_NAMES); do \
			echo ""; \
			$(call subsection,"$$proj"); \
			cd $(WORKSPACE_ROOT)/$$proj && $(MAKE) status --no-print-directory 2>/dev/null || echo "Status não disponível"; \
		done; \
	else \
		$(call check_project_exists); \
		cd $(WORKSPACE_ROOT)/$(PROJECT) && $(MAKE) status; \
	fi

## project-validate: Valida estrutura de um projeto
project-validate:
	@if [ -z "$(PROJECT)" ]; then \
		$(call section,"Validando todos os projetos"); \
		for proj in $(ALL_PROJECT_NAMES); do \
			$(call subsection,"Validando $$proj"); \
			cd $(WORKSPACE_ROOT)/$$proj && $(MAKE) validate --no-print-directory 2>/dev/null || echo "❌ Validação falhou"; \
		done; \
	else \
		$(call check_project_exists); \
		cd $(WORKSPACE_ROOT)/$(PROJECT) && $(MAKE) validate; \
	fi

## projects-report: Gera relatório consolidado de todos os projetos
projects-report:
	$(call section,"Gerando relatório consolidado")
	@mkdir -p $(WORKSPACE_ROOT)/reports
	@echo "# PyAuto Projects Report" > $(WORKSPACE_ROOT)/reports/consolidated_report.md
	@echo "Generated: $$(date)" >> $(WORKSPACE_ROOT)/reports/consolidated_report.md
	@echo "" >> $(WORKSPACE_ROOT)/reports/consolidated_report.md
	@for proj in $(PROJECT_NAMES); do \
		echo "## $$proj" >> $(WORKSPACE_ROOT)/reports/consolidated_report.md; \
		cd $(WORKSPACE_ROOT)/$$proj && $(MAKE) report --no-print-directory 2>/dev/null || echo "Report não disponível"; \
		if [ -f reports/report.md ]; then \
			cat reports/report.md >> $(WORKSPACE_ROOT)/reports/consolidated_report.md; \
		fi; \
		echo "" >> $(WORKSPACE_ROOT)/reports/consolidated_report.md; \
	done
	$(call success,"Relatório consolidado gerado em reports/consolidated_report.md")

# ───────────────────────────────────────────────────────────────────────────
#  DEVELOPMENT
# ───────────────────────────────────────────────────────────────────────────

## test: Executa testes (COV=1 JUNIT=1 VERBOSE=1)
test: venv-check
	$(call run_for_projects,test,Executando testes,\
		python -m pytest \
			$(if $(V),-v,) \
			$(if $(VERBOSE),--verbose,) \
			$(if $(COV),--cov=. --cov-report=term --cov-report=html:reports/coverage,) \
			$(if $(JUNIT),--junitxml=junit/test-results.xml,) \
			$(if $(FAILFAST),--exitfirst,) \
			$(if $(k),'-k $(k)',) \
			$(if $(XVFB),--no-xvfb,) \
			$(if $(m),'-m $(m)',) \
			$(if $(TEST_PATH),$(TEST_PATH),) \
			$(PYTEST_ARGS) \
	)
	$(call success,Testes executados)
	@if [ "$(COV)" = "1" ] && [ -n "$(PROJECT)" ]; then \
		$(call info,Relatório de cobertura gerado em $(PROJECT)/reports/coverage/index.html); \
	fi

## test-cov: Executa testes com cobertura
test-cov: COV=1
test-cov: test

## test-junit: Executa testes com relatório JUnit
test-junit: JUNIT=1
test-junit: test

## test-verbose: Executa testes com saída detalhada
test-verbose: VERBOSE=1
test-verbose: test

## lint: Executa verificação de código (CHECK=1 SECURITY=1)
lint: venv-check
	$(call run_for_projects,lint,Executando lint,\
		$(VENV_BIN)/ruff check . \
	)
	$(call success,Lint executado)
	@if [ "$(CHECK)" = "1" ]; then \
		$(MAKE) lint-check; \
	fi
	@if [ "$(SECURITY)" = "1" ]; then \
		$(MAKE) lint-security; \
	fi

## lint-check: Verifica erros de lint sem correção
lint-check: venv-check
	$(call run_for_projects,lint-check,Verificando erros de lint,\
		$(POETRY) run ruff check . \
			--select=E,F,I,W,UP \
			--ignore=E501,UP007 \
			--statistics \
	)
	$(call success,Verificação de lint completada)

## lint-security: Verifica problemas de segurança
lint-security: venv-check
	$(call run_for_projects,lint-security,Verificando segurança,\
		$(POETRY) run bandit -r . \
			-x '$(EXCLUDE_DIRS_PATTERN)' \
			-ll || true \
	)
	$(call success,Verificação de segurança completada)

## mypy: Executa verificação de tipos com mypy
mypy: venv-check
	$(call run_for_projects,mypy,Executando verificação de tipos,\
		$(VENV_BIN)/mypy . \
			--config-file=$(WORKSPACE_ROOT)/mypy.ini \
			--ignore-missing-imports \
			--no-error-summary \
			--pretty \
	)
	$(call success,Verificação de tipos completada)

## fix-ruff: Executa correções automáticas com Ruff
fix-ruff: venv-check
	$(call run_for_projects,fix-ruff,Executando correções Ruff,\
		$(POETRY) run ruff check --fix . || true \
	)
	$(call success,Correções Ruff executadas)

## fix-isort: Organiza imports com isort
fix-isort: venv-check
	$(call run_for_projects,fix-isort,Organizando imports,\
		$(POETRY) run isort . || true \
	)
	$(call success,Organização de imports executada)

## fix-black: Formata código com Black
fix-black: venv-check
	$(call run_for_projects,fix-black,Formatando com Black,\
		$(POETRY) run black . || true \
	)
	$(call success,Formatação Black executada)

## fix: Executa todas as correções automáticas
fix: fix-ruff fix-isort fix-black fix-lint-issues
	$(call success,Todas as correções automáticas executadas)

## fix-lint-issues: Corrige problemas específicos de lint
fix-lint-issues: venv-check
	$(call run_for_projects,fix-lint-issues,Corrigindo problemas de lint,\
		$(VENV_BIN)/ruff check --fix . \
			--select=DTZ,TRY,ANN,D,INP,PLW \
			--extend-ignore=D100,D101,D102,D103,D104,D105,D106,D107 \
		|| true \
	)
	$(call success,Problemas de lint corrigidos)

## upgrade-syntax: Atualiza sintaxe Python para versão mais recente
upgrade-syntax: venv-check
	$(call run_for_projects,upgrade-syntax,Atualizando sintaxe Python,\
		find . -name "*.py" \
			$(foreach dir,$(EXCLUDE_DIRS),-not -path "./$(dir)/*") \
			-exec $(POETRY) run pyupgrade --py313-plus {} + || true \
	)
	$(call success,Atualização de sintaxe completada)

## format: Formata código (alias para fix-black)
format: fix-black

## build: Constrói pacotes
build: venv-check
	$(call run_for_projects,build,Construindo,\
		python -m build \
	)
	$(call success,Build concluído)

# ───────────────────────────────────────────────────────────────────────────
#  COMPLETE SETUP - PEP8 + INSTALLATION
# ───────────────────────────────────────────────────────────────────────────

## setup-complete: Aplica PEP8 e instala tudo via Poetry
setup-complete: pep8-apply install-workspace
	$(call success,Setup completo finalizado - PEP8 aplicado e dependências instaladas)

## setup-complete-clean: Reinstala tudo do zero com PEP8
setup-complete-clean: venv-clean venv-setup pep8-apply install-workspace
	$(call success,Setup completo do zero finalizado - Ambiente limpo com PEP8)

# ───────────────────────────────────────────────────────────────────────────
#  DEPENDENCY MANAGEMENT
# ───────────────────────────────────────────────────────────────────────────

## install-all: Instala todas as dependências (todos os grupos)
install-all: venv-check
	$(call run_for_projects,install-all,Instalando todas as dependências,\
		if [ ! -f poetry.lock ] || [ pyproject.toml -nt poetry.lock ]; then \
			$(POETRY) lock || true; \
		fi; \
		$(POETRY) install --all-groups || true \
	)
	$(call success,Todas as dependências instaladas)

## install-workspace: Instala TODAS as dependências do workspace PyAuto de uma vez
install-workspace: venv-check
	$(call section,Instalação completa do workspace PyAuto via Poetry)
	@echo "🚀 Instalando dependências do workspace principal..."
	@. $(VENV_DIR)/bin/activate && cd $(WORKSPACE_ROOT) && \
		if [ ! -f poetry.lock ] || [ pyproject.toml -nt poetry.lock ]; then \
			$(VENV_BIN)/poetry lock --no-update || true; \
		fi && \
		$(VENV_BIN)/poetry install --all-extras --with dev || true
	@echo ""
	@echo "📦 Instalando projetos locais em modo desenvolvimento..."
	@. $(VENV_DIR)/bin/activate && \
	for proj in flx flx-database-oracle flx-http-oracle-oic flx-http-oracle-wms client-a-mig-oud client-b-poc-oic-wms flx-adapter-example; do \
		if [ -d "$$proj" ]; then \
			echo "  → Instalando $$proj..."; \
			cd $(WORKSPACE_ROOT)/$$proj && \
				if [ ! -f poetry.lock ] || [ pyproject.toml -nt poetry.lock ]; then \
					$(VENV_BIN)/poetry lock --no-update || true; \
				fi && \
				$(VENV_BIN)/poetry install --all-extras || $(VENV_BIN)/poetry install || true; \
		fi; \
	done
	@echo ""
	@echo "🔗 Instalando projetos em modo editable para desenvolvimento..."
	@. $(VENV_DIR)/bin/activate && cd $(WORKSPACE_ROOT) && \
		$(VENV_BIN)/pip install -e flx/ && \
		$(VENV_BIN)/pip install -e flx-database-oracle/ && \
		$(VENV_BIN)/pip install -e flx-http-oracle-oic/ && \
		$(VENV_BIN)/pip install -e flx-http-oracle-wms/ && \
		$(VENV_BIN)/pip install -e client-a-mig-oud/ && \
		$(VENV_BIN)/pip install -e client-b-poc-oic-wms/ && \
		$(VENV_BIN)/pip install -e flx-adapter-example/
	@echo ""
	@echo "✅ Validando instalação..."
	@. $(VENV_DIR)/bin/activate && cd $(WORKSPACE_ROOT) && \
		$(VENV_BIN)/python -c "import flx, flx_database_oracle, flx_http_oracle_oic, flx_http_oracle_wms, client-a_oud_mig, gn_oic_wms_db; print('✅ Todos os imports funcionando!')" || \
		echo "⚠️ Alguns imports falharam - verificar logs"
	@echo ""
	@echo "📊 Total de pacotes instalados:"
	@$(VENV_BIN)/pip list | wc -l
	$(call success,Instalação completa do workspace PyAuto finalizada!)

## install-workspace-clean: Reinstala TUDO do zero (remove .venv e recria)
install-workspace-clean: venv-clean venv-setup install-workspace
	$(call success,Workspace PyAuto completamente reinstalado do zero!)

## install-editable: Instala apenas os projetos locais em modo editable
install-editable: venv-check
	$(call section,Instalando projetos locais em modo editable)
	@cd $(WORKSPACE_ROOT) && \
		$(POETRY) run pip install -e flx/ && \
		$(POETRY) run pip install -e flx-database-oracle/ && \
		$(POETRY) run pip install -e flx-http-oracle-oic/ && \
		$(POETRY) run pip install -e flx-http-oracle-wms/ && \
		$(POETRY) run pip install -e client-a-mig-oud/ && \
		$(POETRY) run pip install -e client-b-poc-oic-wms/ && \
		$(POETRY) run pip install -e flx-adapter-example/
	$(call success,Projetos instalados em modo editable)

## update: Atualiza dependências
update: venv-check
	$(call run_for_projects,update,Atualizando dependências,\
		if [ ! -f poetry.lock ] || [ pyproject.toml -nt poetry.lock ]; then \
			$(POETRY) lock || true; \
		fi; \
		$(POETRY) update || true \
	)
	$(call success,Dependências atualizadas)

## update-dry-run: Simula atualização de dependências
update-dry-run: venv-check
	$(call run_for_projects,update-dry-run,Simulando atualização de dependências,\
		$(POETRY) update --dry-run || true \
	)
	$(call success,Simulação de atualização completada)

## remove-locks: Remove arquivos poetry.lock
remove-locks:
	$(call section,Removendo arquivos de lock)
	@find . -name "poetry.lock" -delete
	$(call success,Arquivos de lock removidos)

## sync-dependencies: Sincroniza versões entre projetos
sync-dependencies: venv-check
	$(call section,Sincronizando versões de dependências entre projetos)
	@python $(SCRIPTS_DIR)/utilities/sync_dependencies.py \
		$(if $(FORCE),--force,) \
		$(if $(PROJECT),--flx_project $(PROJECT),) \
		$(if $(DRY_RUN),--dry-run,) \
		$(if $(CONSOLIDATE),--consolidate,) \
		$(if $(SOURCE),--source $(SOURCE),)
	$(call success,Sincronização de dependências completada)

## upgrade-deps: Remove locks e atualiza dependências
upgrade-deps: remove-locks update

## update-python-version: Propaga versão do Python para todos os pyproject.toml
update-python-version:
	$(call section,Atualizando versão do Python para $(PYTHON_VERSION) em todos os projetos)
	@for flx_project in $(notdir $(PROJECTS)); do \
		if [ -f "$$flx_project/pyproject.toml" ]; then \
			echo "Atualizando $$flx_project/pyproject.toml..."; \
			sed -i -E \
				's/(^python\s*=\s*"\^)[0-9.]+(")/\1$(PYTHON_VERSION)\2/' \
				"$$flx_project/pyproject.toml" || true; \
			sed -i -E \
				's/(requires-python\s*=\s*">=)[0-9.]+(")/\1$(PYTHON_VERSION)\2/' \
				"$$flx_project/pyproject.toml" || true; \
		fi; \
	done
	$(call success,Versão do Python atualizada em todos os projetos)

## check-poetry-lock: Verifica se poetry.lock está sincronizado
check-poetry-lock: venv-check
	$(call section,Verificando sincronização do poetry.lock)
	@bash $(VENV_SCRIPT) check-lock
	$(call success,Verificação do poetry.lock completada)

## update-poetry-lock: Atualiza poetry.lock se necessário
update-poetry-lock: venv-check
	$(call section,Atualizando poetry.lock se necessário)
	@bash $(VENV_SCRIPT) update-lock
	$(call success,poetry.lock atualizado)

## force-poetry-lock: Força regeneração do poetry.lock
force-poetry-lock: venv-check
	$(call section,Forçando regeneração do poetry.lock)
	@bash $(VENV_SCRIPT) force-lock
	$(call success,poetry.lock regenerado)

## fix-poetry-deps: Corrige problemas de dependências do Poetry
fix-poetry-deps: force-poetry-lock install-dev

# ───────────────────────────────────────────────────────────────────────────
#  PYPROJECT TEMPLATE COMPLIANCE
# ───────────────────────────────────────────────────────────────────────────

## pyproject-template-validate: Validates all projects against enterprise template
pyproject-template-validate: venv-check
	$(call section,Validating PyProject Template Compliance)
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) $(SCRIPTS_DIR)/validate_pyproject_compliance.py
	$(call success,PyProject template validation completed)

## pyproject-template-apply: Applies enterprise template to all projects
pyproject-template-apply: venv-check
	$(call section,Applying PyProject Template to All Projects)
	@if [ -z "$(FORCE)" ]; then \
		$(call warning,This will overwrite all pyproject.toml files); \
		$(call warning,Use FORCE=1 to confirm: make pyproject-template-apply FORCE=1); \
		exit 1; \
	fi
	@echo "Applying enterprise template to all projects..."
	@for proj in $(ALL_PROJECT_NAMES); do \
		if [ -f "$$proj/pyproject.toml" ]; then \
			echo "  → Backing up $$proj/pyproject.toml..."; \
			cp "$$proj/pyproject.toml" "$$proj/pyproject.toml.backup"; \
		fi; \
		echo "  → Applying template to $$proj..."; \
		cp pyproject-template.toml "$$proj/pyproject.toml"; \
		if [ -f "$$proj/src" ]; then \
			PROJECT_MODULE=$$(echo "$$proj" | sed 's/-/_/g'); \
			sed -i "s/PROJECT_NAME/$$proj/g" "$$proj/pyproject.toml"; \
			sed -i "s/PROJECT_MODULE/$$PROJECT_MODULE/g" "$$proj/pyproject.toml"; \
		fi; \
	done
	$(call success,Enterprise template applied to all projects)

## pyproject-template-customize: Customizes template for specific project
pyproject-template-customize:
	$(call require_project,pyproject-template-customize)
	$(call section,Customizing PyProject Template for $(PROJECT))
	@if [ ! -f "$(PROJECT)/pyproject.toml" ]; then \
		$(call error,Project $(PROJECT) does not have pyproject.toml file); \
		exit 1; \
	fi
	@PROJECT_MODULE=$$(echo "$(PROJECT)" | sed 's/-/_/g'); \
		sed -i "s/PROJECT_NAME/$(PROJECT)/g" "$(PROJECT)/pyproject.toml"; \
		sed -i "s/PROJECT_MODULE/$$PROJECT_MODULE/g" "$(PROJECT)/pyproject.toml"
	$(call success,Template customized for $(PROJECT))

## pyproject-template-status: Shows compliance status for all projects
pyproject-template-status: venv-check
	$(call section,PyProject Template Compliance Status)
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) $(SCRIPTS_DIR)/validate_pyproject_compliance.py --status-only || true
	$(call success,Compliance status report completed)

# ───────────────────────────────────────────────────────────────────────────
#  QUALITY ASSURANCE
# ───────────────────────────────────────────────────────────────────────────

## check-script-locations: Verifica se scripts estão nas pastas corretas
check-script-locations:
	$(call run_command,check-script-locations,\
		Verificando localização de scripts,\
		$(PYTHON) $(SCRIPTS_DIR)/utils/script_validation.py \
	)

## cleanup-temp-scripts: Remove scripts temporários antigos (MAX_AGE=30)
cleanup-temp-scripts:
	$(call run_command,cleanup-temp-scripts,\
		Removendo scripts temporários antigos,\
		$(PYTHON) $(SCRIPTS_DIR)/maintenance/cleanup_temp_scripts.py \
			$(if $(MAX_AGE),--max-age $(MAX_AGE),) \
			$(if $(DRY_RUN),--dry-run,) \
	)

## cleanup-temp-scripts-dry: Simula limpeza de scripts temporários
cleanup-temp-scripts-dry:
	$(call run_command,cleanup-temp-scripts-dry,\
		Simulando limpeza de scripts temporários,\
		$(PYTHON) $(SCRIPTS_DIR)/maintenance/cleanup_temp_scripts.py --dry-run \
			$(if $(MAX_AGE),--max-age $(MAX_AGE),) \
	)

## validate-scripts: Executa todas as validações de scripts
validate-scripts: check-script-locations cleanup-temp-scripts-dry
	$(call success,Validações de scripts concluídas)

## standardize: Executa todas as padronizações
standardize: standardize-linting pep8-compliance setup-hooks validate-scripts

## standardize-linting: Padroniza configurações de lint
standardize-linting:
	$(call run_command,standardize-linting,\
		Padronizando configurações de lint,\
		$(PYTHON) $(PROJECT_MANAGE) standardize-linting \
	)

## pep8-compliance: Aplica padrões PEP-8
pep8-compliance:
	$(call run_command,pep8-compliance,\
		Aplicando padrões PEP-8,\
		$(PYTHON) $(PROJECT_MANAGE) pep8-compliance \
	)

## pep8-check: Verifica conformidade com PEP-8
pep8-check:
	$(call run_command,pep8-check,\
		Verificando conformidade com PEP-8,\
		$(PYTHON) $(PROJECT_MANAGE) pep8-check \
	)

## pep8-apply: Aplica padrões PEP8 em todos os projetos
pep8-apply: venv-check
	$(call section,Aplicando padrões PEP8 em todos os projetos)
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) $(SCRIPTS_DIR)/utilities/apply_pep8_standards.py
	$(call success,Padrões PEP8 aplicados em todos os projetos)

## pep8-apply-dry: Simula aplicação de padrões PEP8
pep8-apply-dry: venv-check
	$(call section,Simulando aplicação de padrões PEP8)
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) $(SCRIPTS_DIR)/utilities/apply_pep8_standards.py --dry-run
	$(call success,Simulação completada)

## pep8-validate: Valida conformidade PEP8 de todos os projetos
pep8-validate: venv-check
	$(call section,Validando conformidade PEP8)
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) $(SCRIPTS_DIR)/utilities/apply_pep8_standards.py --validate-only
	$(call success,Validação PEP8 completada)

## setup-hooks: Instala pre-commit hooks
setup-hooks:
	$(call run_command,setup-hooks,\
		Instalando hooks de pre-commit,\
		$(PYTHON) $(PROJECT_MANAGE) setup-hooks \
	)

# ───────────────────────────────────────────────────────────────────────────
#  VERSION CONTROL
# ───────────────────────────────────────────────────────────────────────────

## git-status: Mostra status do Git
git-status:
	$(call run_command,git-status,\
		Status do Git,\
		$(PYTHON) $(GIT_MANAGE) status \
	)

## git-fetch: Busca atualizações do Git
git-fetch:
	$(call run_command,git-fetch,\
		Buscando atualizações Git,\
		$(PYTHON) $(GIT_MANAGE) fetch \
	)

## git-commit: Commit de alterações (COMMIT_MESSAGE=msg)
git-commit:
	$(call run_command,git-commit,\
		Commitando alterações,\
		$(PYTHON) $(GIT_MANAGE) commit \
			$(if $(COMMIT_MESSAGE),"$(COMMIT_MESSAGE)",) \
	)

## git-push: Envia commits para repositório remoto
git-push:
	$(call run_command,git-push,\
		Enviando commits,\
		$(PYTHON) $(GIT_MANAGE) push \
	)

# ───────────────────────────────────────────────────────────────────────────
#  PROJECT MANAGEMENT
# ───────────────────────────────────────────────────────────────────────────

## list-projects: Lista projetos detectados
list-projects:
	$(call section,Projetos detectados)
	@echo "$(BOLD)Projetos na workspace:$(NC)" | \
		tee -a $(LOGFILE_DIR)/list-projects.log
	@for flx_project in $(notdir $(PROJECTS)); do \
		echo "  - $$flx_project" | \
			tee -a $(LOGFILE_DIR)/list-projects.log; \
	done

## status: Mostra status dos projetos
status:
	$(call run_command,status,\
		Status dos projetos,\
		$(PYTHON) $(PROJECT_MANAGE) status \
	)

## new-flx_project: Cria novo projeto (name=abc)
new-flx_project:
	$(call run_command,new-flx_project,\
		Criando novo projeto,\
		$(PYTHON) $(SCAFFOLD_MANAGE) create $(name) \
	)

## scaffold-status: Mostra status do scaffold
scaffold-status:
	$(call run_command,scaffold-status,\
		Status do scaffold,\
		$(PYTHON) $(SCAFFOLD_MANAGE) status \
	)

## sync-scaffold: Sincroniza scaffold com projeto
sync-scaffold:
	$(call run_command,sync-scaffold,\
		Sincronizando projeto com scaffold,\
		$(PYTHON) $(SCAFFOLD_MANAGE) sync \
			$(if $(flx_project),--flx_project $(flx_project),) \
			$(if $(direction),--direction $(direction),) \
	)

## list-projects-deps: Lista projetos detectados para sincronização
list-projects-deps: venv-check
	$(call section,Listando projetos para sincronização de dependências)
	@python $(SCRIPTS_DIR)/utilities/sync_dependencies.py --list-projects
	$(call success,Lista de projetos exibida)

# ═══════════════════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════════════════

help:
	@echo "$(YELLOW)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║  Workspace PyAuto - Comandos disponíveis                       ║$(NC)"
	@echo "$(YELLOW)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BOLD)$(GREEN)Virtual Environment:$(NC)"
	@echo "  venv-check          Verifica integridade do ambiente virtual"
	@echo "  venv-install        Instala dependências principais"
	@echo "  venv-install-dev    Instala dependências de desenvolvimento"
	@echo "  venv-setup          Configuração inicial completa do ambiente"
	@echo "  venv-rebuild        Reconstrói ambiente virtual do zero"
	@echo "  venv-clean          Remove ambiente virtual"
	@echo "  venv-status         Mostra status do ambiente virtual"
	@echo ""
	@echo "$(BOLD)$(GREEN)Aliases (compatibilidade):$(NC)"
	@echo "  install             Alias para venv-install"
	@echo "  install-dev         Alias para venv-install-dev"
	@echo "  setup               Alias para venv-setup"
	@echo ""
	@echo "$(BOLD)$(GREEN)Cleanup:$(NC)"
	@echo "  clean               Limpa artefatos de build e cache"
	@echo ""
	@echo "$(CYAN)Para comandos abaixo: todos os projetos ou específico PROJECT=nome$(NC)"
	@echo ""
	@echo "$(BOLD)$(GREEN)Standardized Project Coordination:$(NC)"
	@echo "  project-run         Executa qualquer target em um projeto (PROJECT=nome TARGET=comando)"
	@echo "  project-status      Mostra status de um projeto ou todos"
	@echo "  project-validate    Valida estrutura de projetos"
	@echo "  projects-report     Gera relatório consolidado de todos os projetos"
	@echo ""
	@echo "$(BOLD)$(GREEN)Dependency Management:$(NC)"
	@echo "  $(BOLD)install-workspace   🚀 Instala TODAS as dependências do PyAuto via Poetry$(NC)"
	@echo "  $(BOLD)install-workspace-clean 🔄 Reinstala TUDO do zero (remove e recria .venv)$(NC)"
	@echo "  install-editable    Instala projetos locais em modo editable"
	@echo "  install-all         Instala todas as dependências (todos os grupos)"
	@echo "  update              Atualiza dependências"
	@echo "  update-dry-run      Simula atualização de dependências"
	@echo "  remove-locks        Remove arquivos poetry.lock"
	@echo "  sync-dependencies   Sincroniza versões entre projetos"
	@echo "  upgrade-deps        Remove locks e atualiza dependências"
	@echo "  check-poetry-lock   Verifica se poetry.lock está sincronizado"
	@echo "  update-poetry-lock  Atualiza poetry.lock se necessário"
	@echo "  force-poetry-lock   Força regeneração do poetry.lock"
	@echo "  fix-poetry-deps     Corrige problemas de dependências do Poetry"
	@echo ""
	@echo "$(BOLD)$(GREEN)Development:$(NC)"
	@echo "  test                Executa testes (COV=1 JUNIT=1 VERBOSE=1)"
	@echo "  test-cov            Executa testes com cobertura"
	@echo "  test-junit          Executa testes com relatório JUnit"
	@echo "  test-verbose        Executa testes com saída detalhada"
	@echo "  lint                Executa verificação de código (CHECK=1 SECURITY=1)"
	@echo "  lint-check          Verifica erros de lint sem correção"
	@echo "  lint-security       Verifica problemas de segurança"
	@echo "  fix                 Executa todas as correções automáticas"
	@echo "  fix-ruff            Executa correções automáticas com Ruff"
	@echo "  fix-isort           Organiza imports com isort"
	@echo "  fix-black           Formata código com Black"
	@echo "  upgrade-syntax      Atualiza sintaxe Python para versão mais recente"
	@echo "  format              Formata código (alias para fix-black)"
	@echo "  build               Constrói pacotes"
	@echo ""
	@echo "$(BOLD)$(GREEN)PyProject Template Compliance:$(NC)"
	@echo "  $(BOLD)pyproject-template-validate   🔍 Validates all projects against enterprise template$(NC)"
	@echo "  $(BOLD)pyproject-template-apply      ⚠️  Applies template to ALL projects (FORCE=1 required)$(NC)"
	@echo "  pyproject-template-customize  Customizes template for specific project (PROJECT=name)"
	@echo "  pyproject-template-status     Shows compliance status for all projects"
	@echo ""
	@echo "$(BOLD)$(GREEN)Quality Assurance:$(NC)"
	@echo "  standardize         Executa todas as padronizações"
	@echo "  standardize-linting Padroniza configurações de lint"
	@echo "  pep8-compliance     Aplica padrões PEP-8"
	@echo "  pep8-check          Verifica conformidade com PEP-8"
	@echo "  setup-hooks         Instala pre-commit hooks"
	@echo "  check-script-locations Verifica se scripts estão nas pastas corretas"
	@echo "  cleanup-temp-scripts Remove scripts temporários antigos (MAX_AGE=30)"
	@echo "  cleanup-temp-scripts-dry Simula limpeza de scripts temporários"
	@echo "  validate-scripts    Executa todas as validações de scripts"
	@echo ""
	@echo "$(BOLD)$(GREEN)Version Control:$(NC)"
	@echo "  git-status          Mostra status do Git"
	@echo "  git-fetch           Busca atualizações do Git"
	@echo "  git-commit          Commit de alterações (COMMIT_MESSAGE=msg)"
	@echo "  git-push            Envia commits para repositório remoto"
	@echo ""
	@echo "$(BOLD)$(GREEN)Project Management:$(NC)"
	@echo "  list-projects       Lista projetos detectados"
	@echo "  list-projects-deps  Lista projetos para sincronização de dependências"
	@echo "  status              Mostra status dos projetos"
	@echo "  new-flx_project         Cria novo projeto (name=abc)"
	@echo "  scaffold-status     Mostra status do scaffold"
	@echo "  sync-scaffold       Sincroniza scaffold com projeto"
	@echo ""
	@echo "$(BOLD)$(YELLOW)Controle de Cores:$(NC)"
	@echo "  NO_COLOR=1          Desabilita todas as cores"
	@echo "  make help NO_COLOR=1    Exemplo sem cores"
	@echo ""
	@echo "$(YELLOW)Projetos detectados:$(NC) $(notdir $(PROJECTS))"
	@echo "$(CYAN)Para executar em projeto específico: make <comando> PROJECT=nome$(NC)"
	@echo "$(CYAN)Logs salvos em: $(LOGFILE_DIR)$(NC)"
