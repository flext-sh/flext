---
name: flext-agent-strict-rules
description: Mandatory rules for all coding agents — simple runtime aliases only (never FlextRuntime.Aliases.* for c,m,r,t,u,p,d,e,h,s,x), correct typing for narrowing (isinstance/TypeGuard, never type()), dismantle polymorphic code into centralized Pydantic v2 models, no loose methods. Apply across all projects (32+); use multiple agents in parallel for speed; lint-clean, no warnings/errors.
---

# Flext Agent Strict Rules (Mandatory)

**Scope**: All coding agents working in this repository.  
**Authority**: CLAUDE.md §3 Code Law, §9 Agent Instructions. This skill expands and enforces them.

---

## 1. Simple Runtime Aliases Only (Mandatory — No Exception)

- **Forbidden**: Never use `FlextRuntime.Aliases.constants()`, `.models()`, `.result()`, `.typings()`, `.protocols()`, `.utilities()`, `.decorators()`, `.exceptions()`, `.handlers()`, `.service_base()`, or `.mixins()` to define package-level aliases. Remove any such usage totally.
- **Required**: Use **simple runtime aliases only**: direct assignment to the facade class (e.g. `c = FlextConstants`, `m = FlextModels`, `r = FlextResult`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = FlextDecorators`, `e = FlextExceptions`, `h = FlextHandlers`, `s = FlextService`, `x = FlextMixins`). No alias registry; no staticmethod layer for defining c, m, r, t, u, p, d, e, h, s, x.
- **Facade pattern**: Each facade (e.g. FlextUtilities) MUST expose **staticmethod aliases from external subclasses** so call sites have **one flat namespace** (e.g. `u.foo`, `u.bar`). No subdivision of namespaces (no `u.Mapper.foo` at call sites). Subprojects: access **only** via that project's namespace (`from flext_cli import m, u` then `m.Foo`, `u.parse`).
- **Access**: Through the **project's runtime alias only**, with no subdivision. Subprojects define nested classes for organization then **class-level aliases at the facade root** so call sites use `m.Foo`, `m.Bar`. Aliases and namespaces follow the **MRO protocol only**. Use direct methods; runtime helpers come from **x** (FlextMixins) via MRO.
- **Rule**: One namespace per project. No duplicate alias assignments; no compatibility aliases (`LegacyX = NewX`). Remove all non-runtime aliases and loose (pass-through) methods; use canonical names and direct methods only.
- **Invalid instructions**: Any text that says "resolve via MRO registry (FlextRuntime.Aliases)" or "use FlextRuntime.Aliases" is **wrong**. Remove it. Access is through the **project runtime alias only** (e.g. `m`, `c`, `r`, `t`, `u`, `p`, `d`, `e`, `h`, `s`, `x`); MRO protocol only; **no** alias registry or staticmethod layer.

---

## 2. No Loose Aliases or Pass-Through Methods

- **Remove**: Any alias that only renames another symbol (e.g. `FactoryDiscovery = FactoryDecoratorsDiscovery`, `FlextModelsBase = FlextModelFoundation`, `cast_direct = staticmethod(...)`). Call sites must use the canonical name.
- **Remove**: Methods that only delegate with no added behavior (e.g. `def foo(self): return Bar.baz(self)`). Call `Bar.baz` (or the canonical method) directly.
- **Rule**: Direct methods and single canonical names only. No wrappers that only forward.

---

## 3. Type Narrowing — Use `isinstance` or `TypeGuard`, Never `type()` for Narrowing

- **Forbidden**: Using `type(x) is T` or `type(x) == T` for the purpose of type narrowing in production code. Type checkers do not narrow on `type()`; they do on `isinstance()` and `TypeGuard`. Swapping `isinstance` for `type()` is forbidden.
- **Required**: Use correct typing for type narrowing: `isinstance(x, T)` or a `TypeGuard` so that after the check the type checker knows the type. For Pydantic models and structured data, prefer `model_validate` / `model_validate_json` so validation and type are centralized.
- **Exception**: AST or other code that intentionally requires exact type identity (e.g. `type(node) is ast.Call`) may keep `type()` only when the goal is exact class identity and no narrowing is needed in the same block; prefer `isinstance(node, ast.Call)` where narrowing is desired.
- **Rule**: Use correct typing to avoid type-narrowing failures. Never replace `isinstance` with `type()`.

---

## 4. Polymorphic Code → Centralized Pydantic v2 Models

- **Goal**: Dismantle polymorphic functions and methods into a single contract. Replace multiple branches on type/union with one (or a small set of) Pydantic v2 model(s) that define shape and validation.
- **Use**: Discriminated unions (`Literal` discriminator), `Field`, `model_validator`, `field_validator`, `model_validate`, `model_validate_json`. One entry point for validation; avoid long `if isinstance(...)` chains over many types.
- **Avoid**: Ad-hoc `Union[A, B, C]` handling with repeated `isinstance` in function bodies. Prefer overloads or a single validated model.
- **Rule**: Maximum use of centralized models with Pydantic v2 validation; minimal ad-hoc type branching.

---

## 5. Scale and Parallelism (all projects, strict)

- **Scope**: Apply these rules across **all projects** (flext-core, flext-cli, flext-api, flext-ldif, flext-ldap, flext-meltano, tap/target/dbt variants, etc.). Follow each project's standards (CLAUDE.md, per-project CLAUDE.md).
- **Parallelism**: Use multiple agents in parallel at maximum scale (e.g. one agent per project or per report section) to complete refactors as fast as possible. Each agent: one project or one report section; minimal, verifiable changes; run `make check` and `make test` for touched project.
- **Quality**: Lint-clean with no warnings or errors; stability; remove all unnecessary code. Do not defer violations without explicit operator approval (CLAUDE.md §8).
- **Checklist**: `.reports/EXECUTION-CHECKLIST-aliases-typing-polymorphic.md` — apply in order; validate after each batch.

---

## 6. Verification

- After edits: run the relevant `make check` / `make test` for the touched project. No claims of completion without executable evidence.
- **Reports** (apply in order; use multiple agents in parallel for scale):
  - `.reports/non-runtime-aliases-and-loose-methods.md` — remove listed aliases and loose methods; use canonical names at call sites.
  - `.reports/typing-violations-report.md` — replace `type()` / `__class__` with `isinstance` or TypeGuard.
  - `.reports/polymorphic-refactor-targets.md` — refactor polymorphic functions to centralized Pydantic v2 models.
- **Checklist**: `.reports/EXECUTION-CHECKLIST-aliases-typing-polymorphic.md`.

---

## 7. Exigent Instructions for Agents (Mandatory)

1. **Tipagem**: Use **sempre** a tipagem correta para type narrowing: `isinstance(x, T)` ou `TypeGuard`. Nunca use `type(x) is T` nem `type(x) == T` para narrowing. Nunca troque `isinstance` por `type()`.
2. **Polimorfismo**: Desmonte **todos** os modos polimórficos de funções e métodos: substitua ramificações em 3+ tipos por **modelos Pydantic v2 centralizados** (discriminated unions, `Field`, `@field_validator`, `@model_validator`). Máximo uso de modelos centralizados com validação Pydantic v2; mínimo de ramificações ad-hoc por tipo.
3. **Aliases**: **Somente** aliases de runtime simples (ex.: `c = FlextConstants`, `m = FlextModels`, `x = FlextMixins`). **Nunca** use `FlextRuntime.Aliases` nem qualquer registro de aliases; remova totalmente qualquer uso. Facades expõem **staticmethod aliases das subclasses externas** para um único namespace plano; subprojetos: acessos **somente** no namespace do projeto.
4. **Remoção**: Remover todos os aliases não-runtime e métodos soltos (pass-through); usar apenas métodos diretos e nomes canônicos. Reforçar uso dos aliases de runtime.
5. **Escala**: Use **múltiplos agentes em paralelo em larga escala** (um agente por projeto ou por seção do relatório) para aplicar refators o mais rápido possível nos 32 projetos. Cada agente: um projeto ou uma seção; mudanças mínimas e verificáveis; rodar `make check` e `make test` no projeto tocado.
6. **Qualidade**: Código sem warnings/erros de ruff e pyright; estabilidade; remover código desnecessário. Não altere padrões estabelecidos pelos SKILLS e CLAUDE.md; mudanças cirúrgicas; não perca funcionalidade de negócio.
