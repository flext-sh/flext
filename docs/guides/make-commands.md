# FLEXT Make Commands

<!-- TOC START -->

- [Discover commands](#discover-commands)
- [Canonical workflow](#canonical-workflow)
- [Verb single-pass contract](#verb-single-pass-contract)
- [Markdown quality pipeline](#markdown-quality-pipeline)
- [Test contract](#test-contract)
- [Failure contract](#failure-contract)
- [Scope and generation](#scope-and-generation)
- [Related guides](#related-guides)

<!-- TOC END -->

`make help` at the workspace root is the executable authority for command grammar. This
guide records the invariants that every declared verb must keep.

## Discover commands

```bash
make setup
make help
```

Never infer a target, flag, or selector from historical documentation. When a required
verb is missing or broken, repair the root dispatcher owner and rerun that verb.

## Canonical workflow

Use the standard verbs directly from the workspace root:

```bash
make setup
make gen
make mod
make gen
make gen
make fix
make fmt
make check
make test
make build
```

The consecutive generation passes prove the fixed point after structural rewrites.
`make build` packages the validated candidate; it does not replace runtime verification.
Each verb executes its declared operation directly. No project, file, pattern, action,
phase, fix, or changed-only selector may be attached to a standard verb.

Setup provisions governed gitlinks before creating the runtime environment. Its shared
owner is `flext-infra/src/flext_infra/templates/project/base/submodule_setup_recipe.j2`;
`config.Infra.codegen.make.submodule_timeout_seconds` bounds native provisioning, and
the root credential contract supplies authentication without logging the token.
The recorded gitlink is the parent index entry, not the origin's moving branch tip.
A `.git` marker alone does not prove materialization. Recovery of an unfinished initial
clone must establish checkout identity, absence of a physical index and worktree
content (including ignored files), and initial-clone provenance before provisioning.
An existing empty index can represent intentional staged deletions and is not that
initial state. Established checkouts retain their HEAD, index, files, and local work;
setup verifies their pin ancestry without fetching or rewriting them. Ambiguous state
fails visibly rather than authorizing forced recovery or a larger timeout.

`make help` is the complete live inventory. Additional declared verbs such as `upg`,
`docs`, `audit`, `status`, `waza`, `duplication`, and the release verbs retain their own
single operation and are invoked only when their scope applies.

## Verb single-pass contract

Each mutating verb owns exactly one operation per tool, and `make check` is strictly
read-only — no verb repeats another verb's work across the canonical sequence
`make fix && make fmt && make check`:

| Gate / tool                       | `make check` (read-only)           | `make fmt` (formatters) | `make fix` (one mutation)                  |
| --------------------------------- | ---------------------------------- | ----------------------- | ------------------------------------------ |
| `lint` — ruff                     | read-only `ruff` verdict           | —                       | one `ruff` repair pass                     |
| `format` — ruff                   | — (mutating)                       | `ruff` format pass      | —                                          |
| `markdown` — rumdl                | `rumdl check`                      | —                       | `rumdl check --fix`                        |
| `markdown-format` — rumdl         | `rumdl fmt --check`                | `rumdl fmt`             | —                                          |
| `markdown-code` — ruff (embedded) | format verdict on parseable blocks | —                       | one format pass, clean round-trips spliced |
| `canonical-alias`, `smells`       | read-only scan                     | —                       | declared repair                            |

`make fmt` never runs a lint pass and `make fix` never formats: each operation runs once
per verb, residue found by a mutation is reported there and enforced only by
`make check`, and `make fix`/`make fmt` repeated on a green tree are no-ops.

## Markdown quality pipeline

The markdown standard lives once in `flext-infra/config/tooling.yaml`
(`Infra.tooling.tools.markdown`) and is projected to every repository by `make gen`:

- `rumdl` is the linter (markdownlint-compatible `MD*` rules through the generated
  `.markdownlint.json` / `.markdownlintignore`); syntax findings inside embedded code
  belong to the flext-tests markdown validator, not to a second linter.
- `rumdl fmt` is the formatter and reads the same `.markdownlint.json`:
  `rumdl fmt --check` in `make check`, `rumdl fmt` in `make fmt`. rumdl is locked in
  `uv.lock`; the fleet toolchain has no npm-backed tool (ADR-025).
- `markdown-code` holds parseable embedded Python and doctest examples to the
  ruff-format contract; unparseable documentation fragments are prose and stay with the
  validator. Generated and provider-projected trees (`.agents`, `.claude`, `.gemini`,
  `AGENTS.md`, `target/`, and friends) are excluded by the same SSOT list.

## Test contract

The test-verb law lives in `~/agents/rules/workflow/canonical-commands.md`.
`make test` runs incremental selection against its persistent Testmon database.
`make test-full` is local-only, without Testmon or a time limit, and includes
configured external and CI-excluded markers. Any preceding incremental phase retains
its own receipt and is not the complete-suite result. CI and pre-push use `make test`;
pre-commit runs no tests. External tests keep their declared runtime and authentication
requirements. Repair a conflicting runner at its owner; direct runner commands and
cache-clearing bypasses are prohibited.

Separate receipts preserve each phase's mode, raw result, inventory, execution, and
deselection counts. Warnings are counted per subprocess and globally, including any
explicitly suspended MRO warnings. Only a typed incremental cache hit with database
integrity checks and complete deselection accounting may execute zero tests; it is never
reported as tests passed. The full phase must execute its complete nonempty inventory.

## Failure contract

- The first exception, traceback, and non-zero exit propagate unchanged.
- Warnings, skips, empty output, and missing tools are failures.
- No retry, fallback, suppression, normalization, partial run, or alternate raw tool
  path can replace the canonical verb.

## Scope and generation

`make file-gate FILE=<repository-relative Python file>` validates one literal file
without changing it. The checker resolves its owning project from the declared
workspace topology, using that project's working directory, tool configuration,
imports, and codemod policy. It never validates a member file as the workspace root.
The generated recipe passes separate gate names through the check CLI's comma-separated
`--gates` contract; no raw checker invocation replaces this route.

Each `flext-infra check run` invocation exclusively creates one UUID4 directory under
the typed request's report base. `--reports-dir` selects that base.
Relative bases resolve under `--repository-root`, not
the caller's working directory. All project native artifacts, full raw receipts,
Markdown and SARIF reports stay under that same invocation directory. The CLI prints
the actual report paths. Existing fixed-path reports remain historical files and are
not overwritten; no shared latest writer is published. Consumers of
`u.Infra.check_report_findings` pass the explicit invocation directory printed by
the CLI, never the shared base or an implicitly selected latest run.

The root dispatcher resolves workspace scope from its typed topology. Generated Make
surfaces and documentation are changed at their template or configuration owner, then
regenerated with `make gen`.

An omitted project selection in the workspace checker covers the root and every
declared first-party member. Standalone checkouts cover their own root. Manifest
exclusions remain authoritative, and literal file validation keeps its owning-project
scope.

`make mod` validates the rule fixtures, then invokes the existing Rope census to
normalize constant consumers before the structural fixed-point cycle. The census
derives public `c.*` paths from live facade declarations and inheritance, rewrites
qualified import bindings, and preserves the declaration parts composing `c`.
Config and settings bootstrap owners retain their dedicated default declarations.
Publication requires unchanged source identities; affected projects are checked
through the canonical lint, Pyrefly, and fresh-import gates.

`make gen-footprint` calls the public `flext-infra codegen footprint` diagnostic
for the root and its declared physical members. It reads the typed pending journal
before planning, without acquiring leases, recovering a transaction, or publishing
files. A pending participant outside the declared physical scope fails without
changing its journal or staging. The receipt is a dated preflight, not a completed
generation or fleet-green receipt; generation rechecks the boundary before effects.

The generated local `make audit` invokes the public
`flext-infra workspace verify-lanes --repo-root <checkout>` gate. A workspace
invocation covers its declared members as well as the root. This is detection only:
it does not fetch, prune, merge, stash, delete refs, remove worktrees, or publish
receipts. The coordinator synchronizes integration outside the guard. The guard
compares the explicit live remote integration OID to the available tracking object
and checks that the current lane consumes it.

`FlextInfraGitService.verify_lanes` resolves to the single `FlextInfraGitLanes`
evaluator. Its utility input, `u.Infra.git_lane_facts`, collects native stash OIDs
and local/configured-remote refs only; it neither elects a base nor judges lanes.
Partial native reads retain explicit errors which keep the evaluator red. The
public request is `GitLaneVerificationRequest` and the response is `GitLaneReport`,
including structured violation classes and complete textual findings. Clean linked
worktrees already contained in the same live integration are reported as residue,
never automatically retired. Checked-out refs are not exempted from that proof.

Failures include the full exact refs, stash OIDs, and registered worktrees. A branch
already contained in integration is residue; integration refs and symbolic remote
HEAD are protected. Unknown ownership is inconclusive, never inferred from commit
age or directory mtime. Open PRs and fresh, explicitly owned Bead lanes are allowed.
Inactive owned work requires correlated tracker, ref activity, and worktree evidence;
the activity window comes from the global governance SSOT configured by
`BranchPolicySpec.lane_governance_file`, never a copied threshold. The public
`--governance-file` option selects an explicit coordinator policy. Without valid
policy evidence, ownership/activity is inconclusive rather than assumed safe.
Optional `--evidence-file` selects a typed,
repository-bound coordinator receipt and requires freshness under that same policy.
Provider, tracker, policy, and Git read errors remain failures, not empty inventories.

Live auxiliary reads require explicit `--read-pull-requests` and/or `--read-beads`
selection. Installation never selects a capability. Dormant sources remain typed
unknowns and appear as `NOT EXECUTED` in the inventory; any artifact needing that
missing ownership proof remains inconclusive. Git facts still run independently.
Selected Beads reads consume `BeadsProjectSpec.ownership_command_prefix` and
`ownership_command_cwd` from the repository's `config/beads.yaml`, through the public
city/rig wrapper declared there. An undeclared or failed selected route fails;
the service appends the immutable read-only list protocol. There is no bare `bd`,
alternate database, runtime startup, or retry fallback.
An ownership receipt and live sources cannot be selected together.

A storage-only primary registry row is bound to a checkout only when native Git
proves the caller's Git directory equals shared storage and its top-level agrees
with GitPython's working-tree identity. The raw porcelain remains available as
evidence. An unprovable storage/checkout mapping fails rather than substituting
the request path.

The same Git service rejects stash entries and stale effective bases before a
worktree ADD creates directories or refs. REMOVE proves that the lane tip is an
ancestor of the live integration tip before delegating to the existing clean/index/
untracked preservation boundary. Neither ancestry nor a green inventory grants
retirement authorization. Direct shell/session/sweep enforcement is the separate
governance consumer of this owner, not a second Git hygiene engine.

## Related guides

- [Development](development.md)
- [Testing](testing.md)
- [Getting started](getting-started.md)
