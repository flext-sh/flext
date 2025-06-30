package http

import (
	"net/http"
	"strconv"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/queries"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// PipelineHandler manipula requisições HTTP para pipelines
type PipelineHandler struct {
	service *application.PipelineService
}

// NewPipelineHandler cria um novo handler HTTP
func NewPipelineHandler(service *application.PipelineService) *PipelineHandler {
	return &PipelineHandler{
		service: service,
	}
}

// CreatePipeline manipula POST /api/v1/pipelines
func (h *PipelineHandler) CreatePipeline(c echo.Context) error {
	var cmd commands.CreatePipelineCommand
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

	result, err := h.service.CreatePipeline(c.Request().Context(), cmd)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusCreated, result)
}

// GetPipeline manipula GET /api/v1/pipelines/:id
func (h *PipelineHandler) GetPipeline(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid pipeline ID",
		})
	}

	query := queries.GetPipelineQuery{ID: id}
	result, err := h.service.GetPipeline(c.Request().Context(), query)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// ListPipelines manipula GET /api/v1/pipelines
func (h *PipelineHandler) ListPipelines(c echo.Context) error {
	query := queries.ListPipelinesQuery{}

	// Parse query parameters
	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if limit, err := strconv.Atoi(limitStr); err == nil {
			query.Limit = limit
		}
	}

	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if offset, err := strconv.Atoi(offsetStr); err == nil {
			query.Offset = offset
		}
	}

	if activeStr := c.QueryParam("active"); activeStr != "" {
		if active, err := strconv.ParseBool(activeStr); err == nil {
			query.Active = &active
		}
	}

	// Parse tags as comma-separated values
	if tagsStr := c.QueryParam("tags"); tagsStr != "" {
		// Simple comma split for now
		query.Tags = []string{tagsStr}
	}

	result, err := h.service.ListPipelines(c.Request().Context(), query)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// AddStep manipula POST /api/v1/pipelines/:id/steps
func (h *PipelineHandler) AddStep(c echo.Context) error {
	idStr := c.Param("id")
	pipelineID, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid pipeline ID",
		})
	}

	var cmd commands.AddStepCommand
	if err := c.Bind(&cmd); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	cmd.PipelineID = pipelineID

	if err := c.Validate(cmd); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": err.Error(),
		})
	}

	result, err := h.service.AddStep(c.Request().Context(), cmd)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusCreated, result)
}

// RegisterRoutes registra as rotas do handler
func (h *PipelineHandler) RegisterRoutes(e *echo.Echo) {
	api := e.Group("/api/v1")
	
	api.POST("/pipelines", h.CreatePipeline)
	api.GET("/pipelines/:id", h.GetPipeline)
	api.GET("/pipelines", h.ListPipelines)
	api.POST("/pipelines/:id/steps", h.AddStep)
}