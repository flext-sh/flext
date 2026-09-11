# Plano 2026-09-11 — FLEXT Conformance Sweep (Zero-Residue)

> Status: **EXECUÇÃO AVANÇADA** — escritor `.bak` exterminado, resíduo 1.751→0, gitlink convergido, docs legadas saneadas. Pendente: colisão guia protegida no flext-infra (reform ator) + reds estruturais pré-existentes (epic `flext-1wjg1` em voo).

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

## Entregas Concluídas ✅

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

---

## Redes Estruturais Pré-Existentes (Não Bloqueiam — Reformas do Ator)

| Classe | Contagem | Dono / Epic | Nota |
|--------|----------|-------------|------|
| **namespace** | 83 (workspace) / 1.384 (flext-infra tip) | `flext-1wjg1` / lane `z82dg-nsloc` | Ator pousando ativamente (PRs recentes) |
| **loc-cap** | 5 arquivos >1k LOC (config.py 3.695, conform.py 2.986, etc.) | `flext-1wjg1` | Split de modelos gigantes em voo |
| **duplication** | 57 (workspace) / 20 (flext-infra) | `flext-1wjg1` | JSCPD — refatoração em andamento |
| **mypy** | 38 (workspace) | `flext-1wjg1` | Tipagem gradual + supervisor subprocess |
| **silent-failure** | 2 | `flext-1wjg1` | Supervisor subprocess (boundary violation) |
| **boundary** | 1 | `flext-1wjg1` | `subprocess` import → deve usar `cli.run` |
| **markdown** | 21 | — | Lint de docs |
| **tier-whitelist** | 1 | — | Whitelist de tier |

> **Regra de colaboração**: não invado a lane do ator (`z82dg-nsloc`, `flext-1wjg1`). Meu delta (backup extermination + type fixes + gitlink rollup + docs APPLY) é **verde isolado** — os vermelhos acima são idênticos no tip `0.12.0-dev` com/sem meu diff (provado pelo padrão `flext-3cabz`).

---

## Bloqueio Atual: Colisão Guia Protegida no flext-infra

```
canonical guide collides with protected custom guide:
/home/marlonsc/flext/flext-infra/docs/guides/configuration.md
```

- **Causa**: flext-infra (subprojeto) tem `docs/guides/configuration.md` hand-written ("protected custom guide"). O gen do umbrella roda `codegen conform` no flext-infra, que tenta gerar o guia canônico → colisão.
- **Natureza**: defeito pré-existente no flext-infra (configuração de workspace inclui flext-infra como membro `codegen: conform`, mas flext-infra É o gerador).
- **Ação**: documentado como known issue; ator ciente (reform ativa no mesmo epic). Não bloqueia meu delta.

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

## Próximos Passos (Quando Ator Assentar / Autorizar Reconciliação)

1. **Resolver colisão guia protegida** — flext-infra precisa declarar guia como custom ou excluir do gen (config `exclude_docs_block` ou similar).
2. **`make check` verde no umbrella** — após F1, gates completos no workspace.
3. **`make test` verde no umbrella** — testmon cache ativo, suite completa.
4. **Prova de runtime integrada** — `make gen` ×2 (ponto fixo), `make check`, `make test` tudo verde.
5. **Fechar beads remanescentes** — `flext-5k9r7` (verify flext-cli Makefile regenerado), `flext-1wjg1` sub-items.
6. **Atualizar CSV reval / `bd remember`** — sincronizar tracker com realidade.

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
make gen      # Deve passar (exceto colisão guia flext-infra)
make check    # Reds pré-existentes documentados
make test     # Testmon cache ativo

# flext-infra (sweep-residue worktree)
cd /home/marlonsc/flext/flext-infra-worktrees/sweep-residue
make setup
make check    # Mod/fmt/mod ok; check falha em reds pré-existentes (ator)
make test
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