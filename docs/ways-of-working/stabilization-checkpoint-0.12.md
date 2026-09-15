# Runbook de estabilização — checkpoint 0.12.0

## (a) Ciclo canônico

```bash
make setup
make gen
make gen          # 2× ponto fixo (idempotência)
make fix
make fmt
make check
make test
make build
```

Uma falha → corrigir o dono do verbo; sem inflar timeout; sem remover testmon.

## (b) Contrato beads central

- `bd` roda via `direnv exec <repo> bd ...`
- A ativação vem do `.envrc`/`.envrc.local` gerado (AGENTS_GAS_CITY_ROOT + porta da publicação da cidade + banco da metadata do rig)
- Reparo de identidade: `gc rig set-endpoint flext --inherit`
- Nunca inicializar banco embedded/porta manual (fonte: `flext-infra/docs/guides/execution-context.md`)

## (c) Integração

1. Lane → commit escopado (paths explícitos, nunca `git add -A`)
2. `merge --no-ff` em `0.12.0-dev`
3. Push fast-forward
4. Revalidar gates no SHA mesclado
5. Evidência no bead (comando, cwd, exit, saída decisiva)

## (d) Extermínios vigentes

`APPLY`, `uv.lock`, `mise.lock`, banco local de beads — leitura/geração também, não só gitignore.
