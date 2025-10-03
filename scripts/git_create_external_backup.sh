#!/bin/bash
#
# External Backup Script for FLEXT Workspace
#
# Creates a complete backup OUTSIDE the git repository before pushing to GitHub
# Useful for preserving the current state before major git history rewrites
#
# Usage: ./git_create_external_backup.sh [backup-location]
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default backup location
BACKUP_BASE="${1:-$HOME/flext-backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$BACKUP_BASE/flext-backup-$TIMESTAMP"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  FLEXT External Backup                                    ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

echo -e "${BLUE}📦 Backup Configuration:${NC}"
echo "  Source: $WORKSPACE_ROOT"
echo "  Destination: $BACKUP_DIR"
echo ""

# Create backup directory
echo -e "${BLUE}📁 Creating backup directory...${NC}"
mkdir -p "$BACKUP_DIR"

# Create backup metadata
cat >"$BACKUP_DIR/BACKUP_INFO.txt" <<EOF
FLEXT Workspace Backup
=====================

Backup Created: $(date '+%Y-%m-%d %H:%M:%S')
Source: $WORKSPACE_ROOT
Backup Location: $BACKUP_DIR
Backup Type: Pre-GitHub push safety backup

Git Information:
$(cd "$WORKSPACE_ROOT" && git log -1 --format="Commit: %H%nAuthor: %an <%ae>%nDate: %ad%nMessage: %s" 2>/dev/null || echo "Git information unavailable")

Submodules:
$(cd "$WORKSPACE_ROOT" && git submodule status 2>/dev/null || echo "No submodules or git unavailable")

Repository Statistics:
$(cd "$WORKSPACE_ROOT" && git count-objects -vH 2>/dev/null || echo "Statistics unavailable")
EOF

# Function to calculate directory size
get_dir_size() {
	du -sh "$1" 2>/dev/null | cut -f1 || echo "N/A"
}

# Backup main repository
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Main Repository Backup${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

cd "$WORKSPACE_ROOT"

# Calculate sizes before backup
TOTAL_SIZE=$(get_dir_size "$WORKSPACE_ROOT")
GIT_SIZE=$(get_dir_size "$WORKSPACE_ROOT/.git")

echo -e "${BLUE}📊 Repository Statistics:${NC}"
echo "  Total size: $TOTAL_SIZE"
echo "  Git directory: $GIT_SIZE"
echo ""

echo -e "${BLUE}🔄 Creating tar.gz backup...${NC}"
echo "  This may take several minutes for large repositories..."

# Create compressed backup excluding certain patterns
tar -czf "$BACKUP_DIR/flext-main-repo.tar.gz" \
	-C "$(dirname "$WORKSPACE_ROOT")" \
	--exclude='*.pyc' \
	--exclude='__pycache__' \
	--exclude='.ruff_cache' \
	--exclude='.mypy_cache' \
	--exclude='.pytest_cache' \
	--exclude='htmlcov' \
	--exclude='.coverage' \
	--exclude='*.log' \
	"$(basename "$WORKSPACE_ROOT")" 2>&1 | grep -v "Removing leading"

BACKUP_SIZE=$(get_dir_size "$BACKUP_DIR/flext-main-repo.tar.gz")
echo -e "${GREEN}✅ Main repository backed up: $BACKUP_SIZE${NC}"

# Backup git configuration
echo ""
echo -e "${BLUE}🔧 Backing up git configuration...${NC}"
mkdir -p "$BACKUP_DIR/git-config"

# Backup important git files
if [ -f "$WORKSPACE_ROOT/.gitmodules" ]; then
	cp "$WORKSPACE_ROOT/.gitmodules" "$BACKUP_DIR/git-config/"
	echo "  ✅ .gitmodules"
fi

if [ -f "$WORKSPACE_ROOT/.gitignore" ]; then
	cp "$WORKSPACE_ROOT/.gitignore" "$BACKUP_DIR/git-config/"
	echo "  ✅ .gitignore"
fi

if [ -f "$WORKSPACE_ROOT/.mailmap" ]; then
	cp "$WORKSPACE_ROOT/.mailmap" "$BACKUP_DIR/git-config/"
	echo "  ✅ .mailmap"
fi

# Backup git refs and config
if [ -d "$WORKSPACE_ROOT/.git/refs" ]; then
	cp -r "$WORKSPACE_ROOT/.git/refs" "$BACKUP_DIR/git-config/"
	echo "  ✅ git refs"
fi

if [ -f "$WORKSPACE_ROOT/.git/config" ]; then
	cp "$WORKSPACE_ROOT/.git/config" "$BACKUP_DIR/git-config/"
	echo "  ✅ git config"
fi

# Backup git logs for recovery
echo ""
echo -e "${BLUE}📋 Saving git history snapshot...${NC}"
cd "$WORKSPACE_ROOT"
git log --all --format="%H|%an|%ae|%ad|%s" --date=iso >"$BACKUP_DIR/git-history.txt" 2>/dev/null || true
git reflog --format="%H|%gd|%gs" >"$BACKUP_DIR/git-reflog.txt" 2>/dev/null || true
git tag -l >"$BACKUP_DIR/git-tags.txt" 2>/dev/null || true
echo "  ✅ History snapshot saved"

# Backup submodules list
if [ -f ".gitmodules" ]; then
	echo ""
	echo -e "${BLUE}📦 Submodule information:${NC}"
	git submodule status >"$BACKUP_DIR/submodules-status.txt"

	SUBMODULE_COUNT=$(git submodule status | wc -l)
	echo "  Total submodules: $SUBMODULE_COUNT"
fi

# Create recovery instructions
cat >"$BACKUP_DIR/RECOVERY_INSTRUCTIONS.md" <<'EOF'
# FLEXT Workspace Recovery Instructions

## 📋 What's in This Backup

This backup contains:
- Complete FLEXT workspace tar.gz archive
- Git configuration files (.gitmodules, .gitignore, .mailmap)
- Git refs and configuration
- Complete git history and reflog snapshots
- Submodule status information

## 🔄 Full Repository Recovery

### Option 1: Extract from Backup (Recommended)

```bash
# 1. Extract the backup
cd /path/to/restore/location
tar -xzf flext-main-repo.tar.gz

# 2. Verify git integrity
cd flext
git fsck --full
git status

# 3. Restore submodules (if any)
git submodule update --init --recursive
```

### Option 2: Restore Git Configuration Only

If you only need to restore git configuration:

```bash
cd /path/to/your/flext/repository

# Restore git config files
cp git-config/.gitmodules .
cp git-config/.gitignore .
cp git-config/.mailmap .
cp git-config/config .git/

# Restore refs if needed
cp -r git-config/refs/* .git/refs/
```

## 🔍 Verify Backup Integrity

```bash
# Check backup file integrity
tar -tzf flext-main-repo.tar.gz | head -20

# Check backup size
du -sh flext-main-repo.tar.gz

# Verify git history snapshot
wc -l git-history.txt
head -10 git-history.txt
```

## 📊 Recovery Verification

After recovery, verify:

1. **Git status**: `git status` - should show clean or expected state
2. **Commit history**: `git log --oneline | head -20`
3. **Author normalization**: `git log --format='%aN <%aE>' | sort -u`
4. **Submodules**: `git submodule status`
5. **Tags**: `git tag -l`

## 🚨 Emergency Recovery

If git repository is corrupted:

```bash
# Extract backup
tar -xzf flext-main-repo.tar.gz

# Rename corrupted repository
mv flext flext-corrupted

# Use extracted backup
mv flext-extracted flext

# Verify recovery
cd flext
git fsck --full
git status
```

## 📞 Support

Backup created: See BACKUP_INFO.txt for details
For issues, check git-reflog.txt for recent operations
EOF

# Create quick restore script
cat >"$BACKUP_DIR/quick-restore.sh" <<'EOF'
#!/bin/bash
#
# Quick Restore Script
#
# Usage: ./quick-restore.sh /path/to/restore/location
#

set -euo pipefail

RESTORE_LOCATION="${1:-$HOME/flext-restored}"
BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Restoring FLEXT workspace..."
echo "  From: $BACKUP_DIR"
echo "  To: $RESTORE_LOCATION"
echo ""

# Create restore location
mkdir -p "$RESTORE_LOCATION"

# Extract backup
echo "📦 Extracting backup..."
tar -xzf "$BACKUP_DIR/flext-main-repo.tar.gz" -C "$RESTORE_LOCATION"

echo ""
echo "✅ Restoration complete!"
echo ""
echo "Next steps:"
echo "  1. cd $RESTORE_LOCATION/flext"
echo "  2. git status"
echo "  3. git submodule update --init --recursive"
echo ""
EOF

chmod +x "$BACKUP_DIR/quick-restore.sh"

# Final backup summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ BACKUP COMPLETE${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

echo -e "${CYAN}📊 Backup Summary:${NC}"
echo "  Location: $BACKUP_DIR"
echo "  Main backup: flext-main-repo.tar.gz ($BACKUP_SIZE)"
echo ""

echo -e "${CYAN}📁 Backup Contents:${NC}"
ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{printf "  %-40s %s\n", $9, $5}'
echo ""

echo -e "${CYAN}📝 Recovery Files:${NC}"
echo "  • BACKUP_INFO.txt - Backup metadata and git information"
echo "  • RECOVERY_INSTRUCTIONS.md - Complete recovery guide"
echo "  • quick-restore.sh - One-command restoration script"
echo "  • git-history.txt - Complete commit history snapshot"
echo "  • git-reflog.txt - Reflog for advanced recovery"
echo "  • git-config/ - Git configuration files backup"
echo ""

echo -e "${GREEN}✨ Quick Recovery:${NC}"
echo "  cd $BACKUP_DIR"
echo "  ./quick-restore.sh /path/to/restore"
echo ""

echo -e "${YELLOW}⚠️  Important:${NC}"
echo "  This backup is OUTSIDE your git repository"
echo "  It will NOT be affected by git history rewrites"
echo "  Keep this backup until GitHub push is verified"
echo ""

# Save backup location to a well-known file
echo "$BACKUP_DIR" >"$WORKSPACE_ROOT/.last-backup-location"
echo -e "${BLUE}💾 Backup location saved to: .last-backup-location${NC}"
echo ""
