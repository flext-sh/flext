# FLEXT - Unified Hexagonal Architecture + DDD Implementation

FLEXT é uma implementação moderna de um sistema de pipelines usando **Arquitetura Hexagonal** (Ports & Adapters) combinada com **Domain-Driven Design (DDD)**.

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
go test ./...
```

### Testes de Integração

```bash
go test ./tests/integration/...
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
