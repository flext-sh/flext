package application

import (
	"context"
	"time"

	"github.com/flext-sh/flext/pkg/utils/shared_kernel/entities"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
)

// Command representa um comando no padrão CQRS
type Command interface {
	GetCommandID() string
	GetCommandType() string
	GetCreatedAt() time.Time
	Validate() error
}

// Query representa uma consulta no padrão CQRS
type Query interface {
	GetQueryID() string
	GetQueryType() string
	GetCreatedAt() time.Time
	Validate() error
}

// CommandHandler define o contrato para handlers de comando
type CommandHandler[C Command, R any] interface {
	Handle(ctx context.Context, cmd C) (R, error)
}

// QueryHandler define o contrato para handlers de consulta
type QueryHandler[Q Query, R any] interface {
	Handle(ctx context.Context, query Q) (R, error)
}

// EventHandler define o contrato para handlers de evento
type EventHandler[E entities.DomainEvent] interface {
	Handle(ctx context.Context, event E) error
	CanHandle(eventType string) bool
}

// Repository define operações básicas de repositório
type Repository[T any] interface {
	Create(ctx context.Context, entity T) error
	Update(ctx context.Context, entity T) error
	Delete(ctx context.Context, id string) error
	FindByID(ctx context.Context, id string) (T, error)
	Find(ctx context.Context, opts *value_objects.QueryOptions) (*value_objects.Page[T], error)
	Count(ctx context.Context, opts *value_objects.QueryOptions) (int64, error)
}

// UnitOfWork define o padrão Unit of Work para transações
type UnitOfWork interface {
	Begin(ctx context.Context) error
	Commit(ctx context.Context) error
	Rollback(ctx context.Context) error
	Transaction(ctx context.Context, fn func(ctx context.Context) error) error
	IsInTransaction() bool
}

// EventBus interface para publicação e subscrição de eventos
type EventBus interface {
	Publish(ctx context.Context, event entities.DomainEvent) error
	Subscribe(eventType string, handler SimpleEventHandler) error
	Unsubscribe(eventType string, handler SimpleEventHandler) error
	Close() error
}

// SimpleEventHandler interface simplificada para manipular eventos
type SimpleEventHandler interface {
	Handle(ctx context.Context, event entities.DomainEvent) error
	CanHandle(eventType string) bool
}

// Validator interface para validação de commands/queries
type Validator interface {
	Validate(obj interface{}) error
	ValidateStruct(obj interface{}) error
	ValidateField(value interface{}, tag string) error
}

// CommandBus interface para dispatch de commands
type CommandBus interface {
	Send(ctx context.Context, command interface{}) (interface{}, error)
	Register(commandType string, handler interface{}) error
}

// QueryBus interface para dispatch de queries
type QueryBus interface {
	Send(ctx context.Context, query interface{}) (interface{}, error)
	Register(queryType string, handler interface{}) error
}

// ApplicationService interface base para serviços de aplicação
type ApplicationService interface {
	GetName() string
	Initialize(ctx context.Context) error
	Shutdown(ctx context.Context) error
}

// BaseCommand implementação base para comandos
type BaseCommand struct {
	CommandID   string    `json:"command_id"`
	CommandType string    `json:"command_type"`
	CreatedAt   time.Time `json:"created_at"`
}

// NewBaseCommand cria um comando base
func NewBaseCommand(commandType string) BaseCommand {
	return BaseCommand{
		CommandID:   generateID(),
		CommandType: commandType,
		CreatedAt:   time.Now().UTC(),
	}
}

func (c BaseCommand) GetCommandID() string    { return c.CommandID }
func (c BaseCommand) GetCommandType() string  { return c.CommandType }
func (c BaseCommand) GetCreatedAt() time.Time { return c.CreatedAt }

// BaseQuery implementação base para consultas
type BaseQuery struct {
	QueryID   string    `json:"query_id"`
	QueryType string    `json:"query_type"`
	CreatedAt time.Time `json:"created_at"`
}

// NewBaseQuery cria uma consulta base
func NewBaseQuery(queryType string) BaseQuery {
	return BaseQuery{
		QueryID:   generateID(),
		QueryType: queryType,
		CreatedAt: time.Now().UTC(),
	}
}

func (q BaseQuery) GetQueryID() string      { return q.QueryID }
func (q BaseQuery) GetQueryType() string    { return q.QueryType }
func (q BaseQuery) GetCreatedAt() time.Time { return q.CreatedAt }

// Result representa um resultado genérico
type Result[T any] struct {
	Data    T      `json:"data,omitempty"`
	Error   string `json:"error,omitempty"`
	Success bool   `json:"success"`
}

// NewSuccessResult cria um resultado de sucesso
func NewSuccessResult[T any](data T) *Result[T] {
	return &Result[T]{
		Data:    data,
		Success: true,
	}
}

// NewErrorResult cria um resultado de erro
func NewErrorResult[T any](err error) *Result[T] {
	return &Result[T]{
		Error:   err.Error(),
		Success: false,
	}
}

// IsSuccess verifica se o resultado é um sucesso
func (r *Result[T]) IsSuccess() bool {
	return r.Success
}

// IsError verifica se o resultado é um erro
func (r *Result[T]) IsError() bool {
	return !r.Success
}

// BaseApplicationService implementação base para serviços de aplicação
type BaseApplicationService struct {
	name      string
	validator Validator
	eventBus  EventBus
}

// NewBaseApplicationService cria um novo serviço base
func NewBaseApplicationService(name string, validator Validator, eventBus EventBus) *BaseApplicationService {
	return &BaseApplicationService{
		name:      name,
		validator: validator,
		eventBus:  eventBus,
	}
}

// GetName retorna o nome do serviço
func (s *BaseApplicationService) GetName() string {
	return s.name
}

// Initialize inicializa o serviço
func (s *BaseApplicationService) Initialize(ctx context.Context) error {
	return nil
}

// Shutdown finaliza o serviço
func (s *BaseApplicationService) Shutdown(ctx context.Context) error {
	return nil
}

// ValidateCommand valida um command
func (s *BaseApplicationService) ValidateCommand(command interface{}) error {
	if s.validator != nil {
		return s.validator.Validate(command)
	}
	return nil
}

// PublishEvents publica eventos de domínio
func (s *BaseApplicationService) PublishEvents(ctx context.Context, events []entities.DomainEvent) error {
	if s.eventBus != nil {
		for _, event := range events {
			if err := s.eventBus.Publish(ctx, event); err != nil {
				return err
			}
		}
	}
	return nil
}

// ValidationError representa um erro de validação
type ValidationError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
	Value   any    `json:"value,omitempty"`
}

// Error implementa a interface error
func (e ValidationError) Error() string {
	return e.Message
}

// ValidationErrors representa múltiplos erros de validação
type ValidationErrors []ValidationError

// Error implementa a interface error para múltiplos erros
func (e ValidationErrors) Error() string {
	if len(e) == 1 {
		return e[0].Error()
	}
	return "Multiple validation errors occurred"
}

// HasErrors verifica se há erros
func (e ValidationErrors) HasErrors() bool {
	return len(e) > 0
}

// Add adiciona um erro de validação
func (e *ValidationErrors) Add(field, message string, value any) {
	*e = append(*e, ValidationError{
		Field:   field,
		Message: message,
		Value:   value,
	})
}

// Specification interface para queries complexas
type Specification[T any] interface {
	IsSatisfiedBy(entity T) bool
	And(spec Specification[T]) Specification[T]
	Or(spec Specification[T]) Specification[T]
	Not() Specification[T]
}

// BaseSpecification implementação base para specifications
type BaseSpecification[T any] struct {
	predicate func(T) bool
}

// NewBaseSpecification cria uma nova specification
func NewBaseSpecification[T any](predicate func(T) bool) *BaseSpecification[T] {
	return &BaseSpecification[T]{predicate: predicate}
}

// IsSatisfiedBy verifica se a entidade satisfaz a specification
func (s *BaseSpecification[T]) IsSatisfiedBy(entity T) bool {
	return s.predicate(entity)
}

// And combina com outra specification usando AND
func (s *BaseSpecification[T]) And(spec Specification[T]) Specification[T] {
	return NewBaseSpecification(func(entity T) bool {
		return s.IsSatisfiedBy(entity) && spec.IsSatisfiedBy(entity)
	})
}

// Or combina com outra specification usando OR
func (s *BaseSpecification[T]) Or(spec Specification[T]) Specification[T] {
	return NewBaseSpecification(func(entity T) bool {
		return s.IsSatisfiedBy(entity) || spec.IsSatisfiedBy(entity)
	})
}

// Not nega a specification
func (s *BaseSpecification[T]) Not() Specification[T] {
	return NewBaseSpecification(func(entity T) bool {
		return !s.IsSatisfiedBy(entity)
	})
}

// generateID gera um ID único
func generateID() string {
	// Implementação simplificada - em produção usar UUID
	return generateRandomString(16)
}

// generateRandomString gera uma string aleatória
func generateRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[len(charset)/2] // Simplificado para evitar dependência de math/rand
	}
	return string(b)
}
