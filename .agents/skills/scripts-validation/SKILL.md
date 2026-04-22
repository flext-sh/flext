---
name: scripts-validation
description: Validation services — policy gates, automated checks, ast-grep enforcement, and workspace validation. Use when using flext_infra.check or editing scripts/validation/.

---

# Scripts Validation

## Scope

- `flext_infra.check` module — Validation services (Python module in flext-core)
  - `flext_infra.check.services.WorkspaceChecker`
  - `flext_infra.check.services.PyreflyConfigFixer`
- Legacy scripts (deprecated):
  - `scripts/validation/run_automated_validation.sh` — thin wrapper around `skill_validate.py --all`
  - `scripts/core/skill_validate.py`
- `.agents/skills/*/rules.yml`
- `.agents/skills/*/rules/*.yml`
- `.agents/skills/*/baseline.json`

## References

- `AGENTS.md` — canonical governance source
- `flext-core/src/flext_infra/check/` — Module source
- `.agents/skills/flext-automation-skill-pattern/SKILL.md`
- `.agents/skills/flext-quality-gates/SKILL.md`
- `Makefile`

## Rules

- All validation is data-driven via `rules.yml` files inside each skill folder.
- The generic runner `scripts/core/skill_validate.py` discovers and executes rules.
- Baselines are stored in each skill folder as `baseline.json` (git-tracked).
- Reports are `report.json` (git-ignored, transient).
- All validators must be non-interactive and exit with clear status codes (0=pass, 1=fail, 2=usage, 3=infra).
- `rules.yml` fix metadata must use flat keys only; nested `fix:` structures are invalid.
- Supported rule types are `ast-grep` and `custom`.
- Prefer `ast-grep` rules; use `custom` only when AST matching is not applicable.
- Root `make val` is the mandatory command entrypoint for session validation.
- `make val VALIDATE_SCOPE=workspace` is the mandatory anti-drift gate: scripts inventory + strict skill validation (`scripts-validation`, `rules-github`, `rules-docker`) + `modernize_pyproject.py --audit`.
- Custom validators must be implemented inside the owning skill directory.
- Custom validator output must include machine-readable JSON with `{"violation_count": <int>}` for `skill_validate.py` compatibility.

## Instructions

- When adding a new validation gate, create a `rules.yml` in the relevant skill folder.
- Use `make val` with selectors as the default gate command for session-level validation.
- The orchestrator `scripts/validation/run_automated_validation.sh` auto-discovers all skills — no wiring needed.
- For focused runs, use `make val PROJECT=<name>`.
- Use `--mode strict` for zero-tolerance enforcement, `--mode baseline` for ratchet-only.

## Workflow

1. Identify the validation invariant to enforce.
2. Add rules to the relevant skill's `rules.yml` (type: ast-grep or custom).
3. Place ast-grep rule files in the skill's `rules/` directory.
4. Run `make val PROJECT=<name>` to set and verify targeted scope.
5. Run `make val PROJECTS="proj-a proj-b"` to verify integration scope.
6. Use `make val PROJECT=<name> FIX=1` when auto-fix is required before validation.

## Examples

Good:

```bash
make val PROJECT=flext-core
make val PROJECTS="flext-core flext-api"
make val PROJECT=flext-core FIX=1
make val PROJECT=flext-core VALIDATE_GATES=complexity
make val PROJECT=flext-core VALIDATE_GATES=docstring
make val VALIDATE_SCOPE=workspace
make val FAIL_FAST=1
```

Why good: Data-driven, reproducible, non-interactive, baseline-aware. Gate selectors allow focused validation.

Bad:

```bash
grep -r "dict" . | wc -l
```

Why bad: No baseline comparison, no structured output, no gate behavior.

## Verification

Make gates (primary):

- `make val PROJECT=<name>` — full validate gates (complexity + docstring)
- `make val PROJECT=<name> VALIDATE_GATES=complexity` — complexity only
- `make val PROJECT=<name> VALIDATE_GATES=docstring` — docstring only
- `make val PROJECT=<name> FIX=1` — auto-fix before validate
- `make val PROJECTS="proj-a proj-b"` — multi-project
- `make val VALIDATE_SCOPE=workspace` — repo-level anti-drift validation (inventory + strict skill gates + pyproject audit)
- `make val FAIL_FAST=1` — stop on first project failure

Script-level checks (internal):

- `bash -n scripts/validation/run_automated_validation.sh`

## Scripts

| Path                                             | Purpose                       | Invocation                                       |
| ------------------------------------------------ | ----------------------------- | ------------------------------------------------ |
| `scripts/validation/run_automated_validation.sh` | Internal orchestrator wrapper | `scripts/validation/run_automated_validation.sh` |
| `scripts/core/skill_validate.py`                 | Internal generic skill runner | invoked through `make val` policy flow           |
