package events

import (
	"github.com/flext-sh/flext/pkg/utils/shared_kernel"
	"github.com/google/uuid"
)

const (
	PluginRegisteredEventType  = "plugin.registered"
	PortAddedEventType         = "plugin.port.added"
	PluginActivatedEventType   = "plugin.activated"
	PluginDeactivatedEventType = "plugin.deactivated"
	PluginFailedEventType      = "plugin.failed"
	PluginDeletedEventType     = "plugin.deleted"
)

// PluginRegisteredEvent é emitido quando um novo plugin é registrado
type PluginRegisteredEvent struct {
	domain.BaseDomainEvent
	PluginName string `json:"plugin_name"`
	PluginType string `json:"plugin_type"`
	Version    string `json:"version"`
}

// NewPluginRegisteredEvent cria um novo evento de plugin registrado
func NewPluginRegisteredEvent(pluginID uuid.UUID, name, pluginType, version string) PluginRegisteredEvent {
	return PluginRegisteredEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PluginRegisteredEventType, pluginID),
		PluginName:      name,
		PluginType:      pluginType,
		Version:         version,
	}
}

// PortAddedEvent é emitido quando uma porta é adicionada ao plugin
type PortAddedEvent struct {
	domain.BaseDomainEvent
	PortName string `json:"port_name"`
	PortType string `json:"port_type"`
}

// NewPortAddedEvent cria um novo evento de porta adicionada
func NewPortAddedEvent(pluginID uuid.UUID, portName, portType string) PortAddedEvent {
	return PortAddedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PortAddedEventType, pluginID),
		PortName:        portName,
		PortType:        portType,
	}
}

// PluginActivatedEvent é emitido quando um plugin é ativado
type PluginActivatedEvent struct {
	domain.BaseDomainEvent
}

// NewPluginActivatedEvent cria um novo evento de plugin ativado
func NewPluginActivatedEvent(pluginID uuid.UUID) PluginActivatedEvent {
	return PluginActivatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PluginActivatedEventType, pluginID),
	}
}

// PluginDeactivatedEvent é emitido quando um plugin é desativado
type PluginDeactivatedEvent struct {
	domain.BaseDomainEvent
}

// NewPluginDeactivatedEvent cria um novo evento de plugin desativado
func NewPluginDeactivatedEvent(pluginID uuid.UUID) PluginDeactivatedEvent {
	return PluginDeactivatedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PluginDeactivatedEventType, pluginID),
	}
}

// PluginFailedEvent é emitido quando um plugin falha
type PluginFailedEvent struct {
	domain.BaseDomainEvent
	Reason string `json:"reason"`
}

// NewPluginFailedEvent cria um novo evento de plugin falhado
func NewPluginFailedEvent(pluginID uuid.UUID, reason string) PluginFailedEvent {
	return PluginFailedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PluginFailedEventType, pluginID),
		Reason:          reason,
	}
}

// PluginDeletedEvent é emitido quando um plugin é deletado
type PluginDeletedEvent struct {
	domain.BaseDomainEvent
	PluginName string `json:"plugin_name"`
}

// NewPluginDeletedEvent cria um novo evento de plugin deletado
func NewPluginDeletedEvent(pluginID uuid.UUID, pluginName string) PluginDeletedEvent {
	return PluginDeletedEvent{
		BaseDomainEvent: domain.NewBaseDomainEvent(PluginDeletedEventType, pluginID),
		PluginName:      pluginName,
	}
}
