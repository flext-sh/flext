# P0 Stabilization Finish Line — gates verdes, extermínio de stub/fallback/silenciamento, publicação nos tips

## Contexto (evidência desta sessão, 2026-09-15)

Concluído e VALIDADO (runtime/provas), ainda NÃO commitado na maioria:

1. **Nested workspace exterminado**: `[tool.uv.workspace]` vazios removidos dos 31
   membros via conform dirigido pela fonte → `make setup` exit 0 (286 pkgs).
2. **Skew do venv raiz quebrado**: `flext_infra`/`flext_core`/`flext_cli` agora resolvem
   da árvore fonte (editáveis) — gen/check executam código vivo, não cópia stale das
   06:48.
3. **`make gen` ponto fixo**: 2× exit 0 (32/32 conform).
4. **Bug lazy import (causa raiz)**: `_resolve_lazy_target` em
   `flext-core/_lazy_parts/flextlazy_part_01.py` resolve chaves `..x` pai-relativas
   (antes: concatenação ingênua → `flext_ldif.servers._oid.` → crash no self-check da
   raiz). Prova: getmembers OK em `_oid`, `servers`, `flext_ldif`.
5. **flext-core SLF001**: 8 arquivos de teste refactorados (aliases privados
   module-level deletados; métodos usam caminho qualificado `Tests....Nome`; corpo de
   classe usa nome simples) — **2682 tests passed exit 0**.
6. **flext-core result.py**: branch TYPE_CHECKING herda `p.Result[T]` (runtime intacto —
   conflito de metaclass com Protocol; verificado empiricamente). Alvo: matar a classe
   mypy "got FlextResult expected Result".
7. **flext-auth**: F821 corrigido (`TestsFlextAuthModels.CertificateFixture`); beads
   mintado (`bd init` + alinhamento `dolt_database: flext` ao SSOT `config/beads.yaml`);
   `direnv exec . bd context --json` exit 0. Side effects do bd: bloco BEADS em
   AGENTS.md, CLAUDE.md novo, `.claude/settings.json`, `sync.remote` em
   `.beads/config.yaml` — ADOTAR (bd é owner) exceto onde conform normaliza.
8. **+20 membros**: metadata mintado + alinhado ao SSOT `flext`; direnv+bd funcionando
   (spot-check flext-ldap exit 0).
9. **flext-api**: refactor dedup (`base_request.py`, `base_client.py`,
   `tests/unit/_model_contract.py`) — clonagens request/async_request e tests reduzidas.
10. **flext-tests**: type aliases recursivos → `ct.JsonValue` (codemod 22→0).
11. **Raiz**: MD013 wrapped no handoff README; crash runtime-census da raiz resolvido
    pelo fix lazy.

## Escopo P0 (com ponto de finalização DEFINIDO)

**FIM P0 = todas as ondas abaixo landadas**: gates
`setup/gen×2/fix/fmt/check/test/build/docs` verdes (ou exceção evidenciada por gate
customizado, aceita pelo operador), todos os commits pushed nos tips `0.12.0-dev`,
gitlinks do superprojeto bumped+pushed, PRs merged `--no-ff` com CI real verde no SHA,
beads fechadas com evidência, ADRs/docs/skills atualizados. Publicação = estado final
estável NA branch tip dos projetos afetados (tag opcional a critério do operador no
fechamento).

### Onda 0 — Landar o trabalho validado (primeiro incremento)

1. `git -C flext-infra status` → adjudicar WIP do ator concorrente (conform.py,
   direnv_gate_tests, \_pytest_runner/command.py — eles têm commited
   `48a229fdd`/`40bf142da`; absorver WIP não commitado via fix-forward NO MEU commit
   escopado; nunca descartar).
2. Commits escopados POR CATEGORIA, na ordem de dependência (flext-core →
   flext-cli/flext-tests → flext-infra → membros → raiz):
   - flext-core: lazy fix + result.py TYPE_CHECKING + refactor SLF001 dos 8 tests +
     projeções geradas.
   - flext-tests: typings fix + projeções.
   - flext-infra: WIP absorvido (config/codegen/tests) + projeções.
   - flext-auth: F821 + beads metadata/identity + AGENTS.md/CLAUDE.md bd blocks.
   - Demais 26 membros: beads metadata/identity + projeções geradas.
   - flext-api: refactor dedup + projeções.
   - Raiz: docs (MD013) + projeções.
3. Push FF por repo para `origin/0.12.0-dev` (permission `git push *` autorizada).
   Superprojeto: gitlinks + push.
4. Beads via `direnv exec <repo> bd update` com evidência (comandos, exits, SHAs) em
   `flext-c4k44`/`flext-itpd1.1`.

### Onda 1 — Ladder verde (check triage por fatia)

Pré: rerun `make fix` + `make fmt` (flext-auth lint e flext-core SLF já corrigidos —
provar exit 0).

Fatias por repo (SUBAGENTES code paralelos em worktrees dedicadas alinhadas ao tip; main
session coordena/commita/pusha; workers nunca merge/push):

| Fatia                                                                                                               | Conteúdo (evidência do check 09:2x)                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| flext-cli                                                                                                           | namespace 579 (exemplos → facade pattern `ExamplesFlextCli` MRO; src NS-STRUCT/CONTRACT/IMPORT), tier-whitelist 10 (yaml bare imports → `u.Cli.*`), pyrefly 21, mypy 7, pyright 3, lint SLF001 3                                                                        |
| flext-tests                                                                                                         | namespace 229 (validator/tmatchers/enforcement conformance), mypy 26 (unreachable/unused-ignore/dict-item), runtime-census 54 (class_prefix, proto_not_runtime, smell_function_parameters, const_mutable), silent-failure 8                                             |
| flext-web                                                                                                           | namespace 77 (exemplos + layout base.py), silent-failure 4 (except→sentinel/pass), runtime-census 5 (ENFORCE-046/070/079)                                                                                                                                               |
| flext-api                                                                                                           | pyrefly 13, mypy 15 (classe FlextResult-vs-Result — validar fix TYPE_CHECKING; senão anotar retorno como `p.Result` via `r[...].ok` covariance... sem `type: ignore`), pyright, namespace 5, runtime-census proto_inner_kind (agente já commiteou 02b43df8 — verificar) |
| flext-core                                                                                                          | codemod require-future-annotations nos `__init__.py` gerados (causa raiz: TEMPLATE do gerador não emite `from __future__ import annotations` em facets sem docstring de módulo — corrigir no owner flext-infra templates, não nos arquivos)                             |
| raiz                                                                                                                | direnv DIRENV_CONTRACT `$HOME` vazio no gate (owner: WIP direnv_gate_tests do ator concorrente — coordenar/absorver; o gate expande `$HOME` com env sem HOME → bug do gate, não do .envrc)                                                                              |
| conectores (db-oracle, dbt-_, grpc, ldap, ldif, meltano, observability, oracle-_, plugin, quality, tap-_, target-_) | classes exit=2: mesma taxonomia (namespace/example/test-conformance/pyrefly) — matar por CLASSE de violação ponta-a-ponta via `make mod` + ast-grep, não cottage manual                                                                                                 |

Regras por fatia: mapear dono/consumidor com `code-review-graph` antes de mover símbolo;
mutabilidade não é grafia (dict→Mapping só com prova de contrato); uma classe de
violação por wave do `make mod`; revalidar `make check PROJECT=<repo>` por fatia
landada.

### Onda 2 — Extermínio stub/fallback/silenciamento

1. Detector canônico: gate `silent-failure` + sweep `ast-grep` para `try/except` como
   lógica, `except: pass/return None/return {}`, defaults silenciosos,
   `# type: ignore`/`# noqa` sem justificativa documentada.
2. Correção por causa raiz: erros propagam; `r.Fail` SOMENTE no boundary `e`/`u`; sem
   fallback/compat/shim/old+new; exceção primeira escapa com traceback no CLI.
3. Regras recorrentes viram regra `ast-grep` registrada (ADR-014, `make mod`) — a
   automação é parte da entrega.

### Onda 3 — Revalidação de testes (runtime manda)

1. Sweep: tests que validam funções privadas/estrutura interna/"como é feito",
   mocks/fakes do sistema sob teste, valores hardcoded donos do config/settings (P0 do
   AGENTS.md).
2. Conversão para comportamento+runtime: `tm.that` em facades públicas, fixtures
   `c/t/p/m/u` tipados, contratos lidos do SSOT tipado (nunca congelar valores de
   config), consumidor real para artefatos gerados antes de gates estáticos.
3. `make test <repo>` verde por fatia; infra: timeouts -15/-9 tratados por §8.4 do
   handoff (renovar evidência, sem inflar timeouts).

### Onda 4 — Fechamento e publicação

1. `make check` raiz 32/32 exit 0; `make test` 32/32 exit 0 (exceções: apenas gate
   custom com evidência agregada aceita).
2. `make build` + `make docs` exit 0; `make gen` ponto fixo final.
3. PRs por repo lesionado (native gates; SEM bypass; merge `--no-ff` somente com CI real
   verde no SHA); gitlinks finais; push.
4. Beads: fechar `flext-c4k44`/`flext-itpd1.1` + reconciliar obsoletas tocadas; criar
   beads P1.
5. Docs/ADRs/skills: runbook atualizado com as lições (lazy relative resolution,
   venv-skew, nested workspace, journal CAS); ADR-014 ganha as novas regras ast-grep;
   `flext-law` SKILL atualizado com contrato metadata-mint (`bd init` + SSOT align).
6. **PONTO DE FINALIZAÇÃO**: superprojeto pushed no tip com todos os gitlinks apontando
   para SHAs verdes; relatório final com tabela repo→SHA→gates→evidência nos beads.

## P1 (pós-P0, enfileirado em beads — NÃO nesta sessão)

- Automação namespace por templates (violações recorrentes → gerador/codemod).
- Sweep DRY/YAGNI profundo de reuso `c,t,p,m,u` além dos gates (god components,
  duplicação semântica).
- Reconciliação do backlog beads (286 abertas); retirement de worktrees/branches
  absorvidas (7 lanes raiz + 3 infra, `/tmp/fic-85b`,
  `.claude/worktrees/bugfix+stabilize-0.12.0`).
- Auditoria dos ~23 patches Copernicus em `~/.claude/plans/` (provavelmente contidos nos
  merges).

## Regras de execução (bind para o agente implementador)

- Todo `bd` via `direnv exec <repo> bd ...`; cidade em `~/gc` (porta do
  dolt-state.json).
- Verbos Make canônicos apenas; ferramenta quebrada = defeito no owner a corrigir e
  re-rodar por ela.
- Subagentes: explore (mapear) + code (implementar fatia); main coordena efeitos
  sequenciais (commit/merge/push/bead).
- Ferramentas: `code-review-graph` para mapeamento por grafos; `ast-grep`+`make mod`
  para reescritas estruturais; Context7 MCP para referência pydantic/PEP quando
  necessário.
- Concorrência: fix-forward adopt (nunca reset/stash/descartar); CAS rejeita gen
  concorrente = aguardar ciclo do outro ator (comportamento correto).
- Evidence-first: nenhuma afirmação "verde" sem comando+exit+saída decisiva no mesmo SHA
  do código.

## Riscos / atenuações

- **Ator concorrente ativo em flext-infra/flext-api** → coordenar por absorção; commit
  cedo (Onda 0) para reduzir janela de conflito; nunca editar arquivos que ele tem
  abertos (validar mtime/status antes).
- **result.py TYPE_CHECKING pode não matar a classe mypy** → validar primeiro em
  flext-api; se falhar, a correção real é covariância nas assinaturas do
  protocolo/consumidores — sem `type: ignore`.
- **require-future-annotations em arquivos gerados** → corrigir TEMPLATE no owner
  (flext-infra), regen; nunca hand-edit.
- **Escala (32 repos × N gates)** → fatias por repo com subagentes; uma classe de
  violação por wave; landar incrementalmente (push por repo verde).

## Validação final (aceite)

```
make setup && make gen && make gen        # 0, 0, 0 (ponto fixo)
make fix && make fmt && make check        # 0, 0, 0 (32/32)
make test && make build && make docs      # 0, 0, 0
git -C <repo> status                      # limpo nos 32
git -C <repo> log --oneline -1            # tip pushed (0/0 vs origin)
direnv exec . bd show flext-c4k44 --json  # evidência fechada
```
