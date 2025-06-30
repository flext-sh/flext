package commands

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/domain/entities"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/ports"
	"github.com/google/uuid"
)

// CreatePipelineCommand representa o comando para criar um pipeline
type CreatePipelineCommand struct {
	Name        string                 `json:"name" validate:"required,max=100"`
	Description string                 `json:"description" validate:"max=500"`
	Tags        []string               `json:"tags,omitempty"`
	Config      map[string]interface{} `json:"configuration,omitempty"`
}

// CreatePipelineResult resultado do comando
type CreatePipelineResult struct {
	ID uuid.UUID `json:"id"`
}

// CreatePipelineHandler manipula o comando de criação de pipeline
type CreatePipelineHandler struct {
	repo      ports.PipelineRepository
	publisher ports.EventPublisher
}

// NewCreatePipelineHandler cria um novo handler
func NewCreatePipelineHandler(repo ports.PipelineRepository, publisher ports.EventPublisher) *CreatePipelineHandler {
	return &CreatePipelineHandler{
		repo:      repo,
		publisher: publisher,
	}
}

// Handle executa o comando
func (h *CreatePipelineHandler) Handle(ctx context.Context, cmd CreatePipelineCommand) (*CreatePipelineResult, error) {
	// Criar o agregado pipeline
	pipeline, err := entities.NewPipeline(cmd.Name, cmd.Description)
	if err != nil {
		return nil, err
	}

	// Adicionar tags se fornecidas
	for _, tag := range cmd.Tags {
		pipeline.AddTag(tag)
	}

	// Atualizar configuração se fornecida
	if cmd.Config != nil {
		pipeline.UpdateConfiguration(cmd.Config)
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

	return &CreatePipelineResult{ID: pipeline.ID}, nil
}