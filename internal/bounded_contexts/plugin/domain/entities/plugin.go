package entities

import (
	"errors"
	"fmt"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/events"
	"github.com/flext-sh/flext/internal/shared_kernel/domain"
)

// PluginType define os tipos de plugin disponíveis
type PluginType string

const (
	PluginTypeSource      PluginType = "source"
	PluginTypeTarget      PluginType = "target"
	PluginTypeTransformer PluginType = "transformer"
	PluginTypeUtility     PluginType = "utility"
)

// PluginStatus define os status do plugin
type PluginStatus string

const (
	PluginStatusActive     PluginStatus = "active"
	PluginStatusInactive   PluginStatus = "inactive"
	PluginStatusRegistered PluginStatus = "registered"
	PluginStatusFailed     PluginStatus = "failed"
)

// Port representa uma porta exposta pelo plugin
type Port struct {
	Name        string                 `json:"name"`
	Type        string                 `json:"type"`
	Required    bool                   `json:"required"`
	Description string                 `json:"description"`
	Schema      map[string]interface{} `json:"schema,omitempty"`
}

// Plugin é o agregado raiz para o contexto de plugin
type Plugin struct {
	domain.AggregateRoot
	Name          string                 `json:"name"`
	Type          PluginType             `json:"type"`
	Version       string                 `json:"version"`
	Description   string                 `json:"description"`
	Author        string                 `json:"author"`
	Status        PluginStatus           `json:"status"`
	EntryPoint    string                 `json:"entry_point"`
	Ports         []Port                 `json:"ports"`
	Dependencies  []string               `json:"dependencies"`
	Configuration map[string]interface{} `json:"configuration"`
	Metadata      map[string]interface{} `json:"metadata"`
	Capabilities  []string               `json:"capabilities"`
	IsActive      bool                   `json:"is_active"`
}

// NewPlugin cria um novo agregado plugin
func NewPlugin(name, version, entryPoint string, pluginType PluginType) (*Plugin, error) {
	if name == "" {
		return nil, errors.New("plugin name cannot be empty")
	}
	if version == "" {
		return nil, errors.New("plugin version cannot be empty")
	}
	if entryPoint == "" {
		return nil, errors.New("plugin entry point cannot be empty")
	}
	if !isValidPluginType(pluginType) {
		return nil, fmt.Errorf("invalid plugin type: %s", pluginType)
	}

	p := &Plugin{
		AggregateRoot: domain.NewAggregateRoot(),
		Name:          name,
		Type:          pluginType,
		Version:       version,
		EntryPoint:    entryPoint,
		Status:        PluginStatusRegistered,
		Ports:         make([]Port, 0),
		Dependencies:  make([]string, 0),
		Configuration: make(map[string]interface{}),
		Metadata:      make(map[string]interface{}),
		Capabilities:  make([]string, 0),
		IsActive:      false,
	}

	// Adicionar evento de domínio
	p.AddEvent(events.NewPluginRegisteredEvent(p.ID, p.Name, string(p.Type), p.Version))

	return p, nil
}

// AddPort adiciona uma porta ao plugin
func (p *Plugin) AddPort(port Port) error {
	if port.Name == "" {
		return errors.New("port name cannot be empty")
	}
	if port.Type == "" {
		return errors.New("port type cannot be empty")
	}

	// Verificar se porta já existe
	for _, existingPort := range p.Ports {
		if existingPort.Name == port.Name {
			return fmt.Errorf("port %s already exists", port.Name)
		}
	}

	p.Ports = append(p.Ports, port)
	p.UpdateTimestamp()
	p.AddEvent(events.NewPortAddedEvent(p.ID, port.Name, port.Type))

	return nil
}

// Activate ativa o plugin
func (p *Plugin) Activate() error {
	if p.Status == PluginStatusActive {
		return errors.New("plugin is already active")
	}
	if p.Status == PluginStatusFailed {
		return errors.New("cannot activate failed plugin")
	}

	p.Status = PluginStatusActive
	p.UpdateTimestamp()
	p.AddEvent(events.NewPluginActivatedEvent(p.ID))

	return nil
}

// Deactivate desativa o plugin
func (p *Plugin) Deactivate() {
	if p.Status == PluginStatusInactive {
		return
	}

	p.Status = PluginStatusInactive
	p.UpdateTimestamp()
	p.AddEvent(events.NewPluginDeactivatedEvent(p.ID))
}

// MarkAsFailed marca o plugin como falhado
func (p *Plugin) MarkAsFailed(reason string) {
	p.Status = PluginStatusFailed
	p.Metadata["failure_reason"] = reason
	p.UpdateTimestamp()
	p.AddEvent(events.NewPluginFailedEvent(p.ID, reason))
}

// UpdateConfiguration atualiza a configuração do plugin
func (p *Plugin) UpdateConfiguration(config map[string]interface{}) {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}

	for k, v := range config {
		p.Configuration[k] = v
	}

	p.UpdateTimestamp()
}

// AddDependency adiciona uma dependência ao plugin
func (p *Plugin) AddDependency(dependency string) {
	if dependency == "" {
		return
	}

	// Verificar se dependência já existe
	for _, dep := range p.Dependencies {
		if dep == dependency {
			return
		}
	}

	p.Dependencies = append(p.Dependencies, dependency)
	p.UpdateTimestamp()
}

// GetPortByName busca uma porta pelo nome
func (p *Plugin) GetPortByName(name string) (*Port, error) {
	for _, port := range p.Ports {
		if port.Name == name {
			return &port, nil
		}
	}
	return nil, fmt.Errorf("port %s not found", name)
}

// CanExecute checks if plugin can execute
func (p *Plugin) CanExecute() error {
	if p.Status != PluginStatusActive {
		return errors.New("plugin is not active")
	}
	return nil
}

// Helper methods

func isValidPluginType(pluginType PluginType) bool {
	switch pluginType {
	case PluginTypeSource, PluginTypeTarget, PluginTypeTransformer, PluginTypeUtility:
		return true
	default:
		return false
	}
}
