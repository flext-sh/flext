package commands

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/services"
	"github.com/google/uuid"
)

// ExecutePipelineCommand representa o comando para executar um pipeline
type ExecutePipelineCommand struct {
	PipelineID uuid.UUID              `json:"pipeline_id" validate:"required"`
	Context    map[string]interface{} `json:"context,omitempty"`
}

// ExecutePipelineResult resultado do comando
type ExecutePipelineResult struct {
	ExecutionID uuid.UUID `json:"execution_id"`
}

// ExecutePipelineHandler manipula o comando de execução de pipeline
type ExecutePipelineHandler struct {
	pipelineRepo ports.PipelineRepository
	pluginRepo   services.PluginRepository
	executor     *services.PipelineExecutor
	publisher    ports.EventPublisher
}

// NewExecutePipelineHandler cria um novo handler
func NewExecutePipelineHandler(
	pipelineRepo ports.PipelineRepository,
	pluginRepo services.PluginRepository,
	executor *services.PipelineExecutor,
	publisher ports.EventPublisher,
) *ExecutePipelineHandler {
	return &ExecutePipelineHandler{
		pipelineRepo: pipelineRepo,
		pluginRepo:   pluginRepo,
		executor:     executor,
		publisher:    publisher,
	}
}

// Handle executa o comando
func (h *ExecutePipelineHandler) Handle(ctx context.Context, cmd ExecutePipelineCommand) (*ExecutePipelineResult, error) {
	// Buscar o pipeline
	pipeline, err := h.pipelineRepo.GetByID(ctx, cmd.PipelineID)
	if err != nil {
		return nil, err
	}

	// Executar pipeline
	execution, err := h.executor.Execute(ctx, pipeline)
	if err != nil {
		return nil, err
	}

	// TODO: Persistir execução em repositório de execuções
	// TODO: Publicar evento de execução iniciada/completada

	return &ExecutePipelineResult{ExecutionID: execution.ID}, nil
}