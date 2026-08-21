---
name: flext-law
description: Apply the FLEXT-only architecture, workspace, generation, import, and fleet delta over canonical global execution governance.
---

# FLEXT Law

## Composition

Sole `flext-law` owner. Globals: `inviolable-rules`, `make-check`, `verification-loop`. Load via `flext-context-routing` only. Gas Town rig `flext` is the authoritative workflow surface.

## Architecture and imports

`flext-core <- consumers`. `flext-infra` never runtime. Facades `c→t→p→m→u` + `r/e/x/h/d/s`; reverse `TYPE_CHECKING`-only. One `api.py`; lazy generated root. `from <ns> import s`. Declarations = data; Pydantic v2 + `t.*`/`p.*` at boundaries.

## Search before inventing

Search `c→t→p→m→u` (+`r`/`e`) before helpers. Prefer `u.*`. Bead-note if inventing.

## Sources, generation, and commands

SSOT `config/*.yaml`+settings/schemas. Cutover: owner→regen→delete old. No hand-edit generated consumers. See `make-check`. Fixtures via `flext-tests` facades.

## Config Settings Are SSOT

Config owns configurable facts — never hardcode in code/tests (`UNIVERSAL_CORE` P0).

## Runtime First Completion Gates

See `verification-loop` + public-facade QA.

## Fleet boundary

First-party/standalone share branch-matched law. External/content-only: no mutate. CI = conform + overlays.

## Fleet ancestry and managed topology

Typed inventory+Beads. `0.12.0-dev` ancestor of `main`/`0.20.0-dev`/required branches/worktrees. Merge-forward only. Exclude `gh/*`, Dolt, archives, `external`/`content_only`. Members before superproject gitlinks.

## Toolchain and conform

Conform from Git+manifest. Mise binaries; no `uv`/Python patch pins (`3.13.*`). Ruff+Pyrefly; changed Pyright/Mypy/Pytest. Helm serialized. Release = `flext-infra` Make release/version. `ast-grep` for systemic transforms.

### Gas Town-native lane lifecycle

Preferred workflow: `gt sling` / `gt convoy` / `gt mol` / `gt done` / `gt handoff` for rig `flext`.

Gas Town is the sole lane lifecycle owner. The retired Make lane lifecycle must
not appear in current commands, generated guidance, or consumer documentation.
Disposition: ADR-0016.
Lane completion evidence includes hook status, convoy state, and Refinery merge
evidence. Make evidence covers build and validation only.

## Documentation and ADRs

Living docs follow `docs/standards/documentation.md`. Architecture decisions live in `docs/architecture/adr/` (ADR registry). Docs validation requires these ADR references in provider skills.
