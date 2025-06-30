package application

import (
	"context"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/ports"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/domain/entities"
	"github.com/google/uuid"
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
	ID            uuid.UUID                 `json:"id"`
	Name          string                    `json:"name"`
	Type          string                    `json:"type"`
	Version       string                    `json:"version"`
	Description   string                    `json:"description"`
	Author        string                    `json:"author"`
	Status        string                    `json:"status"`
	EntryPoint    string                    `json:"entry_point"`
	Ports         []PortDTO                 `json:"ports"`
	Dependencies  []string                  `json:"dependencies"`
	Configuration map[string]interface{}    `json:"configuration"`
	Metadata      map[string]interface{}    `json:"metadata"`
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

	// Convert to DTOs
	pluginDTOs := make([]PluginDTO, len(plugins))
	for i, plugin := range plugins {
		pluginDTOs[i] = *s.convertToDTO(plugin)
	}

	return &ListPluginsResult{
		Plugins: pluginDTOs,
		Total:   total,
	}, nil
}

// Helper methods

func (s *PluginService) convertToDTO(plugin *entities.Plugin) *PluginDTO {
	// Convert ports
	ports := make([]PortDTO, len(plugin.Ports))
	for i, port := range plugin.Ports {
		ports[i] = PortDTO{
			Name:        port.Name,
			Type:        port.Type,
			Required:    port.Required,
			Description: port.Description,
			Schema:      port.Schema,
		}
	}

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
		Configuration: plugin.Config,
		Metadata:      plugin.Metadata,
	}
}