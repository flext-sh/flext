# Prompt de continuação — WS-A validação e fechamento (plano 1789162200000)

<!-- TOC START -->

- [Contexto](#contexto)
- [Críticas a resolver antes de declarar WS-A done](#criticas-a-resolver-antes-de-declarar-ws-a-done)
- [Sequência de execução](#sequencia-de-execucao)
- [Critérios de parada](#criterios-de-parada)

<!-- TOC END -->

## Contexto

- Lei aprovada: `render = f(SSOT, templates, PINS)`; qualquer entrada de ambiente no
  render é bug P0.
- Ordem aprovada: WS-A → WS-B → B404 → loc-cap ×5 → #688 → cascade → F2.
- Bead ativa: `flext-3d8bv` (in_progress) em `~/flext`.
- Branch `flext-infra` `0.12.0-dev`: limpa, **ahead 6 / behind 35** de
  `origin/0.12.0-dev`.
- Commits locais: `c8308b280`, `9265c5365`, `d83da30a5`, `b231f99f4`, `f82f509a5` (merge
  fix-forward), `778143f0d`.
- é o padrão; `make fix/fmt/gen/check/test` rodam sem flag.
- PR #225 só pode ser merged com CI verde no SHA merged; nunca bypass.

## Críticas a resolver antes de declarar WS-A done

1. `project_managed_artifacts.py` tem 393 LOC (>200) — fatorar via `make mod`.
2. `Repo(..., search_parent_directories=True)` (linha 231) pode ler catálogo do
   superprojeto em projeto aninhado sem `.git` próprio — restringir ao root do projeto.
3. Golden-test tri-ambiente cobre só VS Code settings — estender para
   pyproject/.gitignore/mise tri-ambiente.
4. Teste do ano é tautológico (fixture lê o mesmo SSOT) — comparar contra valor
   declarado congelado no teste ou provar que `localtime()` sumiu do código.
5. `_project_render_context` duplica construção de spec em vez de reusar
   `_project_spec_from_existing` — dedup.
6. `transaction_residue` (diagnóstico legítimo) sem nota de evidência na bead —
   registrar.
7. Gates nunca rodados: **nenhuma evidência** de `make fix/fmt/check/test` pós-commits.
8. Bead sem notas desde 21:53Z — atualizar com SHAs e evidências.
9. Branch está **behind 35** — integrar origin antes de PR (merge --no-ff, nunca
   rebase/force).

## Sequência de execução

1. `bd update flext-3d8bv --claim` (reafirmar) e `bd show flext-3d8bv` para reconciliar.
2. `git -C flext-infra fetch && git -C flext-infra merge --no-ff origin/0.12.0-dev`
   (fix-forward, preservar WIP alheio).
3. Resolver as críticas 2–5 no dono canônico (sem shim/suppressão).
4. `make fix && make fmt` (escopado ao lane; nunca tocar arquivo alheio).
5. `make gen && make gen` — segunda rodada **exit 0, zero mudanças** (prova de ponto
   fixo).
6. `make check && make test` — green obrigatório, sem exclusões novas.
7. Golden-test tri-ambiente: host com `.flext-runtime`, host limpo, runner CI — bytes
   idênticos.
8. `bd close flext-3d8bv --reason "..."` só com evidências: SHAs, comandos, exit codes.
9. Push fast-forward → PR → CI verde no SHA merged → merge --no-ff → rerun gates no
   merged SHA.
10. Só então avançar a WS-B (journal keyado por pin SHA + lock por repo).

## Critérios de parada

- WS-A fechada com bead closed + CI verde + merged.
- Qualquer gate bloqueando: parar e escalar com comando exato + erro.
- Nunca rebase, force-push, bypass de CI ou descarte de trabalho alheio.
