package persistence

import (
	"context"
	"time"

	"github.com/google/uuid"
)

func (r *UnifiedRepository[T]) calculateChanges(old, new T) map[string]interface{} {
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
