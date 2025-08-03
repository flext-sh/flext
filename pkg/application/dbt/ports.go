package dbt

import (
	"context"
	"errors"

	"github.com/flext-sh/flext/pkg/domain/dbt/domain/entities"
	"github.com/google/uuid"
)

// ProjectRepository defines the interface for dbt project persistence
// This interface is declared by the use case layer (Dependency Inversion)
type ProjectRepository interface {
	Save(ctx context.Context, project *entities.DbtProject) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.DbtProject, error)
	FindByName(ctx context.Context, name string) (*entities.DbtProject, error)
	ExistsByName(ctx context.Context, name string) (bool, error)
	List(ctx context.Context, criteria ListCriteria) ([]*entities.DbtProject, int, error)
	Delete(ctx context.Context, id uuid.UUID) error
	FindByProfileName(ctx context.Context, profileName string) ([]*entities.DbtProject, error)
	FindActiveProjects(ctx context.Context) ([]*entities.DbtProject, error)
}

// EventPublisher defines the interface for publishing domain events
type EventPublisher interface {
	Publish(ctx context.Context, event interface{}) error
}

// InputValidator defines the interface for validating use case inputs
type InputValidator interface {
	ValidateCreateProject(input CreateProjectInput) error
	ValidateUpdateProject(input UpdateProjectInput) error
	ValidateExecuteProject(input ExecuteProjectInput) error
	ValidateAddPackage(input AddPackageInput) error
	ValidateAddSource(input AddSourceInput) error
	ValidateGetProject(input GetProjectInput) error
	ValidateListProjects(input ListProjectsInput) error
	ValidateDeleteProject(input DeleteProjectInput) error
}

// DbtExecutor defines the interface for executing dbt commands
type DbtExecutor interface {
	Run(ctx context.Context, project *entities.DbtProject, context *ExecutionContext) (*ExecutionResult, error)
	Test(ctx context.Context, project *entities.DbtProject, context *ExecutionContext) (*ExecutionResult, error)
	Compile(ctx context.Context, project *entities.DbtProject, context *ExecutionContext) (*ExecutionResult, error)
	Snapshot(ctx context.Context, project *entities.DbtProject, context *ExecutionContext) (*ExecutionResult, error)
	Seed(ctx context.Context, project *entities.DbtProject, context *ExecutionContext) (*ExecutionResult, error)
	Docs(ctx context.Context, project *entities.DbtProject, context *ExecutionContext) (*ExecutionResult, error)
	Source(ctx context.Context, project *entities.DbtProject, context *ExecutionContext) (*ExecutionResult, error)
	Clean(ctx context.Context, project *entities.DbtProject) error
	Deps(ctx context.Context, project *entities.DbtProject) error
}

// ListCriteria represents criteria for listing dbt projects
type ListCriteria struct {
	Limit       int
	Offset      int
	Active      *bool
	ProfileName string
	OrderBy     string
	OrderDir    string
	NameFilter  string
}

// ExecutionContext represents the context for dbt execution
type ExecutionContext struct {
	Target        string                 `json:"target,omitempty"`
	Profile       string                 `json:"profile,omitempty"`
	Vars          map[string]interface{} `json:"vars,omitempty"`
	Models        []string               `json:"models,omitempty"`
	Select        []string               `json:"select,omitempty"`
	Exclude       []string               `json:"exclude,omitempty"`
	Threads       int                    `json:"threads,omitempty"`
	FullRefresh   bool                   `json:"full_refresh,omitempty"`
	Debug         bool                   `json:"debug,omitempty"`
	Warn          bool                   `json:"warn,omitempty"`
	StoreFailures bool                   `json:"store_failures,omitempty"`
	ShowSkipped   bool                   `json:"show_skipped,omitempty"`
}

// ExecutionResult represents the result of dbt execution
type ExecutionResult struct {
	ID          uuid.UUID              `json:"id"`
	ProjectID   uuid.UUID              `json:"project_id"`
	Command     string                 `json:"command"`
	Status      string                 `json:"status"`
	StartedAt   string                 `json:"started_at"`
	CompletedAt string                 `json:"completed_at,omitempty"`
	Duration    int64                  `json:"duration_ms"`
	Results     []ModelResult          `json:"results"`
	Stats       ExecutionStats         `json:"stats"`
	Logs        []LogEntry             `json:"logs"`
	Error       string                 `json:"error,omitempty"`
	Artifacts   map[string]interface{} `json:"artifacts,omitempty"`
}

// ModelResult represents the result of a single model execution
type ModelResult struct {
	NodeID         string                 `json:"node_id"`
	Name           string                 `json:"name"`
	ResourceType   string                 `json:"resource_type"`
	Status         string                 `json:"status"`
	ExecutionTime  float64                `json:"execution_time"`
	RowsAffected   int64                  `json:"rows_affected,omitempty"`
	BytesProcessed int64                  `json:"bytes_processed,omitempty"`
	Error          string                 `json:"error,omitempty"`
	Metadata       map[string]interface{} `json:"metadata,omitempty"`
}

// ExecutionStats contains statistics about the execution
type ExecutionStats struct {
	TotalModels      int     `json:"total_models"`
	SuccessfulModels int     `json:"successful_models"`
	FailedModels     int     `json:"failed_models"`
	SkippedModels    int     `json:"skipped_models"`
	TotalTests       int     `json:"total_tests"`
	PassedTests      int     `json:"passed_tests"`
	FailedTests      int     `json:"failed_tests"`
	ErrorTests       int     `json:"error_tests"`
	WarnTests        int     `json:"warn_tests"`
	TotalSeeds       int     `json:"total_seeds"`
	TotalSnapshots   int     `json:"total_snapshots"`
	ExecutionTime    float64 `json:"execution_time"`
}

// LogEntry represents a log entry from dbt execution
type LogEntry struct {
	Timestamp string                 `json:"timestamp"`
	Level     string                 `json:"level"`
	Message   string                 `json:"message"`
	NodeID    string                 `json:"node_id,omitempty"`
	Data      map[string]interface{} `json:"data,omitempty"`
}

// Common errors
var (
	ErrProjectNotFound          = errors.New("dbt project not found")
	ErrProjectNameAlreadyExists = errors.New("dbt project with this name already exists")
	ErrInvalidInput             = errors.New("invalid input")
	ErrExecutionFailed          = errors.New("dbt execution failed")
	ErrProjectNotActive         = errors.New("dbt project is not active")
	ErrInvalidProjectStructure  = errors.New("invalid dbt project structure")
	ErrDependenciesNotInstalled = errors.New("dbt dependencies not installed")
)

// UpdateProjectInput represents input for updating a dbt project
type UpdateProjectInput struct {
	ID                uuid.UUID              `json:"id" validate:"required"`
	DisplayName       string                 `json:"display_name,omitempty"`
	Description       string                 `json:"description,omitempty"`
	Version           string                 `json:"version,omitempty"`
	ProfileName       string                 `json:"profile_name,omitempty"`
	ModelPaths        []string               `json:"model_paths,omitempty"`
	AnalysisPaths     []string               `json:"analysis_paths,omitempty"`
	TestPaths         []string               `json:"test_paths,omitempty"`
	SeedPaths         []string               `json:"seed_paths,omitempty"`
	MacroPaths        []string               `json:"macro_paths,omitempty"`
	SnapshotPaths     []string               `json:"snapshot_paths,omitempty"`
	DocsPath          string                 `json:"docs_path,omitempty"`
	AssetPath         string                 `json:"asset_path,omitempty"`
	TargetPath        string                 `json:"target_path,omitempty"`
	LogPath           string                 `json:"log_path,omitempty"`
	PackagesPath      string                 `json:"packages_path,omitempty"`
	CleanTargets      []string               `json:"clean_targets,omitempty"`
	Vars              map[string]interface{} `json:"vars,omitempty"`
	OnRunStart        []interface{}          `json:"on_run_start,omitempty"`
	OnRunEnd          []interface{}          `json:"on_run_end,omitempty"`
	RequireDbtVersion string                 `json:"require_dbt_version,omitempty"`
	IsActive          *bool                  `json:"is_active,omitempty"`
}

// ExecuteProjectInput represents input for executing a dbt project
type ExecuteProjectInput struct {
	ProjectID uuid.UUID        `json:"project_id" validate:"required"`
	Command   string           `json:"command" validate:"required,oneof=run test compile snapshot seed docs source clean deps"`
	Context   ExecutionContext `json:"context"`
}

// AddPackageInput represents input for adding a package to a dbt project
type AddPackageInput struct {
	ProjectID uuid.UUID           `json:"project_id" validate:"required"`
	Package   entities.DbtPackage `json:"package" validate:"required"`
}

// AddSourceInput represents input for adding a source to a dbt project
type AddSourceInput struct {
	ProjectID uuid.UUID          `json:"project_id" validate:"required"`
	Source    entities.DbtSource `json:"source" validate:"required"`
}

// UpdateProjectOutput represents the output of updating a dbt project
type UpdateProjectOutput struct {
	Project interface{} `json:"project"`
}
