package events

import (
	"time"

	"github.com/flext-sh/flext/internal/shared_kernel/domain"
	"github.com/google/uuid"
)

const (
	ProjectCreatedEventType    = "dbt.project.created"
	ProjectUpdatedEventType    = "dbt.project.updated"
	ProjectDeletedEventType    = "dbt.project.deleted"
	ProjectActivatedEventType  = "dbt.project.activated"
	ProjectDeactivatedEventType = "dbt.project.deactivated"
)

// DbtProjectCreated evento emitido quando um projeto dbt é criado
type DbtProjectCreated struct {
	domain.BaseDomainEvent
	ProjectID   uuid.UUID `json:"project_id"`
	Name        string    `json:"name"`
	ProfileName string    `json:"profile_name"`
	ProjectDir  string    `json:"project_dir"`
}

// DbtProjectUpdated evento emitido quando um projeto dbt é atualizado
type DbtProjectUpdated struct {
	domain.BaseDomainEvent
	ProjectID uuid.UUID `json:"project_id"`
	Name      string    `json:"name"`
}

// DbtProjectActivated evento emitido quando um projeto dbt é ativado
type DbtProjectActivated struct {
	domain.BaseDomainEvent
	ProjectID uuid.UUID `json:"project_id"`
	Name      string    `json:"name"`
}

// DbtProjectDeactivated evento emitido quando um projeto dbt é desativado
type DbtProjectDeactivated struct {
	domain.BaseDomainEvent
	ProjectID uuid.UUID `json:"project_id"`
	Name      string    `json:"name"`
}

// DbtProjectDeleted evento emitido quando um projeto dbt é deletado
type DbtProjectDeleted struct {
	domain.BaseDomainEvent
	ProjectID uuid.UUID `json:"project_id"`
	Name      string    `json:"name"`
}

// NewProjectDeletedEvent cria um novo evento de projeto deletado
func NewProjectDeletedEvent(projectID uuid.UUID, name string) DbtProjectDeleted {
	return DbtProjectDeleted{
		BaseDomainEvent: domain.NewBaseDomainEvent(ProjectDeletedEventType, projectID),
		ProjectID:       projectID,
		Name:            name,
	}
}

// DbtProjectRunCompleted evento emitido quando uma execução dbt é completada
type DbtProjectRunCompleted struct {
	domain.BaseDomainEvent
	ProjectID   uuid.UUID `json:"project_id"`
	Status      string    `json:"status"`
	CompletedAt time.Time `json:"completed_at"`
}

// DbtPackageAdded evento emitido quando um package é adicionado
type DbtPackageAdded struct {
	domain.BaseDomainEvent
	ProjectID   uuid.UUID `json:"project_id"`
	PackageName string    `json:"package_name"`
	PackageGit  string    `json:"package_git"`
}

// DbtPackageRemoved evento emitido quando um package é removido
type DbtPackageRemoved struct {
	domain.BaseDomainEvent
	ProjectID   uuid.UUID `json:"project_id"`
	PackageName string    `json:"package_name"`
	PackageGit  string    `json:"package_git"`
}

// DbtSourceAdded evento emitido quando uma source é adicionada
type DbtSourceAdded struct {
	domain.BaseDomainEvent
	ProjectID    uuid.UUID `json:"project_id"`
	SourceName   string    `json:"source_name"`
	SourceSchema string    `json:"source_schema"`
}

// DbtSourceUpdated evento emitido quando uma source é atualizada
type DbtSourceUpdated struct {
	domain.BaseDomainEvent
	ProjectID  uuid.UUID `json:"project_id"`
	SourceName string    `json:"source_name"`
}

// DbtRunStarted evento emitido quando uma execução dbt inicia
type DbtRunStarted struct {
	domain.BaseDomainEvent
	RunID     uuid.UUID `json:"run_id"`
	ProjectID uuid.UUID `json:"project_id"`
	Command   string    `json:"command"`
	Args      []string  `json:"args"`
	StartedAt time.Time `json:"started_at"`
}

// DbtRunCompleted evento emitido quando uma execução dbt completa
type DbtRunCompleted struct {
	domain.BaseDomainEvent
	RunID       uuid.UUID `json:"run_id"`
	ProjectID   uuid.UUID `json:"project_id"`
	Command     string    `json:"command"`
	ExitCode    int       `json:"exit_code"`
	DurationMs  int64     `json:"duration_ms"`
	ModelsRun   int       `json:"models_run"`
	TestsRun    int       `json:"tests_run"`
	SeedsRun    int       `json:"seeds_run"`
	Errors      int       `json:"errors"`
	Warnings    int       `json:"warnings"`
	CompletedAt time.Time `json:"completed_at"`
}

// DbtModelExecuted evento emitido quando um model é executado
type DbtModelExecuted struct {
	domain.BaseDomainEvent
	RunID       uuid.UUID `json:"run_id"`
	ProjectID   uuid.UUID `json:"project_id"`
	ModelName   string    `json:"model_name"`
	Status      string    `json:"status"`
	DurationMs  int64     `json:"duration_ms"`
	RowsAffected int64    `json:"rows_affected"`
	ExecutedAt  time.Time `json:"executed_at"`
}

// DbtTestExecuted evento emitido quando um teste é executado
type DbtTestExecuted struct {
	domain.BaseDomainEvent
	RunID      uuid.UUID `json:"run_id"`
	ProjectID  uuid.UUID `json:"project_id"`
	TestName   string    `json:"test_name"`
	Status     string    `json:"status"`
	DurationMs int64     `json:"duration_ms"`
	Failures   int       `json:"failures"`
	ExecutedAt time.Time `json:"executed_at"`
}

// DbtSnapshotExecuted evento emitido quando um snapshot é executado
type DbtSnapshotExecuted struct {
	domain.BaseDomainEvent
	RunID        uuid.UUID `json:"run_id"`
	ProjectID    uuid.UUID `json:"project_id"`
	SnapshotName string    `json:"snapshot_name"`
	Status       string    `json:"status"`
	DurationMs   int64     `json:"duration_ms"`
	RowsAffected int64     `json:"rows_affected"`
	ExecutedAt   time.Time `json:"executed_at"`
}
