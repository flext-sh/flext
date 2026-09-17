# Lazy-init: posse total de `__init__.py` + realinhamento canônico de imports

## 1. Directiva do operador (lei, 2026-09-15)

1. Nenhuma exceção de `__init__.py` manual foi autorizada — exterminar para sempre.
2. Remover o lazy-init duplicado dentro do conform.
3. O código de lazy-init também realinha todos os imports do projeto na ordem correta.
4. Ordem canônica anti-ciclo: `settings → config → c,t,p,m,u → base.py → services/ (e qualquer outro) → api.py → cli.py`; sentido direto (para baixo) usa dot relativo em runtime; sentido reverso (para cima) usa **sempre** `TYPE_CHECKING`.
5. Revalidar funcionamento com `pytest collect`.
6. Ajustar a engine (flext-infra) e testar a correção contra ai-hub.
7. Aplicar a `src`, `tests`, `scripts`, `examples`.
8. Analisar as regras especiais/adicionais existentes da frota.
9. Casos errados são corrigidos **na causa, nos módulos** — nunca enfraquecendo o lazy-init quando ele está fazendo o papel dele.

## 2. Evidência do estado atual

| Fato                                                                                                                                               | Local                                                                                                                                                       | Prova                                     |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Exceção de init manual (`preserve_manual_init` → SKIP)                                                                                             | `flext-infra/src/flext_infra/codegen/lazy_init_planner.py:206-222`                                                                                          | leitura do código                         |
| Marcador de posse do gerador                                                                                                                       | `_constants/codegen_lazy.py:20-25` `AUTOGEN_HEADERS`; `_is_generated` em `codegen/_lazy_init_generation_files.py:91-99`                                     | leitura                                   |
| 41 inits manuais em ai-hub (2 classes: eager manuais; estilo-lazy escritos à mão sem marcador — ex. `services/__init__.py`, `_models/__init__.py`) | inventário `find src tests scripts examples -name __init__.py`                                                                                              | lista no apêndice A                       |
| Lazy-init duplicado no conform                                                                                                                     | `codegen/_conform/execute.py` — branch CHECK linhas 276-291 e branch APPLY linhas 318-328, duas chamadas inline de `FlextInfraCodegenLazyInit.plan_files()` | leitura                                   |
| `LazyInitConfig` é modelo vazio (sem campos)                                                                                                       | `_models/deps_tool_config.py:620-621`                                                                                                                       | leitura — ponto de extensão da política   |
| `ALL_SCAN_PATTERNS` exclui `scripts/` deliberadamente                                                                                              | `_constants/codegen_lazy.py:64-74`                                                                                                                          | leitura — exclusão revogada pela diretiva |
| `make gen` no ai-hub hoje: `Lazy-init plan: 0 effects` (planner SKIP em tudo manual)                                                               | log do operador 2026-09-15                                                                                                                                  | transcript                                |

## 3. Decisões de design

**D1 — Posse total, sem exceção.** Deletar `preserve_manual_init`. Todo `__init__.py` nas superfícies `src/tests/scripts/examples` pertence ao gerador:

- init manual com exports no diretório → `WRITE` (adoção: sobrescreve com artefato lazy marcado).
- init manual sem exports → `REMOVE` como resíduo não autorizado (caminho de adoção único; guarda de remove em `_lazy_init_generation_files.py:112-116` estendida para aceitar conteúdo não-gerado **somente** neste cutover, documentada e limitada — após a adoção todo init é gerado e a guarda original volta a valer integralmente). Terminal estável: gen1 adota, gen2 = no-op (ponto fixo preservado).
- Facade roots (`src/<pkg>`, raiz `tests`) e test-child packages: comportamento atual mantido (sempre WRITE).

**D2 — Um único passe de lazy-init no conform.** Extrair helper único (ex.: `_lazy_phase(request)`) em `_conform/execute.py`: a **mesma** análise `CodegenPhaseAnalysis` serve ao modo CHECK (comparar drift), ao modo APPLY (`append_phase_locked` + commit) e à verificação de receipt (`validate_phase_lazy_receipt`). Nenhuma segunda chamada inline de `plan_files()`. Posse do lazy-init permanece DENTRO da transação do conform (ADR-014; não mover para verbo separado).

**D3 — Ordem canônica como SSOT de config.** Estender `LazyInitConfig` (`_models/deps_tool_config.py`) com:

- `import_layer_order: VariadicTuple[NonEmptyStr]` — vocabulário ordenado declarado em `flext-infra/config/codegen.yaml` (`tooling.lazy-init.import-layer-order: [settings, config, c, t, p, m, u, base, services, api, cli]`);
- `reverse_import_mode: Literal["type_checking"]`, `forward_import_form: Literal["relative_dot"]`.
  Classificador de rank (helper novo, planner mixin ou `u.Infra`): mapeia caminho de módulo → rank — `settings/_settings` (0), `config/_config(+_config/)` (1), `constants/_constants` (2), `typings/_typings` (3), `protocols/_protocols` (4), `models/_models` (5), `utilities/_utilities` (6), `base.py` (7), `services/` e qualquer outro (8), `api.py` (9), `cli.py` (10). Rank maior = camada mais alta. Direto = rank maior importa rank menor (runtime, dot relativo dentro do mesmo pacote); reverso = rank menor alcança rank maior (**somente** `TYPE_CHECKING`); mesmo rank = runtime dot relativo permitido. Imports stdlib/terceiros (incl. `flext_core`/upstream) ficam nos grupos isort existentes, inalterados; `from __future__ import annotations` permanece primeiro.

**D4 — Fase de realinhamento dentro do lazy-init.** Novo mixin do planner (ex.: `codegen/_lazy_init_import_alignment.py`) + renderer CST (infra existente `transformers/_rewrite.py`/`pattern.py`), operando sobre o **mesmo** Rope workspace index já aberto pelo lazy-init (ADR-007: um índice, snapshot + content-hash skip). Para cada módulo das quatro superfícies, emite `CodegenFilePlan`s que: (a) movem imports reversos de runtime para bloco `if TYPE_CHECKING:`; (b) normalizam imports diretos intra-pacote para dot relativo; (c) ordenam os imports do projeto por `(rank, nome)` dentro do grupo de projeto. Publicação pela **mesma** fase lazy-init da transação do conform — um dono, um ponto fixo. `ALL_SCAN_PATTERNS` ganha `scripts/**/__init__.py` (docstring da exclusão deliberada reescrita; a diretiva revoga a razão anterior). Artefatos `__init__.py` gerados não passam por realinhamento (conteúdo é do template).

**D5 — Engine não enfraquece regra; módulo errado se corrige na causa.** O realinhamento reescreve a **forma** do import; se um módulo depende de objeto de camada mais alta em runtime, isso é defeito **do módulo** (mover o objeto, inverter a dependência, reexportar da camada correta) — corrigido por fix-forward nos módulos, provado por `pytest collect` + `make test`. A engine nunca ganha caso especial para acomodar violação.

**D6 — Documentação viva na mesma mudança.** Root `AGENTS.md` (§ Architecture Overview) e ADR-014 ganham a lei da ordem canônica e a posse total de inits; `docs/standards/development.md` atualiza a regra de init manual (agora inexistente).

## 4. Regras especiais existentes (análise pedida) — e como a mudança as respeita

| Regra especial                                                                                                                       | Local                                         | Tratamento                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `BOOTSTRAP_CYCLE_EXCEPTION_SEGMENTS` = `{_lazy_parts, _typings}` — inits vazios para não re-entrar no bootstrap de `flext_core.lazy` | `_constants/codegen_lazy.py:88-92`            | Mantida integralmente; realinhamento não força init nessas superfícies; imports de módulos normais desses segmentos seguem a ordem canônica |
| `LAZY_BOOTSTRAP_ROOT_PACKAGE` = `flext_core` — superfície privada do dono do bootstrap mantém inits sem efeito                       | `codegen_lazy.py:103`                         | Mantida; a posse total não contradiz (esses inits continuam gerados/vazios por lei do bootstrap)                                            |
| `NON_PUBLIC_LAZY_ROOTS` = `{examples, scripts, tests}` — raízes com plumbing lazy privado, não ABI pública                           | `codegen_lazy.py:75-80`                       | Mantida; `scripts` passa a ser superfície plenamente varrida (D4) mantendo o caráter privado                                                |
| Facade roots sempre WRITE; test-child WRITE vazio; sem exports + gerado → REMOVE                                                     | `lazy_init_planner.py`                        | Inalterado, exceto a adoção D1                                                                                                              |
| Guardas de duplicata de nome de classe e colisão de export                                                                           | `lazy_init.py:162-184`                        | Inalteradas                                                                                                                                 |
| `INFRA_ONLY_EXPORTS`, `ALIAS_NAMES`, `__version__` dunders eager                                                                     | planner/constants                             | Inalteradas                                                                                                                                 |
| Config/settings zero-ciclo (importam só stdlib/pydantic/upstream)                                                                    | root AGENTS.md §Architecture                  | Consistente por construção: ranks 0/1 não importam nada do projeto                                                                          |
| `c→t→p→m→u` direto runtime, reverso `TYPE_CHECKING`-only                                                                             | root AGENTS.md                                | A ordem canônica **estende** esta lei (settings/config abaixo de `c`; base/services/api/cli acima de `u`)                                   |
| Pureza do render (render = f(SSOT, templates, PINS))                                                                                 | memória `codegen.render_purity_law`           | Realinhamento é planejado sobre snapshot imutável do Rope index; nada de ambiente entra no render                                           |
| Ruff sem `--select` (pyproject é a única política)                                                                                   | `codegen_lazy.py:110-114`                     | Output do realinhamento deve ser ruff-stável (regras I/E); o ponto fixo ×2 do gen é a prova                                                 |
| Idempotência ×2 de gen/fix/fmt                                                                                                       | memória `codegen.gen_idempotence_requirement` | Critério de aceite em toda tarefa                                                                                                           |

## 5. Tarefas (ordenadas)

**T1 — flext-infra: exterminar `preserve_manual_init`** (D1)

- `codegen/lazy_init_planner.py`: remover o bloco 206-222; ação `WRITE` sempre que houver exports, independente de marcador.
- `codegen/_lazy_init_generation_files.py`: extensão bornecada e documentada da guarda de REMOVE para o cutover de resíduo sem exports.
- `ALL_SCAN_PATTERNS` += `scripts/**/__init__.py` + docstring reescrita.
- Testes de comportamento (runtime, fachadas públicas, sem mocks): init manual com exports é adotado; sem exports é removido; gen ×2 atinge ponto fixo.

**T2 — flext-infra: deduplicar lazy-init no conform** (D2)

- `codegen/_conform/execute.py`: helper único; CHECK/APPLY/receipt consomem a mesma análise; deletar o segundo bloco inline.
- Teste: bytes publicados idênticos aos da pipeline anterior; um único `plan_files()` por invocação.

**T3 — flext-infra: política de ordem canônica como SSOT** (D3)

- Campos em `LazyInitConfig` (`_models/deps_tool_config.py`); linhas em `config/codegen.yaml`; classificador de rank + testes P0 (ordem lida do SSOT, nunca congelada).

**T4 — flext-infra: fase de realinhamento de imports** (D4, D5)

- Mixin do planner + renderer CST; planos publicados pela fase lazy-init da transação do conform; regras: reverso→`TYPE_CHECKING`, direto intra-pacote→dot relativo, ordenação `(rank, nome)` no grupo de projeto; respeito às regras especiais da §4.
- Testes de comportamento em workspace tmp: reverso reescrito; direto normalizado; ordem por rank; `__future__` primeiro; stdlib/terceiros intactos; idempotência ×2.

**T5 — Documentação viva** (D6): AGENTS.md root, ADR-014, `docs/standards/development.md` — na mesma mudança de T1–T4.

**T6 — Gates + aterrissagem flext-infra**: `make setup`, `make gen` ×2, `make fix`, `make fmt`, `make check`, `make test` (cwd `flext-infra`; 2º gen = 0 efeitos). Commit escopado por caminhos → push ff → PR → review → `merge --no-ff` em `0.12.0-dev` → gates rerun no SHA merged (lei `flext.land_full_closure`).

**T7 — ai-hub: prova real** (directiva 5/6)

- Serializar escritores concorrentes (o aborto `atomic source changed` de 2026-09-15 veio de 6 processos `flext_infra` paralelos + `ai-hub-watch.service`; rodar gen com a árvore quieta).
- Dep flext-infra no tip pousado (branch de integração, sem pin).
- `make setup`; `make gen` (1ª: ≥41 efeitos de init + efeitos de realinhamento); `make gen` (2ª: 0 efeitos); `make fix`; `make fmt`.
- Corrigir na causa os módulos com dependência reversa real exposta (D5) — mover/inverter no módulo, nunca na engine.
- Prova do operador: `.venv/bin/python -m pytest --collect-only -q` → exit 0 (sem ciclo de import).
- Smoke de runtime dos nomes antes eager: `AiHubMcpGatewayClientCache` (services.mcp_runtime), `AiHubCrgRuntimeBundle` (\_crg_runtime), `AiHubCodexTree` (\_codex_parts), `ai_hub.AiHub`, `ai_hub.c/m/p/t/u`.
- `make check`; `make test`; commit escopado; PR → `dev` (ai-hub).

**T8 — Frota + rastreio**: beads para a regeneração dos demais 31 membros no próximo `make gen` de cada um (projeção automática; fora do escopo deste plano). Trabalho rastreado via `bd` conforme política ativa por lane.

## 6. Contrato de validação

| Comando (cwd)                                                                                      | Aceite                                                                 |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `flext-infra`: `make setup` / `make gen` ×2 / `make fix` / `make fmt` / `make check` / `make test` | exit 0; 2º gen `Lazy-init plan: 0 effects`                             |
| `flext-infra`: testes novos T1–T4                                                                  | verdes; comportamento via fachadas públicas; ordem lida do SSOT        |
| `ai-hub`: `make gen` ×2                                                                            | 1ª ≥41 efeitos init (+realinhamento); 2ª `0 effects`                   |
| `ai-hub`: `.venv/bin/python -m pytest --collect-only -q`                                           | exit 0 — prova anti-ciclo do operador                                  |
| `ai-hub`: smoke imports (T7)                                                                       | todos os nomes resolvem via lazy                                       |
| `ai-hub`: `make check` / `make test`                                                               | exit 0                                                                 |
| Evidência                                                                                          | comando exato + cwd + exit code + saída decisiva registrados (regra 1) |

## 7. Riscos e bordas

- **Quebras de runtime pós-`TYPE_CHECKING`** = defeito de módulo (D5); expostas pelo collect/test; corrigidas por fix-forward nos módulos — trabalho esperado e bornecado por camada.
- **Escritores concorrentes em ai-hub** abortam o gen (`atomic source changed`); serializar e repetir.
- **Performance**: ~670 módulos no ai-hub; índice Rope compartilhado + snapshot content-hash skip (ADR-007).
- **Composição ruff/isort**: render deve ser estável sob as regras I/E do pyproject; ponto fixo ×2 é a prova.
- **Frota**: mudança de lei afeta 32 repos na próxima geração de cada um — propagação por beads (T8).
- **WIP multi-ator em ai-hub** (17 arquivos sujos hoje): adotar por fix-forward, nunca reset.

## 8. Fora de escopo

- Regeneração/PR dos demais 31 membros (T8 apenas registra).
- Mudanças de comportamento de runtime além da mecânica de imports.
- Novas features na engine além do realinhamento directives.

## Apêndice A — 41 inits manuais em ai-hub (2026-09-15)

`src/ai_hub/_constants`, `_models/_config/_hooks_guard_parts`, `_models/_config`, `_models/_config/_tools_parts`, `_models`, `_models/_model_pipeline_parts`, `_protocols`, `schemas`, `services/adapters`, `services/_codex_parts`, `services/_crg_policy`, `services/_crg_runtime`, `services/_deploy_agents_parts`, `services/_deploy_parts`, `services/_ensure_venv_parts`, `services/_forge_governance`, `services/_forge_operations`, `services/_generate_opencode_parts`, `services/_governance_projection`, `services/_host_runtime_parts`, `services`, `services/_installed_runtime_parts`, `services/_installed_runtime_service_parts`, `services/mcp_runtime`, `services/model_pipeline`, `services/_model_pipeline_policy_parts`, `services/model_pipeline/_policy_parts`, `services/model_pipeline/_release_parts`, `services/_session_learning`, `services/_ssot_relink_parts`, `services/_validate_agent_mcp_parts`, `services/workspace_base`, `services/_workspace_discovery`, `services/_workspace_provider_parts`, `_typings`, `_utilities/_filesystem_parts`, `_utilities`, `_utilities/_workspace_state_parts`, `_utilities/_workspace_toolchain_parts`, `tests/fixtures`, `tests/unit`, `tests/unit/lib`.
