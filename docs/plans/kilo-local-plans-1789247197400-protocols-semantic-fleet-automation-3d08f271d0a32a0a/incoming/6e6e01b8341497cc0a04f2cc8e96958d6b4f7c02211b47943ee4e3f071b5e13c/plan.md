# Automacao de protocols e rewiring da topologia governada

## Objetivo e limite

Recuperar e completar a iniciativa de protocols derivados de models usando o flext-infra atual. Estender census, Rope, codegen e o circuito make mod/ast-grep, sem criar outro motor. Detectar desvios arquiteturais do contrato abaixo, corrigir automaticamente todos os casos cuja preservacao semantica seja demonstravel e propagar a alteracao para os consumidores governados. Casos nao resolvidos permanecem bloqueantes; nao sao sucesso, supressao ou tarefa silenciosamente descartada.

Escopo confirmado pelo operador: topologia governada atual, incluindo src, tests, examples e scripts. Derivar projetos e dependencias do dono atual da topologia, nunca de uma lista congelada ou dos caminhos externos citados em estudos antigos. Consumidores externos conhecidos sao limites explicitos de cobertura; nao escrever fora da topologia. Nao prometer descoberta de consumidores externos desconhecidos. Forks e vendor permanecem fora das regras arquiteturais FLEXT. Gas-city nao sera ativado.

**Decisão do operador (2026-09-12):**

- `scope` / `scope-nav` está **aposentado** — tudo relacionado a ele no repositório pode ser exterminado (referências em skills, configs, regras, docs).
- **Apenas `code-review-graph`** será usado para mapeamento via grafos (call/import/impact/dead-code/architecture).
- **USAR OS PADRÕES CANÔNICOS FLEXT E PYDANTIC NÃO É OPCIONAL** — é o único caminho aceito. Toda mudança deve ser precedida de pesquisa profunda dos padrões atuais no código vivo; nada é deduzido.

Esta entrega é planejamento, não implementação. Nao foram executados gates nem criada evidencia de funcionamento do novo fluxo. A implementação requer agente com permissão de escrita em código. Beads deve ser reconciliado na entrada da implementação; nenhuma bead antiga é considerada aberta, concluída ou autorizada apenas pelo histórico.

## Historico recuperado

| Fonte                                               | Evidencia e uso                                                                                                                                     |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| flext-infra PR #47                                  | Base 0.20.0-dev em ca3b021e469d324829d29f3be38d7d0a87ba2019; PR fechado sem merge; SHA coincide com gitlink da branch antiga do superprojeto        |
| infra 19debb7d41e3ccbb32c5a810d5831565c261779c      | docs/superpowers/plans/2026-07-16-codegen-protocol-generation.md; plano de 10 tarefas, bead mro-iqzh                                                |
| infra 6db292bed7ce56b562804ec3a1bf22b835054152      | Task 1: config, schema e teste; nao comprova conclusao do gerador                                                                                   |
| infra c038e5a5a / 83af97d43 / 3dcdc21f3             | Espelhos de modelos e configuracao, mro-qc84; 83af97d43 adicionou 58 protocols em arquivo de 1391 linhas                                            |
| infra 56afe17032928c429a59c9f51cf887011c760448      | Restauracao de espelhos, mro-dxrp.3.1-.3.5                                                                                                          |
| core PR #403, 224144384                             | Auditoria docs/improvements/protocols-pydantic-solid-audit-pt.md: ISP/DIP, validacao nas bordas, evitar introspeccao privada e contratos implicitos |
| core 50b021133                                      | Estudo de eficiencia Python 3.13/Pydantic; nao e especificacao suficiente de um codemod seguro                                                      |
| infra 50d22cb5f / 67953765b / f70bb06b6 / b2d8faad1 | Correcoes de seguranca: spans de anotacao, locais nao sao interfaces, preservar mutacao, nao ampliar retornos/declaracoes por analise local         |

Reutilizar intencao e evidencias, nao copiar o codigo proposto em julho. O plano antigo continha retornos object fabricados, continue em falhas, writer direto, APIs por confirmar e testes que congelavam configuracao. O guia historico docs/type-system-architecture.md contem contradicoes e erros, incluindo Sequence dita invariante. Esses trechos nao fundamentam uma regra segura. Sequence e covariante; containers mutaveis normalmente sao invariantes. As mensagens de commits sobre gates sao historicas, nao validacao atual.

## Mapa estrutural do flext-infra (inventário 0.12.0-dev)

| Subsistema         | Arquivos | LOC    | Papel                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------ | -------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **codegen/**       | 55       | 14,383 | Pipeline de geração: conformance (pyproject.toml, .mise.toml), lazy init, journal mise, scaffolding, versionamento, pipeline, census/quality gates. Dono de seções `[MANAGED]` e facets.                                                                                                                                                                               |
| **\_utilities/**   | 114      | 26,980 | **Maior subsistema** — implementação compartilhada: Rope (analysis, imports, structure, runtime), git, namespace, pyproject, docs, protected edits, census, aliases, deferred self-ref, transformer base, versioning, worktree.                                                                                                                                        |
| **\_models/**      | 39       | 13,941 | Pydantic models puros (zero behavior) para todos subsistemas.                                                                                                                                                                                                                                                                                                          |
| **refactor/**      | 35       | 6,874  | Orquestração de refatoração: census rules/render, namespace enforcer, class nesting, accessor migration, modernize, classvar autofix, wrapper root, violation analyzer.                                                                                                                                                                                                |
| **detectors/**     | 20       | 2,771  | Detecção rope-semantic: class placement, compat aliases, consumer imports, cyclic imports, deferred self-ref, facade scanner, future annotations, import aliases, inline imports, internal imports, loose objects/tests, LSP diagnostics, manual protocols/typing, namespace source, private import bypass, runtime aliases, silent failures.                          |
| **validate/**      | 30       | 3,772  | Validação: namespace, import cycles, runtime census, lazy map freshness, loc delta, silent failure, skill validator, stub chain, tier whitelist, gate contract, inventory, scanner, pytest diag/testmon, cprofile, fresh import, metadata discipline, manual command.                                                                                                  |
| **gates/**         | 23       | 3,675  | Gates `make check`: abstraction boundary, bandit, budget, canonical alias, deferred self-ref, direnv, duplication, layout, loc cap, markdown, mypy, namespace, pyrefly, pyright, ruff format/lint, runtime census, silent failure, smells, tier whitelist.                                                                                                             |
| **deps/**          | 18       | 3,298  | Modernização de deps: detection, runtime detector, extra paths, pyrefly fixer, pyproject modernizer (fases: consolidate groups, ensure coverage/formatting/mypy/namespace/packaging/pydantic-mypy/pyrefly/pyright/pytest/ruff/vulture, inject comments), TOML phase.                                                                                                   |
| **transformers/**  | 23       | 3,050  | Transformers AST/rope: canonical t-import, census visitors, class reconstructor, compat alias, deprecated remover, future import, hardcoded version, import bypass, import modernizer, lazy import fixer, mro remover, open encoding, pattern, pydantic modernizer, signature/symbol propagator, tier0 import fixer, typing unifier, violation census visitor, smells. |
| **release/**       | 12       | 2,561  | Orquestração release: phases, dispatch, publish, artifact archive/build/execution/metadata/persistence/source, policy render.                                                                                                                                                                                                                                          |
| **workspace/**     | 10       | 2,324  | Serviços: detector, environment (beads, contracts, provenance), flext binding, orchestrator, rope workspace, governance.                                                                                                                                                                                                                                               |
| **\_constants/**   | 23       | 4,307  | Constantes por subsistema. Zero behavior.                                                                                                                                                                                                                                                                                                                              |
| **services/**      | 10       | 941    | CLI route composition: dispatch, routes (codegen, refactor, validate, workspace), route base.                                                                                                                                                                                                                                                                          |
| **fixers/**        | 7        | 2,145  | Adapters: base, gate fixer, orchestrator (enforcement), rope fixer, transformer fixer.                                                                                                                                                                                                                                                                                 |
| **docs/**          | 12       | 1,154  | Tooling: auditor, base service, builder, fixer, generator, server, validator, bundle, checks, report.                                                                                                                                                                                                                                                                  |
| **codemod/**       | 5        | 958    | Engine: batch apply/gates, semantic apply (ast-grep), snapshot reconciler. ADR-014.                                                                                                                                                                                                                                                                                    |
| **promoted/**      | 9        | 1,405  | Framework promoted command: header discovery, registry validation, help rendering, dry-run gating, process-boundary para `scripts/<verb>/<WHAT>`.                                                                                                                                                                                                                      |
| **check/**         | 4        | 755    | Workspace checker: workspace_check, gates registry/mixin, reports.                                                                                                                                                                                                                                                                                                     |
| **\_enforcement/** | 7        | 515    | Engine declarativo: collection base/sources, engine, metadata, selection. Catalog-backed (rules-as-data).                                                                                                                                                                                                                                                              |
| **maintenance/**   | 3        | 307    | Clean service, python version enforcer.                                                                                                                                                                                                                                                                                                                                |
| **\_protocols/**   | 8        | 1,771  | Protocol definitions: base, check, deps, docs, promoted, rope, rope_runtime.                                                                                                                                                                                                                                                                                           |
| **\_typings/**     | 4        | 242    | Type aliases (re-exports flext_core).                                                                                                                                                                                                                                                                                                                                  |
| **Root**           | 20       | 2,176  | Facade layer: api.py, base.py, cli.py, models.py, protocols.py, constants.py, typings.py, utilities.py, worktree.py, git.py, **init**.py (lazy map 787 LOC), \_config.py, \_settings.py, **main**.py, **version**.py, base_selection.py.                                                                                                                               |

**Total: ~92k LOC, 450+ arquivos.**

### Hubs de acoplamento (maior fan-in)

1. **\_utilities, \_models, \_constants** — trio universal importado por ~todos os subsistemas
2. **detectors → refactor/fixers/gates/validate** — fluxo detecção→ação
3. **codegen** — hub para release, validate, refactor, services
4. **services/** — raiz de composição CLI

### Módulos oversized (top 10, >200 LOC)

1. `codegen/conform.py` — **3,396 LOC** (pipeline monolítico pyproject/.mise)
2. `_models/config.py` — **4,366 LOC** (configs de todas tools monolíticas)
3. `_utilities/rope_analysis.py` — **2,022 LOC**
4. `_utilities/pyproject_conform.py` — **1,036 LOC**
5. `_utilities/rope_imports.py` — **905 LOC**
6. `_utilities/namespace_moves.py` — **914 LOC**
7. `_utilities/rope_analysis_workspace.py` — **316 LOC** (parece overlap)
8. `_utilities/namespace.py` — **708 LOC**
9. `_utilities/docs_render.py` — **725 LOC**
10. `refactor/classvar_constant_autofix.py` — **707 LOC**

58 módulos >200 LOC; 15 dos top 25 em `_utilities`.

### Facade hygiene

- **Raiz `flext_infra/` segue padrão FLEXT corretamente**: `api.py` (FlextInfra), `base.py` (FlextInfraServiceBase = `s`), `cli.py` (FlextInfraCli), re-exports `models/protocols/constants/typings/utilities.py`. Famílias de declaração `_constants/_typings/_protocols/_models` são zero-behavior. Comportamento em `_utilities` + `services/` + `base.py`.
- **Desvios flaggados**: `_utilities` (26.9k LOC) deve ser decomposto em packages domain-specific; `codegen/conform.py` deve ser split em stages; `_models/config.py` split por tool/domain. `promoted/` usa imports non-lazy internos.

## Capacidades do code-review-graph (ferramenta exclusiva de grafo)

| Comando read-only                                                                                                      | Uso no plano                                                         |
| ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `status --repo <path> --json`                                                                                          | Verificar frescor do grafo antes de qualquer raciocínio graph-backed |
| `detect-changes --repo <path> --brief`                                                                                 | Evidência de impacto por PR                                          |
| `query callers_of\|callees_of\|imports_of\|importers_of\|children_of\|tests_for\|inheritors_of <symbol> --repo <path>` | Blast radius de símbolos antes de mover/deletar                      |
| `impact --files <list> --depth N --repo <path>`                                                                        | Raio de explosão de mudança multi-arquivo                            |
| `dead-code --kind Function\|Class --json --repo <path>`                                                                | Candidatos a exterminação (precisa verificação de referência antes)  |
| `visualize --format json --repo <path>`                                                                                | Exportar arquitetura/comunidades/fluxos                              |
| `search QUERY --kind TYPE --repo <path>`                                                                               | Busca semântica de entidades                                         |

**Localização**: `~/.local/share/ai-hub/host-tools/current/bin/code-review-graph` (Python wrapper → `code_review_graph.cli.main`). Grafo persistente incremental SQLite em `<repo>/.code-review-graph/graph.db`. Suporta Python, TS/JS, Rust, Go, Java, HCL, ReScript.

**Exterminação do `scope`**: remover referências a `scope`/`scope-nav` em skills, configs, regras, docs do repositório (ver Fase 0.2).

## Donos atuais inspecionados (atualizado com inventário)

| Dono                                                                  | Extensao prevista                                                                                                                                                       |
| --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| codegen/census.py::FlextInfraCodegenCensus                            | Corrigir falha convertida em vazio em `_run_project_census` / `_census_project`; integrar com code-review-graph para cobertura                                          |
| codegen/\_pipeline_stages.py                                          | Reusar census antes/depois, projetos descobertos, estado tipado; adicionar stage `graph-analyze`                                                                        |
| codemod/batch_apply.py::FlextInfraCodemodBatchApply                   | Circuito unico: preflight, plano semantico, fixes sintaticos, re-scan, fingerprint, validacao; acionar code-review-graph `detect-changes` no final                      |
| codemod/semantic_apply.py::FlextInfraCodemodSemanticApply             | Reusar inventario, SemanticMigrationEdit, composicao em memoria, publicacao protegida; inserir plano model-to-protocol                                                  |
| api.infra.rope_workspace(root)                                        | Sessao semantica para simbolos, classes, imports, referencias; fronteiras reais de cada repo                                                                            |
| \_utilities/codemod_rules.py::codemod_rule_plan                       | Descoberta das regras herdadas pelo grafo atual                                                                                                                         |
| codemod/sgconfig.yml, rules/, utils/, tests/                          | Regras ast-grep, guards compartilhados, fixtures; validar ids nao wired                                                                                                 |
| codemod/batch_gates.py::FlextInfraModGateEngine                       | Validacao e aplicacao ast-grep; separar aprovacao de snapshots da validacao normal                                                                                      |
| transformers/typing_unifier.py                                        | Reutilizar limites documentados (spans de anotacao, nao ampliar declaracoes/retornos, preservar mutacao); nao reutilizar substituicao generica Any/object por JsonValue |
| validate/namespace_validator.py e detectores                          | Reusar import/familia/pureza/posicionamento; compartilhar fatos/diagnosticos com census e mod                                                                           |
| _utilities/rope_\* (analysis, imports, structure, runtime, inventory) | Consolidar duplicação rope_analysis vs rope_analysis_workspace; decompor em domain packages                                                                             |
| codegen/conform.py                                                    | Decompor 3.4k LOC em stages: parse SSOT → render templates → overlay preservation → write                                                                               |
| \_models/config.py                                                    | Decompor 4.4k LOC em models por tool/domain (ruff, mypy, pyright, pyrefly, pytest, vulture, bandit, toml, packaging)                                                    |

O código atual mistura AST, regex e Rope. Não afirmar que a migração para Rope já terminou. Ast-grep identifica posições sintáticas; Rope resolve identidades e referências. Transformações que alterem significado nunca serão decididas apenas pelo nome textual m ou por regex.

## Contrato de substituicao segura

Uma substituicao exige simultaneamente: identidade do simbolo resolvida; uso classificado; contrato requerido conhecido; compatibilidade estrutural/variancia demonstrada; grafo de impacto fechado no escopo; ausencia de dependencia runtime da identidade concreta; validacao do artefato e consumidores afetados. Ausencia de prova gera bloqueio tipado com motivo e localizacao.

| Contexto                                                                      | Regra e acao                                                                                                                                                   |
| ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parametro de consumo de instancia                                             | Migrar para p apenas se todas as operacoes usadas estiverem no contrato, inclusive chamadas transitivas; verificar contravariancia, overrides e callbacks      |
| Retorno                                                                       | Migrar somente apos verificar capacidades exigidas pelos consumidores governados; nao remover capacidade mutavel ou API concreta prometida por troca cosmetica |
| Campo de protocol                                                             | Gerar propriedade de leitura quando compativel; converter referencia model para protocol recursivamente com prova de variancia                                 |
| Campo mutavel/propriedade com setter                                          | Preservar capacidade de escrita e invariancia; nao converter automaticamente para propriedade somente leitura                                                  |
| list[Model], dict[K, Model] e genericos invariantes                           | Proibida troca mecanica para list[Protocol]; interface covariante somente quando acesso somente leitura e exigencias de consumidores forem comprovados         |
| Declaracao local, atributo de classe/modulo                                   | Nao ampliar por inspecao isolada; escritores podem estar em mixins ou outros modulos. Exigir prova de grafo completo para mudar capacidades                    |
| Campos Pydantic, discriminadores, RootModel e schemas                         | Manter o contrato runtime de validacao concreto. Nao substituir por protocol como mecanismo de validacao. Separar desse campo a interface de consumo           |
| Construtor, base de classe, model_validate, TypeAdapter, testes de identidade | Preservar a referencia concreta quando parte da operacao runtime. Nao instanciar protocols nem transformar isinstance(Model) em isinstance(Protocol)           |
| type[Model] e factories                                                       | Distinguir classe/factory de instancia; manter ou reutilizar port de factory real, sem inventar assinaturas ou substituir por protocol de instancia            |
| Framework que le anotacoes, decoradores, get_type_hints                       | Tratar como fronteira runtime; so alterar com contrato documentado e prova do consumidor real                                                                  |
| Imports e aliases                                                             | Resolver origem, shadowing e MRO; rewire via facade publicada, manter import runtime quando exigido pela declaracao ou avaliacao real                          |
| Any/object, cast e contratos desconhecidos                                    | Diagnosticar causa; nunca inferir JsonValue ou um protocol vazio para obter green                                                                              |

Os limites preservam a separacao historica entre implementacao/validacao m e consumo p; nao criam allowlist de arquivos. Um concrete model em schema nao e a mesma categoria de desvio que uma dependencia concreta em interface de consumo.

Gerar espelhos de dados de models elegiveis; contratos comportamentais/ISP existentes permanecem autoridades de seus casos de uso, nao copias automaticas de toda implementacao. Verificar se um protocol publicado existente ja satisfaz o uso antes de criar outro. Protocol vazio nao demonstra contrato. runtime_checkable nao valida tipos de campos ou assinaturas: sua presenca nao e prova de substituibilidade.

## Fluxo unico

Topologia e fontes autenticadas -> census compartilhado -> indice semantico Rope -> candidatos ast-grep -> classificacao por papel -> plano tipado de geracao/rewiring -> preflight do lote inteiro -> publicacao pelo dono existente -> regeneracao de facades -> runtime/gates -> novo census -> ponto fixo.

1. Census registra projetos esperados/visitados, erros de leitura/resolucao, simbolos elegiveis, desvios, corrigiveis, bloqueados e referencias externas conhecidas. Falhar ao descobrir projeto nao equivale a projeto com zero violacoes.
2. Identidade qualificada inclui repo, modulo, classe/entidade e origem na facade/MRO; nomes iguais nao implicam mesmo model. Descobrir herdados, nested classes, genericos, propriedades computadas e referencias ciclicas. Excluir ClassVar, PrivateAttr e validators da lista de campos de instancia pelo papel semantico.
3. Construir fechamento transitivo dos campos projetados; usar componentes fortemente conexos para ciclos. Um lote inclui seu fechamento necessario, mesmo quando atravessa repos. Nao partir um componente por limite arbitrario de arquivos.
4. Codegen recebe descritor tipado e snapshot identificado das fontes canonicas, politica, templates e pins. O render nao consulta imports executaveis de projetos, clock, ambiente ou worktree incidental. Reconciliar formalmente esse insumo com a pureza atual do gerador antes de liga-lo ao make gen; nao usar saida gerada como SSOT de si mesma.
5. Templates produzem \_protocols com part classes e facades MRO canonicas, imports publicos e limite de 200 LOC logicas. Politicas configuraveis em YAML tipado; mapeamentos model/protocol derivados, nao registros manuais por classe.
6. Remover protocol gerado obsoleto somente com proveniencia comprovada e nenhum consumidor remanescente. Arquivo manual colidente exige adjudicacao de dono, nunca sobrescrita. Nao criar camada de compatibilidade.
7. make gen e dono da geracao; make mod planeja e solicita a mesma capacidade de codegen ao aplicar cutover, sem writer independente. make check e census verificam os mesmos contratos sem mutacao; make fix reutiliza o circuito existente onde aplicavel, sem copiar regras.

## Regras e cobertura

Estender o catalogo atual com categorias sem duplicar regras ja existentes: modelo concreto em interface; dependencia p->m em superficie projetavel; protocol ausente/desatualizado; perda de capacidade/variancia; anotacao nao resolvida; import fora da facade; ciclo runtime; deriva de familia/MRO; comportamento em declaracao; gerado sem proveniencia; consumidor nao rewireado.

Cada regra declara em dados: identificador, escopo por papel, severidade, pre-condicoes, dono semantico, capacidade de fix e motivo quando nao aplicavel. Ast-grep identifica candidatos em anotacoes e sintaxe comprovadamente local. Acoes dependentes de tipos vao para a fase semantica existente. Re-scan deve reconciliar candidatos com resultados semanticos para nao repetir falsos positivos sobre campos concretos legitimamente preservados.

Nao prometer corrigir toda violacao arquitetural possivel. Este incremento fecha todas as categorias acima e exercita as demais regras existentes no escopo. Novas categorias descobertas devem ter dono, diagnostico, regra/teste e correcao geral antes de fechar sua migracao; nunca patch manual repetido em consumidores. Questoes que mudem requisito de negocio bloqueiam seu componente ate decisao explicita.

## Achados de cruft e duplicação (pendentes — re-despachar exploração focada)

_As explorações de cruft retornaram vazias; re-despachar com escopo estreito antes de iniciar a Fase 0.5._

| Categoria                                    | Candidatos esperados (baseado em inventário)                                                                                                                |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Motores duplicados AST vs Rope vs Regex**  | `transformers/typing_unifier.py` (ast+regex) vs rope declarado; detectors (alguns ast-based) vs rope-semantic; refactor transformers registries             |
| **Vocabulário legado/retired**               | `rg -ni "retired\|legacy\|legado\|deprecated\|obsolete\|no longer\|do not use\|WIP"` em refactor/, transformers/, codemod/, detectors/, codegen/, validate/ |
| **Regras ast-grep não wired**                | IDs em `rules/` (via `codemod/sgconfig.yml` + `_utilities/codemod_rules.py`) sem referência em `tests/` ou wiring em src                                    |
| **Módulos oversized com duplicação interna** | Top 10 acima (conform.py, config.py, rope_analysis.py, etc.) — decompor em domain packages                                                                  |
| **scope/scope-nav references**               | Remover de skills, configs, regras, docs (decisão do operador)                                                                                              |

**Verificação de referência obrigatória antes de declarar dead**: rg do símbolo no workspace completo (`~/flext` incluindo todos submodule src/tests/examples/scripts), considerar lazy-map (`__init__.py` `build_lazy_import_map` / `_LAZY_IMPORTS`), `__all__` exports, facade aliases (`c/t/p/m/u` composition), YAML/config references (rules/_.yml, config/_.yaml, sgconfig.yml), Makefile references. Classificar: **SAFE-DELETE CANDIDATE** / **NEEDS ADJUDICATION** / **ALIVE**. Se não provável unreferenced → NEEDS ADJUDICATION.

## Sequencia de implementacao

### 0. Mapeamento global, simplificação e exterminação de cruft da máquina flext-infra

> **Pré-requisito para todas as fases seguintes**. Esta fase usa `code-review-graph` como única ferramenta de grafo, aplica `yagni`/`simplify`/`safe-delete`/`dry`, e segue **apenas padrões canônicos FLEXT/Pydantic** (pesquisa profunda no código vivo antes de qualquer mudança).

#### 0.1 Inicialização do grafo e baseline

```bash
cd ~/flext/flext-infra
code-review-graph doctor
code-review-graph build --repo src
code-review-graph status --repo src --json  # confirmar frescor
```

- Salvar snapshot do grafo (`.code-review-graph/graph.db`) como baseline.
- Registrar estatísticas: nós, arestas, comunidades, dead-code baseline.

#### 0.2 Exterminação de `scope` / `scope-nav` no repositório

- `rg -rn "scope-nav\|scope " -- src/ docs/ .agents/ .claude/ .kilo/ config/ Makefile* *.mk` → listar todas as referências.
- Para cada ocorrência: verificar se é import/runtime/config/skill/doc. Aplicar `safe-delete`: remover a referência, regerar artefacts se necessário (ex.: skill regenerada), rodar `make check` no dono.
- Critério: zero referências a `scope`/`scope-nav` no repositório; `code-review-graph` é a única ferramenta de grafo citada.

#### 0.3 Decomposição de oversized modules (net-negative LOC, ≤200 LOC/logical)

| Alvo                                                                    | Ação                                                                                                                                                                                                                                      | Padrão canônico                                                              |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `codegen/conform.py` (3,396 LOC)                                        | Split em stages: `ParseSSOTStage`, `RenderTemplatesStage`, `OverlayPreservationStage`, `WritePublicationStage`; cada um ≤200 LOC, compose via pipeline existente                                                                          | ADR-010 codegen cascade; `FlextInfraCodegenPipelineStagesMixin`              |
| `_models/config.py` (4,366 LOC)                                         | Split por tool/domain: `ruff_models.py`, `mypy_models.py`, `pyright_models.py`, `pyrefly_models.py`, `pytest_models.py`, `vulture_models.py`, `bandit_models.py`, `toml_models.py`, `packaging_models.py`; compose via MRO em `config.py` | `m.*` presets; `model_rebuild` forbidden; complete model with runtime import |
| `_utilities/rope_analysis.py` (2,022 LOC)                               | Decompor em `rope_analysis/`: `class_analysis.py`, `method_analysis.py`, `attribute_analysis.py`, `call_graph.py`, `inheritance.py`; consolidar `rope_analysis_workspace.py` overlap                                                      | LAW-2 rope-only; `FlextInfraUtilitiesRopeAnalysis` facade                    |
| `_utilities/rope_imports.py` (905 LOC)                                  | Separar `import_analysis.py`, `import_modernizer.py`, `import_fixer.py`                                                                                                                                                                   | `FlextInfraUtilitiesRopeImports` facade                                      |
| `_utilities/namespace_moves.py` + `namespace.py` (1,622 LOC combinados) | Unificar em `namespace/`: `moves.py`, `analysis.py`, `enforcer.py`                                                                                                                                                                        | ADR-014 namespace rules                                                      |
| `refactor/classvar_constant_autofix.py` (707 LOC)                       | Separar `detection.py`, `fixer.py`, `validation.py`                                                                                                                                                                                       | `FlextInfraRefactorClassvarAutofix` facade                                   |

**Aceite por alvo**:

- `make check` green no dono + dependentes diretos
- Segunda rodada `make gen` + `make mod` = exit 0, zero mudanças (idempotência)
- LOC líquido negativo; nenhum teste quebrado; zero `noqa`/`type: ignore` adicionados
- `code-review-graph impact --files <alterados> --repo src` confirma blast radius contido

#### 0.4 Eliminação de duplicação AST↔Rope↔Regex

- Mapear via `code-review-graph query` e `detect-changes` os caminhos que fazem a mesma coisa por engines diferentes.
- Canonicalizar no **Rope** (LAW-2) para análise semântica; **ast-grep** apenas para detecção sintática local comprovada; **regex** apenas para spans de anotação confirmados (como em `typing_unifier.py:_widens_a_container`).
- Mover detecções AST-only em `detectors/` para Rope (`FlextInfraUtilitiesRopeAnalysis` / `FlextInfraUtilitiesRopeStructure`).
- Remover `import ast`, `ast.parse`, `ast.walk`, `get_ast()` dos caminhos semânticos (LAW-2). Verificar com `grep -rnE "import ast|ast\.parse|get_ast|walk_ast_nodes" src/flext_infra/detectors/ src/flext_infra/transformers/ src/flext_infra/refactor/` → zero ocorrências em código semântico.

#### 0.5 Remoção de cruft verificado (safe-delete + yagni)

Para cada candidato da tabela de cruft (após re-despacho da exploração):

1. **Verificação de referência completa** (6-gate: rg word-boundary + lazy-map + `__all__` + facade alias + MRO base + `p.*` impl).
2. Se **SAFE-DELETE CANDIDATE**: aplicar `safe-delete` — remoção atômica com contrato de recuperação (journal), consumer rewire no mesmo commit, `make check` green, `make test` green.
3. Se **NEEDS ADJUDICATION**: registrar no bead com diagnóstico, bloquear componente até decisão explícita do operador.
4. **Nunca** suprimir, criar shim, allowlist, ou compat layer.

**Aceite Fase 0**:

- `code-review-graph dead-code --json --repo src` → zero funções/classes mortas no workspace governado (exceto NEEDS ADJUDICATION documentados)
- `rg -rn "scope-nav\|scope " -- src/ .agents/ .claude/ .kilo/ config/ docs/` → zero hits
- `grep -rnE "import ast|ast\.parse|get_ast|walk_ast_nodes" src/flext_infra/detectors/ src/flext_infra/transformers/ src/flext_infra/refactor/` → zero (apenas em testes/fixtures se aplicável)
- Todos oversized modules alvo ≤200 LOC, net-negative LOC total
- `make check` + `make test` green em `flext-infra`; `make gen` idempotente
- Beads reconciliados: cada remoção/adjudicação com bead própria ou nota no bead principal

---

### 1. Reconciliar e estabilizar os donos

Revalidar AGENTS, regras atuais de comandos, topologia, SHA, WIP e beads existentes mro-iqzh/mro-qc84/mro-dxrp e sucessoras. Preservar trabalhos concorrentes e nao fechar/superseder beads por presuncao. Criar ou assumir intencao unica com dependencias e evidencias. Nenhum commit/push sem autorizacao vigente.

Corrigir census para falhar com causa, em vez de retornar projetos/violacoes vazios em erro. Separar atualizacao deliberada de snapshots da validacao: validate_rule_fixtures hoje reconcilia, roda SG_UPDATE_ALL e sincroniza fixtures; um snapshot errado deve falhar sem ser regravado automaticamente. Reusar primitivas ja existentes para publicacao/preflight, verificando o dono atual, nao a API lembrada de outra revisao.

Aceite: erro de descoberta/parse/fixture produz falha observavel, sem contagem zero enganosa e sem alterar expectativas. Dry-run nao escreve codigo, config ou snapshots.

### 2. Consolidar fatos semanticos e a matriz de seguranca

Estender contratos Pydantic do census/mod com identidade de origem, papel do uso, capacidades requeridas, prova, dependencias, motivo de bloqueio, hashes/modos de entrada e alcance da mudanca. Reusar indice de simbolos e sessao Rope existente por repo/snapshot. Evitar abrir projeto por classe. Nao introduzir nova hierarquia duplicada de modelos so para transportar relatorios existentes.

Reproduzir via fixtures do circuito os bugs historicos: texto em strings reescrito, local list alterado, cache escrito por outro mixin, retorno que perde metodos, alias sombreado. Adicionar escape por chamada desconhecida: analise local nao prova ausencia de mutacao. Casos desconhecidos falham fechados.

Aceite: census/check/mod concordam sobre identidade, categoria e fixabilidade; todos os casos protegidos permanecem intactos e diagnosticados corretamente.

### 3. Geracao real de protocols

Integrar extracao/classificacao/render ao codegen existente e adicionar templates e regras tipadas minimas. Gerar fechamento de models de dados, incluindo herdados e ciclos, sem copiar validators ou infraestrutura Pydantic para cada protocol. Reutilizar contracts p.Model/p.Result/factories conforme assinatura real e necessidade do consumidor.

Primeiro piloto de capacidade: conjunto pequeno de models reais com consumidor real, selecionado pelo census e dependencia, nao por lista fixa. Incluir pelo menos campo simples, referencia transitiva e colecao com variancia. Confirmar runtime de validacao, serializacao e import antes de codificar expectativas de regressao.

Aceite: instancia concreta satisfaz o contrato estatico; schema/serializacao/identidade de objetos preservados; segundo render sem mudanca de bytes/modos; ausencia de conflito com contratos manuais.

### 4. Rewiring no make mod

Adicionar regras ast-grep e a acao semantica no circuito existente. Planejar geracao, anotacoes, imports, facades e consumidores juntos; aplicar somente apos preflight completo do componente. Validar tipos depois de cada componente, nao esperar o fim da frota para descobrir uma assinatura quebrada.

Resolver referencias pelo grafo Rope e superficie publica, incluindo aliases herdados, overloads, callbacks e genericos. Atualizar spans corretos e imports necessarios; remover apenas imports comprovadamente mortos. Nao renomear globalmente classes m para p: construtores e schemas continuam concretos.

Aceite: produtor e todos os consumidores governados do piloto migrados, sem DTO sombra/dump-reload/cast/ignore/alias de compatibilidade; segunda rodada zero edits e zero findings dessa migracao.

### 5. Seguranca e escala

Autenticar conteudo e modo de todas as entradas antes dos efeitos. Mudanca concorrente invalida o plano: re-inventariar e replanejar fix-forward, nunca reaplicar patch antigo. Locks por repo em ordem deterministica para componentes multi-repo. Publicacao de varios arquivos nao e atomicidade global: registrar progresso pelo journal existente e recuperar somente efeitos autenticados da propria invocacao; nenhuma reversao de trabalho concorrente. Nao retomar automaticamente com snapshot divergente.

Reusar cache/manifesto existente, estendendo chave por fonte, pins, politicas, templates e versoes do motor. Invalidar fechamento reverso quando assinatura muda. Scan somente leitura pode ser paralelo por repos independentes; mutacao serializada por componente/locks. Nao executar instancia compartilhada de Rope em threads sem garantia do dono.

Medir via rota canonica com cProfile antes de otimizar. Registrar arquivos/classes analisados, cache hits, referencias rewireadas, tempo, memoria, rescan e bloqueios. Comparar rodada fria, incremental e no-op. Orquestrador nao define numero otimista de arquivos por lote: usar componentes e budgets da SSOT; componente que exceda budget bloqueia com diagnostico, nao e parcialmente aplicado.

Aceite: interrupcao, conflito CAS, permissao e ciclo sem progresso falham com causa e plano retomavel; no-op nao reescreve projetos; cache nunca esconde drift.

### 6. Propagacao governada e fechamento

Publicar primeiro a capacidade validada de infra; migrar fundacao e consumidores em ordem topologica real, processando ciclos como componentes. Reutilizar a propria automacao em flext-infra, nao manter rota especial de self-migration. Subagentes podem trabalhar em donos/componentes disjuntos; orquestrador coordena evidencias e dependencias, sem writers concorrentes no mesmo fechamento.

Em cada lote: census -> plano -> make mod -> regeneracao canonica -> runtime dos consumidores -> make check/test/build aplicaveis -> census e idempotencia. Confirmar sintaxe e seletores no contrato Make atual antes de invocar; nao copiar ou comandos ad-hoc do plano de julho. Mutacoes usam quando requerido pelo contrato vigente. Toda invocacao parte da raiz canonica aplicavel; respeitar isolamento standalone do infra.

Validacao incremental acelera feedback, mas nao substitui gates finais de toda topologia declarada. Nao excluir tests/examples/scripts para reduzir volume. Registrar componentes bloqueados e resolver a causa em regras/motores antes de fechar. Commits escopados, push FF, PR, CI real e integracao somente com autorizacao; sem bypass ou force. Rerun no SHA integrado e gitlinks coerentes antes de afirmar propagacao publicada.

## Matriz de validacao obrigatoria

1. Fixtures ast-grep valid/invalid e goldens de rewiring revisados independentemente, incluindo nomes identicos e aliases; nunca atualizar snapshots durante a verificacao que pretende prova-los.
2. Testes semanticos de heranca/MRO, genericos PEP 695, Self, recursao, overloads, parametros posicionais/keyword-only, computed fields, ClassVar/PrivateAttr, setters e mutacao por escape.
3. Provas estaticas reais de assignability model->protocol, produtor->consumidor, callbacks e containers nos verificadores suportados; sem cast ou mocks como prova de compatibilidade.
4. Runtime real: imports/lazy facades, modelos completos, model_validate/model_dump, schemas/discriminadores, CLI/API afetadas; manter comportamento, erros e identidade sem adaptadores artificiais.
5. Tests de policy/SSOT usam variacoes validas e derivacao do dono, nao valores atuais congelados. Goldens fixam estrutura, nao configuracao mutavel.
6. Census: nenhuma falha vira vazio; totais conciliam esperado/visitado/falhou; cada desvio corrigido, bloqueado ou classificado como uso valido com motivo semantico.
7. Idempotencia: gen duas vezes, mod duas vezes e ciclo gen/mod/fix/fmt repetido; segunda rodada exit 0, zero alteracoes em bytes/modos e zero novas inconsistencias.
8. Seguranca: dry-run sem escrita, conflito de WIP, interrupcao entre arquivos/repos, colisao com arquivo manual, arquivo removido, symlink/permissao e journal retomado com pins divergentes.
9. Gates nativos Ruff, Pyrefly, Pyright, Mypy, Pytest/cobertura e build aplicaveis, incluindo src/tests/examples/scripts. Evidencias com comando, cwd, exit, saida decisiva, SHA e universo medido; nenhuma alegacao fleet-wide a partir de amostra.
10. **Fase 0 gate**: `code-review-graph dead-code --json --repo src` → zero dead code (exceto NEEDS ADJUDICATION); `scope` exterminado; oversized modules ≤200 LOC; net-negative LOC; LAW-2 compliance (zero AST em caminhos semânticos); `make check`+`make test` green em flext-infra.

## Criterio final

Um comando canonico make mod descobre e corrige os desvios suportados sem edicao manual de consumidores; make gen reconstitui os protocols e facades; census/check detectam drift e falham em cobertura incompleta. Todos os consumidores da topologia governada afetados estao rewireados e validados, nao existem bloqueios da migracao omitidos, segunda rodada e no-op e documentacao do contrato permanece alinhada. Planejamento completo ou piloto green nao equivalem a frota migrada.

**Fase 0 concluída** (grafo inicializado, scope exterminado, máquina simplificada, cruft removido) é pré-condição para Fase 1+. Nenhuma fase subsequente inicia sem Fase 0 green.

Nao ha questao de escopo pendente: topologia governada foi confirmada; limites de seguranca foram recuperados do historico e confrontados com o codigo atual. Questoes de negocio descobertas durante execucao bloqueiam apenas o componente afetado e exigem decisao explicita, sem inventar contrato.
