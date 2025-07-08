package plugin

import (
	"errors"
	"github.com/google/uuid"
)

// PluginType represents the type of plugin
type PluginType string

const (
	PluginTypeSource       PluginType = "source"
	PluginTypeDestination  PluginType = "destination"
	PluginTypeTransform    PluginType = "transform"
	PluginTypeOrchestrator PluginType = "orchestrator"
)

// PluginStatus represents the status of a plugin
type PluginStatus string

const (
	PluginStatusRegistered PluginStatus = "registered"
	PluginStatusActive     PluginStatus = "active"
	PluginStatusInactive   PluginStatus = "inactive"
	PluginStatusError      PluginStatus = "error"
)

// Business errors
var (
	ErrEmptyName       = errors.New("plugin name cannot be empty")
	ErrInvalidType     = errors.New("invalid plugin type")
	ErrInvalidVersion  = errors.New("invalid plugin version")
	ErrAlreadyActive   = errors.New("plugin is already active")
	ErrAlreadyInactive = errors.New("plugin is already inactive")
	ErrCannotActivate  = errors.New("plugin cannot be activated in current state")
)

// Plugin represents a plugin entity
type Plugin struct {
	id           uuid.UUID
	name         string
	pluginType   PluginType
	version      string
	status       PluginStatus
	capabilities []string
	config       Configuration
}

// NewPlugin creates a new plugin
func NewPlugin(name string, pluginType PluginType, version string) (*Plugin, error) {
	if err := validateName(name); err != nil {
		return nil, err
	}

	if err := validateType(pluginType); err != nil {
		return nil, err
	}

	if err := validateVersion(version); err != nil {
		return nil, err
	}

	return &Plugin{
		id:           uuid.New(),
		name:         name,
		pluginType:   pluginType,
		version:      version,
		status:       PluginStatusRegistered,
		capabilities: make([]string, 0),
		config:       NewConfiguration(),
	}, nil
}

// RestorePlugin recreates a plugin from persistence
func RestorePlugin(
	id uuid.UUID,
	name string,
	pluginType PluginType,
	version string,
	status PluginStatus,
	capabilities []string,
	config Configuration,
) *Plugin {
	return &Plugin{
		id:           id,
		name:         name,
		pluginType:   pluginType,
		version:      version,
		status:       status,
		capabilities: capabilities,
		config:       config,
	}
}

// Business Methods

// Activate activates the plugin
func (p *Plugin) Activate() error {
	if p.status == PluginStatusActive {
		return ErrAlreadyActive
	}

	if p.status == PluginStatusError {
		return ErrCannotActivate
	}

	p.status = PluginStatusActive
	return nil
}

// Deactivate deactivates the plugin
func (p *Plugin) Deactivate() error {
	if p.status == PluginStatusInactive {
		return ErrAlreadyInactive
	}

	p.status = PluginStatusInactive
	return nil
}

// SetError sets the plugin to error state
func (p *Plugin) SetError() {
	p.status = PluginStatusError
}

// AddCapability adds a capability to the plugin
func (p *Plugin) AddCapability(capability string) {
	if capability == "" {
		return
	}

	// Check if capability already exists
	for _, c := range p.capabilities {
		if c == capability {
			return
		}
	}

	p.capabilities = append(p.capabilities, capability)
}

// RemoveCapability removes a capability
func (p *Plugin) RemoveCapability(capability string) {
	for i, c := range p.capabilities {
		if c == capability {
			p.capabilities = append(p.capabilities[:i], p.capabilities[i+1:]...)
			return
		}
	}
}

// HasCapability checks if plugin has a capability
func (p *Plugin) HasCapability(capability string) bool {
	for _, c := range p.capabilities {
		if c == capability {
			return true
		}
	}
	return false
}

// UpdateConfiguration updates plugin configuration
func (p *Plugin) UpdateConfiguration(key string, value interface{}) {
	p.config.Set(key, value)
}

// CanExecute checks if plugin can execute
func (p *Plugin) CanExecute() error {
	if p.status != PluginStatusActive {
		return errors.New("plugin is not active")
	}
	return nil
}

// Getters

func (p *Plugin) ID() uuid.UUID                { return p.id }
func (p *Plugin) Name() string                 { return p.name }
func (p *Plugin) Type() PluginType             { return p.pluginType }
func (p *Plugin) Version() string              { return p.version }
func (p *Plugin) Status() PluginStatus         { return p.status }
func (p *Plugin) Capabilities() []string       { return append([]string{}, p.capabilities...) }
func (p *Plugin) Configuration() Configuration { return p.config.Clone() }

// Validation functions

func validateName(name string) error {
	if name == "" {
		return ErrEmptyName
	}
	if len(name) > 100 {
		return errors.New("plugin name too long")
	}
	return nil
}

func validateType(pluginType PluginType) error {
	switch pluginType {
	case PluginTypeSource, PluginTypeDestination, PluginTypeTransform, PluginTypeOrchestrator:
		return nil
	default:
		return ErrInvalidType
	}
}

func validateVersion(version string) error {
	if version == "" {
		return ErrInvalidVersion
	}
	// Add more version validation if needed (e.g., semver)
	return nil
}
