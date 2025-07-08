package http

import (
	"net/http"
	"strconv"

	pluginUC "github.com/flext-sh/flext/internal/usecases/plugin"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

// CleanPluginHandler handles HTTP requests for plugins using Clean Architecture
type CleanPluginHandler struct {
	registerPluginUC *pluginUC.RegisterPluginUseCase
	getPluginUC      *pluginUC.GetPluginUseCase
	listPluginsUC    *pluginUC.ListPluginsUseCase
	deletePluginUC   *pluginUC.DeletePluginUseCase
}

// NewCleanPluginHandler creates a new Clean Architecture plugin handler
func NewCleanPluginHandler(
	registerPluginUC *pluginUC.RegisterPluginUseCase,
	getPluginUC *pluginUC.GetPluginUseCase,
	listPluginsUC *pluginUC.ListPluginsUseCase,
	deletePluginUC *pluginUC.DeletePluginUseCase,
) *CleanPluginHandler {
	return &CleanPluginHandler{
		registerPluginUC: registerPluginUC,
		getPluginUC:      getPluginUC,
		listPluginsUC:    listPluginsUC,
		deletePluginUC:   deletePluginUC,
	}
}

// RegisterPlugin handles plugin registration
func (h *CleanPluginHandler) RegisterPlugin(c echo.Context) error {
	var input pluginUC.RegisterPluginInput
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid input format",
		})
	}

	result, err := h.registerPluginUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, pluginUC.ErrPluginAlreadyExists) {
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

// GetPlugin handles getting a specific plugin
func (h *CleanPluginHandler) GetPlugin(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid plugin ID format",
		})
	}

	input := pluginUC.GetPluginInput{ID: id}
	result, err := h.getPluginUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, pluginUC.ErrPluginNotFound) {
			return c.JSON(http.StatusNotFound, map[string]string{
				"error": "Plugin not found",
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// ListPlugins handles listing plugins with pagination
func (h *CleanPluginHandler) ListPlugins(c echo.Context) error {
	page := 1
	limit := 10

	if pageStr := c.QueryParam("page"); pageStr != "" {
		if p, err := strconv.Atoi(pageStr); err == nil && p > 0 {
			page = p
		}
	}

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 && l <= 100 {
			limit = l
		}
	}

	// Helper function to convert string to pointer
	stringPtr := func(s string) *string {
		if s == "" {
			return nil
		}
		return &s
	}

	input := pluginUC.ListPluginsInput{
		Limit:  limit,
		Offset: (page - 1) * limit, // Convert page to offset
		Type:   stringPtr(c.QueryParam("type")),
		Status: stringPtr(c.QueryParam("status")),
	}

	result, err := h.listPluginsUC.Execute(c.Request().Context(), input)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// DeletePlugin handles plugin deletion
func (h *CleanPluginHandler) DeletePlugin(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid plugin ID format",
		})
	}

	input := pluginUC.DeletePluginInput{ID: id}
	err = h.deletePluginUC.Execute(c.Request().Context(), input)
	if err != nil {
		if errors.Is(err, pluginUC.ErrPluginNotFound) {
			return c.JSON(http.StatusNotFound, map[string]string{
				"error": "Plugin not found",
			})
		}
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.NoContent(http.StatusNoContent)
}
