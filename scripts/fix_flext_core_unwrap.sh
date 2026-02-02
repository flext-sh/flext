#!/bin/bash

# Batch fix script: Replace deprecated .unwrap() with .value in flext-core documentation and code
# Author: Claude Code
# Modes: dry-run, backup, exec, rollback
# Target: 113 occurrences across 22 markdown files + 4 in result.py

set -e

PROJECT_DIR="/home/marlonsc/flext/flext-core"
BACKUP_DIR="/tmp/flext_core_unwrap_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="flext_core_unwrap_${TIMESTAMP}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Modes: dry-run (default), backup, exec, rollback
MODE="${1:-dry-run}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FLEXT-Core unwrap() → .value Batch Fix${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Mode: ${YELLOW}${MODE}${NC}"
echo "Project: ${YELLOW}${PROJECT_DIR}${NC}"
echo "Backup: ${YELLOW}${BACKUP_DIR}/${BACKUP_NAME}${NC}"
echo ""

# Function: Dry run - show what will change
dry_run() {
    echo -e "${BLUE}[DRY-RUN] Analyzing changes...${NC}"
    echo ""

    local file_count=0
    local occurrence_count=0
    local files=()

    while IFS= read -r file; do
        local count=$(grep -o "\.unwrap()" "$file" | wc -l)
        if [ "$count" -gt 0 ]; then
            files+=("$file")
            occurrence_count=$((occurrence_count + count))
            file_count=$((file_count + 1))
            echo -e "${YELLOW}File: $(basename $file)${NC}"
            echo -e "  Occurrences: ${count}"
            echo ""
        fi
    done < <(find "$PROJECT_DIR" \( -name "*.md" -o -name "*.py" \) -type f)

    echo -e "${GREEN}Summary:${NC}"
    echo "  Files affected: ${file_count}"
    echo "  Total occurrences: ${occurrence_count}"
    echo ""
    echo -e "${BLUE}Sample changes (first 3 files):${NC}"

    local sample_count=0
    for file in "${files[@]:0:3}"; do
        echo ""
        echo -e "${YELLOW}File: $(basename $file)${NC}"
        grep -n "\.unwrap()" "$file" | head -3 | while IFS=: read -r line_num line_content; do
            echo "  Line $line_num:"
            echo -e "    ${RED}✗ $line_content${NC}"
            echo -e "    ${GREEN}✓ ${line_content//.unwrap()/.value}${NC}"
        done
    done

    echo ""
    echo -e "${BLUE}To apply changes, run:${NC}"
    echo "  ${YELLOW}$0 exec${NC}"
    echo ""
}

# Function: Create backup before execution
create_backup() {
    echo -e "${BLUE}[BACKUP] Creating timestamped backup...${NC}"

    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

    # Backup all affected files
    find "$PROJECT_DIR" \( -name "*.md" -o -name "result.py" \) -type f | while read -r file; do
        if grep -q "\.unwrap()" "$file"; then
            local rel_path="${file#$PROJECT_DIR/}"
            local backup_file="$BACKUP_DIR/$BACKUP_NAME/$rel_path"
            mkdir -p "$(dirname "$backup_file")"
            cp "$file" "$backup_file"
        fi
    done

    echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR/$BACKUP_NAME${NC}"
    echo "  Files backed up: $(find "$BACKUP_DIR/$BACKUP_NAME" -type f | wc -l)"
    echo ""
}

# Function: Execute the fix
execute_fix() {
    echo -e "${BLUE}[EXEC] Applying fixes...${NC}"

    local fixed_count=0
    local file_count=0

    find "$PROJECT_DIR" \( -name "*.md" -o -name "result.py" \) -type f | while read -r file; do
        local before_count=$(grep -o "\.unwrap()" "$file" 2>/dev/null | wc -l || echo 0)
        if [ "$before_count" -gt 0 ]; then
            # Use sed for in-place replacement
            sed -i 's/\.unwrap()/.value/g' "$file"
            local after_count=$(grep -o "\.unwrap()" "$file" 2>/dev/null | wc -l || echo 0)
            echo -e "  ${GREEN}✓ $(basename $file): ${before_count} → ${after_count}${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}[DONE] All replacements completed${NC}"
    echo ""
}

# Function: Validate the fix
validate_fix() {
    echo -e "${BLUE}[VALIDATE] Checking results...${NC}"

    local remaining=$(grep -r "\.unwrap()" "$PROJECT_DIR" --include="*.md" --include="*.py" 2>/dev/null | wc -l || echo 0)

    if [ "$remaining" -eq 0 ]; then
        echo -e "${GREEN}✓ Success! All .unwrap() calls replaced${NC}"
        return 0
    else
        echo -e "${RED}✗ Error: ${remaining} occurrences still remaining${NC}"
        grep -r "\.unwrap()" "$PROJECT_DIR" --include="*.md" --include="*.py" 2>/dev/null | head -5
        return 1
    fi
}

# Function: Rollback from backup
rollback() {
    if [ ! -d "$BACKUP_DIR/$BACKUP_NAME" ]; then
        echo -e "${RED}✗ Backup not found: $BACKUP_DIR/$BACKUP_NAME${NC}"
        echo ""
        echo "Available backups:"
        ls -1 "$BACKUP_DIR/" 2>/dev/null || echo "  No backups found"
        return 1
    fi

    echo -e "${BLUE}[ROLLBACK] Restoring from backup...${NC}"

    find "$BACKUP_DIR/$BACKUP_NAME" -type f | while read -r backup_file; do
        local rel_path="${backup_file#$BACKUP_DIR/$BACKUP_NAME/}"
        local target_file="$PROJECT_DIR/$rel_path"
        echo -e "  Restoring: $(basename $target_file)"
        cp "$backup_file" "$target_file"
    done

    echo -e "${GREEN}✓ Rollback complete${NC}"
    echo ""
}

# Main execution
case "$MODE" in
    dry-run)
        dry_run
        ;;
    backup)
        create_backup
        ;;
    exec)
        create_backup
        execute_fix
        validate_fix
        ;;
    rollback)
        rollback
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        echo "Usage: $0 [dry-run|backup|exec|rollback]"
        echo ""
        echo "Modes:"
        echo "  dry-run  - Show what will change (default)"
        echo "  backup   - Create backup only"
        echo "  exec     - Create backup and apply fixes"
        echo "  rollback - Restore from last backup"
        exit 1
        ;;
esac
