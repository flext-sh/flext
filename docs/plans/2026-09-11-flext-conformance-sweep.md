# Plano 2026-09-11 — FLEXT Conformance Sweep (Zero-Residue) — REVISÃO CONSOLIDADA

> Status: **DELTA PRÓPRIO 100% POUSADO E RETIRADO** — extermínio `.bak` preservado na linhagem após reescrita de história; lanes retiradas; beads fechadas.
> Revisão: 2026-09-11 (evidência re-mediada nesta sessão: tips, ancestralidade, resíduo, beads, PRs).
> Tip atual: flext `396b359a1e` · flext-infra `bff592284` · resíduo `.bak` raiz: **0**

---

## 1. FEITO — verificado com evidência nesta revisão

### 1.1 Onda 1 (sweep residue — backup-on-apply)

| Entrega | Evidência verificada |
|---------|---------------------|
| Escritor `.bak` exterminado na raiz | flext-infra **PR #673 MERGED** `8279c4f2`; `grep persist_apply_backup src/` = **0** no tip atual |
| Pouso sobreviveu à reescrita de história | `git merge-base --is-ancestor 8279c4f2 origin/0.12.0-dev` → **OK** (reescrita wip/reset não o destruiu) |
| ~1.751 resíduos exterminados (`.bak`/`.tmp`/`.qlty.bkp`) | contagem física 1.751→**0**; 0 regrowth através de ciclos `make gen` |
| Bead `flext-tldqe` | **CLOSED** — 4 evidências registradas |

### 1.2 Onda 2 (gitlink + docs)

| Entrega | Evidência verificada |
|---------|---------------------|
| Gitlink → 5ca3a961c | flext **PR #215 MERGED** `9a73d0f8` |
| Gitlink → 573eb3746 + docs sem `APPLY=Y` legado | flext **PR #216 MERGED** `c4f9fb1b` (8 guias `docs/guides/*.md` saneados) |
| `make gen` no umbrella | **VERDE**, ponto fixo atingido (colisão guia protegida era transitória) |

### 1.3 Onda 3 (ator — absorvida e verificada)

| Entrega | Evidência |
|---------|-----------|
| Descarte do wip `7a5e2e1e8` + cherry-pick `6261a1806` | registro no plano (Deliverable 1); gitlink → `dd65db77c` |
| Zero-variable APPLY (12 templates/testes corrigidos; `_require_apply` macro concertado) | commits `3000b6bc0` (infra), `4159c877b4` + `396b359a1e` (flext) |
| Law 13 — CI steps passam `APPLY=Y` | infra `bff592284` MERGED (sem PR dedicado no log de merges ≤#674) |
| Bead `flext-uw305` (requires_apply) | **CLOSED nesta revisão** — fix upstream PR #674 `573eb3746` + gen verde + ancestry OK |

### 1.4 Higiene de ciclo (executada nesta revisão)

- `flext-uw305` fechada com 4 evidências (state, git, measured, integrated).
- **Lanes retiradas** (lei de retirement): ancestor-proof `--is-ancestor` OK contra base recém-fetchada → worktrees `sweep-residue`, `sweep-conformance`, `3229sweep` removidos; branches locais `feat/sweep-residue-zero` e `feat/sweep-conformance` deletadas; remote/tracking confirmados vazios. **Zero worktrees/branches de sweep restantes.**

---

## 2. FALTA FAZER — com dono e causa

### 2.1 Meu escopo (próximos passos acionáveis)

| # | Item | Como |
|---|------|------|
| 1 | **pyproject.toml fixed-point drift** (9 testes ci_matrix vermelhos) | Reproduzir com script do plano ("Próxima Sessão"); localizar 1ª divergência apply vs verify em `_compose_project_artifact`; fix no dono (conform.py); gen ×2 ponto fixo |
| 2 | **Timeouts de teste (60s)** — setup lento/hostile env (3 testes make_environment) | São violações da Test budget law (`flext-38p39`): otimizar o teste/config, nunca subir limite |
| 3 | **`flext-5k9r7`** (make setup bug) | Verificar se regen dos membros já espalhou o guard corrigido; se sim, fechar com 4 evidências |
| 4 | **`make check`/`make test` verde no umbrella** | Depende de 1–3 + reforma estrutural do ator (2.2) |
| 5 | Umbrella local está 1 commit à frente (`135de0efae` docs/plans) | Emmetir via PR/push pós-revisão do operador |

### 2.2 Escopo do ator (NÃO invadir — reformas em voo, `flext-1wjg1`)

| Classe | Contagem (umbrella) | Dono |
|--------|--------------------:|------|
| namespace | 83 | `flext-1wjg1` / lane `z82dg-nsloc` |
| loc-cap | 5 arquivos >1k LOC | `flext-1wjg1` |
| duplication | 57 | `flext-uuhc4` (foundation dedup) |
| mypy / silent-failure / boundary | 38 / 2 / 1 | `flext-1wjg1` |
| tier-whitelist | 1 (712 violações) | `flext-y3qpq.3` |
| pyproject fixed-point drift | 9 testes | **sobreposição**: investigável pelo meu escopo (2.1.1) |

> **Regra de colaboração mantida**: meu delta é verde isolado; vermelhos estruturais idênticos no tip com/sem meu diff (padrão `flext-3cabz`).

---

## 3. Beads — estado real (verificado)

| Bead | Status | Próximo passo |
|------|--------|---------------|
| `flext-tldqe` (1.716 .bak) | **CLOSED** | — |
| `flext-uw305` (requires_apply) | **CLOSED** (esta revisão) | — |
| `flext-5k9r7` (make setup bug) | OPEN | verificar espalhamento do fix pós-regen → fechar |
| `flext-3cabz` (4 reds codegen tip) | OPEN | convergiu parcialmente; ci_matrix drift é continuação |
| `flext-1wjg1` (epic) + filhas | OPEN EM VOO | ator |
| `flext-cpkk` (CI red pós wave-2) | OPEN | ator/Reforma gates |
| `flext-czzns` | SUPERSEDED | — |

---

## 4. Evidências de pouso (git, todas merged)

| Repo | PR | Merge | Conteúdo |
|------|-----|-------|----------|
| flext-infra | #673 | `8279c4f2` | extermínio backup-on-apply + 6 type fixes |
| flext-infra | #674 | `573eb3746` | pyproject conform namespace scan scope |
| flext | #215 | `9a73d0f8` | gitlink rollup onda 1 |
| flext | #216 | `c4f9fb1b` | gitlink rollup onda 2 + docs APPLY |

---

## 5. Retomada rápida

```bash
cd /home/marlonsc/flext && git fetch origin 0.12.0-dev
env -u BEADS_DOLT_SERVER_DATABASE bd list --status=open   # beads locais (nunca herdar DB de outra sessão)
find . -name "*.bak" -not -path "*-worktrees/*" -not -path "*/.venv/*" -not -path "*/.git/*" -not -path "*/dist/*" | wc -l  # = 0
# Investigar fixed-point drift (2.1.1) e budget de testes (2.1.2) antes de novas lanes.
```

*Plano vivo — atualizar após cada deliverable (lei do plano vivente).*
