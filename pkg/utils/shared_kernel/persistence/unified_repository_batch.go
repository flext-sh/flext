package persistence

import (
	"context"
	"fmt"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/errors"
)

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

		r.cacheMu.Lock()
		delete(r.cache, id)
		r.cacheMu.Unlock()

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
