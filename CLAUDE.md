# CLAUDE.md — Canonical Engineering Rules

**Reviewed**: 2026-02-18

This file is the canonical source of truth for agent behavior in this repository.
Agent-specific files must reference this file and must not duplicate policy text.

## Non-Negotiable Rules

- No bypasses or workaround paths in validation/fix pipelines.
- No silent failure patterns (`2>/dev/null`, `|| true`, warning-only fallthrough for mandatory gates).
- No suppression-based typecheck escapes (`# pyrefly: ignore`, baselines as permanent suppression, ignore comments).
- No project-local `.venv`; workspace `.venv` is mandatory.
- Every required wave step must be complete before advancing.

## Skill System Contract

- Skills are discovered only from `.claude/skills/*/rules.yml`.
- Rule schema uses flat fix keys only: `fix_auto`, `fix_type`, `fix_file`, `fix_script`, `fix_instruction`, `fix_description`.
- Nested `fix:` metadata in `rules.yml` is invalid for `skill_validate.py`/`skill_fix.py` orchestration.
- `fix_auto: true` must resolve to an executable fix mechanism and existing target file/script.
- Prefer `type: ast-grep` rules. Use `type: custom` only when AST-based detection is not applicable.

## Validation/Fix Entry Points

- Validator: `python scripts/core/skill_validate.py --all --mode strict`
- Fixer (dry-run): `python scripts/core/skill_fix.py --all --dry-run`
- Fixer (apply): `python scripts/core/skill_fix.py --all --apply`
- Workspace gate target: `make validate-scripts`
- Clean actionable report target: `make quality-report`
- Hard fail clean gate target: `make check-clean`

Exit code contract:
- `0` pass
- `1` policy failure
- `2` usage/configuration error
- `3` infrastructure/runtime error

## Reporting and Artifacts

- Validation reports are machine-readable JSON artifacts.
- Workspace validation artifacts live under `.reports/validate/`.
- Skill-local reports remain under `.claude/skills/<skill>/report.json` and `.claude/skills/<skill>/fix-report.json`.
- Do not write validation artifacts to `.sisyphus/`.
- Reports must include explicit next actions (`TODO: make PROJECT=<name> <target>`) for every failed gate.

## AST-Grep First and Script Locality

- Prefer `ast-grep` for detection and mechanical rewrites whenever feasible.
- Use `custom` rules only when AST matching cannot express the constraint.
- Custom rule scripts must live inside the owning skill folder (for example, `.claude/skills/<skill>/...`).
- `scripts/core` is reserved for generic orchestrators and shared infra only (`skill_validate.py`, `skill_fix.py`, `stub_supply_chain.py`, and shared helpers).
- Do not add skill-specific fix/validation logic under `scripts/core`.

## Typing Supply Chain Rules

- Manual stubs belong in `typings/`.
- Generated stubs belong in `typings/generated/`.
- Generated stubs are for third-party dependencies only.
- Never generate stubs for internal FLEXT modules (`flext_*`, `client-a_*`, `client-b_*`).
- Internal missing imports are source/type architecture defects and must be fixed in code, not stubbed.

## Required Preflight for Workspace Loops

Before any workspace-wide loop (`make lint`, `make fix`, `make type-check`, `make validate*`):

- Ensure workspace virtualenv exists at `.venv`.
- Ensure no project-local `.venv` directories exist.
- Fail immediately if preflight fails.

## Change Management

- Root-cause fixes only; no temporary mitigation paths.
- Keep changes minimal, explicit, and verifiable.
- Validate behavior with direct command evidence after every change.
- If policy and implementation diverge, update this file first, then sync skill documents.
