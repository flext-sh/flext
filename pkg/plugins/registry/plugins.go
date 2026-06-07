package registry

import (
	"fmt"

	"github.com/flext-sh/flext/pkg/plugins"
)

// RegisterPlugin registers a new plugin in the registry
func (pr *PluginRegistry) RegisterPlugin(plugin plugins.Plugin) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	metadata := plugin.Metadata()
	if err := pr.validatePluginMetadata(metadata); err != nil {
		return fmt.Errorf("plugin metadata validation failed: %w", err)
	}
	if _, exists := pr.plugins[metadata.ID]; exists {
		return fmt.Errorf("plugin with ID %s already exists", metadata.ID)
	}

	pr.plugins[metadata.ID] = metadata
	pr.deployments[metadata.ID] = make([]plugins.PluginDeployment, 0)

	return nil
}

// UnregisterPlugin removes a plugin from the registry
func (pr *PluginRegistry) UnregisterPlugin(pluginID plugins.PluginID) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	if _, exists := pr.plugins[pluginID]; !exists {
		return fmt.Errorf("plugin with ID %s not found", pluginID)
	}
	if deployments, exists := pr.deployments[pluginID]; exists && len(deployments) > 0 {
		return fmt.Errorf("cannot unregister plugin %s: still deployed on %d nodes", pluginID, len(deployments))
	}

	delete(pr.plugins, pluginID)
	delete(pr.deployments, pluginID)
	delete(pr.pluginBinaries, pluginID)

	return nil
}

// GetPlugin retrieves a plugin by ID
func (pr *PluginRegistry) GetPlugin(pluginID plugins.PluginID) (plugins.Plugin, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	metadata, exists := pr.plugins[pluginID]
	if !exists {
		return nil, fmt.Errorf("plugin with ID %s not found", pluginID)
	}

	return pr.createPluginInstance(metadata)
}

// ListPlugins returns all registered plugins
func (pr *PluginRegistry) ListPlugins() ([]plugins.PluginMetadata, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0, len(pr.plugins))
	for _, metadata := range pr.plugins {
		result = append(result, metadata)
	}

	return result, nil
}

// ListPluginsByType returns plugins of specific type
func (pr *PluginRegistry) ListPluginsByType(pluginType plugins.PluginType) ([]plugins.PluginMetadata, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0)
	for _, metadata := range pr.plugins {
		if metadata.Type == pluginType {
			result = append(result, metadata)
		}
	}

	return result, nil
}

// FindPluginsByCapability finds plugins with specific capability
func (pr *PluginRegistry) FindPluginsByCapability(capability string) ([]plugins.PluginMetadata, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0)
	for _, metadata := range pr.plugins {
		for _, cap := range metadata.Capabilities {
			if cap == capability {
				result = append(result, metadata)
				break
			}
		}
	}

	return result, nil
}

// SearchPlugins searches plugins by name, type, or capability
func (pr *PluginRegistry) SearchPlugins(query string) []plugins.PluginMetadata {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0)
	for _, metadata := range pr.plugins {
		if pr.matchesQuery(metadata, query) {
			result = append(result, metadata)
		}
	}

	return result
}

// SetPluginBinary associates a plugin with its binary file path
func (pr *PluginRegistry) SetPluginBinary(pluginID plugins.PluginID, binaryPath string) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	if _, exists := pr.plugins[pluginID]; !exists {
		return fmt.Errorf("plugin with ID %s not found", pluginID)
	}

	pr.pluginBinaries[pluginID] = binaryPath
	return nil
}

// GetPluginBinary returns the binary path for a plugin
func (pr *PluginRegistry) GetPluginBinary(pluginID plugins.PluginID) (string, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	binaryPath, exists := pr.pluginBinaries[pluginID]
	if !exists {
		return "", fmt.Errorf("binary path not found for plugin %s", pluginID)
	}

	return binaryPath, nil
}
