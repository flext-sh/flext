---
name: flext-import-rules
description: >-
  Enforce canonical FLEXT import routing, public facade boundaries,
  declaration-only imports, and cycle-free package direction. Use when adding
  or moving imports, resolving cycles, reviewing external-library boundaries,
  or composing c/m/p/r/t/u/s facades; do not use to invent a project layout.
---

# FLEXT import routing

Treat imports as dependency declarations. Read the target package's public
facade and dependency metadata before changing them; this skill is an
operating procedure, not the declaration SSOT.

## Procedure

1. Identify whether the file owns a facade/bridge or consumes one.
2. Import consumers from the owning package root and its canonical short
   aliases.
3. Let only the facade or bridge owner import its private implementation or
   external framework.
4. Keep runtime dependencies at runtime; use `TYPE_CHECKING` only for symbols
   needed solely by static declarations.
5. Remove the superseded import path in the same change.
6. Run the target repository's configured Ruff and type gates.

## Invariants

- Use absolute imports in production code. Do not use relative or wildcard
  imports.
- Import FLEXT consumers through public package roots, such as
  `from flext_core import c, m, p, r, t, u`.
- Import project-owned `config` and `settings` from that project's public root;
  do not read environment variables or configuration files from leaf modules.
- Let a facade owner import the upstream short alias it extends, compose the
  local facade, and publish the local alias exactly once. Downstream consumers
  import that local alias from the package root.
- Let only the canonical bridge owner import Pydantic, Structlog, database
  drivers, template engines, or other external frameworks. Consumers import
  the validated model or wrapper from its owning FLEXT package.
- Keep private implementation imports inside their public facade/composition
  owner. A consumer importing a private module is an ownership violation.
- Preserve runtime direction `flext-infra -> flext-cli -> flext-core`; core must
  not import cli or infra at runtime.
- Never use `TYPE_CHECKING` to hide a runtime class, method, side effect, or
  dependency cycle. Move declaration-only contracts to their canonical
  protocol/type owner and fix runtime ownership at the source.
- Follow the repository's configured import ordering. Do not invent universal
  required imports that its configuration does not declare.

Read [references/import-rules-detail.md](references/import-rules-detail.md)
only when concrete routing examples are needed.
