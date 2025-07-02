package http

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/commands"
	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/queries"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	shared_kernel_http "github.com/flext-sh/flext/internal/shared_kernel/infrastructure/http"
	"github.com/flext-sh/flext/internal/shared_kernel/infrastructure/validation"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/samber/lo"
)

// PipelineHandler manipula requisições HTTP para pipelines
type PipelineHandler struct {
	*shared_kernel_http.BaseHandler
	service *application.PipelineService
}

// NewPipelineHandler cria um novo handler HTTP
func NewPipelineHandler(service *application.PipelineService, logger logging.Logger) *PipelineHandler {
	return &PipelineHandler{
		BaseHandler: shared_kernel_http.NewBaseHandler("PipelineHandler", logger),
		service:     service,
	}
}

// parseUUID parses and validates a UUID from a path parameter
func (h *PipelineHandler) parseUUID(c echo.Context, param string) (uuid.UUID, error) {
	idStr := c.Param(param)
	if idStr == "" {
		return uuid.Nil, fmt.Errorf("parameter %s is required", param)
	}

	id, err := uuid.Parse(idStr)
	if err != nil {
		return uuid.Nil, fmt.Errorf("invalid UUID format for parameter %s", param)
	}

	return id, nil
}

// sanitizeStringArray limpa um array de strings
func (h *PipelineHandler) sanitizeStringArray(arr []string) []string {
	return lo.FilterMap(arr, func(s string, _ int) (string, bool) {
		clean := strings.TrimSpace(s)
		return clean, clean != ""
	})
}

// CreatePipeline manipula POST /api/v1/pipelines
func (h *PipelineHandler) CreatePipeline(c echo.Context) error {
	var cmd commands.CreatePipelineCommand
	if err := c.Bind(&cmd); err != nil {
		return h.HandleError(c, fmt.Errorf("invalid request body format: %w", err))
	}

	// Sanitizar entrada
	cmd.Name = strings.TrimSpace(cmd.Name)
	cmd.Description = strings.TrimSpace(cmd.Description)
	cmd.Tags = h.sanitizeStringArray(cmd.Tags)

	// Validar usando shared kernel validator
	validator := validation.NewValidator()
	if err := validator.ValidateStruct(cmd); err != nil {
		return h.HandleError(c, err)
	}

	// Executar comando
	result, err := h.service.CreatePipeline(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleCreated(c, result)
}

// GetPipeline manipula GET /api/v1/pipelines/:id
func (h *PipelineHandler) GetPipeline(c echo.Context) error {
	id, err := h.parseUUID(c, "id")
	if err != nil {
		return h.HandleError(c, err)
	}

	query := queries.GetPipelineQuery{PipelineID: id}
	result, err := h.service.GetPipeline(c.Request().Context(), query)
	if err != nil {
		return h.HandleError(c, err)
	}

	if result == nil {
		return h.HandleError(c, fmt.Errorf("pipeline not found"))
	}

	return h.HandleSuccess(c, result)
}

// ListPipelines manipula GET /api/v1/pipelines
func (h *PipelineHandler) ListPipelines(c echo.Context) error {
	// Usar shared kernel para parsing de parâmetros de paginação
	pagination := h.ParsePagination(c)

	// Criar query com os campos corretos
	query := queries.ListPipelinesQuery{
		Limit:  pagination.PageSize,
		Offset: pagination.Offset(),
	}

	// Parse filtros específicos
	if activeStr := c.QueryParam("active"); activeStr != "" {
		if active, err := strconv.ParseBool(activeStr); err == nil {
			query.Active = &active
		}
	}

	// Parse tags
	if tagsStr := c.QueryParam("tags"); tagsStr != "" {
		tags := strings.Split(tagsStr, ",")
		query.Tags = h.sanitizeStringArray(tags)
	}

	// Executar query
	result, err := h.service.ListPipelines(c.Request().Context(), query)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleSuccess(c, result)
}

// UpdatePipeline manipula PUT /api/v1/pipelines/:id
func (h *PipelineHandler) UpdatePipeline(c echo.Context) error {
	id, err := h.parseUUID(c, "id")
	if err != nil {
		return h.HandleError(c, err)
	}

	var cmd commands.UpdatePipelineCommand
	if err := c.Bind(&cmd); err != nil {
		return h.HandleError(c, fmt.Errorf("invalid request body format: %w", err))
	}

	cmd.PipelineID = id

	// Sanitizar entrada
	if cmd.Name != nil {
		sanitized := strings.TrimSpace(*cmd.Name)
		cmd.Name = &sanitized
	}
	if cmd.Description != nil {
		sanitized := strings.TrimSpace(*cmd.Description)
		cmd.Description = &sanitized
	}

	// Validar usando shared kernel validator
	validator := validation.NewValidator()
	if err := validator.ValidateStruct(cmd); err != nil {
		return h.HandleError(c, err)
	}

	// Executar comando
	result, err := h.service.UpdatePipeline(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleError(c, err)
	}

	return h.HandleSuccess(c, result)
}

// AddStep manipula POST /api/v1/pipelines/:id/steps
func (h *PipelineHandler) AddStep(c echo.Context) error {
	pipelineID, err := h.parseUUID(c, "id")
	if err != nil {
		return h.HandleError(c, fmt.Errorf("invalid pipeline ID format: %w", err))
	}

	var cmd commands.AddStepCommand
	if err := c.Bind(&cmd); err != nil {
		return h.HandleError(c, fmt.Errorf("invalid request body format: %w", err))
	}

	cmd.PipelineID = pipelineID

	// Sanitizar dados do step
	cmd.Name = strings.TrimSpace(cmd.Name)

	// Validar usando shared kernel validator
	validator := validation.NewValidator()
	if err := validator.ValidateStruct(cmd); err != nil {
		return h.HandleError(c, err)
	}

	// Executar comando
	result, err := h.service.AddStep(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleServiceError(c, err, "add step")
	}

	return h.HandleCreated(c, result)
}

// ExecutePipeline manipula POST /api/v1/pipelines/:id/execute
func (h *PipelineHandler) ExecutePipeline(c echo.Context) error {
	pipelineID, err := h.parseUUID(c, "id")
	if err != nil {
		return h.HandleError(c, fmt.Errorf("invalid pipeline ID format: %w", err))
	}

	var cmd commands.ExecutePipelineCommand
	if err := c.Bind(&cmd); err != nil {
		return h.HandleError(c, fmt.Errorf("invalid request body format: %w", err))
	}

	cmd.PipelineID = pipelineID

	// Validar comando
	validator := validation.NewValidator()
	if err := validator.ValidateStruct(cmd); err != nil {
		return h.HandleError(c, err)
	}

	// Executar comando
	result, err := h.service.ExecutePipeline(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleServiceError(c, err, "execute pipeline")
	}

	return c.JSON(http.StatusAccepted, shared_kernel_http.SuccessResponse{
		Data:      result,
		Success:   true,
		Timestamp: time.Now().UTC(),
		RequestID: h.getRequestID(c),
	})
}

// HandleServiceError especializa o tratamento de erros de serviço
func (h *PipelineHandler) HandleServiceError(c echo.Context, err error, operation string) error {
	// Usar mapeamento de erros do BaseHandler
	errorType := h.DetermineErrorType(err)

	switch errorType {
	case "not_found":
		return h.HandleError(c, fmt.Errorf("pipeline not found"))
	case "already_exists":
		return h.HandleError(c, fmt.Errorf("pipeline with this name already exists"))
	case "validation":
		return h.HandleError(c, err)
	case "invalid":
		return h.HandleError(c, fmt.Errorf("invalid request: %w", err))
	case "busy":
		return h.HandleError(c, fmt.Errorf("pipeline is currently busy"))
	default:
		return h.HandleError(c, fmt.Errorf("failed to %s: %w", operation, err))
	}
}

// DetermineErrorType determines error type from error message
func (h *PipelineHandler) DetermineErrorType(err error) string {
	errMsg := strings.ToLower(err.Error())
	switch {
	case strings.Contains(errMsg, "not found"):
		return "not_found"
	case strings.Contains(errMsg, "already exists"):
		return "already_exists"
	case strings.Contains(errMsg, "validation"):
		return "validation"
	case strings.Contains(errMsg, "invalid"):
		return "invalid"
	case strings.Contains(errMsg, "busy"):
		return "busy"
	default:
		return "internal"
	}
}

// getRequestID extracts request ID from context
func (h *PipelineHandler) getRequestID(c echo.Context) string {
	return c.Response().Header().Get(echo.HeaderXRequestID)
}

// GetPipelineStatus manipula GET /api/v1/pipelines/:id/status
func (h *PipelineHandler) GetPipelineStatus(c echo.Context) error {
	id, err := h.parseUUID(c, "id")
	if err != nil {
		return h.HandleError(c, err)
	}

	cmd := commands.GetPipelineStatusCommand{PipelineID: id}
	result, err := h.service.GetPipelineStatus(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleServiceError(c, err, "get pipeline status")
	}

	return h.HandleSuccess(c, result)
}

// PausePipeline manipula POST /api/v1/pipelines/:id/pause
func (h *PipelineHandler) PausePipeline(c echo.Context) error {
	id, err := h.parseUUID(c, "id")
	if err != nil {
		return h.HandleError(c, err)
	}

	var cmd commands.PausePipelineCommand
	if err := c.Bind(&cmd); err != nil {
		return h.HandleError(c, fmt.Errorf("invalid request body format: %w", err))
	}

	cmd.PipelineID = id

	// Sanitizar entrada
	cmd.Reason = strings.TrimSpace(cmd.Reason)
	cmd.PausedBy = strings.TrimSpace(cmd.PausedBy)

	// Validar comando
	validator := validation.NewValidator()
	if err := validator.ValidateStruct(cmd); err != nil {
		return h.HandleError(c, err)
	}

	// Executar comando
	result, err := h.service.PausePipeline(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleServiceError(c, err, "pause pipeline")
	}

	return h.HandleSuccess(c, result)
}

// ResumePipeline manipula POST /api/v1/pipelines/:id/resume
func (h *PipelineHandler) ResumePipeline(c echo.Context) error {
	id, err := h.parseUUID(c, "id")
	if err != nil {
		return h.HandleError(c, err)
	}

	var cmd commands.ResumePipelineCommand
	if err := c.Bind(&cmd); err != nil {
		return h.HandleError(c, fmt.Errorf("invalid request body format: %w", err))
	}

	cmd.PipelineID = id

	// Sanitizar entrada
	cmd.ResumedBy = strings.TrimSpace(cmd.ResumedBy)

	// Validar comando
	validator := validation.NewValidator()
	if err := validator.ValidateStruct(cmd); err != nil {
		return h.HandleError(c, err)
	}

	// Executar comando
	result, err := h.service.ResumePipeline(c.Request().Context(), cmd)
	if err != nil {
		return h.HandleServiceError(c, err, "resume pipeline")
	}

	return h.HandleSuccess(c, result)
}

// HealthCheck endpoint for service health verification
func (h *PipelineHandler) HealthCheck(c echo.Context) error {
	healthStatus := map[string]interface{}{
		"status":    "healthy",
		"service":   "flext-pipeline-service",
		"version":   "2.0.0",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
		"checks": map[string]interface{}{
			"pipeline_service": "ok",
			"database":         "ok",
			"memory":           "ok",
		},
	}

	return h.HandleSuccess(c, healthStatus)
}

// RegisterRoutes registra as rotas do handler
func (h *PipelineHandler) RegisterRoutes(e *echo.Echo) {
	api := e.Group("/api/v1")

	// Health check endpoint
	api.GET("/health", h.HealthCheck)

	// Pipeline routes
	api.POST("/pipelines", h.CreatePipeline)
	api.GET("/pipelines/:id", h.GetPipeline)
	api.GET("/pipelines", h.ListPipelines)
	api.PUT("/pipelines/:id", h.UpdatePipeline)
	api.POST("/pipelines/:id/steps", h.AddStep)
	api.POST("/pipelines/:id/execute", h.ExecutePipeline)
	
	// Pipeline status management routes
	api.GET("/pipelines/:id/status", h.GetPipelineStatus)
	api.POST("/pipelines/:id/pause", h.PausePipeline)
	api.POST("/pipelines/:id/resume", h.ResumePipeline)
}