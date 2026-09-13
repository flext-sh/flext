# Handoff — FLEXT Conformance Sweep (sessão 2026-09-11) — PROMPT DE RETOMADA

> Cole este arquivo como 1ª mensagem de uma sessão nova (com `00-index.md` do diretório).
> Execute o preflight §5 ANTES de qualquer mutação.

## 1. Papel e objetivo
Você retoma o **monopólio de limpeza/conformidade do workspace FLEXT hospedado**
(`/home/marlonsc/flext`, sub-frota `flext-*`), sob `AGENTS.md` raiz + skill
`flext-law`. Objetivo aberto: **D1–D6 do §3 do plano vivente** — ponto fixo de
geração por membro, gate de regrowth em CI, budget de teste, reds estruturais
(dono: ator), release v0.13.0, ativação. Pousos HOJE podem ser admin (autorizados),
mas **sempre** PR `--no-ff` → gates no SHA → prova de runtime.

## 2. Estado medido ao fechar a sessão (2026-09-11 ~15:00Z)
| Superfície | Estado |
|---|---|
| flext `origin/0.12.0-dev` | `396b359a1e` (zero-variable APPLY regenerado) |
| flext-infra `origin/0.12.0-dev` | `bff592284` (Law 13 — CI steps com APPLY=Y) |
| flext checkout local | `037a5cb561` (2° commits docs/plans `135de0efae`..: pendente de pousar via PR — **§12(d)**) |
| Resíduo físico | `.bak` raiz = **0**; `persist_apply_backup` = **0** (grep no tip) |
| Worktrees minhas | **NENHUMA** (todas retiradas com ancestry-proof) — abrir `hotfix/conformance-sweep-p` para Onda-P |
| Worktrees do ator | `flext-infra-worktrees/z82dg-nsloc` (reforma estrutural, viva), `flext-work/*` (gov/cooldown/mdignore/ci-frozen), `flext-b3xmn` — **não invadir, não pushar sobre dirty alheio** |
| CRG | watch-daemon multirepo ativo; **grafos podem estar `Built at 79dcca088` (2+ dias)** → `code-review-graph update` OBRIGATÓRIO antes de impact/query |

## 3. Beads — verdade ao fechar (re-verificar §4/§5 do plano)
- `flext-vo335` **OPEN P1** → próximo passo 1: pouso do hotfix D1-D2 (reparar violações V1-V3 de pouso; PR pós-verde).
- `flext-5k9r7` **IN_PROGRESS** (dono executando — não duplicar).
- `flext-2h0un` OPEN P1 (instância) sob classe `flext-3cabz` OPEN P2 (root-cause único) — fixed-point drift `conform.py` apply/verify.
- `flext-9wwed` OPEN P1 (budget; dep `flext-38p39`; absorveu `p8sjy` CLOSED→9wwed).
- `flext-gxgqp` OPEN P2 (gate regrowth + keep_backup opt-in).
- `flext-tldqe`, `flext-uw305` **CLOSED** (4 evidências) — intocáveis.
- Epics do ator `flext-1wjg1`/`flext-y3qpq.3` (+`flext-cpkk` **P0 dono do gate raiz**) — absolver pós-pouso, não re-solver.

## 4. Contexto que precisa sobreviver (lições já codificadas — verifique, não re-derivo)
1. **Tracker**: `env -u BEADS_DOLT_SERVER_DATABASE` para TODO comando `bd` neste tema (poluição de sessão causou horas de falso-bloqueio).
2. **Provas por gerador**, nunca por find/grep literal (A7): gen ×2 byte-idêntico; grafo CRG fresco; `make mod APPLY=Y` é o único mutador; `make gen APPLY=Y` estampa.
3. **Fechamento de bead** cita o escopo exato verde NO momento; pipeline parcial nunca citado como verde — resto vira bead nova.
4. **Regra nova** vaía ao SSOT do dono com snapshot-test (precedente `ban-ai-hub-crg-library-boundary.yml`).
5. **Cápsula `~/agents` 9.477/9.488** — nenhum arquivo/índice novo sem ADR; absorção é in-place no corpo de skill existente (feita: `fleet-lane-discipline`).
6. **Pedidão ao operador sem resposta (§12)**: (a) Onda-P, (b) CRG padrão, (d) política de planos vivos na integração.

## 5. Preflight da nova sessão (executar, registrar saída)
```bash
cd /home/marlonsc/flext && git fetch origin 0.12.0-dev
git rev-parse origin/0.12.0-dev                                    # comparar com §2
find . -name "*.bak" -not -path "*-worktrees/*" -not -path "*/.venv/*" -not -path "*/.git/*" -not -path "*/dist/*" | wc -l   # == 0
env -u BEADS_DOLT_SERVER_DATABASE bd list --status=open            # reconciliar §4 vs §5 do plano
grep -rn "persist_apply_backup" flext-infra/src/ | wc -l           # == 0
```
Divergência → investigar proveniência, consertar no dono, conservar trabalho dirty.

## 6. Primeira ação (se §12(a) confirmado; caso contrário: #1 do §4)
Abrir worktree dedicado `hotfix/conformance-sweep-p` de `origin/0.12.0-dev` e
declarar: objetivo = `flext-vo335` primeiro; gates = §11.3; stop = gates verdes
no SHA integrado + bead fechada com 4 evidências + plano §4 atualizado
(a cada material-step — plano vivente é lei).
