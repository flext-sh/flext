# Migrate tests, scripts and examples to current public contracts

<!-- TOC START -->

- [Assignment contract](#assignment-contract)
- [Exclusive ownership](#exclusive-ownership)
- [Sources to inspect](#sources-to-inspect)
- [Required correction](#required-correction)
- [Acceptance evidence](#acceptance-evidence)

<!-- TOC END -->

## Assignment contract

Work in $HOME/flext on upload-20261007, as explicitly requested by the operator. First
verify the live branch, current WIP, nearest AGENTS.md, .agents/commands/flext-law.md and
branch-matched skills. Preserve and adopt all existing changes; never reset, rebase,
force-push, overwrite unknown work, or restore a historical tree. Historical results
below are diagnosis leads, not current acceptance evidence.

The operator requires tests, scripts and examples to consume current public source
interfaces and the strictest origin-owned types. Do not weaken production signatures
for stale consumers. Prefer canonical models directly. Do not add Any/object,
unnecessary polymorphic parameters, casts, narrowing helpers, model_copy workarounds,
serialization round trips, compatibility paths, mocks, suppressions or blanket
exclusions to silence findings.

Use central Beads through ~/gc and direnv. Before mutations verify 'rtk proxy direnv
exec . bd context --json' from $HOME/gc and the selected hq/server store. Read gc-11qywz
and coordinate a bounded assignment there before implementation; this document is an
execution prompt, not another tracker. Do not restart Gas City orchestration. Do not
launch agents automatically. Coordinate file ownership with the operator's other
agents; only one writer per owner. Freeze source mutations while generation/codemod
transactions run. Generation and workspace gates are serialized by the coordinating
agent.

Every diagnostic, generation, formatting, codemod, test and validation action uses an
existing selector-free root Make verb from $HOME/flext, prefixed with rtk proxy. A
member route is 'rtk proxy make -f flext-core/Makefile check'; use the corresponding
member as needed. Read the Make owner to discover existing verbs; never invent
selectors or bypass Make with bare analyzers/pytest. Structural rewires belong to make
mod. Never generate production files from pytest. Never hand-edit generated
__init__.py, facets, Makefiles or pyproject.toml.

Exception decision rule: authorization alone is insufficient. For each proposed
restoration record the exact rule and scope, verified authorization, present
architectural need, actual offending construct, alternatives considered, and why a
root-cause fix cannot preserve the required contract. If a correct root-cause fix
exists, implement it and do not restore that exception. Do not strengthen or relax
unrelated policy. Missing evidence is not permission to restore. Coordinate any
necessary policy edit with the policy owner; do not add local
noqa/type-ignore/excludes.

Return the changed owners and consumers, current diff, exact command/cwd/exit/decisive
output, runtime evidence, remaining RED findings and exception decisions to the
coordinating Bead. Never claim green from old reports, zero collection, warnings or
partial checks. Do not merge, close Beads or retire worktrees as a worker. The
coordinator handles authorized no-ff/admin integration only after required proof.

## Exclusive ownership

Own stale consumer calls and fixtures only, divided by member/file with the
coordinator; source changes require evidence that the source contract itself is wrong.

## Sources to inspect

Begin with flext-core/tests/unit/test_utilities_type_guards_coverage_100.py,
test_handler_discovery_module.py, test_logging_stages.py, test_registry.py and their
current public owners; expand by actual native diagnostics.

## Required correction

Replace unnecessary raw asserts and literal comparisons introduced in place of valid
tm calls. Preserve genuine negative runtime scenarios without statically invalid
assignments or invented adapters. For guard results investigate the actual
union/public contract before introducing narrowing. Use current typed fixtures and
public c/t/p/m/u, direct canonical models and native interface signatures. Do not
restore broad private-member-access or test complexity exceptions to preserve outdated
tests.

## Acceptance evidence

Prove observable behavior and failure semantics through public boundaries; rerun member
Ruff, Pyrefly, Pyright, Mypy and affected tests using native routes. No reduced test
collection or renamed expectations solely to accept broken behavior.
