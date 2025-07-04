# Arquitetura de Refatoração - Singer SDK Modules

## Visão Geral

Esta arquitetura aplica princípios SOLID, KISS e DRY para criar módulos Singer SDK profissionais, manuteníveis e extensíveis.

## Princípios Aplicados

### 1. SOLID

#### Single Responsibility Principle (SRP)
- Cada classe tem uma única responsabilidade bem definida
- Separação clara entre: conexão, transformação, validação, persistência

#### Open/Closed Principle (OCP)
- Classes abertas para extensão via herança/composição
- Fechadas para modificação do comportamento core

#### Liskov Substitution Principle (LSP)
- Subclasses podem substituir classes base sem quebrar funcionalidade
- Interfaces consistentes em toda hierarquia

#### Interface Segregation Principle (ISP)
- Interfaces pequenas e focadas
- Clientes não dependem de métodos que não usam

#### Dependency Inversion Principle (DIP)
- Dependências via interfaces/abstrações
- Injeção de dependências para testabilidade

### 2. KISS (Keep It Simple, Stupid)
- Métodos pequenos (<20 linhas)
- Complexidade ciclomática <10
- Nomes auto-explicativos

### 3. DRY (Don't Repeat Yourself)
- Código reutilizável em módulos compartilhados
- Configurações centralizadas
- Padrões extraídos para funções

## Arquitetura do flext-target-oracle

### Estrutura de Módulos

```
flext-target-oracle/
├── flext_target_oracle/
│   ├── core/                    # Core business logic
│   │   ├── interfaces/          # Abstract interfaces
│   │   │   ├── __init__.py
│   │   │   ├── connection.py    # IConnectionManager
│   │   │   ├── type_mapper.py   # ITypeMapper
│   │   │   ├── batch_processor.py # IBatchProcessor
│   │   │   ├── validator.py     # IValidator
│   │   │   └── monitor.py       # IMonitor
│   │   │
│   │   ├── models/              # Data models
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Configuration models
│   │   │   ├── batch.py         # Batch processing models
│   │   │   ├── schema.py        # Schema models
│   │   │   └── metrics.py       # Metrics models
│   │   │
│   │   └── exceptions.py        # Custom exceptions
│   │
│   ├── infrastructure/          # Infrastructure implementations
│   │   ├── oracle/
│   │   │   ├── connection.py    # OracleConnectionManager
│   │   │   ├── type_mapper.py   # OracleTypeMapper
│   │   │   ├── optimizer.py     # OracleOptimizer
│   │   │   └── dialect.py       # Oracle-specific SQL
│   │   │
│   │   ├── monitoring/
│   │   │   ├── prometheus.py    # PrometheusMonitor
│   │   │   ├── logging.py       # StructuredLogger
│   │   │   └── null.py          # NullMonitor (no-op)
│   │   │
│   │   └── cache/
│   │       ├── memory.py        # In-memory cache
│   │       └── redis.py         # Redis cache (optional)
│   │
│   ├── application/             # Application services
│   │   ├── services/
│   │   │   ├── batch_service.py # Batch processing service
│   │   │   ├── schema_service.py # Schema management
│   │   │   └── sync_service.py  # Synchronization logic
│   │   │
│   │   └── validators/
│   │       ├── config.py        # Configuration validator
│   │       ├── data.py          # Data validator
│   │       └── schema.py        # Schema validator
│   │
│   ├── adapters/                # Singer SDK adapters
│   │   ├── target.py            # OracleTarget (Singer SDK)
│   │   ├── sink.py              # OracleSink (Singer SDK)
│   │   └── connector.py         # OracleConnector (Singer SDK)
│   │
│   ├── shared/                  # Shared utilities
│   │   ├── constants.py         # Constants
│   │   ├── utils.py             # Utility functions
│   │   └── decorators.py        # Common decorators
│   │
│   └── config.py               # Configuration schema
```

### Classes e Responsabilidades

#### Core Layer

**Interfaces** (Contratos puros):
```python
# IConnectionManager
class IConnectionManager(Protocol):
    def connect(self) -> Connection: ...
    def disconnect(self) -> None: ...
    def test_connection(self) -> bool: ...
    def get_connection_info(self) -> ConnectionInfo: ...

# ITypeMapper
class ITypeMapper(Protocol):
    def map_type(self, source_type: str, context: TypeContext) -> str: ...
    def get_supported_types(self) -> list[str]: ...

# IBatchProcessor
class IBatchProcessor(Protocol):
    def process_batch(self, batch: Batch) -> BatchResult: ...
    def validate_batch(self, batch: Batch) -> ValidationResult: ...
```

**Models** (Imutáveis com Pydantic):
```python
class OracleConfig(BaseModel):
    host: str
    port: int = 1521
    service_name: str
    user: str
    password: SecretStr
    schema: str | None = None
    
    class Config:
        frozen = True  # Imutável
```

#### Infrastructure Layer

**Implementações concretas**:
```python
class OracleConnectionManager(IConnectionManager):
    def __init__(self, config: OracleConfig, logger: ILogger):
        self._config = config
        self._logger = logger
        self._connection: Connection | None = None
        self._lock = threading.Lock()
    
    def connect(self) -> Connection:
        # Implementação específica Oracle
        # Usa oracledb com otimizações
```

**Type Mapping com Strategy Pattern**:
```python
class OracleTypeMapper(ITypeMapper):
    def __init__(self):
        self._strategies = {
            'string': StringTypeStrategy(),
            'integer': IntegerTypeStrategy(),
            'number': NumberTypeStrategy(),
            'boolean': BooleanTypeStrategy(),
            'object': ObjectTypeStrategy(),
            'array': ArrayTypeStrategy(),
        }
```

#### Application Layer

**Services com Single Responsibility**:
```python
class BatchService:
    def __init__(
        self,
        processor: IBatchProcessor,
        validator: IValidator,
        monitor: IMonitor,
    ):
        self._processor = processor
        self._validator = validator
        self._monitor = monitor
    
    async def process_batch_async(self, batch: Batch) -> BatchResult:
        # Valida, processa, monitora
        # Coordena mas não implementa lógica
```

#### Adapters Layer

**Singer SDK Integration**:
```python
class OracleTarget(Target):
    """Singer SDK Target adaptado."""
    
    def __init__(self, config: dict, **kwargs):
        # Inicializa serviços via DI container
        self._container = DIContainer()
        self._setup_services()
        super().__init__(config, **kwargs)
    
    def get_sink(self, stream_name: str) -> OracleSink:
        # Cria sink com serviços injetados
        return OracleSink(
            stream_name=stream_name,
            batch_service=self._container.resolve(BatchService),
            schema_service=self._container.resolve(SchemaService),
        )
```

### Patterns Implementados

1. **Repository Pattern**: Para acesso a dados
2. **Strategy Pattern**: Para type mapping
3. **Factory Pattern**: Para criação de objetos
4. **Observer Pattern**: Para monitoramento
5. **Decorator Pattern**: Para funcionalidades opcionais
6. **Dependency Injection**: Para inversão de controle

## Arquitetura do flext-tap-oracle-wms

### Estrutura de Módulos

```
flext-tap-oracle-wms/
├── src/tap_oracle_wms/
│   ├── core/
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   ├── api_client.py    # IApiClient
│   │   │   ├── authenticator.py # IAuthenticator
│   │   │   ├── paginator.py     # IPaginator
│   │   │   ├── transformer.py   # ITransformer
│   │   │   └── discovery.py     # IDiscovery
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── entity.py        # Entity models
│   │   │   ├── schema.py        # Schema models
│   │   │   ├── page.py          # Pagination models
│   │   │   └── config.py        # Configuration models
│   │   │
│   │   └── exceptions.py
│   │
│   ├── infrastructure/
│   │   ├── wms/
│   │   │   ├── client.py        # WMSApiClient
│   │   │   ├── auth.py          # WMS Authenticators
│   │   │   ├── paginator.py     # WMSPaginator
│   │   │   └── discovery.py     # WMSDiscovery
│   │   │
│   │   ├── http/
│   │   │   ├── client.py        # HTTP client wrapper
│   │   │   ├── retry.py         # Retry logic
│   │   │   └── cache.py         # Response cache
│   │   │
│   │   └── transformers/
│   │       ├── flatten.py       # Object flattener
│   │       ├── type_infer.py    # Type inference
│   │       └── normalize.py     # Data normalizer
│   │
│   ├── application/
│   │   ├── services/
│   │   │   ├── entity_service.py    # Entity management
│   │   │   ├── schema_service.py    # Schema generation
│   │   │   ├── extraction_service.py # Data extraction
│   │   │   └── sync_service.py      # Sync coordination
│   │   │
│   │   └── strategies/
│   │       ├── full_sync.py     # Full sync strategy
│   │       ├── incremental.py   # Incremental sync
│   │       └── hybrid.py        # Hybrid sync
│   │
│   ├── adapters/
│   │   ├── tap.py              # TapOracleWMS (Singer SDK)
│   │   ├── stream.py           # WMSStream (Singer SDK)
│   │   └── catalog.py          # Catalog builder
│   │
│   └── shared/
│       ├── constants.py
│       ├── utils.py
│       └── validators.py
```

### Design Patterns no Tap

1. **Adapter Pattern**: WMS API para Singer SDK
2. **Strategy Pattern**: Diferentes estratégias de sync
3. **Chain of Responsibility**: Pipeline de transformação
4. **Template Method**: Base stream com hooks
5. **Facade Pattern**: Simplifica API complexa

## Implementação dos Princípios

### Exemplo SOLID - Type Mapper

```python
# Interface Segregation
class ITypeMapper(Protocol):
    """Mapeia tipos entre sistemas."""
    def map_type(self, source_type: str, context: TypeContext) -> str: ...

class ITypeValidator(Protocol):
    """Valida compatibilidade de tipos."""
    def is_compatible(self, source: str, target: str) -> bool: ...

# Single Responsibility + Open/Closed
class OracleTypeMapper(ITypeMapper):
    """Mapeia tipos para Oracle."""
    
    def __init__(self, strategies: dict[str, ITypeStrategy]):
        self._strategies = strategies
    
    def map_type(self, source_type: str, context: TypeContext) -> str:
        strategy = self._strategies.get(source_type)
        if not strategy:
            raise UnsupportedTypeError(source_type)
        return strategy.map(context)

# Strategy Pattern para extensibilidade
class VarcharTypeStrategy(ITypeStrategy):
    def map(self, context: TypeContext) -> str:
        max_length = context.get_max_length()
        if max_length > 4000:
            return "CLOB"
        return f"VARCHAR2({max_length} CHAR)"
```

### Exemplo KISS - Batch Processing

```python
# Antes (complexo)
def process_batch(self, batch):
    # 200+ linhas de código
    # Múltiplas responsabilidades
    # Difícil de testar

# Depois (simples)
class BatchService:
    def process_batch(self, batch: Batch) -> BatchResult:
        # Validar
        validation = self._validator.validate(batch)
        if not validation.is_valid:
            return BatchResult.failure(validation.errors)
        
        # Transformar
        transformed = self._transformer.transform(batch)
        
        # Persistir
        result = self._persister.persist(transformed)
        
        # Monitorar
        self._monitor.record_batch(result)
        
        return result
```

### Exemplo DRY - Configuração

```python
# shared/config_base.py
class BaseConfig(BaseModel):
    """Configuração base compartilhada."""
    
    # Campos comuns
    debug: bool = False
    log_level: str = "INFO"
    retry_count: int = 3
    timeout: int = 120
    
    # Validações comuns
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if v not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v

# Oracle Target herda configuração base
class OracleConfig(BaseConfig):
    host: str
    port: int = 1521
    service_name: str
    
# WMS Tap herda configuração base
class WMSConfig(BaseConfig):
    base_url: HttpUrl
    api_version: str = "v10"
```

## Benefícios da Arquitetura

1. **Testabilidade**: Todas as classes podem ser testadas isoladamente
2. **Manutenibilidade**: Código organizado e de fácil compreensão
3. **Extensibilidade**: Novos tipos/features sem modificar código existente
4. **Reusabilidade**: Componentes podem ser reutilizados
5. **Performance**: Otimizações isoladas sem afetar lógica
6. **Monitoramento**: Métricas e logs estruturados built-in

## Próximos Passos

1. Implementar estrutura de diretórios
2. Criar interfaces e modelos
3. Migrar código existente gradualmente
4. Adicionar testes para cada componente
5. Documentar APIs públicas
6. Configurar CI/CD com quality gates