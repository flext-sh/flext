package dto

import "github.com/google/uuid"

// CreatePipelineRequest represents a request to create a pipeline
type CreatePipelineRequest struct {
	Name        string   `json:"name" validate:"required,min=1,max=100"`
	Description string   `json:"description" validate:"max=500"`
	Tags        []string `json:"tags" validate:"dive,min=1,max=50"`
}

// AddStepRequest represents a request to add a step to a pipeline
type AddStepRequest struct {
	Name          string                 `json:"name" validate:"required,min=1,max=100"`
	PluginID      string                 `json:"plugin_id" validate:"required,uuid"`
	Configuration map[string]interface{} `json:"configuration"`
	DependsOn     []string               `json:"depends_on" validate:"dive,uuid"`
}

// ExecutePipelineRequest represents a request to execute a pipeline
type ExecutePipelineRequest struct {
	Parameters map[string]interface{} `json:"parameters"`
}

// PipelineResponse represents a pipeline in responses
type PipelineResponse struct {
	ID          uuid.UUID              `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Tags        []string               `json:"tags"`
	Active      bool                   `json:"active"`
	CreatedAt   string                 `json:"created_at"`
	UpdatedAt   string                 `json:"updated_at"`
	Steps       []PipelineStepResponse `json:"steps"`
}

// PipelineStepResponse represents a pipeline step in responses
type PipelineStepResponse struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	PluginID      uuid.UUID              `json:"plugin_id"`
	Configuration map[string]interface{} `json:"configuration"`
	DependsOn     []uuid.UUID            `json:"depends_on"`
	Order         int                    `json:"order"`
	Status        string                 `json:"status"`
}

// PipelineListResponse represents a list of pipelines
type PipelineListResponse struct {
	Pipelines []PipelineResponse `json:"pipelines"`
	Total     int                `json:"total"`
	Limit     int                `json:"limit"`
	Offset    int                `json:"offset"`
}

// ExecutionResponse represents a pipeline execution response
type ExecutionResponse struct {
	ExecutionID uuid.UUID `json:"execution_id"`
	PipelineID  uuid.UUID `json:"pipeline_id"`
	Status      string    `json:"status"`
	StartedAt   string    `json:"started_at"`
}

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message"`
	Code    string `json:"code,omitempty"`
}

// SuccessResponse represents a generic success response
type SuccessResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// RegisterPluginRequest represents the HTTP request for registering a plugin
type RegisterPluginRequest struct {
	Name          string                 `json:"name" validate:"required,min=1,max=100"`
	Type          string                 `json:"type" validate:"required,oneof=source destination transform orchestrator"`
	Version       string                 `json:"version" validate:"required"`
	Capabilities  []string               `json:"capabilities"`
	Configuration map[string]interface{} `json:"configuration"`
}

// ActivatePluginRequest represents the HTTP request for activating a plugin
type ActivatePluginRequest struct {
	// Empty body - plugin ID comes from URL parameter
}

// UpdatePluginRequest represents the HTTP request for updating a plugin
type UpdatePluginRequest struct {
	Configuration map[string]interface{} `json:"configuration"`
	Capabilities  []string               `json:"capabilities"`
}