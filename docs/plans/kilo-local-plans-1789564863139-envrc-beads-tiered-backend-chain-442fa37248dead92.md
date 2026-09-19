# Plano — `.envrc` gerado: cadeia de backends beads (gascity → bd local → nenhum) +

direnv automático

## 0. Causa raiz (análise do ciclo completo)

**Como é feito hoje (verificado no código):**

- `.envrc` é gerado por `flext-infra codegen conform` a partir de
  `flext-infra/src/flext_infra/templates/project/base/.envrc.j2` + parcial
  `_envrc_beads.j2`.
- Owner Python: `flext_infra/workspace/environment.py` (`_sync_envrc`) e
  `workspace/environment_beads.py` (beads-workspace + `direnv allow` pós-sync).
- `direnv auto` já é automático: `codegen/_conform/execute.py:435` e
  `environment_beads.py:88` rodam `direnv allow <root>` em todo apply que publicou
  `.envrc` (make gen/setup re-sincronizam sem bloquear o shell).

**Defeitos de causa raiz (o que será corrigido):**

1. **Seletor binário, não tipado por tiers**: `_sync_envrc` renderiza o bloco beads
   somente quando `config/beads.yaml` existe **e** `gascity_enabled=True`; caso
   contrário entra num ramo `else` que só faz `unset`. Não existe projeto "beads local"
   nem projeto "sem beads" explicitamente renderizados — o contexto da template é
   `spec | None`, sem estado tipado.
2. **Resíduo duplicado em `.envrc.local`**: todo member repo carrega uma seção gerada
   obsoleta `# === SECTION: Gas City Beads activation (managed) ===` duplicando a
   ativação do bloco gerido do `.envrc` (com condições `jq` divergentes:
   `.dolt_database != ""` vs `length > 0` — prova de drift entre dois "donos"). Nenhum
   template atual de flext-infra emite esse arquivo: é resíduo de um dono antigo.
3. **Fatais silenciosos em tiragem errada**: um projeto sem `.beads/` herda variáveis de
   ambiente do shell pai (GT_ROOT, BEADS_DIR…) sem a cadeia terminal de `unset`.

**Semântica da cadeia (decisão de design, operador reiterou duas vezes):**

- "Se disponível" é definido por **nível declarado do projeto, sondado em runtime**:
  - **Tier `gascity`** (projeto declara participação: `config/beads.yaml` +
    `gascity_enabled=True`): ativa via `AGENTS_GAS_CITY_ROOT` + `dolt-state.json`
    saudável → `BEADS_DOLT_SERVER_*` da publicação da cidade. Cidade declarada e
    indisponível = **erro ruidoso** (nunca degrada para outro ledger: escrever beads
    numa base diferente com a primária fora do ar diverge histórico — proibido por raiz
    4).
  - **Tier `bd local`** (projeto com identidade beads sem cidade:
    `gascity_enabled=False`): `BEADS_DOLT_SERVER_*` desligados; `bd` assume servidor
    Dolt próprio via `.beads/config.yaml` `dolt.auto-start: true` (projeção já existente
    em `beads-config.yaml.j2`); `.envrc` valida identidade local e avisa se `bd` não
    está no PATH.
  - **Tier `none`** (nenhuma identidade beads): cadeia terminal de `unset` sempre
    renderizada.
- "Automaticamente para todos os projetos": `codegen conform` (via make gen por repo,
  inclusive worktrees) escolhe o tier pelo detector e renderiza o `.envrc`
  correspondente; `direnv allow` é curado pelo próprio apply.

## 1. Tarefas (flext-infra)

1. **Modelo tipado (SSOT)** — `_models/_config/beads.py`:
   - Novo `BeadsActivationBackend = Literal["gascity","local","none"]` (tipado, zero
     hardcode de caminho/valor).
   - Extender spec de render do envrc com `backend` (o `BeadsWorkspaceEnvironmentSpec`
     vira payload do nível gascity; nível local/none levam campos de paths/metadados que
     já existem).
2. **Detecção** — `workspace/environment.py`\_sync_envrc``:
   - Sem `config/beads.yaml` e sem `.beads/` → `backend=none` (renderiza igualmente o
     contexto tipado, termina em unset).
   - `config/beads.yaml` presente → backend = `gascity` se `workspace.gascity_enabled`,
     senão `local`.
3. **Templates** — `.envrc.j2` + `_envrc_beads.j2`:
   - Um bloco beads com três ramos triviais por `backend`; manter `watch_file`
     (metadata/dolt-state por tier), `unset` de vars de orquestração herdada,
     `log_msg`/`log_error` por disponibilidade; manter current fail-loud do gascity
     tier.
4. **Extermínio do resíduo `.envrc.local`**:
   - Conform normaliza `.envrc.local` dos membros removendo somente a seção gerada
     obsoleta ("Gas City Beads activation"), preservando overrides custom do operador
     (fix-forward; uses `_is_generated_environment_text` markers).
   - Enforcer: greps = 0 de `AGENTS_GAS_CITY_ROOT` fora do `.envrc` gerado (regra em
     rules/\*.yaml — linha de dados, não detector).
5. **Contratos e testes**:
   - `environment_contracts.py`: valida os três tiers (targets got accuracy: local/none
     tiers não exigem `dolt-state.json`).
   - Unit/fixture: `tests/utilities_fixture_workspace.py` já parametriza
     `gascity_enabled` — cobrir render gascity/local/none + idempotência (segunda
     `make gen` = no-op) + smoke runtime `direnv exec` por tier.

## 2. Validação

- `make gen` duas vezes → no-op exit 0 na 2ª (idempotência antes de tudo).
- `make check` (shellcheck do ENVRC via contratos estáticos + lint) e `make test` em
  flext-infra.
- Runtime por tier no fleet: `flext` (gascity), `.envrc` ativo com
  `AGENTS_GAS_CITY_ROOT` e cidade saudável; tier local e none simulado em
  fixture/worktree temporária com `direnv exec`.
- `direnv allow` automático verificado: alterar `.envrc` gerado e rodar `make gen` deve
  re-ativar sem prompt.
- Sinistro: cidade declarada parada no tier gascity → `.envrc` falha com mensagem
  precisa (jq error), nunca fallback silencioso.

## 3. Fora de escopo

- Mudanças no `bd`/`gascity` binários ou no hook do shell do direnv (~/.bashrc —
  máquina, não repositório).
- Reescrever `.envrc.gascity.j2`/`.envrc.beads-workspace.j2` além do necessário
  compartilhar a nova spec.
