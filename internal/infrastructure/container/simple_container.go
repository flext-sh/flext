package container

import (
	"context"
	"fmt"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/http"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	meltanoServices "github.com/flext-sh/flext/internal/bounded_contexts/meltano/application/services"
)

// SimpleContainer provides basic functionality for testing
type SimpleContainer struct {
	config         *config.Config
	logger         logging.Logger
	meltanoService *meltanoServices.MeltanoService
	meltanoHandler *http.MeltanoHandler
	meltanoGopyHandler *http.MeltanoGopyHandler
}

// NewSimpleContainer creates a minimal container for testing
func NewSimpleContainer(cfg *config.Config) (*SimpleContainer, error) {
	logger := logging.GetLogger()
	
	// Get Python path
	pythonPath := cfg.GetEnvWithDefault("PYTHON_PATH", "/home/marlonsc/flext/.venv/bin/python3")
	
	// Meltano Service with auto-detection
	meltanoSvc, err := meltanoServices.NewMeltanoServiceWithConfig(logger)
	if err != nil {
		logger.Warn("Failed to create Meltano service with auto-detection, falling back to manual configuration",
			logging.F("error", err.Error()))

		// Fallback to manual configuration
		projectRoot := cfg.GetEnvWithDefault("PROJECT_ROOT", ".")
		meltanoSvc = meltanoServices.NewMeltanoService(pythonPath, projectRoot)
	}

	container := &SimpleContainer{
		config:         cfg,
		logger:         logger,
		meltanoService: meltanoSvc,
		meltanoHandler: http.NewMeltanoHandler(meltanoSvc),
		meltanoGopyHandler: http.NewMeltanoGopyHandler(meltanoSvc, logger),
	}

	return container, nil
}

// GetMeltanoHandler returns the Meltano handler
func (c *SimpleContainer) GetMeltanoHandler() *http.MeltanoHandler {
	return c.meltanoHandler
}

// GetMeltanoGopyHandler returns the Meltano Gopy handler
func (c *SimpleContainer) GetMeltanoGopyHandler() *http.MeltanoGopyHandler {
	return c.meltanoGopyHandler
}

// GetPipelineHandler returns nil (disabled)
func (c *SimpleContainer) GetPipelineHandler() interface{} {
	return nil
}

// GetPluginHandler returns nil (disabled)
func (c *SimpleContainer) GetPluginHandler() interface{} {
	return nil
}

// GetDBTHandler returns nil (disabled)
func (c *SimpleContainer) GetDBTHandler() interface{} {
	return nil
}

// GetConnectorsHandler returns nil (disabled)
func (c *SimpleContainer) GetConnectorsHandler() interface{} {
	return nil
}

// Shutdown does graceful shutdown (no context needed for simple container)
func (c *SimpleContainer) Shutdown() error {
	c.logger.Info("Simple container shutdown completed")
	return nil
}

// HealthCheck performs basic health checks
func (c *SimpleContainer) HealthCheck(ctx context.Context) error {
	// Basic health check - just verify meltano service is available
	if c.meltanoService != nil {
		available, err := c.meltanoService.IsAvailable(ctx)
		if err != nil {
			return fmt.Errorf("meltano service health check failed: %w", err)
		}
		if !available {
			return fmt.Errorf("meltano service is not available")
		}
	}
	return nil
}