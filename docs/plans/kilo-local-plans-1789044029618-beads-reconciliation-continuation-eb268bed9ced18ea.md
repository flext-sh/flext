# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md

(Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there

# Plano: Continuação da Reconciliação de Beads + Sincronização GitHub

## Estado atual (evidência)

- Coordenador: `flext-im2my` (in_progress, claimed). Gates atuais: graph clean, 0
  ciclos, 0 filhos abertos sob pais fechados, duplicate gate adjudicado (30 pares
  KEEP_BOTH).
- Feito: skills ~/agents endurecidas (beads-organization, writing-style,
  beads-traceability); script
  `~/agents/skills/tool/beads-organization/scripts/reconcile-inventory.sh` validado;
  comando `/reconcile-beads` e agente `tracker-curator` criados; `wip-hier.sh` corrigido
  (fim de `wip`/`fixes`, `-n`, `--no-verify`); hooks bd instalados; ciclos
  000/020/040/080 auditados por subagentes (vereditos prontos, NÃO aplicados); ciclo 060
  falhou (contexto estourou) e será redividido.
- Inventário ativo: ~270-295 beads (open+in_progress+deferred). CSVs em
  `~/tmp/kilo/flext-beads-*.csv`.
- Pendente em ~/agents: waza falhou por lock concorrente (rodar sequencial) e por
  `poolside-session-extract` (suite de eval existe, skill não) — defeito pré-existente a
  corrigir no owner.

## Fase A — Aplicar vereditos já coletados (4 lotes de 20)

Regra por bead: `bd show --json` re-leitura imediata antes da escrita; mutação em lote
≤20; evidência (id, ação, fonte) anexada ao coordenador após cada lote.

1. **Lote A1 (000)**: titles/descriptions fracos (0c9o, 1ha3,
   1wjg1.4/.7/.8/.9/.10/.13/.15); defer `0ftd.3` (P2, lane 0.20); claims mantidos (0kl7,
   1wjg1, 1wjg1.11 — evidência viva); labels stale removidos.
2. **Lote A2 (020)**: remover `reval250909` dos beads SonarQube 2wjm.\*; `3cabz`
   task→bug (root, bugfix); `2nwjy` add integration-needed; `38p39` add
   partial-violation, rm phantom; titles factuais (1x0iy, 2k4ak).
3. **Lote A3 (040)**: fechar com DONE/OBSOLETE + evidência: `3zrg3`, `44he4`, `4sn0v`,
   `4vwj`, `5s0rj`; defer com data/motivo: `3wqv` (state:infrastructure), `4ndde`,
   `4o9a.1`, `4o9a.4`, `5ra33`, `6lsxp`; add `program:three-owner` (43ng, 4jhx, 5hzi,
   654e); add `lane:release-0.12` (5j70p); melhorar desc (4jhx, 5hzi, 654e).
4. **Lote A4 (080)**: fechar `ay7q` (DONE: leak verificado); remover
   `state:deferred-backlog` de abertos (c68a, d421); `bf8kx` rm bugfix; `bte4j`/`cxj9o`
   rm feature (são bugs); re-parent `cv8ys`/`cxj9o` para feature de integração ativa;
   claims mantidos (bkpj6, co1th, cu85s).

Gate entre lotes: `bd graph check`, `bd dep cycles`, query de filhos-órfãos,
`bd find-duplicates`, query bug-label. Qualquer vermelho para o lote.

## Fase B — Re-auditar ciclo 060 e cobrir população restante

1. Ciclo 060 dividido em 2 subagentes (10+10 beads) com prompt compactado (saída ≤ 2k
   tokens por bead-lote) para não estourar contexto. Aplicar como Fase A.
2. Continuar offsets 100→260 em ondas de 5 subagentes paralelos (CSVs já exportáveis
   pelo script). Aplicar vereditos entre ondas. Critérios idênticos: bugs root+bugfix
   (hotfix só P0/P1), features ≤2 tasks abertas, claims só com executor vivo, deferred
   com data/motivo, título/descrição factual.

## Fase C — Padronização de labels/bugs (sweep final)

1. Corrigir os 14 beads não-bug com label `bugfix`/`hotfix` (mbowt, mbowt.1/.2, bf8kx,
   jwpyy.4, ywet, pkfj, wgwh.2, i6nq.4, pamtx, y3qpq.4.2, wkii.17.33, wkii.17.26.2.20):
   reclassificar tipo ou remover label.
2. Query final deve retornar: 0 parented-bug, 0 bugfix-on-nonbug, 0 invalid-hotfix, 0
   closed-parent, 0 missing-bugfix em bugs abertos.

## Fase D — Claims e deferred

1. Para cada claim in_progress restante: checar worktree/branch/processo/dono; sem
   executor vivo → `bd update --unassign` + nota. Com executor vivo → manter com
   evidência.
2. Deferred: validar `defer_until` e motivo atual; sem data → defer até 2026-10-01
   (portão pós-0.12.0) ou fechar se obsoleto com evidência.

## Fase E — Sincronização GitHub (de tempo em tempo, aqui e a cada onda)

1. `bd dolt push` (sync via `refs/dolt/data`) — gravar exit e remote result no
   coordenador.
2. `git add .beads/issues.jsonl` + commit scoped + `git push` na branch de integração
   (0.12.0-dev) — fix-forward, nunca force.
3. Repetir após Fases B, C, D.

## Fase F — Landing ~/agents (governança contínua)

1. Rodar `make gen` e `make waza` **sequencialmente** (lock). Corrigir
   `poolside-session-extract` no owner: se a skill não existe, remover a suite de eval;
   se existe fora do catálogo, reposicionar.
2. Commit scoped + push em `~/agents` branch `dev`: skills, script, comando, agente,
   regra.
3. Intake .kilo→~/agents (capacidade distinta, com provenance + eval): agentes
   `test-engineer`, `frontend-specialist`(→frontend-developer); skills `csv-wrangling`,
   `data-catalog-and-discovery`, `senior-data-engineer`(→data-engineering),
   `content-research-writer`(extende article-writing). Gates `make audit/check/waza`
   verdes.
4. Remover do `.kilo` os 13 duplicados já cobertos pelo catálogo (changelog-generator,
   skill-share, artifacts-builder, agent-md-refactor, code-skeptic, code-reviewer,
   code-simplifier, architect, docs-specialist, data, test-engineer,
   frontend-specialist + README órfão). `knowledge-catalog-discovery` fica local. Commit
   scoped no flext.

## Fase G — Commits fracos (contínuo)

- Histórico publicado permanece intacto (sem rewrite/force). `wip-hier.sh` já corrigido
  (bash -n exit 0).
- Onde um SHA fraco mapeia para bead, registrar o resumo factual derivado do diff na
  nota do bead (durante Fases A/B).

## Fase H — Fechamento

1. Gate final completo (graph, ciclos, órfãos, duplicatas, labels, claims, deferred).
2. Sync final (dolt push + git push) com evidência.
3. Fechar `flext-im2my` com DONE + resumo quantitativo.

## Riscos

- Vereditos de subagente são propostas: toda escrita re-leitura + evidência; fechamento
  só com prova em nota.
- `.kilo` removal toca o projeto flext: commit scoped separado, só após intake canônico
  verde; se o operador vetar, pular Fase F.4.
- waza lock: nunca paralelizar check+waza.

## Validação

- Cada lote: exits 0 dos 5 gates; contadores antes/depois no coordenador.
- Sync: exit 0 de `bd dolt push` e `git push`, com SHA do push.
- ~/agents: `make audit/check/waza` exit 0.
