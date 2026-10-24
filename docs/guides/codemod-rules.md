# Codemod Rules

<!-- TOC START -->

- [Catalogs and layers](#catalogs-and-layers)
- [Make verbs](#make-verbs)
- [ast-grep rules](#ast-grep-rules)
- [Text rules](#text-rules)
- [Tests and snapshots](#tests-and-snapshots)
- [Workflow](#workflow)

<!-- TOC END -->

FLEXT applies structural migrations through the codemod engine that flext-infra owns.
The provider-neutral authoring procedure (one law per rule, generalization, exactness,
consolidation) is the `codemod` skill. This guide covers the FLEXT engine:
where rules live, the keys it reads, and the verbs that run it. Every value named here
is declared by the flext-infra owner cited next to it; that owner wins over this guide.

## Catalogs and layers

| Layer | ast-grep rules | Text rules |
|---|---|---|
| Universal (every project) | `flext-infra/src/flext_infra/config/rules/ast-grep/` (`sgconfig.yml` with `scope: universal`) | `flext-infra/src/flext_infra/config/rules/mod/sed.yaml` |
| Runtime (consumers of a provider) | an installed package's `sgconfig.yml` with `scope: runtime` | none |
| Project overlay | `<repo>/config/rules/ast-grep/sgconfig.yml` | `<repo>/config/rules/mod/sed.yaml` |

The engine composes the providers in that order:
`flext_infra/_utilities/codemod_rules.py`, `codemod_rule_plan`. Rule ids are unique across
every loaded provider. A text rule may also name the projects it targets in
`distributions`; an empty list means every project (`codemod/text_gates.py`,
`_selected_rules`). Put a rule at the highest layer where its law holds.

## Make verbs

Declared in `flext-infra/src/flext_infra/config/codegen.yaml` (`make.verbs`):

| Surface | Effect |
|---|---|
| `make mod` | Apply ast-grep, semantic and text rules to a proven fixed point; committed snapshots are verified, never rewritten. |
| `flext-infra refactor mod-text` | Replay only the authenticated declarative text rules. |
| `flext-infra refactor ast` | Scan report of the ast-grep and sed cascades over the governed corpus; `--apply` reaches the mechanical fixed point. |
| `flext-infra refactor mod-snapshots --apply` | Regenerate the snapshots of the rules this repository owns, for a reviewed commit. |

`make mod` is the only common Make verb; the rest are `flext-infra refactor`
subcommands (`flext-infra refactor --help`).

Raw `ast-grep scan --update-all`, `sg -U` or engine modules never apply a rule to a
tree. `ast-grep scan --rule <draft> <scratch-copy>` is for prototyping a draft only.

## ast-grep rules

The universal `rewire-test-assert-*` family implements the
[workspace assertion standard](using-flext-tests.md#workspace-assertion-standard).
Its matcher owner is `flext-tests`; its patterns, native fixtures, and generated
snapshots have one writable owner in `flext-infra`. Consumers reexport the same
`tm` binding rather than copying matcher or transformation implementations.
Rules must preserve Python's evaluation and scope semantics, not merely remove
the `assert` token. In particular, narrowing and lazy-message guards use the
terminating public matcher without rebinding a referenced name or changing the
exception category. Runtime comparisons against the original snippets validate
these properties; snapshot text alone does not prove them.

A rule file holds one or more YAML documents (`---`). Each is standard ast-grep
(`id`, `language`, `severity`, `message`, `files`, `rule`, `constraints`, `utils`
references through `matches:`, `transform`, `fix`). Shared guards live in
`config/rules/ast-grep/utils/`.

The engine reads these `metadata` keys, declared in
`flext-infra/src/flext_infra/_constants/refactor.py` (`CODEMOD_RULE_*`):

| Key | Meaning |
|---|---|
| `context` | Per captured metavariable, a predicate the finding must satisfy: `{VAR: {is: <predicate>}}` or `{VAR: {not: <predicate>}}`, with optional `of`, `arg` and `as`. |
| `owner` | The distribution that owns the law; that project's own plan drops the rule. |
| `consumers_of` | The rule applies only to projects whose runtime closure includes that distribution. |
| `relocation` | A detection-only rule names the Rope relocation that repairs it and captures the symbol as `$NAME`. |
| `expected` | The exact finding count receipt; any other count fails. |
| `owned_path_suffix` | Reject owned `.pyi` paths from discovery even without a syntax tree; detection-only, with no context exemption. |

The predicates (`stdlib-module`, `own-package`, `runtime-alias`, `emitted-symbol`,
`member-relocation` and the rest) and their argument contracts are declared in
`CodemodContextPredicate` in the same module. Prefer a predicate over a literal list:
it derives the set from its source of truth.

`concrete-mixin-runtime-ellipsis` also rejects concrete class-local typing shells
whose bodies contain only ellipsis or discarded parameters, including the
`del`/`NotImplementedError` variant. Recompose the real implementation and state
owners instead of moving signatures into another typing-support class. Its
`protocol-declaration` and `resolved-symbol` predicates retain real Protocols and
resolve the typing guard; `declaration-decorator` compares the captured native
function's decorators with its configured module/symbol pair, preserving aliased
ABC and implemented overload declarations without a spelling-based exemption.
Ordinary type-only imports, type aliases and productive method bodies are not
shells. Generated headers do not exempt candidates.

The single-nested-class family (`ban-loose-module-object`, `require-module-class`,
`declare-single-class-export`, `ban-pytest-hook-outside-conftest`) binds every
Python file of the repository: src, tests, scripts, examples and docs code. A
module holds one top-level class, its canonical published bindings, `__all__` and
imports. The exception data is closed and each entry has a fixture: an
executable module's guarded `main()` entry point and generator-emitted dunders
(generator law p.11), plus the tests-tier delta of ADR-028 p.6 — pytest
fixtures, `pytest_*` hooks and `pytest_plugins` at module level, admitted only in
`conftest.py` and `tests/fixtures/**`. Ordinary test modules are not exempt.
Test-suite modules follow the same publication law as `src`: one `Tests<Stem>`
class plus its `__all__`, enforced by `declare-single-class-export` with no path
exemption. Any further exception needs the operator.

`ban-stub-file` is also admitted by owned path, independently of ast-grep matches.
Both `mod` and the codemod `check` gate consume `discover_python_files` through the
same source inventory and common admission. Empty, invalid, generated-header and
outside-`src` stubs remain findings.
Hidden or analysis-ignored descendants of declared source roots remain owned
stub-policy inputs without widening ordinary `.py` analysis. Stub leaf links keep
their own path spelling and do not grant permission to follow foreign targets.

Artifact declarations marked
`retired_typing_root` elect retired first-party typing trees even when ordinary
source scans ignore them; environment, installed dependency, foreign Git and
unmanaged submodule boundaries remain excluded. Reports distinguish `owned-path`
evidence from `ast-grep` evidence and retain authenticated source states.

The typed tooling document rejects stub options and producers in native pairs and
derived declarations. Its canonical loader checks rooted native/topology search paths
once against the elected project and actual installed interpreter roots, without
banning source import paths or installed third-party typing. `CodegenFilePlan` rejects
non-absent `.pyi` output, and authenticated
publication revalidates the same model law before effects, including unchecked copied
plans. Retirement uses `CodegenFilePlan` with absent desired bytes and mode;
`SemanticFilePlan` with no desired content remains a no-op, not a deletion.

## Text rules

`sed.yaml` holds `rules:`, a list of entries. The keys are the `CODEMOD_TEXT_KEY_*`
constants in `_constants/refactor.py`; any other key fails:

| Key | Meaning |
|---|---|
| `id`, `description` | Unique identity and the law it states. |
| `find`, `replace` | Python `re` pattern and replacement (`\g<name>` groups). |
| `flags` | Any of `IGNORECASE`, `MULTILINE`, `DOTALL`. |
| `include`, `exclude` | Repository-relative globs. Markdown targets must be included explicitly. |
| `distributions` | Project names the rule targets; empty means all. |
| `expected` | Exact match count receipt. |
| `capture_equals` | Required equality between captures. |

The engine refuses findings in generated files (fix the generator instead), and a
rewritten Python file must still parse (`codemod/text_gates.py`). Prefer an ast-grep
rule whenever the target has syntax.

## Tests and snapshots

- Every ast-grep rule has `tests/<id>-test.yml` with `valid` and `invalid` cases, plus a
  snapshot under `tests/__snapshots__/<id>-snapshot.yml` for each invalid case.
- `make mod` verifies them and fails on a changed fix output, a missing snapshot, or a
  snapshot of a removed rule or case.
- `flext-infra refactor mod-snapshots --apply` is the only regeneration; its default
  dry run fails while any snapshot differs. Review its diff in the same commit as the
  rule.

## Workflow

1. Search both catalogs and `utils/` for the law; widen an existing rule first.
2. Write or widen the rule and its test. Prototype only on scratch copies.
3. Run `flext-infra refactor mod-snapshots --apply` and review the snapshot diff.
4. Run `flext-infra refactor ast` to see every occurrence across the fleet.
5. Apply with `make mod`, then run `make tests`.
6. Commit the rule, test, snapshot and rewrites together.
