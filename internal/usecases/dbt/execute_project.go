package dbt

import (
	"context"
	"time"

	"github.com/google/uuid"
)

// ExecuteProjectUseCase handles dbt project execution following Clean Architecture
type ExecuteProjectUseCase struct {
	repo      ProjectRepository
	executor  DbtExecutor
	validator InputValidator
	events    EventPublisher
}

// NewExecuteProjectUseCase creates a new execute project use case
func NewExecuteProjectUseCase(
	repo ProjectRepository,
	executor DbtExecutor,
	validator InputValidator,
	events EventPublisher,
) *ExecuteProjectUseCase {
	return &ExecuteProjectUseCase{
		repo:      repo,
		executor:  executor,
		validator: validator,
		events:    events,
	}
}

// Execute performs the dbt project execution
func (uc *ExecuteProjectUseCase) Execute(ctx context.Context, input ExecuteProjectInput) (*ExecutionResult, error) {
	// Validate input
	if err := uc.validator.ValidateExecuteProject(input); err != nil {
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
	if !project.IsActive {
		return nil, ErrProjectNotActive
	}

	// Execute command based on type
	var result *ExecutionResult
	switch input.Command {
	case "run":
		result, err = uc.executor.Run(ctx, project, &input.Context)
	case "test":
		result, err = uc.executor.Test(ctx, project, &input.Context)
	case "compile":
		result, err = uc.executor.Compile(ctx, project, &input.Context)
	case "snapshot":
		result, err = uc.executor.Snapshot(ctx, project, &input.Context)
	case "seed":
		result, err = uc.executor.Seed(ctx, project, &input.Context)
	case "docs":
		result, err = uc.executor.Docs(ctx, project, &input.Context)
	case "source":
		result, err = uc.executor.Source(ctx, project, &input.Context)
	case "clean":
		err = uc.executor.Clean(ctx, project)
		if err == nil {
			result = &ExecutionResult{
				ID:          uuid.New(),
				ProjectID:   project.ID,
				Command:     input.Command,
				Status:      "success",
				StartedAt:   time.Now().Format(time.RFC3339),
				CompletedAt: time.Now().Format(time.RFC3339),
				Stats: ExecutionStats{
					ExecutionTime: 0.1,
				},
			}
		}
	case "deps":
		err = uc.executor.Deps(ctx, project)
		if err == nil {
			result = &ExecutionResult{
				ID:          uuid.New(),
				ProjectID:   project.ID,
				Command:     input.Command,
				Status:      "success",
				StartedAt:   time.Now().Format(time.RFC3339),
				CompletedAt: time.Now().Format(time.RFC3339),
				Stats: ExecutionStats{
					ExecutionTime: 0.5,
				},
			}
		}
	default:
		return nil, ErrInvalidInput
	}

	if err != nil {
		// Update project status on failure
		if input.Command == "run" || input.Command == "test" {
			project.UpdateRunStatus("error")
			uc.repo.Save(ctx, project)
		}
		return nil, err
	}

	// Update project status on success
	if input.Command == "run" || input.Command == "test" {
		project.UpdateRunStatus("success")
		if err := uc.repo.Save(ctx, project); err != nil {
			// Log error but don't fail the operation
		}
	}

	// Publish domain events
	for _, event := range project.GetEvents() {
		if err := uc.events.Publish(ctx, event); err != nil {
			// Log error but don't fail the operation
		}
	}

	// Clear events after publishing
	project.ClearEvents()

	return result, nil
}

// GetProjectUseCase handles retrieving a single dbt project
type GetProjectUseCase struct {
	repo ProjectRepository
}

// NewGetProjectUseCase creates a new get project use case
func NewGetProjectUseCase(repo ProjectRepository) *GetProjectUseCase {
	return &GetProjectUseCase{
		repo: repo,
	}
}

// GetProjectInput represents input for getting a project
type GetProjectInput struct {
	ID uuid.UUID `json:"id" validate:"required"`
}

// GetProjectOutput represents output for getting a project
type GetProjectOutput struct {
	ID                string                 `json:"id"`
	Name              string                 `json:"name"`
	Version           string                 `json:"version"`
	Description       string                 `json:"description"`
	ProfileName       string                 `json:"profile_name"`
	ProjectDir        string                 `json:"project_dir"`
	RequireDbtVersion string                 `json:"require_dbt_version,omitempty"`
	IsActive          bool                   `json:"is_active"`
	LastRun           string                 `json:"last_run,omitempty"`
	LastRunStatus     string                 `json:"last_run_status"`
	ModelPaths        []string               `json:"model_paths"`
	AnalysisPaths     []string               `json:"analysis_paths"`
	TestPaths         []string               `json:"test_paths"`
	SeedPaths         []string               `json:"seed_paths"`
	MacroPaths        []string               `json:"macro_paths"`
	SnapshotPaths     []string               `json:"snapshot_paths"`
	TargetPath        string                 `json:"target_path"`
	LogPath           string                 `json:"log_path"`
	PackagesPath      string                 `json:"packages_path"`
	Vars              map[string]interface{} `json:"vars"`
	Packages          []interface{}          `json:"packages"`
	Sources           []interface{}          `json:"sources"`
	CreatedAt         string                 `json:"created_at"`
	UpdatedAt         string                 `json:"updated_at"`
}

// Execute retrieves a dbt project
func (uc *GetProjectUseCase) Execute(ctx context.Context, input GetProjectInput) (*GetProjectOutput, error) {
	// Find project
	project, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	if project == nil {
		return nil, ErrProjectNotFound
	}

	// Convert to output
	output := &GetProjectOutput{
		ID:                project.ID.String(),
		Name:              project.Name,
		Version:           project.Version,
		Description:       project.Description,
		ProfileName:       project.ProfileName,
		ProjectDir:        project.ProjectDir,
		RequireDbtVersion: project.RequireDbtVersion,
		IsActive:          project.IsActive,
		LastRunStatus:     string(project.LastRunStatus),
		ModelPaths:        project.ModelPaths,
		AnalysisPaths:     project.AnalysisPaths,
		TestPaths:         project.TestPaths,
		SeedPaths:         project.SeedPaths,
		MacroPaths:        project.MacroPaths,
		SnapshotPaths:     project.SnapshotPaths,
		TargetPath:        project.TargetPath,
		LogPath:           project.LogPath,
		PackagesPath:      project.PackagesPath,
		Vars:              project.Vars,
		CreatedAt:         project.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		UpdatedAt:         project.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
	}

	if project.LastRun != nil {
		output.LastRun = project.LastRun.Format("2006-01-02T15:04:05Z07:00")
	}

	// Convert packages to interface{}
	packages := make([]interface{}, len(project.Packages))
	for i, pkg := range project.Packages {
		packages[i] = pkg
	}
	output.Packages = packages

	// Convert sources to interface{}
	sources := make([]interface{}, len(project.Sources))
	for i, source := range project.Sources {
		sources[i] = source
	}
	output.Sources = sources

	return output, nil
}

// ListProjectsUseCase handles listing dbt projects
type ListProjectsUseCase struct {
	repo ProjectRepository
}

// NewListProjectsUseCase creates a new list projects use case
func NewListProjectsUseCase(repo ProjectRepository) *ListProjectsUseCase {
	return &ListProjectsUseCase{
		repo: repo,
	}
}

// ListProjectsInput represents input for listing projects
type ListProjectsInput struct {
	Limit       int    `json:"limit"`
	Offset      int    `json:"offset"`
	Active      *bool  `json:"active,omitempty"`
	ProfileName string `json:"profile_name,omitempty"`
	NameFilter  string `json:"name_filter,omitempty"`
	OrderBy     string `json:"order_by,omitempty"`
	OrderDir    string `json:"order_dir,omitempty"`
}

// ListProjectsOutput represents output for listing projects
type ListProjectsOutput struct {
	Projects []GetProjectOutput `json:"projects"`
	Total    int                `json:"total"`
	Limit    int                `json:"limit"`
	Offset   int                `json:"offset"`
}

// Execute lists dbt projects
func (uc *ListProjectsUseCase) Execute(ctx context.Context, input ListProjectsInput) (*ListProjectsOutput, error) {
	// Set defaults
	if input.Limit <= 0 {
		input.Limit = 20
	}
	if input.Offset < 0 {
		input.Offset = 0
	}
	if input.OrderBy == "" {
		input.OrderBy = "created_at"
	}
	if input.OrderDir == "" {
		input.OrderDir = "desc"
	}

	// Build criteria
	criteria := ListCriteria{
		Limit:       input.Limit,
		Offset:      input.Offset,
		Active:      input.Active,
		ProfileName: input.ProfileName,
		NameFilter:  input.NameFilter,
		OrderBy:     input.OrderBy,
		OrderDir:    input.OrderDir,
	}

	// Get projects
	projects, total, err := uc.repo.List(ctx, criteria)
	if err != nil {
		return nil, err
	}

	// Convert to output
	projectOutputs := make([]GetProjectOutput, len(projects))
	for i, project := range projects {
		output := GetProjectOutput{
			ID:                project.ID.String(),
			Name:              project.Name,
			Version:           project.Version,
			Description:       project.Description,
			ProfileName:       project.ProfileName,
			ProjectDir:        project.ProjectDir,
			RequireDbtVersion: project.RequireDbtVersion,
			IsActive:          project.IsActive,
			LastRunStatus:     string(project.LastRunStatus),
			ModelPaths:        project.ModelPaths,
			AnalysisPaths:     project.AnalysisPaths,
			TestPaths:         project.TestPaths,
			SeedPaths:         project.SeedPaths,
			MacroPaths:        project.MacroPaths,
			SnapshotPaths:     project.SnapshotPaths,
			TargetPath:        project.TargetPath,
			LogPath:           project.LogPath,
			PackagesPath:      project.PackagesPath,
			Vars:              project.Vars,
			CreatedAt:         project.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
			UpdatedAt:         project.UpdatedAt.Format("2006-01-02T15:04:05Z07:00"),
		}

		if project.LastRun != nil {
			output.LastRun = project.LastRun.Format("2006-01-02T15:04:05Z07:00")
		}

		// Convert packages and sources
		packages := make([]interface{}, len(project.Packages))
		for j, pkg := range project.Packages {
			packages[j] = pkg
		}
		output.Packages = packages

		sources := make([]interface{}, len(project.Sources))
		for j, source := range project.Sources {
			sources[j] = source
		}
		output.Sources = sources

		projectOutputs[i] = output
	}

	return &ListProjectsOutput{
		Projects: projectOutputs,
		Total:    total,
		Limit:    input.Limit,
		Offset:   input.Offset,
	}, nil
}
