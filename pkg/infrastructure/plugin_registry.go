package flexcore_plugin

import (
	"context"
	"fmt"
	"sync"

	"github.com/flext-sh/flext/pkg/infrastructure/config"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// FlexcorePlugin represents a plugin that can be executed by FLEXCORE
type FlexcorePlugin interface {
	Execute(ctx context.Context, params map[string]interface{}) (interface{}, error)
	GetPluginInfo() map[string]interface{}
	Validate() error
}

// PluginRegistry manages FLEXT plugins for FLEXCORE integration
type PluginRegistry struct {
	plugins map[string]FlexcorePlugin
	mutex   sync.RWMutex
	config  *config.Config
	logger  logging.Logger
}

// NewPluginRegistry creates a new plugin registry for FLEXCORE
func NewPluginRegistry(cfg *config.Config, logger logging.Logger) *PluginRegistry {
	fmt.Println("🏗️ DIRECT: Creating PluginRegistry")
	
	registry := &PluginRegistry{
		plugins: make(map[string]FlexcorePlugin),
		config:  cfg,
		logger:  logger,
	}

	fmt.Println("🏗️ DIRECT: About to register core plugins...")
	// Auto-register core FLEXT plugins
	registry.registerCorePlugins()
	
	fmt.Printf("🏗️ DIRECT: PluginRegistry created with %d plugins\n", len(registry.plugins))
	return registry
}

// registerCorePlugins registers the core FLEXT plugins
func (pr *PluginRegistry) registerCorePlugins() {
	// FORCE logging - bypass potential logger issues
	fmt.Println("🔌 DIRECT: Registering FLEXCORE plugins")

	// Skip test plugin - focus on Meltano
	fmt.Println("🔧 DIRECT: Creating Meltano plugin...")
	
	// Get Python path directly
	pythonPath := pr.config.GetEnvWithDefault("PYTHON_PATH", "/home/marlonsc/flext/.venv/bin/python3")
	fmt.Printf("🔧 DIRECT: Python path: %s\n", pythonPath)
	
	meltanoPlugin := NewMeltanoPlugin(pr.config, pr.logger)
	if meltanoPlugin == nil {
		fmt.Println("❌ DIRECT: Meltano plugin is nil!")
		return
	}
	
	fmt.Println("✅ DIRECT: Meltano plugin created, registering...")
	if err := pr.RegisterPlugin("meltano", meltanoPlugin); err != nil {
		fmt.Printf("❌ DIRECT: Registration failed: %v\n", err)
	} else {
		fmt.Println("✅ DIRECT: Meltano plugin registered!")
	}

	fmt.Printf("🎯 DIRECT: Total plugins: %d\n", len(pr.plugins))
}

// RegisterPlugin registers a new plugin in the registry
func (pr *PluginRegistry) RegisterPlugin(name string, plugin FlexcorePlugin) error {
	pr.mutex.Lock()
	defer pr.mutex.Unlock()

	// Validate plugin before registration
	if err := plugin.Validate(); err != nil {
		return fmt.Errorf("plugin validation failed for %s: %w", name, err)
	}

	pr.plugins[name] = plugin
	
	pluginInfo := plugin.GetPluginInfo()
	pr.logger.Info("✅ Plugin registered successfully",
		logging.F("name", name),
		logging.F("type", pluginInfo["type"]),
		logging.F("version", pluginInfo["version"]),
		logging.F("description", pluginInfo["description"]))

	return nil
}

// GetPlugin retrieves a plugin by name
func (pr *PluginRegistry) GetPlugin(name string) (FlexcorePlugin, error) {
	pr.mutex.RLock()
	defer pr.mutex.RUnlock()

	plugin, exists := pr.plugins[name]
	if !exists {
		return nil, fmt.Errorf("plugin not found: %s", name)
	}

	return plugin, nil
}

// ExecutePlugin executes a plugin with given parameters
func (pr *PluginRegistry) ExecutePlugin(ctx context.Context, name string, params map[string]interface{}) (interface{}, error) {
	plugin, err := pr.GetPlugin(name)
	if err != nil {
		return nil, err
	}

	pr.logger.Info("🚀 Executing FLEXCORE plugin",
		logging.F("plugin", name),
		logging.F("params", params))

	result, err := plugin.Execute(ctx, params)
	if err != nil {
		pr.logger.Error("❌ Plugin execution failed",
			logging.F("plugin", name),
			logging.F("error", err))
		return nil, fmt.Errorf("plugin execution failed: %w", err)
	}

	pr.logger.Info("✅ Plugin execution completed successfully",
		logging.F("plugin", name))

	return result, nil
}

// ListPlugins returns information about all registered plugins
func (pr *PluginRegistry) ListPlugins() map[string]interface{} {
	pr.mutex.RLock()
	defer pr.mutex.RUnlock()

	pluginsList := make(map[string]interface{})
	
	for name, plugin := range pr.plugins {
		pluginsList[name] = plugin.GetPluginInfo()
	}

	return pluginsList
}

// UnregisterPlugin removes a plugin from the registry
func (pr *PluginRegistry) UnregisterPlugin(name string) error {
	pr.mutex.Lock()
	defer pr.mutex.Unlock()

	if _, exists := pr.plugins[name]; !exists {
		return fmt.Errorf("plugin not found: %s", name)
	}

	delete(pr.plugins, name)
	
	pr.logger.Info("🗑️ Plugin unregistered successfully", logging.F("name", name))
	
	return nil
}

// ValidateAllPlugins validates all registered plugins
func (pr *PluginRegistry) ValidateAllPlugins() error {
	pr.mutex.RLock()
	defer pr.mutex.RUnlock()

	var failures []string
	
	for name, plugin := range pr.plugins {
		if err := plugin.Validate(); err != nil {
			failures = append(failures, fmt.Sprintf("%s: %v", name, err))
			pr.logger.Error("❌ Plugin validation failed",
				logging.F("plugin", name),
				logging.F("error", err))
		} else {
			pr.logger.Info("✅ Plugin validation successful", logging.F("plugin", name))
		}
	}

	if len(failures) > 0 {
		return fmt.Errorf("plugin validation failures: %v", failures)
	}

	pr.logger.Info("✅ All plugins validated successfully",
		logging.F("total_plugins", len(pr.plugins)))

	return nil
}

// GetPluginCount returns the number of registered plugins
func (pr *PluginRegistry) GetPluginCount() int {
	pr.mutex.RLock()
	defer pr.mutex.RUnlock()
	return len(pr.plugins)
}

// Shutdown gracefully shuts down all plugins
func (pr *PluginRegistry) Shutdown() error {
	pr.mutex.Lock()
	defer pr.mutex.Unlock()

	pr.logger.Info("🛑 Shutting down plugin registry")

	// Clear all plugins
	pr.plugins = make(map[string]FlexcorePlugin)

	pr.logger.Info("✅ Plugin registry shutdown completed")
	
	return nil
}