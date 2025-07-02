package http

import (
	"net/http"
	"time"

	"github.com/flext-sh/flext/internal/bounded_contexts/meltano/application/services"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/labstack/echo/v4"
)

// MeltanoGopyHandler provides HTTP endpoints for Python-Go Meltano integration
type MeltanoGopyHandler struct {
	service *services.MeltanoService
	logger  logging.Logger
}

// NewMeltanoGopyHandler creates a new Meltano Gopy HTTP handler
func NewMeltanoGopyHandler(service *services.MeltanoService, logger logging.Logger) *MeltanoGopyHandler {
	return &MeltanoGopyHandler{
		service: service,
		logger:  logger,
	}
}

// RegisterRoutes registers all Meltano Gopy routes
func (h *MeltanoGopyHandler) RegisterRoutes(e *echo.Echo) {
	gopy := e.Group("/api/v1/gopy")
	
	// Basic availability and version endpoints
	gopy.GET("/available", h.CheckAvailable)
	gopy.GET("/version", h.GetVersion)
	
	// Project management
	gopy.POST("/projects", h.CreateProject)
	gopy.GET("/projects/info", h.GetProjectInfo)
	gopy.GET("/projects/list", h.ListProjects)
	
	// Plugin management
	gopy.POST("/plugins", h.AddPlugin)
	gopy.GET("/plugins", h.GetPlugins)
	gopy.POST("/plugins/install", h.InstallPlugins)
	
	// Pipeline execution
	gopy.POST("/pipelines/run", h.RunPipeline)
	gopy.POST("/commands/execute", h.ExecuteCommand)
	
	// State management
	gopy.GET("/state/stats", h.GetStateStats)
	gopy.POST("/state/save", h.SaveState)
	gopy.GET("/state/load", h.LoadState)
	gopy.DELETE("/state/delete", h.DeleteState)
}

// Response structures
type APIResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
	Meta    *MetaInfo   `json:"meta,omitempty"`
}

type MetaInfo struct {
	Timestamp time.Time `json:"timestamp"`
	Endpoint  string    `json:"endpoint"`
	Duration  string    `json:"duration,omitempty"`
}

// Request structures
type CreateProjectRequest struct {
	Name      string `json:"name" validate:"required"`
	Directory string `json:"directory" validate:"required"`
}

type AddPluginRequest struct {
	PluginType string `json:"plugin_type" validate:"required"`
	Name       string `json:"name" validate:"required"`
	Variant    string `json:"variant"`
}

type RunPipelineRequest struct {
	Extractor   string `json:"extractor" validate:"required"`
	Loader      string `json:"loader" validate:"required"`
	Transformer string `json:"transformer"`
}

type ExecuteCommandRequest struct {
	Command string   `json:"command" validate:"required"`
	Args    []string `json:"args"`
}

type SaveStateRequest struct {
	Project string                 `json:"project" validate:"required"`
	Plugin  string                 `json:"plugin" validate:"required"`
	State   map[string]interface{} `json:"state" validate:"required"`
}

type LoadStateRequest struct {
	Project string `json:"project" validate:"required"`
	Plugin  string `json:"plugin" validate:"required"`
}

// Handler implementations

func (h *MeltanoGopyHandler) CheckAvailable(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	available, err := h.service.IsAvailable(ctx)
	if err != nil {
		h.logger.Error("Failed to check Meltano availability", logging.F("error", err.Error()))
	}
	
	response := APIResponse{
		Success: available,
		Data: map[string]interface{}{
			"available": available,
			"message": func() string {
				if available {
					return "Meltano CLI is available and functional"
				}
				return "Meltano CLI not available"
			}(),
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/available",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) GetVersion(c echo.Context) error {
	start := time.Now()
	
	response := APIResponse{
		Success: true,
		Data: map[string]interface{}{
			"gopy_version":    "2.0.0",
			"flext_version":   "2.0.0",
			"meltano_bridge":  "http",
			"integration":     "fully_functional",
			"api_version":     "v1",
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/version",
			Duration:  time.Since(start).String(),
		},
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) CreateProject(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	var req CreateProjectRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, APIResponse{
			Success: false,
			Error:   "Invalid request format",
			Meta: &MetaInfo{
				Timestamp: time.Now(),
				Endpoint:  "/api/v1/gopy/projects",
				Duration:  time.Since(start).String(),
			},
		})
	}
	
	result, err := h.service.InitProject(ctx, req.Name, req.Directory)
	
	response := APIResponse{
		Success: err == nil && result.Success,
		Data: map[string]interface{}{
			"project_name": req.Name,
			"directory":    req.Directory,
			"result":       result,
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/projects",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	if result.Error != "" {
		response.Error = result.Error
		return c.JSON(http.StatusBadRequest, response)
	}
	
	return c.JSON(http.StatusCreated, response)
}

func (h *MeltanoGopyHandler) GetProjectInfo(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	result, err := h.service.GetProjectInfo(ctx)
	
	response := APIResponse{
		Success: err == nil && result.Success,
		Data:    result.Data,
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/projects/info",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	if result.Error != "" {
		response.Error = result.Error
		return c.JSON(http.StatusBadRequest, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) ListProjects(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	rootDir := c.QueryParam("root_dir")
	if rootDir == "" {
		rootDir = "."
	}
	
	projects, err := h.service.ListProjects(ctx, rootDir)
	
	response := APIResponse{
		Success: err == nil,
		Data: map[string]interface{}{
			"projects":  projects,
			"count":     len(projects),
			"root_dir":  rootDir,
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/projects/list",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) AddPlugin(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	var req AddPluginRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, APIResponse{
			Success: false,
			Error:   "Invalid request format",
			Meta: &MetaInfo{
				Timestamp: time.Now(),
				Endpoint:  "/api/v1/gopy/plugins",
				Duration:  time.Since(start).String(),
			},
		})
	}
	
	result, err := h.service.AddPlugin(ctx, req.PluginType, req.Name, req.Variant)
	
	response := APIResponse{
		Success: err == nil && result.Success,
		Data: map[string]interface{}{
			"plugin_type": req.PluginType,
			"name":        req.Name,
			"variant":     req.Variant,
			"result":      result,
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/plugins",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	if result.Error != "" {
		response.Error = result.Error
		return c.JSON(http.StatusBadRequest, response)
	}
	
	return c.JSON(http.StatusCreated, response)
}

func (h *MeltanoGopyHandler) GetPlugins(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	result, err := h.service.GetPlugins(ctx)
	
	response := APIResponse{
		Success: err == nil && result.Success,
		Data:    result.Data,
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/plugins",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	if result.Error != "" {
		response.Error = result.Error
		return c.JSON(http.StatusBadRequest, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) InstallPlugins(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	result, err := h.service.InstallPlugins(ctx)
	
	response := APIResponse{
		Success: err == nil && result.Success,
		Data:    result.Data,
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/plugins/install",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	if result.Error != "" {
		response.Error = result.Error
		return c.JSON(http.StatusBadRequest, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) RunPipeline(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	var req RunPipelineRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, APIResponse{
			Success: false,
			Error:   "Invalid request format",
			Meta: &MetaInfo{
				Timestamp: time.Now(),
				Endpoint:  "/api/v1/gopy/pipelines/run",
				Duration:  time.Since(start).String(),
			},
		})
	}
	
	result, err := h.service.RunPipeline(ctx, req.Extractor, req.Loader, req.Transformer)
	
	response := APIResponse{
		Success: err == nil && result.Success,
		Data: map[string]interface{}{
			"extractor":   req.Extractor,
			"loader":      req.Loader,
			"transformer": req.Transformer,
			"result":      result,
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/pipelines/run",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	if result.Error != "" {
		response.Error = result.Error
		return c.JSON(http.StatusBadRequest, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) ExecuteCommand(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	var req ExecuteCommandRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, APIResponse{
			Success: false,
			Error:   "Invalid request format",
			Meta: &MetaInfo{
				Timestamp: time.Now(),
				Endpoint:  "/api/v1/gopy/commands/execute",
				Duration:  time.Since(start).String(),
			},
		})
	}
	
	result, err := h.service.ExecuteCommand(ctx, req.Command, req.Args)
	
	response := APIResponse{
		Success: err == nil && result.Success,
		Data: map[string]interface{}{
			"command": req.Command,
			"args":    req.Args,
			"result":  result,
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/commands/execute",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	if result.Error != "" {
		response.Error = result.Error
		return c.JSON(http.StatusBadRequest, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) GetStateStats(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	stats, err := h.service.GetStateStats(ctx)
	
	response := APIResponse{
		Success: err == nil,
		Data:    stats,
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/state/stats",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) SaveState(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	var req SaveStateRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, APIResponse{
			Success: false,
			Error:   "Invalid request format",
			Meta: &MetaInfo{
				Timestamp: time.Now(),
				Endpoint:  "/api/v1/gopy/state/save",
				Duration:  time.Since(start).String(),
			},
		})
	}
	
	err := h.service.SavePluginState(ctx, req.Project, req.Plugin, req.State)
	
	response := APIResponse{
		Success: err == nil,
		Data: map[string]interface{}{
			"project": req.Project,
			"plugin":  req.Plugin,
			"message": "State saved successfully",
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/state/save",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) LoadState(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	project := c.QueryParam("project")
	plugin := c.QueryParam("plugin")
	
	if project == "" || plugin == "" {
		return c.JSON(http.StatusBadRequest, APIResponse{
			Success: false,
			Error:   "project and plugin parameters are required",
			Meta: &MetaInfo{
				Timestamp: time.Now(),
				Endpoint:  "/api/v1/gopy/state/load",
				Duration:  time.Since(start).String(),
			},
		})
	}
	
	state, err := h.service.LoadPluginState(ctx, project, plugin)
	
	response := APIResponse{
		Success: err == nil,
		Data: map[string]interface{}{
			"project": project,
			"plugin":  plugin,
			"state":   state,
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/state/load",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	return c.JSON(http.StatusOK, response)
}

func (h *MeltanoGopyHandler) DeleteState(c echo.Context) error {
	start := time.Now()
	ctx := c.Request().Context()
	
	project := c.QueryParam("project")
	plugin := c.QueryParam("plugin")
	
	if project == "" || plugin == "" {
		return c.JSON(http.StatusBadRequest, APIResponse{
			Success: false,
			Error:   "project and plugin parameters are required",
			Meta: &MetaInfo{
				Timestamp: time.Now(),
				Endpoint:  "/api/v1/gopy/state/delete",
				Duration:  time.Since(start).String(),
			},
		})
	}
	
	err := h.service.DeletePluginState(ctx, project, plugin)
	
	response := APIResponse{
		Success: err == nil,
		Data: map[string]interface{}{
			"project": project,
			"plugin":  plugin,
			"message": "State deleted successfully",
		},
		Meta: &MetaInfo{
			Timestamp: time.Now(),
			Endpoint:  "/api/v1/gopy/state/delete",
			Duration:  time.Since(start).String(),
		},
	}
	
	if err != nil {
		response.Error = err.Error()
		return c.JSON(http.StatusInternalServerError, response)
	}
	
	return c.JSON(http.StatusOK, response)
}