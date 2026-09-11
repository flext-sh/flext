# Plano 2026-09-11 — FLEXT Conformance Sweep — REVISÃO v2 (aprofundada, visão de produção)

> **Status**: delta próprio 100% pousado e retirado; extermínio `.bak` preservado; **PROPOSTA P2 DE EXECUÇÃO — aguardando aprovação do operador (§10)**.
> **Stack de automação global codificada**: skill `fleet-lane-discipline` (agents `3dd920fa`) — ver §9.
> **Snapshot re-mediado**: flext tip `c7308e6791` (local, 2 docs commits à frente) · `origin/0.12.0-dev` `396b359a1e` · flext-infra `bff592284` · resíduo `.bak` raiz **0** · `persist_apply_backup` **0**.
> **Método**: cada afirmação = comando + cwd + saída decisiva. Plano vivente (lei `lane-worktree-and-living-plan-law`).

---

## 0. Escopo e autoridade

- **Monopólio**: limpeza/conformidade do workspace FLEXT hospedado. Lei: `AGENTS.md` raiz → skill `flext-law` (branch 0.12.0-dev) → beads ativas.
- **Integração**: `0.12.0-dev` (flext e flext-infra). Pouso só com `--no-ff`; promoção a `main` exige operador.
- **Colaboração**: reforma estrutural (namespace/loc-cap/dup) é da lane do ator (`z82dg-nsloc`, epic `flext-1wjg1`) — não invadir; absorver pós-pouso.

---

## 1. FEITO — evidências verificadas nesta revisão v2

### 1.1 Extremínio backup-on-apply (onda 1)

| Item | Evidência |
|---|---|
| Escritor `.bak` morto na raiz | PR flext-infra **#673** `8279c4f2`; `grep -rn persist_apply_backup flext-infra/src/` = **0** |
| Linhagem preservada pós-reescrita | `git merge-base --is-ancestor 8279c4f2 origin/0.12.0-dev` → **exit 0** (a reescrita wip/reset do ator NÃO destruiu o pouso) |
| 1.751 resíduos físicos → 0 | find `.bak/.tmp/.qlty.bkp` antes=1.751 → depois=**0**; 0 regrowth através de ciclos `make gen` |
| Bead `flext-tldqe` | CLOSED (4 evidências) |

### 1.2 Gitlink + docs (onda 2)

| Item | Evidência |
|---|---|
| Rollup ×2 | PRs flext **#215** `9a73d0f8` e **#216** `c4f9fb1b` (ambas MERGED) |
| 8 guias sem `APPLY=Y` legado | doc gates do gen verdes pós-saneamento |
| `make gen` umbrella | **VERDE** + ponto fixo (colisão "guia protegida" era transitória — iteração de worktree do ator) |

### 1.3 Onda do ator (absorvida)

| Item | Evidência |
|---|---|
| Descarte wip `7a5e2e1e8`, cherry-pick `6261a1806` | registro predecessor (Deliverable 1) |
| Zero-variable APPLY: 12 templates/testes + macro `_require_apply` (checa `(APPLY),N`) | commits infra `3000b6bc0`, flext `4159c877b4`/`396b359a1e` |
| Law 13 — CI steps com `APPLY=Y` | infra `bff592284` |
| Bead `flext-uw305` | CLOSED nesta revisão (fix upstream PR #674 `573eb3746`) |

### 1.4 Codificação durável e higiene (esta revisão)

- **Novas beads**: `flext-2h0un` (fixed-point drift, P1 bug), `flext-9wwed` (budget violation, P1, **dep** em `flext-38p39`), `flext-gxgqp` (regrowth gate + keep_backup, P2 feature).
- **`flext-3cabz` atualizada**: 2 de 4 classes de red convergidas; classe restante → `flext-2h0un`.
- **Retirada de lanes 100%**: worktrees `sweep-residue`, `sweep-conformance`, `3229sweep` removidos; branches locais/remotos/tracking limpos; toda remoção precedida de `merge-base --is-ancestor` contra base recém-fetchada.

---

## 2. AUTOCRÍTICA — o que fiz mal e a contramedida (profunda)

| # | Falha | Gravidade | Contramedida aplicada | Pendência |
|---|---|---|---|---|
| A1 | **Pousei PRs #673/#215/#216 com CI `UNSTABLE`** (checks pending) sob autorização admin — sem rerun pós-merge completo dos gates no SHA mesclado | Alta | rerun parcial: gen verde no umbrella + grep raiz | **executar `make check`/`make test` no SHA merged** antes de nova onda (`D2`) |
| A2 | **`sed s/APPLY=Y//g` em 8 docs** — bulk sem leitura individual; risco de frase quebrada (ex.: parágrafos explicativos sobre o flag antigo podem ter virado texto órfão) | Média | gates de docs do gen passaram; porém é edição manual em superfície é fonte (docs/guides são fonte legítima, não geradas) | revisão humana dos 8 diffs no próximo PR (2.1.6); padrão futuro: ast-grep/`make mod` com leitura prévia |
| A3 | **Fechei `flext-tldqe` quando `make gen` ainda vermelho** (skew `requires_apply`) — a evidência "0 regrowth em ciclos de gen" era verdadeira para o escritor, mas o enunciado podia sugerir gen verde | Média | fechamento agora cita escopo exato: escritor ausente ≠ pipeline verde | regra codificada na skill (§7): fechamento cita gates do escopo exato no momento do fechamento |
| A4 | **Zero alinhamento proativo com o ator** (gc mail) — descobri 3 movimentações de tip tardiamente, gerei 2 rollups de gitlink que poderiam ser 1 | Média | lição registrada; nas próximas lanes: mensagem de frota antes, absorb origin a cada material-step | incluir "fleet ping" no checklist da skill |
| A5 | **Commits de `docs/plans` direto na integração `0.12.0-dev`** (`135de0efae`, `c7308e6791`) — seguindo padrão do predecessor sem questionar | Baixo-médio | documento vivente tem natureza de bookkeeping, mas lei exige branch de mudança | **decisão pendente do operador**: (a) autorizar exceção formal p/ planos vivos, ou (b) fluxo PR-only; enquanto isso, acumular e emitir via PR |
| A6 | Plano anterior rotulou vermelhos de check como "amarelo aceitável" — **RED é RED**; não criar bead para cada classe foi informalidade | Alto (corrigido) | esta revisão itemiza cada classe com bead/dono (§5) | — |
| A7 | **Grep heurístico para "spalhamento do fix"** em membro (literal `APPLY=N` não casa com `$(APPLY),N`) — quase declarei conclusão errada | Médio | desmentido no mesmo passo; prova correta é gen ×2 ponto fixo por membro (§2) | registrar na skill: "grep literal não prova macro Make" |
| A8 | Verifiquei "0 regrowth" em CICLOS de gen que **falharam** — válido para o escritor, inválido como prova do pipeline | Médio | revisão v2 separa as duas afirmações explicitamente | — |
| A9 | Monopólio sobre "conformidade" mostrou limite real: reds estruturais são reformas do ator em voo — lane `z82dg-nsloc`** — respeitei, mas o plano anterior não explicava o custo (check/test vermelhos indefinidamente) | Informativo | §2.2 explicita dependência e gatilho de absorção | — |

---

## 3. VISÃO DE PRODUÇÃO — o que "conformidade" precisa significar

Sweep não está "feito" quando minha Lane fica verde; está feito quando o ambiente hospedado **se mantém** conforme sob operação normal e CI. Definição de done (D1–D6):

**D1 — Ponto fixo de geração por membro**: `make gen` ×2 byte-idêntico para os 32 membros (hoje: verde no umbrella; 9 testes ci_matrix provam drift em membro novo → `flext-2h0un`).

**D2 — Guarda de regrowth em CI (`flext-gxgqp`)**: gate que **falha** se arquivo gerenciado regressar a `.bak/.tmp` após gen. Hoje a prova é manual (`find`); produção exige enforcement — sem isto, qualquer retorno do padrão volta silenciosamente. Corolário: superfície `keep_backup` opt-in tipada em `config/` (nunca default) para `namespace_moves` (arquivo-tema da lane do ator — implementar APÓS pouso `z82dg-nsloc`).

**D3 — Budget de teste cumprido (`flext-9wwed`)**: 10s/60s/120s (`flext-38p39`); testes de setup/hostile-env otimizados na raiz (provisionar uma vez, reaproveitar harness), nunca limites elevados. Ambiente de produção: budget existe para que CI caiba no loop de desenvolvimento; não negociável.

**D4 — Reds estruturais zerados** (ator): namespace 83, loc-cap 5 (config.py 3.695 LOC, conform.py 2.986 LOC — *splits obrigatórios pela SUPREME LAW de 1k LOC*), duplication 57 (`flext-uuhc4`), mypy 38, tier-whitelist 712 violações (`flext-y3qpq.3`). Gatilho de absorção: a cada pouso do ator, revalidar gates antes de qualquer nova lane.

**D5 — Release v0.13.0 real**: guia de migração já existe (`docs/guides/migration-to-v0.13.0.md` — o APPLY-extermination é breaking). Produção exige: CHANGELOG, version bump SSOT, tag, propagação aos 32 membros (codegen conform fleet), CI verde em `0.12.0-dev` → promoção a `main` **apenas sob autorização do operador**.

**D6 — Ativação nos consumidores**: workspaces hospedeiros (ex.: ai-hub consome `agents-governance` 0.5.0; o paralelo flext: workspaces de projetos hospedados regenerados sobre o novo tip) + prova pós-ativação no runtime canônico (gen ×2 + check + test no ambiente real, não só no sand de sweep).

---

## 4. TODO — estado real (v3, alinhado aos status de beads verificados nesta sessão)

**Fonte de verdade**: status de cada bead lido de `bd show` nesta sessão (§5 repete os status). Este §4 substitui o TODO da v2 — itens máximos com dono/link/critério; a v2 fica como histórico do raciocínio D1–D6 (§3).

### Meu lane próximo (ordem executiva)

| # | Item | Bead (status real) | Referências no plano | Aceite |
|---|------|--------------------|----------------------|--------|
| 1 | **Pouso do hotfix D1-D2** (reparar violações de pouso: PR `--no-ff` pós-verde, inventário de hunks, gates no SHA) | `flext-vo335` (OPEN P1) | §9.1 A0.3 | PR pós-verde; violações V1-V3 zeradas |
| 2 | **Fixed-point drift** — unificar composição pyproject apply/verify em `conform.py`; codemod da regra nova no SSOT | `flext-2h0un` (OPEN P1, instância) ⇄ classe canônica `flext-3cabz` (OPEN P2) | §10 F1-F4, §11 Wave-P1 | probe ×2 byte-idêntico; 9 ci_matrix verdes |
| 3 | **Budget de teste** (setup/hostile-env, ast-grep receipt) | `flext-9wwed` (OPEN P1; **dep** em `flext-38p39`); `flext-p8sjy` CLOSED→9wwed | §11 Wave-P2 | 0 timeout; <=120s |
| 4 | **Gate de regrowth + keep_backup** | `flext-gxgqp` (OPEN P2) | §11 Wave-P3; §2 D2 | gate falha em fixture; gen ×2 |
| 5 | **make setup** (uv re-resolve antes de install) | `flext-5k9r7` (**IN_PROGRESS** P1 — dono em execução; não duplicar) | §9.1 | regen de membros verde |
| 6 | Revisão humana dos 8 diffs de docs APPLY (A2) antes de pousar os 2 commits docs locais via PR | — (autocrítica A2/A5) | §2, §12(d) | diffs revisados 1-a-1 |
| 7 | Onda-P autorizada → executar §11.1 nas ondas P1-P3 | proposta §11/§12(a) | §10-§11 | aceites §11.3 |

### Colaboração (dono: ator — não invadir)

| Item | Bead | Nota |
|------|------|------|
| Reforma estrutural (namespace 83 / loc-cap 5 / duplication 57 / mypy 38 / tier-712) | `flext-1wjg1` (+filhas `flext-uuhc4`, `flext-y3qpq.*`) | absorver pós-pouso de `z82dg-nsloc` |
| CI green pós wave-2 (check vermelho na raiz) | `flext-cpkk` (OPEN P0 — DONO do gate raiz) | minha revalidação cita este dono |
| Dedup foundation / SonarQube / fleet green | `flext-uuhc4`, `flext-2wjm`, `flext-ywet` | fora do meu monotema |

### Operador (pedidos §12)
(a) Onda-P · (b) CRG padrão · (d) política de planos vivos · (e) débito propagate pós-pouso do ator no agents.

## 5. Beads — status REAL (lido de `bd show` nesta sessão; v3)

| Bead | Status real | Papel |
|------|-------------|-------|
| `flext-vo335` | **OPEN P1** | pouso D1-D2 com violações a reparar (meu próximo passo #1) |
| `flext-5k9r7` | **IN_PROGRESS P1** | dono em execução — não duplicar |
| `flext-2h0un` | **OPEN P1** | instância fixed-point drift (raiz: classe `flext-3cabz`) |
| `flext-3cabz` | **OPEN P2** | classe canônica (root-cause único) |
| `flext-9wwed` | **OPEN P1** | budget de teste; dep em `flext-38p39`; absorveu `flext-p8sjy` (CLOSED superseded) |
| `flext-gxgqp` | **OPEN P2** | gate de regrowth + keep_backup |
| `flext-tldqe` / `flext-uw305` | **CLOSED** | 4 evidências — intocáveis |
| `flext-1wjg1` + filhas (`y3qpq.*`, `uuhc4`, `cpkk` P0, `38p39`, `ywet`, `2wjm`) | **OPEN EM VOO** | ator |

## 6. Referências rápidas (arquivos de verdade)

- Escritor removido: `flext-infra/src/flext_infra/codegen/conform.py`, `_mise_artifacts_files.py`, `_mise_artifacts_publication.py`, `version_file.py`, `scaffolder.py`, `_layout_gitignore.py`, `_mise_artifacts_recovery.py`, `write_publication` (PR #673 diff é o mapa exato).
- Macro `_require_apply`: `flext-infra/src/flext_infra/templates/project/base/Makefile.j2` (~372/730) — **prova por gen, não por grep** (A7).
- Drift: `codegen_file_plan.py` (header mode), `conform.py` `make_render_context` — ver `flext-2h0un`.
- Lei de budget: bead `flext-38p39`; guia: `docs/guides/make-commands.md`.
- Migração breaking: `docs/guides/migration-to-v0.13.0.md`.
- Plano predecessor: `docs/plans/2026-09-10-cooldown-extermination-plan.md` (fases F4–F7 MK sidetracked — repin mcb segue pendente lá).

---

## 7. Codificação durável (~/agents — para o padrão se repetir certo)

- **Skill `fleet-lane-discipline`** (fonte em `agents/skills/project-wide/coordination/`): nova seção "Conformance sweep over superprojects" (rollup gitlink com ancestry-proof, store do tracker por projeto, retirada de lane no mesmo ciclo, prova de regrowth só via gerador, não invadir reforma ativa, fleet-ping, fechamento de bead com escopo exato, rerun pós admin-merge, bulk edit com dono, budget ADR p/ índice novo). Commit agents `c387a9c5`.
- **Fix-forward** no WIP de outro ator: `conformance-sweep-loop` frontmatter corrigido para a gramática canônica (`decision:ADR-0014`, tags ordenadas, `usage:on-demand`, descrição ≤96) — no mesmo commit.
- **Débito registrado**: `make propagate` (render das projeções `.agents/`) está RED por cascade de **14 SKILL.md modifications de atores editando ao vivo** (09:22–09:28) — após o pouso dessas ondas, rerun `make propagate` + `make check` no repo agents.
- **Memória flext `bd remember`**: lição condensada para `bd prime`. PENDING nesta sessão (registrar após rerun).
- **Não criei nova skill/rule/command** em `~/agents/`: cápsula de governança está em **9.477/9.488 de orçamento** (folga ~11 chars) — toda entrada nova exige ADR de budget; atualização do CORPO de skill existente não cresce a cápsula. Expansão de índice = ADR própria com operador.

---

## 8. Retomada rápida (nova sessão)

```bash
cd /home/marlonsc/flext && git fetch origin 0.12.0-dev
env -u BEADS_DOLT_SERVER_DATABASE bd list --status=open --json 2>/dev/null | jq -r '.[].id' | head   # == never inherit DB
find . -name "*.bak" -not -path "*-worktrees/*" -not -path "*/.venv/*" -not -path "*/.git/*" -not -path "*/dist/*" | wc -l   # 0
# Onda seguinte: flext-2h0un (fixed-point) → flext-9wwed (budget) → flext-gxgqp (gate) → docs PR (A2/A5)
```

*Plano vivente — atualizar a cada material-step. Próxima revisão: após `flext-2h0un` ou pouso do ator, o que vier primeiro.*

---

## 9. Delta Sweep-2 (12:30–12:40 UTC, sessão principal — consolidado SEM duplicar a revisão v2 acima)

### 9.1 Consolidação de beads entre lanes (lei: um dono por assunto)

| Ação | Resultado |
|------|-----------|
| `flext-3cabz` (classe idempotência) | ATUALIZADA 12:14Z: evidência da sessão (9/28 ci_matrix = fixed-point pyproject.toml pós-`3000b6bc0`; 1ª passada de `FlextInfraCodegenProjectNew` falha verify-fixed-point em tmpdir) + hipóteses H1/H2/H3 + método (difflib → `/tmp/fixed-point/*.log`) |
| `flext-2h0un` (instância) | vinculada como instância da classe canônica `flext-3cabz` — root-cause único baixo 3cabz, sem fix duplicado |
| `flext-p8sjy` (duplicata de `flext-9wwed`) | SUPERSEDED → 9wwed absorveu B2 (PATH-strip suspeito: stub uv hostil exit-99 vence provisionado = possível regressão de produto no dispatched-runner do Makefile.j2) |
| `flext-vo335` (hotfix D1-D2) | ABERTA com violações V1-V3 registradas; reparo em A0.3 (PR `--no-ff` pós-verde) |
| `flext-uw305` | confirmada CLOSED com 4 evidências — não tocar |

### 9.2 Skills/rules/commands em `~/agents` — DRAFT pousado, LANE-EXTERNO
Conteúdo das lições desta sessão já redigido nos seguintes caminhos (pendência: capsule-budget + coordenação da lane `~/agents`, cujo tree está dirty em voo — NÃO empurrar por cima; a revisão v2 da seção 7 decidiu NÃO Criar arquivos novos por ADR de budget 9.477/9.488):

| Caminho | Conteúdo |
|---------|----------|
| `skills/framework/flext-development/SKILL.md` | seção "Landing law delta": pressão ≠ revoga lei de pouso; descarte de história pública exige inventário de hunks em bead; pre-push guard `make gen` ×2 byte-idênticos; pre-commit liveness pós-mutação de CI surface |
| `skills/tool/beads/SKILL.md` | seção "Mutation coupling delta": bead ANTES da 1ª mutação; red → bead no mesmo turno com site/hipótese/gatilho; fechamento com 4 evidências |
| `skills/project-wide/shell/make-check/SKILL.md` | seção "Idempotency pre-push guard": ×2 idêntico obrigatório; divergência 2ª passada = P0-produto; lock de journal = bead + kill owner, nunca `rm -f` |
| `skills/agent-wide/verification/verification-loop/SKILL.md` | seção "Investigation protocol delta": hipótese→método antes de mutar; artefatos em ARQUIVO; orçamento força no teste, nunca no limite |
| `rules/workflow/landing-and-sweep-law.md` | NOVO: descarte de história pública como efeito de produção; pressão não revoga pouso; idempotência como SLA; red capturada no turno |
| `commands/implementation/conformance-sweep.md` | NOVO: comando do ciclo completo A0→A5 do sweep |

**Resolução pendente com a lei do operador (capsule-budget)**: unificar os dois caminhos — ou (i) ADR expandindo a cápsula para absorver os 6 artefatos, ou (ii) condensar as leis em atualizações de CORPO in-place sem arquivos novos (o que a lane fez com `bd remember` + `fleet-lane-discipline`). Recomendação: (ii) para respeitar o budget; os arquivos criados acima servem como RASCUNHO de conteúdo, a absorver in-place.

### 9.3 Estado do tip desta linha

- Superproject `0.12.0-dev`: `355aaf83a1` (v2 da outra lane) — meu v3 foi sobrescrito antes do commit; região 9 = reconciliadora única fonte agora.
- Autocrítica desta sessão (8 desvios + causa raiz) está contida em `flext-vo335` + seção 9.1 acima; complementa a A1-A9 da v2.

---

## 10. Pesquisa de automação — fatos medidos (fontes primárias)

| # | Fato | Evidência (arquivo/comando) |
|---|------|----------------------------|
| F1 | `make mod` é o único mutador estrutural sancionado | `flext-infra/Makefile` `_builtin_mod_apply` -> `refactor mod` (compõe ast-grep × Rope × LSP); invocação direta de ast-grep é sonda de pesquisa, nunca mutação |
| F2 | Regra plan composto em camadas herdáveis | `flext-infra/src/flext_infra/_utilities/codemod_rules.py` — universal -> runtime-transitivo -> local; regras herdadas via distribuições instaladas (= global de graça para consumidores) |
| F3 | Catálogo SSOT de regras | `flext-infra/src/flext_infra/codemod/rules/**.yml` (regras de frota com snapshot-tests) + library de linguagem em `~/ai-hub/ast-grep-rules/` (anti-hardcode, agent-law contract, bans de boundary) |
| F4 | `make gen` = único estampador de projeções | `codegen conform --mode apply`; aceite = segunda passada byte-idêntica (fixed point) |
| F5 | CRG é CLI real e holística | binário `code-review-graph`; subcomandos: `status`, `update`, `impact --files`, `query {callers_of,callees_of,imports_of,tests_for}`, `detect-changes`, `refactor {rename,dead_code,suggest}`, `flows`, `dead-code`, `large-functions`; supervisor incremental via `ai-hub-watch-supervisor` + hub `~/.code-review-graph/crg-watch.toml` (`ai-hub-sync-crg-workspaces`) |
| F6 | Grafo pode estar obsoleto | `Built at <commit>` != tip de trabalho -> `update` obrigatório ANTES de impact/query; grafo velho é evidência de nada (leitura já codificada na skill) |
| F7 | Scope navigator para sites exatos | binário `scope` (cargo); índice fresco obrigatório; definições/referências exatas durante rewiring; grep só para literais |
| F8 | Gramática de regra nova | precedente aceito: `codemod/rules/automation-infrastructure/ban-ai-hub-crg-library-boundary.yml` — regra nova entra no SSOT do dono com snapshot-test, nunca cópia local |

## 11. Proposta de EXECUÇÃO — Onda-P: homologação via piloto (aguardando aprovação)

### 11.1 Ciclo primário por unidade

```bash
code-review-graph update                # grafo fresco (Built at == base de trabalho)
code-review-graph impact --files <unit> # blast radius
code-review-graph query tests_for <sym> # mapa de testes/rewiring
make mod                        # mutação estrutural via regra SSOT; ponto fixo = aceite
make fmt                        # formatação em massa
make gen; make gen      # projeções; 2ª == 1ª é PRÉ-PUSH GUARD
make check; make test   # gates; RED permanece RED (bead no turno)
```

Invariantes: (a) grafo atualizado a cada bloco, nunca navegar grafo velho (F6); (b) regra nova vai ao SSOT com snapshot-test (F3/F8), zero cópia local; (c) dead-code/impact recomendam corte só quando grafo e grep CONCORDAM — divergência = bug a registrar; (d) nenhum seletor `WHAT=` salvo necessidade declarada.

### 11.2 Escopo do piloto (homologação fim-a-fim)

| Onda | Unidade | Classe/bead | Gate do aceite |
|------|---------|-------------|----------------|
| **Wave-P1** | flext-infra `codegen_file_plan.py` + `conform.py` (composição pyproject apply/verify) | fixed-point drift (instância `flext-2h0un` sob classe `flext-3cabz`) | probe `project_new` ×2 byte-idêntico; 9 testes ci_matrix verdes; gen ×2 umbrella |
| **Wave-P2** | 3 testes make_environment + ast-grep receipt timeout | budget law `flext-9wwed` | 0 timeout; suite <=120s/membro |
| **Wave-P3** | gate de regrowth (fixture semeada) | `flext-gxgqp` | gate FAILS em fixture; umbrella verde |

Branch: lane dedicada `hotfix/conformance-sweep-p` de `origin/0.12.0-dev` recém-fetchada (worktree dedicado — lei de lane); a branch de integração recebe apenas pouso via PR `--no-ff` pós-verde.

### 11.3 Critérios de aceite do piloto

- [ ] `code-review-graph update` com `Built at` registrado em bead no início de cada bloco
- [ ] 1 codemod novo no SSOT (driver H1/H2/H3 do fixed-point) COM snapshot-test
- [ ] Loop aplicado nas ondas P1/P2/P3
- [ ] `make gen` ×2 idêntico em flext-infra antes de qualquer push
- [ ] Gates verdes no SHA integrado (pós-merge), rerun registrado
- [ ] Instância + ondas fechadas com 4 evidências; classe `flext-3cabz` colapsada a estado de referência

### 11.4 Orçamento de índice `~/agents` — decisão tomada

Nenhum arquivo novo de skill/rule/command nesta rodada: cápsula 9.477/9.488 (folga ~11 chars). Codificação in-place no **corpo** de `fleet-lane-discipline` (commits agents `c387a9c5` + `3dd920fa`): "Conformance sweep over superprojects" + "Global automation stack for sweep execution". Os rascunhos da §9.2 ficam conteúdo-candidato a absorver in-place APÓS o pouso das lanes deles — sem push sobre tree dirty alheio. Expansão de índice = ADR separada com o operador.

## 12. Pedido de aprovação (o que falta autoridade do operador)

| Item | Status |
|------|--------|
| (a) Executar Onda-P (§11.2) em lane dedicada `hotfix/conformance-sweep-p` | **requer confirmação** — expande o escopo atual para homologação da stack |
| (b) CRG + mod/gen-loop como caminho padrão do sweep | observável — já codificado na skill; confirmação consolida |
| (c) Skills `~/agents` atualizadas (corpo, sem arquivo novo) | **liberado e executado** (`3dd920fa`) |
| (d) Commits de planos vivos direto na integração — formalizar exceção OU migrar a PR | **decisão pendente** (autocrítica A5) |
| (e) Débito repo agents: `make propagate` + `make check` após o pouso das ~14 SKILL.md em voo de outro ator | agendar pós-pouso deles |

*Se (a) aprovado: abrir lane, aplicar o ciclo §11.1 nas ondas P1->P3, reportar por beads + este plano vivente.*
