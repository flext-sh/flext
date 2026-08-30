---
name: flext-law
description: Apply the FLEXT-only architecture, workspace, generation, import, and fleet delta over canonical global execution governance.
---

# FLEXT Law

## Composition

Architecture decisions are recorded under `docs/architecture/adr/`; the
ADR records there are the durable rationale this law enforces.

This repository is the sole owner of the skill named `flext-law`. AI Hub
projects it but does not author it. Generic conduct, lane safety, evidence,
Make-command selection, and completion gates remain owned by:

- `~/.agents/skills/inviolable-rules/SKILL.md`
- `~/.agents/skills/make-check/SKILL.md`
- `~/.agents/skills/verification-loop/SKILL.md`

Read those skills and root `AGENTS.md`; this file adds only FLEXT domain law.

## Architecture and imports

- Dependency direction is `flext-core <- consumers`. `flext-infra` owns build,
  conform, codegen, and policy; it is never a runtime dependency.
- Facades compose in strict order `c -> t -> p -> m -> u`, with operational
  `r/e/x/h/d/s`. Reverse imports are `TYPE_CHECKING`-only.
- Each package has one thin `api.py` MRO facade and one simple generated root
  `__init__.py` with automatic lazy public exports. Custom import routers,
  eager alternatives, compatibility aliases, and duplicate facades are
  forbidden.
- Service exposure follows the canonical short alias: `base.py` imports `s`
  from `flext_core`, the package root lazily re-exports `s`, and consumers use
  `from <namespace> import s`. Never rename it to `core_s` or substitute an
  alternative service-base import.
- Declaration layers are pure data. Behavior belongs in utilities, services,
  bases, facades, or CLI layers. Owned data crosses boundaries through typed
  Pydantic v2 models and project `t.*`/`p.*` contracts.

## Sources, generation, and commands

- `config/*.yaml`, typed settings, schemas, and generator policy are the SSOT.
  Change the owner, regenerate every projection, and remove the superseded
  implementation in the same cutover.
- Generated facets, root imports, managed `pyproject.toml` sections, Make
  surfaces, CI, and documentation are never hand-edited at consumers. Their
  canonical owner is `flext-infra` plus explicit `config/` overlays.
- Run setup, conform, codegen, docs, checks, tests, WAZA, and publication only
  through the active workspace root Make dispatcher. A missing or broken verb
  is repaired generically in `flext-infra`, then reused by workspace and
  standalone projects; it is never bypassed.
- `flext-tests` owns reusable fixtures and behavior helpers. Packages consume
  them through public facades rather than creating local copies.

## Fleet boundary

- First-party FLEXT members and standalone repositories consume the same
  branch-matched law, Make control plane, and generated conventions.
- Third-party forks and content-only repositories are not FLEXT members: do
  not mutate, lint, generate, or manage them. Required interaction is declared
  as typed metadata or a bounded `config/` overlay.
- Workspace and standalone CI are generated once by `flext-infra conform`.
  Exceptions are configuration overlays, never duplicate pipelines or custom
  implementations.
- Historical branches, archives, generated outputs, and other worktrees are
  evidence only. The active branch-matched canonical sources define behavior.
