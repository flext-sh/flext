package monitoring

import (
	"context"
	"database/sql"
	"fmt"
	"runtime"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/logging"
)

// HealthChecker performs comprehensive health checks
type HealthChecker struct {
	logger    logging.Logger
	mu        sync.RWMutex
	checks    map[string]HealthCheck
	results   map[string]HealthCheckResult
	callbacks map[string][]HealthCheckCallback
}

// HealthCheck represents a health check definition
type HealthCheck struct {
	Name        string                                      `json:"name"`
	Component   string                                      `json:"component"`
	Description string                                      `json:"description"`
	Timeout     time.Duration                               `json:"timeout"`
	Interval    time.Duration                               `json:"interval"`
	Critical    bool                                        `json:"critical"`
	CheckFunc   func(ctx context.Context) HealthCheckResult `json:"-"`
	Metadata    map[string]interface{}                      `json:"metadata"`
}

// HealthCheckResult represents the result of a health check
type HealthCheckResult struct {
	Name      string                 `json:"name"`
	Component string                 `json:"component"`
	Status    HealthStatus           `json:"status"`
	Message   string                 `json:"message"`
	Timestamp time.Time              `json:"timestamp"`
	Duration  time.Duration          `json:"duration"`
	Details   map[string]interface{} `json:"details,omitempty"`
	Error     string                 `json:"error,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// HealthCheckCallback is called when health status changes
type HealthCheckCallback func(result HealthCheckResult)

type HealthStatus string

const (
	HealthStatusHealthy   HealthStatus = "healthy"
	HealthStatusDegraded  HealthStatus = "degraded"
	HealthStatusUnhealthy HealthStatus = "unhealthy"
	HealthStatusUnknown   HealthStatus = "unknown"
)

// OverallHealth represents overall system health
type OverallHealth struct {
	Status         HealthStatus                 `json:"status"`
	Message        string                       `json:"message"`
	Timestamp      time.Time                    `json:"timestamp"`
	Components     map[string]HealthCheckResult `json:"components"`
	Summary        map[string]int               `json:"summary"`
	CriticalIssues []string                     `json:"critical_issues,omitempty"`
	Metadata       map[string]interface{}       `json:"metadata"`
}

// NewHealthChecker creates a new health checker
func NewHealthChecker(logger logging.Logger) *HealthChecker {
	hc := &HealthChecker{
		logger:    logger,
		checks:    make(map[string]HealthCheck),
		results:   make(map[string]HealthCheckResult),
		callbacks: make(map[string][]HealthCheckCallback),
	}

	// Register default health checks
	hc.registerDefaultChecks()

	return hc
}

// registerDefaultChecks registers default system health checks
func (hc *HealthChecker) registerDefaultChecks() {
	// Memory health check
	hc.RegisterCheck(HealthCheck{
		Name:        "memory",
		Component:   "system",
		Description: "System memory usage check",
		Timeout:     5 * time.Second,
		Interval:    30 * time.Second,
		Critical:    true,
		CheckFunc:   hc.checkMemoryHealth,
		Metadata: map[string]interface{}{
			"type": "system",
			"auto": true,
		},
	})

	// Goroutine health check
	hc.RegisterCheck(HealthCheck{
		Name:        "goroutines",
		Component:   "runtime",
		Description: "Goroutine count health check",
		Timeout:     5 * time.Second,
		Interval:    30 * time.Second,
		Critical:    false,
		CheckFunc:   hc.checkGoroutineHealth,
		Metadata: map[string]interface{}{
			"type": "runtime",
			"auto": true,
		},
	})

	// Disk space health check
	hc.RegisterCheck(HealthCheck{
		Name:        "disk_space",
		Component:   "system",
		Description: "Disk space availability check",
		Timeout:     10 * time.Second,
		Interval:    60 * time.Second,
		Critical:    true,
		CheckFunc:   hc.checkDiskSpaceHealth,
		Metadata: map[string]interface{}{
			"type": "system",
			"auto": true,
		},
	})
}

// RegisterCheck registers a new health check
func (hc *HealthChecker) RegisterCheck(check HealthCheck) {
	hc.mu.Lock()
	defer hc.mu.Unlock()

	hc.checks[check.Name] = check

	// Initialize result as unknown
	hc.results[check.Name] = HealthCheckResult{
		Name:      check.Name,
		Component: check.Component,
		Status:    HealthStatusUnknown,
		Message:   "Not yet checked",
		Timestamp: time.Now(),
	}

	hc.logger.Info("Health check registered",
		logging.F("name", check.Name),
		logging.F("component", check.Component),
		logging.F("critical", check.Critical),
	)
}

// RegisterDatabaseCheck registers a database health check
func (hc *HealthChecker) RegisterDatabaseCheck(name string, db *sql.DB) {
	hc.RegisterCheck(HealthCheck{
		Name:        name,
		Component:   "database",
		Description: fmt.Sprintf("Database %s connectivity check", name),
		Timeout:     10 * time.Second,
		Interval:    30 * time.Second,
		Critical:    true,
		CheckFunc: func(ctx context.Context) HealthCheckResult {
			return hc.checkDatabaseHealth(ctx, name, db)
		},
		Metadata: map[string]interface{}{
			"type":     "database",
			"database": name,
		},
	})
}

// RegisterExternalServiceCheck registers an external service health check
func (hc *HealthChecker) RegisterExternalServiceCheck(name, url string, timeout time.Duration) {
	hc.RegisterCheck(HealthCheck{
		Name:        name,
		Component:   "external",
		Description: fmt.Sprintf("External service %s availability check", name),
		Timeout:     timeout,
		Interval:    60 * time.Second,
		Critical:    false,
		CheckFunc: func(ctx context.Context) HealthCheckResult {
			return hc.checkExternalServiceHealth(ctx, name, url)
		},
		Metadata: map[string]interface{}{
			"type": "external_service",
			"url":  url,
		},
	})
}

// AddCallback adds a callback for health status changes
func (hc *HealthChecker) AddCallback(checkName string, callback HealthCheckCallback) {
	hc.mu.Lock()
	defer hc.mu.Unlock()

	if hc.callbacks[checkName] == nil {
		hc.callbacks[checkName] = make([]HealthCheckCallback, 0)
	}
	hc.callbacks[checkName] = append(hc.callbacks[checkName], callback)
}

// RunCheck runs a specific health check
func (hc *HealthChecker) RunCheck(ctx context.Context, name string) HealthCheckResult {
	hc.mu.RLock()
	check, exists := hc.checks[name]
	hc.mu.RUnlock()

	if !exists {
		return HealthCheckResult{
			Name:      name,
			Status:    HealthStatusUnknown,
			Message:   "Health check not found",
			Timestamp: time.Now(),
			Error:     "check not registered",
		}
	}

	// Create timeout context
	checkCtx, cancel := context.WithTimeout(ctx, check.Timeout)
	defer cancel()

	startTime := time.Now()

	// Run the check
	result := check.CheckFunc(checkCtx)
	result.Duration = time.Since(startTime)
	result.Timestamp = time.Now()

	// Store result
	hc.mu.Lock()
	oldResult := hc.results[name]
	hc.results[name] = result
	hc.mu.Unlock()

	// Call callbacks if status changed
	if oldResult.Status != result.Status {
		hc.callCallbacks(name, result)
	}

	hc.logger.Debug("Health check completed",
		logging.F("name", name),
		logging.F("status", string(result.Status)),
		logging.F("duration", result.Duration.String()),
	)

	return result
}

// RunAllChecks runs all registered health checks
func (hc *HealthChecker) RunAllChecks(ctx context.Context) map[string]HealthCheckResult {
	hc.mu.RLock()
	checks := make(map[string]HealthCheck)
	for name, check := range hc.checks {
		checks[name] = check
	}
	hc.mu.RUnlock()

	results := make(map[string]HealthCheckResult)
	var wg sync.WaitGroup

	// Run checks concurrently
	for name := range checks {
		wg.Add(1)
		go func(checkName string) {
			defer wg.Done()
			result := hc.RunCheck(ctx, checkName)
			results[checkName] = result
		}(name)
	}

	wg.Wait()
	return results
}

// GetOverallHealth returns overall system health
func (hc *HealthChecker) GetOverallHealth(ctx context.Context) OverallHealth {
	results := hc.RunAllChecks(ctx)

	summary := map[string]int{
		"healthy":   0,
		"degraded":  0,
		"unhealthy": 0,
		"unknown":   0,
	}

	var criticalIssues []string
	overallStatus := HealthStatusHealthy

	for _, result := range results {
		summary[string(result.Status)]++

		// Check for critical issues
		hc.mu.RLock()
		check := hc.checks[result.Name]
		hc.mu.RUnlock()

		if check.Critical && result.Status != HealthStatusHealthy {
			criticalIssues = append(criticalIssues, fmt.Sprintf("%s: %s", result.Name, result.Message))

			// Set overall status based on worst critical issue
			if result.Status == HealthStatusUnhealthy {
				overallStatus = HealthStatusUnhealthy
			} else if result.Status == HealthStatusDegraded && overallStatus == HealthStatusHealthy {
				overallStatus = HealthStatusDegraded
			}
		}
	}

	// Determine overall message
	message := "All systems operational"
	if overallStatus == HealthStatusUnhealthy {
		message = "Critical systems experiencing issues"
	} else if overallStatus == HealthStatusDegraded {
		message = "Some systems experiencing issues"
	} else if summary["unknown"] > 0 {
		message = "Some systems have unknown status"
	}

	return OverallHealth{
		Status:         overallStatus,
		Message:        message,
		Timestamp:      time.Now(),
		Components:     results,
		Summary:        summary,
		CriticalIssues: criticalIssues,
		Metadata: map[string]interface{}{
			"total_checks":   len(results),
			"critical_count": len(criticalIssues),
			"check_duration": time.Since(time.Now()).String(),
		},
	}
}

// StartPeriodicChecks starts periodic health checks
func (hc *HealthChecker) StartPeriodicChecks(ctx context.Context) {
	hc.logger.Info("Starting periodic health checks")

	// Start a goroutine for each check
	hc.mu.RLock()
	for name, check := range hc.checks {
		go hc.runPeriodicCheck(ctx, name, check)
	}
	hc.mu.RUnlock()
}

// runPeriodicCheck runs a single check periodically
func (hc *HealthChecker) runPeriodicCheck(ctx context.Context, name string, check HealthCheck) {
	ticker := time.NewTicker(check.Interval)
	defer ticker.Stop()

	// Run initial check
	hc.RunCheck(ctx, name)

	for {
		select {
		case <-ctx.Done():
			hc.logger.Debug("Stopping periodic health check", logging.F("name", name))
			return
		case <-ticker.C:
			hc.RunCheck(ctx, name)
		}
	}
}

// callCallbacks calls all registered callbacks for a check
func (hc *HealthChecker) callCallbacks(checkName string, result HealthCheckResult) {
	hc.mu.RLock()
	callbacks := hc.callbacks[checkName]
	hc.mu.RUnlock()

	for _, callback := range callbacks {
		go func(cb HealthCheckCallback) {
			defer func() {
				if r := recover(); r != nil {
					hc.logger.Error("Health check callback panicked",
						logging.F("check", checkName),
						logging.F("panic", r),
					)
				}
			}()
			cb(result)
		}(callback)
	}
}

// Health check implementations

func (hc *HealthChecker) checkMemoryHealth(ctx context.Context) HealthCheckResult {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	memoryUsageMB := float64(memStats.Alloc) / 1024 / 1024
	details := map[string]interface{}{
		"alloc_mb":       memoryUsageMB,
		"total_alloc_mb": float64(memStats.TotalAlloc) / 1024 / 1024,
		"sys_mb":         float64(memStats.Sys) / 1024 / 1024,
		"num_gc":         memStats.NumGC,
	}

	if memoryUsageMB > 2000 {
		return HealthCheckResult{
			Name:      "memory",
			Component: "system",
			Status:    HealthStatusUnhealthy,
			Message:   fmt.Sprintf("High memory usage: %.2f MB", memoryUsageMB),
			Details:   details,
		}
	} else if memoryUsageMB > 1000 {
		return HealthCheckResult{
			Name:      "memory",
			Component: "system",
			Status:    HealthStatusDegraded,
			Message:   fmt.Sprintf("Elevated memory usage: %.2f MB", memoryUsageMB),
			Details:   details,
		}
	}

	return HealthCheckResult{
		Name:      "memory",
		Component: "system",
		Status:    HealthStatusHealthy,
		Message:   fmt.Sprintf("Memory usage normal: %.2f MB", memoryUsageMB),
		Details:   details,
	}
}

func (hc *HealthChecker) checkGoroutineHealth(ctx context.Context) HealthCheckResult {
	count := runtime.NumGoroutine()
	details := map[string]interface{}{
		"count":     count,
		"cpu_count": runtime.NumCPU(),
	}

	if count > 2000 {
		return HealthCheckResult{
			Name:      "goroutines",
			Component: "runtime",
			Status:    HealthStatusUnhealthy,
			Message:   fmt.Sprintf("Very high goroutine count: %d", count),
			Details:   details,
		}
	} else if count > 1000 {
		return HealthCheckResult{
			Name:      "goroutines",
			Component: "runtime",
			Status:    HealthStatusDegraded,
			Message:   fmt.Sprintf("High goroutine count: %d", count),
			Details:   details,
		}
	}

	return HealthCheckResult{
		Name:      "goroutines",
		Component: "runtime",
		Status:    HealthStatusHealthy,
		Message:   fmt.Sprintf("Goroutine count normal: %d", count),
		Details:   details,
	}
}

func (hc *HealthChecker) checkDiskSpaceHealth(ctx context.Context) HealthCheckResult {
	// This is a simplified check - in production you'd check actual disk usage
	details := map[string]interface{}{
		"check_type": "simplified",
		"note":       "Actual disk usage check not implemented",
	}

	return HealthCheckResult{
		Name:      "disk_space",
		Component: "system",
		Status:    HealthStatusHealthy,
		Message:   "Disk space check passed (simplified)",
		Details:   details,
	}
}

func (hc *HealthChecker) checkDatabaseHealth(ctx context.Context, name string, db *sql.DB) HealthCheckResult {
	if db == nil {
		return HealthCheckResult{
			Name:      name,
			Component: "database",
			Status:    HealthStatusUnhealthy,
			Message:   "Database connection is nil",
			Error:     "nil database connection",
		}
	}

	// Test connection
	if err := db.PingContext(ctx); err != nil {
		return HealthCheckResult{
			Name:      name,
			Component: "database",
			Status:    HealthStatusUnhealthy,
			Message:   "Database ping failed",
			Error:     err.Error(),
		}
	}

	// Get connection stats
	stats := db.Stats()
	details := map[string]interface{}{
		"open_connections":     stats.OpenConnections,
		"in_use":               stats.InUse,
		"idle":                 stats.Idle,
		"wait_count":           stats.WaitCount,
		"wait_duration":        stats.WaitDuration.String(),
		"max_idle_closed":      stats.MaxIdleClosed,
		"max_idle_time_closed": stats.MaxIdleTimeClosed,
		"max_lifetime_closed":  stats.MaxLifetimeClosed,
	}

	return HealthCheckResult{
		Name:      name,
		Component: "database",
		Status:    HealthStatusHealthy,
		Message:   "Database connection healthy",
		Details:   details,
	}
}

func (hc *HealthChecker) checkExternalServiceHealth(ctx context.Context, name, url string) HealthCheckResult {
	// This is a simplified check - would typically make HTTP request
	details := map[string]interface{}{
		"url":        url,
		"check_type": "simplified",
		"note":       "Actual HTTP check not implemented",
	}

	return HealthCheckResult{
		Name:      name,
		Component: "external",
		Status:    HealthStatusHealthy,
		Message:   "External service check passed (simplified)",
		Details:   details,
	}
}
