# ai-hub / flext — Gate Convergence & Extermination Plan (P0 → P2)

Execução sempre sobre o **tip** (`origin/<integration-branch>`), **fix-forward/adopt** para qualquer trabalho paralelo, **bd via direnv**, testes validando **comportamento+runtime** (nunca o "como"). Remoção total de stubs, fallbacks e silenciamento; reuso máximo de `c,t,p,m,u`; SOLID/DRY/YAGNI/SSOT/DI/CA/Pydantic/PEP.

## Estado atual (evidência da sessão)

- **ai-hub @ dev**: 6 commits à frente de `origin/dev` — `e288e8ac6`, `43d18f297`, `d30858791` (daemon/schema fix) + `16f6d0780`, `369c2d47e`, `29848f2cc` (outro ator ADOPTOU meu WIP e completou).
- **Check**: 72 → ~23 violações após ondas adotadas; minha onda NÃO commitada: 10 constantes ENFORCE-079 migradas (portable `GIT_REF_FORBIDDEN`, renderer `MANAGED_TOP_LEVEL_KEYS` dedup, commands_toml `CANONICAL_ARGUMENTS`, scan `WORKTREE_LINE`, ccg_hooks `TERMINAL_STATUSES`, continuous_green `PYTEST_MODULE`, mcp_catalogs `AMBIENT_PROBE_TIMEOUT_SECONDS`, agent_law `AUDIT_FILE_BYTES`, native_models `FORMAT`×2 via decomposição polimórfica `_parse_pair`/`_alias_path`/`_dump_mapping`), maintain NS-CONTRACT dicts→`t.MappingKV`/`t.MutableMappingKV`, models `MaintainIndexEntry`/`MaintainIndexProject`/`MaintainContextIndex`.
- **4 testes falhando**: `test_aihub_hooks_governance_config` ×3 + `test_aihub_governance_projection::test_toml_commands...` ×1 — diagnosticar se é meu rewiring de `CANONICAL_ARGUMENTS` ou WIP do outro ator.
- **Outro ator ATIVO** (não tocar nos dirty dele): `probe.py` (aliases `HttpxAsyncClient`/`HttpxResponse`/`HttpxRequestError` indefinidos — refactor em curso), `validation.py`, `tests/fixtures/hook_client_runtime.py` (removeu `import sys`, deixou usos — F821).
- **flext-infra**: tip `57ca284c8` (fix $HOME direnv + conform import); WIP sujo persiste.
- **hook_client.py (ADR-0018)**: arquivo stdlib-only é exceção declarada; gates sem a isenção: silent-failure ×4, boundary ×2 (`sys.exit`/`json`), NS-CONTRACT ×5 (anotações `dict`/`object`), ENFORCE-079 `_INVOCATION_KEYS`; `pyrefly :114` (container vazio — corrigível in-file).
- **Bug mypy conhecido**: class-attr type aliases quebram narrowing de `isinstance` → padrão seguro: dispatch via `except` (precedente `release.py:422`) ou module-level owner aliases (abordagem do outro ator em `16f6d0780`).
- **Subagentes instáveis** hoje (resultado vazio/idle timeout): 1 retry, depois inline.
- **smell_function_parameters ×13** pendente (deploy cutover ×2, forge ×3, host_runtime ×1, installed_runtime ×2, model_pipeline ×3, release_wheel ×1, validate_mcp ×1).
- Daemon model-pipeline: CORRIGIDO (gen 4 publicado, schema c7da7a sincronizado, bead `flext-ulckf` fechado).

## Invariantes (toda tarefa)

1. Base = tip: `git fetch origin` antes de cada onda; integrar via `git merge --no-ff`; NUNCA rebase/reset/stash trabalho compartilhado.
2. Trabalho concorrente = input de outro ator: adotar por commit (padrão `369c2d47e`), nunca sobrescrever dirty alheio.
3. `bd` com direnv (BASH_ENV não-interativo — caminho já provado).
4. Runtime define comportamento; testes são evidência, não SSOT.
5. Zero stub/fallback/silenciamento; `# type: ignore`/`# noqa` só com justificativa documentada; sem comentários; inglês; ≤200 LOC lógicos/módulo; LOC líquido negativo em refactor.

---

## P0 — Estabilizar e pousar ai-hub (check verde + push)

1. **Diagnosticar e corrigir os 4 testes falhos** (raiz): rodar cada um com `-x`; verificar rewiring de `CANONICAL_ARGUMENTS` em `commands_toml.py`; se os 3 `hooks_governance_config` vêm do fixture WIP do outro ator, coordenar/adotar, não sobrescrever.
2. **hook_client.py:114** pyrefly container vazio — corrigir in-file (tipado stdlib).
3. **Adotar probe.py/validation.py/fixture** do outro ator (lane dele): se estagnado >30min, completar o refactor de aliases module-level dele via fix-forward.
4. **probe.py:294 unreachable**: verificar fix dele; se persistir, early-return no `except` (latência/observed_at computados dentro do except antes do return).
5. **flext-infra — isenção ADR-0018 bornecada** para `src/ai_hub/hook_client.py` no OWNER do gate (após WIP dele pousar, `merge --no-ff` primeiro):
   - `BOUNDARY_SKIP_PATH_FRAGMENTS`-style fragmento de path + skip no detector silent-failure + `exempt_files` config-driven no namespace validator (seguir precedente `scan_dirs` cosmos-3flk9 decisão A) + skip ENFORCE-079 no census.
   - Cada isenção cita ADR-0018 itens 6-7; teste do mecanismo de isenção; commit scoped.
6. `make check` → 0 erros ai-hub (exceto itens de lane alheia em curso); `make test` verde.
7. Commit em ondas scoped: (a) constantes+native_models+maintain; (b) fixes de teste; (c) config de isenção. Push FF `origin/dev`.
8. **bd**: bead "ai-hub gate convergence P0" com evidência (comandos, exit codes, SHAs); fechar após push.

## P1 — Extermínio e otimização (novos commits no tip)

1. **smell_function_parameters ×13** — decompor com models de domínio reais (NUNCA param-bag): deploy cutover → contexto tipado `m.*`; forge `_mutate_github_json`/`_mutate_release` → payload models; probe `_typed_target` → target builder model; daemon `_run_locked_cycle` → cycle context. **ast-grep** inventaria call sites; **code-review-graph** blast radius antes de cada corte.
2. **Sweep stub/fallback/silenciamento**: ast-grep patterns — bare `except`, `except: pass/return`, `unwrap_or(sentinel)`, `contextlib.suppress`, `or {}`/`or []` como fallback (fora hook_client ADR) → propagar `r.Fail` tipado no boundary `u/e`.
3. **Sweep reuso máximo**: `rg` reimplementações locais de helpers `u.Cli`/`u.Infra`/`r.*`/`m.*` (json/toml/atomic/path); consolidar no owner; LOC líquido negativo.
4. **PEP/FLEXT polish**: zerar pyrefly/mypy/pyright restantes; `ClassVar`→`Final` onde imutável.
5. **Idempotência canônica**: após tip do flext-infra no lock (`uv sync` → flext-infra @0.12.0-dev tip), provar `make gen` fixed-point (diff vazio) e `make fix`/`make fmt` no-op exit 0.
6. **Revalidação de testes** (transição para P2): inventariar `tests/` com rg — `mock|patch|MagicMock|monkeypatch|_private|literais hardcode de valores do config` → reescrever para comportamento+runtime via facades + fixtures `tm`; sem asserts de construção interna; mesmos gates que `src/`.
7. Cada onda: commit+push incremental; bd atualizado; documentar isenção ADR-0018 no ADR; atualizar docs/skills (flext-development: padrão exemption + owner-alias mypy).

## P2 — Propagação fleet (workspace flext)

1. Superprojeto: bump gitlinks dos submódulos aos tips empurrados; `make setup/gen/fix/fmt/check/tests` a partir da raiz.
2. Gates dos membros verdes; gitlinks só após push dos membros verificado remotamente.
3. Beads do fleet com evidência de SHA.

## Tooling (mandato)

- **ast-grep**: inventário estrutural antes de cada cutover (registrar comando+resultado).
- **code-review-graph**: blast radius antes de decomposições.
- **Make verbs** apenas para gates; diagnósticos per-file diretos só para leitura.
- **Subagentes**: ondas paralelas em conjuntos disjuntos de arquivos; 1 retry em resultado vazio; senão inline.
- **bd + direnv** sempre.

## Validação (por onda)

- ruff/pyrefly/mypy/pyright per-file → `make check`.
- `pytest -k <domínio>` → `make test` completo antes do push.
- `make gen`/`fix`/`fmt` idempotentes (segunda rodada = no-op).
- Push só verde; registrar SHA no bead.

## Questões abertas

- Janela de coordenação flext-infra: se WIP do outro ator travar a isenção >1h, pousar ai-hub P0 (itens 1,2,4,6,7,8) primeiro, isenção depois.
- Propriedade dos 4 testes falhos (meu rewiring vs fixture dele) — diagnosticar primeiro; adotar conforme.

## Condições de parada

- ai-hub: `make check` 0 erros; `make test` verde; gen/fix/fmt idempotentes; pushado no tip `origin/dev`.
- flext-infra: isenção bornecada+testada, pushada no tip `origin/0.12.0-dev`.
- Beads/ADR/docs/skills atualizados com evidência.
