# Comandos Make do FLEXT

Este guia é a referência canônica para a superfície de comando `make` do monorepo FLEXT. As regras aqui valem para o
workspace raiz; cada projeto `flext-*` ainda possui seus próprios targets locais (`make check`, `make test`, etc.).

## Convenções

- **Poucos verbos, muitas ações**: o formato é `make <verbo> WHAT=<acao>`. Cada verbo agrupa um domínio.
- **`all` é o padrão**: se `WHAT` for omitido, o comando executa a ação `all` daquele verbo.
- **Projetos default = todos**: se `PROJECT` ou `PROJECTS` forem omitidos, o comando abrange todos os projetos do
  workspace.
- **Mutadores são dry-run por padrão**: comandos que alteram arquivos exigem `APPLY=Y` para executar de verdade.
- **Ajuda embutida**: `make <verbo> WHAT=help` lista as ações disponíveis.

## Verbos canônicos

| Verbo | Domínio | Resumo | Exemplo |
| --- | --- | --- | --- |
| `make setup` | workspace | Bootstrap de `.venv` + submódulos | `make setup APPLY=Y` |
| `make build` | build | Build/regen padronizado | `make build WHAT=gen APPLY=Y` |
| `make check` | quality | Quality gates | `make check` |
| `make clean` | workspace | Limpeza de artefatos | `make clean APPLY=Y` |
| `make coordination` | governance | Diagnósticos de coordenação Beads | `make coordination` |
| `make docs` | documentation | Pipeline de documentação | `make docs DOCS_PHASE=validate` |
| `make makefile` | meta | Mostra a superfície de comandos | `make makefile` |
| `make work` | lane lifecycle | Saga bead+GitFlow+worktree+PR | `make work WHAT=start BEAD=<id> KIND=feature NAME=<slug> APPLY=Y` |
| `make ship` | release | Orquestração de release | `make ship WHAT=rel APPLY=Y` |
| `make status` | governance | Status dos Beads | `make status` |
| `make test` | quality | Testes pytest | `make test PROJECT=flext-infra MATCH=docs` |
| `make val` | governance | Validação de gates | `make val` |

## Ações de `build` (`make build WHAT=<acao>`)

| Ação | Alias curto | Muta? | Descrição |
| --- | --- | --- | --- |
| `all` | — | sim | Build/package em todos os projetos selecionados |
| `constraints` | — | sim | Reescreve constraints de dependências |
| `docs` | — | sim | Roda o pipeline de docs |
| `gen` | `make gen` | sim | Regenera arquivos padronizados de projeto |
| `mod` | `make mod` | sim | Moderniza `pyproject.toml` |
| `stubs` | `make stubs` | não | Validação da cadeia de stubs |
| `sync` | `make sync` | sim | Sincroniza Makefiles a partir do `pyproject.toml` |
| `up` | `make up` | sim | Upgrade de dependências do workspace |

## Ações de `check` (`make check WHAT=<acao>`)

| Ação | Alias curto | Descrição |
| --- | --- | --- |
| `all` | `make lint` | Default rápido: `lint` + `pyrefly` |
| `boundary` | `make boundary` | Boundary gate |
| `cqrs` | `make cqrs` | CQRS compliance gate |
| `docker_standardization` | `make docker_standardization` | Centralização de artefatos Docker |
| `fmt` / `format` | `make fmt` / `make format` | Formatação (ruff + markdown) |
| `go` | `make go` | Go quality gate |
| `lint` | `make lint` | Lint + type gates |
| `loc-cap` | `make loc-cap` | Loc-cap gate |
| `markdown` | `make markdown` | Markdown quality gate |
| `mypy` | `make mypy` | mypy gate |
| `pol` | `make pol` | Typing policy gate |
| `pyre` | `make pyre` | Pyrefly repository type check |
| `pyrefly` | `make pyrefly` | Pyrefly scoped type check |
| `pyright` | `make pyright` | Pyright gate |
| `scan` | `make scan` | Security scan gates |
| `silent-failure` | `make silent-failure` | Silent-failure gate |
| `types` | `make types` | Typing supply chain |


## Ações de `work` (`make work WHAT=<acao>`)

Saga pública de lane: bead + GitFlow branch + worktree registrada + PR.
`FlextInfraWorktreeService` continua como motor interno; a superfície pública
não expõe `WHAT=worktree`.

| Ação | Muta? | Descrição |
| --- | --- | --- |
| `start` | sim (`APPLY=Y`) | Cria branch `KIND/NAME`, worktree registrada e grava metadata no bead |
| `status` | não | Reporta branch/worktree/`head_oid`/PR do bead |
| `land` | sim (`APPLY=Y`) | Sync→push→abre/observa PR; exige lane limpa, `head_oid` e bind metadata↔registry |
| `finish` | sim (`APPLY=Y`) | Após PR merged: remove worktree, apaga ref local (CAS) e marca `worktree=removed` |

Seletores:

| Variável | Função |
| --- | --- |
| `BEAD` | id do bead dono da lane (obrigatório em start/land/finish) |
| `KIND` / `NAME` | GitFlow kind (`feature`/`bugfix`/…) e slug kebab-case (start) |
| `BASE` | override opcional da integration base (start) |
| `WORKSPACE` | checkout git alvo (default: projeto atual) |
| `PROJECT` | em workspace-root, se `WORKSPACE` não for passado na CLI, mapeia para `$(PROJECT_ROOT)/$(PROJECT)` |

Controles de segurança (land/finish):

- metadata `worktree` deve coincidir com a lane registrada no git primary
- branches permanentes (`main`/`master`/integration base) são recusadas
- `metadata.head_oid` é obrigatório para CAS em land e em finish quando a lane existe

```bash
make work WHAT=start PROJECT=flext-infra BEAD=mro-xxxx KIND=feature NAME=my-lane APPLY=Y
make work WHAT=status PROJECT=flext-infra BEAD=mro-xxxx
make work WHAT=land PROJECT=flext-infra BEAD=mro-xxxx APPLY=Y
make work WHAT=finish PROJECT=flext-infra BEAD=mro-xxxx APPLY=Y
```

`make ship WHAT=pr` não é dono de lane; land é o owner do PR da lane.

## Ações de `ship` (`make ship WHAT=<acao>`)

| Ação | Alias curto | Muta? | Descrição |
| --- | --- | --- | --- |
| `all` / `rel` | `make rel` | sim | Release workflow |
| `pr` | `make pr` | sim | Gerenciamento de PRs |
| `push` | `make push` | sim | Push de branches/tags |
| `save` | `make save` | sim | Commit de alterações |
| `tag` | `make tag` | sim | Criação de tags |

## Ações de `val` (`make val WHAT=<acao>`)

| Ação | Alias curto | Descrição |
| --- | --- | --- |
| `all` | — | Roda `project` + `workspace` (padrão) |
| `project` | `make project` | Validação ao nível de projeto |
| `workspace` | `make workspace` | Validação ao nível de workspace |

> O `VALIDATE_SCOPE` default é `all`, então `make val` já executa ambos os escopos.

## Seletores de escopo

Use `PROJECT` para um projeto, `PROJECTS` para vários, ou omita para todos:

```bash
make check PROJECT=flext-infra
make test PROJECTS="flext-core flext-cli" MATCH=docs
make build WHAT=gen APPLY=Y              # todos os projetos
```

Não use `PROJECT` e `PROJECTS` juntos.

## Dry-run e mutação

Comandos que alteram o workspace (build, clean, ship, boot, etc.) exibem um dry-run a menos que `APPLY=Y` seja passado:

```bash
make build WHAT=gen          # dry-run
make build WHAT=gen APPLY=Y  # executa
make clean                   # dry-run
make clean APPLY=Y           # executa
```

## Exemplos do dia a dia

```bash
# Bootstrap inicial
make setup APPLY=Y

# Checagem rápida padrão (ruff + pyrefly)
make check

# Checagem em um projeto específico
make check PROJECT=flext-infra

# Regenerar arquivos padronizados
make gen APPLY=Y

# Rodar testes de um projeto
make test PROJECT=flext-infra MATCH=docs

# Validar workspace completo
make val

# Lane saga em um membro
make work WHAT=status PROJECT=flext-infra BEAD=mro-xxxx

# Sincronizar Makefiles após mudar pyproject.toml
make sync APPLY=Y
```

## Descoberta

```bash
make help                  # lista todos os verbos
make build WHAT=help       # lista ações de build
make build WHAT=gen/help   # ajuda detalhada de gen
```

## Veja também

- [Development](development.md) — workflow diário.
- [Testing](testing.md) — gates de teste.
- [Getting Started](getting-started.md) — bootstrap do workspace.
