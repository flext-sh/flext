package http

import (
	"net/http"
	"strconv"

	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application"
	"github.com/flext-sh/flext/internal/bounded_contexts/plugin/application/commands"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// PluginHandler manipula requisições HTTP para plugins
type PluginHandler struct {
	service *application.PluginService
}

// NewPluginHandler cria um novo handler HTTP
func NewPluginHandler(service *application.PluginService) *PluginHandler {
	return &PluginHandler{
		service: service,
	}
}

// RegisterPlugin manipula POST /api/v1/plugins
func (h *PluginHandler) RegisterPlugin(c echo.Context) error {
	var cmd commands.RegisterPluginCommand
	if err := c.Bind(&cmd); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	if err := c.Validate(cmd); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": err.Error(),
		})
	}

	result, err := h.service.RegisterPlugin(c.Request().Context(), cmd)
	if err != nil {
		// Handle specific errors
		if _, ok := err.(commands.PluginAlreadyExistsError); ok {
			return c.JSON(http.StatusConflict, map[string]string{
				"error": err.Error(),
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusCreated, result)
}

// GetPlugin manipula GET /api/v1/plugins/:id
func (h *PluginHandler) GetPlugin(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid plugin ID",
		})
	}

	// Create plugin query (will need to implement this)
	result, err := h.service.GetPlugin(c.Request().Context(), id)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// ListPlugins manipula GET /api/v1/plugins
func (h *PluginHandler) ListPlugins(c echo.Context) error {
	// Parse query parameters
	limit := 50
	offset := 0

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil {
			limit = l
		}
	}

	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if o, err := strconv.Atoi(offsetStr); err == nil {
			offset = o
		}
	}

	pluginType := c.QueryParam("type")
	status := c.QueryParam("status")
	author := c.QueryParam("author")

	result, err := h.service.ListPlugins(c.Request().Context(), limit, offset, pluginType, status, author)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
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
}