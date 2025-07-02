package commands

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/google/uuid"
)

// RegisterPluginCommand representa o comando para registrar um plugin
type RegisterPluginCommand struct {
	Name         string                 `json:"name" validate:"required,max=100"`
	Type         string                 `json:"type" validate:"required,oneof=source target transformer utility"`
	Version      string                 `json:"version" validate:"required"`
	Description  string                 `json:"description,omitempty"`
	Author       string                 `json:"author,omitempty"`
	EntryPoint   string                 `json:"entry_point" validate:"required"`
	Ports        []PortDefinition       `json:"ports,omitempty"`
	Dependencies []string               `json:"dependencies,omitempty"`
	Config       map[string]interface{} `json:"configuration,omitempty"`
}

// PortDefinition define uma porta do plugin
type PortDefinition struct {
	Name        string                 `json:"name" validate:"required"`
	Type        string                 `json:"type" validate:"required"`
	Required    bool                   `json:"required"`
	Description string                 `json:"description,omitempty"`
	Schema      map[string]interface{} `json:"schema,omitempty"`
}

// RegisterPluginResult resultado do comando
type RegisterPluginResult struct {
	ID uuid.UUID `json:"id"`
}

// RegisterPluginHandler manipula o comando de registro de plugin
type RegisterPluginHandler struct {
	repo      ports.PluginRepository
	publisher ports.EventPublisher
}

// NewRegisterPluginHandler cria um novo handler
func NewRegisterPluginHandler(repo ports.PluginRepository, publisher ports.EventPublisher) *RegisterPluginHandler {
	return &RegisterPluginHandler{
		repo:      repo,
		publisher: publisher,
	}
}

// Handle executa o comando
func (h *RegisterPluginHandler) Handle(ctx context.Context, cmd RegisterPluginCommand) (*RegisterPluginResult, error) {
	// Verificar se plugin já existe
	exists, err := h.repo.ExistsByName(ctx, cmd.Name)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, NewPluginAlreadyExistsError(cmd.Name)
	}

	// Criar o agregado plugin
	pluginType := entities.PluginType(cmd.Type)
	plugin, err := entities.NewPlugin(cmd.Name, cmd.Version, cmd.EntryPoint, pluginType)
	if err != nil {
		return nil, err
	}

	// Configurar propriedades opcionais
	plugin.Description = cmd.Description
	plugin.Author = cmd.Author

	// Adicionar portas
	for _, portDef := range cmd.Ports {
		port := entities.Port{
			Name:        portDef.Name,
			Type:        portDef.Type,
			Required:    portDef.Required,
			Description: portDef.Description,
			Schema:      portDef.Schema,
		}
		if err := plugin.AddPort(port); err != nil {
			return nil, err
		}
	}

	// Adicionar dependências se fornecidas
	for _, dep := range cmd.Dependencies {
		plugin.AddDependency(dep)
	}

	// Atualizar configuração se fornecida
	if cmd.Config != nil {
		plugin.UpdateConfiguration(cmd.Config)
	}

	// Persistir no repositório
	if err := h.repo.Save(ctx, plugin); err != nil {
		return nil, err
	}

	// Publicar eventos de domínio
	events := plugin.GetEvents()
	if len(events) > 0 {
		eventInterfaces := make([]interface{}, len(events))
		for i, event := range events {
			eventInterfaces[i] = event
		}
		if err := h.publisher.PublishEvents(ctx, eventInterfaces...); err != nil {
			return nil, err
		}
		plugin.ClearEvents()
	}

	return &RegisterPluginResult{ID: plugin.ID}, nil
}

// PluginAlreadyExistsError erro quando plugin já existe
type PluginAlreadyExistsError struct {
	Name string
}

func (e PluginAlreadyExistsError) Error() string {
	return "plugin " + e.Name + " already exists"
}

func NewPluginAlreadyExistsError(name string) PluginAlreadyExistsError {
	return PluginAlreadyExistsError{Name: name}
}
