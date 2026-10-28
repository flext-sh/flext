# FLEXT Engine Law — Rope-Only Python Interpretation

| Workspace declaration | Accepted decision |
| --- | --- |
| This page; the living census and wave status (beads `flext-pipol`, `flext-u9h2i`). | [ADR-028 Decision 17, amendment 2026-10-28](../architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17) |

Operator law, 2026-10-28: **rope is the only accepted Python interpreter in
FLEXT's own code.** The flext-infra engine never parses, analyzes or rewrites
Python source with the `ast` module, `libcst`, or `re` applied to code — every
such site is deprecated and migrates to rope's PyModules from the single
indexed project.

The operator reiterated the complete cutover on 2026-10-28: "vc tem que
exterminar ast e libcst , e todos fallback" (tracker memory
`operator-order-2026-10-28-exterminate-ast-libcst-fallbacks`). Accessing syntax
nodes through Rope is also a superseded route. Use native DSL queries, source
bindings, scopes and refactorings; a missing capability is repaired at its native
owner, never replaced by a second parser or fallback implementation.

Lint-identity authentication consumes that same governed source inventory and
native bindings. It must not recursively scan report trees, interpret source
with AST, infer a settings owner from a class-name suffix, ignore decoding
failures or discard a finding merely because a probe path cannot be read.
Preserve the diagnostic and authenticate only the exact declared contract.

An interrupted source cutover may need the immutable declaration that preceded
its removal. Read it through the existing Git blob owner with an explicit
revision; its default remains `HEAD`. Historical bytes authenticate the analysis
candidate only. Keep the live physical witness and current publication source
separate, and never publish historical providers to make unresolved consumers
appear valid.

## What stays canonical

| Engine | Domain |
| --- | --- |
| Rope | Python analysis and refactoring: one loop and native session/index per repository per invocation, shared by DI; small dependency-closed cohorts use the same publisher within the five-second transaction budget (ADR-028 [Decision 17](../architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17); ADR-018 [transaction contract](../architecture/adr/018-generator-declarations.md#single-read-single-batch-publication-amended-2026-10-28-campaign-flext-pipol)). This does not mean one physical transaction for the whole invocation. Native refactorings first (rename, move, restructure, ImportOrganizer); custom transforms operate on the indexed PyModules through rope's public API. |
| ast-grep | Declarative rules (detection AND fix), one generalized rule per law (ADR-028 [Decision 11](../architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-11), [Decision 18](../architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18)); the rules catalog is SSOT data. |
| sed | Non-Python text. |
| Generator (`make gen`) | Projections from declared templates. |

## Isolation by repository

The engine never resolves a member module through the interpreter: the
interpreter may elect stdlib modules only (`sys.stdlib_module_names` gate in the
rope native project); member code resolves through the repository's own rope
index. A fresh interpreter — where genuinely required — uses
`u.Infra.runtime_python(root)` and the physical environment elected by checkout
topology: the workspace-owned `.venv` for an attached member, or the checkout's
own `.venv` in standalone mode (ADR-003, Decision 5). It never borrows the engine's
ambient environment. Divergent member libraries never leak into engine analysis.

## Deprecation window

Superseded engine routes follow the workspace's deprecated-signature window:
a typed warning marks the route (`compat: <route> -> <new owner>; fix:
<rewire>`), every use is reported as a finding in the consumer (the census),
rewires land in waves through `make mod`, and the route is deleted when the
census reaches zero. Detection without a fix form is a rule defect.

## Correction authority

Violations in member code are corrected by the engine — declarative rule fixes
for mechanical shapes, rope refactorings for semantic ones — through
`make mod`. Manual member edits are the exception of the exception, justified
in the commit.

## Blocked capabilities

A site with no rope-expressible equivalent (for example, runtime-object
semantics: `is`-identity, `__mro__` of live classes, protocol checks) is
reported as `BLOCKED-ON-ROPE-CAPABILITY` with the rope API evaluated, and
stays untouched until the operator rules; an alternative parser is never
silently kept.
