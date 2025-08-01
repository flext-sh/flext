package persistence

import (
	"context"
	"sort"
	"strings"
	"sync"

	"github.com/flext/flexcore/internal/bounded_contexts/singer/application/ports"
	"github.com/flext/flexcore/internal/bounded_contexts/singer/domain/entities"
	"github.com/flext/flexcore/internal/shared_kernel/domain/value_objects"
	"github.com/google/uuid"
)

// MemoryTapRepository provides an in-memory implementation for testing
type MemoryTapRepository struct {
	mu   sync.RWMutex
	taps map[uuid.UUID]*entities.Tap
}

// NewMemoryTapRepository creates a new in-memory tap repository
func NewMemoryTapRepository() *MemoryTapRepository {
	return &MemoryTapRepository{
		taps: make(map[uuid.UUID]*entities.Tap),
	}
}

// Save stores a tap in memory
func (r *MemoryTapRepository) Save(ctx context.Context, tap *entities.Tap) error {
	if tap == nil {
		return &value_objects.DomainError{
			Code:        "INVALID_TAP",
			Message:     "Tap cannot be nil",
			Description: "Cannot save nil tap",
		}
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	r.taps[tap.ID] = tap
	return nil
}

// GetByID retrieves a tap by ID
func (r *MemoryTapRepository) GetByID(ctx context.Context, id uuid.UUID) (*entities.Tap, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	tap, exists := r.taps[id]
	if !exists {
		return nil, &value_objects.DomainError{
			Code:        "TAP_NOT_FOUND",
			Message:     "Tap not found",
			Description: "Tap with the specified ID does not exist",
		}
	}

	return tap, nil
}

// GetByName retrieves a tap by name
func (r *MemoryTapRepository) GetByName(ctx context.Context, name string) (*entities.Tap, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	for _, tap := range r.taps {
		if tap.Name == name {
			return tap, nil
		}
	}

	return nil, &value_objects.DomainError{
		Code:        "TAP_NOT_FOUND",
		Message:     "Tap not found",
		Description: "Tap with the specified name does not exist",
	}
}

// Update updates a tap
func (r *MemoryTapRepository) Update(ctx context.Context, tap *entities.Tap) (*entities.Tap, error) {
	if tap == nil {
		return nil, &value_objects.DomainError{
			Code:        "INVALID_TAP",
			Message:     "Tap cannot be nil",
			Description: "Cannot update nil tap",
		}
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.taps[tap.ID]; !exists {
		return nil, &value_objects.DomainError{
			Code:        "TAP_NOT_FOUND",
			Message:     "Tap not found",
			Description: "Cannot update non-existent tap",
		}
	}

	r.taps[tap.ID] = tap
	return tap, nil
}

// Delete removes a tap by ID
func (r *MemoryTapRepository) Delete(ctx context.Context, id uuid.UUID) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.taps[id]; !exists {
		return &value_objects.DomainError{
			Code:        "TAP_NOT_FOUND",
			Message:     "Tap not found",
			Description: "Cannot delete non-existent tap",
		}
	}

	delete(r.taps, id)
	return nil
}

// List retrieves taps with filtering and pagination
func (r *MemoryTapRepository) List(ctx context.Context, options ports.QueryOptions) ([]*entities.Tap, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	taps := r.getAllTaps()
	filteredTaps := r.processFilters(taps, options)
	sortedTaps := r.processSorting(filteredTaps, options)
	paginatedTaps := r.processPagination(sortedTaps, options)

	return paginatedTaps, nil
}

// Count returns the total number of taps matching the criteria
func (r *MemoryTapRepository) Count(ctx context.Context, options ports.QueryOptions) (int, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	taps := r.getAllTaps()
	filteredTaps := r.processFilters(taps, options)

	return len(filteredTaps), nil
}

// GetInstalledTaps returns all installed taps
func (r *MemoryTapRepository) GetInstalledTaps(ctx context.Context) ([]*entities.Tap, error) {
	options := ports.QueryOptions{
		Filters: map[string]interface{}{
			"status": entities.TapStatusInstalled,
		},
	}

	return r.List(ctx, options)
}

// GetTapsByType returns taps of a specific type
func (r *MemoryTapRepository) GetTapsByType(ctx context.Context, tapType entities.TapType) ([]*entities.Tap, error) {
	options := ports.QueryOptions{
		Filters: map[string]interface{}{
			"type": tapType,
		},
	}

	return r.List(ctx, options)
}

// GetTapsByStatus returns taps with a specific status
func (r *MemoryTapRepository) GetTapsByStatus(ctx context.Context, status entities.TapStatus) ([]*entities.Tap, error) {
	options := ports.QueryOptions{
		Filters: map[string]interface{}{
			"status": status,
		},
	}

	return r.List(ctx, options)
}

// SearchTaps searches taps by query string
func (r *MemoryTapRepository) SearchTaps(ctx context.Context, query string, options ports.QueryOptions) ([]*entities.Tap, error) {
	if options.Filters == nil {
		options.Filters = make(map[string]interface{})
	}
	options.Filters["search"] = query

	return r.List(ctx, options)
}

// GetTapsByTags returns taps that have any of the specified tags
func (r *MemoryTapRepository) GetTapsByTags(ctx context.Context, tags []string) ([]*entities.Tap, error) {
	options := ports.QueryOptions{
		Filters: map[string]interface{}{
			"tags": tags,
		},
	}

	return r.List(ctx, options)
}

// GetMostUsedTaps returns the most used taps
func (r *MemoryTapRepository) GetMostUsedTaps(ctx context.Context, limit int) ([]*entities.Tap, error) {
	options := ports.QueryOptions{
		SortBy:    "usage_count",
		SortOrder: "desc",
		Limit:     limit,
	}

	return r.List(ctx, options)
}

// GetRecentlyUsedTaps returns recently used taps
func (r *MemoryTapRepository) GetRecentlyUsedTaps(ctx context.Context, limit int) ([]*entities.Tap, error) {
	options := ports.QueryOptions{
		SortBy:    "last_used",
		SortOrder: "desc",
		Limit:     limit,
	}

	return r.List(ctx, options)
}

// Helper methods for List processing

func (r *MemoryTapRepository) getAllTaps() []*entities.Tap {
	var taps []*entities.Tap
	for _, tap := range r.taps {
		taps = append(taps, tap)
	}
	return taps
}

func (r *MemoryTapRepository) processFilters(taps []*entities.Tap, options ports.QueryOptions) []*entities.Tap {
	if options.Filters != nil {
		return r.applyFilters(taps, options.Filters)
	}
	return taps
}

func (r *MemoryTapRepository) processSorting(taps []*entities.Tap, options ports.QueryOptions) []*entities.Tap {
	if options.SortBy != "" {
		r.sortTaps(taps, options.SortBy, options.SortOrder)
	}
	return taps
}

func (r *MemoryTapRepository) processPagination(taps []*entities.Tap, options ports.QueryOptions) []*entities.Tap {
	total := len(taps)
	if options.Offset > 0 {
		if options.Offset >= total {
			return []*entities.Tap{}
		}
		taps = taps[options.Offset:]
	}

	if options.Limit > 0 && options.Limit < len(taps) {
		taps = taps[:options.Limit]
	}

	return taps
}

func (r *MemoryTapRepository) compareByField(tap1, tap2 *entities.Tap, sortBy string) bool {
	switch sortBy {
	case "name":
		return tap1.Name < tap2.Name
	case "created_at":
		return tap1.CreatedAt.Before(tap2.CreatedAt)
	case "updated_at":
		return tap1.UpdatedAt.Before(tap2.UpdatedAt)
	case "usage_count":
		return tap1.UsageCount < tap2.UsageCount
	case "last_used":
		return r.compareLastUsed(tap1, tap2)
	default:
		return tap1.Name < tap2.Name // Default sort by name
	}
}

func (r *MemoryTapRepository) compareLastUsed(tap1, tap2 *entities.Tap) bool {
	if tap1.LastUsed == nil && tap2.LastUsed == nil {
		return false
	}
	if tap1.LastUsed == nil {
		return true
	}
	if tap2.LastUsed == nil {
		return false
	}
	return tap1.LastUsed.Before(*tap2.LastUsed)
}

// applyFilters applies various filters to the tap list
func (r *MemoryTapRepository) applyFilters(taps []*entities.Tap, filters map[string]interface{}) []*entities.Tap {
	var result []*entities.Tap

	for _, tap := range taps {
		if r.matchesFilters(tap, filters) {
			result = append(result, tap)
		}
	}

	return result
}

// matchesFilters checks if a tap matches all the specified filters
func (r *MemoryTapRepository) matchesFilters(tap *entities.Tap, filters map[string]interface{}) bool {
	for key, value := range filters {
		switch key {
		case "type":
			// Handle both string and TapType values
			var expectedType entities.TapType
			switch v := value.(type) {
			case entities.TapType:
				expectedType = v
			case string:
				expectedType = entities.TapType(v)
			default:
				return false
			}
			if tap.Type != expectedType {
				return false
			}
		case "status":
			// Handle both string and TapStatus values
			var expectedStatus entities.TapStatus
			switch v := value.(type) {
			case entities.TapStatus:
				expectedStatus = v
			case string:
				expectedStatus = entities.TapStatus(v)
			default:
				return false
			}
			if tap.Status != expectedStatus {
				return false
			}
		case "search":
			query := strings.ToLower(value.(string))
			if !strings.Contains(strings.ToLower(tap.Name), query) &&
				!strings.Contains(strings.ToLower(tap.Description), query) {
				return false
			}
		case "tags":
			requiredTags := value.([]string)
			if !r.hasAnyTag(tap.Tags, requiredTags) {
				return false
			}
		}
	}
	return true
}

// hasAnyTag checks if the tap has any of the required tags
func (r *MemoryTapRepository) hasAnyTag(tapTags, requiredTags []string) bool {
	for _, required := range requiredTags {
		for _, tapTag := range tapTags {
			if tapTag == required {
				return true
			}
		}
	}
	return false
}

// sortTaps sorts the tap slice by the specified field and order
func (r *MemoryTapRepository) sortTaps(taps []*entities.Tap, sortBy, sortOrder string) {
	sort.Slice(taps, func(i, j int) bool {
		less := r.compareByField(taps[i], taps[j], sortBy)
		if sortOrder == "desc" {
			return !less
		}
		return less
	})
}
