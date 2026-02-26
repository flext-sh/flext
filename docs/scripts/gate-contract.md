# Gate Contract

<!-- TOC START -->

- [Overview](#overview)
- [Script Roles](#script-roles)
- [CLI Contract](#cli-contract)
  - [Validators](#validators)
  - [Fixers](#fixers)
  - [Environment Variables](#environment-variables)
- [Exit Codes](#exit-codes)
- [Modes](#modes)
  - [`baseline` (default)](#baseline-default)
  - [`strict`](#strict)
  - [Mode not applicable](#mode-not-applicable)
- [Artifact Output](#artifact-output)
  - [Naming Contract](#naming-contract)
  - [Report Locations](#report-locations)
- [Skill Rule Contract](#skill-rule-contract)
  - [Report JSON Structure](#report-json-structure)
- [Non-Interactive Guarantee](#non-interactive-guarantee)
- [Determinism](#determinism)
- [Script Header](#script-header)
- [Conformance Checking](#conformance-checking)
- [Examples of Conforming Scripts](#examples-of-conforming-scripts)
  - [Validator (python — skill-based)](#validator-python-skill-based)
  - [Validator (python — standalone)](#validator-python-standalone)
  <!-- TOC END -->

> Canonical specification for all validator and fixer scripts in the FLEXT repository.
>
> **Status**: Active | **Reviewed**: 2026-02-18

---

## Overview

Every script that acts as a **validator** (read-only check) or **fixer** (mutating
repair) must conform to this contract. The contract ensures deterministic behavior,
consistent CLI, stable exit codes, and predictable artifact output — making scripts
composable by the orchestrator and safe for CI.

---

## Script Roles

| Role             | Purpose                      | Default behavior               | Mutates files?                 |
| ---------------- | ---------------------------- | ------------------------------ | ------------------------------ |
| **Validator**    | Checks code against a policy | Read-only scan, report results | Never                          |
| **Fixer**        | Applies automated repairs    | Dry-run (report only)          | Only with `--apply` or `--fix` |
| **Orchestrator** | Runs multiple gates          | Delegates to validators/fixers | Never directly                 |

A script is exactly ONE role. A single script must never combine validate + fix
in its default path.

Canonical implementations in this repository:

- Validator orchestrator: `scripts/core/skill_validate.py`
- Fix orchestrator: `scripts/core/skill_fix.py`

---

## CLI Contract

### Validators

Required flags:

| Flag                      | Type   | Default    | Description                   |
| ------------------------- | ------ | ---------- | ----------------------------- |
| `--root <path>`           | string | `.`        | Repository root to scan       |
| `--mode baseline\|strict` | enum   | `baseline` | Enforcement level (see Modes) |

Optional flags:

| Flag                                   | Type    | Default          | Description                          |
| -------------------------------------- | ------- | ---------------- | ------------------------------------ |
| `--report-file <path>`                 | string  | contract default | Override report output path          |
| `--baseline-file <path>`               | string  | contract default | Override baseline path               |
| `--update-baseline`                    | boolean | `false`          | Write current counts as new baseline |
| `--baseline-strategy total\|per_group` | enum    | `total`          | Baseline comparison method           |

Validators must also accept `--root` as a positional argument (last arg fallback)
for backward compatibility with existing callers.

### Fixers

Required flags:

| Flag            | Type    | Default      | Description                                                |
| --------------- | ------- | ------------ | ---------------------------------------------------------- |
| `--root <path>` | string  | `.`          | Repository root to operate on                              |
| `--dry-run`     | boolean | **required** | Report what would change (no mutation)                     |
| `--apply`       | boolean | n/a          | Actually apply fixes (mutually exclusive with `--dry-run`) |

Optional flags:

| Flag                   | Type   | Default          | Description                 |
| ---------------------- | ------ | ---------------- | --------------------------- |
| `--mode safe\|risky`   | enum   | `safe`           | Fix aggressiveness level    |
| `--report-file <path>` | string | contract default | Override report output path |

A fixer must refuse to run if neither `--dry-run` nor `--apply` is provided (exit 2).

### Environment Variables

Scripts may read environment variables as alternatives to CLI flags, following
this naming convention:

| Variable                      | Equivalent flag           | Example               |
| ----------------------------- | ------------------------- | --------------------- |
| `FLEXT_POLICY_MODE`           | `--mode`                  | `baseline`            |
| `FLEXT_VALIDATION_ROOT`       | `--root`                  | `.`                   |
| `FLEXT_VALIDATION_REPORT_DIR` | `--report-file` directory | `.reports/validation` |

CLI flags take precedence over environment variables.

---

## Exit Codes

| Code | Meaning           | When                                                 |
| ---- | ----------------- | ---------------------------------------------------- |
| `0`  | Pass              | No violations (strict) or within baseline (baseline) |
| `1`  | Fail              | Violations found that exceed policy threshold        |
| `2`  | Invalid arguments | Bad CLI flags, missing required args, invalid mode   |
| `3`  | Runtime error     | Missing tool dependency, I/O error, unexpected crash |

Scripts must never exit with codes outside 0-3.

---

## Modes

### `baseline` (default)

- Compare current violation counts against a stored baseline snapshot.
- Pass if current counts <= baseline counts.
- On first run with no baseline file, auto-initialize from current counts.
- Baseline files live under `.sisyphus/baselines/`.

### `strict`

- Zero-tolerance: any violation is a failure (exit 1).
- No baseline comparison.

### Mode not applicable

Some validators don't have baseline semantics (e.g., syntax checks that must
always pass). These scripts:

- May omit `--mode` from their CLI.
- Must document this in their header comment: `# Gate-Contract: no-mode`.
- Must always exit 0 on pass, 1 on fail.

---

## Artifact Output

### Naming Contract

All artifacts follow: `<skill>--<kind>--<slug>.<ext>`

- `skill`: the owning skill name (e.g., `scripts-validation`)
- `kind`: file format (e.g., `json`, `txt`, `log`)
- `slug`: descriptive identifier (e.g., `policy-gate-latest`)
- `ext`: same as `kind`

### Report Locations

| Type          | Path pattern                                                                                         | Example                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Latest report | `.reports/validate/<gate>/<project>.txt` (workspace) or `.claude/skills/<skill>/report.json` (skill) | `.reports/validate/type-check/flext-core.txt`                |
| Baseline      | `.claude/skills/<skill>/baseline.json`                                                               | `.claude/skills/flext-strict-typing/baseline.json`           |
| Fix report    | `.claude/skills/<skill>/fix-report.json`                                                             | `.claude/skills/flext-pyrefly-typecheck-fix/fix-report.json` |

Do not write validation artifacts to `.sisyphus/`.

---

## Skill Rule Contract

- Skill rules are loaded only from `.claude/skills/*/rules.yml`.
- Rule fix metadata must use flat keys only: `fix_auto`, `fix_type`, `fix_file`, `fix_script`, `fix_instruction`, `fix_description`.
- Nested `fix:` metadata in `rules.yml` is invalid.
- If `fix_auto: true`, the fix mechanism must be executable and target files must exist.
- Prefer `type: ast-grep` rules; use `type: custom` only when AST matching is not applicable.

### Report JSON Structure

Validators should emit a JSON report containing at minimum:

```json
{
  "mode": "baseline|strict",
  "root": ".",
  "scan_succeeded": true,
  "counts": {
    "<group_name>": 0
  }
}
```

Fixers should emit a JSON report containing at minimum:

```json
{
  "mode": "safe|risky",
  "dry_run": true,
  "root": ".",
  "files_checked": 0,
  "files_modified": 0,
  "changes": []
}
```

---

## Non-Interactive Guarantee

Scripts must be fully non-interactive by default:

- No `input()` calls (Python)
- No `read -p` prompts (Bash)
- No `select` menus (Bash)
- No `dialog`/`whiptail` usage

If a script needs interactive mode for manual use, it must:

- Be gated behind an explicit `--interactive` flag.
- Default to non-interactive behavior.

---

## Determinism

- Output must be deterministic given the same input.
- Lists must be sorted (alphabetically by file path, then by line number).
- JSON output must use `indent=2` and `sort_keys=True` (Python) or equivalent.
- Timestamps in reports are acceptable but must not affect exit codes.

---

## Script Header

Every gate script must include these elements in its first 10 lines:

```bash
#!/usr/bin/env bash
# Owner-Skill: .claude/skills/<skill-name>/SKILL.md
```

or for Python:

```python
#!/usr/bin/env python3
# Owner-Skill: .claude/skills/<skill-name>/SKILL.md
"""One-line description of what this gate checks."""
```

---

## Conformance Checking

The contract validator (`scripts/core/check_script_gate_contract.py`) verifies:

1. **Owner-Skill marker** present in first 10 lines.
2. **Shebang line** present (`#!/usr/bin/env bash` or `#!/usr/bin/env python3`).
3. **Exit code hygiene**: bash scripts use only `exit 0`, `exit 1`, `exit 2`, `exit 3`.
4. **No interactive prompts** in default path (unless `--interactive` gated).
5. **Artifact naming**: any explicit report paths in scripts must target `.reports/` and follow the naming contract.
6. **Non-empty**: scripts classified as validators/fixers have >= 20 lines of code.

Scripts not classified as validators or fixers (libraries, orchestrators) are
exempt from gate contract validation but must still have Owner-Skill markers.

---

## Examples of Conforming Scripts

### Validator (python — skill-based)

- `python3 scripts/core/skill_validate.py --skill flext-strict-typing` — discovers rules from `.claude/skills/flext-strict-typing/rules.yml`; accepts `--mode baseline|strict`; exits 0/1/2/3
- `python3 scripts/core/skill_validate.py --skill lib-pydantic-v2` — same contract
- `python3 scripts/core/skill_validate.py --all` — runs all discovered skills

### Validator (python — standalone)

- `.claude/skills/scripts-infra/validate_ownership.py --root .` — exits 0/1; produces JSON report
- `.claude/skills/scripts-infra/validate_artifact_naming.py --root .` — exits 0/1; produces JSON report
