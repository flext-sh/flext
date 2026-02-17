#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# Artifact naming helpers for the <skill>--<kind>--<slug>.<ext> contract.

# Build an artifact filename: skill--kind--slug.ext
# Usage: artifact_name "scripts-validation" "json" "policy-gate-latest" -> "scripts-validation--json--policy-gate-latest.json"
artifact_name() {
  local skill="$1" kind="$2" slug="$3"
  echo "${skill}--${kind}--${slug}.${kind}"
}

# Build full path under .sisyphus/<dir>/
# Usage: artifact_path "reports" "scripts-validation" "json" "policy-gate-latest" -> ".sisyphus/reports/scripts-validation--json--policy-gate-latest.json"
artifact_path() {
  local dir="$1" skill="$2" kind="$3" slug="$4"
  echo ".sisyphus/${dir}/${skill}--${kind}--${slug}.${kind}"
}

# Validate an artifact filename matches the contract
# Returns 0 if valid, 1 if invalid
validate_artifact_name() {
  local filename="$1"
  [[ "$filename" =~ ^[a-z][-a-z0-9]*--[a-z]+--[a-z][-a-z0-9]*\.[a-z]+$ ]]
}
