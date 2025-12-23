#!/bin/bash
# =============================================================================
# FLEXT Monorepo - Add External Project
# =============================================================================
# Adds an external project (datacosmos-br, etc.) to the monorepo workspace.
# The project is cloned, registered in .flext/external-projects.json,
# added to pyproject.toml as an editable dependency, and added to .gitignore.
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
# MAIN
# =============================================================================

box "Adicionar Projeto Externo"

# 1. Project name
echo ""
PROJECT=$(prompt_value "Nome do projeto" "")
if [[ -z "$PROJECT" ]]; then
    error "Nome do projeto e obrigatorio"
    exit 1
fi

# 2. Check if already exists
if project_exists "$PROJECT"; then
    error "Diretorio $PROJECT ja existe"
    exit 1
fi

if is_external_project "$PROJECT"; then
    error "Projeto $PROJECT ja esta registrado em .flext/external-projects.json"
    exit 1
fi

# 3. Organization selection
ORG_CHOICE=$(select_option "Organizacao GitHub?" \
    "datacosmos-br (Recomendado para client-a/client-b)" \
    "flext-sh" \
    "Outra")

case $ORG_CHOICE in
    1) ORG="datacosmos-br" ;;
    2) ORG="flext-sh" ;;
    3) ORG=$(prompt_value "Nome da organizacao" "") ;;
    *) ORG="datacosmos-br" ;;
esac

if [[ -z "$ORG" ]]; then
    error "Organizacao e obrigatoria"
    exit 1
fi

# 4. Branch
BRANCH=$(prompt_value "Branch" "main")

# 5. Build URL
URL="git@github.com:${ORG}/${PROJECT}.git"
HTTPS_URL="https://github.com/${ORG}/${PROJECT}.git"

echo ""
info "URL SSH: $URL"
info "URL HTTPS: $HTTPS_URL"

# 6. Clone repository
echo ""
if confirm "Clonar repositorio agora?"; then
    echo ""
    info "Clonando $PROJECT..."

    if git clone -b "$BRANCH" "$URL" "./$PROJECT" 2>/dev/null; then
        success "Clonado via SSH para ./$PROJECT"
    elif git clone -b "$BRANCH" "$HTTPS_URL" "./$PROJECT" 2>/dev/null; then
        success "Clonado via HTTPS para ./$PROJECT"
    else
        error "Falha ao clonar repositorio"
        echo -e "  ${DIM}Verifique se o repositorio existe e voce tem acesso${NC}"
        exit 1
    fi
fi

# 7. Register in external-projects.json
echo ""
info "Registrando em .flext/external-projects.json..."

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
jq --arg name "$PROJECT" \
   --arg org "$ORG" \
   --arg branch "$BRANCH" \
   --arg url "$URL" \
   --arg https "$HTTPS_URL" \
   --arg ts "$TIMESTAMP" \
   '.projects[$name] = {
     org: $org,
     repo: $name,
     branch: $branch,
     url: $url,
     https_url: $https,
     added: $ts,
     editable: true
   }' \
   .flext/external-projects.json > .flext/external-projects.json.tmp

mv .flext/external-projects.json.tmp .flext/external-projects.json
success "Registrado em .flext/external-projects.json"

# 8. Add to pyproject.toml
echo ""
if confirm "Adicionar ao pyproject.toml como editable?"; then
    info "Adicionando ao pyproject.toml..."

    # Use Python with tomlkit for safe TOML editing
    python3 << EOF
import sys
try:
    import tomlkit
except ImportError:
    print("tomlkit not installed, using fallback method")
    sys.exit(1)

with open('pyproject.toml', 'r') as f:
    doc = tomlkit.load(f)

# Add to tool.poetry.dependencies
if 'tool' not in doc:
    doc['tool'] = {}
if 'poetry' not in doc['tool']:
    doc['tool']['poetry'] = {}
if 'dependencies' not in doc['tool']['poetry']:
    doc['tool']['poetry']['dependencies'] = {}

# Create inline table for the dependency
dep = tomlkit.inline_table()
dep['path'] = './${PROJECT}'
dep['develop'] = True

doc['tool']['poetry']['dependencies']['${PROJECT}'] = dep

with open('pyproject.toml', 'w') as f:
    tomlkit.dump(doc, f)

print("OK")
EOF

    if [[ $? -eq 0 ]]; then
        success "Adicionado ao pyproject.toml"
    else
        warn "Falha ao usar tomlkit, adicionando manualmente..."
        # Fallback: append to file (less elegant but works)
        echo -e "\n# External project: $PROJECT ($ORG)" >> pyproject.toml
        echo "${PROJECT} = { path = \"./$PROJECT\", develop = true }" >> pyproject.toml
        success "Adicionado ao pyproject.toml (fallback)"
    fi
fi

# 9. Add to .gitignore
echo ""
if ! grep -q "^${PROJECT}/$" .gitignore 2>/dev/null; then
    info "Adicionando ao .gitignore..."
    {
        echo ""
        echo "# External project: $PROJECT ($ORG)"
        echo "${PROJECT}/"
    } >> .gitignore
    success "Adicionado ao .gitignore"
else
    info "Ja esta no .gitignore"
fi

# 10. Run poetry lock
echo ""
if confirm "Executar poetry lock?"; then
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
success "Projeto $PROJECT adicionado com sucesso!"
echo ""
echo -e "  ${DIM}Registrado em:${NC}  .flext/external-projects.json"
echo -e "  ${DIM}Path dep em:${NC}    pyproject.toml"
echo -e "  ${DIM}Diretorio:${NC}      ./$PROJECT"
echo ""
warn "O diretorio esta em .gitignore (nao sera commitado no repo principal)"
echo ""
echo -e "  ${DIM}Para trabalhar no projeto:${NC}"
echo -e "    cd $PROJECT"
echo -e "    git checkout -b feature/my-feature"
echo -e "    # ... desenvolvimento ..."
echo -e "    git push origin feature/my-feature"
echo ""
