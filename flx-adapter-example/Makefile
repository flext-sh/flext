###############################################################################
#  Scaffold Python Project Makefile
#  Simple flx_project-specific targets that integrate with root workspace
###############################################################################

# ───────────────═[ Basic Configuration ]═─────────────────────────────────────
WORKSPACE_ROOT ?= $(shell git -C "$(CURDIR)" rev-parse --show-toplevel 2>/dev/null || echo "$(CURDIR)")
PROJECT_ROOT   := $(CURDIR)
PROJECT_NAME   := $(notdir $(PROJECT_ROOT))
PACKAGE_NAME   := project_name

# ───────────────═[ Commands ]═───────────────────────────────────────────────
POETRY     := poetry

# ───────────────═[ Targets ]═─────────────────────────────────────────────────
.DEFAULT_GOAL := help

## Project-specific commands
## ------------------------

## install: Instala dependências do projeto
install:
	@echo "→ Instalando dependências do projeto $(PROJECT_NAME)"
	@$(POETRY) install

## install-dev: Instala dependências de desenvolvimento
install-dev:
	@echo "→ Instalando dependências de desenvolvimento do projeto $(PROJECT_NAME)"
	@$(POETRY) install --with dev

## update: Atualiza dependências do projeto
update:
	@echo "→ Atualizando dependências do projeto $(PROJECT_NAME)"
	@$(POETRY) update

## build: Constrói o pacote do projeto
build:
	@echo "→ Construindo pacote do projeto $(PROJECT_NAME)"
	@$(POETRY) build

## clean: Limpa artefatos do projeto
clean:
	@echo "→ Limpando artefatos do projeto $(PROJECT_NAME)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".coverage" -delete
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

## test: Executa testes do projeto
test:
	@echo "→ Executando testes do projeto $(PROJECT_NAME)"
	@if [ -d "tests" ]; then \
		$(POETRY) run pytest tests/; \
	else \
		echo "Nenhum diretório de testes encontrado."; \
	fi

## lint: Executa lint no projeto
lint:
	@echo "→ Executando lint no projeto $(PROJECT_NAME)"
	@$(POETRY) run ruff check .

## format: Formata código do projeto
format:
	@echo "→ Formatando código do projeto $(PROJECT_NAME)"
	@$(POETRY) run black . && $(POETRY) run isort .

## lint-fix: Corrige problemas de lint automaticamente
lint-fix:
	@echo "→ Corrigindo problemas de lint do projeto $(PROJECT_NAME)"
	@$(POETRY) run ruff check --fix . && $(POETRY) run isort . && $(POETRY) run black .

## Security check
security:
	@echo "→ Verificando segurança do projeto $(PROJECT_NAME)"
	@$(POETRY) run bandit -r . -x test

## standardize: Executa padrões no projeto (formatação + lint)
standardize: format lint-fix

## Integration with workspace
## ------------------------
## workspace: Executa comando no workspace (CMD=comando)
workspace:
	@echo "→ Executando comando no workspace: $(CMD)"
	@cd $(WORKSPACE_ROOT) && make $(CMD) PROJECT=$(PROJECT_NAME)

## root-lint: Utiliza as ferramentas de lint do workspace
root-lint:
	@cd $(WORKSPACE_ROOT) && make -f Makefile.lint lint-fix-all

## root-format: Utiliza as ferramentas de formatação do workspace
root-format:
	@cd $(WORKSPACE_ROOT) && make format PROJECT=$(PROJECT_NAME)

## root-test: Executa testes via workspace
root-test:
	@cd $(WORKSPACE_ROOT) && make test PROJECT=$(PROJECT_NAME)

.PHONY: help
help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  Projeto: $(PROJECT_NAME)"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Comandos do projeto:"
	@echo "  install         Instala dependências do projeto"
	@echo "  install-dev     Instala dependências de desenvolvimento"
	@echo "  update          Atualiza dependências do projeto"
	@echo "  build           Constrói o pacote do projeto"
	@echo "  clean           Limpa artefatos do projeto"
	@echo "  test            Executa testes do projeto"
	@echo "  lint            Executa lint no projeto"
	@echo "  format          Formata código do projeto"
	@echo "  lint-fix        Corrige problemas de lint automaticamente"
	@echo "  security        Verifica segurança do código"
	@echo "  standardize     Executa padrões no projeto (formatação + lint)"
	@echo ""
	@echo "Integração com workspace:"
	@echo "  workspace       Executa comando no workspace (CMD=comando)"
	@echo "  root-lint       Utiliza as ferramentas de lint do workspace"
	@echo "  root-format     Utiliza as ferramentas de formatação do workspace"
	@echo "  root-test       Executa testes via workspace"
	@echo ""
	@echo "Para executar comandos avançados e logs, use: make workspace CMD=comando" 
