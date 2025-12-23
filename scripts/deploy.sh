#!/bin/bash
# =============================================================================
# FLEXT Monorepo - Deploy Pipeline
# =============================================================================
# Interactive deploy with validation, environment selection, and project scope.
# =============================================================================

set -euo pipefail

# Get script directory and source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# Ensure we're in the flext root
cd "$SCRIPT_DIR/.."
require_flext_root

# =============================================================================
# MAIN
# =============================================================================

box "Deploy Pipeline"

# 1. Environment selection
echo ""
header "Ambiente"
ENV_CHOICE=$(select_option "Ambiente de deploy?" \
    "staging" \
    "production")

case $ENV_CHOICE in
    1) DEPLOY_ENV="staging" ;;
    2) DEPLOY_ENV="production" ;;
    *) DEPLOY_ENV="staging" ;;
esac

info "Ambiente: $DEPLOY_ENV"

# Production confirmation
if [[ "$DEPLOY_ENV" == "production" ]]; then
    echo ""
    warn "ATENCAO: Deploy em PRODUCAO!"
    if ! confirm "Tem certeza que deseja continuar?" "n"; then
        info "Deploy cancelado"
        exit 0
    fi
fi

# 2. Version/Tag
echo ""
header "Versao"
CURRENT_VERSION=$(get_version ".")
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")

info "Versao atual: ${CURRENT_VERSION:-N/A}"
info "Tag atual: $CURRENT_TAG"

TAG=$(prompt_value "Tag para deploy" "$CURRENT_TAG")

# Verify tag exists
if ! git rev-parse "$TAG" &>/dev/null; then
    error "Tag $TAG nao existe"
    if confirm "Usar HEAD atual sem tag?"; then
        TAG="HEAD"
    else
        exit 1
    fi
fi

# 3. Project scope
echo ""
header "Escopo"
SCOPE_CHOICE=$(select_option "Projetos a incluir?" \
    "Todos (core + external)" \
    "Apenas core (flext-sh)" \
    "Selecionar manualmente")

case $SCOPE_CHOICE in
    1)
        DEPLOY_PROJECTS=()
        for project in $(list_all_projects); do
            if [[ -d "$project" ]]; then
                DEPLOY_PROJECTS+=("$project")
            fi
        done
        ;;
    2)
        DEPLOY_PROJECTS=()
        if [[ -f ".gitmodules" ]]; then
            while IFS= read -r line; do
                if [[ "$line" =~ path\ =\ (.+) ]]; then
                    project="${BASH_REMATCH[1]}"
                    if [[ -d "$project" ]]; then
                        DEPLOY_PROJECTS+=("$project")
                    fi
                fi
            done < .gitmodules
        fi
        ;;
    3)
        DEPLOY_PROJECTS=()
        for project in $(list_all_projects); do
            if [[ -d "$project" ]] && confirm "  Incluir $project?"; then
                DEPLOY_PROJECTS+=("$project")
            fi
        done
        ;;
esac

echo ""
info "Projetos selecionados: ${#DEPLOY_PROJECTS[@]}"
for project in "${DEPLOY_PROJECTS[@]}"; do
    echo -e "  ${DIM}- $project${NC}"
done

# 4. Pre-deploy validation
echo ""
if confirm "Rodar validacao antes do deploy?"; then
    header "Validacao Pre-Deploy"

    VALIDATION_FAILED=false
    VALIDATED_PROJECTS=0

    for project in "${DEPLOY_PROJECTS[@]}"; do
        if [[ -f "$project/Makefile" ]]; then
            echo -e "  ${CYAN}$project${NC}..."

            # Run validation
            if make -C "$project" validate -s 2>/dev/null; then
                echo -e "    ${GREEN}OK${NC}"
                ((VALIDATED_PROJECTS++))
            else
                echo -e "    ${RED}FALHOU${NC}"
                VALIDATION_FAILED=true
            fi
        else
            echo -e "  ${DIM}$project${NC} (sem Makefile)"
        fi
    done

    echo ""
    if $VALIDATION_FAILED; then
        error "Validacao falhou em alguns projetos"
        if ! confirm "Continuar deploy mesmo assim?" "n"; then
            exit 1
        fi
    else
        success "Validacao passou em $VALIDATED_PROJECTS projetos"
    fi
fi

# 5. Build artifacts (if needed)
echo ""
BUILD_ARTIFACTS=false
if confirm "Gerar artefatos de build (wheels)?" "n"; then
    header "Build"
    BUILD_ARTIFACTS=true

    for project in "${DEPLOY_PROJECTS[@]}"; do
        if [[ -f "$project/pyproject.toml" ]]; then
            info "Building $project..."
            if poetry -C "$project" build 2>/dev/null; then
                success "  $project: wheel + sdist gerados"
            else
                warn "  $project: build falhou"
            fi
        fi
    done
fi

# 6. Deploy confirmation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
header "Resumo do Deploy"
echo ""
echo -e "  ${DIM}Ambiente:${NC}  $DEPLOY_ENV"
echo -e "  ${DIM}Tag:${NC}       $TAG"
echo -e "  ${DIM}Projetos:${NC}  ${#DEPLOY_PROJECTS[@]}"
echo -e "  ${DIM}Artefatos:${NC} $($BUILD_ARTIFACTS && echo "Sim" || echo "Nao")"
echo ""

if ! confirm "Executar deploy?"; then
    info "Deploy cancelado"
    exit 0
fi

# 7. Execute deploy
echo ""
header "Executando Deploy"

# This is a template - customize based on your actual deployment process
DEPLOY_SUCCESS=true

for project in "${DEPLOY_PROJECTS[@]}"; do
    info "Deploying $project..."

    # Check for project-specific deploy script
    if [[ -x "$project/scripts/deploy.sh" ]]; then
        if "$project/scripts/deploy.sh" "$DEPLOY_ENV" "$TAG"; then
            success "  $project deployed"
        else
            error "  $project deploy failed"
            DEPLOY_SUCCESS=false
        fi
    elif [[ -f "$project/Makefile" ]] && grep -q "^deploy:" "$project/Makefile"; then
        if make -C "$project" deploy ENV="$DEPLOY_ENV" TAG="$TAG" -s 2>/dev/null; then
            success "  $project deployed"
        else
            error "  $project deploy failed"
            DEPLOY_SUCCESS=false
        fi
    else
        info "  $project: sem script de deploy (skip)"
    fi
done

# 8. Post-deploy actions
if $DEPLOY_SUCCESS; then
    echo ""
    header "Pos-Deploy"

    # Tag the deployment
    DEPLOY_TAG="${DEPLOY_ENV}-${TAG}-$(date +%Y%m%d-%H%M%S)"
    if confirm "Criar tag de deploy $DEPLOY_TAG?" "n"; then
        git tag "$DEPLOY_TAG"
        success "Tag $DEPLOY_TAG criada"

        if confirm "Push tag?" "n"; then
            git push origin "$DEPLOY_TAG"
            success "Tag pushed"
        fi
    fi
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if $DEPLOY_SUCCESS; then
    success "Deploy concluido com sucesso!"
else
    error "Deploy concluido com erros"
fi
echo ""
echo -e "  ${DIM}Ambiente:${NC} $DEPLOY_ENV"
echo -e "  ${DIM}Tag:${NC}      $TAG"
echo -e "  ${DIM}Hora:${NC}     $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Return appropriate exit code
$DEPLOY_SUCCESS
