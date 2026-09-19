# Plano: Ciclo make 100% verde + gen/fix/fmt idempotentes + pouso em 0.12.0-dev

## Objetivo

Levar `make setup → gen → fix → fmt → check → test` a 100% verde em todos os projetos e
subprojetos, corrigir pela causa raiz, tornar `gen`/`fix`/`fmt` **idempotentes**
(segunda execução = zero diffs), absorver todo WIP (fix-forward) e publicar tudo na
branch de integração `0.12.0-dev` (submódulos + superprojeto).

## Estado real (evidência desta sessão)

- **WIP não pousado**: `flext-core` (result: `ResultFactory` protocol + fábricas de
  módulo `ok_result`/`copy_result`; `TomlValue` via `TypeAliasType`; gates
  mypy/pyrefly/ruff 0 + runtime ok), `flext-infra` (build-constraints renderizado do
  SSOT no release; template movido p/ `release/templates/`; mixins de release com
  famílias de tipo exatas `tuple[...]`; archive typed; fixtures/protocol/dag tests
  rewireados), superprojeto (examples imports corrigidos; enums promovidos a módulo;
  test release_packaging com narrowing estrito).
- **1 teste vermelho conhecido**:
  `test_rerun_continues_the_lane_without_a_second_commit` (lane_commits=2). Causa raiz
  provada por log: o lazy-init/conform do CLI publica 23 artefatos (pyproject completo)
  **depois** do stamp do release; run1 commitou `uv.lock` curto (8 linhas) + pyproject
  cheio; run2 materializou lock de 2239 linhas → 2º commit. A ordem lazy-init ↔ fase
  precisa ser corrigida no dono (CLI runner do flext-infra), não no teste.
- **silent-failure (3 restantes)**: `_mypy_supervisor.py:105/115` (`contextlib.suppress`
  → transformar em resultado tipado `r[bool]` `_signal_group_missing_ok`);
  `gates/duplication.py:173` (`if loaded.failure: return {}` → propagar `p.Result`
  tipado; ausência de arquivo permanece caso benigno com resultado ok-vazio).
  (`_release_artifact_archive.py` já corrigido nesta sessão com `p.Result[bool]`.)
- **Resíduo banido pelo operador**: `config/build-constraints.txt` rastreado em 12 repos
  (api, auth, cli, core, db-oracle, dbt-*, grpc, infra) + não rastreado em ~20;
  `.waza.yaml.bak.1786122144` rastreado no flext-core; nenhum
  `*aihub-prior\*`encontrado. SSOT já atualizado: projeção removida do`config/codegen.yaml`
  (managed_files + templates), seção "Banned residue" adicionada ao gitignore SSOT.
- **suspeitas de não-idempotência** (validar com evidência na Fase 2): `.gitignore`
  derivado da topologia _viva_ (diferente por worktree), re-render `[MANAGED]` do
  pyproject vs tomlsort/yamlfix, `metadata.json` do beads, `uv.lock`.

## Fase 0 — Absorver o WIP (fix-forward, um commit escopado por repo)

1. `flext-core`: commit escopado
   `fix(result): structural ResultFactory + module factories; TomlValue TypeAliasType` —
   incluir `_result/*`, `result.py`, `_protocols/result.py`, `_typings/base.py`. Gates
   antes do commit: ruff + mypy + pyrefly + pytest focado em result.
2. `flext-infra`: commit escopado
   `fix(release): render build constraints from SSOT; typed archive boundary; exact`
   `result families` — incluir `release/*`, `codegen/conform.py`, `config/codegen.yaml`,
   `_constants/base.py`, `_models/config.py`, tests (utilities_release,
   policy_fixture_root_tests, test_release_dag, protocol_tests, utilities_git).
3. Superprojeto: commit escopado
   `fix(examples+tests): canonical imports, module-level enums, typed release test`.
4. Nenhum `git add -A`; sempre paths explícitos. Nunca rebase/force-push.

## Fase 1 — Purgar resíduo banido em TODOS os checkouts

1. Nos 12 repos com arquivo rastreado: `git rm --cached config/build-constraints.txt` e
   remover do worktree; commit `chore: drop banned build-constraints projection`.
2. `flext-core`: `git rm .waza.yaml.bak.1786122144` (mesmo commit ou próprio).
3. Nos demais checkouts: apagar cópias não rastreadas
   (`rm config/build-constraints.txt`).
4. Reexecutar `make gen` depois da Fase 2.1 para re-projetar `.gitignore` com a nova
   seção de banimento; conferir que o arquivo não volta em lugar algum.
5. Validação: `git ls-files | grep build-constraints` vazio em todos; `git status` limpo
   de `*.bak.*`.

## Fase 2 — Idempotência real de gen/fix/fmt (núcleo do pedido)

1. **Provar o problema**: rodar `make gen` 2× no superprojeto e em cada submódulo;
   `git status --porcelain` após a 2ª execução = lista de defeitos. Repetir para `fix` e
   `fmt`. Registrar a lista arquivo-a-arquivo.
2. **Causas raiz a corrigir no dono (flext-infra codegen)**: a. `.gitignore` derivado de
   topologia viva → derivar somente do SSOT declarado (`config/workspace.yaml`), nunca
   da presença de diretórios do checkout. b. Re-render `[MANAGED]` do pyproject com
   ordenação divergente (tomlsort/yamlfix reescrevendo seções geradas) → `fix`/`fmt`
   devem pular regiões `[MANAGED]` (guards por seção), e o gerador é o único writer. c.
   `metadata.json`/`uv.lock` — garantir que `gen` não os toque (dono = beads/make deps).
3. **Prova de idempotência permanente**: estender o `verify-fixed-point` existente
   (codegen/conform.py) para falhar alto quando `gen` rodar 2× e produzir efeitos na 2ª
   passada (já existe máquina de fixed-point; ligá-la ao ciclo `make check`).
4. Aceite: 2ª execução de `gen`, `fix`, `fmt` = zero diffs em todos os repos.

## Fase 3 — Portas vermelhas restantes, uma a uma

1. `_mypy_supervisor.py`: substituir `contextlib.suppress(ProcessGroupAbsentError)` por
   `_signal_group_missing_ok(...) -> p.Result[bool]` tipado (ausência é evento de
   domínio, propagada como resultado, nunca silenciada).
2. `gates/duplication.py:_read_project_config`: retornar `p.Result[...]`; falha de carga
   propaga; arquivo ausente = `ok({})` explícito.
3. Rerun do release (dono: CLI runner do flext-infra): garantir lazy-init/conform ANTES
   do dispatch da fase (pré-fase), e/ou `_stamp_release` rodar `uv lock` após a
   publicação do pyproject. Aceite: rerun loga `release_version_unchanged`,
   `lane_commits == 1`, teste volta a 65 passed/1 slow.
4. Quaisquer novos erros de mypy/pyrefly/ruff/markdown que `make check` revelar:
   corrigir na raiz, sem supressão, um por um.

## Fase 4 — Ciclo completo verde

1. `make setup && make gen && make fix && make fmt && make check && make test` no root,
   na ordem, 100% verde (exit 0, sem warnings normalizados).
2. Repetir `make gen` e provar zero diffs (Fase 2.4).
3. Beads: criar/fechar itens com evidência (comando, exit code, saída decisiva).

## Fase 5 — Pouso em 0.12.0-dev (integração)

1. Por submódulo: commit escopado → `git push` fast-forward de `0.12.0-dev`.
2. Superprojeto: absorver ponteiros dos submódulos, commit, push fast-forward.
3. Se push FF rejeitado: `git merge --no-ff` da base de integração na lane, revalidar
   (gates), land. Nunca rebase/force-push; nunca descartar trabalho de outra lane.
4. Pós-pouso: `make gen` em checkout limpo = zero diffs (confirmação final).

## Riscos / notas

- Lanes concorrentes ativas (flext-wt-constants): absorver, nunca descartar; rebase
  proibido; se conflito real de autoridade, parar e perguntar 1 questão exata.
- `mypy 2.3.1` novo: falhas de inferência pré-existentes (ex.: flat_map em protocol
  genérico) são corrigidas com tipagem precisa nos consumidores — nunca supressão.
- Timeout de testes: usar `@pytest.mark.slow` (SSOT 60s), nunca `pytest.mark.timeout`.
