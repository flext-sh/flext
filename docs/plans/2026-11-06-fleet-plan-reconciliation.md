# Reconciliação de planos — kilo, zcode, codex e claude (2026-11-06)

Fonte: campanha de estabilização da frota `~/flext` em `0.12.0-dev`.
Objetivo: determinar, por evidência, o que dos planos anteriores foi **implementado**,
o que foi **superado** e o que permanece **pendente**, e transformar apenas o pendente
em fila de implementação.

## Fontes inventariadas

| Fonte               | Local                                                         | Volume                      | Natureza                                        |
| ------------------- | ------------------------------------------------------------- | --------------------------- | ----------------------------------------------- |
| Kilo                | `~/flext/.kilo/plans/*`                                       | ~180 arquivos               | planos/handoffs datados (set–nov/2026)          |
| Kilo (sessão atual) | `.kilo/plans/1793937789109-flext-0120dev-noff-admin-merge.md` | 1                           | **plano ativo** desta campanha                  |
| Claude              | `~/flext/docs/plans/*`, `~/.claude/plans/*`                   | ~14 docs + ~50 transcrições | campanha 2026-11-05 / histórico de planejamento |
| Codex               | `~/.codex/plans/<uuid>/*`                                     | 24 sessões                  | snapshots de plano de sessão                    |
| Zcode               | `~/.zcode/plans/plan-sess_*.md`                               | 1                           | plano de **deploy do ai-hub** (projeto externo) |

## Método de evidência

Um item só é considerado **implantado** se houver, no `0.12.0-dev`, prova verificável:
commit/PR mergeado, `make gen` idempotente e gate correspondente verde. Um item é
**superado** quando seu critério de aceite foi absorvido pelo plano ativo (gate zero da frota, projeções canônicas, tipagem por protocolos). O restante vira fila.

## Classificação

### Implementado / superado (histórico)

- Planos Kilo anteriores a 2026-11-01 (handoffs de estabilização, semver/deploy, beads, Rope, lazy-init, fachadas, LOC caps): seus critérios estão absorvidos pelo plano ativo — a frota está integrada em `0.12.0-dev`, `make setup` verde, `make gen` idempotente nos repositórios tocados, e a tipagem é tratada pela fila ativa. Exceções reais foram extraídas para a fila abaixo (espelho de campos herdados, `JsonValue` recursivo, testes OID ACL, dívida de variantes).
- Planos Claude (transcrições `~/.claude/plans`) e snapshots Codex (`~/.codex/plans`): evidência histórica de sessão; nenhum requisito único não contemplado na fila ativa foi encontrado nos snapshots mais recentes.
- Documento `docs/plans/2026-11-05-make-check-campaign.md`: campanha anterior; seus achados (pyright include obsoleto, timeout do umbrella, hooks) já estão corrigidos ou absorvidos pelo gate atual.

### Externo à frota (owner: ai-hub)

- Zcode `plan-sess_d8169c98…`: deploy/ativação do ai-hub. F1 (`deployment_acceptance.py` materializar `stage_home`) é no projeto `~/ai-hub` (`src/ai_hub/services/deployment_acceptance.py`); F2–F4 (ativação, beads, `opencode.db`) são operação do ai-hub. **Não** entram nos gates de `~/flext`; registrados aqui para não se perderem. Executar no repositório ai-hub, com seus próprios gates.

## Progresso da execução (2026-11-06)

Aterrissado em `0.12.0-dev` nesta execução: infra #2151 `bf9724e0` (mixins pydantic contam como bases de campos efetivos; src-layout regular; guarda de alias sobre protocolo autoral); core #760 `e6b46608` (projeções dos campos de mixin; `make gen` idempotente, 2ª execução 0); observability #168 `a4d22bfa` (constantes do pacote + registry retorna mapping; 35→0); quality #267 `fffa825a` (acumuladores próprios, fronteiras com `model_validate`, loop de enum sem shadowing; 30→0). Também zerados nesta campanha: meltano, target/tap/dbt Oracle WMS, target-ldap/ldif, dbt-ldap, ldap, tap-oracle, auth, plugin, tap-oracle-oic, dbt-ldif, oracle-wms.

Restam: `flext-infra` 428, `flext-ldif` 227, `flext-cli` 35, `flext-db-oracle` 32, `flext-api` 24, `flext-tests` 18, `flext-target-oracle` 11, `flext-grpc` 10, `flext-target-oracle-oic` 4, `flext-web` 1.

Bloqueio de ambiente encontrado e reparado: o workspace `.venv` estava ausente (root `make gen` caía no interpretador mise sem metadados de `packaging`); `make setup` republicou o venv. O `make gen` **da raiz** ainda aborta com `atomic source changed` por troca de inode mesmo com `content_changed=False` (publicação reescreve arquivos idênticos durante a verificação); o gen **por repositório** funciona e é idempotente. Antes da sincronização final, corrigir no owner do gerador o skip de escrita idêntica (ou a verificação por conteúdo+inode) — não mascarar.

## Fila de implementação (pendente real, incremental)

Cada item exige PR pequeno, `make gen` incluso quando houver projeção, e medição do gate antes/depois.

1. ~~**Espelho de protocolo com campos herdados**~~ **CONCLUÍDO** (infra #2151 + core #760): mixins pydantic são ancestrais válidos; mirrors projetam identidade/versão/timestamps herdados.
2. **`JsonValue` recursivo (pyrefly).** Literais de schema Singer (`dict[str, dict[str, dict[str, str]]]`) não são aceitos onde `Mapping[str, JsonValue]` é exigido; decidir no owner do alias/contrato (sem cast), regenerar e medir (`flext-target-oracle-oic`, demais targets).
3. **LDIF OID ACL — testes contra o refactor atual.** Reescrever `tests/unit/servers/test_oid_acl_*` para `AclClause/AclLevelRule/build_rule/subject_leaf/render_aci_values`; o stash antigo (`wip: ldif oid-acl lane`) **não** deve ser aplicado. Meta: ldif 227 → 0.
4. **Burn-down `flext-infra` 428 → 0** pelos clusters já mapeados (Rope `scope|None`, `lineno/decorator_list`, testes de codegen, `codemod/batch_apply`).
5. **Demais projetos do censo:** `flext-cli` 35, `flext-db-oracle` 32, `flext-api` 24, `flext-tests` 18, `flext-target-oracle` 11, `flext-grpc` 10, `flext-target-oracle-oic` 4, `flext-web` 1 — mesma regra `p`/`m`/containers.
6. **YAGNI / compatibilidade:** retirar `t.VariadicTuple` (codemod do owner, `grep` = 0), remover shims sem consumidores, decidir `schema_for_model` somente via fatia vertical com `p.DataContract` e gates verdes.
7. **Sincronização final:** os 31 membros em `origin/0.12.0-dev`, ponteiros do umbrella, `make setup`/`gen`×2/`check` na raiz (após o fix do guard de inode), CI verde, zero branches/worktrees/stashes pendentes.

## Critério de conclusão

`make check` = 0 nos 32; `make gen` ×2 = 0 em cada repo; `make setup` verde; testes e CLIs/Make validados; CI de `0.12.0-dev` verde; nenhuma branch paralela/worktree/stash pendente; nenhum item desta fila em aberto.

## Não-objetivos

- Não criar funcionalidades novas.
- Não editar arquivos gerados à mão.
- Não aplicar o stash OID ACL antigo sobre o refactor atual.
- Não usar `# type: ignore`, `cast`, `Any` ou hardcode para fechar gate.
