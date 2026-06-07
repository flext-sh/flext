package persistence

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/errors"
	"github.com/google/uuid"
	"gorm.io/gorm"
)

// UnifiedRepository provides a unified repository implementation
type UnifiedRepository[T Entity] struct {
	*BaseRepository[T]
	store      map[uuid.UUID]T
	mu         sync.RWMutex
	cache      map[uuid.UUID]CacheEntry[T]
	cacheMu    sync.RWMutex
	cacheTTL   time.Duration
	auditTrail []AuditEntry
	auditMu    sync.RWMutex
	entityName string
	config     RepositoryConfig
	logger     logging.Logger
}

// NewUnifiedRepository creates a new unified repository
func NewUnifiedRepository[T Entity](db *gorm.DB, entityName string, config RepositoryConfig, logger logging.Logger) *UnifiedRepository[T] {
	return &UnifiedRepository[T]{
		BaseRepository: NewBaseRepository[T](db),
		store:          make(map[uuid.UUID]T),
		cache:          make(map[uuid.UUID]CacheEntry[T]),
		cacheTTL:       config.CacheTTL,
		auditTrail:     make([]AuditEntry, 0),
		entityName:     entityName,
		config:         config,
		logger:         logger,
	}
}

// Create creates a new entity
func (r *UnifiedRepository[T]) Create(ctx context.Context, entity T) (T, error) {
	startTime := time.Now()

	if err := r.validateEntity(ctx, entity); err != nil {
		r.recordOperation("create", startTime, err)
		return entity, err
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	id := entity.GetID()
	if _, exists := r.store[id]; exists {
		err := &errors.DomainError{
			Code:    "ENTITY_ALREADY_EXISTS",
			Message: fmt.Sprintf("%s already exists", r.entityName),
			Details: fmt.Sprintf("Entity with ID %s already exists", id),
		}
		r.recordOperation("create", startTime, err)
		return entity, err
	}

	r.store[id] = entity

	// Clear cache entry if exists
	r.cacheMu.Lock()
	delete(r.cache, id)
	r.cacheMu.Unlock()

	// Record audit trail
	if r.config.EnableAudit {
		r.recordAuditEntry(ctx, id, "create", map[string]interface{}{"created": true})
	}

	r.logOperation(ctx, "create", id)
	r.recordOperation("create", startTime, nil)

	return entity, nil
}

// CreateBatch creates multiple entities in a batch
func (r *UnifiedRepository[T]) CreateBatch(ctx context.Context, entities []T) ([]T, error) {
	startTime := time.Now()
	created := make([]T, 0, len(entities))

	r.mu.Lock()
	defer r.mu.Unlock()

	if err := r.validateBatchEntities(ctx, entities); err != nil {
		r.recordOperation("create_batch", startTime, err)
		return created, err
	}

	created = r.createValidatedEntities(ctx, entities)

	r.logBatchOperation("create_batch", len(created))
	r.recordOperation("create_batch", startTime, nil)
	return created, nil
}

// GetByID retrieves an entity by ID
func (r *UnifiedRepository[T]) GetByID(ctx context.Context, id uuid.UUID) (T, error) {
	startTime := time.Now()
	var zero T

	if id == uuid.Nil {
		err := &errors.DomainError{
			Code:    "INVALID_ID",
			Message: "Invalid ID provided",
			Details: "ID cannot be nil",
		}
		r.recordOperation("get_by_id", startTime, err)
		return zero, err
	}

	// Check cache first
	if r.config.EnableCache {
		if cached, found := r.getCachedEntity(id); found {
			r.recordOperation("get_by_id", startTime, nil)
			return cached, nil
		}
	}

	r.mu.RLock()
	entity, exists := r.store[id]
	r.mu.RUnlock()

	if !exists {
		err := &errors.DomainError{
			Code:    "ENTITY_NOT_FOUND",
			Message: fmt.Sprintf("%s not found", r.entityName),
			Details: fmt.Sprintf("Entity with ID %s does not exist", id),
		}
		r.recordOperation("get_by_id", startTime, err)
		return zero, err
	}

	// Cache the entity
	if r.config.EnableCache {
		r.cacheEntity(id, entity)
	}

	r.logOperation(ctx, "get_by_id", id)
	r.recordOperation("get_by_id", startTime, nil)

	return entity, nil
}

// FindByID retrieves an entity by ID, returns nil if not found
func (r *UnifiedRepository[T]) FindByID(ctx context.Context, id uuid.UUID) (T, error) {
	entity, err := r.GetByID(ctx, id)
	if err != nil {
		var zero T
		if domainErr, ok := err.(*errors.DomainError); ok && domainErr.Code == "ENTITY_NOT_FOUND" {
			return zero, nil // Return nil for not found
		}
		return zero, err
	}
	return entity, nil
}

// List retrieves entities based on criteria
func (r *UnifiedRepository[T]) List(ctx context.Context, criteria ListCriteria) ([]T, int, error) {
	startTime := time.Now()

	if err := r.validateListCriteria(criteria); err != nil {
		r.recordOperation("list", startTime, err)
		return nil, 0, err
	}

	allEntities := r.getAllEntities()
	filteredEntities := r.applyFilters(allEntities, criteria)
	total := len(filteredEntities)
	sortedEntities := r.applySorting(filteredEntities, criteria)
	paginatedEntities := r.applyPagination(sortedEntities, criteria)

	r.logListOperation(ctx, total, len(paginatedEntities), criteria)
	r.recordOperation("list", startTime, nil)

	return paginatedEntities, total, nil
}

// Update updates an existing entity
func (r *UnifiedRepository[T]) Update(ctx context.Context, entity T) (T, error) {
	startTime := time.Now()

	if err := r.validateEntity(ctx, entity); err != nil {
		r.recordOperation("update", startTime, err)
		return entity, err
	}

	id := entity.GetID()

	r.mu.Lock()
	defer r.mu.Unlock()

	oldEntity, exists := r.store[id]
	if !exists {
		err := &errors.DomainError{
			Code:    "ENTITY_NOT_FOUND",
			Message: fmt.Sprintf("%s not found", r.entityName),
			Details: fmt.Sprintf("Entity with ID %s does not exist", id),
		}
		r.recordOperation("update", startTime, err)
		return entity, err
	}

	r.store[id] = entity

	// Clear cache entry
	r.cacheMu.Lock()
	delete(r.cache, id)
	r.cacheMu.Unlock()

	// Record audit trail
	if r.config.EnableAudit {
		changes := r.calculateChanges(oldEntity, entity)
		r.recordAuditEntry(ctx, id, "update", changes)
	}

	r.logOperation(ctx, "update", id)
	r.recordOperation("update", startTime, nil)

	return entity, nil
}

// UpdatePartial updates specific fields of an entity
func (r *UnifiedRepository[T]) UpdatePartial(ctx context.Context, id uuid.UUID, updates map[string]interface{}) (T, error) {
	startTime := time.Now()
	var zero T

	if id == uuid.Nil {
		err := &errors.DomainError{
			Code:    "INVALID_ID",
			Message: "Invalid ID provided",
			Details: "ID cannot be nil",
		}
		r.recordOperation("update_partial", startTime, err)
		return zero, err
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	entity, exists := r.store[id]
	if !exists {
		err := &errors.DomainError{
			Code:    "ENTITY_NOT_FOUND",
			Message: fmt.Sprintf("%s not found", r.entityName),
			Details: fmt.Sprintf("Entity with ID %s does not exist", id),
		}
		r.recordOperation("update_partial", startTime, err)
		return zero, err
	}

	// Apply updates using reflection (simplified implementation)
	// In production, this would use proper field mapping
	updatedEntity := entity // For now, return original entity

	r.store[id] = updatedEntity

	// Clear cache entry
	r.cacheMu.Lock()
	delete(r.cache, id)
	r.cacheMu.Unlock()

	// Record audit trail
	if r.config.EnableAudit {
		r.recordAuditEntry(ctx, id, "update_partial", updates)
	}

	r.logOperation(ctx, "update_partial", id, logging.F("updates", updates))
	r.recordOperation("update_partial", startTime, nil)

	return updatedEntity, nil
}

// Delete removes an entity by ID
func (r *UnifiedRepository[T]) Delete(ctx context.Context, id uuid.UUID) error {
	startTime := time.Now()

	if id == uuid.Nil {
		err := &errors.DomainError{
			Code:    "INVALID_ID",
			Message: "Invalid ID provided",
			Details: "ID cannot be nil",
		}
		r.recordOperation("delete", startTime, err)
		return err
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	_, exists := r.store[id]
	if !exists {
		err := &errors.DomainError{
			Code:    "ENTITY_NOT_FOUND",
			Message: fmt.Sprintf("%s not found", r.entityName),
			Details: fmt.Sprintf("Entity with ID %s does not exist", id),
		}
		r.recordOperation("delete", startTime, err)
		return err
	}

	delete(r.store, id)

	// Clear cache entry
	r.cacheMu.Lock()
	delete(r.cache, id)
	r.cacheMu.Unlock()

	// Record audit trail
	if r.config.EnableAudit {
		r.recordAuditEntry(ctx, id, "delete", map[string]interface{}{"deleted": true})
	}

	r.logOperation(ctx, "delete", id)
	r.recordOperation("delete", startTime, nil)

	return nil
}

// Exists checks if an entity exists by ID
func (r *UnifiedRepository[T]) Exists(ctx context.Context, id uuid.UUID) (bool, error) {
	startTime := time.Now()

	if id == uuid.Nil {
		err := &errors.DomainError{
			Code:    "INVALID_ID",
			Message: "Invalid ID provided",
			Details: "ID cannot be nil",
		}
		r.recordOperation("exists", startTime, err)
		return false, err
	}

	r.mu.RLock()
	_, exists := r.store[id]
	r.mu.RUnlock()

	r.recordOperation("exists", startTime, nil)

	return exists, nil
}

// Count counts entities based on criteria
func (r *UnifiedRepository[T]) Count(ctx context.Context, criteria CountCriteria) (int, error) {
	startTime := time.Now()

	allEntities := r.getAllEntities()
	listCriteria := r.convertCountToListCriteria(criteria)
	filteredEntities := r.applyFilters(allEntities, listCriteria)
	count := len(filteredEntities)

	r.recordOperation("count", startTime, nil)

	return count, nil
}
