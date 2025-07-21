# CLAUDE.PYTEST_DEBUGGING.md - Processo de Debug de Testes

**Hierarchy**: PROJECT-SPECIFIC - Debugging workflow  
**Reference**: `/home/marlonsc/CLAUDE.md` → Universal methodology  
**Reference**: `/home/marlonsc/flext/flext-api/CLAUDE.md` → Project guidance  
**Last Updated**: 2025-01-20

---

## CONTEXTO DA SESSÃO ATUAL

### Estado Anterior

- **33 projetos padronizados**: pyproject.toml 100% sucessful
- **Erros críticos de import**: Resolvidos em múltiplos projetos
- **flext-api**: 50/50 testes passando após fixes críticos

### Problema Atual em Investigação

**Pipeline storage/retrieval issue**: Pipelines criados não aparecem em operações de listagem, mesmo com singleton pattern implementado.

### Progresso da Sessão

- ✅ **Pydantic imports**: UUID/datetime movidos para runtime imports
- ✅ **Field naming**: Corrigido `pipeline_id` vs `id`, `total_count` vs `total`
- ✅ **Repository methods**: Corrigido `list_all()` para `list(limit, offset)`
- ✅ **Singleton pattern**: Implementado para compartilhar estado entre requests
- 🔄 **Investigando**: Route conflicts e dependency injection issues

---

## METODOLOGIA DE DEBUG APLICADA

### 1. Investigação Sistemática

```bash
# Sempre começar verificando estado real
pytest tests/unit/test_main_endpoints.py::test_list_pipelines_after_creation -v
```

### 2. Análise de Root Cause

1. **Ler código primeiro**: Nunca assumir baseado em nomes
2. **Verificar implementação real**: Usar Read tool extensivamente
3. **Tracear fluxo de dados**: Desde endpoint até repository
4. **Identificar discrepâncias**: Entre expectativa e implementação

### 3. Pattern de Fixes Aplicados

#### Fix 1: Pydantic Forward References

```python
# ANTES - Causava model_rebuild() failures
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from uuid import UUID

# DEPOIS - Runtime imports obrigatórios
from uuid import UUID  # noqa: TC003
```

#### Fix 2: Repository Method Names

```python
# ANTES - Método inexistente
pipelines = await self.pipeline_repo.list_all()

# DEPOIS - Método correto
pipelines = await self.pipeline_repo.list(limit=1000, offset=0)
```

#### Fix 3: Singleton Repository Pattern

```python
# ANTES - Nova instância a cada request
def get_pipeline_service() -> PipelineService:
    return PipelineService(pipeline_repo=InMemoryPipelineRepository())

# DEPOIS - Instância compartilhada
_pipeline_repository_instance: PipelineRepository | None = None

def get_pipeline_service() -> PipelineService:
    global _pipeline_repository_instance
    if _pipeline_repository_instance is None:
        _pipeline_repository_instance = InMemoryPipelineRepository()
    return PipelineService(pipeline_repo=_pipeline_repository_instance)
```

#### Fix 4: Field Name Consistency

```python
# Testes esperam especificamente:
assert "pipeline_id" in data  # NÃO "id"
assert "total_count" in data  # NÃO "total"

# Request format:
client.post("/api/v1/pipelines", json={...})  # NÃO params=
```

---

## PADRÕES DE ERRO IDENTIFICADOS

### 1. **Pydantic v2 Import Issues**

**Sintomas**: `name 'UUID' is not defined` durante model_rebuild()
**Causa**: Imports em TYPE_CHECKING blocks não disponíveis em runtime
**Fix**: Mover para runtime imports com `# noqa: TC003`

### 2. **Repository Interface Mismatch**

**Sintomas**: `'object' has no attribute 'list_all'`
**Causa**: Service chamando métodos inexistentes
**Fix**: Verificar interface real vs esperada

### 3. **Dependency Injection State Loss**

**Sintomas**: Dados criados não aparecem em queries subsequentes
**Causa**: Nova instância de repository a cada request
**Fix**: Implementar singleton pattern

### 4. **Test Assertion Mismatches**

**Sintomas**: KeyError em testes, campos não encontrados
**Causa**: Testes assumindo nomes de campos incorretos
**Fix**: Alinhar com API response real

---

## PRÓXIMOS PASSOS PARA CONTINUAR

### Investigação Atual: Route Conflicts

**Status**: Em andamento - pipelines criados via router não aparecem em main.py endpoints

#### Hipóteses a Investigar

1. **Multiple route definitions**: Router vs main.py endpoints
2. **Different dependency scopes**: Router dependencies vs main dependencies  
3. **Storage isolation**: Separate repository instances per router

#### Comandos para Debug

```bash
# Testar endpoint específico que falha
pytest tests/unit/test_main_endpoints.py::test_list_pipelines_after_creation -v -s

# Verificar se problema é com router endpoints
pytest tests/unit/ -k "pipeline" --tb=short

# Debug com print statements (temporário)
python -c "
from flext_api.dependencies import get_pipeline_service
svc = get_pipeline_service()
print(f'Repository instance: {id(svc.pipeline_repo)}')
print(f'Storage: {svc.pipeline_repo._storage}')
"
```

#### Arquivos para Investigar

1. `src/flext_api/main.py` - Como router está integrado
2. `src/flext_api/endpoints/pipelines.py` - Router endpoints
3. `src/flext_api/dependencies.py` - Dependency injection scope
4. `tests/unit/test_main_endpoints.py` - Onde teste falha

### Pattern de Resolução Esperado

1. **Identificar causa**: Router vs main.py endpoint conflicts
2. **Implementar fix**: Unificar dependency scopes ou routers
3. **Validar fix**: Teste completo passa
4. **Atualizar documentação**: Adicionar pattern ao CLAUDE.md

---

## VALIDAÇÃO ANTES DE COMMIT

### Quality Gates Obrigatórios

```bash
# SEMPRE executar antes de finalizar
make check          # Deve passar 100%

# Verificação específica de testes
pytest tests/unit/test_main_endpoints.py -v
pytest tests/unit/ -k "pipeline" --tb=short
```

### Success Criteria

- ✅ Todos os testes de pipeline passando
- ✅ Pipeline criado aparece em list endpoints
- ✅ Field names consistentes (`pipeline_id`, `total_count`)
- ✅ Singleton pattern mantendo estado
- ✅ Sem erros de import ou type checking

---

## LIÇÕES APRENDIDAS DESTA SESSÃO

### 1. **Pydantic v2 Requer Runtime Imports**

Imports em TYPE_CHECKING causam falhas silenciosas em model_rebuild()

### 2. **Repository Pattern Precisa de Singleton**

FastAPI cria nova instância por request sem singleton pattern

### 3. **Test Assertions Devem Espelhar API Real**

Testes devem usar campos exatos da resposta, não assumir nomes

### 4. **Interface Repository Deve Ser Verificada**

Métodos chamados devem existir na implementação real

### 5. **Debug Sistemático É Essencial**

Ler código antes de assumir comportamento

---

## PARA PRÓXIMA SESSÃO CLAUDE

### Se Pipeline Storage Ainda Falhar

1. **Ler este arquivo primeiro** para entender contexto
2. **Executar diagnostic commands** listados acima
3. **Investigar router integration** em main.py
4. **Verificar dependency scopes** entre router e main
5. **Implementar fix específico** baseado em achados

### Se Outros Testes Falharem

1. **Aplicar patterns desta sessão**:
   - Pydantic imports pattern
   - Singleton repository pattern
   - Field name verification
2. **Usar metodologia sistemática**:
   - Read código antes de assumir
   - Verificar implementação real
   - Aplicar fix específico
   - Validar com testes

### Files Críticos para Monitorar

- `src/flext_api/models/pipeline.py` - Pydantic imports
- `src/flext_api/dependencies.py` - Singleton pattern
- `src/flext_api/endpoints/pipelines.py` - Router endpoints
- `tests/unit/test_main_endpoints.py` - Test assertions

---

**Status**: Debugging em progresso - pipeline storage issue  
**Next Action**: Investigar router vs main.py endpoint conflicts  
**Success Pattern**: Apply systematic debugging + verify real implementation  
**Critical**: Manter patterns de fix descobertos nesta sessão
