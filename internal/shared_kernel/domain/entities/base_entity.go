package entities

import (
	"time"

	"github.com/flext/flexcore/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// Entity interface unificada para todas as entidades de domínio
type Entity interface {
	// Identity management
	GetID() uuid.UUID
	SetID(id uuid.UUID)

	// Timestamps
	GetCreatedAt() time.Time
	GetUpdatedAt() time.Time
	SetUpdatedAt(t time.Time)

	// Soft delete
	IsDeleted() bool
	Delete() error
	Restore() error
	GetDeletedAt() *time.Time

	// Validation
	Validate() error
	IsValid() bool

	// Version control
	GetVersion() int64
	IncrementVersion()

	// Metadata
	GetMetadata() map[string]interface{}
	SetMetadata(key string, value interface{})

	// String representation
	String() string
}

// AggregateRoot interface unificada para raízes de agregados
type AggregateRoot interface {
	Entity

	// Domain events
	GetDomainEvents() []DomainEvent
	ClearDomainEvents()
	AddDomainEvent(event DomainEvent)

	// Aggregate-specific behaviors
	GetAggregateID() uuid.UUID
	GetAggregateType() string
	CheckInvariants() error

	// Snapshot support
	CreateSnapshot() (*AggregateSnapshot, error)
	LoadFromSnapshot(snapshot *AggregateSnapshot) error
}

// DomainEvent interface unificada para eventos de domínio
type DomainEvent interface {
	GetEventID() uuid.UUID
	GetAggregateID() uuid.UUID
	GetEventType() string
	GetEventData() map[string]interface{}
	GetOccurredAt() time.Time
	GetVersion() int64
}

// AggregateSnapshot representa um snapshot de um agregado
type AggregateSnapshot struct {
	AggregateID   uuid.UUID              `json:"aggregate_id"`
	AggregateType string                 `json:"aggregate_type"`
	Version       int64                  `json:"version"`
	Data          map[string]interface{} `json:"data"`
	CreatedAt     time.Time              `json:"created_at"`
}

// BaseEntity implementação unificada da interface Entity
type BaseEntity struct {
	ID           uuid.UUID              `json:"id" gorm:"type:uuid;primary_key" db:"id"`
	CreatedAt    time.Time              `json:"created_at" gorm:"autoCreateTime" db:"created_at"`
	UpdatedAt    time.Time              `json:"updated_at" gorm:"autoUpdateTime" db:"updated_at"`
	DeletedAt    *time.Time             `json:"deleted_at,omitempty" gorm:"index" db:"deleted_at"`
	Version      int64                  `json:"version" gorm:"default:1" db:"version"`
	Metadata     map[string]interface{} `json:"metadata,omitempty" gorm:"type:jsonb" db:"metadata"`
	domainEvents []DomainEvent          `json:"-" gorm:"-"`
}

// NewBaseEntity cria uma nova instância de BaseEntity
func NewBaseEntity() *BaseEntity {
	return &BaseEntity{
		ID:           uuid.New(),
		CreatedAt:    time.Now().UTC(),
		UpdatedAt:    time.Now().UTC(),
		Version:      1,
		Metadata:     make(map[string]interface{}),
		domainEvents: make([]DomainEvent, 0),
	}
}

// GetID retorna o ID da entidade
func (e *BaseEntity) GetID() uuid.UUID {
	return e.ID
}

// SetID define o ID da entidade
func (e *BaseEntity) SetID(id uuid.UUID) {
	e.ID = id
}

// GetCreatedAt retorna a data de criação
func (e *BaseEntity) GetCreatedAt() time.Time {
	return e.CreatedAt
}

// GetUpdatedAt retorna a data de atualização
func (e *BaseEntity) GetUpdatedAt() time.Time {
	return e.UpdatedAt
}

// SetUpdatedAt define a data de atualização
func (e *BaseEntity) SetUpdatedAt(t time.Time) {
	e.UpdatedAt = t
	e.IncrementVersion()
}

// IsDeleted verifica se a entidade foi excluída
func (e *BaseEntity) IsDeleted() bool {
	return e.DeletedAt != nil
}

// Delete marca a entidade como excluída (soft delete)
func (e *BaseEntity) Delete() error {
	if e.IsDeleted() {
		return &value_objects.DomainError{
			Code:        "ENTITY_ALREADY_DELETED",
			Message:     "Entity is already deleted",
			Description: "Cannot delete an entity that is already marked as deleted",
		}
	}

	now := time.Now().UTC()
	e.DeletedAt = &now
	e.SetUpdatedAt(now)

	return nil
}

// Restore restaura uma entidade excluída
func (e *BaseEntity) Restore() error {
	if !e.IsDeleted() {
		return &value_objects.DomainError{
			Code:        "ENTITY_NOT_DELETED",
			Message:     "Entity is not deleted",
			Description: "Cannot restore an entity that is not marked as deleted",
		}
	}

	e.DeletedAt = nil
	e.SetUpdatedAt(time.Now().UTC())

	return nil
}

// GetDeletedAt retorna a data de exclusão
func (e *BaseEntity) GetDeletedAt() *time.Time {
	return e.DeletedAt
}

// Validate valida a entidade
func (e *BaseEntity) Validate() error {
	if e.ID == uuid.Nil {
		return &value_objects.DomainError{
			Code:        "INVALID_ENTITY_ID",
			Message:     "Entity ID cannot be empty",
			Description: "All entities must have a valid UUID",
		}
	}

	if e.CreatedAt.IsZero() {
		return &value_objects.DomainError{
			Code:        "INVALID_CREATED_AT",
			Message:     "Created at cannot be zero",
			Description: "All entities must have a valid creation timestamp",
		}
	}

	if e.UpdatedAt.IsZero() {
		return &value_objects.DomainError{
			Code:        "INVALID_UPDATED_AT",
			Message:     "Updated at cannot be zero",
			Description: "All entities must have a valid update timestamp",
		}
	}

	if e.Version <= 0 {
		return &value_objects.DomainError{
			Code:        "INVALID_VERSION",
			Message:     "Version must be positive",
			Description: "Entity version must be a positive number",
		}
	}

	return nil
}

// IsValid verifica se a entidade é válida
func (e *BaseEntity) IsValid() bool {
	return e.Validate() == nil
}

// GetVersion retorna a versão da entidade
func (e *BaseEntity) GetVersion() int64 {
	return e.Version
}

// IncrementVersion incrementa a versão da entidade
func (e *BaseEntity) IncrementVersion() {
	e.Version++
}

// GetMetadata retorna os metadados da entidade
func (e *BaseEntity) GetMetadata() map[string]interface{} {
	if e.Metadata == nil {
		e.Metadata = make(map[string]interface{})
	}
	return e.Metadata
}

// SetMetadata define um metadado
func (e *BaseEntity) SetMetadata(key string, value interface{}) {
	if e.Metadata == nil {
		e.Metadata = make(map[string]interface{})
	}
	e.Metadata[key] = value
	e.SetUpdatedAt(time.Now().UTC())
}

// String retorna uma representação em string da entidade
func (e *BaseEntity) String() string {
	return e.ID.String()
}

// BaseAggregateRoot implementação unificada de AggregateRoot
type BaseAggregateRoot struct {
	*BaseEntity
	AggregateType string `json:"aggregate_type" gorm:"index" db:"aggregate_type"`
}

// NewBaseAggregateRoot cria uma nova raiz de agregado
func NewBaseAggregateRoot(aggregateType string) *BaseAggregateRoot {
	return &BaseAggregateRoot{
		BaseEntity:    NewBaseEntity(),
		AggregateType: aggregateType,
	}
}

// GetDomainEvents retorna os eventos de domínio
func (a *BaseAggregateRoot) GetDomainEvents() []DomainEvent {
	return a.domainEvents
}

// ClearDomainEvents limpa os eventos de domínio
func (a *BaseAggregateRoot) ClearDomainEvents() {
	a.domainEvents = make([]DomainEvent, 0)
}

// AddDomainEvent adiciona um evento de domínio
func (a *BaseAggregateRoot) AddDomainEvent(event DomainEvent) {
	a.domainEvents = append(a.domainEvents, event)
}

// GetAggregateID retorna o ID do agregado
func (a *BaseAggregateRoot) GetAggregateID() uuid.UUID {
	return a.ID
}

// GetAggregateType retorna o tipo do agregado
func (a *BaseAggregateRoot) GetAggregateType() string {
	return a.AggregateType
}

// CheckInvariants verifica as invariantes do negócio (implementação padrão)
func (a *BaseAggregateRoot) CheckInvariants() error {
	return a.Validate()
}

// CreateSnapshot cria um snapshot do agregado
func (a *BaseAggregateRoot) CreateSnapshot() (*AggregateSnapshot, error) {
	return &AggregateSnapshot{
		AggregateID:   a.ID,
		AggregateType: a.AggregateType,
		Version:       a.Version,
		Data: map[string]interface{}{
			"created_at": a.CreatedAt,
			"updated_at": a.UpdatedAt,
			"deleted_at": a.DeletedAt,
			"metadata":   a.Metadata,
		},
		CreatedAt: time.Now().UTC(),
	}, nil
}

// LoadFromSnapshot carrega o agregado a partir de um snapshot
func (a *BaseAggregateRoot) LoadFromSnapshot(snapshot *AggregateSnapshot) error {
	if snapshot.AggregateID != a.ID {
		return &value_objects.DomainError{
			Code:        "SNAPSHOT_MISMATCH",
			Message:     "Snapshot aggregate ID does not match",
			Description: "Cannot load snapshot from different aggregate",
		}
	}

	a.Version = snapshot.Version

	// Load basic fields from snapshot data
	if createdAt, ok := snapshot.Data["created_at"].(time.Time); ok {
		a.CreatedAt = createdAt
	}

	if updatedAt, ok := snapshot.Data["updated_at"].(time.Time); ok {
		a.UpdatedAt = updatedAt
	}

	if deletedAt, ok := snapshot.Data["deleted_at"].(*time.Time); ok {
		a.DeletedAt = deletedAt
	}

	if metadata, ok := snapshot.Data["metadata"].(map[string]interface{}); ok {
		a.Metadata = metadata
	}

	return nil
}

// BaseDomainEvent implementação unificada de DomainEvent
type BaseDomainEvent struct {
	EventID     uuid.UUID              `json:"event_id"`
	AggregateID uuid.UUID              `json:"aggregate_id"`
	EventType   string                 `json:"event_type"`
	EventData   map[string]interface{} `json:"event_data"`
	OccurredAt  time.Time              `json:"occurred_at"`
	Version     int64                  `json:"version"`
}

// NewBaseDomainEvent cria um novo evento de domínio
func NewBaseDomainEvent(eventType string, aggregateID uuid.UUID, eventData map[string]interface{}, version int64) *BaseDomainEvent {
	return &BaseDomainEvent{
		EventID:     uuid.New(),
		AggregateID: aggregateID,
		EventType:   eventType,
		EventData:   eventData,
		OccurredAt:  time.Now().UTC(),
		Version:     version,
	}
}

// GetEventID retorna o ID do evento
func (e *BaseDomainEvent) GetEventID() uuid.UUID {
	return e.EventID
}

// GetAggregateID retorna o ID do agregado
func (e *BaseDomainEvent) GetAggregateID() uuid.UUID {
	return e.AggregateID
}

// GetEventType retorna o tipo do evento
func (e *BaseDomainEvent) GetEventType() string {
	return e.EventType
}

// GetEventData retorna os dados do evento
func (e *BaseDomainEvent) GetEventData() map[string]interface{} {
	return e.EventData
}

// GetOccurredAt retorna quando o evento ocorreu
func (e *BaseDomainEvent) GetOccurredAt() time.Time {
	return e.OccurredAt
}

// GetVersion retorna a versão do evento
func (e *BaseDomainEvent) GetVersion() int64 {
	return e.Version
}
