# PLANO — flext-gov: governance rules + gates (2026-09-11)

> Aprovado pelo operador. Monopólio do tema no lado flext (WS-F1..F7).
> Epico beads: `flext-ssnc7` (+ filhos `.1`–`.7`, validações `.1.1`/`.2.1`).
> Programas irmãos NÃO são executados aqui: agents WS-A..D e ai-hub runtime
> (WS-H1..H5) pertencem a outros agentes — coordenacao por workstream ID.

## Autoridade

Operador > root `AGENTS.md` > `flext-law` skill > escopo > bead ativo.
Uma autoridade por topico: lei de consumo nova = `docs/standards/consumption-law.md`
+ ADR-015; routing = `docs/GOVERNANCE.md` (linhas, nunca texto duplicado);
identidade de enforcement = catalogo `flext-core`; motor/gates = `flext-infra`.

## Decisoes confirmadas

1. Gramatica R1 (derivada, nunca enumerada): legal no consumidor = `from <pkg>
   import X` com `X ∈ pkg.__all__` (contrato lazy publicado). Qualquer
   `pkg.<submodule>` é violação — inclusive facet modules (`flext_cli.models`),
   reach-throughs (`flext_infra.workspace.detector`) e `flext_core.lazy`.
   Facet modules continuam legais apenas intra-família. Fix hints derivados
   invertendo `_LAZY_IMPORTS`. Primitiva publica de lazy-install no core raiz
   elimina qualquer lista de isenção.
2. ADR-015 (próximo livre; 011/012 existem só na linha 0.20.0-dev; 014 on-disk
   não indexado — reparar índice no mesmo change).
3. Pins: linha 0.12.x — tags nos tips verdes após gates; ai-hub pina tag.
4. IDs: WS-F1..F7 (flext) + WS-H1..H5 (ai-hub, outro agente).

## Lei anti-hardcode (vale TAMBÉM para tests)

Listas de bypass/afrouxamento proibidas — exterminar. Fatos localizáveis via
SSOT/código nunca fixados: gates derivam em runtime (`__all__`,
`_LAZY_IMPORTS`, `importlib.metadata` namespace-shape, constantes `c.Infra`).
Tests: violações sintéticas geradas em runtime sobre a superfície descoberta;
baseline medido (RED no ai-hub) = evidência de bead, nunca fixture committada.
Sem caminhos absolutos / referências fora do repositório; config keys apenas.

## Workstreams (beads)

| WS | Bead | Entrega |
|---|---|---|
| F1 | `flext-ssnc7.1` | Gramática de import consumer + cut-over SSOT (exterminar `ENFORCEMENT_PROJECT_ALIAS_OWNERS`, `ENFORCEMENT_COMPATIBILITY_ALIAS_RENAMES`, `BOUNDARY_SKIP_PROJECTS/CLICK_FILES/TOML_ALLOWED`, `BOUNDARY_FLEXT_CLI_CONCRETE_RE`, `startswith("flext_")`) + primitiva lazy-install pública + rows ENFORCE-099+ |
| F1.v | `flext-ssnc7.1.1` | Validação sintética derivada RED/GREEN |
| F2 | `flext-ssnc7.2` | Scan estrutural de duplicação consumer+família (`.2.1` valida com twin plantado) |
| F3 | `flext-ssnc7.3` | consumption-law.md + ADR-015 + índice ADR + router rows |
| F4 | `flext-ssnc7.4` | `[tool.flext.project]` + budget gate + atomic O_APPEND append (core `u`) + fixed-point exposure |
| F5 | `flext-ssnc7.5` | Tags 0.12.x + AI_HUB_CONSUMER versionado (deps: F1, F4, F7) |
| F6 | `flext-ssnc7.6` | Lei do caminho de contribuição |
| F7 | `flext-ssnc7.7` | ADR-bijection + guarantee-owner no docs auditor; docs de gate em três arquivos |

## Lanes (worktrees dedicadas — pecado nº 1 corrigido)

- `~/flext-work/flext-gov-super` → `feat/flext-gov-consumption-law` (docs/lei/ADR/plano)
- `~/flext-work/flext-core-gov` → `feat/consumer-import-grammar` (F1 core)
- `~/flext-work/flext-infra-gov` → `feat/consumer-gates` (F1/F4 infra)

Base de cada lane = `origin/0.12.0-dev` recém-buscado. Infra tem sessão viva no
umbrella checkout — colisão só no pouso: absorver `--no-ff`, hunk a hunk,
funcionalidade mais nova vence (lei 2026-09-07).

## Lei de execução

Make canônico apenas, `APPLY=Y` única flag de mutação; testmon via `make test
APPLY=Y`; fail loud (warnings/skips/vazio = RED); evidência por claim (comando,
cwd, exit, output decisivo); refactor-in-place, resíduo zero (código
superseded deletado no mesmo change); docs atualizados no mesmo change;
generated surfaces via `make gen APPLY=Y` + ponto fixo; subagentes leves só
descoberta; thread principal dona dos efeitos sequenciados; WIP commitado por
paths explícitos com frequência.

## Pouso

Lane → commits escopados → FF push → PR → review → `merge --no-ff` em
`0.12.0-dev` do membro → gates no SHA mesclado → prova em runtime integrado →
roll-up de gitlinks no super após commits no remote → beads fechados com as
4 evidências. F1/F4/F5 TAGGED antes do consumo ai-hub (registro por WS ID nos
dois trackers).

## Status (vivo — atualizar a cada passo)

- 2026-09-11: beads criados (`flext-ssnc7*`); 3 lanes criadas dos tips frescos
  (super `bfaf0ed861`, core `d8ff74d16`, infra `cd40faa1a`); F1 claimed
  (in_progress).
- 2026-09-11 04:38: F1 core LANE COMPLETA (WIP commit `6440f1529`):
  - `FlextUtilitiesFamilySurface` adicionado em `src/flext_core/_utilities/family_surface.py`
  - `project_alias_owners()`: deriva aliases publicados por pacote (substitui roster congelado)
  - `compatibility_alias_renames()`: deriva mapa `Flext* -> letra` agrupando por módulo dono (33 renames derivados vs 22 tabela antiga)
  - `part_03`: `NAMESPACE_FAMILY_PREFIX` (seed descoberta) + `FAMILY_SURFACE_MIN_PUBLISHED=1` (fail-loud instalação quebrada)
  - `utilities.py`: compõe `FamilySurface` no MRO de `FlextUtilities`
  - Fix/fmt/check cycle: ZERO findings nos meus arquivos (2 pyrefly + 1 mypy corrigidos)
  - Descobertas valiosas: env hazard `UV_PROJECT_ENVIRONMENT` vaza de direnv; golden stale `_golden_public_api.json:1739` (`read_project_metadata` renomeado); infra option rename em voo (`--repository-root`→`--n`/`--ln`); 762 namespace + 38 silent-failure + 7 boundary + 1 tier-whitelist + 9 codemod = dívida pré-existente da reforma live (não meu delta)
- 2026-09-11 05:30: F1 infra LANE COMPLETA (WIP commit `8c4ef3266`):
  - `FlextInfraConsumerImportViolationsDetector` em `src/flext_infra/detectors/consumer_import_violations_detector.py`
  - Implementa gramática R1: legal = `from <pkg> import X` com `X in pkg.__all__`; qualquer `pkg.<submodule>` é violação (facet modules, reach-throughs, flext_core.lazy); intra-family isento (facade assembly)
  - `ConsumerImportViolation` model com `target_package`, `imported_path`, `imported_symbol`, `legal_symbols` para fix hints
  - Integração declarativa: `_INFRA_VIOLATION_FIELDS` + `_detect_consumer_import_violations()`
  - ENFORCE-099 no core (`part_01_b.py`: 4-import-law, flext-import-rules, flext-consumption-law)
  - Fix/fmt/check: ZERO findings nos novos arquivos
- 2026-09-11 06:55: F3 + F2 + F4 (docs + gates):
  - **F3**: `docs/standards/consumption-law.md` (R1–R6 canônico + anti-hardcode + registry de gates em 3 fontes); `docs/architecture/adr/015-consumer-consumption-law.md` (Accepted); índice ADR reparado (ADR-014 indexado + nota de colisão 011/012/016); `docs/GOVERNANCE.md` router (owners por SSOT, anti-hardcode router, mapeamento WS→gate→ENFORCE)
  - **F2**: duplicação consumer+family — `_read_project_config` `[tool.flext.project.duplication]` (scope/min-lines/min-tokens/mode/threshold), constantes `JSCPD_CONSUMER_FAMILY_SCOPE` + `JSCPD_STRUCTURAL_BAN_FORMS`; ENFORCE-099 já ativo
  - **F4**: `[tool.flext.project.budget]` gate (`FlextInfraBudgetGate`: toda registered gate exige budget com time-seconds/memory-mb/tokens; registry divergence = erro) + row `SARIF_TOOL_INFO` + entrada no gate registry; **primitivas atômicas no core `u`** (`append_atomic` O_APPEND + `write_atomic` temp+rename, payload tipado `r[int]` — `FlextResult[None]` é proibido pela lei) — provadas em runtime
  - Pins re-resolvidos no core lane: flext-infra 3229dcc3→bff59228 + flext-cli refresh (resolveu crash de render `ci_private_submodules` + símbolo `Cli.AtomicDirectoryChainPlan`)
  - WIP commits: core `14c63121d`, infra `ba1e5ab70`
  - Descobertas: `FlextResult[None]`/payload None proibidos (base reject); bases de classe não são atributos da subclass (u.X sempre via MRO flat); mod pipeline cria checkpoint commit automático (contém venv! commits escopados obrigatórios)
  - F1/F2/F3/F4 beads claimed/in flight; pendente: F5 (tags 0.12.x + AI_HUB_CONSUMER), F6 (contribuição), F7 (docs auditor/bijection)
  - Próximo: validar gates synthesized RED (snowflake twin), F5 release-consumption quando F1+F4 estiverem landed
