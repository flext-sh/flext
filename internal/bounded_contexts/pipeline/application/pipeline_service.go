package application

import (
	"context"

	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/queries"
	"github.com/flext/flexcore/internal/bounded_contexts/pipeline/application/services"
	domainServices "github.com/flext/flexcore/internal/bounded_contexts/pipeline/domain/services"
)

// PipelineService coordinates pipeline operations
type PipelineService struct {
	createPipelineHandler *commands.CreatePipelineCommandHandler
	updatePipelineHandler *commands.UpdatePipelineCommandHandler
	addStepHandler        *commands.AddStepHandler
	executeHandler        *commands.ExecutePipelineHandler
	getPipelineHandler    *queries.GetPipelineHandler
	listPipelinesHandler  *queries.ListPipelinesHandler
	getStatusHandler      *commands.GetPipelineStatusHandler
	pausePipelineHandler  *commands.PausePipelineHandler
	resumePipelineHandler *commands.ResumePipelineHandler
	executionStatsService *services.PipelineExecutionStatsService
}

// NewPipelineService creates a new pipeline service
func NewPipelineService(
	repo ports.PipelineRepository,
	executor *domainServices.PipelineExecutor,
	executionStatsService *services.PipelineExecutionStatsService,
) *PipelineService {
	if repo == nil {
		panic("PipelineRepository cannot be nil")
	}
	if executor == nil {
		panic("PipelineExecutor cannot be nil")
	}
	// Allow nil for testing - create a placeholder service
	if executionStatsService == nil {
		executionStatsService = &services.PipelineExecutionStatsService{}
	}

	return &PipelineService{
		createPipelineHandler: commands.NewCreatePipelineCommandHandler(repo),
		updatePipelineHandler: commands.NewUpdatePipelineCommandHandler(repo),
		addStepHandler:        commands.NewAddStepHandler(repo),
		executeHandler:        commands.NewExecutePipelineHandler(repo, executor, executionStatsService),
		getPipelineHandler:    queries.NewGetPipelineHandler(repo),
		listPipelinesHandler:  queries.NewListPipelinesHandler(repo),
		getStatusHandler:      commands.NewGetPipelineStatusHandler(repo, executionStatsService),
		pausePipelineHandler:  commands.NewPausePipelineHandler(repo),
		resumePipelineHandler: commands.NewResumePipelineHandler(repo),
		executionStatsService: executionStatsService,
	}
}

// CreatePipeline creates a new pipeline
func (s *PipelineService) CreatePipeline(ctx context.Context, cmd commands.CreatePipelineCommand) (*commands.CreatePipelineResult, error) {
	return s.createPipelineHandler.Handle(ctx, &cmd)
}

// UpdatePipeline updates an existing pipeline
func (s *PipelineService) UpdatePipeline(ctx context.Context, cmd commands.UpdatePipelineCommand) (*commands.UpdatePipelineResult, error) {
	return s.updatePipelineHandler.Handle(ctx, &cmd)
}

// AddStep adds a step to a pipeline
func (s *PipelineService) AddStep(ctx context.Context, cmd commands.AddStepCommand) (*commands.AddStepResult, error) {
	return s.addStepHandler.Handle(ctx, cmd)
}

// ExecutePipeline executes a pipeline
func (s *PipelineService) ExecutePipeline(ctx context.Context, cmd commands.ExecutePipelineCommand) (*commands.ExecutePipelineResult, error) {
	return s.executeHandler.Handle(ctx, cmd)
}

// GetPipeline gets a pipeline by ID
func (s *PipelineService) GetPipeline(ctx context.Context, query queries.GetPipelineQuery) (*queries.PipelineDTO, error) {
	return s.getPipelineHandler.Handle(ctx, query)
}

// ListPipelines lists pipelines
func (s *PipelineService) ListPipelines(ctx context.Context, query queries.ListPipelinesQuery) (*queries.ListPipelinesResult, error) {
	return s.listPipelinesHandler.Handle(ctx, query)
}

// GetPipelineStatus gets pipeline status with health checks and metrics
func (s *PipelineService) GetPipelineStatus(ctx context.Context, cmd commands.GetPipelineStatusCommand) (*commands.GetPipelineStatusResult, error) {
	return s.getStatusHandler.Handle(ctx, cmd)
}

// PausePipeline pauses a running pipeline
func (s *PipelineService) PausePipeline(ctx context.Context, cmd commands.PausePipelineCommand) (*commands.PausePipelineResult, error) {
	return s.pausePipelineHandler.Handle(ctx, cmd)
}

// ResumePipeline resumes a paused pipeline
func (s *PipelineService) ResumePipeline(ctx context.Context, cmd commands.ResumePipelineCommand) (*commands.ResumePipelineResult, error) {
	return s.resumePipelineHandler.Handle(ctx, cmd)
}
