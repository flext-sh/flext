# Worktree alignment assessment — flext × ai-hub

Data: 2026-09-19 · Autor: agente dedicado flext (épico flext-8j4v5)
Escopo: reavaliação profunda da funcionalidade de worktrees, alinhamento com o WIP do ai-hub (descoberta + manutenção), estágio e todos restantes.

## 1. Capacidade atual do flext (o que funciona)

- **Serviço**: `flext_infra/worktree.py` — `FlextInfraWorktreeService` com LIST/ADD/UPDATE/REMOVE (`_constants/workspace.py:19-28`); registry = `git worktree list --porcelain` (`worktree.py:120-134`).
- **Lanes fora do repo**: `_lanes_root()` coloca lanes em `<git-project-externo>/.worktrees/<repo>-<sha12>`; lanes épicos aninham filhos; rollback/fast-forward em `worktree_lifecycle.py`; provisionamento de gitlinks em `worktree_provisioning.py`.
- **Variações reais em disco**: `/home/marlonsc/flext-infra-worktrees/`, `flext-worktrees/`, `flext-wt/`, e lanes internas `flext-infra/.claude/worktrees/*` (19 registradas no flext-infra).
- **Integração gates/gen** (funciona): `.worktrees` em `COMMON_EXCLUDED_DIRS`; `.claude` em `CHECK_EXCLUDED_DIRS` (lanes ai-hub-style não são duplo-escaneadas); tier-whitelist exclui `.worktrees|worktrees|flext-infra-worktrees` + identidade por lane; discovery de projects pula dot-dirs; scratch espelha `.git`→`_git` para submódulos em worktree.
- **Baseline branch**: `repository_baseline_branch` com `refs/remotes/origin/<candidato>` — agora consumindo `branch_policy.integration_branch_preference` (fix `208716f4f`).
- **Testes**: 12 passed na amostra (`test_worktree_paths/topology/add_contract`).

## 2. Contrato ai-hub (para onde alinhar)

- **Descoberta**: `.git/worktrees/*/gitdir` lido direto do filesystem (`_storage_worktrees.py:34`), sem subprocess git.
- **Convenção de local**: `worktrees/<bead-id>` dentro do workspace OU sibling `<repo>-worktrees/` (`WorktreePolicy.sibling_suffix`); BG-GIT-020 nega `git worktree add` fora da convenção.
- **Ciclo de vida**: gascity é o dono (create/assign/merge/cleanup — ADR-0016, ADR-0020); ai-hub só descoberta/identidade/GC-deps.
- **GC**: staleness por mtime + `activity_window_days`; poda só de deps reconstruíveis (`.venv`, `node_modules`, `target`); remoção é **plan-only** até oig6s.5.
- **Eventos**: `bead.worktree.reaped` / `bead.worktree.reap_skipped` (gascity/ADR-0026).
- **Metadata**: worktree deve carregar `.beads` (permissions.worktree.metadata_directory, 0700).

## 3. Desalinhamentos flext × ai-hub

1. **Layout de lanes divergente**: flext usa `<repo>-<sha12>` sob `.worktrees/` externo; ai-hub espera `<repo>-worktrees/<bead-id>` (sibling suffix). Lanes flext existentes (`flext-wt/`, `flext-worktrees/`, `flext-infra-worktrees/`) são invisíveis ao GC do ai-hub.
2. **Sem `.beads` metadata garantida** nas lanes flext (requisito do GC/permissões ai-hub).
3. **Sem emissão/consumo de eventos** `bead.worktree.*` (fase ADR-0026 aberta também no ai-hub).
4. **Estilo de criação**: flext cria worktrees via serviço próprio (library-only) — OK enquanto não use `git worktree add` fora da convenção (BG-GIT-020), mas a convenção em si difere.

## 4. Estágio por plano recuperado

| Plano/ADR | Estágio |
| --- | --- |
| ADR-0016 (gitflow lanes + worktree lifecycle, ai-hub) | Aceito/implementado; gascity é o dono |
| ADR-0026 (CRG autopilot + eventos worktree, ai-hub) | Aberto — aihub-3t7yh (epic), 3t7yh.3.3 (prune watchers) |
| STO-S3/S5 storage GC (aihub-oig6s.*) | S3 in_progress (descoberta+GC-deps landed); S5 (cutover + auto_reap) aberto |
| T2 worktree-aware workspace discovery (aihub-a7dedfbf) | **Blocked** |
| ADR-007 flext (worktree transaction perf) | CURRENT IMPLEMENTATION |
| worker-lane-contract (flext) | Vigente (lei de lanes) |
| plan-reconciliation flext (flext-ro6mj) | Approved; execução sequencial pendente |
| flext-3cabz | 4 testes codegen vermelhos em worktree pristine |

## 5. Todos restantes (por dono)

**flext (este workspace):**
1. flext-bxo4y (P1) — eliminar padrão `.flext-runtime` borrowed-venv em worktrees.
2. flext-xobfw (P1) — tier-whitelist: subprocess morto + falso escopo `.git`-ancestor em linked worktrees.
3. flext-5fxu6.4.13 (P2) — jscpd `**/.claude/**` esconde lanes do check de duplicação.
4. flext-xtzkz (P2) — ledger de aposentadoria de worktrees/branches (ancestry-proved).
5. CLI gap — expor `FlextInfraWorktreeService` em verbo (`flext_infra worktree add|list|remove`) ou wire no work saga (ops START/LAND sem consumidores hoje).
6. `/home/marlonsc/flext/worktrees/` — diretório órfão vazio: adotar como `WORKTREES_DIRNAME` da convenção alinhada ou remover.
7. flext-3cabz — 4 testes codegen vermelhos em worktree pristine.
8. Alinhar `_lanes_root` à convenção ai-hub (`sibling_suffix` + bead-id) — requer acordo com gascity/ai-hub antes (quebra lanes existentes).

**ai-hub (donos externos):**
9. aihub-oig6s.5 — execução da aposentadoria de worktrees (hoje plan-only).
10. aihub-3t7yh.3.3 — prune de watchers CRG de worktrees extintas.
11. aihub-a7dedfbf — T2 worktree-aware discovery (desbloquear).

**Bloqueios transversais vivos (não-worktree, mas impedem check 100%):**
12. flext-w3qcn (P0) — migração de identidade de members incompleta (gen fleet).
13. flext-eb764 — ciclo de import p no flext-ldap.
14. flext-core — namespace 604 (examples de treino) + silent-failure em `_beartype`.

## 6. Decisão recomendada

Não migrar o layout de lanes do flext agora (quebraria 19 worktrees registradas e as lanes de 4+ agentes ativos). Alinhar em duas ondas: (a) curto prazo — flext emite os eventos `bead.worktree.*` e garante `.beads` nas lanes novas (compatibilidade com GC do ai-hub sem mover nada); (b) médio prazo — gascity/ai-hub reconhecem o layout legacy `<repo>-<sha12>` como tool_internal na policy `storage.worktrees` até a aposentadoria natural via flext-xtzkz.
