# ADR-038: Reproducible Setup, Runtime Activation and One Gate for Hook and CI

<!-- TOC START -->

- [Status](#status)
- [Operator orders (2026-11-26, translated from Portuguese)](#operator-orders-2026-11-26-translated-from-portuguese)
- [Context (measured 2026-11-26)](#context-measured-2026-11-26)
- [Decision](#decision)
  - [1. make setup installs; make upg updates](#1-make-setup-installs-make-upg-updates)
  - [2. Runtime root and PATH](#2-runtime-root-and-path)
  - [3. mise bootstrap](#3-mise-bootstrap)
  - [4. One uv command](#4-one-uv-command)
  - [5. FLEXT=<path>](#5-flextpath)
  - [6. Sibling identity](#6-sibling-identity)
  - [7. One gate for the hook and CI (amends ADR-037)](#7-one-gate-for-the-hook-and-ci-amends-adr-037)
  - [8. make mod and project extension](#8-make-mod-and-project-extension)
  - [9. The projection does not depend on the checkout](#9-the-projection-does-not-depend-on-the-checkout)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [Open points](#open-points)

<!-- TOC END -->

## Status

Accepted (operator, 2026-11-26). Implementation pending, tracked by
`flext-itpd1.4.17` and its children; this record is the decision, not a claim
that the code, projections or runtime already follow it. Amends ADR-003, ADR-024,
ADR-030 and ADR-037 where stated below; those records carry a pointer here.

Amended 2026-11-26 (decision 9): projections are independent of the checkout.

## Operator orders (2026-11-26, translated from Portuguese)

1. "`make setup` must always install the workspace/worktree and its subprojects
   in editable mode, without these workarounds; fix every workaround, duplicate,
   old, dead or unnecessary thing in this flow."
2. "Local + CI, but in GitHub CI the subprojects are installed non-editable and
   without a git submodules pull to initialize the sub-repositories."
3. "`make setup` leaves the project usable for development, and updates are made
   absolutely only in `make upg`."
4. "`make check` and tests must be reproducible locally and in CI, ALWAYS; that is
   why dependency adjustment must be controlled by `make setup`."
5. "The mise bootstrap must be independent of mise itself; it is the first thing
   `make setup` does when mise is not available in the correct form."
6. "uv must be atomic, fast and one single command in `make setup` to activate the
   whole workspace that has subprojects."
7. "In local projects the PATH must start with `<project>/.bin`, propagated by
   `make setup`, with the venv always activated through `<project>/.venv/bin`;
   direnv is a complement for the shell and for agents."
8. "Inside a workspace (inside flext) a member uses the workspace's runtime;
   cloned independently it creates its own."
9. "`make setup FLEXT=<path>` puts the flext dependencies at that location as
   editable (fast development)."
10. "The former gen, fmt, fix, check (ruff and pyrefly) and tests (optimized
    pytest-testmon) block the pre-commit hook and CI."
11. "`check-full` and `tests-full` run only at my request; `make ci` does not exist
    in flext projects; the pre-commit hook must do the same thing as the GitHub
    CI, including running `make setup` of the workspace."
12. "`make mod` is for global adjustments and standardizations and must be used
    only at the request of the operator and of the plan; projects may declare
    other verbs and pre/post actions of the verbs through `custom.mk`, supported
    by config overrides."

## Context (measured 2026-11-26)

The current state fails the orders in these places.

| Area              | Measured state                                                                                                                                                                                                                                        | Evidence                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| CI install        | `--no-editable` covers the project too; checkout uses `submodules: recursive`                                                                                                                                                                         | `Makefile.j2:680-682`, `codegen.yaml:541`                             |
| Root lock         | members recorded only as editable paths, no SHA                                                                                                                                                                                                       | root `uv.lock:1577`                                                   |
| Member CI         | checks out the superproject at the moving branch and installs the root lock; the member's SHA-pinned lock is never consumed                                                                                                                           | `_fragments/superproject_checkout.j2`, `artifact_render.py:1011-1064` |
| Standalone member | `make setup` aborts; no `setup`/`upg` target is emitted                                                                                                                                                                                               | `Makefile.j2:322-331, 794-822`                                        |
| Setup installers  | two installers run outside the lock after the sync                                                                                                                                                                                                    | `Makefile.j2:494-500`, `workspace/flext_editable.py:165-214`          |
| mise bootstrap    | mise is managed as a mise tool; the host binary is a symlink into that tool; acquisition and trust run twice                                                                                                                                          | `tool_bootstrap_recipe.j2:9-28, 120-163`, `Makefile.j2:798-805`       |
| Activation        | every verb is wrapped in `direnv exec`; mise documents mise + direnv together as unsupported                                                                                                                                                          | `Makefile.j2:758, 850`, mise.jdx.dev/direnv.html                      |
| Gate              | `CHECK_PHASE ?= primary` is assigned after admission reads it; primary is `lint` + `pyrefly` only; convergence never runs by default and the complete-phase rule ends in a bare `&&`; hook and CI never verify projections and the hook runs no tests | `Makefile.j2:66, 176, 1028`, `codegen.yaml:701`                       |
| Sibling identity  | no gate proves local sibling HEAD = gitlink = locked SHA outside a CI-only PUSH-stage gate                                                                                                                                                            | `environment_provenance.py:699-845`                                   |

Tool facts measured in a scratch tree (uv 0.12.19, mise 2026.11.14):

- One `uv.lock` holds both forms of a sibling when its two sources (path +
  editable; git at a commit) are selected by conflicting PEP 735 dependency
  groups. With all 31 members: `uv lock` 4.5 s warm; the development sync installs
  32 editable; the CI sync, with the sibling trees absent, installs 31 from git at
  the locked commit and the project editable.
- The same switch through extras leaks `Provides-Extra` into built metadata;
  dependency groups never enter built metadata (PEP 735).
- A bare-name `override-dependencies` entry does not see group-selected sources
  and falls back to the package index (a probe locked an unrelated PyPI package).
  A per-package `exclude-dependencies` entry works.
- `--no-sources` conflicts with `--frozen`; `--locked` and `uv lock --check` need
  the sibling trees; `--all-groups` fails when groups conflict.
- An editable overlay installed after the sync is reverted by any project-aware
  `uv sync --frozen` or `uv run --frozen`.
- `mise install` and `mise exec` without lock mode rewrite `mise.lock`; mise
  2026.10.3 rewrites a version 4 lock as version 3.
- `mise generate install-script --version <v>` emits a script carrying the version
  and per-platform checksums; a member directory inherits the root `.mise.toml`
  through the directory hierarchy.

## Decision

### 1. `make setup` installs; `make upg` updates

Nothing reachable from `setup` resolves, upgrades or rewrites a lock, a tool pin,
the mise version or a submodule commit. `setup` consumes only the committed
`uv.lock` and `mise.lock`. Every write belongs to `make upg`.

### 2. Runtime root and PATH

- A checkout inside a workspace uses the workspace's runtime; a checkout cloned
  independently owns its runtime.
- The runtime is `<runtime root>/.bin` and `<runtime root>/.venv`. PATH starts with
  `<runtime root>/.bin`, then `<runtime root>/.venv/bin`.
- `make setup` populates `.bin`. Make builds this PATH itself, the same way locally
  and in CI.
- The generated `.envrc` exports the same PATH for interactive shells and agents.
  It is a complement: no Make verb depends on direnv, and it does not evaluate
  mise.

### 3. mise bootstrap

- The first step of `setup` checks `<runtime root>/.bin/mise --version` against the
  pin. When it differs or the file is absent, the committed install script places
  that exact release there.
- The pin lives in `codegen.yaml` (`toolchain.mise_version`); only `make upg`
  regenerates the install script.
- mise is not a mise tool. Lock mode is on for every setup-reachable mise call.

### 4. One uv command

- Each sibling subproject has two sources selected by the conflicting dependency
  groups `local` (path, editable) and `remote` (git at the recorded commit).
- Development: one `uv sync --frozen` selecting `local`. GitHub CI: the same
  command selecting `remote`, with no submodule checkout.
- FLEXT requirements of a superproject root live only in those two groups. Bare
  internal overrides are replaced by per-package exclusions.
- A project with no sibling subprojects runs the same single command without the
  group switch; its FLEXT dependencies come from the commits in its lock.
- `make upg` writes the `remote` commit of each member from its gitlink.

### 5. `FLEXT=<path>`

`make setup FLEXT=<path>` binds the FLEXT dependencies found at `<path>` as
editable for fast development. It is local only and refused in CI. The
environment is then not the locked one; `make check` reports that state instead
of presenting it as reproducible.

### 6. Sibling identity

A gate in `setup` and in `check`, in both contexts, proves for every internal
distribution that the locked commit equals the gitlink and the local sibling
HEAD. Member CI checks out the member alone and installs the member's own lock.

### 7. One gate for the hook and CI (amends ADR-037)

- The pre-commit hook and the GitHub CI run the same rows from one workflow
  declaration: `make setup`, `make check`, `make tests`.
- Both block on generation, format, fix, `ruff`, `pyrefly` and the incremental
  tests.
- Locally `make check` converges generation → fix → format to a fixed point that
  includes member checkouts, then verifies. In CI it only verifies and fails when
  a byte would change.
- The default phase is assigned before admission reads it.
- `check-full` and `tests-full` run only at the operator's request. There is no
  `make ci`.
- The incremental test selection key includes the sibling commits and the lock
  hashes.

### 8. `make mod` and project extension

- `make mod` applies global adjustments and standardizations. It runs only when
  the operator or the approved plan asks for it; it is not part of the setup,
  check or tests cycle, of the pre-commit hook or of CI.
- A project declares its own additional verbs and the pre/post actions of the
  common verbs in its `custom.mk`, with its values coming from the project's
  config overrides. The generated Makefile stays a projection and is never
  edited for a project need.
- A pre/post action is a project need. It never repairs a generator defect and
  never re-installs, re-binds or re-resolves what `setup` owns.

### 9. The projection does not depend on the checkout

Operator order (2026-11-26, translated from Portuguese): "both; do not simplify
the rules I already gave", answering which profile the flext-infra projections
take.

- A repository's committed projections are a function of its own declarations
  and the generator's version only. Generating from the rig, a linked worktree,
  a standalone clone or CI yields the same bytes.
- Two facts are kept apart:
  - **Repository role:** whether the repository governs members (its own
    `.gitmodules` declares governed members). It is read from the repository and
    selects the workspace-governance entries.
  - **Execution mode:** whether a checkout runs as an attached member or
    standalone (decision 2). Make decides it at execution from the containing
    checkout. It never selects what is generated.
- A repository without governed members that can run attached to a workspace
  receives the entries both execution modes need. Neither mode's rule is
  dropped.
- A catalog entry whose content differs between the two modes renders both
  branches. Make selects one at execution; the projection never changes with
  the checkout.
- Proof: `make check` run twice in two different checkouts of the same revision
  (the rig member and a linked worktree) changes no byte, and the projection is
  identical in both.

## Consequences

- Deleted: selecting the profile by the checkout in which generation runs
  (`detector.py:384-390` as a projection input). The catalog's `profiles` key
  selects by repository role; execution mode moves to the Make runtime.
- Deleted: the mise self-tool flow, the duplicate acquisition and trust, the
  `direnv exec` activation, the `native_isolation` branches, the superproject
  checkout in member CI, the root's bare member overrides, the post-sync
  installers for a workspace's own members.
- A standalone member declares `flext-infra` and `flext-tests` in its own groups
  so its `setup` and `upg` exist.
- Consumer hooks that re-bind the project editable (ai-hub) and that publish
  direnv or trust mise (cosmos-main) are removed by their owners.
- `uv lock --check` runs only where sibling trees exist (development, `upg`).

## Verification contract

Each claim is proven at the real entry point before closure: `make setup` twice
with unchanged lock checksums; the development and CI installs read through
`direct_url.json` (`dir_info.editable` or `vcs_info.commit_id`); a second
`make check` changing no byte; the hook and the CI run producing the same verdict
on the same commit; the six operating cases (workspace root, attached member,
standalone `flext-cli`, ai-hub, datacosmos, cosmos-main).

## Open points

- Cold-cache lock time and the cosmos-main `apps/` layout are not yet measured.
- Whether a tool directory restored from a CI cache is re-verified against the
  lock is unverified.
