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
