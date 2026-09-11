# PLANO — Consolidação da Frota FLEXT: fechamento integral (2026-09-09)

> Aprovado pelo operador (sim, tudo + campanha de dívida incluída).
> Executor: orquestrador + esquadrão de subagentes.
> Lei: `~/agents/AGENTS.md` + `flext-law` + `make-check` + `verification-loop`.
> Comandos: somente Make canônico com `APPLY=Y`, prefixo `MISE_VERSION=2026.9.2`.

## Estado na aprovação (evidências gravadas)
- flext-infra: #650, #653, #661 (CI `--locked` sob CI), #669 (markdown SSOT) MERGED; lanes extintas.
- Sweep onda 1: 31/31 membros regen+push; super rollup `135fd2029a`.
- ai-hub dev: consolidação in-tree do hook client, `.kilo` extinto, wip_hier conforme,
  #669 absorvido — tips `4493dcfce`, `0bf24fc9a`, `b88a43350`; escopos tocados 100% verdes.
- Cosmos-docgen: #81+#144 MERGED; demais PRs já absorvidos; branches aposentadas.
- flext-tests: materialização standalone (Lei 13) → lock PT0S `d5ebe37` + 19 projeções `356e9e1`.
- ~/.agents: 3 correções de lei em `feat/reval250909-adoption` `04e1de7` (push autorizado).

## Fase A — fechar flext-tests
1. Confirmar CI do `356e9e1`; se vermelho, causa raiz seguinte no ciclo standalone.
2. Teardown da materialização `/home/marlonsc/flext-work/flext-tests` após verde (Lei 13).
- **Gate:** CI success no tip.

## Fase B — templates + fixed point do root
1. `gc mail` à lane dona do WIP de templates (`Makefile.j2` script_dispatch, `.envrc.j2`,
   codegen.yaml) pedindo landing; se estagnar, absorver fix-forward (conflito hunk-a-hunk,
   funcionalidade mais nova vence).
2. Root `make gen` fixed point → commit das 5 projeções do super + gitlinks → push.
- **Gate:** gen exit 0 + push FF.

## Fase C — sweep onda 2 (3 subagentes, batches ~10 membros)
1. Regen dos 31 membros contra os templates novos (onda 1 distribuiu saída antiga).
2. Push por membro (absorb `--no-ff` quando origin avançar).
3. Rollup de gitlinks no super + push.
- **Gate:** CI success em core, cli, tests, meltano + `gen check` sem drift.

## Fase D — ai-hub: 3 beads de contrato (1 subagente)
1. `HookClientContract` projetar `fail_closed_events` (builder `AiHub.hook_client_contract`
   + degradação visível no daemon).
2. `foreign_groups`: reconciliar skip-vs-fail de grupos não-mapeados com evidência runtime.
3. Fixture-leaker (`mod-rule-fixtures-*` no HOME) → `tmp_path` + seam `state_path`.
- **Gate:** os 3 tests verdes.

## Fase E — ~/.agents (executada na aprovação)
1. `git push -u origin feat/reval250909-adoption` (autorizado pelo operador).

## Fase F — campanha de dívida estática ai-hub (INCLUÍDA; subagentes em waves)
Baseline capturado: namespace 1106 · codemod 1006 · pyrefly 68 · silent-failure 40 ·
duplication 36 · mypy 13 · loc-cap 9 · tier-whitelist 1 · runtime-census 1.

| Wave | Classe | Método canônico |
|---|---|---|
| F1 | codemod ~1006 | `make fix` + regras ast-grep; residue manual por cluster |
| F2 | namespace ~1106 | `make mod` + renames mecânicos nomenclatura FLEXT, subagentes por diretório |
| F3 | pyrefly + mypy ~81 | tipagem no dono, união discriminada, narrowing — subagentes por módulo |
| F4 | silent-failure ~40 | excepts operacionais tipados (padrão installed_runtime) |
| F5 | duplication + loc-cap + tier + census ~47 | owners compartilhados `u.*`; splits dos 5 arquivos >1000 LOC (1 subagente por arquivo, teste a cada extração) |

- Cada wave: fix → fmt → check parcial da classe → commit escopado → push dev.
- **Gate final:** `make check` 100% verde + `make test` testmon verde.
- Evidência: tabela antes/depois por classe no bead da campanha.

## Fase G — fechamento
1. Beads: fechar consolidação/sweep/campanha com 4 evidências; resíduo
   `fix/conflict-marker-ci-stdlib` (cosmos) classificado.
2. Memória handoff + gc mail de fechamento; teardown de materializações.
- **Gate final:** tips de integração com tudo pousado; zero beads abertos deste plano.

## Ordem
A ∥ C(depende de B) ∥ E imediato → D ∥ F(parte quando B fechar) → G.
**Risco:** F5 (splits config.py 3390 / conform.py 2837) — reescrita real; subagente
dedicado com validação por teste a cada extração.

## Status 2026-09-11 (execução corrente)

- **Fase A (flext-tests):** pendente — CI do tip não revalidado nesta sessão; teardown da materialização não executado.
- **Fase B (templates + fixed point do root):** pendente.
- **Fase C (sweep onda 2):** pendente.
- **Fase D (3 beads de contrato): CONCLUÍDA.** `HookClientContract` projeta `fail_closed_events` (builder + degradação); `foreign_groups` skip de resíduo não-mapeado + descarte de grupos vazios; merge MCP substitui a root owned integral. Extras adotados no blast radius: rename `universal_core→governance_law` completado (modelo+builder), golden claude alinhado ao hook client in-tree, `fixed_socket_path` promovido a fixture compartilhada, credencial proxy pinada nos testes de config, fachada `AiHubGovernanceBundleService` + nesting `artifact_identity` corrigidos. Gate: verde em escopo (deploy 84, opencode 23, wip_hier 5, validate 58 testes) — PR ai-hub #728 (mergeable).
- **Fase E:** feita na aprovação.
- **Fase F (dívida estática):** waves não iniciadas. Baseline reconfirmado + 2 achados de dono: (1) gate `namespace` keyeado no dirname do checkout (flext-infra); (2) suíte ai-hub falha em pares rotativos de arquivos intocados (test-purity, bead aihub-70b34de6).
- **Fase G:** parcial. Bead `aihub-l42it` com evidência completa; merge de #728 bloqueado por: (1) `ai-hub-model-pipeline.service` não ativa — CAS 409 "model or alias facts stale relative to CLIProxy" persiste após strip de voláteis; próximo passo de causa raiz: diffar `request.snapshot.inventory` (parseado) vs `liveInventory` do CCS no ponto do publish (`model-pipeline-publisher.ts:184`); (2) decisão de política: bead-exports rastreados embutem HOME na evidência vs validador de portabilidade.
- **Frota (extra-session):** v3 do model-pipeline adotado no dono do CCS (`MODEL_PIPELINE_SCHEMA_VERSION 2→3`, build+restart, 400 de schema eliminado); recovery do pipeline anula candidato obsoleto em CAS 409; `flext-cli` click floor revertido+publicado e bumps `structlog` não-commitados revertidos — `uv lock --check` do umbrella exit 0; regras duráveis em `~/agents/rules/flext/process-owner-strictness.md`.

### Adendo 2026-09-11 (cadeia de runtime do daemon, mapeada com evidência)
Unidade roda `/home/marlonsc/ai-hub/.venv/bin/ai-hub model-pipeline-daemon`; runtime instalado `0.4.8+90bca03a6cec` perdeu `deployment.json` (falha fechada instantânea, sem saída). Rebuild bloqueado pela política de pins do release (`agents-governance @ git+ssh://…@v0.3.0` não publishable — dono: gate de release flext-infra). Desbloqueio na ordem: (1) resolver política do pin (https ou policy), (2) `make release-build` + `ai-hub runtime --action install`, (3) purge do estado stale já executado, (4) daemon bootstrap geração 1 (CCS vazio confirmado; v3 aceito; recovery void-on-409 e strip de voláteis já pousados). Depois: e2e `deployed_services_match_declaration` + merge #728.

### Adendo 2 — mudanças por projeto (2026-09-11) + worktree dedicada
- **ai-hub** (worktree dedicada `/home/marlonsc/ai-hub-wt/model-pipeline-v3`, 634M, branch `work/wip-hier-v3`, tip `995964e49`, PR #728 mergeable, reparada no registro após prune de terceiro): Fase D completa (fail_closed_events, foreign_groups skip, mcp root-replace), rename governance_law, golden in-tree, fixture socket compartilhada, fachada validate, recovery void-on-409, locks.
- **flext-infra** (`0.12.0-dev` `a0effff42`): `private_direct_refs` (intermediário) → **substituído** pela regra geral "source pyproject é a SSOT" (passthrough verbatim + allow-direct-references deduzido); audit honra refs fonte; validate de namespace deriva forma/nomes do código, nunca de listas (absorção do achado dirname).
- **flext (umbrella)**: plano atualizado 2x (`ba1dc8f2a9`, `6b005bb935`+); merges no-ff absorvendo origin.
- **ccs** (`e2dc8e6c`): `MODEL_PIPELINE_SCHEMA_VERSION 3`, strip de voláteis no CAS, diff canônico no erro 409.
- **~/agents**: `rules/flext/process-owner-strictness.md` novo.
- **Dívidas registradas como itens do plano (lei estendida a tests):** (a) descobrir/executar o mecanismo canônico de install do runtime (elo não documentado) e ativar o daemon; (b) exterminar `class-nesting-mappings.yml` automatizando descoberta por SSOT; (c) fixture `FIXED_HOME` absoluta → tmp_path; (d) pares rotativos de purity (Fase F).
