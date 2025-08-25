# FLEXT - Matriz de Padrões Semânticos PEP

## Prefixos Semânticos por Categoria

### 1. **Flext** - Classes e Componentes Principais

**Uso**: Classes, interfaces, protocolos, componentes principais
**Padrão**: `FlextXxxYyy` (PascalCase)

```python
# ✅ Correto
class FlextResult[T]:
class FlextEntity:
class FlextContainer:
class FlextSettings:
class FlextApiClient:
class FlextLogContext:

# ❌ Incorreto
class flextResult:  # snake_case
class FlextAPIClient:  # Siglas em maiúsculo
class FLEXT_Container:  # SCREAMING_SNAKE_CASE
```

### 2. **TFlext** / **T** - Tipos e TypeVars

**Uso**: Type aliases, TypeVars, protocolos de tipo
**Padrão**: `TFlextXxx` ou `TXxx` (PascalCase com T prefix)

```python
# ✅ Correto - Type aliases específicos FLEXT
TFlextEntityId = TypeVar("TFlextEntityId", bound=int | str)
TFlextResult = FlextResult[T]
TFlextConfig = Dict[str, object]

# ✅ Correto - Type aliases genéricos
TEntityId = TypeVar("TEntityId", bound=int | str)
TData = TypeVar("TData")
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")

# ❌ Incorreto
flext_entity_id = int  # snake_case
FlextEntityId = int    # Sem prefixo T
```

### 3. **flext\_** - Módulos, Pacotes e Funções

**Uso**: Nomes de módulos, packages, funções, variáveis
**Padrão**: `flext_xxx_yyy` (snake_case)

```python
# ✅ Correto - Packages
flext_core
flext_api
flext_auth
flext_db_oracle

# ✅ Correto - Funções
def flext_create_client():
def flext_api_create_app():
def flext_core_setup():

# ✅ Correto - Módulos
flext_auth.py
flext_client.py
flext_config.py

# ❌ Incorreto
flexCore  # camelCase
FLEXT_API  # SCREAMING_SNAKE_CASE
FlextModule  # PascalCase para módulo
```

### 4. **FLEXT\_** - Constantes e Configurações

**Uso**: Constantes, environment variables, configurações globais
**Padrão**: `FLEXT_XXX_YYY` (SCREAMING_SNAKE_CASE)

```python
# ✅ Correto
FLEXT_VERSION = "0.9.0"
FLEXT_DEFAULT_TIMEOUT = 30
FLEXT_MAX_RETRIES = 3
FLEXT_LOG_LEVEL = "INFO"

# Environment variables
FLEXT_API_HOST = "0.0.0.0"
FLEXT_DB_CONNECTION_STRING = "postgresql://..."

# ❌ Incorreto
flext_version = "0.9.0"  # snake_case
FlextVersion = "0.9.0"   # PascalCase
flextVERSION = "0.9.0"   # mixedCase
```

## Padrões por Tipo de Componente

### Entidades de Domínio (DDD)

```python
# Classes base
class FlextEntity[TId]:
class FlextValue:
class FlextAggregateRoot[TId]:
class FlextDomainService:

# Tipos relacionados
TFlextEntityId = TypeVar("TFlextEntityId")
TFlextDomainEvent = TypeVar("TFlextDomainEvent")

# Implementações específicas
class FlextUser(FlextEntity[int]):
class FlextEmail(FlextValue):
```

### Padrões Arquiteturais

```python
# CQRS
class FlextCommand:
class FlextQuery:
class FlextCommandHandler[TCommand]:
class FlextQueryHandler[TQuery, TResult]:

# Repository Pattern
class FlextRepository[TEntity, TId]:
class FlextUserRepository(FlextRepository[FlextUser, int]):

# Service Layer
class FlextApplicationService:
class FlextDomainService:
```

### Sistema de Resultado

```python
# Core Result Pattern
class FlextResult[T]:
class FlextError:
class FlextValidationError(FlextError):

# Tipos relacionados
TFlextResult = FlextResult[T]
TFlextSuccess = T
TFlextFailure = FlextError
```

### HTTP Client e API

```python
# Client Components
class FlextApiClient:
class FlextApiConfig:
class FlextApiRequest:
class FlextApiResponse[T]:

# Plugin System
class FlextApiPlugin:
class FlextApiCachingPlugin(FlextApiPlugin):
class FlextApiRetryPlugin(FlextApiPlugin):

# Builder Pattern
class FlextApiBuilder:
class FlextApiQueryBuilder:
```

### Dependency Injection

```python
# Container System
class FlextContainer:
class FlextServiceProvider:
class FlextServiceDescriptor:

# Types
TFlextService = TypeVar("TFlextService")
TFlextProvider = Callable[[], T]
```

### Logging e Observabilidade

```python
# Logging Components
class FlextLogger:
class FlextLogContext:
class FlextLogFormatter:

# Metrics and Monitoring
class FlextMetrics:
class FlextHealthCheck:
class FlextObservabilityCollector:
```

### Configuração

```python
# Configuration Classes
class FlextSettings(BaseSettings):
class FlextDatabaseConfig(FlextSettings):
class FlextApiConfig(FlextSettings):

# Constants
FLEXT_DEFAULT_CONFIG_PATH = "config/flext.yaml"
FLEXT_ENV_PREFIX = "FLEXT_"
```

## Regras de Compatibilidade PEP

### PEP 8 - Convenções de Nomenclatura

- **Classes**: PascalCase (`FlextApiClient`)
- **Funções/Métodos**: snake_case (`flext_create_client`)
- **Variáveis**: snake_case (`flext_api_instance`)
- **Constantes**: SCREAMING_SNAKE_CASE (`FLEXT_VERSION`)
- **Módulos**: snake_case (`flext_api.py`)

### PEP 484/526 - Type Hints

```python
# ✅ Correto - Type hints modernos
def flext_process_data[T](data: T) -> FlextResult[T]:
    return FlextResult[None].ok(data)

# ✅ Correto - Generic classes
class FlextRepository[TEntity, TId]:
    def find_by_id(self, id: TId) -> FlextResult[TEntity | None]:
        ...

# ❌ Incorreto - Type hints antigos
def flext_process_data(data):  # Sem type hints
def flext_process_data(data: Any) -> Any:  # Muito genérico
```

### PEP 563 - Deferred Evaluation

```python
# ✅ Correto - Future annotations
from __future__ import annotations

class FlextUser:
    def get_manager(self) -> FlextUser | None:  # Self-reference OK
        ...
```

## Padrões de Migração Incremental

### Fase 1: Renomeação Segura

1. Identificar todos os símbolos não-conformes
2. Criar aliases temporários para backward compatibility
3. Atualizar imports progressivamente
4. Remover aliases após confirmação

### Fase 2: Refatoração de Tipos

1. Modernizar type hints para Python 3.13
2. Implementar generic types com nova sintaxe
3. Adicionar strict type checking
4. Validar com mypy strict mode

### Fase 3: Estrutura de Módulos

1. Reorganizar estrutura de diretórios se necessário
2. Padronizar imports públicos em `__init__.py`
3. Implementar lazy loading onde apropriado
4. Validar performance de imports

### Exemplo de Migração Segura

```python
# ANTES (não-conforme)
class flexResult:
    pass

def CreateFlexResult():
    pass

# DURANTE (com aliases)
from __future__ import annotations

class FlextResult[T]:  # ✅ Novo padrão
    pass

# Backward compatibility (temporário)
flexResult = FlextResult  # Alias deprecated

def flext_create_result[T]() -> FlextResult[T]:  # ✅ Novo padrão
    return FlextResult[None].ok()

# Alias deprecated
CreateFlexResult = flext_create_result

# DEPOIS (totalmente conforme)
class FlextResult[T]:
    pass

def flext_create_result[T]() -> FlextResult[T]:
    return FlextResult[None].ok()
```

## Quality Gates para Conformidade PEP

### Lint Rules (ruff)

```toml
[tool.ruff]
# Todas as regras PEP ativadas
extend = "../.ruff-shared.toml"
lint.isort.known-first-party = ["project_name"]
```

### MyPy Configuration

```toml
[tool.mypy]
strict = true
warn_unused_ignores = false
warn_return_any = true
warn_unreachable = true
```

### Testing Standards

- Testar todas as migrações incrementalmente
- Manter backward compatibility até versão major
- Validar performance após refatoração
- Executar quality gates após cada mudança

---

**Implementação**: Esta matriz será aplicada projeto por projeto, mantendo compatibilidade e testando incrementalmente cada mudança.
