package meltano

import (
	"context"
)

// ListProjectsUseCase handles listing Meltano projects
type ListProjectsUseCase struct {
	repo      ProjectRepository
	validator InputValidator
}

// NewListProjectsUseCase creates a new list projects use case
func NewListProjectsUseCase(repo ProjectRepository, validator InputValidator) *ListProjectsUseCase {
	return &ListProjectsUseCase{
		repo:      repo,
		validator: validator,
	}
}

// ListProjectsInput represents the input for listing projects
type ListProjectsInput struct {
	Limit    int    `json:"limit"`
	Offset   int    `json:"offset"`
	OrderBy  string `json:"order_by"`
	OrderDir string `json:"order_dir"`
}

// ListProjectsOutput represents the output of listing projects
type ListProjectsOutput struct {
	Projects []ProjectSummary `json:"projects"`
	Total    int              `json:"total"`
}

// ProjectSummary represents a summary of a project
type ProjectSummary struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	Path        string `json:"path"`
	PluginCount int    `json:"plugin_count"`
	IsActive    bool   `json:"is_active"`
	CreatedAt   string `json:"created_at"`
	UpdatedAt   string `json:"updated_at"`
}

// Execute lists projects with pagination
func (uc *ListProjectsUseCase) Execute(ctx context.Context, input ListProjectsInput) (*ListProjectsOutput, error) {
	// Validate input
	if err := uc.validator.ValidateListProjects(input); err != nil {
		return nil, err
	}

	// Set defaults
	if input.Limit <= 0 {
		input.Limit = 50
	}
	if input.OrderBy == "" {
		input.OrderBy = "created_at"
	}
	if input.OrderDir == "" {
		input.OrderDir = "desc"
	}

	// Create criteria
	criteria := ListCriteria{
		Limit:    input.Limit,
		Offset:   input.Offset,
		OrderBy:  input.OrderBy,
		OrderDir: input.OrderDir,
	}

	// Get projects
	projects, total, err := uc.repo.List(ctx, criteria)
	if err != nil {
		return nil, err
	}

	// Convert to output format
	summaries := make([]ProjectSummary, len(projects))
	for i, project := range projects {
		summaries[i] = ProjectSummary{
			ID:          project.ID.String(),
			Name:        project.Name,
			Description: project.Description,
			Path:        project.RootPath,
			PluginCount: len(project.Plugins),
			IsActive:    project.Status == "active", // Convert status to boolean
			CreatedAt:   project.CreatedAt.Format("2006-01-02T15:04:05Z"),
			UpdatedAt:   project.UpdatedAt.Format("2006-01-02T15:04:05Z"),
		}
	}

	return &ListProjectsOutput{
		Projects: summaries,
		Total:    total,
	}, nil
}
