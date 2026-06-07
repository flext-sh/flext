// Package entities provides shared domain entities for the FlexT ecosystem
// This eliminates code duplication across bounded contexts
package entities

import (
	"errors"
	"time"

	"github.com/google/uuid"
)

// UnifiedPipelineStatus represents the status of a pipeline - SINGLE SOURCE OF TRUTH
type UnifiedPipelineStatus string

const (
	UnifiedPipelineStatusDraft     UnifiedPipelineStatus = "draft"
	UnifiedPipelineStatusActive    UnifiedPipelineStatus = "active"
	UnifiedPipelineStatusRunning   UnifiedPipelineStatus = "running"
	UnifiedPipelineStatusCompleted UnifiedPipelineStatus = "completed"
	UnifiedPipelineStatusFailed    UnifiedPipelineStatus = "failed"
	UnifiedPipelineStatusPaused    UnifiedPipelineStatus = "paused"
	UnifiedPipelineStatusArchived  UnifiedPipelineStatus = "archived"
)

// UnifiedPipelineType represents the type of a pipeline - SINGLE SOURCE OF TRUTH
type UnifiedPipelineType string

const (
	UnifiedPipelineTypeETL       UnifiedPipelineType = "etl"
	UnifiedPipelineTypeELT       UnifiedPipelineType = "elt"
	UnifiedPipelineTypeStream    UnifiedPipelineType = "stream"
	UnifiedPipelineTypeBatch     UnifiedPipelineType = "batch"
	UnifiedPipelineTypeRealTime  UnifiedPipelineType = "realtime"
	UnifiedPipelineTypeAnalytics UnifiedPipelineType = "analytics"
)

// UnifiedPipelineStep represents a step in a pipeline - ELIMINATING DUPLICATION
type UnifiedPipelineStep struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	Type          string                 `json:"type"`
	PluginID      uuid.UUID              `json:"plugin_id,omitempty"`
	Configuration map[string]interface{} `json:"configuration"`
	Order         int                    `json:"order"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
	RetryCount    int                    `json:"retry_count"`
	MaxRetries    int                    `json:"max_retries"`
	Timeout       time.Duration          `json:"timeout"`
	IsEnabled     bool                   `json:"is_enabled"`
	CreatedAt     time.Time              `json:"created_at"`
}

// NewUnifiedPipelineStep creates a new pipeline step
func NewUnifiedPipelineStep(name, stepType string) *UnifiedPipelineStep {
	return &UnifiedPipelineStep{
		ID:            uuid.New(),
		Name:          name,
		Type:          stepType,
		Configuration: make(map[string]interface{}),
		DependsOn:     make([]uuid.UUID, 0),
		RetryCount:    0,
		MaxRetries:    3,
		Timeout:       30 * time.Minute,
		IsEnabled:     true,
		CreatedAt:     time.Now(),
	}
}

// UnifiedPipeline represents a data pipeline entity - SINGLE SOURCE OF TRUTH
// This eliminates the duplication between flexcore and bounded_contexts
type UnifiedPipeline struct {
	BaseAggregateRoot

	// Core pipeline data
	Name          string                 `json:"name"`
	Description   string                 `json:"description"`
	Type          UnifiedPipelineType    `json:"type"`
	Status        UnifiedPipelineStatus  `json:"status"`
	Steps         []UnifiedPipelineStep  `json:"steps"`
	Tags          []string               `json:"tags"`
	Owner         string                 `json:"owner"`
	Configuration map[string]interface{} `json:"configuration"`
	Schedule      string                 `json:"schedule,omitempty"`
	LastRunAt     *time.Time             `json:"last_run_at,omitempty"`
	NextRunAt     *time.Time             `json:"next_run_at,omitempty"`
	IsActive      bool                   `json:"is_active"`
}

// NewUnifiedPipeline creates a new pipeline - ELIMINATING CONSTRUCTOR DUPLICATION
func NewUnifiedPipeline(name, description, owner string) (*UnifiedPipeline, error) {
	if name == "" {
		return nil, errors.New("pipeline name cannot be empty")
	}
	if owner == "" {
		return nil, errors.New("pipeline owner cannot be empty")
	}

	pipeline := &UnifiedPipeline{
		BaseAggregateRoot: *NewBaseAggregateRoot("pipeline"),
		Name:              name,
		Description:       description,
		Type:              UnifiedPipelineTypeETL, // Default type
		Status:            UnifiedPipelineStatusDraft,
		Steps:             make([]UnifiedPipelineStep, 0),
		Tags:              make([]string, 0),
		Owner:             owner,
		Configuration:     make(map[string]interface{}),
		IsActive:          false,
	}

	// Add domain event
	pipeline.AddDomainEvent(NewBaseDomainEvent("pipeline.created", pipeline.GetID(), map[string]interface{}{
		"name":  name,
		"owner": owner,
	}, pipeline.GetVersion()))

	return pipeline, nil
}
