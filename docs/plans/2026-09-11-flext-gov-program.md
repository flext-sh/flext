# PLANO — flext-gov: governance rules + gates (2026-09-11) — v2

> Aprovado pelo operador. Monopólio do tema no lado flext (WS-F1..F7).
> Epico beads: `flext-ssnc7` (+ filhos `.1`–`.7`, validações `.1.1`/`.2.1`).
> Programas irmãos NÃO são executados aqui: agents WS-A..D e ai-hub runtime
> (WS-H1..H5) pertencem a outros agentes — coordenacao por workstream ID.
>
> **v2 (2026-09-11 12:35): autocrítica aplicada.** F1 reaberto (fechamento
> prematuro: nenhum pouso em 0.12.0-dev). Detector/budget corrigidos na raiz
> (`c8a429d59`). Ledger de docs alinhado à realidade (`b25d519d51`).

## Autoridade

Operador > root `AGENTS.md` > `flext-law` skill > escopo > bead ativo.
Uma autoridade por tópico: lei de consumo = `docs/standards/consumption-law.md`

- ADR-015; routing = `docs/GOVERNANCE.md` (linhas, nunca texto duplicado);
identidade de enforcement = catálogo `flext-core`; motor/gates = `flext-infra`.
Fechamento de bead = 4 evidências: (1) estado registrado, (2) git history na
lane de integração, (3) realidade medida (comando/cwd/exit/output), (4) código
integrado. **Nenhum bead fecha com WIP não pousado** — lição aplicada ao F1.

## Snapshot (_commits_ e estados, 2026-09-11 13:10)

STATUS LEGENDA: ◐ = `in_progress` no registro bd · ○ = `open` · ✓ = `closed`
Fonte da verdade dos status: `bd list` (não o texto deste plano — qualquer
divergência é erro DESTE plano e deve ser corrigido nele, ajustando o estado
cadastrado, nunca o texto à mão para "concordar").

### TODO vivo (1:1 com beads — verdade real `bd list`, nunca o texto)

| Bead | Status real (bd) | Lane/branch · SKA no lane | Última evidência | Próxima ação (dono) |
|---|---|---|---|---|
| `flext-ssnc7` (epic) | ○ | — | filhos abaixo | fechar após filhos com 4 evidências |
| `.1` F1 R1 | ◐ in_progress | core `feat/consumer-import-grammar` `6440f1529`+`14c63121d`; infra `feat/consumer-gates` `8c4ef3266`+`c8a429d59` | detector v2 (lineno real, raízes derivadas); budget v2 | detector v3 (asname + memo); pouso R6 (push→PR→`--no-ff`) — agente flext |
| `.1.1` validação F1 | ○ | — | — | twin sintético RED→GREEN após pouso |
| `.2` F2 R2 | ◐ in_progress | infra `feat/consumer-gates` `ba1e5ab70` | config reader consumer+family | contaminação cruzada; apagar `_scope_paths`; unificar `_read_project_config`; ENFORCE-100 — agente flext |
| `.2.1` validação F2 | ○ | — | — | twin plantado RED após pouso |
| `.3` F3 docs | ◐ in_progress | super `feat/flext-gov-consumption-law` `3ebf812055`+`b25d519d51` | ledger honesto (ENFORCE pendências declaradas) | gates markdown do super após P0 — agente flext |
| `.4` F4 gates-as-products | ◐ in_progress | infra `ba1e5ab70`+`c8a429d59`; core `14c63121d` | budget deriva de `ALLOWED_GATES`; primitivas provadas em runtime | fsync/O_NOFOLLOW/EINTR; domínio único (`u.Cli` → core `u`); telemetria budget; verdadeiro projection em project_new — agente flext |
| `.5` F5 tags/versão consumível | ○ (bloqueado por .1 + .4) | — | — | tags 0.12.x + `AI_HUB_CONSUMER.md` após pousos que satisfaçam gates |
| `.6` F6 contribuição | ○ | — | R6 descrito em `GOVERNANCE.md` | formalizar gates de workflow (fluxo separado) |
| `.7` F7 docs auditor | ○ | — | — | three-file gate docs + bijection (pré-requisito F5) |
| `.8` F-AGE automação/piloto | ◐ in_progress | super `bcf2a130bb` (proposta) | ciclo canonizado; crg doctor diagnosticou graph crítico e registrou fix | AGUARDA APROVAÇÃO DO OPERADOR → P0 pouso → `crg build` → piloto RED→GREEN |

Pipeline congelado: ver `~/.agents/commands/flext/gov-automation-cycle.md` (gen → mod escopado → gates → crg → pouso).

### Como ler as SKAs (rastreabilidade)

Cada linha do TODO aponta para commits reais em lanes locais (core:
`feat/consumer-import-grammar`; infra: `feat/consumer-gates`; super:
`feat/flext-gov-consumption-law`), todos com subjects `[WIP] <WS>` e
commits escopados. Sem push: o pouso (push → PR → `--no-ff`) é um pedido
de aprovação separado do operador, conforme R6 — nada de produtivo passa
da lane sem autorização explícita.

### Mapa SKA → conteúdo por repo (rastreabilidade dos [WIP])

| Repo | Branch | SKA | Conteúdo |
|---|---|---|---|
| flext-core (lane) | `feat/consumer-import-grammar` | `6440f1529` | F1 core: `FlextUtilitiesFamilySurface` (owners + renames 33 derivados), `part_03` constants |
| flext-core (lane) | ˆ | `14c63121d` | F4 core: `FlextUtilitiesFiles` (`append_atomic`/`write_atomic`, payload `r[int]`), pin refresh infra→`bff59228` + cli |
| flext-infra (lane) | `feat/consumer-gates` | `8c4ef3266` | F1 infra: detector + model + engine wiring |
| flext-infra (lane) | ˆ | `ba1e5ab70` | F2/F4: duplicação consumer+family + budget gate |
| flext-infra (lane) | ˆ | `c8a429d59` | Autocrítica: detector v2 grounded; budget deriva de `ALLOWED_GATES` (−64 LOC líquida) |
| super (lane) | `feat/flext-gov-consumption-law` | `3ebf812055` / `b25d519d51` | F3 docs + ledger honesto |

Pins vivos (core lane `uv.lock`): flext-infra `rev=0.12.0-dev#bff59228`,
flext-cli re-resolvido. **Nunca rodar `uv sync` sem
`UV_PROJECT_ENVIRONMENT=$PWD/.venv VIRTUAL_ENV=$PWD/.venv`** (ver também
`~/.agents/rules/flext/flext-venv-hermeticity.md` + `bd remember
fleet-venv-hazard`).

## Lei anti-hardcode (vale TAMBÉM para tests)

Listas de bypass/afrouxamento proibidas — exterminar. Fatos deriváveis de
SSOT/código nunca fixados: gates derivam em runtime (`__all__`,
`_LAZY_IMPORTS`, `importlib.metadata`, `c.Infra.ALLOWED_GATES`,
`core_u.project_alias_owners()`). Tests: violações sintéticas geradas em
runtime; baseline medido = evidência de bead, nunca fixture committada. Sem
caminhos absolutos; config keys apenas.

## Estado por workstream — entregue / lacunas / próximos (produção)

### WS-F1 — R1 grammática de import consumer · bead `flext-ssnc7.1` · REABERTO

**Entregue** (fatos, locais exatos):

- R1 core: `flext-core/src/flext_core/_utilities/family_surface.py`
  — `project_alias_owners()` + `compatibility_alias_renames()` (33 derivados
  vs 22 da tabela congelada); constantes `c.NAMESPACE_FAMILY_PREFIX` e
  `FAMILY_SURFACE_MIN_PUBLISHED` em
  `_constants/_enforcement_parts/flextconstantsenforcement_part_03.py`.
- R1 infra: `flext-infra/src/flext_infra/detectors/consumer_import_violations_detector.py`
  — AST com `node.lineno` real; raio de família de
  `core_u.project_alias_owners()`; wildcard/submódulo/símbolo-não-publicado
  tipados; hint canônico via mapa de renames derivado.
  Model `ConsumerImportViolation` em `_models/refactor_namespace_enforcer.py`;
  wiring declarativo `declarative_enforcement.py` (`_INFRA_VIOLATION_FIELDS`);
  catálogo ENFORCE-099 em
  `flext-core/.../_enforcement_catalog_rows_parts/_parts/flextconstantsenforcementcatalogrows_part_01_b.py`.

**Lacunas de qualidade** (owner explícito, fecham antes de pousar):

1. `_published_symbols` importa a raiz por statement — memoizar por
   execução de `detect_file` (escopo por arquivo OK).
2. Aliases (`from flext_core import FlextResult as R`): o símbolo original
   está em `alias.name` (correto); consumo que renomeia alias local
   (`as Z`) entra falso-positivo se `alias.asname` usado no texto do
   current_import — capturar `alias.asname or alias.name` para o texto.
   ⇒ corrigir no detector v3 (pequeno).
3. Validação sintética `.1.1` (RED/GREEN) não executada — twin plantado,
   baseline RED medido, depois GREEN.

**Próximo (ordem, comandos canônicos):**

1. Detector v3 aliases + memo (lane core-gov→infra-gov), `make fix/fmt`;
   teste unitário na infra via `make test APPLY=Y` (escopado).
2. Prova em runtime: plantar violação sintética em `examples/` de um
   membro e rodar o detector declarativo via engine (evidência RED).
3. Ciclo de pouso R6: FF push → draft PR → review → `--no-ff` em
   `0.12.0-dev` (core, depois infra) → gates no SHA mesclado.
4. Fechar .1.1 e .1 com as 4 evidências.

### WS-F2 — R2 duplicação consumer+família · bead `flext-ssnc7.2`

**Entregue**: leitor de config `[tool.flext.project.duplication]`
(scope/min-lines/min-tokens/mode/threshold) em
`flext-infra/src/flext_infra/gates/duplication.py` `_read_project_config`

- `JSCPD_CONSUMER_FAMILY_SCOPE`/`JSCPD_STRUCTURAL_BAN_FORMS` em
`_constants/check.py`; escopo canônico ampliado
(src/testes/scripts/examples/templates/config).

**Lacunas de qualidade (produção)**:

1. **Contaminação cruzada de config**: `_render_scope_dirs` lê a config DO
   projeto checado e aplica a TODOS os projetos descobertos no escopo do
   scan — corrigir para scoped por projeto antes de qualquer baseline largo.
2. `_scope_paths` legado duplica a lógica de escopo → apagar (resíduo zero).
3. `_read_project_config` duplicado entre gates → dono único (helper em
   `base_gate` ou `u.Infra`) — DRY/JSCPD.
4. Riscos de rollout: ampliar escopo 8→10 linhas + dirs extras explode
   findings no primeiro regen — waveform: baselines por membro em lane,
   classificados debt-vs-defeito, antes do pouso; gate em warn→erro.
5. Catálogo ENFORCE-100 (duplicação consumer scans) + validação `.2.1`
   (twin plantado RED).

### WS-F3 — R3 lei de camadas · bead `flext-ssnc7.3`

**Entregue** (lane super `3ebf812055` + `b25d519d51`):
`docs/standards/consumption-law.md` (R1–R6 + anti-hardcode + registry);
`docs/architecture/adr/015-consumer-consumption-law.md` (Accepted); índice
ADR reparado (014 indexado; nota colisão 011/012–020 line, 016 reservado);
`docs/GOVERNANCE.md` router (owners/distância; typo `fleft` corrigido;
ENFORCE pendências declaradas corretamente).

**Próximo**: gates markdown do super (`make check` na lane — nunca
executado; executar após merge dos PRs); consumo de cbh: registrar
consultas de porta `consumption-law.md` no índice de docs do super
(`docs/index.md` router, se houver); F6 contribuição (path) escreve seção
própria referenciando R6 com link, sem duplicar texto.

### WS-F4 — R4 gates-as-products · bead `flext-ssnc7.4`

**Entregue**:

- Budget gate `flext-infra/src/flext_infra/gates/budget.py` — gate set deriva
  de `c.Infra.ALLOWED_GATES`, `BUDGET_REQUIRED_FIELDS`
  (time-seconds/memory-mb/tokens) em `_constants/check.py`; pyproject
  ilegível = falha alta (não confunde com ausente); row `SARIF_TOOL_INFO`
  "budget" + entrada no registry (`workspace_check_gates.py`).
- Primitivas atômicas `flext-core/src/flext_core/_utilities/files.py`,
  compostas em `utilities.py` (MRO flat); provadas runtime: O_APPEND
  (linha-atômica) + rename; payload tipado `r[int]` — **lei descoberta:
  `FlextResult[None]` e payload None são proibidos** (reject na base do
  Result).

**Lacunas (produção)**:

1. Durabilidade: append/write sem `fsync` — perder dados em queda; adicionar
   `fsync` + loop EINTR/EWOULDBLOCK + `os.O_NOFOLLOW` (safety-path) —
   parametrizar via constantes, nunca inline.
2. Conflito de domínio: `u.Cli.atomic_write_text_file/_binário_fiel` já existem
   na frota — **dono único**: migrar os chamados para `u.FlextUtilitiesFiles`
   e apagar os duplicados (net-negative) OU converter these para delegar ao
   core; NÃO manter dois donos (lei SSOT). Ping flext-cli lane.
3. Budgets como constants vs config SSOT (ADR-005): thresholds tail
   (`JSCPD_*`, `_DEFAULT_*` budget) migram para `config/codegen.yaml`
   scaffold/budget seção (dados, não código) — make gen projeta.
4. Telemetria: `_run_gate` mede tempo/memória e grava no GateExecution
   (report/sarif) — budget vira enforcement real, não só validação de
   presença; warn-1-ciclo-then-hard (lei de estabilização 2026-09-08).
5. Exposição fixed-point: projeção `[tool.flext.project]` no scaffold de
   project_new (consumidores novos surgem conformes).

### WS-F5 — R5 release-consumption · bead `flext-ssnc7.5` (aberto)

Depende F1+F4+F7. Plano de produção:

1. Tags 0.12.x só em tips com gates verdes no SHA mesclado (proibido tag em
   local-green).
2. `AI_HUB_CONSUMER.md` versionado por release: gerado a partir de
   consumption-law + changelog (não hand-edit); pipeline docs.
3. ai-hub consome via pin de tag + verificação R1 no CI do consumidor
   (baseline RED → refatorar → GREEN), registrado nos dois trackers por WS ID.

### WS-F6 — R6 lei do caminho de contribuição · bead `flext-ssnc7.6`

Corpo de R6 já escrito em `docs/GOVERNANCE.md` (lifecycle + 4 evidências);
entregável restante: lei formalizada em `consumption-law.md §R6` já existe —
faltam GATES de worlflow (WIP subjects, escopo de add, hook de merge) —
tratar em flext-infra gates de workflow ou hooks (rastreio separado).

### WS-F7 — docs bijection/owner · bead `flext-ssnc7.7`

Docs de gate em três arquivos (law/governance/core docs), bijeckção no docs
auditor — ver bead; prerequisite para F5.

## Matriz produção (critérios de aceite)

| Entregável | Aceite de produção |
|---|---|
| R1 gate | RED sintética → GREEN; zero hardcode de rostos; consumidores (ai-hub pilot) lintam com gate em CI; docs R1 validados |
| R2 gate | baselines por membro classificados; threshold sob config SSOT; ENFORCE-100 registrado |
| Budget | telemetria real em GateExecution; warn→hard após 1 ciclo verde; ENFORCE-101 |
| Primitivas | domínio único (core-u), consumidores `u.Cli` migrados/deletados, fsync+O_NOFOLLOW, fixed point (+idempotence) |
| Tags F5 | tag após gates no SHA mesclado; AI_HUB_CONSUMER gerado e versionado |
| Docs | markdown gates verdes no super; zero texto duplicado entre docs (router-only). |

## Onda de automação canonizada (pesquisa 2026-09-11 12:5x — APROVE-REQUEST]

**Descoberta**: a plataforma já cobre o ciclo completo com verbos declarados;
o plano v2 não explorava os escopos do `mod` nem o grafo de reviews.

1. **`make mod APPLY=Y` NÃO "só ast-grep"**: executa ast-grep + fixed point +
   Ruff + Pyrefly + **diagnósticos LSP reais** num único verbo. Escopos
   declarados: `--module <dotted>`, `--namespace <c|m|p|t|u…>` — ondas por
   módulo/slot, sem varrer a frota. Catálogo vivo: 101 regras yaml em
   `flext-infra/src/flext_infra/codemod/rules/` (donos ADR-014).
2. **`code-review-graph` (crg)** como ferramenta de agente (CLI ai-hub; nunca
   dependência de código — regra `ban-ai-hub-crg-library-boundary.yml`):
   `build`/`update --brief`, `detect-changes`, `impact <sym>` (raio de
   explosão p/ pousos e PR reviews), `dead-code` (YAGNI objetivo p/ R2),
   `refactor suggest`, `install`/`daemon` (hooks de watch), `doctor`.
   Registry multi-repo JÁ contém `flext/flext-core`; grafo ausente
   (doctor: critical) — primeira ação = `build`.
3. **Ciclo canonizado** (documentado em skill+command novos em `~/.agents`):
   `gen → mod (escopado) → fix → fmt → check → test → crg evidence →
   commit escopado → FF push → PR → --no-ff integr. → gates no SHA →
   crg update no tip`.

### Piloto de homologação (proposta de objetivo produtivo)

**Alvo**: colocar F1+R1 (gramática) em nível produtivo NA branch de
integração `0.12.0-dev` e homologar via piloto real:

- P0 — pouso infra+core (lanes → PRs → merge `--no-ff`, gates no SHA).
- P1 — regime crg: `code-review-graph build` (core + infra tips mesclados) +
  `daemon start` opcional durante a onda; `doctor` verde.
- P2 — piloto consumidor: escolher 1 consumidor real (ai-hub plate) ->
  baseline `codes-review-graph detect-changes` + consumer-grammar gate
  **RED** (violações derivadas, ex. `flext_core.lazy`, `flext_cli.models`) →
  fix forward dos consumidores no piloto → **GREEN** → evidência no bead
  (4 fontes) + `AI_HUB_CONSUMER.md` base (F5 antecipado mínimo).
- P3 — se RED→GREEN provado: elevar gate a strict nos membros (warn→hard)
  e liberar F5 tags na linha 0.12.x.
- P4 — espelhar pilot doctrine para R2 (duplitação consumer+família) nos
  tips mesclados com crg `dead-code` como feed de resíduo.

### Pedido de aprovação ao operador

Aprovar (a) execução das ondas com o ciclo canonizado acima (gen→mod→gates→
crg→pouso), (b) build/daemon do crg nos tips de integração, e (c) piloto
P2 conforme descrito, com regime stop: **se P2 não prover RED→GREEN dentro
do primeiro ciclo, mantenho warn e reporto** — nenhum rollout hard sem
aprovação nova.

## Riscos vivos

- Sessão concorrente no infra (rename `--repository-root`→`--ln`, namespace
  reform) — colisão só no pouso: absorver `--no-ff`, hunk-a-hunk, mais novo
  vence (lei 2026-09-07).
- CI do core tip d8ff já vermelho antes do delta (762 namespace etc.):
  adotar no pouso; nunca varrer por cima.
- Checkpoints do `make mod` incluem `.venv`/caches — commits sempre por
  paths escopados.

## Referências

- Lei: `docs/standards/consumption-law.md` · ADR: 015 · router: `docs/GOVERNANCE.md`
- Beads: épico `flext-ssnc7` (+ filhos; `.1` REABERTO); memórias: `fleet-venv-hazard`,
  espaço técnico `technical-lesson-2026-09-05-xdist-silent-death` (padrão de lição em runtime)
- Skills: `~/.agents/skills/framework/flext-gates-as-products/SKILL.md` (novo);
  regra de registro: `~/.agents/rules/flext/gate-registry-ownership.md` (novo)
- SHAs: core `6440f1529` `14c63121d`; infra `8c4ef3266` `ba1e5ab70` `c8a429d59`;
  super `3ebf812055` `b25d519d51`
- Arquivos-alvo: detector `flext_infra/detectors/consumer_import_violations_detector.py`;
  budget `flext_infra/gates/budget.py`; duplicação `flext_infra/gates/duplication.py`;
  primitivas `flext_core/_utilities/files.py`; family surface
  `flext_core/_utilities/family_surface.py`; catálogo ENFORCE-099
  `flext_core/_constants/_enforcement_catalog_rows_parts/_parts/flextconstantsenforcementcatalogrows_part_01_b.py`.
