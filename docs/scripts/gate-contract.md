# Gate Contract

> This is the canonical gate-contract document. Workspace validation uses the
> root dispatcher (`make check WHAT=<action>`); script-specific CLI examples
> remain explicit where no verified Make route exists.

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

- Skill validator: `flext-infra validate skill-validate --skill <name>` (canonical CLI, one invocation per skill)
- Enforcement fixer: `flext-infra codegen fix-enforcement` (dry-run by default; mutates only with `--apply`)

---

## CLI Contract

### Validators

Required flags:

| Flag              | Type    | Default | Description             |                               |
| ----------------- | ------- | ------- | ----------------------- | ----------------------------- |
| `--root <path>`   | string  | `.`     | Repository root to scan |                               |
| `--mode baseline\ | strict` | enum | `baseline` | Enforcement level (see Modes) |  |

Optional flags:

| Flag                        | Type       | Default          | Description                          |                            |
| --------------------------- | ---------- | ---------------- | ------------------------------------ | -------------------------- |
| `--report-file <path>`      | string     | contract default | Override report output path          |                            |
| `--baseline-file <path>`    | string     | contract default | Override baseline path               |                            |
| `--update-baseline`         | boolean    | `false`          | Write current counts as new baseline |                            |
| `--baseline-strategy total\ | per_group` | enum | `total` | Baseline comparison method |  |

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

| Flag                   | Type   | Default          | Description                 |                          |
| ---------------------- | ------ | ---------------- | --------------------------- | ------------------------ |
| `--mode safe\          | risky` | enum | `safe` | Fix aggressiveness level |  |
| `--report-file <path>` | string | contract default | Override report output path |                          |

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

|Type|Path pattern|Example|
|-------------|----------------------------------------------------------------------------------------------------|------------------------------------------------------------|
|Latest report|`.reports/validate/<gate>/<project>.txt` (workspace) or `~/.agents/skills/<skill>/report.json` (skill)|`.reports/validate/type-check/flext-core.txt`|
|Baseline|`~/.agents/skills/<skill>/baseline.json`|`~/.agents/skills/flext-strict-typing/baseline.json`|
|Fix report|`~/.agents/skills/<skill>/fix-report.json`|`~/.agents/skills/flext-pyrefly-typecheck-fix/fix-report.json`|

Do not write validation artifacts to `.sisyphus/`.

---

## Skill Rule Contract

- Skill rules are loaded only from the active `~/.agents/skills/*/rules.yml`.
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
# Owner-Skill: ~/.agents/skills/<skill-name>/SKILL.md
```

or for Python:

```python
#!/usr/bin/env python3
# Owner-Skill: ~/.agents/skills/<skill-name>/SKILL.md
"""One-line description of what this gate checks."""
```

---

## Conformance Checking

The contract validator (`flext-infra validate skill-validate --skill <name>`) verifies:

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

- `flext-infra validate skill-validate --skill flext-strict-typing` — discovers
  rules from the active `config.AiHub.paths.agents_home` provider; accepts `--mode baseline|strict`;
  exits 0/1
- `flext-infra validate skill-validate --skill flext-pydantic-models --mode strict`
  — same contract
- one invocation per skill (see the Makefile `validate` targets); the retired
  `scripts/core/skill_validate.py --all` flag form no longer exists

### Validator (python — standalone)

- `flext-infra validate skill-validate --skill <name>` — validates owner and
  artifact metadata through the canonical provider; exits 0/1
