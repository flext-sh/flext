package http

import (
	"net/http"
	"strconv"
	"strings"

	pipelineUC "github.com/flext-sh/flext/pkg/application/pipeline"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/pkg/errors"
)

// CleanPipelineHandler handles HTTP requests for pipelines using Clean Architecture
type CleanPipelineHandler struct {
	createPipelineUC  *pipelineUC.CreatePipelineUseCase
	executePipelineUC *pipelineUC.ExecutePipelineUseCase
	getPipelineUC     *pipelineUC.GetPipelineUseCase
	listPipelinesUC   *pipelineUC.ListPipelinesUseCase
	deletePipelineUC  *pipelineUC.DeletePipelineUseCase
}

// NewCleanPipelineHandler creates a new Clean Architecture pipeline handler
func NewCleanPipelineHandler(
	createPipelineUC *pipelineUC.CreatePipelineUseCase,
	executePipelineUC *pipelineUC.ExecutePipelineUseCase,
	getPipelineUC *pipelineUC.GetPipelineUseCase,
	listPipelinesUC *pipelineUC.ListPipelinesUseCase,
	deletePipelineUC *pipelineUC.DeletePipelineUseCase,
) *CleanPipelineHandler {
	return &CleanPipelineHandler{
		createPipelineUC:  createPipelineUC,
		executePipelineUC: executePipelineUC,
		getPipelineUC:     getPipelineUC,
		listPipelinesUC:   listPipelinesUC,
		deletePipelineUC:  deletePipelineUC,
	}
}

// CreatePipeline handles POST /api/v1/clean/pipelines
func (h *CleanPipelineHandler) CreatePipeline(c echo.Context) error {
	var input pipelineUC.CreatePipelineInput
	if err := c.Bind(&input); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "Invalid request body format",
			Code:    http.StatusBadRequest,
		})
	}

	result, err := h.createPipelineUC.Execute(c.Request().Context(), input)
	if err != nil {
		return handleCleanServiceError(c, err, "create pipeline")
	}

	return c.JSON(http.StatusCreated, result)
}

// GetPipeline handles GET /api/v1/clean/pipelines/:id
func (h *CleanPipelineHandler) GetPipeline(c echo.Context) error {
	id, err := parseUUID(c.Param("id"))
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "Invalid pipeline ID format",
			Code:    http.StatusBadRequest,
		})
	}

	input := pipelineUC.GetPipelineInput{ID: id}
	result, err := h.getPipelineUC.Execute(c.Request().Context(), input)
	if err != nil {
		return handleCleanServiceError(c, err, "get pipeline")
	}

	return c.JSON(http.StatusOK, result)
}

// ListPipelines handles GET /api/v1/clean/pipelines
func (h *CleanPipelineHandler) ListPipelines(c echo.Context) error {
	input := pipelineUC.ListPipelinesInput{
		Limit:  10, // Default
		Offset: 0,  // Default
	}

	// Parse query parameters
	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if limit, err := strconv.Atoi(limitStr); err == nil && limit > 0 && limit <= 1000 {
			input.Limit = limit
		} else {
			return c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "Bad Request",
				Message: "Invalid limit parameter (must be between 1 and 1000)",
				Code:    http.StatusBadRequest,
			})
		}
	}

	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if offset, err := strconv.Atoi(offsetStr); err == nil && offset >= 0 {
			input.Offset = offset
		} else {
			return c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "Bad Request",
				Message: "Invalid offset parameter (must be >= 0)",
				Code:    http.StatusBadRequest,
			})
		}
	}

	if activeStr := c.QueryParam("active"); activeStr != "" {
		if active, err := strconv.ParseBool(activeStr); err == nil {
			input.Active = &active
		} else {
			return c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "Bad Request",
				Message: "Invalid active parameter (must be true or false)",
				Code:    http.StatusBadRequest,
			})
		}
	}

	if tagsStr := c.QueryParam("tags"); tagsStr != "" {
		tags := strings.Split(tagsStr, ",")
		// Clean and filter empty tags
		var cleanTags []string
		for _, tag := range tags {
			if trimmed := strings.TrimSpace(tag); trimmed != "" {
				cleanTags = append(cleanTags, trimmed)
			}
		}
		input.Tags = cleanTags
	}

	if orderBy := c.QueryParam("order_by"); orderBy != "" {
		input.OrderBy = orderBy
	}

	if orderDir := c.QueryParam("order_dir"); orderDir != "" {
		if orderDir == "ASC" || orderDir == "DESC" {
			input.OrderDir = orderDir
		} else {
			return c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "Bad Request",
				Message: "Invalid order_dir parameter (must be ASC or DESC)",
				Code:    http.StatusBadRequest,
			})
		}
	}

	result, err := h.listPipelinesUC.Execute(c.Request().Context(), input)
	if err != nil {
		return handleCleanServiceError(c, err, "list pipelines")
	}

	return c.JSON(http.StatusOK, result)
}

// ExecutePipeline handles POST /api/v1/clean/pipelines/:id/execute
func (h *CleanPipelineHandler) ExecutePipeline(c echo.Context) error {
	id, err := parseUUID(c.Param("id"))
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "Invalid pipeline ID format",
			Code:    http.StatusBadRequest,
		})
	}

	var executionRequest struct {
		Environment  string                 `json:"environment,omitempty"`
		DryRun       bool                   `json:"dry_run,omitempty"`
		Variables    map[string]interface{} `json:"variables,omitempty"`
		StepOverride []string               `json:"step_override,omitempty"`
	}

	if err := c.Bind(&executionRequest); err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "Invalid request body format",
			Code:    http.StatusBadRequest,
		})
	}

	input := pipelineUC.ExecutePipelineInput{
		PipelineID: id,
		Context:    executionRequest.Variables,
	}

	result, err := h.executePipelineUC.Execute(c.Request().Context(), input)
	if err != nil {
		return handleCleanServiceError(c, err, "execute pipeline")
	}

	return c.JSON(http.StatusAccepted, result)
}

// DeletePipeline handles DELETE /api/v1/clean/pipelines/:id
func (h *CleanPipelineHandler) DeletePipeline(c echo.Context) error {
	id, err := parseUUID(c.Param("id"))
	if err != nil {
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "Invalid pipeline ID format",
			Code:    http.StatusBadRequest,
		})
	}

	input := pipelineUC.DeletePipelineInput{ID: id}
	err = h.deletePipelineUC.Execute(c.Request().Context(), input)
	if err != nil {
		return handleCleanServiceError(c, err, "delete pipeline")
	}

	return c.NoContent(http.StatusNoContent)
}

// RegisterRoutes registers the Clean Architecture routes
func (h *CleanPipelineHandler) RegisterRoutes(e *echo.Echo) {
	cleanAPI := e.Group("/api/v1/clean")

	cleanAPI.POST("/pipelines", h.CreatePipeline)
	cleanAPI.GET("/pipelines/:id", h.GetPipeline)
	cleanAPI.GET("/pipelines", h.ListPipelines)
	cleanAPI.POST("/pipelines/:id/execute", h.ExecutePipeline)
	cleanAPI.DELETE("/pipelines/:id", h.DeletePipeline)
}

// handleCleanServiceError handles errors from Clean Architecture use cases
func handleCleanServiceError(c echo.Context, err error, operation string) error {
	// Wrap error with context
	_ = errors.Wrapf(err, "failed to %s", operation) // Suppress unused variable warning

	// Map common errors to HTTP status codes
	errorMessage := strings.ToLower(err.Error())

	switch {
	case strings.Contains(errorMessage, "not found"):
		return c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "Not Found",
			Message: "The requested resource does not exist",
			Code:    http.StatusNotFound,
		})
	case strings.Contains(errorMessage, "already exists"):
		return c.JSON(http.StatusConflict, ErrorResponse{
			Error:   "Conflict",
			Message: "Resource already exists",
			Code:    http.StatusConflict,
		})
	case strings.Contains(errorMessage, "validation") || strings.Contains(errorMessage, "invalid"):
		return c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: err.Error(),
			Code:    http.StatusBadRequest,
		})
	case strings.Contains(errorMessage, "running") || strings.Contains(errorMessage, "busy"):
		return c.JSON(http.StatusConflict, ErrorResponse{
			Error:   "Conflict",
			Message: "Resource is currently busy or running",
			Code:    http.StatusConflict,
		})
	case strings.Contains(errorMessage, "permission") || strings.Contains(errorMessage, "unauthorized"):
		return c.JSON(http.StatusForbidden, ErrorResponse{
			Error:   "Forbidden",
			Message: "Insufficient permissions",
			Code:    http.StatusForbidden,
		})
	default:
		return c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "Internal Server Error",
			Message: "An unexpected error occurred",
			Code:    http.StatusInternalServerError,
		})
	}
}

// parseUUID helper function
func parseUUID(idStr string) (uuid.UUID, error) {
	if strings.TrimSpace(idStr) == "" {
		return uuid.Nil, errors.New("ID parameter is required")
	}

	id, err := uuid.Parse(idStr)
	if err != nil {
		return uuid.Nil, errors.Wrap(err, "invalid UUID format")
	}

	return id, nil
}
