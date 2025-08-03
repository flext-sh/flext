package pipeline

import (
	"context"
	"fmt"
)

// PipelineService provides high-level pipeline operations
type PipelineService struct {
	pipelineRepo   PipelineRepository
	eventPublisher EventPublisher
}

// NewPipelineService creates a new pipeline service
func NewPipelineService(pipelineRepo PipelineRepository, eventPublisher EventPublisher) *PipelineService {
	return &PipelineService{
		pipelineRepo:   pipelineRepo,
		eventPublisher: eventPublisher,
	}
}

// CreatePipeline creates a new pipeline
func (s *PipelineService) CreatePipeline(ctx context.Context, input CreatePipelineInput) (*CreatePipelineOutput, error) {
	useCase := NewCreatePipelineUseCase(s.pipelineRepo, &NoOpInputValidator{}, s.eventPublisher)
	return useCase.Execute(ctx, input)
}

// GetPipeline gets a pipeline by ID
func (s *PipelineService) GetPipeline(ctx context.Context, input GetPipelineInput) (*GetPipelineOutput, error) {
	useCase := NewGetPipelineUseCase(s.pipelineRepo, &NoOpInputValidator{})
	return useCase.Execute(ctx, input)
}

// GetPipelineByName gets a pipeline by name
func (s *PipelineService) GetPipelineByName(ctx context.Context, input GetPipelineByNameInput) (*GetPipelineOutput, error) {
	useCase := NewGetPipelineByNameUseCase(s.pipelineRepo, &NoOpInputValidator{})
	return useCase.Execute(ctx, input)
}

// ListPipelines lists pipelines with criteria
func (s *PipelineService) ListPipelines(ctx context.Context, input ListPipelinesInput) (*ListPipelinesOutput, error) {
	useCase := NewListPipelinesUseCase(s.pipelineRepo, &NoOpInputValidator{})
	return useCase.Execute(ctx, input)
}

// AddStep adds a step to a pipeline
func (s *PipelineService) AddStep(ctx context.Context, input AddStepInput) (*AddStepOutput, error) {
	useCase := NewAddStepUseCase(s.pipelineRepo, &NoOpInputValidator{}, s.eventPublisher)
	return useCase.Execute(ctx, input)
}

// ExecutePipeline executes a pipeline
func (s *PipelineService) ExecutePipeline(ctx context.Context, input ExecutePipelineInput) (*ExecutePipelineOutput, error) {
	useCase := NewExecutePipelineUseCase(s.pipelineRepo, &NoOpInputValidator{}, s.eventPublisher)
	return useCase.Execute(ctx, input)
}

// DeletePipeline deletes a pipeline
func (s *PipelineService) DeletePipeline(ctx context.Context, input DeletePipelineInput) error {
	useCase := NewDeletePipelineUseCase(s.pipelineRepo, &NoOpInputValidator{}, s.eventPublisher)
	return useCase.Execute(ctx, input)
}

// NoOpInputValidator provides a no-op implementation for input validation
type NoOpInputValidator struct{}

func (v *NoOpInputValidator) ValidateCreatePipelineInput(input CreatePipelineInput) error { return nil }
func (v *NoOpInputValidator) ValidateCreatePipeline(input CreatePipelineInput) error      { return nil }
func (v *NoOpInputValidator) ValidateUpdatePipelineInput(input UpdatePipelineInput) error { return nil }
func (v *NoOpInputValidator) ValidateDeletePipelineInput(input DeletePipelineInput) error { return nil }
func (v *NoOpInputValidator) ValidateGetPipelineInput(input GetPipelineInput) error       { return nil }
func (v *NoOpInputValidator) ValidateGetPipeline(input GetPipelineInput) error            { return nil }
func (v *NoOpInputValidator) ValidateListPipelinesInput(input ListPipelinesInput) error   { return nil }
func (v *NoOpInputValidator) ValidateListPipelines(input ListPipelinesInput) error        { return nil }
func (v *NoOpInputValidator) ValidateGetPipelineByNameInput(input GetPipelineByNameInput) error {
	return nil
}
func (v *NoOpInputValidator) ValidateGetPipelineByName(input GetPipelineByNameInput) error {
	return nil
}
func (v *NoOpInputValidator) ValidateAddStepInput(input AddStepInput) error { return nil }
func (v *NoOpInputValidator) ValidateAddStep(input AddStepInput) error      { return nil }
func (v *NoOpInputValidator) ValidateExecutePipelineInput(input ExecutePipelineInput) error {
	return nil
}
func (v *NoOpInputValidator) ValidateExecutePipeline(input ExecutePipelineInput) error { return nil }
func (v *NoOpInputValidator) ValidateDeletePipeline(input DeletePipelineInput) error   { return nil }

// HealthCheck performs health checks on the pipeline service
func (s *PipelineService) HealthCheck(ctx context.Context) error {
	// Check if we can perform basic operations
	_, _, err := s.pipelineRepo.List(ctx, ListCriteria{Limit: 1, Offset: 0})
	if err != nil {
		return fmt.Errorf("pipeline repository health check failed: %w", err)
	}
	return nil
}

// GetRepository returns the underlying repository for direct access
func (s *PipelineService) GetRepository() PipelineRepository {
	return s.pipelineRepo
}

// GetEventPublisher returns the event publisher for direct access
func (s *PipelineService) GetEventPublisher() EventPublisher {
	return s.eventPublisher
}
