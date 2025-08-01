package container

import (
	"context"
	"fmt"
	"sync"

	// Shared kernel imports
	"github.com/flext/flexcore/internal/shared_kernel/infrastructure/auth"
	"github.com/flext/flexcore/internal/shared_kernel/infrastructure/config"

	// Bounded context imports
	pipelineApp "github.com/flext/flexcore/internal/bounded_contexts/pipeline/application"
	pipelinePorts "github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/ports"
	pipelineServices "github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/services"

	pluginApp "github.com/flext/flexcore/internal/bounded_contexts/plugin/application"
	pluginPorts "github.com/flext/flexcore/internal/bounded_contexts/plugin/application/ports"

	// Infrastructure imports
	"github.com/flext/flexcore/internal/infrastructure/database"
	"github.com/flext/flexcore/internal/infrastructure/events"
	"github.com/flext/flexcore/internal/infrastructure/execution"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/flext/flexcore/internal/infrastructure/persistence"
)

// UnifiedContainer provides dependency injection using unified configuration
type UnifiedContainer struct {
	mu sync.RWMutex

	// Configuration
	configAdapter *config.ConfigAdapter

	// Shared Infrastructure
	authService    *auth.UnifiedAuthService
	eventPublisher events.EventPublisher
	logger         logging.Logger
	dbConnection   *database.Connection

	// Repositories - using concrete implementations for compatibility
	pipelineRepo pipelinePorts.PipelineRepository
	pluginRepo   pluginPorts.PluginRepository

	// Domain Services
	pipelineExecutor *pipelineServices.PipelineExecutor

	// Application Services
	pipelineService *pipelineApp.PipelineService
	pluginService   *pluginApp.PluginService
}

// NewUnifiedContainer creates a new container with unified configuration
func NewUnifiedContainer() (*UnifiedContainer, error) {
	// Load unified configuration
	configAdapter, err := config.NewConfigAdapter()
	if err != nil {
		return nil, fmt.Errorf("failed to create config adapter: %w", err)
	}

	container := &UnifiedContainer{
		configAdapter: configAdapter,
	}

	if err := container.initializeInfrastructure(); err != nil {
		return nil, fmt.Errorf("failed to initialize infrastructure: %w", err)
	}

	if err := container.initializeRepositories(); err != nil {
		return nil, fmt.Errorf("failed to initialize repositories: %w", err)
	}

	if err := container.initializeServices(); err != nil {
		return nil, fmt.Errorf("failed to initialize services: %w", err)
	}

	if err := container.initializeHandlers(); err != nil {
		return nil, fmt.Errorf("failed to initialize handlers: %w", err)
	}

	return container, nil
}

// initializeInfrastructure sets up shared infrastructure components
func (c *UnifiedContainer) initializeInfrastructure() error {
	// Logger
	c.logger = logging.GetLogger()

	// Event Publisher
	c.eventPublisher = events.NewInMemoryEventPublisher()

	// Database connection
	unifiedConfig := c.configAdapter.GetUnifiedConfig()
	if unifiedConfig.Features.DatabaseEnabled {
		dbConfig := c.configAdapter.GetLegacyConfig().Database
		dbConn, err := database.NewConnection(&dbConfig, c.logger)
		if err != nil {
			c.logger.Warn("Failed to create database connection, using memory mode",
				logging.F("error", err.Error()))
		} else {
			c.dbConnection = dbConn
		}
	}

	// Unified Auth Service - convert config to expected format
	authConfig := unifiedConfig.Auth
	unifiedAuthConfig := auth.UnifiedAuthConfig{
		JWTSecret:          authConfig.JWTSecret,
		TokenExpiry:        authConfig.JWTExpiry,
		RefreshTokenExpiry: authConfig.RefreshExpiry,
		EnableBasicAuth:    authConfig.EnableBasicAuth,
		EnableAPIKeyAuth:   authConfig.EnableAPIKeys,
		EnableOAuth2:       authConfig.EnableOAuth2,
		OAuth2Config: auth.OAuth2Config{
			ClientID:     authConfig.OAuth2Config.ClientID,
			ClientSecret: authConfig.OAuth2Config.ClientSecret,
			RedirectURL:  authConfig.OAuth2Config.RedirectURL,
			AuthURL:      authConfig.OAuth2Config.AuthURL,
			TokenURL:     authConfig.OAuth2Config.TokenURL,
			Scopes:       authConfig.OAuth2Config.Scopes,
		},
	}

	authSvc, err := auth.NewUnifiedAuthService(unifiedAuthConfig, c.logger)
	if err != nil {
		return fmt.Errorf("failed to create auth service: %w", err)
	}
	c.authService = authSvc

	// Register auth providers based on configuration
	if authConfig.EnableBasicAuth {
		provider := auth.NewBasicAuthProvider(c.logger)
		c.authService.RegisterProvider(provider)
		c.logger.Info("Basic auth provider registered")
	}

	if authConfig.EnableAPIKeys {
		provider := auth.NewAPIKeyProvider(c.logger)
		c.authService.RegisterProvider(provider)
		c.logger.Info("API key provider registered")
	}

	if authConfig.EnableOAuth2 {
		oauth2Config := auth.OAuth2Config{
			ClientID:     authConfig.OAuth2Config.ClientID,
			ClientSecret: authConfig.OAuth2Config.ClientSecret,
			RedirectURL:  authConfig.OAuth2Config.RedirectURL,
			AuthURL:      authConfig.OAuth2Config.AuthURL,
			TokenURL:     authConfig.OAuth2Config.TokenURL,
			Scopes:       authConfig.OAuth2Config.Scopes,
		}
		provider, err := auth.NewOAuth2Provider(oauth2Config, c.logger)
		if err != nil {
			c.logger.Warn("Failed to create OAuth2 provider", logging.F("error", err.Error()))
		} else {
			c.authService.RegisterProvider(provider)
			c.logger.Info("OAuth2 provider registered")
		}
	}

	c.logger.Info("Unified infrastructure initialized successfully")
	return nil
}

// initializeRepositories sets up repository layer
func (c *UnifiedContainer) initializeRepositories() error {
	// Use database repositories if available, otherwise fallback to in-memory
	if c.dbConnection != nil && c.configAdapter.GetUnifiedConfig().Database.Driver == "postgres" {
		c.logger.Info("Using PostgreSQL repositories with unified configuration")
		c.pipelineRepo = persistence.NewPostgreSQLPipelineRepository(c.dbConnection, c.logger)
		c.pluginRepo = persistence.NewPostgreSQLPluginRepository(c.dbConnection, c.logger)
	} else {
		c.logger.Info("Using in-memory repositories (database not available)")
		c.pipelineRepo = persistence.NewInMemoryPipelineRepository()
		c.pluginRepo = persistence.NewInMemoryPluginRepository()
	}

	c.logger.Info("Repositories initialized with unified configuration")
	return nil
}

// initializeServices sets up application and domain services
func (c *UnifiedContainer) initializeServices() error {
	// Infrastructure Services for Real Execution
	workDir := c.configAdapter.GetUnifiedConfig().GetEnvWithDefault("WORK_DIR", "/tmp/flext")
	pythonPath := c.configAdapter.GetUnifiedConfig().GetEnvWithDefault("PYTHON_PATH", "python3")

	// Create real plugin executor adapter
	realPluginExecutor := execution.NewDomainPluginExecutorAdapter(
		c.logger,
		workDir,
		pythonPath,
	)

	// Domain Services with Real Execution
	c.pipelineExecutor = pipelineServices.NewPipelineExecutor(
		c.pluginRepo.(pipelineServices.PluginRepository),
		realPluginExecutor,
	)

	// Application Services
	c.pipelineService = pipelineApp.NewPipelineService(c.pipelineRepo, c.pipelineExecutor, nil) // TODO: Implement PipelineExecutionStatsService

	// Create event publisher adapter for plugin service
	eventAdapter := NewEventPublisherAdapter(c.eventPublisher)
	c.pluginService = pluginApp.NewPluginService(c.pluginRepo, eventAdapter)

	c.logger.Info("Application services initialized with unified container")
	return nil
}

// initializeHandlers sets up HTTP handlers
func (c *UnifiedContainer) initializeHandlers() error {
	// HTTP handlers will be created by the main application
	// when needed, using the services from this container
	c.logger.Info("HTTP handler initialization deferred to main application")
	return nil
}

// GetConfigAdapter returns the configuration adapter
func (c *UnifiedContainer) GetConfigAdapter() *config.ConfigAdapter {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.configAdapter
}

// GetAuthService returns the unified auth service
func (c *UnifiedContainer) GetAuthService() *auth.UnifiedAuthService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.authService
}

// GetLogger returns the logger instance
func (c *UnifiedContainer) GetLogger() logging.Logger {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.logger
}

// GetPipelineService returns the pipeline application service
func (c *UnifiedContainer) GetPipelineService() *pipelineApp.PipelineService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pipelineService
}

// GetPluginService returns the plugin application service
func (c *UnifiedContainer) GetPluginService() *pluginApp.PluginService {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pluginService
}

// Legacy compatibility methods

// GetPipelineRepo returns the pipeline repository interface
func (c *UnifiedContainer) GetPipelineRepo() pipelinePorts.PipelineRepository {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pipelineRepo
}

// GetPluginRepo returns the plugin repository interface
func (c *UnifiedContainer) GetPluginRepo() pluginPorts.PluginRepository {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return c.pluginRepo
}

// HealthCheck performs health checks on all components
func (c *UnifiedContainer) HealthCheck(ctx context.Context) error {
	// Check database connection
	if c.dbConnection != nil {
		if err := c.dbConnection.HealthCheck(ctx); err != nil {
			return fmt.Errorf("database health check failed: %w", err)
		}
	}

	// Check auth service
	if c.authService == nil {
		return fmt.Errorf("auth service not initialized")
	}

	// Check repositories
	if c.pipelineRepo == nil || c.pluginRepo == nil {
		return fmt.Errorf("repositories not initialized")
	}

	// Check services
	if c.pipelineService == nil || c.pluginService == nil {
		return fmt.Errorf("application services not initialized")
	}

	c.logger.Info("Unified container health check completed successfully")
	return nil
}

// Shutdown gracefully shuts down the container
func (c *UnifiedContainer) Shutdown() error {
	c.logger.Info("Shutting down unified container")

	// Close database connection
	if c.dbConnection != nil {
		if err := c.dbConnection.Close(); err != nil {
			c.logger.Error("Failed to close database connection",
				logging.F("error", err.Error()))
			return err
		}
	}

	c.logger.Info("Unified container shutdown completed")
	return nil
}

// EventPublisherAdapter adapts the legacy event publisher to new interface
type EventPublisherAdapter struct {
	publisher events.EventPublisher
}

// NewEventPublisherAdapter creates a new event publisher adapter
func NewEventPublisherAdapter(publisher events.EventPublisher) *EventPublisherAdapter {
	return &EventPublisherAdapter{publisher: publisher}
}

// PublishEvent publishes a single event
func (a *EventPublisherAdapter) PublishEvent(ctx context.Context, event interface{}) error {
	return a.publisher.Publish(ctx, event)
}

// PublishEvents publishes multiple events
func (a *EventPublisherAdapter) PublishEvents(ctx context.Context, events ...interface{}) error {
	for _, event := range events {
		if err := a.publisher.Publish(ctx, event); err != nil {
			return err
		}
	}
	return nil
}
