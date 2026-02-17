#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# =============================================================================
# FLEXT Monorepo - Remove External Project
# =============================================================================
# Removes an external project from the monorepo workspace.
# Unregisters from .flext/external-projects.json and optionally removes directory.
# =============================================================================

set -euo pipefail

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# Ensure we're in the flext root
cd "$SCRIPT_DIR/.."
require_flext_root
ensure_jq

# =============================================================================
# ARGUMENTS
# =============================================================================

PROJECT="${1:-}"

if [[ -z $PROJECT ]]; then
	echo ""
	echo "Uso: $0 <project-name>"
	echo ""
	echo "Projetos externos registrados:"
	list_external_projects | while read -r p; do
		local org
		org=$(get_project_info "$p" "org")
		echo "  - $p ($org)"
	done
	echo ""
	exit 1
fi

# =============================================================================
# MAIN
# =============================================================================

box "Remover Projeto Externo"

# 1. Check if project is registered
if ! is_external_project "$PROJECT"; then
	error "Projeto $PROJECT nao esta registrado como externo"
	echo -e "  ${DIM}Verifique com: make discover${NC}"
	exit 1
fi

# Get project info before removal
ORG=$(get_project_info "$PROJECT" "org")
URL=$(get_project_info "$PROJECT" "url")

echo ""
info "Projeto: $PROJECT"
info "Organizacao: $ORG"
info "URL: $URL"

# 2. Confirm removal
echo ""
if ! confirm "Remover projeto $PROJECT do workspace?" "n"; then
	info "Cancelado"
	exit 0
fi

# 3. Remove from external-projects.json
echo ""
info "Removendo de .flext/external-projects.json..."
jq "del(.projects[\"$PROJECT\"])" .flext/external-projects.json >.flext/external-projects.json.tmp
mv .flext/external-projects.json.tmp .flext/external-projects.json
success "Removido de .flext/external-projects.json"

# 4. Remove from pyproject.toml
echo ""
info "Removendo de pyproject.toml..."
python3 <<EOF || true
try:
    import tomlkit
    with open('pyproject.toml', 'r') as f:
        doc = tomlkit.load(f)

    if 'tool' in doc and 'poetry' in doc['tool'] and 'dependencies' in doc['tool']['poetry']:
        if '${PROJECT}' in doc['tool']['poetry']['dependencies']:
            del doc['tool']['poetry']['dependencies']['${PROJECT}']
            with open('pyproject.toml', 'w') as f:
                tomlkit.dump(doc, f)
            print("OK")
        else:
            print("NOT_FOUND")
    else:
        print("NOT_FOUND")
except ImportError:
    print("SKIP")
EOF
success "Removido de pyproject.toml"

# 5. Remove directory
echo ""
if [[ -d "./$PROJECT" ]]; then
	if confirm "Remover diretorio ./$PROJECT?" "n"; then
		# Check for uncommitted changes
		if has_changes "./$PROJECT"; then
			warn "Existem mudancas nao commitadas em $PROJECT"
			if ! confirm "Remover mesmo assim? (mudancas serao perdidas)" "n"; then
				info "Diretorio mantido"
			else
				rm -rf "./$PROJECT"
				success "Diretorio removido"
			fi
		else
			rm -rf "./$PROJECT"
			success "Diretorio removido"
		fi
	else
		info "Diretorio mantido em ./$PROJECT"
	fi
else
	info "Diretorio ./$PROJECT nao existe"
fi

# 6. Update poetry.lock
echo ""
if confirm "Executar poetry lock?" "n"; then
	info "Atualizando poetry.lock..."
	if poetry lock --no-update 2>/dev/null; then
		success "Lock atualizado"
	else
		warn "poetry lock falhou - execute manualmente depois"
	fi
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Projeto $PROJECT removido do workspace"
echo ""
