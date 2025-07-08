package http

import (
	"fmt"
	"net/http"
	"strconv"

	"github.com/flext-sh/flext/internal/infrastructure/dbt"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/labstack/echo/v4"
)

// DBTHandler handles dbt-related HTTP requests
type DBTHandler struct {
	dbtManager *dbt.DBTManager
	logger     logging.Logger
}

// NewDBTHandler creates a new dbt handler
func NewDBTHandler(dbtManager *dbt.DBTManager, logger logging.Logger) *DBTHandler {
	return &DBTHandler{
		dbtManager: dbtManager,
		logger:     logger,
	}
}

// DBTRunRequest represents a dbt run request
type DBTRunRequest struct {
	Models []string `json:"models,omitempty"`
	Target string   `json:"target,omitempty"`
}

// DBTTestRequest represents a dbt test request
type DBTTestRequest struct {
	Models []string `json:"models,omitempty"`
	Target string   `json:"target,omitempty"`
}

// DBTCompileRequest represents a dbt compile request
type DBTCompileRequest struct {
	Models []string `json:"models,omitempty"`
	Target string   `json:"target,omitempty"`
}

// DBTDocsRequest represents a dbt docs request
type DBTDocsRequest struct {
	Serve bool `json:"serve,omitempty"`
	Port  int  `json:"port,omitempty"`
}

// DBTSeedRequest represents a dbt seed request
type DBTSeedRequest struct {
	Seeds  []string `json:"seeds,omitempty"`
	Target string   `json:"target,omitempty"`
}

// DBTSnapshotRequest represents a dbt snapshot request
type DBTSnapshotRequest struct {
	Snapshots []string `json:"snapshots,omitempty"`
	Target    string   `json:"target,omitempty"`
}

// DBTInitRequest represents a dbt init request
type DBTInitRequest struct {
	ProjectName string `json:"project_name"`
}

// DBTProfileRequest represents a dbt profile creation request
type DBTProfileRequest struct {
	ProfileName string                 `json:"profile_name"`
	Config      map[string]interface{} `json:"config"`
}

// RegisterRoutes registers dbt routes
func (h *DBTHandler) RegisterRoutes(e *echo.Echo) {
	dbtGroup := e.Group("/api/v1/dbt")

	// Project management
	dbtGroup.POST("/init", h.InitProject)
	dbtGroup.GET("/info", h.GetProjectInfo)
	dbtGroup.POST("/profile", h.CreateProfile)
	dbtGroup.POST("/connection/test", h.TestConnection)

	// dbt commands
	dbtGroup.POST("/run", h.Run)
	dbtGroup.POST("/test", h.Test)
	dbtGroup.POST("/compile", h.Compile)
	dbtGroup.POST("/docs", h.GenerateDocs)
	dbtGroup.POST("/seed", h.Seed)
	dbtGroup.POST("/snapshot", h.Snapshot)

	// Information endpoints
	dbtGroup.GET("/models", h.ListModels)
	dbtGroup.GET("/tests", h.ListTests)
	dbtGroup.GET("/history", h.GetRunHistory)
}

// InitProject initializes a new dbt project
func (h *DBTHandler) InitProject(c echo.Context) error {
	var req DBTInitRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	if req.ProjectName == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Project name is required",
		})
	}

	result, err := h.dbtManager.InitProject(c.Request().Context(), req.ProjectName)
	if err != nil {
		h.logger.Error("Failed to initialize dbt project",
			logging.F("project_name", req.ProjectName),
			logging.F("error", err.Error()),
		)
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, result)
}

// GetProjectInfo retrieves dbt project information
func (h *DBTHandler) GetProjectInfo(c echo.Context) error {
	info, err := h.dbtManager.GetProjectInfo(c.Request().Context())
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, info)
}

// CreateProfile creates a dbt profile
func (h *DBTHandler) CreateProfile(c echo.Context) error {
	var req DBTProfileRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	if req.ProfileName == "" {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Profile name is required",
		})
	}

	err := h.dbtManager.CreateProfile(req.ProfileName, req.Config)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]string{
		"message": "Profile created successfully",
		"profile": req.ProfileName,
	})
}

// TestConnection tests dbt database connection
func (h *DBTHandler) TestConnection(c echo.Context) error {
	target := c.QueryParam("target")

	result, err := h.dbtManager.CheckConnection(c.Request().Context(), target)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error":  err.Error(),
			"result": result,
		})
	}

	return c.JSON(http.StatusOK, result)
}

// Run executes dbt run command
func (h *DBTHandler) Run(c echo.Context) error {
	var req DBTRunRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	result, err := h.dbtManager.Run(c.Request().Context(), req.Models, req.Target)
	if err != nil {
		h.logger.Error("DBT run failed",
			logging.F("models", req.Models),
			logging.F("target", req.Target),
			logging.F("error", err.Error()),
		)
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error":  err.Error(),
			"result": result,
		})
	}

	return c.JSON(http.StatusOK, result)
}

// Test executes dbt test command
func (h *DBTHandler) Test(c echo.Context) error {
	var req DBTTestRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	result, err := h.dbtManager.Test(c.Request().Context(), req.Models, req.Target)
	if err != nil {
		h.logger.Error("DBT test failed",
			logging.F("models", req.Models),
			logging.F("target", req.Target),
			logging.F("error", err.Error()),
		)
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error":  err.Error(),
			"result": result,
		})
	}

	return c.JSON(http.StatusOK, result)
}

// Compile executes dbt compile command
func (h *DBTHandler) Compile(c echo.Context) error {
	var req DBTCompileRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	result, err := h.dbtManager.Compile(c.Request().Context(), req.Models, req.Target)
	if err != nil {
		h.logger.Error("DBT compile failed",
			logging.F("models", req.Models),
			logging.F("target", req.Target),
			logging.F("error", err.Error()),
		)
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error":  err.Error(),
			"result": result,
		})
	}

	return c.JSON(http.StatusOK, result)
}

// GenerateDocs generates dbt documentation
func (h *DBTHandler) GenerateDocs(c echo.Context) error {
	var req DBTDocsRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	if req.Port == 0 {
		req.Port = 8080
	}

	result, err := h.dbtManager.Docs(c.Request().Context(), req.Serve, req.Port)
	if err != nil {
		h.logger.Error("DBT docs generation failed",
			logging.F("serve", req.Serve),
			logging.F("port", req.Port),
			logging.F("error", err.Error()),
		)
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error":  err.Error(),
			"result": result,
		})
	}

	response := map[string]interface{}{
		"result": result,
	}

	if req.Serve {
		response["docs_url"] = map[string]interface{}{
			"url":  fmt.Sprintf("http://localhost:%d", req.Port),
			"port": req.Port,
		}
	}

	return c.JSON(http.StatusOK, response)
}

// Seed executes dbt seed command
func (h *DBTHandler) Seed(c echo.Context) error {
	var req DBTSeedRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	result, err := h.dbtManager.Seed(c.Request().Context(), req.Seeds, req.Target)
	if err != nil {
		h.logger.Error("DBT seed failed",
			logging.F("seeds", req.Seeds),
			logging.F("target", req.Target),
			logging.F("error", err.Error()),
		)
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error":  err.Error(),
			"result": result,
		})
	}

	return c.JSON(http.StatusOK, result)
}

// Snapshot executes dbt snapshot command
func (h *DBTHandler) Snapshot(c echo.Context) error {
	var req DBTSnapshotRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body",
		})
	}

	result, err := h.dbtManager.Snapshot(c.Request().Context(), req.Snapshots, req.Target)
	if err != nil {
		h.logger.Error("DBT snapshot failed",
			logging.F("snapshots", req.Snapshots),
			logging.F("target", req.Target),
			logging.F("error", err.Error()),
		)
		return c.JSON(http.StatusInternalServerError, map[string]interface{}{
			"error":  err.Error(),
			"result": result,
		})
	}

	return c.JSON(http.StatusOK, result)
}

// ListModels lists all available dbt models
func (h *DBTHandler) ListModels(c echo.Context) error {
	models, err := h.dbtManager.ListModels(c.Request().Context())
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"models": models,
		"count":  len(models),
	})
}

// ListTests lists all available dbt tests
func (h *DBTHandler) ListTests(c echo.Context) error {
	tests, err := h.dbtManager.ListTests(c.Request().Context())
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"tests": tests,
		"count": len(tests),
	})
}

// GetRunHistory retrieves dbt run history
func (h *DBTHandler) GetRunHistory(c echo.Context) error {
	limitStr := c.QueryParam("limit")
	limit := 10 // default limit

	if limitStr != "" {
		if parsedLimit, err := strconv.Atoi(limitStr); err == nil && parsedLimit > 0 {
			limit = parsedLimit
		}
	}

	history, err := h.dbtManager.GetRunHistory(c.Request().Context(), limit)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": err.Error(),
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"history": history,
		"count":   len(history),
		"limit":   limit,
	})
}
