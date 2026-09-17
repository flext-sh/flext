# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md (Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there
# Checkpoint 0.12.0 — Integrar PRs com CI verde + teste cd-infra (windows/macos/linux)

Data: 2026-09-10 (rev2 pós-diagnóstico) · Bead-mãe: `flext-yirgp` · Integração: `origin/0.12.0-dev` (= `ec347f3867`, fetch feito)

## Causa raiz confirmada (evidência de execução)

1. **SSOT correto, projeção stale.** `flext-infra/config/codegen.yaml` declara `structlog>=25.5.0` + `uv_constraint_dependencies: ["structlog<26"]` + `click>=8.3.3` (consistente). O `pyproject.toml` do root estava com `structlog>=26.1.0` (projeção não regenerada) → `uv sync` exit 2 ("flext depends on structlog>=26.1.0 and structlog<26"). Isso era o "setup (blocking)"/"Boot" vermelho no CI do PR #668 e do tip.
2. **Schema do manifesto NÃO mudou.** Dump runtime do modelo instalado (`RepositoryRef`: `kind` required, `checkout` opcional default `root`; `ProjectSpec.repository_root_rel` required) confirma que o shape atual de `config/workspace.yaml` (committed) é o correto. Migração temporal para `checkout/workspace_root_rel` foi revertida — nenhum drift restante em workspace.yaml.
3. **Ref de baseline faltava localmente.** `refs/remotes/origin/0.12.0-dev` não existia no clone → gen falhava em `provider baseline ref is missing`. Corrigido com `git fetch origin 0.12.0-dev`.
4. **WIP não autorizado preservado.** Checkout de inspeção do flext-infra carregava hand-edits em arquivos gerenciados (`click>=8.4.2` regressão do floor, `structlog>=25.5.0,<26` redundante). Preservado em `stash@{0}` do flext-infra ("preserved pre-integration WIP"). **Não restaurar** — viola piso corrigido e regra de não editar gerenciados.

## Já executado (não repetir)

- flext-infra submodule: detached em `9cc03838648` (= origin/0.12.0-dev), workdir limpo; gitlink staged no superproject (ca15e5c4 → 9cc03838).
- `git fetch origin 0.12.0-dev` → `ec347f3867`.
- `make gen`: **32/32 conform OK**, 31 `pyproject.toml` publicados (structlog re-projetado). Passo lazy-init final foi abortado pelo usuário (read-only, 0 efeitos planejados) — rerun para completar fixed-point.

## Fases restantes

### Fase A — Provar ciclo local verde

1. `make gen` (rerun; esperar fixed-point, exit 0).
2. Verificar `pyproject.toml` root: linha structlog == `>=25.5.0` (grep).
3. `make gen` → EXIT=0 esperado (contradição eliminada).
4. `make gen` → capturar exit + resíduos por gate.
5. `make test` (testmon) → exit + totals.

### Fase B — Commit scoped + push + CI verde

1. Commit por paths exatos: `flext-infra` (gitlink), `pyproject.toml` (root + membros alterados), `uv.lock`, `Makefile` (se drift de gen). Nunca `git add -A`; nunca `git submodule update`.
2. `git push` FF para `0.12.0-dev`.
3. CI: re-run dos checks no novo SHA (`gh run rerun` ou o push dispara). Confirmar `ci` + `release-plan` + `merge-guard` verdes. Se vermelho: `gh run view --log-failed`, corrigir no dono (SSOT/template), push, re-gates.
4. SonarCloud branch gate (`Security Rating on New Code`): se ainda vermelho no tip novo, corrigir achados na fonte (sem silenciar).

### Fase C — Fechar PR #668

1. Diff vazio (head 06312e == base): `gh pr merge 668 --merge` (no-ff); se GitHub recusar por diff vazio, `gh pr close 668` com comentário provando equivalência de árvore.
2. Re-gates no SHA merged; bead `flext-yirgp` atualizada com evidência (comando, cwd, exit, output, SHA).

### Fase D — Restaurar chamada manual (switch) do ci-matrix pelo dono

1. Arqueologia no flext-infra: `git log -p --all -- '*ci-matrix*'` + template `base/.github/workflows/ci-matrix.yml.j2`; identificar o trecho da chamada manual removido sem autorização (região do commit `f3cd6120161`).
2. Restaurar **no template dono** (flext-infra), mantendo trigger exclusivamente `workflow_dispatch` (policy dispatch-only, nunca bind à integration line).
3. `make gen` reprojeta em todos; commit/push por membro em slices (5–7 por vez); gitlinks no superproject.

### Fase E — Teste cd-infra (dispatch manual nos 3 OSes)

1. `gh workflow run ci-matrix.yml --ref 0.12.0-dev` em flext-infra, flext-core e superproject flext (switch manual).
2. `gh run watch` → conclusão **success** nos jobs windows/macos/distro-matrix.
3. Falha de plataforma = corrigir no template/dono e re-dispatchar; nunca desativar job.
4. Evidência por repo (run ID, URL, conclusões, SHA) gravada na bead.

## Riscos

| Risco | Contramedida |
|---|---|
| stash@{0} (hand-edits) voltar ao worktree | Não pop; documentar na bead como recovery ref only |
| gen não-fixado (lazy-init abortado) | Rerun gen até no-op antes do commit |
| index.lock por shells órfãos | Verificar `ps` antes de git de escrita; não matar processos de outros agentes |
| Runners Windows custosos | Dispatch apenas nos 3 repos representativos |

## Done

1. Local: gen fixed-point + setup/check/test EXIT=0 (testmon).
2. Push FF; CI verde (`ci`, `release-plan`, merge-guard) no SHA novo; PR #668 fechado com evidência.
3. ci-matrix com chamada manual restaurada nos 32 projetos (via dono + gen, sem hand-edit).
4. Dispatch manual verde nos 3 OSes nos repos representativos; evidência na bead.
5. Beads fechadas com comando/cwd/exit/output/SHA; branch de integração gravada.

## Fora de escopo

- Lanes p0 `flext-9pia0`/`flext-r8lsm`/`flext-bkpj6` (outras sessões), publicação PyPI, backlog 0.20.
