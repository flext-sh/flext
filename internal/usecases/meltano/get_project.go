package meltano

import (
	"context"
	"github.com/google/uuid"
)

// GetProjectUseCase handles retrieving a single Meltano project
type GetProjectUseCase struct {
	repo      ProjectRepository
	validator InputValidator
}

// NewGetProjectUseCase creates a new get project use case
func NewGetProjectUseCase(repo ProjectRepository, validator InputValidator) *GetProjectUseCase {
	return &GetProjectUseCase{
		repo:      repo,
		validator: validator,
	}
}

// GetProjectInput represents the input for getting a project
type GetProjectInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

// GetProjectOutput represents the output of getting a project
type GetProjectOutput struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name"`
	Description   string                 `json:"description"`
	Path          string                 `json:"path"`
	Configuration map[string]interface{} `json:"configuration"`
	Plugins       []PluginSummary        `json:"plugins"`
	Schedules     []ScheduleSummary      `json:"schedules"`
	Environments  []string               `json:"environments"`
	CreatedAt     string                 `json:"created_at"`
	UpdatedAt     string                 `json:"updated_at"`
}

// PluginSummary represents a summary of a plugin
type PluginSummary struct {
	Name        string `json:"name"`
	Type        string `json:"type"`
	Namespace   string `json:"namespace"`
	IsInstalled bool   `json:"is_installed"`
}

// ScheduleSummary represents a summary of a schedule
type ScheduleSummary struct {
	Name     string `json:"name"`
	Job      string `json:"job"`
	Interval string `json:"interval"`
	IsActive bool   `json:"is_active"`
}

// Execute retrieves a project by ID
func (uc *GetProjectUseCase) Execute(ctx context.Context, input GetProjectInput) (*GetProjectOutput, error) {
	// Validate input
	if err := uc.validator.ValidateGetProject(input); err != nil {
		return nil, err
	}

	// Get the project
	project, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	if project == nil {
		return nil, ErrProjectNotFound
	}

	// Convert plugins to summary format
	plugins := make([]PluginSummary, len(project.Plugins))
	for i, plugin := range project.Plugins {
		plugins[i] = PluginSummary{
			Name:        plugin.Name,
			Type:        string(plugin.Type),
			Namespace:   plugin.Namespace,
			IsInstalled: true, // Assume installed for simplicity
		}
	}

	// Convert schedules to summary format
	schedules := make([]ScheduleSummary, len(project.Schedules))
	for i, schedule := range project.Schedules {
		schedules[i] = ScheduleSummary{
			Name:     schedule.Name,
			Job:      schedule.Job,
			Interval: schedule.Interval,
			IsActive: schedule.Enabled,
		}
	}

	// Convert environments to string list
	envNames := make([]string, len(project.Environments))
	for i, env := range project.Environments {
		envNames[i] = env.Name
	}

	// Convert to output format
	return &GetProjectOutput{
		ID:            project.ID.String(),
		Name:          project.Name,
		Description:   project.Description,
		Path:          project.RootPath,
		Configuration: project.Settings,
		Plugins:       plugins,
		Schedules:     schedules,
		Environments:  envNames,
		CreatedAt:     project.CreatedAt.Format("2006-01-02T15:04:05Z"),
		UpdatedAt:     project.UpdatedAt.Format("2006-01-02T15:04:05Z"),
	}, nil
}
