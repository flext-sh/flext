package container

import (
	"context"
	"fmt"
	"sync"

	pipelineApp "github.com/flext/flexcore/internal/bounded_contexts/pipeline/application"
	pipelinePorts "github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/ports"
	pipelineAppServices "github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/services"
	pipelineServices "github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/services"

	pluginApp "github.com/flext/flexcore/internal/bounded_contexts/plugin/application"
	pluginPorts "github.com/flext/flexcore/internal/bounded_contexts/plugin/application/ports"

	meltanoServices "github.com/flext/flexcore/internal/bounded_contexts/meltano/application/services"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/flext/flexcore/internal/infrastructure/database"
	"github.com/flext/flexcore/internal/infrastructure/dbt"
	"github.com/flext/flexcore/internal/infrastructure/events"
	"github.com/flext/flexcore/internal/infrastructure/flexcore_plugin"
	"github.com/flext/flexcore/internal/infrastructure/http"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/flext/flexcore/internal/infrastructure/persistence"
	"github.com/flext/flexcore/internal/infrastructure/plugin_execution"
	"github.com/flext/flexcore/internal/infrastructure/singer"
	"github.com/pkg/errors"
)

// Container gerencia as dependências da aplicação
type Container struct {
	mu sync.RWMutex

	// Configuration
	config *config.Config

	// Infrastructure
	dbConnection   *database.Connection
	eventPublisher events.EventPublisher
	logger         logging.Logger

	// Repositories (interface types for flexibility)
	pipelineRepo  pipelinePorts.PipelineRepository
	pluginRepo    pluginPorts.PluginRepository
	executionRepo pipelinePorts.ExecutionRepository

	// Domain Services
	pipelineExecutor *pipelineServices.PipelineExecutor

	// Application Services
	pipelineService       *pipelineApp.PipelineService
	pluginService         *pluginApp.PluginService
	meltanoService        *meltanoServices.MeltanoService
	executionStatsService *pipelineAppServices.PipelineExecutionStatsService
	dbtManager            *dbt.DBTManager
	singerManager         *singer.SingerManager

	// FLEXCORE Plugin Registry
	flexcorePluginRegistry *flexcore_plugin.PluginRegistry

	// HTTP Handlers
	pipelineHandler       *http.CleanPipelineHandler
	pluginHandler         *http.PluginHandler
	unifiedMeltanoHandler *http.UnifiedMeltanoHandler
	meltanoGopyHandler    *http.MeltanoGopyHandler
	connectorsHandler     *http.ConnectorsHandler
	webHandler            *http.SimpleBootstrapHandler
	flexcoreHandler       *http.FlexcoreHandler
}

// NewContainer cria um novo container de dependências
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
	// Infrastructure
	c.logger = logging.GetLogger()
	c.eventPublisher = events.NewInMemoryEventPublisher()

	// Database connection (only if enabled)
	if err := c.initializeDatabase(); err != nil {
		return errors.Wrap(err, "initializing database connection in container")
	}

	// Repositories
	if err := c.initializeRepositories(); err != nil {
		return errors.Wrap(err, "initializing repository layer")
	}

	// Domain Services - Use Real Plugin Executor with Complete Environment
	executorFactory := plugin_execution.NewExecutorFactory()

	// Try to create production executor with complete environment
	productionExecutor, err := executorFactory.CreateProductionExecutor(
		c.pluginRepo.(pipelineServices.PluginRepository),
	)

	if err != nil {
		c.logger.Warn("Failed to create production executor, falling back to development mode",
			logging.F("error", err.Error()))

		// Fallback: Setup basic plugin directory and install samples for development
		if err := executorFactory.SetupPluginDirectory(); err != nil {
			c.logger.Warn("Failed to setup plugin directory", logging.F("error", err))
		}
		if err := executorFactory.InstallSamplePlugins(); err != nil {
			c.logger.Warn("Failed to install sample plugins", logging.F("error", err))
		}

		// Create basic real pipeline executor
		c.pipelineExecutor = executorFactory.CreatePipelineExecutor(
			c.pluginRepo.(pipelineServices.PluginRepository),
		)
	} else {
		// Use production executor
		c.pipelineExecutor = productionExecutor
		c.logger.Info("✅ Production pipeline executor with complete environment created")
	}

	// Create execution stats service
	c.executionStatsService = pipelineAppServices.NewPipelineExecutionStatsService(
		c.executionRepo,
		c.pipelineRepo,
	)

	// Create event publisher adapter
	eventAdapter := NewEventPublisherAdapter(c.eventPublisher)

	// Application Services
	c.pipelineService = pipelineApp.NewPipelineService(c.pipelineRepo, c.pipelineExecutor, c.executionStatsService)

	c.pluginService = pluginApp.NewPluginService(
		c.pluginRepo,
		eventAdapter,
	)

	// Get Python path for both Meltano and DBT
	pythonPath := c.config.GetEnvWithDefault("PYTHON_PATH", "/home/marlonsc/flext/.venv/bin/python3")

	// Meltano Service with auto-detection
	meltanoSvc, err := meltanoServices.NewMeltanoServiceWithConfig(c.logger)
	if err != nil {
		c.logger.Warn("Failed to create Meltano service with auto-detection, falling back to manual configuration",
			logging.F("error", err.Error()))

		// Fallback to manual configuration
		projectRoot := c.config.GetEnvWithDefault("PROJECT_ROOT", ".")
		c.meltanoService = meltanoServices.NewMeltanoService(pythonPath, projectRoot)
	} else {
		c.meltanoService = meltanoSvc
	}

	// DBT Manager
	dbtConfig := &dbt.DBTConfig{
		ProjectPath:   c.config.GetEnvWithDefault("DBT_PROJECT_PATH", "./dbt_project"),
		ProfilesDir:   c.config.GetEnvWithDefault("DBT_PROFILES_DIR", "~/.dbt"),
		PythonPath:    pythonPath,
		DBTPath:       c.config.GetEnvWithDefault("DBT_PATH", "dbt"),
		VenvPath:      c.config.GetEnvWithDefault("VENV_PATH", "/home/marlonsc/flext/.venv"),
		DefaultTarget: c.config.GetEnvWithDefault("DBT_DEFAULT_TARGET", "dev"),
	}
	var dbtErr error
	c.dbtManager, dbtErr = dbt.NewDBTManager(dbtConfig, c.logger)
	if dbtErr != nil {
		c.logger.Warn("Failed to initialize DBT manager",
			logging.F("error", dbtErr.Error()),
		)
	}

	// Singer Manager
	singerWorkDir := c.config.GetEnvWithDefault("SINGER_WORK_DIR", "/tmp/flext-singer")
	meltanoProjectDir := c.config.GetEnvWithDefault("MELTANO_PROJECT_PATH", "")
	c.singerManager = singer.NewSingerManager(c.logger, singerWorkDir, meltanoProjectDir)

	// FLEXCORE Plugin Registry - Register FLEXT plugins for FLEXCORE execution
	fmt.Println("🏗️ CONTAINER: About to create FLEXCORE PluginRegistry...")
	c.flexcorePluginRegistry = flexcore_plugin.NewPluginRegistry(c.config, c.logger)
	fmt.Printf("🏗️ CONTAINER: FLEXCORE PluginRegistry created: %v\n", c.flexcorePluginRegistry != nil)

	// HTTP Handlers
	// TODO: Implement CleanPipelineHandler properly
	// c.pipelineHandler = http.NewCleanPipelineHandler(...)
	c.logger.Info("Pipeline handler temporarily disabled during container setup")
	c.pluginHandler = http.NewPluginHandler(c.pluginService, c.logger)
	c.connectorsHandler = http.NewConnectorsHandler(c.logger)

	// UNIFIED HANDLER: All Meltano, Singer, DBT operations via flext-meltano library
	c.unifiedMeltanoHandler = http.NewUnifiedMeltanoHandler(c.meltanoService, c.logger)
	c.logger.Info("✅ Unified Meltano handler created (Meltano + Singer + DBT via flext-meltano)")

	// Gopy integration handler for Python-Go bridge via HTTP
	c.meltanoGopyHandler = http.NewMeltanoGopyHandler(c.meltanoService, c.logger)

	// Web interface handler - Simple Bootstrap + HTMX version
	c.webHandler = http.NewSimpleBootstrapHandler(c.logger)

	// FLEXCORE handler - Integration with FLEXCORE container
	c.flexcoreHandler = http.NewFlexcoreHandler(c.flexcorePluginRegistry, c.logger)

	return nil
}

// initializeDatabase inicializa a conexão com o banco de dados
func (c *Container) initializeDatabase() error {
	// Check if database is enabled in feature flags
	if !c.config.Features.DatabaseEnabled {
		c.logger.Info("Database disabled by feature flag, using memory mode")
		// Force memory mode when database is disabled
		memoryConfig := c.config.Database
		memoryConfig.Driver = "memory"

		dbConn, err := database.NewConnection(&memoryConfig, c.logger)
		if err != nil {
			return fmt.Errorf("failed to create memory database connection: %w", err)
		}

		c.dbConnection = dbConn
		return nil
	}

	dbConn, err := database.NewConnection(&c.config.Database, c.logger)
	if err != nil {
		return fmt.Errorf("failed to create database connection: %w", err)
	}

	c.dbConnection = dbConn

	// Executar migrations se usando banco real
	if c.config.Database.Driver != "memory" {
		migrator := database.NewMigrator(c.dbConnection.GetDB(), c.logger)

		ctx := context.Background()
		if err := migrator.Run(ctx); err != nil {
			return fmt.Errorf("failed to run database migrations: %w", err)
		}
	}

	return nil
}

// initializeRepositories inicializa os repositories baseado na configuração
func (c *Container) initializeRepositories() error {
	// Use PostgreSQL repositories if database is enabled
	if c.dbConnection != nil && c.config.Features.DatabaseEnabled && c.config.Database.Driver == "postgres" {
		c.logger.Info("Using PostgreSQL repositories",
			logging.F("driver", c.config.Database.Driver),
			logging.F("database_enabled", true),
		)

		// Create PostgreSQL repositories
		pgPipelineRepo := persistence.NewPostgreSQLPipelineRepository(c.dbConnection, c.logger)
		pgPluginRepo := persistence.NewPostgreSQLPluginRepository(c.dbConnection, c.logger)
		pgExecutionRepo := persistence.NewPostgreSQLExecutionRepository(c.dbConnection, c.logger)

		c.pipelineRepo = pgPipelineRepo
		c.pluginRepo = pgPluginRepo
		c.executionRepo = pgExecutionRepo

		c.logger.Info("PostgreSQL repositories initialized successfully",
			logging.F("repositories", []string{"pipeline", "plugin"}),
			logging.F("type", "postgresql"),
			logging.F("database", c.config.Database.Database),
			logging.F("host", c.config.Database.Host),
			logging.F("port", c.config.Database.Port),
		)
		return nil
	}

	// Fallback to in-memory repositories for guaranteed compatibility
	c.logger.Info("Using in-memory repositories (database not enabled)")

	memPipelineRepo := persistence.NewInMemoryPipelineRepository()
	memPluginRepo := persistence.NewInMemoryPluginRepository()
	memExecutionRepo := persistence.NewInMemoryExecutionRepository()

	c.pipelineRepo = memPipelineRepo
	c.pluginRepo = memPluginRepo
	c.executionRepo = memExecutionRepo

	return nil
}

// GetConfig retorna a configuração
func (c *Container) GetConfig() *config.Config {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.config
}

// GetDatabaseConnection retorna a conexão com o banco
func (c *Container) GetDatabaseConnection() *database.Connection {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.dbConnection
}

// GetPipelineService retorna o serviço de pipeline
func (c *Container) GetPipelineService() *pipelineApp.PipelineService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pipelineService
}

// GetPluginService retorna o serviço de plugin
func (c *Container) GetPluginService() *pluginApp.PluginService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pluginService
}

// GetPipelineHandler retorna o handler HTTP de pipeline
func (c *Container) GetPipelineHandler() *http.CleanPipelineHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pipelineHandler
}

// GetPluginHandler retorna o handler HTTP de plugin
func (c *Container) GetPluginHandler() *http.PluginHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pluginHandler
}

// GetMeltanoService retorna o serviço de Meltano
func (c *Container) GetMeltanoService() *meltanoServices.MeltanoService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.meltanoService
}

// GetUnifiedMeltanoHandler retorna o handler HTTP unificado (Meltano + Singer + DBT)
func (c *Container) GetUnifiedMeltanoHandler() *http.UnifiedMeltanoHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.unifiedMeltanoHandler
}

// Deprecated: Use GetUnifiedMeltanoHandler instead
func (c *Container) GetMeltanoHandler() *http.UnifiedMeltanoHandler {
	return c.GetUnifiedMeltanoHandler()
}

// NewCleanContainer creates a new container for Clean Architecture
func NewCleanContainer(cfg *config.Config, db interface{}) (*Container, error) {
	return NewContainer(cfg)
}

// GetHandlers returns all HTTP handlers for the Clean Architecture (disabled)
// func (c *Container) GetHandlers() (*http.PipelineHandler, *http.PluginHandler, interface{}, *http.MeltanoHandler) {
//	return c.GetPipelineHandler(), c.GetPluginHandler(), nil, c.GetMeltanoHandler()
// }

// GetDBTManager retorna o gerenciador de DBT
func (c *Container) GetDBTManager() *dbt.DBTManager {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.dbtManager
}

// Deprecated: Use GetUnifiedMeltanoHandler instead
func (c *Container) GetDBTHandler() *http.UnifiedMeltanoHandler {
	return c.GetUnifiedMeltanoHandler()
}

// GetConnectorsHandler retorna o handler HTTP de conectores
func (c *Container) GetConnectorsHandler() *http.ConnectorsHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.connectorsHandler
}

// GetMeltanoGopyHandler retorna o handler HTTP de integração Gopy
func (c *Container) GetMeltanoGopyHandler() *http.MeltanoGopyHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.meltanoGopyHandler
}

// GetSingerManager retorna o gerenciador Singer
func (c *Container) GetSingerManager() *singer.SingerManager {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.singerManager
}

// Deprecated: Use GetUnifiedMeltanoHandler instead
func (c *Container) GetSingerHandler() *http.UnifiedMeltanoHandler {
	return c.GetUnifiedMeltanoHandler()
}

// GetWebHandler retorna o handler HTTP da interface web
func (c *Container) GetWebHandler() *http.SimpleBootstrapHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.webHandler
}

// GetFlexcorePluginRegistry retorna o registry de plugins FLEXCORE
func (c *Container) GetFlexcorePluginRegistry() *flexcore_plugin.PluginRegistry {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.flexcorePluginRegistry
}

// GetFlexcoreHandler retorna o handler HTTP FLEXCORE
func (c *Container) GetFlexcoreHandler() *http.FlexcoreHandler {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.flexcoreHandler
}

// HealthCheck executa verificações de saúde do sistema
func (c *Container) HealthCheck(ctx context.Context) error {
	// Verificar saúde do banco de dados
	if c.dbConnection != nil {
		if err := c.dbConnection.HealthCheck(ctx); err != nil {
			return fmt.Errorf("database health check failed: %w", err)
		}
	}

	// TODO: Adicionar outras verificações de saúde
	return nil
}

// Shutdown faz o shutdown gracioso do container
func (c *Container) Shutdown() error {
	c.logger.Info("Shutting down container")

	// Fechar conexão com banco
	if c.dbConnection != nil {
		if err := c.dbConnection.Close(); err != nil {
			c.logger.Error("Failed to close database connection",
				logging.F("error", err.Error()),
			)
			return err
		}
	}

	c.logger.Info("Container shutdown completed")
	return nil
}

// Ensure interfaces are implemented
var _ pipelinePorts.PipelineRepository = (*persistence.InMemoryPipelineRepository)(nil)

// var _ pipelinePorts.PipelineRepository = (*persistence.PostgreSQLPipelineRepository)(nil) // Disabled until interface fixed

// Interface compatibility checks
// var _ pipelinePorts.EventPublisher = (*events.InMemoryEventPublisher)(nil)
var _ pluginPorts.PluginRepository = (*persistence.InMemoryPluginRepository)(nil)

// var _ pluginPorts.PluginRepository = (*persistence.PostgreSQLPluginRepository)(nil) // Disabled until interface fixed

// var _ pluginPorts.EventPublisher = (*events.InMemoryEventPublisher)(nil)
var _ pipelineServices.PluginRepository = (*persistence.InMemoryPluginRepository)(nil)

// var _ pipelineServices.PluginRepository = (*persistence.PostgreSQLPluginRepository)(nil) // Disabled until interface fixed
