package pipeline

import (
	"context"
)

// ListPipelinesUseCase handles listing pipelines
type ListPipelinesUseCase struct {
	repo      PipelineRepository
	validator InputValidator
}

// NewListPipelinesUseCase creates a new list pipelines use case
func NewListPipelinesUseCase(repo PipelineRepository, validator InputValidator) *ListPipelinesUseCase {
	return &ListPipelinesUseCase{
		repo:      repo,
		validator: validator,
	}
}


// ListPipelinesOutput represents the output of listing pipelines
type ListPipelinesOutput struct {
	Pipelines []PipelineListItem
	Total     int
	Limit     int
	Offset    int
}

// PipelineListItem represents a pipeline in the list
type PipelineListItem struct {
	ID          string
	Name        string
	Description string
	IsActive    bool
	Tags        []string
	StepCount   int
	CreatedAt   string
	UpdatedAt   string
}

// Execute lists pipelines based on criteria
func (uc *ListPipelinesUseCase) Execute(ctx context.Context, input ListPipelinesInput) (*ListPipelinesOutput, error) {
	// Set defaults
	if input.Limit <= 0 {
		input.Limit = 20
	}
	if input.Limit > 100 {
		input.Limit = 100
	}
	if input.Offset < 0 {
		input.Offset = 0
	}

	// Create criteria for repository
	criteria := ListCriteria{
		Limit:    input.Limit,
		Offset:   input.Offset,
		Active:   input.Active,
		Tags:     input.Tags,
		OrderBy:  input.OrderBy,
		OrderDir: input.OrderDir,
	}

	// Get pipelines from repository
	pipelines, total, err := uc.repo.List(ctx, criteria)
	if err != nil {
		return nil, err
	}

	// Convert to output format
	items := make([]PipelineListItem, len(pipelines))
	for i, pipeline := range pipelines {
		items[i] = PipelineListItem{
			ID:          pipeline.ID.String(),
			Name:        pipeline.Name,
			Description: pipeline.Description,
			IsActive:    pipeline.IsActive,
			Tags:        pipeline.Tags,
			StepCount:   len(pipeline.Steps),
			CreatedAt:   "2024-01-01T00:00:00Z", // In real implementation, get from persistence
			UpdatedAt:   "2024-01-01T00:00:00Z", // In real implementation, get from persistence
		}
	}

	return &ListPipelinesOutput{
		Pipelines: items,
		Total:     total,
		Limit:     input.Limit,
		Offset:    input.Offset,
	}, nil
}