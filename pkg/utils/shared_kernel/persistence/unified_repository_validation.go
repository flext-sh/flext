package persistence

import (
	"context"
	"fmt"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/flext-sh/flext/pkg/utils/shared_kernel/errors"
	"github.com/google/uuid"
)

func (r *UnifiedRepository[T]) validateEntity(ctx context.Context, entity T) error {
	if entity.GetID() == uuid.Nil {
		return &errors.DomainError{
			Code:    "INVALID_ENTITY_ID",
			Message: "Entity ID cannot be nil",
			Details: "Entity must have a valid UUID",
		}
	}
	return nil
}

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
