#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# FLEXT File Locking Protocol for Multi-Agent Coordination
# Usage: ./file_lock.sh lock <file_path> <agent_name>
#        ./file_lock.sh unlock <file_path> <agent_name>
#        ./file_lock.sh check <file_path>

set -euo pipefail

LOCK_DIR=".locks"
FLEXT_TOKEN=".token"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create lock directory
mkdir -p "$LOCK_DIR"

case "${1:-help}" in
lock)
	FILE_PATH="$2"
	AGENT_NAME="$3"
	LOCK_FILE="$LOCK_DIR/$(basename "$FILE_PATH").lock"

	if [ -f "$LOCK_FILE" ]; then
		CURRENT_AGENT=$(cat "$LOCK_FILE")
		if [ "$CURRENT_AGENT" = "$AGENT_NAME" ]; then
			log_warning "Already locked by $AGENT_NAME"
			exit 0
		else
			log_error "File locked by $CURRENT_AGENT"
			exit 1
		fi
	fi

	# Try to acquire flock
	exec 200>"$LOCK_FILE"
	if flock -n 200; then
		echo "$AGENT_NAME" >&200
		echo "FLOCK_${AGENT_NAME}_$(basename "$FILE_PATH")" >>"$FLEXT_TOKEN"
		log_success "Locked $FILE_PATH for $AGENT_NAME"
	else
		log_error "Failed to acquire lock"
		exit 1
	fi
	;;

unlock)
	FILE_PATH="$2"
	AGENT_NAME="$3"
	LOCK_FILE="$LOCK_DIR/$(basename "$FILE_PATH").lock"

	if [ ! -f "$LOCK_FILE" ]; then
		log_warning "Not locked"
		exit 0
	fi

	CURRENT_AGENT=$(cat "$LOCK_FILE")
	if [ "$CURRENT_AGENT" != "$AGENT_NAME" ]; then
		log_error "Locked by $CURRENT_AGENT, not $AGENT_NAME"
		exit 1
	fi

	rm -f "$LOCK_FILE"
	sed -i "/FLOCK_${AGENT_NAME}_$(basename "$FILE_PATH")/d" "$FLEXT_TOKEN"
	echo "RELEASE_${AGENT_NAME}_$(basename "$FILE_PATH")" >>"$FLEXT_TOKEN"
	log_success "Unlocked $FILE_PATH"
	;;

check)
	FILE_PATH="$2"
	LOCK_FILE="$LOCK_DIR/$(basename "$FILE_PATH").lock"

	if [ -f "$LOCK_FILE" ]; then
		CURRENT_AGENT=$(cat "$LOCK_FILE")
		log_info "Locked by $CURRENT_AGENT"
		exit 1
	else
		log_success "Available"
		exit 0
	fi
	;;

cleanup)
	# Clean locks older than 5 minutes
	find "$LOCK_DIR" -name "*.lock" -mmin +5 -delete 2>/dev/null || true
	log_success "Cleaned old locks"
	;;

*)
	echo "Usage: $0 [lock|unlock|check|cleanup] <file_path> [agent_name]"
	echo "Examples:"
	echo "  $0 lock src/flext_core/models.py AgentPlanExecutor"
	echo "  $0 unlock src/flext_core/models.py AgentPlanExecutor"
	echo "  $0 check src/flext_core/models.py"
	echo "  $0 cleanup"
	;;
esac
