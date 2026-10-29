# FLEXT session router

Compose these exact authorities in order:

1. `~/.agents/AGENTS.md`
2. `~/.agents/skills/project-wide/shell/make-check/SKILL.md`
3. `.agents/skills/flext-context-routing/SKILL.md`
4. `.agents/skills/flext-law/SKILL.md`
5. `~/.agents/skills/agent-wide/verification/verification-loop/SKILL.md` at each
   completion boundary

The three global skills own generic execution governance. FLEXT owns the local
`flext-law` domain delta. AI Hub may distribute these surfaces but may not redefine
either owner. Fail closed when an exact path is missing; never resolve an identically
named skill from another catalog or branch.

Before source repair or reorganization, reconcile the active approved plan and the
affected documentation, tracker, skill, rule and command owners through root
`AGENTS.md` "Documentation first" and
`~/agents/rules/architecture/engineering-core.md`. Complete their owner updates
before implementation; consultation alone does not align a stale execution plan.
Apply the operator's specification-preservation requirement in root `AGENTS.md`:
present evidence and impacts and obtain an explicit operator decision before any
simplification, reduction or deviation. For `gen`/`mod`, ADR-018 owns the approved
small coherent transaction contract: the common barrier covers cooperating
Make/Rope readers and writers, interrupted publication blocks readers, rollback
touches only authenticated effects of that transaction, and native refresh is
incremental. The active Bead records implementation and verification separately.
Source validation, generated publication and installed consumption remain separate
receipts under the existing verification owner.

For Pydantic, configuration, settings or facade composition, first read
[ADR-005's domain boundaries](../../docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md#domain-boundaries-and-value-flow-amended-2026-10-28)
and the [Pydantic guide](../../docs/guides/using-pydantic.md).
Distinguish a value's source, its data contract and its class composition.
Use ADR-028 Decision 14 for the latest enum and schema policy, not a superseded
plan or cached skill value. Models, protocol projection and service DI retain
their separate owners; update source, generated output and installed activation
with distinct receipts.

For source-derived model/service protocols, compose
[ADR-018](../../docs/architecture/adr/018-generator-declarations.md#model-and-service-protocol-projection)
and the
[Pydantic consumer guide](../../docs/guides/using-pydantic.md#source-derived-protocol-contracts).
Its current protocol amendment owns projection shape, all-Python consumer scope,
native Rope migration and pilot-before-rollout proof. Cover every pilot variation,
then complete that same pattern's fleet declarations and consumer rewires, real
runtime, native gates and integration closure before beginning another pattern.
The older protocol/stub
plan's supersession notice distinguishes this authorized first-party generation
from the retained SDK and local-stub prohibition. Preserve the MRO/environment
plan's acceptance while following the operator's protocol-first sequence; the
active Bead records receipts and does not redefine the architecture.

For structural cleanup, also compose the canonical global `search-first`, `yagni`,
`ssot`, `solid`, `simplify`, and `dry` skills in that order. Execute rewires through
root `make mod`; native Rope owns Python hierarchy, bindings, references and
refactorings under ADR-028 Decision 17. Declarative rules retain their declared
owner; they do not authorize FLEXT-authored AST, LibCST or textual Python analyzers.
Public ai-hub commands, hooks, MCP routes, and `ai-hub-*` daemons may
enrich that discovery when available, but FLEXT never imports ai-hub or CRG libraries
and their absence is not an error. Git stays owned by `flext-infra`; GitHub and CRG stay
owned by ai-hub. Per-symbol mapping registries and repetitive manual call-site edits are
not execution inputs.
