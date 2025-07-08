package http

import (
	"fmt"
	"net/http"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/meltano/application/services"
	"github.com/flext-sh/flext/internal/infrastructure/http/middleware"
	"github.com/labstack/echo/v4"
)

// MeltanoHandler handles HTTP requests for Meltano operations
type MeltanoHandler struct {
	meltanoService *services.MeltanoService
}

// NewMeltanoHandler creates a new Meltano handler
func NewMeltanoHandler(meltanoService *services.MeltanoService) *MeltanoHandler {
	return &MeltanoHandler{
		meltanoService: meltanoService,
	}
}

// RegisterRoutes registers Meltano routes
func (h *MeltanoHandler) RegisterRoutes(e *echo.Echo) {
	meltano := e.Group("/api/v1/meltano")
	meltano.Use(middleware.ErrorHandler())

	// Project management
	meltano.POST("/projects", h.InitProject)
	meltano.GET("/projects", h.ListProjects)
	meltano.GET("/projects/:name", h.GetProjectInfo)

	// Plugin management
	meltano.POST("/projects/:name/plugins", h.AddPlugin)
	meltano.GET("/projects/:name/plugins", h.GetPlugins)
	meltano.POST("/projects/:name/plugins/install", h.InstallPlugins)

	// Pipeline operations
	meltano.POST("/projects/:name/run", h.RunPipeline)
	meltano.POST("/projects/:name/command", h.ExecuteCommand)

	// Adapter management
	meltano.POST("/projects/:name/adapters", h.CreateAdapter)

	// Health check and monitoring
	meltano.GET("/health", h.Health)
	meltano.GET("/stats", h.GetProcessPoolStats)

	// State management
	meltano.GET("/state/stats", h.GetStateStats)
	meltano.GET("/projects/:name/executions", h.ListExecutions)
	meltano.GET("/projects/:name/executions/:id", h.GetExecution)
	meltano.POST("/projects/:name/plugins/:plugin/state", h.SavePluginState)
	meltano.GET("/projects/:name/plugins/:plugin/state", h.LoadPluginState)
	meltano.DELETE("/projects/:name/plugins/:plugin/state", h.DeletePluginState)
}

// InitProjectRequest represents a project initialization request
type InitProjectRequest struct {
	Name      string `json:"name" validate:"required"`
	Directory string `json:"directory,omitempty"`
	Template  string `json:"template,omitempty"`
}

// Request types are shared between handlers

// CreateAdapterRequest represents an adapter creation request
type CreateAdapterRequest struct {
	Type   string                 `json:"type" validate:"required"` // "tap" or "target"
	Name   string                 `json:"name" validate:"required"`
	Config map[string]interface{} `json:"config,omitempty"`
}

// InitProject initializes a new Meltano project
func (h *MeltanoHandler) InitProject(c echo.Context) error {
	var req InitProjectRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request format")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	result, err := h.meltanoService.InitProject(c.Request().Context(), req.Name, req.Directory)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to initialize project: %v", err))
	}

	if !result.Success {
		return echo.NewHTTPError(http.StatusBadRequest, result.Error)
	}

	return c.JSON(http.StatusCreated, result)
}

// ListProjects lists available Meltano projects
func (h *MeltanoHandler) ListProjects(c echo.Context) error {
	rootDir := c.QueryParam("root_dir")
	if rootDir == "" {
		rootDir = "."
	}

	projects, err := h.meltanoService.ListProjects(c.Request().Context(), rootDir)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to list projects: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"projects": projects,
		"count":    len(projects),
	})
}

// GetProjectInfo gets information about a specific project
func (h *MeltanoHandler) GetProjectInfo(c echo.Context) error {
	result, err := h.meltanoService.GetProjectInfo(c.Request().Context())
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to get project info: %v", err))
	}

	if !result.Success {
		return echo.NewHTTPError(http.StatusNotFound, result.Error)
	}

	return c.JSON(http.StatusOK, result)
}

// AddPlugin adds a plugin to the project
func (h *MeltanoHandler) AddPlugin(c echo.Context) error {
	var req AddPluginRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request format")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	result, err := h.meltanoService.AddPlugin(c.Request().Context(), req.PluginType, req.Name, req.Variant)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to add plugin: %v", err))
	}

	if !result.Success {
		return echo.NewHTTPError(http.StatusBadRequest, result.Error)
	}

	return c.JSON(http.StatusCreated, result)
}

// GetPlugins gets all plugins in the project
func (h *MeltanoHandler) GetPlugins(c echo.Context) error {
	result, err := h.meltanoService.GetPlugins(c.Request().Context())
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to get plugins: %v", err))
	}

	if !result.Success {
		return echo.NewHTTPError(http.StatusInternalServerError, result.Error)
	}

	return c.JSON(http.StatusOK, result)
}

// InstallPlugins installs all plugins in the project
func (h *MeltanoHandler) InstallPlugins(c echo.Context) error {
	result, err := h.meltanoService.InstallPlugins(c.Request().Context())
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to install plugins: %v", err))
	}

	if !result.Success {
		return echo.NewHTTPError(http.StatusBadRequest, result.Error)
	}

	return c.JSON(http.StatusOK, result)
}

// RunPipeline runs a Meltano pipeline
func (h *MeltanoHandler) RunPipeline(c echo.Context) error {
	var req RunPipelineRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request format")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	result, err := h.meltanoService.RunPipeline(c.Request().Context(),
		req.Extractor, req.Loader, req.Transformer)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to run pipeline: %v", err))
	}

	status := http.StatusOK
	if !result.Success {
		status = http.StatusBadRequest
	}

	return c.JSON(status, result)
}

// ExecuteCommand executes a raw Meltano command
func (h *MeltanoHandler) ExecuteCommand(c echo.Context) error {
	var req ExecuteCommandRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request format")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), req.Command, req.Args)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to execute command: %v", err))
	}

	status := http.StatusOK
	if !result.Success {
		status = http.StatusBadRequest
	}

	return c.JSON(status, result)
}

// CreateAdapter creates a Meltano adapter
func (h *MeltanoHandler) CreateAdapter(c echo.Context) error {
	var req CreateAdapterRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request format")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	// Validate adapter type
	if req.Type != "tap" && req.Type != "target" {
		return echo.NewHTTPError(http.StatusBadRequest, "Adapter type must be 'tap' or 'target'")
	}

	// Ensure config contains the adapter name
	if req.Config == nil {
		req.Config = make(map[string]interface{})
	}
	req.Config["name"] = req.Name

	result, err := h.meltanoService.CreateAdapter(c.Request().Context(), req.Type, req.Config)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to create adapter: %v", err))
	}

	if !result.Success {
		return echo.NewHTTPError(http.StatusBadRequest, result.Error)
	}

	return c.JSON(http.StatusCreated, result)
}

// Health checks the health of the Meltano service
func (h *MeltanoHandler) Health(c echo.Context) error {
	available, err := h.meltanoService.IsAvailable(c.Request().Context())
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"status":    "unhealthy",
			"available": false,
			"error":     err.Error(),
		})
	}

	status := "healthy"
	httpStatus := http.StatusOK

	if !available {
		status = "unhealthy"
		httpStatus = http.StatusServiceUnavailable
	}

	return c.JSON(httpStatus, map[string]interface{}{
		"status":    status,
		"available": available,
		"service":   "meltano",
	})
}

// GetProcessPoolStats returns statistics about the Meltano process pool
func (h *MeltanoHandler) GetProcessPoolStats(c echo.Context) error {
	stats := h.meltanoService.GetProcessPoolStats()

	return c.JSON(http.StatusOK, map[string]interface{}{
		"service":      "meltano",
		"process_pool": stats,
		"timestamp":    fmt.Sprintf("%d", time.Now().Unix()),
	})
}

// State Management Handlers

// GetStateStats returns statistics about state management
func (h *MeltanoHandler) GetStateStats(c echo.Context) error {
	stats, err := h.meltanoService.GetStateStats(c.Request().Context())
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to get state stats: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"service":   "meltano",
		"state":     stats,
		"timestamp": time.Now().Unix(),
	})
}

// ListExecutions lists recent executions for a project
func (h *MeltanoHandler) ListExecutions(c echo.Context) error {
	projectName := c.Param("name")
	limit := 50 // Default limit

	if limitParam := c.QueryParam("limit"); limitParam != "" {
		if parsedLimit, err := fmt.Sscanf(limitParam, "%d", &limit); err != nil || parsedLimit != 1 {
			return echo.NewHTTPError(http.StatusBadRequest, "Invalid limit parameter")
		}
	}

	executions, err := h.meltanoService.ListExecutions(c.Request().Context(), projectName, limit)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to list executions: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"project":    projectName,
		"executions": executions,
		"count":      len(executions),
		"limit":      limit,
	})
}

// GetExecution retrieves details of a specific execution
func (h *MeltanoHandler) GetExecution(c echo.Context) error {
	executionID := c.Param("id")

	execution, err := h.meltanoService.GetExecution(c.Request().Context(), executionID)
	if err != nil {
		return echo.NewHTTPError(http.StatusNotFound,
			fmt.Sprintf("Execution not found: %v", err))
	}

	return c.JSON(http.StatusOK, execution)
}

// SavePluginStateRequest represents a plugin state save request
type SavePluginStateRequest struct {
	State map[string]interface{} `json:"state" validate:"required"`
}

// SavePluginState saves state for a plugin
func (h *MeltanoHandler) SavePluginState(c echo.Context) error {
	projectName := c.Param("name")
	pluginName := c.Param("plugin")

	var req SavePluginStateRequest
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid request format")
	}

	if err := c.Validate(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}

	if err := h.meltanoService.SavePluginState(c.Request().Context(), projectName, pluginName, req.State); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to save plugin state: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"project": projectName,
		"plugin":  pluginName,
		"message": "State saved successfully",
	})
}

// LoadPluginState loads state for a plugin
func (h *MeltanoHandler) LoadPluginState(c echo.Context) error {
	projectName := c.Param("name")
	pluginName := c.Param("plugin")

	state, err := h.meltanoService.LoadPluginState(c.Request().Context(), projectName, pluginName)
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to load plugin state: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"project": projectName,
		"plugin":  pluginName,
		"state":   state,
	})
}

// DeletePluginState deletes state for a plugin
func (h *MeltanoHandler) DeletePluginState(c echo.Context) error {
	projectName := c.Param("name")
	pluginName := c.Param("plugin")

	if err := h.meltanoService.DeletePluginState(c.Request().Context(), projectName, pluginName); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError,
			fmt.Sprintf("Failed to delete plugin state: %v", err))
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"project": projectName,
		"plugin":  pluginName,
		"message": "State deleted successfully",
	})
}
