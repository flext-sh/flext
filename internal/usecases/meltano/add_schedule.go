package meltano

import (
	"context"
	"github.com/flext/flexcore/internal/bounded_contexts/meltano/domain/entities"
	"github.com/google/uuid"
)

// AddScheduleUseCase handles adding schedules to Meltano projects
type AddScheduleUseCase struct {
	repo      ProjectRepository
	validator InputValidator
	events    EventPublisher
}

// NewAddScheduleUseCase creates a new add schedule use case
func NewAddScheduleUseCase(repo ProjectRepository, validator InputValidator, events EventPublisher) *AddScheduleUseCase {
	return &AddScheduleUseCase{
		repo:      repo,
		validator: validator,
		events:    events,
	}
}

// AddScheduleInput represents the input for adding a schedule
type AddScheduleInput struct {
	ProjectID uuid.UUID `json:"project_id" validate:"required"`
	Name      string    `json:"name" validate:"required,min=1,max=100"`
	Job       string    `json:"job" validate:"required"`
	Interval  string    `json:"interval" validate:"required"`
	Enabled   bool      `json:"enabled"`
}

// AddScheduleOutput represents the output of adding a schedule
type AddScheduleOutput struct {
	ID        string `json:"id"`
	ProjectID string `json:"project_id"`
	Name      string `json:"name"`
	Job       string `json:"job"`
	Interval  string `json:"interval"`
	Enabled   bool   `json:"enabled"`
	CreatedAt string `json:"created_at"`
}

// Execute adds a schedule to a project
func (uc *AddScheduleUseCase) Execute(ctx context.Context, input AddScheduleInput) (*AddScheduleOutput, error) {
	// Validate input
	if err := uc.validator.ValidateAddSchedule(input); err != nil {
		return nil, err
	}

	// Get the project
	project, err := uc.repo.FindByID(ctx, input.ProjectID)
	if err != nil {
		return nil, err
	}
	if project == nil {
		return nil, ErrProjectNotFound
	}

	// Create schedule
	schedule := entities.MeltanoSchedule{
		ID:       uuid.New(),
		Name:     input.Name,
		Job:      input.Job,
		Interval: input.Interval,
		Enabled:  input.Enabled,
	}

	// Add schedule to project
	project.Schedules = append(project.Schedules, &schedule)

	// Save the updated project
	if err := uc.repo.Save(ctx, project); err != nil {
		return nil, err
	}

	// Publish event
	event := ScheduleAddedEvent{
		ProjectID:    input.ProjectID,
		ScheduleID:   schedule.ID,
		ScheduleName: schedule.Name,
		Job:          schedule.Job,
	}

	if err := uc.events.Publish(ctx, event); err != nil {
		// Log error but don't fail
	}

	return &AddScheduleOutput{
		ID:        schedule.ID.String(),
		ProjectID: input.ProjectID.String(),
		Name:      schedule.Name,
		Job:       schedule.Job,
		Interval:  schedule.Interval,
		Enabled:   schedule.Enabled,
		CreatedAt: "2024-01-01T00:00:00Z", // In real implementation, get from schedule
	}, nil
}
