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
   is a violation. Operator order 2026-10-24 (verbatim): "os tests sempre seguem as
   mesmas regras de felxt, mas com conftest e fixtures/ a mais com um pouco mais de
   liberdade, de resto é igual, as outras pasta python sempre igual a src". So
   `tests/` follows every rule here; only `conftest.py` and `tests/fixtures/` carry the
   tests-tier delta (pytest fixture and hook functions, scenario data bound by
   fixtures), declared once in the catalog as that tier's exception data. Every other
   Python folder (`examples/`, `scripts/`, and any other) follows exactly the `src/`
   rules. Scenario trees (`tests/fixtures/<scenario>/**`) are input data for the
   engines under test, not code under test: they may hold deliberately violating
   sources, carry no generated `__init__.py`, and are excluded from lint, generation
   and the rule catalog through flext-infra's single exclude owner. Modules directly
   under `tests/fixtures/` stay fully governed. The scenario root is the
   `flext_fixture_trees_root` pytest ini key: flext-infra projects it into every
   generated pytest configuration from `scenario_data_roots`, and the flext-tests
   fixture-tree plugin registers and reads it (`c.Tests.FIXTURE_TREES_INI`). That
   plugin keeps every scenario directory out of live collection and hands tests
   `fixture_tree("<scenario>")` (`p.Tests.FixtureTree`), which copies the tree into
   the test's `tmp_path` or into a given `destination` such as a pytester consumer.
   Tests never use pytester's `copy_example`, whose `pytester_example_dir` key exists
   only while the pytester plugin is active.
7. **The deprecated-signature window is the standard route to zero compatibility
   code without breakage.** Operator order 2026-10-24 (verbatim): "toda a assinatura
   antiga fica marcada com warning indicando o caminho novo até migrarmos tudo e daí
   exterminamos o código antigo (isso tem que incluir os projetos externos mais
   tarde)" and "não é contradição, é garantir que não vamos manter ABSOLUTAMENTE NADA
   DE CÓDIGO ANTIGO DE COMPATIBILIDADE E SEM QUEBRAR O PROJETO" (tracker memory
   `operator-ruling-2026-10-24-deprecated-signature-window`). Every removed or renamed
   public signature stays as a thin pass-through to its new owner, marked with the
   stdlib `warnings.deprecated` marker `compat: <old> -> <new owner>; fix: <exact
   rewire>`. A constant carries the equivalent PEP 593 marker (bead `flext-1engx.12`).
   The marked declaration does not fail CI. Every remaining use of it does: type
   checkers report deprecated use as an error, and that report is the census. The
   rewire is applied by rule in each consumer's wave. The pass-through is deleted when
   the census reaches zero, external projects included (bead `flext-1engx.11`). An
   unmarked old path, or a zero-use marked path still present, is a defect. Current
   state: rule `report-compat-deprecated-marker.yml` still flags declarations; it is
   corrected under bead `flext-xws5d`.
8. **One standard, automated.** The rules are identical for every project, applied by
   flext-infra's engines and the code-review graph as automatically as possible;
   duplicated code and domain violations are rejected, never accepted as debt.
   Operator order 2026-10-24 (verbatim): "EXTREMAMENTE IMPORTANTE , LEI EXTREMA vc tem
   que fazer as correcoes de violacoes ser ao maximo possível automatizadas por
   flext-infra gen,upg,mod,fix,fmt !!!!!!!!!!!!!!!! correções manuais tem que ser A
   EXCESSÃO DA EXCESSÃO, E tem que propagar globalmente sem gerar erros, lints, fmts,
   outras violacoes". Every violation class is corrected by a flext-infra engine
   reached through `make gen`, `make upg`, `make mod`, `make fix` or `make fmt` (a
   generator source, a codemod rule with fixtures, a fixer), applied to every project,
   and its output is itself clean: a fix that leaves a lint, format, type or rule
   finding anywhere is a defective fix. A manual edit is allowed only for a genuinely
   unique case that no rule can express (the exception of the exception), and its
   reason is stated in the commit.
9. **No embedded code or long text constants.** Operator order 2026-10-24 (verbatim):
   "código de constnats longos tipo esse a seguir em constatns ou inline (até mesmo em
   testgs) são violacoes gravíssimas". Source code or long text built as string
   literals (multi-line literals, implicit concatenation of statement lines, scripts
   handed to a subprocess or `exec`) is forbidden in every tier, constants modules and
   tests included. Behavior is exercised by calling the public API directly with
   fixture data; templates live in the generator's template files; long data lives in
   typed configuration owners.
10. **Imports go through package lazy exports, never module paths or module objects.**
    Operator orders 2026-10-24 (verbatim): "violacao gravissima -> from
    flext_infra.validate.testmon_db import FlextInfraTestmonDbInspector <<<< import por
    modulo ao inves de usar `__init__.py` lazy import" and "violacao gravissima import do
    modulo e uso por ele-> class FlextContext(flext_context.FlextModelsContextState
    .ContextState, FlextUtilitiesContext)". A name is imported from the nearest package
    whose generated lazy `__init__` publishes it: the package root for consumers, the
    family package (`_models`, `_utilities`, …) for siblings and facade composition.
    Importing from a module path below that package, or importing a module object and
    reaching its classes by attribute, is forbidden in every tier, own package included,
    and in generated facades too. Operator order 2026-10-24 (verbatim): "mesmo em
    `__init__.py`, as as aliases simples tem que estar declaradas no modulo e exportadas
    em `__all__` para entrarem nele (ou herdar do namespace anterior) , nao faça fixes com
    violacoes, nunca, jamais, corrija pela causa raiz e regras". A short alias (`c`, `t`,
    `p`, `m`, `u`, `s`, …) is declared once in its owning module and listed in that
    module's `__all__`; an `__init__.py` only re-exports it (or inherits it from the
    parent namespace) and never assigns it.
11. **Tools are used natively and fully.** Operator order 2026-10-24 (verbatim): "nao
    usar funcionaldiade de ferramentas da melhor forma por causa de probleams nossos é
    VIOLAÇÃO EXTREMAMEMENTE GRAVE, CONSIDERANDO ISSO UM BYPASS OU FALLBACK, CORRIJA TUDO
    PARA FUNCIONAR SEMPRE FUNCIONAR DA FORMA CORRETA". A local defect never justifies
    reduced use of a tool: that is a bypass. When an owner verb or engine is broken, it
    is repaired at once so the tool's full capability runs through it; deferring,
    narrowing or degrading its use meanwhile is the same bypass. For the codemod
    catalog this means:
    - rules apply through `ast-grep scan --update-all`, and rule semantics are native
      ast-grep (`utils`, `constraints`, `transforms`, `rewriters`). SSOT-derived rules
      come from the class-A producers and renderers registered in
      `Infra.codegen.ast_grep`. They are rendered in memory by the `make mod` cascade,
      one document per shape, and are not projected into repositories (bead
      `flext-13s6n` removes the current per-rule projection);
    - per-finding Python admission is to be retired. Current state (2026-10-24): rules
      carrying `metadata.context` are still admitted per finding (bead `flext-uwwxc`);
    - the staged scan configuration is reproducible with native ast-grep, so a native
      scan and `make mod` agree.
12. **Validation applies every FLEXT rule in the real tree.** Operator order 2026-10-24:
    a concept, design or fix is validated in the real tree under the full FLEXT law
    and the project's own tool configuration, through the canonical gates. Scratch
    files, loose classes, default tool presets and isolated probes that skip the real
    rules are fake evidence, never proof. A type-checker proof uses the gate's exact
    interpreter binding.
13. **The `make mod` pipeline has a fixed order.**
    1. The canonical import header, generated from SSOT: the dependency namespace
       singletons, the project's own aliases, and the facade-module letter taken from
       the upstream facade, with reverse-layer letters under `if TYPE_CHECKING:`.
       Insertion fires only for names a module uses but binds nowhere. Its native
       form is one generated `import-header--<package>` rule per declaring package
       and scope: it inserts one `from <package> import ...` line with every name
       that package resolves there. A module inside a declaring package imports
       from the deepest declaring package containing it; any other module imports
       from the unique shallowest one. Step 3 prunes the unused names. ast-grep
       applies one insertion per anchor and run, so a per-name insertion would
       need a pass per name; a per-package insertion converges within the pass cap.
       In step 2, the generated `module-member--<package>` rules rewrite
       `<child>.<Name>` to `Name` when `<child>` is a child package bound by
       `from <package> import <child>`. The next pass's step 1 imports `Name`,
       and step 3 removes the module-object import.
    2. The whole codemod catalog, repeated until nothing changes.
    3. Last, ruff `--fix --select` over the import families declared in the tooling
       SSOT.
14. **Pydantic declarations are complete at import.** Every model, settings, config and
    service class is complete when its module is imported (`__pydantic_complete__`),
    with no `model_rebuild`.
    - A protocol-typed model field uses `t.Port[p.X]`, Pydantic's official field-level
      marker. A protocol metaclass is not FLEXT-conformant because the metaclass is
      private API.
    - `arbitrary_types_allowed` is banned.
    - A field naming a sibling through its own enclosing family class is banned
      (`ban-enclosing-family-field-reference`): the enclosing class is unbound while
      its body runs, so the model stays incomplete. The fix extracts the nested member
      into its own family module.
    - Facade roots (`c`, `t`, `p`, `m`, `u`) never inherit a model.

## Definitions

- **Facade module:** the first segment below the package root is a canonical facade
  file (`constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py`) or its
  private family package (`_constants`, `_typings`, `_protocols`, `_models`,
  `_utilities`).
- **Layer-0 module:** `_config`, `_settings` and their source helpers, plus the lazy
  loader (`lazy` and `_lazy`); they import only stdlib and their foundation libraries
  (pydantic, pydantic-settings, yaml). The roots are data in
  `c.Infra.IMPORT_LAW_LAYER_ZERO_ROOTS`, read only by `u.Infra.import_module_role`.
  Operator ruling 2026-10-24: a pytest plugin distribution's plugin modules (the
  modules its `pytest11` entry points register, flext-tests `_fixtures/*` included)
  are layer-0 for that plugin's foundation libraries (pytest, hypothesis); the catalog
  derives them from the entry points, and nothing else is allowed there.
- **Allowed roots outside the facades:** stdlib (derived from `sys.stdlib_module_names`),
  `__future__`, the module's own package root, and FLEXT-family roots (derived from
  installed distribution metadata). No library list exists anywhere. The one declared
  exception is the stdlib backports in tooling `lazy-init.stdlib-backports`
  (`typing_extensions`, operator decision 2026-10-24), which import like the standard
  library. Type checkers recognize the PEP 747 `TypeForm` special form only through its
  own name binding, so a type expression is passed to a `TypeForm[T]` parameter as
  `TypeForm(X)` with `from typing_extensions import TypeForm`; `t.TypeForm` is the
  facade's annotation alias and is never called (rule `ban-typeform-alias-call`).
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
- **Embedded code** (Decision 9, `ban-embedded-source-literal`): a multi-line string
  literal (one string, a triple-quoted block or an implicit concatenation) whose lines
  start a Python statement, and any implicit concatenation spanning three or more line
  breaks. Rendered source moves to a template under `templates/` rendered through
  `u.Cli.template_*`; test source moves to files under `tests/fixtures/<scenario>`, which
  a test receives through the `fixture_tree` fixture (owner `u.Tests.materialize`,
  flext-tests).

- **Pydantic completeness** (Decision 14): `ban-enclosing-family-field-reference`,
  `ban-arbitrary-types-allowed` and `ban-model-rebuild`.

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
