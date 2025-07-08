// Package entities provides shared domain entities for the FlexT ecosystem
// This eliminates Plugin code duplication across bounded contexts
package entities

import (
	"errors"
	"fmt"
	"time"
)

// UnifiedPluginType represents the type of plugin - SINGLE SOURCE OF TRUTH
type UnifiedPluginType string

const (
	UnifiedPluginTypeSource      UnifiedPluginType = "source"
	UnifiedPluginTypeTarget      UnifiedPluginType = "target"
	UnifiedPluginTypeTransformer UnifiedPluginType = "transformer"
	UnifiedPluginTypeLoader      UnifiedPluginType = "loader"
	UnifiedPluginTypeExtractor   UnifiedPluginType = "extractor"
	UnifiedPluginTypeProcessor   UnifiedPluginType = "processor"
	UnifiedPluginTypeUtility     UnifiedPluginType = "utility"
	UnifiedPluginTypeValidator   UnifiedPluginType = "validator"
)

// UnifiedPluginStatus represents the status of plugin - SINGLE SOURCE OF TRUTH
type UnifiedPluginStatus string

const (
	UnifiedPluginStatusActive     UnifiedPluginStatus = "active"
	UnifiedPluginStatusInactive   UnifiedPluginStatus = "inactive"
	UnifiedPluginStatusRegistered UnifiedPluginStatus = "registered"
	UnifiedPluginStatusFailed     UnifiedPluginStatus = "failed"
	UnifiedPluginStatusLoading    UnifiedPluginStatus = "loading"
	UnifiedPluginStatusUnloaded   UnifiedPluginStatus = "unloaded"
)

// UnifiedPort represents a port exposed by the plugin - ELIMINATING DUPLICATION
type UnifiedPort struct {
	Name        string                 `json:"name"`
	Type        string                 `json:"type"`
	Required    bool                   `json:"required"`
	Description string                 `json:"description"`
	Schema      map[string]interface{} `json:"schema,omitempty"`
	Direction   string                 `json:"direction"` // "input", "output", "bidirectional"
}

// UnifiedPluginMetadata represents plugin metadata - CONSOLIDATED
type UnifiedPluginMetadata struct {
	Repository    string            `json:"repository,omitempty"`
	Documentation string            `json:"documentation,omitempty"`
	License       string            `json:"license,omitempty"`
	Homepage      string            `json:"homepage,omitempty"`
	Keywords      []string          `json:"keywords,omitempty"`
	Categories    []string          `json:"categories,omitempty"`
	Requirements  map[string]string `json:"requirements,omitempty"`
	FailureReason string            `json:"failure_reason,omitempty"`
	LoadedAt      time.Time         `json:"loaded_at,omitempty"`
	Health        string            `json:"health,omitempty"`
}

// UnifiedPlugin represents a plugin entity - SINGLE SOURCE OF TRUTH
// This eliminates the duplication between flexcore and bounded_contexts
type UnifiedPlugin struct {
	BaseAggregateRoot

	// Core plugin data
	Name          string                 `json:"name"`
	Type          UnifiedPluginType      `json:"type"`
	Version       string                 `json:"version"`
	Description   string                 `json:"description"`
	Author        string                 `json:"author"`
	Status        UnifiedPluginStatus    `json:"status"`
	EntryPoint    string                 `json:"entry_point"`
	Ports         []UnifiedPort          `json:"ports"`
	Dependencies  []string               `json:"dependencies"`
	Configuration map[string]interface{} `json:"configuration"`
	Capabilities  []string               `json:"capabilities"`
	Tags          []string               `json:"tags"`
	Metadata      UnifiedPluginMetadata  `json:"metadata"`
	IsActive      bool                   `json:"is_active"`
}

// NewUnifiedPlugin creates a new plugin - ELIMINATING CONSTRUCTOR DUPLICATION
func NewUnifiedPlugin(name, version, entryPoint string, pluginType UnifiedPluginType) (*UnifiedPlugin, error) {
	if name == "" {
		return nil, errors.New("plugin name cannot be empty")
	}
	if version == "" {
		return nil, errors.New("plugin version cannot be empty")
	}
	if entryPoint == "" {
		return nil, errors.New("plugin entry point cannot be empty")
	}
	if !isValidUnifiedPluginType(pluginType) {
		return nil, fmt.Errorf("invalid plugin type: %s", pluginType)
	}

	plugin := &UnifiedPlugin{
		BaseAggregateRoot: *NewBaseAggregateRoot("plugin"),
		Name:              name,
		Type:              pluginType,
		Version:           version,
		EntryPoint:        entryPoint,
		Status:            UnifiedPluginStatusRegistered,
		Ports:             make([]UnifiedPort, 0),
		Dependencies:      make([]string, 0),
		Configuration:     make(map[string]interface{}),
		Capabilities:      make([]string, 0),
		Tags:              make([]string, 0),
		Metadata: UnifiedPluginMetadata{
			LoadedAt: time.Now(),
			Health:   "unknown",
		},
		IsActive: false,
	}

	// Add domain event
	plugin.AddDomainEvent(NewBaseDomainEvent("plugin.registered", plugin.GetID(), map[string]interface{}{
		"name":    name,
		"type":    string(pluginType),
		"version": version,
	}, plugin.GetVersion()))

	return plugin, nil
}

// AddPort adds a port to the plugin - UNIFIED IMPLEMENTATION
func (p *UnifiedPlugin) AddPort(port UnifiedPort) error {
	if port.Name == "" {
		return errors.New("port name cannot be empty")
	}
	if port.Type == "" {
		return errors.New("port type cannot be empty")
	}

	// Check if port already exists
	for _, existingPort := range p.Ports {
		if existingPort.Name == port.Name {
			return fmt.Errorf("port %s already exists", port.Name)
		}
	}

	p.Ports = append(p.Ports, port)
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("port.added", p.GetID(), map[string]interface{}{
		"port_name": port.Name,
		"port_type": port.Type,
	}, p.GetVersion()))

	return nil
}

// RemovePort removes a port from the plugin
func (p *UnifiedPlugin) RemovePort(portName string) error {
	for i, port := range p.Ports {
		if port.Name == portName {
			p.Ports = append(p.Ports[:i], p.Ports[i+1:]...)
			p.IncrementVersion()
			p.AddDomainEvent(NewBaseDomainEvent("port.removed", p.GetID(), map[string]interface{}{
				"port_name": portName,
			}, p.GetVersion()))
			return nil
		}
	}
	return fmt.Errorf("port %s not found", portName)
}

// Activate activates the plugin - UNIFIED BUSINESS LOGIC
func (p *UnifiedPlugin) Activate() error {
	if p.Status == UnifiedPluginStatusActive {
		return errors.New("plugin is already active")
	}
	if p.Status == UnifiedPluginStatusFailed {
		return errors.New("cannot activate failed plugin")
	}

	p.Status = UnifiedPluginStatusActive
	p.IsActive = true
	p.Metadata.Health = "healthy"
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.activated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))

	return nil
}

// Deactivate deactivates the plugin
func (p *UnifiedPlugin) Deactivate() {
	if p.Status == UnifiedPluginStatusInactive {
		return
	}

	p.Status = UnifiedPluginStatusInactive
	p.IsActive = false
	p.Metadata.Health = "inactive"
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.deactivated", p.GetID(), map[string]interface{}{
		"name": p.Name,
	}, p.GetVersion()))
}

// MarkAsFailed marks the plugin as failed
func (p *UnifiedPlugin) MarkAsFailed(reason string) {
	p.Status = UnifiedPluginStatusFailed
	p.IsActive = false
	p.Metadata.FailureReason = reason
	p.Metadata.Health = "failed"
	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.failed", p.GetID(), map[string]interface{}{
		"name":   p.Name,
		"reason": reason,
	}, p.GetVersion()))
}

// UpdateConfiguration updates the plugin configuration
func (p *UnifiedPlugin) UpdateConfiguration(config map[string]interface{}) {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}

	for k, v := range config {
		p.Configuration[k] = v
	}

	p.IncrementVersion()
	p.AddDomainEvent(NewBaseDomainEvent("plugin.configuration.updated", p.GetID(), map[string]interface{}{
		"configuration": config,
	}, p.GetVersion()))
}

// AddDependency adds a dependency to the plugin
func (p *UnifiedPlugin) AddDependency(dependency string) {
	if dependency == "" {
		return
	}

	// Check if dependency already exists
	for _, dep := range p.Dependencies {
		if dep == dependency {
			return
		}
	}

	p.Dependencies = append(p.Dependencies, dependency)
	p.IncrementVersion()
}

// RemoveDependency removes a dependency from the plugin
func (p *UnifiedPlugin) RemoveDependency(dependency string) {
	for i, dep := range p.Dependencies {
		if dep == dependency {
			p.Dependencies = append(p.Dependencies[:i], p.Dependencies[i+1:]...)
			p.IncrementVersion()
			break
		}
	}
}

// AddCapability adds a capability to the plugin
func (p *UnifiedPlugin) AddCapability(capability string) {
	if capability == "" {
		return
	}

	// Check if capability already exists
	for _, cap := range p.Capabilities {
		if cap == capability {
			return
		}
	}

	p.Capabilities = append(p.Capabilities, capability)
	p.IncrementVersion()
}

// AddTag adds a tag to the plugin
func (p *UnifiedPlugin) AddTag(tag string) {
	if tag == "" {
		return
	}

	// Check if tag already exists
	for _, existingTag := range p.Tags {
		if existingTag == tag {
			return
		}
	}

	p.Tags = append(p.Tags, tag)
	p.IncrementVersion()
}

// RemoveTag removes a tag from the plugin
func (p *UnifiedPlugin) RemoveTag(tag string) {
	for i, existingTag := range p.Tags {
		if existingTag == tag {
			p.Tags = append(p.Tags[:i], p.Tags[i+1:]...)
			p.IncrementVersion()
			break
		}
	}
}

// GetPortByName returns a port by name
func (p *UnifiedPlugin) GetPortByName(name string) (*UnifiedPort, error) {
	for _, port := range p.Ports {
		if port.Name == name {
			return &port, nil
		}
	}
	return nil, fmt.Errorf("port %s not found", name)
}

// GetInputPorts returns all input ports
func (p *UnifiedPlugin) GetInputPorts() []UnifiedPort {
	var inputPorts []UnifiedPort
	for _, port := range p.Ports {
		if port.Direction == "input" || port.Direction == "bidirectional" {
			inputPorts = append(inputPorts, port)
		}
	}
	return inputPorts
}

// GetOutputPorts returns all output ports
func (p *UnifiedPlugin) GetOutputPorts() []UnifiedPort {
	var outputPorts []UnifiedPort
	for _, port := range p.Ports {
		if port.Direction == "output" || port.Direction == "bidirectional" {
			outputPorts = append(outputPorts, port)
		}
	}
	return outputPorts
}

// CanExecute checks if plugin can execute
func (p *UnifiedPlugin) CanExecute() error {
	if p.Status != UnifiedPluginStatusActive {
		return errors.New("plugin is not active")
	}
	if p.Metadata.Health == "failed" {
		return errors.New("plugin health check failed")
	}
	return nil
}

// HasCapability checks if the plugin has a specific capability
func (p *UnifiedPlugin) HasCapability(capability string) bool {
	for _, cap := range p.Capabilities {
		if cap == capability {
			return true
		}
	}
	return false
}

// HasTag checks if the plugin has a specific tag
func (p *UnifiedPlugin) HasTag(tag string) bool {
	for _, t := range p.Tags {
		if t == tag {
			return true
		}
	}
	return false
}

// HasDependency checks if the plugin has a specific dependency
func (p *UnifiedPlugin) HasDependency(dependency string) bool {
	for _, dep := range p.Dependencies {
		if dep == dependency {
			return true
		}
	}
	return false
}

// IsCompatibleWith checks if this plugin is compatible with another plugin
func (p *UnifiedPlugin) IsCompatibleWith(other *UnifiedPlugin) bool {
	// Basic compatibility check - can be extended
	return p.Type != other.Type // Different types can work together
}

// Validate validates the plugin
func (p *UnifiedPlugin) Validate() error {
	if p.Name == "" {
		return errors.New("name is required")
	}

	if p.Version == "" {
		return errors.New("version is required")
	}

	if p.EntryPoint == "" {
		return errors.New("entry point is required")
	}

	if !isValidUnifiedPluginType(p.Type) {
		return fmt.Errorf("invalid plugin type: %s", p.Type)
	}

	// Validate ports
	portNames := make(map[string]bool)
	for _, port := range p.Ports {
		if port.Name == "" {
			return errors.New("port name cannot be empty")
		}
		if portNames[port.Name] {
			return fmt.Errorf("duplicate port name: %s", port.Name)
		}
		portNames[port.Name] = true
	}

	return nil
}

// Helper functions

func isValidUnifiedPluginType(pluginType UnifiedPluginType) bool {
	switch pluginType {
	case UnifiedPluginTypeSource, UnifiedPluginTypeTarget, UnifiedPluginTypeTransformer,
		UnifiedPluginTypeLoader, UnifiedPluginTypeExtractor, UnifiedPluginTypeProcessor,
		UnifiedPluginTypeUtility, UnifiedPluginTypeValidator:
		return true
	default:
		return false
	}
}

// GetPluginTypeCategory returns the category of the plugin type
func GetPluginTypeCategory(pluginType UnifiedPluginType) string {
	switch pluginType {
	case UnifiedPluginTypeSource, UnifiedPluginTypeExtractor:
		return "input"
	case UnifiedPluginTypeTarget, UnifiedPluginTypeLoader:
		return "output"
	case UnifiedPluginTypeTransformer, UnifiedPluginTypeProcessor:
		return "processing"
	case UnifiedPluginTypeUtility, UnifiedPluginTypeValidator:
		return "utility"
	default:
		return "unknown"
	}
}
