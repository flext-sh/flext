package http

import (
	"net/http"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
)

// TemplAPIHandler fornece endpoints para componentes reativos
type TemplAPIHandler struct{}

// NewTemplAPIHandler cria um novo handler para APIs reativas
func NewTemplAPIHandler() *TemplAPIHandler {
	return &TemplAPIHandler{}
}

// RegisterRoutes registra as rotas da API reativa
func (h *TemplAPIHandler) RegisterRoutes(e *echo.Echo) {
	api := e.Group("/api")
	
	// Dashboard endpoints
	api.GET("/dashboard/stats", h.GetDashboardStats)
	api.GET("/activity/recent", h.GetRecentActivity)
	api.GET("/stats/:type", h.GetStatValue)
	
	// Data endpoints
	api.GET("/pipelines/table", h.GetPipelinesTable)
	api.GET("/plugins/table", h.GetPluginsTable)
	api.GET("/logs/recent", h.GetRecentLogs)
	
	// Chart endpoints
	api.GET("/charts/:id/data", h.GetChartData)
}

// GetDashboardStats retorna estatísticas do dashboard
func (h *TemplAPIHandler) GetDashboardStats(c echo.Context) error {
	stats := map[string]interface{}{
		"pipelines":    3,
		"plugins":      8,
		"activeJobs":   2,
		"systemStatus": "healthy",
		"timestamp":    time.Now().Unix(),
	}
	return c.JSON(http.StatusOK, stats)
}

// GetRecentActivity retorna atividades recentes (HTML fragment)
func (h *TemplAPIHandler) GetRecentActivity(c echo.Context) error {
	activities := []map[string]string{
		{"time": "2 minutes ago", "action": "Pipeline 'Data ETL' completed successfully", "type": "success"},
		{"time": "5 minutes ago", "action": "Plugin 'Oracle Connector' registered", "type": "info"},
		{"time": "10 minutes ago", "action": "Pipeline 'Log Processing' started", "type": "info"},
		{"time": "15 minutes ago", "action": "System health check passed", "type": "success"},
	}

	html := ""
	for _, activity := range activities {
		icon := "fas fa-info-circle"
		if activity["type"] == "success" {
			icon = "fas fa-check-circle"
		}

		html += `<div class="flex items-start space-x-3 p-3 border-l-4 border-` + activity["type"] + `-400 bg-` + activity["type"] + `-50 rounded-r-lg mb-3 transition-all duration-300 hover:shadow-md">`
		html += `<div class="flex-shrink-0"><i class="` + icon + ` text-` + activity["type"] + `-500 mt-1"></i></div>`
		html += `<div class="min-w-0 flex-1">`
		html += `<p class="text-sm text-gray-600">` + activity["time"] + `</p>`
		html += `<p class="text-sm font-medium text-gray-900">` + activity["action"] + `</p>`
		html += `</div></div>`
	}

	return c.HTML(http.StatusOK, html)
}

// GetStatValue retorna um valor de estatística específico
func (h *TemplAPIHandler) GetStatValue(c echo.Context) error {
	statType := c.Param("type")
	
	switch statType {
	case "Pipelines":
		return c.String(http.StatusOK, "3")
	case "Plugins":
		return c.String(http.StatusOK, "8")
	case "Active Jobs":
		return c.String(http.StatusOK, "2")
	default:
		return c.String(http.StatusOK, "0")
	}
}

// GetPipelinesTable retorna a tabela de pipelines (HTML fragment)
func (h *TemplAPIHandler) GetPipelinesTable(c echo.Context) error {
	pipelines := []map[string]interface{}{
		{"id": 1, "name": "Data ETL Pipeline", "status": "active", "steps": 4, "created": "2025-06-30"},
		{"id": 2, "name": "Log Processing", "status": "running", "steps": 3, "created": "2025-06-29"},
		{"id": 3, "name": "Analytics Pipeline", "status": "inactive", "steps": 5, "created": "2025-06-28"},
	}

	html := ""
	for _, pipeline := range pipelines {
		statusColor := "bg-gray-100 text-gray-800"
		switch pipeline["status"] {
		case "active":
			statusColor = "bg-green-100 text-green-800"
		case "running":
			statusColor = "bg-blue-100 text-blue-800"
		case "inactive":
			statusColor = "bg-gray-100 text-gray-800"
		}

		html += `<tr class="hover:bg-gray-50 transition-colors">`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">` + strconv.Itoa(pipeline["id"].(int)) + `</td>`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">` + pipeline["name"].(string) + `</td>`
		html += `<td class="px-6 py-4 whitespace-nowrap"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ` + statusColor + `">` + pipeline["status"].(string) + `</span></td>`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">` + strconv.Itoa(pipeline["steps"].(int)) + `</td>`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">` + pipeline["created"].(string) + `</td>`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">`
		html += `<div class="flex space-x-2">`
		html += `<button class="text-blue-600 hover:text-blue-900 transition" hx-get="/web/pipelines/` + strconv.Itoa(pipeline["id"].(int)) + `" hx-target="body"><i class="fas fa-eye"></i></button>`
		html += `<button class="text-green-600 hover:text-green-900 transition" hx-post="/api/pipelines/` + strconv.Itoa(pipeline["id"].(int)) + `/execute"><i class="fas fa-play"></i></button>`
		html += `<button class="text-red-600 hover:text-red-900 transition" hx-delete="/api/pipelines/` + strconv.Itoa(pipeline["id"].(int)) + `" hx-confirm="Are you sure?"><i class="fas fa-trash"></i></button>`
		html += `</div></td>`
		html += `</tr>`
	}

	return c.HTML(http.StatusOK, html)
}

// GetPluginsTable retorna a tabela de plugins (HTML fragment)
func (h *TemplAPIHandler) GetPluginsTable(c echo.Context) error {
	plugins := []map[string]interface{}{
		{"name": "tap-oracle-wms", "type": "extractor", "version": "1.0.0", "status": "active", "description": "Oracle WMS data extractor"},
		{"name": "target-postgres", "type": "loader", "version": "2.1.0", "status": "active", "description": "PostgreSQL data loader"},
		{"name": "tap-ldap", "type": "extractor", "version": "1.2.3", "status": "inactive", "description": "LDAP directory extractor"},
	}

	html := ""
	for _, plugin := range plugins {
		typeColor := "bg-blue-100 text-blue-800"
		switch plugin["type"] {
		case "extractor":
			typeColor = "bg-blue-100 text-blue-800"
		case "loader":
			typeColor = "bg-green-100 text-green-800"
		case "transformer":
			typeColor = "bg-yellow-100 text-yellow-800"
		}

		statusColor := "bg-gray-100 text-gray-800"
		if plugin["status"] == "active" {
			statusColor = "bg-green-100 text-green-800"
		}

		html += `<tr class="hover:bg-gray-50 transition-colors">`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">` + plugin["name"].(string) + `</td>`
		html += `<td class="px-6 py-4 whitespace-nowrap"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ` + typeColor + `">` + plugin["type"].(string) + `</span></td>`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">` + plugin["version"].(string) + `</td>`
		html += `<td class="px-6 py-4 whitespace-nowrap"><span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ` + statusColor + `">` + plugin["status"].(string) + `</span></td>`
		html += `<td class="px-6 py-4 text-sm text-gray-500">` + plugin["description"].(string) + `</td>`
		html += `<td class="px-6 py-4 whitespace-nowrap text-sm font-medium">`
		html += `<div class="flex space-x-2">`
		html += `<button class="text-blue-600 hover:text-blue-900 transition"><i class="fas fa-eye"></i></button>`
		html += `<button class="text-yellow-600 hover:text-yellow-900 transition"><i class="fas fa-toggle-on"></i></button>`
		html += `<button class="text-red-600 hover:text-red-900 transition" hx-confirm="Are you sure?"><i class="fas fa-trash"></i></button>`
		html += `</div></td>`
		html += `</tr>`
	}

	return c.HTML(http.StatusOK, html)
}

// GetRecentLogs retorna logs recentes (HTML fragment)
func (h *TemplAPIHandler) GetRecentLogs(c echo.Context) error {
	logs := []string{
		"[2025-06-30 15:30:45] INFO: Server started successfully",
		"[2025-06-30 15:30:46] INFO: Database connection established",
		"[2025-06-30 15:30:47] WARN: Plugin initialization took longer than expected",
		"[2025-06-30 15:30:48] INFO: Pipeline executor initialized",
		"[2025-06-30 15:30:49] INFO: Web interface handler registered",
	}

	html := ""
	for _, log := range logs {
		html += log + "\n"
	}

	return c.String(http.StatusOK, html)
}

// GetChartData retorna dados para gráficos
func (h *TemplAPIHandler) GetChartData(c echo.Context) error {
	chartId := c.Param("id")
	
	switch chartId {
	case "overviewChart":
		data := map[string]interface{}{
			"labels": []string{"Pipelines", "Plugins", "Active Jobs"},
			"datasets": []map[string]interface{}{
				{
					"data":            []int{3, 8, 2},
					"backgroundColor": []string{"#3B82F6", "#10B981", "#F59E0B"},
				},
			},
		}
		return c.JSON(http.StatusOK, data)
	case "performanceChart":
		data := map[string]interface{}{
			"labels": []string{"00:00", "04:00", "08:00", "12:00", "16:00", "20:00"},
			"datasets": []map[string]interface{}{
				{
					"label":           "CPU Usage %",
					"data":            []int{45, 32, 78, 65, 89, 23},
					"borderColor":     "#3B82F6",
					"backgroundColor": "rgba(59, 130, 246, 0.1)",
					"fill":            true,
				},
				{
					"label":           "Memory Usage %",
					"data":            []int{35, 42, 58, 55, 69, 33},
					"borderColor":     "#10B981",
					"backgroundColor": "rgba(16, 185, 129, 0.1)",
					"fill":            true,
				},
			},
		}
		return c.JSON(http.StatusOK, data)
	default:
		return c.JSON(http.StatusNotFound, map[string]string{"error": "Chart not found"})
	}
}
