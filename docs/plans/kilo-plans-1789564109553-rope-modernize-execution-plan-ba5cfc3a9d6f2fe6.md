# Rope Modernize — Plano de Execução v3 (absorção contínua automatizada + PR lane)

<!-- TOC START -->
- [0. EXCLUSÃO AUTORITATIVA (operador)](#0-exclusao-autoritativa-operador)
- [1. NÚCLEO DE AUTOMAÇÃO — ~/wip-hier.sh (uso avançado, sem loops ad-hoc)](#1-nucleo-de-automacao-wip-hiersh-uso-avancado-sem-loops-ad-hoc)
- [2. PR DA LANE NO GITHUB — abrir NO COMEÇO, manter vivo](#2-pr-da-lane-no-github-abrir-no-comeco-manter-vivo)
- [3. LEI DE RESOLUÇÃO DE CONFLITOS (recorrente em toda absorção)](#3-lei-de-resolucao-de-conflitos-recorrente-em-toda-absorcao)
- [4. ESTADO VERIFICADO (2026-09-16T14:30Z)](#4-estado-verificado-2026-09-16t1430z)
- [5. FASES](#5-fases)
  - [R0 — Pousar os merges em andamento + PR (primeira sessão de execução)](#r0-pousar-os-merges-em-andamento-pr-primeira-sessao-de-execucao)
  - [R1 — Ciclo-padrão recorrente (executado NO INÍCIO DE CADA FASE/onda seguinte)](#r1-ciclo-padrao-recorrente-executado-no-inicio-de-cada-faseonda-seguinte)
  - [R2 — Provar mod semantic phase-0 (desbloqueia flext-oquk7)](#r2-provar-mod-semantic-phase-0-desbloqueia-flext-oquk7)
  - [R3 — Ondas de ataque aos 71 residuais (58F+13E, infra) — uma por vez, R1 antes de cada](#r3-ondas-de-ataque-aos-71-residuais-58f13e-infra-uma-por-vez-r1-antes-de-cada)
  - [R4 — pyrefly 79 por ondas](#r4-pyrefly-79-por-ondas)
  - [R5 — Fechamento](#r5-fechamento)
- [6. REGRAS DE OURO (v2 §1 mantida + adições)](#6-regras-de-ouro-v2-1-mantida-adicoes)
- [7. RISCOS](#7-riscos)
- [8. Pendências de decisão do operador (não bloqueiam R0)](#8-pendencias-de-decisao-do-operador-nao-bloqueiam-r0)
<!-- TOC END -->

> Historical evidence only. This plan records an earlier execution context and
> its command examples are not current workspace guidance. Use the root
> `AGENTS.md` and `make help` for the active contract.

Data: 2026-09-16T14:35Z · Worktree: `~/flext-worktrees/rope-modernize` · Lane: `feature/rope-modernize` (32/32 repos)
Planos-base absorvidos: `1789500358999-rope-modernize-unification.md` (v4 render purity) + v2 (auto-crítica §1 mantida integralmente).

## 0. EXCLUSÃO AUTORITATIVA (operador)

**Beads/Dolt/metadata FORA do escopo.** Beads autoritativos = Gas City (banco `flext` via direnv; `bd status` 3265/277 open — funcionando). Não rodar `wip-beads.sh`, não mutar `.beads/*`, sem sync/export. `bd` somente-leitura; fechamento de bead com evidência é permitido (governança). Única exceção: `bd dolt commit -m "..."` para destravar gate `unmerged Beads state` — documentada no log da onda.

## 1. NÚCLEO DE AUTOMAÇÃO — `~/wip-hier.sh` (uso avançado, sem loops ad-hoc)

O script é o operador padrão de frota. Capacidades verificadas no código-fonte (1527 linhas): descobre super+submódulos (ordem deepest-first), preserve-commits WIP de toda a hierarquia, alinha branches, **push com retry automático: fetch + `merge --no-ff` da branch de integração quando o push é rejeitado**, detecta behind → `merge --no-ff`, fast-forwarda gitlinks, roda os verbos canônicos (`setup deps gen fix fmt check test`) apenas onde a posse está limpa (guards: locked / HEAD=integração / sujidade alheia → skip), e **retirement**: poda worktrees stale, apaga branches locais/remotas já contidas na integração, fecha PRs sem nada a oferecer à base.

**Invocações padrão do plano (sempre da raiz da worktree, via background_process, log analisado):**

```bash
~/wip-hier.sh                                  # 1) DISCOVERY: tabela completa (tree, branch, sha, dirty, ahead, PR, behind) — SEMPRE primeiro
~/wip-hier.sh --apply                          # 2) CAPTURE: preserve-commit + align + push lanes (+merge --no-ff automático em push rejeitado)
~/wip-hier.sh --apply --no-retire              #    variante: quando preservar branches/PRs candidatos ainda não absorvidos
```

**Regras de uso:**
- RODAR discovery antes de qualquer fase; o estado da frota decide o passo seguinte — nunca assumir.
- `--apply` padrão; `--no-retire` somente enquanto houver lanes candidatas vivas (ex.: #235/#681 pré-absorção).
- Conflitos que o git não resolve sozinho (modify/delete, conteúdo divergente) = resolução manual PELA LEI (§3) — o script para ali e o resolution é meu, nunca `git checkout --theirs/ours` cego.
- Verbos canônicos do script são o ciclo E-ABS-5 completo por membro; skip por sujidade alheia é SINAL de outro dono ativo — registrar e não insistir.
- Logs: `~/.local/state/wip-hier/latest.log` — analisar após cada rodada (background + subagente para logs grandes).

## 2. PR DA LANE NO GITHUB — abrir NO COMEÇO, manter vivo

1. **R0.0 (primeiro ato da execução):** abrir/verificar PRs da lane como registro vivo:
   - `gh pr create -R flext-sh/flext --base 0.12.0-dev --head feature/rope-modernize -t "rope-modernize: unified rope engine (one writer per destination, mod semantic phase-0)" -F pr-body.md`
   - `gh pr create -R flext-sh/flext-infra --base 0.12.0-dev --head feature/rope-modernize -t "infra: rope modernize engine + lazy-init one-writer fix" -F pr-body-infra.md`
   - Se já existir PR aberto para a lane: `gh pr edit` no body (nunca duplicar).
2. **Toda onda pousada** = commit+push + `gh pr edit <n> --body` anexando evidência numérica (test-ids F/E, exit codes, SHAs). O body do PR é o diário da lane.
3. PRs são da lane, não de snapshot: manter abertos até o estabilizador/integrador mergear; o retirement do wip-hier os fecha quando vazios — comportamento correto, não interferir.
4. `gh` pode exigir aprovação por-invocação no sandbox: preparar os comandos exatos e pedir desbloqueio em lote no início da sessão de execução.

## 3. LEI DE RESOLUÇÃO DE CONFLITOS (recorrente em toda absorção)

1. **Killed files ficam mortos** (`_lazy_init_import_alignment.py` etc.): `git rm` na resolução; integração só reformata/extermina o que a lane já matou.
2. **A lane é dona** de: rules tree (config/rules/{mod,ast,rope}), env-boundary (settings tipados + gateway `u.Infra.env_lookup`), unificação `_codegen` (partials), stub result, alignment (mod-side), toggle `mod.phases`, guards (`ban-copy-from-result-alias` fica).
3. **`.envrc`**: versão lane vence (`source_env_if_exists` tipado, CI-safe) sobre `watch_file`+`source_env` da integração.
4. **Submodule pointers** = tips da lane (contêm a integração via merges `--no-ff`).
5. **Dirty idêntico em N membros** = drift de projeção do template absorvido: preserve-commit via wip-hier (não investigar por repo).
6. Never rebase/reset/stash/force-push de trabalho alheio; `merge --no-ff` é o único mecanismo; commit scoped por paths (`git add -A` só em preserve-commit da lane no próprio worktree — o que o wip-hier já faz por nós).
7. Após cada absorção com toque em templates: `make gen` ×2 — segunda rodada tree limpa (idempotência).

## 4. ESTADO VERIFICADO (2026-09-16T14:30Z)

| Item | Estado | Evidência |
| --- | --- | --- |
| lazy_init fix (flext-j64nz) | LANDED+PUSHED, bead CLOSED | infra `4ee618f59`; lane `3fb4505c7`; ruff verde; probe revertido |
| Absorção tip anterior | 32/32 MERGED+PUSHED | infra `3fb4505c7`; 30 membros; flext-tests `da0a506`; super `a3793f9010` |
| **MERGES EM ANDAMENTO** | **31/31 membros "modified content"** — WIP concorrente do estabilizador ativo (tabs: infra templates/cli_routes_refactor/_config/contract, grpc Makefile) | `git status` super 14:33Z |
| Suíte infra | 58F+13E estável (sem regressão pré/pós-merge) | rodadas 573s/143s; conjunto por test-id idêntico |
| pyrefly infra src | **79 erros** | `uv run pyrefly check src` |
| gen ×2 super | RUN1 exit 0; RUN2 tree limpa | bgp_0aa960a2; super clean |
| Lanes candidatas NÃO absorvidas | super: `origin/aeolian-sodalite` (2 commits, PR #235); infra: `origin/promoted-framework-lift` (1 commit, PR #681) | `git log HEAD..origin/*` |
| mod ×2 alignment | NÃO validado | pendente (R2) |
| PRs da lane | NÃO existem ainda | `gh pr list` (só #235/#681/#245/#246/#231) |

## 5. FASES

### R0 — Pousar os merges em andamento + PR (primeira sessão de execução)
1. `~/wip-hier.sh` (discovery, background) → ler tabela; confirmar escopo dos 31 dirty.
2. Absorver lanes candidatas (para o retirement não as matar e o conteúdo entrar na lane):
   - super: `git merge --no-ff origin/aeolian-sodalite` (2 preserve-commits, PR #235);
   - infra: `git merge --no-ff origin/promoted-framework-lift` (`0f4bffe25`, PR #681);
   - conflitos → §3; push imediato de cada repo.
3. `~/wip-hier.sh --apply --no-retire` → capture da frota inteira: preserve-commits + push lanes (retry com merge --no-ff automático onde o remote avançou). Conflitos restantes → §3, re-push.
4. Verificar tip nova do estabilizador (fetch nos 32; o discovery do passo 1 já mostra behind): reabsorver pela §3 se houver.
5. `make gen` ×2 no super (idempotência); commit+push de qualquer drift.
6. Abrir PRs da lane (§2.1) e popular o body com o estado R0.
7. `~/wip-hier.sh --apply` (agora COM retirement) → limpa branches/worktrees/PRs já contidos.

### R1 — Ciclo-padrão recorrente (executado NO INÍCIO DE CADA FASE/onda seguinte)
```text
discovery (wip-hier dry-run) → há dirty/behind/nova lane?
  sim  → absorb candidatos (merge --no-ff, lei §3) → wip-hier --apply → gen ×2 → push → PR edit (evidência)
  não  → prosseguir a onda
```
Nenhuma onda de código começa com a frota suja ou behind. Este ciclo substitui TODOS os loops ad-hoc de multi-repo da v2.

### R2 — Provar mod semantic phase-0 (desbloqueia flext-oquk7)
1. Em `flext-infra`: `make mod` ×2 (background, log). Critérios: exit 0 ×2; 2ª rodada zero findings; journal sem dual-ownership em api.py/cli.py; tree limpa.
2. Se phase-0 morreu por acoplamento ao lazy_init gen-side: root cause em `codemod/semantic_apply.py` (phase 0 self-contained); probe env-gated revertido antes do commit.
3. Evidência por test-id → `bd close flext-oquk7` com números (governança permitida).

### R3 — Ondas de ataque aos 71 residuais (58F+13E, infra) — uma por vez, R1 antes de cada
Regra por onda: root-cause no owner → fix → re-run do arquivo de teste owner (números por test-id) → commit scoped + push → `gh pr edit` anexando evidência. Testes não-conformes à lei: REMOVER após provar behavior atual pela rota pública (CLI/facade) — nunca adaptar para passar.
- **W1 — DocsGenerateRequest/apply + docs/auditor (~12):** pesquisar dono atual do toggle apply (pipeline? CLI flag?); campo migrou → testes seguem a rota pública; campo exterminado → remover testes com prova de runtime. Arquivos: `test_codegen_conform`(2), `docs/main_*`(3), `generator_*`(4), `auditor_command_contract`(3).
- **W2 — YAML timestamp precision (12, `test_plan_collection`):** fix no serializer (preservação por construction), não no teste.
- **W3 — Fixture `.beads/metadata.json` (13 ERROR):** fixture usa caminho canônico de conform (é fixture de codegen, não trabalho de beads).
- **W4 — Conform round-trip + beads-projection + fanout/dispatch (~10).**
- **W5 — Check CLI/extended + mod circuit (~10).**
- **W6 — Cauda (~8):** lazy_init alias/helpers/process, pydantic_modernizer, ast-grep rules, root export, maintenance headers, invocation scope.
Ferramentas: `code-review-graph impact` antes de mexer em owners; `ast-grep` search para padrões duplicados; `make mod` para fixes estruturais repetidos.

### R4 — pyrefly 79 por ondas
Recount por arquivo (output salvo/agrupado) → ondas por módulo (`_conform/{render,execute,plan}` primeiro — flext-1x66z) → `make check` verde no escopo → commit+push+PR edit. `safety.yaml`: conferir realidade dos 4 remanescentes antes.

### R5 — Fechamento
Suíte numérica canônica por membro atingido (venv próprio, `make test` no dir); `~/.agents/VALIDATE_ON_CHANGE.md` += leis novas (probe-grep pré-commit; testmon totals não são prova; direnv beads; scripts de frota em arquivo; dirty idêntico = drift de projeção); board ALL + beads com evidência; PRs da lane atualizados com o mapa final.

## 6. REGRAS DE OURO (v2 §1 mantida + adições)

- Probe: revertido ANTES do commit; grep de segurança no staged (`environ.get|print(|FLEXT_DEBUG`).
- Evidência = conjunto de test-ids F/E + exit codes; totals de passed com testmon não provam nada.
- direnv antes de bd/make; endpoint dolt city-owned; nunca pinar porta.
- Longos = background_process + subagente para análise; frota = wip-hier (nunca loops inline `bash -c`).
- make <verbo> no dir do projeto; nunca seletores inventados; `mod ×2`/`gen ×2` exigem 2ª rodada limpa.
- NUNCA deduzir; frames reais; parar e perguntar em conflito autoritativo.

## 7. RISCOS

1. **Estabilizador ativo na MESMA worktree** (31 dirty agora): wip-hier pula verbos em trees com dono ativo — correto; capturar WIP dele via preserve-commit (é o design do script) e não editar arquivos com tabs abertos dele simultaneamente.
2. **Retirement prematuro** de #235/#681: usar `--no-retire` até as lanes candidatas estarem absorvidas na nossa lane (R0.2 antes de qualquer retirement).
3. **gh no sandbox** pode pedir aprovação por comando: pedir desbloqueio em lote no início.
4. **mod ×2 pode expor acoplamento** do phase-0 ao gen-side morto: R2 antes de R3 (a correção pode mover código que as ondas W4/W5 tocam).
5. **Remoção de testes**: sempre precedida de prova de runtime pela rota pública; evidência no PR.

## 8. Pendências de decisão do operador (não bloqueiam R0)

- PR #231 (wip duplicate mayor/rig): recomendo fechar (marcador de duplicata) — aguardo ordem.
- Dependabot #245/#246: fora do mandato absorvedor até ordem explícita.
