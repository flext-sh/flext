# Protocols and quality gates: resume checkpoint

Status recorded on 2026-11-09 at the operator's request to stop. Work is **incomplete**. Preserve all existing changes and coordinate with the FLEXT integration chat before editing shared owners. The active tracking issue is `flext-vjj1s.8`.

## Objective and constraints

- Establish and test structural model protocols without `t.schema_for_model`; use native Pydantic model ownership for serializable schema fields, structural protocols at consumer boundaries, and existing opaque ports only for non-serializable capabilities.
- Propagate using `flext-infra` native `mod`, `mod-text`, `gen`, `fmt`, and `fix`; validate Ruff, Pyrefly, Pyright, Mypy, pytest, and real consumers throughout the requested FLEXT fleet and external projects using the current workspace.
- Do not suppress findings, weaken lint configuration, hand-edit generated projections, discard shared work, or treat partial checks as full acceptance. Preserve destination CAS and native tool behavior.

## Workspace at checkpoint

- Root: `/home/marlonsc/flext`, branch `fix/setup-gen-deadlock`, HEAD `5c48c2e0d7c40a32b8cdef87c7a42b9105f1f865`.
- Infra: `/home/marlonsc/flext/flext-infra`, branch `upload-20261007`, HEAD `4dfb50517613221322378e3151fc9543f5148f2f`.
- Root, Infra, Core, Web and many other members contain uncommitted changes, including shared work from other actors. `git status --short` in each repository is the live authority; do not reset, stash, or overwrite it. Root Makefile and 32 member Makefiles were generated to expose an optional test-file selector.
- No matching `flext-infra refactor mod`, `workspace tests-full`, `codegen generate`, or `make tests-full` process was observed at checkpoint. Other chats may still work independently; coordinate before touching their areas.
- No final integration, push, fleet-wide validation, or completion is claimed.

## Verified results and limits

- Core full pytest: 2,448 passed, receipt `flext-core/.reports/tests/20261109T085132.931057Z-4107428`. This predates later Core changes and does not validate the current tree. A subsequent Core four-lint check passed for the event-protocol change, receipt `flext-core/.reports/check/c7c36296-91ca-44d1-b1c0-e059c28198c7`; Core settings was later modified by the integration chat and needs current revalidation.
- Web: four lints passed, receipt `flext-web/.reports/check/9afeff23-910b-4f98-b0c1-a86c3f01a918`; 156 pytest passed, receipt `flext-web/.reports/tests/20261109T104054.317716Z-2082778`. Native generation reached 91 planned, zero written in `.reports/refactor/web-native-all-generator-final-current.log`. Results are bounded to those runs, not the fleet. Later shared-owner changes require appropriate revalidation.
- Infra native `pydantic-native-protocol-model-envelope` published 97 files, with staged fixed-point and four fresh-import probes passing; log `flext-infra/.reports/refactor/native-model-envelopes-verified-fixtures-apply.log`. The following complete four-lint run failed with Ruff 6, Pyrefly 125, Pyright 18, Mypy 26: receipt `flext-infra/.reports/check/af54367b-521a-4f08-b3b0-7716891ee723`. Later fixes exist; these counts are a historical snapshot, not current counts. A separate full Ruff run later passed, receipt `flext-infra/.reports/check/3618f2a6-bc67-45e1-b0ad-e5447bb20373`, before further changes.
- Envelope tuple/identity tests passed five cases, receipt `flext-infra/.reports/tests/20261109T113901.437404Z-3432923`; nested preview tests passed eight cases with Git storage protection intact, receipt `flext-infra/.reports/tests/20261109T112028.164719Z-3101870`. Optional and sequence admission changes and new fixtures were being prepared when stopped; inspect and test their actual state before applying again.
- Mixed-model publication passed five focused tests with runtime identity, schema, serialization and four-checker evidence: `flext-infra/.reports/tests/20261109T114806.057457Z-3599779`. Do not infer a green complete Infra suite from focused cases.
- An opaque mutable cache pilot passed the four checkers and a real write/identity test, receipt `flext-infra/.reports/tests/20261109T111744.900382Z-3044455`. Native rule `opaque-mutable-model-ports` was still in preview: `.reports/refactor/infra-opaque-port-native-lexical-preview.log` ended with two pending semantic files and successful fresh-import probes; this is **not** an applied or green result.
- Real fixture consumers completed upgrade, setup with current FLEXT, generation, sdist, wheel and strict documentation build after using real Git history. The containing pytest file still had two failing test bodies: receipt `flext-infra/.reports/tests/20261109T120746.961640Z-3914239`.
- Infra full pytest was still failing. The last full runs exposed source-view, Make-verb fixture, mixed-source ownership, private-import resolution, and consumer lifecycle issues; inspect latest `flext-infra/.reports/tests/` receipts and associated logs rather than assuming any failure has been fixed.

## Resume in order

1. Re-read current source, repository instructions, active issue comments and concurrent coordination. Recheck repository and process state; this checkpoint is not a lock or a clean-tree requirement.
2. Finish and validate the in-progress envelope optional/sequence admission and the opaque mutable-port rule with native previews, negative cases, real runtime and the four type/lint tools. Inspect the current dirty files before continuing; the stopped agents may have left partial edits. Apply in bulk only after the native contract is proven.
3. Complete remaining pytest causes at their owners. Relevant work: `tests/unit/codegen/test_codegen_make_verbs.py`, source-view handling, private-import cutover, `tests/unit/codegen/test_codegen_config_lifecycle.py`, and the mixed authored/generated `tests/utilities.py` fixture. The integration chat removed the obsolete `declare_governed_kind` call and was investigating the fixture's `extra_verbs` and `verb_groups` inputs. Use `make tests-full FILE=<repository-relative-test>` for focused reproduction, followed by the unscoped full suite.
4. Re-run full Infra Ruff, Pyrefly, Pyright and Mypy without `--file`; fix remaining findings at shared owners and repeat full pytest. Verify actual reports and exit codes; never repeat `--file` as if it were multi-select.
5. Propagate the verified solution through all requested FLEXT members and authorized external consumers with native automation; validate each relevant project, real runtime, generation fixed points, and full requested gates. Reconcile committed branches, generated artifacts and integration with the coordinating chat. Do not claim completion until all requested scope is proved.

## Coordination and cautions

- The operator authorized coordination with the FLEXT integration and Datacosmos/Odoo chats. The FLEXT integration chat is `01a1bec2-8b63-7503-a8d9-d79aaac922d7`; it was independently handling kind mod-text admission, Core settings, editor/qlty generation and Mise bootstrap. Check its current status before editing overlapping owners.
- User-confirmed lint catalog changes for Infra commits `46b8b1906c` and `7c7f18316c` were reported by that chat; they are not general authority to alter other lint rule selection or severity. Web was checked both with the earlier policy and with that reported authorized projection.
- The initial broad claim that receipt `f10a8211-c450-46bd-a566-0372c94f9eb2` covered multiple `--file` inputs was withdrawn: the CLI accepts one file and selected only the last. Do not reuse that claim.
- AI Hub's real retirement-help entrypoint and environment setup passed earlier using current editable FLEXT, but external projects have not all passed their required final checks. The envelope rule's AI Hub support was not proven and was not authorized for blind application.
