# Handoff — Sessão conformance sweep 2026-09-11 (12:43 UTC)

> Commeo restrito: pega-o-voa. Este documento é o CURSOR completo para retomar o trabalho. Tudo o que era nesário para o próximo agente executar sem re-pesquisar está aqui, com endereços exatos.

---

## 1. Estado fino do projeto (verificado, não estimado)

| Superfície | Estado |
|------------|--------|
| **Superproject** `/home/marlonsc/flext`, branch `0.12.0-dev` | tip local `516d9adc80` (pushed `4dea5c3712..516d9adc80`) |
| **flext-infra** (submódulo) | HEAD `bff592284` — encadeado: meus `3000b6bc0` (cleanup APPLY 9 arq.) + `bff592284` (Law 13, **dono a verificar**, A0.1) |
| **Base do meu pous** | `573eb3746` (wip `7a5e2e1e8` excisado via reset+cherry-pick→`dd65db77c`) |
| **Worktrees de flext-infra** | `flext-infra/worktrees/promoted-framework-lift` (de outra lane — NÃO tocar) |
| **~30 submódulos dirty** | `m` prefix (working-dirty) vs `[+SHA]` (gitlink divergente) — A0.2 triagem obrigatória ANTES de commit umbrella |
| **Suíte de testes** | flext-infra: verde PARCIAL (27 pontuais em 6 arquivos); 9 reds ci_matrix (fixed-point pyproject.toml) + 3 timeouts make_environment + 1 ast-grep timeout (mod_circuit) + 1 git-identity (docs generator) |
| **`make gen APPLY=Y`** | VERDE ×2 no escopo flext-infra repo; **PUSH ÉVitar** até fixed-point do pyproject (classe `flext-3cabz`) fechado |
| **crg graph** | `Built at commit 79dcca088` — STALE 2+ dias vs tip; rodar `code-review-graph update` antes de qualquer citação |
| **Capsule-budget de ~/agents** | capsuula 9.477/9.488 (folga ~11 chars) — NÃO criar artifacts novos sem ADR; tudo novo vai in-place no corpo |

---

## 2. Beads (the truth) — status real no bd

| Bead | P | Status | O que falta |
|------|---|--------|-------------|
| `flext-vo335` (P1) | Hotfix D1-D2 + violações V1/V2/V3 | ABERTA | ordena A0.3: branch hotfix → PR → --no-ff → gates no SHA integrado |
| `flext-3cabz` (P2) | Classe idempotência pyproject.toml | ABERTA (atualizada 12:14Z com H1/H2/H3 + método difflib→/tmp/fixed-point) | root cause + fix + teste de convergência |
| `flext-2h0un` (P2) | Instância da 3cabz | ABERTA (linkada) | evidence-only |
| `flext-9wwed` (P2) | Budget law + B2 PATH-strip | ABERTA (absorveu p8sjy) | B2 reproduzir PATH-strip com Makefile de fixture; B1 fixture ≤10s |
| `flext-gxgqp` (P2) | Gate CI de backup-regrowth + keep_backup | ABERTA | impl |
| `flext-p8sjy` | Duplicata de 9wwed | CLOSED superseded | — |
| `flext-uw305` | requires_apply template | CLOSED (4 evidências) | — |
| `flext-f73ii` (P3) | worktrees órfãs de conform | ABERTA | lock órfão de journal pertence aqui |
| `flext-cpkk` (P0) | make check raiz CI block | ABERTA | desbloqueia pós-ator |
| `flext-y3qpq.2/3/5` | R1 toolchain / R2 gates / R4 RC | ABERTOS | ordem R1→R5 rege |

Regen: `env -u BEADS_DOLT_SERVER_DATABASE bd list --status=open --json`

---

## 3. Onde está o conhecimento

| Artefato | Caminho | Uso |
|----------|---------|-----|
| **Plano vivente** | `docs/plans/2026-09-11-flext-conformance-sweep.md` | §0 refs canônicas; §1 autocrítica 8 desvios; §3 SLAs de produção (SLA-1..5); §4 linhas de ação A0-A5; §5 riscos+gatilhos; §10 pesquisa crg/mód/rules; §11 ciclo de automação + piloto; §12 pedido de aprovação; §9 delta sweep-2 (colisão com lane oposta) |
| Planos correlatos | `docs/plans/2026-09-09-fleet-consolidation-closure-plan.md`, `2026-09-10-cooldown-extermination-plan.md` | contexto |
| ADRs workspace | `docs/architecture/adr/` (ADR-001..010) | decisões de arquitetura |
| ADRs ~/agents | `~/agents/docs/adr/ADR-0012/0013` | crg-autopilot, fork versions |
| Regra nova (RASCUNHO apt) | `~/agents/rules/workflow/landing-and-sweep-law.md` | leis: descarte histórico inventário prévio; push FF = viol; idempotência SLA; red no turn |
| Comando (RASCUNHO apt) | `~/agents/commands/implementation/conformance-sweep.md` | ciclo completo A0→A5 |
| Skills atualizadas in-place (CORPO, legal silo-budget) | `~/agents/skills/framework/flext-development` (landing delta), `tool/beads` (mutation coupling), `project-wide/shell/make-check` (pré-push guard ×2 + graph loop), `agent-wide/verification/verification-loop` (investigation protocol), `project-wide/coordination/fleet-lane-discipline` (graph freshness law) | seções novas no fim de cada SKILL.md — guardando conteúdo pendente ADR capsule |
| Rules ast-grep SSOT | `flext-infra/src/flext_infra/codemod/rules/` (139) + `~/agents/ast-grep-rules/universal/` | toda regra nova com snapshot-test em `ast-grep-rule-tests/` |
| crg capa CLI | `code-review-graph {status,update,impact,query,detect-changes,refactor,flows,dead-code,large-functions,update,doctor,daemon}` | automação de evidência |
| bd remember (fila) | `fleet-stabilization-2026-09-08`, `lane-worktree-and-living-plan-law`, `operator-correction-learning` | lições absorvidas |

---

## 4. Como as conclusões foram obtidas (método, para reproduzir/validar)

1. **Toda afirmação = comando + cwd + saída decisiva** (lei 117). Evidência por file-log (diff/difflib nunca stdout-códigos — codegen inunda).
2. Bead ANTES de mutação; red → bead no MESMO cursor; fechamento = 4 evidências.
3. Push FF na integração = **VIOL establecido**, reparo em A0.3 PR --no-ff pós-verde.
4. Colisões entre lanes resolvidas por fix-forward + unificação de beads (3cabz classe / 2h0un instância / p8sjy→9wwed supersede).
5. Todo-alviously-sempre reconstruído de: `bd list --status=open` + plan-index + skills body (nunca de memória narrativa).

---

## 5. Como remontar os TODOs (protocolo)

```bash
cd /home/marlonsc/flext
env -u BEADS_DOLT_SERVER_DATABASE bd list --status=open --json | jq -r '.[] | "\(.priority)\t\(.id)\t\(.title)"' | sort -n
# 1. mapear cada bead → item do todo (flext-3cabz→A1, 9wwed→B1/B2, gxgqp→gate backup, cpkk→A3-locking-actor, f73ii→lock, vo335→A0.3)
# 2. completar com o plan-index: docs/plans/2026-09-11-flext-conformance-sweep.md §4 (A0-A5) + §11 (piloto A6)
# 3. marcar in_progress o piloto (crg update + trapézio 11.1 nas 9 reds ci_matrix + make_environment B1/B2)
# 4. adição: capsule-budget resolução pendente ver §9.2 + seção 12 do plano
```

Estado alvo: **todo ↔ plano ↔ beads com MESMAS refs e status**; atualiza o todo a cada transição, turno a turno.

---

## 6. Ordem de retomada (primeiras 4 ações, em sequência)

1. **crg update** e citação do built-at commit (todos os cliques subsequercitéticos de impact/query partem daí — §10 fatos)
2. **Piloto A6 (§11.1 ciclo)** nas 2 unidades: ci_matrix red + make_environment B1/B2 fixture — ONE re-reg no snapshot-test; gate de aceite: ci_matrix 28/28 verde
3. **A0.1+A0.2 paralelos** (proveniência bff592284 + triagem submódulos)
4. **A0.3 fret**: hotfix branch → PR → --no-ff → gates no SHA merged → fechar flext-vo335

---

## 7. Proibições duráveis desta sessão (lidas no pós-mortem)

- Não push FF na integração em nenhuma superfície sob pressão (leitura registrada)
- Não criar bead "pré-existente" sem red uncaptured: red observada = bead no MESMO turn
- Não citar grafo crg sem registrar seu Built at commit
- Não `git add -A` em nenhum submodule/superprojeto
- Não `rm -f` de lock de journal — bead `flext-f73ii` + kill do owner
- Não invadir lantas ativas (`promoted-framework-lift`, `z82dg-nsloc`); absorver pós-merge
- Não criar arquivos novos sob `~/agents/rules|commands|skills` sem ADR de capsule-budget; corpos in-place são livres

---

## 8. Numeros-chave (quick resume)

| KPI | Valor |
|-----|-------|
| anos da sessão: commits superproject | 9 (4159c877b4 → 516d9adc80) |
| commits flext-infra | 3 (dd65db77c, bff592284, 3000b6bc0) |
| reds fixed-point testes ci_matrix | 9/28 — classe flext-3cabz |
| Timeout testes make_environment | 3 ×60s — flext-9wwed |
| verts strategy: VERDE hoje | flext-infra: gen ×2, workspace+docs-auditor+conform+make-env gate=27 testes pontuais |
| crg | 33.744 nodes/230k edges, build 79dcca088 (stale) |

---

*Fim do handoff. Próximo agente: comece da seção 6, item 1.*

---

## 9. Reconciliação skills/ADRs/docs ↔ código (12:52 UTC — confronto pós-handoff v1)

Método: leitura dos donos canônicos (deep-research router procedure, flext-development SKILL, ADR-010, rule `production-readiness`) confrontada contra o código real e o estado medido da sessão. O router-procedure de web-research (firecrawl/exa) não apply ab — tarefa de reconciliação local; propagationpreserved: nada foi normalizado.

### 9.1 Tabela de mapeamento: contrato ADR-010 ↔ SLA do plano ↔ estado medido

| ADR-010 §Verification contract | SLA no plano §3 | Estado medido no tip `bff592284` | Conclusão |
|---|---|---|---|
| (1) `make gen` ×2 byte-idempotente | SLA-1 Idempotência | **RED** — 9 ci_matrix + classe `flext-3cabz` (prova 1ª passada de `FlextInfraCodegenProjectNew` falha em tmpdir) | **BLOQUEIA o piloto de produção** |
| (2) Standardization audit zero-drift | SLA-2 Gate CI | RED (`flext-cpkk` P0; base vermelha = entrega vermelha pela rule `production-readiness`) | bloqueia |
| (3) `make mod` zero actionable/detection-only + **rota CRG sancionada** | automação §10-11 (ciclo crg+mod+gen) | mod viável (139 regras SSOT); CRG com grafo STALE @79dcca088 | piloto usa a rota já sancionada pelo ADR — não é invenção desta sessão |
| (4) testmon canônico / budget (10s) | SLA-3 Budget | VULNERADO (3×60s+, `flext-9wwed`) | bloqueia |
| (5) fence de consumers/projetos independentes | — | out-of-scope indie | — |

### 9.2 Drifts de DOCUMENTAÇÃO corrigidos nesta reconciliação
| # | Drift | Correção aplicada |
|---|-------|-------------------|
| DR1 | Skill `flext-development` "Landing law delta" afirmava o guard gen-×2 como lei desta sessão | **corrigido in-place**: ADR-010 §Verification contract (item 1) é o DONO; skill restata para o caso pressão, não re-inventa |
| DR2 | Plano §10 apresentava o loop crg como invenção | esclarecido: **ADR-010 item 3 já sanciona a rota ai-hub CRG/LSP** como evidência sem pré-requisito de host — o ciclo §11 é ADR-conformant |
| DR3 | Framing "pré-existente fora de escopo" (meu delta verde) usado para Reds estruturais | rule `production-readiness` proíbe: defeito no blast radius é adotado ("combined state is the deliverable") — Reds do ator só são ACEITÁVEIS como beads abertas com promoção bloqueada, nunca como "fora do meu mirante" |

### 9.3 Regras que precisam ser CODIFICADAS para o piloto de produção com propagação completa (cadeia de fechamento)

Ordem ADR-010-conforme (cada gate fecha até o próximo abrir):
1. **Fechar SLA-1** (`flext-3cabz`): idempotência pyproject.toml → item 1 do ADR-010 verificável.
2. **Fechar SLA-3** (`flext-9wwed`): budget fixture + PATH-strip → item 4 verificável.
3. **Fechar SLA-2** (`flext-cpkk`, absorvendo XML do ator `z82dg-nsloc` fix-forward): item 2 audit-zero-drift + item 3 mod-zero-findings.
4. **Landing canônico**: hotfix/conformance-sweep-d1d2 → PR → `--no-ff` → gates no SHA integrado (fecha `flext-vo335` V1-V3).
5. **Piloto homologação** = estado onde os itens 1-4 do ADR-010 estão verdes no SHA integrado + `flext-gxgqp` (gate de regrowth) implementado — só aí a branch de integração está "produtiva para homologação".

### 9.4 Inputs atualizados nesta passada
- Handoff v2 = este arquivo (seção 9 nova).
- Skill `flext-development`: drift DR1 corrigido (ADR-010 como owner).
- Plan: §10/§11 leem-se com a nota DR2 (rota CRG = ADR-010-sancionada).
- Beads: `flext-3cabz` recebeu o mapeamento ADR-010↔SLA↔piloto como aceite.

*Fim da reconciliação. Próximo agente: seção 6 do handoff v1 continua válida como ordem de retomada; a cadeia 9.3 substitui qualquer leitura de Reds como "fora de alcance".*

---

## 10. FUSÃO — handoff flext-gov (sessão irmão) × este handoff (13:05 UTC)

Fonte fundida: `~/flext-work/flext-gov-super/docs/plans/2026-09-11-flext-gov-handoff.md` (SKA a853d3e599) — programa de consumo/GOV (`epic flext-ssnc7`, ADR-015, consumption-law.md, GOVERNANCE.md). Nada do outro arquivo foi reescrito; a fusão vive AQUI como mapa único, e o decreto §13 deles (§10.4) governa as duas sessões.

### 10.1 Duas cadeias de gate, uma sequência (sinergia central)

| Fase | Cadeia flext-gov (ssnc7) | Cadeia conformance sweep (este doc) | Acoplamento |
|------|--------------------------|--------------------------------------|-------------|
| Pre-code | Decree §13: revalidar TODO↔bd + merge-base --is-ancestor + fetch antes de ANY efeito | §5 remontagem TODO ↔ bd ↔ plan-index (mesmo método) | idêntica mecânica — revalidar AMBOS os TODOs |
| Landing | **A1 approval**: pousar as 3 lanes (`feat/consumer-import-grammar` @14c63121d core, `feat/consumer-gates` @c8a429d59 infra, `feat/flext-gov-consumption-law` @a853d3e599 super) com `--no-ff` → 0.12.0-dev | **A0.3**: PR `--no-ff` do hotfix sweep | **uma única fila de pousos** — A1 do gov ANTES do A0.3 do sweep evita re-push |
| Grafo | **A2 approval**: crg build + daemon NOS TIPS INTEGRADOS (graphs ausentes nas lanes; doctor crítico) | §10 §6.1: `crg update` @built-at commit | A2 fecha a lacuna de grafo das duas sessões no MESMO ciclo |
| Piloto | **A3 approval**: piloto RED→GREEN real consumer (ai-hub) + warn→hard | Piloto A6 §11.2 (ci_matrix 9 reds + make_environment B1/B2) | um só plano de homologação: RED→GREEN ambas as classes |
| Fechamento | F5 (tags/AI_HUB_CONSUMER) abre só pós F1+F4 pousados + gates verdes | Cadeia 9.3: SLA-1→SLA-3→SLA-2→landing→piloto | mesma ordem lógica de dependência |

### 10.2 Estado de acumulação entre as sessões (o que uma deixou para a outra)

1. **Meus pushes moveram `origin/0.12.0-dev`** (`396b359a1e..9526645ea9`) — o §12 do handoff-gov exige `git fetch` + `merge-base --is-ancestor` nas 3 lanes ANTES do `--no-ff` (absorção obrigatória, hunk-a-hunk). As 3 lanes NÃO pousadas podem estar atrás do meu tip.
2. **Pino comum**: core lane `uv.lock` = `flext-infra rev=0.12.0-dev#bff592284` — MESMO tip que esta sessão modificou com `3000b6bc0`/`bff592284`; o `bd show ssnc7.1` (F1 detector) deve absorver meu cleanup + o gate ci_matrix pós-fix.
3. **Resíduo operativos da lane infra-gov**: generated surfaces do `make gen` NÃO commitadas (`M Makefile M README M docs/api-reference M pyproject.toml`) — receita: abrir lane, `make check`, commitar escopado ANTES do pouso; nunca lane nova. Alinha com meu A0.2 (triagem dirty).
4. **Beads** (SSOT dupla): `bd list | grep -E 'ssnc7|3cabz|9wwed|vo335|gxgqp|cpkk'` — TODOs dos dois planos convergem no bd; §13 do gov + §5 deste handoff remontam a partir do MESMO fonte.
5. **ENFORCE**: 099 única linha viva; 100/101 pendentes — não "deliverar"; meu SLA-3 (budget) é complementar ao ENFORCE-101 (R4) de F4 — mesmo domínio, beads distintos: cross-referenciar, não duplicar.
6. **Autoridade**: ADR-015 + consumption-law.md + meu ADR-010 §verification contract (reconciliação §9) formam o tripé — nenhum vencendo o outro; divergência = bead, nunca narrativa.
7. **agentsctl sync é delivery, não dono** — vale para os dois lados; arquivo canônico > réplica.

### 10.3 Cadeia única de retomada (merge das duas ordens)

1. Ler AMBOS os handoffs (§1-§9 aqui; §1-§13 lá) → revalidar TODO↔bd×2 (decree §13).
2. Pedir **A1** ao operador → pousar 3 lanes gov com `--no-ff` (absorvendo meu tip 9526645ea9) + A0.3 do sweep em um PR por lane.
3. Pedir **A2** → `crg update/build` nos tips integrados (fecha a lacuna de grafo das duas sessões).
4. Executar **piloto A6 §11 + A3 §7-gov**: RED→GREEN ci_matrix/9wwed (esta cadeia) + RED→GREEN consumer (gov).
5. Fechamento: beads das DUAS sessões fecham com 4 evidências cada; registro `bd remember` por transição de aprovação (protocolo END OF TURN do §13).

### 10.4 Decreto de continuidade (vigência dupla — aplica-se a ambas as sessões)
- Nunca mover texto de plano past reality; corrigir bead/status, não a narrativa.
- bd é SSOT de execução; SKAs/git são evidência; narrativa nunca é.
- Cada aprovação A1..A3 confirmação EXPLÍCITA do operador (nunca inferida).
- Ao reiniciar: ler handoff → §decree → pedir aprovação → só então tocar código.
