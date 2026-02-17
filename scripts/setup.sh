#!/bin/bash
# =============================================================================
# FLEXT Monorepo - Interactive Setup
# =============================================================================
# Initial setup for the FLEXT workspace with interactive configuration.
# =============================================================================

set -euo pipefail

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# Ensure we're in the flext root
cd "$SCRIPT_DIR/.."

# =============================================================================
# MAIN
# =============================================================================

box "FLEXT Monorepo Setup"

# 1. Check Python version
echo ""
header "Verificando Python"
if command -v python3.13 &>/dev/null; then
	PYTHON_VERSION=$(python3.13 --version 2>&1)
	success "Python 3.13 encontrado: $PYTHON_VERSION"
elif command -v python3 &>/dev/null; then
	PYTHON_VERSION=$(python3 --version 2>&1)
	if [[ $PYTHON_VERSION =~ 3\.13 ]]; then
		success "Python 3.13 encontrado: $PYTHON_VERSION"
	else
		warn "Python encontrado mas nao e 3.13: $PYTHON_VERSION"
		info "FLEXT requer Python 3.13+"
	fi
else
	error "Python 3 nao encontrado"
	exit 1
fi

# 2. Installation mode
echo ""
header "Modo de Instalacao"
MODE=$(select_option "Como deseja configurar o workspace?" \
	"dev - Desenvolvedor (editable, todos os projetos)" \
	"user - Usuario (via GitHub, apenas runtime)" \
	"minimal - Minimo (flext-core + cli apenas)")

case $MODE in
1) MODE="dev" ;;
2) MODE="user" ;;
3) MODE="minimal" ;;
*) MODE="dev" ;;
esac

info "Modo selecionado: $MODE"

# 3. Virtual environment
echo ""
header "Ambiente Virtual"
VENV_PATH=".venv"
if [[ -d $VENV_PATH ]]; then
	info "venv existente encontrado em $VENV_PATH"
	if confirm "Usar venv existente?"; then
		CREATE_VENV=false
	else
		CREATE_VENV=true
	fi
else
	CREATE_VENV=true
fi

if $CREATE_VENV && confirm "Criar venv em $VENV_PATH?"; then
	info "Criando ambiente virtual..."
	python3 -m venv "$VENV_PATH"
	success "venv criado em $VENV_PATH"
fi

# Activate venv for subsequent commands
if [[ -f "$VENV_PATH/bin/activate" ]]; then
	source "$VENV_PATH/bin/activate"
	success "venv ativado"
fi

# 4. Poetry installation
echo ""
header "Poetry"
if command -v poetry &>/dev/null; then
	POETRY_VERSION=$(poetry --version 2>&1)
	success "Poetry encontrado: $POETRY_VERSION"
else
	warn "Poetry nao encontrado"
	if confirm "Instalar Poetry?"; then
		info "Instalando Poetry..."
		curl -sSL https://install.python-poetry.org | python3 -
		success "Poetry instalado"
		export PATH="$HOME/.local/bin:$PATH"
	fi
fi

# 5. Poetry plugins (dev mode only)
if [[ $MODE == "dev" ]]; then
	echo ""
	header "Plugins Poetry"
	if confirm "Instalar plugins para monorepo?"; then
		info "Instalando poetry-plugin-mono-repo-deps..."
		poetry self add poetry-plugin-mono-repo-deps 2>/dev/null ||
			warn "Plugin ja instalado ou falha na instalacao"
		success "Plugins configurados"
	fi
fi

# 6. Git submodules (dev mode only)
if [[ $MODE == "dev" ]]; then
	echo ""
	header "Git Submodules (flext-sh)"
	if [[ -f ".gitmodules" ]]; then
		SUBMODULE_COUNT=$(grep -c "path = " .gitmodules 2>/dev/null || echo "0")
		info "$SUBMODULE_COUNT submodules definidos em .gitmodules"

		if confirm "Inicializar/atualizar submodules?"; then
			info "Inicializando submodules..."
			git submodule init
			git submodule update --recursive
			success "Submodules atualizados"
		fi
	else
		warn ".gitmodules nao encontrado"
	fi
fi

# 7. External projects
if [[ $MODE == "dev" ]]; then
	echo ""
	header "Projetos Externos (datacosmos-br)"
	if [[ -f ".flext/external-projects.json" ]]; then
		EXTERNAL_COUNT=$(jq '.projects | length' .flext/external-projects.json 2>/dev/null || echo "0")

		if [[ $EXTERNAL_COUNT -gt 0 ]]; then
			info "$EXTERNAL_COUNT projetos externos registrados:"
			jq -r '.projects | to_entries[] | "  - \(.key) (\(.value.org))"' .flext/external-projects.json

			echo ""
			if confirm "Clonar projetos externos faltantes?"; then
				jq -r '.projects | to_entries[] | "\(.key)|\(.value.url)|\(.value.branch)"' .flext/external-projects.json |
					while IFS='|' read -r name url branch; do
						if [[ ! -d "./$name" ]]; then
							info "Clonando $name..."
							git clone -b "$branch" "$url" "./$name" 2>/dev/null &&
								success "$name clonado" ||
								warn "Falha ao clonar $name"
						else
							info "$name ja existe"
						fi
					done
			fi
		else
			info "Nenhum projeto externo registrado"
			info "Use 'make add-project' para adicionar projetos externos"
		fi
	fi
fi

# 8. Install dependencies
echo ""
header "Instalacao de Dependencias"

case $MODE in
dev)
	if confirm "Instalar todas as dependencias (poetry install)?"; then
		info "Instalando dependencias..."
		poetry install --all-extras 2>/dev/null &&
			success "Dependencias instaladas" ||
			warn "Algumas dependencias podem ter falhado"
	fi
	;;
user)
	if confirm "Instalar dependencias via GitHub?"; then
		info "Instalando via GitHub..."
		poetry install -E github 2>/dev/null &&
			success "Dependencias instaladas" ||
			warn "Algumas dependencias podem ter falhado"
	fi
	;;
minimal)
	if confirm "Instalar dependencias minimas?"; then
		info "Instalando dependencias minimas..."
		poetry install 2>/dev/null &&
			success "Dependencias instaladas" ||
			warn "Algumas dependencias podem ter falhado"
	fi
	;;
esac

# 9. Verify installation
echo ""
header "Verificacao"

# Count projects
TOTAL_PROJECTS=0
SUBMODULE_PROJECTS=0
EXTERNAL_PROJECTS=0

if [[ -f ".gitmodules" ]]; then
	SUBMODULE_PROJECTS=$(grep -c "path = " .gitmodules 2>/dev/null || echo "0")
fi

if [[ -f ".flext/external-projects.json" ]]; then
	EXTERNAL_PROJECTS=$(jq '.projects | length' .flext/external-projects.json 2>/dev/null || echo "0")
fi

TOTAL_PROJECTS=$((SUBMODULE_PROJECTS + EXTERNAL_PROJECTS))

info "Projetos core (flext-sh): $SUBMODULE_PROJECTS"
info "Projetos externos: $EXTERNAL_PROJECTS"
info "Total: $TOTAL_PROJECTS"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Setup concluido!"
echo ""
echo -e "  ${DIM}Modo:${NC}     $MODE"
echo -e "  ${DIM}venv:${NC}     $VENV_PATH"
echo -e "  ${DIM}Projetos:${NC} $TOTAL_PROJECTS"
echo ""
echo -e "  ${DIM}Proximos passos:${NC}"
echo "    source $VENV_PATH/bin/activate  # Ativar venv"
echo "    make check                       # Validar projetos"
echo "    make add-project                 # Adicionar projeto externo"
echo ""
