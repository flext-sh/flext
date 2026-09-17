# Unificação da engine de modernização via rope + extermínio de helpers/setters (piloto ai-hub)

## Missão (contrato do operador)

1. Helpers/setters desnecessários → **formas diretas** dos modelos; zero aliases de compatibilidade, zero workarounds; rewire em nível de workspace E de projeto.
2. **UM único CLI** para ajustes: `flext-infra refactor mod` (`make mod`), com dry-run e toggles de componentes, loop rope unificado e callback.
3. Manter: regras beartype em runtime do flext-core; `make mod` (ast-grep + sed-by-list); engine rope.
4. **Exterminar**: engines de reescrita baseadas em `re`, `ast`, `libcst` e o motor `tokenize` do `accessor-migrate` — regras migram para **rules-as-data parametrizadas** (`src/flext_infra/rules/*.yaml` + rows em `config/*.yaml`; padrão já usado em ai-hub `ast-grep-rules/`).
5. Piloto: **ai-hub** (`~/ai-hub`), modo fix-forward adopt com agentes paralelos.
6. Cada incremento termina 100% verde: ruff, pyrefly e coleta pytest do(s) projeto(s) tocado(s). Regra raiz identificada por item; se não compor, PARAR e perguntar.
7. Atualizar skills/docs/ADRs/beads e compartilhar no board a cada incremento pousado.

## Estado atual (evidência coletada)

- Superfície unificada JÁ existe: rota `refactor mod` → `FlextInfraCodemodBatchApply` (src/flext_infra/codemod/batch_apply.py): plano de regras via `u.Infra.codemod_rule_plan` (providers universal/runtime, descoberta por distribuição), gates de texto (sed-by-list), rope semantic apply (transaction paths), ponto fixo, gates de lint (ruff/pyrefly); dry-run falha com contagem de findings pendentes. Regras declaradas como dados: `flext-infra/src/flext_infra/rules/*.yaml` + `config/infra.yaml [enforcement.rules]` (lei do pacote: "add a YAML row, not a detector class").
- Engine paralela a exterminar: rota `refactor accessor-migrate` → `FlextInfraAccessorMigrationOrchestrator` + mixins `_accessor_rewrite.py` (tokenize) / `_accessor_report.py`; catálogo `c.ENFORCEMENT_ACCESSOR_RENAMES` (flext-core `_constants/_enforcement_parts/flextconstantsenforcement_part_06.py`, 20 entradas); warnings de accessors soltos `get_/set_/is_` via `c.Infra.ACCESSOR_WARNING_PREFIXES`.
- Edições já aplicadas ANTES do modo plano (não commitadas, reconciliar na tarefa 1):
  - flext-core part_06: +3 entradas de rename do ai-hub (`is_internal_backend`, `is_dirty_tree`, `set_proxy_credential`) e constante `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS = {"get_field_value"}`.
  - flext-infra `_accessor_rewrite.py`: consome a isenção de contratos externos.
- flext-core: WIP de peer em result.py convergiu (runtime `r[int].ok(1)` verde). `make gen PROJECT=flext-core` verde após reparos de cutover de peers (project_metadata façade, mise_toolchain anotações, _conform `_file_plan`/`_link_mode`).
- Piloto ai-hub (branch dev, WIP paralelo de outros agentes em ~15 arquivos): `is_success→success` já aplicado por agente paralelo; restam 3 accessors soltos (`is_internal_backend` protocol property; `is_dirty_tree` static helper com 1 call site; `set_proxy_credential` helper de teste com 8 call sites) e 1 falso positivo (`get_field_value` = override obrigatório de `pydantic_settings.BaseSettingsSource` — contrato externo imutável, NÃO renomear).
- Concorrência: lock global do journal de codegen (bead flext-fkfmu) pode bloquear gates — repetir em contention; OOM transitório já observado — rodar gates serialmente.

## Decisões (regra raiz por item)

- **D1 — Owner das regras de rename**: rules-as-data. Renames genéricos de frota → ast-grep rules em `flext-infra/src/flext_infra/rules/accessor-*.yaml` (uma regra concreta por par, auto-fix, validadas pelos fixtures do mod). Os 3 renames do ai-hub → `ai-hub/ast-grep-rules/*.yml` (dono é o projeto). **Reverter** as 3 entradas que adicionei ao catálogo flext-core (owner errado). **Manter** `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS` no flext-core (lei de enforcement de frota) — consumido pela regra de detecção.
- **D2 — CLI único**: `flext-infra refactor mod` / `make mod` (workspace) e `flext-infra refactor mod --repository-root <proj>` (projeto). Adicionar toggle `--components` ao input do mod (default: todos; ex.: `accessor`, `pydantic`, `dataclass`… mapeando famílias de regras por diretório/etiqueta), dry-run default mantido. Callback: rope semantic apply continua dono das edições estruturais; ast-grep dono das reescritas sintáticas; nenhum segundo loop paralelo.
- **D3 — Extermínio**: deletar rota `accessor-migrate`, `FlextInfraAccessorMigrationOrchestrator`, mixins, modelos `AccessorMigration*` e o catálogo `ENFORCEMENT_ACCESSOR_RENAMES` (após migrar as ~17 entradas legadas para rules YAML). Varredura dirigida por `rg "import re\b|import ast\b|import libcst"` em `src/flext_infra/**` classificando cada rewriter: vira ast-grep rule (sintático), rope semantic apply (estrutural) ou row de enforcement config (detecção) — senão é deletado. Detecção AST remanescente só sobrevive se NÃO reescrever (AGENTS flext-infra: "some detectors still use AST — verify"; a lei nova do operador bane engines de REESCRITA re/ast/libcst). Beartype runtime flext-core: intocado.
- **D4 — Enforcement**: accessors públicos soltos (`get_/set_/is_`, exceto `_`-prefix e `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS`) = finding bloqueante no scan do mod (detection-only com orientação de verbo canônico: drop prefix / resolve_/fetch_/build_/provide_). Regra ast-grep parametrizada primeiro; só escala para rope-semantic se falso positivo material for provado.
- **D5 — Verde por ciclo**: cada tarefa termina com os gates canônicos do(s) projeto(s) tocado(s): `make check` + `make test` (flext-infra, flext-core quando tocado), ai-hub: ruff + pyrefly + `pytest --collect-only` limpos + make próprio; idempotência x2 do mod (segunda rodada sem findings) como prova de ponto fixo.

## Tarefas ordenadas (batches completos e independentes)

1. **Reconciliar estado pré-plano**: reverter as 3 entradas do catálogo flext-core; manter `ENFORCEMENT_ACCESSOR_EXTERNAL_CONTRACTS`; `make check/test PROJECT=flext-core` verde.
2. **Rules de frota (migração do catálogo)**: criar `accessor-rename-*.yaml` em `flext-infra/src/flext_infra/rules/` com as ~17 renames legadas (is_success→success, get_logger→fetch_logger, …) como ast-grep rules com fix; fixture-validated pelo gate do mod; `make mod` x2 na frota fixa.
3. **Rules do ai-hub**: 3 regras em `ai-hub/ast-grep-rules/` (`is_internal_backend→internal_backend`, `is_dirty_tree→dirty_tree`, `set_proxy_credential→provide_proxy_credential`); rodar mod no ai-hub (após post no board avisando o lane, adotando o WIP paralelo); conferir 8+1 call sites rewireados; ruff/pyrefly/pytest-collection do ai-hub 100%.
4. **Regra de detecção bloqueante**: ast-grep detection-only para accessors soltos com isenção de contrato externo; mod scan passa a falhar com findings pendentes (inclui `set_proxy_credential`-like futuros).
5. **CLI único + toggles**: `--components` no `FlextInfraCodemodBatchApply` (modelo tipado, default todos); exterminar rota `accessor-migrate`, orquestrador, mixins, modelos `AccessorMigration*`, catálogo flext-core; reescrever os testes de accessor-migration como testes de comportamento via mod (sem mocks/patch).
6. **Extermínio re/ast/libcst**: inventário com `rg`, classificar por item (tabela no bead), migrar ou deletar; prova zero-resíduo (`rg "from libcst|import ast\b|re\.(sub|match|compile)\(" src/flext_infra` vazio em código de reescrita); gates flext-infra verdes.
7. **Documentação/knowledge**: ADR-014 addendum (unificação no mod; engines exterminadas; regras-as-data para accessors); docs flext-infra do mod; skills (`flext-development`/codemod) atualizadas; beads: evidência em flext-d3ja0 + beads de follow-up; board posts ALL por incremento pousado.

## Riscos e mitigação

- Testes flext-infra acoplados ao `accessor-migrate` → reescrever behavior-first via mod, não deletar cobertura.
- WIP paralelo em ai-hub → post no board antes de rodar mod no projeto; re-read status antes de aplicar; nunca stash/reset.
- Contenção do lock global (flext-fkfmu) e OOM → repetir gate sob contention; gates serialmente.
- ast-grep pode super-matchar (test doubles com nomes iguais) → narrow via constraints do rule file; fixtures provam cobertura; escalar a rope só com evidência.

## Validated done (critério final)

- `make mod` (workspace) e `flext-infra refactor mod --repository-root ~/ai-hub` ambos: apply → x2 sem findings; scan falha se accessor solto for reintroduzido.
- ai-hub: ruff/pyrefly zero erros; pytest coleta 100%; comportamento dos 3 renames coberto por testes de comportamento.
- flext-infra/flext-core: make check + test exit 0.
- Zero resíduo: nenhum import de `libcst`, nenhum rewriter re/ast remanescente, rota accessor-migrate inexistente, catálogo removido, documentação/ADR/skills/beads atualizados.
