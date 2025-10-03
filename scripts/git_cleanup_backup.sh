#!/bin/bash
#
# Git History Cleanup - Backup & Safety Script
#
# Creates comprehensive backups before destructive history operations
# Usage: ./git_cleanup_backup.sh [--all-submodules]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BACKUP_ROOT="${HOME}/flext-history-backup-$(date +%Y%m%d-%H%M%S)"
CURRENT_DIR="$(pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FLEXT Git History Backup System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to backup a single repository
backup_repo() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")

    echo -e "${YELLOW}📦 Backing up: ${repo_name}${NC}"

    # Create backup directory
    local backup_dir="${BACKUP_ROOT}/${repo_name}"
    mkdir -p "$backup_dir"

    # 1. Clone the repository (preserves full history)
    echo "   → Cloning repository..."
    git clone --mirror "$repo_path" "${backup_dir}/${repo_name}.git" 2>&1 | sed 's/^/     /'

    # 2. Export commit history to text
    echo "   → Exporting commit history..."
    (cd "$repo_path" && git log --all --format='%H|%an|%ae|%ad|%s' > "${backup_dir}/commit-history.txt")

    # 3. Create pre-cleanup tag
    echo "   → Creating pre-cleanup tag..."
    (cd "$repo_path" && git tag -f "pre-cleanup-$(date +%Y%m%d-%H%M%S)" 2>&1 | sed 's/^/     /')

    # 4. Export branch information
    echo "   → Exporting branch info..."
    (cd "$repo_path" && git branch -a > "${backup_dir}/branches.txt")

    # 5. Export tag information
    echo "   → Exporting tags..."
    (cd "$repo_path" && git tag -l > "${backup_dir}/tags.txt")

    # 6. Save current HEAD reference
    echo "   → Saving HEAD reference..."
    (cd "$repo_path" && git rev-parse HEAD > "${backup_dir}/HEAD.txt")

    # 7. Create metadata file
    cat > "${backup_dir}/metadata.json" <<EOF
{
    "repo_name": "${repo_name}",
    "repo_path": "${repo_path}",
    "backup_date": "$(date -Iseconds)",
    "backup_dir": "${backup_dir}",
    "commit_count": $(cd "$repo_path" && git rev-list --all --count),
    "current_branch": "$(cd "$repo_path" && git branch --show-current)",
    "current_head": "$(cd "$repo_path" && git rev-parse HEAD)"
}
EOF

    echo -e "${GREEN}   ✅ Backup complete: ${backup_dir}${NC}"
    echo ""
}

# Function to create rollback script
create_rollback_script() {
    local rollback_script="${BACKUP_ROOT}/ROLLBACK.sh"

    cat > "$rollback_script" <<'EOF'
#!/bin/bash
#
# ROLLBACK SCRIPT - Restore from backup
#
# ⚠️  WARNING: This will FORCE RESET repositories to pre-cleanup state!
#
# Usage: ./ROLLBACK.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}========================================${NC}"
echo -e "${RED}⚠️  GIT HISTORY ROLLBACK${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}This will restore ALL repositories to pre-cleanup state.${NC}"
echo -e "${YELLOW}Any changes made after backup will be LOST!${NC}"
echo ""
read -p "Are you ABSOLUTELY sure? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled."
    exit 1
fi

BACKUP_DIR="$(dirname "$0")"

for repo_backup in "$BACKUP_DIR"/*; do
    if [ -d "$repo_backup" ] && [ -f "$repo_backup/metadata.json" ]; then
        repo_name=$(basename "$repo_backup")

        if [ "$repo_name" == "ROLLBACK.sh" ]; then
            continue
        fi

        echo -e "${YELLOW}🔄 Rolling back: ${repo_name}${NC}"

        # Read original repo path from metadata
        original_path=$(grep -o '"repo_path": "[^"]*' "$repo_backup/metadata.json" | cut -d'"' -f4)

        if [ -d "$original_path" ]; then
            # Reset to pre-cleanup tag
            original_head=$(cat "$repo_backup/HEAD.txt")
            (cd "$original_path" && git reset --hard "$original_head")
            echo -e "${GREEN}   ✅ Restored: ${original_path}${NC}"
        else
            echo -e "${RED}   ❌ Original repo not found: ${original_path}${NC}"
        fi
    fi
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ ROLLBACK COMPLETE${NC}"
echo -e "${GREEN}========================================${NC}"
EOF

    chmod +x "$rollback_script"
    echo -e "${GREEN}📝 Rollback script created: ${rollback_script}${NC}"
    echo ""
}

# Main execution
main() {
    # Create backup root directory
    mkdir -p "$BACKUP_ROOT"

    echo -e "${BLUE}Backup location: ${BACKUP_ROOT}${NC}"
    echo ""

    # Check if --all-submodules flag is present
    if [[ "${1:-}" == "--all-submodules" ]]; then
        echo -e "${YELLOW}Backing up ALL submodules...${NC}"
        echo ""

        # Backup main repository first
        backup_repo "$CURRENT_DIR"

        # Backup each submodule
        git submodule status | awk '{print $2}' | while read -r submodule; do
            if [ -d "$submodule/.git" ]; then
                backup_repo "${CURRENT_DIR}/${submodule}"
            else
                echo -e "${RED}⚠️  Skipping ${submodule} (not initialized)${NC}"
            fi
        done
    else
        # Backup only current repository
        backup_repo "$CURRENT_DIR"
    fi

    # Create rollback script
    create_rollback_script

    # Create summary
    cat > "${BACKUP_ROOT}/BACKUP_INFO.txt" <<EOF
FLEXT Git History Backup
========================

Backup Date: $(date)
Backup Location: ${BACKUP_ROOT}

Repositories Backed Up:
$(find "$BACKUP_ROOT" -name "metadata.json" -exec dirname {} \; | xargs -I {} basename {})

To rollback changes:
    cd ${BACKUP_ROOT}
    ./ROLLBACK.sh

To inspect a backup:
    cd ${BACKUP_ROOT}/<repo-name>
    cat metadata.json
    cat commit-history.txt

Keep this backup until you're CERTAIN the cleanup was successful!
EOF

    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ ALL BACKUPS COMPLETE${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}Backup saved to: ${BACKUP_ROOT}${NC}"
    echo -e "${YELLOW}IMPORTANT: Keep this backup until cleanup is verified!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review: cat ${BACKUP_ROOT}/BACKUP_INFO.txt"
    echo "  2. Proceed with cleanup operations"
    echo "  3. If needed, rollback: cd ${BACKUP_ROOT} && ./ROLLBACK.sh"
    echo ""
}

main "$@"
