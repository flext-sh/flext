package commands

import (
	"context"
	"time"

	"github.com/flext-sh/flext/pkg/domain/pipeline/application/ports"
	"github.com/flext-sh/flext/pkg/domain/pipeline/domain/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
	"github.com/google/uuid"
)

// UpdatePipelineCommand represents the command to update a pipeline
type UpdatePipelineCommand struct {
	PipelineID    uuid.UUID              `json:"pipeline_id" validate:"required"`
	Name          *string                `json:"name,omitempty" validate:"omitempty,min=3,max=100"`
	Description   *string                `json:"description,omitempty" validate:"omitempty,max=500"`
	IsActive      *bool                  `json:"is_active,omitempty"`
	Tags          []string               `json:"tags,omitempty"`
	Configuration map[string]interface{} `json:"configuration,omitempty"`
	Schedule      *string                `json:"schedule,omitempty"`
}

// Validate validates the command
func (c *UpdatePipelineCommand) Validate() error {
	if c.PipelineID == uuid.Nil {
		return &value_objects.DomainError{
			Code:    "INVALID_COMMAND",
			Message: "Pipeline ID is required",
		}
	}

	if c.Name != nil && (len(*c.Name) < 3 || len(*c.Name) > 100) {
		return &value_objects.DomainError{
			Code:    "INVALID_COMMAND",
			Message: "Name must be between 3 and 100 characters",
		}
	}

	return nil
}

// UpdatePipelineResult represents the result of updating a pipeline
type UpdatePipelineResult struct {
	PipelineID  uuid.UUID `json:"pipeline_id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	IsActive    bool      `json:"is_active"`
	Status      string    `json:"status"`
	UpdatedAt   time.Time `json:"updated_at"`
	Version     int       `json:"version"`
}

// UpdatePipelineCommandHandler handles pipeline updates
type UpdatePipelineCommandHandler struct {
	pipelineRepo ports.PipelineRepository
}

// NewUpdatePipelineCommandHandler creates a new command handler
func NewUpdatePipelineCommandHandler(
	pipelineRepo ports.PipelineRepository,
) *UpdatePipelineCommandHandler {
	return &UpdatePipelineCommandHandler{
		pipelineRepo: pipelineRepo,
	}
}

// Handle executes the update pipeline command
func (h *UpdatePipelineCommandHandler) Handle(ctx context.Context, cmd *UpdatePipelineCommand) (*UpdatePipelineResult, error) {
	if err := cmd.Validate(); err != nil {
		return nil, err
	}

	pipeline, err := h.getPipelineForUpdate(ctx, cmd.PipelineID)
	if err != nil {
		return nil, err
	}

	if err := h.applyUpdates(pipeline, cmd); err != nil {
		return nil, err
	}

	return h.saveAndBuildResult(ctx, pipeline)
}

// getPipelineForUpdate retrieves the pipeline for update
func (h *UpdatePipelineCommandHandler) getPipelineForUpdate(ctx context.Context, pipelineID uuid.UUID) (*entities.Pipeline, error) {
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

// applyUpdates applies the updates to the pipeline
func (h *UpdatePipelineCommandHandler) applyUpdates(pipeline *entities.Pipeline, cmd *UpdatePipelineCommand) error {
	// Update basic fields
	if cmd.Name != nil {
		pipeline.Name = *cmd.Name
	}

	if cmd.Description != nil {
		pipeline.Description = *cmd.Description
	}

	if cmd.Tags != nil {
		pipeline.Tags = cmd.Tags
	}

	if cmd.Configuration != nil {
		pipeline.UpdateConfiguration(cmd.Configuration)
	}

	if cmd.Schedule != nil {
		pipeline.SetSchedule(*cmd.Schedule)
	}

	// Update activation status
	if cmd.IsActive != nil {
		if *cmd.IsActive {
			if err := pipeline.Activate(); err != nil {
				return &value_objects.DomainError{
					Code:        "ACTIVATION_FAILED",
					Message:     "Failed to activate pipeline",
					Description: err.Error(),
				}
			}
		} else {
			pipeline.Deactivate()
		}
	}

	return nil
}

// saveAndBuildResult saves the pipeline and builds the result
func (h *UpdatePipelineCommandHandler) saveAndBuildResult(ctx context.Context, pipeline *entities.Pipeline) (*UpdatePipelineResult, error) {
	// Version is already incremented by domain methods

	updatedPipeline, err := h.pipelineRepo.Update(ctx, pipeline)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "UPDATE_FAILED",
			Message:     "Failed to update pipeline",
			Description: err.Error(),
		}
	}

	return &UpdatePipelineResult{
		PipelineID:  updatedPipeline.GetID(),
		Name:        updatedPipeline.Name,
		Description: updatedPipeline.Description,
		IsActive:    updatedPipeline.IsActive,
		Status:      string(updatedPipeline.Status),
		UpdatedAt:   updatedPipeline.GetUpdatedAt(),
		Version:     int(updatedPipeline.GetVersion()),
	}, nil
}
