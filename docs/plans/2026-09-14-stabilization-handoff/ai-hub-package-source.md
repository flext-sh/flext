# Documentation

<!-- TOC START -->
- [Atualização de transferência — 2026-09-14](#atualizacao-de-transferencia-2026-09-14)
- [1. Sintoma medido](#1-sintoma-medido)
- [2. Causas (arquivo:linha)](#2-causas-arquivolinha)
- [3. Mudança (um dono, sem daemon)](#3-mudanca-um-dono-sem-daemon)
- [3b. Defeito adicional encontrado: projeções de governança commitadas com marcadores de conflito](#3b-defeito-adicional-encontrado-projecoes-de-governanca-commitadas-com-marcadores-de-conflito)
- [3c. Fronteira flext ↔ ai-hub decidida pelo operador (14/09, atualização)](#3c-fronteira-flext-ai-hub-decidida-pelo-operador-1409-atualizacao)
- [4. Aceite (prova em runtime real)](#4-aceite-prova-em-runtime-real)
<!-- TOC END -->

## Atualização de transferência — 2026-09-14

Estado e crítica atuais: `~/.claude/plans/happy-puzzling-flask-handoff-20260914-audit.md`.
S2 ainda não foi concluída: não consumir um SHA de template parcial como entrega
beads identidade-apenas/AGENTS quatro regiões. Infra #731 reúne contribuições na
lane; não equivale ao SHA de merge da S2 completa esperado por este pacote.
O ambiente primário tem trabalho ativo em infra #732. Coordenar por estado fresco.
Este adendo não declara deploy, repin, envio de mensagem ou aceite do ai-hub.

---

# ai-hub — `.envrc` carregado em toda sessão de agente (pacote para a sessão do ai-hub)

Origem: bead flext `flext-itpd1.1` (P-1b). Ordem do operador (14/09): o `.envrc` do diretório de
trabalho deve carregar em **todo** agente, **sempre**, inclusive em git worktrees. Sem export
manual, sem fallback, sem jeitinho. Este documento é o pacote de execução; a sessão do ai-hub
executa numa lane própria do ai-hub com os gates nativos do ai-hub.

## 1. Sintoma medido

- **Onde:** sessão Claude Code (job em background) rodando em
  `~/flext/.claude/worktrees/bugfix+stabilize-0.12.0`.
- **Ambiente herdado do shell que lançou o agente, com o direnv do ai-hub:**
  - `DIRENV_FILE=~/ai-hub/.envrc`
  - `BEADS_DOLT_SERVER_DATABASE=aihub`
  - `VIRTUAL_ENV=~/ai-hub/.venv`
- **Efeito:** `bd list` no flext → `PROJECT IDENTITY MISMATCH` (banco `aihub` servido para o
  projeto flext).
- **Contraprova:** o shell interativo do operador funciona (`BEADS_DOLT_SERVER_DATABASE=flext`),
  porque `config/host_runtime.yaml:33-34` → `templates/host-runtime/bash.rc.sh.j2:23-25`
  (`eval "$(direnv hook bash)"`) só cobre shells interativos.

## 2. Causas (arquivo:linha)

1. **Hooks declarados mas não implantados:** `config/agents.yaml:49-117` declara a surface `hooks`
   do Claude (session-start, subagent-start, stop, stop-failure, session-end, pretool, posttool,
   user-prompt). Porém `~/.claude/settings.json` não tem chave `hooks`, então nenhum hook do
   ai-hub roda no Claude hoje.
2. **Nenhum adapter para `CwdChanged`:** `agents.yaml:26` lista `CwdChanged` em
   `supported_events`, mas nenhum adapter o assina. Trocar de repositório dentro da sessão nunca
   recarrega o ambiente.
3. **Ninguém grava o ambiente da sessão:**
   - O Claude Code expõe `CLAUDE_ENV_FILE` apenas a processos de hook `SessionStart`/`Setup`/
     `CwdChanged`/`FileChanged` e aplica esse arquivo aos comandos Bash seguintes (confirmado no
     binário instalado 2.1.269).
   - A cadeia `SessionStart` em `config/hooks.yaml:1636-1638` (`ccg_hooks.session_start_with_core`,
     `governance_capsule.session_start`) só injeta contexto.
4. **A fronteira certa já existe:** `AiHubHookClient.run_cli`
   (`src/ai_hub/services/hook_client.py:88-149`) roda **dentro do processo do cliente** lançado
   pelo Claude, com `payload.cwd` e o ambiente do agente.
   - O daemon (socket `settings.AiHub.hooks.socket_path`) não enxerga `CLAUDE_ENV_FILE`.
   - Precedente de leitura de ambiente nativo nessa mesma fronteira: `hook_client.py:111-125`
     (`hook_project_root_env`).
5. **opencode:** `config/opencode.yaml:10` instala `@simonwjackson/opencode-direnv`, que é fail-open.
   - Um `.envrc` bloqueado vira só um toast; os demais erros são engolidos.
   - Roda uma única vez por `session.created`.
6. **Kilo:** não tem mecanismo. **Codex:** nenhum mecanismo documentado confirmado localmente
   (`shell_environment_policy` é estático).

## 3. Mudança (um dono, sem daemon)

1. **`config/agents.yaml`, engine do Claude:**
   - Declarar a variável do arquivo de ambiente, por exemplo
     `engine.hook_env_file_var: CLAUDE_ENV_FILE`, tipada no modelo do engine de agente (mesmo
     padrão de `hook_project_root_env`).
   - Adicionar o adapter `cwd-changed` (`events: [CwdChanged]`, `command_template: ai-hub-hook`,
     `protocol: json`) ao lado de `session-start`.
2. **`hook_client.run_cli`:** para `SessionStart` e `CwdChanged`, quando o engine declara
   `hook_env_file_var` e a variável está definida, antes do dispatch ao daemon:
   - Executar o `direnv` instalado (binário do dono `host_runtime`) como `direnv export bash` com
     `cwd=payload.cwd`.
   - Anexar o stdout ao arquivo apontado pela variável.
   - Usar o dono de subprocesso existente (`u.AiHub`/`u.Cli`); nenhum helper novo.
3. **Falha declarada, nunca silenciosa:** `.envrc` bloqueado ou `direnv` com erro vira
   `system_message` no `HookDecision`, com o caminho e o stderr. Sem skip e sem fallback.
4. **Deploy canônico:** `agentsctl sync` para que `~/.claude/settings.json` contenha de fato os
   hooks gerenciados (SessionStart e CwdChanged incluídos). A segunda execução não pode mudar bytes.
5. **Demais provedores:**
   - opencode/Kilo: substituir o plugin fail-open por um mecanismo do dono ai-hub com a mesma
     semântica (recarrega no cwd da sessão, falha visível).
   - Codex: só se houver mecanismo documentado; senão registrar `NOT SUPPORTED` com a referência
     da documentação.
6. **Fora deste pacote:** a confiança `direnv allow` de worktrees novas pertence ao caminho que
   cria a worktree.
   - A parte do flext-infra (`.envrc.j2` e bootstrap) está sendo feita na sessão flext (P-1b/P-1c).

## 3b. Defeito adicional encontrado: projeções de governança commitadas com marcadores de conflito

- **Onde:** `flext-cli`, no commit que o superprojeto aponta (`5b2b182d`).
- **Arquivos rastreados com `<<<<<<< HEAD` / `>>>>>>> origin/integration/sweep-20260830`:** 69, entre
  `.claude/rules/*.md`, `.claude/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`,
  `.claude/agents/python-reviewer.md`, `.claude/settings.json`, `.agents/projection.json` e os
  `.agents-governance.json`.
  - Contagem em `HEAD` (amostra): `.claude/settings.json` 3, `.claude/rules/runtime--fail-loud.md` 1,
    `.agents/projection.json` 1.
  - Nada disso é mudança não commitada: `git status` limpo em `.claude`/`.agents`.
- **Efeito:**
  - `settings.json` com marcadores é JSON inválido para o Claude Code nesse repositório.
  - Regras e skills projetadas chegam aos agentes com as duas versões misturadas.
- **Dono:** a projeção do ai-hub (`agentsctl sync`), não edição manual no membro.
- **Correção e aceite:**
  - A sessão do ai-hub regenera as projeções do flext-cli pelo dono.
  - A projeção passa a recusar publicar (e o `agentsctl check` passa a acusar) qualquer arquivo
    projetado contendo marcadores de conflito.
  - Prova: `git -C flext-cli grep -c '^<<<<<<< ' HEAD -- .claude .agents` retorna vazio após o
    commit da regeneração.

## 3c. Fronteira flext ↔ ai-hub decidida pelo operador (14/09, atualização)

- **flext não conhece ai-hub nem Gas City.** Nenhum arquivo, chave, template ou doc do flext cita ai-hub/gc.
- **`.envrc` do flext** termina só com `source_env_if_exists .envrc.local` (rastreado, criado uma vez, nunca
  sobrescrito). O ai-hub injeta o ambiente dele (Gas City → Beads → standalone, `BEADS_DOLT_SERVER_*`) por
  biblioteca direnv própria em `~/.config/direnv/lib/` e pelos hooks de agente — nunca por arquivo no flext.
- **Beads no flext = identidade apenas** (`issue_prefix`, `backend/database/dolt_database/project_id`,
  `config/beads.yaml` de identidade, instalação do `bd`, gitignore `.beads`, `bd hooks`). Servidor, host,
  porta, modo, tipos custom e rotas vêm só do ambiente fornecido pelo ai-hub.
- **AGENTS.md** é gerado pelo flext-infra com 4 regiões; o ai-hub escreve apenas dentro da região `external`
  preservada verbatim. CLAUDE.md não é gerado pelo flext.
- **GitHub runtime** sai do flext e passa ao ai-hub: `gh pr create/edit` do release, `gh release create/upload`
  de assets, `scripts/workspace/dependabot_merge.py`, `.github/workflows/conflict-marker-check.yml`. Os
  arquivos `.github/**` de CI/dependabot gerados pelo SSOT do flext-infra ficam no flext.
- **Projeções de runtime do ai-hub** (`.github/{agents,hooks,skills,instructions}`, `aihub-hooks`, `.claude/`,
  `.agents/` etc.) não são rastreadas pelo flext; o flext usa padrões genéricos de ignore (sem nomear a
  ferramenta). A saída de runtime do ai-hub não pode aparecer como não rastreada nos repos flext.
- **Repin**: o ai-hub espera os SHAs de merge do PR flext-infra #727 e da fatia `.envrc.j2` (S2) em `0.12.0-dev`.
  - Estado 14/09 ~17:45Z: #727 mergeado em `b13793fb1` (SHA já enviado). A fatia `.envrc.j2` existe só como
    `[WIP] 95baa0c0d` na branch `bugfix/stabilize-0.12.0` do flext-infra (não mergeada; modelos ainda carregam
    `gascity`/endpoint). SHA de merge da S2 ainda pendente — enviar após o pouso da S2 completa.

## 4. Aceite (prova em runtime real)

- **Worktree nova:** sessão Claude Code nova numa worktree nova do flext. O primeiro comando Bash
  mostra `BEADS_DOLT_SERVER_DATABASE=flext` e `VIRTUAL_ENV=<worktree>/.venv` sem nenhum export
  manual; `bd list` funciona.
- **Troca de repositório:** `cd` para outro repositório dentro da sessão (`CwdChanged`) troca para os
  valores daquele repositório.
- **`.envrc` bloqueado:** produz mensagem visível do hook com o caminho.
- **Deploy:** `agentsctl sync` ×2 → a 2ª execução muda 0 bytes; `~/.claude/settings.json` contém os
  hooks gerenciados de SessionStart e CwdChanged.
- **Gates:** gates nativos do ai-hub verdes; teste funcional público do `hook_client`, sem mock, com
  um `.envrc` real em `tmp_path` e `CLAUDE_ENV_FILE` apontando para `tmp_path`.
