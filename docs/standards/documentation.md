# Documentation Standards

**Single source of truth for how FLEXT documentation is authored, generated, validated, and published.**

All documentation automation lives in **one engine**: the docs services inside
`flext-infra` (`src/flext_infra/docs/`, `src/flext_infra/_utilities/docs*.py`).
There is no parallel docs tooling — no per-project scripts, no duplicated
generators, no hand-maintained API listings. If a docs capability is missing,
it is added to the flext-infra engine, never beside it.

## Pipeline

The canonical entry point is the `docs` verb of the root `Makefile`:

```bash
make docs WHAT=generate PROJECT=flext-core APPLY=Y  # regenerate derived docs (mutating)
make docs WHAT=build PROJECT=flext-core             # strict build -> .reports/docs/site
make docs WHAT=validate PROJECT=flext-core          # link/nav/reference validation
make docs WHAT=audit PROJECT=flext-core             # docstring + content audit
```

- `generate` is the only mutating phase and **requires `APPLY=Y`**; without it
  the run is a dry preview. It regenerates the derived surfaces only:
  `docs/api-reference/generated/**` and `docs/projects/generated/**`. The prune
  step never touches hand-written docs.
- `build` runs `mkdocs build --strict` for every project; output goes to
  `<project>/.reports/docs/site`.
- `validate` checks nav entries, internal links, and generated references.
- `audit` writes `<project>/.reports/docs/audit-report.md` covering docstring
  coverage (D/DOC), placeholder/stale content, and generated-surface drift.

Omitting `PROJECT` runs the phase across the whole workspace; orchestration
logs land in `.reports/workspace/docs/<project>.log`.

## Docstrings

Docstrings follow **PEP 257 + Google style**, enforced by Ruff in strict mode
(`select = ["ALL"]`, `preview = true`). The full standard, with real FLEXT
examples and the validation checklist, is
[standards/docstrings/PEP257-GOOGLE-RUFF.md](docstrings/PEP257-GOOGLE-RUFF.md).

Key points:

- **D401 (imperative mood) and D417 (undocumented parameters) are enforced.**
  Only `D203`, `D213`, and the soft `DOC201/DOC202/DOC402/DOC501/DOC502` set
  are ignored by design, per each project's `pyproject.toml`.
- Every public symbol earns a docstring that answers *why it exists*, not what
  the signature already says. Docstrings are written by hand; the audit phase
  measures coverage, it does not generate prose.
- Module docstrings carry the copyright + SPDX header inside the docstring.

## Generation from code

The engine derives documentation from the code itself, never from parallel
hand-maintained copies:

- **Public contract** — the API reference is generated from each project's
  public exports (`c`, `m`, `t`, `p`, `u`, `r`, `e`, `x`, `h`, `d`, `s`,
  `api`, `cli`, `base`, `services`), with a `doc_summary` per symbol and
  classifiers (facade, model, protocol, service, …) computed from the code.
- **Code communities** — `docs/architecture/communities/**` is generated from
  the code-review-graph community detection over the workspace call graph, so
  the architecture pages track the code as it actually is.
- **Project overviews** — `docs/projects/generated/**` aggregates version,
  dependencies, and structure facts from each project's own metadata.

## External site

The workspace documentation site is published to **docs.flext.sh**:

- Deployment is driven by the GitHub Pages workflow
  (`.github/workflows/docs.yml`), which runs the same `build` phase in
  strict mode and uploads `.reports/docs/site`.
- The site domain is fixed by the `CNAME` file in the deployed artifact.
- The root site nav is rendered from
  `flext-infra/src/flext_infra/templates/mkdocs_root.yml.j2`; nav changes are
  made in the template, never in a checked-in `mkdocs.yml` (generated, not
  versioned).
- Content-heavy trees that are reference material for the repo but not part of
  the published site (`references/**`, `projects/flext-*`, `releases/**`,
  `arc42/**`) are excluded via `tool.flext.docs.exclude_docs` in the root
  `pyproject.toml`. Exclusion from the site does not exempt them from the
  audit: stale or placeholder content is a defect anywhere under `docs/`.

## Authoring rules

- **English only.** Code, docstrings, docs, comments, and template output are
  written in English; non-English legacy text is translated in the same edit
  that touches the region.
- **Generated files are read-only.** Anything under a `generated/` directory
  carries an AUTO-GENERATED header and is reproduced by the `generate` phase;
  edit the source (code, templates, config), never the artifact.
- **Facts, not vibes.** Version numbers, test counts, and capability claims in
  docs must trace to the project metadata or a command output. When a fact
  cannot be verified cheaply, omit it and point at the gate that produces it
  (`make gen WHAT=check`, `make check`, `make docs WHAT=audit`).
- **One home per topic.** A subject has exactly one canonical page; everything
  else links to it. No duplicated standards across `docs/`, `README.md`, and
  skills — pointers only.

## Validation before landing

A documentation change is complete only with:

```bash
make docs WHAT=build              # strict build, 0 errors
make docs WHAT=validate           # links/nav green
make docs WHAT=audit              # no new placeholder/stale findings
```

and, for generator or template changes under `flext-infra`, the scoped project
gates (`make check PROJECT=flext-infra`, `make test PROJECT=flext-infra
MATCH=docs`).
