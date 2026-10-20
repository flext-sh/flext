# Repair Pyrefly source-root identity

<!-- TOC START -->

- [Assignment contract](#assignment-contract)
- [Exclusive ownership](#exclusive-ownership)
- [Sources to inspect](#sources-to-inspect)
- [Required correction](#required-correction)
- [Acceptance evidence](#acceptance-evidence)

<!-- TOC END -->

## Assignment contract

Work in $HOME/flext on upload-20261007, as explicitly requested by the operator. First verify the live branch, current WIP, nearest AGENTS.md, .agents/commands/flext-law.md and branch-matched skills. Preserve and adopt all existing changes; never reset, rebase, force-push, overwrite unknown work, or restore a historical tree. Historical results below are diagnosis leads, not current acceptance evidence.

The operator requires tests, scripts and examples to consume current public source interfaces and the strictest origin-owned types. Do not weaken production signatures for stale consumers. Prefer canonical models directly. Do not add Any/object, unnecessary polymorphic parameters, casts, narrowing helpers, model_copy workarounds, serialization round trips, compatibility paths, mocks, suppressions or blanket exclusions to silence findings.

Use central Beads through ~/gc and direnv. Before mutations verify 'rtk proxy direnv exec . bd context --json' from $HOME/gc and the selected hq/server store. Read gc-11qywz and coordinate a bounded assignment there before implementation; this document is an execution prompt, not another tracker. Do not restart Gas City orchestration. Do not launch agents automatically. Coordinate file ownership with the operator's other agents; only one writer per owner. Freeze source mutations while generation/codemod transactions run. Generation and workspace gates are serialized by the coordinating agent.

Every diagnostic, generation, formatting, codemod, test and validation action uses an existing selector-free root Make verb from $HOME/flext, prefixed with rtk proxy. A member route is 'rtk proxy make -f flext-core/Makefile check'; use the corresponding member as needed. Read the Make owner to discover existing verbs; never invent selectors or bypass Make with bare analyzers/pytest. Structural rewires belong to make mod. Never generate production files from pytest. Never hand-edit generated __init__.py, facets, Makefiles or pyproject.toml.

Exception decision rule: authorization alone is insufficient. For each proposed restoration record the exact rule and scope, verified authorization, present architectural need, actual offending construct, alternatives considered, and why a root-cause fix cannot preserve the required contract. If a correct root-cause fix exists, implement it and do not restore that exception. Do not strengthen or relax unrelated policy. Missing evidence is not permission to restore. Coordinate any necessary policy edit with the policy owner; do not add local noqa/type-ignore/excludes.

Return the changed owners and consumers, current diff, exact command/cwd/exit/decisive output, runtime evidence, remaining RED findings and exception decisions to the coordinating Bead. Never claim green from old reports, zero collection, warnings or partial checks. Do not merge, close Beads or retire worktrees as a worker. The coordinator handles authorized no-ff/admin integration only after required proof.

## Exclusive ownership

Own Pyrefly search-path derivation and relevant tests; preserve analysis coverage.

## Sources to inspect

flext-infra/src/flext_infra/deps/extra_paths.py; config/tooling.yaml path rules; modernizer Pyrefly tests and projection owner.

## Required correction

Investigate pyrefly_search_paths adding _included_pyrefly_env_dirs even though project-shared-search-paths is empty and policy explains that scripts.* has one package identity. Analysis inclusion and import search roots are different concepts. Repair their conflation using typed existing owners. Never exclude tests/examples/scripts to remove duplicate identities or missing imports.

## Acceptance evidence

Exercise real public package imports and native Pyrefly after regeneration. Verify all intended trees remain analyzed and package identities remain qualified. Historical full check reported 18 generated-initializer missing imports; recalculate current findings.
