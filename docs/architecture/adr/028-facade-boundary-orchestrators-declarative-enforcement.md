# ADR-028 — Facade Boundary: External Libraries, Orchestrators, Declarative Enforcement

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Definitions](#definitions)
- [Enforcement](#enforcement)
- [Consequences](#consequences)
- [Rollout](#rollout)

<!-- TOC END -->

- **Status:** ACCEPTED — operator orders 2026-10-24 (verbatim below)
- **Date:** 2026-10-24
- **Scope:** every internal FLEXT project (`internal_flext`) and all code tracked in its
  repository — `src/` packages and every other tier (`tests/`, `examples/`, `scripts/`,
  docs code) — with the same standardized rules in every project
- **Complements:** ADR-005 (config/settings SSOT), ADR-014 (family shape), ADR-018
  (generator declarations: derive, never list), ADR-027 (facade single-owner law)

## Context

Operator orders, 2026-10-24, verbatim:

> "vc nao pode usar griffe assim direto tem que usar via c,t,p,m,u !!!!! , nada fora
> deles pode usar bibliotecas externas (fora as de flext e c,t,p,m,u e as internas de
> python) é a regra de flext"
>
> "precisa coloca as rules em agents, AGENTS.md, skills, ADRs e bans e fixes, nao pode
> permitir deixar isso voltar a acontecer em todos os lugares e vá sempre corrigindo"
>
> "esses modulos fora de c,t,p,m,u e api tem que ser sempre orchestradores (fora de
> c,t,p,m,u nao pode ter declaracoes dos objetos deles nem mesmo em declaracoes
> implicitas (e delas sem permitir que elas violem as das outras tb), tem que banir,
> impor e fazer logo ) começando logo agora em seu trabalho em flext-infra e nela em
> geral e depois em todas as outras"
>
> (quoting a `_utilities` body that narrows `griffe.ExprTuple | griffe.ExprList |
> griffe.ExprSet` with `isinstance` and re-parses elements with `ast.literal_eval`)
> "violacao !!!!"
>
> "as violacoes estatiscas de flext-core tem que ser todas migradas para flext-infra de
> forma declarativa !!!!!!!!!!!!!!!!11 e removida dele"

Trigger: `flext_infra/codegen/python_model.py` imported `griffe` directly from a
service module, and the follow-up utility still named griffe types inline and re-parsed
values by hand. A census on 2026-10-24 (`ast` over every `flext-*/src` package, stdlib
derived from `sys.stdlib_module_names`) found 112 runtime third-party imports in modules
outside the facades across 12 repositories.

## Decision

1. **External libraries only inside the facades.** A third-party library is imported at
   runtime only by a `c`/`t`/`p`/`m`/`u` family module of the owning domain, or by a
   layer-0 config/settings module for its foundation libraries. Every other module
   imports only the Python standard library and FLEXT packages.
2. **Library types only through declarations.** Inside the facades too, an external
   library's types are named only through `t` aliases (and `p` protocols where the
   contract is structural). `u` behavior consumes those names. `u` never re-narrows or
   re-parses (`isinstance` chains, `ast.literal_eval`, manual dict walking) what a `t`/`m`
   declaration validates once at the owner boundary; it uses the library's native
   typed primitives.
3. **Modules outside `c/t/p/m/u` and `api` are orchestrators.** They compose calls to
   the facades and hold no declaration of a facade kind, explicit or implicit:
   - no constants, literal name sets or lookup tables (→ `c`);
   - no type aliases, `TypeVar`s, inline `Literal[...]` domains or ad hoc unions (→ `t`);
   - no `Protocol` classes (→ `p`);
   - no models, `dict`/`TypedDict` payload contracts or settings (→ `m`);
   - no reusable helper functions or nested helpers (→ `u`).
4. **The families do not violate one another.** `c` holds constants only, `t` types only,
   `p` protocols only, `m` models only, `u` behavior only, each in the import order
   `c → t → p → m → u` (reverse imports `TYPE_CHECKING`-only) and with one owner per
   object (ADR-027).
5. **Static enforcement lives only in flext-infra, declaratively.** Every static
   (source-shape) violation check is a declarative rule in flext-infra's catalog,
   applied by its generic engines (`make mod` fixes, `make check` detection). flext-core
   keeps no static enforcement catalog, predicate data or source-analysis engine; the
   existing ones migrate to flext-infra in one cutover with zero residue.
6. **Every module is one nested class.** All declarations of every module — in every
   tier of the repository, not only `src/` — live inside its single top-level nested
   class (ADR-018 point 11). The few exceptions (an executable `main()`, pytest
   fixtures and hooks in `conftest.py`, generator-emitted dunders) are declared once,
   documented, and validated automatically by the declarative catalog; anything else
   is a violation.
7. **Marked compatibility fails its users, not its declaration.** An old,
   compatibility or fallback path that must survive a rewiring window carries the
   stdlib `warnings.deprecated` marker with `compat: <old> -> <new owner>; fix: <exact
   rewire>`. The marked declaration does not fail CI; every remaining use of it does
   (type checkers report deprecated use as an error), so the rewire is forced and the
   path dies with its last consumer.
8. **One standard, automated.** The rules are identical for every project, applied by
   flext-infra's engines and the code-review graph as automatically as possible;
   duplicated code and domain violations are rejected, never accepted as debt.

## Definitions

- **Facade module:** the first segment below the package root is a canonical facade
  file (`constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py`) or its
  private family package (`_constants`, `_typings`, `_protocols`, `_models`,
  `_utilities`).
- **Layer-0 module:** `_config`, `_settings` and their source helpers; they import only
  stdlib and their foundation libraries (pydantic, pydantic-settings, yaml).
- **Allowed roots outside the facades:** stdlib (derived from `sys.stdlib_module_names`),
  `__future__`, the module's own package root, and FLEXT-family roots (derived from
  installed distribution metadata). No library list exists anywhere.
- **Runtime import:** a top-level import statement. Imports under `if TYPE_CHECKING:`
  never run and are outside the boundary.

## Enforcement

All in flext-infra's declarative catalog, propagated to every consumer:

- **Owner routing** (`library-facade-boundary.yml`, `ban-*-library-import`): which
  distribution owns each library; rows stay in step with
  `c.ENFORCEMENT_LIBRARY_OWNERS` in the same change.
- **Facade boundary** (this ADR, Decision 1): any runtime import outside the allowed
  roots in a non-facade module. Derived roots, no library names.
- **Library types** (Decision 2): an external library's types referenced inline outside
  `_typings`/`_protocols`, `u` included.
- **Declaration placement** (Decisions 3–4): the declaration-placement rule family
  (constants, aliases, `Literal` domains, protocols, models, payload dicts, reusable
  helpers outside their family; cross-family violations), with fixtures and `make mod`
  fixes wherever the move is mechanical, and where/why/how diagnostics otherwise.

A violation is RED in `make check`; a diagnostic is guidance, never a waiver.

## Consequences

- Services, CLI routes, codegen and workflow modules shrink to orchestration; logic and
  declarations move to the owning domain facade (`u.Cli` for toml/yaml/json/files/
  templates, `u.Infra` for infra-only libraries, `t`/`p` for their types).
- flext-core loses its static enforcement engine and catalog; runtime behavior of the
  facades is unchanged.
- New libraries need only a facade owner; no rule edit names them.

## Rollout

1. flext-infra first (its four sweep scopes, the griffe owner, then the remaining
   sites), then every other repository in dependency order.
2. flext-core static enforcement migrates to flext-infra declarative rules in one cutover
   and is deleted from flext-core.
3. Proof per repository: the declarative rules report zero findings, `make mod` is a
   fixed point, runtime imports of every package succeed, and the gates are green.
