# Resume FLEXT Work — `<BEAD_ID>`

Resume the work whose live state is recorded in Bead `<BEAD_ID>`. This prompt is
only an entry point; the current Bead, live code, and canonical repository sources
are authoritative.

## Required context

- **Active Bead:** `<BEAD_ID>`
- **Primary skill:** `<SKILL_NAME>`
- **Lane:** `<ROOT|FLEXT_INFRA|SUBMODULE_NAME>`
- **Writable files:** `<EXPLICIT_FILE_OWNERSHIP_MATRIX>`
- **Reference project:** resolve the canonical comparison project path from the live workspace (e.g. `git rev-parse --show-toplevel` sibling lookup) rather than hard-coding a machine-specific absolute path
- **Current references:** list every inspected `file:line` before editing.

## Resume procedure

1. Run `bd show <BEAD_ID>` and inspect the current Git state.
2. Read every mutable target again; old prompts and summaries never override live code.
3. Record `TARGET`, `IMPACT`, `RISK`, ownership, and the next incomplete action in
   the Bead.
4. Run the narrow baseline for the active lane.
5. Edit at most five files per batch unless a public change requires callers and
   exports in the same atomic batch.
6. Run import, lint, type, scoped test, CLI, and documentation gates that apply.
7. Fix failures forward, then record commands, exit codes, and decisive output.
8. Commit explicit paths, fast-forward push, and record the SHA before changing lanes.

## Hard constraints

- Never reset, restore, stash, clean, revert, or destructively check out shared work.
- Do not add shims, fallbacks, legacy aliases, conversion layers, pass-through
  wrappers, suppressions, stubs, hardcodes, or parallel old/new APIs.
- Update all consumers, exports, documentation, and tests with every public change.
- In `flext-infra`, structural rewrites use Rope and existing mnemonic services;
  do not add AST- or regular-expression-based rewrites.
- Keep `_parts/__init__.py` out of new canonical aggregation paths. Replace an
  existing aggregator only in its own green batch with all consumers updated.

## Reference shape

Validate these anchors against the live reference project before using them:

- `src/algar_oud_mig/api.py`: public MRO facade without inline logic.
- `src/algar_oud_mig/base.py`: service base and model-derived command parameters.
- `src/algar_oud_mig/cli.py`: thin router, typed handlers, and integer-returning `main()`.
- `src/algar_oud_mig/__init__.py`: export-only lazy public exports.
- `constants.py`, `models.py`, `protocols.py`, `typings.py`, and `utilities.py`:
  thin `c/m/p/t/u` facades composed through MRO and nested namespaces.

## Public-change census

Before changing a facade, public class, CLI route, or export, inspect and update:

- package `api.py`, `base.py`, `cli.py`, `__main__.py`, `__init__.py`, stubs,
  lazy-import maps, and `__all__`;
- `[project.scripts]` in `pyproject.toml`;
- facade owners and their private namespace implementations;
- consumers under `src/`, `tests/`, `docs/`, `examples/`, scripts, and dependent packages;
- documentation configuration, generated docs, and contract tests.

## Minimum validation template

Use canonical Make verbs where available; replace placeholders with the active scope.

```bash
uv run python -c "import <package>; print(<package>.__name__)"
ruff check <touched-files> --no-fix
make check CHECK_GATES=lint
pyrefly check <touched-files>
pyright <touched-files-or-project>
make test PROJECT=<project> MATCH=<narrow-match>
make docs PROJECT=<project> DOCS_PHASE=audit
<entrypoint> --help
```

Run only applicable commands, but never omit a required gate silently. Store long
findings in `.beads/artifacts/<BEAD_ID>/` and keep the Bead note concise.

## Next action

Load `<SKILL_NAME>`, read the Bead and live code, validate the reference anchors,
and complete only the next unfinished green slice.
