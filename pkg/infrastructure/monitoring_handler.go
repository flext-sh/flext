package http

import (
	"net/http"
	"strconv"

	"github.com/flext-sh/flext/pkg/infrastructure/monitoring"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

// MonitoringHandler handles monitoring-related HTTP requests
type MonitoringHandler struct {
	realtimeMonitor  *monitoring.RealtimeMonitor
	metricsCollector *monitoring.MetricsCollector
	traceManager     *monitoring.TraceManager
	healthChecker    *monitoring.HealthChecker
}

// NewMonitoringHandler creates a new monitoring handler
func NewMonitoringHandler(realtimeMonitor *monitoring.RealtimeMonitor, metricsCollector *monitoring.MetricsCollector, traceManager *monitoring.TraceManager, healthChecker *monitoring.HealthChecker) *MonitoringHandler {
	return &MonitoringHandler{
		realtimeMonitor:  realtimeMonitor,
		metricsCollector: metricsCollector,
		traceManager:     traceManager,
		healthChecker:    healthChecker,
	}
}

// GetSystemStats returns current system statistics
func (h *MonitoringHandler) GetSystemStats(c echo.Context) error {
	stats := h.realtimeMonitor.GetSystemStats()
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    stats,
	})
}

// GetPerformanceStats returns current performance statistics
func (h *MonitoringHandler) GetPerformanceStats(c echo.Context) error {
	stats := h.realtimeMonitor.GetPerformanceStats()
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    stats,
	})
}

// GetPipelineStats returns statistics for a specific pipeline
func (h *MonitoringHandler) GetPipelineStats(c echo.Context) error {
	pipelineIDStr := c.Param("id")

	pipelineID, err := uuid.Parse(pipelineIDStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]interface{}{
			"success": false,
			"error":   "Invalid pipeline ID format",
		})
	}

	stats, exists := h.realtimeMonitor.GetPipelineStats(pipelineID)
	if !exists {
		return c.JSON(http.StatusNotFound, map[string]interface{}{
			"success": false,
			"error":   "Pipeline statistics not found",
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    stats,
	})
}

// GetAllPipelineStats returns statistics for all pipelines
func (h *MonitoringHandler) GetAllPipelineStats(c echo.Context) error {
	params := h.extractPaginationParams(c)
	allStats := h.realtimeMonitor.GetAllPipelineStats()

	filteredStats := h.filterStatsByStatus(allStats, params.Status)
	paginatedStats := h.applyPagination(filteredStats, params)

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"pipelines": paginatedStats.Data,
			"total":     paginatedStats.Total,
			"limit":     paginatedStats.Limit,
			"offset":    paginatedStats.Offset,
		},
	})
}

// PaginationParams holds pagination and filtering parameters
type PaginationParams struct {
	Status string
	Limit  int
	Offset int
}

// PaginatedResult holds paginated data
type PaginatedResult struct {
	Data   []interface{}
	Total  int
	Limit  int
	Offset int
}

// extractPaginationParams extracts pagination parameters from request
func (h *MonitoringHandler) extractPaginationParams(c echo.Context) PaginationParams {
	params := PaginationParams{
		Status: c.QueryParam("status"),
		Limit:  50, // default
		Offset: 0,  // default
	}

	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 {
			params.Limit = l
		}
	}

	if offsetStr := c.QueryParam("offset"); offsetStr != "" {
		if o, err := strconv.Atoi(offsetStr); err == nil && o >= 0 {
			params.Offset = o
		}
	}

	return params
}

// filterStatsByStatus filters pipeline stats by status
func (h *MonitoringHandler) filterStatsByStatus(allStats map[string]*monitoring.PipelineStats, status string) []interface{} {
	var filteredStats []interface{}
	for _, stats := range allStats {
		if status == "" || stats.Status == status {
			filteredStats = append(filteredStats, stats)
		}
	}
	return filteredStats
}

// applyPagination applies pagination to the filtered data
func (h *MonitoringHandler) applyPagination(data []interface{}, params PaginationParams) PaginatedResult {
	total := len(data)
	end := params.Offset + params.Limit
	if end > total {
		end = total
	}

	var paginatedData []interface{}
	if params.Offset < total {
		paginatedData = data[params.Offset:end]
	} else {
		paginatedData = []interface{}{}
	}

	return PaginatedResult{
		Data:   paginatedData,
		Total:  total,
		Limit:  params.Limit,
		Offset: params.Offset,
	}
}

// GetRealtimeDashboard returns comprehensive dashboard data
func (h *MonitoringHandler) GetRealtimeDashboard(c echo.Context) error {
	systemStats := h.realtimeMonitor.GetSystemStats()
	performanceStats := h.realtimeMonitor.GetPerformanceStats()
	allPipelineStats := h.realtimeMonitor.GetAllPipelineStats()

	// Calculate dashboard metrics
	dashboardData := map[string]interface{}{
		"system":      systemStats,
		"performance": performanceStats,
		"pipelines": map[string]interface{}{
			"total":     len(allPipelineStats),
			"running":   h.countPipelinesByStatus(allPipelineStats, "running"),
			"completed": h.countPipelinesByStatus(allPipelineStats, "completed"),
			"failed":    h.countPipelinesByStatus(allPipelineStats, "failed"),
			"recent":    h.getRecentPipelines(allPipelineStats, 10),
		},
		"alerts": h.generateSystemAlerts(systemStats, performanceStats),
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    dashboardData,
	})
}

// GetWebSocketInfo returns WebSocket connection information
func (h *MonitoringHandler) GetWebSocketInfo(c echo.Context) error {
	// This would integrate with WebSocket manager to get connection stats
	// For now, return mock data
	wsInfo := map[string]interface{}{
		"connected_clients": 5,
		"total_connections": 25,
		"active_topics": []string{
			"system_stats",
			"performance",
			"pipelines",
			"alerts",
			"pipeline_logs",
		},
		"uptime": "2h 15m 30s",
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    wsInfo,
	})
}

// GetMetricsHistory returns historical metrics data
func (h *MonitoringHandler) GetMetricsHistory(c echo.Context) error {
	metricType := c.QueryParam("type")
	hoursStr := c.QueryParam("hours")

	hours := 24 // default
	if hoursStr != "" {
		if h, err := strconv.Atoi(hoursStr); err == nil && h > 0 {
			hours = h
		}
	}

	// Generate mock historical data
	historyData := h.generateMetricsHistory(metricType, hours)

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"metric_type": metricType,
			"hours":       hours,
			"data_points": historyData,
		},
	})
}

// countPipelinesByStatus counts pipelines by their status
func (h *MonitoringHandler) countPipelinesByStatus(stats map[string]*monitoring.PipelineStats, status string) int {
	count := 0
	for _, s := range stats {
		if s.Status == status {
			count++
		}
	}
	return count
}

// getRecentPipelines returns the most recent pipelines
func (h *MonitoringHandler) getRecentPipelines(stats map[string]*monitoring.PipelineStats, limit int) []interface{} {
	var recent []interface{}

	// Convert to slice and sort by start time (simplified)
	for _, s := range stats {
		recent = append(recent, s)
		if len(recent) >= limit {
			break
		}
	}

	return recent
}

// generateSystemAlerts generates alerts based on current system state
func (h *MonitoringHandler) generateSystemAlerts(systemStats *monitoring.SystemStats, perfStats *monitoring.PerformanceStats) []interface{} {
	var alerts []interface{}

	if memAlert := h.checkMemoryAlert(systemStats); memAlert != nil {
		alerts = append(alerts, memAlert)
	}

	if errAlert := h.checkErrorRateAlert(perfStats); errAlert != nil {
		alerts = append(alerts, errAlert)
	}

	if pipeAlert := h.checkPipelineAlert(systemStats); pipeAlert != nil {
		alerts = append(alerts, pipeAlert)
	}

	return alerts
}

// checkMemoryAlert checks for high memory usage
func (h *MonitoringHandler) checkMemoryAlert(systemStats *monitoring.SystemStats) map[string]interface{} {
	if systemStats.MemoryUsage.UsagePercent > 80 {
		return map[string]interface{}{
			"type":     "memory",
			"severity": "warning",
			"message":  "High memory usage detected",
			"value":    systemStats.MemoryUsage.UsagePercent,
		}
	}
	return nil
}

// checkErrorRateAlert checks for high error rate
func (h *MonitoringHandler) checkErrorRateAlert(perfStats *monitoring.PerformanceStats) map[string]interface{} {
	if perfStats.ErrorRate > 0.05 {
		return map[string]interface{}{
			"type":     "errors",
			"severity": "critical",
			"message":  "High error rate detected",
			"value":    perfStats.ErrorRate,
		}
	}
	return nil
}

// checkPipelineAlert checks for failed pipelines
func (h *MonitoringHandler) checkPipelineAlert(systemStats *monitoring.SystemStats) map[string]interface{} {
	if systemStats.FailedPipelines > 0 {
		return map[string]interface{}{
			"type":     "pipelines",
			"severity": "warning",
			"message":  "Failed pipelines detected",
			"value":    systemStats.FailedPipelines,
		}
	}
	return nil
}

// generateMetricsHistory generates mock historical metrics data
func (h *MonitoringHandler) generateMetricsHistory(metricType string, hours int) []map[string]interface{} {
	var dataPoints []map[string]interface{}

	for i := hours; i > 0; i-- {
		timestamp := h.generateTimestamp(i)
		value := h.generateMetricValue(metricType, i)

		dataPoints = append(dataPoints, map[string]interface{}{
			"timestamp": timestamp,
			"value":     value,
		})
	}

	return dataPoints
}

// generateTimestamp creates a timestamp for historical data
func (h *MonitoringHandler) generateTimestamp(hoursBack int) string {
	return "2024-01-01T" + strconv.Itoa(24-hoursBack) + ":00:00Z"
}

// generateMetricValue generates a mock value based on metric type
func (h *MonitoringHandler) generateMetricValue(metricType string, i int) interface{} {
	switch metricType {
	case "cpu":
		return 10.0 + float64(i%20) // Mock CPU usage
	case "memory":
		return 30.0 + float64(i%50) // Mock memory usage
	case "requests":
		return 100 + i*10 // Mock request count
	case "errors":
		return float64(i%5) / 100.0 // Mock error rate
	default:
		return float64(i % 100)
	}
}

// GetComprehensiveMetrics returns comprehensive metrics from MetricsCollector
func (h *MonitoringHandler) GetComprehensiveMetrics(c echo.Context) error {
	if h.metricsCollector == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Metrics collector not available",
		})
	}

	metrics := h.metricsCollector.GetMetrics()
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    metrics,
	})
}

// GetAlerts returns current system alerts
func (h *MonitoringHandler) GetAlerts(c echo.Context) error {
	if h.metricsCollector == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Metrics collector not available",
		})
	}

	alerts := h.metricsCollector.GetAlerts()
	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"alerts": alerts,
			"count":  len(alerts),
		},
	})
}

// GetTraces returns distributed tracing information
func (h *MonitoringHandler) GetTraces(c echo.Context) error {
	if h.traceManager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Trace manager not available",
		})
	}

	// Query parameters
	status := c.QueryParam("status")
	limitStr := c.QueryParam("limit")

	var traces []*monitoring.Trace
	if status == "active" {
		traces = h.traceManager.GetActiveTraces()
	} else {
		traces = h.traceManager.GetRecentTraces()
	}

	// Apply limit if specified
	if limitStr != "" {
		if limit, err := strconv.Atoi(limitStr); err == nil && limit > 0 && limit < len(traces) {
			traces = traces[:limit]
		}
	}

	stats := h.traceManager.GetTracingStatistics()

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data": map[string]interface{}{
			"traces":     traces,
			"statistics": stats,
		},
	})
}

// GetTrace returns a specific trace by ID
func (h *MonitoringHandler) GetTrace(c echo.Context) error {
	if h.traceManager == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Trace manager not available",
		})
	}

	traceID := c.Param("id")
	trace, exists := h.traceManager.GetTrace(traceID)

	if !exists {
		return c.JSON(http.StatusNotFound, map[string]interface{}{
			"success": false,
			"error":   "Trace not found",
		})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"data":    trace,
	})
}

// GetHealthCheck returns comprehensive health check results
func (h *MonitoringHandler) GetHealthCheck(c echo.Context) error {
	if h.healthChecker == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Health checker not available",
		})
	}

	ctx := c.Request().Context()
	health := h.healthChecker.GetOverallHealth(ctx)

	// Determine HTTP status based on health
	httpStatus := http.StatusOK
	if health.Status == "unhealthy" {
		httpStatus = http.StatusServiceUnavailable
	} else if health.Status == "degraded" {
		httpStatus = http.StatusPartialContent
	}

	return c.JSON(httpStatus, map[string]interface{}{
		"success": health.Status != "unhealthy",
		"data":    health,
	})
}

// GetComponentHealth returns health status for a specific component
func (h *MonitoringHandler) GetComponentHealth(c echo.Context) error {
	if h.healthChecker == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Health checker not available",
		})
	}

	component := c.Param("component")
	ctx := c.Request().Context()

	result := h.healthChecker.RunCheck(ctx, component)

	if result.Status == "unknown" && result.Error == "check not registered" {
		return c.JSON(http.StatusNotFound, map[string]interface{}{
			"success": false,
			"error":   "Component health check not found",
		})
	}

	httpStatus := http.StatusOK
	if result.Status == "unhealthy" {
		httpStatus = http.StatusServiceUnavailable
	} else if result.Status == "degraded" {
		httpStatus = http.StatusPartialContent
	}

	return c.JSON(httpStatus, map[string]interface{}{
		"success": result.Status != "unhealthy",
		"data":    result,
	})
}

// PostMetricValue allows setting custom business metrics
func (h *MonitoringHandler) PostMetricValue(c echo.Context) error {
	if h.metricsCollector == nil {
		return c.JSON(http.StatusServiceUnavailable, map[string]interface{}{
			"success": false,
			"error":   "Metrics collector not available",
		})
	}

	var request struct {
		Name     string  `json:"name" validate:"required"`
		Category string  `json:"category" validate:"required"`
		Value    float64 `json:"value" validate:"required"`
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

	h.metricsCollector.SetBusinessMetric(request.Name, request.Category, request.Value)

	return c.JSON(http.StatusOK, map[string]interface{}{
		"success": true,
		"message": "Metric value set successfully",
		"data": map[string]interface{}{
			"name":     request.Name,
			"category": request.Category,
			"value":    request.Value,
		},
	})
}
