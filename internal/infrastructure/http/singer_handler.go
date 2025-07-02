package http

import (
	"fmt"
	"net/http"
	"strconv"

	"github.com/flext-sh/flext/internal/bounded_contexts/singer/application/services"
	"github.com/flext-sh/flext/internal/bounded_contexts/singer/domain/entities"
	"github.com/flext-sh/flext/internal/infrastructure/singer"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// SingerHandler manipula requisições HTTP para Singer
type SingerHandler struct {
	service *services.SingerService
	manager *singer.SingerManager
}

// NewSingerHandler cria um novo handler HTTP para Singer
func NewSingerHandler(service *services.SingerService, manager *singer.SingerManager) *SingerHandler {
	return &SingerHandler{
		service: service,
		manager: manager,
	}
}

// CreateSpec manipula POST /api/v1/singer/specs
func (h *SingerHandler) CreateSpec(c echo.Context) error {
	var req services.CreateSpecRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	if err := c.Validate(req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": err.Error(),
		})
	}

	response, err := h.service.CreateSpec(c.Request().Context(), req)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusCreated, response)
}

// GetSpec manipula GET /api/v1/singer/specs/:id
func (h *SingerHandler) GetSpec(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	response, err := h.service.GetSpec(c.Request().Context(), id)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, response)
}

// UpdateSpec manipula PUT /api/v1/singer/specs/:id
func (h *SingerHandler) UpdateSpec(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	var req services.UpdateSpecRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	if err := c.Validate(req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": err.Error(),
		})
	}

	response, err := h.service.UpdateSpec(c.Request().Context(), id, req)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, response)
}

// DeleteSpec manipula DELETE /api/v1/singer/specs/:id
func (h *SingerHandler) DeleteSpec(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	if err := h.service.DeleteSpec(c.Request().Context(), id); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusNoContent, nil)
}

// ListSpecs manipula GET /api/v1/singer/specs
func (h *SingerHandler) ListSpecs(c echo.Context) error {
	req := services.ListSpecsRequest{}

	// Parse query parameters
	if typeStr := c.QueryParam("type"); typeStr != "" {
		singerType := entities.SingerType(typeStr)
		if singerType == entities.SingerTypeTap || singerType == entities.SingerTypeTarget {
			req.Type = &singerType
		}
	}

	if activeStr := c.QueryParam("active"); activeStr != "" {
		if active, err := strconv.ParseBool(activeStr); err == nil {
			req.Active = &active
		}
	}

	req.Query = c.QueryParam("q")

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if limit, err := strconv.Atoi(limitStr); err == nil {
			req.Limit = limit
		}
	}

	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if offset, err := strconv.Atoi(offsetStr); err == nil {
			req.Offset = offset
		}
	}

	response, err := h.service.ListSpecs(c.Request().Context(), req)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, response)
}

// ExecuteSpec manipula POST /api/v1/singer/specs/:id/execute
func (h *SingerHandler) ExecuteSpec(c echo.Context) error {
	idStr := c.Param("id")
	specID, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	var req services.ExecuteSpecRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	req.SpecID = specID

	if err := c.Validate(req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": err.Error(),
		})
	}

	result, err := h.service.ExecuteSpec(c.Request().Context(), req)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusAccepted, result)
}

// GetExecution manipula GET /api/v1/singer/executions/:id
func (h *SingerHandler) GetExecution(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid execution ID",
		})
	}

	response, err := h.service.GetExecution(c.Request().Context(), id)
	if err != nil {
		return c.JSON(http.StatusNotFound, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, response)
}

// ListExecutions manipula GET /api/v1/singer/specs/:id/executions
func (h *SingerHandler) ListExecutions(c echo.Context) error {
	idStr := c.Param("id")
	specID, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	limit := 50 // default
	offset := 0

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if parsedLimit, err := strconv.Atoi(limitStr); err == nil {
			limit = parsedLimit
		}
	}

	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if parsedOffset, err := strconv.Atoi(offsetStr); err == nil {
			offset = parsedOffset
		}
	}

	executions, err := h.service.ListExecutions(c.Request().Context(), specID, limit, offset)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"executions": executions,
		"limit":      limit,
		"offset":     offset,
	})
}

// DiscoverSchema manipula POST /api/v1/singer/specs/:id/discover
func (h *SingerHandler) DiscoverSchema(c echo.Context) error {
	idStr := c.Param("id")
	specID, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	var config map[string]interface{}
	if err := c.Bind(&config); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	catalog, err := h.service.DiscoverSchema(c.Request().Context(), specID, config)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, catalog)
}

// TestConnection manipula POST /api/v1/singer/specs/:id/test
func (h *SingerHandler) TestConnection(c echo.Context) error {
	idStr := c.Param("id")
	specID, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	var config map[string]interface{}
	if err := c.Bind(&config); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	if err := h.service.TestConnection(c.Request().Context(), specID, config); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"status": "Connection test successful",
	})
}

// ActivateSpec manipula POST /api/v1/singer/specs/:id/activate
func (h *SingerHandler) ActivateSpec(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	if err := h.service.ActivateSpec(c.Request().Context(), id); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"status": "Specification activated",
	})
}

// DeactivateSpec manipula POST /api/v1/singer/specs/:id/deactivate
func (h *SingerHandler) DeactivateSpec(c echo.Context) error {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid spec ID",
		})
	}

	if err := h.service.DeactivateSpec(c.Request().Context(), id); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"status": "Specification deactivated",
	})
}

// RegisterRoutes registra as rotas do handler Singer
func (h *SingerHandler) RegisterRoutes(e *echo.Echo) {
	api := e.Group("/api/v1/singer")

	// Especificações
	api.POST("/specs", h.CreateSpec)
	api.GET("/specs/:id", h.GetSpec)
	api.PUT("/specs/:id", h.UpdateSpec)
	api.DELETE("/specs/:id", h.DeleteSpec)
	api.GET("/specs", h.ListSpecs)

	// Execução
	api.POST("/specs/:id/execute", h.ExecuteSpec)
	api.GET("/specs/:id/executions", h.ListExecutions)
	api.GET("/executions/:id", h.GetExecution)

	// Operações especiais
	api.POST("/specs/:id/discover", h.DiscoverSchema)
	api.POST("/specs/:id/test", h.TestConnection)
	api.POST("/specs/:id/activate", h.ActivateSpec)
	api.POST("/specs/:id/deactivate", h.DeactivateSpec)

	// Meltano integration endpoints
	api.POST("/meltano/init", h.InitMeltanoProject)
	api.POST("/meltano/install", h.InstallPlugin)
	api.GET("/meltano/status", h.GetMeltanoStatus)

	// Singer Hub integration
	api.GET("/hub/search", h.SearchHub)
	api.POST("/hub/install", h.InstallFromHub)

	// Enhanced sync operations
	api.POST("/sync", h.ExecuteSync)
	api.GET("/sync/executions", h.ListSyncExecutions)
	api.GET("/sync/executions/:id", h.GetSyncExecution)
	api.POST("/sync/executions/:id/cancel", h.CancelSyncExecution)
}

// Meltano Integration Endpoints

// InitMeltanoProject inicializa um projeto Meltano
func (h *SingerHandler) InitMeltanoProject(c echo.Context) error {
	var request struct {
		ProjectPath string `json:"project_path" validate:"required"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid request body",
		})
	}

	if err := c.Validate(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	err := h.manager.InitializeMeltanoProject(c.Request().Context(), request.ProjectPath)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": "Meltano project initialized successfully",
		"data": map[string]interface{}{
			"project_path": request.ProjectPath,
		},
	})
}

// InstallPlugin instala um plugin via Meltano
func (h *SingerHandler) InstallPlugin(c echo.Context) error {
	var request struct {
		Type   string `json:"type" validate:"required,oneof=extractors loaders"`
		Name   string `json:"name" validate:"required"`
		PipURL string `json:"pip_url,omitempty"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid request body",
		})
	}

	if err := c.Validate(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	err := h.manager.InstallSingerPlugin(c.Request().Context(), request.Type, request.Name, request.PipURL)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": fmt.Sprintf("Plugin %s installed successfully", request.Name),
	})
}

// GetMeltanoStatus retorna o status do Meltano
func (h *SingerHandler) GetMeltanoStatus(c echo.Context) error {
	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	// TODO: Implementar verificação de status real do Meltano
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"meltano_available": true,
			"version":           "unknown",
			"project_path":      "not_initialized",
		},
	})
}

// SearchHub busca especificações no Singer Hub
func (h *SingerHandler) SearchHub(c echo.Context) error {
	category := c.QueryParam("category")

	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	hubSpecs, err := h.manager.DiscoverSingerHub(c.Request().Context(), category)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"plugins": hubSpecs,
			"total":   len(hubSpecs),
		},
	})
}

// InstallFromHub instala uma especificação do Singer Hub
func (h *SingerHandler) InstallFromHub(c echo.Context) error {
	var request struct {
		Name   string `json:"name" validate:"required"`
		Type   string `json:"type" validate:"required,oneof=extractors loaders"`
		PipURL string `json:"pip_url" validate:"required"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid request body",
		})
	}

	if err := c.Validate(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	err := h.manager.InstallSingerPlugin(c.Request().Context(), request.Type, request.Name, request.PipURL)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to install plugin: %s", err.Error()),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": fmt.Sprintf("Plugin %s installed successfully", request.Name),
	})
}

// Enhanced Sync Operations

// ExecuteSync executa uma sincronização Singer (tap + target)
func (h *SingerHandler) ExecuteSync(c echo.Context) error {
	var request struct {
		Tap          string                     `json:"tap" validate:"required"`
		Target       string                     `json:"target" validate:"required"`
		TapConfig    map[string]interface{}     `json:"tap_config" validate:"required"`
		TargetConfig map[string]interface{}     `json:"target_config" validate:"required"`
		Catalog      *entities.Catalog          `json:"catalog,omitempty"`
		State        *entities.State            `json:"state,omitempty"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid request body",
		})
	}

	if err := c.Validate(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	executionID, err := h.manager.ExecuteSync(
		c.Request().Context(),
		request.Tap,
		request.Target,
		request.TapConfig,
		request.TargetConfig,
		request.Catalog,
		request.State,
	)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	return c.JSON(http.StatusAccepted, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"execution_id": executionID,
			"status":       "started",
		},
	})
}

// ListSyncExecutions lista execuções de sincronização
func (h *SingerHandler) ListSyncExecutions(c echo.Context) error {
	// TODO: Implementar listagem completa de execuções de sincronização
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"executions": []interface{}{},
			"total":      0,
		},
	})
}

// GetSyncExecution retorna detalhes de uma execução de sincronização
func (h *SingerHandler) GetSyncExecution(c echo.Context) error {
	executionIDStr := c.Param("id")
	
	executionID, err := uuid.Parse(executionIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid execution ID format",
		})
	}

	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	status, exists := h.manager.GetExecutionStatus(executionID)
	if !exists {
		return c.JSON(http.StatusNotFound, map[string]interface{}{
			"success": false,
			"error":   "Execution not found",
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    status,
	})
}

// CancelSyncExecution cancela uma execução de sincronização
func (h *SingerHandler) CancelSyncExecution(c echo.Context) error {
	executionIDStr := c.Param("id")
	
	executionID, err := uuid.Parse(executionIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid execution ID format",
		})
	}

	if h.manager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Singer manager not available",
		})
	}

	if err := h.manager.CancelExecution(executionID); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": "Execution cancelled successfully",
	})
}
