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

The root dispatcher resolves workspace scope from its typed topology. Generated Make
surfaces and documentation are changed at their template or configuration owner, then
regenerated with `make gen`.

## Related guides

- [Development](development.md)
- [Testing](testing.md)
- [Getting started](getting-started.md)
