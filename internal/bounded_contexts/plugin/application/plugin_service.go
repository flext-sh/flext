package application

import (
	"context"
	"errors"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/google/uuid"
	"github.com/samber/lo"
)

// PluginService coordena operações do bounded context de plugin
type PluginService struct {
	// Command handlers
	registerPluginHandler *commands.RegisterPluginHandler

	// Dependencies
	repo      ports.PluginRepository
	publisher ports.EventPublisher
}

// NewPluginService cria um novo serviço de plugin
func NewPluginService(
	repo ports.PluginRepository,
	publisher ports.EventPublisher,
) *PluginService {
	return &PluginService{
		// Command handlers
		registerPluginHandler: commands.NewRegisterPluginHandler(repo, publisher),

		// Dependencies
		repo:      repo,
		publisher: publisher,
	}
}

// Commands

// RegisterPlugin executa o comando de registro de plugin
func (s *PluginService) RegisterPlugin(ctx context.Context, cmd commands.RegisterPluginCommand) (*commands.RegisterPluginResult, error) {
	return s.registerPluginHandler.Handle(ctx, cmd)
}

// Queries (Simple implementations for now)

// PluginDTO representa um plugin na resposta
type PluginDTO struct {
	ID            uuid.UUID              `json:"id"`
	Name          string                 `json:"name"`
	Type          string                 `json:"type"`
	Version       string                 `json:"version"`
	Description   string                 `json:"description"`
	Author        string                 `json:"author"`
	Status        string                 `json:"status"`
	EntryPoint    string                 `json:"entry_point"`
	Ports         []PortDTO              `json:"ports"`
	Dependencies  []string               `json:"dependencies"`
	Configuration map[string]interface{} `json:"configuration"`
	Metadata      map[string]interface{} `json:"metadata"`
}

// PortDTO representa uma porta na resposta
type PortDTO struct {
	Name        string                 `json:"name"`
	Type        string                 `json:"type"`
	Required    bool                   `json:"required"`
	Description string                 `json:"description"`
	Schema      map[string]interface{} `json:"schema,omitempty"`
}

// ListPluginsResult resultado da consulta de listagem
type ListPluginsResult struct {
	Plugins []PluginDTO `json:"plugins"`
	Total   int         `json:"total"`
}

// GetPlugin busca um plugin por ID
func (s *PluginService) GetPlugin(ctx context.Context, id uuid.UUID) (*PluginDTO, error) {
	plugin, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	return s.convertToDTO(plugin), nil
}

// ListPlugins lista plugins com filtros
func (s *PluginService) ListPlugins(ctx context.Context, limit, offset int, pluginType, status, author string) (*ListPluginsResult, error) {
	filter := ports.ListPluginsFilter{
		Limit:  limit,
		Offset: offset,
		Author: author,
	}

	// Parse plugin type
	if pluginType != "" {
		pt := entities.PluginType(pluginType)
		filter.Type = &pt
	}

	// Parse status
	if status != "" {
		ps := entities.PluginStatus(status)
		filter.Status = &ps
	}

	plugins, total, err := s.repo.List(ctx, filter)
	if err != nil {
		return nil, err
	}

	// Convert to DTOs using functional programming
	pluginDTOs := lo.Map(plugins, func(plugin *entities.Plugin, _ int) PluginDTO {
		return *s.convertToDTO(plugin)
	})

	return &ListPluginsResult{
		Plugins: pluginDTOs,
		Total:   total,
	}, nil
}

// UnregisterPlugin remove um plugin do sistema
func (s *PluginService) UnregisterPlugin(ctx context.Context, id uuid.UUID) error {
	// Verificar se o plugin existe
	plugin, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return err
	}

	// Verificar se o plugin pode ser removido (não está sendo usado)
	if plugin.Status == entities.PluginStatusActive {
		return errors.New("cannot unregister active plugin - deactivate it first")
	}

	// Remover do repositório
	return s.repo.Delete(ctx, id)
}

// UpdatePlugin atualiza as propriedades de um plugin
func (s *PluginService) UpdatePlugin(ctx context.Context, id uuid.UUID, updateData map[string]interface{}) (*PluginDTO, error) {
	plugin, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	if err := s.applyPluginUpdates(plugin, updateData); err != nil {
		return nil, err
	}

	if err := s.repo.Save(ctx, plugin); err != nil {
		return nil, err
	}

	if err := s.publishPluginEvents(ctx, plugin); err != nil {
		return nil, err
	}

	return s.convertToDTO(plugin), nil
}

// applyPluginUpdates applies the update data to the plugin
func (s *PluginService) applyPluginUpdates(plugin *entities.Plugin, updateData map[string]interface{}) error {
	s.updateBasicFields(plugin, updateData)

	if err := s.updatePluginStatus(plugin, updateData); err != nil {
		return err
	}

	s.updatePluginConfiguration(plugin, updateData)
	return nil
}

// updateBasicFields updates basic string fields of the plugin
func (s *PluginService) updateBasicFields(plugin *entities.Plugin, updateData map[string]interface{}) {
	if description, ok := updateData["description"].(string); ok {
		plugin.Description = description
	}

	if author, ok := updateData["author"].(string); ok {
		plugin.Author = author
	}
}

// updatePluginStatus updates the plugin status with proper transitions
func (s *PluginService) updatePluginStatus(plugin *entities.Plugin, updateData map[string]interface{}) error {
	status, ok := updateData["status"].(string)
	if !ok {
		return nil
	}

	newStatus := entities.PluginStatus(status)
	switch newStatus {
	case entities.PluginStatusActive:
		return plugin.Activate()
	case entities.PluginStatusInactive:
		plugin.Deactivate()
		return nil
	case entities.PluginStatusFailed:
		reason := s.getFailureReason(updateData)
		plugin.MarkAsFailed(reason)
		return nil
	}
	return nil
}

// getFailureReason extracts failure reason from update data
func (s *PluginService) getFailureReason(updateData map[string]interface{}) string {
	if reason, ok := updateData["failure_reason"].(string); ok && reason != "" {
		return reason
	}
	return "manually set to failed"
}

// updatePluginConfiguration updates the plugin configuration
func (s *PluginService) updatePluginConfiguration(plugin *entities.Plugin, updateData map[string]interface{}) {
	if config, ok := updateData["configuration"].(map[string]interface{}); ok {
		plugin.UpdateConfiguration(config)
	}
}

// publishPluginEvents publishes all pending events from the plugin
func (s *PluginService) publishPluginEvents(ctx context.Context, plugin *entities.Plugin) error {
	events := plugin.GetEvents()
	if len(events) == 0 {
		return nil
	}

	eventInterfaces := make([]interface{}, len(events))
	for i, event := range events {
		eventInterfaces[i] = event
	}

	if err := s.publisher.PublishEvents(ctx, eventInterfaces...); err != nil {
		return err
	}

	plugin.ClearEvents()
	return nil
}

// Helper methods

func (s *PluginService) convertToDTO(plugin *entities.Plugin) *PluginDTO {
	// Convert ports using functional programming
	ports := lo.Map(plugin.Ports, func(port entities.Port, _ int) PortDTO {
		return PortDTO{
			Name:        port.Name,
			Type:        port.Type,
			Required:    port.Required,
			Description: port.Description,
			Schema:      port.Schema,
		}
	})

	return &PluginDTO{
		ID:            plugin.ID,
		Name:          plugin.Name,
		Type:          string(plugin.Type),
		Version:       plugin.Version,
		Description:   plugin.Description,
		Author:        plugin.Author,
		Status:        string(plugin.Status),
		EntryPoint:    plugin.EntryPoint,
		Ports:         ports,
		Dependencies:  plugin.Dependencies,
		Configuration: plugin.Configuration,
		Metadata:      plugin.Metadata,
	}
}
