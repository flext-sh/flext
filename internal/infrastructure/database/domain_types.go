package database

import (
	"fmt"
	"time"

	"github.com/google/uuid"
)

// Domain types that match the database schema

// Pipeline represents a pipeline entity for database operations
type Pipeline struct {
	ID          uuid.UUID              `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Status      PipelineStatus         `json:"status"`
	Tags        []string               `json:"tags"`
	Metadata    map[string]interface{} `json:"metadata"`
	Steps       []*Step                `json:"steps"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
	CreatedBy   string                 `json:"created_by"`
	Version     int                    `json:"version"`
}

// Step represents a pipeline step
type Step struct {
	ID           uuid.UUID              `json:"id"`
	PipelineID   uuid.UUID              `json:"pipeline_id"`
	Name         string                 `json:"name"`
	Type         StepType               `json:"type"`
	Config       map[string]interface{} `json:"config"`
	Dependencies []uuid.UUID            `json:"dependencies"`
	Order        int                    `json:"order"`
	CreatedAt    time.Time              `json:"created_at"`
}

// Plugin represents a plugin entity for database operations
type Plugin struct {
	ID           uuid.UUID `json:"id"`
	Name         string    `json:"name"`
	Type         string    `json:"type"`
	Version      string    `json:"version"`
	Description  string    `json:"description"`
	Author       string    `json:"author"`
	EntryPoint   string    `json:"entry_point"`
	Dependencies []string  `json:"dependencies"`
	ConfigSchema string    `json:"config_schema"`
	Status       string    `json:"status"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// Execution represents a pipeline execution
type Execution struct {
	ID           uuid.UUID              `json:"id"`
	PipelineID   uuid.UUID              `json:"pipeline_id"`
	Status       string                 `json:"status"`
	StartedAt    *time.Time             `json:"started_at"`
	CompletedAt  *time.Time             `json:"completed_at"`
	Duration     time.Duration          `json:"duration"`
	Success      bool                   `json:"success"`
	ErrorMessage string                 `json:"error_message"`
	Logs         []ExecutionLog         `json:"logs"`
	Metrics      map[string]interface{} `json:"metrics"`
	CreatedAt    time.Time              `json:"created_at"`
}

// ExecutionLog represents a log entry for an execution
type ExecutionLog struct {
	Timestamp time.Time  `json:"timestamp"`
	Level     string     `json:"level"`
	Message   string     `json:"message"`
	StepID    *uuid.UUID `json:"step_id,omitempty"`
}

// Enums and status types

// PipelineStatus represents the status of a pipeline
type PipelineStatus int

const (
	PipelineStatusCreated PipelineStatus = iota
	PipelineStatusActive
	PipelineStatusInactive
	PipelineStatusArchived
	PipelineStatusDeleted
)

func (s PipelineStatus) String() string {
	switch s {
	case PipelineStatusCreated:
		return "created"
	case PipelineStatusActive:
		return "active"
	case PipelineStatusInactive:
		return "inactive"
	case PipelineStatusArchived:
		return "archived"
	case PipelineStatusDeleted:
		return "deleted"
	default:
		return "unknown"
	}
}

func (s *PipelineStatus) FromString(str string) error {
	switch str {
	case "created":
		*s = PipelineStatusCreated
	case "active":
		*s = PipelineStatusActive
	case "inactive":
		*s = PipelineStatusInactive
	case "archived":
		*s = PipelineStatusArchived
	case "deleted":
		*s = PipelineStatusDeleted
	default:
		return fmt.Errorf("unknown pipeline status: %s", str)
	}
	return nil
}

// StepType represents the type of a pipeline step
type StepType int

const (
	StepTypeSource StepType = iota
	StepTypeTransform
	StepTypeDestination
	StepTypeUtility
)

func (t StepType) String() string {
	switch t {
	case StepTypeSource:
		return "source"
	case StepTypeTransform:
		return "transform"
	case StepTypeDestination:
		return "destination"
	case StepTypeUtility:
		return "utility"
	default:
		return "unknown"
	}
}

func (t *StepType) FromString(str string) error {
	switch str {
	case "source":
		*t = StepTypeSource
	case "transform":
		*t = StepTypeTransform
	case "destination":
		*t = StepTypeDestination
	case "utility":
		*t = StepTypeUtility
	default:
		return fmt.Errorf("unknown step type: %s", str)
	}
	return nil
}

// Error types
var (
	ErrPipelineNotFound  = fmt.Errorf("pipeline not found")
	ErrPluginNotFound    = fmt.Errorf("plugin not found")
	ErrExecutionNotFound = fmt.Errorf("execution not found")
	ErrDuplicateName     = fmt.Errorf("name already exists")
)

// NewPipeline creates a new pipeline
func NewPipeline(name, description, createdBy string) *Pipeline {
	return &Pipeline{
		ID:          uuid.New(),
		Name:        name,
		Description: description,
		Status:      PipelineStatusCreated,
		Tags:        make([]string, 0),
		Metadata:    make(map[string]interface{}),
		Steps:       make([]*Step, 0),
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
		CreatedBy:   createdBy,
		Version:     1,
	}
}

// NewStep creates a new step
func NewStep(pipelineID uuid.UUID, name string, stepType StepType) *Step {
	return &Step{
		ID:           uuid.New(),
		PipelineID:   pipelineID,
		Name:         name,
		Type:         stepType,
		Config:       make(map[string]interface{}),
		Dependencies: make([]uuid.UUID, 0),
		CreatedAt:    time.Now(),
	}
}

// NewPlugin creates a new plugin
func NewPlugin(name, pluginType, version, author, entryPoint string) *Plugin {
	return &Plugin{
		ID:           uuid.New(),
		Name:         name,
		Type:         pluginType,
		Version:      version,
		Author:       author,
		EntryPoint:   entryPoint,
		Dependencies: make([]string, 0),
		Status:       "inactive",
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}
}

// NewExecution creates a new execution
func NewExecution(pipelineID uuid.UUID) *Execution {
	return &Execution{
		ID:         uuid.New(),
		PipelineID: pipelineID,
		Status:     "pending",
		Logs:       make([]ExecutionLog, 0),
		Metrics:    make(map[string]interface{}),
		CreatedAt:  time.Now(),
	}
}
