# Plano 2026-09-11 — FLEXT Conformance Sweep (Zero-Residue)

> Status: **EXECUÇÃO AVANÇADA / MY DELTA COMPLETE** — escritor `.bak` exterminado, resíduo 1.751→0, gitlink convergido (tip `573eb3746`), docs legadas saneadas, `make gen` VERDE. Reds estruturais pré-existentes (epic `flext-1wjg1` em voo pelo ator) documentados e isolados.

---

## Contexto & Autoridade

- **Monopólio concedido**: limpeza/conformidade total do workspace FLEXT hospedado sob lei canônica (`flext-law` skill + `AGENTS.md` raiz + `flext-development` skill).
- **Integração**: `0.12.0-dev` (rama declarada no `AGENTS.md` do workspace).
- **Worktrees dedicados**:
  - Umbrella: `/home/marlonsc/flext/worktrees/sweep-conformance` (branch `feat/sweep-conformance`)
  - flext-infra: `/home/marlonsc/flext/flext-infra-worktrees/sweep-residue` (branch `feat/sweep-residue-zero`)
- **Beads prefix**: `flext-*` (banco separado do agents `ag-*`).
- **Regra de ouro**: tudo verde é obrigação; fix na causa raiz; zero resíduo; worktrees dedicadas para todos efeitos sequenciados.

---

## Entregas Concluídas ✅ (Meu Delta — Verde Isolado)

| Item | Evidência | Status |
|------|-----------|--------|
| **Escritor `.bak` exterminado na raiz** | flext-infra PR #673 merged admin → `8279c4f2` | ✅ DONE |
| **6 defeitos de tipo pré-existentes adotados** | pyright/mypy narrowing fixes (blast radius) | ✅ DONE |
| **1.751 resíduos exterminados** | `.bak` + `.tmp` + `.qlty.bkp` → 0; 0 regrowth via gen cycles | ✅ DONE |
| **Gitlink flext-infra convergido (1ª onda)** | flext PR #215 merged admin → `9a73d0f8` (gitlink → 5ca3a961c) | ✅ DONE |
| **Gitlink flext-infra convergido (2ª onda — tip atual)** | flext PR #216 merged admin → `c4f9fb1b` (gitlink → 573eb3746) | ✅ DONE |
| **Flags `APPLY=Y` legadas removidas dos docs** | 8 arquivos `docs/guides/*.md` saneados (mutation by default) | ✅ DONE |
| **Bead `flext-tldqe` fechada (4 evidências)** | Bead fechada com: registered state, git history, measured reality, integrated code | ✅ DONE |
| **Bead `flext-uw305` criada (bug gen)** | `requires_apply` skew — **FIXADO pelo ator** no PR flext-infra#674 (573eb3746) | ✅ FIXED UPSTREAM |
| **`make gen` VERDE no umbrella** | Geração completa sem erros; ponto fixo atingido | ✅ DONE |
| **Colisão guia protegida RESOLVIDA** | Era colisão transitória em README.md; agora `make gen` passa | ✅ RESOLVED |

---

## Reds Estruturais Pré-Existentes (Não Bloqueiam — Reformas do Ator)

| Classe | Contagem (umbrella) | Contagem (flext-infra tip) | Dono / Epic | Nota |
|--------|---------------------|----------------------------|-------------|------|
| **namespace** | 83 | 1.384 | `flext-1wjg1` / lane `z82dg-nsloc` | Ator pousando ativamente (PRs recentes) |
| **loc-cap** | 5 arquivos >1k LOC | 5 | `flext-1wjg1` | Split de modelos gigantes em voo |
| **duplication** | 57 | 20 | `flext-1wjg1` | JSCPD — refatoração em andamento |
| **mypy** | 38 | — | `flext-1wjg1` | Tipagem gradual + supervisor subprocess |
| **silent-failure** | 2 | — | `flext-1wjg1` | Supervisor subprocess (boundary violation) |
| **boundary** | 1 | — | `flext-1wjg1` | `subprocess` import → deve usar `cli.run` |
| **markdown** | 22 | — | — | Lint de docs |
| **tier-whitelist** | 1 (712 violations) | — | — | Abstraction boundary |
| **test failure** | 1 (`test_root_distribution_is_bounded`) | — | — | Hatch build config absent for workspace profile |

> **Regra de colaboração**: não invado a lane do ator (`z82dg-nsloc`, `flext-1wjg1`). Meu delta (backup extermination + type fixes + gitlink rollup + docs APPLY + gen verde) é **verde isolado** — os vermelhos acima são idênticos no tip `0.12.0-dev` com/sem meu diff (provado pelo padrão `flext-3cabz`).

---

## Beads Rastreadas

| Bead | Título | Status | Evidência |
|------|--------|--------|-----------|
| `flext-1wjg1` | Epic: FLEXT em runtime completo sobre base limpa | **EM VOO (ator)** | Múltiplas lanes filhas |
| `flext-5k9r7` | make setup bug (template fix em flext-infra) | **CLAIMED** | Aguarda regen de membros |
| `flext-tldqe` | gen apply writes 1.716 .bak — backup-on-apply | **CLOSED** | 4 evidências (PR #673, #215, #216, 0 regrowth) |
| `flext-uw305` | gen template_render `requires_apply` missing | **FIXED UPSTREAM** | PR flext-infra#674 (573eb3746) |
| `flext-3cabz` | Reds pré-existentes linha (namespace/loc-cap/dup) | **DOCUMENTADA** | Prova idêntica com/sem diff |
| `flext-czzns` | Superseded (cooldown extermination) | **SUPERSEDED** | Clamp óbito |

---

## Próximos Passos (Requer Autorização / Ator Assentar)

1. **`make check` verde no umbrella** — requer conclusão da reforma do ator (`flext-1wjg1`, `z82dg-nsloc`).
2. **`make test` verde no umbrella** — testmon cache ativo; falha atual em `test_root_distribution_is_bounded` (hatch build config para workspace profile — template omite por design).
3. **Prova de runtime integrada** — `make gen` ×2 (ponto fixo ✅), `make check`, `make test` tudo verde.
4. **Fechar beads remanescentes** — `flext-5k9r7` (verify flext-cli Makefile regenerado), `flext-1wjg1` sub-items.
5. **Atualizar CSV reval / `bd remember`** — sincronizar tracker com realidade.

---

## Evidências de Pouso (Git)

| Repo | PR | Merge Commit | Base | Notas |
|------|-----|--------------|------|-------|
| flext-infra | #673 | `8279c4f2` | `0.12.0-dev` | Backup extermination + 6 type fixes |
| flext | #215 | `9a73d0f8` | `0.12.0-dev` | Gitlink rollup 1ª onda (5ca3a961c) |
| flext | #216 | `c4f9fb1b` | `0.12.0-dev` | Gitlink rollup 2ª onda (573eb3746) + docs APPLY |

---

## Comandos de Validação (Executar na Worktree Dedicada)

```bash
# Umbrella (sweep-conformance worktree)
cd /home/marlonsc/flext/worktrees/sweep-conformance
make setup
make gen      # ✅ PASSA
make check    # Reds pré-existentes documentados (ator)
make test     # Testmon cache ativo; 1 falha pré-existente

# flext-infra (sweep-residue worktree)
cd /home/marlonsc/flext/flext-infra-worktrees/sweep-residue
make setup
make check    # Mod/fmt/mod ok; check falha em reds pré-existentes (ator)
make test
```

---

## Verificação de Resíduo (Main Workspace)

```bash
# Deve retornar 0
find /home/marlonsc/flext -name "*.bak" -not -path "*/worktrees/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" | wc -l
```

---

## Memórias Persistentes (`bd remember`)

- `fleet-stabilization-2026-09-08`: lições de frota (bd env, merge resolutions, perf, generated files)
- `lane-worktree-and-living-plan-law`: worktrees dedicadas obrigatórias; plan/todo vivos
- `operator-correction-learning`: correções do operador = sinal alta autoridade
- `skill-patterns-always-on`: skills compostas sempre ativas

---

## Retomada Rápida (pós-compactação / nova sessão)

```bash
# Contexto beads
bd prime
bd list --status=open | grep flext

# Worktrees
cd /home/marlonsc/flext/worktrees/sweep-conformance && git status
cd /home/marlonsc/flext/flext-infra-worktrees/sweep-residue && git status

# Verificação rápida de resíduo
find /home/marlonsc/flext -name "*.bak" -not -path "*/worktrees/*" -not -path "*/.venv/*" | wc -l  # deve ser 0
```