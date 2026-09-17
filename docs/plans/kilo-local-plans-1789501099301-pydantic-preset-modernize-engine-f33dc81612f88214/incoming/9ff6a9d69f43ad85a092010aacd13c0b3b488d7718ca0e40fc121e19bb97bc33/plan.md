# Modernize Pydantic via Rope: presets canônicos, CLI unificada e extermínio de engines re/ast/libcst

## Missão

Exterminar workarounds/aliases de compatibilidade Pydantic e rewire para formas diretas (`m.*` presets do flext-core), com a engine impondo a lei em nível workspace e projeto. Cobaia: **ai-hub** (`~/ai-hub`, branch `dev`, WIP alheio presente — fix-forward, nunca stash/reset/revert). Toda correção vira **regra parametrizada na engine** (catálogo flext-core + rules YAML flext-infra), nunca conserto pontual.

## Estado verificado (evidência)

- **Cobaia**: `ai_hub/_models/base.py` declara 6 bases locais em `m.BaseModel` + `u.ConfigDict` manual (`FrozenConfigModel`, `FrozenBoundaryModel`, `FrozenBinaryBoundaryModel`, `IgnoredBoundaryModel`, `SerializedBoundaryModel`, `MutableBoundaryModel`) → **482 referências em ~66 arquivos**. Docstring é workaround declarado (evitar ciclo de import / coerção YAML).
- **Owner de presets**: flext-core `_models/_base_parts/` (Tier 0). `MutableBoundaryModel` ≡ `m.StrictManagedModel` (existe). `FrozenConfigModel`/`SerializedModel`/`EnvelopeModel`/`BinaryModel` **não têm preset** → lacuna a fechar no flext-core (lei: preset faltante = fechar no dono).
- **CLI unificada já existe**: `FixEnforcementCommand` (`flext-infra/_models/check.py:118`) → `services/cli_routes_codegen.py:59` → `FlextInfraEnforcementFixerOrchestrator` (fixers/orchestrator.py) com `apply` (dry-run default), `rules=()` (toggle), `safe_only`, `check_after` e adapters `gate|manual|rope|transformer` (`_ADAPTER_CLASSES`). `make mod` = ast-grep + sed (`codemod/`: `sgconfig.yml`, `rules/*.yml` ~105 regras, `text_rules.yml`, `batch_apply.py`, `semantic_apply.py`).
- **Catálogo SSOT**: flext-core `_constants/_enforcement_catalog_rows_parts/*` (linhas BEARTYPE_ROWS `ENFORCE-XXX`) + `PREDICATE_BINDINGS` (`_utilities/_enforcement_parts/enforcement_part_01.py`) + `ENFORCEMENT_FIX_ACTIONS` (`_constants/_enforcement_parts/flextconstantsenforcement_part_08.py`) + montagem em `_utilities/_enforcement_parts/enforcement_part_04.py` (`_fix_action_for`, `build_canonical_catalog`). Runtime beartype: `ModelConfigParams` (`_models/_enforcement/_params.py`) + `field_visitor.v_model_config` (`_utilities/_beartype/field_visitor.py:185`).
- **Engines a exterminar (inventário)**: `import ast` em **39 arquivos** (gates: duplication, abstraction_boundary, silent_failure*, namespace_validator, deferred_self_reference*; transformers: pydantic_modernizer, typing_unifier, compatibility_alias, open_encoding, pattern, dataclass_modelizer, \_rewrite; detectors: consumer_import_violations, silent_failure, deferred_self_reference; `_utilities/*_ast.py`); `libcst` em **7 arquivos** (`compatibility_alias_cst`, `qualified_names`, `private_import_cst`, `class_nesting_cst`, `class_nesting_references`, `mro_remover`, `project_alias_migrator`, `codegen/_lazy_init_import_alignment`). **Não há** `config/rules/` em flext-infra ainda — regras ast-grep vivem em `src/flext_infra/codemod/rules/`.
- **Superfícies aprovadas (lei do operador)**: beartype runtime (flext-core), ast-grep + sed (`make mod`), rope. Proibidas para regras novas: `re`, `ast` cru, `libcst`.

## Decisões tomadas

1. **Novos presets em flext-core** (Tier 0, `_base_parts/flextmodelsbase_part_01.py`), nomes canônicos sem "Boundary" (vocabulário m.\*): `ConfigModel` (frozen+extra=forbid+populate_by_name, NÃO-strict — coerção YAML preservada), `EnvelopeModel` (frozen+strict+validate_default+extra=ignore+str_strip+populate_by_name), `SerializedModel` (FrozenModel+serialize_by_alias), `BinaryModel` (FrozenModel+ser/val_json_bytes base64). `populate_by_name=True` **aditivo** na raiz `ManagedModel` → `FrozenBoundaryModel` ≡ `m.FrozenModel`, `MutableBoundaryModel` ≡ `m.StrictManagedModel`.
2. **Regra nova `consumer_config_dict`** (ENFORCE-080+): beartype MODEL_CONFIG flag `forbid_local_config_dict` (violação quando `target.__dict__.get("model_config")` não-vazio fora do owner `flext_core._models`) + linha em BEARTYPE_ROWS + fix_action kind **`codemod`** (novo) apontando para regras ast-grep/sed parametrizadas.
3. **Regras de rewire como ast-grep/sed parametrizados**, nunca transformer python-ast novo: `rewire-consumer-preset-bases.yml` (bases + model_config → preset) + sed para as 482 refs de nomes locais → nomes de presets. Parâmetros (mapa assinatura→preset) em **`flext-infra/config/rules/preset-rewire.yaml`** (novo SSOT parametrizado).
4. **CLI única**: estender `FixEnforcementCommand` com `components: tuple[str, ...]` (toggle: `beartype|astgrep|sed|rope|gates`) + novo adapter **`CodemodFixerAdapter`** (kind `codemod`) que roda o batch ast-grep/sed existente no mesmo loop rope (projeto rope aberto uma vez, callback por arquivo, um relatório). `make mod` e `fix` continuam como verbos públicos da MESMA CLI. Dry-run = `apply=False` (já suportado).
5. **Extermínio por ondas** (cada onda = 1 bead + ciclo 100% verde), ordem: (W1) transformers de mutação raw-ast/libcst; (W2) detectors `_utilities/*_ast.py`, `*_cst.py`; (W3) gates raw-ast → ast-grep/rope/beartype; (W4) banir reimports (`ban-raw-ast-parser`, `ban-libcst-import`, `ban-re-parse` como regras ast-grep + beartype) e apagar engines mortas.

## Plano de execução (ondas fechadas — cada uma termina ruff + pyrefly + coleta pytest 100% verdes)

### Onda 0 — Coordenação e baseline (paralela, agora)

- Board: missão + divisão de streams (main=presets/regra/catalogo; agente A em curso=flext-tests uniões inline; agente B=baseline gates ai-hub + inventário re/ast/libcst tabela por arquivo com disposição; agente C=CLI unificada + CodemodFixerAdapter + config/rules).
- Beads: 1 bead épico por onda (W1–W4) + bead cobaia ai-hub; claim/update a cada mudança de estado de repo.

### Onda 1 — Presets no dono (flext-core) — main

1. `_base_parts/flextmodelsbase_part_01.py`: `populate_by_name=True` em `ManagedModel`; presets `ConfigModel`, `EnvelopeModel`, `SerializedModel`, `BinaryModel` (estilo do arquivo, `ClassVar[mp.ConfigDict]`, docstrings, inglês, sem comentários novos).
2. Testes unitários em `flext-core/tests/unit/_models/` (comportamento: frozen, extra, populate_by_name, coerção não-strict do ConfigModel, base64 do BinaryModel) — lendo expectativas dos próprios presets, sem hardcode de valores de config (P0).
3. Gates: `make check PROJECT=flext-core` + `make test PROJECT=flext-core` (subconjunto unitário se runtime global estiver vermelho por WIP alheio — registrar no bead).

### Onda 2 — Regra runtime + catálogo — main

1. `ModelConfigParams.forbid_local_config_dict: bool = False`; branch em `v_model_config` (exempt: `target.__module__.startswith("flext_core._models")` — fronteira de ownership documentada).
2. `PREDICATE_BINDINGS["consumer_config_dict"]` (enforcement_part_01) + linha BEARTYPE_ROWS ENFORCE-080 + `ENFORCEMENT_FIX_ACTIONS["ENFORCE-080"] = {kind: "codemod", target: "rewire-consumer-preset", params: {sg_rules: [...], sed: {...}}, safe: true}`.
3. Testes: violação detectada em classe consumidora (fora do owner), owner isento.

### Onda 3 — Regras parametrizadas + CLI única (flext-infra) — agente C + main

1. `flext-infra/config/rules/preset-rewire.yaml`: mapa `signature→preset` (SSOT parametrizado lido pelo codemod batch).
2. Regras ast-grep: `rewire-consumer-preset-configdict.yml` (class base + model_config → preset) e `rewire-consumer-preset-refs.yml`; sed para refs de nomes (fonte: config YAML).
3. `CodemodFixerAdapter` (kind `codemod`) em `fixers/` + registro em `_ADAPTER_CLASSES`; `FixEnforcementCommand.components` + `_command_ctx`; loop rope unificado com callback por arquivo (um projeto rope, relatório único).
4. Gate de preflight do orquestrador passa a exigir adapter para kind `codemod` (já genérico).

### Onda 4 — Cobaia ai-hub (projeto-nível) — main + agente B

1. Verificar resolução do flext-core no venv do ai-hub (editável local vs git 0.12.0-dev); se git-pinned: pousar Onda 1–2 primeiro, `make setup` no ai-hub, então validar.
2. Dry-run: CLI única `mod`/`fix-enforcement` com `components=astgrep,sed,rope`, `apply=false`, `rules=ENFORCE-080` → relatório preview (482 refs / 66 arquivos).
3. Apply → `make check` + `make test` no ai-hub (ruff/pyrefly/coleta pytest 100%); `_models/base.py` fica só com utilitários legítimos (validators compartilhados), 6 bases exterminadas sem alias de compatibilidade.
4. Commit escopado por projeto; beads atualizados com evidência (comando, exit code, contagens).

### Onda 5 — Extermínio das engines re/ast/libcst — ondas W1–W4 (streams paralelos, 1 bead cada)

- W1 transformers (pydantic_modernizer, typing_unifier, compatibility_alias, open_encoding, pattern, dataclass_modelizer, \_rewrite, mro_remover(cst), project_alias_migrator(cst)): recompor como regras ast-grep (rewire) ou rope (quando precisar de resolução semântica); registrar no `_TRANSFORMERS` apenas os que sobrevivem via rope.
- W2 detectors `_utilities/*_ast.py`, `*_cst.py`, `qualified_names`, `class_nesting_*`: ast-grep + rope-semantic.
- W3 gates (duplication, abstraction_boundary, silent_failure*, namespace_validator, deferred_self_reference*): ast-grep/rope/beartype, mantendo assinatura do gate no `make check`.
- W4: regras de banimento (`ban-raw-ast-parser`, `ban-libcst-import`, `ban-re-parse`) + remoção dos módulos mortos + `libcst` sai das dependências se órfã.

### Onda 6 — Conhecimento e fechamento

- Atualizar no MESMO ciclo de cada onda: skill `pydantic-development` (novos presets + regra consumer-preset), `flext-law`/AGENTS.md (lei de superfícies de regra: beartype+ast-grep+sed+rope; proibidas re/ast/libcst), ADR novo (ADR-015: "Parametrized rule surfaces & single modernize CLI"), docs/guides.
- Board: resultado por onda com evidência; aprendizados compartilhados.

## Validação (por ciclo, inegociável)

- `make check PROJECT=<afetado>` (lint=ruff, pyrefly, pyright) e `make test PROJECT=<afetado>`; coleta pytest sem INTERNALERROR.
- Workspace: `make check` global ao fechar cada onda.
- ai-hub: `make check` + `make test` no projeto (nível projeto), depois `mod` dry-run→apply.
- Erros de WIP alheio (ex.: FlextMroViolation de flext-tests) são adotados e corrigidos no dono (fix-forward), nunca contornados.

## Riscos e mitigations

- **flext-core git-pinned no ai-hub**: pousar ondas 1–2 e re-sincronizar antes do apply na cobaia (verificar resolução real antes).
- **`populate_by_name` aditivo na cadeia**: aceita field-name além de alias — mudança aditiva; rodar testes de settings/config do workspace para provar.
- **ConfigModel não-strict**: deliberado (coerção YAML é o contrato da cobaia); documentado no preset; `EnvelopeModel` mantém extra=ignore por contrato de envelope externo existente (comportamento preservado).
- **Extermínio W1–W4 é programa multi-sessão**: beads por onda com escopo fechado; nada fica pela metade dentro de uma onda (senão não fecha o ciclo).
- **Conflito multi-agente**: regra fix-forward no board; rebase proibido; adoção do estado atual do arquivo antes de editar.

## Fora de escopo (explícito)

- Migrar consumidores além da cobaia (outros flext-\*) nesta sessão — vira beads de follow-up após padrão provado na cobaia.
- Trocar o verbo público `make mod`/`fix` por CLI nova — a unificação é interna à CLI existente.
