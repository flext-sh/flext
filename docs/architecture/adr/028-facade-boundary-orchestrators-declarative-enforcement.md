# ADR-028 — Facade Boundary: External Libraries, Orchestrators, Declarative Enforcement

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
  - [Decision 1](#decision-1)
  - [Decision 2](#decision-2)
  - [Decision 3](#decision-3)
  - [Decision 4](#decision-4)
  - [Decision 5](#decision-5)
  - [Decision 6](#decision-6)
  - [Decision 7](#decision-7)
  - [Decision 8](#decision-8)
  - [Decision 9](#decision-9)
  - [Decision 10](#decision-10)
  - [Decision 11](#decision-11)
  - [Decision 12](#decision-12)
  - [Decision 13](#decision-13)
  - [Decision 14](#decision-14)
  - [Decision 15](#decision-15)
  - [Decision 16](#decision-16)
  - [Decision 17](#decision-17)
  - [Decision 18](#decision-18)
  - [Decision 19](#decision-19)
- [Bidirectional Traceability](#bidirectional-traceability)
- [Definitions](#definitions)
- [Enforcement](#enforcement)
- [Consequences](#consequences)
- [Rollout](#rollout)

<!-- TOC END -->

- **Status:** ACCEPTED — operator orders 2026-10-24 (verbatim below); amended by
  operator orders and rulings of 2026-10-25 (Decision 9 examples, Decision 14 entity
  equality, Decisions 15–19) and the 2026-10-26 artifact-only fixture contract
  (Decision 6)
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

### Decision 1

  1. **External libraries only inside the facades.** A third-party library is imported at
    runtime only by a `c`/`t`/`p`/`m`/`u` family module of the owning domain, or by a
    layer-0 config/settings module for its foundation libraries. Layer-zero source
    helpers of the same package may depend on one another only when their native
    ownership and acyclic proposed graph are proven under [ADR-005 §2](005-config-settings-constants-templates-schemas-ssot.md#2-facade-and-layer-direction-is-strict);
    none imports its own `c/t/p/m/u` family. Every other module imports only the
    Python standard library and FLEXT packages.

### Decision 2

  1. **Library types only through declarations.** Inside the facades too, an external
    library's types are named only through `t` aliases (and `p` protocols where the
    contract is structural). `u` behavior consumes those names. `u` never re-narrows or
    re-parses (`isinstance` chains, `ast.literal_eval`, manual dict walking) what a `t`/`m`
    declaration validates once at the owner boundary; it uses the library's native
    typed primitives.

### Decision 3

  1. **Modules outside `c/t/p/m/u` and `api` are orchestrators.** They compose calls to
    the facades and hold no declaration of a facade kind, explicit or implicit:
    - no constants, literal name sets or lookup tables (→ `c`);
    - no type aliases, `TypeVar`s, inline `Literal[...]` domains or ad hoc unions (→ `t`);
    - no `Protocol` classes (→ `p`);
    - no models, `dict`/`TypedDict` payload contracts or settings (→ `m`);
    - no reusable helper functions or nested helpers (→ `u`).

### Decision 4

  1. **The families do not violate one another.** `c` holds constants only, `t` types only,
    `p` protocols only, `m` models only, `u` behavior only, each in the import order
    `c → t → p → m → u` (reverse imports `TYPE_CHECKING`-only) and with one owner per
    object (ADR-027).

### Decision 5

1. **Static enforcement lives only in flext-infra, declaratively.** Every static
   (source-shape) violation check is a declarative rule in flext-infra's catalog,
   applied by its generic engines (`make mod` fixes, `make check` detection). flext-core
   keeps no static enforcement catalog, predicate data or source-analysis engine; the
   existing ones migrate to flext-infra in one cutover with zero residue.

### Decision 6

  1. **Every module is one nested class.** All declarations of every
    tier of the repository, not only `src/` — live inside its single top-level nested
    class (ADR-018 point 11). The few exceptions (an executable `main()`, pytest
    fixtures and hooks in `conftest.py`, generator-emitted dunders) are declared once,
    documented, and validated automatically by the declarative catalog; anything else
    is a violation. Operator order 2026-10-24 (verbatim): "os tests sempre seguem as
    mesmas regras de felxt, mas com conftest e fixtures/ a mais com um pouco mais de
    liberdade, de resto é igual, as outras pasta python sempre igual a src". So
    `tests/` follows every rule here. The canonical global
    `testing/observable-runtime` rule's artifact-only amendment of 2026-10-26
    supersedes permission for executable fixture modules under `tests/fixtures/`.

    That root contains artifacts and data only, including source-shaped bytes used
    as engine inputs. It contains no executable test classes, builders, aliases,
    models, package initializers or `conftest.py`, at any depth. File extension
    alone does not establish executable ownership; artifacts are never imported
    or executed in the suite process.

    Executable declarations and builders belong to the test-code `c/t/p/m/u`
    families, pytest wiring to `conftest.py` outside the artifact root, and behavior
    to the declared test layers. Every other executable Python folder follows the
    same rules as `src/`. The shared inventory owner keeps artifact bytes outside
    live collection, lint, types, refactoring and generation, without inspecting
    their content to decide applicability. These boundaries are declared once and
    propagated; a local exclusion is not another enforcement owner.

    The existing scenario-root declaration is the
    `flext_fixture_trees_root` pytest ini key: flext-infra projects it into every
    generated pytest configuration from `scenario_data_roots`, and the flext-tests
    fixture-tree plugin registers and reads it (`c.Tests.FIXTURE_TREES_INI`). That
    plugin keeps every scenario directory out of live collection and hands tests
    `fixture_tree("<scenario>")` (`p.Tests.FixtureTree`), which copies the tree into
    the test's `tmp_path` or into a declared consumer destination.
    Tests never use pytester's `copy_example`, whose `pytester_example_dir` key exists
    only while the pytester plugin is active.

### Decision 7

  1. **The deprecated-signature window is the standard route to zero compatibility
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

### Decision 8

  1. **One standard, automated.** The rules are identical for every project, applied by
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

  2. **Generated projections are gate-clean by construction** (amended 2026-10-28,
    campaign `flext-pipol`): every projection published by `make gen` or `make mod`
    passes typing, lint, format and check gates under the frozen rule catalog with
    zero post-adjustment, manual OR automated. A post-render cleanup pass — the
    engine running a fixer or formatter over its own output — is prohibited;
    cleanliness is a property of the template and renderer, and a projection that
    needs repair is repaired at its generating source. The admission proof is the
    cycle: `make gen` followed directly by `make check` is green, and `make fmt` /
    `make fix` are no-ops, on every repository
    ([ADR-018 verification contract](018-generator-declarations.md#verification-contract)).

    **Implementation status:** this is an accepted contract pending complete
    engine implementation and runtime proof under `flext-pipol`. Existing
    post-render repair code is a migration finding, not evidence that the
    contract is already satisfied. Small publication transactions use
    [ADR-018's cooperative-reader barrier](018-generator-declarations.md#single-read-single-batch-publication-amended-2026-10-28-campaign-flext-pipol);
    their fast validation does not reduce any frozen gate policy or replace
    full slice acceptance.

### Decision 9

  1. **No embedded code or long text constants.** Operator order 2026-10-24 (verbatim):
    "código de constnats longos tipo esse a seguir em constatns ou inline (até mesmo em
    testgs) são violacoes gravíssimas". Source code or long text built as string
    literals (multi-line literals, implicit concatenation of statement lines, scripts
    handed to a subprocess or `exec`) is forbidden in every tier, constants modules and
    tests included. Behavior is exercised by calling the public API directly with
    fixture data; templates live in the generator's template files; long data lives in
    typed configuration owners. Code examples are the inverse case and are governed,
    not exempt: operator order 2026-10-25, verbatim (tracker memory
    `operator-order-2026-10-25-embedded-code-same-rules`): "até mesmo o código dentro
    docstring e markdown tem que sempre atualizado, testado, formatado e atender as
    mesmas regras flext que o projeto". Every example in a docstring or Markdown file
    tracks the current API, runs under the documentation tests, is formatted, and
    follows every decision of this ADR (root-letter imports, no library names
    outside the facades, the Pydantic way).

### Decision 10

  1. **Imports go through package lazy exports, never module paths or module objects.**
    Operator orders 2026-10-24 (verbatim): "violacao gravissima -> from
    flext_infra.validate.testmon_db import FlextInfraTestmonDbInspector <<<< import por
    modulo ao inves de usar `__init__.py` lazy import" and "violacao gravissima import do
    modulo e uso por ele-> class FlextContext(flext_context.FlextModelsContextState
    .ContextState, FlextUtilitiesContext)". A name is imported from the nearest package
    whose generated lazy `__init__` publishes its direct declaring module: the
    declared facade surface at the package root, or the owning family package
    (`_models`, `_utilities`, …) for family declarations and composition.
    Descendant exports are not automatically lifted into ancestor initializers.
    A child's `__all__` describes that child's surface; it does not authorize an
    ancestor to publish every internal subclass. Preserve declared facade letters
    and child-package metadata without flattening directory boundaries. Methods of
    a component subclass are reached only through the nearest composed MRO facade
    at each nested family stage, not by a sibling calling the leaf class directly
    ([ADR-014 §1](014-family-part-shape-rope-codemod-rules.md#1-semantic-facade-ownership),
    [ADR-018 nested projection](018-generator-declarations.md#nested-facade-projection)).
    Importing from a module path below that package, or importing a module object and
    reaching its classes by attribute, is forbidden in every tier, own package included,
    and in generated facades too. Operator order 2026-10-24 (verbatim): "mesmo em
    `__init__.py`, as as aliases simples tem que estar declaradas no modulo e exportadas
    em `__all__` para entrarem nele (ou herdar do namespace anterior) , nao faça fixes com
    violacoes, nunca, jamais, corrija pela causa raiz e regras". A short alias (`c`, `t`,
    `p`, `m`, `u`, `s`, …) is declared once in its owning module and listed in that
    module's `__all__`; an `__init__.py` only re-exports it (or inherits it from the
    parent namespace) and never assigns it.

    Hierarchical composition imports the upstream letters. Operator rulings
    2026-10-25 (verbatim): "essa é a forma canonica, isso tem que estar declarado,
    documentado e automatizado, confirme com as regras atuais" and "veja que estamos
    falando nas declaracoes de c,t,p,m e u usar import deles das bibliotecas mais
    altas para composição enquanto elas estão sendo compostas para uso hierárquico".
    Inside the declaration modules of the five families, while the package's own
    facades are being composed, the letters of the upstream packages it composes
    (`from flext_cli import c, t, p, m, u`) are the canonical binding: each own family
    composes the upstream same-letter class by MRO. The boundaries around it:
      - Elect the spelling from native references at the class header. Retain a bare
        upstream letter when its identity is used there; when an existing verified
        alias is the used binding, retain only that alias. A later publication of the
        package's own letter does not make an earlier bare binding occupied. Never
        emit both `u` and `u as provider_u` from one provider when the bare binding
        has no independent reference. This applies equally to nested namespaces;
        it does not create a per-library alias list or change the MRO identity.
      - the package's own letter inside its own family is forbidden in every form,
        including `<pkg>.u` reached through the package module object (ENFORCE-051);
      - a same-family sibling is imported from the family package;
      - modules outside the families read every letter from their own package root
        (ENFORCE-003, which also owns `if TYPE_CHECKING:` imports);
      - a later layer stays TYPE_CHECKING-only from any package
        (`ban-reverse-runtime-import`).

    A letter of any facade package read through its module object (`import pkg`,
    then `pkg.u.X`) is detected by the single rule `ban-letter-module-object`.

### Decision 11

 1. **Tools are used natively and fully.** Operator order 2026-10-24 (verbatim): "nao
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
     - no per-finding Python admission exists: every finding is the native match. A
       project fact a catalog rule needs is a stable generated utility (`own-package`,
       `facade-package`, `runtime-alias`, ...) referenced through `matches:`, or a file
       scope the generated provider publishes and the stage applies through
       `metadata.scope` (`in`/`not-in`, or `partition` for one generated rule
       `<id>--<package>[--<key>]` per file group). Runtime import cycles are the
       whole-graph `ban-cyclic-import` gate, not a rule;
     - the staged scan configuration is reproducible with native ast-grep, so a native
       scan and `make mod` agree.

### Decision 12

 1. **Validation applies every FLEXT rule in the real tree.** Operator order 2026-10-24:
    a concept, design or fix is validated in the real tree under the full FLEXT law
    and the project's own tool configuration, through the canonical gates. Scratch
    files, loose classes, default tool presets and isolated probes that skip the real
    rules are fake evidence, never proof. A type-checker proof uses the gate's exact
    interpreter binding.

### Decision 13

 1. **The `make mod` pipeline has a fixed order.**
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

### Decision 14

 1. **Pydantic declarations are complete at import.** Every model, settings, config and
    service class is complete when its module is imported (`__pydantic_complete__`),
    with no `model_rebuild`.
     - A protocol-typed model field uses `t.Port[p.X]`, Pydantic's official field-level
       marker. A protocol metaclass is not FLEXT-conformant because the metaclass is
       private API.
     - `arbitrary_types_allowed` is banned.
     - A strict contract declaring an Enum field retains the member's type during
       Python validation and handoff by reference. Pydantic's `use_enum_values=True`
       extracts its primitive value during validation, so it cannot be inherited by
       the [Core `ContractModel` preset](https://github.com/flext-sh/flext-core/blob/0.12.0-dev/src/flext_core/_models/_base/Flextmodelsbase_part_02.py#L133-L143).
       Serialize primitive values at the outward JSON boundary, not between strict
       contracts.
     - A field naming a sibling through its own enclosing family class is banned
       (`ban-enclosing-family-field-reference`): the enclosing class is unbound while
       its body runs, so the model stays incomplete. The fix extracts the nested member
       into its own family module.
     - Facade roots (`c`, `t`, `p`, `m`, `u`) never inherit a model.
     - Entity equality follows Pydantic (operator ruling 2026-10-25, tracker memory
       `operator-ruling-2026-10-25-entity-equality-pydantic-way`, verbatim: "o que
       pydantic recomenda em relação a isso, o que fazer, qual a forma mais pydantic
       way, é a que precisa ser feito mesmo que precise refatorar o uso
       globalmente"). `m.Entity` and `m.AggregateRoot` define no custom
       `__eq__`/`__hash__`: equality is value-based (same type and field values),
       identity is compared explicitly by id, entity collections are keyed by id, a
       mutable entity is unhashable, and only frozen models hash, by value. Consumers
       relying on identity equality are rewired fleet-wide by rule.

### Decision 15

 1. **Library names never leave the facades; exports are named by capability.**
    Operator orders 2026-10-25, verbatim (tracker memories
    `operator-order-2026-10-25-library-names-only-in-facades` and
    `operator-rulings-2026-10-25-libnames-locks-ldif-rope`): "lembre de ser CA/DI, os
    modulos fora c,t,p,m,u como services e outros moduloes, e projetos externos, nao
    podem ficar sabendo nem do nome da biblioteca, eles usam interface genéricas" and
    "bibliotecas externas só em C,T,P,M,U e a exportação tem que ser prefixada pela
    funcionalidade e não pela biblioteca, por exemplo git_, refactor_ , workspace_ ,
    , ..... use refatoração em massa por sed, ast-grep e rope para automatizar isso ,
    pois depois vc tem que aplicar essa refatoração em massa em ai-hub e outros
    projetos flext que usam flext-infra". Decision 1 keeps the import inside the
    facade; this decision keeps the name there too:
     - only `c/t/p/m/u` implementation modules name a library (rope, griffe,
       networkx, libcst, ast-grep), in their private module and class names;
     - every outward surface — `p` protocols, `u` methods, `m` fields, `t` aliases,
       CLI options and documentation — uses a capability name prefixed by
       functionality (`git_`, `refactor_`, `workspace_`; `p.Infra.WorkspaceSnapshot`,
       `module_ast`, `rename`, `move`, `extract`), never `rope_*`, `Rope*`, `griffe_*`
       or any other library name;
     - the rename is a mass refactoring by rule (sed, ast-grep and rope through
       `make mod`), keeps the deprecated-signature window (Decision 7) for external
       consumers, and is then applied to ai-hub and every other project that uses
       flext-infra (census under bead `flext-1engx.11`).

### Decision 16

 1. **Maximum CA/DI decoupling; duplication and smells at zero.** Operator order
    2026-10-25, verbatim (tracker memory
    `operator-order-2026-10-25-max-decoupling-ca-di`): "lembre-se que tudo tem que ser
    o máximo desacoplado com as regras ca/di de flext-core e sempre corrija as
    duplicatas por jscpd e smells de qlty com as regras strict de flext".
     - Dependencies are `p` protocols injected at the composition root; dependencies
       point inward.
     - `ContextVar`, `lru_cache` and `ClassVar` holders used as service locators are
       forbidden; a dependency arrives through its port.
     - Pluggable implementations (LDIF and LDAP servers and their equivalents) are
       injected only by DI. Registries, priority lists and ready-made lists are
       forbidden, and their users — services and the `c/t/p/m/u` families — never
       know which implementation they hold. Operator order 2026-10-25, verbatim
       (tracker memory `operator-order-2026-10-25-servers-di-never-registry`): "os
       servers em ldif, ldap sao sempre usados por DI, nunca, never jamais por
       registry ou listas prontas, os usuários (services) nunca podem saber que
       server eles estão usando e e c,t,p,m,u a mesma coisa, a interface deles tem
       que ser sempre descoplada 100% do tempo e sempre, qq coisa fora isso é violação
       gravíssima".
     - Library access happens only in the owning `c/t/p/m/u` modules (Decisions 1 and
       15).
     - Every change leaves jscpd duplication and qlty smells at zero under the strict
       FLEXT configuration. The fix is extraction to the canonical owner, never an
       ignore, a raised threshold or a narrowed scope. The only authorized jscpd
       exception is the license header.

     - Rules are generalized and few (Decision 18).
     - `FlextResult` (`r`) railway combinators (`.map`, `.flat_map`, `.map_or`,
       `.unwrap_or`, `r.traverse`, `r.from_validation`, `r.create_from_callable`) and
       covariant `p.Result[Never]` failure constructors (`r.fail`, `r.fail_op`,
       `r.from_failure`) replace imperative `if res.failure: return ...` ladders,
       manual `for`/`try` accumulation blocks, and local `outcome = r[T]` type aliases,
       enforced and auto-repaired through `railroad-result.yml` in `make mod`.

### Decision 17

 1. **Rope owns the workspace model and its refactorings.** Operator order
    2026-10-25, verbatim (tracker memory
    `operator-order-2026-10-25-rope-owns-model-refactors`): "lembre-se que tudo tem que
    ser o máximo desacoplado com as regras ca/di de flext-core, exemplo, rope nao tem
    referencia de todos os objetos em memória da workspace ? e ele tem metodos de
    refatoração, isso tem que ser usado ao inves de custom".
     - Each governed repository invocation reuses exactly one workspace project as its
       in-memory model (module cache, parsed modules, file listing, import tools, and
       change validation), exposed only through `p.Infra.WorkspaceSnapshot`; the
       `u.Infra` owner is the only module that names it (Decision 15). A workspace-level
       command uses its declared repository loop and creates one project per repository;
       it does not model sibling repositories as one project or open redundant projects
       for the same repository during that invocation.
     - **Amendment 2026-10-28 — accepted contract, implementation pending:**
       refresh is always incremental within that same native project.
       After a transaction, invalidate only changed resources, affected
       inventories and their dependent semantic facts, including moves and
       retirements; retain unchanged observations and inference. Reopening the
       project, full rediscovery or global cache clearing is not the refresh
       strategy. The common publication barrier precedes the first live
       bootstrap/import/source read and protects later lazy reads; it is not
       limited to snapshot construction. Staged validators use the independent
       candidate without reacquiring a parent-held live barrier. ADR-018 owns
       ordering, crash recovery and guarded rollback of owned effects.
     - Renames, moves and import rewrites use rope's native refactorings (rename with
       documentation occurrences, move, restructure, multi-project refactoring).
     - Custom parse, discovery, import-graph and rename/move planners that duplicate
       that model are deleted in the cutover that rewires their consumers (bead
       `flext-1engx.15`). What rope cannot express (format-preserving LibCST
       transforms, ast-grep rules, YAML and Markdown text renames, admission policy)
       keeps its own owner.
     - Numbered inheritance fragments implementing the same capability do not gain
       artificial responsibilities to evade a destination collision. Their methods
       consolidate at one implementation owner while the public facade retains its
       contract
       ([Core failure-factory declaration](https://github.com/flext-sh/flext-core/blob/0.12.0-dev/AGENTS.md#failure-factory-responsibility)).
       Native refactorings handle every part of that cutover they can express.

### Decision 18

 1. **Rules are generalized and few.** Operator order 2026-10-25, verbatim (tracker
    memory `operator-order-2026-10-25-rules-generalized-min-count`): "o sed, rope e
    ast-grep rules tem que estar sempre alinhados com as regras corretas de forma
    generalizada e automaticas usando sempre máximo de funcionalidades padrões das
    ferrametnas que as embasam e reduzir ao máximo ao número de rules que são
    executadas". One generalized rule per law, expressed with the tool's native
    features (ast-grep `constraints`, `utils`, `transform`, `rewriters`; rope
    refactorings); no per-package or per-library clones; a one-shot migration rule
    with a zero fleet census is deleted with its test and snapshot; the number of
    executed rules is tracked against a typed budget. The authoring declaration is
    [Codemod Rules, One rule per law](../../guides/codemod-rules.md#one-rule-per-law).

### Decision 19

 1. **Models import `u` only two ways; each family owns its Pydantic surface.**
    Operator ruling 2026-10-25, verbatim (tracker memory
    `operator-ruling-2026-10-25-models-u-imports-pydantic-home`): "models podem import
    u apenas de 2 formas, u do projeto flext maiis alto que ela importa, ou classe
    privada _utilities de seu namespace por casos bem restritos, veja que mdoels nao
    pode exportar metodos, ele precisa pydantic best practices sempre, anliase o caso
    com cuidado e arrume para evitar problemas, temos_utilities/pydantic.py que se
    estiver exportando pydantic que models precisa, ele precisa ser migrado para
    _models/pydantic.py e seu uso atualizado em todos os repos global wide, isso vale
    para c,t,p,m, e u de forma equivalente".
     - A `_models` module imports either the upstream FLEXT project's `u` (the
       hierarchical binding of Decision 10) or, in very restricted cases, a private
       `_utilities` class of its own namespace.
     - Models export no methods; they follow Pydantic best practices.
     - The Pydantic surface that models need lives in `_models/pydantic.py`, not
       `_utilities/pydantic.py`; it is migrated and every use is rewired in every
       repository. The same principle holds per family for `c`, `t`, `p`, `m` and `u`.

## Bidirectional Traceability

Each accepted decision links to its nearest workspace declaration and subproject
contract; those declarations link back to the exact decision anchor below. Project URLs
are pinned to the same `0.12.0-dev` release line used by their branch-matched law. Beads
record execution, status, and evidence; they do not replace either direction of the
architecture link.

| Decision | Workspace declaration | Subproject declaration and execution |
| --- | --- | --- |
| [8 — one standard, automated; gate-clean projections](#decision-8) | [Root `AGENTS.md`, automated correction](../../../AGENTS.md#automated-correction-is-the-law); [make commands guide, Convergence](../../guides/make-commands.md#convergence-shared-worktree-and-clean-rules); [ADR-018 verification contract](018-generator-declarations.md#verification-contract) | Campaign `flext-pipol` (gate-clean slice `flext-wznvp`); lazy-init wrapping cure `flext-tlqrw`; engine post-cleanup removal tracked on `flext-pipol` |
| [5 — static enforcement](#decision-5) | [Governance decision map](../../GOVERNANCE.md#adr-028-decision-map) | [Infra, ADR-028 Decision 5: Declarative enforcement](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/AGENTS.md#adr-028-decision-5-declarative-enforcement); Bead `flext-43iz8` |
| [15 — capability names](#decision-15) | [Root `AGENTS.md`, Decision 15](../../../AGENTS.md#adr-028-decision-15); [public core guide, What flext-core must not absorb](../../guides/using-flext-core.md#what-flext-core-must-not-absorb); [Governance decision map](../../GOVERNANCE.md#adr-028-decision-map) | [Infra `AGENTS.md`, Decision 15](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/AGENTS.md#adr-028-decision-15); external consumer census: `flext-1engx.11` |
| [16 — CA/DI and zero findings](#decision-16) | [Root `AGENTS.md`, Decision 16](../../../AGENTS.md#adr-028-decision-16); [consumer law, R2](../../standards/consumption-law.md#r2-no-duplication-structural-scan); [Governance decision map](../../GOVERNANCE.md#adr-028-decision-map) | [Infra `AGENTS.md`, Decision 16](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/AGENTS.md#adr-028-decision-16); [Target LDAP CA/DI declaration](https://github.com/flext-sh/flext-target-ldap/blob/0.12.0-dev/AGENTS.md#adr-028-decision-16-ca-di-and-quality); implementation and quality gates: `flext-1engx.15`, `flext-pawp5` |
| [17 — workspace model and native refactorings](#decision-17) | [Root `AGENTS.md`, Decision 17](../../../AGENTS.md#adr-028-decision-17); [Governance decision map](../../GOVERNANCE.md#adr-028-decision-map); [stabilization decision-link section](../../ways-of-working/stabilization-checkpoint-0.12.md#adr-028-decision-links); [Core failure-factory declaration](https://github.com/flext-sh/flext-core/blob/0.12.0-dev/AGENTS.md#failure-factory-responsibility) | [Infra `AGENTS.md`, Decision 17](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/AGENTS.md#adr-028-decision-17); [execution context, Workspace snapshot and analysis engine](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/docs/guides/execution-context.md#workspace-snapshot-and-analysis-engine); implementation: `flext-1engx.15` |
| [18 — generalized rules](#decision-18) | [Root `AGENTS.md`, Decision 18](../../../AGENTS.md#adr-028-decision-18); [Governance decision map](../../GOVERNANCE.md#adr-028-decision-map); [codemod guide, One rule per law](../../guides/codemod-rules.md#one-rule-per-law); [stabilization decision-link section](../../ways-of-working/stabilization-checkpoint-0.12.md#adr-028-decision-links) | [Infra `AGENTS.md`, Decision 18](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/AGENTS.md#adr-028-decision-18); projection cleanup: `flext-13s6n` |
| AI Hub consumer route | [AI Hub ADR-0039](https://github.com/datacosmos-br/ai-hub/blob/dev/docs/adr/0039-universal-law-references-in-governed-docs.md); [ADR catalog](https://github.com/datacosmos-br/ai-hub/blob/dev/docs/adr/README.md#fleet-canon); [engineering-law routing](https://github.com/datacosmos-br/ai-hub/blob/dev/docs/engineering-laws.md); [FLEXT development skill](https://github.com/datacosmos-br/agents/blob/dev/skills/framework/flext-development/SKILL.md) | Consumer Bead `aihub-9qdu6`; reciprocal-link Bead `flext-1engx.16` |
| [9 — governed embedded examples](#decision-9) | [Root `AGENTS.md`, embedded-code rule](../../../AGENTS.md#adr-028-decision-9); [documentation standard](../../standards/documentation.md#command-and-test-examples) | The docs Bead `flext-0exhi` records authoring and executable-doc validation. |
| Prior codemod ADR sections | [ADR-014 §5, Gate alignment](014-family-part-shape-rope-codemod-rules.md#5-gate-alignment-one-law-shared-consumers); [ADR-014 §6, Native tool responsibilities](014-family-part-shape-rope-codemod-rules.md#6-native-tool-responsibilities-amended-by-adr-028); [ADR-017, ADR-028 Supersession](017-parametrized-rule-surfaces-single-modernize-cli.md#adr-028-supersession) | These sections link back to the superseding decisions above. |

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
- **Library-prefixed exports** (operator ruling 2026-10-25: "bibliotecas externas só
  em C,T,P,M,U e a exportação tem que ser prefixada pela funcionalidade e não pela
  biblioteca"): `ban-library-named-facade-member` flags a facade member whose name
  starts with an installed third-party distribution (`rope_*`, `Pytest*`), not a
  capability prefix (`git_`, `refactor_`, `workspace_`). The renames are mass-applied
  through a deprecated-signature window.

The catalog follows one rule per law (operator order 2026-10-25). Facts that vary per
package, letter or library become the values of one document (`constraints` regex,
`any` branches, `utils`, `rewriters` with a `rewrite` transform), never one document
per value. One-shot migrations with a zero fleet census are deleted. The executed-rule
count per project is a gate metric whose budget is a typed configuration key
([codemod rules guide](../../guides/codemod-rules.md#one-rule-per-law)).

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
