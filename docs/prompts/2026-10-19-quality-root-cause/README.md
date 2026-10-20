# Root-cause correction prompts — 2026-10-19

These are operator-requested prompts for manual dispatch, not a second task tracker. Work and evidence remain in central Bead gc-11qywz. No agent was launched by creating these files. No exception restoration is approved by this document.

The criticism before restoration is mandatory: preserve an exception only when verified authorization, a current architectural requirement and evidence of necessity all exist. Prefer a correct owner fix whenever possible. Do not restore the historical exception catalog wholesale.

- [Critically review architectural lint exceptions](01-exception-critical-review.md)
- [Repair generated lazy exports and absolute imports](02-generated-lazy-initializers.md)
- [Repair analyzer environment ownership](03-tool-runtime-environment.md)
- [Repair Pyrefly source-root identity](04-pyrefly-module-identities.md)
- [Repair Mypy projection and remaining source contracts](05-mypy-contracts-and-projection.md)
- [Migrate tests, scripts and examples to current public contracts](06-consumer-interface-migration.md)
- [Repair semantic codemod publication and typed fixtures](07-semantic-codemod-publication.md)
- [Repair origin-owned typing and facade generation](08-runtime-typing-and-facades.md)
- [Repair security, dependency and duplication gate causes](09-security-dependencies-duplication.md)
- [Coordinate serialized generation and final integration proof](10-integrated-generation-and-landing.md)

## Dispatch order and collision control

Start with 01 to assess policy. Implement 02–05 at their canonical producers with one writer at a time for shared templates; 03 already contains unvalidated WIP. Consumer work in 06–09 may proceed on explicitly disjoint files after producer contracts are established. 07 owns semantic publication, including the active IDE test. 10 coordinates all generation, gates and landing.

Each prompt is self-contained. Do not send several agents to write the same primary checkout files simultaneously. Before each assignment read live WIP and agree ownership through Beads. Generation/codemod publication must never race source edits.

Historical evidence: core native make check exited 2, receipt .reports/gates/20261019T204234.985057Z-1487714/check/1f7b879b-72e6-414c-8366-dc9b4de57e54. That snapshot was RED, with lint 2464, format 1, security 1765, Pyrefly 21, Mypy 59, Pyright 1, dependency 6, duplication 2 and codemod 1826 admitted findings. It must be refreshed before acceptance; the prompts do not claim these counts remain current.
