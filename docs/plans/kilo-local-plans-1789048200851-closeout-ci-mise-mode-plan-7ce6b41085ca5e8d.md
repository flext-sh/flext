# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md (Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there

# Plan: checkpoint-0.12.0 closeout — CI verde (mise artifact mode) + p0 fichadas

## Contexto (estado real, evidenciado hoje 2026-09-10)

- PR #211 MERGED: `ec347f3867` em `origin/0.12.0-dev`; root local FF no merged tip.
- `make setup` GREEN local (EXIT=0, 281 pkgs; floor `click>=8.3.3` ≤ ceiling meltano
  `<8.4`).
- 31 members + superproject pushados (projeções beads-header + gitlinks).
- Regras canônicas em `~/agents` (fonte) já portam: release-closeout (merge playbook,
  concorrência, beads evidence), workspace-toolchain (floor≤ceiling); derivado
  `~/.agents` IDÊNTICO.
- Beads: `flext-sikjh` FECHADA (fix `172e363a4` + 5 tests passed). `flext-yirgp` aberta
  com 5 p0 dependentes.
- Bead nova `flext-0suy3` (floor writer ceiling-aware).

## Problema a resolver (bloqueia CI verde)

CI do merged tip `ec347f3867` = FAILURE no step `CI=Y make conform`:
`published Mise artifact mode is noncanonical: flext-api/.mise.toml` — em
`_mise_artifacts_verification.py:690` (`current.value.mode != required_mode`, spec
0o644; fail assíncrona pós `[OK] conform ×32`, no `_builtin_gen_check` do
Makefile:1058).

Diagnóstico já feito:

- Git file-modes OK em todos os 31 members (100644/100755 conforme `PUBLICATION_SPECS`).
- Clone fresco: modos perfeitos (644/755/644) → checkout não é a causa; algo entre
  `setup`/`conform` e o `gen_check` altera/atualiza o estado no runner.
- Local não reproduz com o mesmo quick check (verify-fixed-point verde hoje); repro em
  execução em clone isolado `/tmp/kilo/ci-repro` (bg: `CI=Y make setup` +
  `CI=Y make conform`).
- Outras pendências: lane `gen` em loop no root (timeout 900) — não colidir; 4 p0
  restantes (9pia0/r8lsm/bkpj6 lanes ativas; 5k9r7 aguarda CI).

## Plano (ordem de execução)

### Fase 1 — Reprodução e root cause do failure de CI (bloqueio #1)

1. Ler `/tmp/kilo/repro-conform.log` do background `bgp_08cda61c7001Cl2yl3P96AgDAK`
   (clone isolado).
   - Se EXIT=0: não reproduz local → runner-specific; inspecionar log do GH com foco em
     `st_mode`/umask do runner e comparar byte/mode do arquivo publicado pelo `conform`
     no runner (passos anteriores do job).
   - Se falhar com o mesmo erro: reproduzido — depurar o `read_state(...).value.mode` do
     `.mise.toml` pós-conform no clone (`stat` + diff com o esperado) e isolar o
     call-site do publish que grava mode ≠ 0o644 no `_mise_artifacts_*`/`_codegen`
     (presumível owner: staging/copy do `before` com shutil.copymode herdando mode do
     journal/staging, ex. 0o600/0o755).
2. Fix na RAIZ (owner `flext-infra` codegen publish path): garantir `permission_mode`
   explícito do spec em todo path de publicação/`update` — sem bypass/allowlist.
3. Teste de regressão no test file de mise artifacts (contrato: published mode == spec,
   qualquer umask).
4. `make gen` (owner lane: aguardar loop acabar) → commits por paths explícitos → push
   com retry (40×15s) em `0.12.0-dev` (members ≠ root separados).
5. CI reroda: CI do tip deve ficar GREEN. Atualizar beads `cpkk` e `5k9r7` com a
   evidência (close `5k9r7` se CI flext-cli verde).

### Fase 2 — Fechamento do ciclo de pendências

1. `flext-5k9r7`: close se CI do flext-cli no novo tip verde (evidência gh run).
2. `flext-cpkk` (CI green): status update com run links; close quando todos os checks do
   `0.12.0-dev` verde.
3. `flext-9pia0`, `flext-r8lsm`, `flext-bkpj6`: pertencem a lanes ativas — NÃO reclamar
   escopo; apenas registrar ponte (evidência no `flext-yirgp`).
4. `flext-yirgp`: close com --force SE os 5 dependentes fechados; caso
   contrário落地 status real documentado (integração landed, dependências ativas).

### Fase 3 — Regras em `~/agents/` (fonte canônica) + fechamento

1. Atualizar `skills/agent-wide/governance/release-closeout/SKILL.md` (fonte `~/agents`)
   com o padrão novo aprendido: reprodução de CI failure em clone isolado e o ciclo
   `confoma→gen_check` de file-mode; sincronizar derivado `~/.agents` (identidade
   byte-a-byte; make gen do repo agents se for o SSOT do projection).
2. Commit/push no repo `agents` (branch `feat/reval250909-adoption` — o passeio
   fix-forward da lane ativa).
3. Memória kilo: salvar lição do CI mode-check + repro local e o estado final do ciclo.

## Critérios de validação (real, sem erros)

- `CI=Y make setup && make conform && make audit && make check && make test` EXIT=0 no
  tip pós-fix (mínimo: setup + conform/audit VERDES em clone fresco e no root).
- CI GitHub do `0.12.0-dev` no novo SHA: job `ci` SUCCESS.
- Todos os modos publicados = specs (`0o644`/`0o755`) em 32 projetos — verificação
  `git ls-files -s` auditada e teste de regressão.
- Beads: `sikjh` closed (feito), `5k9r7` close com CI evidence, `yirgp` fechado ou
  pendência documentada, `0suy3` fileada.
- `~/.agents` ≡ `~/agents` skills, sem divergência pós-push.

## Riscos / surrounding

- Lanes concorrentes ativas no root (gen loop, tmux pids dinâmicos): nunca matar;
  commits por paths explícitos para gitlinks+projeções apenas.
- Worktree `~/flext-release-012` mantém `M flext-infra` gitlink: não destruir.
- Se o erro de CI for _runner-only_ (não reproduzível local): ínspeção commit das
  permissões no Actions e correção idempotente (umask explícito no publish) — de
  qualquer forma, fix no owner `flext-infra`.
