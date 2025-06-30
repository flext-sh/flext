package application

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/queries"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
)

// PipelineService coordena operações do bounded context de pipeline
type PipelineService struct {
	// Command handlers
	createPipelineHandler *commands.CreatePipelineHandler
	addStepHandler        *commands.AddStepHandler
	
	// Query handlers
	getPipelineHandler   *queries.GetPipelineHandler
	listPipelinesHandler *queries.ListPipelinesHandler
}

// NewPipelineService cria um novo serviço de pipeline
func NewPipelineService(
	repo ports.PipelineRepository,
	publisher ports.EventPublisher,
) *PipelineService {
	return &PipelineService{
		// Command handlers
		createPipelineHandler: commands.NewCreatePipelineHandler(repo, publisher),
		addStepHandler:        commands.NewAddStepHandler(repo, publisher),
		
		// Query handlers
		getPipelineHandler:   queries.NewGetPipelineHandler(repo),
		listPipelinesHandler: queries.NewListPipelinesHandler(repo),
	}
}

// Commands

// CreatePipeline executa o comando de criação de pipeline
func (s *PipelineService) CreatePipeline(ctx context.Context, cmd commands.CreatePipelineCommand) (*commands.CreatePipelineResult, error) {
	return s.createPipelineHandler.Handle(ctx, cmd)
}

// AddStep executa o comando de adição de passo
func (s *PipelineService) AddStep(ctx context.Context, cmd commands.AddStepCommand) (*commands.AddStepResult, error) {
	return s.addStepHandler.Handle(ctx, cmd)
}

// Queries

// GetPipeline executa a consulta de pipeline por ID
func (s *PipelineService) GetPipeline(ctx context.Context, query queries.GetPipelineQuery) (*queries.PipelineDTO, error) {
	return s.getPipelineHandler.Handle(ctx, query)
}

// ListPipelines executa a consulta de listagem de pipelines
func (s *PipelineService) ListPipelines(ctx context.Context, query queries.ListPipelinesQuery) (*queries.ListPipelinesResult, error) {
	return s.listPipelinesHandler.Handle(ctx, query)
}