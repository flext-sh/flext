package entities

import (
	"fmt"
	"path/filepath"
	"time"

	"github.com/flext/flexcore/internal/bounded_contexts/dbt/domain/events"
	"github.com/flext/flexcore/internal/shared_kernel/domain"
)

// DbtProject representa um projeto dbt
type DbtProject struct {
	domain.AggregateRoot

	// Metadados do projeto
	Name              string `json:"name" validate:"required,min=1,max=100"`
	Version           string `json:"version" validate:"required"`
	Description       string `json:"description" validate:"max=500"`
	ProfileName       string `json:"profile_name" validate:"required"`
	RequireDbtVersion string `json:"require_dbt_version,omitempty"`

	// Caminhos
	ProjectDir    string   `json:"project_dir" validate:"required"`
	ModelPaths    []string `json:"model_paths"`
	AnalysisPaths []string `json:"analysis_paths"`
	TestPaths     []string `json:"test_paths"`
	SeedPaths     []string `json:"seed_paths"`
	MacroPaths    []string `json:"macro_paths"`
	SnapshotPaths []string `json:"snapshot_paths"`
	TargetPath    string   `json:"target_path"`
	LogPath       string   `json:"log_path"`
	PackagesPath  string   `json:"packages_path"`

	// Variáveis
	Vars map[string]interface{} `json:"vars"`

	// Estado
	IsActive      bool       `json:"is_active"`
	LastRun       *time.Time `json:"last_run,omitempty"`
	LastRunStatus RunStatus  `json:"last_run_status"`

	// Configurações
	Models    ModelConfig    `json:"models"`
	Seeds     SeedConfig     `json:"seeds"`
	Tests     TestConfig     `json:"tests"`
	Snapshots SnapshotConfig `json:"snapshots"`

	// Packages e dependências
	Packages []DbtPackage `json:"packages"`
	Sources  []DbtSource  `json:"sources"`
}

// RunStatus define os status possíveis de execução
type RunStatus string

const (
	RunStatusSuccess RunStatus = "success"
	RunStatusError   RunStatus = "error"
	RunStatusSkipped RunStatus = "skipped"
	RunStatusRunning RunStatus = "running"
	RunStatusPending RunStatus = "pending"
)

// ModelConfig configuração para models
type ModelConfig struct {
	Materialization string                 `json:"materialization,omitempty"`
	Tags            []string               `json:"tags,omitempty"`
	PreHook         []string               `json:"pre_hook,omitempty"`
	PostHook        []string               `json:"post_hook,omitempty"`
	Vars            map[string]interface{} `json:"vars,omitempty"`
	CustomConfigs   map[string]interface{} `json:"custom_configs,omitempty"`
}

// SeedConfig configuração para seeds
type SeedConfig struct {
	QuoteColumns  *bool                  `json:"quote_columns,omitempty"`
	ColumnTypes   map[string]string      `json:"column_types,omitempty"`
	Tags          []string               `json:"tags,omitempty"`
	CustomConfigs map[string]interface{} `json:"custom_configs,omitempty"`
}

// TestConfig configuração para tests
type TestConfig struct {
	Severity      string                 `json:"severity,omitempty"`
	Tags          []string               `json:"tags,omitempty"`
	CustomConfigs map[string]interface{} `json:"custom_configs,omitempty"`
}

// SnapshotConfig configuração para snapshots
type SnapshotConfig struct {
	TargetDatabase string                 `json:"target_database,omitempty"`
	TargetSchema   string                 `json:"target_schema,omitempty"`
	Strategy       string                 `json:"strategy,omitempty"`
	UpdatedAt      string                 `json:"updated_at,omitempty"`
	UniqueKey      string                 `json:"unique_key,omitempty"`
	Tags           []string               `json:"tags,omitempty"`
	CustomConfigs  map[string]interface{} `json:"custom_configs,omitempty"`
}

// DbtPackage representa um package dbt
type DbtPackage struct {
	Name     string `json:"name,omitempty"`
	Git      string `json:"git,omitempty"`
	Revision string `json:"revision,omitempty"`
	Version  string `json:"version,omitempty"`
	Path     string `json:"path,omitempty"`
}

// DbtSource representa uma source dbt
type DbtSource struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	Database    string                 `json:"database,omitempty"`
	Schema      string                 `json:"schema"`
	Tables      []DbtTable             `json:"tables"`
	Meta        map[string]interface{} `json:"meta,omitempty"`
	Tags        []string               `json:"tags,omitempty"`
}

// DbtTable representa uma table em uma source
type DbtTable struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	Columns     []DbtColumn            `json:"columns,omitempty"`
	Tests       []DbtTest              `json:"tests,omitempty"`
	Meta        map[string]interface{} `json:"meta,omitempty"`
	Tags        []string               `json:"tags,omitempty"`
}

// DbtColumn representa uma coluna
type DbtColumn struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	DataType    string                 `json:"data_type,omitempty"`
	Tests       []DbtTest              `json:"tests,omitempty"`
	Meta        map[string]interface{} `json:"meta,omitempty"`
	Tags        []string               `json:"tags,omitempty"`
}

// DbtTest representa um teste dbt
type DbtTest struct {
	Name   string                 `json:"name"`
	Config map[string]interface{} `json:"config,omitempty"`
}

// NewDbtProject cria um novo projeto dbt
func NewDbtProject(name, version, profileName, projectDir string) (*DbtProject, error) {
	if name == "" {
		return nil, fmt.Errorf("project name cannot be empty")
	}
	if version == "" {
		return nil, fmt.Errorf("project version cannot be empty")
	}
	if profileName == "" {
		return nil, fmt.Errorf("profile name cannot be empty")
	}
	if projectDir == "" {
		return nil, fmt.Errorf("project directory cannot be empty")
	}

	project := &DbtProject{
		AggregateRoot: domain.NewAggregateRoot(),
		Name:          name,
		Version:       version,
		ProfileName:   profileName,
		ProjectDir:    projectDir,
		IsActive:      true,
		LastRunStatus: RunStatusPending,
		Vars:          make(map[string]interface{}),
		Packages:      []DbtPackage{},
		Sources:       []DbtSource{},

		// Valores padrão
		ModelPaths:    []string{"models"},
		AnalysisPaths: []string{"analysis"},
		TestPaths:     []string{"tests"},
		SeedPaths:     []string{"data"},
		MacroPaths:    []string{"macros"},
		SnapshotPaths: []string{"snapshots"},
		TargetPath:    "target",
		LogPath:       "logs",
		PackagesPath:  "dbt_packages",

		// Configurações padrão
		Models: ModelConfig{
			Materialization: "table",
			Tags:            []string{},
			Vars:            make(map[string]interface{}),
			CustomConfigs:   make(map[string]interface{}),
		},
		Seeds: SeedConfig{
			Tags:          []string{},
			ColumnTypes:   make(map[string]string),
			CustomConfigs: make(map[string]interface{}),
		},
		Tests: TestConfig{
			Severity:      "error",
			Tags:          []string{},
			CustomConfigs: make(map[string]interface{}),
		},
		Snapshots: SnapshotConfig{
			Strategy:      "timestamp",
			Tags:          []string{},
			CustomConfigs: make(map[string]interface{}),
		},
	}

	// Emitir evento de criação
	project.AddEvent(events.DbtProjectCreated{
		BaseDomainEvent: domain.NewBaseDomainEvent("dbt.project.created", project.GetID()),
		ProjectID:       project.GetID(),
		Name:            name,
		ProfileName:     profileName,
		ProjectDir:      projectDir,
	})

	return project, nil
}

// UpdateConfiguration atualiza a configuração do projeto
func (p *DbtProject) UpdateConfiguration(models ModelConfig, seeds SeedConfig, tests TestConfig, snapshots SnapshotConfig) {
	p.Models = models
	p.Seeds = seeds
	p.Tests = tests
	p.Snapshots = snapshots
	p.MarkAsUpdated()

	// Emitir evento de atualização
	p.AddEvent(events.DbtProjectUpdated{
		BaseDomainEvent: domain.NewBaseDomainEvent("dbt.project.updated", p.GetID()),
		ProjectID:       p.GetID(),
		Name:            p.Name,
	})
}

// AddPackage adiciona um package ao projeto
func (p *DbtProject) AddPackage(pkg DbtPackage) error {
	if pkg.Name == "" && pkg.Git == "" {
		return fmt.Errorf("package must have either name or git URL")
	}

	// Verificar se package já existe
	for _, existingPkg := range p.Packages {
		if existingPkg.Name == pkg.Name && existingPkg.Git == pkg.Git {
			return fmt.Errorf("package already exists")
		}
	}

	p.Packages = append(p.Packages, pkg)
	p.MarkAsUpdated()

	// Emitir evento
	p.AddEvent(events.DbtPackageAdded{
		BaseDomainEvent: domain.NewBaseDomainEvent("dbt.package.added", p.GetID()),
		ProjectID:       p.GetID(),
		PackageName:     pkg.Name,
		PackageGit:      pkg.Git,
	})

	return nil
}

// RemovePackage remove um package do projeto
func (p *DbtProject) RemovePackage(name, git string) error {
	for i, pkg := range p.Packages {
		if pkg.Name == name && pkg.Git == git {
			// Remover package
			p.Packages = append(p.Packages[:i], p.Packages[i+1:]...)
			p.MarkAsUpdated()

			// Emitir evento
			p.AddEvent(events.DbtPackageRemoved{
				BaseDomainEvent: domain.NewBaseDomainEvent("dbt.package.removed", p.GetID()),
				ProjectID:       p.GetID(),
				PackageName:     name,
				PackageGit:      git,
			})

			return nil
		}
	}

	return fmt.Errorf("package not found")
}

// AddSource adiciona uma source ao projeto
func (p *DbtProject) AddSource(source DbtSource) error {
	if source.Name == "" {
		return fmt.Errorf("source name cannot be empty")
	}
	if source.Schema == "" {
		return fmt.Errorf("source schema cannot be empty")
	}

	// Verificar se source já existe
	for _, existingSource := range p.Sources {
		if existingSource.Name == source.Name {
			return fmt.Errorf("source already exists")
		}
	}

	p.Sources = append(p.Sources, source)
	p.MarkAsUpdated()

	// Emitir evento
	p.AddEvent(events.DbtSourceAdded{
		BaseDomainEvent: domain.NewBaseDomainEvent("dbt.source.added", p.GetID()),
		ProjectID:       p.GetID(),
		SourceName:      source.Name,
		SourceSchema:    source.Schema,
	})

	return nil
}

// UpdateSource atualiza uma source existente
func (p *DbtProject) UpdateSource(sourceName string, updatedSource DbtSource) error {
	for i, source := range p.Sources {
		if source.Name == sourceName {
			p.Sources[i] = updatedSource
			p.MarkAsUpdated()

			// Emitir evento
			p.AddEvent(events.DbtSourceUpdated{
				BaseDomainEvent: domain.NewBaseDomainEvent("dbt.source.updated", p.GetID()),
				ProjectID:       p.GetID(),
				SourceName:      sourceName,
			})

			return nil
		}
	}

	return fmt.Errorf("source not found")
}

// SetVariable define uma variável do projeto
func (p *DbtProject) SetVariable(key string, value interface{}) {
	if p.Vars == nil {
		p.Vars = make(map[string]interface{})
	}
	p.Vars[key] = value
	p.MarkAsUpdated()
}

// GetVariable obtém uma variável do projeto
func (p *DbtProject) GetVariable(key string) (interface{}, bool) {
	value, exists := p.Vars[key]
	return value, exists
}

// UpdateRunStatus atualiza o status da última execução
func (p *DbtProject) UpdateRunStatus(status RunStatus) {
	p.LastRunStatus = status
	now := time.Now()
	p.LastRun = &now
	p.MarkAsUpdated()

	// Emitir evento
	p.AddEvent(events.DbtProjectRunCompleted{
		BaseDomainEvent: domain.NewBaseDomainEvent("dbt.project.run.completed", p.GetID()),
		ProjectID:       p.GetID(),
		Status:          string(status),
		CompletedAt:     now,
	})
}

// Activate ativa o projeto
func (p *DbtProject) Activate() {
	p.IsActive = true
	p.MarkAsUpdated()

	// Emitir evento
	p.AddEvent(events.DbtProjectActivated{
		BaseDomainEvent: domain.NewBaseDomainEvent("dbt.project.activated", p.GetID()),
		ProjectID:       p.GetID(),
		Name:            p.Name,
	})
}

// Deactivate desativa o projeto
func (p *DbtProject) Deactivate() {
	p.IsActive = false
	p.MarkAsUpdated()

	// Emitir evento
	p.AddEvent(events.DbtProjectDeactivated{
		BaseDomainEvent: domain.NewBaseDomainEvent("dbt.project.deactivated", p.GetID()),
		ProjectID:       p.GetID(),
		Name:            p.Name,
	})
}

// GetModelPath retorna o caminho completo para models
func (p *DbtProject) GetModelPath() string {
	if len(p.ModelPaths) > 0 {
		return filepath.Join(p.ProjectDir, p.ModelPaths[0])
	}
	return filepath.Join(p.ProjectDir, "models")
}

// GetTargetPath retorna o caminho completo para target
func (p *DbtProject) GetTargetPath() string {
	return filepath.Join(p.ProjectDir, p.TargetPath)
}

// GetLogPath retorna o caminho completo para logs
func (p *DbtProject) GetLogPath() string {
	return filepath.Join(p.ProjectDir, p.LogPath)
}

// ValidateConfiguration valida a configuração do projeto
func (p *DbtProject) ValidateConfiguration() error {
	validator := newDbtProjectValidator()

	validator.
		validateModelPaths(p.ModelPaths).
		validateProfile(p.ProfileName).
		validatePackages(p.Packages).
		validateSources(p.Sources)

	return validator.getFirstError()
}

// dbtProjectValidator provides fluent validation for DBT projects
type dbtProjectValidator struct {
	firstError error
}

// newDbtProjectValidator creates a new validator instance
func newDbtProjectValidator() *dbtProjectValidator {
	return &dbtProjectValidator{}
}

// validateModelPaths validates that at least one model path is provided
func (v *dbtProjectValidator) validateModelPaths(modelPaths []string) *dbtProjectValidator {
	if v.firstError == nil && len(modelPaths) == 0 {
		v.firstError = fmt.Errorf("at least one model path is required")
	}
	return v
}

// validateProfile validates that a profile name is provided
func (v *dbtProjectValidator) validateProfile(profileName string) *dbtProjectValidator {
	if v.firstError == nil && profileName == "" {
		v.firstError = fmt.Errorf("profile name is required")
	}
	return v
}

// validatePackages validates that packages have either name or git URL
func (v *dbtProjectValidator) validatePackages(packages []DbtPackage) *dbtProjectValidator {
	if v.firstError != nil {
		return v
	}

	for _, pkg := range packages {
		if pkg.Name == "" && pkg.Git == "" {
			v.firstError = fmt.Errorf("package must have either name or git URL")
			break
		}
	}
	return v
}

// validateSources validates that sources have required fields
func (v *dbtProjectValidator) validateSources(sources []DbtSource) *dbtProjectValidator {
	if v.firstError != nil {
		return v
	}

	for _, source := range sources {
		if source.Name == "" {
			v.firstError = fmt.Errorf("source name cannot be empty")
			break
		}
		if source.Schema == "" {
			v.firstError = fmt.Errorf("source schema cannot be empty")
			break
		}
	}
	return v
}

// getFirstError returns the first validation error found, or nil if no errors
func (v *dbtProjectValidator) getFirstError() error {
	return v.firstError
}

// GetPackageByName encontra um package por nome
func (p *DbtProject) GetPackageByName(name string) *DbtPackage {
	for _, pkg := range p.Packages {
		if pkg.Name == name {
			return &pkg
		}
	}
	return nil
}

// GetSourceByName encontra uma source por nome
func (p *DbtProject) GetSourceByName(name string) *DbtSource {
	for _, source := range p.Sources {
		if source.Name == name {
			return &source
		}
	}
	return nil
}

// GetTableFromSource encontra uma table em uma source
func (p *DbtProject) GetTableFromSource(sourceName, tableName string) *DbtTable {
	source := p.GetSourceByName(sourceName)
	if source == nil {
		return nil
	}

	for _, table := range source.Tables {
		if table.Name == tableName {
			return &table
		}
	}
	return nil
}
