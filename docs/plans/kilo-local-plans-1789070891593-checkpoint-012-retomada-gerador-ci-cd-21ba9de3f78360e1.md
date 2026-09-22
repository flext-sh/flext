# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md

<!-- TOC START -->

- [Estado real (verificado agora — não repetir diagnóstico)](#estado-real-verificado-agora-nao-repetir-diagnostico)
- [Fases (código-mode, em todo mutável, verbo canônico root/member)](#fases-codigo-mode-em-todo-mutavel-verbo-canonico-rootmember)
  - [F1 — flext-infra: fechar a lane do gerador](#f1-flext-infra-fechar-a-lane-do-gerador)
  - [F2 — Root: fixed-point + gates locais](#f2-root-fixed-point-gates-locais)
  - [F3 — Land membros + superproject (slices ~8)](#f3-land-membros-superproject-slices-8)
  - [F4 — CI verde no tip (bloqueador central)](#f4-ci-verde-no-tip-bloqueador-central)
  - [F5 — Ciclos PR/branch/worktree](#f5-ciclos-prbranchworktree)
  - [F6 — cd-infra: dispatch manual nos 3 OSes](#f6-cd-infra-dispatch-manual-nos-3-oses)
  - [F7 — Beads + regras (fechamento contínuo)](#f7-beads-regras-fechamento-continuo)
- [Done](#done)
- [Fora de escopo](#fora-de-escopo)
- [Riscos](#riscos)

<!-- TOC END -->

(Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there

# Checkpoint 0.12.0 — consolidação final: land residual + CI verde + cd-infra +

fechamento de ciclos

Rev4 (consolida rev3 + sessões "Finalização release 0.12.0" e "Fixing make setup") ·
Bead-mãe: `flext-yirgp` · Integração: `origin/0.12.0-dev`

## Estado real (verificado agora — não repetir diagnóstico)

1. **Já poussado**: PR #211 merged (`ec347f3867` = origin tip); setup reparado (click
   8.3.3); feature do gerador commitada e poussada em flext-infra (`b616988c9`
   auto-dispatch de script verbs, `1b575a329` structlog floor, `2e92a92ad` fixtures) —
   infra HEAD = origin tip; `flext-sikjh` fechada (SSH identity `172e363a4`); skills
   `~/agents` sincronizadas com a fonte canônica (`~/agents`, RC-IDENTICAL).
2. **flext-infra — drift residual não-commitado (4 arquivos, +30/-3)**:
   - `Makefile`: projeção com drift (header `make gen`, define `_dispatch`, blank-lines
     fantasmas).
   - `pyproject.toml`: linha `structlog>=25.5.0,<27` (inline `<26` — igual ao padrão
     hand-edit do `stash@{0}`; SUSPEITO, o gen fixed-point é o árbitro) + reformato
     tomlsort do ruff per-file-ignores (legítimo).
   - `_utilities/__init__.py`: lazy export `MypyDarwinSupervisor` (módulo existe) —
     export legítimo faltando.
   - `tests/unit/__init__.py`: lazy export `policy_violation_project` (fixture existe em
     `tests/unit/fixtures.py:224`) — legítimo.
3. **Root @ `ec347f3867`**: Makefile + `scripts/{hooks,workspace}/__init__.py` +
   `uv.lock` modificados; 31 membros `m` (drift de projeção Makefile, sem commits locais
   além de origin — flext-core 0 ahead); gitlink infra `MM` (staged defasado vs HEAD
   atual).
4. **CI do tip VERMELHO (bloqueador central, preexistente em 71ebd/fcf2ae/ec347f)**:
   `published Mise artifact mode is noncanonical: flext-api/.mise.toml` — falha no step
   audit (`make conform` → `_builtin_gen_check`, Makefile:1058). Fresh checkout tem
   modos corretos (0644); algo entre checkout e gen_check no runner altera o modo. Root
   cause NÃO encontrada; repro em clone isolado foi iniciada e morreu com a sessão.
5. **Pendências de ciclo**: PR flext-infra #668 aberto (diff vazio, head==base);
   worktree `flext-release-012` + branch `merge/pr211b` lingering (conteúdo já
   integrado); cd-infra 3-OSes nunca dispatchado; beads: `flext-yirgp` aberta bloqueada
   por 5 p0 (`9pia0`/`r8lsm`/`bkpj6` em progresso por lanes ativas — coordenar, não
   duplicar; `5k9r7` aguarda CI da flext-cli; `cpkk` = CI verde).
6. **Não tocar**: `stash@{0}` do infra (nunca pop), ADR-014 não-rastreado (lane rope),
   WIP de lanes ativas (rope/deps) — sempre commit por paths exatos.

## Fases (código-mode, em todo mutável, verbo canônico root/member)

### F1 — flext-infra: fechar a lane do gerador

1. `make gen` (cwd flext-infra) até fixed-point — **árbitro** do drift: o que o gen
   mantém é canônico (exports, tomlsort); o que ele reverte era drift (inline `<26`,
   blanks).
2. Corrigir no dono qualquer não-idempotência que o fixed-point expuser (template
   `Makefile.j2`: mover `\n` incondicionais para dentro dos `{% if %}`).
3. `make gen` + `make test` (cwd infra); falha → corrigir no dono.
4. Commit por paths exatos (Makefile, pyproject.toml,
   `src/flext_infra/_utilities/__init__.py`, `tests/unit/__init__.py`) + push FF.

### F2 — Root: fixed-point + gates locais

1. `make gen` (cwd root) até 2ª rodada sem diff (exit 0).
2. `make gen` → exit 0.
3. `make gen` + `make test` (testmon) → registrar exit por gate.

### F3 — Land membros + superproject (slices ~8)

1. Por membro com drift: commit paths exatos (`Makefile`, `pyproject.toml`, `uv.lock` se
   mudou) + push FF.
2. Superproject: commit gitlinks (31 + infra no HEAD real) + root
   `Makefile`/`uv.lock`/`scripts/{hooks,workspace}/__init__.py` + push FF.
3. Proibido: `git submodule update`, `git add -A`, reset/restore/rebase/force-push, pop
   do stash.

### F4 — CI verde no tip (bloqueador central)

1. Reproduzir o audit em clone isolado do tip: replicar os steps do workflow até
   `make conform` e isolar onde o file-mode do `flext-api/.mise.toml` diverge de 0644
   (suspeitos: escrita do gen no runner, umask do runner, ordem setup→audit).
2. Corrigir no dono (writer do artefato / verificador de modo em flext-infra —
   publicação via `u.Infra.publish_file_plans` preserva mode; garantir que o mode
   publicado seja o do spec 0644 sempre, não o do filesystem local).
3. Re-land (F1–F3 se necessário) e verificar no novo SHA: `ci`, `release-plan`,
   merge-guard, SonarCloud — verde.
4. `flext-5k9r7`/`flext-cpkk`: com CI verde, registrar evidência e fechar o que a
   evidência provar.

### F5 — Ciclos PR/branch/worktree

1. PR flext-infra #668 (diff vazio): `gh pr merge --merge`; se GitHub recusar, close com
   comentário provando head==base.
2. Worktrees/branches já integrados (`flext-release-012`, `merge/pr211b`, residuais de
   merge): verificar árvore ≡ tip → `git worktree remove` + deletar branches
   locais/remotas mescladas. Nada de lane ativa é apagado.

### F6 — cd-infra: dispatch manual nos 3 OSes

1. `gh workflow run ci-matrix.yml --ref 0.12.0-dev` em flext-infra, flext-core, flext
   (root).
2. `gh run watch` até success em windows/macos/distro-matrix.
3. Falha de plataforma → corrigir no template dono → regen → re-land → re-dispatch.
   Nunca desativar job.

### F7 — Beads + regras (fechamento contínuo)

1. `flext-yirgp`: evidência por fase (comando, cwd, exit, output decisivo, SHA) + branch
   de integração; fechar quando os 5 dependentes p0 permitirem (forçar close destrói
   execution truth — proibido).
2. Lanes p0 ativas (`9pia0`/`r8lsm`/`bkpj6`): coordenar via board/beads, adotar tips
   delas por merge no-ff quando prontas; nunca duplicar.
3. `~/agents` (fonte canônica `~/agents`): portar lições deste ciclo (mode-noncanonical
   root cause, fixed-point como árbitro de drift) na mesma change.

## Done

- infra + 31 membros + superproject pushed FF; gen fixed-point; setup/check/test exit 0
  local.
- CI verde no tip novo (`ci`/`release-plan`/merge-guard/Sonar); PR #668 fechado.
- ci-matrix verde nos 3 OSes nos 3 repos representativos (run IDs + URLs na bead).
- Worktrees/branches integrados removidos; beads com evidência e status correto.

## Fora de escopo

Implementação das lanes p0 ativas (`9pia0`/`r8lsm`/`bkpj6` em progresso alheias),
ADR-014 não-rastreado, publicação PyPI, backlog 0.20.

## Riscos

| Risco                                                        | Contramedida                                                                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| Lane concorrente muta o root durante F2/F3                   | Commit por paths; retry contra index.lock; nunca matar lane viva                                                    |
| Repro do mode-noncanonical não reproduz localmente           | Instrumentar o verificador (flext-infra) para emitir mode esperado vs observado no runner; log do CI como evidência |
| `structlog<26` inline ser canônico novo (commit `1b575a329`) | Gen fixed-point + `make deps` decidem; nunca hand-revert                                                            |
| Runners Windows custosos                                     | Dispatch só nos 3 repos representativos                                                                             |
