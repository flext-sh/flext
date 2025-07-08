package entities

import (
	"time"

	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

// MeltanoProject represents a Meltano project entity
type MeltanoProject struct {
	*domain.AggregateRoot

	// Project identification
	Name        string `json:"name"`
	DisplayName string `json:"display_name,omitempty"`
	Description string `json:"description,omitempty"`
	Version     string `json:"version,omitempty"`

	// Project paths and configuration
	RootPath    string `json:"root_path"`
	ConfigPath  string `json:"config_path"`
	Environment string `json:"environment"`

	// Project metadata
	Status    ProjectStatus `json:"status"`
	CreatedAt time.Time     `json:"created_at"`
	UpdatedAt time.Time     `json:"updated_at"`
	LastRunAt *time.Time    `json:"last_run_at,omitempty"`

	// Project configuration
	Settings     map[string]interface{} `json:"settings,omitempty"`
	Plugins      []*MeltanoPlugin       `json:"plugins,omitempty"`
	Schedules    []*MeltanoSchedule     `json:"schedules,omitempty"`
	Environments []*MeltanoEnvironment  `json:"environments,omitempty"`
}

// ProjectStatus represents the status of a Meltano project
type ProjectStatus string

const (
	ProjectStatusActive    ProjectStatus = "active"
	ProjectStatusInactive  ProjectStatus = "inactive"
	ProjectStatusError     ProjectStatus = "error"
	ProjectStatusMigrating ProjectStatus = "migrating"
)

// MeltanoPlugin represents a Meltano plugin
type MeltanoPlugin struct {
	ID        uuid.UUID              `json:"id"`
	Name      string                 `json:"name"`
	Namespace string                 `json:"namespace,omitempty"`
	Type      PluginType             `json:"type"`
	Variant   string                 `json:"variant,omitempty"`
	PipURL    string                 `json:"pip_url,omitempty"`
	Settings  map[string]interface{} `json:"settings,omitempty"`
	Config    map[string]interface{} `json:"config,omitempty"`
	Extras    []string               `json:"extras,omitempty"`
	Commands  map[string]interface{} `json:"commands,omitempty"`
	CreatedAt time.Time              `json:"created_at"`
	UpdatedAt time.Time              `json:"updated_at"`
}

// PluginType represents the type of Meltano plugin
type PluginType string

const (
	PluginTypeExtractor    PluginType = "extractors"
	PluginTypeLoader       PluginType = "loaders"
	PluginTypeTransformer  PluginType = "transformers"
	PluginTypeOrchestrator PluginType = "orchestrators"
	PluginTypeFileBundle   PluginType = "files"
	PluginTypeUtility      PluginType = "utilities"
)

// MeltanoSchedule represents a Meltano schedule
type MeltanoSchedule struct {
	ID        uuid.UUID         `json:"id"`
	Name      string            `json:"name"`
	Job       string            `json:"job"`
	Interval  string            `json:"interval"`
	StartDate *time.Time        `json:"start_date,omitempty"`
	Env       map[string]string `json:"env,omitempty"`
	Enabled   bool              `json:"enabled"`
	CreatedAt time.Time         `json:"created_at"`
	UpdatedAt time.Time         `json:"updated_at"`
}

// MeltanoEnvironment represents a Meltano environment
type MeltanoEnvironment struct {
	ID        uuid.UUID              `json:"id"`
	Name      string                 `json:"name"`
	Config    map[string]interface{} `json:"config,omitempty"`
	CreatedAt time.Time              `json:"created_at"`
	UpdatedAt time.Time              `json:"updated_at"`
}

// MeltanoRun represents a Meltano pipeline run
type MeltanoRun struct {
	*domain.AggregateRoot

	// Run identification
	ProjectID uuid.UUID `json:"project_id"`
	JobID     string    `json:"job_id"`
	RunID     string    `json:"run_id"`

	// Run configuration
	Command     []string               `json:"command"`
	Environment string                 `json:"environment"`
	Config      map[string]interface{} `json:"config,omitempty"`

	// Run status and timing
	Status     RunStatus      `json:"status"`
	StartedAt  time.Time      `json:"started_at"`
	FinishedAt *time.Time     `json:"finished_at,omitempty"`
	Duration   *time.Duration `json:"duration,omitempty"`

	// Run results
	ExitCode    *int   `json:"exit_code,omitempty"`
	Output      string `json:"output,omitempty"`
	ErrorOutput string `json:"error_output,omitempty"`
	LogPath     string `json:"log_path,omitempty"`

	// Metrics
	RecordsProcessed *int64 `json:"records_processed,omitempty"`
	BytesProcessed   *int64 `json:"bytes_processed,omitempty"`

	// State management
	StateBackupPath string `json:"state_backup_path,omitempty"`
}

// RunStatus represents the status of a Meltano run
type RunStatus string

const (
	RunStatusPending   RunStatus = "pending"
	RunStatusRunning   RunStatus = "running"
	RunStatusCompleted RunStatus = "completed"
	RunStatusFailed    RunStatus = "failed"
	RunStatusCancelled RunStatus = "cancelled"
)

// NewMeltanoProject creates a new Meltano project
func NewMeltanoProject(name, rootPath string) *MeltanoProject {
	now := time.Now()
	aggregateRoot := domain.NewAggregateRoot()
	return &MeltanoProject{
		AggregateRoot: &aggregateRoot,
		Name:          name,
		RootPath:      rootPath,
		Environment:   "dev",
		Status:        ProjectStatusActive,
		CreatedAt:     now,
		UpdatedAt:     now,
		Settings:      make(map[string]interface{}),
		Plugins:       make([]*MeltanoPlugin, 0),
		Schedules:     make([]*MeltanoSchedule, 0),
		Environments:  make([]*MeltanoEnvironment, 0),
	}
}

// AddPlugin adds a plugin to the project
func (p *MeltanoProject) AddPlugin(plugin *MeltanoPlugin) {
	now := time.Now()
	plugin.CreatedAt = now
	plugin.UpdatedAt = now

	p.Plugins = append(p.Plugins, plugin)
	p.UpdatedAt = now
}

// RemovePlugin removes a plugin from the project
func (p *MeltanoProject) RemovePlugin(pluginID uuid.UUID) bool {
	for i, plugin := range p.Plugins {
		if plugin.ID == pluginID {
			p.Plugins = append(p.Plugins[:i], p.Plugins[i+1:]...)
			p.UpdatedAt = time.Now()
			return true
		}
	}
	return false
}

// GetPlugin retrieves a plugin by ID
func (p *MeltanoProject) GetPlugin(pluginID uuid.UUID) *MeltanoPlugin {
	for _, plugin := range p.Plugins {
		if plugin.ID == pluginID {
			return plugin
		}
	}
	return nil
}

// GetPluginByName retrieves a plugin by name
func (p *MeltanoProject) GetPluginByName(name string) *MeltanoPlugin {
	for _, plugin := range p.Plugins {
		if plugin.Name == name {
			return plugin
		}
	}
	return nil
}

// AddSchedule adds a schedule to the project
func (p *MeltanoProject) AddSchedule(schedule *MeltanoSchedule) {
	now := time.Now()
	schedule.CreatedAt = now
	schedule.UpdatedAt = now

	p.Schedules = append(p.Schedules, schedule)
	p.UpdatedAt = now
}

// UpdateLastRun updates the last run timestamp
func (p *MeltanoProject) UpdateLastRun() {
	now := time.Now()
	p.LastRunAt = &now
	p.UpdatedAt = now
}

// SetStatus sets the project status
func (p *MeltanoProject) SetStatus(status ProjectStatus) {
	p.Status = status
	p.UpdatedAt = time.Now()
}

// NewMeltanoPlugin creates a new Meltano plugin
func NewMeltanoPlugin(name string, pluginType PluginType) *MeltanoPlugin {
	return &MeltanoPlugin{
		ID:       uuid.New(),
		Name:     name,
		Type:     pluginType,
		Settings: make(map[string]interface{}),
		Config:   make(map[string]interface{}),
		Commands: make(map[string]interface{}),
		Extras:   make([]string, 0),
	}
}

// UpdateSettings updates plugin settings
func (plugin *MeltanoPlugin) UpdateSettings(settings map[string]interface{}) {
	if plugin.Settings == nil {
		plugin.Settings = make(map[string]interface{})
	}

	for key, value := range settings {
		plugin.Settings[key] = value
	}

	plugin.UpdatedAt = time.Now()
}

// NewMeltanoRun creates a new Meltano run
func NewMeltanoRun(projectID uuid.UUID, command []string) *MeltanoRun {
	now := time.Now()
	aggregateRoot := domain.NewAggregateRoot()
	return &MeltanoRun{
		AggregateRoot: &aggregateRoot,
		ProjectID:     projectID,
		JobID:         generateJobID(),
		RunID:         generateRunID(),
		Command:       command,
		Environment:   "dev",
		Status:        RunStatusPending,
		StartedAt:     now,
		Config:        make(map[string]interface{}),
	}
}

// Start marks the run as started
func (r *MeltanoRun) Start() {
	r.Status = RunStatusRunning
	r.StartedAt = time.Now()
}

// Complete marks the run as completed
func (r *MeltanoRun) Complete(exitCode int, output, errorOutput string) {
	now := time.Now()
	r.Status = RunStatusCompleted
	r.FinishedAt = &now
	r.ExitCode = &exitCode
	r.Output = output
	r.ErrorOutput = errorOutput

	duration := now.Sub(r.StartedAt)
	r.Duration = &duration
}

// Fail marks the run as failed
func (r *MeltanoRun) Fail(exitCode int, output, errorOutput string) {
	now := time.Now()
	r.Status = RunStatusFailed
	r.FinishedAt = &now
	r.ExitCode = &exitCode
	r.Output = output
	r.ErrorOutput = errorOutput

	duration := now.Sub(r.StartedAt)
	r.Duration = &duration
}

// Cancel marks the run as cancelled
func (r *MeltanoRun) Cancel() {
	now := time.Now()
	r.Status = RunStatusCancelled
	r.FinishedAt = &now

	duration := now.Sub(r.StartedAt)
	r.Duration = &duration
}

// Helper functions to generate IDs
func generateJobID() string {
	return uuid.New().String()[:8]
}

func generateRunID() string {
	return uuid.New().String()
}
