package server

import (
	"context"
	"fmt"
	"runtime"
	"strings"
	"sync"
	"time"

	"github.com/labstack/echo/v4"
)

// MetricsCollector colete métricas do sistema
type MetricsCollector struct {
	mu sync.RWMutex

	// Request metrics
	totalRequests   int64
	requestDuration []time.Duration
	errorCount      int64

	// System metrics
	startTime       time.Time
	lastHealthCheck time.Time
	healthStatus    string

	// Performance metrics
	avgResponseTime time.Duration
	maxResponseTime time.Duration
	minResponseTime time.Duration
}

// NewMetricsCollector cria um novo coletor de métricas
func NewMetricsCollector() *MetricsCollector {
	return &MetricsCollector{
		startTime:       time.Now(),
		lastHealthCheck: time.Now(),
		healthStatus:    "healthy",
		minResponseTime: time.Hour, // Initialize with high value
	}
}

// RecordRequest registra uma requisição
func (mc *MetricsCollector) RecordRequest(duration time.Duration, hasError bool) {
	mc.mu.Lock()
	defer mc.mu.Unlock()

	mc.totalRequests++
	mc.requestDuration = append(mc.requestDuration, duration)

	if hasError {
		mc.errorCount++
	}

	// Update min/max response times
	if duration > mc.maxResponseTime {
		mc.maxResponseTime = duration
	}
	if duration < mc.minResponseTime {
		mc.minResponseTime = duration
	}

	// Calculate average (simple moving average of last 100 requests)
	if len(mc.requestDuration) > 100 {
		mc.requestDuration = mc.requestDuration[1:]
	}

	var total time.Duration
	for _, d := range mc.requestDuration {
		total += d
	}
	mc.avgResponseTime = total / time.Duration(len(mc.requestDuration))
}

// GetMetrics retorna métricas atuais
func (mc *MetricsCollector) GetMetrics() map[string]interface{} {
	mc.mu.RLock()
	defer mc.mu.RUnlock()

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	errorRate := float64(0)
	if mc.totalRequests > 0 {
		errorRate = float64(mc.errorCount) / float64(mc.totalRequests) * 100
	}

	return map[string]interface{}{
		"server": map[string]interface{}{
			"uptime":            time.Since(mc.startTime).String(),
			"version":           "1.0.0",
			"status":            mc.healthStatus,
			"last_health_check": mc.lastHealthCheck.Format(time.RFC3339),
		},
		"requests": map[string]interface{}{
			"total":             mc.totalRequests,
			"errors":            mc.errorCount,
			"error_rate":        errorRate,
			"avg_response_time": mc.avgResponseTime.String(),
			"max_response_time": mc.maxResponseTime.String(),
			"min_response_time": mc.minResponseTime.String(),
		},
		"system": map[string]interface{}{
			"memory": map[string]interface{}{
				"alloc":       memStats.Alloc,
				"total_alloc": memStats.TotalAlloc,
				"sys":         memStats.Sys,
				"heap_alloc":  memStats.HeapAlloc,
				"heap_sys":    memStats.HeapSys,
				"heap_idle":   memStats.HeapIdle,
				"heap_inuse":  memStats.HeapInuse,
				"stack_sys":   memStats.StackSys,
				"gc_runs":     memStats.NumGC,
			},
			"goroutines": runtime.NumGoroutine(),
			"cpu_count":  runtime.NumCPU(),
		},
	}
}

// PerformHealthCheck realiza verificação de saúde
func (mc *MetricsCollector) PerformHealthCheck(ctx context.Context) {
	mc.mu.Lock()
	defer mc.mu.Unlock()

	mc.lastHealthCheck = time.Now()

	// Simple health check logic
	if mc.errorCount > 0 && float64(mc.errorCount)/float64(mc.totalRequests) > 0.5 {
		mc.healthStatus = "degraded"
	} else if mc.avgResponseTime > 5*time.Second {
		mc.healthStatus = "slow"
	} else {
		mc.healthStatus = "healthy"
	}
}

// MetricsMiddleware middleware para coletar métricas
func (mc *MetricsCollector) MetricsMiddleware() echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			start := time.Now()

			err := next(c)

			duration := time.Since(start)
			hasError := err != nil || c.Response().Status >= 400

			mc.RecordRequest(duration, hasError)

			return err
		}
	}
}

// GetPrometheusMetrics retorna métricas no formato Prometheus
func (mc *MetricsCollector) GetPrometheusMetrics() string {
	mc.mu.RLock()
	defer mc.mu.RUnlock()

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	errorRate := float64(0)
	if mc.totalRequests > 0 {
		errorRate = float64(mc.errorCount) / float64(mc.totalRequests)
	}

	var builder strings.Builder

	// FLEXT specific metrics
	builder.WriteString("# HELP flext_requests_total Total number of requests processed\n")
	builder.WriteString("# TYPE flext_requests_total counter\n")
	builder.WriteString(fmt.Sprintf("flext_requests_total %d\n", mc.totalRequests))

	builder.WriteString("# HELP flext_errors_total Total number of errors\n")
	builder.WriteString("# TYPE flext_errors_total counter\n")
	builder.WriteString(fmt.Sprintf("flext_errors_total %d\n", mc.errorCount))

	builder.WriteString("# HELP flext_error_rate Error rate percentage\n")
	builder.WriteString("# TYPE flext_error_rate gauge\n")
	builder.WriteString(fmt.Sprintf("flext_error_rate %.4f\n", errorRate))

	builder.WriteString("# HELP flext_response_time_seconds Average response time in seconds\n")
	builder.WriteString("# TYPE flext_response_time_seconds gauge\n")
	builder.WriteString(fmt.Sprintf("flext_response_time_seconds %.6f\n", mc.avgResponseTime.Seconds()))

	builder.WriteString("# HELP flext_max_response_time_seconds Maximum response time in seconds\n")
	builder.WriteString("# TYPE flext_max_response_time_seconds gauge\n")
	builder.WriteString(fmt.Sprintf("flext_max_response_time_seconds %.6f\n", mc.maxResponseTime.Seconds()))

	builder.WriteString("# HELP flext_uptime_seconds Server uptime in seconds\n")
	builder.WriteString("# TYPE flext_uptime_seconds gauge\n")
	builder.WriteString(fmt.Sprintf("flext_uptime_seconds %.0f\n", time.Since(mc.startTime).Seconds()))

	// Go runtime metrics
	builder.WriteString("# HELP go_memstats_alloc_bytes Number of bytes allocated and still in use\n")
	builder.WriteString("# TYPE go_memstats_alloc_bytes gauge\n")
	builder.WriteString(fmt.Sprintf("go_memstats_alloc_bytes %d\n", memStats.Alloc))

	builder.WriteString("# HELP go_memstats_total_alloc_bytes Total number of bytes allocated\n")
	builder.WriteString("# TYPE go_memstats_total_alloc_bytes counter\n")
	builder.WriteString(fmt.Sprintf("go_memstats_total_alloc_bytes %d\n", memStats.TotalAlloc))

	builder.WriteString("# HELP go_memstats_sys_bytes Number of bytes obtained from system\n")
	builder.WriteString("# TYPE go_memstats_sys_bytes gauge\n")
	builder.WriteString(fmt.Sprintf("go_memstats_sys_bytes %d\n", memStats.Sys))

	builder.WriteString("# HELP go_memstats_heap_alloc_bytes Number of heap bytes allocated and still in use\n")
	builder.WriteString("# TYPE go_memstats_heap_alloc_bytes gauge\n")
	builder.WriteString(fmt.Sprintf("go_memstats_heap_alloc_bytes %d\n", memStats.HeapAlloc))

	builder.WriteString("# HELP go_goroutines Number of goroutines that currently exist\n")
	builder.WriteString("# TYPE go_goroutines gauge\n")
	builder.WriteString(fmt.Sprintf("go_goroutines %d\n", runtime.NumGoroutine()))

	builder.WriteString("# HELP process_cpu_count Number of CPUs\n")
	builder.WriteString("# TYPE process_cpu_count gauge\n")
	builder.WriteString(fmt.Sprintf("process_cpu_count %d\n", runtime.NumCPU()))

	return builder.String()
}
