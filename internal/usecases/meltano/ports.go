package meltano

import (
	"context"
	"errors"

	"github.com/flext-sh/flext/internal/bounded_contexts/meltano/domain/entities"
	"github.com/google/uuid"
)

// ProjectRepository defines the interface for Meltano project persistence
// This interface is declared by the use case layer (Dependency Inversion)
type ProjectRepository interface {
	Save(ctx context.Context, project *entities.MeltanoProject) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.MeltanoProject, error)
	FindByName(ctx context.Context, name string) (*entities.MeltanoProject, error)
	ExistsByName(ctx context.Context, name string) (bool, error)
	List(ctx context.Context, criteria ListCriteria) ([]*entities.MeltanoProject, int, error)
	Delete(ctx context.Context, id uuid.UUID) error
	FindByStatus(ctx context.Context, status entities.ProjectStatus) ([]*entities.MeltanoProject, error)
	FindActiveProjects(ctx context.Context) ([]*entities.MeltanoProject, error)
}

// MeltanoRunRepository defines the interface for Meltano run persistence
type MeltanoRunRepository interface {
	Save(ctx context.Context, run *entities.MeltanoRun) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.MeltanoRun, error)
	FindByRunID(ctx context.Context, runID string) (*entities.MeltanoRun, error)
	FindByProjectID(ctx context.Context, projectID uuid.UUID, criteria RunListCriteria) ([]*entities.MeltanoRun, int, error)
	List(ctx context.Context, criteria RunListCriteria) ([]*entities.MeltanoRun, int, error)
	Delete(ctx context.Context, id uuid.UUID) error
	FindActiveRuns(ctx context.Context) ([]*entities.MeltanoRun, error)
	FindByStatus(ctx context.Context, status entities.RunStatus) ([]*entities.MeltanoRun, error)
}

// EventPublisher defines the interface for publishing domain events
type EventPublisher interface {
	Publish(ctx context.Context, event interface{}) error
}

// InputValidator defines the interface for validating use case inputs
type InputValidator interface {
	ValidateCreateProject(input CreateProjectInput) error
	ValidateUpdateProject(input UpdateProjectInput) error
	ValidateAddPlugin(input AddPluginInput) error
	ValidateRunPipeline(input RunPipelineInput) error
	ValidateAddSchedule(input AddScheduleInput) error
	ValidateGetProject(input GetProjectInput) error
	ValidateListProjects(input ListProjectsInput) error
	ValidateDeleteProject(input DeleteProjectInput) error
}

// MeltanoExecutor defines the interface for executing Meltano commands
type MeltanoExecutor interface {
	Execute(ctx context.Context, project *entities.MeltanoProject, run *entities.MeltanoRun) error
	Install(ctx context.Context, project *entities.MeltanoProject, pluginName string) error
	Invoke(ctx context.Context, project *entities.MeltanoProject, pluginName string, args []string) error
	Test(ctx context.Context, project *entities.MeltanoProject, pluginName string) error
	Discover(ctx context.Context, project *entities.MeltanoProject, pluginName string) (map[string]interface{}, error)
	Config(ctx context.Context, project *entities.MeltanoProject, pluginName string) (map[string]interface{}, error)
	State(ctx context.Context, project *entities.MeltanoProject, jobName string) (map[string]interface{}, error)
	Schedule(ctx context.Context, project *entities.MeltanoProject, scheduleName string) error
	Environment(ctx context.Context, project *entities.MeltanoProject, envName string) error
}

// ListCriteria represents criteria for listing Meltano projects
type ListCriteria struct {
	Limit       int
	Offset      int
	Status      *entities.ProjectStatus
	Environment string
	OrderBy     string
	OrderDir    string
	NameFilter  string
}

// RunListCriteria represents criteria for listing Meltano runs
type RunListCriteria struct {
	Limit     int
	Offset    int
	ProjectID *uuid.UUID
	Status    *entities.RunStatus
	JobID     string
	OrderBy   string
	OrderDir  string
}

// Common errors
var (
	ErrProjectNotFound           = errors.New("meltano project not found")
	ErrProjectNameAlreadyExists  = errors.New("meltano project with this name already exists")
	ErrPluginNameAlreadyExists   = errors.New("plugin with this name already exists")
	ErrScheduleNameAlreadyExists = errors.New("schedule with this name already exists")
	ErrRunNotFound               = errors.New("meltano run not found")
	ErrInvalidInput              = errors.New("invalid input")
	ErrExecutionFailed           = errors.New("meltano execution failed")
	ErrProjectNotActive          = errors.New("meltano project is not active")
	ErrPluginNotFound            = errors.New("plugin not found")
	ErrInvalidCommand            = errors.New("invalid meltano command")
	ErrConfigurationError        = errors.New("meltano configuration error")
)

// UpdateProjectInput represents input for updating a Meltano project
type UpdateProjectInput struct {
	ID          uuid.UUID              `json:"id" validate:"required"`
	DisplayName string                 `json:"display_name,omitempty"`
	Description string                 `json:"description,omitempty"`
	Version     string                 `json:"version,omitempty"`
	Environment string                 `json:"environment,omitempty"`
	Status      *entities.ProjectStatus `json:"status,omitempty"`
	Settings    map[string]interface{} `json:"settings,omitempty"`
}

// AddScheduleInput is defined in add_schedule.go

// ExecutionContext represents the context for Meltano execution
type ExecutionContext struct {
	Environment     string                 `json:"environment,omitempty"`
	Config          map[string]interface{} `json:"config,omitempty"`
	StateBackend    string                 `json:"state_backend,omitempty"`
	LogLevel        string                 `json:"log_level,omitempty"`
	DryRun          bool                   `json:"dry_run,omitempty"`
	FullRefresh     bool                   `json:"full_refresh,omitempty"`
	ForceRefresh    bool                   `json:"force_refresh,omitempty"`
	SelectFilter    []string               `json:"select_filter,omitempty"`
	ExcludeFilter   []string               `json:"exclude_filter,omitempty"`
	Vars            map[string]interface{} `json:"vars,omitempty"`
}

// ExecutionResult represents the result of Meltano execution
type ExecutionResult struct {
	RunID            string                 `json:"run_id"`
	ProjectID        string                 `json:"project_id"`
	Command          []string               `json:"command"`
	Status           string                 `json:"status"`
	StartedAt        string                 `json:"started_at"`
	FinishedAt       string                 `json:"finished_at,omitempty"`
	Duration         int64                  `json:"duration_ms"`
	ExitCode         int                    `json:"exit_code"`
	Output           string                 `json:"output,omitempty"`
	ErrorOutput      string                 `json:"error_output,omitempty"`
	LogPath          string                 `json:"log_path,omitempty"`
	RecordsProcessed int64                  `json:"records_processed,omitempty"`
	BytesProcessed   int64                  `json:"bytes_processed,omitempty"`
	StateBackupPath  string                 `json:"state_backup_path,omitempty"`
	Artifacts        map[string]interface{} `json:"artifacts,omitempty"`
}

// PluginInfo represents information about a Meltano plugin
type PluginInfo struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Namespace   string                 `json:"namespace,omitempty"`
	Type        string                 `json:"type"`
	Variant     string                 `json:"variant,omitempty"`
	PipURL      string                 `json:"pip_url,omitempty"`
	Settings    map[string]interface{} `json:"settings,omitempty"`
	Config      map[string]interface{} `json:"config,omitempty"`
	Extras      []string               `json:"extras,omitempty"`
	Commands    map[string]interface{} `json:"commands,omitempty"`
	IsInstalled bool                   `json:"is_installed"`
	Version     string                 `json:"version,omitempty"`
	CreatedAt   string                 `json:"created_at"`
	UpdatedAt   string                 `json:"updated_at"`
}

// ScheduleInfo represents information about a Meltano schedule
type ScheduleInfo struct {
	ID        string            `json:"id"`
	Name      string            `json:"name"`
	Job       string            `json:"job"`
	Interval  string            `json:"interval"`
	StartDate string            `json:"start_date,omitempty"`
	Env       map[string]string `json:"env,omitempty"`
	Enabled   bool              `json:"enabled"`
	NextRun   string            `json:"next_run,omitempty"`
	LastRun   string            `json:"last_run,omitempty"`
	CreatedAt string            `json:"created_at"`
	UpdatedAt string            `json:"updated_at"`
}

// ProjectStats represents statistics about a Meltano project
type ProjectStats struct {
	TotalPlugins     int                            `json:"total_plugins"`
	PluginsByType    map[string]int                 `json:"plugins_by_type"`
	TotalSchedules   int                            `json:"total_schedules"`
	ActiveSchedules  int                            `json:"active_schedules"`
	TotalRuns        int                            `json:"total_runs"`
	SuccessfulRuns   int                            `json:"successful_runs"`
	FailedRuns       int                            `json:"failed_runs"`
	LastRunAt        string                         `json:"last_run_at,omitempty"`
	AverageRunTime   float64                        `json:"average_run_time_ms"`
	TotalRunTime     int64                          `json:"total_run_time_ms"`
	RecordsProcessed int64                          `json:"total_records_processed"`
	BytesProcessed   int64                          `json:"total_bytes_processed"`
	Environments     []string                       `json:"environments"`
	ConfiguredPaths  map[string]string              `json:"configured_paths"`
	SystemInfo       map[string]interface{}         `json:"system_info"`
}

// Event types for Meltano domain
type ProjectDeletedEvent struct {
	ProjectID uuid.UUID `json:"project_id"`
	Name      string    `json:"name"`
}

type ScheduleAddedEvent struct {
	ProjectID    uuid.UUID `json:"project_id"`
	ScheduleID   uuid.UUID `json:"schedule_id"`
	ScheduleName string    `json:"schedule_name"`
	Job          string    `json:"job"`
}

// Additional errors for schedules and environments
var (
	ErrScheduleNotFound          = errors.New("meltano schedule not found")
	ErrEnvironmentNotFound       = errors.New("meltano environment not found")
)