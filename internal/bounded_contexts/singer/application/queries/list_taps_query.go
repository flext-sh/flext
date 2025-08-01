package queries

import (
	"context"

	"github.com/flext/flexcore/internal/bounded_contexts/singer/application/ports"
	"github.com/flext/flexcore/internal/bounded_contexts/singer/domain/entities"
	"github.com/flext/flexcore/internal/shared_kernel/domain/value_objects"
)

// ListTapsQuery represents a query to list taps
type ListTapsQuery struct {
	Page      int      `json:"page" validate:"min=1"`
	PageSize  int      `json:"page_size" validate:"min=1,max=100"`
	Type      string   `json:"type,omitempty"`
	Status    string   `json:"status,omitempty"`
	Search    string   `json:"search,omitempty"`
	Tags      []string `json:"tags,omitempty"`
	SortBy    string   `json:"sort_by,omitempty"`
	SortOrder string   `json:"sort_order,omitempty"`
}

// PaginationInfo represents pagination information
type PaginationInfo struct {
	CurrentPage int   `json:"current_page"`
	PageSize    int   `json:"page_size"`
	TotalItems  int64 `json:"total_items"`
	TotalPages  int   `json:"total_pages"`
	HasNext     bool  `json:"has_next"`
	HasPrevious bool  `json:"has_previous"`
}

// ListTapsResponse represents the response of listing taps
type ListTapsResponse struct {
	Taps       []*TapDTO       `json:"taps"`
	Pagination *PaginationInfo `json:"pagination"`
}

// ListTapsHandler handles list taps queries
type ListTapsHandler struct {
	tapRepo ports.TapRepository
}

// NewListTapsHandler creates a new list taps handler
func NewListTapsHandler(tapRepo ports.TapRepository) *ListTapsHandler {
	return &ListTapsHandler{
		tapRepo: tapRepo,
	}
}

// Handle executes the list taps query
func (h *ListTapsHandler) Handle(ctx context.Context, query ListTapsQuery) (*ListTapsResponse, error) {
	// Validate query
	if err := h.validateQuery(query); err != nil {
		return nil, err
	}

	// Set default values
	if query.Page == 0 {
		query.Page = 1
	}
	if query.PageSize == 0 {
		query.PageSize = 10
	}

	// Build repository options (convert to port options directly)
	portOptions := ports.QueryOptions{
		Limit:     query.PageSize,
		Offset:    (query.Page - 1) * query.PageSize,
		SortBy:    query.SortBy,
		SortOrder: query.SortOrder,
		Filters:   make(map[string]interface{}),
	}

	// Add filters to map
	if query.Type != "" {
		portOptions.Filters["type"] = query.Type
	}
	if query.Status != "" {
		portOptions.Filters["status"] = query.Status
	}
	if query.Search != "" {
		portOptions.Filters["search"] = query.Search
	}
	if len(query.Tags) > 0 {
		portOptions.Filters["tags"] = query.Tags
	}

	// Get taps from repository
	taps, err := h.tapRepo.List(ctx, portOptions)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to list taps",
			Description: err.Error(),
		}
	}

	// Get total count for pagination
	total, err := h.tapRepo.Count(ctx, portOptions)
	if err != nil {
		return nil, &value_objects.DomainError{
			Code:        "REPOSITORY_ERROR",
			Message:     "Failed to count taps",
			Description: err.Error(),
		}
	}

	// Convert to DTOs
	tapDTOs := make([]*TapDTO, len(taps))
	for i, tap := range taps {
		tapDTOs[i] = h.mapToDTO(tap)
	}

	// Calculate pagination
	totalPages := (int64(total) + int64(query.PageSize) - 1) / int64(query.PageSize)
	hasNext := int64(query.Page) < totalPages
	hasPrev := query.Page > 1

	pagination := &PaginationInfo{
		CurrentPage: query.Page,
		PageSize:    query.PageSize,
		TotalItems:  int64(total),
		TotalPages:  int(totalPages),
		HasNext:     hasNext,
		HasPrevious: hasPrev,
	}

	return &ListTapsResponse{
		Taps:       tapDTOs,
		Pagination: pagination,
	}, nil
}

// validateQuery validates the query
func (h *ListTapsHandler) validateQuery(query ListTapsQuery) error {
	if query.Page < 0 {
		return &value_objects.DomainError{
			Code:        "INVALID_PAGE",
			Message:     "Page must be positive",
			Description: "Page number must be greater than 0",
		}
	}

	if query.PageSize < 0 || query.PageSize > 100 {
		return &value_objects.DomainError{
			Code:        "INVALID_PAGE_SIZE",
			Message:     "Page size must be between 1 and 100",
			Description: "PageSize must be in the range [1, 100]",
		}
	}

	return nil
}

// mapToDTO converts tap entity to DTO (reusing from get_tap_query.go)
func (h *ListTapsHandler) mapToDTO(tap *entities.Tap) *TapDTO {
	return &TapDTO{
		ID:                tap.ID.String(),
		Name:              tap.Name,
		DisplayName:       tap.DisplayName,
		Description:       tap.Description,
		Type:              tap.Type,
		Status:            tap.Status,
		TapVersion:        tap.TapVersion,
		PipName:           tap.PipName,
		Executable:        tap.Executable,
		Repository:        tap.Repository,
		HomePage:          tap.HomePage,
		Settings:          tap.Settings,
		ConfigSchema:      tap.ConfigSchema,
		StreamMaps:        tap.StreamMaps,
		Capabilities:      tap.Capabilities,
		SupportedFeatures: tap.SupportedFeatures,
		Author:            tap.Author,
		License:           tap.License,
		Tags:              tap.Tags,
		InstallationPath:  tap.InstallationPath,
		PythonVersion:     tap.PythonVersion,
		Dependencies:      tap.Dependencies,
		UsageCount:        tap.UsageCount,
		CreatedAt:         tap.CreatedAt.Format("2006-01-02T15:04:05Z"),
		UpdatedAt:         tap.UpdatedAt.Format("2006-01-02T15:04:05Z"),
		Version:           tap.Version,
	}
}
