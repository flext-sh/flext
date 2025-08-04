// Package container - Dependency Injection Container for FLEXT Service
package container

import (
	"context"
	"fmt"
	"time"

	"github.com/flext-sh/flext/pkg/controlpanel/configuration/config"
	"github.com/flext-sh/flext/pkg/controlpanel/handlers"
	"github.com/flext-sh/flext/pkg/logging"
	"github.com/flext-sh/flext/pkg/plugins/registry"
	"github.com/flext-sh/flext/pkg/plugins/deployment"
	"github.com/flext-sh/flext/pkg/plugins/communication"
	"github.com/flext-sh/flext/pkg/plugins/loader"
)

// Container manages dependency injection for FLEXT services
type Container struct {
	config               *config.Config
	logger               logging.Logger
	flexcoreHandler      *handlers.FlexCoreHandler
	meltanoHandler       *handlers.MeltanoHandler
	pluginHandler        interface{} // TODO: Implement when plugin system is ready
	pipelineHandler      interface{} // TODO: Implement when pipeline system is ready
	
	// Plugin System Dependencies (injected via DI)
	pluginRegistry       *registry.PluginRegistry
	deploymentManager    *deployment.PluginDeploymentManager
	communicationBus     *communication.FlexCoreCommunicationBus
	pluginLoader         *loader.PluginLoader
}

// NewContainer creates a new DI container
func NewContainer(cfg *config.Config) (*Container, error) {
	if cfg == nil {
		return nil, fmt.Errorf("config cannot be nil")
	}

	logger := logging.GetLogger()

	// Initialize plugin system via DI
	pluginRegistry, deploymentManager, communicationBus, pluginLoader, err := initializePluginSystem(cfg, logger)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize plugin system via DI: %w", err)
	}

	// Initialize real handlers
	flexcoreHandler := handlers.NewFlexCoreHandler(cfg, logger)
	meltanoHandler := handlers.NewMeltanoHandler(cfg, logger)

	logger.Info("FLEXT Service DI Container initialized with production handlers",
		logging.F("flexcore_handler", "✅ FlexCoreHandler"),
		logging.F("meltano_handler", "✅ MeltanoHandler"),
		logging.F("plugin_system", "✅ Plugin System via DI"),
		logging.F("plugin_handler", "⏳ Future implementation"),
		logging.F("pipeline_handler", "⏳ Future implementation"))

	return &Container{
		config:               cfg,
		logger:               logger,
		flexcoreHandler:      flexcoreHandler,
		meltanoHandler:       meltanoHandler,
		pluginHandler:        nil, // TODO: Implement when ready
		pipelineHandler:      nil, // TODO: Implement when ready
		
		// Plugin System Dependencies
		pluginRegistry:       pluginRegistry,
		deploymentManager:    deploymentManager,
		communicationBus:     communicationBus,
		pluginLoader:         pluginLoader,
	}, nil
}

// initializePluginSystem initializes the complete plugin system via dependency injection
func initializePluginSystem(cfg *config.Config, logger logging.Logger) (*registry.PluginRegistry, *deployment.PluginDeploymentManager, *communication.FlexCoreCommunicationBus, *loader.PluginLoader, error) {
	logger.Info("🔌 Initializing Plugin System via DI...")

	// Initialize plugin registry
	pluginRegistry := registry.NewPluginRegistry()

	// Initialize communication bus
	redisURL := "redis://localhost:6380" // Default Redis URL
	// Extract from config if available
	if cfg != nil {
		// TODO: Extract from actual config when Redis config is added
		redisURL = "redis://localhost:6380"
	}

	nodeID := fmt.Sprintf("flext-service-%d", time.Now().Unix())
	nodeURL := "http://localhost:8081"

	communicationBus, err := communication.NewFlexCoreCommunicationBus(redisURL, nodeID, nodeURL)
	if err != nil {
		return nil, nil, nil, nil, fmt.Errorf("failed to create communication bus: %w", err)
	}

	// Initialize deployment manager
	deploymentManager := deployment.NewPluginDeploymentManager(pluginRegistry)
	deploymentManager.SetCommunicator(communicationBus)

	// Initialize plugin loader
	pluginLoader := loader.NewPluginLoader(pluginRegistry, communicationBus, logger)

	// Register core plugin factories via DI (the ONLY place specific plugins are known)
	loader.RegisterCorePluginFactories(pluginLoader, logger)

	// Load and register core plugins using default configurations
	if err := loadCorePlugins(pluginLoader, logger); err != nil {
		return nil, nil, nil, nil, fmt.Errorf("failed to load core plugins: %w", err)
	}

	// Set up cross-references
	pluginRegistry.SetCommunicator(communicationBus)
	pluginRegistry.SetDeploymentManager(deploymentManager)

	// Start plugin system services
	if err := startPluginSystemServices(pluginRegistry, deploymentManager, communicationBus, logger); err != nil {
		return nil, nil, nil, nil, fmt.Errorf("failed to start plugin system services: %w", err)
	}

	logger.Info("✅ Plugin System initialized via DI")
	return pluginRegistry, deploymentManager, communicationBus, pluginLoader, nil
}

// loadCorePlugins loads core plugins using the plugin loader
func loadCorePlugins(pluginLoader *loader.PluginLoader, logger logging.Logger) error {
	logger.Info("📦 Loading core plugins via plugin loader...")

	// Get default plugin configurations
	configs := loader.GetDefaultPluginConfigurations()

	// Load plugins from configurations
	ctx := context.Background()
	if err := pluginLoader.LoadPluginsFromConfiguration(ctx, configs); err != nil {
		return fmt.Errorf("failed to load plugins from configuration: %w", err)
	}

	logger.Info("✅ Core plugins loaded successfully via DI")
	return nil
}

// startPluginSystemServices starts all plugin system background services
func startPluginSystemServices(registry *registry.PluginRegistry, deploymentMgr *deployment.PluginDeploymentManager, commBus *communication.FlexCoreCommunicationBus, logger logging.Logger) error {
	logger.Info("🚀 Starting plugin system services...")

	// Start plugin registry
	if err := registry.Start(); err != nil {
		return fmt.Errorf("failed to start plugin registry: %w", err)
	}

	// Start deployment manager
	if err := deploymentMgr.Start(); err != nil {
		return fmt.Errorf("failed to start deployment manager: %w", err)
	}

	// Start communication bus
	if err := commBus.Start(); err != nil {
		return fmt.Errorf("failed to start communication bus: %w", err)
	}

	logger.Info("✅ All plugin system services started")
	return nil
}

// GetPluginHandler returns the plugin handler
func (c *Container) GetPluginHandler() interface{} {
	if c.pluginHandler != nil {
		c.logger.Info("Plugin handler retrieved from DI container")
		return c.pluginHandler
	}
	
	c.logger.Info("Plugin handler not yet implemented - future expansion")
	return nil
}

// GetUnifiedMeltanoHandler returns the unified Meltano handler
func (c *Container) GetUnifiedMeltanoHandler() interface{} {
	if c.meltanoHandler != nil {
		c.logger.Info("Unified Meltano handler retrieved from DI container",
			logging.F("handler_type", "MeltanoHandler"),
			logging.F("features", "Meltano + Singer + DBT via flext-meltano"))
		return c.meltanoHandler
	}
	
	c.logger.Warn("Meltano handler is nil - initialization failed")
	return nil
}

// GetFlexcoreHandler returns the FlexCore handler
func (c *Container) GetFlexcoreHandler() interface{} {
	if c.flexcoreHandler != nil {
		c.logger.Info("FlexCore handler retrieved from DI container",
			logging.F("handler_type", "FlexCoreHandler"),
			logging.F("features", "FlexCore coordination + plugin management"))
		return c.flexcoreHandler
	}
	
	c.logger.Warn("FlexCore handler is nil - initialization failed")
	return nil
}

// GetPipelineHandler returns the pipeline handler
func (c *Container) GetPipelineHandler() interface{} {
	if c.pipelineHandler != nil {
		c.logger.Info("Pipeline handler retrieved from DI container")
		return c.pipelineHandler
	}
	
	c.logger.Info("Pipeline handler not yet implemented - future expansion")
	return nil
}

// GetPluginRegistry returns the plugin registry
func (c *Container) GetPluginRegistry() *registry.PluginRegistry {
	if c.pluginRegistry != nil {
		c.logger.Info("Plugin registry retrieved from DI container")
		return c.pluginRegistry
	}
	
	c.logger.Warn("Plugin registry is nil - initialization failed")
	return nil
}

// GetDeploymentManager returns the deployment manager
func (c *Container) GetDeploymentManager() *deployment.PluginDeploymentManager {
	if c.deploymentManager != nil {
		c.logger.Info("Deployment manager retrieved from DI container")
		return c.deploymentManager
	}
	
	c.logger.Warn("Deployment manager is nil - initialization failed")
	return nil
}

// GetCommunicationBus returns the communication bus
func (c *Container) GetCommunicationBus() *communication.FlexCoreCommunicationBus {
	if c.communicationBus != nil {
		c.logger.Info("Communication bus retrieved from DI container")
		return c.communicationBus
	}
	
	c.logger.Warn("Communication bus is nil - initialization failed")
	return nil
}

// GetPluginLoader returns the plugin loader
func (c *Container) GetPluginLoader() *loader.PluginLoader {
	if c.pluginLoader != nil {
		c.logger.Info("Plugin loader retrieved from DI container")
		return c.pluginLoader
	}
	
	c.logger.Warn("Plugin loader is nil - initialization failed")
	return nil
}

// Stop gracefully stops all services managed by the DI container
func (c *Container) Stop() error {
	c.logger.Info("🛑 Stopping DI container services...")

	// Stop plugin system services
	if c.communicationBus != nil {
		if err := c.communicationBus.Stop(); err != nil {
			c.logger.Error("⚠️ Error stopping communication bus", logging.F("error", err))
		} else {
			c.logger.Info("✅ Communication bus stopped")
		}
	}

	if c.deploymentManager != nil {
		if err := c.deploymentManager.Stop(); err != nil {
			c.logger.Error("⚠️ Error stopping deployment manager", logging.F("error", err))
		} else {
			c.logger.Info("✅ Deployment manager stopped")
		}
	}

	if c.pluginRegistry != nil {
		if err := c.pluginRegistry.Stop(); err != nil {
			c.logger.Error("⚠️ Error stopping plugin registry", logging.F("error", err))
		} else {
			c.logger.Info("✅ Plugin registry stopped")
		}
	}

	c.logger.Info("✅ DI container services stopped successfully")
	return nil
}
