# wip-hier.sh — Decomposição em módulos ~/wip-hier/ (DRY/YAGNI, flags-only)

Plano de implementação · Não altera o plano de execução rope-modernize (`1789564109553-rope-modernize-execution-plan.md`), que continua válido e referencia `~/wip-hier.sh` — que permanece funcionando como shim.

## 1. Objetivo e restrições

Decompor `~/wip-hier.sh` (1527 linhas, monólito bash) em módulos sourced sob `~/wip-hier/`, **sem perder nenhuma funcionalidade** e **sem reescrever lógica** (refactor mecânico de extração). UX final: **flags-only modernizado** (decisão do operador) — sem subcomandos; `--help` detalhado por flag. Tudo sob `~/`.

- Preserve TODOS os comentários `# Why:` com suas funções (conhecimento institucional medido em runtime).
- Nenhuma função renomeada; nenhum fluxo alterado; defaults idênticos.
- **Shellcheck 100% compliant (decisão do operador)**: `bin/wip-hier` + todos `lib/*.sh` com ZERO findings shellcheck — inclusive os que já existem no monólito baseline. Correções de findings pré-existentes são o único desvio permitido do movimento verbatim; cada correção é validada pelos gates de paridade (§6.3–§6.7), que continuam bloqueando qualquer diferença comportamental.
- **Lei de pureza dos bins (operador, 2026-09-16)**: `bin/wip-hier` e `bin/wip-hier-check` NÃO executam git/gh/bd e não carregam cálculos complexos de variáveis — toda primitiva vive nas libs, que são incrementadas para isso: `require_work_tree`/`resolve_root` (20-topology), `init_log_paths` (00-config), `log_has`/`gitlink_agrees` (10-git), `85-fixture.sh` (todo o plumbing git da família sintética). Bins ficam com parse, loader, tabelas de dados e fluxo de orquestração apenas.
- Única adição funcional (marcada NEW): `--no-gates` / `--gates <lista>` — hoje os verbos canônicos rodam sempre; o ciclo absorvedor precisa de rodadas capture-only. Comportamento default inalterado.

## 2. Layout final

```text
~/wip-hier/
├── bin/wip-hier            # entrypoint: parse de flags, loader de módulos, main() + epílogo tee/PIPESTATUS (verbatim)
├── lib/
│   ├── 00-config.sh        # constantes readonly (MAKE_VERBS, MAKE_TIMEOUT, LOSS_BARRIER_LINES, NET_*), env exports (GIT_TERMINAL_PROMPT...), LOGDIR, die/have, globais mutáveis documentadas (DO, APPLY, RETIRE, INCLUDE_FOREIGN, ROOT, KIND, ROWFILE, INTEG...)
│   ├── 10-git.sh           # do_git/show_cmd/git_mutates, nfetch/npush/ngh, abs_git_dir/abs_common_dir, tree_kind, current_head/named_branch/current_sha, ref_exists, is_dirty, ahead_count, sync_cell, bind_upstream, switch_to
│   ├── 20-topology.sh      # resolução do root (loop superproject), gitmodules_paths, collect_subs, worktree_bound_branch, unique_local_branch_at, branch_bound_elsewhere, sanitize_branch_name, detached_worktree_branch, locate_root_branch, integration_branch, has_envrc
│   ├── 30-github.sh        # github_origin_repo, open_pr_number, open_pr_for_head
│   ├── 40-safety.sh        # warn_alternates, has_unmerged, conflict_marker, generated_file, real_wip_files (+barreira de perda), worktree_locked, worktree_pinned, protected_branch, spent_ref
│   ├── 50-capture.sh       # commit_summary/commit_details, push_head (retry fetch+merge --no-ff), resolve_gitlink_conflicts, handle_conflict, sweep_repo
│   ├── 60-retire.sh        # RETIRED map usage, retire_worktrees/retire_branches/retire_prs/retire_repo
│   ├── 70-gates.sh         # run_gates (+ os 3 guards de posse, verbatim)
│   └── 80-report.sh        # emit_row, sorted_rows, report, print_origin_map, _skip_user_dir/_scan_root/scan_git_dirs/discover_same_origin/family_rows (foreign scan)
│   └── 85-fixture.sh       # NEW: família sintética para --apply (todo o plumbing git do fixture; não carregada pelo sweep)
├── bin/wip-hier-check      # NEW: orquestrador declarativo dos gates §6 (passos/matrizes/asserts como dados; consome as libs como sondas)
├── .baseline/wip-hier-v1.sh  # cópia imutável do monólito original (referência de paridade)
├── .baseline/wip-hier-v1-fixed.sh  # baseline + fix L39 (referência de paridade dry-run; o baseline original crasha — SC2296/bad substitution)
└── README.md               # uso (help por flag), mapa de módulos, checklist de paridade
```

`~/wip-hier.sh` vira shim de 3 linhas: `exec ~/wip-hier/bin/wip-hier "$@"` — docs, handoffs e o plano rope-modernize continuam válidos sem edição.

## 3. Mecânica de "import" (bash-nativo)

- Loader no `bin/wip-hier`: source `lib/[0-9]*.sh` em ordem lexicográfica (numeração = ordem de dependência: config → git → topology → github → safety → capture → retire → gates → report).
- Guard de colisão: ao carregar, `declare -F` antes/depois de cada módulo; função redefinida = `die` loud (impede duplicação silenciosa — DRY garantido em runtime).
- `set -euo pipefail` apenas no entrypoint; os re-arms `set -euo pipefail` em subshells dentro de `report()` permanecem verbatim.
- Epílogo `} 2>&1 | tee "$LOGFILE" "$LATEST"` + `PIPESTATUS` permanece no entrypoint, byte-a-byte.

## 4. CLI (flags-only modernizado)

```text
usage: wip-hier [flags]
  (sem flags)         discovery + dry-run: tabela da frota + plano sem escritas
  --apply             capture: preserve-commit WIP, alinhar branch, push lanes
                      (push rejeitado → fetch + merge --no-ff + re-push)
  --no-retire         pular aposentadoria de branches/worktrees/PRs já contidos
  --include-foreign   varrer também clones same-origin fora da família viva
  --no-gates      NEW pular verbos canônicos (setup deps gen fix fmt check test)
  --gates <lista> NEW override da lista de verbos (default: todos, em ordem)
  --help              ajuda completa, uma seção por flag com exemplos
```

- Flags legados mantêm semântica exata; parse continua `while [[ $# -gt 0 ]]` com `die "unknown arg"` para input desconhecido.
- `--no-gates`/`--gates` só alteram o bloco `== canonical verbs ==` (chamada de `run_gates`); nada mais.

## 5. Passos de implementação (ordem)

1. `mkdir -p ~/wip-hier/{bin,lib,.baseline}`; `cp ~/wip-hier.sh ~/wip-hier/.baseline/wip-hier-v1.sh`.
2. Extrair módulos NA ORDEM §2, movendo funções verbatim (copia-e-cola puro, comentários inclusos). Sem reescrita.
3. Escrever `bin/wip-hier`: loader (§3) + parse de flags (§4) + `main()` com o bloco de orquestração final (print_origin_map → process_tree da raiz → foreign loop → exit) verbatim.
4. Inventario de paridade de funções: `declare -F | diff` entre baseline rodado via `bash -c 'source ~/wip-hier/.baseline/wip-hier-v1.sh --help'` (adaptar: extrair com `bash --norc -c 'source ...; declare -F'` se viável) e o novo — conjuntos idênticos (± helpers do parse se inevitável, listados no README).
5. Substituir `~/wip-hier.sh` pelo shim (§2).
6. `git -C ~/wip-hier init && git add -A && git commit -m "wip-hier: decompose monolith into lib modules (parity-refactor)"` (versionar; provenance).
7. Atualizar Kilo allowlist (permissões): adicionar `~/wip-hier/bin/wip-hier *` (manter `~/wip-hier.sh *` se existir).

## 6. Validação (gates de aceitação, em ordem)

Todos os gates rodam via `~/wip-hier/bin/wip-hier-check` (verbo canônico; artefatos em `~/.local/state/wip-hier/check/`). Passos: `syntax lint parity loader fleet flags fixture shim`.

1. **Sintaxe/lint:** `bash -n` em todos os `lib/*.sh` + `bin/*`; `shellcheck -x -P SCRIPTDIR` nos dois entrypoints — **ZERO findings (100% compliant, teto = 0, não o baseline)**, com as libs seguidas cross-file (portanto cobertas transitivamente). Mais o gate de pureza: nenhum comando `git`/`gh`/`bd` em posição de comando nos bins. Findings pré-existentes herdados do monólito são corrigidos na raiz nos módulos extraídos (sem `# shellcheck disable`, sem masks); a imutabilidade fica apenas em `.baseline/` (referência de paridade). Gates 3–7 provam que nenhuma correção mudou comportamento. Nota: `source-path=SCRIPTDIR` + `shell=bash` são metadados de resolução (não masks); loader unrolled com paths literais em vez de glob — único jeito shellcheck-100% sem diretiva de silêncio (§3 atualizado por §1).
2. **Loader:** rodar `~/wip-hier/bin/wip-hier --help` — sem colisões, ajuda renderiza por flag.
3. **Paridade dry-run na frota real:** a partir de `~/flext-worktrees/rope-modernize`, rodar back-to-back `bash ~/wip-hier/.baseline/wip-hier-v1.sh` e `~/wip-hier/bin/wip-hier`; `diff` das saídas normalizando linhas voláteis (`time:`, `log:`, caminhos com pid/ROWFILE). ZERO diferença no restante.
4. **Paridade de flags:** repetir o passo 3 com `--no-retire` e `--include-foreign` (dry-run) — mesmo plano impresso.
5. **NEW flags:** `--no-gates` em dry-run → bloco `== canonical verbs ==` ausente; `--gates setup,gen` → só os dois verbos no plano/show.
6. **Fixture apply (mesclagem + retirement):** construir família sintética em `/tmp/wip-hier-fixture`: origin bare + clone A (lane com commit + arquivo dirty) + submódulo com ponteiros divergentes (gitlink conflict path) + branch spent (contida na base) + worktree limpa da branch spent. Rodar `--apply --no-retire` → assert: preserve-commit criado, lane pushed, gitlink resolvido como descendente comprovado (ou abort loud), worktree/branch spent NÃO aposentadas (--no-retire); rodar `--apply` → branch spent aposentada, worktree removida. Sem `gh`/origin GitHub na fixture → caminhos PR pulados como projetado (`not-github`).
7. **Shim:** `~/wip-hier.sh` (sem args) idêntico ao passo 3.

## 7. Riscos e mitigações

1. **Ordem de load/global colidindo** → numeração de dependência + guard de redefinição com `die`.
2. **Drift silencioso na extração** (o monólito cheio de armadilhas medidas: PIPESTATUS, subshell `set -e`, `--pathspec-from-file`) → movimento verbatim + paridade diff seca como gate; qualquer diff não-volátil bloqueia. As correções shellcheck (agora obrigatórias, §1) são o único desvio autorizado e ficam sob o mesmo gate de paridade.
3. **Perda dos `# Why:`** → checklist de revisão: grep de contagem `# Why:` baseline vs novo (mesmo número).
4. **Chamadores externos** (docs/planos/allowlists usam `~/wip-hier.sh`) → shim preserva o caminho; nada externo muda.

## 8. Fora de escopo

Rewrite de lógica, otimização, XDG, subcomandos, remoção de flags legados, mudança de defaults, qualquer feature além de `--no-gates`/`--gates`.
