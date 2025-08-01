package flexcore_plugin

import (
	"context"

	"github.com/flext/flexcore/internal/infrastructure/logging"
)

// TestPlugin is a simple test plugin for FLEXCORE
type TestPlugin struct {
	logger logging.Logger
}

// NewTestPlugin creates a new test plugin
func NewTestPlugin(logger logging.Logger) *TestPlugin {
	return &TestPlugin{
		logger: logger,
	}
}

// Execute implements the FLEXCORE plugin interface
func (tp *TestPlugin) Execute(ctx context.Context, params map[string]interface{}) (interface{}, error) {
	tp.logger.Info("🧪 Test plugin executed", logging.F("params", params))
	return map[string]interface{}{
		"status":  "success",
		"message": "Test plugin execution completed",
		"params":  params,
	}, nil
}

// GetPluginInfo returns plugin information
func (tp *TestPlugin) GetPluginInfo() map[string]interface{} {
	return map[string]interface{}{
		"name":        "test",
		"type":        "executor",
		"version":     "1.0.0",
		"description": "Simple test plugin for FLEXCORE",
		"author":      "FLEXT Team",
	}
}

// Validate checks if the plugin is properly configured
func (tp *TestPlugin) Validate() error {
	tp.logger.Info("✅ Test plugin validation successful")
	return nil
}