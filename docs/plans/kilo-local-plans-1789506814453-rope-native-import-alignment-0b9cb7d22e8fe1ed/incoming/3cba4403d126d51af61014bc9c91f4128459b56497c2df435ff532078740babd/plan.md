# Alinhamento de imports rope-native (substitui a fase libcst do plano lazy-init)

## 1. Diretriz do operador (2026-09-15, lei vigente)

1. Exterminar engines baseadas em `re`, `ast` e `libcst` — superfícies canônicas:
   **engine rope**, **make mod (ast-grep + sed)**, **regras parametrizadas como dados**
   (config: `enforcement.rules`, `tooling.yaml`, `codemod/rules/*.yml`).
2. Manter: regras beartype em runtime de flext-core, make mod, engine rope.
3. Engine força formas diretas, sem workarounds nem aliases de compatibilidade (já
   banidos por `ban-compat-alias.yml` / `ban-private-import.yml`).
4. Uma única CLI canônica com dry-run e toggles de componentes por config — `make mod` /
   `flext_infra refactor mod` é a superfície (seletor-free; toggles = dados, nunca flags
   ad-hoc).
5. ai-hub como cobaia em escala; fix-forward adopt com múltiplos agentes; atualizar
   skills/docs/ADRs/beads e compartilhar no board.
6. Padrão gerado 100% lint-free; cada ciclo corrige integralmente ruff, pyrefly e coleta
   pytest; regra raiz sempre identificada; parar e perguntar só se não houver composição
   correta.

## 2. Evidência do estado atual (reidratada, fix-forward)

| Fato                                                                                                                                                                                   | Local                                                                                        | Prova             |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------- |
| Engine rope de imports já canônica: `ModuleImports`, `from_import(module, level, pairs)`, reescrita por `import_info`, `sort_imports`, `get_changed_source`, padrão violação→reescrita | `flext-infra/src/flext_infra/_utilities/rope_imports.py`                                     | leitura completa  |
| Loop de fases rope do mod com `_apply_plan` + `_check_residue` (convergência a resíduo zero) e callbacks no fingerprint de progresso                                                   | `codemod/semantic_apply.py`                                                                  | leitura           |
| Regras parametrizadas ast-grep + utils SSOT + testes snapshot                                                                                                                          | `codemod/rules/*.yml`, `codemod/utils/*.yml`, `sgconfig.yml`, `codemod/tests/`               | leitura           |
| Regras de enforcement como dados ("detector owns no policy")                                                                                                                           | `config/infra.yaml` `enforcement.rules`                                                      | leitura           |
| Política de camadas já SSOT (T3 landed): `lazy-init.import-layer-order` + `reverse_import_mode` + `forward_import_form`                                                                | `config/tooling.yaml:711-730`, `_models/deps_tool_config.py:620-672`                         | leitura           |
| Integração lazy-init↔alignment commitada por ator concorrente (eb6a03131) apontando p/ mixin libcst                                                                                   | `codegen/lazy_init.py:20,27-31,190-212`                                                      | git log + leitura |
| Rascunho libcst a exterminar (não commitado)                                                                                                                                           | `codegen/_lazy_init_import_alignment.py`, `codegen/_lazy_init_import_layers.py`              | git status        |
| Facade rope-AST sancionado (sem `import ast` no consumidor; flext-6flt)                                                                                                                | `_wrapper_rewrite.py:20-24`, `FlextInfraUtilitiesRopeRuntime`                                | leitura           |
| Resíduos `ast`/`libcst` existentes fora do escopo desta fatia                                                                                                                          | `rope_imports.py:5,344`, `refactor/project_alias_migrator.py`, `transformers/*_cst.py`, etc. | grep              |
| Superfície mod: `make mod` → `refactor mod --apply` (escopo = cwd; dry-run = scan sem apply)                                                                                           | `Makefile:736-742,1199-1202`                                                                 | leitura           |
| Trabalho concorrente a adotar (não tocar): `cli_routes_refactor.py`, `dataclass_modelizer.py`, `__init__.py`                                                                           | git status flext-infra                                                                       | leitura           |

## 3. Decisões de design

**D1 — Engine rope-native única (extermina libcst).** O dono é
`FlextInfraUtilitiesRopeImports`:

- **Detecção**: sobre o workspace index rope (mesmo índice do lazy-init, ADR-007),
  classificar cada statement de import (`get_module_imports` + `imported_module_paths`,
  que já resolve níveis relativos) contra os ranks da ordem SSOT
  (`config.Infra.tooling.lazy_init.import_layer_order`). Ranks desconhecidos → tier
  `services` (plano D3). Violações = dados tipados (`m.Infra.ImportAlignmentViolation`):
  `reverse_import` (rank alvo > rank fonte) e `non_relative_forward` (rank alvo < rank
  fonte em forma absoluta).
- **Escopo semântico** (não é enfraquecimento): só módulos na árvore do pacote do
  projeto (`module_name` sob `project_package`); skip de `__init__.py` gerado (header
  AUTOGEN), de imports na fachada-raiz (`from <pkg> import ...` — forma canônica da
  frota), de imports dentro de bloco `if TYPE_CHECKING:` e de imports aninhados
  (função/try/if — idiom lazy/deferred legítimo). tests/scripts/examples são
  consumidores fora da árvore: não criam ciclo interno.
- **Reescrita forward**: reatribuir
  `import_stmt.import_info = from_import(tail, level=ups, pairs)` (padrão já
  estabelecido em rope_imports) + `remove_duplicates` + `sort_imports` +
  `get_changed_source` + `resource.write`.
- **Reescrita reverse→TYPE_CHECKING**: remover o statement via rope
  (`imports_list.remove`) e reinseri-lo dentro de `if TYPE_CHECKING:`;
  `from typing import TYPE_CHECKING` garantido via `add_import` quando ausente. A
  localização/edição do bloco usa spans computados pelo facade rope-AST (`RopeRuntime`),
  sem `re`/`ast`/`libcst` no nosso código; o splice é o mesmo ato de `sed` sancionado
  pelo make mod. Idempotência: segunda passada não vê violação (import relativo →
  level>0; import em TC → skip por span).
- **Membros mistos na mesma linha** (`import a; from b import c`): dividir a linha
  (parte fica, parte migra) — semântica preservada, sem silenciar violação.

**D2 — Dois pontos de entrada canônicos, uma engine.**

- `make mod` (loop rope): nova fase `import-alignment` em `semantic_apply.py` com
  `_apply_plan` + `_check_residue` (2ª passada = zero resíduo) e callback incluído no
  fingerprint de progresso.
- `make gen` (conform): o planner lazy-init consome o MESMO planner rope
  (`plan_import_alignment`) e publica `CodegenFilePlan`s pela fase lazy-init (D2/D4 do
  plano original preservados; conteúdo vem do rope, não de libcst).

**D3 — CLI única, toggles por config, dry-run nativo.** Nenhuma flag nova na CLI:
`tooling.yaml` ganha `mod.phases.import-alignment: true` (toggle de componente como
dado; política segue ADR-005). Dry-run = `make mod` em modo scan (sem `--apply`) — já
existe na superfície `refactor`; verificação em T5.

**D4 — Extermínio com escopo bounded (lei 13/23).**

- Esta fatia: deletar `_lazy_init_import_alignment.py` (rascunho libcst) +
  `_lazy_init_import_layers.py`; rewirar `lazy_init.py` para o planner rope (fix-forward
  no arquivo commitado).
- Épico rastreado (beads, fora desta fatia): migração dos resíduos `ast`/`libcst`/`re`
  restantes (`project_alias_migrator`, `transformers/*_cst.py`, `tier0_import_fixer`,
  `class_nesting_cst`, `compatibility_alias_cst`, `_wrapper_rewrite`,
  `rope_imports._referenced_runtime_aliases` etc.) para rope/facade, um bead por owner,
  net-LOC negativo.

**D5 — Regras parametrizadas.** A parametrização desta lei é DADO: `tooling.yaml` (ordem
de camadas, modos) + modelos de violação validados. Regras ast-grep novas somente para
bans estaticamente expressíveis identificados na execução (cada uma com snapshot test em
`codemod/tests/`); nada de detector com policy embutida.

**D6 — Cobaia ai-hub em escala.** Resolução provada (task de exploração, 2026-09-15):
ai-hub vive em `~/ai-hub` (standalone, branch `dev`, árvore dirty: 29 modificados + 1
não rastreado) e seu `.venv` tem `flext_infra` instalado **editable** apontando para
`~/flext/flext-infra/src` (`_editable_impl_flext_infra.pth`) — o mesmo no venv raiz do
workspace. O pin remoto em `pyproject.toml`/`uv.lock` é inerte em runtime. Comando
canônico da cobaia: `cd ~/ai-hub && make gen` (=
`ai-hub/.venv/bin/python -m flext_infra codegen conform --root ~/ai-hub --scope self --mode apply`),
que executa a árvore flext-infra LOCAL não-commitada. Não existe verbo `PROJECT=` na
raiz do workspace para gen de membro único. Rodar com árvore quieta e escritores
serializados; adotar o WIP dirty por fix-forward (nunca reset); `gen` ×2 (1ª: efeitos
init+alinhamento; 2ª: 0), `mod` ×2, `pytest --collect-only -q` exit 0 (prova
anti-ciclo), smoke de runtime (ai_hub.AiHub, c/m/p/t/u, services),
`make check`/`make test`; defeitos de módulo expostos (D5 do plano original) corrigidos
na causa, nunca na engine.

## 4. Tarefas (ordenadas, cada uma verde ao fim do ciclo)

**T0 — Verificação de API rope** (sem mutação): introspecção da rope instalada
(`ModuleImports`, spans de statement, comportamento com bloco `if TYPE_CHECKING:`),
registrada como evidência no plano; define o mecanismo exato de span/bloco da D1.

**T1 — Extermínio do rascunho libcst + rewire** (D4): deletar os 2 arquivos;
`lazy_init.py` passa a chamar o planner rope (assinatura: workspace index + config
SSOT); `u.Infra.codegen_file_requires_effect` continua filtrando efeitos. Gates:
ruff/pyrefly/pyright/mypy (bounded) zero no escopo tocado.

**T2 — Detecção + modelos** (D1): `m.Infra.ImportAlignmentViolation` + classificador no
rope workspace (`_utilities/`), política 100% de config; testes de comportamento
(workspace tmp via `tm`/flext-tests, sem mocks): forward→relativo, reverse→TC,
fachada-raiz intocada, aninhado intocado, gerado skip, ordem lida do SSOT (nunca
congelada — P0).

**T3 — Reescrita rope** (D1): métodos em `FlextInfraUtilitiesRopeImports`
(`align_module_imports(rope_project, resource, *, order, source_module, project_package, apply)`);
splices TC idempotentes ×2; testes snapshot de formas.

**T4 — Integração mod + gen** (D2/D3): fase `import-alignment` em `semantic_apply.py`
com convergência zero-resíduo + callback; toggle `mod.phases.import-alignment` em
`tooling.yaml`; planner lazy-init publicando CodegenFilePlans; teste "um único plano por
arquivo, ×2 no-op".

**T5 — Gates integrais do ciclo** (diretriz 6): `make setup`, `make fix`, `make fmt`,
`make check` (ruff, pyrefly, pyright, mypy capped, smells, codemod, loc-cap…),
`make test` em flext-infra — TODOS os achados corrigidos na causa no mesmo ciclo;
`make gen` ×2 com 2º = 0 efeitos; proibidoollow-up de warning.

**T6 — Cobaia ai-hub** (D6): caminho provado — `cd ~/ai-hub && make gen` resolve o
flext-infra LOCAL via editable install; antes: serializar escritores
(`ai-hub-watch.service` parado/árvore quieta) e inventariar o WIP dirty (29 arquivos)
para fix-forward; sequência: `gen` (1ª: efeitos) → `gen` (2ª: 0) → `mod` ×2 → correção
na causa dos módulos com dependência reversa real → `pytest --collect-only -q` exit 0 →
smoke runtime → `make check`/`make test`; evidência: comando + cwd + exit code + saída
decisiva; commits escopados por caminhos; PR → `dev`; re-run de gates no SHA merged.

**T7 — Conhecimento vivo + coordenação** (diretriz 5): ADR-014 emendado (lei rope-native
de alinhamento + ledger de extermínio re/ast/libcst com beads); AGENTS.md raiz
§Architecture (forma canônica de imports); `docs/standards/development.md`; skills
`flext-law` e `flext-development`; board post ALL com o design + decisões para os
agentes paralelos; memória persistida; beads: épico de extermínio + fatias.

## 5. Contrato de validação

| Comando (cwd)                                         | Aceite                                                     |
| ----------------------------------------------------- | ---------------------------------------------------------- |
| flext-infra `make check` / `make test`                | exit 0; zero achados ruff/pyrefly/pyright/mypy no escopo   |
| flext-infra `make gen` ×2                             | 2º `Lazy-init plan: 0 effects`                             |
| flext-infra `make mod` ×2                             | 2ª passada sem efeitos (resíduo zero)                      |
| testes T2–T4                                          | verdes; comportamento por fachadas públicas; ordem do SSOT |
| ai-hub `make gen` ×2 + `make mod` ×2                  | 1ª com efeitos; 2ª sem efeitos                             |
| ai-hub `.venv/bin/python -m pytest --collect-only -q` | exit 0 (anti-ciclo)                                        |
| ai-hub `make check` / `make test`                     | exit 0                                                     |

## 6. Riscos e bordas

- **Splice TC**: mecanismo depende da introspecção T0; se rope não expuser span
  confiável para o bloco, alternativa fail-loud: gate reporta a violação reverse sem
  auto-relocação, e a correção é fix-forward no módulo (D5) — decisão documentada, sem
  workaround silencioso.
- **Conflito com isort/ruff**: saída deve ser estável sob regras I; `normalize_imports`
  (rope+ruff I,F401) já é o compositor canônico — reutilizar.
- **WIP dirty em ai-hub (29+1 arquivos)**: gen roda sobre WIP de outros atores — adotar
  por fix-forward (re-ler, integrar, nunca resetar); aborto `atomic source changed`
  indica escritor concorrente → serializar e repetir.
- **Editable dual-venv**: qualquer mutação no working tree flext-infra afeta
  imediatamente TODA a frota que rode codegen neste host — gates flext-infra verdes
  antes de qualquer cobaia.
- **Multi-ator**: `cli_routes_refactor.py`, `dataclass_modelizer.py`, `__init__.py` são
  de outros atores — adotar, nunca resetar; edições em `lazy_init.py` re-lidas antes de
  cada mudança.
- **Fora de escopo**: regeneração dos demais 31 membros (beads T8 do plano original);
  migração integral dos resíduos ast/libcst (épico próprio, beads); novas features além
  do alinhamento.
