# Handoff — Fix-forward frota flext (0.12.0-dev) + migração detector.py para GitPython

## Objetivo original

`make setup` falhava porque `flext-infra` estava em `feature/ban-gitpython-imports` em vez de `0.12.0-dev`. O usuário pediu fix-forward absoluto: sem stash, sem rollback, merge-no-ff, absorver todo fallout em toda a frota.

Depois o usuário pediu para migrar o `detector.py` para usar GitPython (`_git/` owner) em vez de subprocess git manual — a causa raiz do pre-push hook falhar com "workspace member gitlink is missing: flext-infra" quando `GIT_DIR` está setado pelo pre-commit framework.

## O que já foi feito (completo)

### 1. flext-infra — branch + commit + push parcial
- `flext-infra` está em `0.12.0-dev` (checkout feito)
- 5 commits locais não-pushed:
  - `735a20c1` chore: codegen conform — pyproject drift
  - `1f4cd683` chore: codegen conform — add mod verb + update ast-grep rules
  - `ed81b480` Merge branch 'feature/ban-gitpython-imports' into 0.12.0-dev
  - `0a4b0d04` feat(infra): fix-forward workspace git identity + config model + worktree transaction
  - `9243f9c3` fix(codemod): allow GitPython imports inside _git/ from workspace scope
- Push **bloqueado**: pre-push hook roda `make gen APPLY=Y` que falha com "workspace member gitlink is missing: flext-infra" porque `GIT_DIR` está setado pelo pre-commit

### 2. Superprojeto — gitlink atualizado
- Gitlink do `flext-infra` atualizado para `ed81b480` e pushed (`3c612c22a`)
- Isso desbloqueia o push do flext-infra **mas** o pre-push hook ainda falha por causa do detector.py

### 3. Migração _git/ owner para GitPython (parcial — código modificado mas não commitado)

**Arquivos modificados em flext-infra (dirty, não commitado):**

- `src/flext_infra/_utilities/_git/repo.py` — criada classe `FlextInfraUtilitiesGitRepo` com métodos `_repo()`, `_open_repo()`, `_refresh_binary()` (encapsulando as funções soltas `git_repo`, `git_open_repo`, `git_refresh_binary`)
- `src/flext_infra/_utilities/_git/semantic.py` — herda de `FlextInfraUtilitiesGitRepo` + `FlextInfraUtilitiesGitWorktreeMixin` (MRO diamante OO puro); substituído `git_repo()` → `cls._repo()` em todos os métodos; adicionado `git_gitlink_spec()` e `gitmodule_contract()`
- `src/flext_infra/_utilities/_git/worktree.py` — herda de `FlextInfraUtilitiesGitRepo`; substituído `git_repo()` → `cls._repo()`, `git_open_repo()` → `cls._open_repo()`
- `src/flext_infra/_utilities/_git/scope.py` — herda de `FlextInfraUtilitiesGitSemanticMixin`; métodos convertidos para `@classmethod`
- `src/flext_infra/_models/git.py` — adicionado `GitSubmoduleContractRequest`, `GitSubmoduleContractReport`
- `src/flext_infra/_models/_git/identity.py` — adicionado campo `is_inside_work_tree` ao `GitIdentityReport`

**O que falta na migração:**
- `src/flext_infra/workspace/detector.py` — **ainda tem 12 chamadas `u.Cli.capture`/`u.Cli.run_raw`** (subprocess git). Precisa ser migrado para usar `u.Infra.git_*`.
- Testes ainda falham (34 falhas na última rodada) — principalmente por causa do detector.py não migrado e problemas de modelo.

### 4. Estado da frota

**Submódulos divergentes (gitlink do superprojeto desatualizado):**
- `flext-cli`, `flext-dbt-ldap`, `flext-grpc`, `flext-oracle-wms`, `flext-plugin`, `flext-tap-oracle-wms`, `flext-target-ldap`, `flext-target-oracle` — todos em `0.12.0-dev`, 0/0 vs origin, dirty leve (codegen drift)
- `flext-ldap`, `flext-quality`, `flext-tests` — também divergentes agora (novos desde a última análise)

**Submódulos com dirty (codegen drift):**
- Todos os 22+ submódulos têm dirty — projections antigas do SSOT do flext-infra

**Superprojeto dirty:**
- 12 gitlinks para atualizar
- `.beads/config.yaml`, `.github/dependabot.yml`, `.github/workflows/`, `.gitignore`, `.pre-commit-config.yaml`, `AGENTS.md`, `Makefile`, `docs/guides/`, `pyproject.toml`, `scripts/lib/surface_validation.py`, `tests/unit/provider_surface_tests.py`, `uv.lock`
- 4 untracked: `docs/references/2026-08-05-docs-centralization-handoff.md`, `docs/references/three-owner-enforcement-ledger.json`, `docs/references/three-owner-enforcement-ledger.md`, `docs/superpowers/plans/2026-08-05-three-owner-p0-handoff.md`

## Próximos passos (ordem correta)

### Passo 1 — Terminar migração detector.py para GitPython

Substituir as 12 chamadas `u.Cli.capture`/`u.Cli.run_raw` em `src/flext_infra/workspace/detector.py`:

| Linha | Comando atual | Substituir por |
|-------|-------------|----------------|
| ~215 | `git remote get-url origin` | `u.Infra.git_remote_url(m.Infra.GitRemoteUrlRequest(repo_root=repository_root, remote="origin"))` |
| ~309 | `git rev-parse --show-superproject-working-tree` | `u.Infra.git_superproject_working_tree(m.Infra.GitRepoRequest(repo_root=resolved_root))` |
| ~319 | `git rev-parse --is-inside-work-tree` | `u.Infra.git_identity(m.Infra.GitRepoRequest(repo_root=resolved_root))` → check `.value.is_inside_work_tree` |
| ~654 | `git config --file .gitmodules --get-regexp` | `u.Infra.gitmodule_contract(m.Infra.GitSubmoduleContractRequest(repo_root=superproject_root, member_path=member_path))` |
| ~685 | `git config --file .gitmodules --get {section}.url` | (mesmo método acima — retorna url e branch) |
| ~700 | `git config --file .gitmodules --get {section}.branch` | (mesmo método acima) |
| ~725 | `git rev-parse --show-toplevel` | `u.Infra.git_show_toplevel(m.Infra.GitRepoRequest(repo_root=project_root))` → use `.value.workspace_root` |
| ~827 | `git config --get remote.origin.url` | `u.Infra.git_remote_url(m.Infra.GitRemoteUrlRequest(repo_root=member_root, remote="origin"))` |
| ~834 | `git ls-files --stage -- member_path` | `u.Infra.git_gitlink_spec(m.Infra.GitRefRequest(repo_root=superproject_root, reference=member_path))` |
| ~850 | `git rev-parse --verify HEAD^{commit}` | `u.Infra.git_resolve_commit(m.Infra.GitCommitishRequest(repo_root=member_root, commitish="HEAD^{commit}"))` |
| ~909 | `git rev-parse --is-inside-work-tree` | `u.Infra.git_identity(m.Infra.GitRepoRequest(repo_root=resolved_project_root))` → check `.value.is_inside_work_tree` |
| ~924 | `git rev-parse --show-superproject-working-tree` | `u.Infra.git_superproject_working_tree(m.Infra.GitRepoRequest(repo_root=resolved_project_root))` |

### Passo 2 — Rodar testes e corrigir falhas

```bash
cd flext-infra
make check CHECK_GATES=lint,format
make test
```

Corrigir as ~34 falhas restantes (principalmente testes do detector e codegen).

### Passo 3 — Commit + push flext-infra

```bash
cd flext-infra
git add -A
git commit -m "refactor(detector): migrate workspace detector to GitPython _git/ owner"
git push origin 0.12.0-dev
```

### Passo 4 — make setup + make gen (regenerar frota)

```bash
cd /home/marlonsc/flext
make setup
make gen WHAT=apply APPLY=Y
make gen  # verificar idempotência
```

### Passo 5 — Commit + push em cada submódulo dirty

```bash
for sm in flext-api flext-auth flext-cli flext-core flext-db-oracle flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms flext-grpc flext-ldap flext-ldif flext-meltano flext-observability flext-oracle-oic flext-oracle-wms flext-plugin flext-quality flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic flext-target-ldap flext-target-ldif flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms flext-tests flext-web; do
  cd /home/marlonsc/flext/$sm
  git add -A
  git commit -m "chore: fix-forward codegen drift from flext-infra"
  git push origin 0.12.0-dev
done
```

### Passo 6 — Superprojeto: gitlinks + codegen drift + untracked

```bash
cd /home/marlonsc/flext
git add flext-infra flext-api flext-auth flext-cli flext-core flext-db-oracle flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms flext-grpc flext-ldap flext-ldif flext-meltano flext-observability flext-oracle-oic flext-oracle-wms flext-plugin flext-quality flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic flext-target-ldap flext-target-ldif flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms flext-tests flext-web
git add .beads/config.yaml .github/dependabot.yml .github/workflows/ .gitignore .pre-commit-config.yaml AGENTS.md Makefile docs/guides/ pyproject.toml scripts/lib/surface_validation.py tests/unit/provider_surface_tests.py uv.lock
git add docs/references/2026-08-05-docs-centralization-handoff.md docs/references/three-owner-enforcement-ledger.json docs/references/three-owner-enforcement-ledger.md docs/superpowers/plans/2026-08-05-three-owner-p0-handoff.md
git commit -m "chore: fix-forward fleet gitlinks + codegen drift (0.12.0-dev)"
git push origin 0.12.0-dev
```

### Passo 7 — Validação final

```bash
make setup
make check
make test
```

## Regras absolutas

- **Sem stash, sem rollback, sem abort de merge** — fix-forward sempre
- **Sem `git add -A` no superprojeto** — `git add` scoped por path
- **Push rejeitado (FF)** → parar e escalar com git error + SHAs (regra 8)
- **Sem métodos soltos** — sempre classes nested, MRO diamante OO puro (sem "Mixin" no nome)

## Arquivos-chave

- `flext-infra/src/flext_infra/workspace/detector.py` — detector que precisa migração
- `flext-infra/src/flext_infra/_utilities/_git/repo.py` — `FlextInfraUtilitiesGitRepo` (criado)
- `flext-infra/src/flext_infra/_utilities/_git/semantic.py` — métodos git semânticos (modificado)
- `flext-infra/src/flext_infra/_utilities/_git/worktree.py` — métodos git worktree (modificado)
- `flext-infra/src/flext_infra/_utilities/_git/scope.py` — métodos git scope (modificado)
- `flext-infra/src/flext_infra/_models/git.py` — modelos request/report (modificado)
- `flext-infra/src/flext_infra/_models/_git/identity.py` — `GitIdentityReport` com `is_inside_work_tree` (modificado)

## Branch / remoto

- Todos os repos em `0.12.0-dev`
- `origin/0.12.0-dev` do flext-infra = `b4fc9325` (já tem merges #269, #270, #271)
- `flext-infra` local tem 5 commits adicionais não-pushed
- Superprojeto `origin/0.12.0-dev` = `3c612c22a` (gitlink flext-infra atualizado)
