package monitoring

import (
	"context"
	"runtime"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/samber/lo"
)

// MetricsCollector collects comprehensive system and application metrics
type MetricsCollector struct {
	logger logging.Logger
	mu     sync.RWMutex

	// Prometheus metrics
	httpRequestsTotal       *prometheus.CounterVec
	httpRequestDuration     *prometheus.HistogramVec
	httpActiveConnections   prometheus.Gauge
	systemMemoryUsage       prometheus.Gauge
	systemCPUUsage          prometheus.Gauge
	goRoutines              prometheus.Gauge
	gcDuration              prometheus.Histogram
	pipelineExecutions      *prometheus.CounterVec
	pipelineExecutionTime   *prometheus.HistogramVec
	databaseConnections     prometheus.Gauge
	databaseQueryDuration   *prometheus.HistogramVec
	connectorOperations     *prometheus.CounterVec
	connectorResponseTime   *prometheus.HistogramVec
	errorRate               *prometheus.CounterVec
	businessMetrics         *prometheus.GaugeVec

	// Custom metrics tracking
	customMetrics map[string]float64
	alerts        []Alert
	startTime     time.Time
}

// Alert represents a monitoring alert
type Alert struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Severity    AlertSeverity          `json:"severity"`
	Status      AlertStatus            `json:"status"`
	Labels      map[string]string      `json:"labels"`
	Annotations map[string]string      `json:"annotations"`
	StartsAt    time.Time              `json:"starts_at"`
	EndsAt      *time.Time             `json:"ends_at,omitempty"`
	Value       float64                `json:"value"`
	Threshold   float64                `json:"threshold"`
	Metadata    map[string]interface{} `json:"metadata"`
}

type AlertSeverity string
type AlertStatus string

const (
	AlertSeverityInfo     AlertSeverity = "info"
	AlertSeverityWarning  AlertSeverity = "warning"
	AlertSeverityError    AlertSeverity = "error"
	AlertSeverityCritical AlertSeverity = "critical"

	AlertStatusFiring   AlertStatus = "firing"
	AlertStatusResolved AlertStatus = "resolved"
	AlertStatusPending  AlertStatus = "pending"
)

// NewMetricsCollector creates a new metrics collector
func NewMetricsCollector(logger logging.Logger) *MetricsCollector {
	mc := &MetricsCollector{
		logger:        logger,
		customMetrics: make(map[string]float64),
		alerts:        make([]Alert, 0),
		startTime:     time.Now(),
	}

	mc.initPrometheusMetrics()
	return mc
}

// initPrometheusMetrics initializes all Prometheus metrics
func (mc *MetricsCollector) initPrometheusMetrics() {
	// HTTP metrics
	mc.httpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "flext_http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status_code"},
	)

	mc.httpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "flext_http_request_duration_seconds",
			Help:    "HTTP request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)

	mc.httpActiveConnections = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "flext_http_active_connections",
			Help: "Number of active HTTP connections",
		},
	)

	// System metrics
	mc.systemMemoryUsage = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "flext_system_memory_usage_bytes",
			Help: "System memory usage in bytes",
		},
	)

	mc.systemCPUUsage = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "flext_system_cpu_usage_percent",
			Help: "System CPU usage percentage",
		},
	)

	mc.goRoutines = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "flext_goroutines_count",
			Help: "Number of goroutines",
		},
	)

	mc.gcDuration = promauto.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "flext_gc_duration_seconds",
			Help:    "Garbage collection duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
	)

	// Pipeline metrics
	mc.pipelineExecutions = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "flext_pipeline_executions_total",
			Help: "Total number of pipeline executions",
		},
		[]string{"pipeline_id", "status"},
	)

	mc.pipelineExecutionTime = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "flext_pipeline_execution_duration_seconds",
			Help:    "Pipeline execution duration in seconds",
			Buckets: []float64{.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10, 30, 60, 300},
		},
		[]string{"pipeline_id"},
	)

	// Database metrics
	mc.databaseConnections = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "flext_database_connections_active",
			Help: "Number of active database connections",
		},
	)

	mc.databaseQueryDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "flext_database_query_duration_seconds",
			Help:    "Database query duration in seconds",
			Buckets: []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5},
		},
		[]string{"operation", "table"},
	)

	// Connector metrics
	mc.connectorOperations = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "flext_connector_operations_total",
			Help: "Total number of connector operations",
		},
		[]string{"connector_type", "operation", "status"},
	)

	mc.connectorResponseTime = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "flext_connector_response_time_seconds",
			Help:    "Connector operation response time in seconds",
			Buckets: []float64{.01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
		},
		[]string{"connector_type", "operation"},
	)

	// Error metrics
	mc.errorRate = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "flext_errors_total",
			Help: "Total number of errors by type and component",
		},
		[]string{"component", "error_type", "severity"},
	)

	// Business metrics
	mc.businessMetrics = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "flext_business_metrics",
			Help: "Custom business metrics",
		},
		[]string{"metric_name", "category"},
	)
}

// RecordHTTPRequest records HTTP request metrics
func (mc *MetricsCollector) RecordHTTPRequest(method, endpoint, statusCode string, duration time.Duration) {
	mc.httpRequestsTotal.WithLabelValues(method, endpoint, statusCode).Inc()
	mc.httpRequestDuration.WithLabelValues(method, endpoint).Observe(duration.Seconds())
}

// SetActiveConnections sets the number of active HTTP connections
func (mc *MetricsCollector) SetActiveConnections(count int) {
	mc.httpActiveConnections.Set(float64(count))
}

// RecordPipelineExecution records pipeline execution metrics
func (mc *MetricsCollector) RecordPipelineExecution(pipelineID, status string, duration time.Duration) {
	mc.pipelineExecutions.WithLabelValues(pipelineID, status).Inc()
	mc.pipelineExecutionTime.WithLabelValues(pipelineID).Observe(duration.Seconds())
}

// RecordDatabaseQuery records database query metrics
func (mc *MetricsCollector) RecordDatabaseQuery(operation, table string, duration time.Duration) {
	mc.databaseQueryDuration.WithLabelValues(operation, table).Observe(duration.Seconds())
}

// SetDatabaseConnections sets the number of active database connections
func (mc *MetricsCollector) SetDatabaseConnections(count int) {
	mc.databaseConnections.Set(float64(count))
}

// RecordConnectorOperation records connector operation metrics
func (mc *MetricsCollector) RecordConnectorOperation(connectorType, operation, status string, duration time.Duration) {
	mc.connectorOperations.WithLabelValues(connectorType, operation, status).Inc()
	mc.connectorResponseTime.WithLabelValues(connectorType, operation).Observe(duration.Seconds())
}

// RecordError records error metrics
func (mc *MetricsCollector) RecordError(component, errorType, severity string) {
	mc.errorRate.WithLabelValues(component, errorType, severity).Inc()
}

// SetBusinessMetric sets a custom business metric
func (mc *MetricsCollector) SetBusinessMetric(name, category string, value float64) {
	mc.mu.Lock()
	defer mc.mu.Unlock()

	key := name + ":" + category
	mc.customMetrics[key] = value
	mc.businessMetrics.WithLabelValues(name, category).Set(value)
}

// CollectSystemMetrics collects system-level metrics
func (mc *MetricsCollector) CollectSystemMetrics() {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// Memory metrics
	mc.systemMemoryUsage.Set(float64(memStats.Alloc))

	// Goroutine metrics
	mc.goRoutines.Set(float64(runtime.NumGoroutine()))

	// GC metrics
	if memStats.NumGC > 0 {
		gcDuration := time.Duration(memStats.PauseNs[(memStats.NumGC+255)%256])
		mc.gcDuration.Observe(gcDuration.Seconds())
	}
}

// StartMetricsCollection starts periodic metrics collection
func (mc *MetricsCollector) StartMetricsCollection(ctx context.Context, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	mc.logger.Info("Starting metrics collection",
		logging.F("interval", interval.String()),
	)

	for {
		select {
		case <-ctx.Done():
			mc.logger.Info("Stopping metrics collection")
			return
		case <-ticker.C:
			mc.CollectSystemMetrics()
			mc.evaluateAlerts()
		}
	}
}

// evaluateAlerts evaluates alert conditions
func (mc *MetricsCollector) evaluateAlerts() {
	mc.mu.Lock()
	defer mc.mu.Unlock()

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// Memory usage alert
	memoryUsageMB := float64(memStats.Alloc) / 1024 / 1024
	if memoryUsageMB > 1000 { // 1GB threshold
		mc.triggerAlert("high_memory_usage", AlertSeverityWarning, 
			"High memory usage detected", memoryUsageMB, 1000)
	}

	// Goroutine count alert
	goroutineCount := float64(runtime.NumGoroutine())
	if goroutineCount > 1000 {
		mc.triggerAlert("high_goroutine_count", AlertSeverityWarning,
			"High goroutine count detected", goroutineCount, 1000)
	}

	// Clean up resolved alerts
	mc.cleanupResolvedAlerts()
}

// triggerAlert triggers an alert
func (mc *MetricsCollector) triggerAlert(name string, severity AlertSeverity, description string, value, threshold float64) {
	// Check if alert already exists using functional programming
	if existingAlert, found := lo.Find(mc.alerts, func(alert Alert) bool {
		return alert.Name == name && alert.Status == AlertStatusFiring
	}); found {
		// Update existing alert
		var existingIndex int
	for i, alert := range mc.alerts {
		if alert.Name == existingAlert.Name && alert.Status == existingAlert.Status {
			existingIndex = i
			break
		}
	}
		mc.alerts[existingIndex].Value = value
		return
	}

	// Create new alert
	alert := Alert{
		ID:          name + "_" + time.Now().Format("20060102150405"),
		Name:        name,
		Description: description,
		Severity:    severity,
		Status:      AlertStatusFiring,
		StartsAt:    time.Now(),
		Value:       value,
		Threshold:   threshold,
		Labels: map[string]string{
			"alert_name": name,
			"severity":   string(severity),
		},
		Annotations: map[string]string{
			"description": description,
			"summary":     description,
		},
		Metadata: map[string]interface{}{
			"triggered_by": "metrics_collector",
			"component":    "observability",
		},
	}

	mc.alerts = append(mc.alerts, alert)
	mc.logger.Warn("Alert triggered",
		logging.F("alert_name", name),
		logging.F("severity", string(severity)),
		logging.F("value", value),
		logging.F("threshold", threshold),
	)
}

// cleanupResolvedAlerts removes resolved alerts older than 1 hour
func (mc *MetricsCollector) cleanupResolvedAlerts() {
	cutoff := time.Now().Add(-time.Hour)
	// Use functional programming to filter alerts
	mc.alerts = lo.Filter(mc.alerts, func(alert Alert, _ int) bool {
		// Keep alerts that are not old resolved alerts
		if alert.Status == AlertStatusResolved && alert.EndsAt != nil && alert.EndsAt.Before(cutoff) {
			return false // Skip old resolved alerts
		}
		return true
	})
}

// GetMetrics returns comprehensive metrics
func (mc *MetricsCollector) GetMetrics() map[string]interface{} {
	mc.mu.RLock()
	defer mc.mu.RUnlock()

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	return map[string]interface{}{
		"system": map[string]interface{}{
			"memory": map[string]interface{}{
				"alloc_bytes":        memStats.Alloc,
				"total_alloc_bytes":  memStats.TotalAlloc,
				"sys_bytes":          memStats.Sys,
				"heap_alloc_bytes":   memStats.HeapAlloc,
				"heap_sys_bytes":     memStats.HeapSys,
				"heap_idle_bytes":    memStats.HeapIdle,
				"heap_inuse_bytes":   memStats.HeapInuse,
				"stack_inuse_bytes":  memStats.StackInuse,
				"stack_sys_bytes":    memStats.StackSys,
			},
			"gc": map[string]interface{}{
				"num_gc":        memStats.NumGC,
				"pause_total_ns": memStats.PauseTotalNs,
				"next_gc":       memStats.NextGC,
				"last_gc":       time.Unix(0, int64(memStats.LastGC)),
			},
			"goroutines": runtime.NumGoroutine(),
			"cpu_count":  runtime.NumCPU(),
		},
		"runtime": map[string]interface{}{
			"uptime_seconds": time.Since(mc.startTime).Seconds(),
			"start_time":     mc.startTime,
			"go_version":     runtime.Version(),
		},
		"custom_metrics": mc.customMetrics,
		"alerts": map[string]interface{}{
			"active_count": mc.getActiveAlertCount(),
			"total_count":  len(mc.alerts),
			"alerts":       mc.alerts,
		},
		"health": map[string]interface{}{
			"status":     mc.getHealthStatus(),
			"components": mc.getComponentHealth(),
		},
	}
}

// getActiveAlertCount returns the number of active alerts
func (mc *MetricsCollector) getActiveAlertCount() int {
	count := 0
	for _, alert := range mc.alerts {
		if alert.Status == AlertStatusFiring {
			count++
		}
	}
	return count
}

// getHealthStatus returns overall health status
func (mc *MetricsCollector) getHealthStatus() string {
	activeAlerts := mc.getActiveAlertCount()
	if activeAlerts == 0 {
		return "healthy"
	}

	// Check for critical alerts
	for _, alert := range mc.alerts {
		if alert.Status == AlertStatusFiring && alert.Severity == AlertSeverityCritical {
			return "critical"
		}
	}

	// Check for error alerts
	for _, alert := range mc.alerts {
		if alert.Status == AlertStatusFiring && alert.Severity == AlertSeverityError {
			return "degraded"
		}
	}

	return "warning"
}

// getComponentHealth returns health status for each component
func (mc *MetricsCollector) getComponentHealth() map[string]interface{} {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	components := map[string]interface{}{
		"memory": map[string]interface{}{
			"status":       mc.getMemoryHealth(memStats),
			"usage_bytes":  memStats.Alloc,
			"usage_mb":     float64(memStats.Alloc) / 1024 / 1024,
		},
		"goroutines": map[string]interface{}{
			"status": mc.getGoroutineHealth(),
			"count":  runtime.NumGoroutine(),
		},
		"gc": map[string]interface{}{
			"status":   "healthy",
			"num_gc":   memStats.NumGC,
			"last_gc":  time.Unix(0, int64(memStats.LastGC)),
		},
	}

	return components
}

// getMemoryHealth returns memory health status
func (mc *MetricsCollector) getMemoryHealth(memStats runtime.MemStats) string {
	memoryUsageMB := float64(memStats.Alloc) / 1024 / 1024
	if memoryUsageMB > 2000 {
		return "critical"
	} else if memoryUsageMB > 1000 {
		return "warning"
	}
	return "healthy"
}

// getGoroutineHealth returns goroutine health status
func (mc *MetricsCollector) getGoroutineHealth() string {
	count := runtime.NumGoroutine()
	if count > 2000 {
		return "critical"
	} else if count > 1000 {
		return "warning"
	}
	return "healthy"
}

// GetAlerts returns current alerts
func (mc *MetricsCollector) GetAlerts() []Alert {
	mc.mu.RLock()
	defer mc.mu.RUnlock()
	
	// Create a copy to avoid race conditions
	alerts := make([]Alert, len(mc.alerts))
	copy(alerts, mc.alerts)
	return alerts
}

// ClearResolvedAlerts clears all resolved alerts
func (mc *MetricsCollector) ClearResolvedAlerts() {
	mc.mu.Lock()
	defer mc.mu.Unlock()

	filteredAlerts := make([]Alert, 0)
	for _, alert := range mc.alerts {
		if alert.Status != AlertStatusResolved {
			filteredAlerts = append(filteredAlerts, alert)
		}
	}

	mc.alerts = filteredAlerts
}