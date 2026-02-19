#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
set -euo pipefail

echo "[validate-scripts] running pre-test validation gates (no pytest)"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
	echo "[validate-scripts] ERROR: workspace .venv missing at $ROOT_DIR/.venv"
	echo "[validate-scripts] Run 'make setup' first."
	exit 1
fi

"$VENV_PYTHON" "$ROOT_DIR/scripts/core/skill_validate.py" --skill scripts-validation --mode strict "$@"
