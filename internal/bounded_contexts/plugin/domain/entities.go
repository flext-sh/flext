// Plugin Domain Entities - Bounded Context for Plugin Management
package domain

import (
	"time"
	"github.com/google/uuid"
)

// Plugin represents a FLEXT plugin
type Plugin struct {
	ID          uuid.UUID
	Name        string
	Type        PluginType
	Version     string
	Description string
	Author      string
	FilePath    string
	Config      PluginConfig
	Status      PluginStatus
	CreatedAt   time.Time
	UpdatedAt   time.Time
	LoadedAt    *time.Time
}

// PluginType represents the type of plugin
type PluginType string

const (
	PluginTypeExtractor   PluginType = "extractor"
	PluginTypeLoader      PluginType = "loader"
	PluginTypeTransform   PluginType = "transform"
	PluginTypeUtility     PluginType = "utility"
)

// PluginStatus represents plugin status
type PluginStatus string

const (
	PluginStatusAvailable PluginStatus = "available"
	PluginStatusLoaded    PluginStatus = "loaded"
	PluginStatusFailed    PluginStatus = "failed"
	PluginStatusDisabled  PluginStatus = "disabled"
)

// PluginConfig represents plugin configuration
type PluginConfig struct {
	Executable   string                 `json:"executable"`
	PythonModule string                 `json:"python_module,omitempty"`
	Environment  map[string]string      `json:"environment,omitempty"`
	Parameters   map[string]interface{} `json:"parameters,omitempty"`
}

// PluginExecution represents a plugin execution instance
type PluginExecution struct {
	ID         uuid.UUID
	PluginID   uuid.UUID
	Status     PluginStatus
	StartTime  time.Time
	EndTime    *time.Time
	Input      map[string]interface{}
	Output     map[string]interface{}
	Error      string
	ExecutedBy string
}

// NewPlugin creates a new plugin
func NewPlugin(name, version, description, author, filePath string, pluginType PluginType, config PluginConfig) *Plugin {
	return &Plugin{
		ID:          uuid.New(),
		Name:        name,
		Type:        pluginType,
		Version:     version,
		Description: description,
		Author:      author,
		FilePath:    filePath,
		Config:      config,
		Status:      PluginStatusAvailable,
		CreatedAt:   time.Now().UTC(),
		UpdatedAt:   time.Now().UTC(),
	}
}

// NewPluginExecution creates a new plugin execution
func NewPluginExecution(pluginID uuid.UUID, input map[string]interface{}, executedBy string) *PluginExecution {
	return &PluginExecution{
		ID:         uuid.New(),
		PluginID:   pluginID,
		Status:     PluginStatusLoaded,
		StartTime:  time.Now().UTC(),
		Input:      input,
		ExecutedBy: executedBy,
	}
}

// Complete marks the execution as completed
func (pe *PluginExecution) Complete(output map[string]interface{}) {
	now := time.Now().UTC()
	pe.Status = PluginStatusAvailable
	pe.EndTime = &now
	pe.Output = output
}

// Fail marks the execution as failed
func (pe *PluginExecution) Fail(errorMessage string) {
	now := time.Now().UTC()
	pe.Status = PluginStatusFailed
	pe.EndTime = &now
	pe.Error = errorMessage
}