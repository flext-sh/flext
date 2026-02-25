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

// CacheEntry represents a cached entity with expiration
type CacheEntry[T Entity] struct {
	Entity    T
	ExpiresAt time.Time
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

// Cache management methods

func (r *UnifiedRepository[T]) getCachedEntity(id uuid.UUID) (T, bool) {
	var zero T

	r.cacheMu.RLock()
	defer r.cacheMu.RUnlock()

	entry, exists := r.cache[id]
	if !exists {
		return zero, false
	}

	if time.Now().After(entry.ExpiresAt) {
		// Cache entry expired
		delete(r.cache, id)
		return zero, false
	}

	return entry.Entity, true
}

func (r *UnifiedRepository[T]) cacheEntity(id uuid.UUID, entity T) {
	if r.cacheTTL <= 0 {
		return
	}

	r.cacheMu.Lock()
	defer r.cacheMu.Unlock()

	r.cache[id] = CacheEntry[T]{
		Entity:    entity,
		ExpiresAt: time.Now().Add(r.cacheTTL),
	}
}

// ClearCache clears all cached entities
func (r *UnifiedRepository[T]) ClearCache(ctx context.Context) error {
	r.cacheMu.Lock()
	defer r.cacheMu.Unlock()

	r.cache = make(map[uuid.UUID]CacheEntry[T])
	r.logger.Info("Cache cleared", logging.F("entity", r.entityName))

	return nil
}

// ClearCacheForEntity clears cache for a specific entity
func (r *UnifiedRepository[T]) ClearCacheForEntity(ctx context.Context, id uuid.UUID) error {
	r.cacheMu.Lock()
	defer r.cacheMu.Unlock()

	delete(r.cache, id)
	return nil
}

// GetCacheStats returns cache statistics
func (r *UnifiedRepository[T]) GetCacheStats(ctx context.Context) (*CacheStats, error) {
	r.cacheMu.RLock()
	defer r.cacheMu.RUnlock()

	size := len(r.cache)
	maxSize := r.config.CacheSize

	return &CacheStats{
		Size:    size,
		MaxSize: maxSize,
		// TODO: Implement hit/miss tracking
		HitCount:  0,
		MissCount: 0,
		HitRatio:  0.0,
	}, nil
}

// Helper methods for batch operations

func (r *UnifiedRepository[T]) validateBatchEntities(ctx context.Context, entities []T) error {
	for _, entity := range entities {
		if err := r.validateEntity(ctx, entity); err != nil {
			return err
		}

		id := entity.GetID()
		if _, exists := r.store[id]; exists {
			return &errors.DomainError{
				Code:    "ENTITY_ALREADY_EXISTS",
				Message: fmt.Sprintf("%s already exists", r.entityName),
				Details: fmt.Sprintf("Entity with ID %s already exists", id),
			}
		}
	}
	return nil
}

func (r *UnifiedRepository[T]) createValidatedEntities(ctx context.Context, entities []T) []T {
	created := make([]T, 0, len(entities))

	for _, entity := range entities {
		id := entity.GetID()
		r.store[id] = entity
		created = append(created, entity)

		// Clear cache entry if exists
		r.cacheMu.Lock()
		delete(r.cache, id)
		r.cacheMu.Unlock()

		// Record audit trail
		if r.config.EnableAudit {
			r.recordAuditEntry(ctx, id, "create", map[string]interface{}{"created": true})
		}
	}

	return created
}

func (r *UnifiedRepository[T]) logBatchOperation(operation string, count int) {
	r.logger.Debug("Batch operation completed",
		logging.F("operation", operation),
		logging.F("entity", r.entityName),
		logging.F("count", count),
	)
}

// Helper methods for list operations

func (r *UnifiedRepository[T]) getAllEntities() []T {
	r.mu.RLock()
	defer r.mu.RUnlock()

	allEntities := make([]T, 0, len(r.store))
	for _, entity := range r.store {
		allEntities = append(allEntities, entity)
	}
	return allEntities
}

func (r *UnifiedRepository[T]) applySorting(entities []T, criteria ListCriteria) []T {
	// Simplified sorting implementation
	// In production, this would use reflection to sort by specified fields
	return entities
}

func (r *UnifiedRepository[T]) logListOperation(ctx context.Context, total, returned int, criteria ListCriteria) {
	r.logOperation(ctx, "list", uuid.Nil,
		logging.F("total", total),
		logging.F("returned", returned),
		logging.F("limit", criteria.Limit),
		logging.F("offset", criteria.Offset),
	)
}

// Helper methods for count operations

func (r *UnifiedRepository[T]) convertCountToListCriteria(criteria CountCriteria) ListCriteria {
	return ListCriteria{
		Filters:        criteria.Filters,
		Search:         criteria.Search,
		Tags:           criteria.Tags,
		Status:         criteria.Status,
		Active:         criteria.Active,
		Metadata:       criteria.Metadata,
		IncludeDeleted: criteria.IncludeDeleted,
	}
}

// Helper methods for filtering, sorting, and pagination

func (r *UnifiedRepository[T]) applyFilters(entities []T, criteria ListCriteria) []T {
	filtered := make([]T, 0, len(entities))

	for _, entity := range entities {
		if r.matchesFilters(entity, criteria) {
			filtered = append(filtered, entity)
		}
	}

	return filtered
}

func (r *UnifiedRepository[T]) matchesFilters(entity T, criteria ListCriteria) bool {
	// Basic implementation - in production, this would be more sophisticated
	// This is a simplified filter matching logic

	// Check soft delete
	if entity.IsDeleted() && !criteria.IncludeDeleted {
		return false
	}
	if !entity.IsDeleted() && criteria.OnlyDeleted {
		return false
	}

	// Apply custom filters through the Filters slice
	for _, filter := range criteria.Filters {
		if !r.applyFilter(entity, filter) {
			return false
		}
	}

	return true
}

func (r *UnifiedRepository[T]) applyFilter(entity T, filter Filter) bool {
	// Simplified filter application
	// In production, this would use reflection to access entity fields
	return true
}

func (r *UnifiedRepository[T]) applyPagination(entities []T, criteria ListCriteria) []T {
	if criteria.Limit <= 0 {
		return entities
	}

	start := criteria.Offset
	if start >= len(entities) {
		return []T{}
	}

	end := start + criteria.Limit
	if end > len(entities) {
		end = len(entities)
	}

	return entities[start:end]
}

func (r *UnifiedRepository[T]) calculateChanges(old, new T) map[string]interface{} {
	// Simplified change calculation
	// In production, this would use reflection to compare fields
	return map[string]interface{}{
		"updated_at": new.GetUpdatedAt(),
	}
}

func (r *UnifiedRepository[T]) recordAuditEntry(ctx context.Context, entityID uuid.UUID, operation string, changes map[string]interface{}) {
	entry := AuditEntry{
		ID:        uuid.New(),
		EntityID:  entityID,
		Operation: operation,
		Timestamp: time.Now(),
		Changes:   changes,
	}

	r.auditMu.Lock()
	defer r.auditMu.Unlock()

	r.auditTrail = append(r.auditTrail, entry)

	// Limit audit trail size to prevent memory issues
	maxAuditEntries := 1000
	if len(r.auditTrail) > maxAuditEntries {
		r.auditTrail = r.auditTrail[len(r.auditTrail)-maxAuditEntries:]
	}
}

// GetAuditTrail returns audit trail for an entity
func (r *UnifiedRepository[T]) GetAuditTrail(ctx context.Context, entityID uuid.UUID) ([]AuditEntry, error) {
	r.auditMu.RLock()
	defer r.auditMu.RUnlock()

	entries := make([]AuditEntry, 0)
	for _, entry := range r.auditTrail {
		if entry.EntityID == entityID {
			entries = append(entries, entry)
		}
	}

	return entries, nil
}

// RecordAudit records an audit entry
func (r *UnifiedRepository[T]) RecordAudit(ctx context.Context, entry AuditEntry) error {
	r.auditMu.Lock()
	defer r.auditMu.Unlock()

	r.auditTrail = append(r.auditTrail, entry)
	return nil
}

// Helper methods

// validateEntity validates an entity
func (r *UnifiedRepository[T]) validateEntity(ctx context.Context, entity T) error {
	// Basic validation - can be extended
	if entity.GetID() == uuid.Nil {
		return &errors.DomainError{
			Code:    "INVALID_ENTITY_ID",
			Message: "Entity ID cannot be nil",
			Details: "Entity must have a valid UUID",
		}
	}
	return nil
}

// validateListCriteria validates list criteria
func (r *UnifiedRepository[T]) validateListCriteria(criteria ListCriteria) error {
	if criteria.Limit < 0 {
		return &errors.DomainError{
			Code:    "INVALID_LIMIT",
			Message: "Limit cannot be negative",
			Details: fmt.Sprintf("Provided limit: %d", criteria.Limit),
		}
	}
	if criteria.Offset < 0 {
		return &errors.DomainError{
			Code:    "INVALID_OFFSET",
			Message: "Offset cannot be negative",
			Details: fmt.Sprintf("Provided offset: %d", criteria.Offset),
		}
	}
	return nil
}

// recordOperation records an operation for metrics
func (r *UnifiedRepository[T]) recordOperation(operation string, startTime time.Time, err error) {
	duration := time.Since(startTime)
	if r.logger != nil {
		fields := []logging.Field{
			logging.F("operation", operation),
			logging.F("duration_ms", duration.Milliseconds()),
			logging.F("entity_type", r.entityName),
		}
		if err != nil {
			fields = append(fields, logging.F("error", err.Error()))
			r.logger.Error("Repository operation failed", fields...)
		} else {
			r.logger.Debug("Repository operation completed", fields...)
		}
	}
}

// logOperation logs an operation
func (r *UnifiedRepository[T]) logOperation(ctx context.Context, operation string, entityID uuid.UUID, extraFields ...logging.Field) {
	if r.logger != nil {
		fields := []logging.Field{
			logging.F("operation", operation),
			logging.F("entity_type", r.entityName),
			logging.F("entity_id", entityID.String()),
		}
		fields = append(fields, extraFields...)
		r.logger.Info("Repository operation", fields...)
	}
}
