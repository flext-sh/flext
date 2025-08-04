package persistence

import (
	"context"
	"errors"
	"reflect"

	"github.com/flext-sh/flext/pkg/utils/shared_kernel"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/value_objects"
	"gorm.io/gorm"
)

// BaseRepository implementação base para repositórios usando GORM
type BaseRepository[T any] struct {
	db        *gorm.DB
	tableName string
}

// NewBaseRepository cria uma nova instância do repository base
func NewBaseRepository[T any](db *gorm.DB) *BaseRepository[T] {
	repo := &BaseRepository[T]{
		db: db,
	}

	// Inferir nome da tabela a partir do tipo T
	repo.tableName = repo.getTableName()

	return repo
}

// Create cria uma nova entidade
func (r *BaseRepository[T]) Create(ctx context.Context, entity T) error {
	result := r.db.WithContext(ctx).Create(entity)
	if result.Error != nil {
		return r.handleError(result.Error)
	}
	return nil
}

// Update atualiza uma entidade existente
func (r *BaseRepository[T]) Update(ctx context.Context, entity T) error {
	result := r.db.WithContext(ctx).Save(entity)
	if result.Error != nil {
		return r.handleError(result.Error)
	}
	if result.RowsAffected == 0 {
		return &value_objects.DomainError{
			Code:        "ENTITY_NOT_FOUND",
			Message:     "Entity not found for update",
			Description: "No rows were affected during update operation",
		}
	}
	return nil
}

// Delete remove uma entidade pelo ID
func (r *BaseRepository[T]) Delete(ctx context.Context, id string) error {
	var entity T
	result := r.db.WithContext(ctx).Delete(&entity, "id = ?", id)
	if result.Error != nil {
		return r.handleError(result.Error)
	}
	if result.RowsAffected == 0 {
		return &value_objects.DomainError{
			Code:        "ENTITY_NOT_FOUND",
			Message:     "Entity not found for deletion",
			Description: "No rows were affected during delete operation",
		}
	}
	return nil
}

// FindByID encontra uma entidade pelo ID
func (r *BaseRepository[T]) FindByID(ctx context.Context, id string) (T, error) {
	var entity T
	result := r.db.WithContext(ctx).First(&entity, "id = ?", id)
	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return entity, &value_objects.DomainError{
				Code:        "ENTITY_NOT_FOUND",
				Message:     "Entity not found",
				Description: "No entity found with the provided ID",
			}
		}
		return entity, r.handleError(result.Error)
	}
	return entity, nil
}

// Find encontra entidades com opções de query
func (r *BaseRepository[T]) Find(ctx context.Context, opts *value_objects.QueryOptions) (*value_objects.Page[T], error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	// Construir query base
	query := r.db.WithContext(ctx).Model(new(T))

	// Aplicar filtros
	query = r.applyFilters(query, opts.Filters)

	// Contar total de registros
	var total int64
	if err := query.Count(&total).Error; err != nil {
		return nil, r.handleError(err)
	}

	// Aplicar ordenação
	query = r.applySort(query, opts.Sort)

	// Aplicar paginação
	if opts.Pagination != nil {
		query = query.Offset(opts.Pagination.Offset()).Limit(opts.Pagination.PageSize)
	}

	// Executar query
	var entities []T
	if err := query.Find(&entities).Error; err != nil {
		return nil, r.handleError(err)
	}

	// Criar página de resultados
	page := value_objects.NewPage(entities, total, opts.Pagination)
	return page, nil
}

// Count conta o número de entidades que atendem aos critérios
func (r *BaseRepository[T]) Count(ctx context.Context, opts *value_objects.QueryOptions) (int64, error) {
	if opts == nil {
		opts = value_objects.NewQueryOptions()
	}

	query := r.db.WithContext(ctx).Model(new(T))
	query = r.applyFilters(query, opts.Filters)

	var count int64
	if err := query.Count(&count).Error; err != nil {
		return 0, r.handleError(err)
	}

	return count, nil
}

// applyFilters aplica filtros à query
func (r *BaseRepository[T]) applyFilters(query *gorm.DB, filters []value_objects.Filter) *gorm.DB {
	for _, filter := range filters {
		switch filter.Operator {
		case "eq":
			query = query.Where(filter.Field+" = ?", filter.Value)
		case "ne":
			query = query.Where(filter.Field+" != ?", filter.Value)
		case "gt":
			query = query.Where(filter.Field+" > ?", filter.Value)
		case "gte":
			query = query.Where(filter.Field+" >= ?", filter.Value)
		case "lt":
			query = query.Where(filter.Field+" < ?", filter.Value)
		case "lte":
			query = query.Where(filter.Field+" <= ?", filter.Value)
		case "like":
			query = query.Where(filter.Field+" LIKE ?", "%"+filter.Value.(string)+"%")
		case "in":
			query = query.Where(filter.Field+" IN ?", filter.Value)
		}
	}
	return query
}

// applySort aplica ordenação à query
func (r *BaseRepository[T]) applySort(query *gorm.DB, sorts []value_objects.Sort) *gorm.DB {
	for _, sort := range sorts {
		if sort.Field != "" {
			direction := "ASC"
			if sort.Order == "desc" {
				direction = "DESC"
			}
			query = query.Order(sort.Field + " " + direction)
		}
	}
	return query
}

// getTableName infere o nome da tabela a partir do tipo T
func (r *BaseRepository[T]) getTableName() string {
	var entity T
	t := reflect.TypeOf(entity)

	// Se for um pointer, pegar o tipo underlying
	if t.Kind() == reflect.Ptr {
		t = t.Elem()
	}

	// Usar nome do tipo como nome da tabela (em lowercase)
	tableName := t.Name()
	if tableName != "" {
		// Converter para snake_case básico
		return toSnakeCase(tableName)
	}

	return "entities"
}

// handleError trata erros do GORM e os converte para domain errors
func (r *BaseRepository[T]) handleError(err error) error {
	if err == nil {
		return nil
	}

	// Tratar erros específicos do GORM
	if errors.Is(err, gorm.ErrRecordNotFound) {
		return &value_objects.DomainError{
			Code:        "ENTITY_NOT_FOUND",
			Message:     "Entity not found",
			Description: "The requested entity does not exist",
		}
	}

	if errors.Is(err, gorm.ErrDuplicatedKey) {
		return &value_objects.DomainError{
			Code:        "ENTITY_ALREADY_EXISTS",
			Message:     "Entity already exists",
			Description: "An entity with the same unique identifier already exists",
		}
	}

	if errors.Is(err, gorm.ErrInvalidTransaction) {
		return &value_objects.DomainError{
			Code:        "TRANSACTION_ERROR",
			Message:     "Transaction error",
			Description: "Database transaction failed",
		}
	}

	// Erro genérico
	return &value_objects.DomainError{
		Code:        "DATABASE_ERROR",
		Message:     "Database operation failed",
		Description: err.Error(),
	}
}

// toSnakeCase converte CamelCase para snake_case
func toSnakeCase(s string) string {
	var result []rune
	for i, r := range s {
		if i > 0 && r >= 'A' && r <= 'Z' {
			result = append(result, '_')
		}
		if r >= 'A' && r <= 'Z' {
			result = append(result, r+32) // Convert to lowercase
		} else {
			result = append(result, r)
		}
	}
	return string(result)
}

// WithTransaction executa operações dentro de uma transação
func (r *BaseRepository[T]) WithTransaction(ctx context.Context, fn func(repo application.Repository[T]) error) error {
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		txRepo := &BaseRepository[T]{
			db:        tx,
			tableName: r.tableName,
		}
		return fn(txRepo)
	})
}

// GetDB retorna a instância do GORM DB (para casos especiais)
func (r *BaseRepository[T]) GetDB() *gorm.DB {
	return r.db
}
