# 00-index — Handoff «FLEXT Conformance Sweep» (2026-09-11)

> Fonte única de continuidade. Nova sessão: leia ESTE índice, depois `handoff.md`,
> depois o plano vivente e as beads — nunca restaure transcript/cursor como autoridade.

## 1. Documentos autoritativos (nesta ordem)

| Caminho | Papel |
|---|---|
| `../2026-09-11-flext-conformance-sweep.md` | **Plano vivente**: §0 autoridade · §1 feito+evidências · §2 autocrítica A1-A9 · §3 produção D1-D6 · §4 TODO v3 (real) · §5 beads reais · §10 fatos de automação · §11 proposta Onda-P · §12 pedidos ao operador |
| `handoff.md` | Prompt de retomada desta sessão (contexto, ambiente, método) |
| `audit-2026-09-11.md` | **Auditoria documento×código** (governance-audit): drifts P1 (AGENTS.md regra 17), rascunhos untracked sem ADR, vínculo Onda-P→RC epic R4 — tabela com dono-corrige |
| Beads (tracker `flext-*`) | Estado vivo de execução — verifique com `bd show`, jamais de memória |
| `/home/marlonsc/agents/skills/project-wide/coordination/fleet-lane-discipline/SKILL.md` | Lei da lane + stack de automação (commits `c387a9c5`, `3dd920fa`) |
| `docs/guides/migration-to-v0.13.0.md` | Contrato breaking (APPLY zero-variable) do release v0.13.0 |

## 2. Como remontar os TODOs (método, não cópia)

1. `env -u BEADS_DOLT_SERVER_DATABASE bd list --status=open` (nunca herdar DB de outra sessão).
2. Para cada cand=eira relevante (`vo335, 5k9r7, 2h0un, 3cabz, 9wwed, gxgqp`): `bd show <id>` e ler o status do HEADER (`OPEN/IN_PROGRESS/CLOSED/SUPERSEDED`).
3. Cruzar com §4 do plano vivente (tabela v3) — divergência entre bead e plano = conserta o PLANO (bead é estado; plano projeta).
4. Só então reivindicar UM próximo bead (§4 linha 1) e declarar objetivo/gates/stop.

## 3. Como as conclusões foram alcançadas (trilha)

- Toda afirmação do §1 do plano nasceu de comando medido (grep/pip/find/merge-base) registrado em bead com **4 evidências** (registered state, git history, measured reality, integrated code) — lei `rules/…/beads-verification` + ADR-0007.
- Automatização: fatos F1–F8 (§10) medidos em código-fonte dos donos (`codemod_rules.py`, Makefile, binários `code-review-graph`/`scope`).
- Autocrítica vinda do erro real (pouso com CI pending, sed em bulk, fechamento de bead com gen vermelho) — §2, cada item com contramedida.
