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
2. Root `make gen APPLY=Y` fixed point → commit das 5 projeções do super + gitlinks → push.
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
- **Gate final:** `make check APPLY=Y` 100% verde + `make test` testmon verde.
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
