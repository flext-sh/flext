package entities

import (
	"time"

	"github.com/flext-sh/flext/pkg/utils/shared_kernel/errors"
	"github.com/google/uuid"
)

// PipelineEntity interface especializada para entidades de pipeline
type PipelineEntity interface {
	Entity

	// Pipeline-specific behaviors
	GetName() string
	SetName(name string) error
	GetDescription() string
	SetDescription(description string)

	// Status management
	GetStatus() string
	SetStatus(status string) error
	IsActive() bool
	Activate() error
	Deactivate() error

	// Pipeline execution
	CanExecute() bool
	GetLastExecutionAt() *time.Time
	SetLastExecutionAt(t time.Time)
	GetExecutionCount() int64
	IncrementExecutionCount()
}

// PluginEntity interface especializada para entidades de plugin
type PluginEntity interface {
	Entity

	// Plugin-specific behaviors
	GetName() string
	SetName(name string) error
	GetType() string
	SetType(pluginType string) error
	GetPluginVersion() string
	SetPluginVersion(version string) error

	// Configuration management
	GetConfiguration() map[string]interface{}
	SetConfiguration(config map[string]interface{}) error
	GetConfigurationSchema() map[string]interface{}

	// Plugin state
	IsEnabled() bool
	Enable() error
	Disable() error
	GetInstallationPath() string
	SetInstallationPath(path string) error
}

// AuthEntity interface especializada para entidades de autenticação
type AuthEntity interface {
	Entity

	// Authentication-specific behaviors
	GetUserID() uuid.UUID
	SetUserID(userID uuid.UUID) error
	GetRole() string
	SetRole(role string) error
	GetPermissions() []string
	SetPermissions(permissions []string) error

	// Session management
	GetLastLoginAt() *time.Time
	SetLastLoginAt(t time.Time)
	IsSessionValid() bool
	GetSessionExpiresAt() *time.Time
	SetSessionExpiresAt(t time.Time)

	// Security
	GetPasswordHash() string
	SetPasswordHash(hash string) error
	RequiresPasswordChange() bool
	IsLocked() bool
	Lock() error
	Unlock() error
}

// ExecutionEntity interface especializada para entidades de execução
type ExecutionEntity interface {
	Entity

	// Execution-specific behaviors
	GetStatus() string
	SetStatus(status string) error
	GetStartedAt() *time.Time
	SetStartedAt(t time.Time)
	GetCompletedAt() *time.Time
	SetCompletedAt(t time.Time)

	// Progress tracking
	GetProgress() float64
	SetProgress(progress float64) error
	GetStepsTotal() int
	GetStepsCompleted() int
	SetStepsCompleted(completed int) error

	// Results and errors
	GetResult() map[string]interface{}
	SetResult(result map[string]interface{})
	GetError() string
	SetError(errorMsg string)
	HasError() bool

	// Duration calculation
	GetDuration() time.Duration
	IsCompleted() bool
	IsRunning() bool
	IsFailed() bool
}

// SingerEntity interface especializada para entidades Singer/Meltano
type SingerEntity interface {
	Entity

	// Singer-specific behaviors
	GetTapName() string
	SetTapName(name string) error
	GetTargetName() string
	SetTargetName(name string) error
	GetStream() string
	SetStream(stream string) error

	// Schema management
	GetSchema() map[string]interface{}
	SetSchema(schema map[string]interface{}) error
	GetCatalog() map[string]interface{}
	SetCatalog(catalog map[string]interface{}) error

	// State management
	GetState() map[string]interface{}
	SetState(state map[string]interface{}) error
	GetBookmark() string
	SetBookmark(bookmark string) error

	// Metrics
	GetRecordsExtracted() int64
	IncrementRecordsExtracted(count int64)
	GetRecordsLoaded() int64
	IncrementRecordsLoaded(count int64)
	GetLastSyncAt() *time.Time
	SetLastSyncAt(t time.Time)
}

// BasePipelineEntity implementação base para entidades de pipeline
type BasePipelineEntity struct {
	*BaseEntity
	Name            string     `json:"name" gorm:"index" db:"name"`
	Description     string     `json:"description" db:"description"`
	Status          string     `json:"status" gorm:"default:inactive" db:"status"`
	LastExecutionAt *time.Time `json:"last_execution_at" db:"last_execution_at"`
	ExecutionCount  int64      `json:"execution_count" gorm:"default:0" db:"execution_count"`
}

// NewBasePipelineEntity cria uma nova entidade de pipeline
func NewBasePipelineEntity(name, description string) *BasePipelineEntity {
	return &BasePipelineEntity{
		BaseEntity:     NewBaseEntity(),
		Name:           name,
		Description:    description,
		Status:         "inactive",
		ExecutionCount: 0,
	}
}

// GetName retorna o nome do pipeline
func (p *BasePipelineEntity) GetName() string {
	return p.Name
}

// SetName define o nome do pipeline
func (p *BasePipelineEntity) SetName(name string) error {
	if name == "" {
		return &errors.DomainError{
			Code:        "INVALID_PIPELINE_NAME",
			Message:     "Pipeline name cannot be empty",
			Details: "All pipelines must have a valid name",
		}
	}
	p.Name = name
	p.SetUpdatedAt(time.Now().UTC())
	return nil
}

// GetDescription retorna a descrição do pipeline
func (p *BasePipelineEntity) GetDescription() string {
	return p.Description
}

// SetDescription define a descrição do pipeline
func (p *BasePipelineEntity) SetDescription(description string) {
	p.Description = description
	p.SetUpdatedAt(time.Now().UTC())
}

// GetStatus retorna o status do pipeline
func (p *BasePipelineEntity) GetStatus() string {
	return p.Status
}

// SetStatus define o status do pipeline
func (p *BasePipelineEntity) SetStatus(status string) error {
	validStatuses := []string{"active", "inactive", "running", "failed", "completed"}
	for _, validStatus := range validStatuses {
		if status == validStatus {
			p.Status = status
			p.SetUpdatedAt(time.Now().UTC())
			return nil
		}
	}

	return &errors.DomainError{
		Code:        "INVALID_PIPELINE_STATUS",
		Message:     "Invalid pipeline status",
		Details: "Pipeline status must be one of: active, inactive, running, failed, completed",
	}
}

// IsActive verifica se o pipeline está ativo
func (p *BasePipelineEntity) IsActive() bool {
	return p.Status == "active"
}

// Activate ativa o pipeline
func (p *BasePipelineEntity) Activate() error {
	return p.SetStatus("active")
}

// Deactivate desativa o pipeline
func (p *BasePipelineEntity) Deactivate() error {
	return p.SetStatus("inactive")
}

// CanExecute verifica se o pipeline pode ser executado
func (p *BasePipelineEntity) CanExecute() bool {
	return p.IsActive() && p.Status != "running"
}

// GetLastExecutionAt retorna a última execução
func (p *BasePipelineEntity) GetLastExecutionAt() *time.Time {
	return p.LastExecutionAt
}

// SetLastExecutionAt define a última execução
func (p *BasePipelineEntity) SetLastExecutionAt(t time.Time) {
	p.LastExecutionAt = &t
	p.SetUpdatedAt(time.Now().UTC())
}

// GetExecutionCount retorna o contador de execuções
func (p *BasePipelineEntity) GetExecutionCount() int64 {
	return p.ExecutionCount
}

// IncrementExecutionCount incrementa o contador de execuções
func (p *BasePipelineEntity) IncrementExecutionCount() {
	p.ExecutionCount++
	p.SetUpdatedAt(time.Now().UTC())
}

// BasePluginEntity implementação base para entidades de plugin
type BasePluginEntity struct {
	*BaseEntity
	Name                string                 `json:"name" gorm:"index" db:"name"`
	Type                string                 `json:"type" gorm:"index" db:"type"`
	Version             string                 `json:"version" db:"version"`
	Configuration       map[string]interface{} `json:"configuration" gorm:"type:jsonb" db:"configuration"`
	ConfigurationSchema map[string]interface{} `json:"configuration_schema" gorm:"type:jsonb" db:"configuration_schema"`
	Enabled             bool                   `json:"enabled" gorm:"default:false" db:"enabled"`
	InstallationPath    string                 `json:"installation_path" db:"installation_path"`
}

// NewBasePluginEntity cria uma nova entidade de plugin
func NewBasePluginEntity(name, pluginType, version string) *BasePluginEntity {
	return &BasePluginEntity{
		BaseEntity:          NewBaseEntity(),
		Name:                name,
		Type:                pluginType,
		Version:             version,
		Configuration:       make(map[string]interface{}),
		ConfigurationSchema: make(map[string]interface{}),
		Enabled:             false,
	}
}

// GetName retorna o nome do plugin
func (p *BasePluginEntity) GetName() string {
	return p.Name
}

// SetName define o nome do plugin
func (p *BasePluginEntity) SetName(name string) error {
	if name == "" {
		return &errors.DomainError{
			Code:        "INVALID_PLUGIN_NAME",
			Message:     "Plugin name cannot be empty",
			Details: "All plugins must have a valid name",
		}
	}
	p.Name = name
	p.SetUpdatedAt(time.Now().UTC())
	return nil
}

// GetType retorna o tipo do plugin
func (p *BasePluginEntity) GetType() string {
	return p.Type
}

// SetType define o tipo do plugin
func (p *BasePluginEntity) SetType(pluginType string) error {
	validTypes := []string{"tap", "target", "transformer", "extractor", "loader"}
	for _, validType := range validTypes {
		if pluginType == validType {
			p.Type = pluginType
			p.SetUpdatedAt(time.Now().UTC())
			return nil
		}
	}

	return &errors.DomainError{
		Code:        "INVALID_PLUGIN_TYPE",
		Message:     "Invalid plugin type",
		Details: "Plugin type must be one of: tap, target, transformer, extractor, loader",
	}
}

// GetPluginVersion retorna a versão do plugin
func (p *BasePluginEntity) GetPluginVersion() string {
	return p.Version
}

// SetPluginVersion define a versão do plugin
func (p *BasePluginEntity) SetPluginVersion(version string) error {
	if version == "" {
		return &errors.DomainError{
			Code:        "INVALID_PLUGIN_VERSION",
			Message:     "Plugin version cannot be empty",
			Details: "All plugins must have a valid version",
		}
	}
	p.Version = version
	p.SetUpdatedAt(time.Now().UTC())
	return nil
}

// GetConfiguration retorna a configuração do plugin
func (p *BasePluginEntity) GetConfiguration() map[string]interface{} {
	if p.Configuration == nil {
		p.Configuration = make(map[string]interface{})
	}
	return p.Configuration
}

// SetConfiguration define a configuração do plugin
func (p *BasePluginEntity) SetConfiguration(config map[string]interface{}) error {
	if config == nil {
		config = make(map[string]interface{})
	}
	p.Configuration = config
	p.SetUpdatedAt(time.Now().UTC())
	return nil
}

// GetConfigurationSchema retorna o schema de configuração
func (p *BasePluginEntity) GetConfigurationSchema() map[string]interface{} {
	if p.ConfigurationSchema == nil {
		p.ConfigurationSchema = make(map[string]interface{})
	}
	return p.ConfigurationSchema
}

// IsEnabled verifica se o plugin está habilitado
func (p *BasePluginEntity) IsEnabled() bool {
	return p.Enabled
}

// Enable habilita o plugin
func (p *BasePluginEntity) Enable() error {
	p.Enabled = true
	p.SetUpdatedAt(time.Now().UTC())
	return nil
}

// Disable desabilita o plugin
func (p *BasePluginEntity) Disable() error {
	p.Enabled = false
	p.SetUpdatedAt(time.Now().UTC())
	return nil
}

// GetInstallationPath retorna o caminho de instalação
func (p *BasePluginEntity) GetInstallationPath() string {
	return p.InstallationPath
}

// SetInstallationPath define o caminho de instalação
func (p *BasePluginEntity) SetInstallationPath(path string) error {
	p.InstallationPath = path
	p.SetUpdatedAt(time.Now().UTC())
	return nil
}

// BaseExecutionEntity implementação base para entidades de execução
type BaseExecutionEntity struct {
	*BaseEntity
	Status         string                 `json:"status" gorm:"default:pending" db:"status"`
	StartedAt      *time.Time             `json:"started_at" db:"started_at"`
	CompletedAt    *time.Time             `json:"completed_at" db:"completed_at"`
	Progress       float64                `json:"progress" gorm:"default:0" db:"progress"`
	StepsTotal     int                    `json:"steps_total" gorm:"default:0" db:"steps_total"`
	StepsCompleted int                    `json:"steps_completed" gorm:"default:0" db:"steps_completed"`
	Result         map[string]interface{} `json:"result" gorm:"type:jsonb" db:"result"`
	Error          string                 `json:"error" db:"error"`
}

// NewBaseExecutionEntity cria uma nova entidade de execução
func NewBaseExecutionEntity() *BaseExecutionEntity {
	return &BaseExecutionEntity{
		BaseEntity:     NewBaseEntity(),
		Status:         "pending",
		Progress:       0.0,
		StepsTotal:     0,
		StepsCompleted: 0,
		Result:         make(map[string]interface{}),
	}
}

// GetStatus retorna o status da execução
func (e *BaseExecutionEntity) GetStatus() string {
	return e.Status
}

// SetStatus define o status da execução
func (e *BaseExecutionEntity) SetStatus(status string) error {
	validStatuses := []string{"pending", "running", "completed", "failed", "cancelled"}
	for _, validStatus := range validStatuses {
		if status == validStatus {
			e.Status = status
			e.SetUpdatedAt(time.Now().UTC())
			return nil
		}
	}

	return &errors.DomainError{
		Code:        "INVALID_EXECUTION_STATUS",
		Message:     "Invalid execution status",
		Details: "Execution status must be one of: pending, running, completed, failed, cancelled",
	}
}

// GetStartedAt retorna quando a execução iniciou
func (e *BaseExecutionEntity) GetStartedAt() *time.Time {
	return e.StartedAt
}

// SetStartedAt define quando a execução iniciou
func (e *BaseExecutionEntity) SetStartedAt(t time.Time) {
	e.StartedAt = &t
	e.SetUpdatedAt(time.Now().UTC())
}

// GetCompletedAt retorna quando a execução completou
func (e *BaseExecutionEntity) GetCompletedAt() *time.Time {
	return e.CompletedAt
}

// SetCompletedAt define quando a execução completou
func (e *BaseExecutionEntity) SetCompletedAt(t time.Time) {
	e.CompletedAt = &t
	e.SetUpdatedAt(time.Now().UTC())
}

// GetProgress retorna o progresso da execução
func (e *BaseExecutionEntity) GetProgress() float64 {
	return e.Progress
}

// SetProgress define o progresso da execução
func (e *BaseExecutionEntity) SetProgress(progress float64) error {
	if progress < 0.0 || progress > 100.0 {
		return &errors.DomainError{
			Code:        "INVALID_PROGRESS",
			Message:     "Progress must be between 0 and 100",
			Details: "Execution progress must be a valid percentage",
		}
	}
	e.Progress = progress
	e.SetUpdatedAt(time.Now().UTC())
	return nil
}

// GetStepsTotal retorna o total de passos
func (e *BaseExecutionEntity) GetStepsTotal() int {
	return e.StepsTotal
}

// GetStepsCompleted retorna os passos completados
func (e *BaseExecutionEntity) GetStepsCompleted() int {
	return e.StepsCompleted
}

// SetStepsCompleted define os passos completados
func (e *BaseExecutionEntity) SetStepsCompleted(completed int) error {
	if completed < 0 {
		return &errors.DomainError{
			Code:        "INVALID_STEPS_COMPLETED",
			Message:     "Steps completed cannot be negative",
			Details: "Steps completed must be a non-negative number",
		}
	}
	e.StepsCompleted = completed

	// Update progress automatically
	if e.StepsTotal > 0 {
		e.Progress = (float64(completed) / float64(e.StepsTotal)) * 100.0
	}

	e.SetUpdatedAt(time.Now().UTC())
	return nil
}

// GetResult retorna o resultado da execução
func (e *BaseExecutionEntity) GetResult() map[string]interface{} {
	if e.Result == nil {
		e.Result = make(map[string]interface{})
	}
	return e.Result
}

// SetResult define o resultado da execução
func (e *BaseExecutionEntity) SetResult(result map[string]interface{}) {
	if result == nil {
		result = make(map[string]interface{})
	}
	e.Result = result
	e.SetUpdatedAt(time.Now().UTC())
}

// GetError retorna o erro da execução
func (e *BaseExecutionEntity) GetError() string {
	return e.Error
}

// SetError define o erro da execução
func (e *BaseExecutionEntity) SetError(errorMsg string) {
	e.Error = errorMsg
	e.SetUpdatedAt(time.Now().UTC())
}

// HasError verifica se há erro na execução
func (e *BaseExecutionEntity) HasError() bool {
	return e.Error != ""
}

// GetDuration calcula a duração da execução
func (e *BaseExecutionEntity) GetDuration() time.Duration {
	if e.StartedAt == nil {
		return 0
	}

	endTime := time.Now().UTC()
	if e.CompletedAt != nil {
		endTime = *e.CompletedAt
	}

	return endTime.Sub(*e.StartedAt)
}

// IsCompleted verifica se a execução foi completada
func (e *BaseExecutionEntity) IsCompleted() bool {
	return e.Status == "completed"
}

// IsRunning verifica se a execução está rodando
func (e *BaseExecutionEntity) IsRunning() bool {
	return e.Status == "running"
}

// IsFailed verifica se a execução falhou
func (e *BaseExecutionEntity) IsFailed() bool {
	return e.Status == "failed"
}
