# Estabilização 0.12.0 — recuperação, centralização beads, documentação e automação

## Missão (operador, 2026-09-15)

Recuperar as últimas sessões (Kilo + Codex), alinhar com o beads centralizado do Gas
City (uso obrigatório via direnv), replanejar usando toda a informação recuperada para
melhorar documentação, automações e skills, e então implementar: concluir e estabilizar
a versão do FLEXT neste estado, com validação e correção coordenadas e remoção (absorção
adjudicada) de todo o trabalho paralelo incompleto.

## Estado recuperado (evidência)

### Sessão Kilo (ses_f5e00094bffeC88CFrf3lIdv3n, 2026-09-14/15)

- ruff/pyrefly/rumdl zerados nos 32 projetos (causa raiz: nested workspace em
  `flext-infra/pyproject.toml` removido; ~50 arquivos de teste com conflitos de merge
  resolvidos adotando `origin/bugfix/stabilize-0.12.0`).
- `uv.lock` des-trackado em 11 submódulos + `.gitignore` (staged, sem commit).
- Root movido para `0.12.0-dev`; WIP adotado via merge `--no-ff`.
- `make setup`/`make gen` rodaram sob bloqueio de journal de ator concorrente
  (resolvido: lock liberado); ciclo completo de gates NÃO terminou verde.
- Beads local sendo exterminado em favor do servidor Dolt central do Gas City (config
  `.beads/config.yaml` + `metadata.json` modificados na raiz; templates `.envrc*.j2` +
  `.envrc.gascity.j2` criados em flext-infra, SEM commit).
- Thread final inacabada: automatizar correções recorrentes via templates (gate de
  namespace do flext-auth com 49 erros era o caso ativo).

### Handoff vigente do flext-infra (docs/roadmap/namespace-automation-handoff-2026-09-14.md)

- Entrega corrente: PR #734 Draft, branch `fix/workspace-hygiene-0.12.0`, tip publicado
  `5eb47cd21`; CI do Draft SKIPPED (não é aceite). PR #732 MERGED (mergeCommit
  758467a6a); remoto avançou até `ee9e5e018` (corrige nested workspace `flext-api` —
  causa comum de falha de setup). PRs #731 (até `ec9813edd`) e #733 (`flext-ro6mj.1`)
  aguardam reconciliação.
- `make test` infra: exit 2, timeouts reais (-15/-9), suíte interrompida ~10-21%; nenhum
  verde completo. `make check` mais recente: Ruff/Mypy/Pyrefly 0; Pyright -2
  KeyboardInterrupt; namespace 382 findings (gate custom vermelho tolerado pelo operador
  com evidência — atualização da retomada).
- Beads central provado via `direnv exec ~/flext bd ...` (context/show exit 0; identity
  preservada); `gc doctor`→`gc start` usados quando Dolt caiu. Bead ativa do trabalho:
  `flext-c4k44` + `flext-5fxu6.4` (in_progress).
- Migração sem-lock PENDENTE: template ainda executa `uv sync`/`uv lock`; modernizer e
  release ainda leem lock. MAKE gerado novo (uv via mise exec, `--no-project`) presente
  no WIP do root Makefile.
- Sequência de retomada (§8): confirmar estado/reproduzir primeira falha → corrigir
  automação em ordem de dependência (6 tiers: batch_gates/snapshot → classvar/rope_fixer
  → typing_unifier → semantic_apply/class_nesting → batch_apply/namespace →
  validate/census) → ladder de gates §8.3 → aceite §8.4 (analisadores zero-erro,
  test/build/docs exit 0, ponto fixo, merge --no-ff, revalidação no SHA mesclado, 4
  fontes de evidência no Beads). Críticas §4 a não repetir: prioridade dirige a onda
  (uma classe de violação ponta-a-ponta via make mod, sem cottage manual); mover
  constante só após provar contratos; mutabilidade não é grafia (dict→Mapping proibido
  sem prova); evidência no mesmo SHA do código; gates respondem a pergunta do seu
  escopo.
- Bead-mãe candidata já existente: `flext-c4k44` (fechamento/testes) + `flext-5fxu6.4`
  (owner, in_progress) — reconciliar em vez de duplicar.

### Sessão Codex (2026-09-14/15 — extraída)

- Sessão principal (01a0a0f1, cwd ~/flext, épico `flext-itpd1`, bead `flext-itpd1.1`
  in_progress): lane worktree `.claude/worktrees/bugfix+stabilize-0.12.0`; **PR #731**
  (flext-infra, bugfix/stabilize-0.12.0 → 0.12.0-dev) DRAFT; **PR flext#240**
  (superprojeto) OPEN sem merge; `make check` 32/32 exit 2; `make gen` FAILED às 02:45;
  turno abortado 02:40:38 sem handoff (pedido 3×). Beads fechadas antes da sessão:
  `flext-xeg9x`, `flext-5mgye`; obsoletas marcadas: 13axf, dj2f6, t4hyd, didi7, kmtt3,
  xtzkz, 9oljq, a0edu, 09686, 1wjg1.10. PR #727 + 30 PRs de membros merged pré-sessão.
- Subagente Copernicus (01a0a188): patches candidatos PRONTOS em `~/.claude/plans/` (git
  apply --check exit 0, NÃO aplicados):
  `flext-infra-apply-selector-cutover-owner-draft.git.patch` (106 caminhos, remoção do
  seletor APPLY/apply_changes→dry_run), `flext-infra-combined-cutover.git.patch`,
  `flext-foundation-tap-contract-fixes.git.patch` (breadcrumb []→() em
  flext-tap-oracle-wms), `flext-target-oic-validation.git.patch` (TypeAdapter em
  flext-target-oracle-oic).
- Itens abertos que alimentam esta estabilização: (1) consertar make gen e rodar o ciclo
  canônico; (2) revisar+aplicar patches do Copernicus; (3) merge PR #731 + PR #240; (4)
  fechar `flext-itpd1.1` com evidência.
- Reconciliação de beads: `flext-itpd1.1` (codex) ≈ `flext-c4k44`/`flext-5fxu6.4` (kilo)
  — mesma frente de estabilização; continuar nas existentes, sem duplicar.

### Repositório (censo 2026-09-15)

- Superprojetos e 31 submódulos em `0.12.0-dev`, exceto **flext-infra em
  `fix/workspace-hygiene-0.12.0`** (lane não mesclada, commits: 712624c9d, 5eb47cd21,
  4e3c01128 + WIP não commitado em conform.py/codegen.yaml/templates).
- Todos os 32 repositórios com WIP sujo (projeções geradas + config beads + Makefile
  uv-owner rework + exemplos/tests hand-edits). Gitlinks dos 31 submódulos avançados vs.
  ponteiro do superprojeto.
- `flext-cli`: churn `bd init` revertido no topo.

### Gas City / beads centralizado

- Cidade: `~/gc`; `AGENTS_GAS_CITY_ROOT` exportado em
  `~/.config/environment.d/40-agents.conf`.
- Servidor Dolt central: PID 2146710, porta 14499, estado em
  `~/gc/.gc/runtime/packs/dolt/dolt-state.json` (running=true).
- Rig `flext` registrado (prefix flext, default_branch 0.12.0-dev, suspended_on_start).
- Contrato de ativação (docs já commitadas na lane infra em
  `docs/guides/execution-context.md`): `.envrc.local` gerado carrega
  `AGENTS_GAS_CITY_ROOT`, lê porta da publicação da cidade, banco da metadata do rig;
  prova: `direnv exec <repo> bd show <id> --json`. Reparo de identidade:
  `gc rig set-endpoint flext --inherit`.
- Exemplar funcional: `flext-plugin/.envrc.local` (não trackado) — seção gerada com
  guard em `AGENTS_GAS_CITY_ROOT` + `BEADS_DOLT_AUTO_START=0`.
- **Raiz e demais membros ainda SEM `.envrc.local`** — bd na raiz rodou sem o contrato
  direnv (uso incorreto corrigido pelo operador).

## Plano

### Fase R — Recuperação (concluída ao fechar este documento)

1. [x] Sessão Kilo recuperada (transcrição + digest).
2. [ ] Sessão Codex extraída (task em curso).
3. [ ] Verificação de rota canônica bd→cidade (task em curso).
4. [ ] Mapa de wiring `gascity_enabled`/conform (task em curso).
5. [ ] Adjudicação do WIP da frota (task em curso).

### Fase P — Replanejamento e melhorias (docs/automação/skills)

1. Consolidar este plano com os resultados dos subagentes.
2. Criar/atualizar bead-mãe da estabilização no beads central (via direnv).
3. Documentação:
   - Runbook de estabilização 0.12.0 em `docs/ways-of-working/` (fontes: plano WS-A,
     lições do ciclo: idempotência gen dupla, journal CAS, absorção fix-forward, merge
     --no-ff, gates no SHA mesclado).
   - Revisar `docs/guides/` vs. realidade (make-commands, testing) — só onde houver
     drift comprovado.
   - Drift confirmado (scan 2026-09-15): guias make-commands/development/ testing
     LIMPOS; resíduo do contrato aposentado (APPLY=/WHAT=/uv.lock) em: `AGENTS.md:111`
     (SSOT! "with for mutation"), `docs/GOVERNANCE.md:95`,
     `docs/version-policy.md:28-29` (inventa verbo `ship` inexistente; verbos reais:
     release-plan/version/tag/build), `docs/architecture/adr/010:81`, `adr/004` (5
     pontos), `docs/architecture/arc42/12-glossary.md:68`,
     `docs/architecture/settings-config-canonical-pattern.md:144,165`,
     `docs/scripts/gate-contract.md:4`. `docs/plans/*` históricos = evidência, não
     reescrever. Corrigir SSOT e docs vivos; ADRs recebem nota de superação, não
     reescrita silenciosa.
4. Automação (dono canônico flext-infra):
   - Aterrissar a lane `fix/workspace-hygiene-0.12.0` (templates
     `.envrc.gascity.j2`/`.envrc.j2`/`.envrc.beads-workspace.j2`, conform beads routes,
     `.envrc.local` merge policy) — é a automação que elimina a classe de erro "beads
     fora do contrato direnv".
   - Retomar a thread de automação por templates (erros recorrentes →
     templates/codemods), começando pelo gate de namespace (flext-auth).
5. Skills: atualizar `.agents/skills/flext-law/SKILL.md` (ou referência) com a lei de
   uso do beads central via direnv (não é preferência; é contrato).

### Fase I — Implementação da estabilização

1. **Contrato beads**: gerar `.envrc.local`/seção gascity na raiz e membros via conform
   da lane infra aterrissada; `direnv allow`; provar `direnv exec . bd show` — a partir
   daqui TODO bd via `direnv exec`. Wiring confirmado (scan): `gascity_enabled` default
   True (sem overlay em `repository_policy_overlays` do manifest do membro) — nenhum
   edit em workspace.yaml é necessário para ATIVAR; `make gen` (scope=all) na raiz
   renderiza root+31 membros; o motor conform lê os templates do flext-infra INSTALADO
   (Git tip da branch de integração) ⇒ a lane `fix/workspace-hygiene-0.12.0` precisa ser
   commitada, mesclada `--no-ff` em `0.12.0-dev` e PUSHED antes do
   `make setup`/`make gen` pegarem o template novo. Se o city-state faltar, a ativação
   direnv falha barulhenta (jq error) — comportamento desejado (fail loud).
2. **Absorção do WIP** (fix-forward, nada descartado):
   - flext-infra: commit do WIP na lane, merge `--no-ff` para `0.12.0-dev`.
   - Demais 31 repos: commits escopados por categoria (A beads-config, B projeções
     geradas via `make gen` do novo motor, C hand-edits adjudicados), cada um na sua
     lane → merge `--no-ff` em `0.12.0-dev`.
   - Exterminar resíduo: `uv.lock`/`mise.lock` tracked, `.bak`, churn `bd init` do
     flext-cli (reverter o par init/revert = manter estado pré-init se for o estado
     canônico).
3. **Gates**: `make gen` → `make mod` → `make gen` 2x (ponto fixo) → `make fix` →
   `make fmt` → `make check` → `make test` → `make build` → `make docs` → `make gen`
   (sequência canônica do handoff §8.3; uma falha → parar e corrigir o dono; sem inflar
   timeouts, sem remover testmon). Aceite de check (§atualização):
   Ruff/Mypy/Pyright/Pyrefly zero erros; gates customizados podem ficar vermelhos COM
   evidência explícita (agregado + por gate); nunca chamar check verde com exit != 0.
4. **Landing**: gitlinks do superprojeto atualizados, commit escopado, push FF para
   `origin/0.12.0-dev`; bead fechada com evidência (comandos, exit codes, SHAs).
5. **Beads**: reconciliar backlog (286 abertas): fechar as tornadas obsoletas pelos
   ciclos já landados, atualizar as P0 vigentes com estado real.

### Critérios de parada

**CHECKPOINT 2026-09-15T06:20Z (evidência em flext-c4k44 + flext-itpd1.1):**

CONCLUÍDO:

- Recuperação total (kilo ses_f5e000..., codex 01a0a0f1/01a0a188) + replan (este
  documento) + docs (8 arquivos alinhados ao contrato selector-free, ADRs com nota de
  superação) + skills (flext-law: contrato direnv beads + resume entry points) + runbook
  (docs/ways-of-working/stabilization- checkpoint-0.12.md).
- flext-infra: lane fix/workspace-hygiene-0.12.0 + origin/bugfix absorvidos, merge
  --no-ff → 0.12.0-dev, pushed (b15407933); PR #731 MERGED.
- Frota: 30 membros com WIP absorbido em commits escopados (projeções convergidas +
  beads central + reparos), pushed FF nos tips.
- Superprojeto: docs+skills, projeções raiz (+.envrc/.envrc.local gascity), gitlinks
  31/31 — 3 commits, pushed (5dd525ea57); PR #240 MERGED (admin, autorização do operador
  registrada); merge do PR absorvido local (e092bef1a2, pushed).
- Gates: make setup exit 0 (286 pkgs, sem locks); make fix 32/32 PASS; make fmt 32/32
  PASS; make gen exit 0 pré-merge (32/32 conform).
- Contrato beads central: raiz com seção gascity renderizada;
  `direnv exec . bd context --json` exit 0 (backend dolt); bd updates de evidência exit
  0 via direnv.

PENDENTE (próxima janela exclusiva — o CAS rejeita gen concorrente, correto):

1. `make gen` pós-merge até ponto fixo (2x zero-diff) — bloqueado por edição concorrente
   de fontes flext-auth/flext-infra pelo segundo ator (atomic-source-changed; aguardar
   ciclo dele terminar).
2. `.beads/metadata.json` dos membros (dolt_mode=server) — render do gerador no mesmo
   gen; destrava o direnv dos 28 membros e a classe exit=1 do check.
3. `make check` — findings reais em ~7 repos (api: pyrefly=10 mypy=14 namespace=1;
   cli/core/tests/web/raiz exit=2) — corrigir por causa raiz.
4. `make test` — suíte do infra segue em timeout (-15) a ~10-21%; reaproveitar §8.4 do
   handoff.
5. Resíduos: journal prepared tx db00d46c (recupera no primeiro gen limpo); retirement
   de worktrees/branches já absorvidos (usar `crg prune` como modelo de higiene + bead
   flext-xtzkz); 23 patches ~/.claude/plans já contidos nos merges — auditar antes de
   descartar.

## Regra de execução

Subagentes para exploração/tasks simples; thread principal coordena efeitos sequenciados
(commit, merge, push, fechamento de bead). Todo bd via direnv após a Fase I.1. Nada de
rebase/force-push/descarte de trabalho alheio.
