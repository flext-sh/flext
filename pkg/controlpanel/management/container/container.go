// Package container - Dependency Injection Container for FLEXT Service
package container

import (
	"fmt"

	"github.com/flext-sh/flext/pkg/controlpanel/configuration/config"
	"github.com/flext-sh/flext/pkg/controlpanel/handlers"
	"github.com/flext-sh/flext/pkg/logging"
)

// Container manages dependency injection for FLEXT services
type Container struct {
	config               *config.Config
	logger               logging.Logger
	flexcoreHandler      *handlers.FlexCoreHandler
	meltanoHandler       *handlers.MeltanoHandler
	pluginHandler        interface{} // TODO: Implement when plugin system is ready
	pipelineHandler      interface{} // TODO: Implement when pipeline system is ready
}

// NewContainer creates a new DI container
func NewContainer(cfg *config.Config) (*Container, error) {
	if cfg == nil {
		return nil, fmt.Errorf("config cannot be nil")
	}

	logger := logging.GetLogger()

	// Initialize real handlers
	flexcoreHandler := handlers.NewFlexCoreHandler(cfg, logger)
	meltanoHandler := handlers.NewMeltanoHandler(cfg, logger)

	logger.Info("FLEXT Service DI Container initialized with production handlers",
		logging.F("flexcore_handler", "✅ FlexCoreHandler"),
		logging.F("meltano_handler", "✅ MeltanoHandler"),
		logging.F("plugin_handler", "⏳ Future implementation"),
		logging.F("pipeline_handler", "⏳ Future implementation"))

	return &Container{
		config:               cfg,
		logger:               logger,
		flexcoreHandler:      flexcoreHandler,
		meltanoHandler:       meltanoHandler,
		pluginHandler:        nil, // TODO: Implement when ready
		pipelineHandler:      nil, // TODO: Implement when ready
	}, nil
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
