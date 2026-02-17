#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# =============================================================================
# FLEXT Monorepo - Smart Commit (Conventional Commits)
# =============================================================================
# Interactive commit with conventional commits format and optional pre-checks.
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

box "Smart Commit"

# 1. Find projects with changes
echo ""
header "Projetos com Mudancas"

CHANGED_PROJECTS=()
CHANGED_FILES=()

# Check root workspace
if has_changes "."; then
	ROOT_CHANGES=$(git diff --name-only HEAD 2>/dev/null | wc -l)
	ROOT_STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l)
	ROOT_UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)
	TOTAL_ROOT=$((ROOT_CHANGES + ROOT_STAGED + ROOT_UNTRACKED))

	if [[ $TOTAL_ROOT -gt 0 ]]; then
		echo -e "  ${CYAN}workspace${NC} ($TOTAL_ROOT arquivos)"
		CHANGED_PROJECTS+=(".")
	fi
fi

# Check subprojects
for project in $(list_all_projects); do
	if [[ -d $project ]] && has_changes "$project"; then
		PROJECT_CHANGES=$(git -C "$project" diff --name-only HEAD 2>/dev/null | wc -l)
		PROJECT_STAGED=$(git -C "$project" diff --cached --name-only 2>/dev/null | wc -l)
		PROJECT_UNTRACKED=$(git -C "$project" ls-files --others --exclude-standard 2>/dev/null | wc -l)
		TOTAL_PROJECT=$((PROJECT_CHANGES + PROJECT_STAGED + PROJECT_UNTRACKED))

		if [[ $TOTAL_PROJECT -gt 0 ]]; then
			echo -e "  ${CYAN}$project${NC} ($TOTAL_PROJECT arquivos)"
			CHANGED_PROJECTS+=("$project")
		fi
	fi
done

if [[ ${#CHANGED_PROJECTS[@]} -eq 0 ]]; then
	info "Nenhuma mudanca encontrada"
	exit 0
fi

# 2. Select commit type
echo ""
header "Tipo de Commit"
TYPE_CHOICE=$(select_option "Tipo?" \
	"feat - Nova funcionalidade" \
	"fix - Correcao de bug" \
	"refactor - Refatoracao" \
	"docs - Documentacao" \
	"chore - Manutencao" \
	"test - Testes" \
	"style - Formatacao")

case $TYPE_CHOICE in
1) TYPE="feat" ;;
2) TYPE="fix" ;;
3) TYPE="refactor" ;;
4) TYPE="docs" ;;
5) TYPE="chore" ;;
6) TYPE="test" ;;
7) TYPE="style" ;;
*) TYPE="feat" ;;
esac

# 3. Scope (optional)
echo ""
SCOPE=$(prompt_value "Escopo (projeto ou vazio)" "")
if [[ -n $SCOPE ]]; then
	SCOPE_STR="($SCOPE)"
else
	SCOPE_STR=""
fi

# 4. Message
echo ""
MSG=$(prompt_value "Mensagem (imperativo, sem ponto final)" "")
if [[ -z $MSG ]]; then
	error "Mensagem e obrigatoria"
	exit 1
fi

# Build commit message
COMMIT_MSG="${TYPE}${SCOPE_STR}: ${MSG}"

echo ""
info "Mensagem de commit:"
echo -e "  ${BOLD}$COMMIT_MSG${NC}"

# 5. Pre-commit checks
echo ""
if confirm "Rodar make check antes do commit?" "n"; then
	echo ""
	info "Executando make check..."
	if make check; then
		success "Check passou"
	else
		error "Check falhou"
		if ! confirm "Continuar mesmo assim?" "n"; then
			exit 1
		fi
	fi
fi

# 6. Select which projects to commit
echo ""
header "Projetos para Commit"

COMMIT_ALL=false
if [[ ${#CHANGED_PROJECTS[@]} -eq 1 ]]; then
	# Only one project, auto-select
	SELECTED_PROJECTS=("${CHANGED_PROJECTS[@]}")
	info "Apenas ${SELECTED_PROJECTS[0]} tem mudancas"
else
	if confirm "Commit em todos os ${#CHANGED_PROJECTS[@]} projetos?"; then
		SELECTED_PROJECTS=("${CHANGED_PROJECTS[@]}")
		COMMIT_ALL=true
	else
		# Manual selection
		SELECTED_PROJECTS=()
		for project in "${CHANGED_PROJECTS[@]}"; do
			if confirm "  Incluir $project?"; then
				SELECTED_PROJECTS+=("$project")
			fi
		done
	fi
fi

if [[ ${#SELECTED_PROJECTS[@]} -eq 0 ]]; then
	info "Nenhum projeto selecionado"
	exit 0
fi

# 7. Stage and commit
echo ""
header "Executando Commits"

for project in "${SELECTED_PROJECTS[@]}"; do
	if [[ $project == "." ]]; then
		PROJECT_NAME="workspace"
		PROJECT_PATH="."
	else
		PROJECT_NAME="$project"
		PROJECT_PATH="$project"
	fi

	echo ""
	info "Commitando $PROJECT_NAME..."

	# Stage all changes
	git -C "$PROJECT_PATH" add -A

	# Check if there's something to commit
	if git -C "$PROJECT_PATH" diff --cached --quiet; then
		info "  Nada para commitar em $PROJECT_NAME"
		continue
	fi

	# Commit
	if git -C "$PROJECT_PATH" commit -m "$COMMIT_MSG"; then
		success "  Commit criado em $PROJECT_NAME"
	else
		error "  Falha no commit em $PROJECT_NAME"
	fi
done

# 8. Push (optional)
echo ""
if confirm "Push automatico?" "n"; then
	echo ""
	header "Push"

	for project in "${SELECTED_PROJECTS[@]}"; do
		if [[ $project == "." ]]; then
			PROJECT_NAME="workspace"
			PROJECT_PATH="."
		else
			PROJECT_NAME="$project"
			PROJECT_PATH="$project"
		fi

		BRANCH=$(get_current_branch "$PROJECT_PATH")
		info "Push $PROJECT_NAME ($BRANCH)..."

		if git -C "$PROJECT_PATH" push origin "$BRANCH" 2>/dev/null; then
			success "  Push concluido em $PROJECT_NAME"
		else
			warn "  Push falhou em $PROJECT_NAME (verifique acesso)"
		fi
	done
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Commits concluidos!"
echo ""
echo -e "  ${DIM}Mensagem:${NC} $COMMIT_MSG"
echo -e "  ${DIM}Projetos:${NC} ${#SELECTED_PROJECTS[@]}"
echo ""
