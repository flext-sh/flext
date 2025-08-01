package ports

import (
	"context"

	"github.com/flext/flexcore/internal/bounded_contexts/singer/domain/entities"
	"github.com/google/uuid"
)

// SingerSpecRepository define o contrato para persistência de especificações Singer
type SingerSpecRepository interface {
	// CRUD operations
	Save(ctx context.Context, spec *entities.SingerSpec) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.SingerSpec, error)
	FindByName(ctx context.Context, name string) (*entities.SingerSpec, error)
	FindAll(ctx context.Context) ([]*entities.SingerSpec, error)
	Delete(ctx context.Context, id uuid.UUID) error
	Update(ctx context.Context, spec *entities.SingerSpec) error

	// Query operations
	FindByType(ctx context.Context, singerType entities.SingerType) ([]*entities.SingerSpec, error)
	FindActive(ctx context.Context) ([]*entities.SingerSpec, error)
	FindByNameAndType(ctx context.Context, name string, singerType entities.SingerType) (*entities.SingerSpec, error)
	Search(ctx context.Context, query string) ([]*entities.SingerSpec, error)

	// Bulk operations
	SaveAll(ctx context.Context, specs []*entities.SingerSpec) error
	DeleteAll(ctx context.Context, ids []uuid.UUID) error

	// Exists check
	Exists(ctx context.Context, id uuid.UUID) (bool, error)
	ExistsByName(ctx context.Context, name string) (bool, error)
}

// SingerExecutionRepository define o contrato para persistência de execuções Singer
type SingerExecutionRepository interface {
	// CRUD operations
	Save(ctx context.Context, execution *entities.SingerExecution) error
	FindByID(ctx context.Context, id uuid.UUID) (*entities.SingerExecution, error)
	FindAll(ctx context.Context) ([]*entities.SingerExecution, error)
	Delete(ctx context.Context, id uuid.UUID) error
	Update(ctx context.Context, execution *entities.SingerExecution) error

	// Query operations
	FindBySpecID(ctx context.Context, specID uuid.UUID) ([]*entities.SingerExecution, error)
	FindByPipelineID(ctx context.Context, pipelineID uuid.UUID) ([]*entities.SingerExecution, error)
	FindByStatus(ctx context.Context, status entities.ExecutionStatus) ([]*entities.SingerExecution, error)
	FindRunning(ctx context.Context) ([]*entities.SingerExecution, error)
	FindCompleted(ctx context.Context) ([]*entities.SingerExecution, error)
	FindFailed(ctx context.Context) ([]*entities.SingerExecution, error)

	// Pagination
	FindWithPagination(ctx context.Context, offset, limit int) ([]*entities.SingerExecution, int64, error)
	FindBySpecIDWithPagination(ctx context.Context, specID uuid.UUID, offset, limit int) ([]*entities.SingerExecution, int64, error)

	// Statistics
	CountByStatus(ctx context.Context, status entities.ExecutionStatus) (int64, error)
	CountBySpecID(ctx context.Context, specID uuid.UUID) (int64, error)
	GetExecutionStats(ctx context.Context) (map[string]int64, error)

	// Cleanup
	DeleteOldExecutions(ctx context.Context, maxAge int) error
	DeleteBySpecID(ctx context.Context, specID uuid.UUID) error
}

// SingerStateRepository define o contrato para persistência de estados Singer
type SingerStateRepository interface {
	// State management
	SaveState(ctx context.Context, specID uuid.UUID, state *entities.State) error
	GetState(ctx context.Context, specID uuid.UUID) (*entities.State, error)
	DeleteState(ctx context.Context, specID uuid.UUID) error
	ListStates(ctx context.Context) (map[uuid.UUID]*entities.State, error)

	// Stream state management
	SaveStreamState(ctx context.Context, specID uuid.UUID, streamName string, state entities.StreamState) error
	GetStreamState(ctx context.Context, specID uuid.UUID, streamName string) (*entities.StreamState, error)
	DeleteStreamState(ctx context.Context, specID uuid.UUID, streamName string) error
	ListStreamStates(ctx context.Context, specID uuid.UUID) (map[string]entities.StreamState, error)

	// Backup and restore
	BackupState(ctx context.Context, specID uuid.UUID, backupName string) error
	RestoreState(ctx context.Context, specID uuid.UUID, backupName string) error
	ListBackups(ctx context.Context, specID uuid.UUID) ([]string, error)
	DeleteBackup(ctx context.Context, specID uuid.UUID, backupName string) error
}

// EventPublisher define o contrato para publicação de eventos Singer
type EventPublisher interface {
	// Event publishing
	PublishEvent(ctx context.Context, event interface{}) error
	PublishEvents(ctx context.Context, events ...interface{}) error

	// Event subscription
	Subscribe(eventType string, handler func(event interface{}) error) error
	Unsubscribe(eventType string, handler func(event interface{}) error) error
}
