# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md (Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there

# Corrigir deps (structlog/click) na causa raiz via gerador + fechar checkpoint 0.12.0

Data: 2026-09-10 · Plano-mãe: `.kilo/plans/1789065585607-checkpoint-012-ci-green-cd-infra.md` (fases/aprovação anteriores continuam válidos) · Branch de integração: `origin/0.12.0-dev` (superproject + membros) · Bead-mãe: `flext-yirgp`

## Objetivo

Resolver definitivamente os conflitos de dependência (structlog cap<26, click floor) **pelo gerador** — SSOT `flext-infra config/codegen.yaml` + `make gen` — eliminando os hand-edits de pyproject.toml feitos como unblock, e então concluir as fases restantes do checkpoint (CI verde, PR #668, switch ci-matrix, dispatch cd-infra, fechamento).

## Estado atual (evidência desta sessão)

- **SSOT já corrigido e commitado** em `flext-infra/config/codegen.yaml` @ `f41875666`: perfil `flext_core` com `structlog>=25.5.0,<27` (obedece o decreto meltano 4.2.2/structlog<26). `click>=8.3.3` já está no perfil `flext-cli` (linha ~1164). Ambos os valores são os decretados (memória: `flext.structlog_cap`, `deps.floor_ceiling_conflict`).
- **Problema do `m.Cli.AtomicFileState` era venv desatualizado**: `flext-cli` instalado no venv compartilhado apontava para git @659571ca (código antigo sem o modelo completo). Após instalação do checkout local, desapareceu.
- **Hand-edits não canônicos feitos como unblock** (devem ser superseded pelo gen — mesmos valores, mas precisa virar projeção do gerador):
  - `structlog>=25.5.0,<27` em ~29 `flext-*/pyproject.toml` + `flext/pyproject.toml` (root).
  - `click>=8.3.3,<8.4` + structlog em `flext-cli/pyproject.toml`.
- **Bloqueio da Fase 1 do plano original esclarecido**: `make setup` no flext-infra agora passa (pós-fixes). Falhas anteriores: structlog>=26.1.0 vs capa<26 (resolvido no SSOT); click>=8.4.2 vs meltano click<8.4 (resolvido no SSOT).
- **Descoberta nova**: `make gen` no **root** falhou validando `config/workspace.yaml` com 66 erros (`RepositoryRef.checkout` required, `kind` extra_forbidden) — mas o `RepositoryRef` no working tree do flext-infra TEM `kind` e `checkout` com default. Portanto o gen do root importou **flext_infra de outra fonte** (venv compartilhado `~/flext/.venv` tem `_editable_impl_flext_infra.pth` + `flext_infra-0.12.0.dist-info`; PYTHONPATH do root é `flext/src`, que não contém `flext_infra`). Causa provável: pth/dist-info apontando para worktree antigo (release worktree). A sido corrigido por setup canônico do root re-provisionando editables.
- **Dívida provocada por mim (recuperar, fix-forward)**: `git stash` no flext-infra (antes do rebase) contém WIP pré-existente de outra lane (Makefile, check.py, conform.py, workspace_check.py, models.py, templates, tests) + arquivos não-rastreados `rope_rules*` seguindo no disco. O stash `MUST` ser restaurado (nunca descartar trabalho compartilhado). Além disso o rebase reordenou f13da7200 sobre 9cc038386 — branch local divergiu e foi reconciliada por rebase; partir daqui, só FF/no-ff.

## Fases

### Fase 0 — Recuperar WIP e reconciliar flext-infra (pré-requisito, fix-forward)

1. `git stash list` em `flext-infra`; `git stash pop` do WIP. Resolver qualquer conflito preservando AMBAS as intenções (WIP da outra lane + commits de structlog/click). Se conflito severo (duas intenções incompatíveis), `bd` + pergunta única.
2. Rodar em `flext-infra`: `make gen` (iterar até fixed-point) → `make gen` → `make gen` → `make test`. Evidência: comando+cwd+exit+output.
3. Commit scoped do WIP reconciliado (não é meu conteúdo — manter mensagem fiel ao trabalho) e push FF em `0.12.0-dev` do flext-infra.

### Fase 1 — Deps na causa raiz: gen do root projetando todos os pyprojects

1. Provar qual flext_infra o gen do root resolve: `python3 -c "import flext_infra; print(flext_infra.__file__)"` com o mesmo env de `PROJECT_FLEXT_INFRA`. Se apontar fora de `~/flext/flext-infra`, rodar `make gen` no root para re-provisionar editables e repetir.
2. `make gen` no root. Critério: 0 erros de validação de `config/workspace.yaml` e fixed-point.
   - Se o erro de `RepositoryRef` persistir com o flext_infra correto: investigar no histórico (`git log -p` do `_models/config.py` vs `config/workspace.yaml`) qual lado é dono (manifest é handwritten SSOT; modelo é código). Corrigir o lado errado NO DONO, nunca o lado conveniente.
3. Os hand-edits de pyproject devem coincidir com a saída do gen (mesmos valores SSOT). Se divergir, **o gen vence** — adotar a saída do gerador.
4. Landing por membro: commit scoped dos `pyproject.toml` regenerados em cada repo → push FF (se tip andou, `git merge --no-ff origin/0.12.0-dev` antes, nunca rebase/force-push) → gitlinks no superproject commitados e push.
   - Em batches de 5–7 membros por sessão (regra 23).

### Fase 2 — CI verde no flext-infra e PR #668

1. Re-gates locais no tip: `make setup/check/test` (testmon) em flext-infra.
2. Reexecutar CI GitHub (`gh run rerun 34422325214 -R flext-sh/flext-infra` ou trigger pós-push legítimo); se ainda vermelho, `gh run view --log-failed` e corrigir na causa raiz (SSOT/templates, nunca bypass).
3. Resolver SonarCloud branch-gate ("Security Rating on New Code < A") corrigindo os findings ativos, não silenciando.
4. Merge de #668 (`gh pr merge 668 --merge`, no-ff). Diff vazio → se recusar, `gh pr close --comment` com prova de equivalência de árvore. Re-executar gates no SHA merged.
5. Espelhar gitlink no superproject, commit scoped, push.

### Fase 3 — Recuperar "manual switch" do ci-matrix pelo dono (template flext-infra)

1. Arqueologia em flext-infra: `git log -p --all -- '*ci-matrix*'` + template `.github/workflows/ci-matrix.yml.j2` (owner) → identificar o trecho removido (última alteração `f3cd6120161`, 2026-09-09).
2. Restaurar o trecho **no template** (nunca hand-edit do output), trigger exclusivamente `workflow_dispatch`.
3. `make gen` no root → reprojeta os workflows nos 32 projetos com fixed-point.
4. Landing por membro: commit scoped `.github/workflows/ci-matrix.yml` → push FF → gitlinks no superproject (batches de 5–7).

### Fase 4 — Teste cd-infra (switch manual)

1. Dispatch em onda representativa: `gh workflow run ci-matrix.yml --ref 0.12.0-dev -R flext-sh/<repo>` para flext-infra, flext-core e flext (superproject). Nunca auto-bound à linha de integração.
2. Monitorar `gh run watch`/`gh run list`; expectativa: `distro-matrix` (5 distros linux via docker), `macos`, `windows` → success.
3. Falha de plataforma → corrigir no template/flext-infra e re-dispatch; nunca desativar job.

### Fase 5 — Ciclo canônico final e fechamento

1. No superproject: `make gen/fmt/fix/check/test` full fleet (32/32), testmon obrigatório, sem `PROJECT=`/`WHAT=`/`PYTEST_ARGS=`.
2. Docs (`docs/releases/latest.md`, ADRs citados) atualizadas na MESMA mudança.
3. Fechar beads (`flext-yirgp`, cadeia, `flext-cpkk`/`flext-5k9r7` se CI de flext-cli verde) com comando/cwd/exit/output/SHA; gravação final na branch de integração.
4. Lanes p0 `flext-9pia0`/`flext-r8lsm`/`flext-bkpj6` **fora deste ciclo**.

## Riscos / contramedidas

| Risco                                                | Contramedida                                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------- |
| Stash pop conflita com rebase já aplicado            | Preservar ambos os intents; conflito severo → parar e perguntar 1 questão |
| Gen do root validar workspace.yaml com modelo errado | Diagnosticar import-path do flext_infra antes de tocar no manifest        |
| Hand-edits ≠ saída do gen                            | Gen vence; adotar projeção, nunca congelar                                |
| `git submodule update`                               | PROIBIDO (reseta gitlinks) — commits por paths exatos                     |
| Piped `tail` descarta exit code                      | Capturar output completo ou sem pipe                                      |
| Lock de journal do codegen                           | Transiente; retry após confirmar nenhum processo vivo                     |
| Runners macos/windows gastando minutos               | Dispatch representativo (3 repos), expandir só sob instrução              |

## Critério de Done

1. `make setup/gen/check/test` verde no root (full fleet) e no flext-infra — **projetado pelo gerador**, zero hand-edit residual (diff `git status` limpo em pyprojects).
2. Deps resolvidas pelo SSOT: structlog `>=25.5.0,<27` e click `>=8.3.3` derivados de `config/codegen.yaml`, com fixed-point de gen.
3. PR #668 fechado (merged/absorvido) com CVI verde re-executado no SHA merged.
4. `ci-matrix.yml` com switch manual restaurado nos 32 projetos via template + `make gen`.
5. Dispatch manual com 3 jobs success (windows/macos/linux-matrix) em flext-infra/flext-core/flext; evidência em beads.
6. Beads fechadas com evidência (comando, cwd, exit, output, SHA); docs em dia; branch de integração com provas.
