package http

import (
	"net/http"
	"strings"

	"github.com/flext-sh/flext/pkg/domain/plugin/application"
	"github.com/flext-sh/flext/pkg/domain/plugin/application/commands"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	shared_kernel_http "github.com/flext-sh/flext/pkg/infrastructure/http"
	"github.com/flext-sh/flext/pkg/validation"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// PluginHandler manipula requisições HTTP para plugins
type PluginHandler struct {
	*shared_kernel_http.BaseHandler
	service *application.PluginService
}

// NewPluginHandler cria um novo handler HTTP
func NewPluginHandler(service *application.PluginService, logger logging.Logger) *PluginHandler {
	return &PluginHandler{
		BaseHandler: shared_kernel_http.NewBaseHandler("PluginHandler", logger),
		service:     service,
	}
}

// RegisterPlugin manipula POST /api/v1/plugins
func (h *PluginHandler) RegisterPlugin(c echo.Context) error {
	var cmd commands.RegisterPluginCommand
	if err := h.ValidateRequest(c, &cmd); err != nil {
		return h.HandleError(c, err)
	}

	// Sanitize input data
	cmd.Name = validation.SanitizeString(cmd.Name)
	cmd.Type = validation.SanitizeString(cmd.Type)
	cmd.Version = validation.SanitizeString(cmd.Version)
	cmd.Description = validation.SanitizeString(cmd.Description)
	cmd.Author = validation.SanitizeString(cmd.Author)
	cmd.EntryPoint = validation.SanitizeString(cmd.EntryPoint)

	// Sanitize dependencies
	sanitizedDeps := make([]string, len(cmd.Dependencies))
	for i, dep := range cmd.Dependencies {
		sanitizedDeps[i] = validation.SanitizeString(dep)
	}
	cmd.Dependencies = sanitizedDeps

	result, err := h.service.RegisterPlugin(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleCreated(c, result)
}

// GetPlugin manipula GET /api/v1/plugins/:id
func (h *PluginHandler) GetPlugin(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return h.HandleError(c, err)
	}

	result, err := h.service.GetPlugin(c.Request().Context(), id)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleSuccess(c, result)
}

// ListPlugins manipula GET /api/v1/plugins
func (h *PluginHandler) ListPlugins(c echo.Context) error {
	pagination := h.ParsePagination(c)

	// Parse filters
	pluginType := strings.TrimSpace(c.QueryParam("type"))
	status := strings.TrimSpace(c.QueryParam("status"))
	author := strings.TrimSpace(c.QueryParam("author"))

	result, err := h.service.ListPlugins(c.Request().Context(), pagination.PageSize, pagination.Offset(), pluginType, status, author)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandlePaginatedSuccess(c, result, pagination)
}

// UnregisterPlugin manipula DELETE /api/v1/plugins/:id
func (h *PluginHandler) UnregisterPlugin(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return h.HandleError(c, err)
	}

	err = h.service.UnregisterPlugin(c.Request().Context(), id)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleNoContent(c)
}

// UpdatePlugin manipula PUT /api/v1/plugins/:id
func (h *PluginHandler) UpdatePlugin(c echo.Context) error {
	idStr := c.Param("id")

	// Validate and sanitize ID parameter
	idStr = validation.SanitizeString(idStr)
	if idStr == "" {
		return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
			Error:   "Bad request",
			Message: "Plugin ID is required",
			Code:    "BAD_REQUEST",
		})
	}

	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
			Error:   "Bad request",
			Message: "Invalid plugin ID format",
			Code:    "BAD_REQUEST",
		})
	}

	var updateData map[string]interface{}
	if err := c.Bind(&updateData); err != nil {
		return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
			Error:   "Bad request",
			Message: "Invalid request body format",
			Code:    "BAD_REQUEST",
		})
	}

	// Validate and sanitize update fields
	if description, ok := updateData["description"].(string); ok {
		updateData["description"] = validation.SanitizeString(description)
		validator := validation.NewValidator()
		validator.ValidateDescription(description, false).
			ValidateUserInput("description", description)

		if validator.HasErrors() {
			return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
				Error:   "Validation Error",
				Message: validator.Error().Error(),
				Code:    "BAD_REQUEST",
			})
		}
	}

	if author, ok := updateData["author"].(string); ok {
		updateData["author"] = validation.SanitizeString(author)
		validator := validation.NewValidator()
		validator.MaxLength("author", author, 100).
			ValidateUserInput("author", author)

		if validator.HasErrors() {
			return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
				Error:   "Validation Error",
				Message: validator.Error().Error(),
				Code:    "BAD_REQUEST",
			})
		}
	}

	if status, ok := updateData["status"].(string); ok {
		updateData["status"] = validation.SanitizeString(status)
		validStatuses := []string{"active", "inactive", "pending", "deprecated"}
		validStatus := false
		for _, vs := range validStatuses {
			if status == vs {
				validStatus = true
				break
			}
		}
		if !validStatus {
			return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
				Error:   "Bad request",
				Message: "Invalid status (must be: active, inactive, pending, or deprecated)",
				Code:    "BAD_REQUEST",
			})
		}
	}

	result, err := h.service.UpdatePlugin(c.Request().Context(), id, updateData)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return c.JSON(http.StatusNotFound, shared_kernel_http.ErrorResponse{
				Error:   "Plugin not found",
				Message: "The requested plugin does not exist",
				Code:    "NOT_FOUND",
			})
		}

		if strings.Contains(err.Error(), "invalid") || strings.Contains(err.Error(), "validation") {
			return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
				Error:   "Validation Error",
				Message: err.Error(),
				Code:    "BAD_REQUEST",
			})
		}

		return c.JSON(http.StatusInternalServerError, shared_kernel_http.ErrorResponse{
			Error:   "Internal Server Error",
			Message: err.Error(),
			Code:    "INTERNAL_SERVER_ERROR",
		})
	}

	return c.JSON(http.StatusOK, result)
}

// RegisterRoutes registra as rotas do handler
func (h *PluginHandler) RegisterRoutes(e *echo.Echo) {
	api := e.Group("/api/v1")

	api.POST("/plugins", h.RegisterPlugin)
	api.GET("/plugins/:id", h.GetPlugin)
	api.GET("/plugins", h.ListPlugins)
	api.PUT("/plugins/:id", h.UpdatePlugin)
	api.DELETE("/plugins/:id", h.UnregisterPlugin)
}
