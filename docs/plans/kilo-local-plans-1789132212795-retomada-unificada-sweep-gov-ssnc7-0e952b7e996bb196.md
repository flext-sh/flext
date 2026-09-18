# Plano Unificado de Retomada — Épico bd → Absorção Total → Remote-ização → Execução (sweep × `flext-ssnc7` × ai-hub × agents)

> **Decretos do operador (vigentes)**: · 13:21Z — F0 assume como MEU absolutamente tudo
> de ai-hub e agents (beads, TODOs, insumos md, workspaces, worktrees, PRs, branches
> locais/remotas, bloqueios) com atualização completa; F1 grava workspaces/worktrees do
> projeto + subprojetos em branches remotas + PRs e REMOVE do host; rigs agents/ai-hub
> ficam na posição da integração remota; cria worktree dedicada; fases seguintes
> executam a cadeia. · 13:26Z — Resultado da F0 = este plano codificado como **ÉPICO no
> bd**, com **uma bead por fase** ligada ao épico, todas com **todos os critérios que
> `bd lint` exige**; e na própria F0, **correlacionar TODAS as beads abertas absorvidas
> por este plano — inclusive deferred, claimed (in_progress) e blocked** — com caminho
> de desbloqueio registrado; **autonomia total** para levar o plano até o fim sem nenhum
> bloqueio ou desculpa. · 13:29Z — (i) o plano ADMITE que o **bd está sempre funcional
> por linha de comando**: falha do bd = defeito reparado NO DONO no mesmo turno, nunca
> bloqueio ou desculpa; (ii) o **gas-city NÃO pode ser reativado** — coordenação
> exclusivamente via bd + git + PRs. · 13:54Z — **Nenhuma fase termina sem**: propagação
> CONCLUÍDA para as branches de integração dos projetos/subprojetos do seu blast radius
> (do épico: TODOS), tudo **100% green e aplicado em runtime real sem falhas ou
> warning**, e **beads completamente fechadas**. · 13:56Z — Além disso, nenhuma fase
> termina sem **toda a documentação atualizada** e **toda a parte projetada regerada**
> pelo gerador dono (`make gen`, ×2 idempotente — projeções nunca hand-editadas). Itens
> incorporados à barra §3.0 (agora 5 itens). · Autonomia 13:26Z **converte os gates
> A1/A2/A3 em gates de REGISTRO** (decisão + evidência na bead da fase antes de
> avançar). Só decisão NOVA, destrutiva e fora do escopo reabre pergunta ao operador.
> Pergunta sobre `~/flext` dispensada — decisão registrada em F1.1. · 14:45Z —
> **REESCOPO: o trabalho hands-on se resume a FLEXT.** F0.4-F0.6 (gravar/pousar
> ai-hub+agents, fix regra 17 na fonte ai-hub) NÃO executam nesta sessão — permanecem
> como ROTAS registradas na correlação para os atores donos; edit feito em
> `ai-hub/UNIVERSAL_CORE.md` foi revertido (tree limpa). F0 fecha com o entregável flext
> (estrutura bd + correlação total ×3 trackers).

## 0. Autoridade e fontes

1. Decretos acima > `AGENTS.md` raiz do checkout ativo → `flext-law` branch-matched →
   bead ativa.
2. Handoff sweep: `docs/plans/2026-09-11-conformance-sweep-handoff.md` (+
   `00-index.md`/`handoff.md`/`audit-2026-09-11.md`).
3. Handoff gov:
   `~/flext-work/flext-gov-super/docs/plans/2026-09-11-flext-gov-handoff.md` + plano
   `2026-09-11-flext-gov-program.md`.
4. Plano vivente sweep: `docs/plans/2026-09-11-flext-conformance-sweep.md` (D1-D6, TODO
   v3, F1-F8, Onda-P).
5. Tripé: ADR-015 + consumption-law ∥ ADR-010 §Verification contract. Decretos §13 (gov)
   e §10.4 (sweep) vigoram no que não for substituído.
6. **Premissas de execução (13:29Z)**: (a) bd CLI sempre funcional — toda operação de
   tracker via `bd` com `env -u BEADS_DOLT_SERVER_DATABASE` (nunca herdar DB de sessão);
   (b) gas-city PERMANECE DESATIVADO — nenhum `gc-*`/reativação; coordenação de frota =
   bd (remember/notes/deps) + git + PRs.

## 1. Estado medido (fatos verificados nesta sessão de planejamento)

| #   | Fato                                                                                                                                                                                                                                                                                         | Evidência                                                                                   | Consequência                                                                                                                                       |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| N1  | **P0**: umbrella pin → `flext-infra@3000b6bc0`, mas infra origin = `bff592284` (commit nunca pushado)                                                                                                                                                                                        | `git ls-tree HEAD flext-infra` + `git ls-remote origin 0.12.0-dev` (em `flext/flext-infra`) | PR do `3000b6bc0` abre a fila de pousos (F2)                                                                                                       |
| N2  | infra local `0.12.0-dev` = `3000b6bc0`, 1 à frente do origin                                                                                                                                                                                                                                 | `git log`/`rev-parse` em `flext/flext-infra`                                                | Push FF proibido; pouso via PR `--no-ff`                                                                                                           |
| N3  | infra checkout sujo: `config/codegen.yaml` (1443+/1438- churn integral), `qualified_names.py` (6), `test_main.py` (1)                                                                                                                                                                        | `git diff --stat` em `flext/flext-infra`                                                    | Branch/PR de absorção na F1; proveniência no PR                                                                                                    |
| N4  | core checkout sujo: 9 arquivos CI/Makefile/conftest/typings/Dockerfiles (21+/14-)                                                                                                                                                                                                            | `git diff --stat` em `flext/flext-core`                                                     | Idem F1 (churn concorrente assumido)                                                                                                               |
| N5  | umbrella `uv.lock` modificado (49+/50-) + ~31 submódulos "modified content"                                                                                                                                                                                                                  | `git status` umbrella                                                                       | Gravação em PR na F1; nada commitado por cima                                                                                                      |
| N6  | umbrella local == origin == `503ea36d56`                                                                                                                                                                                                                                                     | `git rev-parse origin/0.12.0-dev`                                                           | Re-fetch obrigatório no F0                                                                                                                         |
| N7  | Nesta sessão de planejamento o `bd` estava bloqueado pelo sandbox                                                                                                                                                                                                                            | tentativas `bd` aqui                                                                        | Premissa 13:29Z: bd CLI funcional na execução; F0 abre com censo `bd` completo; falha do bd em execução = reparo no dono no turno (nunca desculpa) |
| N8  | Regra 17 ainda diz "with for mutation" (`AGENTS.md:109-113`) dentro do bloco **AI-HUB MANAGED UNIVERSAL CORE**                                                                                                                                                                               | leitura do arquivo                                                                          | Dono real = fonte gerida no repo **ai-hub**; fix na fonte + re-projeção, nunca hand-edit no umbrella                                               |
| N9  | `~/flext-work/`: 8+ worktrees de programa (`flext-core-gov`, `flext-infra-gov`, `flext-gov-super`, `flext-tests`, `flext-infra-cooldown-extermination`, `flext-infra-mdignore`, `retire-logs`, `reval-fp-probe`) + worktrees de ator nos subrepos (`z82dg-nsloc`, `promoted-framework-lift`) | `ls ~/flext-work/` + handoffs                                                               | Inventário de gravação→remoção da F1                                                                                                               |

## 2. Estrutura de execução no bd (entregável da F0)

### 2.1 Épico + bead por fase

| Bead (filha do épico) | Título                                                                                                      | Escopo (uma linha)                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| épico                 | `Retomada Unificada 2026-09-11 — absorção total → remote-ização → piloto (sweep × ssnc7 × ai-hub × agents)` | superset de `flext-ssnc7`; fecha só com filhos + correlacionadas fechadas + propagação universal provada |
| F0                    | Absorção total ai-hub+agents + estrutura épico/beads + correlação total                                     | censo, posse, pousos ai-hub/agents, épico+beads lint-clean, correlação universal                         |
| F1                    | Remote-ização das worktrees + limpeza do host + rigs alinhados + worktrees dedicadas                        | grava→PR→remove; rigs == origin; `~/flext-work/sweep-p/` criada                                          |
| F2                    | Pre-code + fila única de pousos (registro A1)                                                               | detector v3, pino, projeção regra 17 + 7 pousos `--no-ff` com gates rerun no SHA                         |
| F3                    | Grafo crg nos tips integrados (registro A2)                                                                 | build + doctor verde + lei de built-at                                                                   |
| F4                    | Piloto unificado de homologação (registro A3 + §12a)                                                        | ondas 1-7 da tabela §3.5, incluindo landing do sweep                                                     |
| F5                    | Fechamento total — propagação universal + épico                                                             | F5 gov (tags/AI_HUB_CONSUMER), varredura de propagação em TODOS os projetos/subprojetos, épico fechado   |

### 2.2 Template de criação — nada menos do que `bd lint` exige

```bash
env -u BEADS_DOLT_SERVER_DATABASE bd create "<título>" -t epic | feature | task | bug -p \
  "<contexto + escopo + fontes (caminhos/SHAs) + proibições aplicáveis>" \
  --design "<abordagem: passos das seções F* deste plano + leis de pouso/evidência + barra §3.0>" \
  --acceptance "<critérios medíveis: propagação (merge-base por repo), gates 100% green zero warning no SHA integrado, runtime real, beads fechadas, bd lint zero>" \
  --parent < 0-2 > --description < id-do-epico > \
  --validate                              # cria só com descrição completa
env -u BEADS_DOLT_SERVER_DATABASE bd lint # ZERO issues antes de sair da F0
```

- Dependências: cada fase `blocked-by` a anterior (exceto F0); bloqueios legítimos de
  execution-time (ex.: PR travado por proteção de branch com revisor humano externo)
  recebem `blocked-by` + caminho de desbloqueio + escalation NO TURNO — nunca stall
  silencioso.
- **bd é primitiva garantida (13:29Z)**: falha de qualquer comando `bd` = defeito do
  dono (dolt/serviço/DB local) reparado NO MESMO turno e operação reemitida — nunca
  contorno, nunca TODO paralela, nunca desculpa de fase.
- Closure de cada fase = barra §3.0 COMPLETA (5 itens).

### 2.3 Correlação total das beads absorvidas (regra anti-bloqueio)

1. Censo universal em cada tracker (flext, ai-hub, agents): `bd list --json` filtrando
   **open, in_progress (claimed), deferred e blocked-by** — nada fica fora por status.
2. Para CADA bead absorvida: link `related`/`parent-child` à bead da fase que a
   executa + rota: `absorvida-em:F<n>`, `superseded-by:<fase>` (com evidência) ou
   `unblock:<ação concreta>`.
3. Beads deferred/blocked SEM rota = violação de F0: recebem rota ou são
   superseded/closed com evidência no mesmo turno. Meta: **zero beads órfãs, zero
   bloqueios sem dono** no fim da F0.
4. Candidatas conhecidas (revalidar no censo): sweep
   `vo335/3cabz/2h0un/9wwed/gxgqp/cpkk/f73ii` + `5k9r7` (claimed) + família do ator
   `1wjg1/y3qpq.*/uuhc4/38p39/2wjm/ywet` (absorção pós-pouso) · gov `ssnc7` +
   `.1-.8`/`.1.1`/`.2.1` · ai-hub WS-H1..H5 e agents WS-A..D conforme censo.

### 2.4 Gates de registro (ex-A1/A2/A3)

Antes de F2/F3/F4 iniciarem:
`bd update <bead-da-fase> --notes "gate A<n>: decisão registrada, evidência <refs>"`.
Avançar é autorizado pelo decreto de autonomia; pausa só para conflito de autoridade
novo ou ação destrutiva fora do escopo.

## 3. Fases

### 3.0 Barra de fechamento comum — UMA fase só termina (bead CLOSED) com os 5 itens, no blast radius dela

1. **Propagação concluída**: para cada projeto/subprojeto tocado — SHA pousado `--no-ff`
   na integração + `git fetch` +
   `git merge-base --is-ancestor <SHA> origin/<integração>` = exit 0 POR REPO; gitlinks
   do umbrella re-rollados aos tips de integração (quando submódulo mudou); pins
   `uv.lock` consistentes; TODOs/planos vivos espelhados.
2. **100% green, zero warning, no SHA INTEGRADO** (nunca local-green): `make gen` ×2
   byte-idêntico + `make check` + `make test` = exit 0 com **zero falha, zero warning,
   zero skip silencioso, saída decisiva** (lei: warning/saída vazia/tool ausente = RED;
   nunca normalizado nem suprimido; teste que quebra com config legítima = defeito do
   teste).
3. **Runtime real provado**: efeito aplicado e OBSERVADO no runtime canônico do
   workspace real (não sandbox): regen real ×2, gates no ambiente vivo, consumo real
   onde aplicável (runtime precede estático; config editada só está "ativa" com prova de
   sessão independente).
4. **Documentação atualizada + projetada regerada**: (a) TODA doc afetada pelo blast
   radius atualizada no MESMO ciclo — docs canônicas (`docs/`, guias, ADRs, README),
   planos vivos, TODOs, gates markdown — defasagem documental = defeito (bead), nunca
   work-around; (b) TODA superfície PROJETADA regerada pelo GERADOR dono (`make gen`) —
   blocos geridos (ex.: AI-HUB MANAGED UNIVERSAL CORE), api-reference, README, pyproject
   `[MANAGED]`, templates — com ×2 byte-idêntico provado; **hand-edit de projeção é
   proibido**: corrige-se a fonte + re-gera.
5. **Beads completamente fechadas**: bead da fase + TODAS as beads ativas do blast
   radius CLOSED com as 4 evidências (estado registrado, git history na integração,
   realidade medida, código integrado); descobertas novas viram bead COM ROTA para fase
   futura (nunca resíduo aberto sem dono); `bd lint` zero.

Sem os 5 itens a fase NÃO termina: bead permanece in_progress e o estado exato é
reportado — nada de "parcial verde" (finish-to-done; regra 22).

### 3.1 F0 — Absorção total + estrutura bd

1. **Estrutura primeiro**: criar épico + beads F0-F5 (§2.1-2.2); `bd lint` zero;
   correlação §2.3 completa.
2. **Censo completo ai-hub + agents** (+ flext):
   `git status/branch -a/worktree list/stash list/log -20` por repo, PRs abertos,
   branches locais vs remotas (ahead/behind), locks de journal + owners (kill do owner,
   nunca `rm -f`), TODOs/planos/insumos md, SKILLs em edição (~14 in-flight), rascunhos
   untracked (`landing-and-sweep-law.md`, `conformance-sweep.md`).
3. **Assumir posse**: `bd update --claim --notes` em TODAS as beads
   abertas/deferred/blocked dos três trackers; stale/superseded fechadas com evidência.
4. **Gravar trabalho em voo**: cada superfície dirty/untracked → branch remota escopada
   (`absorb/<fonte>-<tema>-2026-09-11`) + PR + proveniência no corpo. Rascunhos de
   `~/agents`: absorção IN-PLACE nos corpos de skills (cápsula 9.477/9.488 — zero
   arquivos novos) e então removidos.
5. **Pousar nas integrações de ai-hub/agents pela rota canônica de cada repo**
   (pré-requisito do alinhamento de rigs): ai-hub via PR → merge; agents pela sua rota.
   Proteção externa real (reviewer humano exigido pela plataforma) = único stop
   legítimo, pergunta exata no turno.
6. **Fix da regra 17 na FONTE ai-hub** (N8): contrato zero-variable (mutação-por-padrão;
   verificação read-only `codegen conform --mode check`/`make check`) +
   `make propagate` + `make check` (fecha débito §12e); re-projeção chega ao umbrella no
   pouso F2.2.
7. **Fechamento F0 (barra §3.0)**: propagação = ai-hub e agents com o trabalho absorvido
   NA integração remota; green = gates dos dois repos 100% zero warning no SHA
   integrado + propagate sem warning; runtime = rigs reais consumindo a nova posição;
   beads F0 + correlacionadas da fase fechadas (F1-F5 permanecem abertas por desenho —
   rotas registradas).
8. **Atualização completa**: TODOs, beads, planos vivos e insumos md dos três mundos
   refletindo posse e rotas — divergência bead×plano conserta o PLANO.

### 3.2 F1 — Remote-ização + limpeza do host + rigs + worktrees dedicadas

1. **Decisão registrada (autonomia; pergunta dispensada)**: `~/flext` permanece como
   **rig do flext** — estado sujo (N5 + N3/N4) gravado em branches/PRs, tree limpa,
   alinhado à origin; base das worktrees dedicadas. Removidos do host: worktrees de
   `~/flext-work/*` (N9) e worktrees de subrepos.
2. **Gravar antes de remover**: por worktree — dirty commitado por paths escopados na
   branch da worktree (ou branch de absorção), push, PR com proveniência + cross-ref na
   bead. Resíduo infra-gov (`M Makefile/README/api-reference/pyproject.toml` gerados):
   `make check` na lane ANTES de commitar output gerado (gov §12).
3. **Remoção física**: `git worktree remove` só com (a) tree clean, (b) push confirmado,
   (c) `git merge-base --is-ancestor <HEAD> origin/<branch>`. Branches permanecem (PRs
   as referenciam).
4. **Rigs agents/ai-hub == `origin/<integração>`**: após F0.5 — fetch + fast-forward
   local, tree limpa; registro e coordenação EXCLUSIVAMENTE via bd + git + PRs (gas-city
   desativado).
5. **Worktrees dedicadas**: raiz única `~/flext-work/sweep-p/` (umbrella p/ docs; infra
   p/ código; lanes quando o trabalho delas rodar), de `origin/0.12.0-dev`
   recém-fetchado; lista na bead F1. Nenhum trabalho fora delas daqui em diante.
6. **Fechamento F1 (barra §3.0)**: propagação = TODAS as branches de worktrees remotas
   com ancestry-proof + rigs fast-forwardados; green = lanes com resíduo commitado
   passam `make check` escopado zero warning; runtime = host físico verificado
   (`git worktree list` por repo mostra só rigs + dedicadas; rigs na posição da origin);
   beads F1 + locks (`flext-f73ii`) fechadas.

### 3.3 F2 — Pre-code + fila única de pousos (gate de registro A1)

Pre-code (worktrees dedicadas):

1. **Triage dos PRs de absorção** (N3/N4/N5): hunks classificados (meu / alheio-assumido
   / lixo de ambiente) na bead; lixo = bead de reparo no dono, nunca commit escondido.
2. **Detector v3** (`flext-ssnc7.1`): aliases `alias.asname or alias.name` + memo
   `_published_symbols` por `detect_file`; worktree da infra lane `feat/consumer-gates`;
   `make fix/fmt` + `make test` escopado; push atualiza o PR.
3. **Pino comum**: após pouso do `3000b6bc0`, re-resolver core lane `uv.lock` ao novo
   tip (guards `UV_PROJECT_ENVIRONMENT`/`VIRTUAL_ENV`); absorver cleanup zero-variável
   no detector.
4. **Projeção regra 17 no umbrella** (vinda do ai-hub, F0.6) como PR do umbrella.
5. **Registro A1** na bead F2 com a fila completa e estado de cada PR.

Fila única de pousos — ordem (gov antes de sweep evita re-push); cada item:
ancestry-proof → PR → merge `--no-ff` → **gates rerun no SHA merged**: 6. `flext-infra`:
PR `3000b6bc0` (N1/N2; parte de `flext-vo335`). 7. Umbrella: gitlink rollup + projeção
regra 17 + N5 resolvido. 8. Gov core lane (`14c63121d` + detector v3 + pino
re-resolvido) — absorver origin hunk-a-hunk antes. 9. Gov infra lane (`c8a429d59` + v3 +
resíduo da F1.2). 10. Gov super lane (`551e936c88`); depois `make check` de gates
markdown no super (`flext-ssnc7.3`). 11. PRs de absorção da F1 — merge conforme
classificação (WIP incompleto de reforma fica PR aberto + rota na bead, nunca
descartado). 12. **Slot do sweep**: `hotfix/conformance-sweep-p` pousa aqui SÓ se ondas
1-2 (F4) já verdes; caso o piloto ainda não tenha corrido, o slot fica reservado com
rota na bead e o fecho de `flext-vo335` migra para F4. CI RED pré-existente é absorvido
no pouso, nunca resolvido nele.

**Fechamento F2 (barra §3.0)**: propagação = cada repo pousado com `--is-ancestor`
provado + gitlinks/pins do umbrella re-rollados aos novos tips; green = gates rerun 100%
zero warning EM CADA SHA merged (violação V1 de `flext-vo335` não se repete) + gen ×2
real no umbrella; runtime = workspace real regenerado sobre os novos tips + detector
executando no ambiente vivo; beads das unidades pousadas fechadas (vo335 só se slot 12
executou; senão rota F4).

### 3.4 F3 — Grafo crg (gate de registro A2)

`code-review-graph build` nos tips INTEGRADOS (core+infra+umbrella) + daemon opcional;
`doctor` sai de critical. Lei de frescura: `update` no início de cada bloco com
`Built at <commit>` na bead — grafo velho é evidência de nada.

**Fechamento F3 (barra §3.0)**: propagação n/a (grafo é artefato de host, mas o built-at
deve ser dos SHAs já propagados em F2 — citar os 3 commits); green = `doctor` sem
critical + `status` limpo; runtime = grafos vivos no workspace real usados por
`impact/query` nesta sessão; beads F3 fechadas.

### 3.5 F4 — Piloto unificado (gates de registro A3 + §12a)

Lane `hotfix/conformance-sweep-p` de `origin/0.12.0-dev` recém-fetchada. Ciclo:
`crg update → impact → tests_for → make mod (escopado) → make fmt → make gen ×2 byte-idêntico (pré-push guard) → make check/test → commit escopado`.

| Ordem | Onda                          | Conteúdo                                                                                                                                                     | Bead(s)                     | Aceite                                                      |
| ----- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------- | ----------------------------------------------------------- |
| 1     | Wave-P1 (SLA-1)               | fixed-point pyproject (H1/H2/H3 em `codegen_file_plan.py`/`conform.py`); regra nova no SSOT `codemod/rules/` COM snapshot-test; prova por gen ×2, nunca grep | `flext-3cabz`+`flext-2h0un` | probe ×2 byte-idêntico; 9 ci_matrix verdes; gen ×2 umbrella |
| 2     | Wave-P2 (SLA-3)               | budget: B1 fixture ≤10s (provisionar 1×); B2 PATH-strip reproduzido com fixture (stub uv exit-99); orçamento força no teste, nunca no limite                 | `flext-9wwed`               | 0 timeout; ≤120s/membro                                     |
| 3     | SLA-2                         | gate raiz zero-drift + mod-zero-findings; absorver fix-forward do ator                                                                                       | `flext-cpkk`                | audit zero-drift no SHA integrado                           |
| 4     | Landing do sweep (slot F2.12) | PR `--no-ff` → gates rerun → fecha V1-V3                                                                                                                     | `flext-vo335`               | violações zeradas; 4 evidências                             |
| 5     | Gov consumer pilot (A3)       | ai-hub consumidor real: baseline `crg detect-changes` + gate R1 RED (`flext_core.lazy`, `flext_cli.models`) → fix forward → GREEN                            | `flext-ssnc7.1.1`/`.2.1`    | RED→GREEN provado; `AI_HUB_CONSUMER.md` base                |
| 6     | Wave-P3                       | gate de regrowth (fixture semeada FAILS) + `keep_backup` opt-in em config                                                                                    | `flext-gxgqp`               | gate falha em fixture; umbrella verde                       |
| 7     | warn→hard                     | só com RED→GREEN no 1º ciclo; senão warn mantido + report                                                                                                    | `flext-ssnc7.8`             | gates strict liberados p/ F5                                |

**Fechamento F4 (barra §3.0)**: propagação = cada onda pousada via PR `--no-ff` com
`--is-ancestor` + gitlinks re-rollados; green = gates rerun no SHA integrado por onda,
100% zero warning (ci_matrix 28/28, budget sem timeout, regrowth gate falhando em
fixture); runtime = piloto consumer REAL (ai-hub) com RED→GREEN observado em sessão
independente + warn→hard aplicado ao vivo; beads
`3cabz/2h0un/9wwed/vo335/cpkk/gxgqp/1.1/2.1/7.8` fechadas com 4 evidências.

### 3.6 F5 — Fechamento total: propagação universal + épico

1. **F5 do gov**: tags 0.12.x só em tips com gates verdes no SHA merged (nunca
   local-green); `AI_HUB_CONSUMER.md` GERADO (não hand-edit); ai-hub consome via pin de
   tag + verificação R1 no CI do consumidor.
2. **Varredura universal de propagação**: para TODOS os projetos e subprojetos (flext +
   31 submódulos, ai-hub, agents): integração remota contém o SHA final (`--is-ancestor`
   por repo), gitlinks do umbrella == tips de integração, `uv.lock` pins consistentes.
3. **Varredura de docs + projeções**: `make gen` ×2 byte-idêntico em CADA membro (zero
   superfície defasada); docs canônicas/guias/ADRs/README/gates markdown dos três mundos
   conferidos contra o estado final — qualquer drift = regeneração ou correção na fonte
   ANTES do fecho.
4. **Varredura runtime real**: `make check/test` no ambiente vivo do umbrella e dos
   repos tocados — 100% green, zero warning, saída decisiva; consumidor (ai-hub)
   operando na tag nova.
5. **Fechamento do épico (barra §3.0 em escala total)**: beads F0-F5 fechadas + **zero
   correlacionadas abertas/deferred/blocked sem rota** nos três trackers + `bd lint`
   zero + estado do host mantido (rigs + worktrees dedicadas) + TODOs/planos/docs dos
   três mundos espelhando a realidade final.

## 4. Fronteiras de sessão (lotes realistas)

| Sessão | Escopo            | Stop                                                                                                                                                                                                                   |
| ------ | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1     | F0 completo       | ✅ FEITA (14:45Z reescopo): épico `flext-cpzjo` + F0-F5 lint-clean ×3 trackers; correlação 322/134/33 com rota; ai-hub/agents como rotas                                                                               |
| S2     | F1 completo       | ✅ FEITA: 9 worktrees gravadas→PR→removidas com ancestry-proof; rigs+dedicadas verificados ao vivo; `flext-f73ii` pousada (#682, merge `200bff03a`, 2 passed no SHA merged) e fechada; F0/F1 fechadas com 4 evidências |
| S3     | F2 completo       | barra §3.0: pousos com gates rerun zero warning no SHA + gitlinks/pins propagados                                                                                                                                      |
| S4     | F3 + F4 ondas 1-2 | doctor verde + SLA-1/SLA-3 fechadas com runtime                                                                                                                                                                        |
| S5     | F4 ondas 3-7      | barra §3.0 do piloto: tudo pousado, warn→hard, beads fechadas                                                                                                                                                          |
| S6     | F5 completo       | propagação universal + épico fechado + bd lint zero nos três trackers                                                                                                                                                  |

## 5. Riscos e contramedidas

| Risco                                                 | Contramedida                                                                          |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Fase declarada encerrada com green local apenas       | barra §3.0: gates SÓ no SHA integrado; local-green não fecha bead                     |
| Warning/skip tratado como aceitável                   | lei: warning = RED; nunca normalizado/suprimido; vira bead no turno                   |
| Remoção de worktree com trabalho não gravado          | tree clean + push + ancestry-proof                                                    |
| Rigs alinhados com trabalho local não pousado         | F0.5 pousa ANTES do align (F1.4); align = fast-forward apenas                         |
| Merge travado por proteção externa (reviewer humano)  | único stop legítimo: pergunta exata no turno + rota na bead                           |
| PR de absorção misturando provenâncias                | uma branch/PR por superfície de origem; proveniência no corpo                         |
| Origin mover durante execução                         | re-fetch + `--is-ancestor` a cada material-step; absorver hunk-a-hunk                 |
| Red tratado como fora de escopo (DR3)                 | red no blast radius = bead no turno                                                   |
| Duplicação SLA-3 × ENFORCE-101                        | cross-ref `flext-9wwed` ↔ `flext-ssnc7.4`                                             |
| Grafo stale citado                                    | built-at por bloco (F3)                                                               |
| Venv contaminado entre worktrees                      | guards `UV_PROJECT_ENVIRONMENT`/`VIRTUAL_ENV` sempre                                  |
| Cápsula `~/agents`                                    | zero arquivos novos; absorção in-place; expansão = ADR com operador                   |
| Bead deferred/blocked virar desculpa                  | regra §2.3: rota obrigatória na F0; re-censo a cada END OF TURN de fase               |
| Doc defasada ou projeção hand-editada passando batida | barra §3.0 item 4: docs no mesmo ciclo + regen ×2 pelo gerador; drift = bead no turno |
| Falha do bd usada como desculpa                       | premissa 13:29Z: reparo no dono no turno, operação reemitida                          |

## 6. Proibições duráveis

Push FF na integração · `git add -A` · descartar trabalho alheio (absorção é lei) ·
`rm -f` em lock de journal (kill do owner + bead) · citar crg sem built-at · bead sem
red capturada no turno · arquivos novos em `~/agents` sem ADR · mover texto de plano
past reality · fechar bead com WIP não pousado · fechar fase com green local / warning /
skip silencioso / doc defasada / projeção não regerada (barra §3.0) · hand-edit de
superfície projetada (corrige a fonte + `make gen`) · `FlextResult[None]`/payload None ·
enumeração handcode de facts deriváveis · trabalho fora das worktrees dedicadas após F1
· deixar bloqueio sem rota registrada (§2.3) · reativar gas-city ou usar `gc-*` · tratar
falha do bd CLI como desculpa (reparo no dono no turno).

## 7. Pedidos ao operador

| Item                                                                    | Status                                                                                                                    |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Absorção/remote-ização/rigs/worktree (13:21Z)                           | DADO                                                                                                                      |
| Épico + bead por fase + correlação total + autonomia até o fim (13:26Z) | DADO — A1/A2/A3 viraram gates de registro (§2.4)                                                                          |
| bd CLI sempre funcional + gas-city desativado (13:29Z)                  | DADO — premissas §0.6                                                                                                     |
| Barra de fechamento por fase (13:54Z)                                   | DADO — §3.0: propagação + 100% green runtime real sem warning + beads fechadas                                            |
| Docs atualizadas + projetada regerada no fecho de cada fase (13:56Z)    | DADO — §3.0 item 4                                                                                                        |
| Únicos stops restantes                                                  | proteção externa real de plataforma (reviewer humano exigido) ou ação destrutiva fora do escopo — pergunta exata no turno |

## 8. Validação do plano

1. F0: `bd lint` = zero nos trackers flext/ai-hub/agents; épico + beads F0-F5 com
   description/design/acceptance completos; censo com **todas** as beads
   open/claimed/deferred/blocked correlacionadas com rota.
2. Cada fase termina com a barra §3.0 inteira (5 itens) registrada na bead: 4
   evidências + merge-base por repo + gates zero warning no SHA integrado + runtime
   observado + docs atualizadas/projeções regeradas ×2.
3. F1: `git worktree list` por repo mostra só rigs + worktrees dedicadas; rigs
   `rev-parse HEAD == origin/<integração>`.
4. TODOs dos planos vivos espelhados em cada END OF TURN; gates de registro anotados nas
   beads F2/F3/F4 antes de avançar.
5. Fim do épico: propagação universal provada por repo (§3.6.2), docs+projeções
   regeradas ×2 por membro (§3.6.3), varredura green/runtime real sem warning (§3.6.4),
   zero beads abertas/deferred/blocked sem rota nos três trackers, `bd lint` zero, host
   no estado-final da F1 mantido.
6. Premissas vigentes em TODAS as fases: bd operante por CLI (falha = reparo no dono no
   turno) e nenhuma invocação `gc-*`/gas-city.
