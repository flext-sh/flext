# Make consolidation — restart handoff, 2026-10-30

This is a dated execution snapshot requested by the operator. It is not a new
plan, tracker, architectural decision or qualification receipt. Current work and
evidence belong to Bead **`flext-9t6gn`**. Read its latest comments before acting;
other authorized sessions may have advanced the shared checkout after this capture.

## Intent and restart boundary

Continue the approved consolidation of Make, templates, generation and semantic
refactoring. Restore the real `setup`, `gen` and `mod` paths, preserve functionality,
reduce custom code, and complete all consumers and generated projections.
Do not start another campaign or replace the existing executor, DSL, publisher,
catalog, operational inventory, cache or journal.

The current blocking boundary is **before the Infra CLI**: a generated lazy map
points to `flext_infra._protocols.runtime`, while the source declaration remains in
`_protocols/rope_runtime.py`. The last attempted `mod` exited with code 2 before
planning. A timeout or a different error on an earlier run did not qualify the
generator, refactoring engine, SDK or fleet.

The operator selected this repair contract explicitly:

> Manter a proibição: desacoplar os inputs do mesmo gerador dos agregadores
> gerados, sem criar outro gerador.

The owning decision is [ADR-018's projector bootstrap dependency cut][bootstrap].
It preserves [ADR-028 Decision 10][imports]. Do not hand-edit initializers,
restore an obsolete module, introduce a compatibility alias, add a direct-module
import exception, or invoke a second cold generator.

## Approved scope and sequence

The five approved batches remain open:

| Batch | Intended result | Current qualification |
| --- | --- | --- |
| Stabilization and editable setup | Real Make paths and authenticated physical environments | Blocked by bootstrap; source repairs exist |
| Existing automation pilot | AI Hub `require_prepared` transfer to `u.Cli.verify_guarded_directory_chain` | Full consumer cutover and runtime unproved |
| Native Rope completion | Remove Infra AST/LibCST, duplicate analyses and fallbacks | Native and legacy paths still coexist |
| Semantic standardization | Names, domains, nesting, imports and model/protocol contracts | Automation repairs and source moves remain unqualified |
| Templates and consumers | One declared owner per output and full scenario matrix | Full generation and propagation unproved |

The AI Hub ownership-transfer pilot was explicitly approved in the resumed plan.
It precedes that plan's earlier peripheral rollout. Preserve the additional
DBT-LDIF, TAP-LDIF and TARGET-LDIF coverage; an attempted DBT command stopped before
Make and did not qualify a pilot.

The full matrix remains root FLEXT plus its declared members; a member Makefile
selected from the root; independent clones; `CI=Y` selecting only its target even
with absent members; a hosted runner; explicit scaffold including Python automation
for a non-Python project; generated and mixed files; interruptions and `clean`;
and the physical workspaces `~/devops-oud-iac`, `~/ai-hub`, `~/cosmos-main`,
`~/cosmos-docgen` and `~/invest`. Reconfirm membership from `.gitmodules` and
preserve unmanaged gitlinks, authored deltas and project-owned operations.

## Contracts that must not be rediscovered or weakened

- Consult and reconcile documentation, ADRs, rules, skills and Beads before code.
  Runtime precedes test changes. Fixtures belong in `tests/fixtures`; no mocks,
  source-inspection assertions, tautologies or frozen configuration expectations.
- Preserve shared WIP through fix-forward and adoption. No reset, destructive
  rollback, clean-tree requirement or unverified authorship attribution.
- Common verbs are `setup`, `upg`, `gen`, `mod`, `fix`, `fmt`, `check`, `tests`,
  `tests-full`, `help`, `build` and `clean`. Product operations remain owned by
  their products. `gen` and `mod` share capabilities, not recursive public calls.
- `tests` uses persistent incremental Testmon. `tests-full` runs the full applicable
  population once without Testmon or an incremental pre-pass, preserving its DB.
- Expected failures follow typed branches and `FlextResult`. Native failures retain
  cause, traceback, metadata and affected scope at the actual boundary. Block unsafe
  dependents, preserve independent successes, and finish nonzero if errors remain.
  Cancellation must not become an ordinary success or operational failure.
- Pass validated objects by reference. Reuse defaults, composed `m` models and `p`
  protocols. Do not replace transport with `model_copy`, dumps/revalidation, casts
  or narrowing wrappers. Preserve immutable snapshots where they protect evidence.
- Keep `use_enum_values=False`, existing strictness and required default validation.
  Python values/dumps retain enums; JSON serialization occurs at its real boundary.
- Lint/type rule selections, severities, scopes and interpreter bindings are frozen.
  Repair source or resolution; do not suppress findings or alter policy for green.
- Lazy dispatch belongs only to generated `__init__.py`. Consumers use static public
  namespace imports; no function-local, deferred or ad-hoc dynamic import repair.
- Names follow native identity and semantic ownership: no `_parts`, numeric fragments,
  duplicate directory prefixes or invented collision suffixes. Align classes,
  subclasses, models, protocols, modules and domains, with nested `c/t/p/m/u` and
  MRO facades at directory boundaries. Preserve the `services` boundary exception.
- Existing templates define refactored module structure as well as new modules.
  Rope supplies authenticated inventory, preserved bodies and references to the same
  renderer and publisher. No parallel string renderer or copying bodies to callers.
- The campaign deadline remains 60 seconds per Make invocation. Use native cProfile
  to locate the cause; do not increase the deadline, narrow the population to claim
  a speedup, or automatically retry unchanged inputs. The Bead's small-transaction
  and loading targets remain requirements, not performance already demonstrated.
- Only `upg` writes locks and has the specific editable-source/gitlink guard in
  ADR-030. The earlier Rope-only exception is not a blanket guard waiver.

## Immediate blockers and exact source state

### Bootstrap and naming corruption

Source inspection found `scripts/normalize_module_names.py` in Infra using per-file
`git mv` and global `str.replace` over dotted variants derived from
`old.parents[1]`. A bare `rope_runtime` variant can affect an unrelated protocol
namespace and initializer string. This is not the native semantic migration path.
Do not infer who executed it. Preserve valid moves and close consumers and lazy
projections in the native candidate; absorb necessary capability into the existing
`semantic_apply._module_naming_candidates` owner before retiring the parallel route.

The `.8` bootstrap owner reported these source-only stages saved:

- CLI dispatch uses the original process-exit input without the aggregate model.
- Original `RopeModuleFinder`, `RopeSourceAccess` and `RopeProject` protocols moved
  to the existing WorkspaceSnapshot owner; Runtime inherits through package exports.
- Lazy-init inputs use upstream basic models/types and native SDK identities.
- Original FilePlan moved to CodegenTransaction, with Artifact MRO updated;
  original inventory/layout/run inputs moved to CodegenLazyInit with Rope MRO;
  lazy root-render inputs moved to LazyInit while preserving the main skeleton.

This did **not** restore the CLI at handoff. Remaining source closure includes
planner/render leaf inputs, configuration passed by reference, entry profiling and
route/API aggregate dependencies. MRO/forward-reference review remains open.
Do not apply an isolated `TYPE_CHECKING` edit: PEP 695 aliases and Pydantic can
evaluate those names at runtime. The first two application aliases were not the
whole census; the typing module also contained roughly thirty SDK aliases.

### Newly verified candidate-to-disk fallback

At capture, Infra HEAD was
`2372e5e51722935c50ab1f128929adeab336e201`; the branch was ahead of its remote.
Source inspection, not merely the commit subject, confirmed that
`_utilities/_rope/native_project.py` catches `ModuleSyntaxError` in `get_pymodule`
and `get_module`, reads physical disk outside the candidate, and constructs a
string module. The staged delta additionally stores that physical parse in the
native module cache. This violates the candidate/source and no-fallback contract.
It is an open critical repair, **not accepted stabilization**. Preserve unrelated
changes and fix the candidate's actual invalid source at its owner; do not admit
the physical fallback or blame the SDK for the consumer's invalid candidate.

Before this handoff was finalized, `.8` reported a bounded source repair removing
those two fallback branches and their unused imports, preserving native delegation.
Independent review was still active and no Make had exercised that repair. Re-read
the live hunk and its review; do not reset to the captured HEAD or mistake the
source removal for qualified candidate integrity.

### Native operations and remaining legacy paths

`CLASS_NESTING` still reached `nesting_cst.py` from the semantic cutover, and
ownership admission still contained Infra-authored AST parsing before matching.
The native-cutover owner is repairing those existing paths. Do not claim that
renaming their entrypoints completed the AST/LibCST removal.

The existing `ownership_transfer` rule rewrites consumers and retires an old
declaration only after authenticating a compatible **existing** destination.
It does not move a method body. Root1 is extending the existing SDK MoveMethod
owner for a coherent static/class-method batch. Its first implementation still
had review findings involving shadowing, receiver identity, imports, private
mangling and implicit slots. Do not adopt it before the next review/runtime.

AI Hub requested the path/read pair from
`ai_hub.services._deploy.receipts.AiHubDeployReceipts` to
`ai_hub.adapters.deployment_receipt.AiHubDeploymentReceiptAdapter.path/read`.
The destination may be seeded only inside the same unpublished native candidate.
Do not publish a stub or copy the reader into callers. `DeploymentReceipt` and
`RuntimeDeploymentReceipt` are different contracts despite similar filenames.

## Source repairs adopted, not globally qualified

| Owner | Source change | Limit of current evidence |
| --- | --- | --- |
| Protocol projection | Native attribute bindings reused; aliases canonicalized; ambiguity/collision return Result; failure precedes retirement | Independent source review approved; new public Result caller test still awaits real runtime |
| Workspace detector | Reuse admitted distribution and verify original local snapshots instead of reparsing root metadata | Source reviewed; no measured total speedup |
| Make documentation | Existing guide matrix/test section derives from the typed Make catalog and one existing-template-family renderer | Full generation/convergence unproved |
| DocScope | Removed tuple-of-FieldInfo default defect | Source repair; full generator unproved |
| Mise activation | `.envrc.j2` adds command-local `MISE_LOCKED=1` to `mise env` | Generated activation and cold behavior unproved |
| Setup | Frozen install followed by declared bootstrap requirements and fresh editable selector, with authenticated sources | Consumer physical origins still require proof |
| Gen control | Metadata/bootstrap before Python, same publisher, prepared plans, cohort hooks and native failed-repository IDs | Final blocked-dependent handling and runtime need review |
| Semantic publication | Readset transport and plan composer preserve original inputs, including projection-only effects | Source review; no runtime qualification |
| SDK MRO | One native C3 pass; no DFS approximation/retry; unresolved order not cached | Source review; no full fleet qualification |
| SDK version guards | Proven native import-only runtime-version branch, preserving unknown conditions | Source review; full consumer acceptance open |
| Core Result / MOD | Explicit exception policy and cancellation preservation in existing primitives | Some runtime reached wrappers; operation incomplete |
| Composition predicate | Per-module native query and early negative result at moved `_codemod/project.py` | Source and guide reviewed; post-change replay blocked before CLI |

The protocol source cut touched `protocol_model_sources`, `render`, `_inventory`
and `_inventory_models` in `_utilities/protocol_models.py`, and its single source
consumer `_model_protocol_sources` in `codegen/_conform/existing_plan.py`.
The former Mapping-only test in `test_model_protocol_native_mro.py` was deliberately
not changed before real runtime. Do not mark that test debt complete.

## Native execution evidence

All commands below ran in `/home/marlonsc/flext` unless otherwise stated.
Profiling captures are owner-thread wall timing, not worker CPU, whole-operation
acceptance or automatically comparable populations. `partial=False` does not mean
the command completed successfully.

| Session | Canonical invocation and bound | Actual result |
| --- | --- | --- |
| 67033 | `make help`, direnv, TERM 58 + KILL 2 | Exit 0; exposed stale `tests-full` help text despite corrected catalog |
| 53387 | `make gen FLEXT_INFRA_PROFILE=true`, direnv, INT 48 + KILL 12 | Exit 124; 32 selected; Root lazy 6.690 s, then API lazy; no managed/final publication proof |
| API member attempt | `direnv exec <flext-api> make -C flext-api gen CI=Y` | Exit 1 before Make: member `.envrc` blocked |
| 21712 | `make -f flext-api/Makefile gen CI=Y FLEXT_INFRA_PROFILE=true`, Root direnv, INT 48 + KILL 12 | Exit 124; actual root API, scope self, one repository; managed protocol inventory reached |
| 35308, peer receipt | `make mod`, direnv, TERM 58 + KILL 2 | Exit 124; `requested_utilities` completed without former Generic failure; operation incomplete |
| 28107, peer receipt | `make mod FLEXT_INFRA_PROFILE=true`, direnv, INT 48 + KILL 12 | Exit 124; 41.944 s capture; layout/composition hot path; no full refactor |
| 95987, peer receipt | Same profiled MOD entry | Exit 2 before CLI: missing `_protocols.runtime`; no post-change profile |
| DBT-LDIF, peer receipt | `make gen` from member, TERM 58 + KILL 2 | Exit 1 before Make; direnv blocked and credentials source missing; no pilot publication |

Persistent locators:

- Root gen log: `.reports/make-gen-causal-mro.log`.
- Root profile: `.reports/codegen/gen-cd96f83e116144fab4c528abcba83b34.pstats.txt`.
  Capture PID 4001438; 29.013 s; discovery 13.565 s, member loading 11.181 s.
- API logs: `.reports/make-gen-api-ci-mro.log` and
  `.reports/make-gen-api-selected-ci.log`.
- API profile: `flext-api/.reports/codegen/` followed by
  `gen-2ccc4c481ca24637ad49418329c6acf8.pstats.txt`.
  PID 135361; 44.284 s; model-protocol inventory 38.753 s before its new cut.
- MOD profile: `.reports/refactor/` followed by
  `mod-c5f81ec047e54882acc612425898ab37.pstats.txt`.
- DBT log reported by its owner: `.reports/rewrite-facades-gen-dbt-ldif.log`.

The Root plan collector was configured disabled with no sources when the cited
Root gen ran. Its successful hook was a configured no-op, not extraction or proof
that documentation/Beads automation completed. No full Ruff/Pyrefly/Pyright/Mypy/
Pytest/build/CI/integrated acceptance exists for this campaign.

## Coordination cursor

These chat identifiers locate the actual owners; read their latest state, not
just this snapshot. No Make from this chat remained running at handoff. Peer
cursors reported no active Make at capture; obtain a fresh START/END handoff
before launching a new heavy command.

| Chat / Bead | Responsibility |
| --- | --- |
| `01a169f6-6f88-7290-993a-ce570830902a`, `flext-9t6gn` | Original campaign, independent review, Root/API generation and this handoff |
| `01a18299-c89c-7640-80ec-c72894daa59f`, `flext-vjj1s.8` | Unique bootstrap writer; setup/editable installs; control helper/execute/conform; prefix candidates and CAS composition |
| `01a1827e-4146-7a23-80f7-1463b40c7d6c`, `flext-u9h2i` | Dirty Rope SDK, MRO/version guard/MoveMethod; Core Result/MOD; composition predicate |
| `01a18a11-80aa-7b90-8958-d6788ce6468a` | Facade DSL, existing renderer/templates, native-cutover adapters; plan outcomes/publication and blocked-control consumers |
| `01a1826e-a543-7873-bb13-3454a45b7e53`, `aihub-6sls5.1` | AI Hub application, environment/credentials, hook/JSONC/reader consumers; no competing Infra installer |
| `01a18502-adf4-7b72-8a71-cf98b88afdda`, `aihub-6sls5.2` | Canonical governance, plan collector, existing tracker/receipt transport and projection delivery |

The Main actor also had an active `imports.py` Result producer/consumer cut and
template-render-context changes. Consume their SourceEND before evaluating that
dependency scope. This is not a request for a globally quiet or clean tree.

AI Hub's companion handoff is persisted at
`~/ai-hub/docs/plans/2026-10-30-aihub-stabilization-handoff.md`, with its own ADR
and Bead links. Its latest reported HEAD was
`ebff70b7d032fef5f91f6d7e1a0febc3412a1b38`; this is not an integrated runtime
receipt. Fresh PEP 610 evidence still showed seven FLEXT editables and Rope from
Git revision `becece05`, so eight local origins were not admitted. The declared
AI Hub product verb `maintain-environment` still needs native generation before
use. Environment/credentials, JSONC and installed artifacts retain that handoff's
owners; do not copy its plan or infer deployment from source or SDK tests.

Governance/collector context remains with the QA chat. Its companion handoff is
`~/ai-hub/docs/plans/2026-10-30-aihub-stabilization-handoff.md`. Collector Markdown
normalization was source-only, still had `.unwrap` paths, and its all-Result cut
was incomplete. The MaintainTracker bridge was still proposed, with an `ok(None)`
defect reported in `maintain_todo`. Agents HEAD reported at handoff was
`75a2e28d7afbff0daae8cf33f9c87df9d74ecbcf`; PR 255's last reported remote head
was `d79e37670fb8e05cf0cde48522e1e4418d4215ac`. Older green local receipts do not
qualify those newer sources or integration. These are peer snapshots, not new
checks by this session.

At the initial capture, Root was branch `upload-20261007`, HEAD
`583a883d700b28d997af7dea9aa34803e8eb7a6e`, with shared modifications. Infra was
the same branch and HEAD noted above, with staged source/script changes. Dirty
Rope HEAD was `785c94e6f66105ef17f512d98702947bce340144`; its dirty content,
not that commit alone, was under test. These are discovery snapshots, not SHAs
qualified by the historical runs. Do not reset any checkout to these values.

## Resume procedure and stop condition

1. Read root AGENTS, the [session router][router], the topic ADRs and
   `bd show flext-9t6gn --json` plus its latest comments. Reconcile current source
   and peer fences; retain the existing Bead and original plan.
2. Close the approved bootstrap dependency group and review original-model identity,
   wire/default/validation behavior and cold imports. Repair the verified physical
   fallback at its actual owner before accepting candidate analysis.
3. Re-exercise the original public entry through direnv and Make. After bootstrap,
   Root `gen` must demonstrate the control projections actually published before
   Python analysis; all failures and written effects retain their native receipts.
4. Have the installer owner prove dirty Rope and all declared FLEXT editable origins
   in the physical AI Hub/OUD environments. Do not infer origins from Root setup,
   an old pin or a successful selector subprocess. Do not prepare dc16 yet.
5. Continue the ownership-transfer pilot and semantic naming/refactoring through
   existing typed rules and native Rope. Close bodies, signatures, aliases,
   inheritance, imports, documentation and lazy outputs in the same candidate.
6. Only after real consumer behavior, update the existing tests and run all native
   applicable gates. Prove convergence, reviewed integration and the integrated SHA.
   Retire old plans one at a time after transferring valid decisions and pending
   execution to their correct owners. Do not delete plans in this handoff operation.

Completion means the full approved matrix, all applicable native checks and tests,
consumer runtime, projection convergence and integrated evidence. Source review,
an attempted command, a narrow green result, a timeout, or this handoff is not Done.

[bootstrap]: ../architecture/adr/018-generator-declarations.md#projector-bootstrap-dependency-cut
[imports]: ../architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-10
[router]: ../../.agents/commands/flext-law.md
