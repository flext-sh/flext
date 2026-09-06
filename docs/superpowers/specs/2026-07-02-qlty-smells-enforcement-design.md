# qlty Smells → FLEXT Enforcement (detection-only, warnings para todos, sempre)

## Context

`qlty smells --all --sarif --include-tests` reporta **1386 findings / 8 tipos** no workspace
(similar-code 697, function-parameters 248, function-complexity 181, file-complexity 103,
return-statements 80, nested-control-flow 36, identical-code 24, boolean-logic 17). Hoje: zero
integração qlty (só `parse_smells.py` ad-hoc na raiz), todas as regras ruff de complexidade
globalmente ignoradas no SSoT (`tool_config.yml`), nenhuma métrica de função no flext-infra.

Objetivo: cada tipo de smell vira violação de arquitetura FLEXT com **detecção totalmente
automática** (flext-core enforcement runtime + flext-infra gate), **warnings não-supressíveis
para TODOS os tipos, SEMPRE**, com solução FLEXT-law por tipo
(MRO/OO/YAGNI/KISS/SOLID/CA/DI/PEP8/Py3.13/Pydantic2). Detecção via introspecção beartype-style
(runtime) + SARIF do scanner Rust qlty (gate) — zero walkers re/ast artesanais. Sem aumento de
erro de lint; testes 100% verdes.

## Decisões travadas (usuário)

1. **Detection only** — correções viram beads (não corrigir os 1386 nesta iteração).
2. **Gate (flext-infra) + runtime (flext-core)** — dupla camada.
3. **Report-only → flip** — gate exit 0 agora; flip para STRICT = 1 constante.
4. **"Warnings para todos, sempre"** — TODO finding de TODO tipo emite warning em TODA execução
   de detecção. Modo report-only afeta só exit code, NUNCA a emissão de warnings. Sem exclusões
   de scaffolding no qlty.toml (tudo reportado); sem threshold de silêncio.

## Verificado por exploração (base factual)

- flext-core enforcement é 100% table-driven: `PREDICATE_BINDINGS`
  (`_utilities/_enforcement_parts/enforcement_part_01.py:37-198`), 47 tags
  (`_constants/_enforcement_parts/flextconstantsenforcement_part_04.py:61-109`), textos
  (problem,fix) em `ENFORCEMENT_RULES_TEXT` (part_05), catálogo por row-tables
  (`_enforcement_catalog_rows_parts/`), emit em `enforcement_emit.py:64-90` via
  `warnings.warn(FlextMroViolation)`.
- IDs livres: **ENFORCE-071..078** (056 aposentado, não reusar; 022/040 inline em
  `enforcement_part_04.py`; **066..070 ocupados por trabalho concorrente em andamento** — regras
  runtime compat-alias/one-class-per-module/private-bypass/deep-namespace/library-abstraction).
- **COORDENAÇÃO (2026-07-02):** agente concorrente ativo em flext-core enforcement (11 arquivos
  dirty). Sequência ajustada: flext-infra primeiro (sem overlap de arquivos), flext-core quando
  a árvore assentar. Todos os IDs `ENFORCE-067..074` deste documento leem-se como
  `ENFORCE-071..078` (071 = smell_function_parameters runtime; 072..078 = CODE_SMELL delegado).
- Gate novo flext-infra = subclass `FlextInfraGate` (template `gates/loc_cap.py`) + row em
  `SARIF_TOOL_INFO` (`_constants/check.py:25-46`, `ALLOWED_GATES` deriva) + registry
  (`check/workspace_check_gates.py:30-41`).
- `qlty smells` default = changed-files-only; full scan exige `--all`. SARIF:
  `runs[0].results[].ruleId "qlty:<type>"`.
- LOC caps: `enforcement_part_01.py` JÁ está a 210 (>200) — resplit obrigatório ao tocar;
  constants part_05 (183) transborda com 8 textos — resplit via `make gen`.
- `flext-oracle-wms/pyproject.toml:406-411` é o ÚNICO projeto com
  `filterwarnings=["error",...]` — warnings de import-time viram erro de collection lá.
- `tests/unit/test_public_api_contract.py` + `_golden_public_api.json` quebram com qualquer
  constante pública nova — atualizar no mesmo batch.
- `enforcement_emit.py:32` faz `c.ENFORCEMENT_RULES_TEXT[tag]` — binding sem texto = KeyError em
  class-creation (crash de import). Texto+binding SEMPRE no mesmo commit.
- flext_infra já importa flext_core (35 arquivos) — textos SSOT no core, infra importa. Sem
  ciclo.

## Arquitetura

### A. flext-core — runtime + SSOT de regras (ENFORCE-067..074)

**Novos dados (CONSTANTS-FIRST, tudo row-driven):**

- `EnforcementSmellTag(StrEnum)` — 8 membros
  `smell_function_parameters, smell_function_complexity, smell_file_complexity,
  smell_return_statements, smell_nested_control_flow, smell_boolean_logic, smell_similar_code,
  smell_identical_code` (part_01).
- `ENFORCEMENT_SMELL_THRESHOLDS: MappingProxyType[EnforcementSmellTag,int]` = {params:5, returns:5,
  nesting:4, function_complexity:14, file_complexity:49} — semântica documentada
  `violação quando observado > max` (reproduz qlty ≥15/≥50). +
  `ENFORCEMENT_SMELL_RULE_IDS: frozenset` ENFORCE-067..074 (part_04).
- 8 rows (problem, fix) em `ENFORCEMENT_RULES_TEXT` (part_05 → **resplit via make gen**, 183/200).
  Textos FLEXT-law por tipo:
  - `smell_function_parameters`: fix CONTEXTUAL — single caller → inline; option bag verdadeiro →
    UM `m.<Domain>Spec` via `model_validate(kwargs)`; API pública fixed-shape → mantém params
    tipados explícitos. "Criar params model só para calar a regra é ABOMINABLE."
  - `smell_function_complexity`: decomposição OO — extrair passos coesos em métodos de mixin
    MRO/facade aninhada; `match-case` + dispatch `MappingProxyType`; combinadores `r[T]`.
  - `smell_file_complexity`: part-split via `make gen`; grupos coesos → mixins `_parts/` compostos
    root-most via MRO; ≤200 LOC lógicas.
  - `smell_return_statements`: railway — colapsar escadas de return em cadeias `r[T]`
    (map/flat_map/match); guard-clauses só no head.
  - `smell_nested_control_flow`: early returns/guards + `r[T]`; pirâmides loop+if →
    comprehensions/dispatch tables.
  - `smell_boolean_logic`: predicado nomeado (`@staticmethod`/`@computed_field`); or-chains de
    igualdade → membership `StrEnum`/`frozenset`; escadas booleanas por tipo → `match-case`.
  - `smell_similar_code`: composição MRO mixin no projeto root-most (flext-core > flext-cli/infra
    > consumers); abstração nova exige prova ≥8× LOC dedup; scaffolding codegen conserta-se no
    TEMPLATE do gerador.
  - `smell_identical_code`: deletar toda cópia exceto a root-most; re-exportar via facade dona.
    Tolerância zero.
- Catálogo: novo source kind `CODE_SMELL` (`EnforcementSourceKind` em
  `_models/_enforcement/_base.py:83-93`) + `EnforcementSmellSource(kind, smell, threshold)`
  (`_sources.py`) + braço na union (`_catalog.py:22-31`). NOVA part
  `flextconstantsenforcementcatalogrows_part_05.py` (via make gen) com `SMELL_ROWS` 7 rows
  ENFORCE-068..074; **description/notes construídos a partir de
  `ENFORCEMENT_RULES_TEXT[tag]`** (SSOT, sem duplicar texto). ENFORCE-067 vai em `BEARTYPE_ROWS`
  (part_04, headroom OK) — mesmo batch do binding.
- `build_canonical_catalog` (`enforcement_part_04.py`): comprehension `smell_specs` sobre
  `c.SMELL_ROWS`.

**Warning class:** `FlextSmellViolation(FlextMroViolation)` em `_constants/enforcement.py` (após
L36) + `FlextExceptions.SmellViolation` ClassVar (`exceptions.py:39`) + exports via `make gen`
(root exports/typing parts/`__init__.pyi` — set gerado atômico). `emit()`
(`enforcement_emit.py`): categoria = `FlextSmellViolation` quando
`rule_id in c.ENFORCEMENT_SMELL_RULE_IDS`, senão `FlextMroViolation`; estender derivação
`_BEARTYPE_TAG_TO_RULE`/anchor para rows CODE_SMELL
(warning sempre carrega ENFORCE-NNN + anchor + Fix).

**Predicate runtime `smell_function_parameters` (ATIVO — "todos, sempre"):**

- SEM predicate kind novo: estender `MethodShapeParams += max_params: int = 0`
  (`_params.py:116-121`) + branch em `v_method_shape`
  (`_utilities/_beartype/method_visitor.py`): `inspect.getattr_static` + `__code__.co_argcount +
  co_kwonlyargcount` − offset self/cls (staticmethod 0, função/classmethod 1). Introspecção pura de
  code-object — beartype-style, zero leitura de source.
- Exemptions LEGAIS (lei AGENTS.md, não silenciamento): dunders (`__*__`) e espelhos da API
  Pydantic (`model_*` — model_dump=13 espelha assinatura da lib, sem fix sancionado).
- Binding row `"smell_function_parameters": (pk.METHOD_SHAPE, msp(max_params=c.ENFORCEMENT_SMELL_THRESHOLDS[...]))`
  em `enforcement_part_01.py` (**resplit obrigatório: já a 210 LOC**). Iterator: ampliar
  `case "no_accessor_methods" | "smell_function_parameters":` em
  `enforcement_collect_part_02.py:72`. Categoria NAMESPACE em part_04.
- **Mitigação flext-oracle-wms (único projeto `filterwarnings=["error"]`):** adicionar row
  `"default::flext_core.FlextMroViolation"` ao filterwarnings dele — warnings ficam VISÍVEIS
  (não suprimidos; alinha com semântica workspace ENFORCEMENT_MODE=WARN; "error" local contradiz
  o design WARN do core). Verificar resolução lazy do path da classe no parse do filtro.
- Demais 7 smells: catalog-only no runtime (impossível introspectar complexidade/clones em
  class-creation sem source) — warnings deles fluem SEMPRE pelo gate (canal B). Cobertura "todos,
  sempre" = união dos dois canais.

**Não-supressibilidade:**

- Guard test `test_enforcement_warning_visibility.py`: probe adicional `FlextSmellViolation`;
  assert presença no output do pytest sandboxed com filterwarnings reais.
- Contrato subclass em `test_enforcement_reports.py`: `issubclass(FlextSmellViolation,
  FlextMroViolation)` — umbrella herdado.
- `ensure_pytest.py`: sem mudança (MERGE só adiciona ignore de PytestCollectionWarning; nunca
  cala UserWarning descendants).

### B. flext-infra — gate `smells` (qlty SARIF, report-only, warna sempre)

- **NOVO** `gates/smells.py` (~95 LOC, template loc_cap.py): `FlextInfraSmellsGate` —
  `gate_id="smells"`, `can_fix=False`.
  - Resolver binário explícito: `shutil.which("qlty")` + fallback `Path.home()/".qlty/bin/qlty"`
    (constante). **Ausência = Issue visível severity NOTE/ERROR, nunca false-green**
    (base_gate._run mascara spawn-failure como exit 1/stdout vazio — tratar).
  - cwd = workspace root (config SSOT em `<workspace>/.qlty/`; projetos são submodules) — novo
    hook template `_check_cwd()` em `base_gate.py` (+7 LOC, default project_dir, zero mudança nos
    10 gates existentes); comando
    `[QLTY_BINARY, "smells", "--all", "sarif", "--include-tests", "--no-snippets", "--quiet", "--no-upgrade-check", <project_dir.name>]`.
  - `_issues_from_sarif` classmethod PURO (testável com fixture literal): `u.Cli.json_parse` →
    `runs[0].results[]`; `ruleId "qlty:<type>"` → `Issue.code`; uri prefix-stripped; mensagem
    enriquecida = `"{sarif_text} — {problem}. Fix: {fix} [ENFORCE-NNN §anchor]"` via
    `c.Infra.SMELLS_RULE_TAGS` (ruleId→tag) + `from flext_core import c as c;
    c.ENFORCEMENT_RULES_TEXT[tag]` — **SSOT de textos = flext-core, infra só mapeia** (drift
    test).
  - **"Todos, sempre":** após parse, `warnings.warn(issue.formatted, FlextSmellViolation,
    stacklevel=2)` por finding — warnings emitidos em TODA execução do gate, independente do modo.
  - `passed = True` em `GateMode.WARN`, `not issues` em STRICT; severity WARNING→ERROR no flip.
- Constantes (`_constants/check.py`, +~30 LOC): `GateMode(StrEnum)` WARN/STRICT;
  `SMELLS_GATE_MODE = GateMode.WARN` (**flip = esta linha**); `QLTY_BINARY`,
  `QLTY_BINARY_FALLBACK`, `SMELLS_QLTY_ARGS`, `SMELLS_RULE_PREFIX`, `SMELLS_RULE_TAGS`
  (MappingProxyType 8 rows); row
  `SARIF_TOOL_INFO["smells"] = ("Qlty Smells", "https://docs.qlty.sh/analysis/smells")`.
- Wiring: import + row em `GATE_CLASSES`; `make gen` p/ export maps; `base.mk` — adicionar `smells`
  ao allowlist CHECK_GATES (L293-294), help (L226) **e ao default gate string (L298)** — detecção
  automática em todo `make check`/CI desde já (exit 0 em WARN). Relatórios por tipo grátis via
  `.reports/check/check-report.{md,sarif}` (agrupamento por `issue.code` já existe).
- `.qlty/qlty.toml`: **SEM excludes de scaffolding** (todos, sempre — tudo reportado), sem override
  de thresholds (baseline 1386 = defaults). Raiz-causa do scaffolding = 1 bead de centralização no
  codegen.

### C. Cleanup (pressão net-LOC + higiene)

Arquivar (mv, nunca rm — política global) para `.reports/archive/qlty-legacy/`: raiz
`parse_smells.py, qlty_results.json, smells.json, repo_smells.sarif, prompts_smells.sarif,
flext_ldif_constants_smells.sarif`; flext-core
`parse_smells.py.bak, smells.json.bak, smells.sarif.bak, smells_output.txt.bak, qlty_out.txt.bak,
qlty_output.json.bak, qlty_output.txt.bak, qlty_results.sarif.bak, parse_sarif.py.bak.bak`;
flext-cli `qlty_smells.txt.bak`. O gate substitui `parse_smells.py`.

### D. Beads (correções futuras + governança)

- 8 beads de fix por categoria (prefixo `mro-`), cada um com a solução FLEXT-law do tipo +
  contagem/projetos do SARIF.
- 1 bead: centralizar scaffolding codegen (`__version__.py` ×30, `tests/base.py` ×28,
  `_exports.py` ×14, `_parts/__init__.py`) via shared imports no gerador.
- 1 bead: flip STRICT — bloqueado por: fixes zerados + provisionamento qlty em CI + entrada em
  PRE_COMMIT_CONFIG + sanity assert de contagem não-zero workspace (proteção contra drift de
  descoberta de submodules do qlty).
- 1 bead: enriquecer `rope_inventory._record` com param_count/return_count/nesting/complexity em
  `m.Infra.Census.Object` (substrato rope p/ verbos de autofix da iteração de fixes — YAGNI agora,
  requisito lá).

## Sequenciamento (R18: batches ≤5 arquivos, gates verdes por batch)

**flext-core primeiro (SSOT), depois flext-infra (drift test depende), depois make/cleanup/beads.**

1. **B1 constants (5):** part_01 (+EnforcementSmellTag), part_04 (+categoria, thresholds,
   rule-ids), part_05 (+8 textos → make gen resplit), NOVA catalog rows part_05,
   `enforcement_catalog_rows.py` (compor 5º parent). Inerte (binding ausente → sem mudança de
   comportamento).
2. **B2 warning class (3 + regen):** `_constants/enforcement.py` (FlextSmellViolation),
   `enforcement_emit.py` (categoria por rule-id + derivação anchor p/ CODE_SMELL), `exceptions.py`;
   `make gen` (set gerado atômico); atualizar `_golden_public_api.json`.
3. **B3 catálogo (4):** `_base.py` (+CODE_SMELL), `_sources.py` (+EnforcementSmellSource),
   `_catalog.py` (union), `enforcement_part_04.py` (smell_specs). Teste kind-coverage verde dentro
   do batch.
4. **B4 runtime params (5):** `_params.py` (+max_params), `method_visitor.py` (branch introspecção),
   `enforcement_part_01.py` (binding + **resplit make gen**, já 210 LOC),
   `enforcement_collect_part_02.py` (case widening), catalog rows part_04 (row ENFORCE-067
   BEARTYPE — mesmo batch, senão KeyError no builder). **Pré-scan:** `python -W default -c "import
   flext_core, flext_cli"` contando FlextSmellViolation; **canário:** pytest flext-oracle-wms +
   flext-ldif.
5. **B5 oracle-wms (1):** row `"default::flext_core.FlextMroViolation"` no filterwarnings de
   `flext-oracle-wms/pyproject.toml`. Canário pytest de novo.
6. **B6 testes core (5):** `test_enforcement_catalog.py`, `test_enforcement_apt_hooks.py`,
   `test_enforcement_accessors.py`, `test_enforcement_warning_visibility.py`,
   `test_enforcement_reports.py` (asserts conforme design: contagem by_kind, thresholds alinhados,
   binding contract, probe visibilidade, pytest.warns(FlextSmellViolation), negativos
   *args/dunder/5-params, cls/staticmethod offsets).
7. **B7 infra base (2):** `gates/base_gate.py` (_check_cwd hook), `_constants/check.py`
   (constantes + SARIF_TOOL_INFO row).
8. **B8 infra gate (4 + regen):** `gates/smells.py`, `workspace_check_gates.py` (registry), NOVO
   `tests/unit/check/smells_gate_tests.py` (identity, fixture SARIF pura, warn-mode passa com
   issues, binário ausente visível, drift test tags→textos core, warning emission),
   `gate_registry_tests.py` (+2 asserts); `make gen`.
9. **B9 não-Python:** `base.mk` (allowlist+help+default), cleanup mv, smoke `make check
   CHECK_GATES=smells` na raiz → exit 0 + contagens por tipo no report + warnings no stderr.
10. **B10 beads:** criar os 11 beads via `bd create`.

## Verificação (por batch, DIRETO via ~/flext/.venv — NUNCA make check)

- Baseline ANTES (salvo em scratchpad): `ruff check src tests` (contagem), `pyrefly check` (0),
  `pytest -q` (contagens) para flext-core e flext-infra.
- APÓS cada batch: ruff ≤ baseline (alvo igual), pyrefly 0, pytest 0 falhas novas.
- Canários cross-project após B4/B5: `pytest -q` em flext-oracle-wms (único "error"-filter) e
  flext-ldif (Entry.create=20).
- Smoke E2E final: `make check CHECK_GATES=smells` → relatório `.reports/check/check-report.md`
  com breakdown por tipo; warnings FlextSmellViolation visíveis.
- **Fallback documentado:** se canários B4/B5 revelarem vermelho não-consertável dentro da
  iteração, reverter APENAS o binding row (B4 parcial — mecanismo permanece, testado por unit com
  params diretos) e converter ativação em bead bloqueado pelos fix-beads de assinatura. Warnings de
  function-parameters continuam SEMPRE via gate (canal B) — cobertura "todos, sempre" preservada.

## Riscos aceitos

- Net LOC do feature ≈ +320 core/infra vs −80 código + artefatos arquivados — aumento autorizado
  pelo pedido explícito de incremento de enforcement (regra global exige autorização: este plano
  é a autorização registrada).
- Flood de warnings em import (intencional — "todos, sempre"); único quebra-testes conhecido
  (oracle-wms) tratado em B5.
- qlty externo: ausência do binário = Issue visível; provisionamento CI = pré-requisito do bead de
  flip.
- Drift de schema SARIF do qlty: parser puro + fixture pinada 0.632.0.

## Passo 0 (pós-aprovação)

Escrever spec em `docs/superpowers/specs/2026-07-02-qlty-smells-enforcement-design.md` (conteúdo
= este plano) + commit; criar bead master da iteração (`bd create`) antes de codar.
