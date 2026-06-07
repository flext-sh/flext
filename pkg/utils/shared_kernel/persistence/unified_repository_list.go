package persistence

import (
	"context"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

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
	if entity.IsDeleted() && !criteria.IncludeDeleted {
		return false
	}
	if !entity.IsDeleted() && criteria.OnlyDeleted {
		return false
	}

	for _, filter := range criteria.Filters {
		if !r.applyFilter(entity, filter) {
			return false
		}
	}

	return true
}

func (r *UnifiedRepository[T]) applyFilter(entity T, filter Filter) bool {
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
