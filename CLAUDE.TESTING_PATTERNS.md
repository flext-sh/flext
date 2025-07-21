# CLAUDE.TESTING_PATTERNS.md - Padrões de Teste e Correção de Lint

**Hierarquia**: WORKSPACE-PATTERNS  
**Referência**: `/home/marlonsc/CLAUDE.md` → Metodologia universal  
**Referência**: `./CLAUDE.md` → Padrões do workspace FLEXT  
**Última Atualização**: 2025-01-20

---

## 🎯 MISSÃO ATUAL: Correção Sistemática de Lint e Testes

### Status do Progresso

- ✅ **FLEXT API**: Todos os 31 erros de lint corrigidos
- ✅ **Pipeline Endpoints**: Conflitos de criação/listagem resolvidos
- ✅ **Testes Funcionais**: 100% dos testes passando sem skip
- ✅ **Singleton Pattern**: Implementado para persistência de dados
- ✅ **Field Naming**: Padronização `pipeline_id`, `total_count`
- 🔄 **Documentação**: CLAUDE.md atualizado com padrões descobertos

---

## 🔧 PADRÕES CRÍTICOS DESCOBERTOS

### 1. Singleton Repository Pattern (FUNDAMENTAL)

**Problema Resolvido**: Pipelines criados não apareciam na listagem

**Solução Implementada**:

```python
# Global repository instance - CRITICAL para persistência
_pipeline_repository_instance: PipelineRepository | None = None

def get_pipeline_service() -> PipelineService:
    global _pipeline_repository_instance
    if _pipeline_repository_instance is None:
        _pipeline_repository_instance = InMemoryPipelineRepository()
    return PipelineService(pipeline_repo=_pipeline_repository_instance)
```

**Por que funciona**: Garante que todos os endpoints compartilhem a mesma instância de repositório em memória.

### 2. Nomenclatura de Campos (API Response Standards)

**Padrão Obrigatório**:

- `pipeline_id` (NUNCA `id`)
- `total_count` (NUNCA `total`)
- Requests POST usam `json=` (NUNCA `params=`)

**Teste Pattern**:

```python
# ✅ CORRETO
response = client.post("/api/v1/pipelines", json={"name": "test"})
assert response.json()["pipeline_id"]  # Campo correto
assert response.json()["total_count"]  # Campo correto

# ❌ ERRADO
response = client.post("/api/v1/pipelines", params={"name": "test"})
assert response.json()["id"]  # Campo incorreto
```

### 3. Import Pattern para Pydantic

**CRÍTICO**: UUID e datetime DEVEM ser imports runtime:

```python
# ✅ CORRETO - Runtime imports
from uuid import UUID  # noqa: TC003
from datetime import datetime  # noqa: TC003

# ❌ ERRADO - Causa falhas em model_rebuild()
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from uuid import UUID
    from datetime import datetime
```

---

## 🧪 METODOLOGIA DE CORREÇÃO DE TESTES

### Fase 1: Identificação de Conflitos

1. **Executar todos os testes**: `make test`
2. **Identificar falhas específicas**: Focar em 422 validation errors
3. **Mapear endpoints conflitantes**: POST vs GET inconsistencies

### Fase 2: Análise de Código

1. **Verificar dependencies.py**: Singleton pattern implementado?
2. **Checar field naming**: `pipeline_id` vs `id` consistency
3. **Validar request format**: `json=` vs `params=`

### Fase 3: Implementação Sistemática

1. **Corrigir um endpoint por vez**: Create → List → Get → Execute
2. **Validar com testes**: Executar teste específico após cada correção
3. **Verificar integração**: Testar workflow completo

### Fase 4: Validação Final

1. **Todos os testes passando**: `make test` = 100% success
2. **Lint limpo**: `make lint` = 0 violations
3. **Type check**: `make type-check` = 0 errors

---

## 🎯 COMANDOS ESSENCIAIS PARA DEBUGGING

### Testes Específicos

```bash
# Testar endpoint específico
pytest tests/unit/test_main_endpoints.py::test_create_pipeline_endpoint -v

# Debug com output completo
pytest -vvv --tb=long tests/unit/test_main_endpoints.py

# Testar workflow completo
pytest -k "workflow" -v

# Coverage detalhado
pytest --cov-report=html
```

### Lint e Type Check

```bash
# Lint projeto específico
cd flext-api && make lint

# Type check com detalhes
cd flext-api && make type-check

# Check completo
cd flext-api && make check
```

---

## 📋 CHECKLIST DE QUALIDADE (ZERO TOLERANCE)

### Antes de Cada Commit

- [ ] **Lint**: `make lint` = 0 violations
- [ ] **Type Check**: `make type-check` = 0 errors  
- [ ] **Tests**: `make test` = 100% pass rate
- [ ] **Coverage**: Mínimo 90% coverage
- [ ] **No conflitos**: Singleton pattern implementado
- [ ] **Field naming**: Nomenclatura padronizada

### Validação de Endpoints

- [ ] **Create**: POST com `json=`, retorna `pipeline_id`
- [ ] **List**: GET retorna `total_count`, array `pipelines`
- [ ] **Get**: GET por ID retorna objeto completo
- [ ] **Execute**: POST atualiza status para `running`

---

## 🚨 ANTI-PATTERNS IDENTIFICADOS

### 1. Múltiplas Instâncias de Repository

**NUNCA**: Criar nova instância a cada request
**SEMPRE**: Usar singleton pattern global

### 2. Inconsistência de Field Names

**NUNCA**: Misturar `id`/`pipeline_id` ou `total`/`total_count`
**SEMPRE**: Usar nomenclatura padronizada consistente

### 3. Request Format Mismatch

**NUNCA**: Usar `params=` para POST requests
**SEMPRE**: Usar `json=` para dados estruturados

### 4. TYPE_CHECKING para Runtime Types

**NUNCA**: Colocar UUID/datetime em TYPE_CHECKING
**SEMPRE**: Import runtime com `# noqa: TC003`

---

## 🔄 PRÓXIMOS PASSOS

### Para Futuras Sessões Claude

1. **Verificar este documento primeiro**: Antes de modificar qualquer código
2. **Aplicar padrões estabelecidos**: Não reinventar soluções
3. **Validar com comandos específicos**: Usar comandos documentados
4. **Manter singleton pattern**: NUNCA quebrar a persistência de dados
5. **Seguir nomenclatura**: Field names são CRÍTICOS

### Expansão dos Padrões

- Aplicar padrões similares em outros projetos FLEXT
- Documentar novos anti-patterns descobertos
- Criar templates para novos endpoints

---

## 🏆 RESULTADOS ALCANÇADOS

### Métricas de Sucesso

- **31 lint errors** → **0 lint errors**
- **Testes falhando** → **100% testes passando**
- **Pipeline creation/listing disconnect** → **Funcionalidade completa**
- **Field naming inconsistency** → **Nomenclatura padronizada**
- **Request format errors** → **Formato consistente**

### Padrões Estabelecidos

- Singleton repository pattern (reutilizável)
- Field naming standards (aplicável workspace-wide)
- Import patterns para Pydantic (universal)
- Test debugging methodology (reproduzível)

---

**Autoridade**: Padrões específicos para correção de testes e lint no FLEXT
**Escopo**: Metodologia reproduzível para manutenção de qualidade
**Manutenção**: Atualizar quando novos padrões forem descobertos

---

## 📚 REFERÊNCIAS CRUZADAS

- **flext-api/CLAUDE.md**: Implementação específica dos padrões
- **flext-core/CLAUDE.md**: Foundation patterns utilizados
- **CLAUDE.md**: Workspace standards e quality gates
- **CLAUDE.local.md**: Issues temporários relacionados
