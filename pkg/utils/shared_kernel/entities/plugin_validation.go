package entities

import (
	"errors"
	"fmt"
)

// Validate validates the plugin
func (p *UnifiedPlugin) Validate() error {
	var err error
	portNames := make(map[string]bool)

	switch {
	case p.Name == "":
		err = errors.New("name is required")
	case p.Version == "":
		err = errors.New("version is required")
	case p.EntryPoint == "":
		err = errors.New("entry point is required")
	case !isValidUnifiedPluginType(p.Type):
		err = fmt.Errorf("invalid plugin type: %s", p.Type)
	default:
		for _, port := range p.Ports {
			switch {
			case port.Name == "":
				err = errors.New("port name cannot be empty")
			case portNames[port.Name]:
				err = fmt.Errorf("duplicate port name: %s", port.Name)
			default:
				portNames[port.Name] = true
			}
			if err != nil {
				break
			}
		}
	}

	return err
}

func isValidUnifiedPluginType(pluginType UnifiedPluginType) bool {
	valid := false
	switch pluginType {
	case UnifiedPluginTypeSource, UnifiedPluginTypeTarget, UnifiedPluginTypeTransformer,
		UnifiedPluginTypeLoader, UnifiedPluginTypeExtractor, UnifiedPluginTypeProcessor,
		UnifiedPluginTypeUtility, UnifiedPluginTypeValidator:
		valid = true
	}
	return valid
}

// GetPluginTypeCategory returns the category of the plugin type
func GetPluginTypeCategory(pluginType UnifiedPluginType) string {
	category := "unknown"
	switch pluginType {
	case UnifiedPluginTypeSource, UnifiedPluginTypeExtractor:
		category = "input"
	case UnifiedPluginTypeTarget, UnifiedPluginTypeLoader:
		category = "output"
	case UnifiedPluginTypeTransformer, UnifiedPluginTypeProcessor:
		category = "processing"
	case UnifiedPluginTypeUtility, UnifiedPluginTypeValidator:
		category = "utility"
	}
	return category
}
