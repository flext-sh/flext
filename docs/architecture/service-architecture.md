# FLEXT - Enterprise Data Integration Service Architecture

**Document Status**: SOURCE OF TRUTH  
**Version**: 0.9.0
**Last Updated**: 2025-08-01

---

## 🚨 FUNDAMENTAL ARCHITECTURAL CONCEPT

### WHAT IS FLEXT

**FLEXT is a SINGLE SERVICE** that runs in the `flext` namespace in the workspace, implementing **Clean Architecture + Domain Driven Design (DDD)** with complete orchestration via **Plugin System + Dependency Injection**.

**CRITICAL CONCEPT**: The projects `flext-core`, `flext-api`, `flext-auth`, `flext-cli`, `flext-grpc`, `flext-plugin`, `flext-web` **ARE SIMPLY LIBRARIES** that provide specific functionalities for the main service.

**REAL IMPLEMENTATION**: The main service is implemented in Go at `/home/marlonsc/flext/cmd/flext/main.go` with complete architecture of bounded contexts and DI container.

---

## 🏛️ FLEXT SERVICE ARCHITECTURE

### Real Structure of the Main Service

```
/home/marlonsc/flext/
├── cmd/flext/                      # 🚀 MAIN SERVICE (Go)
│   └── main.go                     # Entry point: Bootstrap + Container + Server
├── internal/                       # 🔧 INTERNAL IMPLEMENTATION (Clean Architecture)
│   └── bounded_contexts/           # 🎯 BOUNDED CONTEXTS (DDD)
│       └── singer/                # Singer Protocol Context (current implementation)
├── flext-*/                        # 📚 PYTHON LIBRARIES (Imported via gRPC/HTTP)
│   ├── flext-core/                # Shared Types & Base Classes
│   ├── flext-api/                 # FastAPI REST Endpoints
│   ├── flext-auth/                # Authentication Services
│   ├── flext-cli/                 # CLI Commands
│   ├── flext-grpc/                # gRPC Services
│   ├── flext-plugin/              # Plugin Framework
│   └── flext-web/                 # Django Web Interface
└── plugins/                        # 🔌 EXTERNAL PLUGINS
    ├── extractors/                 # Data Extraction Plugins
    ├── loaders/                   # Data Loading Plugins
    ├── transforms/                # Data Transformation Plugins
    └── utilities/                 # Utility Plugins
```

---

## 🔧 REAL DEPENDENCY INJECTION + BOUNDED CONTEXTS SYSTEM

### REAL Architecture: FLEXCORE Container + FLEXT Service + Libraries

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           RUNTIME EXECUTION ENVIRONMENT                        │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                        FLEXCORE CONTAINER                                 │  │
│  │     🏗️ DISTRIBUTED EVENT-DRIVEN RUNTIME (Go)                             │  │
│  │  ┌─────────────┬─────────────┬─────────────────┬─────────────────────┐  │  │
│  │  │Event Sourcing│ CQRS Pattern │ Plugin System  │ Distributed Cluster │  │  │
│  │  │     +       │      +       │       +        │         +           │  │  │
│  │  │ Audit Trail │ Read/Write   │HashiCorp-style │  Redis/etcd Coord   │  │  │
│  │  └─────────────┴─────────────┴─────────────────┴─────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                   ⬇️ EXECUTES ⬇️                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                          FLEXT SERVICE (Go)                               │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                   DI CONTAINER (container.go)                       │  │  │
│  │  │  ┌────────────┬────────────┬─────────────┬─────────────────────┐  │  │  │
│  │  │  │ Pipeline   │  Plugin    │  Meltano    │   Infrastructure    │  │  │  │
│  │  │  │ Services   │  Services  │  Services   │     Services        │  │  │  │
│  │  │  └────────────┴────────────┴─────────────┴─────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                   BOUNDED CONTEXTS (DDD)                            │  │  │
│  │  │  ┌──────────┬──────────┬──────────┬──────────────────────────────┐  │  │  │
│  │  │  │Pipeline  │ Plugin   │ Meltano  │ Singer │ WMS │ DBT │ Workflow│  │  │  │
│  │  │  │Context   │ Context  │ Context  │Context │ Ctx │ Ctx │ Context │  │  │  │
│  │  │  └──────────┴──────────┴──────────┴──────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                   ⬇️ INTEGRATES ⬇️                               │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │              PYTHON LIBRARIES (External Integration)                     │  │
│  │  ┌─────────────┬──────────────┬───────────────────────────────────────┐  │  │
│  │  │ flext-api   │  flext-auth  │    flext-grpc/web/cli/plugin         │  │  │
│  │  │(FastAPI REST│  (JWT Auth)  │   (gRPC/Django/CLI/Framework)        │  │  │
│  │  │  Endpoints) │   Service    │        Services                      │  │  │
│  │  └─────────────┴──────────────┴───────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         flext-core (Python)                              │  │
│  │                    Base Types + Domain Models                            │  │
│  │      (Shared via HTTP/gRPC/subprocess between Go & Python)               │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Como Funciona a Orquestração REAL

#### 1. **Inicialização do Serviço** (Implementação Real)

```go
// cmd/flext/main.go - CÓDIGO REAL DO SERVIÇO
func main() {
    // 1. Parse command line flags
    var (
        configPath = flag.String("config", "", "Path to configuration file")
        debug      = flag.Bool("debug", false, "Enable debug logging")
    )
    flag.Parse()

    // 2. Create application bootstrap
    bootstrap := application.NewAppBootstrap(application.AppTypeStandalone, "flext", "2.0.0")
    if *configPath != "" {
        bootstrap = bootstrap.WithConfigPath(*configPath)
    }
    if *debug {
        bootstrap = bootstrap.WithLogLevel("debug")
    }

    // 3. Initialize application configuration
    appConfig, err := bootstrap.Initialize()
    if err != nil {
        fmt.Printf("Failed to initialize application: %v\n", err)
        os.Exit(1)
    }

    // 4. Create DI Container for comprehensive functionality
    appContainer, err := container.NewContainer(appConfig.Config)
    if err != nil {
        appConfig.Logger.Error("Failed to initialize container", logging.F("error", err.Error()))
        os.Exit(1)
    }

    // 5. Create and configure HTTP server
    srv := server.NewServer(appConfig.Config, appConfig.Logger)
    srv.SetupBasicRoutes()

    // 6. Register all domain handlers from DI container
    registerHandlers(srv, appContainer, appConfig.Logger)

    // 7. Register Clean Architecture handlers if enabled
    if appConfig.Config.CleanArchitecture.IsEnabled() {
        registerCleanArchitectureHandlers(srv, appConfig, appContainer)
    }

    // 8. Setup graceful shutdown
    shutdown := application.NewGracefulShutdownHandler(appConfig.Logger, appConfig.Config.Server.ShutdownTimeout)
    shutdown.AddShutdownFunc("server", srv.Stop)
    shutdown.AddShutdownFunc("container", func(ctx context.Context) error {
        return appContainer.Shutdown()
    })

    // 9. Start server
    go func() {
        appConfig.Logger.Info("Starting server", logging.F("address", appConfig.Config.Address()))
        if err := srv.Start(); err != nil {
            appConfig.Logger.Error("Server failed to start", logging.F("error", err.Error()))
            os.Exit(1)
        }
    }()

    // 10. Wait for shutdown signal
    shutdown.WaitForShutdown()
}
```

#### 2. **DI Container Real** (Implementação Real)

```go
// internal/infrastructure/container/container.go - CÓDIGO REAL
func NewContainer(cfg *config.Config) (*Container, error) {
    c := &Container{
        config: cfg,
    }

    if err := c.initializeServices(); err != nil {
        return nil, errors.Wrap(err, "initializing container services")
    }
    return c, nil
}

func (c *Container) initializeServices() error {
    // 1. Infrastructure Layer
    c.logger = logging.GetLogger()
    c.eventPublisher = events.NewInMemoryEventPublisher()

    // 2. Database connection (PostgreSQL ou Memory)
    if err := c.initializeDatabase(); err != nil {
        return errors.Wrap(err, "initializing database connection in container")
    }

    // 3. Repository Layer (Domain Persistence)
    if err := c.initializeRepositories(); err != nil {
        return errors.Wrap(err, "initializing repository layer")
    }

    // 4. Domain Services - Plugin Executor with Production Environment
    executorFactory := plugin_execution.NewExecutorFactory()

    productionExecutor, err := executorFactory.CreateProductionExecutor(
        c.pluginRepo.(pipelineServices.PluginRepository),
    )

    if err != nil {
        // Fallback to development mode
        c.pipelineExecutor = executorFactory.CreatePipelineExecutor(
            c.pluginRepo.(pipelineServices.PluginRepository),
        )
    } else {
        c.pipelineExecutor = productionExecutor
        c.logger.Info("✅ Production pipeline executor created")
    }

    // 5. Application Services (Use Cases)
    c.executionStatsService = pipelineAppServices.NewPipelineExecutionStatsService(
        c.executionRepo, c.pipelineRepo,
    )

    eventAdapter := NewEventPublisherAdapter(c.eventPublisher)

    c.pipelineService = pipelineApp.NewPipelineService(
        c.pipelineRepo, c.pipelineExecutor, c.executionStatsService,
    )

    c.pluginService = pluginApp.NewPluginService(
        c.pluginRepo, eventAdapter,
    )

    // 6. External Service Integrations (Python Libraries via HTTP/subprocess)
    pythonPath := c.config.GetEnvWithDefault("PYTHON_PATH", "/home/marlonsc/flext/.venv/bin/python3")

    // Meltano Service Integration
    meltanoSvc, err := meltanoServices.NewMeltanoServiceWithConfig(c.logger)
    if err != nil {
        projectRoot := c.config.GetEnvWithDefault("PROJECT_ROOT", ".")
        c.meltanoService = meltanoServices.NewMeltanoService(pythonPath, projectRoot)
    } else {
        c.meltanoService = meltanoSvc
    }

    // DBT Manager Integration
    dbtConfig := &dbt.DBTConfig{
        ProjectPath: c.config.GetEnvWithDefault("DBT_PROJECT_PATH", "./dbt_project"),
        PythonPath:  pythonPath,
        VenvPath:    c.config.GetEnvWithDefault("VENV_PATH", "/home/marlonsc/flext/.venv"),
    }
    c.dbtManager, _ = dbt.NewDBTManager(dbtConfig, c.logger)

    // 7. HTTP Handlers (Presentation Layer)
    c.pipelineHandler = http.NewPipelineHandler(c.pipelineService, c.logger)
    c.pluginHandler = http.NewPluginHandler(c.pluginService, c.logger)
    c.meltanoHandler = http.NewMeltanoHandler(c.meltanoService)
    c.connectorsHandler = http.NewConnectorsHandler(c.logger)
    c.webHandler = http.NewSimpleBootstrapHandler(c.logger)

    return nil
}
```

#### 3. **Como Bibliotecas Python são Integradas** (Implementação Real)

O serviço Go **NÃO carrega bibliotecas Python como plugins dinâmicos**. Em vez disso, ele as executa como **processos externos** ou **serviços HTTP independentes** via subprocess calls.

```go
// internal/bounded_contexts/meltano/application/services/meltano_service.go - REAL
type MeltanoService struct {
    logger       logging.Logger
    pythonPath   string
    projectRoot  string
    workingDir   string
}

func (s *MeltanoService) ExecutePipeline(ctx context.Context, request ExecutePipelineRequest) (*ExecutionResult, error) {
    // 1. Prepare Meltano command - Executes Python library as subprocess
    cmd := exec.CommandContext(ctx, s.pythonPath, "-m", "meltano",
        "run", request.ExtractorName, request.LoaderName)
    cmd.Dir = s.workingDir

    // 2. Set environment variables for Python libraries
    cmd.Env = append(os.Environ(),
        fmt.Sprintf("MELTANO_PROJECT_ROOT=%s", s.projectRoot),
        "PYTHONPATH=/home/marlonsc/flext/flext-core/src:/home/marlonsc/flext/flext-meltano/src",
    )

    // 3. Execute Python subprocess
    output, err := cmd.CombinedOutput()
    if err != nil {
        s.logger.Error("Meltano execution failed",
            logging.F("error", err.Error()),
            logging.F("output", string(output)))
        return nil, fmt.Errorf("meltano execution failed: %w", err)
    }

    // 4. Parse Python library output and return to Go service
    result := &ExecutionResult{
        Status: "completed",
        Output: string(output),
        Duration: time.Since(startTime),
    }

    return result, nil
}
```

```go
// internal/infrastructure/http/pipeline_handler.go - REAL HTTP HANDLER
func (h *PipelineHandler) ExecutePipeline(c *gin.Context) {
    var request ExecutePipelineRequest
    if err := c.ShouldBindJSON(&request); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    // Use Pipeline Service from DI Container
    result, err := h.pipelineService.Execute(c.Request.Context(), pipelineApp.ExecuteCommand{
        Name:      request.Name,
        Extractor: request.Extractor,
        Loader:    request.Loader,
        Config:    request.Config,
    })

    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }

    c.JSON(200, result)
}
```

#### 4. **FLEXCORE como Container de Execução** (Implementação Real)

**CONCEITO CRÍTICO**: FLEXCORE fornece o **runtime environment** distribuído e orientado a eventos onde o serviço FLEXT executa.

```go
// flexcore/internal/application/services/workflow_service.go - FLEXCORE RUNTIME
type WorkflowService struct {
    eventBus     messaging.EventBus        // Event Sourcing + CQRS
    pluginLoader plugins.PluginLoader      // HashiCorp-style plugins
    cluster      cluster.CoordinationLayer  // Distributed coordination
    repository   repositories.EventStore   // Event Store for audit trail
}

// FLEXCORE executes FLEXT service workflows
func (ws *WorkflowService) ExecuteFlextPipeline(ctx context.Context, pipelineID string) error {
    // 1. Event Sourcing - Record pipeline execution event
    event := domain.NewPipelineExecutionStartedEvent(pipelineID, time.Now())
    if err := ws.eventBus.Publish(ctx, event); err != nil {
        return fmt.Errorf("failed to publish pipeline event: %w", err)
    }

    // 2. CQRS - Separate command processing
    command := commands.NewExecutePipelineCommand(pipelineID)
    if err := ws.commandBus.Send(ctx, command); err != nil {
        return fmt.Errorf("failed to execute pipeline command: %w", err)
    }

    // 3. Plugin System - Load and execute FLEXT plugins dynamically
    flextPlugin, err := ws.pluginLoader.LoadPlugin("flext-service")
    if err != nil {
        return fmt.Errorf("failed to load FLEXT service plugin: %w", err)
    }

    // 4. Distributed Cluster - Coordinate across nodes
    if err := ws.cluster.CoordinateExecution(ctx, pipelineID); err != nil {
        return fmt.Errorf("failed to coordinate distributed execution: %w", err)
    }

    // 5. Execute FLEXT service within FLEXCORE container
    result, err := flextPlugin.Execute(ctx, map[string]interface{}{
        "pipeline_id": pipelineID,
        "environment": "production",
        "cluster_node": ws.cluster.GetNodeID(),
    })

    // 6. Store execution result in event store
    completionEvent := domain.NewPipelineExecutionCompletedEvent(pipelineID, result)
    return ws.eventBus.Publish(ctx, completionEvent)
}
```

```go
// flexcore/cmd/server/main.go - FLEXCORE CONTAINER STARTUP
func main() {
    // 1. Initialize FLEXCORE distributed runtime
    flexcoreContainer := flexcore.NewContainer()

    // 2. Setup event sourcing + CQRS
    eventStore := flexcoreContainer.GetEventStore()
    commandBus := flexcoreContainer.GetCommandBus()
    queryBus := flexcoreContainer.GetQueryBus()

    // 3. Setup plugin system for FLEXT service
    pluginLoader := plugins.NewHashicorpStyleLoader()

    // 4. Register FLEXT service as a plugin in FLEXCORE
    flextPlugin := &FlextServicePlugin{
        servicePath: "/home/marlonsc/flext/cmd/flext/main.go",
        configPath:  "/home/marlonsc/flext/config.yaml",
    }
    pluginLoader.RegisterPlugin("flext-service", flextPlugin)

    // 5. Setup distributed cluster coordination
    cluster := cluster.NewRedisCoordinator(redisConfig)

    // 6. Initialize workflow engine with FLEXT service
    workflowService := services.NewWorkflowService(
        eventBus, pluginLoader, cluster, eventStore,
    )

    // 7. Start FLEXCORE container (which executes FLEXT service)
    server := server.NewFlexcoreServer(workflowService)
    log.Info("Starting FLEXCORE container with FLEXT service...")
    if err := server.Start(":8080"); err != nil {
        log.Fatal("FLEXCORE container failed to start:", err)
    }
}
```

#### 5. **Plugin de Extração Dinâmico**

```python
# plugins/extractors/tap-oracle.py
from flext_core import FlextResult, JsonDict
from flext_plugin.interfaces import ExtractorInterface
import cx_Oracle

class OracleExtractorPlugin(ExtractorInterface):
    """Plugin para extração de dados do Oracle."""

    def name(self) -> str:
        return "tap-oracle"

    def type(self) -> str:
        return "extractor"

    def version(self) -> str:
        return "1.0.0"

    def extract(self, config: JsonDict) -> FlextResult[JsonDict]:
        """Extrair dados do Oracle Database."""
        try:
            # Conectar ao Oracle
            connection = cx_Oracle.connect(
                user=config["username"],
                password=config["password"],
                dsn=config["dsn"]
            )

            # Executar queries
            cursor = connection.cursor()
            cursor.execute(config["query"])

            # Converter resultados
            columns = [desc[0] for desc in cursor.description]
            data = []

            for row in cursor.fetchall():
                data.append(dict(zip(columns, row)))

            cursor.close()
            connection.close()

            return FlextResult.ok({
                "records": data,
                "count": len(data),
                "source": "oracle"
            })

        except Exception as e:
            return FlextResult.fail(f"Oracle extraction failed: {e}")

# Export plugin factory
def create_plugin():
    return OracleExtractorPlugin()
```

---

## 🌊 FLUXO DE OPERAÇÃO DO SERVIÇO

### Cenário: Executar Pipeline de Dados

#### 1. **Requisição HTTP**

```bash
curl -X POST http://localhost:8080/api/v1/pipelines/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "oracle-to-postgres",
    "extractor": "tap-oracle",
    "loader": "target-postgres",
    "config": {
      "source": {
        "host": "oracle.company.com",
        "username": "user",
        "password": "pass",
        "query": "SELECT * FROM customers"
      },
      "target": {
        "host": "postgres.company.com",
        "database": "warehouse",
        "table": "customers"
      }
    }
  }'
```

#### 2. **Fluxo Interno do Serviço**

```go
// internal/infrastructure/http/pipeline_handler.go
func (h *PipelineHandler) ExecutePipeline(w http.ResponseWriter, r *http.Request) {
    // 1. Autenticação via flext-auth plugin
    authService := h.container.Resolve("auth.service").(auth.Service)
    user, err := authService.ValidateToken(r.Header.Get("Authorization"))
    if err != nil {
        http.Error(w, "Unauthorized", 401)
        return
    }

    // 2. Parse request
    var request PipelineExecuteRequest
    if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
        http.Error(w, "Invalid request", 400)
        return
    }

    // 3. Executar pipeline via Plugin Orchestrator
    orchestrator := h.container.Resolve("pipeline.orchestrator").(pipeline.Orchestrator)
    result, err := orchestrator.Execute(r.Context(), pipeline.ExecuteCommand{
        Name:      request.Name,
        Extractor: request.Extractor,
        Loader:    request.Loader,
        Config:    request.Config,
        User:      user,
    })

    // 4. Return response
    if err != nil {
        http.Error(w, err.Error(), 500)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(result)
}
```

#### 3. **Plugin Orchestrator**

```go
// internal/bounded_contexts/pipeline/orchestrator.go
func (o *Orchestrator) Execute(ctx context.Context, cmd ExecuteCommand) (*ExecuteResult, error) {
    // 1. Resolver extractor plugin
    extractor, err := o.pluginManager.GetExtractor(cmd.Extractor)
    if err != nil {
        return nil, fmt.Errorf("extractor not found: %w", err)
    }

    // 2. Resolver loader plugin
    loader, err := o.pluginManager.GetLoader(cmd.Loader)
    if err != nil {
        return nil, fmt.Errorf("loader not found: %w", err)
    }

    // 3. Executar extração
    extractResult, err := extractor.Extract(cmd.Config.Source)
    if err != nil {
        return nil, fmt.Errorf("extraction failed: %w", err)
    }

    // 4. Executar carregamento
    loadResult, err := loader.Load(extractResult.Data, cmd.Config.Target)
    if err != nil {
        return nil, fmt.Errorf("loading failed: %w", err)
    }

    // 5. Salvar pipeline execution
    execution := &domain.PipelineExecution{
        ID:           uuid.New(),
        PipelineName: cmd.Name,
        Status:       "completed",
        ExtractedRows: extractResult.Count,
        LoadedRows:    loadResult.Count,
        StartTime:     time.Now(),
        EndTime:       time.Now(),
        User:          cmd.User,
    }

    repo := o.container.Resolve("pipeline.repository").(domain.PipelineRepository)
    if err := repo.SaveExecution(ctx, execution); err != nil {
        return nil, fmt.Errorf("failed to save execution: %w", err)
    }

    return &ExecuteResult{
        ExecutionID:   execution.ID,
        Status:        "completed",
        ExtractedRows: extractResult.Count,
        LoadedRows:    loadResult.Count,
        Duration:      execution.EndTime.Sub(execution.StartTime),
    }, nil
}
```

---

## 🔧 CONFIGURAÇÃO DE DEPLOYMENT

### Docker Compose do Serviço

```yaml
# docker-compose.yml
version: "3.8"

services:
  flext-service:
    build: .
    ports:
      - "8080:8080" # HTTP API
      - "50051:50051" # gRPC
      - "3000:3000" # Web Interface
    environment:
      - FLEXT_ENV=production
      - FLEXT_PLUGIN_DIR=/app/plugins
      - FLEXT_CONFIG_FILE=/app/config.yaml
      - JWT_SECRET=${JWT_SECRET}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./plugins:/app/plugins:ro
      - ./config.yaml:/app/config.yaml:ro
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: flext
      POSTGRES_USER: flext
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Dockerfile do Serviço

```dockerfile
# Dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=1 GOOS=linux go build -o flext-service cmd/flext/main.go

FROM python:3.13-slim

# Install Go runtime for plugin loading
RUN apt-get update && apt-get install -y \
    golang \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Go service binary
COPY --from=builder /app/flext-service .

# Install Python libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Python plugin libraries
COPY flext-*/src/ ./libraries/
COPY plugins/ ./plugins/

# Set up Python path
ENV PYTHONPATH=/app/libraries

EXPOSE 8080 50051 3000

CMD ["./flext-service"]
```

---

## 📊 MONITORAMENTO E OBSERVABILIDADE

### Como o Serviço Expõe Métricas

```go
// internal/infrastructure/monitoring/metrics.go
func (m *MetricsCollector) ExposeMetrics() {
    // Plugin execution metrics
    prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "flext_plugin_executions_total",
            Help: "Total plugin executions",
        },
        []string{"plugin_name", "plugin_type", "status"},
    )

    // Pipeline execution metrics
    prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "flext_pipeline_duration_seconds",
            Help: "Pipeline execution duration",
        },
        []string{"pipeline_name", "extractor", "loader"},
    )

    // Library usage metrics
    prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "flext_library_memory_usage_bytes",
            Help: "Memory usage by library",
        },
        []string{"library_name"},
    )
}
```

### Health Check Endpoint

```go
// internal/infrastructure/http/health_handler.go
func (h *HealthHandler) CheckHealth(w http.ResponseWriter, r *http.Request) {
    health := &HealthStatus{
        Service: "flext",
        Status:  "healthy",
        Version: "2.0.0",
        Libraries: map[string]string{
            "flext-core": "2.0.0",
            "flext-api":  "2.0.0",
            "flext-auth": "2.0.0",
            "flext-grpc": "2.0.0",
            "flext-web":  "2.0.0",
        },
        Plugins: h.pluginManager.GetLoadedPlugins(),
        Database: h.checkDatabase(),
        Redis:    h.checkRedis(),
    }

    json.NewEncoder(w).Encode(health)
}
```

---

## ✅ BENEFÍCIOS DESTA ARQUITETURA

### 1. **Simplicidade Operacional**

- ✅ **UM ÚNICO SERVIÇO** para deploy, não 7+ microserviços
- ✅ **UM ÚNICO PONTO** de configuração e monitoramento
- ✅ **UM ÚNICO LOG STREAM** para debugging
- ✅ **UM ÚNICO HEALTH CHECK** para verificar status

### 2. **Flexibilidade Máxima**

- ✅ **Plugins dinâmicos** podem ser adicionados/removidos sem restart
- ✅ **Bibliotecas modulares** podem ser habilitadas/desabilitadas via config
- ✅ **Hot reload** de plugins para development
- ✅ **Versionamento independente** de cada biblioteca

### 3. **Performance Superior**

- ✅ **Zero network overhead** entre bibliotecas (in-process)
- ✅ **Shared memory** entre componentes
- ✅ **Connection pooling** centralizado
- ✅ **Cache compartilhado** entre todas as funcionalidades

### 4. **Desenvolvimento Facilitado**

- ✅ **Dependency Injection** elimina coupling
- ✅ **Clean Architecture** mantém boundaries claros
- ✅ **Plugin interfaces** padronizam extensões
- ✅ **Bibliotecas testáveis** independentemente

---

## 🚀 COMANDOS DE OPERAÇÃO

### Iniciar o Serviço

```bash
# Development
cd /home/marlonsc/flext
make dev-service

# Production
docker-compose up -d flext-service
```

### Gerenciar Plugins

```bash
# Listar plugins carregados
curl http://localhost:8080/api/v1/plugins

# Instalar novo plugin
curl -X POST http://localhost:8080/api/v1/plugins \
  -d '{"name": "tap-mysql", "file": "/tmp/tap-mysql.so"}'

# Recarregar plugins
curl -X POST http://localhost:8080/api/v1/plugins/reload
```

### Monitorar o Serviço

```bash
# Health check
curl http://localhost:8080/health

# Métricas Prometheus
curl http://localhost:8080/metrics

# Logs em tempo real
docker logs -f flext-service
```

---

## 🔄 FLUXO COMPLETO DE OPERAÇÃO COM FLEXCORE

### 1. **Fluxo de Requisição Completo: FlexCore → FLEXT → Bibliotecas Python**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FLUXO COMPLETO DE OPERAÇÃO                             │
└─────────────────────────────────────────────────────────────────────────────────┘

1. EXTERNAL REQUEST
   ↓
2. FLEXCORE CONTAINER (Event Sourcing + CQRS)
   ├─ Event: PipelineExecutionRequested
   ├─ Command: ExecutePipelineCommand
   ├─ Query: GetPipelineConfiguration
   └─ Plugin System: Load FLEXT service plugin
   ↓
3. FLEXT SERVICE (Go - Clean Architecture + DDD)
   ├─ HTTP Handler (Presentation Layer)
   ├─ Pipeline Service (Application Layer)
   ├─ Domain Services (Business Logic)
   ├─ DI Container (Infrastructure)
   └─ Subprocess Execution
   ↓
4. PYTHON LIBRARIES (External Process Integration)
   ├─ flext-core: Base Types + Domain Models
   ├─ flext-api: FastAPI REST Services
   ├─ flext-meltano: ETL Orchestration
   └─ flext-plugin: Plugin Framework
   ↓
5. RESPONSE BACK THROUGH LAYERS
   ↓
6. EXTERNAL RESPONSE (JSON/gRPC/Web Interface)
```

### 2. **Exemplo Concreto: Pipeline Oracle → PostgreSQL**

```bash
# 1. External API Request
curl -X POST http://flexcore.company.com:8080/api/v1/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "data-migration-oracle-postgres",
    "pipeline": {
      "name": "oracle-to-postgres",
      "extractor": "tap-oracle",
      "loader": "target-postgres",
      "config": {
        "source": {"host": "oracle.db", "query": "SELECT * FROM customers"},
        "target": {"host": "postgres.db", "database": "warehouse"}
      }
    }
  }'
```

```go
// 2. FLEXCORE Event Processing
func (ws *WorkflowService) ProcessDataMigrationWorkflow(ctx context.Context, req WorkflowRequest) error {
    // Event Sourcing: Record workflow started
    startEvent := events.NewWorkflowStartedEvent(req.WorkflowID, req.Pipeline)
    if err := ws.eventStore.SaveEvent(ctx, startEvent); err != nil {
        return fmt.Errorf("failed to save workflow start event: %w", err)
    }

    // CQRS: Command to execute pipeline
    command := commands.NewExecutePipelineCommand{
        PipelineID: req.Pipeline.Name,
        Config:     req.Pipeline.Config,
        Context:    ctx,
    }

    // Plugin System: Load FLEXT service plugin
    flextPlugin, err := ws.pluginLoader.LoadPlugin("flext-service")
    if err != nil {
        return fmt.Errorf("failed to load FLEXT service plugin: %w", err)
    }

    // Distributed Coordination: Reserve cluster resources
    if err := ws.cluster.ReserveResources(ctx, req.WorkflowID); err != nil {
        return fmt.Errorf("failed to reserve cluster resources: %w", err)
    }

    // Execute FLEXT service within FLEXCORE container
    result, err := flextPlugin.ExecutePipeline(ctx, command)
    if err != nil {
        // Event Sourcing: Record failure
        failEvent := events.NewWorkflowFailedEvent(req.WorkflowID, err.Error())
        ws.eventStore.SaveEvent(ctx, failEvent)
        return fmt.Errorf("FLEXT pipeline execution failed: %w", err)
    }

    // Event Sourcing: Record completion
    completeEvent := events.NewWorkflowCompletedEvent(req.WorkflowID, result)
    return ws.eventStore.SaveEvent(ctx, completeEvent)
}
```

```go
// 3. FLEXT Service Processing (Internal)
func (h *PipelineHandler) ExecutePipeline(c *gin.Context) {
    var request PipelineExecuteRequest
    if err := c.ShouldBindJSON(&request); err != nil {
        h.logger.Error("Invalid request format", logging.F("error", err.Error()))
        c.JSON(400, gin.H{"error": "Invalid request format"})
        return
    }

    // Clean Architecture: Use case execution via DI container
    pipelineService := h.container.GetPipelineService()
    result, err := pipelineService.Execute(c.Request.Context(), pipelineApp.ExecuteCommand{
        Name:      request.Name,
        Extractor: request.Extractor,
        Loader:    request.Loader,
        Config:    request.Config,
    })

    if err != nil {
        h.logger.Error("Pipeline execution failed",
            logging.F("pipeline", request.Name),
            logging.F("error", err.Error()))
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }

    h.logger.Info("Pipeline executed successfully",
        logging.F("pipeline", request.Name),
        logging.F("records_processed", result.RecordsProcessed))

    c.JSON(200, gin.H{
        "status": "completed",
        "pipeline": request.Name,
        "records_processed": result.RecordsProcessed,
        "execution_time_ms": result.ExecutionTimeMs,
    })
}
```

```python
# 4. Python Library Integration (subprocess execution)
# internal/infrastructure/python_bridge.go calls Python libraries
pythonCmd := exec.CommandContext(ctx,
    "/home/marlonsc/flext/.venv/bin/python3",
    "-m", "flext_meltano.cli",
    "run", "tap-oracle", "target-postgres"
)

pythonCmd.Env = append(os.Environ(),
    "PYTHONPATH=/home/marlonsc/flext/flext-core/src:/home/marlonsc/flext/flext-meltano/src",
    fmt.Sprintf("FLEXT_CONFIG=%s", configJSON),
)

output, err := pythonCmd.CombinedOutput()
```

```python
# 5. Python Library Execution (flext-meltano)
from flext_core import Pipeline, PipelineExecution
from flext_meltano.application.services import MeltanoOrchestrator

async def execute_pipeline(config: dict) -> PipelineExecution:
    """Execute Meltano pipeline using flext-core domain entities."""

    # Use flext-core domain models
    pipeline = Pipeline(
        name=config["name"],
        extractor=config["extractor"],
        loader=config["loader"]
    )

    # Meltano orchestration
    orchestrator = MeltanoOrchestrator()
    result = await orchestrator.run_pipeline(
        extractor=pipeline.extractor,
        loader=pipeline.loader,
        config=config["config"]
    )

    # Return standardized domain entity
    return PipelineExecution(
        pipeline_id=pipeline.id,
        status="completed",
        records_processed=result.record_count,
        execution_time_ms=result.duration_ms
    )
```

### 3. **Configuração e Deployment Completo**

```yaml
# docker-compose.production.yml - FLEXCORE + FLEXT DEPLOYMENT
version: "3.8"

services:
  # FLEXCORE Container - Event-driven runtime
  flexcore-container:
    build:
      context: ./flexcore
      dockerfile: Dockerfile.production
    ports:
      - "8080:8080" # FlexCore API Gateway
      - "9090:9090" # Prometheus metrics
      - "6379:6379" # Redis coordination
    environment:
      - FLEXCORE_ENV=production
      - FLEXCORE_CLUSTER_MODE=true
      - FLEXCORE_EVENT_STORE=postgres
      - FLEXCORE_PLUGIN_DIR=/app/plugins
    volumes:
      - ./plugins:/app/plugins:ro
      - ./config/flexcore.yaml:/app/config.yaml:ro
    depends_on:
      - postgres-events
      - redis-coordination
    command: ["./flexcore-server", "--config", "/app/config.yaml"]

  # FLEXT Service - Clean Architecture service (plugin within FlexCore)
  flext-service:
    build:
      context: .
      dockerfile: cmd/flext/Dockerfile.production
    environment:
      - FLEXT_ENV=production
      - FLEXT_CONFIG_FILE=/app/flext-config.yaml
      - FLEXT_PLUGIN_DIR=/app/plugins
      - PYTHON_PATH=/app/.venv/bin/python3
      - PYTHONPATH=/app/libraries
    volumes:
      - ./config/flext.yaml:/app/flext-config.yaml:ro
      - ./plugins:/app/plugins:ro
      - ./flext-*/src:/app/libraries:ro
    # Note: FLEXT runs as plugin inside FlexCore, not standalone
    profiles: ["development-only"]

  # Python Libraries Runtime Environment
  python-runtime:
    build:
      context: .
      dockerfile: python.Dockerfile
    environment:
      - PYTHONPATH=/app/libraries
    volumes:
      - ./flext-core/src:/app/libraries/flext_core:ro
      - ./flext-api/src:/app/libraries/flext_api:ro
      - ./flext-meltano/src:/app/libraries/flext_meltano:ro
      - ./flext-plugin/src:/app/libraries/flext_plugin:ro
    command: ["python3", "-c", "import time; time.sleep(3600)"] # Keep alive
    profiles: ["development-only"]

  # Event Store for FlexCore Event Sourcing
  postgres-events:
    image: postgres:15
    environment:
      POSTGRES_DB: flexcore_events
      POSTGRES_USER: flexcore
      POSTGRES_PASSWORD: ${FLEXCORE_POSTGRES_PASSWORD}
    volumes:
      - flexcore_events_data:/var/lib/postgresql/data
      - ./flexcore/migrations:/docker-entrypoint-initdb.d:ro

  # Coordination Layer for FlexCore Cluster
  redis-coordination:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes", "--cluster-enabled", "yes"]
    volumes:
      - flexcore_coordination_data:/data

  # FLEXT Database (separate from FlexCore events)
  postgres-flext:
    image: postgres:15
    environment:
      POSTGRES_DB: flext
      POSTGRES_USER: flext
      POSTGRES_PASSWORD: ${FLEXT_POSTGRES_PASSWORD}
    volumes:
      - flext_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d:ro

volumes:
  flexcore_events_data:
  flexcore_coordination_data:
  flext_data:
```

```yaml
# config/flexcore.yaml - FLEXCORE CONFIGURATION
cluster:
  enabled: true
  node_id: "flexcore-node-1"
  coordination:
    redis:
      host: redis-coordination
      port: 6379
      cluster: true

event_sourcing:
  enabled: true
  store:
    type: "postgres"
    connection_string: "postgres://flexcore:${FLEXCORE_POSTGRES_PASSWORD}@postgres-events:5432/flexcore_events"
  snapshots:
    enabled: true
    interval: 100 # Take snapshot every 100 events

cqrs:
  enabled: true
  command_timeout: "30s"
  query_timeout: "10s"

plugins:
  enabled: true
  directory: "/app/plugins"
  hashicorp_style: true
  dynamic_loading: true

  # Register FLEXT service as plugin
  services:
    flext-service:
      type: "workflow_executor"
      binary_path: "/app/plugins/flext-service"
      config_path: "/app/flext-config.yaml"
      health_check_endpoint: "http://localhost:8081/health"
      capabilities:
        - "pipeline_execution"
        - "data_extraction"
        - "data_loading"
        - "meltano_orchestration"

observability:
  prometheus:
    enabled: true
    port: 9090
    path: "/metrics"
  distributed_tracing:
    enabled: true
    jaeger_endpoint: "http://jaeger:14268/api/traces"
```

```yaml
# config/flext.yaml - FLEXT SERVICE CONFIGURATION
server:
  host: "0.0.0.0"
  port: 8081
  shutdown_timeout: "30s"

database:
  driver: "postgres"
  host: "postgres-flext"
  port: 5432
  database: "flext"
  username: "flext"
  password: "${FLEXT_POSTGRES_PASSWORD}"

features:
  database_enabled: true
  clean_architecture:
    enabled: true

python:
  venv_path: "/app/.venv"
  libraries_path: "/app/libraries"
  modules:
    - "flext_core"
    - "flext_api"
    - "flext_meltano"
    - "flext_plugin"

plugins:
  directory: "/app/plugins"
  auto_discovery: true

meltano:
  project_root: "/app/meltano-projects"
  python_path: "/app/.venv/bin/python3"

dbt:
  project_path: "/app/dbt-projects"
  profiles_dir: "/app/.dbt"
```

### 4. **Monitoramento e Observabilidade Integrados**

```go
// flexcore/internal/infrastructure/monitoring/metrics.go
func (m *FlexCoreMetrics) RegisterFlextServiceMetrics() {
    // FlexCore-level metrics
    prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "flexcore_workflow_executions_total",
            Help: "Total workflow executions in FlexCore",
        },
        []string{"workflow_type", "status", "service"},
    )

    prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "flexcore_workflow_duration_seconds",
            Help: "Workflow execution duration",
        },
        []string{"workflow_type", "service"},
    )

    // FLEXT service metrics (from plugin)
    prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "flexcore_flext_pipeline_executions_total",
            Help: "FLEXT pipeline executions via FlexCore",
        },
        []string{"pipeline_name", "extractor", "loader", "status"},
    )

    // Python library integration metrics
    prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "flexcore_python_subprocess_duration_seconds",
            Help: "Python library subprocess execution time",
        },
        []string{"library", "operation"},
    )

    // Event sourcing metrics
    prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "flexcore_events_stored_total",
            Help: "Total events stored in event store",
        },
        []string{"event_type", "aggregate_type"},
    )
}
```

```bash
# scripts/deploy-production.sh - DEPLOYMENT SCRIPT
#!/bin/bash

echo "🚀 Deploying FLEXT with FlexCore Container..."

# Build FlexCore container
echo "Building FlexCore container..."
docker build -t flexcore:production ./flexcore

# Build FLEXT service plugin
echo "Building FLEXT service plugin..."
cd cmd/flext && go build -o ../../plugins/flext-service main.go && cd ../..

# Prepare Python libraries
echo "Preparing Python libraries..."
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./flext-core
pip install -e ./flext-api
pip install -e ./flext-meltano
pip install -e ./flext-plugin

# Start production environment
echo "Starting production environment..."
docker-compose -f docker-compose.production.yml up -d

# Health checks
echo "Running health checks..."
./scripts/health-check-flexcore.sh
./scripts/health-check-flext.sh

echo "✅ FLEXT with FlexCore deployment completed!"
echo "🌐 FlexCore API: http://localhost:8080"
echo "📊 Metrics: http://localhost:9090/metrics"
```

---

## ✅ BENEFÍCIOS DESTA ARQUITETURA FLEXCORE + FLEXT

### 1. **Arquitetura Distribuída e Resiliente**

- ✅ **FlexCore Container**: Runtime distribuído com coordenação de cluster
- ✅ **Event Sourcing**: Audit trail completo de todas as operações
- ✅ **CQRS Pattern**: Separação otimizada de leitura/escrita
- ✅ **Plugin System**: Carregamento dinâmico estilo HashiCorp
- ✅ **Distributed Coordination**: Sincronização multi-nó via Redis/etcd

### 2. **Flexibilidade Máxima com Governança**

- ✅ **Serviço Único**: FLEXT como plugin dentro do FlexCore container
- ✅ **Bibliotecas Modulares**: Python libraries como processos externos
- ✅ **Hot Reload**: Plugins podem ser recarregados sem restart
- ✅ **Versionamento Independente**: FlexCore, FLEXT, e bibliotecas evoluem separadamente
- ✅ **Multi-Language**: Go para performance, Python para flexibilidade

### 3. **Observabilidade e Auditoria Completas**

- ✅ **Event Store**: Todos os eventos são persistidos e auditáveis
- ✅ **Distributed Tracing**: Rastreamento completo através das camadas
- ✅ **Métricas Unificadas**: Prometheus metrics do FlexCore ao Python
- ✅ **Centralized Logging**: Logs estruturados de toda a stack
- ✅ **Health Monitoring**: Health checks em cada camada

### 4. **Performance e Escalabilidade Enterprise**

- ✅ **Distributed Execution**: Workloads distribuídos automaticamente
- ✅ **Resource Coordination**: Reserva inteligente de recursos do cluster
- ✅ **Async Processing**: Event-driven execution com processamento assíncrono
- ✅ **Caching Layers**: Cache distribuído para performance
- ✅ **Load Balancing**: Distribuição automática de carga entre nós

---

## 🔒 CONCLUSÃO

**FLEXT é um SERVIÇO ÚNICO e PODEROSO** executando dentro do **FLEXCORE CONTAINER DISTRIBUÍDO** que orquestra todas as funcionalidades de integração de dados através de:

### Arquitetura de 3 Camadas

1. **FLEXCORE CONTAINER** (Camada Superior):

   - Runtime distribuído orientado a eventos (Go)
   - Event Sourcing + CQRS Pattern
   - Plugin System estilo HashiCorp
   - Coordenação de cluster distribuído

2. **FLEXT SERVICE** (Camada Intermediária):

   - Serviço único em Clean Architecture + DDD (Go)
   - Plugin carregado dinamicamente pelo FlexCore
   - DI Container com bounded contexts
   - Integration layer para bibliotecas Python

3. **Python LIBRARIES** (Camada Externa):
   - `flext-core`, `flext-api`, `flext-auth`, `flext-cli`, `flext-grpc`, `flext-plugin`, `flext-web`
   - **SÃO SIMPLESMENTE BIBLIOTECAS** integradas via subprocess
   - Especialização em domínios específicos
   - Reutilização em diferentes contextos

### Benefícios Únicos

- **Máxima Flexibilidade**: Plugin system + library architecture
- **Mínima Complexidade**: Serviço único com runtime distribuído
- **Performance Superior**: Event-driven + in-process quando possível
- **Auditoria Completa**: Event sourcing de todas as operações
- **Escalabilidade Enterprise**: Distributed cluster coordination

Esta arquitetura oferece **enterprise-grade reliability** com **startup agility**, permitindo extensões via plugins FlexCore enquanto mantém **performance superior** através do FLEXT service e **flexibilidade máxima** através das bibliotecas Python especializadas.

---

**DOCUMENT VERSION**: 2.0.0 - SOURCE OF TRUTH  
**MAINTAINER**: FLEXT Architecture Team  
**NEXT REVIEW**: 2025-04-22
