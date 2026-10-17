# FLEXT Make Commands

<!-- TOC START -->

- [Discover commands](#discover-commands)
- [Architecture admission and acceptance](#architecture-admission-and-acceptance)
- [Canonical workflow](#canonical-workflow)
- [Operation ownership](#operation-ownership)
- [Constants migration](#constants-migration)
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

## Architecture admission and acceptance

Command success does not replace architecture acceptance. Start with
[root AGENTS.md](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md), the
[session router](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/commands/flext-law.md), and its exact
[routing](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-context-routing/SKILL.md) and
[FLEXT law](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-law/SKILL.md) owners. The router composes
global `search-first`, `yagni`, `ssot`, `solid`, `simplify` and `dry`; concrete
dependency and data boundaries additionally follow the canonical global
`dep-injection`, `clean-architecture` and `pydantic-development` skills under
`~/.agents/skills/`. Read their procedures, not a copied local substitute.

Before gen/mod/fix-namespace, record the domain owner, declaration family,
namespace, affected consumers and obsolete paths in the active Bead. FLEXT law's
**Architecture and imports** owns facade MRO `c -> t -> p -> m -> u`, inward
dependencies, data-only declarations and explicit `p`-port/`api` composition.
Root **Architecture Overview** owns config/settings as layer-zero SSOT with no
own-namespace imports. Repair declaration and dependency order at their owner;
do not hide a cycle through local imports, eager exports or compatibility aliases.

Reuse an existing helper only at its correct domain boundary. Parse owned input
once through canonical Pydantic models and preserve typed serialization/results.
The **Sources, generation, and commands** section of FLEXT law owns source-only
projection changes and canonical regeneration. Never hand-edit generated member
guides, facades or Makefiles to obtain a green result.

After each bounded repair, prove complete consumer rewiring, removal of the old
route and net-negative simplification of redundant implementation without reduced
functionality. No duplicate engine, fallback, shim, suppression or weakened
configuration is acceptance. Apply global `make-check` and `verification-loop`:
record command, CWD, exit, scope and original receipt; exercise the public runtime,
run applicable lint/type/test/docs gates and prove repeated gen/fix/fmt are no-ops
on the unchanged candidate. Later edits invalidate overlapping evidence. Root-only
checks are not fleet proof; failures and unexecuted gates remain explicit.

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

Under [ADR-025's October 9 amendments](../architecture/adr/025-npm-free-fleet-toolchain.md),
setup provisions current committed locks without resolution or lock writes; audit
judges missing, stale or incomplete locks, and CI runs audit after setup. An absent
Mise self-pin uses the qualified host provisioning path, not an invented release.
Functional installation failures always remain red. `make upg` owns resolution
and lock writes. Distributed JavaScript tools belong to one owned Bun project
with `package.json` and a frozen lock, never a Mise npm backend; native Node
wrappers remain where used. These contracts are not current runtime receipts.

## Operation ownership

Each verb enters its existing domain owner. Generation and conformance share the
same projection planner and transaction publisher; they do not share permission
to repair authored declarations.

| Verb | Owned operation |
| --- | --- |
| `setup` | Install committed locks, synchronize the physical environment and generate declared runtime bindings |
| `gen` | Render and publish projections from the current declarations |
| `upg` | Project current declarations with the frozen producer, then resolve dependencies and write locks |
| `mod` | Apply the declared semantic and structural consumer rewrites |
| `fix` | Apply conformance repairs and the configured fixable gates |
| `fmt` | Run the configured formatters |
| `check` | Run the configured read-only gates and check conformance |
| `test` | Execute behavioral tests with the persistent Testmon database |

The generated dispatcher invokes conformance checking only through `make check`
and conformance repair only through `make fix`. Installing, generating,
upgrading, rewriting or formatting does not implicitly run a global conformance
check. Each operation still proves the prerequisites and effects it actually
consumes. Native environment verification, input authentication and publication
receipt verification remain required; they are not global conformance scans.

General code audits belong exclusively to `make check`. `make test` executes
tests; it does not run the general check gates. Generation reads the declarations,
templates and source exports needed for its projections, including lazy
initializers and facade imports. Its publisher guards the consumed file identities,
destination preimages and journaled effects without traversing the generator's
executable dependency graph. Documentation generation uses the same physical
publication boundary. Facade generation preserves authored declarations and imports
outside the selected family's exported bindings. The namespace rule catalog,
consumed by `make check`, owns their architecture findings.

The read-only conformance observer verifies the completed journal, actual inputs,
effects and requested scope through that same publication owner. It does not
repeat the executable dependency audit owned by the `fresh-import` check gate.

Facades and the planned package initializers required by their imports form one
dependent publication group. Generation reuses those initializer plans rather than
publishing a facade against an older export map. Unrelated managed artifacts remain
outside that group.

Completed receipts retain their original input evidence. The advancing publication
frontier contains outputs: a later phase proves those outputs before consuming them,
and authenticates its own inputs before effects. Read-only inputs from a completed
phase do not become outputs that every subsequent phase must revalidate.

Generation uses the provisioned physical runtime without first activating the
environment file it may regenerate. Verbs that consume activation enter the
declared environment before their handlers. Both routes retain the same physical
workspace and interpreter ownership checks.

Setup in the declared CI context synchronizes the environment without authorizing a
local `.envrc`. Native tool installation and version proof remain mandatory. Backend
executable names belong to the typed toolchain entry and its generated Mise options;
the installer does not repair an incorrect name through shell renames or retries.
CI tool caches match the generated Mise configuration as well as the committed
locks and package metadata. A cache from another declaration is not a restore
candidate. Upgrade projects the Mise configuration and dispatcher before reparsing
the dispatcher to resolve and install its current backend keys; post-generation
hooks run once after the upgraded environment converges.

Runtime bindings are generated outputs. `setup` and `gen` render them from the
declared configuration without migrating authored configuration or retiring its
Git index entries. For tracked editor settings, `fix` owns the existing migration:
preserve the portable configuration in its declaration owner before retiring
tracking and publishing the runtime-local binding. A binding refresh cannot
silently authorize that source migration.

Within the same `make upg` invocation, the existing committed lock first
provisions the frozen producer. That producer projects `pyproject.toml` and its
native resolution views before the resolver upgrades either view. Lock
reconciliation, installation and verification then consume those projections.
A usable committed lock and a producer that supports the current declarations
are prerequisites. This ordering does not promise compatibility with an older
producer or introduce a separate bootstrap command.

## Constants migration

The constants-consumer phase uses Rope identities, class ancestry, occurrence
coordinates and native import plans. Python detection and transformation at this
owner do not use a separate AST, CST or regular-expression parser. Its edits
participate in the existing semantic publication and fixed-point loop.

The census recognizes `typing.Final` by its resolved identity, including aliased
imports and lowercase declaration names. A user-defined type named `Final` does
not establish constant ownership. Parameter positions come from Rope occurrences
in the same immutable module snapshot, including multiline signatures.

Within the declared constants family, a class-level `typing.Final` annotation
becomes `ClassVar` so a composed Pydantic namespace does not create an instance
field. Rope resolves aliases and qualified imports; same-spelled user types,
module bindings and function-local declarations retain their contracts. The
initializer remains unchanged, including `frozenset` expressions that depend on
runtime inputs. Annotation repair does not authorize extracting a calculated
collection or replacing its elements.

Constant imports resolve through their unique reaching declarations and the
published facade's MRO. Local shadowing, import cycles and competing owners reject
the candidate before publication. Consumer tests exercise public tap, target and
dbt providers; their expected values come from the same upstream facades rather
than freezing current configuration.

The same phase can reuse an existing public string or nonnegative decimal
integer constant in a complete function return. Rope proves the literal region,
its exact inferred type and its single assignment owner;
computed expressions, docstrings, defaults and metadata retain their meaning.
An enum member cannot replace a plain string return because its runtime type
differs from `str`.

For singleton `typing.Literal` field annotations, the phase can reuse an
existing public `enum.StrEnum` member with the same wire string. Aliased and
qualified `Literal` imports keep their identity. Defaults and discriminator
metadata remain intact. This rule does not create new enums or rewrite
multi-value Literals or function annotations; those contexts require their own
semantic proof before automatic publication.

Existing singleton `frozenset` constants can replace matching built-in
constructions on the right side of `in` and `not in`. String and decimal integer
elements must be literal declarations. Computed values, mutable inputs and
same-spelled user functions are excluded. Construction and return contexts keep
fresh-object identity; this rule does not extract new collection declarations.

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
  `uv.lock`; the Mise npm backend remains retired (ADR-025). The amended Bun
  project contract for distributed JavaScript tools does not change this formatter.
- `markdown-code` holds parseable embedded Python and doctest examples to the
  ruff-format contract; unparseable documentation fragments are prose and stay with the
  validator. Generated and provider-projected trees (`.agents`, `.claude`, `.gemini`,
  `AGENTS.md`, `target/`, and friends) are excluded by the same SSOT list.

## Test contract

The test-verb law lives in `~/agents/rules/workflow/canonical-commands.md`.
`make test` runs incremental selection against its persistent Testmon database.
An explicitly requested full run also retains the canonical Testmon cache under
[FLEXT law](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-law/SKILL.md#sources-generation-and-commands).
External tests follow the root connectivity prerequisites. Any preceding incremental
phase retains its own receipt and is not the complete-suite result. CI and pre-push use
`make test`; pre-commit runs the CI check partition and incremental tests. External tests keep their declared runtime and authentication
requirements. Repair a conflicting runner at its owner; direct runner commands and
cache-clearing bypasses are prohibited.

Separate receipts preserve each phase's mode, raw result, inventory, execution, and
deselection counts. Warnings are counted per subprocess and globally, including any
explicitly suspended MRO warnings. Only a typed incremental cache hit with database
integrity checks and complete deselection accounting may execute zero tests; it is never
reported as tests passed. The full phase must execute its complete nonempty inventory.
An empty incremental selection remains distinct from an absent selection. Native
Testmon selection and the collection manifest must agree before any test executes;
an empty manifest must never expand into an unselected run of the complete target.

## Failure contract

- The first exception, traceback, and non-zero exit propagate unchanged.
- Warnings, empty output, and missing tools are failures. Connectivity availability
  skips follow [root prerequisite law](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md#production-readiness-and-connectivity-tests)
  and never count as successful connectivity or production validation.
- No retry, fallback, suppression, normalization, partial run, or alternate raw tool
  path can replace the canonical verb.

The recovery contract under implementation also covers a journal-listed
`TEMPORARY` directory intent whose original preimage was absent and whose creation
receipt is still `None`. Reconciliation must remain strictly inside the original
authenticated transaction root. An observed empty directory is a new input to
that reconciliation; it cannot stand in for the missing historical creation
receipt.

Removal requires an exact identity guard and applies only to the proven empty
directory. The original authenticated manifest must agree before and after the
removal. Unknown nonempty content, a different directory or parent identity, or
divergent aliases remain failures and are preserved. Already published independent
effects remain published. Native regression tests and runtime proof for this
recovery case are pending; this contract is not a successful recovery receipt.

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

Root `make check` currently checks only the root project; it is not a fleet-wide
receipt. Run a member's standard verb from the workspace root with
`make -f <member>/Makefile <verb>`, for example:

```bash
make -f flext-meltano/Makefile check
make -f flext-meltano/Makefile test
make -f flext-meltano/Makefile build
```

The source template
`flext-infra/src/flext_infra/templates/project/base/Makefile.j2`, in its derived-paths
and repository-root sections, binds `PROJECT_ROOT` to the selected Makefile's
checkout rather than CWD. Attached members share the containing workspace's runtime
environment. Standalone checkouts and member worktrees without a containing
superproject own their runtime environment and run `make <verb>` from their own
root. Selecting the member Makefile adds no project selector or alternate dispatcher.
Manifest exclusions remain authoritative, and literal file validation keeps its
owning-project scope. Generated Make surfaces and documentation are changed at their
template or configuration owner, then regenerated with `make gen`.

`make project-new` creates the declared project through the shared scaffold service.
Generated settings use `FlextSettings.resolve_env_file` with the project's declared
namespace: an explicit `FLEXT_ENV_FILE` takes precedence over the namespace file and
the consumer's working-directory `.env`. Discovery never depends on the installed
package's location. Settings use the framework's per-class singleton; YAML business
configuration keeps its independent frozen lifecycle. Hosted setup selects the
existing non-editable installation path, so runtime acceptance must also verify that
the generated package is loaded from its own environment.
The generated API supplies the ping service's configuration and settings ports
explicitly. Its service base uses the Core kernel, and separate service instances
retain their injected settings without reading module globals. The CLI binds the
already-composed API alias.

`make mod` validates the rule fixtures and applies declared consumer text cutovers,
then invokes the existing Rope census before the structural fixed-point cycle. The census
derives public `c.*` paths from live facade declarations and inheritance, rewrites
qualified import bindings, and preserves the declaration parts composing `c`.
Config and settings bootstrap owners retain their dedicated default declarations.
Publication requires unchanged source identities; affected projects are checked
through the canonical lint, Pyrefly, and fresh-import gates.
The census classifies constants by their declaration contract before the containing
file's family, so constants in utilities, protocols, models, and services remain
visible as placement violations.

`make gen-footprint` calls the public `flext-infra codegen footprint` diagnostic
for the root and its declared physical members. It reads the typed pending journal
before planning, without acquiring leases, recovering a transaction, or publishing
files. A pending participant outside the declared physical scope fails without
changing its journal or staging. The receipt is a dated preflight, not a completed
generation or fleet-green receipt; generation rechecks the boundary before effects.

`make profile-gen` runs the generation handler under cProfile and retains its
original exit status. `make profile-gen-report` reads that profile. Keep source
inputs unchanged during a capture and record the command's wall time separately
from the profiler's function timings. Workspace planning uses worker processes;
the parent profile records their waits. An individual project's profile runs its
single planning task in the profiling process and exposes that task's call costs.

`make validate-lifecycle` is the workspace-only, serial lifecycle operation. It
discovers governed members from the typed workspace topology and runs the root,
then each member, through `setup`, `gen`, `upg`, `setup`, `gen`, and `gen`. It
does not include external consumers, create PRs, publish commits, switch branches,
or change integration declarations. `upg` retains its dependency-resolution and
lock-verification contract; this operation is not read-only.

Each command runs in its owning checkout, with a typed receipt recording its
command, working directory and exit status. The first failure stops the operation;
unreached commands remain unexecuted, never successful. Attached members share
their physical superproject runtime, so attached validation does not substitute
for standalone consumer proof. Ordinary root verbs remain repository-local and
cannot, by themselves, establish a fleet-wide result.

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
