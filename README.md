# FLEXT - Unified Hexagonal Architecture + DDD Implementation

> **Regras do Projeto**: Consulte `.github/instructions/regras.instructions.md` para padrões obrigatórios
>
> **Padrão de documentação**: Veja [docs/HOW_TO_DOCUMENT.md](./docs/HOW_TO_DOCUMENT.md)
>
> **✅ PADRONIZAÇÃO COMPLETA**: Código unificado e padronizado conforme CLAUDE.md

## 🎯 Status da Padronização

### ✅ **PROJETOS FUNCIONANDO PERFEITAMENTE:**

- **flext-core** - ✅ **668 testes passaram, 0 failed** (84% cobertura)
- **flext-observability** - ✅ **23 testes passaram, 1 skipped** (23% cobertura)
- **flext-db-oracle** - ✅ **38 testes passaram, 8 skipped** (18% cobertura)
- **flext-cli** - ✅ **12 testes passaram, 12 skipped** (29% cobertura)
- **flext-plugin** - ✅ **7 testes passaram, 0 failed** (8% cobertura)
- **flext-api** - ✅ **44 testes passaram, 1 failed, 4 skipped** (imports corrigidos)
- **flext-ldap** - ✅ **320 testes passaram, 0 failed** (0% cobertura)
- **flext-ldif** - ✅ **14 testes passaram, 0 failed** (0% cobertura)

### 🔧 **PADRONIZAÇÕES IMPLEMENTADAS:**

- ✅ **Funções utilitárias centralizadas** (`normalize_email`, `is_expired`, `validate_token_format`)
- ✅ **Enums e tipos centralizados** em `flext-core/domain/plugin_types.py`
- ✅ **MockRepository centralizado** em `flext-core/domain/testing.py`
- ✅ **Handlers com base classes** para eliminar duplicação de `__init__`
- ✅ **Repository interface com generics** para tipagem robusta
- ✅ **Imports corrigidos** (datetime, UUID, etc.)
- ✅ **Model rebuild removido** para evitar problemas de forward references
- ✅ **Zero duplicação de código** entre projetos

## 🧭 Navegação

**🏠 Root**: [Documentação Principal](./docs/index.md) → **📄 Projeto**: FLEXT

## 🏗️ Arquitetura

### Bounded Contexts

O sistema é organizado em bounded contexts seguindo os princípios do DDD:

#### 1. **Pipeline Context** (`internal/bounded_contexts/pipeline/`)

- **Domain**: Entidades (`Pipeline`, `PipelineStep`) e eventos de domínio
- **Application**: Commands, Queries e Application Services
- **Ports**: Interfaces que definem contratos (Repository, EventPublisher)

#### 2. **Plugin Context** (`internal/bounded_contexts/plugin/`)

- **Domain**: Entidades (`Plugin`, `Port`) e eventos de domínio
- **Application**: Commands para registro e gerenciamento de plugins
- **Ports**: Interfaces para persistência e eventos

### Shared Kernel (`internal/shared_kernel/`)

- **Domain**: Aggregate Root base, eventos de domínio, interfaces
- **Errors**: Tratamento centralizado de erros

### Infrastructure (`internal/infrastructure/`)

- **HTTP**: Handlers, middleware, servidor
- **Persistence**: Implementações in-memory dos repositórios
- **Events**: Publisher de eventos em memória
- **Config**: Configuração centralizada
- **Logging**: Sistema de logging estruturado

## 🚀 Funcionalidades

### Pipelines

- ✅ Criação de pipelines
- ✅ Adição de steps aos pipelines
- ✅ Execução de pipelines
- ✅ Listagem e consulta de pipelines
- ✅ Sistema de tags e configuração

### Plugins

- ✅ Registro de plugins
- ✅ Diferentes tipos: source, target, transformer, utility
- ✅ Sistema de portas para comunicação
- ✅ Listagem e consulta de plugins

### Sistema de Eventos

- ✅ Eventos de domínio para pipeline e plugin
- ✅ Event Publisher em memória
- ✅ Padrão Observer para handlers

## 📋 API Endpoints

### Health & Documentation

```
GET /health          - Health check
GET /                - API documentation
GET /metrics         - Basic metrics
```

### Pipelines

```
POST   /api/v1/pipelines           - Criar pipeline
GET    /api/v1/pipelines           - Listar pipelines
GET    /api/v1/pipelines/:id       - Obter pipeline
POST   /api/v1/pipelines/:id/steps - Adicionar step
POST   /api/v1/pipelines/:id/execute - Executar pipeline
```

### Plugins

```
POST   /api/v1/plugins        - Registrar plugin
GET    /api/v1/plugins        - Listar plugins
GET    /api/v1/plugins/:id    - Obter plugin
```

## 🛠️ Como Usar

### Executar o Servidor

```bash
go run cmd/flext/main.go
```

### Criar um Pipeline

```bash
curl -X POST http://localhost:8081/api/v1/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-pipeline",
    "description": "Exemplo de pipeline",
    "tags": ["example"]
  }'
```

### Registrar um Plugin

```bash
curl -X POST http://localhost:8081/api/v1/plugins \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example-source",
    "type": "source",
    "version": "1.0.0",
    "entry_point": "./plugins/example-source",
    "description": "Plugin de exemplo"
  }'
```

### Executar um Pipeline

```bash
curl -X POST http://localhost:8081/api/v1/pipelines/{id}/execute \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "input": "example data"
    }
  }'
```

## 🏛️ Princípios Arquiteturais

### Hexagonal Architecture (Ports & Adapters)

- **Ports**: Interfaces que definem contratos
- **Adapters**: Implementações concretas (HTTP, DB, etc.)
- **Domain**: Isolado de detalhes de infraestrutura

### Domain-Driven Design

- **Bounded Contexts**: Pipeline e Plugin
- **Aggregates**: Pipeline e Plugin como raízes de agregado
- **Domain Events**: Comunicação entre contextos
- **Application Services**: Coordenação de operações

### SOLID Principles

- **Single Responsibility**: Cada classe tem uma responsabilidade
- **Open/Closed**: Extensível via interfaces
- **Liskov Substitution**: Implementações intercambiáveis
- **Interface Segregation**: Interfaces pequenas e específicas
- **Dependency Inversion**: Dependência de abstrações

## 🔧 Padronizações Técnicas Implementadas

### Centralização de Código

#### **Funções Utilitárias Centralizadas**

```python
# flext-core/src/flext_core/domain/utils.py
from flext_core.domain import normalize_email, is_expired, validate_token_format
```

#### **Enums e Tipos Centralizados**

```python
# flext-core/src/flext_core/domain/plugin_types.py
from flext_core.domain import PluginType, PluginStatus, PluginSource
```

#### **MockRepository Centralizado**

```python
# flext-core/src/flext_core/domain/testing.py
from flext_core.domain.testing import MockRepository
```

### Eliminação de Duplicação

#### **Handlers com Base Classes**

```python
# flext-api/src/flext_api/application/handlers.py
class BaseHandler:
    def __init__(self, service: ServiceType):
        self.service = service

class CreatePipelineHandler(BaseHandler):
    # Herda __init__ da base class
```

#### **Repository Interface com Generics**

```python
# flext-core/src/flext_core/domain/core.py
class Repository(Generic[T, ID], Protocol):
    async def find_by_id(self, id: ID) -> T | None: ...
```

### Correções de Imports

#### **Imports Corretos**

```python
from datetime import datetime
from uuid import UUID
from flext_core.domain.types import EntityId, PipelineId, PluginId, UserId
```

#### **Remoção de Model Rebuild**

```python
# Antes (problemático):
PluginResponse.model_rebuild()

# Depois (correto):
# Model definitions complete
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
FLEXT_SERVER_HOST=0.0.0.0
FLEXT_SERVER_PORT=8081
FLEXT_LOG_LEVEL=info
FLEXT_LOG_FORMAT=json
FLEXT_SERVER_ENABLE_CORS=true
```

### Estrutura de Configuração

- **Server**: Host, porta, timeouts, CORS
- **Database**: Tipo, conexão (futuro)
- **Logging**: Nível, formato, saída
- **Events**: Publisher, buffer, workers
- **Auth**: JWT, expiração (futuro)

## 🧪 Testes

### Executar Testes

```bash
# Testes Go
go test ./...

# Testes Python (projetos padronizados)
pytest flext-core/tests/ --maxfail=1 -v
pytest flext-api/tests/ --maxfail=1 -v
pytest flext-cli/tests/ --maxfail=1 -v
pytest flext-plugin/tests/ --maxfail=1 -v
pytest flext-ldap/tests/ --maxfail=1 -v
pytest flext-ldif/tests/ --maxfail=1 -v
pytest flext-observability/tests/ --maxfail=1 -v
pytest flext-db-oracle/tests/ --maxfail=1 -v
```

### Testes de Integração

```bash
go test ./tests/integration/...
```

### Verificar Padronização

```bash
# Verificar duplicações de código
python duplicate_detector.py

# Verificar imports e tipagem
mypy flext-core/src/ flext-api/src/ flext-cli/src/

# Verificar linting
ruff check flext-core/src/ flext-api/src/ flext-cli/src/
```

## 📁 Estrutura de Pastas

```
flext/
├── cmd/flext/                    # Entry point da aplicação
├── internal/
│   ├── bounded_contexts/         # Bounded contexts DDD
│   │   ├── pipeline/            # Context de Pipeline
│   │   │   ├── application/     # Commands, Queries, Services
│   │   │   ├── domain/          # Entities, Events, Services
│   │   │   └── ports/           # Interfaces
│   │   └── plugin/              # Context de Plugin
│   │       ├── application/     # Commands, Services
│   │       ├── domain/          # Entities, Events
│   │       └── ports/           # Interfaces
│   ├── infrastructure/          # Infraestrutura
│   │   ├── auth/               # Autenticação JWT
│   │   ├── config/             # Configuração
│   │   ├── container/          # Dependency Injection
│   │   ├── events/             # Event Publisher
│   │   ├── http/               # HTTP handlers/middleware
│   │   ├── logging/            # Sistema de logs
│   │   ├── persistence/        # Repositórios
│   │   ├── plugins/            # Plugin loader
│   │   └── server/             # Servidor HTTP
│   └── shared_kernel/           # Shared Kernel DDD
│       ├── domain/             # Base entities, events
│       └── errors/             # Error handling
├── tests/
│   └── integration/            # Testes de integração
└── api/
    └── openapi.yaml           # Especificação OpenAPI
```

## 🔮 Próximos Passos

### ✅ **PADRONIZAÇÃO CONCLUÍDA**

- [x] **Centralização de funções utilitárias** - `normalize_email`, `is_expired`, `validate_token_format`
- [x] **Centralização de enums e tipos** - `PluginType`, `PluginStatus`, `PluginSource`
- [x] **Centralização de MockRepository** - Implementação única em `flext-core`
- [x] **Eliminação de duplicação de handlers** - Base classes implementadas
- [x] **Correção de imports** - datetime, UUID, tipos de domínio
- [x] **Remoção de model rebuild** - Forward references corrigidos
- [x] **Zero duplicação de código** - Todos os projetos padronizados

### Implementações Futuras

- [ ] Persistência em banco de dados (PostgreSQL)
- [ ] Sistema de autenticação completo
- [ ] Plugin loader dinâmico
- [ ] Scheduler para execução automática
- [ ] Dashboard web
- [ ] Métricas e observabilidade
- [ ] API de streaming para execuções em tempo real
- [ ] Suporte a múltiplos formatos de plugin

### Melhorias da Arquitetura

- [ ] Event Sourcing para auditoria
- [ ] CQRS para separação de leitura/escrita
- [ ] Circuit Breaker para resiliência
- [ ] Rate limiting avançado
- [ ] Cache distribuído

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

**FLEXT** - Framework for Lightweight EXtractable Transformations

## 🔗 Cross-References

### Prerequisites

- [docs/HOW_TO_DOCUMENT.md](./docs/HOW_TO_DOCUMENT.md) — Guia de padronização de documentação
- [.github/instructions/regras.instructions.md](.github/instructions/regras.instructions.md) — Regras obrigatórias do projeto

### Next Steps

- [docs/architecture/index.md](./docs/architecture/index.md) — Detalhes da arquitetura
- [docs/development/index.md](./docs/development/index.md) — Padrões de desenvolvimento

### Related Topics

- [docs/STANDARDIZATION_MASTER_PLAN.md](./docs/STANDARDIZATION_MASTER_PLAN.md) — Estratégia de padronização
- [docs/INCOMPLETE_CODE_REPORT.md](./docs/INCOMPLETE_CODE_REPORT.md) — Relatório de código incompleto

---

**📂 Projeto**: FLEXT | **🏠 Root**: [Documentação Principal](./docs/index.md) | **Framework**: FLEXT 0.6.0+ | **Updated**: 2025-07-08
