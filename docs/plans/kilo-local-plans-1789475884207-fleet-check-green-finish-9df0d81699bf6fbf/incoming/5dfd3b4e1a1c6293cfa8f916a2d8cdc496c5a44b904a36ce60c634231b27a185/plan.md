# Fleet Check-Green Finish — continuação da estabilização 0.12.0 (nova sessão)

## Contexto evidenciado (2026-09-15, sessão anterior)

LANDED e pushed em `origin/0.12.0-dev` (tips):

- Raiz `28130920dd`: docs MD013 + projeção oracle marker + 30 gitlinks.
- 31 membros synced nos tips. `make gen` ×2 exit 0 (ponto fixo), `make fix` 32/32, `make fmt` 32/32.
- Resíduo `bd init` (dolt/hooks/interactions.jsonl/README/.gitignore) removido de 25 rotas `.beads` de membros — contrato SSOT `conform.py:758-787` (rota de membro = só identidade: config.yaml, metadata.json, .local_version, last-touched). Ledger central preservado (bd server mode 127.0.0.1:14499, db `flext`).
- Slices lint: flext-cli `92e59ae8` (SLF001 ×3, aliases de classe aninhada eliminados), flext-core `27f4d21b9` (D107 ×2 + fmt wraps), flext-tests `01e084b` (SLF001 proto alias).
- Evidência no bead `flext-c4k44` (via `direnv exec . gc bd update --append-notes`).

INVENTÁRIO FRESCO (make check 15:01, ~4200 violações 32/32 FAIL):

| Classe                                        | Escala                                                       | Owner da correção                                             |
| --------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------- |
| namespace NS-STRUCT                           | ~2900 (struct)                                               | exemplos→facade classes; módulos Single Class Nested          |
| namespace NS-CONTRACT/IMPORT + census ENFORCE | ~1150 + 1166 findings                                        | bare `Flext*` imports → alias `c/t/p/m/u`                     |
| NS-LAYOUT                                     | ~180                                                         | cli.py + `<família>/base.py` + services/ faltantes            |
| pyrefly/mypy/pyright                          | por repo (cli 21+6, api, tests 26…)                          | nos sites, sem suppression                                    |
| tier-whitelist                                | 10 (cli)                                                     | yaml bare imports → `u.Cli`                                   |
| silent-failure                                | ~12                                                          | except propaga; `r.Fail` só em boundary e/u                   |
| duplication (jscpd gate)                      | 2 (flext-api async_client)                                   | extermiar clone, um owner                                     |
| codemod require-future-annotations            | 21 (`_parts/__init__.py` docstring-only, maioria flext-core) | inserir future import pós-docstring                           |
| DIRENV_CONTRACT `$HOME` vazio                 | 2+                                                           | owner: gate flext-infra (operador) — coordenar, NÃO contornar |

ESTADO DOS AGENTES AO ENCERRAR (worktrees dos membros, NÃO commitado):

- Com edições em voo (ADOTAR via fix-forward, nunca descartar): flext-ldif (~45 arq), flext-observability (~27), flext-plugin (~15), flext-grpc (~8), flext-core (~5), flext-db-oracle (~5), flext-api (~4), flext-auth (~2), flext-ldap (1), flext-quality (1 + teste logger runtime-law).
- Re-despachos edit-first sem edições visíveis: flext-web, flext-cli, flext-tests, flext-meltano (validar tree antes de re-assumir).
- flext-infra: DOMÍNIO DO OPERADOR (refactor rope `_rope/` em voo). NÃO editar. Se gates de membros falharem com import/syntax de flext-infra = estado mid-flight do operador; aguardar e re-validar.

## Leis vinculantes do operador (resumo operacional)

1. Obedecer ao que `make setup/gen/fix/fmt/check/test` gera; nunca o contrário.
2. Fix-forward adopt SEMPRE; proibido rollback/restore/stash/reset/revert; base de trabalho = tip `0.12.0-dev` de cada repo; push FF direto no tip, incremental.
3. Causa raiz sempre — inclusive warnings, cosméticos e pré-existentes.
4. Facade pattern OBRIGATÓRIO: `modulo.py` = pasta `_[modulo]/` (base.py + outros _.py); base.py ABSORVE TUDO das classes internas (MRO completa); PROIBIDO `_parts/`/`__part_NN.py`; facade = só `from ._[modulo] import Classes`+ classe MRO vazia;`make gen`gera`**init**` (execução CENTRAL, nunca nos subagentes).
5. Anti-GOD-module: Single Class Nested flext por módulo; DRY/SOLID/YAGNI/SSOT em settings/config/c-t-p-m-u/base/services/api/cli; protocols `p.*` + Pydantic `m.*` para tudo; ultra-DRY via c/t/p/m/u (REDUZIR LOC; ≤200 LOC lógicos).
6. Tests = runtime law: validar comportamento via facades públicas; exterminar mocks/fakes/validação privada/hardcoded de config; tests não definem funcionamento — runtime define.
7. jscpd para duplicados (exterminar); ruff e pyrefly SEMPRE verdes em todos os arquivos; zero `# noqa`/`type: ignore`.
8. bd sempre via `direnv exec <repo> gc bd ...`; evidência em `flext-c4k44`/`flext-itpd1.1`.
9. Subagentes em paralelo por repo (um por repo, zero sobreposição), main coordena commit/push/gen/gitlinks/beads; workers nunca pusham.
10. Ferramentas: ast-grep para classes mecânicas, jscpd para duplicação, code-review-graph para mapear donos/consumidores antes de mover símbolos, Context7 p/ referência pydantic/PEP.

## Onda A — Reassimilar e landar o que está em voo (primeiro incremento)

1. Por repo com tree suja (lista acima): `git status --short` → revisar diff hunk a hunk → validar `make check` no repo até exit 0 (se flext-infra quebrar o import, esperar janela do operador e re-validar). Comitar escopado por classe (`fix(namespace): ...`, `refactor(facade): ...`, `chore(beads): ...`) + push FF no tip.
2. Re-dispachar (edit-first, relatório obrigatório) repos cujos agentes não deixaram trabalho: web, cli, tests, meltano — e os taps/targets sem sinal (tap-oracle-oic, tap-oracle-wms, target-ldap+ldif, target-oracle+oic, target-oracle-wms).
3. `make gen` central após qualquer facade nova (`_[modulo]/` criada) — gera os `__init__`; re-provar ponto fixo ×2.
4. Bump gitlinks da raiz por lote de repos landados + push.

## Onda B — Completar o ladder por repo (fila de fatias)

Ordem por massa restante (re-inventariar com `make check` por repo após Onda A):

1. flext-cli (615: struct 400, contract/import 175, tier-whitelist 10, pyrefly 21, mypy 6, census 75)
2. flext-core (663: struct 370, contract/import 225, layout 5 + codemod 21)
3. flext-ldif (286), flext-tests (264: struct 163, mypy 26, census 54, silent-failure 8), flext-infra (246 — SOMENTE se o operador liberar)
4. Médios: oracle-wms (147), target-oracle-wms (128), tap-oracle-wms (112), target-oracle (104), quality (103), db-oracle (100), api (10 — fechar com duplication ×2)
5. Pequenos: grpc (90), tap-oracle-oic (88), meltano (109), observability (109), plugin (84), web (82), ldap (72), target-ldap (77), auth (65), plugin…

Táticas por classe (uma classe por passe, revalidar `make check PROJECT=<repo>` por passe):

- contract/import + census: sweep ast-grep `from flext_<x> import Flext<Y>` → alias; validar runtime do import.
- NS-STRUCT: converter exemplos em facade classes (stem `Flext<Repo>`), funções top-level → métodos; tests → nested `TestsFlext<Repo>` MRO.
- NS-LAYOUT: scaffold `cli.py`, `<família>/base.py`, `services/` espelhando flext-api (layout=0) e flext-core.
- pyrefly/mypy/pyright: no site; unused-ignore = remover ignore e corrigir o tipo; sem suppression.
- silent-failure: propagar; `r.Fail` apenas em boundaries e/u.
- duplication: jscpd por repo; um owner + rewire consumidores + deletar clone (api: `async_client.py` vs `client.py`/`base_client.py`).

## Onda C — Absorção de lanes soltas (trees limpas)

1. `chore/absorb-inflight-20260911b` (~16 repos, 2 commits cada): deltas reais (ex.: +112 linhas pyproject de gen antigo). Merge --no-ff na tip; se projeção conflitar, vence o gen ATUAL (resolver regenerando); validar `make check/test` antes do push.
2. `wip/duplicate/flext/<repo>` (6 repos, 1-2 commits): ancestry/diff vs tip; conteúdo já absorvido = lane retireável (após prova `git cherry`); delta real = merge fix-forward.
3. Lanes fix: flext-api `fix/api-http-contracts-tip` (3), `fix/configdict-single-owner` (1); flext-infra `f4-infra` (1), `feat/mod-sed-list-import` (2), `fix/flext-5fxu6-generator-facades` (3 — só com operador). Absorver semântica útil por merge --no-ff contra tip fresco.
4. `0.20.0-dev` = baseline FORWARD — não absorver ao contrário.

## Onda D — Revalidação de testes (runtime manda)

1. `make test` por repo (via agentes na validação final + make test fleet na raiz); timeouts -15/-9 do infra: renovar evidência por §8.4 do handoff, sem inflar timeouts.
2. Sweep de mocks/fakes/validação privada: `rg -l 'unittest.mock|MagicMock|mocker|monkeypatch|patch\('` por repo → converter para comportamento via facades públicas (bead R25/flext-c4k44 já tem o padrão); provisionamento real (Oracle/Docker) falha ALTO — nunca skip-convert.
3. Valores config-owned nos testes → ler do SSOT tipado (nunca congelar).

## Onda E — Fechamento

1. `make setup && make gen && make gen` (0,0,0) → `make fix && make fmt && make check` (32/32) → `make test && make build && make docs`.
2. Gitlinks finais da raiz → push; PRs por repo lesionado com merge `--no-ff` (CI real no SHA; autorização admin 23:07 do operador registrada como tal).
3. Beads: fechar `flext-c4k44`/`flext-itpd1.1` com evidência (comandos+exits+SHAs); criar beads P1 (automação namespace por templates, reconciliação 286 beads abertas, retire de worktrees/lanes, auditoria Copernicus).
4. Docs: runbook com lições (lazy relative resolution, venv-skew, beads route SSOT, journal CAS, gateway flaky→resume); ADR-014 ganha regras ast-grep/jscpd; `flext-law` SKILL atualizado (facade-MRO + metadata-mint contract).
5. Aceite: `git status` limpo nos 32; tips pushed (0/0 vs origin); relatório final repo→SHA→gates→evidência no bead.

## Riscos / mitigações

- **Gateway upstream flaky (503/idle-timeout mata agentes)**: despachar edit-first (editar antes de validar), rajadas curtas, retomar via task_id (contexto preservado) — padrão com 100% de sucesso de retomada.
- **flext-infra em work pelo operador**: jamais editar; membros esperam janela e re-validam; direnv gate bug = dono infra.
- **Conflito de git index** (ator concorrente commitando): aguardar lock, re-avaliar estado, adotar.
- **Projeções gen vs lanes antigas**: gen atual vence; regenerar pós-merge.
- **Relatórios vazios de agentes**: proibir; relatório obrigatório com arquivo+classe+exit; auditoria da main por `git status` sempre.

## Validação final (aceite)

```
make setup && make gen && make gen        # 0,0,0 ponto fixo
make fix && make fmt && make check        # 0,0,0 (32/32)
make test && make build && make docs      # 0,0,0
git status limpo nos 32 + tips pushed (0/0 vs origin)
direnv exec . gc bd show flext-c4k44 --rig flext --json  # evidência fechada
```
