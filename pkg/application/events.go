package plugin

import (
	"github.com/google/uuid"
	"time"
)

// PluginRegisteredEvent is published when a new plugin is registered
type PluginRegisteredEvent struct {
	PluginID     uuid.UUID
	Name         string
	Type         string
	Version      string
	RegisteredAt time.Time
}

// PluginActivatedEvent is published when a plugin is activated
type PluginActivatedEvent struct {
	PluginID    uuid.UUID
	ActivatedAt time.Time
}

// PluginDeactivatedEvent is published when a plugin is deactivated
type PluginDeactivatedEvent struct {
	PluginID      uuid.UUID
	DeactivatedAt time.Time
}

// PluginConfigurationUpdatedEvent is published when plugin configuration is updated
type PluginConfigurationUpdatedEvent struct {
	PluginID  uuid.UUID
	UpdatedAt time.Time
	Changes   map[string]interface{}
}

// PluginErrorEvent is published when a plugin encounters an error
type PluginErrorEvent struct {
	PluginID   uuid.UUID
	Error      string
	OccurredAt time.Time
}

// PluginDeletedEvent is published when a plugin is deleted
type PluginDeletedEvent struct {
	PluginID  uuid.UUID
	DeletedAt time.Time
}
