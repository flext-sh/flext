# Achados da auditoria — Concluir o pipeline com integração contínua e prova real

<!-- TOC START -->

- [A. Estado real da integração](#a-estado-real-da-integracao)
  - [A.1 Workspaces existentes (nenhum clone criado)](#a1-workspaces-existentes-nenhum-clone-criado)
  - [A.2 Os 17 membros sem a revisão de entrada — verificado, exatamente 17](#a2-os-17-membros-sem-a-revisao-de-entrada-verificado-exatamente-17)
  - [A.3 Publicação (main workspace x recovery)](#a3-publicacao-main-workspace-x-recovery)
  - [A.4 WIP montado no merge da raiz (recuperação)](#a4-wip-montado-no-merge-da-raiz-recuperacao)
- [B. Contrato .venv — falha exata localizada](#b-contrato-venv-falha-exata-localizada)
  - [B.1 A falha membro-como-standalone](#b1-a-falha-membro-como-standalone)
  - [B.2 Symlink de venv é tolerado (contrário ao contrato de rejeição)](#b2-symlink-de-venv-e-tolerado-contrario-ao-contrato-de-rejeicao)
  - [B.3 Sanitização de ambiente herdado — já existe, lacuna confirmada](#b3-sanitizacao-de-ambiente-herdado-ja-existe-lacuna-confirmada)
  - [B.4 Atualização de Python](#b4-atualizacao-de-python)
  - [B.5 Consumidores e documentação](#b5-consumidores-e-documentacao)
- [C. make mod e orçamento de suíte](#c-make-mod-e-orcamento-de-suite)
- [D. Pipeline AI Hub (ccs / CLIProxy / systemd)](#d-pipeline-ai-hub-ccs-cliproxy-systemd)
  - [D.1 Workspaces](#d1-workspaces)
  - [D.2 Mapa de componentes (arquivo:linha)](#d2-mapa-de-componentes-arquivolinha)
  - [D.3 CI AI Hub — divergência confirmada](#d3-ci-ai-hub-divergencia-confirmada)
  - [D.4 Épico e evidências](#d4-epico-e-evidencias)
- [E. Beads relevantes inventariados (leitura)](#e-beads-relevantes-inventariados-leitura)
- [F. Lacunas de evidência (a fechar na execução)](#f-lacunas-de-evidencia-a-fechar-na-execucao)

<!-- TOC END -->

Data: 2026-09-22 · Modo: somente-leitura (3 explorações + leitura inline) · Branch:
`0.12.0-dev` Plano associado:
`docs/plans/2026-09-22-pipeline-integracao-continua-plano.md` Escopo: recuperação de
integração FLEXT, contrato `.venv`, `make mod`, pipeline AI Hub (ccs/CLIProxy), CI.

> Evidência citada como `arquivo:linha`. Nada foi mutado durante a auditoria
> (explorações 100% leitura; Bash bloqueado no modo plano na sessão que produziu estes
> achados).

---

## A. Estado real da integração

### A.1 Workspaces existentes (nenhum clone criado)

| Workspace                                                                   | Branch @ HEAD                                                                                                                 | Estado                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/home/marlonsc/flext` (principal)                                          | `0.12.0-dev` @ `daa51e8822`                                                                                                   | **Avançou durante a auditoria** (`1e59a9d493` → `daa51e8822`, "update submodules to latest gitlinks", 2026-09-22 12:23:14 -03, reflog) — outro agente estava commitando na raiz. Sem merge aberto; 2 drifts de gitlink unstaged (`flext-core`, `flext-tests`); `flext-core` 4 dirty, `flext-tests` 2 dirty.                                       |
| `/home/marlonsc/flext-worktrees/rope-recovery-20260921` (**a recuperação**) | `recovery/rope-automation-20260921` @ `a17f35a1ed` "[WIP] preserve workspace generation and incremental integration contract" | **MERGE ABERTO**: `MERGE_HEAD=1e59a9d493` (a revisão de entrada), merge-base `9229858e21`. Status: 51 entradas = **31 UU (gitlinks)** + 15 M + 4 A. Conflito de documento restante: `docs/ways-of-working/worker-lane-contract.md` (ours 147 linhas, theirs 145). Cada membro tem checkout próprio no branch `recovery/rope-automation-20260921`. |
| `/home/marlonsc/flext-integration-20260922`                                 | `integration/beads-20260922` @ `fa9dd41cf7`                                                                                   | Stale: sem merge, 35 unstaged (31 gitlinks + 4 `__init__.py`), membros detached (ex. core @ `4534bb02e`). Não é o local da integração ativa.                                                                                                                                                                                                      |
| `~/.worktrees/flext-infra-fix-20260921`                                     | —                                                                                                                             | Prunable (diretório vazio).                                                                                                                                                                                                                                                                                                                       |
| `~/.worktrees/flext-infra-dedup-20260921`                                   | —                                                                                                                             | Worktree do módulo flext-infra, não do superprojeto.                                                                                                                                                                                                                                                                                              |

### A.2 Os 17 membros sem a revisão de entrada — verificado, exatamente 17

Critério: HEAD do branch recovery **não contém** o gitlink stage-3 registrado na raiz
`1e59a9d493`. Todos os 17 têm merge aberto; em 15 deles `MERGE_HEAD` = o SHA de entrada
exato; `flext-auth` e `flext-plugin` mesclam um commit de consolidação diferente (mesma
pendência):

`auth`, `dbt-ldap`, `dbt-ldif`, `dbt-oracle`, `dbt-oracle-wms`, `ldap`, `oracle-oic`,
`plugin`, `quality`, `tap-ldap`, `tap-ldif`, `tap-oracle`, `target-ldap`,
`target-oracle`, `target-oracle-oic`, `tests`, `web`.

Já contêm a revisão (sem merge aberto): `api`, `cli`, `core`, `db-oracle`, `grpc`,
`infra`, `ldif`, `meltano`, `observability`, `oracle-wms`, `tap-oracle-oic`,
`tap-oracle-wms`, `target-ldif`, `target-oracle-wms`.

### A.3 Publicação (main workspace x recovery)

- Na workspace **principal**, todos os 31 membros estão `0/0` vs `origin/0.12.0-dev`
  (publicados).
- Na **recuperação**, os 31 HEADs estão **à frente** de `origin/0.12.0-dev` (trabalho
  não publicado no dev). Apenas 5 branches recovery publicados no remote
  (`auth, dbt-oracle-wms, quality, target-ldap, target-oracle`).
- WIP não commitado na recuperação: `flext-tests` 78 arquivos, `flext-plugin` 17,
  `flext-core` 16, `flext-quality` 12, mais 13 membros com 2-5.
- PRs abertos (drafts recovery, por membro): api#110, core#489, infra#804/#801,
  dbt-ldap#107, dbt-oracle#107, dbt-oracle-wms#107, grpc#102, ldap#120, tap-ldap#105,
  tap-ldif#105, tap-oracle#100, target-ldif#106, target-oracle#111,
  target-oracle-oic#106, web#99 (+ não-drafts associados).

### A.4 WIP montado no merge da raiz (recuperação)

Além dos 31 UU e do documento: 15 `M` staged (`src/flext/*.py`, `custom.mk`,
`docs/plans/…`, `.agents/…/connections.py`) e 4 `A`
(`codemod/rules/refactor/{apply_renames.py,cacophony.csv, cli-prefixes.csv,infra-dedup.csv}`).
Preservar com commits de caminhos explícitos; nunca descartar.

---

## B. Contrato `.venv` — falha exata localizada

Dono canônico (header dos 32 Makefiles): `flext-infra/config/codegen.yaml` +
`flext-infra/src/flext_infra/templates/project/base/Makefile.j2` (regenerar via
`make gen`).

### B.1 A falha membro-como-standalone

- `flext-core/Makefile:40` — `MAKE_PROFILE := standalone` (projeção de
  `config:make_profile`; idem nos demais membros).
- `flext-core/Makefile:120-126` (idem raiz `Makefile:112-127`):
  `ifneq ($(filter standalone,$(MAKE_PROFILE))$(GEN_INIT_ONLY),)` →
  `REPOSITORY_ROOT := $(MAKEFILE_ROOT)`. **O perfil standalone atalha o probe real do
  superprojeto** (`git rev-parse --show-superproject-working-tree`, linha 124). Um
  membro (submódulo real, `.git` FILE apontando para `.git/modules/…`) com perfil
  projetado `standalone` resolve `RUNTIME_ROOT = <membro>` e
  `RUNTIME_VENV = <membro>/.venv` (`Makefile:161-165`). É exatamente o desvio relatado.
- Correção conforme contrato: a relação Git REAL decide — o probe do superprojeto sempre
  executa (exceto `GEN_INIT_ONLY`); perfil standalone aplica-se só quando o probe não
  acha superprojeto.

### B.2 Symlink de venv é tolerado (contrário ao contrato de rejeição)

- Raiz `Makefile:467-493` — `SETUP_ENVIRONMENT_RECIPE`: `[ -L "$(RUNTIME_VENV)" ]` é
  aceito como "borrowed environment" e **não provisiona** ("the borrower provisions
  nothing and the owner stays the only writer").
- Raiz `Makefile:500-503` — `BORROW_RUNTIME_VENV_RECIPE`: **cria**
  `ln -sfn "$(RUNTIME_VENV)" "$(PROJECT_VENV)"` ("Linking is provisioning").
- Raiz `Makefile:98` — `PROJECT_STATE_ROOT := $(PROJECT_ROOT)/../.flext-runtime/<nome>`
  (estado fora da árvore; padrão emprestado do bead `flext-bxo4y`).
- Contrário ao contrato novo: rejeitar `.venv` e `.venv/bin` simbólicos (inclusive
  quebrados) **antes de qualquer efeito**; o symlink normal do executável python para o
  interpretador gerenciado permanece. Precedente de rejeição `-L` a replicar: raiz
  `Makefile:253-285` (storage Mise — checa antes, cria, checa depois). `make gen`
  propaga o texto para os 32 Makefiles.

### B.3 Sanitização de ambiente herdado — já existe, lacuna confirmada

- Raiz `Makefile:188-202`:
  `override VIRTUAL_ENV/UV_PROJECT/UV_PROJECT_ENVIRONMENT/PATH` + export; PATH
  sanitizado remove o bin do caller.
- Raiz `Makefile:520`:
  `UV_RUN := env -u MYPYPATH -u VIRTUAL_ENV -u UV_PROJECT -u PROJECT_ROOT …`.
- `REPOSITORY_ROOT` de origem ambiente é sobrescrito pela derivação (`Makefile:112-127`,
  comentário explícito sobre `.envrc` vazado).
- Lacuna restante: variáveis/args Make não redirecionam **exceto** pelo atalho
  standalone (B.1).

### B.4 Atualização de Python

- `Makefile:482-484`: `uv venv` só cria quando falta `RUNTIME_PYTHON`; `Makefile:538`
  `UV_SYNC_FLAGS` (`--reinstall-package flext-infra` etc. — limitado ao runtime
  compartilhado). Com B.1 não corrigido, um membro-classificado-standalone escreveria
  `<membro>/.venv` (ambiente alheio).

### B.5 Consumidores e documentação

- Regeneração: os 32 Makefiles (raiz + 31 membros) via `make gen`; o mesmo gerador
  projeta consumidores externos (ai-hub) — beads `flext-zxwqa` (68 commits atrás),
  `flext-2nwjy`, `flext-ts0t9`, `flext-t9fay`.
- Documentação que ainda autoriza ambiente emprestado: os comentários dos próprios
  Makefiles (`Makefile:467-503`, replicados em 32 árvores) + varredura pendente em
  `docs/` e `flext-infra/docs/` na execução.

---

## C. `make mod` e orçamento de suíte

- Raiz `Makefile:734-740`: `mod` → `_activated-mod` → `_builtin_mod_apply`
  (`Makefile:1170-1171`) = `$(PROJECT_FLEXT_INFRA) refactor mod --apply` — **catálogo
  completo, sem seletor** ("selector-free"); o escopo é o cwd. Confirmado o risco de
  escopo relatado.
- Journal de geração: `flext-infra-codegen-transaction-journal.json.lock`
  (`Makefile:1126`).
- Checkpoint/estabilidade do mod: beads `flext-5fxu6.4.11` (mod aborta via unwrap),
  `flext-ronp2` (engine sed-by-list), `flext-k7vvp`, `flext-ujjrk`, `flext-t5uhw`,
  `flext-d7uhm` (64 findings detection-only), `flext-vjj1s.3`.
- Orçamento pytest (projeção): `PYTEST_PROCESS_TIMEOUT_SECONDS := 660`,
  `override PYTEST_RUN_TIMEOUT_SECONDS := 600` (`Makefile:57-63`).

---

## D. Pipeline AI Hub (ccs / CLIProxy / systemd)

### D.1 Workspaces

- `/home/marlonsc/ai-hub` — branch `dev`, **clean**, @ `80c15e20f` (sync com
  origin/dev).
- `/home/marlonsc/ccs` — `main` @ `7a5f9875` (8.9.0-fd.17); dirty leve
  (`.beads/config.yaml`, AGENTS/CLAUDE, backups mcp).
- `/home/marlonsc/cliproxy` — branch `fix/quota-suspension-recovery` @ `c64dcefc`
  ("accept an empty direct-models projection per ADR-0023"); **upstream `[gone]` — não
  publicado**.

### D.2 Mapa de componentes (arquivo:linha)

- **ccs**: flag `--api-key-only` existe só no ccs
  (`ccs/src/commands/tokens-command.ts:9,76,99`). Provisioning ai-hub:
  `ai-hub/config/tools.yaml:131-149`. **Zero referências em ai-hub** (rg
  `api-key-only|api_key_only|apiKeyOnly` → 0) — incremento 1 pendente (bead
  `aihub-6k1.29`).
- **Inventário vivo**: `ai-hub/config/models.yaml:8-13` (`CLIPROXY_BASE_ENDPOINT`,
  `/v0/management/model-inventory`, probe `/v1`); adapter
  `model_pipeline/inventory.py:58-90`.
- **Sondagem**: `models.yaml:143-160` (timeout 10s, max_tokens 2048, paralelismo 16,
  rotas anthropic/openai); runner `model_pipeline/probe.py`.
- **4 faixas**: `models.yaml:18-42` (balanced/fast/frontier/most-capable + mínimos de
  contexto/saída); contrato ADR-0023 (`docs/adr/0023-…four-independent-lanes.md`).
- **Ciclo 600 s**: `models.yaml:5-6`; daemon `model_pipeline_daemon.py:384`; READY só
  após publicação completa (`:206-216`, `:369-381`); fail-loud `restart: no` (`:273-275`
  systemctl).
- **Acoplamento descoberta×seleção** (incremento 2 pendente):
  `model_pipeline/cycle.py:70-119`, segunda leitura de inventário em `:92` (comentário
  CAS de fatos stale). Bead `aihub-6k1.28`.
- **Publicação**: snapshot `model_pipeline/snapshot.py:142-144` (target `ccs`,
  `CCS_MODEL_PIPELINE_ENDPOINT` = `127.0.0.1:3184/api/config/model-pipeline`,
  `services.yaml:114`); recibo `PublicationReceiptV3` (`state.py:121-142`); relatórios
  `ai-hub-models.md/.json` (`models.yaml:180-185`, `retained_snapshots: 2`); consumidor
  de aliases `model_pipeline/consumer.py:21,65-131` (falha alto em drift).
- **systemd/credenciais**: unidades em `config/services.yaml` (ccs-cliproxy `:48-61`,
  ccs-dashboard `:62-81`, ai-hub-model-pipeline `:82-117` notify); render
  `generate_systemd_units.py:225` com `LoadCredentialEncrypted=` `:245-249`; mecanismo
  existente de credenciais = **systemd-creds** (`host_runtime.yaml:61-62`; escrita
  `_host_runtime_parts/credentials.py:37` `_COMMAND="systemd-creds"`; leitura
  `_credential_source.py` — só `CREDENTIALS_DIRECTORY` em systemd ou env em foreground);
  daemon não imprime segredo (`model_pipeline_daemon.py:323-336`).

### D.3 CI AI Hub — divergência confirmada

- PR **#854** `[WIP] Keep installed runtime wheels reproducible and workspaces isolated`
  (`fix/editable-runtime-assets`, não-draft): `ci` FAILURE, `merge-guard` FAILURE,
  `release-plan` FAILURE (run 35744553820).
  - **WIP no commit**: guard rejeita subject `^\[WIP\]|^WIP|^wip` em dev ("WIP head
    cannot merge into dev: [WIP] preserve deterministic installed wheel identity…").
  - **WIP no título**: release-plan falhou com
    `PR_TITLE: [WIP] Restore editable setup without release artifacts`.
  - **3 projeções regeradas** (step "gen fixed point (blocking)", gerador republicou →
    árvore suja → exit 1): `scripts/__init__.py`,
    `src/ai_hub/services/_installed_runtime_parts/__init__.py`,
    `src/ai_hub/services/_session_learning/__init__.py`.
  - Local dev estava clean — a divergência existe **só no branch do PR**.
- dev tip com runs FAILURE: CI `35746445654`, Docs `35746445781`; PR #836 (dev→main) CI
  `35746454609`.
- Outros PRs: #856/#855 drafts, #842-#838 dependabot, #836 release.

### D.4 Épico e evidências

- `aihub-6k1` [EPIC P0 in_progress] "Model Pipeline v3 four lanes + CLIProxy execution
  resilience". Sequência registrada (nota 2026-09-22): **.30 setup → .29 credenciais →
  inventário vazio → .28 descoberta+probe desacoplada → ciclos cliente real (3 antes + 3
  depois do reinício)** — bate com a ordem do operador. `.30` IN_PROGRESS; `.29`/`.28`
  OPEN; `.25` (release/ativação) OPEN; bugs `.9` (serviço forking vs systemctl restart),
  `.18`, `.21`, `.23` OPEN.
- **Reconciliação aihub-6k1 ↔ flext-itpd1.3: NÃO registrada** (única nota cruzada é
  sobre flext-cpzjo, absorvida-em:None). Pendência da Fase 0.
- **Timeout da suíte**: `aihub-kvx0x.6.2` [BUG P0 in_progress] — "make test no worktree
  hook-convergence coleta 1903 testes, excede orçamento global 600 s, encerrado com
  raw_return_code=-15". Correlatos: `aihub-jlp8n.6`, `aihub-6k1.21`.
- **192 achados: SEM registro** em qualquer bead (busca "192" em flext e aihub → vazio).
  Análogos: `flext-67w2d` (272 findings), `flext-cpkk`, `flext-d7uhm` (64). Exige
  reprodução via `make check` na recuperação e registro em bead próprio.

---

## E. Beads relevantes inventariados (leitura)

- Coordenação: `flext-itpd1.3` (P0 in_progress; dependências `flext-itpd1`,
  `flext-yjjim`; 7 dependentes), `flext-itpd1.2`, `flext-itpd1.4`.
- Merges/PRs: `flext-whndf`, `flext-ap01g`, `flext-5anhp`, `flext-cpkk` (CI blocker),
  `flext-5j70p` (merge-guard WIP morto em pull_request).
- .venv: `flext-bxo4y` (padrão borrowed `.flext-runtime`), `flext-5fxu6.4.7` (Makefile
  gerado hardcode `.venv/bin/python`).
- make mod: `flext-5fxu6.4.11`, `flext-k7vvp`, `flext-ujjrk`, `flext-ronp2`,
  `flext-vjj1s.3`, `flext-t5uhw`, `flext-d7uhm`.
- ai-hub geração: `flext-zxwqa`, `flext-2nwjy`, `flext-ts0t9`, `flext-t9fay`.
- Orçamentos: `flext-ss5r9`, `flext-maygx`, `flext-oftik`, `flext-pffx4`, `flext-t9q8h`,
  `flext-yjjim`.
- P0 novos: `flext-dk13k` (fix-enforcement corrompe flext-core), `flext-2muq7` (script
  rogue `security_chain.sh` roda git proibido fleet-wide).
- Runbook canônico: `docs/ways-of-working/stabilization-checkpoint-0.12.md` (ciclo
  nativo, testmon, publicar membro antes do gitlink, merge `--no-ff`, evidência no bead,
  sem inflação de timeout).

## F. Lacunas de evidência (a fechar na execução)

1. **192 achados sem registro** — reproduzir `make check` na workspace de recuperação,
   registrar contagem e donos em bead novo (ligado a `flext-itpd1.3`).
2. **Marcador do cenário de substituição de ambiente não localizado** — localizar na
   execução com `rg -n 'skip|marker|deselect' … | rg -i 'env|venv|replace|swap'` em
   `flext-infra/tests` e `ai-hub/tests` + markers em pyproject; dar rota canônica
   executável.
3. **cliproxy upstream `[gone]`** — publicar branch antes de qualquer integração que o
   referencie.
4. **Live mutation na raiz** — reaveriguar o tip `daa51e8822` (e eventuais novos) antes
   de cada lote: `git -C /home/marlonsc/flext log --oneline -3` + status; incorporar com
   merge `--no-ff`.
