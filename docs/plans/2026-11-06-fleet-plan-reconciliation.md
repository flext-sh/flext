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

Zerados também após o registro inicial: `flext-core` (#760, #761 `da927555` — `HasDomainEvents` vincula ao modelo de evento próprio), `flext-target-oracle-oic` (#149 `34f9b682` — constantes de schema em `dict[str, JsonValue]`, provado com pyrefly), `flext-web` (0 após #761), `flext-grpc` (#154 `83e16a5e` — contratos runtime em exemplos/managers, payload pelo modelo).

Restam: `flext-infra` 394, `flext-ldif` ~225.

**Porta forward do OID ACL (design próprio pendente):** a refatoração `04c13768` ("oid fixes") removeu os modelos `AciAllow`/`AciRule` e os métodos `build_aci_rule`/`convert_targetattr`/`named_target_attrs`/`generate_acl_name` da camada de conversão, substituindo-os por `AclClause/AclLevelRule/AclBindRule` + `build_rule`/`subject_leaf`/`AclPipeline`, mas deixou a pipeline e os testes chamando a API antiga. Restaurar a camada antiga por inteiro reverte o refactor (piores gates: o flip de campos foi rejeitado pelo conformance) e não é aceitável. A correção correta é concluir o refactor: re-apontar `AclPipeline.build_aci_rules` e os testes OID ACL (assemble/source/convert_oud) para a camada nova (`AclLevelRule`/`AclBindRule`), preservando o comportamento OUD verificado (`SuperUser`→Directory Manager, `attr=[]`/`attr!=(*)` diagnósticos, `OUD_TARGETATTR_ALL`).

LDIF (227) — estado funcional apurado: `tests/unit/servers/test_oid_acl_convert.py` e `test_oid_acl_endtoend.py` têm **7 falhas** e `test_oid_servers.py` falha na coleta (fixture `schema` com assinatura inválida). Os módulos `test_oid_acl_assemble.py`/`test_oid_acl_convert_oud.py` são **stale** contra a API removida (`AciRule/AciAllow`, `build_aci_rule`, `convert_subject_to_oud`); a API atual é `AclClause/AclLevelRule/AclBindRule`, `build_rule`, `subject_leaf`, `AclPipeline.render_aci_values`. Próximo passo: corrigir a fixture e as 7 falhas funcionais, depois decidir entre reescrever ou aposentar os dois módulos stale com cobertura equivalente comprovada.

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

## Rodada de convergência e landing (2026-11-07)

Decisão do operador (2026-11-07, registrada no tracker como `operator-decision-2026-11-07-land-now-red-base`): landar agora com a base vermelha pré-existente; achados restantes permanecem em beads.

- Censo: 1.021 refs nos 32 repositórios; todas decididas (mescladas, superadas ou rejeitadas com SHA e motivo em `flext-bhvgw`). Stashes e worktrees sujos preservados em `preserve/*-20261107` antes de qualquer remoção.
- Adotados em `upload-20261007`: protocol-guard (#2156), setup-lock-hygiene, layout-catalog-roots, gen-removal (`flext-otcin`), cli spawn-argv, tests connectivity-executables e docker-surface, contratos de dbt-ldap/observability/tap-oracle/tap-oracle-wms/target-ldap.
- Correções de causa raiz: admissão no-op do gen pulada (gen de membro 160 s → 28 s), alias de protocolo projetado deixou de oscilar, constantes do meltano sem base Pydantic, `DbOracle.engine(url)` honra credenciais da URL (`flext-dhzep`), dependências por URL `@0.12.0-dev` (`flext-3mma0`).
- Rope 1.15.2+dc.4 (`64cbd65b`) projetado na frota e no lock da workspace.
- Landing: `upload-20261007` → `0.12.0-dev` nos 31 membros (merge commit), produtores primeiro.

Pendências reais (beads abertos): achados de `make check` da frota; gen da raiz acima do orçamento (`flext-obayy`, `flext-srb6l`); formação dos `uv.lock` de membro (`flext-zzynv`); itens de gerador e regras (`flext-q9qkq`, `flext-i49ap`, `flext-vw3bw`, `flext-kt51y`, `flext-nas61`, `flext-bqr5e`, `flext-p93dh`, `flext-pblzr`, `flext-ccsjh`); decisão de verbo `make mod` (`flext-py33d`).
