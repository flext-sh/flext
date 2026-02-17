#!/bin/bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# =============================================================================
# FLEXT Monorepo - Release Automation
# =============================================================================
# Automated release with version bumping, changelog, and GitHub release.
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

box "Release Pipeline"

# 1. Get current version
echo ""
header "Versao Atual"
CURRENT_VERSION=$(get_version ".")
info "Versao do workspace: ${CURRENT_VERSION:-N/A}"

# Show versions of key projects
for project in flext-core flext-cli flext-ldif; do
	if [[ -d $project ]]; then
		PROJECT_VERSION=$(get_version "$project")
		echo -e "  ${DIM}$project:${NC} ${PROJECT_VERSION:-N/A}"
	fi
done

# 2. Version bump type
echo ""
header "Tipo de Release"
BUMP_CHOICE=$(select_option "Tipo de versao?" \
	"patch (${CURRENT_VERSION:-0.0.0} -> $(bump_version "${CURRENT_VERSION:-0.0.0}" patch))" \
	"minor (${CURRENT_VERSION:-0.0.0} -> $(bump_version "${CURRENT_VERSION:-0.0.0}" minor))" \
	"major (${CURRENT_VERSION:-0.0.0} -> $(bump_version "${CURRENT_VERSION:-0.0.0}" major))")

case $BUMP_CHOICE in
1) BUMP_TYPE="patch" ;;
2) BUMP_TYPE="minor" ;;
3) BUMP_TYPE="major" ;;
*) BUMP_TYPE="patch" ;;
esac

NEW_VERSION=$(bump_version "${CURRENT_VERSION:-0.0.0}" "$BUMP_TYPE")
info "Nova versao: $NEW_VERSION"

# 3. Scope
echo ""
header "Escopo do Release"
SCOPE_CHOICE=$(select_option "Quais projetos?" \
	"Projeto especifico" \
	"Todos os projetos modificados" \
	"Todos os projetos")

case $SCOPE_CHOICE in
1)
	SCOPE="single"
	TARGET_PROJECT=$(prompt_value "Nome do projeto" "flext-core")
	if [[ ! -d $TARGET_PROJECT ]]; then
		error "Projeto $TARGET_PROJECT nao encontrado"
		exit 1
	fi
	TARGET_PROJECTS=("$TARGET_PROJECT")
	;;
2)
	SCOPE="changed"
	TARGET_PROJECTS=()
	for project in $(list_changed_projects); do
		TARGET_PROJECTS+=("$project")
	done
	if [[ ${#TARGET_PROJECTS[@]} -eq 0 ]]; then
		info "Nenhum projeto com mudancas"
		exit 0
	fi
	;;
3)
	SCOPE="all"
	TARGET_PROJECTS=()
	for project in $(list_all_projects); do
		if [[ -d $project ]]; then
			TARGET_PROJECTS+=("$project")
		fi
	done
	;;
esac

echo ""
info "Projetos selecionados: ${#TARGET_PROJECTS[@]}"
for project in "${TARGET_PROJECTS[@]}"; do
	echo -e "  ${DIM}- $project${NC}"
done

# 4. Validate before release
echo ""
if confirm "Rodar validacao completa antes do release?" "n"; then
	echo ""
	header "Validacao"
	info "Executando make validate..."

	VALIDATION_FAILED=false
	for project in "${TARGET_PROJECTS[@]}"; do
		if [[ -d $project ]] && [[ -f "$project/Makefile" ]]; then
			echo -e "  ${CYAN}$project${NC}..."
			if make -C "$project" validate -s 2>/dev/null; then
				echo -e "    ${GREEN}OK${NC}"
			else
				echo -e "    ${RED}FALHOU${NC}"
				VALIDATION_FAILED=true
			fi
		fi
	done

	if $VALIDATION_FAILED; then
		error "Validacao falhou em alguns projetos"
		if ! confirm "Continuar mesmo assim?" "n"; then
			exit 1
		fi
	else
		success "Validacao passou"
	fi
fi

# 5. Bump versions
echo ""
if confirm "Atualizar versoes nos pyproject.toml?"; then
	header "Atualizando Versoes"

	for project in "${TARGET_PROJECTS[@]}"; do
		if [[ -f "$project/pyproject.toml" ]]; then
			info "Atualizando $project para $NEW_VERSION..."

			python3 <<EOF || true
try:
    import tomlkit
    with open('$project/pyproject.toml', 'r') as f:
        doc = tomlkit.load(f)

    if 'project' in doc and 'version' in doc['project']:
        doc['project']['version'] = '$NEW_VERSION'
    elif 'tool' in doc and 'poetry' in doc['tool'] and 'version' in doc['tool']['poetry']:
        doc['tool']['poetry']['version'] = '$NEW_VERSION'

    with open('$project/pyproject.toml', 'w') as f:
        tomlkit.dump(doc, f)
    print("OK")
except Exception as e:
    print(f"ERROR: {e}")
EOF
			success "  $project -> $NEW_VERSION"
		fi
	done
fi

# 6. Generate changelog (optional)
echo ""
CHANGELOG_GENERATED=false
if confirm "Gerar changelog automatico?" "n"; then
	header "Changelog"

	CHANGELOG_FILE="CHANGELOG.md"
	RELEASE_DATE=$(date +%Y-%m-%d)

	# Get commits since last tag
	LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

	if [[ -n $LAST_TAG ]]; then
		COMMITS=$(git log "$LAST_TAG"..HEAD --oneline --no-merges 2>/dev/null || true)
	else
		COMMITS=$(git log --oneline --no-merges -20 2>/dev/null || true)
	fi

	if [[ -n $COMMITS ]]; then
		# Create changelog entry
		ENTRY="## [$NEW_VERSION] - $RELEASE_DATE\n\n"

		# Categorize commits
		FEATURES=$(echo "$COMMITS" | grep -E "^[a-f0-9]+ feat" || true)
		FIXES=$(echo "$COMMITS" | grep -E "^[a-f0-9]+ fix" || true)
		OTHERS=$(echo "$COMMITS" | grep -vE "^[a-f0-9]+ (feat|fix)" || true)

		if [[ -n $FEATURES ]]; then
			ENTRY+="### Features\n"
			while IFS= read -r commit; do
				MSG=$(echo "$commit" | sed 's/^[a-f0-9]* feat[^:]*: //')
				ENTRY+="- $MSG\n"
			done <<<"$FEATURES"
			ENTRY+="\n"
		fi

		if [[ -n $FIXES ]]; then
			ENTRY+="### Bug Fixes\n"
			while IFS= read -r commit; do
				MSG=$(echo "$commit" | sed 's/^[a-f0-9]* fix[^:]*: //')
				ENTRY+="- $MSG\n"
			done <<<"$FIXES"
			ENTRY+="\n"
		fi

		if [[ -n $OTHERS ]]; then
			ENTRY+="### Other Changes\n"
			while IFS= read -r commit; do
				MSG=$(echo "$commit" | sed 's/^[a-f0-9]* [^:]*: //')
				ENTRY+="- $MSG\n"
			done <<<"$OTHERS"
			ENTRY+="\n"
		fi

		# Prepend to changelog
		if [[ -f $CHANGELOG_FILE ]]; then
			echo -e "$ENTRY$(cat $CHANGELOG_FILE)" >"$CHANGELOG_FILE"
		else
			echo -e "# Changelog\n\n$ENTRY" >"$CHANGELOG_FILE"
		fi

		success "Changelog atualizado"
		CHANGELOG_GENERATED=true
	else
		info "Nenhum commit para adicionar ao changelog"
	fi
fi

# 7. Commit changes
echo ""
if confirm "Criar commit de release?"; then
	header "Commit"

	git add -A
	git commit -m "chore(release): $NEW_VERSION" || info "Nada para commitar"
	success "Commit de release criado"
fi

# 8. Create tag
echo ""
TAG_NAME="v$NEW_VERSION"
if confirm "Criar tag $TAG_NAME?"; then
	header "Tag"

	if $CHANGELOG_GENERATED; then
		git tag -a "$TAG_NAME" -m "Release $NEW_VERSION" -m "See CHANGELOG.md for details"
	else
		git tag -a "$TAG_NAME" -m "Release $NEW_VERSION"
	fi
	success "Tag $TAG_NAME criada"
fi

# 9. Push
echo ""
if confirm "Push para origin (commits + tag)?"; then
	header "Push"

	BRANCH=$(get_current_branch)
	git push origin "$BRANCH"
	success "Push de commits"

	git push origin "$TAG_NAME"
	success "Push de tag"
fi

# 10. GitHub Release (optional)
echo ""
if command -v gh &>/dev/null && confirm "Criar GitHub Release?" "n"; then
	header "GitHub Release"

	if $CHANGELOG_GENERATED && [[ -f $CHANGELOG_FILE ]]; then
		# Extract latest release notes from changelog
		NOTES=$(awk "/^## \[$NEW_VERSION\]/,/^## \[/" "$CHANGELOG_FILE" | head -n -1)
		gh release create "$TAG_NAME" --title "Release $NEW_VERSION" --notes "$NOTES"
	else
		gh release create "$TAG_NAME" --title "Release $NEW_VERSION" --generate-notes
	fi
	success "GitHub Release criado"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Release $NEW_VERSION concluido!"
echo ""
echo -e "  ${DIM}Versao:${NC}   $NEW_VERSION"
echo -e "  ${DIM}Tag:${NC}      $TAG_NAME"
echo -e "  ${DIM}Projetos:${NC} ${#TARGET_PROJECTS[@]}"
echo ""
