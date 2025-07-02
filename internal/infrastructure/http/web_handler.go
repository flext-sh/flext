package http

import (
	"net/http"
	"strconv"

	"github.com/flext-sh/flext/internal/bounded_contexts/pipeline/application/queries"
	pluginApplication "github.com/flext-sh/flext/internal/bounded_contexts/plugin/application"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/labstack/echo/v4"
)

// WebHandler provides web interface endpoints
type WebHandler struct {
	logger          logging.Logger
	pipelineQueries *queries.GetPipelineQuery
	pluginService   *pluginApplication.PluginService
}

// NewWebHandler creates a new web interface handler
func NewWebHandler(
	logger logging.Logger,
	pipelineQueries *queries.GetPipelineQuery,
	pluginService *pluginApplication.PluginService,
) *WebHandler {
	return &WebHandler{
		logger:          logger,
		pipelineQueries: pipelineQueries,
		pluginService:   pluginService,
	}
}

// RegisterRoutes registers web interface routes
func (h *WebHandler) RegisterRoutes(e *echo.Echo) {
	// Setup template renderer
	e.Renderer = &TemplRenderer{}
	
	// Web interface routes
	e.GET("/web", h.Dashboard)
	e.GET("/web/pipelines", h.PipelinesList)
	e.GET("/web/pipelines/:id", h.PipelineDetail)
	e.GET("/web/plugins", h.PluginsList)
	e.GET("/web/monitoring", h.MonitoringDashboard)

	// Static files
	e.Static("/static", "web/static")
	
	// Register API endpoints for reactive components
	apiHandler := NewTemplAPIHandler()
	apiHandler.RegisterRoutes(e)
}

// Dashboard serves the main dashboard page
func (h *WebHandler) Dashboard(c echo.Context) error {
	data := map[string]interface{}{
		"Title":   "FLEXT Dashboard",
		"Version": "2.0.0",
	}

	return c.Render(http.StatusOK, "dashboard.html", data)
}

// PipelinesList serves the pipelines list page
func (h *WebHandler) PipelinesList(c echo.Context) error {
	data := map[string]interface{}{
		"Title": "Pipelines - FLEXT",
	}

	return c.Render(http.StatusOK, "pipelines.html", data)
}

// PipelineDetail serves individual pipeline details
func (h *WebHandler) PipelineDetail(c echo.Context) error {
	id := c.Param("id")
	pipelineID, err := strconv.ParseInt(id, 10, 64)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "Invalid pipeline ID")
	}

	data := map[string]interface{}{
		"Title":      "Pipeline Details - FLEXT",
		"PipelineID": pipelineID,
	}

	return c.Render(http.StatusOK, "pipeline_detail.html", data)
}

// PluginsList serves the plugins list page
func (h *WebHandler) PluginsList(c echo.Context) error {
	data := map[string]interface{}{
		"Title": "Plugins - FLEXT",
	}

	return c.Render(http.StatusOK, "plugins.html", data)
}

// MonitoringDashboard serves the monitoring dashboard
func (h *WebHandler) MonitoringDashboard(c echo.Context) error {
	data := map[string]interface{}{
		"Title": "Monitoring - FLEXT",
	}

	return c.Render(http.StatusOK, "monitoring.html", data)
}
