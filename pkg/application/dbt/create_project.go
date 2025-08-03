package dbt

import (
	"context"

	"github.com/flext-sh/flext/pkg/domain/dbt/domain/entities"
)

// CreateProjectUseCase handles dbt project creation following Clean Architecture
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

// CreateProjectInput represents the input for creating a dbt project
type CreateProjectInput struct {
	Name              string                 `json:"name" validate:"required,min=1,max=100"`
	Version           string                 `json:"version" validate:"required"`
	Description       string                 `json:"description" validate:"max=500"`
	ProfileName       string                 `json:"profile_name" validate:"required"`
	ProjectDir        string                 `json:"project_dir" validate:"required"`
	RequireDbtVersion string                 `json:"require_dbt_version,omitempty"`
	Vars              map[string]interface{} `json:"vars,omitempty"`
	ModelPaths        []string               `json:"model_paths,omitempty"`
	AnalysisPaths     []string               `json:"analysis_paths,omitempty"`
	TestPaths         []string               `json:"test_paths,omitempty"`
	SeedPaths         []string               `json:"seed_paths,omitempty"`
	MacroPaths        []string               `json:"macro_paths,omitempty"`
	SnapshotPaths     []string               `json:"snapshot_paths,omitempty"`
	TargetPath        string                 `json:"target_path,omitempty"`
	LogPath           string                 `json:"log_path,omitempty"`
	PackagesPath      string                 `json:"packages_path,omitempty"`
}

// CreateProjectOutput represents the output after creating a dbt project
type CreateProjectOutput struct {
	ID                string `json:"id"`
	Name              string `json:"name"`
	Version           string `json:"version"`
	Description       string `json:"description"`
	ProfileName       string `json:"profile_name"`
	ProjectDir        string `json:"project_dir"`
	RequireDbtVersion string `json:"require_dbt_version,omitempty"`
	IsActive          bool   `json:"is_active"`
	LastRunStatus     string `json:"last_run_status"`
	CreatedAt         string `json:"created_at"`
}

// Execute performs the dbt project creation
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

	// Create dbt project entity
	project, err := entities.NewDbtProject(
		input.Name,
		input.Version,
		input.ProfileName,
		input.ProjectDir,
	)
	if err != nil {
		return nil, err
	}

	// Set optional fields
	if input.Description != "" {
		project.Description = input.Description
	}
	if input.RequireDbtVersion != "" {
		project.RequireDbtVersion = input.RequireDbtVersion
	}
	if input.Vars != nil {
		project.Vars = input.Vars
	}

	// Set paths if provided
	if len(input.ModelPaths) > 0 {
		project.ModelPaths = input.ModelPaths
	}
	if len(input.AnalysisPaths) > 0 {
		project.AnalysisPaths = input.AnalysisPaths
	}
	if len(input.TestPaths) > 0 {
		project.TestPaths = input.TestPaths
	}
	if len(input.SeedPaths) > 0 {
		project.SeedPaths = input.SeedPaths
	}
	if len(input.MacroPaths) > 0 {
		project.MacroPaths = input.MacroPaths
	}
	if len(input.SnapshotPaths) > 0 {
		project.SnapshotPaths = input.SnapshotPaths
	}
	if input.TargetPath != "" {
		project.TargetPath = input.TargetPath
	}
	if input.LogPath != "" {
		project.LogPath = input.LogPath
	}
	if input.PackagesPath != "" {
		project.PackagesPath = input.PackagesPath
	}

	// Validate project configuration
	if err := project.ValidateConfiguration(); err != nil {
		return nil, err
	}

	// Save project
	if err := uc.repo.Save(ctx, project); err != nil {
		return nil, err
	}

	// Publish domain events
	for _, event := range project.GetEvents() {
		if err := uc.events.Publish(ctx, event); err != nil {
			// Log error but don't fail the operation
			// In a real implementation, you might want to use a proper logger
		}
	}

	// Clear events after publishing
	project.ClearEvents()

	// Return result
	return &CreateProjectOutput{
		ID:                project.ID.String(),
		Name:              project.Name,
		Version:           project.Version,
		Description:       project.Description,
		ProfileName:       project.ProfileName,
		ProjectDir:        project.ProjectDir,
		RequireDbtVersion: project.RequireDbtVersion,
		IsActive:          project.IsActive,
		LastRunStatus:     string(project.LastRunStatus),
		CreatedAt:         project.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}, nil
}
