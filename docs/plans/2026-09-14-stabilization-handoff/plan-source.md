# Documentation

<!-- TOC START -->

- [Atualização de autoridade (2026-09-14)](#atualizacao-de-autoridade-2026-09-14)
- [Contexto](#contexto)
- [Decisões do operador em vigor](#decisoes-do-operador-em-vigor)
  - [S2b — Extermínio GitHub/gh](#s2b-exterminio-githubgh)
- [Estado medido (14/09 ~16:20Z)](#estado-medido-1409-1620z)
- [Progresso 14/09 ~17:05Z (lane)](#progresso-1409-1705z-lane)
- [Progresso 14/09 ~17:45Z — PAUSA (handoff)](#progresso-1409-1745z-pausa-handoff)
- [Ciclo de cada fatia (sem exceção)](#ciclo-de-cada-fatia-sem-excecao)
- [Fatias](#fatias)
  - [S0 — Checkpoint do trabalho já feito](#s0-checkpoint-do-trabalho-ja-feito)
  - [S1 — Superfície Make sem modo](#s1-superficie-make-sem-modo)
  - [S2 — Extermínio ai-hub/Gas City](#s2-exterminio-ai-hubgas-city)
  - [S3 — AGENTS.md gerido com 4 regiões](#s3-agentsmd-gerido-com-4-regioes)
  - [S4 — Erros de execução do make check](#s4-erros-de-execucao-do-make-check)
  - [S5 — Restante do P-1c (bootstrap seguro)](#s5-restante-do-p-1c-bootstrap-seguro)
  - [S6 — Frota e flext-core](#s6-frota-e-flext-core)
  - [S7 — Superprojeto e docs](#s7-superprojeto-e-docs)
  - [S8 — Testes e pouso](#s8-testes-e-pouso)
- [Verificação final](#verificacao-final)

<!-- TOC END -->

## Atualização de autoridade (2026-09-14)

> Historical evidence only. This plan records an earlier execution context and its
> command examples are not current workspace guidance. Use the root `AGENTS.md` and
> `make help` for the active contract.

Cursor atual: `~/.claude/plans/happy-puzzling-flask-handoff-20260914-audit.md`, bead
`flext-itpd1.1`. O corpo abaixo preserva o plano histórico; números de PR, SHAs e
estados das 17:45 não são atuais. Pedido mais recente: produzir handoff crítico e
publicar a posição da lane como WIP, sem declarar estabilização feita.

Decisão nova 21:40 UTC: custom checks de flext-infra pertencem a outro agente. Não
desligar gates; separar responsabilidade/evidência. S4/custom enforcers não são trabalho
deste executor. Pouso completo exige incorporar a entrega do dono.

Reconciliações obrigatórias: S2b preserva CI/actions próprios, portanto seu grep zero
global não é aceite válido; avaliar fronteira por responsabilidade. S5 não autoriza
normalizar falhas/pular repositórios contra a regra estrita posterior. WIP é checkpoint,
não pouso; testes acompanham cada fatia que altera comportamento. Provas de ancestry
devem distinguir base absorvida de lane pousada. O handoff novo contém o estado fresco
dos 32, pendências e crítica dessas contradições.

---

# FLEXT 0.12.0 estável — execução contínua até o pouso (causa raiz, extermínio)

## Contexto

Operador (14/09): estabilizar 0.12.0 sem falhas, sem rollback/remendo/workaround,
exterminando over-engineering e bypass que duplica SSOT. Épico `flext-itpd1`, bead
`flext-itpd1.1` (tracker:
`export BEADS_DOLT_SERVER_HOST=127.0.0.1 BEADS_DOLT_SERVER_PORT=14499`
`BEADS_DOLT_SERVER_DATABASE=flext; bd …`). Lane: worktree
`.claude/worktrees/bugfix+stabilize-0.12.0`, branch `bugfix/stabilize-0.12.0` (super) e
flext-infra `bugfix/stabilize-0.12.0` (PR draft

# 727). Execução **contínua até o fim**: cada fatia termina com verbos canônicos + commit

`[WIP]` + push FF + nota na bead; só se para por bloqueio real.

## Decisões do operador em vigor

1. **flext não conhece nem usa ai-hub nem Gas City** (nenhum nome, chave, tool,
   diretório, doc, teste).
2. **Beads = identidade apenas.** Gerado: `issue_prefix` (`.beads/config.yaml`),
   `backend/database/ dolt_database/project_id` (`.beads/metadata.json`),
   `config/beads.yaml` (workspace/database/prefix derivados do repo), instalação do `bd`
   via mise, seções de gitignore do `.beads`, `bd hooks install`. Servidor, host, porta,
   modo, auto-start, export, backup, tipos custom, rotas: **só do ambiente**.
3. **Sem modo não-apply em nenhum verbo Make** (`setup gen fix fmt check test …`):
   `APPLY`/`CHECK_ONLY`/ `check_mode` exterminados. O CLI Python do flext-infra mantém
   `--dry-run`/`--mode check` para uso direto e CI.
4. **Makefile não valida parâmetros** (nem `APPLY`, nem `WHAT`, nem verbos, nem
   `INDEX`): valores errados falham onde o verbo os usa. Variável não consumida é
   ignorada.
5. **AGENTS.md gerido por `make gen`** com 4 regiões: (a) esqueleto geral gerido; (b)
   customização externa, preservada verbatim; (c) projetos flext (só na raiz do
   workspace, derivado do SSOT); (d) totalmente custom, preservada, com aviso aos
   agentes de que mudanças ali valem só para este repo.
6. `make fix`/`make fmt` aplicam e reportam achados sem falhar; `make check` aplica e
   **falha** com achados remanescentes. setup/gen são bootstraps seguros: erro de
   config/consistência → WARNING, erro essencial → falha. Gerador = flext-infra do venv;
   sem validação de gitlink/tip. Bypass que duplica SSOT → exterminar e religar
   consumidores sem perguntar caso a caso. Retirada de PR/branch/worktree autorizada
   após prova.
7. Budget SSOT exterminado; sem gate novo de gitlink; desempenho = só remoções;
   `~/wip-hier.sh` corrigido.
8. **Tudo de gh/GitHub sai de flext-infra e do superprojeto flext** (projeções
   `.github/**`, uso do CLI `gh` e da API GitHub, variáveis `GITHUB_*`, pins de actions,
   dependabot, copilot, PR/release em GitHub): o dono passa a ser o ai-hub. Detalhe e
   fronteira (URL de remote git ≠ gh) na fatia S2b.

### S2b — Extermínio GitHub/gh

- Regra: flext-infra deixa de gerar/ler/validar qualquer superfície GitHub; consumidores
  religados ao que é git puro; o que o ai-hub precisa assumir entra no pacote ai-hub
  (S7).
- Ordem (inventário 14/09):
  1. Mortos: `_models/settings.py:51-72` campos `GITHUB_*` +
     `_constants/base.py:394-399`; protocolo `GithubService` (`_protocols/base.py:675`);
     template órfão `.github/scripts/flext-law-loop.sh.j2` + cópia raiz.
  2. `.github/**` necessario aos projetos flext e gerado pelo SSOT do flext-infra FICA
     (operador 14/09): workflows CI/ci-matrix/docs/release, dependabot, `ci-template`,
     scripts de hooks/policy, prompts, pins de actions e seus modelos/validadores/testes
     continuam no flext-infra. Arquivos custom em `.github/` tambem ficam. Sai apenas o
     que e projecao de runtime geravel pelo ai-hub
     (`.github/{agents,hooks,skills,instructions}/`, hooks `aihub-hooks/_`): flext-infra
     nao gera/le/valida (ex.: exclude `GITHUB_AGENT_PROJECTION_DIRS` e `tooling.yaml`
     `.github/hooks` "owned by ai-hub" saem) e o pacote ai-hub assume. Orfao
     `flext-law-loop.sh.j2` sem dono SSOT: remover junto com a copia raiz apos provar
     zero consumidor. Fronteira sempre por `.gitignore` gerado (operador 14/09): custom
     em `.github/` nunca e apagado; os caminhos de runtime geraveis externamente entram
     como padroes genericos de ignore (sem nomear o gerador), e o que ja esta rastreado
     sai do indice com `git rm --cached` (arquivo local preservado).
  3. Release sem GitHub: `_orchestrator_dispatch._publish_release_branch` (`gh pr`),
     `_orchestrator_publish._github_release` (`gh release`), `GH`,
     `PULL_REQUEST_MERGE_SUBJECT_RE`/`pr_title`/`PR_TITLE`, `INDEX=N` "GitHub assets";
     release termina em tag + recibo + publicação de índice; testes de release
     religados.
  4. Docs: `_utilities/_docs_github_links.py`, `DocsGithubRepoSpec`,
     `GITHUB_REPO_URL/NAME`, `stale_github_organizations`/`github_repos`, ramos de
     `docs_render.py`/`docs_contract.py`; excludes `GITHUB_AGENT_PROJECTION_DIRS` no
     gate markdown.
  5. `GITHUB_PATH` em `tool_bootstrap_recipe.j2:173-176`; tokens
     `GITHUB_TOKEN/GH_TOKEN/MISE_GITHUB_*` passam a vir só do ambiente (sem nomear
     GitHub no código).
  6. Superprojeto: `scripts/workspace/dependabot_merge.py` e
     `.github/workflows/conflict-marker-check.yml` saem (dono ai-hub); docs vivas sem
     GitHub.
- Mantidos (git puro, não gh): URLs de providers/`.gitmodules`/remotes; backends
  `github:` do mise continuam enquanto os binários só existirem como release (decisão
  registrada no pacote ai-hub).
- Prova: grep `\.github/|gh pr|gh release|GITHUB_|github_actions|GithubWorkflow` = 0 em
  flext-infra vivos; `make setup/gen/check/test` e `release plan` executam sem `gh`.

## Estado medido (14/09 ~16:20Z)

- flext-infra commits na lane: `265346e77` (budget), `b7385f600` (fix/fmt
  apply-and-report, fix/apply), `bf1e1e532` (orquestrador roda tudo, `FAIL_FAST` fora,
  gates sem `FORCE_COLOR`). Super: `8090291786`.
- Verbos: setup 0; gen ×2 0 (ponto fixo); fix 0 (WARN restantes); fmt 0 (32/32);
  `make check` #2 **rodou 32/32 até o fim**, exit 1, 32 FAIL por achados + 2 erros de
  execução:
  - flext-infra `runtime_census`:
    `ModuleNotFoundError flext_infra._utilities._gen_requirements` (lazy `__init__`
    ainda aponta o módulo removido pelo A5; `make gen` regenera). Revela também que
    exceção de um gate derruba os demais gates do projeto.
  - flext-tests `runtime_census`: `TypeError str | ModelMetaclass` em
    `flext-tests/src/flext_tests/_typings/base.py:61` (`"TestobjectAtom"` entre aspas
    dentro de alias PEP 695).
- **Não commitado em flext-infra** (validado por
  `flext-infra codegen conform --root flext-infra --what makefile --mode check`: plan
  OK, só drift esperado do Makefile):
  - P-1c templates: WARN do mise não fatal; `uv` ausente no parse = `$(warning)`; setup
    faz `direnv allow` nos membros.
  - A5: `.gen` exterminado (yaml, enforcement, 9 specs, loader, `resolve_gen_path`,
    constantes); políticas `delegated/manual/create-only` exterminadas (vocabulário
    `full|merge`); exceção `.env.example` do release religada a
    `codegen.templates.entries`.
  - A4: ancestralidade de branch exterminada ponta a ponta (validação, plano, modelos,
    campos baseline/technical/governed, `scaffolded_repository`, chaves yaml,
    `GITHUB_SHA`/`MERGE_HEAD`, fixture, 4 testes).
- P0.2 adjudicado: retirar #226/#235/#231/`wip/duplicate/*`; #239 adotado; de #225
  adotar só `[project.scripts]` raiz → `flext.workspace:FlextRootWorkspace.main`,
  `flext.dev:FlextRootDev.main`, `flext.docs:FlextRootDocs.main` (hoje apontam `:main`
  inexistente).
- P0.4: duplicatas fechadas (`13axf`,`dj2f6`→`bdmdg`; `t4hyd`→`6x6jr`; `didi7`→`b5dkz`).
- `~/wip-hier.sh`: `bash -n` OK; shellcheck NOT EXECUTED (sem binário; instalação é do
  ambiente do operador).

## Progresso 14/09 ~17:05Z (lane)

- S0+S1 editados e validados com exportado (condição do shell do operador): `make gen`
  exit 0 (310 arquivos), 2ª `make gen` exit 0 com `mode=apply` e 0 publicados (ponto
  fixo); `make setup` exit 0; `make fix` 32/32 passed (WARN só em flext-infra,
  flext-target-ldap, flext-tests); `make fmt` 32/32 passed; `make check` em execução.
  Makefile raiz sem `APPLY|CHECK_ONLY|PUBLIC_INPUTS|CHECK_CAPABLE|_builtin_gen_check`.
- Docs-fonte: `make gen` falhou uma vez por `make conform` em
  `docs/guides/configuration.md` (contrato de verbos do gerador de docs funcionando);
  guias, standards, ADRs, AGENTS.md e skill corrigidos.
- S4 flext-tests: alias `NormalizationInput` corrigido (aspas + membro `RootModel`
  redundante); `__value__` avalia sem erro.
- Membros: todos em `origin/0.12.0-dev` exato (0/0), 14–22 arquivos regenerados, 0
  untracked, `0.12.0-dev` sem proteção. Operador (14/09): propagar sempre à integração e
  a `~/flext`; merges autorizados.
- Pouso após `make check`: commit flext-infra (S0+S1 juntos: hunks compartilhados) →
  push → PR #727 Ready → merge commit; membros por `land_members.sh` (branch, commit sem
  `[WIP]`, PR, merge commit); super adota `c2dba374e0` por merge `--no-ff`, re-rola
  gitlinks, merge commit; `~/flext` sai do isolamento de worktree (ExitWorktree) e faz
  fetch/merge ff das integrações + `make gen`, adotando WIP local por fix-forward.

## Progresso 14/09 ~17:45Z — PAUSA (handoff)

Retomada: `~/.claude/plans/happy-puzzling-flask-handoff.md` (tabela de estado + próximos
passos em ordem).

- Pousado em `0.12.0-dev`: flext-infra #727 merge `b13793fb1`; 30 membros (PRs de
  projeções regeneradas, SHAs na nota de `flext-itpd1.1`); membros da lane em
  `0.12.0-dev` local nesses SHAs.
- Super: merge `-s ours` de `c2dba374e0` (uv.lock/`--refresh` já no dono flext-infra;
  excludes aihub-hooks rejeitados) + `5806a67377` (31 gitlinks, `[project.scripts]` →
  `FlextRoot*.main`); PR #240 **aberto, sem merge**.
- flext-infra: `[WIP] 95baa0c0d` S2 só templates (push feito, sem PR, sem
  regenerar/validar).
- `make check` parado por ordem em 9/32: 0 tracebacks; PASS flext-api; FAIL por achados
  raiz, auth, cli, core (619), db-oracle, dbt-ldap, dbt-ldif, dbt-oracle. Execução
  completa 32/32 ainda devida.
- Beads fechadas: `flext-xeg9x`, `flext-5mgye` (obsoletas por S1).
- Pendente: merge #240 → propagar `~/flext` → S2 2ª metade (modelos/python/testes) → S2b
  → S3 → S4 → S5 → S6 → S7 → S8.

## Ciclo de cada fatia (sem exceção)

edição no dono → `make gen` ×2 (2ª sem efeito) → `make setup` → `make fix` → `make fmt`
→ `make check` (tem de **executar até o fim**; achados não bloqueiam a fatia, erro de
execução bloqueia) → grep de resíduo zero da fatia → commit `[WIP]` escopado
(`git -C flext-infra commit -- <paths>`) → push FF → atualizar PR #727 e bead.
`make test` entra na fatia S8.

## Fatias

### S0 — Checkpoint do trabalho já feito

1. `make gen` ×2 (regenera lazy `__init__` do `_utilities`, projeta templates P-1c).
2. Ciclo completo; 3 commits separados: (a) templates P-1c, (b) A5 `.gen`+políticas, (c)
   A4 ancestralidade.

### S1 — Superfície Make sem modo

Dono: `flext-infra/src/flext_infra/templates/project/base/Makefile.j2`,
`config/codegen.yaml`, `_models/config.py`, `promoted/`, testes.

- `Makefile.j2`: remover `PUBLIC_INPUTS`/`COMMAND_LINE_INPUTS`/`UNKNOWN_INPUTS` e o
  `$(error)` (66-70); validação de `INDEX` (74-77); `APPLY`/`CHECK_ONLY` (78-84,
  comentário 57-61); `CHECK_CAPABLE_VERBS` e guarda (159-172); `MAKE_PROFILE` inválido
  (204-205); linha de help do APPLY (~462); alvos workspace
  `_builtin_{fmt,fix,fix_enforcement}_check` com `$(error)` (579-596); roteamento
  condicional (762-793) vira incondicional: `deps→_builtin_deps_upgrade`,
  `fmt→_builtin_fmt_all`, `fix→_builtin_fix_all`,
  `fix-enforcement→_builtin_fix_enforcement`, `gen→_builtin_gen_all`,
  `mod→_builtin_mod_apply`; docs sempre `--apply` nas `mutable_actions`; apagar irmãos
  `_check` inalcançáveis (grep de chamadores antes).
  `SETUP_BOOTSTRAP_ONLY`/`GEN_INIT_ONLY`/`REPOSITORY_ROOT`: manter só a derivação
  interna, sem guarda de origem. Guardas essenciais ficam (executável make, `HOME`,
  cygpath, aviso do uv).
- `check` aplica: recipe de check roda gates com `--apply` e falha com achados; fix/fmt
  aplicam e só avisam. Implementar no dono `check/workspace_check.py` trocando o ramo
  atual (`apply and not check_only`) por um parâmetro explícito do CLI usado só pelas
  recipes de fix/fmt (ex.: `--report-findings`), sem knob no Make.
- Verbo `conform` (só-leitura) sai de `make.verbs`; `ci.yml.j2:97` passa a chamar
  `flext-infra codegen conform --mode check` pelo interpretador do venv (CLI mantém
  modos).
- `MakeVerbSpec.check_mode` + 7 linhas `check_mode: true` + comentários option A/A'
  (`codegen.yaml:333-335,981`, `_models/config.py:909-913`) removidos.
- Script dispatch (R28): remover `promoted/base.py:27-33` `PROMOTED_APPLY_VALUES`,
  `promoted/invocation.py:49-93` (`validate_command_contract` de APPLY,
  `validate_apply_env`), `promoted/dispatcher.py:83-115` ramo dry-run, strings
  `promoted/rendering.py:54,124,156,182`, `_utilities/docs_render.py:249`; teste
  `tests/unit/promoted/test_apply_contract.py` apagado.
- Anti-regressão: `_constants/docs.py:133` `DOCS_APPLY_RE` → `\bAPPLY=` (rejeita
  qualquer valor); `tests/unit/docs/auditor_command_contract_tests.py` estendido.
- Testes Make: `tests/unit/codegen/test_codegen_make_environment.py` (638-690, 845-872 e
  comentários) reescritos para o contrato novo (ignorado, verbo aplica);
  `tests/constants.py:56` `APPLY`/`CHECK_ONLY` saem.
- Docs com `APPLY=`: `AGENTS.md:111`, `.agents/skills/flext-law/SKILL.md:98`,
  `docs/GOVERNANCE.md:95`, `docs/guides/make-commands.md:42`,
  `docs/guides/using-flext-tests.md:120`, `docs/architecture/arc42/12-glossary.md:68`,
  `docs/standards/consumption-law.md:123`, `docs/standards/development.md:77`, ADR-004
  (65,86,92), ADR-010 (81),
  `flext-infra/docs/guides/{make-commands, using-flext-tests}.md`,
  `flext-infra/docs/index.md:49`. `flext-law-loop.sh.j2` `APPLY` local → `DO_APPLY`.
- Prova: `make gen` aplica; `make check WHAT=xyz` falha no uso; grep
  `APPLY|CHECK_ONLY|check_mode` = 0 em templates/config/src/tests/docs vivos; 32
  Makefiles regenerados.

### S2 — Extermínio ai-hub/Gas City

- Mapa atual (14/09 ~17:10Z, pós S1): fonte `_models/config.py` (238
  GithubWorkflowRenderSpec.gascity_enabled, 413 EnvrcRenderSpec.gascity, 1481-1492
  custom_issue_types+validador, 1532 target.gascity_enabled, 1672-1715
  BeadsConfigRenderSpec endpoint/gascity/types/dolt, 2314 WorkspaceBeadsServerSpec, 2361
  beads_enabled, 2370/2515 gascity_enabled, 2422-2431
  ledger_id/ledger_prefix/beads_server, 3268+3287 BeadsWorkspaceEnvironmentSpec, 52 e
  3519 alias BeadsEndpointSpec); `_models/mise_toolchain.py` (305 gascity, 400
  BeadsEndpointSpec, 416-471 endpoint/ types/dolt/export/backup/flush + validador);
  `_protocols/base.py` (123-133, 235); `codegen/conform.py` (493, 609 rotas beads;
  619-705
  `_conform_workspace_beads_routes`/`_beads_route_state`/`_is_dry_run_config_backup`;
  809, 2027-2061, 2096); `workspace/detector.py` (33 `_composed_beads_identity_error`,
  261-276 ledger, 289, 462, 552, 587-592, 639); `workspace/environment_beads.py` +
  `environment.py:60,71` + `services/cli_routes_workspace.py:11` + `api.py:11` + lazy
  exports `__init__.py`/`workspace/__init__.py`; templates `.envrc.j2`,
  `.envrc.beads-workspace.j2`, `beads-config.yaml.j2`, `beads-metadata.json.j2`,
  `.mise.toml.j2`, `config/beads.yaml.j2`, `config/workspace.yaml.j2:113`,
  `.github/scripts/check-beads-policy.sh.j2`. Testes:
  `tests/utilities_fixture_workspace.py`,
  `tests/unit/codegen/test_codegen_beads_projection.py`,
  `tests/unit/workspace/{test_beads_environment_sync, worktree_fixture,`
  `test_workspace_member_ledger_identity, test_repository_local_topology}.py`; config
  `config/codegen.yaml`.
- Chave-mestra: `gascity_enabled` fora de `WorkspaceSpec`, `RepositoryConformTarget`,
  `RepositoryPolicyOverlaySpec`, render specs (`GithubWorkflowRenderSpec`,
  `EnvrcRenderSpec.gascity`, `BeadsConfigRenderSpec`, `MiseTomlRenderSpec`), protocolos
  `_protocols/base.py`, `workspace/detector.py:289, 587-592,639`,
  `codegen/conform.py:811,2029-2098`.
- Toolchain: `ToolchainSpec.gascity`, bloco `gascity:` e `protected_mise_tools` gascity
  (`codegen.yaml:77-97`), bloco gc em `.mise.toml.j2`.
- Beads: `BeadsToolSpec.endpoint_origin/endpoint_status/required_custom_types/`
  `dolt_mode/export_auto/backup_enabled/dolt_disable_event_flush` e yaml
  `codegen.yaml:115-143`; `BeadsEndpointSpec`;
  `WorkspaceBeadsServerSpec`/`beads_server`; `ledger_id/ledger_prefix` + cross-check
  `detector.py:261-278`; `beads_enabled`;
  `BeadsProjectSpec.version/custom_issue_types` + validador;
  `BeadsWorkspaceEnvironmentSpec`; `workspace/environment_beads.py` mixin de sync +
  `.envrc.beads-workspace.j2` + rota CLI; `direnv allow` Python duplicado removido (dono
  único = recipe de setup); `_conform_workspace_beads_routes`/`_beads_route_state`/
  `_is_dry_run_config_backup` (`conform.py:621-714`) e checagens de symlink/rota
  `detector.py:33-66,461-560`; `.github/scripts/check-beads-policy.sh.j2` + entradas
  managed/template (sem invocador). Templates: `beads-config.yaml.j2` só `issue_prefix`;
  `beads-metadata.json.j2` sem `dolt_mode`; `.envrc.j2:83-111` sem bloco beads/gascity e
  terminando só com `source_env_if_exists .envrc.local` (`.envrc.local` rastreado,
  criado uma única vez quando ausente, nunca sobrescrito — decisão do operador 14/09 via
  sessão ai-hub; o ai-hub injeta o ambiente dele por biblioteca direnv própria fora do
  flext); `config/beads.yaml.j2` sem `version/custom_issue_types`;
  `workspace.yaml.j2:113` sem `beads_enabled`. `config/beads.yaml` ausente → identidade
  derivada do repo (padrão `project_new.py:127-132`) com WARNING, nunca aborto; nome do
  workspace derivado do repositório, não do arquivo beads (`detector.py:590`); marcador
  de "repo governado" (`detector.py:665`, `api.py:50`) passa ao manifesto.
- Resíduo ai-hub em flext-infra: `codegen.yaml:449-451` (repo ai-hub), gitignore
  `codegen.yaml:1440-1505` (seções gc/aihub/`.gc/`/`*aihub-prior*`),
  `config/infra.yaml:13` prefixo `ai-hub`, `codegen-overrides.yaml:93`,
  `tooling.yaml:77-81` exclude `.github/hooks` "owned by ai-hub",
  `_constants/workspace.py:90` `.ai-hub`, `_constants/source_code.py:77-83`
  `GITHUB_AGENT_PROJECTION_DIRS`, `_constants/check.py:134` `/ai_hub_hook_client/`,
  `_constants/base.py:274`, `validate/tier_whitelist.py:90` `.gc`, regras codemod
  `ban-ai-hub-*` + testes/snapshots, textos em `ci.yml.j2:107`,
  `install-git-hooks.sh.j2:10`, `flext-aggressive-scale-refactor.prompt.md.j2:24-29`,
  `copilot-instructions.md.j2` (aponta só o AGENTS.md do repo), comentários citados no
  inventário; testes (`test_codegen_beads_projection.py`,
  `utilities_fixture_workspace.py:108-154`, `test_beads_environment_sync.py`,
  `test_codegen_artifact_ssot.py:106-107`, `test_mod_circuit.py:21`,
  `test_codegen_conform.py` comentários, `layout_tests.py`,
  `lazy_init_helpers_tests.py`, `extended_gate_bandit_markdown_tests.py:197-200`,
  `governance_authority_tests.py:82-83`,
  `test_infra_refactor_namespace_enforcer.py:480-488`,
  `test_infra_git_identity_submodules.py:230`) religados para fixtures neutras.
- Prova: grep case-insensitive
  `ai-hub|ai_hub|aihub|agentsctl|gascity|gas city|gas_city|\.gc/|dolt-state|`
  `inherited_city|AGENTS_GAS_CITY_ROOT` = 0 em flext-infra
  src/config/templates/tests/docs vivos e nas projeções; `bd list` funciona com o
  ambiente do operador após `make gen` (sem export manual além do ambiente dele).

### S3 — AGENTS.md gerido com 4 regiões

- Novo managed file `AGENTS.md` (owner `agents`, policy `merge`) em `codegen.yaml`
  `managed_files` + `templates.entries` (`base/AGENTS.md.j2`), dono de merge no ponto de
  despacho `codegen/conform.py:1039-1060` (mesmo padrão do owner `vscode`); nenhum
  parser externo.
- Marcadores genéricos HTML
  (`<!-- flext:region managed|external|projects|local begin/end -->`). `managed` =
  esqueleto (ponteiro de lei FLEXT branch-matched, verbos canônicos, estrutura);
  `external` = preservada verbatim; `projects` = só `MakeProfile.WORKSPACE`, renderizada
  de `WorkspaceSpec.subprojects` / catálogo
  (`_utilities/_docs_generate_root.py:81-107`); `local` = preservada, cabeçalho
  "mudanças aqui valem só para este repositório".
- Migração determinística do conteúdo atual (32 AGENTS.md): pares de comentário
  `BEGIN/END` de terceiros → `external` intactos; demais seções manuscritas → `local`;
  nada descartado. Marcador ausente/duplicado → WARNING e reparo preservando todo
  conteúdo em ordem. `CLAUDE.md` não é tocado.
- Testes funcionais em `tmp_path`: preservação byte a byte de `external`/`local`,
  `projects` só na raiz, ponto fixo na 2ª geração.

### S4 — Erros de execução do `make check`

- flext-tests `_typings/base.py:61`: remover as aspas de `TestobjectAtom` (lane
  flext-tests).
- `check/workspace_check_gates.py:298-339`: exceção de um gate vira falha daquele gate
  com traceback completo no relatório (exit ≠0), os demais gates do projeto concluem.
- Reexecutar `make check` 32/32: zero tracebacks.

### S5 — Restante do P-1c (bootstrap seguro)

- A1 validadores cruzados no import (`_models/config.py` 141-148 já removido; demais
  232-256, 548-563, 596-603, 771-789, 858-861, 1022-1087): sem função → exterminar; com
  função → WARNING; nenhum import aborta. Inclui `gates_skip`/`project_check_gates`
  mortos + validadores.
- A2: gen roda só com o flext-infra do venv; resolução de uv só nos verbos que usam uv.
- A11: `submodule_setup_recipe.j2:74-129` validações de gitlink/branch exterminadas;
  `uv sync --refresh` (`Makefile.j2:341`) sem `--refresh`.
- C: repo com defeito de consistência → WARNING e pulado com estado intacto; demais
  publicam; resumo lista pulados.
- `_builtin-audit` sem `codegen conform` duplicado; split CI `check`+`check complement`
  vira uma invocação.
- R6 `[tool.flext.docs].package_name` exterminado (template `pyproject.toml.j2:113`,
  `deps/modernizer.py:142`, leitor) + `exclude_docs` preservado; R10 ignores ancorados
  em `codegen-overrides.yaml:60-82`; R7 `{#- -#}`.
- Prova: checkout tmp com config quebrada → setup/gen concluem com WARNINGs e estado
  coeso; 2ª execução sem diff.

### S6 — Frota e flext-core

- flext-core: remover `budget` de `_models/project_metadata.py:88`; `_settings.py:165`
  mapeamento `AI_HUB_`; docstrings ai-hub (`_settings.py:369`, `_config.py:209`,
  `_utilities/settings.py:17-21`).
- Membros: `make gen` na raiz projeta
  Makefile/CI/pyproject/.mise/.beads/.envrc/AGENTS.md; `git rm uv.lock` nos 12 que
  rastreiam; `base.mk` legado órfão em flext-core/flext-cli/flext-api apagado após
  provar que nenhum Makefile o inclui; flext-cli: 69 projeções com marcadores de
  conflito entram como conteúdo externo — remover do versionamento as que não pertencem
  ao repo (não geradas pelo flext-infra) após adjudicação por arquivo.
- Uma lane `bugfix/stabilize-0.12.0` por membro com mudança; PR draft; merge commit após
  CI verde.

### S7 — Superprojeto e docs

- `pyproject.toml [project.scripts]` corrigido; `scripts/workspace/dependabot_merge.py`
  safe-delete (CodeQL #6); `exclude_docs` restaurado do histórico; gitlinks → merge
  SHAs.
- Docs vivas sem ai-hub/Gas City: apagar `docs/AI_HUB_CONSUMER.md`; reescrever
  `docs/GOVERNANCE.md:47-48,72`, ADR-010 (187-189,236), ADR-015 (54,96),
  `docs/standards/consumption-law.md:103-111,122,148`, `docs/index.md:37-39`,
  `docs/guides/skill-automation-pattern.md:20`, glossário,
  `settings-config-canonical-pattern.md:13`, `config-ssot-migration-plan.md:116`,
  `flext-infra/docs/guides/skill-automation-pattern.md:25`. Históricos (`docs/plans/`,
  triagens) ficam como evidência.
- Pacote ai-hub (`~/.claude/plans/ai-hub-envrc-agent-hooks.md`) atualizado e reenviado
  ao operador: flext não exporta mais endpoint Dolt nem conhece gc (ambiente fornece
  `BEADS_DOLT_SERVER_*`); projeções no AGENTS.md escrevem só dentro da região
  `external`; saídas de runtime não podem cair não rastreadas nos repos flext; 3b
  (flext-cli) mantido.

### S8 — Testes e pouso

- `make test` na lane (flext-infra primeiro, depois frota); correção no dono de cada
  falha.
- PR #727 → Ready → CI verde → merge commit em `0.12.0-dev`; PRs dos membros idem; super
  re-rola gitlinks, CI verde, merge commit; `make gen` na checkout do operador sem erro.
- Retirada com prova (`git merge-base --is-ancestor` contra base recém-buscada): #226,
  #235, #231, #239, #225, `wip/duplicate/*`, worktrees/branches supersedidas; PRs
  fechados com comentário de SHAs.
- Beads: `flext-itpd1.1` e filhas fechadas com 4 fontes; obsoletas restantes (`kmtt3`,
  `xtzkz`, `9oljq`, `a0edu`, `09686`, `1wjg1.10`) com evidência; `bd lint` 0 nas
  tocadas.
- `~/wip-hier.sh`: shellcheck quando o binário existir no ambiente; senão NOT EXECUTED
  registrado.

## Verificação final

- Root e membros: `make gen` ×2 sem diff; `make setup`, `make fix`, `make fmt`,
  `make check`, `make test` executam até o fim; `make check`/`make test` exit 0 no
  estado pousado.
- Greps = 0 nos vivos: `APPLY|CHECK_ONLY|check_mode`,
  `ai-hub|aihub|agentsctl|gascity|\.gc/|AGENTS_GAS_CITY_ROOT`,
  `project.budget|BudgetGate|gate_budgets|check complement`,
  `codegen.gen|branch_ancestry|GITHUB_SHA`.
- `.beads/config.yaml` só `issue_prefix`; `bd list` OK com o ambiente do operador.
- AGENTS.md dos 32 repos com as 4 regiões, conteúdo pré-existente preservado, ponto
  fixo.
- CI `0.12.0-dev` verde nos 32 heads; `--is-ancestor` = 0; gitlinks ≡ `.gitmodules`;
  nenhum `uv.lock` em membros; CodeQL abertos = 0.
