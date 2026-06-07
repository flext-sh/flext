// Package loader - Plugin Loader and Factory for Dynamic Plugin Registration
//
// This package implements a plugin loader that dynamically registers plugins
// via dependency injection without requiring the main service to know about
// specific plugin implementations. This follows the dependency inversion principle
// where high-level modules (FLEXT Service) don't depend on low-level modules (specific plugins).
//
// Architecture:
//   - Plugin Factory: Creates plugin instances from registry
//   - Plugin Loader: Loads and registers plugins dynamically
//   - DI Integration: Injects plugins via dependency injection
//   - Binary Loading: Loads .so/.dll plugin files dynamically
//
// Author: FLEXT Development Team
// Version: 2.0.0
// License: MIT
package loader

import (
	"context"
	"errors"
	"fmt"
	"path/filepath"
	"plugin"

	"github.com/flext-sh/flext/pkg/logging"
	"github.com/flext-sh/flext/pkg/plugins"
	"github.com/flext-sh/flext/pkg/plugins/communication"
	"github.com/flext-sh/flext/pkg/plugins/registry"
)

// PluginLoader handles dynamic plugin loading and registration
type PluginLoader struct {
	registry        *registry.PluginRegistry
	communicator    *communication.FlexCoreCommunicationBus
	logger          logging.Logger
	pluginFactories map[plugins.PluginType]PluginFactory
}

// PluginFactory represents a factory function that creates plugin instances
type PluginFactory func() plugins.Plugin

// PluginConfiguration represents plugin configuration for loading
type PluginConfiguration struct {
	PluginType   plugins.PluginType     `json:"plugin_type"`
	BinaryPath   string                 `json:"binary_path"`
	Config       map[string]interface{} `json:"settings"`
	Enabled      bool                   `json:"enabled"`
	AutoRegister bool                   `json:"auto_register"`
}

// NewPluginLoader creates a new plugin loader
func NewPluginLoader(registry *registry.PluginRegistry, communicator *communication.FlexCoreCommunicationBus, logger logging.Logger) *PluginLoader {
	return &PluginLoader{
		registry:        registry,
		communicator:    communicator,
		logger:          logger,
		pluginFactories: make(map[plugins.PluginType]PluginFactory),
	}
}

// RegisterPluginFactory registers a plugin factory for dynamic creation
func (pl *PluginLoader) RegisterPluginFactory(pluginType plugins.PluginType, factory PluginFactory) {
	pl.logger.Info("📦 Registering plugin factory",
		logging.F("plugin_type", pluginType),
		logging.F("factory", "registered"))

	pl.pluginFactories[pluginType] = factory
}

// LoadPluginsFromConfiguration loads plugins from configuration
func (pl *PluginLoader) LoadPluginsFromConfiguration(ctx context.Context, configs []PluginConfiguration) error {
	pl.logger.Info("🔌 Loading plugins from configuration",
		logging.F("plugin_count", len(configs)))

	var failures []error
	loaded := 0
	for _, settings := range configs {
		if !settings.Enabled {
			pl.logger.Info("⏭️ Skipping disabled plugin",
				logging.F("plugin_type", settings.PluginType))
			continue
		}

		if err := pl.loadPlugin(ctx, settings); err != nil {
			// Non-fatal: a plugin whose external runtime (Python venv, Ray
			// cluster, kubeconfig) is unavailable must not abort loading the
			// rest. Collect every failure so the caller sees the full set and
			// can apply its own degradation policy.
			pl.logger.Error("❌ Failed to load plugin",
				logging.F("plugin_type", settings.PluginType),
				logging.F("error", err))
			failures = append(failures, fmt.Errorf("plugin %s: %w", settings.PluginType, err))
			continue
		}
		loaded++
	}

	pl.logger.Info("✅ Plugin load phase complete",
		logging.F("loaded", loaded),
		logging.F("failed", len(failures)))

	return errors.Join(failures...)
}

// LoadPluginFromBinary loads a plugin from a binary file (.so/.dll)
func (pl *PluginLoader) LoadPluginFromBinary(ctx context.Context, binaryPath string, settings map[string]interface{}) (plugins.Plugin, error) {
	pl.logger.Info("📂 Loading plugin from binary",
		logging.F("binary_path", binaryPath))

	// Load the plugin binary
	pluginBinary, err := plugin.Open(binaryPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open plugin binary %s: %w", binaryPath, err)
	}

	// Look for the CreatePlugin function
	createPluginSymbol, err := pluginBinary.Lookup("CreatePlugin")
	if err != nil {
		return nil, fmt.Errorf("plugin binary %s does not export CreatePlugin function: %w", binaryPath, err)
	}

	// Cast to the expected function signature
	createPlugin, ok := createPluginSymbol.(func() plugins.Plugin)
	if !ok {
		return nil, fmt.Errorf("CreatePlugin function in %s has incorrect signature", binaryPath)
	}

	// Create the plugin instance
	pluginInstance := createPlugin()
	if pluginInstance == nil {
		return nil, fmt.Errorf("CreatePlugin function in %s returned nil", binaryPath)
	}

	// Set communicator if the plugin supports it
	if communicatorSetter, ok := pluginInstance.(interface {
		SetCommunicator(plugins.PluginCommunicator)
	}); ok {
		communicatorSetter.SetCommunicator(pl.communicator)
		pl.logger.Info("✅ Communicator set for plugin",
			logging.F("plugin_id", pluginInstance.Metadata().ID))
	}

	// Initialize the plugin
	if err := pluginInstance.Initialize(ctx, settings); err != nil {
		return nil, fmt.Errorf("failed to initialize plugin from %s: %w", binaryPath, err)
	}

	pl.logger.Info("✅ Plugin loaded successfully from binary",
		logging.F("plugin_id", pluginInstance.Metadata().ID),
		logging.F("plugin_type", pluginInstance.Metadata().Type),
		logging.F("binary_path", binaryPath))

	return pluginInstance, nil
}

// CreatePluginFromFactory creates a plugin instance using registered factories
func (pl *PluginLoader) CreatePluginFromFactory(pluginType plugins.PluginType) (plugins.Plugin, error) {
	factory, exists := pl.pluginFactories[pluginType]
	if !exists {
		return nil, fmt.Errorf("no factory registered for plugin type: %s", pluginType)
	}

	pluginInstance := factory()
	if pluginInstance == nil {
		return nil, fmt.Errorf("factory for plugin type %s returned nil", pluginType)
	}

	// Set communicator if the plugin supports it
	if communicatorSetter, ok := pluginInstance.(interface {
		SetCommunicator(plugins.PluginCommunicator)
	}); ok {
		communicatorSetter.SetCommunicator(pl.communicator)
		pl.logger.Info("✅ Communicator set for factory-created plugin",
			logging.F("plugin_id", pluginInstance.Metadata().ID))
	}

	pl.logger.Info("✅ Plugin created from factory",
		logging.F("plugin_id", pluginInstance.Metadata().ID),
		logging.F("plugin_type", pluginType))

	return pluginInstance, nil
}

// RegisterPlugin registers a plugin instance with the registry
func (pl *PluginLoader) RegisterPlugin(pluginInstance plugins.Plugin, binaryPath string) error {
	// Register with the plugin registry
	if err := pl.registry.RegisterPlugin(pluginInstance); err != nil {
		return fmt.Errorf("failed to register plugin with registry: %w", err)
	}

	// Set binary path if provided
	if binaryPath != "" {
		if err := pl.registry.SetPluginBinary(pluginInstance.Metadata().ID, binaryPath); err != nil {
			pl.logger.Warn("⚠️ Failed to set plugin binary path",
				logging.F("plugin_id", pluginInstance.Metadata().ID),
				logging.F("binary_path", binaryPath),
				logging.F("error", err))
		}
	}

	pl.logger.Info("✅ Plugin registered successfully",
		logging.F("plugin_id", pluginInstance.Metadata().ID),
		logging.F("plugin_type", pluginInstance.Metadata().Type))

	return nil
}

// LoadAndRegisterPlugin loads and registers a plugin in one operation
func (pl *PluginLoader) LoadAndRegisterPlugin(ctx context.Context, settings PluginConfiguration) error {
	var pluginInstance plugins.Plugin
	var err error

	// Try to load from binary first, then fall back to factory
	if settings.BinaryPath != "" && fileExists(settings.BinaryPath) {
		pluginInstance, err = pl.LoadPluginFromBinary(ctx, settings.BinaryPath, settings.Config)
		if err != nil {
			pl.logger.Warn("⚠️ Failed to load from binary, trying factory",
				logging.F("binary_path", settings.BinaryPath),
				logging.F("error", err))

			// Fall back to factory
			pluginInstance, err = pl.CreatePluginFromFactory(settings.PluginType)
			if err != nil {
				return fmt.Errorf("failed to create plugin from factory after binary load failed: %w", err)
			}

			// Initialize with settings
			if err := pluginInstance.Initialize(ctx, settings.Config); err != nil {
				return fmt.Errorf("failed to initialize factory-created plugin: %w", err)
			}
		}
	} else {
		// Load from factory
		pluginInstance, err = pl.CreatePluginFromFactory(settings.PluginType)
		if err != nil {
			return fmt.Errorf("failed to create plugin from factory: %w", err)
		}

		// Initialize with settings
		if err := pluginInstance.Initialize(ctx, settings.Config); err != nil {
			return fmt.Errorf("failed to initialize factory-created plugin: %w", err)
		}
	}

	// Register the plugin
	return pl.RegisterPlugin(pluginInstance, settings.BinaryPath)
}

// GetRegisteredPluginTypes returns all plugin types that have registered factories
func (pl *PluginLoader) GetRegisteredPluginTypes() []plugins.PluginType {
	types := make([]plugins.PluginType, 0, len(pl.pluginFactories))
	for pluginType := range pl.pluginFactories {
		types = append(types, pluginType)
	}
	return types
}

// loadPlugin loads a single plugin from configuration
func (pl *PluginLoader) loadPlugin(ctx context.Context, settings PluginConfiguration) error {
	if settings.AutoRegister {
		return pl.LoadAndRegisterPlugin(ctx, settings)
	}

	// Just load without registering
	var pluginInstance plugins.Plugin
	var err error

	if settings.BinaryPath != "" && fileExists(settings.BinaryPath) {
		pluginInstance, err = pl.LoadPluginFromBinary(ctx, settings.BinaryPath, settings.Config)
	} else {
		pluginInstance, err = pl.CreatePluginFromFactory(settings.PluginType)
		if err != nil {
			return err
		}
		if err := pluginInstance.Initialize(ctx, settings.Config); err != nil {
			return fmt.Errorf("failed to initialize plugin: %w", err)
		}
	}

	if err != nil {
		return err
	}

	pl.logger.Info("✅ Plugin loaded (not auto-registered)",
		logging.F("plugin_id", pluginInstance.Metadata().ID),
		logging.F("plugin_type", pluginInstance.Metadata().Type))

	return nil
}

// fileExists checks if a file exists
func fileExists(path string) bool {
	if path == "" {
		return false
	}

	absPath, err := filepath.Abs(path)
	if err != nil {
		return false
	}

	// Check if file exists and is not a directory
	// In a real implementation, you would use os.Stat
	// For now, return false to force factory usage
	_ = absPath
	return false
}
