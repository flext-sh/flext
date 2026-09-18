# Rope Modernize Engine — Migração Unificada + Extermínio ast/re/libcst + Saída do Motor Estático de flext-core

## Contexto e regras raiz

- **Lei de data contract** (AGENTS.md): sem `dict`/`TypedDict`/`dataclass`/`NamedTuple`
  como contrato — só `m.*` (Pydantic-2), `p.*`, `r[T]`.
- **Dono canônico de enforcement**: `flext-infra` (build/tooling, nunca runtime).
  `flext-core` é fundação: zero tooling estático.
- **Superfície única de execução**: `make mod` → `FlextInfraCodemodBatchApply` (loop
  fix-forward: ast-grep cascade + sed-by-list (`text_rules.yml`) + fases rope
  (`FlextInfraCodemodSemanticApply`), ponto fixo por fingerprint, dry-run nativo).
- **Diretriz do operador**: exterminar transformadores baseados em `re`/`ast`/`libcst`;
  migrar para (a) fases rope semânticas e (b) rules parametrizadas
  (`codemod/rules/*.yml` + `utils/` guards + fixtures `tests/`); manter beartype
  **runtime** (claw) em flext-core; **migrar o desvio de validação estática AST do
  beartype para flext-infra e removê-lo totalmente de flext-core**.
- **Cobaia**: `ai-hub` (37 dataclasses mapeados: 6 conversíveis → `m.FrozenModel`, 30
  skips catalogados com razão exata). Modo fix-forward adopt (WIP paralelo de outros
  agentes é adotado, nunca revertido).
- **Gates por ciclo**: ruff, pyrefly, mypy, coleta pytest — 100% verdes em cada
  incremento; nada pela metade.

## Arquitetura-alvo (UM loop, UM CLI)

```
make mod [dry-run] / flext-infra refactor mod
├── fase 1: ast-grep cascade   (rules parametrizadas: codemod/rules/*.yml, utils/, tests/)
├── fase 2: sed-by-list        (text_rules.yml, com receipt de contagem exata)
├── fase 3: fases rope         (SemanticApply: future-annotations, class-nesting,
│                               deferred-models, compat-alias, private-import,
│                               + NOVAS: dataclass-modelizer, pydantic-modernizer,
│                                       static-enforcement (ex-beartype AST))
└── ponto fixo (fingerprint) → gates (ruff/pyrefly/mypy/pytest) → publicação atômica
```

Toggles de componentes: estender o input model do `mod` (`m.Infra.ModScanReport`/batch)
com seleção de fases (`phases: [...]`, default todas) — dry-run já existe
(`effective_dry_run`). Callbacks já existem (`SemanticMigrationEdit` + `_apply_plan`);
novas fases seguem o mesmo contrato.

## Workstreams (ordem de execução)

### W1 — Migrar motor estático de flext-core → flext-infra (EXTERMINAR de flext-core)

1. Inventariar em flext-core: `FlextUtilitiesBeartypeEngine` + `_utilities/_beartype/*`
   (visitors AST: attr/class/field/method/module/import/deprecated + helpers) + rows
   estáticas de `FlextConstantsEnforcement*` (ENFORCE-039/041/043/044, catálogo de
   reescrita tipo `get_beartype_conf→build_beartype_conf`).
2. Para cada row/check estático: expressar como rule parametrizada ast-grep
   (`codemod/rules/ban-*.yml` + fixture `tests/`) ou sed-by-list. Já existem
   equivalentes (`ban-model-rebuild.yml` ≙ ENFORCE-041) — deduplicar, não duplicar. Rows
   puramente de dados (sentinelas de nomes/path) viram valores parametrizados nas rules
   ou `config/` de flext-infra.
3. Rope não é necessário aqui (padrões mecânicos AST→ast-grep cobre). O gate `check` de
   flext-infra passa a validar as mesmas regras pelo loop `mod`.
4. Remoção total em flext-core: deletar `beartype_engine.py`, `_beartype/`, rows
   estáticas do enforcement, e rewiring de consumidores (importar de flext-infra via
   facade `u.Infra`/gates — nunca private import). **Mantém** em flext-core:
   `_beartype_bootstrap.py` (claw runtime), `beartype_conf.py`,
   `beartype_typingext_patch.py`, constantes `BEARTYPE_MODE`/`EnforcementMode` (config
   runtime).
5. Consumidores de runtime que usavam o engine estático em flext-core (se houver em
   services/utilities): rewire para não depender de validação estática em runtime.

### W2 — dataclass → `m.FrozenModel` como fase rope (exterminar meu transformer ast/re)

1. Criar `u.Infra.plan_dataclass_modelizer_cutover(rope_workspace=…, sources=…)` (padrão
   de `plan_class_nesting_cutover`): classifica cada `@dataclass` (frozen? campos
   serializáveis str/int/float/bool/None/Path? sem `__init__`/`__post_init__`? sem
   keywords order/unsafe_hash?) → reescreve header p/ `m.FrozenModel`, remove decorator,
   rewiria `m` no import de fachada existente (`from <pkg> import c, m, p…`) — regra
   determinística já validada; fallback `from flext_core import m`.
2. Nova fase `dataclass-modelizer` em `FlextInfraCodemodSemanticApply.apply()` +
   `_check_residue` + `_verify_fixed_point`.
3. **Exterminar** `transformers/dataclass_modelizer.py` (ast/re), a rota CLI
   `modernize-dataclass` que criei hoje e seu registro — bypass do loop único é
   violação.
4. Skips não conversíveis (30 no ai-hub: `os.stat_result`, mutáveis, `__post_init__`)
   ficam catalogados no relatório da fase, não viram silêncio.

### W3 — Extermínio dos demais transformadores ast/re/libcst

Inventário (11 arquivos): `pydantic_modernizer` (ast), `typing_unifier` (ast),
`compatibility_alias` (ast), `pattern` (re), `open_encoding` (ast), `mro_remover`
(libcst), `hardcoded_version` (re), `_rewrite` (ast, base compartilhada),
`smells/boolean_logic` (ast), + `FlextInfraSourceRewriter`.

- Mecânicos/textuais → sed-by-list (`text_rules.yml`) ou ast-grep rule: `open_encoding`,
  `hardcoded_version`, `pattern`.
- Semânticos → fase rope: `pydantic_modernizer` (v1→v2), `dataclass_modelizer` (W2),
  `compatibility_alias` (jà existe fase compat-alias — convergir e deletar o
  transformer), `mro_remover`/`typing_unifier`/`boolean_logic` (avaliar: rope refactor
  ou rule; rope para renome/assinatura, ast-grep para padrões fixos).
- Cada migração: rule + fixture de teste + aplicação até ponto fixo + deleção do
  transformer e de `FlextInfraSourceRewriter` quando órfão.

### W4 — CLI único com toggles

- `mod` recebe seleção de fases/componentes (ex.:
  `--phases ast,text,rope:dataclass-modelizer` ou model field equivalente) e mantém
  dry-run; uma única entrada (`make mod` / `flext-infra refactor mod`). Nenhuma rota
  paralela de modernização sobrevive.

### W5 — Rollout cobaia + gates por ciclo

1. ai-hub (project level): `make mod` dry-run → revisar census (6 conversões + skips) →
   apply → `make check`/`make test` (ruff/pyrefly/mypy/pytest) 100% verdes; corrigir
   toda violação revelada (fix-forward, adotando WIP paralelo dos outros agentes).
2. flext workspace (workspace level): idem, pacote a pacote (flext-core primeiro por
   causa do W1), gates a cada ciclo.
3. Beartype runtime regredindo? Smoke de import flext-core em cada ciclo (claw ativo).

### W6 — Conhecimento (mesma entrega, não depois)

- **ADR novo** (docs/architecture/adr/): "Unified rope/rule modernize engine; static
  enforcement em flext-infra; runtime beartype em flext-core".
- **Skills/docs**: atualizar `flext-law`/`flext-development` (surface: fases do mod,
  como add rule, como add fase rope) + AGENTS.md delta.
- **Beads**: épico `mod-engine-unification` + filhas por workstream; cada ciclo fecha
  bead com evidência (comando, exit, output decisivo).
- **Board**: post para ALL com census do ai-hub, regras raiz, e contrato das novas fases
  — para os agentes paralelos seguirem o mesmo trilho.

## Validação (por ciclo, obrigatória)

- `make check` (lint/pyrefly/mypy/gates) e `make test` no escopo tocado — zero erros.
- Ponto fixo do mod: 2ª rodada consecutiva = no-op exit 0 (idempotência antes de tudo).
- ai-hub: import smoke + pytest collection limpa; conversões W2 mantêm comportamento
  (FrozenModel == semântica frozen/slots salvo validação).
- flext-core: coleção de testes do enforcement existente rewireada para flext-infra;
  grep provando `import ast` ausente de `_utilities/_beartype` pós-migração.

## Riscos

- W1 toca fundação runtime: migrar em fatias pequenas, gate verdes por fatia; nunca
  deixar flext-core quebrado entre commits.
- Equivalência semântica de rules ast-grep vs visitors Python: cada visitor → rule com
  fixture espelhando os casos de teste atuais; contagem esperada (receipt) prova
  cobertura.
- WIP paralelo: fix-forward adopt; re-ler árvore antes de cada apply; `git add` por
  paths explícitos.

## Suposições explícitas

1. beartype **runtime** (claw bootstrap, conf, typingext patch, BEARTYPE_MODE) permanece
   em flext-core; apenas o motor **estático** (visitors AST + rows de enforcement +
   engine dispatcher) migra e é exterminado de lá.
2. `config/rules/` citado = `flext-infra/src/flext_infra/codemod/{rules,utils,tests}` +
   `text_rules.yml` (não existe `flext-infra/config/rules/` hoje); novas rules nascem
   aí, parametrizadas.

## Fora de escopo

- Reescrever beartype upstream (defects mro-31mj permanecem patcheados).
- Migração de pacotes Singer/dbt (após workspace green, em onda própria do mesmo loop).
