# Rope Modernize — Programa Mestre Unificado · EXECUÇÃO (P0 → C1–C9 → W → Cn+1)

> **Status: EM EXECUÇÃO** desde 2026-09-15T22:45Z. Ordem executada do começo; **ponto de
> controle ao fim de cada fase** = evidência de gate (comando, exit, contagens) +
> checkpoint no board + commit escopado na lane. Base de trabalho: worktree COMPLETA do
> superprojeto `~/flext-worktrees/rope-modernize` > [feature/rope-modernize],
> `make setup` após branch correto; TODOS os projetos em lanes `feature/rope-modernize`
> (31/31) com `0.12.0-dev` local na tip da origin; sync SEMPRE por merge `--no-ff` por
> projeto (nunca rebase/reset).

## AUTO-CRÍTICA E PROTOCOLO CORRIGIDO (2026-09-16T02:30Z — obrigatório em todo ciclo)

Falhas cometidas na execução — cada uma vira regra de protocolo:

1. **`git checkout -- src/` destruiu trabalho não-commitado** (perda do env-boundary,
   toggles e extermínio no adoption tree). PROTOCOLO: antes de qualquer operação que
   reverta/normalize a árvore, TODO trabalho em curso já está commitado E poussado na
   lane (regra 2). Nunca existe edição não-persistida mais velha que a próxima ação
   potencialmente destrutiva.
2. **Suite de testes só rodou quando o operador cobrou** ("nada funciona"). PROTOCOLO: o
   suite do projeto tocado roda ANTES de declarar a fase pronta (testmon canônico,
   subagente em paralelo aceitável); resultado numérico obrigatório no checkpoint. Falha
   descoberta tarde = fase não terminada.
3. **Bug de fórmula no meu próprio planner** (`level = len-1-common`, off-by-one) —
   corrigi o sintoma 3× (base.py) antes de achar que o gerador era meu código.
   PROTOCOLO: sintoma recorrente ⇒ suspeitar PRIMEIRO do código novo próprio; prova
   unitária da fórmula (4 casos de nível relativo) antes de qualquer regen que a
   consuma.
4. **Seletor `PROJECT=` inventado no verbo test** (rodou escopo workspace, 31× falha de
   venv). PROTOCOLO: gramática canônica = `make <verbo>` DENTRO do diretório do projeto;
   seletores somente os declarados no `make help`.
5. **Merge de outro ator concluído às cegas** (`--no-edit` com conflitos semânticos
   pendentes; duas divisões paralelas do mesmo god-module). PROTOCOLO: antes de concluir
   merge alheio — listar TODOS os conflitos, mapear donos por taxonomia (a mais
   nova/completa vence; gêmeos morrem), resolver explicitamente, smoke import antes do
   commit.
6. **Loop meta** (chamadas repetidas de manutenção sem progresso). PROTOCOLO: toda ação
   precisa avançar o passo serial corrente; ações de limpeza/inspeção sem efeito =
   defeito de execução, parar imediatamente.
7. **Nunca deduzir** (regra 4 do operador): rastrear o frame real que lança/importa
   antes de qualquer suposição.

## AUTO-CRÍTICA 2 (2026-09-16T13:02Z — rodada api.py/flext-j64nz)

O que a rodada E4 revelou sobre execução:

1. **Debug teatral**: probes por import-order/capture ergueram 5 tentativas antes do
   env-gate in-file (1 comando). PROTOCOLO: probe = env-gated + in-file + revert
   imediato — nunca monkeypatch import-order.
2. **Filtro cego**: construí duas versões do filtro de composição (rendered_destinations
   de file_plans; before.content) quando a resposta estava na DECISÃO v4 §2.1 ("gen
   único escritor; rope dentro do gen") — o alignment NUNCA foi fase do gen. PROTOCOLO:
   antes de implementar QUALQUER fix, reler as decisões SSOT do plano; a resposta estava
   lá.
3. **Prova numerada**: os probes de journal existem (append被告#1=56/api 1×,
   #2=9/existing56/api 1×+exist 1×) — sem eles não haveria causa-raiz. PROTOCOLO: ctodo
   bug de fluxo = pró-cada-fix com números, não com narrativa.
4. **Waits longos**: bloquearam o ciclo em waits desnecessárrios. PROTOCOLO: suite
   grande via subagente background/junitxml, thread principal nunca espera >5min sem
   ação.

MILESTONE (flext-j64nz resolvido na raiz): o GEN flow tinha DOIS escritores por destino
(templates render api/cli/ping E o gen-side alignment via lazy-init analysis) — o
gen-side alignment foi EXTERMINADO (lei v4 §2.1 render purity + §2.2 "um motor dois
modos"); alignment sobrevive como semantic-phase fazente do mod (semantic_apply phase 0,
já pousado). Testes: 17/17 test_codegen_setup_submodules VERDES na primeira prova
pós-correção estrutural. O gen flow volta a ter um único escritor por destino — o erro
de dual-writer no journal é impossível por construção.

## ESTADO REAL VERIFICADO (evidência 2026-09-16T02:15–02:30Z)

- **Lane unificada** `feature/rope-modernize` @ 501762387 (infra): adoption das 3 lanes
  UNIQUE-WORK infra (optional-city 9c · toolchain-spec restore 2c · f4-infra 1c) + C1 +
  C2-T4 + extermínio exclude-newer/cooldown (e4ba1e9cc, −104 linhas) + toggles mod +
  gateway `u.Infra.env_lookup`. Smoke unificado VERDE: Journal/Session (gêmeos
  unificados na taxa `_codegen` de 10 partials + fachada única `codegen.py`), toggle
  `mod.phases.import-alignment`, exclude-newer morto, campos tipados `settings.Infra.*`.
  Fix da fórmula de nível relativo do planner (`len-common`) provado em 4 casos —
  **pendente de commit**.
- **flext-core**: 2683/2683 verdes (baseline mantido) após stub result (superfície de
  instância completa), part_06 revertida (3 entradas ai-hub), yaml parse fail-wrap
  (`yaml_safe_load` não lança mais), export fantasma `core` removido.
- **flext-tests**: lane com reparos de fixture (payload: BaseException, TypeAliasType,
  fallback repr no fim da cadeia; ciclo base↔matchers quebrado com import adiado;
  commit + merge da origin concluídos).
- **31/31 membros** com `.venv` próprio (setup canônico serial por membro) — `make test`
  workspace desbloqueado.
- **Lanes**: EMPTY descartadas (4 infra + /tmp scratch); UNIQUE-WORK infra ADOTADAS (3);
  PENDENTES: 5 lanes superproject (plan-reconciliation, untrack-gitlink,
  constants-remediation, lane-r41, aeolian-sodalite) + core configdict-owner.
- **Débito medido**: infra 98F/29E (classificação: 73 regressões da lane / 36
  fixture-venv / 18 pré-existente); pyrefly ~64 no tip (flext-1x66z); beads 293 abertos
  com decisões prontas (`/tmp/beads_decisions.md`: CLOSE 17 · PROGRAM 29 · BUGFIX 18 ·
  KEEP 229).

## ORDEM DE EXECUÇÃO CORRIGIDA (serial, um passo por vez, evidência por passo)

- **E1** Commit+push do fix da fórmula do planner (rope_imports.py).
- **E2** `conform apply` + `check` ×2 na lane unificada (regen canônico, ponto fixo
  provado; `.._settings` estável com a fórmula correta).
- **E3** Suite infra: `make test` DENTRO de flext-infra (testmon; venvs de membros
  existem — re-classificar o resíduo real das 36 de fixture).
- **E4** Corrigir grupos (a) das 73: 46× "multiple generation phases own
  flext_demo/api.py" (conflito de registro pós-split — investigar dono das fases); 14×
  msg journal-recovery (atualizar expectativa ao runtime); 11× scaffolder passa campos
  removidos (fix no call-site); 6× layout→render_project_gitignore (verificar composição
  static); 4× misc (WHAT-dispatch frozen-settings → teste via construtor público sem
  env; namespace_moves `u.Infra`).
- **E5** Aplicar decisões de beads via bd (17 close · 29 program-tag/dep · 18 bugfix sem
  épico).
- **E6** Superproject: adotar 5 lanes (preserve-commit WIP → merge --no-ff)
  - configdict-owner; atualizar pins; push.
- **E7** ~~Ciclo completo por repo (PR→0.12.0-dev)~~ **SUBSTITUÍDO pelo operador
  (2026-09-16T12:20Z):** a tip `0.12.0-dev` passa a ser conduzida por OUTRO agente
  (estabilização). Meu papel: **UNIFICADOR/ABSORVEDOR** — (a) unificar nesta lane TODAS
  as PRs/branches/worktrees/WIPs pendentes e paralelas relativas a `~/flext/`; (b) puxar
  CONTINUAMENTE a tip `0.12.0-dev` via `git merge --no-ff origin/0.12.0-dev` na minha
  worktree dedicada a cada ciclo, adotando o trabalho do agente estabilizador
  (fix-forward); (c) manter tudo verde e poussado na lane para que a integração aconteça
  pelo agente de estabilização.
- **E8** Débito pyrefly (flext-1x66z: \_conform 44 já em correção pela adoção da taxa
  nova, safety 4 = resolução cross-package do stub — reavaliar pós-E4) + waves W
  restantes do programa.

## UNIFICAÇÃO — plano `1789489334832-rope-gen-engine-strict-init` (v4) + pendentes

(2026-09-16T12:20Z)

O plano v4 (engine rope-gen + LOC-cap + fechamento 0.12.0; supersede de 3) é **absorvido
neste programa** como linha de execução paralela — decisões herdadas e válidas: render
purity (`render = f(SSOT, templates, PINS)`), rope dentro do gen (um motor, dois modos),
init strict/total (GEN-W001..W005, GEN-E001), resiliência transacional input-CAS,
rules-as-data, cobaias (cosmos-docgen → agents/), landing via PR +
`merge --admin --merge` (autorização operador registrada), exemption lint só escopada
com OPERATOR-AUTHORIZED. Lições operacionais v4 (§0) incorporadas ao protocolo E (batch
realista, commit incremental imediato, board+quiescência antes de gen, paths explícitos,
gen é o ÚNICO escritor de projeções).

**Estado herdado do v4 (2026-09-15T17:55Z)** — reconciliar no E-ABS:

- LOC-cap: codegen ✔ e conform ✔ (peers); **config ✘** (13 `?? _models/_config/*.py`
  - split genuíno a pousar); residual `_codegen/__init__.py` 51KB (F2.W1) — PARCIALMENTE
    absorvido pela minha unificação da taxonomia `_codegen` (10 partials + fachada
    única) e do `_models/__init__.py` (regen canônico).
- Fleet subagentes v4: cli/core DONE (interdependentes, landing coordenado core→cli);
  tests/ldif relatórios vazios (auditar trees); web/db-oracle/grpc/ meltano/dbt-oracle
  FAILED 503 (resumíveis via task_id); observability em curso.
- `gen` nunca verde ×2 na linha v4 — meu E2 provou apply+check verdes ×2 na lane
  unificada (adotar esse estado como base).
- Beads v4: flext-471ws (loc-cap), flext-wjozx (missão), flext-fkfmu (lock), flext-c4k44
  (suíte timeout), flext-5fxu6.4 (dono gerador) — associar ao épico flext-exbwv no
  E5-continuação.

**Mandato absorvedor/puxador (contínuo):**

- PUXAR a cada ciclo: `git fetch` + `git merge --no-ff origin/0.12.0-dev` em TODOS os
  31+1 repositórios da worktree dedicada; adotar o trabalho do agente estabilizador;
  resolver conflitos com a lei (novo vence, gêmeos morrem).
- UNIFICAR: PRs/branches/worktrees pendentes de `~/flext/` entram na lane
  (preserve-commit → merge --no-ff → push), mantendo o mapa de lanes vivo.
- REGIME: agentes únicos sobre flext com total desbloqueio (v4 §0.5); a quiescência só
  se aplica a edição humana concorrente.

> Supersede e unifica: `1789501099301-pydantic-preset-modernize-engine.md`,
> `1789500349934-rope-modernize-engine-unification.md`,
> `1789500930535-accessor-modernize-rope-unification.md`,
> `1789500368402-rope-modernize-engine-plan.md`,
> `1789506814453-rope-native-import-alignment.md`. Agentes paralelos executam streams
> deste programa; conflitos entre planos de origem estão reconciliados nas Decisões
> abaixo.

## Missão

Exterminar workarounds, aliases de compatibilidade e TODA engine de reescrita
`re`/`ast`/`libcst`/`tokenize` em flext-infra; rewire para formas diretas (presets
`m.*`, nomes canônicos, imports alinhados). UMA engine impõe a lei em nível workspace e
projeto: o loop rope unificado por trás de `make mod` (ast-grep + sed + fases rope), com
toggles de componente COMO DADOS e TODOS os parâmetros e patterns em VÁRIOS arquivos sob
`config/rules/` (`mod/` política do verbo · `ast/` engine ast-grep renomeada para `ast`
· `rope/` fases rope), dry-run nativo e callback por fase. Execução em WORKTREE
DEDICADA, sincronizada com a branch de integração por merge `--no-ff` (nunca ficar para
trás). Manter: beartype RUNTIME em flext-core (claw), `make mod`, engine rope. Cobaia:
`~/ai-hub` (branch `dev`, WIP paralelo — fix-forward adopt). Cada ciclo termina 100%
verde (ruff, pyrefly, mypy, coleta/pytest); testes não-conformes à lei de testes são
REMOVIDOS — o que vale é o RUNTIME; regra raiz identificada por item; se não compor
corretamente, PARAR e perguntar.

## Regras-raiz

1. **Três instrumentos, somente**: rope (semântico), `make mod` (ast-grep YAML +
   sed-by-list parametrizados), rows de config (detecção/política). Engines Python de
   reescrita re/ast/libcst/tokenize são exterminadas, nunca encapsuladas — consumidores
   rewired para os três instrumentos.
2. **Fábrica de fachada vive no mixin dono**; nome canônico = nome consumido pela frota;
   exterminar alias + rewire na MESMA mudança. Provado: `from_result` em
   `FlextResultConstruction`, `copy_from_result` exterminado, 50/50 testes, runtime
   provado.
3. **Stub≡runtime**: membro de stub TYPE_CHECKING sem implementação no MRO é defeito
   bloqueante (ocorreu em flext-cli `r[p.Cli.Settings].ok`).
4. **Preset faltante fecha no dono (Tier 0)**: bases locais de projeto viram presets
   `m.*` em flext-core; consumidores rewired; zero alias.
5. **Toggles são dados, não flags**: seleção de componentes/fases do mod em
   `config/tooling.yaml` (`mod.phases.*`), defaults lidos do SSOT, nunca hardcoded;
   dry-run = modo scan sem `--apply`. Nenhuma rota paralela de modernização sobrevive.
6. **Rules são dados, em vários arquivos sob `config/rules/`** (novo SSOT, lei ADR-005;
   hoje inexistente — nasce neste programa):
   - `config/rules/mod/` — política do verbo mod: toggles de fase, mapas (preset-rewire,
     accessor-renames), isenções (external-contracts), listas sed;
   - `config/rules/ast/` — engine ast-grep **renomeada para `ast`** (verbo/ componente
     `ast`): patterns `*.yml` + fixtures `tests/` (migrados de
     `src/flext_infra/codemod/{rules,utils,tests}`);
   - `config/rules/rope/` — parâmetros e patterns das fases rope (modelos de violação,
     defaults por fase, ordem de camadas referenciada do SSOT). Rows de enforcement
     continuam em `config/infra.yaml [enforcement.rules]`; catálogo beartype
     (BEARTYPE_ROWS/ENFORCE-XXX) em flext-core. Nunca detector/transformer novo com
     policy embutida.
7. **beartype split**: RUNTIME fica em flext-core (`_beartype_bootstrap.py` claw,
   `beartype_conf.py`, `beartype_typingext_patch.py`, `BEARTYPE_MODE`) — INTOCÁVEL.
   Motor ESTÁTICO de validação AST (`beartype_engine.py`, `_utilities/_beartype/*`
   visitors, rows estáticas ENFORCE-039..071) migra para flext-infra como rules/rope e é
   removido de flext-core.
8. **Fix-forward adopt**: WIP paralelo é adotado, nunca stash/reset/revert; re-ler
   árvore antes de cada write; `git add` por paths explícitos; locks stale do journal →
   repetir gate sob contenção (flext-fkfmu); gates seriais (OOM transitório observado).
9. **Worktree dedicada + sync `--no-ff`**: TODO o trabalho executa numa worktree/branch
   dedicada alinhada ao tip do GitHub (`flext.worktree_tip_ alignment`); antes de cada
   ciclo (e ao detectar divergência), merge da branch de integração via `--no-ff` na
   lane — preserva histórico, adota o trabalho dos peers, nunca deixa a lane para trás;
   nunca rebase/force-push em branch compartilhada. Landing por commit escopado → push
   fast-forward → PR → review → merge `--no-ff` na integração → gates rerun no SHA
   merged (`flext.land_full_closure`).
10. **Lei de testes — runtime é a autoridade**: testes validam o COMPORTAMENTO REAL dos
    módulos por INTERFACES PÚBLICAS (fachadas, CLI, api.py) — nunca funções privadas,
    construção interna, mocks/patch, fakes, valores hardcodeados de config, ou snapshots
    de estrutura mutável. Teste que não adere aos padrões de qualidade é REMOVIDO
    (descartado), não adaptado com shim/mock para passar; cobertura que não prova
    runtime é cobertura morta. Conflito teste × runtime observado → corrige-se o teste;
    runtime provado por smoke/execução real antes de qualquer gate estático.

## Interpretação rope-mediated (CONFIRMADA por evidência)

Tipos de nó `ast` recebidos via API/facade rope são permitidos (padrão sancionado:
`_wrapper_rewrite.py:20-24` via `FlextInfraUtilitiesRopeRuntime`, flext-6flt;
`_typings/rope.py`). Banido: `import ast|libcst|re` para parse/rewrite próprio.
Zero-literal (`import ast` = 0 em flext-infra) só se o operador pedir espelho próprio
dos tipos — não é o default.

## Estado verificado (evidência consolidada)

- **flext-core**: coleção 2683 testes / 0 erros; classe circular-import e twin-class de
  result.py corrigidas (board `board_8032fb78`); cutover `from_result` completo neste
  worktree; pyrefly pacote = 74 erros (métrica → 0); `make gen PROJECT=flext-core` verde
  após reparos de cutover de peers.
- **Loop mod JÁ canônico**: `make mod` (Makefile:736 → `RUN_PUBLIC,mod`) →
  `refactor mod` → `FlextInfraCodemodBatchApply` (`codemod/batch_apply.py`): plano via
  `u.Infra.codemod_rule_plan`, cascade ast-grep (~105 rules em `codemod/rules/`,
  `sgconfig.yml`), sed-by-list (`text_rules.yml` com receipts),
  `FlextInfraCodemodSemanticApply` (fases rope com `_apply_plan` + `_check_residue`
  zero-resíduo + callbacks no fingerprint), gates lint, dry-run nativo (scan sem
  `--apply`).
- **Lado gen/conform**: `m.Infra.CodegenConformRequest`
  (`_models/_config/artifact.py:417`) com `root/what/scope/mode` — `mode=CHECK` =
  dry-run, `mode=APPLY` = aplicação atômica via `CodegenFilePlan`; rota
  `services/cli_routes_codegen.py:67`. Planner lazy-init já integrado ao alignment por
  commit de ator concorrente (eb6a03131) apontando ao mixin libcst — rewirar para
  planner rope (fix-forward, não revert).
- **Enforcement**: `FixEnforcementCommand` (`_models/check.py:118`) →
  `FlextInfraEnforcementFixerOrchestrator` (`fixers/orchestrator.py`) com `apply`
  (dry-run default), `rules=()`, `safe_only`, `check_after`, adapters
  `gate|manual|rope|transformer` (`_ADAPTER_CLASSES`). Catálogo flext-core: 79 rules / 6
  kinds (BEARTYPE_ROWS, `PREDICATE_BINDINGS` enforcement_part_01,
  `ENFORCEMENT_FIX_ACTIONS` part_08, montagem part_04; runtime: `ModelConfigParams` +
  `field_visitor.v_model_config:185`).
- **Engine accessor a exterminar**: rota `refactor accessor-migrate` →
  `FlextInfraAccessorMigrationOrchestrator` + mixins `_accessor_rewrite.py` (tokenize) /
  `_accessor_report.py`; catálogo `c.ENFORCEMENT_ACCESSOR_RENAMES` (20 entradas;
  part_06) + `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS = {"get_field_value"}` (contrato
  pydantic_settings — NÃO renomear). **Pré-plano já aplicado (reconciliar na C0)**: +3
  entradas ai-hub em part_06 (owner errado → reverter; isenção EXTERNAL_CONTRACTS →
  manter) e `_accessor_rewrite.py` consumindo a isenção.
- **Fundação rope**:
  `_utilities/_rope/{project,rope_structure,rope_imports, rope_source}.py`,
  `fixers/rope_fixer.py`, `FlextInfraRopeWorkspace` (`workspace/rope.py`; índice único,
  snapshot + content-hash, ADR-007). `rope_imports.py` já expõe `ModuleImports`,
  `from_import`, `sort_imports`, `get_changed_source`.
- **Camadas SSOT (landed)**: `config/tooling.yaml` `lazy-init` (`import-layer-order`,
  `reverse-import-mode: type_checking`, `forward-import-form: relative_dot`).
- **Inventário a exterminar (flext-infra)**: `libcst` **8** arquivos
  (`codegen/_lazy_init_import_alignment.py`,
  `_utilities/{qualified_names,compatibility_alias_cst,private_import_cst,`
  `class_nesting_cst,class_nesting_references}.py`, `transformers/mro_remover.py`,
  `refactor/project_alias_migrator.py`) + rascunho `_lazy_init_import_layers.py`; `ast`
  **37–39** (contagem fechada pela varredura dirigida da C-ex term; transformers:
  pydantic*modernizer, typing_unifier, compatibility_alias, open_encoding,
  dataclass_modelizer, \_rewrite, smells/*; detectors: silent*failure,
  deferred_self_reference, consumer_import_violations; gates: duplication,
  abstraction_boundary, namespace_validator; \_utilities/*\_ast.py e afins;
  codegen/\_lazy_init_planner_collision.py); re (transformers/pattern,
  hardcoded_version); tokenize (\_accessor_rewrite.py).
- **Cobaia ai-hub** (`dev`, WIP ~15 arquivos de outros agentes): 6 bases locais em
  `ai_hub/_models/base.py` → 482 refs / 66 arquivos (docstring declara o workaround); 37
  dataclasses mapeadas (6 → `m.FrozenModel`, 30 skips catalogados); 3 accessors soltos
  (`is_internal_backend`, `is_dirty_tree`, `set_proxy_credential`→8 call sites) + 1
  falso positivo externo (`get_field_value`); `is_success→success` já aplicado por
  agente paralelo; mesmo framework Make (`mod` Makefile:742).
- **Concorrência**: `cli_routes_refactor.py`, `dataclass_modelizer.py`, `__init__.py`
  (flext-infra) são de outros atores — adotar; aborto `atomic source changed` já
  observado no ai-hub → escritores serializados.

## Arquitetura-alvo (verbos: `mod` modernize · `ast` engine ast-grep · `gen` gerador por

templates)

```
make mod [dry-run=scan] / flext-infra refactor mod  ← ÚNICO verbo de modernize
├── fase 1: engine `ast`       (config/rules/ast/*.yml + fixtures tests/)
├── fase 2: sed-by-list        (config/rules/mod/sed.yaml, receipt de contagem)
├── fase 3: fases rope         (SemanticApply/_apply_plan/_check_residue):
│     import-alignment · accessor-renames · dataclass-modelizer ·
│     pydantic-presets · compat-alias · private-import · future-annotations ·
│     class-nesting · deferred-models · contract-drift (stub≡runtime)
├── componente enforcement     (rows ENFORCE-XXX com fix_action kind `codemod`
│     executam AS MESMAS regras/fases do mod — nenhum segundo loop de execução)
├── ponto fixo (fingerprint) → gates (ruff/pyrefly/mypy/pytest) → publicação
make gen (gerador por templates; conform mode=CHECK/APPLY)  ← GERAÇÃO
└── consome os MESMOS planners rope; publica CodegenFilePlans (transação atômica)
make fix / fmt / check / test                 ← verbos públicos canônicos, intactos

config/rules/                      ← SSOT de parâmetros E patterns (vários arquivos)
├── mod/    (política do verbo: toggles, preset-rewire, accessor-renames,
│            external-contracts, sed lists)
├── ast/    (engine `ast`: patterns *.yml + fixtures tests/ — migrados de
│            src/flext_infra/codemod/{rules,utils,tests}; verbo renomeado p/ `ast`)
└── rope/   (params/patterns das fases rope: modelos de violação, defaults por fase)
tooling.yaml: mod.phases.<nome>: true|false   ← toggle de componente (dado)
```

**Rotas de modernize exterminadas** (execução só existe no mod):
`refactor accessor-migrate`, `refactor modernize-dataclass`, `fix-enforcement` como
executor próprio (orchestrator/adapters de execução morrem; seleção de política vira
rows do catálogo com fix_action apontando às regras/fases do mod). Taxonomia final de
verbos: `mod` (modernize), `ast` (engine ast-grep, também componente do mod), `gen`
(gerador por templates), `fix/fmt/check/test` públicos — nenhum outro verbo de ajuste
sobrevive.

## Decisões (regra raiz por item; conflitos de origem resolvidos)

- **D1 — Taxonomia de verbos do operador**: `mod` = modernize (ÚNICA superfície de
  ajuste/reescrita: `make mod` / `refactor mod`); `ast` = engine ast-grep (verbo próprio
  renomeado de "codemod"; roda como fase 1 do mod e como scan standalone
  `refactor ast`); `gen` = gerador por templates (`make gen` / conform
  `mode=CHECK|APPLY`, transação atômica `CodegenFilePlan`) consumindo os MESMOS planners
  rope — geração, nunca ajuste. `fix-enforcement` perde o loop de execução próprio: rows
  ENFORCE-XXX com fix_action kind `codemod` apontam às regras/fases do mod; orquestrador
  e adapters de execução são exterminados. Rotas exterminadas: `accessor-migrate`,
  `modernize-dataclass`, executor `fix-enforcement`. Toggles nunca são flags novas:
  `tooling.yaml` `mod.phases.*` (+ enum tipado lendo o SSOT).
- **D2 — Rules-as-data em `config/rules/` (vários arquivos; params E patterns) +
  descoberta por distribuição**: `config/rules/mod/` (preset-rewire.yaml,
  accessor-renames.yaml, external-contracts.yaml, sed.yaml — política do verbo),
  `config/rules/ast/` (patterns `*.yml` + fixtures `tests/` migrados de
  `src/flext_infra/codemod/{rules,utils,tests}`; diretório antigo DELETADO após
  migração), `config/rules/rope/` (violation models, defaults por fase). Renames
  específicos de projeto ficam no projeto (`ai-hub/ast-grep-rules/`). **Constraint de
  empacotamento (evidência `codemod_rules.py`)**: providers de frota são descobertos via
  `find_spec(...).submodule_search_locations` + `codemod/sgconfig.yml` NO pacote (linhas
  216–222) e `ruleDirs` não pode escapar da raiz do provider (linhas 336–339). Repo-root
  `config/rules/` fora do pacote é INVISÍVEL para alvos externos (ai-hub) e para wheels.
  Composição correta (Option C): (a) `config/rules/` repo-root = SSOT; (b) pyproject
  force-include mapeia `config/rules/` → dentro do wheel como dados da distribuição; (c)
  `_provider_configs` passa a resolver o config do provider via
  `Distribution.locate_file("config/rules/ast")` (editável resolve o checkout; wheel
  resolve o dado incluído) com jail de `ruleDirs` reancorado à raiz
  `config/rules/<engine>/` do provider; (d) teste de descoberta a partir de raiz
  estrangeira (tmp project + sgconfig local) prova o caminho ai-hub. Nenhuma
  projeção/gerada — SSOT único.
- **D3 — Import-alignment rope-native** (spec do plano 1789506814453, a mais detalhada —
  adotada por inteiro): detecção sobre o workspace index rope contra ranks do SSOT;
  violações tipadas (`m.Infra.ImportAlignmentViolation`: `reverse_import`,
  `non_relative_forward`); forward → relativo in-place; reverse não-usado em runtime →
  bloco único `if TYPE_CHECKING:` (splice via facade rope-AST,
  `from typing import TYPE_CHECKING` garantido); reverse usado em runtime → fase FALHA
  com diagnóstico (bloquear > gerar quebrado); escopo: árvore do pacote, skips (init
  gerado, fachada-raiz, TYPE_CHECKING, imports aninhados); membros mistos dividem a
  linha; idempotente ×2.
- **D4 — Presets no dono**: `populate_by_name=True` aditivo em `ManagedModel`; presets
  `ConfigModel` (frozen+forbid+populate_by_name, NÃO-strict — coerção YAML),
  `EnvelopeModel` (frozen+strict+validate_default+ignore+strip), `SerializedModel`
  (FrozenModel+serialize_by_alias), `BinaryModel` (FrozenModel+json bytes base64).
  Mapeamento cobaia: `MutableBoundaryModel`≡`m.StrictManagedModel`,
  `FrozenBoundaryModel`≡ `m.FrozenModel`, demais → presets novos.
- **D5 — Regra runtime `consumer_config_dict`** (ENFORCE-080): flag beartype
  `forbid_local_config_dict` (exempt owner `flext_core._models` documentado); fix_action
  kind NOVO `codemod` → regras parametrizadas (D2).
- **D6 — Accessors**: públicos soltos `get_/set_/is_` (exceto `_`-prefix e
  `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS`) = finding bloqueante detection-only no scan
  do mod, com orientação de verbo canônico (drop prefix /
  resolve*/fetch*/build*/provide*). Catálogo `ENFORCEMENT_ACCESSOR_RENAMES` migram para
  rules YAML (D2) e o catálogo é removido; `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS`
  fica em flext-core (lei de frota) consumido pela regra.
- **D7 — Contract-drift checker** (tema desta sessão): checker único via índice rope —
  stub TYPE_CHECKING × MRO runtime; reporta membro faltante/excedente e fábrica
  duplicada (canônico = nome consumido pela frota); rows em `config/rules/`. Queima os
  74 erros pyrefly de flext-core do mesmo tema (dataclass/TypedDict/dict → p|m.\* via
  census rope).
- **D8 — beartype split (regra-raiz 7; Q1 resolvida pelo operador)**: runtime fica;
  motor estático migra em fatias para rules ast-grep/rope (dedup com existentes, ex.
  `ban-model-rebuild` ≙ ENFORCE-041); consumers rewired via facade `u.Infra`/gates,
  nunca private import. Timing CONFIRMADO: W-beartype-static executa APÓS C2–C9 (padrão
  do loop provado na cobaia e frota primeiro), como wave isolada com smoke de claw por
  fatia.
- **D9 — Verde por ciclo, na lane sincronizada**: antes de cada ciclo, merge `--no-ff`
  da integração na worktree dedicada; idempotência ×2 do mod e do gen como prova de
  ponto fixo; teste não-conforme à regra-raiz 10 encontrado no escopo do ciclo é
  REMOVIDO no mesmo ciclo (o runtime prova o comportamento); nada pela metade dentro do
  ciclo.

## Ciclos (ordenados; P0 primeiro; streams paralelos onde marcado; cada um verde integral)

### P0 — Governança viva, worktrees/PR e coordenação (imediata; autoridade total

concedida pelo operador)

0. **Autoridade (operador)**: o dono deste programa puxa para si QUALQUER
   bead/lane/rota/trabalho paralelo que caiba no escopo (accessor-migrate,
   modernize-dataclass, rascunhos de config/rules, lazy-init alignment, planos dos
   agentes) — claim no beads, adoção fix-forward, um único trilho; nada deste tema fica
   fora do programa.
1. **Worktrees/branches dedicadas + PR** por repo tocado (flext-infra, flext-core;
   ai-hub recebe a cobaia em lane serializada), alinhadas ao tip do GitHub; merge
   `--no-ff` da integração antes de começar; um PR por ciclo.
2. **Beads como SSOT de execução**: ÉPICO mestre do programa + bead por ciclo/wave
   (C1..C10, W1..W4) com tasks filhas e prioridades; CLAIM das beads existentes
   relacionadas (flext-d3ja0, flext-fkfmu, e qualquer bead em curso de
   accessor/dataclass/config-rules — absorvidas, não duplicadas); bead cobaia ai-hub;
   bead do cutover `from_result` (worktree); bead do inventário dirigido ast (fecha
   contagem); bead baseline de testes não-conformes (escopo de remoção da regra-raiz
   10).
3. **Conhecimento atualizado JÁ em P0** (declara o programa; mantido a cada ciclo;
   reconciliado no Cn+1): ADR-014 emendado (lei dos 3 instrumentos, verbos mod/ast/gen,
   worktree+no-ff, ledger de extermínio) + ADR-017 criado em rascunho aceito
   ("Parametrized rule surfaces & single modernize CLI", evoluído por ciclo); skills
   `flext-law`, `pydantic-development`, `flext-development`, `flext-gates-as-products`
   (taxonomia de verbos, lei de testes/remoção, lei de worktree); commands
   (`.agents/commands/flext-law.md`, superfície do mod/ast/gen); docs/AGENTS (raiz
   §Architecture: forma canônica de imports + lei de testes; flext-infra: rules-as-data
   em `config/rules/`); `docs/roadmap/namespace-automation-handoff` com a tabela do
   programa.
4. **Reconciliação de estado**: re-ler git status dos três repos (prevalece a árvore
   atual — fix-forward); reverter as 3 entradas ai-hub de `ENFORCEMENT_ACCESSOR_RENAMES`
   (owner errado); MANTER `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS`; `_accessor_rewrite`
   consome a isenção até a wave accessor exterminá-lo.
5. **Board ALL**: missão, streams (main=presets/catálogo/drift; A=import-alignment rope;
   B=accessor/dataclass rules + baseline cobaia; C=árvore config/rules + componente
   enforcement no mod), protocolo worktree+`--no-ff` por ciclo, lei de testes (remoção
   de não-conformes), serialização de escritores no ai-hub, e mapa de absorções (o que
   foi puxado para o programa e de onde veio).

### C1 — Árvore `config/rules/` + engine `ast` + descoberta + guardas (flext-infra)

1. Criar `config/rules/{mod,ast,rope}/`; renomear a engine ast-grep para verbo `ast`
   (componente/fase 1 do mod; scan standalone `refactor ast`).
2. Migrar `src/flext_infra/codemod/{rules,utils,tests}` → `config/rules/ast/`
   (patterns + fixtures) e `text_rules.yml` → `config/rules/mod/sed.yaml`; diretório
   antigo DELETADO na mesma mudança (sem old+new).
3. Descoberta Option C (D2): `_provider_configs` via `Distribution.locate_file`
   - jail reancorado; pyproject force-include de `config/rules/` no wheel;
     `u.Infra.codemod_rule_plan` e `sgconfig.yml` rewired ao novo layout.
4. Guarda do cutover provado: `config/rules/ast/ban-copy-from-result-alias.yml`
   - fixture em `config/rules/ast/tests/`.
5. Provas: descoberta a partir de raiz estrangeira (tmp project); `make mod` dry-run → 0
   pending; fixtures validadas; `make ast` scan → relatório; lint/type escopado verde.
   Board claim ANTES de mover arquivos de `codemod/` (atores concorrentes atuam na
   área).

### C2 — Import-alignment rope-native (stream A; spec D3, tarefas T0–T5 do plano

1789506814453, adotadas literalmente): T0 introspecção rope (sem mutação; se API não
compor → PARAR e perguntar); T1 deletar rascunhos libcst
(`_lazy_init_import_alignment.py`, `_lazy_init_import_layers.py`) + rewirar
`lazy_init.py` (integração eb6a03131) ao planner rope; T2 detecção + modelos
(violations; testes de comportamento sem mocks; ordem do SSOT, P0); T3 reescrita
`align_module_imports` em `FlextInfraUtilitiesRopeImports` (splices TC idempotentes;
snapshots); T4 fase `import-alignment` no SemanticApply + toggle
`mod.phases.import-alignment` em tooling.yaml + planner publicando CodegenFilePlans (um
plano por arquivo, ×2 no-op); T5 gates integrais flext-infra
(`make setup/fix/fmt/check/test`; `make gen` ×2 com 2º = 0 efeitos).

### C3 — Presets no dono (flext-core; stream main)

D4 + testes unitários de comportamento (frozen, extra, populate_by_name, coerção
não-strict, base64) lendo expectativas dos presets (P0).
`make check/test PROJECT=flext-core`.

### C4 — Regra runtime + catálogo (stream main)

D5: flag + branch em `v_model_config` (exempt documentado); bindings + row ENFORCE-080 +
fix_action kind `codemod`; testes violação/consumidor/isento.

### C5 — Parâmetros em config/rules + componente enforcement no mod (stream C)

1. Popular `config/rules/mod/`: preset-rewire.yaml, accessor-renames.yaml (das ~17
   entradas legadas + 20 do catálogo), external-contracts.yaml, sed.yaml (refs de
   nomes); `config/rules/rope/`: violation models + defaults por fase.
2. Patterns ast-grep rewire em `config/rules/ast/`
   (`rewire-consumer-preset-configdict.yml`, `rewire-consumer-preset-refs.yml`,
   `accessor-rename-*.yml`) + fixtures; sed lê mapa de `config/rules/mod/`.
3. Fix_action kind `codemod` (rows ENFORCE-XXX) passa a executar AS regras/fases do mod:
   `FlextInfraCodemodBatchApply` ganha componente `enforcement` (toggle
   `mod.phases.enforcement`, enum tipado default = todos); executor `fix-enforcement`
   (orchestrator + adapters de execução) é exterminado; seus testes ou viram
   behavior-first por interface pública via mod, ou são REMOVIDOS (regra-raiz 10);
   preflight do mod valida toda row com kind `codemod` tem regra/fase resolvida em
   `config/rules/`.
4. Dry-run workspace → relatório único por componente; apply → verde integral
   flext-infra + flext-core; `make mod` ×2.

### C6 — Contract-drift checker (stream main)

D7; apontar às fachadas flext-core (r/e/x/h/d/s, c/t/p/m/u); drift → 0; testes do
checker por fachada pública (sem mocks). Escopo honesto da métrica pyrefly (74): C6
queima o SUBCONJUNTO da classe drift (stub↔runtime, fábrica duplicada, forms
dataclass/TypedDict/dict → p|m.\*); resíduos de outras classes (ex. lambda-typing em
testes) são corrigidos na raiz nos ciclos em que seus arquivos são tocados, com
flext-core pyrefly = 0 como critério de saída de C9 — sem overpromise por ciclo.

### C7 — Accessors (stream B)

1. Rules frota (D2/D6) com fix, fixture-validated; `make mod` ×2 na frota.
2. Rules ai-hub: `is_internal_backend→internal_backend`, `is_dirty_tree→dirty_tree`,
   `set_proxy_credential→provide_proxy_credential`; post no board antes de rodar no
   lane; conferir 8+1 call sites.
3. Detection bloqueante (accessor solto, isenções) no scan do mod.
4. Exterminar: rota `accessor-migrate`, orquestrador, mixins tokenize/report, modelos
   `AccessorMigration*`, catálogo part_06 (após migração); testes de accessor-migration
   ou viram behavior-first por interface pública, ou são REMOVIDOS (regra-raiz 10 — sem
   mocks/patch; runtime prova o rewire).

### C8 — dataclass-modelizer rope phase (stream B)

1. `u.Infra.plan_dataclass_modelizer_cutover(rope_workspace, sources)` (padrão
   `plan_class_nesting_cutover`): classifica `@dataclass` (frozen/serializável/sem
   `__init__`/`__post_init__`/keywords) → header `m.FrozenModel`, remove decorator,
   rewire import `m` da fachada.
2. Fase `dataclass-modelizer` no SemanticApply + `_check_residue` +
   `_verify_fixed_point`; skips catalogados no relatório (30 do ai-hub), nunca silêncio.
3. Exterminar `transformers/dataclass_modelizer.py` (ast/re), rota `modernize-dataclass`
   e registro (bypass do loop = violação).

### C9 — Cobaia ai-hub (main + B; escritores SERIALIZADOS)

1. Verificar resolução de flext-core no venv do ai-hub (editável vs git-pinned
   0.12.0-dev); se pinned: pousar C3–C4 antes, `make setup` ai-hub.
2. Dry-run `refactor mod --repository-root ~/ai-hub`
   (components=ast,sed,rope,enforcement; apply=false; rules=ENFORCE-080) → preview: 482
   refs presets + 3 accessors + 6 dataclasses + skips.
3. Apply fix-forward → `_models/base.py` resta utilitários legítimos; 6 bases
   exterminadas; imports alinhados; `make gen` ×2 e `make mod` ×2 (2ª = 0);
   `pytest --collect-only -q` exit 0 (anti-ciclo); `make check` + `make test` ai-hub
   100%; smoke runtime (`ai_hub.AiHub`, c/m/p/t/u, services).
4. Commits escopados por projeto; beads com evidência (comando, exit, contagens).

### C10..n — Extermínio restante (waves W, 1 bead cada, arquivo morto DELETADO

na mesma wave; ordem: read-only → mutadores)

- **W-transformers**: pydantic_modernizer, typing_unifier, compatibility_alias (+fase
  existente convergida), open_encoding, pattern (re), hardcoded_version (re), \_rewrite,
  smells/boolean_logic, mro_remover (cst), project_alias_migrator (cst), qualified_names
  (cst) → ast-grep rule (mecânico) ou fase rope (semântico); `FlextInfraSourceRewriter`
  deletado quando órfão.
- **W-detectors/utils**: `*_ast.py`, `*_cst.py`, private\*import\**, class*nesting\**,
  silent*failure\**, deferred*self_reference\*\*, namespace, codegen_facades,
  protected_edit_apply, rope_source, rope_imports (resíduo
  `_referenced_runtime_aliases`), `codegen/_lazy_init_planner_collision.py`.
- **W-gates**: duplication, abstraction_boundary, namespace_validator →
  ast-grep/rope/beartype mantendo assinatura no `make check`.
- **W-beartype-static** (D8; ver Q1): migrar visitors/rows estáticos de flext-core →
  rules/rope; deletar `beartype_engine.py` + `_utilities/_beartype/` estático de
  flext-core; runtime intacto; smoke claw por ciclo.
- **W-bans+deps**: `ban-raw-ast-parser`, `ban-libcst-import`, `ban-re-parse`,
  `ban-tokenize-rewrite` + remoção de módulos mortos + `libcst` fora das deps se órfã;
  prova zero-resíduo (`rg` dirigido vazio em código de reescrita).

### Cn+1 — Conhecimento vivo (no MESMO ciclo de cada wave; reconciliação final do

declarado em P0)

ADR-014 emendado (lei dos 3 instrumentos + interpretação rope-mediated + ledger de
extermínio com beads) + **ADR-017 novo** ("Parametrized rule surfaces & single modernize
CLI"; 015/016 já ocupados — corrige referência do plano pydantic). Skills:
`pydantic-development`, `flext-law`, `flext-gates-as-products`, `flext-development`
(superfícies: fases do mod, como add rule, como add fase rope). AGENTS.md raiz
§Architecture (forma canônica de imports) + AGENTS flext-infra.
`docs/standards/development.md`; `docs/roadmap/namespace-automation-handoff` (tabela).
Board ALL por incremento pousado com evidência; memória persistida.

## Validação (por ciclo, inegociável)

- flext-infra `make check` / `make test`: exit 0; ruff/pyrefly/pyright/mypy zero no
  escopo.
- flext-infra `make gen` ×2: 2º = 0 efeitos (lazy-init plan).
- flext-infra `make mod` ×2: 2ª = sem findings (resíduo zero).
- flext-core `make check` / `make test`: exit 0; baseline 2683/0 mantido; claw smoke.
- ai-hub `make gen` ×2 + `make mod` ×2: 1ª com efeitos; 2ª sem.
- ai-hub `pytest --collect-only -q`: exit 0 (anti-ciclo).
- ai-hub `make check` / `make test`: exit 0.
- Testes novos: comportamento por interfaces públicas; ordem/params do SSOT (P0); sem
  mocks/patch.
- Conformidade de testes (por ciclo): testes do escopo que violem a regra-raiz 10
  (privados, mocks, hardcode) REMOVIDOS; runtime provado por smoke/execução real
  primeiro.
- Lane (por ciclo): worktree dedicada; merge `--no-ff` da integração executado; nenhum
  rebase/force-push em branch compartilhada.
- `rg` dirigido pós-wave: zero import re/ast/libcst/tokenize em código de REESCRITA.
- Layout pós-C1: `config/rules/{mod,ast,rope}/` existem e são lidos pela engine;
  `src/flext_infra/codemod/{rules,utils,tests}` removido.
- Descoberta pós-C1 (Option C): plan de rules resolvido a partir de raiz estrangeira
  (tmp project c/ sgconfig local) e em wheel construído (force-include presente).

- Runtime proof para mudanças de comportamento (smoke `r[str].ok/from_result`, presets,
  claw), nunca só teste. Commit escopado por ciclo; push fast-forward.

## Riscos e mitigações

- **Rope API gap** (spans de bloco TC, inserção) → T0 spike primeiro; se não compor:
  PARAR e perguntar (lei); alternativa fail-loud documentada (gate reporta reverse sem
  auto-relocação; correção fix-forward no módulo).
- **Empacotamento das rules (Option C)**: divergência editável × wheel — editável
  resolve `locate_file` ao checkout; wheel depende do force-include do pyproject.
  Mitigação: teste de descoberta em raiz estrangeira + smoke de wheel construído no CI
  do ciclo C1; jail de `ruleDirs` reancorado (nunca removido) para impedir escape de
  provider.
- **flext-core git-pinned no ai-hub** → pousar C3–C4 antes do apply.
- **`populate_by_name` aditivo** → testes de settings/config do workspace.
- **ast-grep super-match** (test doubles) → constraints estreitas + fixtures; escalar a
  rope só com falso positivo material provado.
- **Testes acoplados a rotas exterminadas** (accessor-migrate, modernize-dataclass) →
  reescrever SOMENTE onde existe comportamento real de interface pública a fixar; caso
  contrário REMOVER (regra-raiz 10: cobertura que não prova runtime é cobertura morta —
  remoção é o padrão, não exceção).
- **Concorrência/locks/OOM** → board claim antes de editar; re-ler; gates seriais;
  repetir sob contenção; nunca stash/reset.
- **Equivalência visitors↔rules** → fixture espelhando casos atuais + receipt de
  contagem.
- **W-beartype-static toca fundação** → fatias pequenas, verde por fatia, runtime
  intacto (split D8).

## Decisões fechadas pelo operador

- **Q1 — Timing de W-beartype-static**: APÓS C2–C9 (confirmado 2026-09-15); runtime claw
  intacto em todos os ciclos, smoke por fatia.
- **P0 governance-first**: docs, skills, commands, ADRs, beads, tasks e épicos
  atualizados JÁ em P0; branches/worktrees/PRs tomadas no início; autoridade TOTAL para
  absorver qualquer trabalho paralelo que caiba no plano.
- Taxonomia de verbos (`mod` modernize · `ast` engine · `gen` templates) e layout
  `config/rules/{mod,ast,rope}/` com descoberta Option C — decisões do operador
  incorporadas em D1/D2; sem perguntas abertas restantes.

## Fora de escopo (explícito)

- Migrar consumidores além da cobaia nesta sessão (outros flext-\*, Singer/dbt) → beads
  de follow-up no mesmo loop.
- Reescrever beartype upstream (defects mro-31mj permanecem patcheados).
- Trocar verbos públicos (`make mod`, `make gen`, `fix`) por CLI nova — a unificação é
  interna às superfícies existentes.
- Regeneração dos demais 31 membros do workspace (beads próprios).
