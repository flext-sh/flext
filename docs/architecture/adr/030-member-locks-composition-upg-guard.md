# ADR-030 — Member Locks, Workspace Lock Composition, and the Upgrade Guard

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

- **Status:** ACCEPTED — operator ruling 2026-10-25 (verbatim below); the upgrade
  guard implementation is pending (see [Current state](#current-state))
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

Earlier on 2026-10-25 the workspace adopted "only the root lock": members tracked no
`uv.lock`, and a member checked out without its workspace failed setup. The operator
then ruled, verbatim (tracker memory
`operator-ruling-2026-10-25-member-locks-uv-mise-upg-guard`):

> "vale para uv e para mise, somente make upg faz atualização de locks, para os
> pacotes python só o uv que necessita de trava e commit completo de código da
> workspace e subprojetos (somente quando for workspace com .venv editavel, em caso
> de pip instalado en eduatbke o uv.lock se adequa ao que está ligado a ele e
> projetos flext em modo standalone se liga assim), em casos de projetos standalone
> sendo testado com .venv editavel externa o projeto externo precisa estar
> commitado sem dirty e o projeto standalone que usa eles também gravado com
> gitlinks atualizados em commit para uv fazer isso, veja como fazer isso da melhor
> forma possível e garantir a hieraraquia de depencencias exatas pelo sha"

and, answering the lock question directly (tracker memory
`operator-rulings-2026-10-25-libnames-locks-ldif-rope`, answer 2):

> "os locks dos membros tem que ser mantidos, mas tem que ser formados por eles, e o
> da workspace com a composição dos deles, é importante fazer uma trava para make
> upg só com rode repositórios limpos em casa .venv editável e com os gitlinks
> ajustados, sem isso não vamos ter como manter a consistencias e testes no ci
> remoto, analise para fazer isso funcionar e a melhor forma"

The planned removal of member `uv.lock` files is cancelled.

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
5. **`make upg` is guarded** (next section). A lock written over uncommitted code or
   stale gitlinks pins a SHA that the remote cannot reproduce, which breaks remote CI
   consistency; the guard makes that impossible.

## Lock formation and composition

| Context | Who forms the lock | What the lock binds |
| --- | --- | --- |
| Member inside the workspace | the member, from its own declarations | its declared internal Git requirements, pinned by exact SHA |
| Workspace root | the root, composing the member locks | every member at the committed gitlink SHA plus the composed third-party resolution |
| Standalone FLEXT checkout | the checkout itself | the internal requirements it declares, pinned by exact SHA |
| Installed as a package (pip, non-editable) | not applicable | the consumer's `uv.lock` follows what it is bound to |
| Standalone with an external editable `.venv` | the standalone consumer | the external project's committed SHA, recorded through the consumer's committed gitlinks |

Remote CI installs the committed locks frozen and never relocks (tracker memory
`operator-ruling-2026-10-24-ci-frozen-homologated-locks`). Member CI therefore
installs from the member's own committed lock, and workspace CI from the composed
workspace lock.

## The upgrade guard

The guard applies to uv only and runs in the `make upg` preflight, before any lock
is written; the first defect fails loud:

1. **Editable workspace** (`.venv` with editable members): every governed
   repository is clean — the workspace and every subproject have their code fully
   committed — and each committed gitlink in the superproject equals that member's
   HEAD.
2. **Standalone with an external editable install**: the external checkout is clean,
   its HEAD is reachable from its integration branch, and the consumer's committed
   gitlink or locked SHA equals that HEAD.
3. **Non-editable install**: no guard condition applies; the lock follows the bound
   distribution.

The guard reads Git state only. It never commits, stashes, resets or repairs on the
operator's behalf; a violation is a RED result naming the dirty path or the stale
gitlink, and the operator or agent commits and reruns `make upg`.

The guard is scoped to `make upg` only. It is the explicit operator exception to the
root `AGENTS.md` Shared Worktree Contract, which otherwise prohibits a clean tree as
a prerequisite: lock writing pins SHAs that remote CI must reproduce, so only this
verb requires committed state. No other verb inherits the requirement.

**One-time Rope exception, 2026-10-28.** The operator answered "Autorizar
exceção pontual para Rope" to the explicit request to update only the Rope pin
and corresponding locks through `make upg`, then activate through `make setup`,
with the current WIP preserved and every gate retained. Tracker memory
`operator-exception-2026-10-28-rope-only-upg-wip` records the question and answer.
This exception covers the causal native-SDK cutover only. It changes neither
the permanent guard nor other dependency resolutions, permits no site-packages
patch, and does not establish SDK qualification or installation evidence.

Selected source updates cover runtime, optional and development declarations
through the existing requirement-group traversal. They change only the selected
direct-reference URL; extras, markers, native inclusion tables, array positions
and comments retain their owners. Distinct conditional overrides remain native
UV policy: conflicting source URLs cannot be collapsed into one project
requirement and must fail before publication.

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

**One `make upg` pass.** The guard runs first, then members in `.gitmodules` order,
then the root. uv runs `lock --upgrade`; Mise locks only the tools whose version
changes. `uv lock --upgrade` implies `--refresh` and costs about one second per
project. Open gap: the 60-second verb budget on a real version bump. The proposed
answer is concurrent per-member relocks with a bounded job count through the
existing process owner, within the authenticated GitHub quota (5000 requests per
hour); a real concurrent bump has not been measured yet.

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

- The upgrade guard is **not implemented**. The
  [proposed design](#proposed-design-implementation-pending) is agent 11's; V1 and V2
  are settled on fixtures, the 60-second budget on a real bump is not yet measured,
  and until the design lands the guard is the target contract, not running
  behavior.
- The composition mechanism (members first, then the root, in one `make upg` pass)
  is part of the same pending design, as is the 60-second budget on a real bump.
- Member locks that were already removed are restored by `make upg`, never by hand.

## Consequences

- A member, a standalone checkout and a pip-installed consumer each reproduce the
  same exact dependency hierarchy, because every lock pins by SHA and every writer
  is `make upg`.
- `make upg` refuses to run over uncommitted work; agents commit first, then upgrade.
- Remote CI stays reproducible: every pinned SHA exists on the remote.
