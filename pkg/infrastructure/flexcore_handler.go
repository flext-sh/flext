package http

import (
	"context"
	"fmt"
	"net/http"
	"os/exec"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/flexcore_plugin"
	"github.com/flext-sh/flext/pkg/infrastructure/logging"
	shared_kernel_http "github.com/flext-sh/flext/pkg/infrastructure/http"
	"github.com/labstack/echo/v4"
)

// FlexcoreHandler handles FLEXCORE plugin execution requests
type FlexcoreHandler struct {
	*shared_kernel_http.BaseHandler
	pluginRegistry *flexcore_plugin.PluginRegistry
	logger         logging.Logger
}

// NewFlexcoreHandler creates a new FLEXCORE handler
func NewFlexcoreHandler(pluginRegistry *flexcore_plugin.PluginRegistry, logger logging.Logger) *FlexcoreHandler {
	return &FlexcoreHandler{
		BaseHandler:    shared_kernel_http.NewBaseHandler("FlexcoreHandler", logger),
		pluginRegistry: pluginRegistry,
		logger:         logger,
	}
}

// ExecutePlugin handles POST /api/v1/flexcore/plugins/:name/execute
func (h *FlexcoreHandler) ExecutePlugin(c echo.Context) error {
	pluginName := c.Param("name")
	if pluginName == "" {
		return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
			Error:   "Bad Request",
			Message: "Plugin name is required",
			Code:    "REQUIRED_FIELD",
		})
	}

	var params map[string]interface{}
	if err := c.Bind(&params); err != nil {
		return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
			Error:   "Bad Request",
			Message: "Invalid request body format",
			Code:    "INVALID_JSON",
		})
	}

	// Add request metadata
	if params == nil {
		params = make(map[string]interface{})
	}
	params["request_id"] = c.Response().Header().Get(echo.HeaderXRequestID)
	params["user_agent"] = c.Request().UserAgent()
	params["remote_ip"] = c.RealIP()

	h.logger.Info("🚀 Executing FLEXCORE plugin",
		logging.F("plugin", pluginName),
		logging.F("params", params),
		logging.F("request_id", c.Response().Header().Get(echo.HeaderXRequestID)))

	// HACK: Execute Meltano directly if plugin name is "meltano"
	if pluginName == "meltano" {
		h.logger.Info("🎯 DIRECT: Executing Meltano plugin directly", logging.F("params", params))
		
		result, err := h.executeMeltanoDirect(c.Request().Context(), params)
		if err != nil {
			return h.HandleError(c, err)
		}

		return h.HandleSuccess(c, map[string]interface{}{
			"plugin": pluginName,
			"result": result,
			"status": "success",
		})
	}

	// Execute plugin via registry
	result, err := h.pluginRegistry.ExecutePlugin(c.Request().Context(), pluginName, params)
	if err != nil {
		h.logger.Error("❌ FLEXCORE plugin execution failed",
			logging.F("plugin", pluginName),
			logging.F("error", err))
		return h.HandleError(c, err)
	}

	h.logger.Info("✅ FLEXCORE plugin execution completed",
		logging.F("plugin", pluginName),
		logging.F("request_id", c.Response().Header().Get(echo.HeaderXRequestID)))

	return h.HandleSuccess(c, map[string]interface{}{
		"plugin": pluginName,
		"result": result,
		"status": "success",
	})
}

// ListPlugins handles GET /api/v1/flexcore/plugins
func (h *FlexcoreHandler) ListPlugins(c echo.Context) error {
	plugins := h.pluginRegistry.ListPlugins()

	return h.HandleSuccess(c, map[string]interface{}{
		"plugins": plugins,
		"count":   h.pluginRegistry.GetPluginCount(),
	})
}

// GetPlugin handles GET /api/v1/flexcore/plugins/:name
func (h *FlexcoreHandler) GetPlugin(c echo.Context) error {
	pluginName := c.Param("name")
	if pluginName == "" {
		return c.JSON(http.StatusBadRequest, shared_kernel_http.ErrorResponse{
			Error:   "Bad Request",
			Message: "Plugin name is required",
			Code:    "REQUIRED_FIELD",
		})
	}

	plugin, err := h.pluginRegistry.GetPlugin(pluginName)
	if err != nil {
		return c.JSON(http.StatusNotFound, shared_kernel_http.ErrorResponse{
			Error:   "Not Found",
			Message: "Plugin not found",
			Code:    "NOT_FOUND",
		})
	}

	pluginInfo := plugin.GetPluginInfo()
	return h.HandleSuccess(c, pluginInfo)
}

// ValidatePlugins handles POST /api/v1/flexcore/validate
func (h *FlexcoreHandler) ValidatePlugins(c echo.Context) error {
	h.logger.Info("🔧 Validating all FLEXCORE plugins")

	err := h.pluginRegistry.ValidateAllPlugins()
	if err != nil {
		h.logger.Error("❌ Plugin validation failed", logging.F("error", err))
		return h.HandleError(c, err)
	}

	h.logger.Info("✅ All FLEXCORE plugins validated successfully")

	return h.HandleSuccess(c, map[string]interface{}{
		"status":        "validated",
		"plugin_count":  h.pluginRegistry.GetPluginCount(),
		"message":       "All plugins validated successfully",
	})
}

// RegisterRoutes registers the FLEXCORE handler routes
func (h *FlexcoreHandler) RegisterRoutes(e *echo.Echo) {
	flexcoreAPI := e.Group("/api/v1/flexcore")

	flexcoreAPI.GET("/plugins", h.ListPlugins)
	flexcoreAPI.GET("/plugins/:name", h.GetPlugin)
	flexcoreAPI.POST("/plugins/:name/execute", h.ExecutePlugin)
	flexcoreAPI.POST("/validate", h.ValidatePlugins)

	h.logger.Info("✅ FLEXCORE handler routes registered",
		logging.F("base_path", "/api/v1/flexcore"),
		logging.F("endpoints", []string{
			"GET /plugins",
			"GET /plugins/:name", 
			"POST /plugins/:name/execute",
			"POST /validate",
		}))
}

// executeMeltanoDirect executes Meltano directly via Python subprocess
func (h *FlexcoreHandler) executeMeltanoDirect(ctx context.Context, params map[string]interface{}) (interface{}, error) {
	h.logger.Info("🎭 DIRECT: Executing Meltano via direct Python call", logging.F("params", params))
	
	// Parse parameters
	command, _ := params["command"].(string)
	if command == "" {
		command = "run"
	}
	
	extractor, _ := params["extractor"].(string)
	loader, _ := params["loader"].(string)
	dryRun, _ := params["dry_run"].(bool)
	
	jobID := fmt.Sprintf("meltano-direct-%d", time.Now().Unix())
	startTime := time.Now()
	
	if dryRun {
		return map[string]interface{}{
			"job_id":    jobID,
			"status":    "success", 
			"exit_code": 0,
			"output":    fmt.Sprintf("DRY RUN: Would execute meltano %s %s %s", command, extractor, loader),
			"dry_run":   true,
			"start_time": startTime,
			"end_time":   time.Now(),
		}, nil
	}
	
	// Execute real Meltano command via .venv/bin/meltano
	workspaceDir := "/home/marlonsc/flext"
	meltanoPath := "/home/marlonsc/flext/.venv/bin/meltano"
	
	var cmdArgs []string
	cmdArgs = append(cmdArgs, meltanoPath, command)
	if extractor != "" {
		cmdArgs = append(cmdArgs, extractor)
	}
	if loader != "" {
		cmdArgs = append(cmdArgs, loader)
	}
	
	// Execute with timeout
	execCtx, cancel := context.WithTimeout(ctx, 5*time.Minute)
	defer cancel()
	
	cmd := exec.CommandContext(execCtx, cmdArgs[0], cmdArgs[1:]...)
	cmd.Dir = workspaceDir
	cmd.Env = append(cmd.Environ(), "MELTANO_ENVIRONMENT=dev")
	
	output, err := cmd.CombinedOutput()
	endTime := time.Now()
	
	result := map[string]interface{}{
		"job_id": jobID,
		"start_time": startTime,
		"end_time": endTime,
		"duration": endTime.Sub(startTime).Seconds(),
		"output": string(output),
	}
	
	if err != nil {
		h.logger.Error("❌ DIRECT: Meltano execution failed", logging.F("error", err))
		result["status"] = "error"
		result["exit_code"] = 1
		result["error_output"] = err.Error()
	} else {
		h.logger.Info("✅ DIRECT: Meltano execution successful", logging.F("job_id", jobID))
		result["status"] = "success"
		result["exit_code"] = 0
	}
	
	return result, nil
}