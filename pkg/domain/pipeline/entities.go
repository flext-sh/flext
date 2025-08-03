// Pipeline Domain Entities - Bounded Context for Pipeline Management
package domain

import (
	"time"
	"github.com/google/uuid"
)

// Pipeline represents a data integration pipeline
type Pipeline struct {
	ID          uuid.UUID
	Name        string
	Description string
	Extractor   string
	Loader      string
	Config      PipelineConfig
	Status      PipelineStatus
	CreatedAt   time.Time
	UpdatedAt   time.Time
	CreatedBy   string
}

// PipelineConfig represents pipeline configuration
type PipelineConfig struct {
	Source PipelineSourceConfig `json:"source"`
	Target PipelineTargetConfig `json:"target"`
	Options map[string]interface{} `json:"options,omitempty"`
}

// PipelineSourceConfig represents source configuration
type PipelineSourceConfig struct {
	Type     string                 `json:"type"`
	Host     string                 `json:"host,omitempty"`
	Port     int                    `json:"port,omitempty"`
	Database string                 `json:"database,omitempty"`
	Username string                 `json:"username,omitempty"`
	Password string                 `json:"password,omitempty"`
	Query    string                 `json:"query,omitempty"`
	Config   map[string]interface{} `json:"config,omitempty"`
}

// PipelineTargetConfig represents target configuration
type PipelineTargetConfig struct {
	Type     string                 `json:"type"`
	Host     string                 `json:"host,omitempty"`
	Port     int                    `json:"port,omitempty"`
	Database string                 `json:"database,omitempty"`
	Username string                 `json:"username,omitempty"`
	Password string                 `json:"password,omitempty"`
	Table    string                 `json:"table,omitempty"`
	Config   map[string]interface{} `json:"config,omitempty"`
}

// PipelineStatus represents pipeline status
type PipelineStatus string

const (
	PipelineStatusCreated    PipelineStatus = "created"
	PipelineStatusRunning    PipelineStatus = "running"
	PipelineStatusCompleted  PipelineStatus = "completed"
	PipelineStatusFailed     PipelineStatus = "failed"
	PipelineStatusCancelled  PipelineStatus = "cancelled"
)

// PipelineExecution represents a pipeline execution instance
type PipelineExecution struct {
	ID            uuid.UUID
	PipelineID    uuid.UUID
	Status        PipelineStatus
	StartTime     time.Time
	EndTime       *time.Time
	ExtractedRows int64
	LoadedRows    int64
	ErrorMessage  string
	ExecutedBy    string
	Metadata      map[string]interface{}
}

// NewPipeline creates a new pipeline
func NewPipeline(name, description, extractor, loader, createdBy string, config PipelineConfig) *Pipeline {
	return &Pipeline{
		ID:          uuid.New(),
		Name:        name,
		Description: description,
		Extractor:   extractor,
		Loader:      loader,
		Config:      config,
		Status:      PipelineStatusCreated,
		CreatedAt:   time.Now().UTC(),
		UpdatedAt:   time.Now().UTC(),
		CreatedBy:   createdBy,
	}
}

// NewPipelineExecution creates a new pipeline execution
func NewPipelineExecution(pipelineID uuid.UUID, executedBy string) *PipelineExecution {
	return &PipelineExecution{
		ID:         uuid.New(),
		PipelineID: pipelineID,
		Status:     PipelineStatusRunning,
		StartTime:  time.Now().UTC(),
		ExecutedBy: executedBy,
		Metadata:   make(map[string]interface{}),
	}
}

// Complete marks the execution as completed
func (pe *PipelineExecution) Complete(extractedRows, loadedRows int64) {
	now := time.Now().UTC()
	pe.Status = PipelineStatusCompleted
	pe.EndTime = &now
	pe.ExtractedRows = extractedRows
	pe.LoadedRows = loadedRows
}

// Fail marks the execution as failed
func (pe *PipelineExecution) Fail(errorMessage string) {
	now := time.Now().UTC()
	pe.Status = PipelineStatusFailed
	pe.EndTime = &now
	pe.ErrorMessage = errorMessage
}

// Duration returns the execution duration
func (pe *PipelineExecution) Duration() time.Duration {
	if pe.EndTime == nil {
		return time.Since(pe.StartTime)
	}
	return pe.EndTime.Sub(pe.StartTime)
}