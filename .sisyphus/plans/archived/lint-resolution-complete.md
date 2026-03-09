# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Resolução Completa de Problemas de Lint - FLEXT Ecosystem

## TL;DR

> **Objetivo**: Resolver TODOS os problemas de lint em 33 projetos FLEXT (~4,200+ violações) seguindo CLAUDE.md e skills do flext-core
> 
> **Escopo**: Todos os projetos (`src/`, `tests/`, `examples/`) - 4 linters com ZERO tolerância
> 
> **Abordagem**: Multi-agente paralelo (5 agentes) em 5 fases sequenciais
> 
> **Estado Atual**: 
> - flext-core: 953 violações (49% dos 176 arquivos afetados)
> - Maiores problemas: `Any`/`object` (45 arquivos), retornos `T | None` (52 arquivos)
> - 21 arquivos com supressões de linter (`# type: ignore`, `# noqa`)
> 
> **Estimativa de Esforço**: XL (6-8 semanas com 5 agentes em paralelo)
> **Execução Paralela**: SIM - 5 ondas de agentes
> **Caminho Crítico**: Fase 0 (flext-core Wave 0) → Fase 1 → Fase 2 → Fase 3 → Fase 4 (31 projetos)

---

## Contexto

### Solicitação Original
Resolver todos os problemas de lint usando as regras de CLAUDE.md e skills em flext-core para adequar tudo aos padrões e best practices estabelecidos.

### Regras Aplicáveis (de CLAUDE.md e Skills)

**1. Quality Gates (flext-quality-gates)**
- 4 linters obrigatórios: ruff, mypy, pyright, pyrefly
- ZERO erros, ZERO warnings - tolerância absoluta
- Supressões (# type: ignore, # noqa) são PROIBIDAS
- Validação: `make check` em cada projeto

**2. Regras de Typing (flext-strict-typing)**
- `Any`/`object`: PROIBIDOS → usar `t.GeneralValueType`, `t.Scalar`, etc.
- `dict[str, Any]`: PROIBIDO → usar `t.ConfigMap`, `t.Dict`
- Inline unions (`str | int | float`): PROIBIDAS → vir de `typings.py`
- `| None`: INLINE-ONLY, nunca em definições de tipo
- `FlextResult` (`r[T]`): MANDATÓRIO para operações fallíveis
- Type narrowing: `isinstance()` ou `TypeGuard`, NUNCA `type()`
- `from __future__ import annotations`: em TODOS os arquivos Python

**3. Regras de Import (flext-import-rules)**
- Ordem: future → stdlib → third-party → first-party → local
- Aliases canônicos: `c`, `m`, `t`, `u`, `p`, `r`, `e`, `d`, `h`, `s`, `x`
- Sem imports relativos, sem wildcard imports
- Sem dupla atribuição de aliases

**4. Padrões de Código (flext-agent-strict-rules)**
- Pydantic v2: TODAS as classes herdam de BaseModel via MRO
- MRO inheritance: Todas as classes em hierarquia aninhada
- Zero hacks: sem `model_rebuild()`, `cast()`, `eval()`, `exec()`
- Sem aliases legado: `LegacyX = NewX` PROIBIDO
- ast-grep obrigatório para todas as transformações de código

**5. Multi-Agente (CLAUDE.md §10 + flext-5agent-coordination)**
- 5 agentes trabalhando em paralelo com ownership de arquivos
- 5 fases sequenciais (dependência entre fases)
- Zero overlap - cada agente tem arquivos/projetos exclusivos

---

## Current State Analysis

### Visão Geral dos 33 Projetos

| Projeto | pyproject.toml | Estimativa de Violações | Prioridade |
|---------|---------------|------------------------|------------|
| **flext-core** | ✅ | **953** | **P0 (CRÍTICA)** |
| flext-ldif | ✅ | 582 | P2 |
| flext-workspace | ✅ | 471 | P1 |
| algar-oud-mig | ✅ | 289 | P3 |
| flext-cli | ✅ | 258 | P1 |
| flext-api | ✅ | 130 | P1 |
| flext-plugin | ✅ | 120 | P2 |
| flext-ldap | ✅ | 115 | P2 |
| flext-meltano | ✅ | 106 | P2 |
| flext-quality | ✅ | 105 | P1 |
| flext-oracle-oic | ✅ | 101 | P2 |
| flext-oracle-wms | ✅ | 96 | P2 |
| flext-auth | ✅ | 80 | P1 |
| gruponos-meltano-native | ✅ | 78 | P3 |
| flext-observability | ✅ | 73 | P2 |
| flext-web | ✅ | 86 | P2 |
| flext-tap-ldap | ✅ | 68 | P2 |
| flext-tap-oracle-wms | ✅ | 67 | P2 |
| flext-tap-oracle | ✅ | 76 | P2 |
| flext-tap-oracle-oic | ✅ | 72 | P2 |
| flext-tap-ldif | ✅ | 63 | P2 |
| flext-target-ldif | ✅ | 56 | P2 |
| flext-db-oracle | ✅ | 56 | P2 |
| flext-target-oracle-oic | ✅ | 56 | P2 |
| flext-target-oracle-wms | ✅ | 58 | P2 |
| flext-target-oracle | ✅ | 50 | P2 |
| flext-grpc | ✅ | 41 | P2 |
| flext-dbt-oracle-wms | ✅ | 37 | P2 |
| flext-dbt-ldap | ✅ | 29 | P2 |
| flext-dbt-ldif | ✅ | 24 | P2 |
| flext-dbt-oracle | ✅ | 16 | P2 |
| flexcore | ✅ | 8 | P1 |
| **TOTAL** | **33/33** | **~4,200+** | - |

**Nota**: flext-core é P0 (prioridade máxima) pois é a base para todos os outros 32 projetos.

### Análise Detalhada: flext-core

**Arquivos analisados**: 176 arquivos Python
**Arquivos com violações**: 86 arquivos (49%)

#### Categorias de Violação em flext-core

| Categoria | Severidade | Arquivos Afetados | Descrição |
|-----------|------------|-------------------|-----------|
| `any_or_object_annotation` | 🔴 Média | 45 | Uso de `Any`/`object` em type annotations |
| `return_union_none` | 🔴 Média | 52 | Retornos `T \| None` em vez de `r[T]` |
| `inline_composed_type` | 🟡 Baixa | 14 | Unions inline como `str \| int \| float \| bool` |
| `linter_suppression_comment` | 🟡 Baixa | 21 | Comentários `# type: ignore`, `# noqa` |
| `print_statement` | 🔴 Média | 1 | Uso de `print()` em código de produção |
| `type_is_comparison` | 🔴 Média | 1 | Uso de `type(x) is T` em vez de `isinstance()` |

#### Padrões de Violação Mais Comuns (Heurístico)

- **Parâmetros sem annotations**: ~2,755 (maior classe de problema)
- **Missing `from __future__ import annotations`**: ~302 arquivos
- **Desordem de imports**: ~300 arquivos
- **Retornos sem annotations**: ~54 (concentrados em `flext-plugin`)

#### Arquivos com Maior Número de Violações (flext-core)

1. `_utilities/mapper.py` - múltiplas violações (Any, inline types, return Union None)
2. `_models/base.py` - Any annotations + return Union None
3. `decorators.py` - Any annotations + inline types
4. `_models/collections.py` - Any annotations + inline types
5. `protocols.py` - Any annotations + return Union None
6. `exceptions.py` - inline types + return Union None
7. `runtime.py` - Any annotations + suppression comments
8. `container.py` - Any annotations
9. `registry.py` - Any annotations + return Union None
10. `_utilities/checker.py` - Any annotations + return Union None

### Top 5 Alvos de Maior Impacto

1. **flext-core** (953 violações, P0) - Base de todo o ecossistema
2. **flext-ldif** (582 violações) - Domain library usado por taps/targets
3. **flext-workspace** (471 violações) - Ferramentas de infraestrutura
4. **algar-oud-mig** (289 violações) - Projeto custom de alto perfil
5. **flext-cli** (258 violações) - Platform library usada por meltano

---

## Estratégia de Correção por Categoria

### Categoria 1: `any_or_object_annotation` (45 arquivos, Prioridade Alta)

**Problema**: Uso de `Any`/`object` em type annotations

**Solução**:
- Substituir `Any` → `t.GeneralValueType`, `t.Scalar`, `t.ConfigMap`
- Substituir `object` → `t.GeneralValueType`
- Para `dict[str, Any]` → usar `t.ConfigMap` ou `t.Dict`

**Arquivos críticos para focar**:
1. `_utilities/mapper.py` (maior número de ocorrências)
2. `_models/base.py` (modelos base afetam todo o ecossistema)
3. `decorators.py`
4. `_models/collections.py`
5. `protocols.py` (contratos públicos)
6. `exceptions.py`
7. `runtime.py`
8. `container.py`
9. `registry.py`

### Categoria 2: `return_union_none` (52 arquivos, Prioridade Alta)

**Problema**: Funções retornando `T | None` para operações fallíveis

**Solução**:
- Converter retornos `T | None` → `r[T]` (FlextResult)
- Usar `r[T].ok(value)` para sucesso
- Usar `r.fail("mensagem")` para falha
- Compor com `map()`, `flat_map()`, `lash()`, `value_or()`

**Arquivos críticos**:
1. `_models/base.py`
2. `_utilities/mapper.py`
3. `protocols.py`
4. `exceptions.py`
5. `_models/collections.py`
6. `_utilities/guards.py`
7. `_utilities/checker.py`

### Categoria 3: `linter_suppression_comment` (21 arquivos, Prioridade Média)

**Problema**: Comentários `# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`

**Solução**:
- **REMOVER TODOS** - zero tolerância para supressões
- Corrigir o código subjacente em vez de suprimir
- Se houver caso edge legítimo, documentar com justificativa técnica detalhada

**Arquivos afetados**:
- `runtime.py`
- `flext_infra/codegen/__main__.py` (também tem `print()`)
- `flext_infra/codegen/transforms.py`
- Vários arquivos `__init__.py` em `flext_infra/`

### Categoria 4: `inline_composed_type` (14 arquivos, Prioridade Baixa)

**Problema**: Unions inline como `str | int | float | bool`

**Solução**:
- Definir tipos em `typings.py` usando `X: TypeAlias = ...`
- Usar aliases existentes: `t.Scalar`, `t.GeneralValueType`, `t.Primitives`
- NUNCA usar inline unions em código

**Arquivos críticos**:
1. `_utilities/mapper.py`
2. `_utilities/guards.py`
3. `exceptions.py`
4. `_models/collections.py`

### Categoria 5: Outras Violações (Baixo Volume)

- **`print_statement`** (1 arquivo): `flext_infra/codegen/__main__.py` - usar `FlextLogger`/structlog
- **`type_is_comparison`** (1 arquivo): `flext_tests/_validator/tests.py` - usar `isinstance()`

---

## Metis Review

### Gaps Identificados

1. **Escopo**: 33 projetos é um trabalho massivo (~4,200+ violações). A abordagem deve ser sequencial por fases, começando com flext-core (953 violações).

2. **Coordenação**: Lint fixes cruzam muitos arquivos (86 em flext-core), potencialmente violando regras de ownership. Solução: estruturar fixes por zona de ownership.

3. **Breaking Changes**: Mudanças de tipo (`Any` → `t.GeneralValueType`) afetam APIs públicas. Todas as chamadas em 33 projetos precisam ser atualizadas.

4. **Verificação**: Todos os 4 linters devem passar sem erros nem warnings. Testes devem continuar passando.

5. **Commits**: Regra AXIOMÁTICA de commit-after-validation - cada validação passando = commit + push imediato.

### Guardrails Aplicados

- **Fix forward only**: Nunca fazer rollback (`git revert`, `git reset`, `git checkout` para descartar trabalho)
- **Faseamento obrigatório**: Seguir CLAUDE.md §10 fases 0-4 na ordem correta
- **Ownership estrito**: Cada agente só toca seus arquivos designados
- **Zero supressões**: Nenhum comentário de supressão de linter permitido
- **ast-grep supremacy**: Todas as transformações de código via ast-grep (sg), nunca sed/awk/scripts custom

---

## Work Objectives

### Objetivo Principal
Corrigir 100% das violações de lint em todos os 33 projetos FLEXT, garantindo que:
1. Todos os 4 linters (ruff, mypy, pyright, pyrefly) passem com ZERO erros/warnings
2. Testes continuem passando (`make test`)
3. Código siga estritamente CLAUDE.md e skills
4. MRO inheritance e namespace composition estejam corretos

### Deliverables Concretos
- flext-core: 100% lint-clean (fases 0-3)
- 31 projetos consumidores: 100% lint-clean (fase 4)
- Todos os testes passando
- Documentação atualizada (se necessário)

### Definition of Done
- [ ] `make check` em cada projeto = ZERO erros de todos os 4 linters
- [ ] `make test` em cada projeto = todos os testes passando
- [ ] Zero comentários de supressão (# type: ignore, # noqa, etc.)
- [ ] Todos os commits pushed para remote
- [ ] `git status` limpo em todos os projetos

### Must Have
- Correção de TODAS as violações de tipo (Any, object, dict[str, Any], inline unions)
- Correção de TODAS as violações de import (ordem, relativos, wildcard)
- Correção de TODAS as violações de código (bare except, print(), type() narrowing)
- Aplicação de MRO inheritance em todos os módulos
- Conversão para Pydantic v2 patterns extensivamente

### Must NOT Have (Guardrails)
- NENHUMA supressão de linter (# type: ignore, # noqa)
- NENHUM script de automação para mass edits (use ast-grep apenas)
- NENHUM rollback de código (git revert, git reset)
- NENHUMA mudança fora do escopo de lint (novas features)
- NENHUM arquivo modificado fora do ownership do agente

---

## Verification Strategy

### Decisão de Testes
- **Infraestrutura existe**: Cada projeto tem pyproject.toml com configuração de testes
- **Testes automatizados**: SIM - `make test` em cada projeto
- **Framework**: pytest com coverage
- **Agent-Executed QA**: Cada tarefa inclui `make check` e `make test` como critério de aceitação

### Cenários de QA (Agent-Executados)

**Scenario: Validação de lint em flext-core**
  Tool: Bash
  Preconditions: Projeto flext-core clonado, dependências instaladas
  Steps:
    1. cd flext-core
    2. Executar: make check
    3. Verificar: Saída mostra "All checks passed" ou similar
    4. Verificar: Exit code = 0
    5. Verificar: Nenhum erro de ruff, mypy, pyright, pyrefly
  Expected Result: Todos os 4 linters passam com ZERO erros/warnings
  Evidence: Capturar saída completa do make check

**Scenario: Validação de testes em projeto**
  Tool: Bash
  Preconditions: Lint já passou no projeto
  Steps:
    1. cd <projeto>
    2. Executar: make test
    3. Verificar: Saída mostra "passed" para todos os testes
    4. Verificar: Exit code = 0
    5. Verificar: Coverage atinge threshold do pyproject.toml
  Expected Result: Todos os testes passam
  Evidence: Capturar saída completa do make test

**Scenario: Verificação de supressões**
  Tool: Bash (grep)
  Preconditions: Código já corrigido
  Steps:
    1. Executar: grep -r "# type: ignore" src/ tests/ examples/ || true
    2. Executar: grep -r "# noqa" src/ tests/ examples/ || true
    3. Verificar: Nenhuma ocorrência encontrada
  Expected Result: Zero comentários de supressão
  Evidence: Saída dos comandos grep (deve ser vazia)

---

## Execution Strategy

### Resumo das Fases (CLAUDE.md §10)

```
Fase 0 (SOLO): Agente 4 completa Wave 0 e faz PUSH
  → Todos os outros agentes BLOQUEADOS até Fase 0 completar

Fase 1 (Paralelo): Agente 4 continua + Agente 5 inicia
  → Ambos commitam e fazem push independentemente

Fase 2 (Paralelo): Agente 1 (Dispatcher) + Agente 3 (Service)
  → Ambos commitam e fazem push independentemente

Fase 3 (SOLO): Agente 2 (Registry)
  → Commita e faz push

Fase 4 (Paralelo): Todos os 5 agentes nos projetos consumidores
  → Cada agente trabalha em seus projetos designados em paralelo
```

### Matriz de Ownership (flext-core)

| Arquivo | Owner | Outros Permissão |
|---------|-------|------------------|
| `dispatcher.py` | Agente 1 | READ only |
| `constants.py` | Agente 1 | READ only |
| `_models/cqrs.py` | Agente 1 | READ only |
| `registry.py` | Agente 2 | READ only |
| `typings.py` | Agente 2 | READ only |
| `service.py` | Agente 3 | READ only |
| `_models/base.py` | Agente 3 | READ only |
| `result.py` | Agente 4 | READ only |
| `exceptions.py` | Agente 4 | READ only |
| `runtime.py` | Agente 4 | Agente 5 READ only |
| `loggings.py` | Agente 4 | READ only |
| `container.py` | Agente 5 (primary) | Agente 1: ADD only; Agente 4: return types only |
| `decorators.py` | Agente 5 | READ only |
| `handlers.py` | Agente 5 | READ only |
| `mixins.py` | Agente 5 | READ only |
| `protocols.py` | SECTION-OWNED | Cada agente: própria seção ONLY |
| `__init__.py` | ❄️ FROZEN | Cada agente adiciona apenas novos exports |

### Partição de Projetos Consumidores (Fase 4)

| Agente | Projetos | Count |
|--------|----------|-------|
| Agente 1 | `algar-oud-mig`, `flexcore`, `flext-api` | 3 |
| Agente 2 | `flext-auth`, `flext-cli`, `flext-db-oracle` | 3 |
| Agente 3 | `flext-grpc`, `flext-ldap`, `flext-ldif`, `flext-meltano` | 4 |
| Agente 4 | `flext-observability`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-quality`, `flext-tap-oracle-wms`, `flext-target-ldif` | 7 |
| Agente 5 | `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-target-ldap`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`, `flext-web`, `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`, `gruponos-meltano-native` | 14 |

### Critical Path

```
Fase 0 (Agente 4) → Fase 1 (Agente 4+5) → Fase 2 (Agente 1+3) → Fase 3 (Agente 2) → Fase 4 (Todos)
```

**Observações**:
- Cada fase só inicia quando a anterior completar e fizer push
- Na Fase 4, todos os 5 agentes trabalham em paralelo (zero overlap)
- Lint scoping: cada agente roda linters APENAS nos arquivos que modificou durante o trabalho paralelo
- No final de cada fase: agente que completou a fase roda FULL project lint (`make check`) antes de push

---

## TODOs

### FASE 0: flext-core - Wave 0 (Agente 4 - SOLO)

**BLOQUEANTE**: Todos os outros agentes aguardam esta fase completar.

- [ ] 0.1. Corrigir lint em result.py
  **O que fazer**:
  - Remover usos de `Any`, `object`, `dict[str, Any]`
  - Substituir por `t.GeneralValueType`, `t.Scalar`, `t.ConfigMap`
  - Garantir `from __future__ import annotations` no início
  - Corrigir type narrowing (usar `isinstance`, nunca `type()`)
  - Adicionar tipos de retorno explícitos em todos os métodos
  - Garantir uso correto de `r[T]` para operações fallíveis
  
  **Must NOT do**:
  - Não adicionar `# type: ignore` ou `# noqa`
  - Não usar `cast()` (exceto em casos justificados no código)
  - Não modificar outros arquivos além de result.py
  
  **Recommended Agent Profile**:
  - **Category**: ultrabrain (lógica complexa de tipos genéricos)
  - **Skills**: `flext-strict-typing`, `flext-patterns`, `flext-agent-strict-rules`
  
  **Parallelization**:
  - **Can Run In Parallel**: NO (fase SOLO)
  - **Blocks**: Toda Fase 1
  - **Blocked By**: Nada (início do projeto)
  
  **References**:
  - `flext-core/src/flext_core/result.py` - arquivo principal
  - `flext-core/src/flext_core/typings.py` - tipos disponíveis (t.*)
  - `flext-core/src/flext_core/protocols.py` - seção Result (linhas 299-512, A4)
  
  **Acceptance Criteria**:
  - [ ] ruff check result.py = 0 erros
  - [ ] mypy result.py = 0 erros
  - [ ] pyright result.py = 0 erros
  - [ ] pyrefly result.py = 0 erros
  - [ ] Nenhum `# type: ignore` ou `# noqa` no arquivo
  - [ ] Todos os métodos têm tipos de retorno explícitos
  
  **Agent-Executed QA Scenarios**:
  ```
  Scenario: Validação de lint em result.py
    Tool: Bash
    Steps:
      1. cd flext-core && ruff check src/flext_core/result.py
      2. cd flext-core && mypy src/flext_core/result.py
      3. cd flext-core && pyright src/flext_core/result.py
      4. cd flext-core && pyrefly check src/flext_core/result.py
    Expected Result: Todos os comandos retornam exit code 0
  ```
  
  **Commit**: YES
  - Message: `style(result): fix all lint violations in result.py`
  - Files: `flext-core/src/flext_core/result.py`
  - Pre-commit: `cd flext-core && make check`

- [ ] 0.2. Corrigir lint em exceptions.py
  **O que fazer**:
  - Remover usos de `Any`, `object`, `dict[str, Any]`
  - Substituir por tipos apropriados de `t.*`
  - Garantir `from __future__ import annotations`
  - Adicionar tipos de retorno explícitos
  
  **Must NOT do**:
  - Não adicionar supressões de linter
  - Não modificar outros arquivos
  
  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: `flext-strict-typing`, `flext-agent-strict-rules`
  
  **Parallelization**:
  - **Can Run In Parallel**: NO (fase SOLO)
  - **Blocks**: Toda Fase 1
  - **Blocked By**: Nada
  
  **References**:
  - `flext-core/src/flext_core/exceptions.py`
  - `flext-core/src/flext_core/protocols.py` - seções de exceções (A4)
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam (0 erros)
  - [ ] Zero supressões
  
  **Agent-Executed QA Scenarios**:
  ```
  Scenario: Validação de lint em exceptions.py
    Tool: Bash
    Steps:
      1. cd flext-core && ruff check src/flext_core/exceptions.py
      2. cd flext-core && mypy src/flext_core/exceptions.py
      3. cd flext-core && pyright src/flext_core/exceptions.py
      4. cd flext-core && pyrefly check src/flext_core/exceptions.py
    Expected Result: Todos os comandos retornam exit code 0
  ```
  
  **Commit**: YES (separado da task 0.1)

- [ ] 0.3. Corrigir lint em runtime.py
  **O que fazer**:
  - Aplicar mesmas regras de typing e import
  - Agente 5 pode ler este arquivo (MRO chain reference)
  
  **Must NOT do**:
  - Agente 4 é owner, Agente 5 é READ only
  
  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: `flext-strict-typing`
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 0.4. Corrigir lint em loggings.py
  **O que fazer**:
  - Aplicar regras de typing e import
  
  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: `flext-strict-typing`
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 0.5. Corrigir lint na seção Result de protocols.py (A4)
  **O que fazer**:
  - Corrigir apenas a seção Result (linhas aprox 299-512)
  - Adicionar protocols no final da seção (append only)
  - NUNCA reordenar ou tocar em outras seções
  
  **Must NOT do**:
  - Não tocar em seções de outros agentes
  - Não reordenar protocols existentes
  
  **Recommended Agent Profile**:
  - **Category**: quick
  - **Skills**: `flext-strict-typing`, `flext-architecture-layers`
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Seção Result lint-clean
  
  **Commit**: YES

- [ ] 0.6. Corrigir lint na seção ResultLike de protocols.py (A4)
  **O que fazer**:
  - Corrigir apenas protocols relacionados a ResultLike
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Seção ResultLike lint-clean
  
  **Commit**: YES

- [ ] 0.7. Corrigir lint na seção VariadicCallable de protocols.py (A4)
  **O que fazer**:
  - Corrigir apenas protocols VariadicCallable
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Seção VariadicCallable lint-clean
  
  **Commit**: YES

- [ ] 0.8. Corrigir lint na seção ResourceFactory de protocols.py (A4)
  **O que fazer**:
  - Corrigir apenas protocols ResourceFactory
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Seção ResourceFactory lint-clean
  
  **Commit**: YES

- [ ] 0.9. Corrigir lint na seção Log de protocols.py (A4)
  **O que fazer**:
  - Corrigir apenas protocols Log, StructlogLogger, Metadata
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Seções Log/StructlogLogger/Metadata lint-clean
  
  **Commit**: YES

- [ ] 0.10. Rodar FULL lint check em flext-core e fazer push
  **O que fazer**:
  - `cd flext-core && make check`
  - Verificar ZERO erros de todos os 4 linters
  - Commitar todas as mudanças
  - `git pull --rebase`
  - `git push`
  
  **Must NOT do**:
  - Não fazer push se houver qualquer erro de linter
  
  **Acceptance Criteria**:
  - [ ] `make check` retorna exit code 0
  - [ ] `git status` mostra "nothing to commit, working tree clean"
  - [ ] Push realizado com sucesso
  
  **Agent-Executed QA Scenarios**:
  ```
  Scenario: Full lint check em flext-core
    Tool: Bash
    Steps:
      1. cd flext-core
      2. make check
      3. echo $?  # Verificar exit code
    Expected Result: Exit code = 0
  ```
  
  **Commit**: YES (último commit da Fase 0)
  - Message: `style(flext-core): complete Wave 0 lint fixes - phase ready`

---

### FASE 1: flext-core - Wave 1 (Agente 4 + Agente 5 - PARALELO)

**Pré-condição**: Aguardar Fase 0 completar e fazer `git pull --rebase`

#### Agente 4 Tasks:

- [ ] 1.1. Continuar correções em result.py (exception propagation, safe(), chaining)
  **O que fazer**:
  - Completar quaisquer correções restantes em result.py
  - Adicionar métodos safe(), chaining patterns
  - Garantir que todos os tipos estão corretos
  
  **Recommended Agent Profile**:
  - **Category**: ultrabrain
  - **Skills**: `flext-strict-typing`, `flext-patterns`, `flext-agent-strict-rules`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (com Agente 5)
  - **Blocks**: Nada (dentro da fase)
  - **Blocked By**: Fase 0 completa
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam em result.py
  
  **Commit**: YES

- [ ] 1.2. Atualizar seções de protocols.py (A4) conforme necessário
  **O que fazer**:
  - Ajustar protocols nas seções de ownership do A4
  
  **Acceptance Criteria**:
  - [ ] Seções A4 lint-clean
  
  **Commit**: YES

#### Agente 5 Tasks:

- [ ] 1.3. Corrigir lint em container.py
  **O que fazer**:
  - Remover usos proibidos de typing
  - Corrigir imports e ordem
  - Adicionar tipos de retorno
  - Aplicar Pydantic v2 patterns
  
  **Must NOT do**:
  - Agente 1 pode fazer ADD only no dispatcher singleton
  - Agente 4 pode modificar apenas return types
  
  **Recommended Agent Profile**:
  - **Category**: deep (DI container é complexo)
  - **Skills**: `flext-strict-typing`, `lib-dependency-injector`, `flext-patterns`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (com Agente 4)
  - **Blocks**: Nada (dentro da fase)
  - **Blocked By**: Fase 0 completa
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam em container.py
  - [ ] Agente 1 e 4 podem fazer modificações permitidas
  
  **Commit**: YES

- [ ] 1.4. Corrigir lint em decorators.py
  **O que fazer**:
  - Corrigir typing e imports
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 1.5. Corrigir lint em handlers.py
  **O que fazer**:
  - Corrigir typing e imports
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 1.6. Corrigir lint em mixins.py
  **O que fazer**:
  - Corrigir typing e imports
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 1.7. Corrigir lint nas seções de protocols.py (A5)
  - Context, RuntimeBootstrapOptions, DI
  - Handler
  - RegisterableService, ServiceFactory
  
  **Acceptance Criteria**:
  - [ ] Seções A5 lint-clean
  
  **Commit**: YES

- [ ] 1.8. Fazer commit e push (Agente 5)
  **O que fazer**:
  - Commitar todas as mudanças do Agente 5
  - `git pull --rebase`
  - `git push`
  
  **Acceptance Criteria**:
  - [ ] Push realizado
  
  **Commit**: YES

- [ ] 1.9. Fazer commit e push (Agente 4)
  **O que fazer**:
  - Commitar todas as mudanças do Agente 4
  - `git pull --rebase`
  - `git push`
  
  **Acceptance Criteria**:
  - [ ] Push realizado
  
  **Commit**: YES

---

### FASE 2: flext-core - Wave 2 (Agente 1 + Agente 3 - PARALELO)

**Pré-condição**: Aguardar Fase 1 completar e fazer `git pull --rebase`

#### Agente 1 Tasks:

- [ ] 2.1. Corrigir lint em dispatcher.py
  **O que fazer**:
  - Corrigir typing e imports
  - Aplicar patterns de MRO inheritance
  
  **Recommended Agent Profile**:
  - **Category**: deep (orquestração complexa)
  - **Skills**: `flext-strict-typing`, `flext-architecture-layers`, `flext-patterns`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (com Agente 3)
  - **Blocks**: Nada (dentro da fase)
  - **Blocked By**: Fase 1 completa
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 2.2. Corrigir lint em constants.py
  **O que fazer**:
  - Corrigir typing e imports
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 2.3. Corrigir lint em _models/cqrs.py
  **O que fazer**:
  - Corrigir typing e imports
  - Aplicar Pydantic v2 patterns
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 2.4. Corrigir lint nas seções de protocols.py (A1)
  - CommandBus, Middleware, Processor
  
  **Acceptance Criteria**:
  - [ ] Seções A1 lint-clean
  
  **Commit**: YES

- [ ] 2.5. Fazer commit e push (Agente 1)
  **Acceptance Criteria**:
  - [ ] Push realizado
  
  **Commit**: YES

#### Agente 3 Tasks:

- [ ] 2.6. Corrigir lint em service.py
  **O que fazer**:
  - Corrigir typing e imports
  - Aplicar patterns de serviço
  
  **Recommended Agent Profile**:
  - **Category**: deep
  - **Skills**: `flext-strict-typing`, `flext-patterns`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (com Agente 1)
  - **Blocks**: Nada (dentro da fase)
  - **Blocked By**: Fase 1 completa
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 2.7. Corrigir lint em _models/base.py
  **O que fazer**:
  - Corrigir typing e imports
  - Aplicar Pydantic v2 patterns
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 2.8. Corrigir lint nas seções de protocols.py (A3)
  - Model, Config, Service, Validation
  - ValidatorSpec
  
  **Acceptance Criteria**:
  - [ ] Seções A3 lint-clean
  
  **Commit**: YES

- [ ] 2.9. Fazer commit e push (Agente 3)
  **Acceptance Criteria**:
  - [ ] Push realizado
  
  **Commit**: YES

---

### FASE 3: flext-core - Wave 3 (Agente 2 - SOLO)

**Pré-condição**: Aguardar Fase 2 completar e fazer `git pull --rebase`

- [ ] 3.1. Corrigir lint em registry.py
  **O que fazer**:
  - Corrigir typing e imports
  - Aplicar patterns de registro
  
  **Recommended Agent Profile**:
  - **Category**: deep
  - **Skills**: `flext-strict-typing`, `flext-patterns`
  
  **Parallelization**: NO (fase SOLO)
  
  **Acceptance Criteria**:
  - [ ] Todos os 4 linters passam
  
  **Commit**: YES

- [ ] 3.2. Corrigir lint em typings.py
  **O que fazer**:
  - Verificar CRITICAMENTE a tabela de aliases (NAMED ALIAS TABLE)
  - NON-RECURSIVE aliases DEVEM usar `X: TypeAlias = ...`
  - RECURSIVE aliases DEVEM usar `type X = ...`
  - NUNCA mudar a syntax sem aprovação explícita
  - Rodar MANDATORY CRASH TEST antes e depois:
    ```bash
    python3 -c "import sys; [sys.modules.pop(k) for k in list(sys.modules) if 'flext' in k]; import flext_core; t=flext_core.t; [print('PASS',n) if isinstance('x',getattr(t,n)) else print('FAIL',n) for n in ['Primitives','Scalar','Container','MetadataValue','RegisterableService']]"
    ```
  - Resultado esperado: 5 linhas começando com PASS
  
  **Must NOT do**:
  - NUNCA mudar `X: TypeAlias = ...` para `type X = ...` em aliases não-recursivos
  - NUNCA usar `isinstance()` com aliases recursivos
  
  **Recommended Agent Profile**:
  - **Category**: ultrabrain (tipos complexos, risco de runtime crash)
  - **Skills**: `flext-strict-typing`, `flext-type-system`, `python-313-typing`
  
  **Acceptance Criteria**:
  - [ ] MANDATORY CRASH TEST passa (5 PASS)
  - [ ] Todos os 4 linters passam
  - [ ] Zero mudanças em aliases sem aprovação
  
  **Commit**: YES

- [ ] 3.3. Corrigir lint na seção Registry de protocols.py (A2)
  **O que fazer**:
  - Corrigir apenas seção Registry
  
  **Acceptance Criteria**:
  - [ ] Seção A2 lint-clean
  
  **Commit**: YES

- [ ] 3.4. Rodar FULL lint check em flext-core e fazer push
  **O que fazer**:
  - `cd flext-core && make check`
  - Verificar ZERO erros
  - Commitar e fazer push
  
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] Push realizado
  
  **Commit**: YES
  - Message: `style(flext-core): complete lint fixes - all phases done`

---

### FASE 4: Projetos Consumidores (Todos os 5 Agentes - PARALELO)

**Pré-condição CRÍTICA**: TODOS os agentes DEVEM:
1. Rodar `cd flext-core && make check` e verificar ZERO erros
2. Fazer `git pull --rebase` no flext-core
3. SÓ ENTÃO começar nos projetos consumidores

**Abordagem**: Cada agente trabalha em seus projetos designados em paralelo.

#### Agente 1 Projetos (3):

- [ ] 4.1. Corrigir lint em `algar-oud-mig`
  **O que fazer**:
  - Aplicar todas as regras de lint
  - Garantir MRO inheritance correto
  - Herdar de facades dos projetos pais conforme arquitetura
  
  **Acceptance Criteria**:
  - [ ] `make check` passa (ZERO erros)
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.2. Corrigir lint em `flexcore`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.3. Corrigir lint em `flext-api`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

#### Agente 2 Projetos (3):

- [ ] 4.4. Corrigir lint em `flext-auth`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.5. Corrigir lint em `flext-cli`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.6. Corrigir lint em `flext-db-oracle`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

#### Agente 3 Projetos (4):

- [ ] 4.7. Corrigir lint em `flext-grpc`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.8. Corrigir lint em `flext-ldap`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.9. Corrigir lint em `flext-ldif`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.10. Corrigir lint em `flext-meltano`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

#### Agente 4 Projetos (7):

- [ ] 4.11. Corrigir lint em `flext-observability`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.12. Corrigir lint em `flext-oracle-oic`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.13. Corrigir lint em `flext-oracle-wms`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.14. Corrigir lint em `flext-plugin`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.15. Corrigir lint em `flext-quality`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.16. Corrigir lint em `flext-tap-oracle-wms`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.17. Corrigir lint em `flext-target-ldif`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

#### Agente 5 Projetos (14):

- [ ] 4.18. Corrigir lint em `flext-tap-ldap`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.19. Corrigir lint em `flext-tap-ldif`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.20. Corrigir lint em `flext-tap-oracle`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.21. Corrigir lint em `flext-tap-oracle-oic`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.22. Corrigir lint em `flext-target-ldap`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.23. Corrigir lint em `flext-target-oracle`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.24. Corrigir lint em `flext-target-oracle-oic`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.25. Corrigir lint em `flext-target-oracle-wms`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.26. Corrigir lint em `flext-web`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.27. Corrigir lint em `flext-dbt-ldap`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.28. Corrigir lint em `flext-dbt-ldif`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.29. Corrigir lint em `flext-dbt-oracle`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.30. Corrigir lint em `flext-dbt-oracle-wms`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

- [ ] 4.31. Corrigir lint em `gruponos-meltano-native`
  **Acceptance Criteria**:
  - [ ] `make check` passa
  - [ ] `make test` passa
  
  **Commit**: YES

---

## Commit Strategy

| Após Task | Mensagem | Arquivos | Verificação |
|-----------|----------|----------|-------------|
| Cada arquivo | `style(scope): fix lint violations in <file>` | `<file>.py` | `make check` no arquivo |
| Cada fase | `style(flext-core): complete <phase> lint fixes` | Todos da fase | `make check` completo |
| Cada projeto | `style(<project>): fix all lint violations` | Todo o projeto | `make check && make test` |

**AXIOMATIC Commit-After-Validation**:
Após QUALQUER validação passar (linters, testes, `make check`), TODAS as mudanças pendentes DEVEM ser commitadas e pushed IMEDIATAMENTE.

Sequência obrigatória:
1. Validação passa
2. `git add -A` (em todo projeto com mudanças)
3. `git commit -m "<mensagem convencional>"`
4. `git pull --rebase`
5. `git push`
6. Confirmar `git status` limpo

---

## Success Criteria

### Comandos de Verificação Final

```bash
# Para cada um dos 33 projetos:
cd <projeto>
make check    # Deve retornar exit code 0
make test     # Deve retornar exit code 0, todos os testes passando

# Verificação de supressões:
grep -r "# type: ignore" src/ tests/ examples/ || true  # Deve retornar vazio
grep -r "# noqa" src/ tests/ examples/ || true          # Deve retornar vazio
grep -r "# pyright: ignore" src/ tests/ examples/ || true  # Deve retornar vazio
grep -r "# pyrefly: ignore" src/ tests/ examples/ || true  # Deve retornar vazio

# Verificação git:
git status    # Deve mostrar "nothing to commit, working tree clean"
git log --oneline -5  # Deve mostrar commits recentes do projeto
```

### Checklist Final

- [ ] Todos os 33 projetos: `make check` = ZERO erros de todos os 4 linters
- [ ] Todos os 33 projetos: `make test` = todos os testes passando
- [ ] Zero comentários de supressão (# type: ignore, # noqa, etc.)
- [ ] Todos os commits feitos e pushed para remote
- [ ] `git status` limpo em todos os projetos
- [ ] flext-core: MANDATORY CRASH TEST passa (5 PASS)
- [ ] Todos os projetos seguem MRO inheritance corretamente
- [ ] Zero usos de `Any`, `object`, `dict[str, Any]` em type annotations
- [ ] Zero inline unions (`str | int | float | bool`)
- [ ] Todos os arquivos têm `from __future__ import annotations`
- [ ] Zero imports relativos ou wildcard imports

---

## Considerações Importantes

### 1. Multi-Agente Coordenação
- Cada agente tem ownership estrito de arquivos
- Nunca tocar arquivos de outros agentes
- Em caso de conflito em arquivo próprio: resolver manualmente
- Em caso de conflito em arquivo de outro: `git checkout --theirs <file>`

### 2. protocols.py
- Cada agente toca apenas sua(s) seção(ões)
- Sempre adicionar no final da seção (append only)
- NUNCA reordenar ou reformatar globalmente
- Seções marcadas como ❄️ FROZEN não devem ser modificadas

### 3. FROZEN Files
- `context.py`, `settings.py`, `models.py`, `utilities.py`
- `_utilities/*`, `_runtime_metadata.py`, `__version__.py`
- `__init__.py` (apenas adicionar novos exports)

Estes arquivos só podem ser modificados para adicionar annotations (type hints, Field(), PrivateAttr) necessários para regras AXIOMÁTICAS. Nunca modificar lógica comportamental.

### 4. Testes e Exemplos
- Todos os arquivos em `tests/` e `examples/` DEVEM seguir as mesmas regras
- Não há relaxamento "test-only" ou "example-only"
- Test fixtures devem usar `Field()`, modelos tipados, retornos `r[T]`
- Dados de teste devem usar tipos `t.*`

### 5. ast-grep Supremacy
- Usar `ast-grep` (sg) para TODAS as transformações estruturais
- NUNCA usar sed, awk, scripts custom, ou pipelines shell para transformar código
- Workflow: (1) `ast-grep search` → (2) `ast-grep replace` → (3) `make check`

### 6. Git Immutability (AXIOMÁTICO)
- NUNCA fazer rollback: `git revert`, `git reset`, `git checkout <file>` para descartar trabalho
- SEMPRE fix forward: aceitar, melhorar, e corrigir para frente
- `git checkout --theirs` SÓ permitido durante rebase de arquivo que você NÃO own

---

## Próximos Passos

Para iniciar a execução deste plano:

1. Execute `/start-work` para ativar o orquestrador Sisyphus
2. Sisyphus irá:
   - Registrar este plano como o boulder ativo
   - Iniciar a Fase 0 (Agente 4 solo)
   - Coordenar as transições de fase
   - Garantir que todas as regras sejam seguidas

**ATENÇÃO**: Este é um trabalho de grande escala (XL). Recomenda-se:
- Reservar tempo adequado (4-6 semanas)
- Monitorar progresso regularmente
- Fazer backups antes de começar (embora git immutability garanta histórico)
- Ter disponibilidade para resolver conflitos de merge

---

*Plano criado por: Prometheus (Planner)*
*Data: 2026-03-04*
*Versão: 1.0*
*Baseado em: CLAUDE.md §10, flext-quality-gates, flext-strict-typing, flext-import-rules, flext-agent-strict-rules, flext-5agent-coordination*
