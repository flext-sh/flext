# ADR-025 — The fleet toolchain has no npm backend

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Evidence](#evidence)
- [References](#references)

<!-- TOC END -->

- **Status:** ACCEPTED (operator approval 2026-10-08, tracker memory
  `operator-ruling-2026-10-08-npm-free-toolchain`)
- **Amended:** operator rulings of 2026-10-09, recorded in the selected native
  Beads stores as `operator-ruling-2026-10-09-setup-resilient` (FLEXT) and
  `operator-ruling-2026-10-09-bun-project-everywhere` (AI Hub primary
  `aihub/project5e6a1521`, checkout `~/ai-hub`). The October 8 evidence below
  predates these amendments and does not prove their implementation.
- **Supersedes:** ADR-020 (bun installs the npm-backed mise tools)
- **Scope:** `flext-infra` `toolchain.tools`, every generated `.mise.toml`,
  `mise.lock`, `Makefile`, and the `markdown-format` gate.
- **Bead:** `flext-0shvv`
- **Complements:** ADR-004 (generated Make), ADR-005 (SSOT), ADR-010
  (standardization).

## Context

ADR-020 made bun the installer for the two npm-backed fleet tools
(`npm:@ast-grep/cli`, `npm:prettier`). The investigation for `flext-0shvv`
measured three defects in that design:

1. **bun is not self-contained.** When the global install directory has no
   `package.json`, bun walks up to an ancestor project. Under
   `~/.local/share/mise/installs/npm-*`, that ancestor is the operator's home:
   `bin/prettier`, `bin/sg` and `bin/gemini` were symlinks into
   `~/node_modules`, and `~/package.json` received bun pins. mise has no
   setting or hook that stops the walk-up.
2. **The lock carried no integrity.** Under bun, `mise.lock` keeps only the
   top-level version of an npm tool: no checksum and no dependency graph.
3. **The gate was falsely green.** The real prettier 3.5.3 failed files that
   the PATH-resolved prettier from `~/node_modules` accepted. Two
   `tooling.yaml` exclusions, justified as a "runner-side prettier"
   disagreement on 2026-10-07, hid that same defect.

In addition, a bare `mise install` in `make setup` also installed every tool of
the operator's global Mise registry.

## Decision

1. **No npm-backed tool in the fleet toolchain.** The toolchain model rejects
    an `npm:` selector at load. `npm_package_manager`, the npm-only `inline`
    form and the `[settings.npm]` projection remain retired. Removal of the
    `bun` entry was the October 8 disposition, not the amended contract:
    distributed JavaScript tools, including FLEXT's, belong to one owned Bun
    project with `package.json` and its frozen lock. This does not restore the
    Mise npm backend or remove native Node wrappers where consumers use them.
2. **ast-grep comes from aqua** (`aqua:ast-grep/ast-grep`), locked per
   platform in `mise.lock` like every other aqua tool. ast-grep publishes
   glibc-only binaries; no channel ships a musl build.
3. **rumdl formats markdown.** The `markdown-format` gate runs
   `rumdl fmt --check` in `make check` and `rumdl fmt` in `make fmt`, reading
   the same generated `.markdownlint.json` as the `markdown` gate. rumdl is
   locked in `uv.lock`. The generated `.prettierrc` and `.prettierignore` are
   retired projections that `make gen` deletes. MD077, disabled only because
   prettier contradicted it, is enabled again. The two exclusions that hid the
   runner disagreement are removed.
4. **`make setup` installs only declared tools.** Every generated
   `mise install` receives the explicit key list
   (`toolchain.mise_install_keys`), so the operator's global registry is never
   provisioned by a project verb.
5. **Setup provisions; audit judges locks.** `make setup` provisions from the
    current committed locks without resolving releases or writing locks.
    Missing, stale or incomplete lock declarations remain defects judged by
    `make audit`, which CI runs after setup. An absent Mise self-pin permits
    the qualified host Mise provisioning path; it never invents a pin or
    certifies lock integrity. Functional installation failures always keep
    setup red, with their native diagnostics and exit status.
    The audit's `flext-infra codegen mise-proof` checks declared tools in order
    and stops at the first defect: the `mise.lock` entry exists and carries a
   current-platform checksum (unless the tool declares `lock_checksum: false`
   because its upstream publishes none); `mise where` names the install root;
   `mise which <binary>` and every symlink hop stay inside that root; the
   tool's declared `version_probe` (data in `codegen.yaml`, no default)
    reports the locked version. Audit has no fallback, retry, or warning-only
    verdict. `make upg` alone owns resolution and lock writes.

## Consequences

- Provisioning uses only declared destinations, never an ancestor JavaScript
  project or the host's global npm registry. Native binary, Python and Bun
  dependency locks retain their respective owners; none certifies another's
  dependency graph.
- prettier-only normalizations (table padding, embedded-code reformatting) are
  no longer enforced; the rumdl rule set in `tooling.yaml` is the single
  markdown contract.
- Consumers whose org layer still pins `prettier` in `tool_version_pins` fail
  config validation (an unknown pin is rejected) until the pin is removed in the
  propagation wave; at decision time that is `flext-cli` and `flext-core`.
- The October 8 global Mise/npm disposition is historical. The October 9 Bun
  project ruling supersedes it for distributed JavaScript tools; this record
  does not authorize modifying host configuration.
- Source-owner cutovers and installed-artifact proof remain separate work.
  This documentary amendment certifies neither current provisioning nor CI.

## Evidence

These are dated October 8 observations, not receipts for the amended contract.

- Research and option matrix: `flext-0shvv` proposal (mise `v2026.10.3` source
  `src/backend/npm.rs`, `src/toolset/tool_version.rs`,
  `src/cli/install.rs`).
- A read-only `rumdl fmt --check` (and `rumdl check`) over the root workspace with
  the new `.markdownlint.json` projection (MD077 enabled) found no file to rewrite
  and no finding in 4606 files; the `markdown-format` gate passed read-only in the
  root and all 31 members (2026-10-08).
- On the implementing host, `make setup` ran `flext-infra codegen mise-proof` and
  proved all 16 declared `toolchain.tools` entries (lock checksum, install-root
  containment, version probe); `ast-grep 0.45.3` resolved inside
  `installs/aqua-ast-grep-ast-grep`. Implementation: flext-infra PR #1848.

## References

- ADR-020 (superseded)
- ai-hub ADR-0037 (user registry ownership)
- [mise npm backend](https://mise.jdx.dev/dev-tools/backends/npm.html)
