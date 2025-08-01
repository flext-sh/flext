package http

import (
	"strconv"

	"github.com/labstack/echo/v4"

	"github.com/flext/flexcore/internal/bounded_contexts/singer/application/commands"
	"github.com/flext/flexcore/internal/bounded_contexts/singer/application/queries"
	"github.com/flext/flexcore/internal/bounded_contexts/singer/application/services"
	"github.com/flext/flexcore/internal/bounded_contexts/singer/domain/entities"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	base_http "github.com/flext/flexcore/internal/shared_kernel/infrastructure/http"
)

// TapHandler handles HTTP requests for tap operations
type TapHandler struct {
	*base_http.BaseHandler
	tapService *services.TapService
}

// NewTapHandler creates a new tap handler
func NewTapHandler(tapService *services.TapService, logger logging.Logger) *TapHandler {
	return &TapHandler{
		BaseHandler: base_http.NewBaseHandler("tap-handler", logger),
		tapService:  tapService,
	}
}

// GetTap retrieves a single tap by ID
// GET /api/v1/taps/:id
func (h *TapHandler) GetTap(c echo.Context) error {
	tapID := c.Param("id")
	if tapID == "" {
		return h.HandleError(c, &entities.TapError{
			Code:    "INVALID_TAP_ID",
			Message: "Tap ID is required",
		})
	}

	tap, err := h.tapService.GetTap(c.Request().Context(), tapID)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleSuccess(c, tap)
}

// ListTaps retrieves a paginated list of taps
// GET /api/v1/taps
func (h *TapHandler) ListTaps(c echo.Context) error {
	// Parse query parameters
	query := queries.ListTapsQuery{}

	// Parse pagination
	if pageStr := c.QueryParam("page"); pageStr != "" {
		if page, err := strconv.Atoi(pageStr); err == nil && page > 0 {
			query.Page = page
		}
	}
	if pageSizeStr := c.QueryParam("page_size"); pageSizeStr != "" {
		if pageSize, err := strconv.Atoi(pageSizeStr); err == nil && pageSize > 0 {
			query.PageSize = pageSize
		}
	}

	// Parse filters
	query.Type = c.QueryParam("type")
	query.Status = c.QueryParam("status")
	query.Search = c.QueryParam("search")
	query.SortBy = c.QueryParam("sort_by")
	query.SortOrder = c.QueryParam("sort_order")

	// Parse tags (comma-separated)
	if tagsStr := c.QueryParam("tags"); tagsStr != "" {
		// Simple split by comma for now
		query.Tags = []string{tagsStr} // In production, you'd split properly
	}

	response, err := h.tapService.ListTaps(c.Request().Context(), query)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleSuccess(c, response)
}

// InstallTap installs a new tap
// POST /api/v1/taps/install
func (h *TapHandler) InstallTap(c echo.Context) error {
	var cmd commands.InstallTapCommand

	if err := h.ValidateRequest(c, &cmd); err != nil {
		return h.HandleError(c, err)
	}

	tap, err := h.tapService.InstallTap(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleCreated(c, tap)
}

// GetTapStats returns statistics about taps
// GET /api/v1/taps/stats
func (h *TapHandler) GetTapStats(c echo.Context) error {
	stats, err := h.tapService.GetTapStats(c.Request().Context())
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleSuccess(c, stats)
}

// HealthCheck returns the health status of the tap service
// GET /api/v1/taps/health
func (h *TapHandler) HealthCheck(c echo.Context) error {
	err := h.tapService.HealthCheck(c.Request().Context())
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleSuccess(c, map[string]string{
		"status":  "healthy",
		"service": "tap-service",
	})
}

// GetTapTypes returns available tap types
// GET /api/v1/taps/types
func (h *TapHandler) GetTapTypes(c echo.Context) error {
	types := []map[string]string{
		{"value": string(entities.TapTypeExtractor), "label": "Extractor"},
		{"value": string(entities.TapTypeLoader), "label": "Loader"},
		{"value": string(entities.TapTypeUtility), "label": "Utility"},
	}

	return h.HandleSuccess(c, map[string]interface{}{
		"types": types,
	})
}

// GetTapStatuses returns available tap statuses
// GET /api/v1/taps/statuses
func (h *TapHandler) GetTapStatuses(c echo.Context) error {
	statuses := []map[string]string{
		{"value": string(entities.TapStatusInstalled), "label": "Installed"},
		{"value": string(entities.TapStatusNotInstalled), "label": "Not Installed"},
		{"value": string(entities.TapStatusUpdating), "label": "Updating"},
		{"value": string(entities.TapStatusFailed), "label": "Failed"},
		{"value": string(entities.TapStatusDeprecated), "label": "Deprecated"},
	}

	return h.HandleSuccess(c, map[string]interface{}{
		"statuses": statuses,
	})
}

// RegisterRoutes registers all tap routes
func (h *TapHandler) RegisterRoutes(g *echo.Group) {
	// Core CRUD operations
	g.GET("/taps/:id", h.GetTap)
	g.GET("/taps", h.ListTaps)

	// Command operations
	g.POST("/taps/install", h.InstallTap)

	// Utility operations
	g.GET("/taps/stats", h.GetTapStats)
	g.GET("/taps/health", h.HealthCheck)

	// Metadata endpoints
	g.GET("/taps/types", h.GetTapTypes)
	g.GET("/taps/statuses", h.GetTapStatuses)
}
