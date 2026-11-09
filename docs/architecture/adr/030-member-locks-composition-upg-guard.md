# ADR-030 — Member Locks and Workspace Lock Composition

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Lock formation and composition](#lock-formation-and-composition)
- [The upgrade guard](#the-upgrade-guard)
- [Proposed design (implementation pending)](#proposed-design-implementation-pending)
- [Superseded statements](#superseded-statements)
- [Current state](#current-state)
- [Consequences](#consequences)

<!-- TOC END -->

- **Status:** ACCEPTED for lock ownership and composition; Git-state admission
  guards are removed by the current operator correction recorded on `flext-92rpb`.
- **Date:** 2026-10-25
- **Scope:** the FLEXT superproject, every member, standalone FLEXT checkouts and
  external consumers that bind FLEXT editable (ai-hub and others)
- **Tracker memories:** `operator-ruling-2026-10-25-member-locks-uv-mise-upg-guard`,
  `operator-rulings-2026-10-25-libnames-locks-ldif-rope` (answer 2)
- **Supersedes:** the same-day "only the root lock" decision recorded in ADR-003
  (verification contract), in the root `AGENTS.md` `flext-0029c` target paragraph,
  in `.agents/skills/flext-law/SKILL.md`, in `flext-infra/AGENTS.md` and in
  `flext-infra/docs/guides/execution-context.md` ("Dependency locks")
- **Complements:** ADR-003 (root workspace metadata), ADR-024 (DI config contract:
  a repository declares only its own deltas), ADR-025 (fleet toolchain), ADR-029
  (one complete cycle per slice)

## Context

Members retain their own locks so standalone installations have their own native
dependency resolution. Lock ownership does not impose Git-state prerequisites on
development commands or equality between an explicitly selected editable tree and
a committed dependency pin.

## Decision

1. **Member locks are kept.** Every member and every standalone FLEXT repository
   commits its own `uv.lock` and `mise.lock`. Each is formed from that repository's
   own declarations only (ADR-024: a repository declares only itself).
2. **The workspace lock is the composition of the member locks.** For uv, the
   superproject's `uv.lock` composes what the members declare and lock. For Mise,
   the composition is the configuration layering itself: each configuration root
   locks beside itself and no merged root lock duplicates member facts (see the
   [proposed design](#proposed-design-implementation-pending)). The workspace never
   introduces a resolution that contradicts a member lock, and a member never reads
   the workspace lock as its own.
3. **Only `make upg` writes locks**, for uv and for Mise alike. `make setup`,
   `make gen`, `make fmt` and every other verb install from or read the committed
   locks and never write them (global `conformance-sweep` rule; ADR-029).
4. **The dependency hierarchy is pinned by exact SHA.** Internal requirements keep
   their Git URL and declared integration line in `pyproject.toml`; each lock pins
   the exact commit (tracker memory
   `operator-ruling-2026-10-24-lock-sha-pyproject-url-waves`). Composition preserves
   those pins, so the workspace lock and each member lock agree commit by commit.
5. **Native tools own upgrade execution.** Clean-tree, branch, gitlink and
   editable-HEAD-versus-lock admission layers do not precede their commands.

## Lock formation and composition

| Context                                      | Who forms the lock                    | What the lock binds                                                                      |
| -------------------------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------- |
| Member inside the workspace                  | the member, from its own declarations | its declared internal Git requirements, pinned by exact SHA                              |
| Workspace root                               | the root, composing the member locks  | every member at the committed gitlink SHA plus the composed third-party resolution       |
| Standalone FLEXT checkout                    | the checkout itself                   | the internal requirements it declares, pinned by exact SHA                               |
| Installed as a package (pip, non-editable)   | not applicable                        | the consumer's `uv.lock` follows what it is bound to                                     |
| Standalone with an external editable `.venv` | the standalone consumer               | the external project's committed SHA, recorded through the consumer's committed gitlinks |

Remote CI installs the committed locks frozen and never relocks (tracker memory
`operator-ruling-2026-10-24-ci-frozen-homologated-locks`). Member CI therefore
installs from the member's own committed lock, and workspace CI from the composed
workspace lock.

Local `make setup FLEXT=<workspace>` retains the consumer's mandatory frozen
installation before source binding. Executor self-hosting must use the native
declaration owners without forming or writing another lock, followed by the
existing typed selection owner in the physical consumer environment. That owner
validates the complete selection and publishes its existing receipt. Local
override paths are runtime inputs, never captured in generated Makefiles. The
frozen installation owns dependency resolution; the executor bootstrap binds its
declared editable requirements without dependency resolution or unrelated UV
configuration overriding the explicit source selection. The
[execution-context contract](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/docs/guides/execution-context.md#generation-staging-transaction-journals-and-modernization)
owns the source-only bootstrap target and its still-pending implementation and
cold consumer proof; workspace-only export cannot be presumed to include the
excluded editable path dependencies described below. Local source binding does
not require the selected HEAD to equal the frozen installation's Git pin.

**Release eligibility.** Clarification of 2026-11-02, documentation only (reconciliation
of the retired 2026-09-10 cooldown plan, bead `flext-tvkbj`); no decision changes. The
releases `make upg` may lock are bounded by one fleet cooldown, declared once as
`codegen.toolchain.dependency_cooldown_days` in
`flext-infra/src/flext_infra/config/codegen.yaml` (global rule `security/supply-chain`:
a rolling cooldown, never a fixed date). The generator projects that single value to
the Mise `[settings]` `minimum_release_age` and to the `cooldown.default-days` of every
Dependabot ecosystem entry; requirements a project takes by direct Git reference (the
FLEXT members and `rope`) are excluded from the Dependabot cooldown. uv carries no
cooldown key: `exclude-newer` and `exclude-newer-package` stay banned in every form,
and conform removes both from `[tool.uv]` unconditionally
(`flext-infra/src/flext_infra/_utilities/_pyproject/uv_sources.py`). Vulnerable
transitive packages are held by hand-reviewed floors in `uv_constraint_dependencies`,
projected to `[tool.uv] constraint-dependencies` (tracker memory
`operator-ruling-2026-10-24-security-cooldown-and-fp`; bead `flext-y9dqj`).

## The upgrade guard

There is no Git-state admission guard. `make upg` calls the native dependency
writers on declared manifests; generation uses the executing tool, and
`make setup FLEXT=<path>` binds the selected source trees. A differing HEAD,
uncommitted work or a stale gitlink is not a reason to refuse those operations.
The original command's functional result is the evidence.

**One-time Rope exception, 2026-10-28.** The operator answered "Autorizar
exceção pontual para Rope" to the explicit request to update only the Rope pin
and corresponding locks through `make upg`, then activate through `make setup`,
with the current WIP preserved and every gate retained. Tracker memory
`operator-exception-2026-10-28-rope-only-upg-wip` records the question and answer.
This historical exception covered the causal native-SDK cutover only. It permits no site-packages
patch, and does not establish SDK qualification or installation evidence.

Selected source updates cover runtime, optional and development declarations
through the existing requirement-group traversal. They change only the selected
direct-reference URL; extras, markers, native inclusion tables, array positions
and comments retain their owners. Distinct conditional overrides remain native
UV policy: conflicting source URLs cannot be collapsed into one project
requirement and must fail before publication.
The existing pyproject owner separates override selection from the URL-only
replacement of each requirement; both consume the same captured document.

**Closure, 2026-10-31.** The operator ruled the one-time Rope exception used up
(answer: "Exception used up, remove"). The selected-upgrade path it relied on
(`FLEXT_INFRA_UPGRADE_PACKAGES`, the Python `--upgrade-package` route and the
selected-override projection) is removed: it was a second uv lock writer running
inside the environment it had to repair, against the repair-never-deadlocks
ruling. `make upg` now has one uv lock writer, the native `uv lock --upgrade`
in the generated template, followed by the frozen sync and `workspace
verify-lock`. The two paragraphs above are historical evidence only.

## Proposed design (implementation pending)

Agent 11's design for the stabilization task force, recorded 2026-10-25. It is a
design, not implemented behavior. Its two verification questions, V1 and V2, were
measured on fixtures the same day and are settled below; the implementation is
pending.

**Mise.**

- Each member's `.mise.toml` declares only its own deltas, generated from its
  declared toolchain.
- The root sets `monorepo_root = true` with `[monorepo] lockfile = false`, and its
  `config_roots` are derived from `.gitmodules`.
- Each configuration locks beside itself; the workspace composition is the
  configuration layering. A merged root lock is rejected because it would either
  delete the member locks or duplicate their facts.
- **V1 (settled):** with `[monorepo] lockfile = false`, each configuration root
  locks only its own declared tools, one process per root, which is what the ruling
  requires. `lockfile = true` locks everything in one process but merges and
  deletes the member locks, which contradicts the ruling; it is rejected. Evidence:
  fixture `~/tmp/flext-1engx/agent11/v1`, measured with `mise lock --dry-run`.

**uv.**

- Members are excluded from the uv workspace (the `exclude` list derived from
  `.gitmodules`) and declared at the root as editable path sources.
- Each member keeps its FLEXT dependencies as Git sources at an exact SHA and runs
  `uv lock` to form its own `uv.lock`; the root `uv.lock` is the composition.
- **V2 (settled):** a member pinning a dependency as Git at an exact SHA while the
  root binds the same distribution as an editable path fails with `conflicting
  URLs`, because uv applies the path dependency's own sources. A root `[tool.uv]
  override-dependencies` entry for every FLEXT member, together with the root's
  editable path sources, resolves it: the root lock records the overrides, and the
  excluded member still locks its own `uv.lock` pinned by SHA. The generator derives
  both lists from `.gitmodules` (no hand-kept list). Evidence: fixture
  `~/tmp/flext-1engx/agent11/v2`.
- Rejected alternative: isolated per-member copies, which is the retired synthetic
  resolver machinery.

**One `make upg` pass.** Native resolution processes members in `.gitmodules` order,
then the root. uv runs `lock --upgrade`, which implies `--refresh` and costs about
one second per project.

The Mise half follows design D1 (operator approval 2026-10-31), native and before
any flext-infra import, in the generated template (flext-infra
`docs/guides/execution-context.md`, generated `make upg`):

1. acquire the pinned Mise;
2. classify `uv.lock` and every governed `mise.lock` with the acquired Mise's own
   TOML reader (`mise fmt --stdin`, which reads no lock), deleting an invalid lock
   so its native writer regenerates it;
3. per governed repository, one `mise lock --bump --dry-run --json` whose output
   must be exactly `[]`; otherwise each declared tool previews alone and
   `mise lock --bump <changed tools>` locks only those;
4. the locked `mise install`.

The only flext-infra step left, `deps repair-mise-platforms` (locked tools missing
a declared platform, which Mise does not report), runs last from an isolated
executor environment synced from the frozen lock.

The 60-second gap is closed by measurement (scratch dc-recon, mise 2026.10.3,
uv 0.13.4, 2026-10-31):

- no-change `make upg`: 18–26 s in total, of which the whole-lock `[]` gate takes
  0.06 s warm or 4 s cold;
- one changed tool: only that tool is relocked (about 7 s for four platforms);
- a full relock costs 44–55 s, so it runs only when a lock is invalid or absent:
  a corrupt root `mise.lock` is regenerated in a 63 s `make upg`.

Concurrent per-member relocks are not needed.

**CI.** Root CI checks out submodules at their gitlinks and runs `uv sync --frozen`
and `mise install --locked`. Member CI runs on the member's own frozen locks.
`make check` gains `uv lock --check` per project.

**Evidence the design relies on** (external contracts, to be re-verified against the
pinned tool versions before implementation):

- Mise documentation on lockfiles and monorepo configuration roots;
- uv workspace documentation: one workspace has a single lockfile, and `exclude`
  removes a member from it;
- `uv lock --upgrade` implies `--refresh`;
- `uv.lock` records Git sources with `?rev=<sha>`, which is the exact-SHA pin.

## Superseded statements

The following statements are superseded by this ADR and point here:

- ADR-003, verification contract: "The workspace root lock is the only lock of a
  member … members track no `uv.lock`" and "A member checked out without its
  workspace fails setup loudly".
- Root `AGENTS.md`, Build & Test: "one native root uv workspace and lock" in the
  `flext-0029c` target paragraph.
- `.agents/skills/flext-law/SKILL.md`: "one root uv workspace and lock".
- `flext-infra/AGENTS.md`, Commands: "one native root uv workspace and lock".
- `flext-infra/docs/guides/execution-context.md`, Dependency locks: "The workspace
  root lock is the only lock of a workspace member … a member tracks no `uv.lock`".

ADR-003 §2 (`[tool.uv.workspace] members` and `workspace = true` sources derived
from `.gitmodules`) stays the running contract for now. The proposed design above
replaces it with members excluded from the uv workspace and bound as editable path
sources plus derived root overrides; that replacement takes effect only when the
design lands, and ADR-003 §2 is then marked superseded in the same change.

## Current state

As of this ADR (2026-10-25):

- Git-state admission guards are not part of the target contract. The
  [proposed composition design](#proposed-design-implementation-pending) retains
  its native-resolution verification and real-bump budget.
- The composition mechanism (members first, then the root, in one `make upg` pass)
  is part of the same pending design, as is the 60-second budget on a real bump.
- Member locks that were already removed are restored by `make upg`, never by hand.

## Consequences

- A member, a standalone checkout and a pip-installed consumer each reproduce the
  same exact dependency hierarchy, because every lock pins by SHA and every writer
  is `make upg`.
- `make upg` refuses to run over uncommitted work; agents commit first, then upgrade.
- Remote CI stays reproducible: every pinned SHA exists on the remote.
