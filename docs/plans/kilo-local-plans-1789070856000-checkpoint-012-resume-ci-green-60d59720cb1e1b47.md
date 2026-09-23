# rev6 — revalidação completa + inventário + orquestração por subagentes

<!-- TOC START -->

- [Modelo de orquestração (lei desta execução)](#modelo-de-orquestracao-lei-desta-execucao)
- [Inventário vivo (verificado nesta sessão; revalidar no início da execução)](#inventario-vivo-verificado-nesta-sessao-revalidar-no-inicio-da-execucao)
  - [Worktrees](#worktrees)
  - [Subprojetos (31) — pós roll-up 20:58](#subprojetos-31-pos-roll-up-2058)
  - [Branches (root)](#branches-root)
  - [PRs](#prs)
  - [Beads do ciclo (+ bloqueios)](#beads-do-ciclo-bloqueios)
  - [Locks/leases](#locksleases)
- [Fases de execução (ordenadas; executor = coordenador + subagentes)](#fases-de-execucao-ordenadas-executor-coordenador-subagentes)
  - [R0 — Revalidação de abertura (subagente explore, ~2min)](#r0-revalidacao-de-abertura-subagente-explore-2min)
  - [R1 — flext-cli + flext-tests: integração non-FF (coordenador)](#r1-flext-cli-flext-tests-integracao-non-ff-coordenador)
  - [R2 — flext-infra: convergência com a lane (coordenador)](#r2-flext-infra-convergencia-com-a-lane-coordenador)
  - [R3 — Root: land final do ciclo (coordenador)](#r3-root-land-final-do-ciclo-coordenador)
  - [R4 — CI verde (subagentes monitoram, coordenador decide)](#r4-ci-verde-subagentes-monitoram-coordenador-decide)
  - [R5 — PR #668 (coordenador)](#r5-pr-668-coordenador)
  - [R6 — ci-matrix em TODOS os 32 (coordenador + subagente de regen)](#r6-ci-matrix-em-todos-os-32-coordenador-subagente-de-regen)
  - [R7 — dispatch manual 3 OSes (coordenador)](#r7-dispatch-manual-3-oses-coordenador)
  - [R8 — Fechamento de ciclos (coordenador)](#r8-fechamento-de-ciclos-coordenador)
  - [R9 — Track de endurecimento (subagentes por slice, multi-sessão)](#r9-track-de-endurecimento-subagentes-por-slice-multi-sessao)
- [Execução — estado capturado (21:35, rev6.1)](#execucao-estado-capturado-2135-rev61)
- [Execução — resultado final da sessão (23:5x, rev6.2)](#execucao-resultado-final-da-sessao-235x-rev62)
- [STATUS BOARD — todas as tarefas (rev6.3, 00:2x de 11/09)](#status-board-todas-as-tarefas-rev63-002x-de-1109)
- [Próximos passos imediatos](#proximos-passos-imediatos)
- [LANES DE EXECUÇÃO (rev6.4, 01:5x de 11/09)](#lanes-de-execucao-rev64-015x-de-1109)
- [Regras fixas (inalteradas do rev5)](#regras-fixas-inalteradas-do-rev5)
- [Done (rev6)](#done-rev6)
- [Fora de escopo (rev6)](#fora-de-escopo-rev6)

<!-- TOC END -->

Suppress: substitui o corpo rev5 deste arquivo. O rev5 consolidou 8 planos; o rev6
adiciona o inventário vivo completo (worktrees/branches/PRs/beads/bloqueios) e o modelo
de orquestração exigido pelo operador.

## Modelo de orquestração (lei desta execução)

- **Sessão principal = coordenadora**: mantém o estado, decide, valida evidências,
  commita/pusha nos pontos de convergência (git é o único terreno onde colisões são
  caras).
- **Subagentes rápidos executam unidades borned**: census (explore), diagnóstico isolado
  (general em clone/scratch), varreduras de superfície (explore), fix mecânico escopado
  (general com paths exatos).
- Contrato de evidência por subagente: comando, cwd, exit, output decisivo, SHA — sem
  narrativa.
- Padrões de dispatch: 1 unidade = 1 subagente; nenhum subagente toca arquivos de lane
  ativa; gen/commit/push ficam no coordenador (lock do journal é serial).
- background_process para qualquer coisa >60s, com padrão de pronto e log.

## Inventário vivo (verificado nesta sessão; revalidar no início da execução)

### Worktrees

| Worktree            | Branch                    | SHA        | Estado                                                                        |
| ------------------- | ------------------------- | ---------- | ----------------------------------------------------------------------------- |
| ~/flext             | 0.12.0-dev                | 772b5968d7 | pushado; **contém gitlink STALE do flext-infra (9cc038386)** — corrigir em R3 |
| ~/flext-release-012 | release/checkpoint-0.12.0 | 78dae0851f | conteúdo já mergeado (PR #211); remover em R8                                 |

### Subprojetos (31) — pós roll-up 20:58

| Grupo                   | Membros                      | Estado                                                                                                                                                                                                                                                |
| ----------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sincronizados           | 26 sem flext-cli/tests/infra | commit "chore: regenerate projections — ci checkout-mode normalization" + push OK                                                                                                                                                                     |
| **Divergidos (non-FF)** | flext-cli, flext-tests       | commit local feito; push rejeitado — remote avançou (outra lane pushou). Merge `--no-ff` de origin/0.12.0-dev no local, resolver, revalidar, push (R1)                                                                                                |
| Lane ativa              | flext-infra                  | tip e42584e97 (meus 2 fixes + 3 commits da lane); worktree com WIP dela (Makefile, pyproject.toml, \_utilities/**init**.py, tests/unit/**init**.py, + possíveis conform.py) + projeções ci.yml/Makefile não commitadas — esperar/absorver a lane (R2) |

### Branches (root)

- `0.12.0-dev` (ativa, = origin após pushes) · `release/checkpoint-0.12.0` (mergeada;
  deletar em R8) · remotes: origin + infra-origin/0.12.0-dev,
  infra-origin/fix/standalone-uv-sources-single-writer (verificar órfã em R8)

### PRs

- flext root: **0 abertos** (checado 20:44)
- flext-infra: **#668** `wip:release/checkpoint-0.12.0` → 0.12.0-dev, diff vazio,
  mergeable UNKNOWN (R5)
- Demais repos: verificar no início da execução (gh pr list; presumido 0)

### Beads do ciclo (+ bloqueios)

| Bead                        | Tipo/Prio       | Estado/Bloqueio                                                            |
| --------------------------- | --------------- | -------------------------------------------------------------------------- |
| flext-yirgp (mãe/epic)      | integração      | aberta; 5 dependentes p0                                                   |
| flext-mphw1                 | bug p0          | mise-mode — **fix pousado** (f4b4f3f11+e42584e97); fecha com CI verde (R4) |
| flext-maygx                 | bug p1          | lint subprocess storm >timeout; fix = batch por tool (track R9)            |
| flext-cpkk                  | CI green        | aguarda CI do tip novo (R4)                                                |
| flext-5k9r7                 | setup/guard     | aguarda CI flext-cli pós-merge (R1→R4)                                     |
| flext-9pia0 / r8lsm / bkpj6 | p0 lanes ativas | não reclamar escopo; só ponte de evidência                                 |
| flext-0suy3, flext-tvenh    | task/bug        | 0suy3 filed; tvenh = deps modernize × uv_constraint_dependencies (R9)      |

### Locks/leases

- Journal codegen `.git/flext-infra-codegen-transaction-journal.json(.lock)`: `ps` antes
  de gen; zombie comprovadamente órfão = matar (precedente aprovado); vivo = esperar.
- Nenhum rebase wedged conhecido agora (o de 17:19 foi resolvido pela própria
  maquinaria).

## Fases de execução (ordenadas; executor = coordenador + subagentes)

### R0 — Revalidação de abertura (subagente explore, ~2min)

Census refresh: `gh pr list` nos 32 repos ativos, `git status -sb` nos 31 membros +
root, `bd list` (blockers de yirgp), `gh run list` (flext + infra, branch 0.12.0-dev).
Retorna tabela; coordenador decide se R1..R8 mudam de ordem.

### R1 — flext-cli + flext-tests: integração non-FF (coordenador)

1. Por membro: fetch; `git merge --no-ff origin/0.12.0-dev` (fix-forward; nunca rebase).
2. Conflito → resolução adotando o mais novo (projeções regeneráveis: re-gen resolve;
   código: união semântica).
3. `make gen` no root depois (fixed-point absorve qualquer drift de projeção).
4. Push FF. Evidência na bead.

### R2 — flext-infra: convergência com a lane (coordenador)

1. Se lane pousou WIP: fetch + merge no-ff se divergiu; as projeções (ci.yml/Makefile)
   do worktree entram no meu gen do R3.
2. Se lane parada/órfã (ps sem processo + WIP velho): adjudicar fix-forward — commit das
   projeções por paths, WIP de código preservado e classificado (bd).
3. Gitlink root do infra: 9cc038386 → tip real (corrige o stale do meu commit
   772b5968d7).

### R3 — Root: land final do ciclo (coordenador)

1. `make gen` até fixed-point (absorve R1/R2).
2. Commit por paths: 31 gitlinks + root Makefile +
   scripts/{hooks,workspace}/**init**.py + uv.lock. Push.
3. `make setup/check/test` (testmon) — exit por gate; vermelho → dono (ver R9 para os
   conhecidos).

### R4 — CI verde (subagentes monitoram, coordenador decide)

1. `gh run list/view` no tip novo (flext + infra + cli + tests).
2. Esperança: job `ci` verde (prova mphw1: normalização no runner). Vermelho →
   `gh run view --log-failed` → subagente diagnostica → fix no dono → re-land.
3. Fechar: mphw1 (com run verde), cpkk, 5k9r7 (se CI cli verde).

### R5 — PR #668 (coordenador)

Diff vazio: `gh pr merge 668 --merge`; recusado → close + comentário de equivalência de
árvore.

### R6 — ci-matrix em TODOS os 32 (coordenador + subagente de regen)

1. codegen.yaml: restaurar `workspace-member` nos profiles de ci-matrix.yml + 5
   Dockerfiles (~L1328/L1795); comentário com a regra do operador.
2. `test_codegen_ci_matrix.py`: travar INCLUSÃO (inverte o lock de 78830c7db).
3. `make gen` → 29 membros ganham o arquivo; land em slices (script fleet-rollup.sh
   reaproveitado — guardas de lane).

### R7 — dispatch manual 3 OSes (coordenador)

`gh workflow run ci-matrix.yml --ref 0.12.0-dev` em flext-infra, flext-core, flext;
watch até success; falha → template dono → re-land → re-dispatch.

### R8 — Fechamento de ciclos (coordenador)

1. Worktree flext-release-012 removido; branch release/checkpoint-0.12.0 local+remota
   deletada (pós #668).
2. infra-origin/fix/standalone-uv-sources-single-writer: adjudicar (mergeada? órfã?).
3. Stashes (root@0 pr211, infra@0/@1): recovery-ref documentado na bead — nunca pop.
4. Beads: yirgp force-close se dependentes ok; senão estado real. Memória kilo (lições:
   umask runner, rebase-wedged adopt, roll-up script).

### R9 — Track de endurecimento (subagentes por slice, multi-sessão)

1. maygx: batch lint por tool (1 processo/tool, N paths) — protected_edit_linting.
2. namespace (~1385)/loc-cap: slices por módulo com ast-grep + `make mod`; gates verdes
   por slice.
3. Exterminar `rules/class-nesting-mappings.yml` → descoberta SSOT automatizada.
4. tvenh: deps modernize vs uv_constraint_dependencies no dono.
5. Testes lentos de setup (T4): diagnóstico em clone isolado.

## Execução — estado capturado (21:35, rev6.1)

**Landed/pushado:**

- flext-infra `b616988c9..e42584e97`: fix ci modes (f4b4f3f11: normalize step + mensagem
  observado/canônico + contrato teste) + docs fixture (e42584e97).
- Root `772b5968d7`: projeção ci.yml + gitlink infra (STALE 9cc038386 — corrigir em R3).
- R1: flext-cli `267363ce` (merge no-ff absorveu darwin process-group lane) ·
  flext-tests `13263b9` (theirs para projeções geradas).
- Roll-up 20:58: 28 membros com projeções commitadas+pushadas.

**Segunda causa raiz descoberta (CI pós-fix ainda vermelho):**

- O passo Normalize rodou no runner (20:57:47) e o conform falhou igual (20:59:21) → o
  drift vem do **checkout de submódulos DENTRO do make setup** (log: "Submodule
  'flext-api': checked out" 20:58:00, sob umask 002).
- Fix aplicado (não commitado): `submodule_setup_recipe.j2` — `umask 022` no início da
  receita de provisionamento.

**Terceira causa raiz (members standalone):**

- CI usa `uv sync --locked` → locks stale pinam flext-core SHA antigo
  (structlog>=26.1.0) × cli `structlog<26` → insatisfatível (flext-cli 267363ce ci
  failure).
- Fix: `make gen` por membro (unlocked+refresh re-resolve o lock) → commit uv.lock →
  push. Script em preparação (R1c).
- flext-tests: falha separada e transitória (mise install tools erro no runner) → re-run
  após lock land.

**Reds do suite flext-infra (parciais, random+maxfail mascaram):**

- auditor fixture beads.yaml → FIXADO (e42584e97).
- layout_gitignore tracked-in-ignored-dir → **FIXADO agora** (`_git/scope.py`:
  check_ignore nunca veta ls-files; 2 curto-circuitos removidos; dono: flext-e3708).
- namespace timeout → flext-maygx (track R9).
- validate scan + detector identity + main_tests init → em diagnóstico (contagem total
  rodando).

**Beads (lint 100% no ciclo):** mphw1✓ maygx✓ cpkk✓ tvenh✓ + novas: didi7 (R6
ci-matrix), ywu2d (R9 epic endurecimento), e3708 (layout bug), ml7gk (PR #668). yirgp
segue mãe; 9pia0/r8lsm/bkpj6 lanes ativas intocadas.

**Ajuste de orquestração:** subagentes nesta sessão NÃO têm shell (deny global) →
coordenador executa todo shell/git/bd/gh; subagentes ficam para edição/análise de
arquivos. Padrão de scripts com guardas em scratch para loops de frota.

## Execução — resultado final da sessão (23:5x, rev6.2)

**Corrigido e provado em runtime (root CI avançou através destes gates):**

1. Mise mode noncanonical → ci.yml.j2 normalize step + submodule umask 022 (f4b4f3f11,
   99a9c9504) — mode gate PASSA no runner.
2. Invalid TOML em flext-api/.mise.toml + .beads/config.yaml (conflict markers
   commitados por merge alheio) → resolução canônica (35274468).
3. Mesma corrupção em flext-auth → resolvida (e746a86d).
4. click floor 8.4.2 re-mutado pelo replay 1b575a329 → restaurado 8.3.3 na SSOT (piso ≤
   teto meltano; flext-tvenh/0suy3).
5. Diagnóstico de drift: e3882e5fe — drift gates imprimem unified diff limitado
   (committed vs rendered + modes).

**Landed/propagado:** R1 cli `267363ce`/tests `13263b9`/api `35274468`/auth `e746a86d`
(merges no-ff) · roll-ups 28+31 membros · locks R1c 31/31 OK · root
`f98434ee24`→`e8370d5695` (gitlinks sempre atualizados) · PR #668 MERGED · ci-matrix
32/32 + dispatch rodando · worktree release-012 + branch release deletados · R8 limpo.

**Bloqueador restante (isolado com diff exato):** root lazy-init render diverge por
ambiente — runner 11 facades vs local 5 (superfície de membros: tips vs gitlinks). Bead
p0 `flext-b3xmn` com diff, passos, direção de fix (SSOT-declarar a lista, remover
dependência do estado instalado). Próxima slice: implementar o derivation SSOT-driven,
regenerar os 4 facets, land, CI green.

**Matrix (R7):** pernas alpine/macos/ubuntu falham com defeitos de ambiente próprios
(mkdir '/.flext-runtime' sem HOME; bootstrap exit 2) — fichados sob epic `flext-ywu2d`.

**Beads do ciclo (lint 100%):** mphw1✓ maygx✓ cpkk✓ tvenh✓ didi7✓ ywu2d✓ e3708✓
ml7gk✓(closed) b3xmn✓ · mãe yirgp aberta (dependentes p0 ativos).

## STATUS BOARD — todas as tarefas (rev6.3, 00:2x de 11/09)

| #   | Tarefa                                                                                | Fase     | Status                                                                                                                                                                                                                                                                                                    | Evidência                                                                                           |
| --- | ------------------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| 1   | Mise mode noncanonical (umask 002)                                                    | F0       | ✅ **CORRIGIDO E PROVADO**                                                                                                                                                                                                                                                                                | ci.yml.j2 normalize + umask 022 recipe; root CI passou o mode gate (runs 34540625063+, 34543042154) |
| 2   | Invalid TOML (conflict markers commitados)                                            | F0       | ✅ corrigido                                                                                                                                                                                                                                                                                              | flext-api `35274468`, flext-auth `e746a86d`                                                         |
| 3   | click floor 8.4.2 re-mutado                                                           | F0       | ✅ corrigido na SSOT                                                                                                                                                                                                                                                                                      | 8.3.3 restaurado; gen 3× verde                                                                      |
| 4   | Drift gates cegos (só paths)                                                          | F0       | ✅ melhorado                                                                                                                                                                                                                                                                                              | `codegen_file_drift_report` (e3882e5fe) — diff unified no failure                                   |
| 5   | PRs abertos                                                                           | R5       | ✅ **PR #668 MERGED** (22:24Z); root: 0 abertos                                                                                                                                                                                                                                                           | bead ml7gk closed                                                                                   |
| 6   | ci-matrix em todos os projetos                                                        | R6       | ✅ **32/32 presentes** (censo pós-gen) + catálogo/teste já travam inclusão                                                                                                                                                                                                                                | censo script; bead didi7                                                                            |
| 7   | Dispatch manual 3 OSes                                                                | R7       | ✅ disparado 3 repos (2×); pernas falham = bugs de plataforma                                                                                                                                                                                                                                             | runs 34540691143/93441/96313; epic ywu2d                                                            |
| 8   | Frota: locks refresh                                                                  | R1c      | ✅ 31/31 OK (setup canônico)                                                                                                                                                                                                                                                                              | r1c v2: OK:31 FAILED:none                                                                           |
| 9   | Frota: integração non-FF                                                              | R1       | ✅ 31/31 (merges no-ff, zero conflitos)                                                                                                                                                                                                                                                                   | fleet-integrate: OK:31                                                                              |
| 10  | Gitlinks do root                                                                      | R3       | ✅ sincronizados aos tips                                                                                                                                                                                                                                                                                 | root `5257fd4b38` pushed                                                                            |
| 11  | Worktree/branches release                                                             | R8       | ✅ removidos/deletados                                                                                                                                                                                                                                                                                    | worktree list = só root                                                                             |
| 12  | Beads do ciclo lint 100%                                                              | F0       | ✅ 9/9                                                                                                                                                                                                                                                                                                    | mphw1 maygx cpkk tvenh didi7 ywu2d e3708 ml7gk✅ b3xmn                                              |
| 13  | Lazy-init drift 5↔11 facades                                                         | —        | 🔴 **diagnóstico completo, fix pendente** — runner renderiza 11 facades (módulos inexistentes = runtime-broken) mesmo com tudo sincronizado; regressão entrou na cadeia de merges da lane (360c8b4c1→13dd5c6c6); escopo do fix: `_lazy_init_planner_*.py` (derivar letras dos módulos próprios do pacote) | bead b3xmn com diff completo + run 34548077920                                                      |
| 14  | Pernas matrix (alpine HOME/macos/ubuntu)                                              | R7       | 🔴 bugs de plataforma reais                                                                                                                                                                                                                                                                               | epic ywu2d com evidência                                                                            |
| 15  | Reds do suite infra (namespace timeout, validate scan, detector identity, main_tests) | R9       | 🔴 track de endurecimento                                                                                                                                                                                                                                                                                 | maygx + epic ywu2d; contagem total pendente                                                         |
| 16  | class-nesting-mappings.yml exterminio                                                 | R9       | ⏳ epic ywu2d                                                                                                                                                                                                                                                                                             | ordem do operador registrada                                                                        |
| 17  | tvenh deps×constraints                                                                | R9       | ⏳ bead p0                                                                                                                                                                                                                                                                                                | —                                                                                                   |
| 18  | Sweep 238 beads (vereditos/labels)                                                    | paralela | ⏳ lane dedicada                                                                                                                                                                                                                                                                                          | fora deste ciclo                                                                                    |

## Próximos passos imediatos

1. CI do root em `5257fd4b38` — se conform passar, audit/check/test seguem; reds
   conhecidos tratados como beads 14–17.
2. Fechar b3xmn com CI verde; pernas do matrix por bug individual.
3. Root land final + relatório de closure na yirgp.

## LANES DE EXECUÇÃO (rev6.4, 01:5x de 11/09)

**Lane dedicada b3xmn** (worktree `~/flext-b3xmn`, branch
`fix/lazyinit-facade-divergence` @ `c8a042e930`):

- Repro do drift **CONFIRMADA em bench isolado** (submódulos nos gitlinks + venv locked)
  — o drift é determinístico do estado repo+venv; o workspace principal renderizava 5
  por estado stale local (venv antigo pré-lock-sync).
- Em curso: `make setup` + `make conform` no bench (sequência exata do runner) → repro
  com introspecção local disponível.
- Correção anti-hardcode pousada nesta lane: `f1c45bf1e` (OPERATIONAL_MODULES derivado
  de OPERATION_FACADES — ordem do operador), adotado e ampliado pela lane ativa
  (`a0effff42`: shape por AST, nunca listas) + `d68b5f3fd`/derivados (mode-only report
  com observed/desired).
- Ordem permanente do operador registrada: listas de bypass/afrouxamento e hardcodes
  (incl. absolutos/fora-do-repo) = extermínio; regras devem ser completas e
  generalizadas; vale PARA TESTS.

**Demais lanes ativas observadas**: namespace-rules (infra.yaml, validate/base.py), deps
modernize, docs/plano. Todas respeitadas via paths explícitos + gitlink-sync contínuo.

## Regras fixas (inalteradas do rev5)

único mutável; verbos canônicos; testmon; commit por paths; fix-forward sem
reset/rebase/force-push; ps antes de gen; lane ativa = território dela; subagentes não
tocam git de escrita; evidência = comando/cwd/exit/output/SHA.

## Done (rev6)

1. R0–R8 verdes com evidência gravada nas beads (mphw1 fechada com CI verde).
2. 32 repos sincronizados; ci-matrix presente em todos; dispatch 3-OS verde.
3. Worktrees/branches/PRs/stashes coerentes; yirgp fechada ou dependências documentadas.
4. R9 encabeçado com maygx classificado e primeira slice pousada (se janela da sessão
   permitir).

## Fora de escopo (rev6)

Publicação PyPI; lanes p0 ativas (9pia0/r8lsm/bkpj6); sweep 238 beads (track paralela
linkada); ADR-014/rope.
