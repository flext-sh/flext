package registry

import (
	"fmt"
	"strings"

	"github.com/flext-sh/flext/pkg/plugins"
)

func (pr *PluginRegistry) validatePluginMetadata(metadata plugins.PluginMetadata) error {
	if metadata.ID == "" {
		return fmt.Errorf("plugin ID is required")
	}
	if metadata.Name == "" {
		return fmt.Errorf("plugin name is required")
	}
	if metadata.Version == "" {
		return fmt.Errorf("plugin version is required")
	}
	if metadata.Type == "" {
		return fmt.Errorf("plugin type is required")
	}
	return nil
}

func (pr *PluginRegistry) createPluginInstance(metadata plugins.PluginMetadata) (plugins.Plugin, error) {
	switch metadata.Type {
	case plugins.PluginTypeMeltano:
		return nil, fmt.Errorf("plugin instance creation not implemented for %s", metadata.Type)
	case plugins.PluginTypeRay:
		return nil, fmt.Errorf("plugin instance creation not implemented for %s", metadata.Type)
	case plugins.PluginTypeKubernetes:
		return nil, fmt.Errorf("plugin instance creation not implemented for %s", metadata.Type)
	default:
		return nil, fmt.Errorf("unknown plugin type: %s", metadata.Type)
	}
}

func (pr *PluginRegistry) matchesQuery(metadata plugins.PluginMetadata, query string) bool {
	queryLower := strings.ToLower(query)
	matches := strings.Contains(strings.ToLower(metadata.Name), queryLower) ||
		strings.Contains(strings.ToLower(metadata.Description), queryLower) ||
		strings.Contains(strings.ToLower(string(metadata.Type)), queryLower)

	for _, capability := range metadata.Capabilities {
		if matches {
			break
		}
		matches = strings.Contains(strings.ToLower(capability), queryLower)
	}

	return matches
}
