#!/bin/bash
# Wrapper script for editing files with lock coordination
# Usage: ./edit_with_lock.sh <file_path> <agent_name> <editor_command>

set -euo pipefail

FILE_PATH="$1"
AGENT_NAME="$2"
EDITOR_CMD="${3:-nano}"

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

# Try to acquire lock
if ./scripts/file_lock.sh lock "$FILE_PATH" "$AGENT_NAME"; then
	log_success "Lock acquired, opening editor..."

	# Open editor
	$EDITOR_CMD "$FILE_PATH"

	# Release lock
	./scripts/file_lock.sh unlock "$FILE_PATH" "$AGENT_NAME"
	log_success "Lock released"
else
	log_error "Failed to acquire lock for $FILE_PATH"
	exit 1
fi
