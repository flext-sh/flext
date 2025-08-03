package commands

import (
	"context"
	"time"

	"github.com/flext-sh/flext/pkg/domain/pipeline/application/ports"
	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
	"github.com/google/uuid"
)

// CreatePipelineCommand represents the command to create a new pipeline
type CreatePipelineCommand struct {
	Name          string                 `json:"name" validate:"required,min=3,max=100"`
	Description   string                 `json:"description" validate:"max=500"`
	Type          string                 `json:"type" validate:"required,oneof=etl stream batch realtime analytics"`
	Tags          []string               `json:"tags,omitempty"`
	Schedule      string                 `json:"schedule,omitempty"`
	Configuration map[string]interface{} `json:"configuration,omitempty"`
	CreatedBy     string                 `json:"created_by" validate:"required"`
}

// Validate validates the command
func (c *CreatePipelineCommand) Validate() error {
	if c.Name == "" {
		return &value_objects.DomainError{
			Code:    "INVALID_COMMAND",
			Message: "Pipeline name is required",
		}
	}
	if len(c.Name) < 3 || len(c.Name) > 100 {
		return &value_objects.DomainError{
			Code:    "INVALID_COMMAND",
			Message: "Name must be between 3 and 100 characters",
		}
	}
	return nil
}

// CreatePipelineResult represents the result of creating a pipeline
type CreatePipelineResult struct {
	PipelineID string    `json:"pipeline_id"`
	Name       string    `json:"name"`
	Status     string    `json:"status"`
	Type       string    `json:"type"`
	CreatedAt  time.Time `json:"created_at"`
	CreatedBy  string    `json:"created_by"`
}

// CreatePipelineCommandHandler handles the creation of pipelines
type CreatePipelineCommandHandler struct {
	pipelineRepo ports.PipelineRepository
}

// NewCreatePipelineCommandHandler creates a new command handler
func NewCreatePipelineCommandHandler(
	pipelineRepo ports.PipelineRepository,
) *CreatePipelineCommandHandler {
	return &CreatePipelineCommandHandler{
		pipelineRepo: pipelineRepo,
	}
}

// Handle executes the create pipeline command
func (h *CreatePipelineCommandHandler) Handle(ctx context.Context, cmd *CreatePipelineCommand) (*CreatePipelineResult, error) {
	if err := cmd.Validate(); err != nil {
		return nil, err
	}

	if err := h.checkPipelineNameUniqueness(ctx, cmd.Name); err != nil {
		return nil, err
	}

	pipeline, err := h.createAndConfigurePipeline(cmd)
	if err != nil {
		return nil, err
	}

	return h.savePipelineAndBuildResult(ctx, pipeline, cmd.CreatedBy)
}

// checkPipelineNameUniqueness verifies that the pipeline name is not already in use
func (h *CreatePipelineCommandHandler) checkPipelineNameUniqueness(ctx context.Context, name string) error {
	existing, err := h.pipelineRepo.GetByName(ctx, name)
	if err == nil && existing != nil {
		return &value_objects.DomainError{
			Code:        "PIPELINE_NAME_EXISTS",
			Message:     "Pipeline with this name already exists",
			Description: "Choose a different name for the pipeline",
		}
	}
	return nil
}

// createAndConfigurePipeline creates a new pipeline and configures it based on the command
func (h *CreatePipelineCommandHandler) createAndConfigurePipeline(cmd *CreatePipelineCommand) (*entities.Pipeline, error) {
	pipelineType, err := h.parsePipelineType(cmd.Type)
	if err != nil {
		return nil, err
	}

	pipeline, err := entities.NewPipeline(cmd.Name, cmd.Description)
	if err != nil {
		return nil, err
	}

	pipeline.Type = pipelineType
	h.applyOptionalConfiguration(pipeline, cmd)

	return pipeline, nil
}

// applyOptionalConfiguration applies optional fields to the pipeline
func (h *CreatePipelineCommandHandler) applyOptionalConfiguration(pipeline *entities.Pipeline, cmd *CreatePipelineCommand) {
	if cmd.Schedule != "" {
		pipeline.SetSchedule(cmd.Schedule)
	}

	if len(cmd.Tags) > 0 {
		pipeline.Tags = cmd.Tags
	}

	if cmd.Configuration != nil {
		pipeline.UpdateConfiguration(cmd.Configuration)
	}
}

// savePipelineAndBuildResult saves the pipeline and returns the result
func (h *CreatePipelineCommandHandler) savePipelineAndBuildResult(ctx context.Context, pipeline *entities.Pipeline, createdBy string) (*CreatePipelineResult, error) {
	if err := h.pipelineRepo.Save(ctx, pipeline); err != nil {
		return nil, err
	}

	return &CreatePipelineResult{
		PipelineID: pipeline.GetID().String(),
		Name:       pipeline.Name,
		Status:     string(pipeline.Status),
		Type:       string(pipeline.Type),
		CreatedAt:  pipeline.GetCreatedAt(),
		CreatedBy:  createdBy,
	}, nil
}

// parsePipelineType converts string to PipelineType enum
func (h *CreatePipelineCommandHandler) parsePipelineType(typeStr string) (entities.PipelineType, error) {
	typeMap := map[string]entities.PipelineType{
		"etl":       entities.PipelineTypeETL,
		"analytics": entities.PipelineTypeAnalytics,
		"stream":    entities.PipelineTypeStream,
		"batch":     entities.PipelineTypeBatch,
		"realtime":  entities.PipelineTypeRealTime,
	}

	if pipelineType, exists := typeMap[typeStr]; exists {
		return pipelineType, nil
	}

	return entities.PipelineTypeETL, &application.ValidationError{
		Field:   "type",
		Message: "Invalid pipeline type",
		Value:   typeStr,
	}
}

// UpdatePipelineStatusCommand represents the command to update pipeline status
type UpdatePipelineStatusCommand struct {
	PipelineID uuid.UUID `json:"pipeline_id" validate:"required"`
	Status     string    `json:"status" validate:"required,oneof=active paused inactive"`
	UpdatedBy  string    `json:"updated_by" validate:"required"`
}

// Validate validates the command
func (c *UpdatePipelineStatusCommand) Validate() error {
	if c.PipelineID == uuid.Nil {
		return &value_objects.DomainError{
			Code:    "INVALID_COMMAND",
			Message: "Pipeline ID is required",
		}
	}
	return nil
}

// UpdatePipelineStatusResult represents the result of updating pipeline status
type UpdatePipelineStatusResult struct {
	PipelineID uuid.UUID `json:"pipeline_id"`
	OldStatus  string    `json:"old_status"`
	NewStatus  string    `json:"new_status"`
	UpdatedAt  time.Time `json:"updated_at"`
	UpdatedBy  string    `json:"updated_by"`
}

// UpdatePipelineStatusCommandHandler handles pipeline status updates
type UpdatePipelineStatusCommandHandler struct {
	pipelineRepo ports.PipelineRepository
}

// NewUpdatePipelineStatusCommandHandler creates a new command handler
func NewUpdatePipelineStatusCommandHandler(
	pipelineRepo ports.PipelineRepository,
) *UpdatePipelineStatusCommandHandler {
	return &UpdatePipelineStatusCommandHandler{
		pipelineRepo: pipelineRepo,
	}
}

// Handle executes the update pipeline status command
func (h *UpdatePipelineStatusCommandHandler) Handle(ctx context.Context, cmd *UpdatePipelineStatusCommand) (*UpdatePipelineStatusResult, error) {
	if err := cmd.Validate(); err != nil {
		return nil, err
	}

	pipeline, err := h.getPipelineForUpdate(ctx, cmd.PipelineID)
	if err != nil {
		return nil, err
	}

	oldStatus := pipeline.Status

	if err := h.updatePipelineStatus(pipeline, cmd.Status); err != nil {
		return nil, err
	}

	return h.saveAndBuildStatusResult(ctx, pipeline, oldStatus, cmd.UpdatedBy)
}

// getPipelineForUpdate retrieves the pipeline for status update
func (h *UpdatePipelineStatusCommandHandler) getPipelineForUpdate(ctx context.Context, pipelineID uuid.UUID) (*entities.Pipeline, error) {
	pipeline, err := h.pipelineRepo.GetByID(ctx, pipelineID)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "PIPELINE_NOT_FOUND",
			Message:     "Pipeline not found",
			Description: err.Error(),
		}
	}
	return pipeline, nil
}

// updatePipelineStatus updates the pipeline status based on the command
func (h *UpdatePipelineStatusCommandHandler) updatePipelineStatus(pipeline *entities.Pipeline, status string) error {
	switch status {
	case "active":
		if err := pipeline.Activate(); err != nil {
			return &value_objects.DomainError{
				Code:        "ACTIVATION_FAILED",
				Message:     "Failed to activate pipeline",
				Description: err.Error(),
			}
		}
	case "paused", "inactive":
		pipeline.Deactivate()
	}
	return nil
}

// saveAndBuildStatusResult saves the pipeline and builds the result
func (h *UpdatePipelineStatusCommandHandler) saveAndBuildStatusResult(ctx context.Context, pipeline *entities.Pipeline, oldStatus entities.PipelineStatus, updatedBy string) (*UpdatePipelineStatusResult, error) {
	pipeline.IncrementVersion()

	if err := h.pipelineRepo.Save(ctx, pipeline); err != nil {
		return nil, &value_objects.DomainError{
			Code:        "UPDATE_FAILED",
			Message:     "Failed to update pipeline",
			Description: err.Error(),
		}
	}

	return &UpdatePipelineStatusResult{
		PipelineID: pipeline.GetID(),
		OldStatus:  string(oldStatus),
		NewStatus:  string(pipeline.Status),
		UpdatedAt:  pipeline.GetUpdatedAt(),
		UpdatedBy:  updatedBy,
	}, nil
}
