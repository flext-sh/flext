package meltano

import (
	"context"
	"fmt"
	"path/filepath"

	"github.com/flext-sh/flext/internal/bounded_contexts/meltano/domain/entities"
	"github.com/google/uuid"
)

// CreateProjectUseCase handles Meltano project creation following Clean Architecture
type CreateProjectUseCase struct {
	repo      ProjectRepository
	validator InputValidator
	events    EventPublisher
}

// NewCreateProjectUseCase creates a new create project use case
func NewCreateProjectUseCase(
	repo ProjectRepository,
	validator InputValidator,
	events EventPublisher,
) *CreateProjectUseCase {
	return &CreateProjectUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// CreateProjectInput represents the input for creating a Meltano project
type CreateProjectInput struct {
	Name        string                 `json:"name" validate:"required,min=1,max=100"`
	DisplayName string                 `json:"display_name,omitempty"`
	Description string                 `json:"description,omitempty"`
	Version     string                 `json:"version,omitempty"`
	RootPath    string                 `json:"root_path" validate:"required"`
	Environment string                 `json:"environment,omitempty"`
	Settings    map[string]interface{} `json:"settings,omitempty"`
}

// CreateProjectOutput represents the output after creating a Meltano project
type CreateProjectOutput struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	DisplayName string                 `json:"display_name,omitempty"`
	Description string                 `json:"description,omitempty"`
	Version     string                 `json:"version,omitempty"`
	RootPath    string                 `json:"root_path"`
	ConfigPath  string                 `json:"config_path"`
	Environment string                 `json:"environment"`
	Status      string                 `json:"status"`
	Settings    map[string]interface{} `json:"settings,omitempty"`
	CreatedAt   string                 `json:"created_at"`
	UpdatedAt   string                 `json:"updated_at"`
}

// Execute performs the Meltano project creation
func (uc *CreateProjectUseCase) Execute(ctx context.Context, input CreateProjectInput) (*CreateProjectOutput, error) {
	// Validate input
	if err := uc.validator.ValidateCreateProject(input); err != nil {
		return nil, err
	}

	// Check if project already exists
	existingProject, err := uc.repo.FindByName(ctx, input.Name)
	if err != nil {
		return nil, err
	}
	if existingProject != nil {
		return nil, ErrProjectNameAlreadyExists
	}

	// Validate root path
	if !filepath.IsAbs(input.RootPath) {
		return nil, fmt.Errorf("root path must be absolute")
	}

	// Create Meltano project entity
	project := entities.NewMeltanoProject(input.Name, input.RootPath)

	// Set optional fields
	if input.DisplayName != "" {
		project.DisplayName = input.DisplayName
	}
	if input.Description != "" {
		project.Description = input.Description
	}
	if input.Version != "" {
		project.Version = input.Version
	}
	if input.Environment != "" {
		project.Environment = input.Environment
	}
	if input.Settings != nil {
		project.Settings = input.Settings
	}

	// Set config path
	project.ConfigPath = filepath.Join(input.RootPath, "meltano.yml")

	// Save project
	if err := uc.repo.Save(ctx, project); err != nil {
		return nil, err
	}

	// Publish domain events
	for _, event := range project.GetEvents() {
		if err := uc.events.Publish(ctx, event); err != nil {
			// Log error but don't fail the operation
		}
	}

	// Clear events after publishing
	project.ClearEvents()

	// Return result
	return &CreateProjectOutput{
		ID:          project.GetID().String(),
		Name:        project.Name,
		DisplayName: project.DisplayName,
		Description: project.Description,
		Version:     project.Version,
		RootPath:    project.RootPath,
		ConfigPath:  project.ConfigPath,
		Environment: project.Environment,
		Status:      string(project.Status),
		Settings:    project.Settings,
		CreatedAt:   project.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt:   project.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}, nil
}

// AddPluginUseCase handles adding plugins to Meltano projects
type AddPluginUseCase struct {
	repo      ProjectRepository
	validator InputValidator
	events    EventPublisher
}

// NewAddPluginUseCase creates a new add plugin use case
func NewAddPluginUseCase(
	repo ProjectRepository,
	validator InputValidator,
	events EventPublisher,
) *AddPluginUseCase {
	return &AddPluginUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// AddPluginInput represents the input for adding a plugin to a Meltano project
type AddPluginInput struct {
	ProjectID   uuid.UUID              `json:"project_id" validate:"required"`
	Name        string                 `json:"name" validate:"required"`
	Type        string                 `json:"type" validate:"required,oneof=extractors loaders transformers orchestrators files utilities"`
	Namespace   string                 `json:"namespace,omitempty"`
	Variant     string                 `json:"variant,omitempty"`
	PipURL      string                 `json:"pip_url,omitempty"`
	Settings    map[string]interface{} `json:"settings,omitempty"`
	Config      map[string]interface{} `json:"config,omitempty"`
	Extras      []string               `json:"extras,omitempty"`
	Commands    map[string]interface{} `json:"commands,omitempty"`
}

// AddPluginOutput represents the output after adding a plugin
type AddPluginOutput struct {
	ID        string                 `json:"id"`
	Name      string                 `json:"name"`
	Type      string                 `json:"type"`
	Namespace string                 `json:"namespace,omitempty"`
	Variant   string                 `json:"variant,omitempty"`
	PipURL    string                 `json:"pip_url,omitempty"`
	Settings  map[string]interface{} `json:"settings,omitempty"`
	Config    map[string]interface{} `json:"config,omitempty"`
	Extras    []string               `json:"extras,omitempty"`
	Commands  map[string]interface{} `json:"commands,omitempty"`
	CreatedAt string                 `json:"created_at"`
	UpdatedAt string                 `json:"updated_at"`
}

// Execute adds a plugin to a Meltano project
func (uc *AddPluginUseCase) Execute(ctx context.Context, input AddPluginInput) (*AddPluginOutput, error) {
	// Validate input
	if err := uc.validator.ValidateAddPlugin(input); err != nil {
		return nil, err
	}

	// Find project
	project, err := uc.repo.FindByID(ctx, input.ProjectID)
	if err != nil {
		return nil, err
	}
	if project == nil {
		return nil, ErrProjectNotFound
	}

	// Check if plugin already exists
	existingPlugin := project.GetPluginByName(input.Name)
	if existingPlugin != nil {
		return nil, ErrPluginNameAlreadyExists
	}

	// Convert string type to PluginType
	var pluginType entities.PluginType
	switch input.Type {
	case "extractors":
		pluginType = entities.PluginTypeExtractor
	case "loaders":
		pluginType = entities.PluginTypeLoader
	case "transformers":
		pluginType = entities.PluginTypeTransformer
	case "orchestrators":
		pluginType = entities.PluginTypeOrchestrator
	case "files":
		pluginType = entities.PluginTypeFileBundle
	case "utilities":
		pluginType = entities.PluginTypeUtility
	default:
		return nil, fmt.Errorf("invalid plugin type: %s", input.Type)
	}

	// Create plugin
	plugin := entities.NewMeltanoPlugin(input.Name, pluginType)
	if input.Namespace != "" {
		plugin.Namespace = input.Namespace
	}
	if input.Variant != "" {
		plugin.Variant = input.Variant
	}
	if input.PipURL != "" {
		plugin.PipURL = input.PipURL
	}
	if input.Settings != nil {
		plugin.Settings = input.Settings
	}
	if input.Config != nil {
		plugin.Config = input.Config
	}
	if input.Extras != nil {
		plugin.Extras = input.Extras
	}
	if input.Commands != nil {
		plugin.Commands = input.Commands
	}

	// Add plugin to project
	project.AddPlugin(plugin)

	// Save project
	if err := uc.repo.Save(ctx, project); err != nil {
		return nil, err
	}

	// Publish domain events
	for _, event := range project.GetEvents() {
		if err := uc.events.Publish(ctx, event); err != nil {
			// Log error but don't fail the operation
		}
	}

	// Clear events after publishing
	project.ClearEvents()

	// Return result
	return &AddPluginOutput{
		ID:        plugin.ID.String(),
		Name:      plugin.Name,
		Type:      string(plugin.Type),
		Namespace: plugin.Namespace,
		Variant:   plugin.Variant,
		PipURL:    plugin.PipURL,
		Settings:  plugin.Settings,
		Config:    plugin.Config,
		Extras:    plugin.Extras,
		Commands:  plugin.Commands,
		CreatedAt: plugin.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt: plugin.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}, nil
}

// RunPipelineUseCase handles running Meltano pipelines
type RunPipelineUseCase struct {
	repo      ProjectRepository
	runRepo   MeltanoRunRepository
	executor  MeltanoExecutor
	validator InputValidator
	events    EventPublisher
}

// NewRunPipelineUseCase creates a new run pipeline use case
func NewRunPipelineUseCase(
	repo ProjectRepository,
	runRepo MeltanoRunRepository,
	executor MeltanoExecutor,
	validator InputValidator,
	events EventPublisher,
) *RunPipelineUseCase {
	return &RunPipelineUseCase{
		repo:      repo,
		runRepo:   runRepo,
		executor:  executor,
		validator: validator,
		events:    events,
	}
}

// RunPipelineInput represents the input for running a Meltano pipeline
type RunPipelineInput struct {
	ProjectID   uuid.UUID              `json:"project_id" validate:"required"`
	Command     []string               `json:"command" validate:"required,min=1"`
	Environment string                 `json:"environment,omitempty"`
	Config      map[string]interface{} `json:"config,omitempty"`
}

// RunPipelineOutput represents the output after starting a pipeline run
type RunPipelineOutput struct {
	RunID       string                 `json:"run_id"`
	JobID       string                 `json:"job_id"`
	ProjectID   string                 `json:"project_id"`
	Command     []string               `json:"command"`
	Environment string                 `json:"environment"`
	Status      string                 `json:"status"`
	StartedAt   string                 `json:"started_at"`
	Config      map[string]interface{} `json:"config,omitempty"`
}

// Execute runs a Meltano pipeline
func (uc *RunPipelineUseCase) Execute(ctx context.Context, input RunPipelineInput) (*RunPipelineOutput, error) {
	// Validate input
	if err := uc.validator.ValidateRunPipeline(input); err != nil {
		return nil, err
	}

	// Find project
	project, err := uc.repo.FindByID(ctx, input.ProjectID)
	if err != nil {
		return nil, err
	}
	if project == nil {
		return nil, ErrProjectNotFound
	}

	// Check if project is active
	if project.Status != entities.ProjectStatusActive {
		return nil, ErrProjectNotActive
	}

	// Create run
	run := entities.NewMeltanoRun(input.ProjectID, input.Command)
	if input.Environment != "" {
		run.Environment = input.Environment
	}
	if input.Config != nil {
		run.Config = input.Config
	}

	// Save run
	if err := uc.runRepo.Save(ctx, run); err != nil {
		return nil, err
	}

	// Start execution asynchronously
	go func() {
		// Update project last run
		project.UpdateLastRun()
		uc.repo.Save(context.Background(), project)

		// Execute pipeline
		err := uc.executor.Execute(context.Background(), project, run)
		if err != nil {
			run.Fail(1, "", err.Error())
		}

		// Save run result
		uc.runRepo.Save(context.Background(), run)

		// Publish events
		for _, event := range run.GetEvents() {
			uc.events.Publish(context.Background(), event)
		}
	}()

	// Return result
	return &RunPipelineOutput{
		RunID:       run.RunID,
		JobID:       run.JobID,
		ProjectID:   run.ProjectID.String(),
		Command:     run.Command,
		Environment: run.Environment,
		Status:      string(run.Status),
		StartedAt:   run.StartedAt.Format("2006-01-02T15:04:05Z07:00"),
		Config:      run.Config,
	}, nil
}