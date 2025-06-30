package commands

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/google/uuid"
)

// AddStepCommand representa o comando para adicionar um passo ao pipeline
type AddStepCommand struct {
	PipelineID    uuid.UUID              `json:"pipeline_id" validate:"required"`
	Name          string                 `json:"name" validate:"required,max=100"`
	PluginID      uuid.UUID              `json:"plugin_id" validate:"required"`
	Configuration map[string]interface{} `json:"configuration,omitempty"`
	DependsOn     []uuid.UUID            `json:"depends_on,omitempty"`
}

// AddStepResult resultado do comando
type AddStepResult struct {
	StepID uuid.UUID `json:"step_id"`
}

// AddStepHandler manipula o comando de adição de passo
type AddStepHandler struct {
	repo      ports.PipelineRepository
	publisher ports.EventPublisher
}

// NewAddStepHandler cria um novo handler
func NewAddStepHandler(repo ports.PipelineRepository, publisher ports.EventPublisher) *AddStepHandler {
	return &AddStepHandler{
		repo:      repo,
		publisher: publisher,
	}
}

// Handle executa o comando
func (h *AddStepHandler) Handle(ctx context.Context, cmd AddStepCommand) (*AddStepResult, error) {
	// Buscar o pipeline
	pipeline, err := h.repo.GetByID(ctx, cmd.PipelineID)
	if err != nil {
		return nil, err
	}

	// Criar o passo
	step := entities.PipelineStep{
		Name:          cmd.Name,
		PluginID:      cmd.PluginID,
		Configuration: cmd.Configuration,
		DependsOn:     cmd.DependsOn,
	}

	// Adicionar o passo ao pipeline
	if err := pipeline.AddStep(step); err != nil {
		return nil, err
	}

	// Persistir no repositório
	if err := h.repo.Save(ctx, pipeline); err != nil {
		return nil, err
	}

	// Publicar eventos de domínio
	events := pipeline.GetEvents()
	if len(events) > 0 {
		eventInterfaces := make([]interface{}, len(events))
		for i, event := range events {
			eventInterfaces[i] = event
		}
		if err := h.publisher.PublishEvents(ctx, eventInterfaces...); err != nil {
			return nil, err
		}
		pipeline.ClearEvents()
	}

	// Obter o ID do último passo adicionado
	lastStep := pipeline.Steps[len(pipeline.Steps)-1]
	return &AddStepResult{StepID: lastStep.ID}, nil
}