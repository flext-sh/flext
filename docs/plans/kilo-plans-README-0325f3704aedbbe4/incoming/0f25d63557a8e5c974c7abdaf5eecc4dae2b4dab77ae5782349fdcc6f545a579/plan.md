# Adendos — rope-modernize / flext-infra

Estes adendos complementam o plano coordenador
[`../1789582482542-rope-modernize-phase1-plan.md`](../1789582482542-rope-modernize-phase1-plan.md).
Eles registram proveniência, cronologia e reconciliação; não substituem Gas City
Beads como tracker nem os comandos runtime como evidência.

## Convenção de evidência

- **CURRENT** — confirmado no source/CRG do tree atual.
- **COMMAND** — comando, exit/saída ou SHA visível no transcript histórico.
- **HANDOFF** — afirmação de repasse ainda não confirmada no tree atual.
- **HISTORICAL** — foi verdadeiro naquele horário, mas não valida o SHA atual.
- **PENDING** — precisa ser relido via `direnv`/Make/Git no início da execução.

## Índice

- [`claude-chronology-2026-09-16.md`](claude-chronology-2026-09-16.md) — horários e avanços das sessões Claude paradas.
- [`current-state-conflicts-2026-09-16.md`](current-state-conflicts-2026-09-16.md) — aceite/rejeição dos claims e conflitos entre checkouts.
- [`cross-plan-coordination-2026-09-16.md`](cross-plan-coordination-2026-09-16.md) — relação com planos Kilo concorrentes e divisão de responsabilidade.
- [`beads-lanes-prs-2026-09-16.md`](beads-lanes-prs-2026-09-16.md) — estado histórico e releitura obrigatória de tracker/landing.
- [`1789582669805-claude-repass-2026-09-16.md`](1789582669805-claude-repass-2026-09-16.md) — repasse e adjudicação datados do plano fleet-wide `1789582669805`; não é posição runtime atual.

## Âncoras atuais

- Super `rope-modernize`: `89fc3096335b53d81cdc52afe7cc8c785514bdb2`.
- Gitlink de `flext-infra` registrado no super: `96c52f1d6e671f5403282e7764b29d29cc061c15`.
- Checkout efetivo de `flext-infra`: `d83ccc6160c1862e7443cf87e5fce8a6855ce559`,
  com WIP concorrente em docs e source; esse checkout ainda não é uma projeção
  aceita pelo superprojeto.
- Plano coordenador: `.kilo/plans/1789582482542-rope-modernize-phase1-plan.md`.
- Análise histórica Ruff/codemod:
  `.kilo/plans/1789582669805-flext-infra-ruff-codemod-repair.md`.
- Plano cooperativo do checkout principal:
  `/home/marlonsc/flext/.kilo/plans/1789582508056-flext-infra-runtime-modernization.md`.

Estas âncoras foram relidas em 2026-09-17. Revalidá-las antes de cada mutação;
mudança de HEAD, gitlink ou WIP invalida conclusões estruturais sobre paths
sobrepostos. Estado executável e aceite continuam no Gas City Bead
`flext-3rld2`, não nestes adendos.
