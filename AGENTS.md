# AGENTS.md — FLEXT Canonical Engineering Law

## § Meta do FLEXT (North Star — governa todas as ações)

FLEXT é a plataforma fundacional tipada e ecossistema de pacotes Python para integração de dados, tooling de plataforma e conectores operacionais enterprise. Todo pacote `flext-*` herda de uma única fonte de verdade arquitetural (`flext-core`) e serve a esta meta: **garantir que toda integração seja construída sobre primitivas tipadas, validadas e reutilizáveis** — com contratos `r[T]` em todo caminho falível, facades canônicas (`c/m/t/p/u`) por responsabilidade, e zero código ad-hoc.

O sucesso do FLEXT é medido por: net-LOC negativo em refactors, zero `Any`/bypass/stub, e toda mudança verde validada com evidência antes de declarar pronto.

### Cadeia de governança inviolável (sempre ativa)

Esta Meta e as regras universais abaixo governam **todas as ações de todos os agentes em todas as sessões**, sem exceção, atalho, ou flexibilização por conveniência, urgência ou trivialidade percebida. A cadeia é always-on via prelúdio do `~/.ai-hub/AGENTS.md` + hooks `ai-hub-hook.sh` (PreToolUse/PostToolUse/SessionStart/Stop) + carregamento deste arquivo:

1. **Meta do FLEXT** (acima) — o norte que toda decisão técnica serve.
2. **Universal Agent Law** (abaixo, espelha `~/.ai-hub/AGENTS.md`) — R0–R15 invioláveis.
3. **Regras FLEXT** (abaixo do bloco universal) — stack, naming, contratos, runtime.
4. **Skills path-scoped** (`.agents/skills/*/SKILL.md`) — carregadas por contexto.

Se qualquer ação não puder servir à Meta nem obedecer às regras limpas, o agente PARA e pergunta ao operador — nunca desvia, contorna, ou executa às cegas.

### Precedência absoluta de decisão (sempre ativa, inegociável)

Quando camadas conflitam, a ordem abaixo decide — e o artefato de camada inferior é AJUSTADO para refletir a camada superior, nunca o contrário:

1. **Pedido vivo do operador** — prioridade máxima. Sobrepõe beads, planos, ADRs, skills e documentação. Se um pedido conflita com qualquer artefato, o artefato (bead/plano/ADR/skill/doc) é corrigido para seguir o pedido.
2. **Beads** — sobrepõem ADRs, skills e docs.
3. **ADRs** — sobrepõem skills e docs.
4. **Skills e docs** — base; cedem a qualquer camada acima.

Em caso de dúvida, conflito ou ambiguidade, o agente PERGUNTA ao operador antes de agir — sempre.

<!-- mro-wkii.14 (agent: codegen) — regras universais U2–U8 gravadas por pedido vivo; não remover sem ADR + pedido do operador. Base flext-core (runtime config/settings) em estabilização por outro agente — esta lane é governança + scaffold. -->

### Regras universais FLEXT para config/settings, typing e MRO (sempre ativas, invioláveis)

Estas regras (U2–U8) complementam a precedência (U1, acima) e a Universal Agent Law (R0–R19). Onde qualquer ADR/skill/doc conflitar, o artefato é AJUSTADO — nunca a regra.

<!-- mro-i6nq.7 (agent: codex) — U2/U4 follow live U18: direct validated singletons only, with every intermediary removed. -->
- **U2 — Strict config/settings access (single form).** Always use `from <namespace> import config, settings`, then consume `config.<Namespace>.<domain>` / `settings.<Namespace>.<domain>` directly (for example, `from ai_hub import config, settings` followed by `config.AiHub.*` / `settings.AiHub.*`). No MRO-provided access, instance attribute, alias, forwarding member, wrapper, proxy, or model-less mapping is permitted.
- **U3 — Modelado, nunca model-less no consumo.** Domínios são `BaseModel` validados (`frozen=True, extra="forbid"` por domínio; `Root` `frozen=True, extra="ignore"`); `model_validate` na borda; **nunca `dict`/`Any`/`object` no consumo**. Ingestão YAML model-less fica confinada à borda (`FlextConfig` lendo `config/*.yaml`).
- **U4 — Zero config/settings intermediaries.** `ConfigProxy`, `SettingsProxy`, `config_access`, `settings_access`, `self.config`, `self.settings`, forwarding getters/properties, importlib resolvers, pass-through wrappers, and compatibility aliases are forbidden and must be removed at the source. Consumers access only the direct namespaced singletons from U2. Config payload schemas are declaration-only Pydantic models owned by `_models/config.py`; the `config.py` / `settings.py` foundation and their private subclasses never import `c/t/p/m/u` at runtime.
- **U5 — Import direction `c → t → p → m → u`.** Forward (alta consome baixa) em runtime; reverse SEMPRE via `TYPE_CHECKING`; cross-project (consumer → base upstream) livre em runtime; leaf config/settings nunca importam a facade `c/t/p/m/u` do próprio projeto em runtime; exceção cuidadosa documentada com prova de não-ciclo.
- **U6 — Typing estrito.** Nunca `Any`/`object`. Anotar sempre com tipos (`t.*` aliases), nunca com classes. Composto usa alias de `t` (`t.MappingOf[K,V]`, `t.SequenceOf[T]`, …). Nullable sempre explícito `T | None` (fora, nunca implícito). Em `models`, importar `p` via `TYPE_CHECKING` (models fica Pydantic-only em runtime). Em `protocols`, importar `m` via `TYPE_CHECKING` (reverse obrigatório; tipa os `@property` com o modelo real).
- **U7 — Zero helpers soltos / zero aliases de compat.** Nenhuma função helper fora do facade MRO; nenhum alias/shim/`DEPRECATED` de compatibilidade; remoção no mesmo ciclo (net-LOC ≤ 0).
- **U8 — Comentário de coordenação por edição.** Toda edição em superfície compartilhada (`AGENTS.md`, ADRs, facades `c/t/p/m/u`, leaf config/settings, codegen, `__init__` gerado) leva comentário curto no trecho alterado indicando agente + bead + motivo, para evitar conflito entre agentes em paralelo.

<!-- mro-wkii.14 (agent: codegen) — U9–U11 + lição anti-destruição gravadas por pedido vivo após incidente em que um agente destruiu o WIP pendente de todos os agentes; linguagem dura proposital; não remover sem ADR + pedido do operador. -->

- **U9 — Nunca brigar com mudança de outro agente (inviolável).** Worktree é compartilhado. É PROIBIDO sobrescrever, reverter, desfazer, "limpar" ou misturar no próprio commit qualquer trabalho que não seja da sua lane (staged OU unstaged). Conflito real ⇒ coordenar por bead/U8, ajustar o SEU, ou PARAR e perguntar ao operador. Cada commit leva APENAS os pathspecs da sua lane (`git commit -- <paths explícitos>`); `git add .` e qualquer comando que puxe staging/worktree alheio são proibidos. Misturar WIP alheio no seu commit é brigar com outro agente — falha grave.
- **U10 — Analisar se o comando é destrutivo ANTES de executar (inviolável).** Antes de qualquer comando, classificar o blast-radius: é destrutivo, irreversível ou de efeito amplo? Exemplos proibidos sem confirmação explícita do operador: `git reset`, `git checkout`, `git restore`, `git clean`, `git stash`, `git revert`, `git push --force`/`--force-with-lease`, `rm -rf`, sobrescrever arquivo com `Write` em cima de trabalho alheio, apagar branches/tags, qualquer push non-fast-forward. Destrutivo ou de escopo incerto ⇒ PARAR, mostrar o comando exato e o risco, e AGUARDAR confirmação. Rollback é sempre proibido (reforça R1): nunca desfazer trabalho — seu ou de outro — por conta própria.
- **U11 — Gravar sempre, validar sempre, nunca deixar quebrado (inviolável).** Toda alteração é GRAVADA (commit + fast-forward push com SHA evidenciado no bead) e VALIDADA (gates verdes: import smoke + `ruff --no-fix` + typecheck + testes escopados) antes de seguir. O projeto NUNCA pode ficar quebrado por qualquer alteração: a árvore permanece importável/coletável a todo instante (reforça R18). Red gate ou tree quebrada = incidente ativo: parar tudo, corrigir na origem, só continuar verde. "Depois eu valido/commito" é proibido — nenhum trabalho fica solto, pendente ou vermelho.

### Lição gravada — incidente de destruição de WIP multi-agente (não repetir)

Um agente destruiu, de uma vez, todas as mudanças pendentes (staged/unstaged) de todos os agentes neste worktree compartilhado. Causa-raiz: comando de efeito amplo executado sem análise de blast-radius e sem pathspec, somado a trabalho solto (não gravado) e ausência de validação contínua. Esta sessão cometeu falhas da mesma família e as registra como autocrítica para não repeti-las:

- Misturei WIP de outra lane no meu commit (commit parcial sem pathspec estrito ⇒ 43 arquivos/1319 linhas de `mro-wkii.13` entraram em `5c025e77`). Isso é brigar com outro agente (viola U9). Correção: commit SEMPRE com `-- <paths explícitos>`, nunca `git add .`.
- Continuei a escrever em lane compartilhada enquanto havia WIP alheio no mesmo submódulo, ampliando a superfície de conflito. Correção: checar `bd list --status=in_progress` e `git status` antes de escrever; com agentes em paralelo, isolar por pathspec e comentário U8, ou parar e coordenar.
- Li caminhos por pressa (path errado) em vez de verificar antes de agir. Correção: confirmar existência/conteúdo real (read-only) antes de qualquer escrita; nunca confiar só em memória/sumário.

Mecanismos obrigatórios de prevenção (sempre ativos): (1) pathspec explícito em todo `git add`/`git commit`; (2) análise de blast-radius antes de cada comando (U10); (3) gravação e validação contínuas (U11) para que nenhum trabalho fique solto e destruível; (4) rollback absolutamente proibido (R1/U10); (5) em dúvida, parar e perguntar ao operador (R16).

<!-- mro-zri7 (agent: kimi) — U12–U15 gravadas por pedidos vivos (2026-07-11): espelham UNIVERSAL_CORE §23, /flext-law §1A–§1B e agent-law-full §5.0; não remover sem ADR + pedido do operador. -->
<!-- mro-vzdq (agent: kimi) — U15 estendida com h/d/s e U16 (lei de testes strict) gravadas por pedido vivo (2026-07-11); espelham /flext-law §1B.1 e §8 + UNIVERSAL_CORE Rule 22; não remover sem ADR + pedido do operador. -->

- **U12 — Padrão de engenharia sênior obrigatório (inviolável).** Toda mudança — inclusive as "pequenas" — é entregue como engenheiro/arquiteto extremamente experiente: o aceite é produção, escalabilidade e manutenção ("funciona" não basta; cada linha sobrevive a 5 anos de manutenção: tipada, testável, observável, superfície mínima, zero código morto). SOLID, KISS, YAGNI, SSOT, Clean Architecture (domínio no núcleo; frameworks/drivers na borda), DI e PEP são o padrão — não opcionais. Erros bobos, código simplista/descartável, bad/god patterns (omnisciente ⇒ dividir por responsabilidade), over-engineering (tão grave quanto under-engineering) e legado mantido/ressuscitado são defeitos graves corrigidos na origem.
- **U13 — Zero dissimulação técnica (inviolável).** Proibido silenciar erros (`except: pass`, `# noqa`/`type: ignore` sem justificativa provada e registrada), bypass, shim, fallback que inventa/defaulta dados, mock/fake/"fingir" fora de testes, e fix superficial "faz-o-gate-passar" que deixa a causa-raiz viva. Erro propaga alto ou retorna `r.fail(...)` com contexto. Erro bobo que passou no gate = gate faltante a corrigir, não caso a esconder. Mocks só em fronteiras externas verdadeiras (rede, clock, filesystem), preferindo `tm/tv/tt`.
- **U14 — Python 3.13 + Pydantic boundary-only + PEP strict (inviolable).** Use only modern typing (builtin generics, `X | Y`, `type` statements, structural protocols; never `Any`/`object`). Every external owned payload is validated exactly once at its true ingress boundary with `model_validate(...)` or `model_validate_json(...)` into the canonical `m.*` model. From that point onward, layers pass the same validated model instance directly through `p.*` contracts. Internal `model_dump(...)` → `model_validate(...)` reconstruction, mapping/JSON copies, and repeated validation are forbidden. `model_dump(...)` / `model_dump_json(...)` are allowed only at a true external egress adapter. Model-less contracts (`dict`, JSON payload objects, `TypedDict`, `dataclass`) are forbidden. PEP 8/257/420 applies; prefer modern stdlib; use Google-style docstrings where adopted. Artifacts (code, comments, docstrings, logs, identifiers, `.j2` template output) are always in English. U2–U8 remain jointly inviolable.
- **U15 — Estrutura FLEXT strict, uma só forma, biblioteca produtiva (inviolável).** Os padrões estruturais FLEXT aplicam-se de forma strict em TODO pacote: facades canônicas `c/t/p/m/u` (+ operacionais `r/e/x/h/d/s` — `FlextResult/FlextExceptions/FlextMixins/FlextHandlers/FlextDecorators/FlextService` conforme a família define em `flext_core`), `api.py` como facade MRO fina sobre a classe composta, `cli.py`, `base.py` (base de serviço expondo o singleton `s` do projeto), `services/*` por MRO, privados `_constants/_models/_protocols/_typings/_utilities`, config/settings SSOT (U2). É PROIBIDO manter padrões alternativos ou branches paralelas de estrutura para a mesma responsabilidade — existe UMA forma canônica; a alternativa é removida no mesmo ciclo (U7). Cada biblioteca DEVE entregar COMPLETA na sua camada de responsabilidade: facades, utilitários e serviços funcionam plenamente, ponta a ponta, na responsabilidade que a camada possui — nada errado, incompleto ou "para depois" fica mantido. O código tem que ser PRODUTIVO: o que está errado ou incompleto é corrigido na origem até funcionar plenamente — nunca contornado, nunca maquiado.
- **U16 — Testes strict: funcionalidade real só pela interface pública (inviolável; espelha /flext-law §8 e UNIVERSAL_CORE Rule 22).** Testes provam O QUE o módulo faz pela sua interface PÚBLICA, nunca COMO ele é construído. Framework é `flext-tests` com aliases `t*` (`tm/tv/tt`) e modelos `Tests*`. Layout canônico e unificado: UM `conftest.py` unificado por projeto (nunca conftests espalhados), fixtures tipadas em `tests/fixtures/` sobre `c/t/p/m/u`, módulos de teste somente sob `tests/unit/`, `tests/integration/`, `tests/e2e/`. Cada módulo de teste é uma camada fina com UMA classe nested única por unidade pública testada (classe externa = unidade, classes internas = cenários), totalmente automatizada e a mais leve possível, contendo APENAS a lógica real do teste (arrange via fixtures padronizadas, act pela interface pública, assert do resultado observável). PROIBIDO fake, mock, `unittest.mock.patch` e `monkeypatch` da unidade testada em qualquer suíte — teste que finge verde é defeito grave: reescrito na raiz ou deletado. Se um comportamento não pode ser testado de verdade pela interface pública, a INTERFACE/arquitetura está errada — corrige-se o design, nunca a honestidade do teste. Assertions só na superfície pública (métodos de facade, modelos exportados, artefatos emitidos) — validar como o módulo é feito (atributos privados, contagem de chamadas internas, detalhes de ramificação) é proibido mesmo quando "conveniente". Código de teste é código FLEXT: importa e usa `c/t/p/m/u` exatamente como produção — sem `dict`/`Any` cru, sem bypass, sem payload model-less (U2–U8 valem em testes).

<!-- mro-gisf (agent: kimi) — U17 (facetas puras declaration-only + models só Pydantic 2-way) gravada por pedido vivo (2026-07-11); espelha /flext-law §1.14; não remover sem ADR + pedido do operador. -->
- **U17 — Pure declaration-only facets + boundary Pydantic models (inviolable; mirrors /flext-law §1.14; live operator order 2026-07-12).** `constants` (c), `typings` (t), `protocols` (p), `models` (m), `settings`, and `config` are purely declarative: helpers, functions, and concrete methods are forbidden, whether public or private (regex compilation, fluent builders, property accessors, static/class helpers). Behavior lives only in `u`/utilities, `cli`, `api`, `base`, and `services/*`; an abstract Protocol signature with `...` is declaration, not behavior. A model is defined only in the owning `models` facet and contains fields only, with zero custom methods, validators, computed fields, serializers, or private state. Validate once at the external boundary, then retain and pass the canonical model instance directly. Derived values are computed by a factory in `u` and stored as plain fields. Frozen models use immutable defaults (`tuple`/`frozenset`, never `list`/`dict`). `dict`/`TypedDict`/`NamedTuple`/`dataclass`/`SimpleNamespace`/typed JSON payloads are strictly forbidden as data structures or contracts in every internal layer; use the owning `m.*` Pydantic model and a corresponding `p.*` protocol.

<!-- mro-3o9s (agent: kimi) — U18 (config/settings como base SSOT consumida PELAS facetas) gravada por pedido vivo (2026-07-11); espelha /flext-law §2.0+§2.2+§2.3; não remover sem ADR + pedido do operador. -->
<!-- mro-i6nq.9 (agent: codex) — U18 validates once at singleton composition and forbids validation-on-access intermediaries. -->
- **U18 — config/settings are always the SSOT consumed by `c/t/p/m/u`, with zero intermediaries (inviolable; mirrors /flext-law §2.0+§2.2+§2.3; live operator order 2026-07-11).** Facets never re-derive, hardcode, or re-read sources (environment, files, defaults) already owned by `config` / `settings`. The only access form is `from <namespace> import config, settings`, followed by direct consumption of the fully loaded namespaced singletons (`config.<Project>.*` / `settings.<Project>.*`) for the project and all subprojects (U2). Every intermediary is forbidden and must be removed at the source in the same cycle (U7): no forwarding function/method/property, `@cached_property`, `config.X_config()`, pass-through getter, access wrapper, mapping subscript contract, proxy, importlib resolver, `self.*`, `u.*`, or MRO route. Config schemas live only in `_models/config.py`, which imports only Pydantic and declares nested domain models (`frozen=True, extra="forbid"`) plus `Root` (`frozen=True, extra="ignore"`). The `config.py` / `settings.py` composition boundary validates the complete loaded payload exactly once with `Root.model_validate(...)` while constructing the frozen singleton, and the package root exports those exact singleton identities without wrapping; access never triggers re-reading, per-slice revalidation, or a property/getter. A new config domain adds one nested `_models/config.py` model and one validated `Root` field, nothing else. A facet-owned duplicate of an SSOT value is a source defect. The singletons are composed only by the project's `config.py` and `settings.py` over private `_*/*.py` subclasses (`_constants/_models/_protocols/_utilities` for config/settings); those private foundation modules never import the project's `c/t/p/m/u` at runtime and may use them only under `TYPE_CHECKING`. Dependency direction is one-way: facets consume config/settings; config/settings never consume facets.

<!-- mro-d421 (agent: codex) — U19 records the live direct-object interface rule and removes internal model roundtrips. -->
- **U19 — Interfaces are model/protocol contracts and reuse source objects directly (inviolable; live operator order 2026-07-12).** Every owned interface argument, return value, property, event, and service dependency is a canonical `m.*` model exposed through a `p.*` protocol. Once a boundary validates an object, every downstream layer and subproject uses that same source object directly: no dump/revalidate roundtrip, mapping/JSON projection, adapter copy, duplicate DTO, forwarding model, or shadow schema. Reuse an upstream model/protocol as-is whenever its semantics are unchanged, composing behavior through MRO/OO. A project may declare a new model/protocol only when it adds a documented domain field, invariant, capability, or semantic adjustment that the source contract does not represent; name-only or package-local duplication is forbidden. JSON bytes/text may exist only momentarily at a true external adapter and must be validated immediately; JSON-shaped objects never cross an internal interface.

<!-- mro-j47u (agent: codex) — U20 records the operator's universal MRO/lazy/tooling contract. -->
- **U20 — MRO/OO, facade order, correct `TYPE_CHECKING`, and lazy public exports are universal invariants (inviolable; live operator order 2026-07-12).** Every project extends the canonical upstream aliases and owns nested namespaces in strict dependency order `c → t → p → m → u`; reverse edges exist only under `TYPE_CHECKING` when required by that order or a proven runtime cycle. Public objects are exported through the generated PEP 562 lazy map plus matching `TYPE_CHECKING` declarations; leaf code maximizes canonical namespaced aliases and never replaces this design with direct concrete imports or parallel facades. Generic lint/type defaults do not overrule the architecture. A diagnostic may be disabled globally only when a reproducible command proves that the specific tool cannot model this exact MRO/lazy construct, no project-side correction exists, the code is listed in the closed canonical tooling SSOT with an inline rationale, and the setting is propagated to every repository. Such exceptions are never generalized to adjacent codes, files, or real defects; per-file ignore hints remain forbidden.

<!-- mro-j47u (agent: codex) — U21 records the operator's supreme responsibility order. -->
- **U21 — Responsabilidade técnica total antes de qualquer mutação (inviolável; pedido vivo 2026-07-12).** Antes de editar, o agente compreende e prova o contrato completo, dono canônico, consumidores, superfícies geradas/deployadas, blast radius, cutover e validação real. Pressa, pressão, limite de contexto ou aparência de simplicidade NUNCA autorizam implementação simplista, parcial, opaca, descartável, especulativa ou não validada. Código, config, template, schema, documentação, migração e automação permanecem completos, produtivos, inspecionáveis e continuamente verdes. Placeholder/blob que esconde estrutura obrigatória, reescrita pela metade, teste/resultado fake, estado intermediário quebrado ou cutover antes de todos os consumidores serem provados é violação grave. Se a correção completa ainda não pode ser provada, PARAR, registrar evidência exata e perguntar — nunca improvisar nem correr.

<!-- BEGIN UNIVERSAL AGENT LAW (portable; regenerable; do not edit inside) -->

## Universal Agent Law (portable core)

This block references `~/.ai-hub/AGENTS.md` as the single source of truth for the universal cross-project law. The full detailed version lives in `~/.ai-hub/docs/agent-law-full.md`.

### Supreme Rule — Absolute Truth, Never Lie

Honesty at 100%, always, backed by real evidence. "I could not" is always acceptable.

### Supreme Law — Resolve, Never Hide

Fix every defect at the root in GitOps/source and verify green. No bypass, workaround, or suppression.

### Supreme Responsibility — Understand Completely, Then Change Safely

Research the full contract, consumers, generated surfaces, blast radius, and
real validation path before every mutation. Rushed, partial, simplistic,
opaque, fake, incomplete, or broken artifacts are forbidden.

### Core Rules (R0–R19)

- R0: Zero-tolerance for bypass/fallback/hardcode/stub. Fix root cause generically.
- R1: Fix-forward-only. Never `git checkout/restore/reset --hard/stash/revert` another's work.
- R2: Root-cause only. No TODOs, fakes, fallbacks, suppressions.
- R3: Stay in scope. No unrequested changes.
- R4: Evidence before claiming done (command + exit code + output).
- R5: Land your work — commit and push verified changes, no agent attribution.
- R6: Strict typing. No `Any`/bare `object`.
- R7: Bare commands only; no `.venv/bin/` prefixes.
- R8: Fix docs at the source.
- R9: GitOps is the only cluster-management channel.
- R10: Blocked operation protocol — STOP, diagnose, hand to user, wait.
- R11: Execute as planned, else stop and ask.
- R12: Production-readiness — every non-green is an incident.
- R13: Change accountability — atomic, impact/risk declared, no compat shims.
- R14: Dev/prod parity.
- R15: Bead ledger discipline — continuous status and evidence.
- R16: Operator-precedence + ask-when-unsure. A live operator/user request ALWAYS supersedes every bead, plan, ADR, skill, and doc; the strict precedence is **operator request > beads > ADRs > skills > docs**. When a request conflicts with any of these, the request wins and the conflicting artifact MUST be adjusted in the SAME cycle (update bead, edit ADR/plan/skill/doc, record SHA/evidence) — never refuse or defer a request by citing a lower artifact as authority. On ANY doubt or ambiguity, STOP and ASK the operator before acting — never guess or assume.
- R17: Law binds EVERY agent (subagents included, any depth). Every delegation prompt MUST embed the Supreme Rule, Supreme Law, R18, and the exact validation commands. A subagent violation is the coordinator's violation.
- R18: Continuous-green — tree importable/collectable at EVERY instant, not just mission end. Per edit batch (≤5 files): fresh-import smoke + `ruff --no-fix` + typecheck + scoped tests, all green before next batch. Facade/public member move/rename/removal updates ALL consumers (grep-proof, workspace-wide) in the SAME batch. Broken import/collection = active incident: stop everything, fix first.
- R19: Supreme responsibility — understand and prove the complete contract and all consumers before mutation; never rush or land partial, simplistic, opaque, fake, incomplete, or broken work.

### Context-Economy Directive

Do not restate these rules. Prefer targeted tool calls and `make` verbs.

<!-- END UNIVERSAL AGENT LAW -->

## Scope and authoritative sources

1. User request (highest)
1. `AGENTS.md` (this file)
1. `~/.claude/AGENTS.md`
1. `.agents/skills/*/SKILL.md`

`AGENTS.md` below is the operational summary for the monorepo. Detailed mechanics live in SKILL docs.

## Quick execution flow (per task)

1. Confirm active bead/issue and ownership with `bd ready` and `bd show <id>`.
1. Read the relevant local scoped SKILL docs before editing.
1. Run the narrowest smell/quality discovery first (`qlty`, `rg`, `sg`, or `scope` as available).
1. Reuse canonical origin before creating helpers/abstractions.
1. Make the minimal fix, then run the first local validation gate.
1. Update impacted callers in the same cycle.
1. Record evidence and next step in Beads before any handoff.

Any unresolved blocker at step 6 keeps the change incomplete.

## Non-negotiables

- Do not introduce bypasses, shims, fallbacks, compat aliases, or pass-through wrappers.
- No ad-hoc helper inflation without proving the canonical owner is missing.
- No broad edits outside the active lane.
- Do not edit `.beads/*.jsonl` manually.
- Prefer `make`/`ruff`/`pyrefly` workflows over one-off scripts for broad refactors.
- If a command is blocked or ambiguous, stop and surface evidence instead of inventing a workaround.

## FLEXT architecture constraints (compact)

### Stack and style

- Python 3.13+, Pydantic v2, Ruff, Pyrefly, Pyright, Mypy, Make.
- Follow MRO namespace classes and project facades (`c/m/t/p/u`, etc.).
- One canonical class/namespace owner per concern before adding new constructs.
- Prefer composing via MRO + mixins over duplicate utilities.

### Naming and contracts

- Keep aliases canonical: `c`, `m`, `t`, `p`, `u`, and operational aliases (`r`, `e`, `s`, `x`) from project facades.
- Facade owner modules that extend upstream FLEXT facades by MRO import the upstream short alias and use it as the base class, then rebind the local public alias at the bottom, e.g. `from flext_cli import m, u`; `class FlextPluginModels(m): ...`; `m = FlextPluginModels`.
- Project `base.py` may import upstream runtime `s` as the service base and rebind local `s` once, e.g. `from flext_core import s`; `class FlextDbOracleServiceBase(s, FlextDbOracleUtilitiesDbOracle): ...`; `s = FlextDbOracleServiceBase`.
- Project `api.py` stays a thin MRO facade over the composed runtime class and publishes the package operational alias, e.g. `class FlextDbOracleApi(FlextDbOracleApiRuntime): ...`; `db_oracle = FlextDbOracleApi`.
- Use `r[T]` for fallible app paths (avoid ad-hoc error dicts or raw exceptions for control flow).
- Keep `__init__.py` as export-only.
- Keep abstractions layered by project boundaries (`src` first, tests/examples/scripts are consumers).

### API/runtime constraints

<!-- mro-wkii.17 (agent: codex) — validate once at the external CLI boundary and preserve object identity. -->
- The `flext-cli` boundary validates dynamic external arguments exactly once into the canonical `m.*` request; internal services receive that same object through its `p.*` protocol.
- Avoid raw `os.environ` in `src/` runtime; go through settings abstractions.
- Do not import abstracted framework libs directly from consumer projects; use FLEXT abstractions.
- Reject speculative architecture migration without a concrete blocker and a scoped acceptance target.

### Config / parametrization SSOT (ADR-005)

- Five concerns, one owner each: `constants` = defaults/invariants (`c.*`); `config/` = execution parametrization; `settings` = env-override (`FlextSettings`); `templates/*.j2` = large strings (Jinja2 via `flext-cli`); sibling `schemas/*.schema.json` = validation.
- Execution parametrization lives **only** under a package `config/` dir; no schema/config source outside it.
- `config` ≠ `settings`: the settings-bound subset is a separate file (`config/settings.yaml`).
- Large/derived structures are **generated** by `_constants/_generated.py` from `config/`; hardcoding a large structure in `_constants/` is a blocked defect.
- **Enforcement rules are DATA, not code (LAW1):** 100% of static enforcement rules live ONLY under `flext-infra/config/*.yaml` as Pydantic-2-validated records — zero rule logic in Python (no bespoke per-rule detector classes, no `ClassVar` banned/allowlist rule tables). `flext-core` holds runtime/beartype rules only. Engine = a rope-semantic fact base + a closed operator set, both in `u.Infra` (models stay pure data, zero methods).
- **Static enforcement is rope-semantic ONLY (LAW2):** use rope's semantic model (`get_scope`/`get_defined_names`/`get_attributes`/`get_superclasses`/`PyName`); `import ast`, `ast.parse`, `ast.walk`, `ast.Module`, and `PyModule.get_ast()`/`walk_ast_nodes` are BANNED in the enforcement path. The ast-grep MCP is allowed only as a read-only navigation sensor under the newest operator order; it never owns rules, fixes, or acceptance.
- Layering (no runtime cycle): `flext-core` runtime-minimal (stdlib only, no Jinja2, never imports cli/infra at runtime) — owns ONLY runtime/beartype rules → `flext-cli` owns the universal template/config/schema engine → `flext-infra` enforces (all static rules as config data, evaluated by the rope-semantic engine).
- Canonical: [`docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`](docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md) · plan [`docs/architecture/config-ssot-migration-plan.md`](docs/architecture/config-ssot-migration-plan.md) · beads `mro-wkii`.

### Strict typing, import layering, config access (R16 — inviolable)

- **Typing**: never `Any`/`object`; never annotate with a concrete class. Use `t.*` aliases and `p.*` protocols; composite types use a `t.*` alias with `| None` on the **outside** (`t.Foo | None`). Import `p` and `m` under `TYPE_CHECKING` to sharpen typing (protocol modules import `m` under `TYPE_CHECKING`).
- **No loose helpers / no compat aliases**: no standalone functions or compatibility shims; everything flows through `c/t/p/m/u` composed by MRO.
- **Import order** strict `c → t → p → m → u`: a later facade may import earlier ones at runtime; the reverse (earlier importing later, e.g. `c` importing `m`) must be `TYPE_CHECKING`-only. `m` may lazy-import `c`; internal modules may, with extreme care, import a sibling directly only to break a real cycle.
- **Config/settings access is single-form**: always `from <namespace> import config, settings` then `config.<Ns>.*` / `settings.<Ns>.*` (e.g. `from ai_hub import config, settings` → `config.AiHub.*`). Namespace fields are validated nested models, never model-less mappings. Every package root exports its exact namespaced singleton directly; MRO, proxies, instance attributes, forwarding members, and access wrappers never transport config/settings.
- **Edit-coordination comment**: when editing a file, add a short inline comment explaining the change *for the other agent* so concurrent agents don't conflict or re-revert each other.

## Project map

- Governed packages: `flext-*`.
- Root docs and onboarding: `docs/`.
- Shared tests: `tests/` and project-local `tests/` trees.
- Scripts/tools: `scripts/`, `workspace_custom.mk`, top-level `Makefile`.

## Build, test, and local dev commands

```bash
make help
make boot
make check
make check PROJECT=<proj> CHECK_GATES=<gates>
make test PROJECT=<proj> MATCH=<expr>
make docs DOCS_PHASE=<generate|fix|audit|build|validate> PROJECT=<proj>
make val VALIDATE_SCOPE=workspace
make ship WHAT=<save|tag|push|pr|rel>
```

Common gate values: `lint`, `format`, `pyrefly`, `mypy`, `pyright`, `markdown`, `go`, `loc-cap`, `boundary`, `coordination`.

Recommended baseline for contribution work:

- `make check CHANGED_ONLY=1`
- `make test PROJECT=<proj> MATCH=docs`
- `make val VALIDATE_SCOPE=workspace`

## Testing and quality gates

- `ruff` and `pyrefly` are the first gates for touched files.
- For project-level contract changes, run project-local checks before wider propagation.
- Keep failure evidence in Beads: command, output, and exit code.

### Safe validation before production (universal)

- Validations and tests must be REAL — they execute the actual code path — yet
  must never mutate the active workspace or environment. Anything that would
  write outside the bead lane runs in an isolated sandbox (`pytester`,
  `tmp_path`, temp-dir synthetic packages); evidence artifacts under
  `.beads/artifacts/` are the only permitted side effects.
- Activating a behavior/enforcement change as the workspace or production
  default is a SEPARATE, explicit final gate: allowed only after the full
  validation chain (unit + E2E + read-only baseline) is green with recorded
  evidence — never in the same edit that introduces the change.

## Commit and PR behavior

- Default profile is land-immediately: after scoped green validation, stage only
  the active bead lane files, commit, push fast-forward, and record SHA/evidence
  in Beads.
- The operator grants durable authorization for normal scoped `git add`,
  `git commit`, and fast-forward `git push`; do not stop at “needs
  authorization” for routine landing.
- Never use `git add .` in the shared worktree. Use explicit pathspecs and
  coordinate overlaps through Beads before staging.
- Escalate only destructive, non-fast-forward, history-rewrite, rollback, or
  cross-lane ambiguity. A dirty worktree outside the bead is not a blocker when
  explicit pathspecs can isolate the lane.
- PRs/commits should state: scope, why, commands run, and remaining risk.

## Tooling and agent workflow (ECC alignment)

- Use repository skills: `.agents/skills/*` and `gd`/`scope`/`sg` where available.
- `make` is the canonical execution lane; avoid direct `git`-wide scripts when a Make target exists.
- FLEXT participates in the `~/.ai-hub` distributed workspace base: `make cosmos-help` exposes dispatcher verbs; the common base is maintained from `~/.ai-hub` via `make workspaces WHAT=distribute APPLY=1`.
- Bead system (`bd`) is the mandatory work ledger.
- Agent lanes (Claude, Codex, Gemini, and their subagents) claim work via `bd` (epics/tasks), keep child beads for disjoint scopes, and record evidence in bead notes rather than chat-only state.
- Subagents write verbose findings to disk (`coordination/resultados/` or `.beads/artifacts/`) and update `bd` only with filepath and status.
- Repeated cross-file edits require caller/audit validation before marking done.

## Verification expectation

A task is complete only with:

- objective command evidence (command + exit code + output),
- a scoped commit and fast-forward push, with SHA recorded in Beads,
- no unresolved scoped smells in the touched lane,
- bead notes updated with blocker status or completion evidence.
