# CLAUDE.md — Pointer Index

**Reviewed**: 2026-04-06 | **Scope**: Pointer-only entrypoint for Claude-compatible agents

Canonical source: [`AGENTS.md`](AGENTS.md). This file stays brief on purpose. Do not duplicate governance here.

## Load Order

1. Read [`AGENTS.md`](AGENTS.md).
2. For facade, import, or namespace work, load:
   - [`.claude/skills/flext-mro-namespace-rules/SKILL.md`](.claude/skills/flext-mro-namespace-rules/SKILL.md)
   - [`.claude/skills/flext-import-rules/SKILL.md`](.claude/skills/flext-import-rules/SKILL.md)
   - [`.claude/skills/flext-patterns/SKILL.md`](.claude/skills/flext-patterns/SKILL.md)
3. For doc or skill edits, also load:
   - [`.claude/skills/flext-docs-pointer-policy/SKILL.md`](.claude/skills/flext-docs-pointer-policy/SKILL.md)
   - [`.claude/skills/skill-format-universal/SKILL.md`](.claude/skills/skill-format-universal/SKILL.md)

## Namespace Checklist

- `src/` facades: `Flext<Project><Tier>`
- `tests/` facades: `TestsFlext<Project><Tier>`
- Public facades own exactly one local domain namespace at the root.
- Test-only scope stays under `<Domain>.Tests`.
- Compose `_models/*` and `_utilities/*` through facade MRO; never manually wrap them into nested flat classes.
- Same-project cross-facade imports are runtime-illegal unless `AGENTS.md` §4 explicitly allows them through `TYPE_CHECKING`.
- Keep organic MRO paths at call sites: `u.Infra.*`, `c.Tests.*`, `m.TargetOracle.*`; do not flatten them to `m.ExecuteResult`.

## Maintenance

- All rule changes land in `AGENTS.md` first.
- Keep `CLAUDE.md` pointer-only and under 50 lines.
- Validate governance changes with `make validate VALIDATE_SCOPE=workspace`.
