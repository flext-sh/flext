#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
set -euo pipefail

python3 scripts/core/skill_validate.py --skill scripts-validation --mode strict "$@"
