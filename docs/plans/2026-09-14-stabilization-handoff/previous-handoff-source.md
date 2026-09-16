## Handoff substituído para retomada — 2026-09-14

Leia `~/.claude/plans/happy-puzzling-flask-handoff-20260914-audit.md` primeiro.
Este arquivo preserva o snapshot das 17:45 UTC e não deve orientar branches,
PRs, processos ou próximos comandos sem a atualização. A bead `flext-itpd1.1`
permanece em andamento. Publicação atual é WIP; green/green não foi alcançado.

---

# Handoff — FLEXT 0.12.0 estável (continuação em nova sessão)

Pausado pelo operador em 2026-09-14 ~17:45Z. Plano aprovado (SSOT de escopo e decisões):
`~/.claude/plans/happy-puzzling-flask.md`. Épico `flext-itpd1`, bead ativa `flext-itpd1.1`
(notas completas com todos os SHAs). Pacote ai-hub: `~/.claude/plans/ai-hub-envrc-agent-hooks.md`.

## Como retomar

1. Tracker (não mudar config do beads):
   `export BEADS_DOLT_SERVER_HOST=127.0.0.1 BEADS_DOLT_SERVER_PORT=14499 BEADS_DOLT_SERVER_DATABASE=flext; bd show flext-itpd1.1`
2. Lane: worktree `/home/marlonsc/flext/.claude/worktrees/bugfix+stabilize-0.12.0`
   (entrar com EnterWorktree `path`), branch `bugfix/stabilize-0.12.0` no super e no flext-infra.
3. Ler o plano inteiro, depois esta seção "Estado" e seguir "Próximos passos" na ordem.

## Ordens vigentes do operador (mais nova vence)

- Executar o plano até o fim; validar cada ação antes de declarar pronto.
- Sempre: fix-forward/adopt, PRs propagados à integração `0.12.0-dev` (merge commit autorizado),
  propagar a `~/flext`, beads fechadas com evidência.
- flext com zero conhecimento de ai-hub/Gas City; beads só identidade; nenhum verbo Make com modo
  não-apply; Makefile não valida parâmetros; AGENTS.md 4 regiões; gh/GitHub runtime sai, mas `.github/**`
  gerado pelo SSOT do flext-infra e arquivos custom ficam (fronteira por `.gitignore` genérico);
  `.envrc` termina só com `source_env_if_exists .envrc.local`.

## Estado (medido)

| Item | Estado |
|---|---|
| flext-infra S0+S1+A4+A5 | `1ccd926e7`, PR #727 merge `b13793fb1` em `0.12.0-dev` |
| 30 membros (projeções regeneradas) | PRs merged; SHAs na nota da bead; lane dos membros em `0.12.0-dev` local nesses SHAs |
| Super | merge `-s ours` de `c2dba374e0` (adjudicado) + `5806a67377` (31 gitlinks, `[project.scripts]` → `FlextRoot*.main`); push feito; **PR flext-sh/flext#240 aberto, não mergeado** |
| flext-infra S2 (1ª metade) | `[WIP] 95baa0c0d` só templates (`.envrc.j2`, `beads-config.yaml.j2`, `beads-metadata.json.j2`, `.mise.toml.j2`, `check-beads-policy.sh.j2`, `config/beads.yaml.j2`, `config/workspace.yaml.j2`); push feito; sem PR; **não regenerado/validado ainda** |
| `make check` frota | parado por ordem em 9/32; 0 tracebacks; PASS flext-api; FAIL por achados: raiz, auth, cli, core (619: namespace 585, silent-failure 18, codemod 9, pyrefly 3, pyright 2, mypy 1, runtime-census 1), db-oracle (pyrefly `services/api_runtime.py:123`), dbt-ldap, dbt-ldif, dbt-oracle. Relatórios em `<lane>/.reports/workspace/check/*.log` |
| Validação anterior (lane) | gen ×2 ponto fixo; setup 0; fix 32/32; fmt 32/32 |
| Beads | fechadas nesta sessão: `flext-xeg9x`, `flext-5mgye` (obsoletas por S1) |
| `~/flext` (checkout do operador) | **não propagado**; sessão externa (pid 3657409) roda `make -C <membro> gen` em loop e apaga o lock do journal — coordenar antes |

## Próximos passos (ordem)

1. **PR #240**: conferir checks (`gh pr checks 240 -R flext-sh/flext`), merge commit
   (`gh pr merge 240 -R flext-sh/flext --merge`), `git merge-base --is-ancestor` contra base recém-buscada.
2. **Propagar a `~/flext`**: sair do isolamento (ExitWorktree keep); em `~/flext` fetch e merge ff de
   `0.12.0-dev` no super e `git submodule update` para os gitlinks; adotar WIP local por fix-forward
   (nunca reset/stash); rodar `make setup` e `make gen` (o erro do operador era guarda APPLY + Timeout de lock
   da sessão externa). Defeito anotado: Timeout de lock sai como traceback cru → mensagem acionável no dono
   (`codegen` transaction journal).
3. **S2 2ª metade** (flext-infra, mapa de linhas no plano §S2): remover `gascity_enabled`
   (`_models/config.py` 238, 1532, 1680, 1715, 2370, 2515; `detector.py` 215-291, 587-592, 639;
   `conform.py` 2027-2031, 2042, 2054, 2096), `EnvrcRenderSpec.gascity` (413), `BeadsConfigRenderSpec`
   endpoint/types/dolt (1665-1705) → só `issue_prefix`, `WorkspaceBeadsServerSpec` (2314) + `beads_server`,
   `ledger_id/ledger_prefix` (2422-2429) + cross-check `detector.py:261-278`, `beads_enabled` (2361),
   `BeadsProjectSpec.custom_issue_types`+validador (1481-1494), `WorkspaceEnvironmentSyncRequest.beads` +
   `BeadsWorkspaceEnvironmentSpec` (3267-3322), `mise_toolchain.py` `gascity` (305) + `BeadsEndpointSpec`
   (400) + campos endpoint/types/dolt/export/backup/flush (416-473), `_protocols/base.py` 118-135 e 234-237,
   `workspace/environment_beads.py` (mixin; manter só `FlextInfraWorkspaceEnvironmentSync` sem ramo beads —
   o `direnv allow` Python é duplicado da recipe de setup: exterminar), `environment.py:56-88` param `context`,
   `api.py:11`, `services/cli_routes_workspace.py:11,36-46`, `conform.py:493-495,609-711`
   (rotas beads), `detector.py:27-66,461-477,523-560` (symlink/rota). `codegen.yaml` toolchain gascity/beads
   endpoint; template `.envrc.beads-workspace.j2`; `check-beads-policy.sh.j2` sem invocador → remover com entradas.
   Testes listados no plano §S2. Então gen ×2, setup, fix, fmt, check (executa até o fim), grep de resíduo,
   commit sem `[WIP]`, PR, merge, propagar membros (`land_members.sh`) e super; enviar merge SHA à sessão ai-hub
   (ela espera o SHA do `.envrc.j2`).
4. S2b, S3, S4 (isolamento de exceção por gate em `check/workspace_check_gates.py`), S5, S6, S7, S8 conforme plano.
5. Achados de `make check` (lista acima) entram por dono nas fatias S5/S6/S8; `make check` precisa rodar 32/32.

## Scripts de apoio (cópias duráveis em `~/.claude/plans/land_members.sh` e `~/.claude/plans/roll_members.sh`)

- `land_members.sh <assunto> <membro>…`: por membro limpo exige HEAD == `origin/0.12.0-dev`, cria
  `bugfix/stabilize-0.12.0`, `add -u`, commit, push, `gh pr create --base 0.12.0-dev`, `gh pr merge --merge`.
- `roll_members.sh <membro>…`: exige limpo, HEAD ancestral do merge e árvore idêntica; atualiza
  `0.12.0-dev` local ff e faz switch.

## Limites do harness observados

- Um só `&&`/`&` e um só `|` por comando; `;` só após `export`.
- `git -C ~/flext` recusado enquanto em worktree (usar ExitWorktree).
- Nota de bd com `$CLAUDE_JOB_DIR` literal foi recusada.
- Pendentes após pouso: retirar branches remotas `bugfix/stabilize-0.12.0` dos membros e PRs antigos
  (#226, #235, #231, #239, #225, `wip/duplicate/*`) só com prova `--is-ancestor` (S8).
