# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md

<!-- TOC START -->

- [Estado atual (evidência)](#estado-atual-evidencia)
- [Fase A — Fechar os vermelhos e aterrissar flext-infra](#fase-a-fechar-os-vermelhos-e-aterrissar-flext-infra)
- [Fase B — Raiz do flext-tvenh (modernizer × contratos)](#fase-b-raiz-do-flext-tvenh-modernizer-contratos)
- [Fase C — Propagação da frota e aterrissagem no superprojeto](#fase-c-propagacao-da-frota-e-aterrissagem-no-superprojeto)
- [Fase D — Consolidação de testes (plano original, slice seguinte)](#fase-d-consolidacao-de-testes-plano-original-slice-seguinte)
- [Regras transversais](#regras-transversais)

<!-- TOC END -->

(Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there

# Plano — Fechamento do ciclo flext-infra + propagação da frota + consolidação de testes

## Estado atual (evidência)

- Pushes já na integração `origin/0.12.0-dev` (flext-infra):
  - `9222b18a0` test(runner): contrato fail-loud do `flext-ozlu0` (erro de política em
    coleção → exit não-zero e nomeia o ofensor) + slow markers nos testes de processo +
    `r[CodeType]`.
  - `bdd1e9c4a` fix(template): `@flext-regenerate: make gen`.
  - `f13da7200` test(docs): fixtures alinhados (version no pyproject do workspace,
    beads.yaml no auditor).
- Não-commitado meu (validado via scratch: fixed-point do overlay ✓):
  - `_utilities/pyproject_conform.py`: `_dependency_order_key` compartilhado + merge do
    overlay em ordem canônica.
  - `_models/check.py` + `check/workspace_check.py`: campo `workspace` duplicado
    removido do `check run` (ScopeMixin já dá `repository_root`), 4 consumidores
    rewirados.
- Vermelhos atuais (última rodada `make test`: 66 passed, exit 2, maxfail=2):
  1. `generator_guides_tests.py::test_removed_root_guide_plans_only_exact_owned_member_deletion`
     — "subproject origin differs from its .gitmodules URL: flext-a" (fixture/validação
     de gitmodules mais estrita).
  2. `transaction_directory_journal_tests.py::test_appended_phase_rejects_replaced_created_parent`
     — mensagem esperada divergiu ("docs destination changed after planning..." vs
     "generation destination parent differs from journal").
- Beads: `flext-ozlu0` (claimed, a fechar); `flext-tvenh` (defeito: deps modernize ergue
  floors contra `uv_constraint_dependencies`).
- WIP alheio no tree (lane concorrente): `models.py`, `_models/rope_rules.py`,
  `_utilities/rope_rule_loader.py`, `codemod/rope_rules/`. Não commito; valido a árvore
  combinada.

## Fase A — Fechar os vermelhos e aterrissar flext-infra

1. Investigar e corrigir (dono mínimo) os 2 vermelhos atuais; iterar `make test` em
   flext-infra até verde (testmon encolhe a seleção a cada rodada; maxfail=2 Revela o
   próximo par). Critério de parada: 0 failed. Roadblock: se um vermelho pertencer ao
   WIP alheio, registrar no bead e seguir com escopo próprio.
2. Rodar `make gen` em flext-infra (lint, loc-cap, boundary, canonical-alias, etc.) até
   verde.
3. Commit por paths explícitos (conform + check model + eventuais fixes de teste), push
   FF; se rejeitado, `git merge --no-ff origin/0.12.0-dev`, resolver, revalidar, push
   (nunca rebase/force-push).

## Fase B — Raiz do flext-tvenh (modernizer × contratos)

1. Corrigir `deps modernize --rewrite-constraints` para clampear floors reescritos ao
   envelope `uv_constraint_dependencies` (structlog permanece `>=25.5.0,<27` na frota).
   Owner: flext-infra deps/modernizer + SSOT comment já existente é o contrato.
2. Teste de contrato: reescrita contra um floor proibido pela constraint falha/clampa
   (não congela valores de config no teste).
3. `make test` + `make check` em flext-infra; commit; push (mesmo protocolo FF/merge).
4. Fechar `flext-tvenh` com `DONE:` + comando/exit/SHA.

## Fase C — Propagação da frota e aterrissagem no superprojeto

1. `make gen` no root do workspace (janela do lock do journal transacional do codegen;
   validamos `blocking=False` → janela rápida, retry sem alterar o timeout do owner)
   para propagar a anotação e o template aos 32 membros. Risco OOM visto antes: rodar
   sem testes paralelos simultâneos.
2. Commit nos membros apenas dos Makefiles regenerados (paths explícitos, um commit por
   membro), push de cada membro na sua integração.
3. Superprojeto: atualizar gitlinks dos membros tocados + flext-infra (já avançou 3
   SHAs), commit por paths explícitos, push FF em `origin/0.12.0-dev`; rejeição → merge
   --no-ff da base, resolver, revalidar, push.
4. Validação final do ciclo: `make gen` e `make test` no root (frota completa).

## Fase D — Consolidação de testes (plano original, slice seguinte)

1. Inventário atual: nº de nós por membro (testmon/junit), topo de duplicação semântica
   (mesmo comportamento em arquivos distintos).
2. Consolidar suites duplicadas em fixtures parametrizados `flext-tests` (`tm` +
   pytester), apagar testes redundantes, manter o contrato fail-loud do runner
   (flext-ozlu0) como proteção contra falso verde.
3. Ativar/afinar testmon (seleção incremental) + xdist nas suítes: medição antes/depois
   (wall clock e contagem de nós) como evidência.
4. Cada fatia: um bead, slice curto, `make test/check` verde por membro antes do
   próximo.

## Regras transversais

- Beads primeiro: claim antes de escrever; atualizar após cada mudança de estado; fechar
  só com `DONE:`/`SUPERSEDED:` + prova.
- Commits por paths explícitos; nunca `git add -A`; nunca
  stash/reset/revert/rebase/force-push.
- WIP de outras lanes: adotar e preservar; commit apenas do meu escopo.
- Lock do journal: retry rápido (janelas curtas), sem hack de timeout.
- Warnings: zero tolerância na aterrissagem final (fase C.4).
