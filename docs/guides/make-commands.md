# Comandos Make do FLEXT

<!-- TOC START -->
- Convenções
- [Verbos canônicos](#verbos-canônicos)
- Knobs declarados
- [Custom hooks](#custom-hooks)
- [Seletores de escopo](#seletores-de-escopo)
- [Exemplos do dia a dia](#exemplos-do-dia-a-dia)
- [Descoberta](#descoberta)
- Veja também
<!-- TOC END -->

Este guia é a referência canônica para a superfície de comando `make` do workspace FLEXT. A fonte da verdade
desta superfície é o próprio `make help`; este guia documenta o mesmo contrato em prosa. As regras valem para
o workspace raiz; cada projeto `flext-*` possui seus próprios targets locais gerados pelo mesmo template.

## Convenções

- **Poucos verbos, muitas ações**: o formato é `make <verbo> WHAT=<acao>`. Cada verbo agrupa um domínio.
- **Mutadores são dry-run por padrão**: comandos que alteram arquivos exigem `APPLY=Y` para executar de verdade.
- **Gates por escopo**: `PROJECT=<name>` restringe o gate a um membro; sem `PROJECT`, o verbo percorre o workspace.
- **Ajuda embutida**: `make help` lista todos os verbos e knobs.

## Verbos canônicos

Saída de `make help` (perfil workspace):

| Verbo | Domínio | Ações (`WHAT=`) | Exemplo |
| --- | --- | --- | --- |
| `help` | meta | `usage` | `make help` |
| `setup` | ambiente | — | `make setup` |
| `deps` | dependências | `check`, `lock`, `upgrade` | `make deps WHAT=upgrade DEPENDENCY=flext-infra APPLY=Y` |
| `build` | build | `artifacts` | `make build WHAT=artifacts` |
| `check` | quality | `all`, `lint`, `pyrefly`, `mypy`, `pyright`, `security`, `markdown`, `smells`, `direnv` | `make check WHAT=lint PROJECT=flext-infra` |
| `test` | quality | `all`, `full`, `cache-status`, `cache-clear`, `cache-checkpoint` | `make test PROJECT=flext-infra` |
| `fmt` | formatação | `check`, `all`, `apply` | `make fmt WHAT=apply APPLY=Y` |
| `fix` | correção | `check`, `all`, `apply` | `make fix WHAT=apply APPLY=Y` |
| `run` | runtime | `default` | `make run WHAT=default APPLY=Y` |
| `status` | diagnósticos | `diagnostics` | `make status` |
| `docs` | documentação | `all`, `generate`, `fix`, `audit`, `build`, `validate` | `make docs WHAT=validate` |
| `clean` | limpeza | `status`, `generated` | `make clean WHAT=generated APPLY=Y` |
| `release` | release | `status` | `make release WHAT=status` |
| `gen` | geração | `check`, `all`, `apply`, `init` | `make gen WHAT=apply APPLY=Y` |
| `mod` | modernização | `check`, `all`, `apply` | `make mod WHAT=all APPLY=Y` |

## Knobs declarados

| Knob | Verbo | Efeito |
| --- | --- | --- |
| `WORKSPACE` | geral | repositório alvo (default: projeto atual) |
| `BEAD` | geral | item do tracker vinculado a um checkpoint |
| `BASE` | geral | branch de integração usada pelo checkpoint |
| `DEPENDENCY` | `deps upgrade` | um nome de distribuição (default: todos os pacotes) |
| `DEPS_REFRESH` | `deps upgrade` | `Y` renova o cache de fontes uv |
| `PROJECT` | gates | restringe o verbo a um membro declarado |
| `APPLY=Y` | mutadores | executa a mutação (sem ele, dry-run) |

## Custom hooks

`custom.mk` estende a superfície sem duplicá-la:

- `pre-<verb>`, `post-<verb>`, `pre-<verb>-<what>`, `post-<verb>-<what>` envolvem um handler declarado.
- `_custom_<verb>_<what>` define um novo `WHAT` para um verbo existente.

Definidos neste projeto: `post-boot`.

## Seletores de escopo

Use `PROJECT` para um projeto; omita para o workspace inteiro:

```bash
make check WHAT=lint PROJECT=flext-infra
make test PROJECT=flext-infra
make check WHAT=mypy PROJECT=flext-ldif
```

## Exemplos do dia a dia

```bash
# Bootstrap inicial
make setup

# Checagem rápida padrão
make check

# Checagem em um projeto específico
make check WHAT=lint PROJECT=flext-infra

# Regenerar projeções (conform + lazy-init + docs + mise)
make gen WHAT=apply APPLY=Y

# Rodar testes de um projeto
make test PROJECT=flext-infra

# Validar documentação
make docs WHAT=validate
```

## Descoberta

```bash
make help                  # lista todos os verbos e knobs
```

## Veja também

- [Development](development.md) — workflow diário.
- [Testing](testing.md) — gates de teste.
- [Getting Started](getting-started.md) — bootstrap do workspace.
