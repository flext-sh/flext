# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Refatorador de Classes — Ajuste de Regras, Declaracao e Uso de Modulos

## TL;DR

Definir e implementar um **motor de regras declarativas** para refatoracao de classes que respeite rigorosamente:
- composicao MRO por familia (`c`, `t`, `p`, `m`, `u`) derivada de `pyproject.toml` + codigo real;
- politicas especificas por modulo privado (`_models`, `_utilities`, `_dispatcher`, `_decorators`, `_runtime*`);
- propagacao global de referencias sem fallback/compat wrappers.

Este plano ajusta o que ja existe em `flext-core/src/flext_infra/refactor/` para parar transformacoes simplificadas e passar a aplicar regras corretas por contexto.

---

## Contexto

### Pedido consolidado

Voce pediu um plano para:
- ajustar o refatorador atual;
- definir **como as regras serao declaradas**;
- definir **como os modulos serao usados** para os ajustes;
- garantir MRO correto para `c/t/p/m/u` e comportamento correto em `_models/_utilities/_dispatcher/...`.

### Evidencias lidas

- `CLAUDE.md` (leis arquiteturais e de importacao)
- skill `flext-architecture-layers` (cadeias e composicao)
- skill `flext-patterns` (MRO, anti-patterns)
- implementacao atual:
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py`
  - `flext-core/src/flext_infra/refactor/transformers/class_nesting.py`
  - `flext-core/src/flext_infra/refactor/transformers/helper_consolidation.py`
  - `flext-core/src/flext_infra/refactor/transformers/nested_class_propagation.py`
  - `flext-core/src/flext_infra/refactor/analysis.py`
  - `flext-core/src/flext_infra/refactor/rules/class-nesting-mappings.yml`

### Metis Gap Analysis (incorporado)

Pontos obrigatorios adicionados no plano:
- matriz de politica por familia de modulo;
- declaracao de regras v2 com campos de validacao pre/post;
- delta explicito "estado atual vs estado requerido";
- rollout em ondas com gates de bloqueio e rollback.

---

## Objetivo de Trabalho

Criar uma versao v2 do refatorador de classes que seja **policy-driven** e nao heuristica simples.

### Definicao de Pronto

- [x] Regras de composicao para `c/t/p/m/u` declaradas e validadas.
- [x] Regras por modulo privado (`_models`, `_utilities`, `_dispatcher`, `_decorators`, `_runtime*`) declaradas e aplicadas.
- [x] Pipeline impede transformacao fora de politica (bloqueia, nao "corrige silenciosamente").
- [x] Propagacao global AST cobre imports, type hints, bases e referencias.
- [ ] `make check` e testes dos projetos impactados passam sem suppressions.

---

## Estado Atual vs Estado Requerido

### Estado atual (implementado hoje)

- scanner/analyzer detectam classes e helpers por arquivo;
- `ClassNestingTransformer` move classes top-level para namespace alvo;
- `HelperConsolidationTransformer` move funcoes top-level para staticmethods;
- `NestedClassPropagationTransformer` propaga parte das referencias;
- regras guiadas por mapping YAML com `confidence`.

### Problemas atuais

- sem classificador formal de projeto/familia por dependencias (`pyproject`);
- sem matriz de politica por familia de modulo privado;
- sem validacao MRO declarativa para `c/t/p/m/u`;
- targets de mapping podem ser semanticamente incorretos;
- propagacao ainda nao e governada por contrato de composicao completo.

### Estado requerido

- engine com **Policy Resolver** (projeto + familias + pais esperados);
- schema v2 com `module_family`, `facade_family`, `expected_bases`, `forbidden_targets`, `pre_checks`, `post_checks`;
- validadores bloqueantes pre-transform e post-transform;
- transformacoes condicionadas por politica da familia, nao por match textual isolado.

---

## Estrategia de Declaracao de Regras (v2)

### Arquivos de regra

- `flext-core/src/flext_infra/refactor/rules/class-policy-v2.yml` (novo)
- `flext-core/src/flext_infra/refactor/rules/class-policy-v2.schema.json` (novo)

### Campos minimos (obrigatorios)

- `project_kind`: `core | domain | platform | integration | app`
- `facade_family`: `c | t | p | m | u`
- `module_family`: `_models | _utilities | _dispatcher | _decorators | _runtime | other_private`
- `source_symbol`
- `target_facade_class`
- `target_namespace_path`
- `expected_base_chain`
- `forbidden_targets`
- `confidence`
- `pre_checks[]`
- `post_checks[]`
- `rewrite_scope`: `file | project | workspace`

### Politica por modulo privado (obrigatoria)

- `_models`: permitido reorganizar classes de composicao de `m`; proibido enviar para `u/d/dispatcher`.
- `_utilities`: permitido consolidar helpers em `u`; proibido alterar sem validação de estado/assinatura.
- `_dispatcher`: permitido reorganizar sob `FlextDispatcher`; obrigatorio propagar referencias cross-project.
- `_decorators`: permitido consolidar em `d`; obrigatorio preservar callable contract.
- `_runtime*`: somente transforms explicitamente whitelistadas; default = bloqueado.

---

## Regra de MRO para c/t/p/m/u

O refatorador deve calcular pais esperados por familia em 2 passos:

1. Inferencia por `pyproject.toml` (dependencias de familia)
2. Confirmacao por classes reais encontradas no projeto

### Exemplo (algar-oud-mig)

Com base no projeto real, o padrao vigente e:
- `AlgarOudMigModels(FlextLdapModels, FlextCliModels)`
- `AlgarOudMigConstants(FlextLdapConstants, FlextCliConstants)`
- `AlgarOudMigTypes(FlextLdapTypes, FlextCliTypes)`
- `AlgarOudMigProtocols(FlextLdapProtocols, FlextCliProtocols)`
- `AlgarOudMigUtilities(FlextLdapUtilities, FlextCliUtilities)`

O engine deve validar que a ordem e coerente e que os namespaces herdados esperados estao acessiveis.

---

## Ondas de Execucao

### Dependency Matrix (TODOs -> Etapas)

- **Etapa 1 (modulos piloto)**
  - Requer TODOs: `1, 2, 5, 6, 9`
  - Escopo: `flext-core/src/flext_core/_dispatcher/*` e `flext-core/src/flext_core/_utilities/*`

- **Etapa 2 (projetos piloto)**
  - Requer TODOs: `3, 4, 7, 8`
  - Requer Etapa 1 aprovada
  - Escopo: `flext-ldap` e `algar-oud-mig`

- **Etapa 3 (global workspace)**
  - Requer TODO: `10`
  - Requer Etapas 1 e 2 aprovadas
  - Escopo: workspace completo

### Failure Semantics

- Se uma etapa falhar em qualquer gate (lint/type/test/user-approval):
  - bloquear promocao para a proxima etapa;
  - executar rollback da etapa atual;
  - permitir retry da mesma etapa (max 3 tentativas);
  - apos 3 falhas, exigir decisao humana para continuar.

### Artefatos obrigatorios por etapa

- Dry-run diff: `.sisyphus/refactor/dry-run-{etapa}-{timestamp}.diff`
- Dry-run summary JSON: `.sisyphus/refactor/dry-run-{etapa}-{timestamp}.json`
- Gate report: `.sisyphus/refactor/gates-{etapa}-{timestamp}.md`
- Sign-off usuario: `.sisyphus/refactor/signoff-{etapa}-{timestamp}.md`

## TODOs

- [x] 1. Definir matriz de politica por familia de modulo

  **Incremental Mode**: `EXTEND`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py` (consumidor de policy)
  - `flext-core/src/flext_infra/refactor/analysis.py` (classificacao por familia)
  - Famílias-alvo: `_models`, `_utilities`, `_dispatcher`, `_decorators`, `_runtime*`

  **What to do**:
  - Formalizar regras para `_models/_utilities/_dispatcher/_decorators/_runtime*`.
  - Definir operacoes permitidas/proibidas por familia.

  **Must NOT do**:
  - Nao usar regra unica para todos os `_private`.

  **Files**:
  - `flext-core/src/flext_infra/refactor/rules/class-policy-v2.yml` (novo)

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: `flext-architecture-layers`, `flext-patterns`

  **Acceptance Criteria**:
  - [ ] Cada familia tem policy explicita.
  - [ ] Existe bloco de operacoes proibidas por familia.

- [x] 2. Definir schema v2 bloqueante

  **Incremental Mode**: `NEW` (minimo inevitavel)

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/rules/class-policy-v2.schema.json`
  - `flext-core/src/flext_infra/refactor/rules/class-policy-v2.yml`
  - Entradas de classe: `loose_name/target_namespace/target_name/module_family/facade_family`

  **What to do**:
  - Criar schema JSON com campos obrigatorios da politica v2.
  - Rejeitar regra sem `module_family/facade_family/pre_checks/post_checks`.

  **Files**:
  - `flext-core/src/flext_infra/refactor/rules/class-policy-v2.schema.json` (novo)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `rules-src`, `python-modern-type-syntax`

  **Acceptance Criteria**:
  - [ ] Config invalida falha com erro claro.

- [x] 3. Implementar Project Classifier por pyproject + codigo

  **Incremental Mode**: `NEW`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/project_classifier.py`
  - `pyproject.toml` dos projetos alvo (somente leitura para inferencia)
  - Fachadas de referencia: `*models.py`, `*constants.py`, `*typings.py`, `*protocols.py`, `*utilities.py`

  **What to do**:
  - Ler dependencias do `pyproject.toml` e inferir tipo de projeto.
  - Confirmar pais por classes reais (`models/constants/typings/protocols/utilities`).

  **Files**:
  - `flext-core/src/flext_infra/refactor/project_classifier.py` (novo)

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: `flext-architecture-layers`, `backend-data-patterns`

  **Acceptance Criteria**:
  - [ ] Classificador retorna `project_kind` e pais esperados de `c/t/p/m/u`.

- [x] 4. Implementar MRO Resolver por familia

  **Incremental Mode**: `NEW`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/mro_resolver.py`
  - Cadeias de familias: `c`, `t`, `p`, `m`, `u`
  - Classes principais por projeto: `Flext*Constants/Types/Protocols/Models/Utilities`

  **What to do**:
  - Resolver cadeia esperada de `c/t/p/m/u` e validar ordem.
  - Expor lista de namespaces esperados acessiveis por MRO.

  **Files**:
  - `flext-core/src/flext_infra/refactor/mro_resolver.py` (novo)

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: `python-313-typing`, `flext-architecture-layers`

  **Acceptance Criteria**:
  - [ ] Falha bloqueante quando base order nao bate com policy.

- [x] 5. Adicionar Pre-Check Gate no rule pipeline

  **Incremental Mode**: `EXTEND`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py`
  - `flext-core/src/flext_infra/refactor/analysis.py`
  - Bloqueios em symbols/classes fora de policy por familia

  **What to do**:
  - Integrar pre-checks antes de qualquer rewrite AST.
  - Bloquear transform em familias/targets proibidos.

  **Files**:
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py` (ajuste)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `flext-refactoring-workflow`

  **Acceptance Criteria**:
  - [ ] Transform proibido retorna erro explicito e nao altera arquivo.

- [x] 6. Separar transformers por policy family-aware

  **Incremental Mode**: `EXTEND`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/transformers/class_nesting.py`
  - `flext-core/src/flext_infra/refactor/transformers/helper_consolidation.py`
  - `flext-core/src/flext_infra/refactor/transformers/nested_class_propagation.py`
  - Targets de classe em `_models/_utilities/_dispatcher/_decorators/_runtime*`

  **What to do**:
  - Tornar `class_nesting/helper_consolidation/propagation` dependentes de `module_family`.
  - Aplicar comportamento especifico por familia.

  **Files**:
  - `flext-core/src/flext_infra/refactor/transformers/class_nesting.py`
  - `flext-core/src/flext_infra/refactor/transformers/helper_consolidation.py`
  - `flext-core/src/flext_infra/refactor/transformers/nested_class_propagation.py`

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: `flext-refactoring-workflow`, `python-type-narrowing`

  **Acceptance Criteria**:
  - [ ] Cada transformer recebe contexto de policy.

- [x] 7. Reforcar propagacao global com escopo declarativo

  **Incremental Mode**: `EXTEND`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py`
  - `flext-core/src/flext_infra/refactor/analysis.py`
  - Referencias de classe: imports, annotations, bases, chamadas, isinstance

  **What to do**:
  - Implementar `rewrite_scope` (file/project/workspace).
  - Propagar imports, annotations, bases e referencias conforme escopo.

  **Files**:
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py`
  - `flext-core/src/flext_infra/refactor/analysis.py`

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: `flext-refactoring-workflow`, `rules-src`

  **Acceptance Criteria**:
  - [ ] Nenhuma referencia antiga restante para symbols transformados.

- [x] 8. Ajustar mappings atuais para policy v2

  **Incremental Mode**: `REUSE`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/rules/class-nesting-mappings.yml`
  - `flext-core/src/flext_infra/refactor/rules/class-policy-v2.yml`
  - Classes mapeadas atuais (ex.: `TimeoutEnforcer`, `FlextModelFoundation`, `ResultHelpers`)

  **What to do**:
  - Migrar `class-nesting-mappings.yml` para novo formato com campos v2.
  - Corrigir targets semanticamente invalidos.

  **Files**:
  - `flext-core/src/flext_infra/refactor/rules/class-nesting-mappings.yml`
  - `flext-core/src/flext_infra/refactor/rules/class-policy-v2.yml`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `backend-data-patterns`

  **Acceptance Criteria**:
  - [ ] Todos os entries validam no schema v2.

- [x] 9. Implementar Post-Check Gate bloqueante

  **Incremental Mode**: `EXTEND`

  **Afeta modulos/classes**:
  - `flext-core/src/flext_infra/refactor/validation.py`
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py`
  - Validacao final de familias `c/t/p/m/u` e referencias transformadas

  **What to do**:
  - Validar import resolution + MRO + typecheck-target apos rewrite.
  - Falha deve impedir marcar transform como sucesso.

  **Files**:
  - `flext-core/src/flext_infra/refactor/validation.py` (novo)
  - `flext-core/src/flext_infra/refactor/rules/class_nesting.py`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `flext-quality-gates`

  **Acceptance Criteria**:
  - [ ] Regra retorna erro quando post-check falha.

- [x] 10. Cobertura de testes por familia de modulo

  **Incremental Mode**: `EXTEND`

  **Afeta modulos/classes**:
  - `flext-core/tests/unit/test_refactor_policy_family_rules.py`
  - `flext-core/tests/integration/test_refactor_policy_mro.py`
  - Cenarios por familia: `_models`, `_utilities`, `_dispatcher`, `_decorators`, `_runtime*`

  **What to do**:
  - Criar testes por familia (`_models/_utilities/_dispatcher/...`) e por `c/t/p/m/u`.
  - Incluir cenarios negativos (transform proibido).

  **Files**:
  - `flext-core/tests/unit/test_refactor_policy_family_rules.py` (novo)
  - `flext-core/tests/integration/test_refactor_policy_mro.py` (novo)

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: `testing-patterns`, `flext-quality-gates`

  **Acceptance Criteria**:
  - [ ] Tests cobrem regras positivas e bloqueios obrigatorios.

- [x] 11. Rollout controlado por ondas

  **Incremental Mode**: `REUSE`

  **Afeta modulos/classes**:
  - `.sisyphus/drafts/refactor-policy-rollout.md`
  - Pipeline atual de execucao dry-run/apply do refatorador
  - Gates de validacao workspace/project/file

  **What to do**:
  - **Etapa 1 (modulos piloto)**: aplicar em 2-4 modulos privados de baixo risco (`_dispatcher`, `_utilities`) no `flext-core`.
  - **Etapa 2 (projetos piloto)**: aplicar em 1 projeto domain + 1 integration (ex.: `flext-ldap` e `algar-oud-mig`).
  - **Etapa 3 (global)**: aplicar em workspace completo apos aprovacao das etapas 1 e 2.
  - Pre-check de existencia dos alvos antes de cada etapa (path + pyproject + facades).
  - Para cada etapa, executar ciclo protegido por git:
    1. criar branch da etapa (`refactor-policy/etapa-{n}`)
    2. `git stash` + checkpoint antes do apply
    3. dry-run + gerar artefatos (diff/json/report)
    4. apply controlado
    5. type/lint/test gates
    6. **checkpoint de validacao com usuario** (revisao de artefatos + aprovacao explicita)
    7. somente apos aprovacao, seguir para proxima etapa
  - Rollback da etapa (obrigatorio em falha ou rejeicao): restaurar checkpoint + limpar branch de etapa.

  **Files**:
  - `.sisyphus/drafts/refactor-policy-rollout.md` (novo)

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `flext-refactoring-workflow`

  **Acceptance Criteria**:
  - [ ] Cada etapa tem gate de entrada/saida com rollback claro.
  - [ ] Nao existe promocao de etapa sem aprovacao explicita do usuario.
  - [ ] Etapa 1 valida regra por modulo; Etapa 2 valida regra por projeto; Etapa 3 valida regra global.
  - [ ] Falha em qualquer gate bloqueia a proxima etapa automaticamente.
  - [ ] Todos os artefatos de dry-run/gates/signoff sao gerados por etapa.

- [x] 12. Documentar contrato operacional do refatorador

  **Incremental Mode**: `EXTEND`

  **Afeta modulos/classes**:
  - `flext-core/docs/refactor/class-policy-v2.md`
  - Contratos de uso dos modulos privados e familias `c/t/p/m/u`

  **What to do**:
  - Documentar declaracao de regras v2, exemplos por familia, casos de excecao.
  - Documentar "nao simplificar `_private`".

  **Files**:
  - `flext-core/docs/refactor/class-policy-v2.md` (novo)

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `rules-docs`

  **Acceptance Criteria**:
  - [ ] Guia inclui matrix por familia e exemplos de MRO por projeto.

---

## Final Verification Wave

- [x] F1. **Policy Compliance Audit** (`oracle`)
  - Validar que cada transform aplicado respeita policy da familia e MRO.

- [ ] F2. **Code Quality Gate** (`unspecified-high`)
  - Rodar lint/type/test nos projetos impactados.

- [x] F3. **Real Refactor QA** (`unspecified-high`)
  - Dry-run e apply em amostras de core/domain/integration/app.

- [x] F4. **Scope Fidelity Check** (`deep`)
  - Verificar que ajuste focou em regras/refatorador, sem scope creep.

---

## Commit Strategy

- Commit 1: schema + policy declarations
- Commit 2: classifier + mro resolver + gates
- Commit 3: transformers family-aware + propagation
- Commit 4: tests + docs + rollout artifacts

---

## Success Criteria

- [x] Refatorador decide transformacao por politica declarativa e contexto do projeto.
- [x] Regras para `_models/_utilities/_dispatcher/...` estao explicitas e testadas.
- [x] MRO de `c/t/p/m/u` e validado antes e depois da transformacao.
- [x] Nenhum ajuste depende de alias de compatibilidade.
- [x] Operacao em workspace inteiro ocorre com gates e rollback seguro.

### Observacao de bloqueio remanescente (F2)

- Gate global `make check CHECK_GATES=lint,type` foi executado novamente em `2026-03-06`.
- Lint foi zerado no escopo do refatorador (29 -> 0), mas permanece backlog tipado global (`pyrefly=219`) fora do escopo estrito das regras v2.
