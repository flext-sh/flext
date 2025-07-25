package http

import (
	"net/http"

	"github.com/flext-sh/flext/internal/bounded_contexts/meltano/application/services"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/labstack/echo/v4"
)

// UnifiedMeltanoHandler handles all Meltano, Singer, and DBT requests via flext-meltano library
// This consolidates all data integration functionality into a single handler
type UnifiedMeltanoHandler struct {
	meltanoService *services.MeltanoService
	logger         logging.Logger
}

// NewUnifiedMeltanoHandler creates a new unified handler for all data integration operations
func NewUnifiedMeltanoHandler(meltanoService *services.MeltanoService, logger logging.Logger) *UnifiedMeltanoHandler {
	return &UnifiedMeltanoHandler{
		meltanoService: meltanoService,
		logger:         logger,
	}
}

// RegisterRoutes registers all unified data integration routes
func (h *UnifiedMeltanoHandler) RegisterRoutes(e *echo.Echo) {
	// Meltano operations
	meltanoGroup := e.Group("/api/v1/meltano")
	meltanoGroup.GET("/version", h.GetMeltanoVersion)
	meltanoGroup.POST("/run", h.RunMeltano)
	meltanoGroup.POST("/test", h.TestMeltano)
	meltanoGroup.GET("/plugins", h.ListMeltanoPlugins)
	meltanoGroup.POST("/install", h.InstallMeltanoPlugin)

	// Singer operations (via flext-meltano)
	singerGroup := e.Group("/api/v1/singer")
	singerGroup.GET("/taps", h.ListSingerTaps)
	singerGroup.GET("/targets", h.ListSingerTargets)
	singerGroup.POST("/discover", h.DiscoverSingerCatalog)
	singerGroup.POST("/run", h.RunSingerPipeline)

	// DBT operations (via flext-meltano)
	dbtGroup := e.Group("/api/v1/dbt")
	dbtGroup.POST("/run", h.RunDBT)
	dbtGroup.POST("/test", h.TestDBT)
	dbtGroup.POST("/compile", h.CompileDBT)
	dbtGroup.GET("/models", h.ListDBTModels)
}

// Meltano Operations

func (h *UnifiedMeltanoHandler) GetMeltanoVersion(c echo.Context) error {
	h.logger.Info("Getting Meltano version via flext-meltano")

	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "version", []string{})
	if err != nil {
		h.logger.Error("Failed to get Meltano version", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

func (h *UnifiedMeltanoHandler) RunMeltano(c echo.Context) error {
	var request struct {
		Command string   `json:"command"`
		Args    []string `json:"args"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"error": "Invalid request format",
		})
	}

	h.logger.Info("Running Meltano command via flext-meltano",
		logging.F("command", request.Command),
		logging.F("args", request.Args))

	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), request.Command, request.Args)
	if err != nil {
		h.logger.Error("Meltano execution failed", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

func (h *UnifiedMeltanoHandler) TestMeltano(c echo.Context) error {
	h.logger.Info("Testing Meltano via flext-meltano")

	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "test", []string{})
	if err != nil {
		h.logger.Error("Meltano test failed", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

func (h *UnifiedMeltanoHandler) ListMeltanoPlugins(c echo.Context) error {
	h.logger.Info("Listing Meltano plugins via flext-meltano")

	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "list", []string{"plugins"})
	if err != nil {
		h.logger.Error("Failed to list Meltano plugins", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

func (h *UnifiedMeltanoHandler) InstallMeltanoPlugin(c echo.Context) error {
	var request struct {
		Type string `json:"type"`
		Name string `json:"name"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"error": "Invalid request format",
		})
	}

	h.logger.Info("Installing Meltano plugin via flext-meltano",
		logging.F("type", request.Type),
		logging.F("name", request.Name))

	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "add", []string{request.Type, request.Name})
	if err != nil {
		h.logger.Error("Failed to install Meltano plugin", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

// Singer Operations (via flext-meltano Singer integration)

func (h *UnifiedMeltanoHandler) ListSingerTaps(c echo.Context) error {
	h.logger.Info("Listing Singer taps via flext-meltano")

	// Use flext-meltano to list available taps
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "list", []string{"extractors"})
	if err != nil {
		h.logger.Error("Failed to list Singer taps", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
		"type":    "singer_taps",
	})
}

func (h *UnifiedMeltanoHandler) ListSingerTargets(c echo.Context) error {
	h.logger.Info("Listing Singer targets via flext-meltano")

	// Use flext-meltano to list available targets
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "list", []string{"loaders"})
	if err != nil {
		h.logger.Error("Failed to list Singer targets", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
		"type":    "singer_targets",
	})
}

func (h *UnifiedMeltanoHandler) DiscoverSingerCatalog(c echo.Context) error {
	var request struct {
		TapName string `json:"tap_name"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"error": "Invalid request format",
		})
	}

	h.logger.Info("Discovering Singer catalog via flext-meltano",
		logging.F("tap", request.TapName))

	// Use flext-meltano to discover catalog
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "invoke", []string{request.TapName, "--discover"})
	if err != nil {
		h.logger.Error("Failed to discover Singer catalog", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
		"tap":     request.TapName,
	})
}

func (h *UnifiedMeltanoHandler) RunSingerPipeline(c echo.Context) error {
	var request struct {
		TapName    string `json:"tap_name"`
		TargetName string `json:"target_name"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"error": "Invalid request format",
		})
	}

	h.logger.Info("Running Singer pipeline via flext-meltano",
		logging.F("tap", request.TapName),
		logging.F("target", request.TargetName))

	// Use flext-meltano to run Singer pipeline
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "run", []string{request.TapName, request.TargetName})
	if err != nil {
		h.logger.Error("Singer pipeline execution failed", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

// DBT Operations (via flext-meltano DBT integration)

func (h *UnifiedMeltanoHandler) RunDBT(c echo.Context) error {
	var request struct {
		Command string   `json:"command"`
		Models  []string `json:"models,omitempty"`
	}

	if err := c.Bind(&request); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"error": "Invalid request format",
		})
	}

	h.logger.Info("Running DBT via flext-meltano",
		logging.F("command", request.Command),
		logging.F("models", request.Models))

	// Build DBT command args
	args := []string{"dbt:" + request.Command}
	if len(request.Models) > 0 {
		args = append(args, "--models")
		args = append(args, request.Models...)
	}

	// Use flext-meltano to run DBT
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "invoke", args)
	if err != nil {
		h.logger.Error("DBT execution failed", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
		"command": request.Command,
	})
}

func (h *UnifiedMeltanoHandler) TestDBT(c echo.Context) error {
	h.logger.Info("Testing DBT via flext-meltano")

	// Use flext-meltano to test DBT
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "invoke", []string{"dbt:test"})
	if err != nil {
		h.logger.Error("DBT test failed", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

func (h *UnifiedMeltanoHandler) CompileDBT(c echo.Context) error {
	h.logger.Info("Compiling DBT via flext-meltano")

	// Use flext-meltano to compile DBT
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "invoke", []string{"dbt:compile"})
	if err != nil {
		h.logger.Error("DBT compilation failed", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

func (h *UnifiedMeltanoHandler) ListDBTModels(c echo.Context) error {
	h.logger.Info("Listing DBT models via flext-meltano")

	// Use flext-meltano to list DBT models
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "invoke", []string{"dbt:list", "--resource-type", "model"})
	if err != nil {
		h.logger.Error("Failed to list DBT models", logging.F("error", err))
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    result,
	})
}

// Health check for unified handler
func (h *UnifiedMeltanoHandler) HealthCheck(c echo.Context) error {
	h.logger.Info("Checking unified Meltano handler health")

	// Test flext-meltano connection
	result, err := h.meltanoService.ExecuteCommand(c.Request().Context(), "version", []string{})
	if err != nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"status": "unhealthy",
			"error":  err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"status":           "healthy",
		"handler":          "unified_meltano",
		"flext_meltano":    "operational",
		"capabilities":     []string{"meltano", "singer", "dbt"},
		"version_check":    result,
		"library":          "flext-meltano Python integration",
	})
}