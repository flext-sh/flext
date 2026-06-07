package persistence

import (
	"context"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	"github.com/google/uuid"
)

// CacheEntry represents a cached entity with expiration
type CacheEntry[T Entity] struct {
	Entity    T
	ExpiresAt time.Time
}

func (r *UnifiedRepository[T]) getCachedEntity(id uuid.UUID) (T, bool) {
	var zero T

	r.cacheMu.RLock()
	defer r.cacheMu.RUnlock()

	entry, exists := r.cache[id]
	if !exists {
		return zero, false
	}

	if time.Now().After(entry.ExpiresAt) {
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
		Size:      size,
		MaxSize:   maxSize,
		HitCount:  0,
		MissCount: 0,
		HitRatio:  0.0,
	}, nil
}
