package monitoring

import (
	"context"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/google/uuid"
)

// Note: MetricsCollector is imported from metrics_collector.go

// RealtimeMonitor provides real-time monitoring capabilities
type RealtimeMonitor struct {
	websocketManager WebSocketBroadcaster
	logger           logging.Logger
	metrics          *MetricsCollector
	mu               sync.RWMutex
	
	// Current system state
	systemStats      *SystemStats
	pipelineStats    map[string]*PipelineStats
	performanceStats *PerformanceStats
	
	// Monitoring configuration
	updateInterval   time.Duration
	retentionPeriod  time.Duration
	
	// Control channels
	ctx              context.Context
	cancel           context.CancelFunc
}

// SystemStats represents current system statistics
type SystemStats struct {
	Timestamp        time.Time            `json:"timestamp"`
	TotalPipelines   int                  `json:"total_pipelines"`
	RunningPipelines int                  `json:"running_pipelines"`
	FailedPipelines  int                  `json:"failed_pipelines"`
	TotalPlugins     int                  `json:"total_plugins"`
	ActivePlugins    int                  `json:"active_plugins"`
	SystemHealth     string               `json:"system_health"`
	MemoryUsage      MemoryStats          `json:"memory_usage"`
	CPUUsage         float64              `json:"cpu_usage"`
	Uptime          time.Duration         `json:"uptime"`
	Version         string                `json:"version"`
}

// PipelineStats represents pipeline execution statistics
type PipelineStats struct {
	PipelineID       uuid.UUID            `json:"pipeline_id"`
	Name             string               `json:"name"`
	Status           string               `json:"status"`
	StartTime        time.Time            `json:"start_time"`
	EndTime          *time.Time           `json:"end_time,omitempty"`
	Duration         time.Duration        `json:"duration"`
	StepsCompleted   int                  `json:"steps_completed"`
	TotalSteps       int                  `json:"total_steps"`
	Progress         float64              `json:"progress"`
	CurrentStep      string               `json:"current_step"`
	ErrorMessage     string               `json:"error_message,omitempty"`
	Logs             []LogEntry           `json:"logs"`
	Metrics          map[string]float64   `json:"metrics"`
}

// PerformanceStats represents system performance metrics
type PerformanceStats struct {
	Timestamp        time.Time            `json:"timestamp"`
	RequestsPerSecond float64             `json:"requests_per_second"`
	ResponseTime     PerformanceMetrics   `json:"response_time"`
	ErrorRate        float64              `json:"error_rate"`
	ThroughputMBps   float64              `json:"throughput_mbps"`
	ActiveConnections int                 `json:"active_connections"`
	QueueDepth       int                  `json:"queue_depth"`
	CacheHitRate     float64              `json:"cache_hit_rate"`
}

// PerformanceMetrics represents timing metrics
type PerformanceMetrics struct {
	Average    time.Duration `json:"average"`
	Median     time.Duration `json:"median"`
	P95        time.Duration `json:"p95"`
	P99        time.Duration `json:"p99"`
	Min        time.Duration `json:"min"`
	Max        time.Duration `json:"max"`
}

// MemoryStats represents memory usage statistics
type MemoryStats struct {
	Allocated     uint64  `json:"allocated_mb"`
	TotalAlloc    uint64  `json:"total_alloc_mb"`
	System        uint64  `json:"system_mb"`
	UsagePercent  float64 `json:"usage_percent"`
	GCPauseTotal  uint64  `json:"gc_pause_total_ns"`
	GCPauseAvg    uint64  `json:"gc_pause_avg_ns"`
	NumGC         uint32  `json:"num_gc"`
}

// LogEntry represents a log entry for real-time display
type LogEntry struct {
	Timestamp time.Time `json:"timestamp"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
	Source    string    `json:"source"`
	Context   map[string]interface{} `json:"context,omitempty"`
}

// AlertInfo represents an active alert
type AlertInfo struct {
	ID          string    `json:"id"`
	Type        string    `json:"type"`
	Severity    string    `json:"severity"`
	Message     string    `json:"message"`
	Timestamp   time.Time `json:"timestamp"`
	Source      string    `json:"source"`
	Resolved    bool      `json:"resolved"`
	ResolvedAt  *time.Time `json:"resolved_at,omitempty"`
}

// NewRealtimeMonitor creates a new real-time monitor
func NewRealtimeMonitor(websocketManager WebSocketBroadcaster, logger logging.Logger) *RealtimeMonitor {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &RealtimeMonitor{
		websocketManager: websocketManager,
		logger:           logger,
		metrics:          &MetricsCollector{},
		pipelineStats:    make(map[string]*PipelineStats),
		updateInterval:   1 * time.Second,
		retentionPeriod:  24 * time.Hour,
		ctx:              ctx,
		cancel:           cancel,
		systemStats: &SystemStats{
			Version:     "2.0.0",
			SystemHealth: "healthy",
		},
		performanceStats: &PerformanceStats{},
	}
}

// Start begins real-time monitoring
func (rm *RealtimeMonitor) Start() error {
	rm.logger.Info("Starting real-time monitor")
	
	// Start monitoring goroutines
	go rm.systemStatsUpdater()
	go rm.performanceStatsUpdater()
	go rm.alertMonitor()
	
	rm.logger.Info("Real-time monitor started")
	return nil
}

// Stop stops real-time monitoring
func (rm *RealtimeMonitor) Stop() error {
	rm.logger.Info("Stopping real-time monitor")
	rm.cancel()
	return nil
}

// systemStatsUpdater periodically updates and broadcasts system statistics
func (rm *RealtimeMonitor) systemStatsUpdater() {
	ticker := time.NewTicker(rm.updateInterval)
	defer ticker.Stop()
	
	for {
		select {
		case <-rm.ctx.Done():
			return
		case <-ticker.C:
			rm.updateSystemStats()
			rm.broadcastSystemStats()
		}
	}
}

// performanceStatsUpdater periodically updates performance metrics
func (rm *RealtimeMonitor) performanceStatsUpdater() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-rm.ctx.Done():
			return
		case <-ticker.C:
			rm.updatePerformanceStats()
			rm.broadcastPerformanceStats()
		}
	}
}

// alertMonitor monitors for system alerts
func (rm *RealtimeMonitor) alertMonitor() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-rm.ctx.Done():
			return
		case <-ticker.C:
			rm.checkAlerts()
		}
	}
}

// updateSystemStats collects current system statistics
func (rm *RealtimeMonitor) updateSystemStats() {
	rm.mu.Lock()
	defer rm.mu.Unlock()
	
	// Update timestamp
	rm.systemStats.Timestamp = time.Now()
	
	// Update pipeline counts
	runningCount := 0
	failedCount := 0
	totalCount := len(rm.pipelineStats)
	
	for _, stats := range rm.pipelineStats {
		switch stats.Status {
		case "running":
			runningCount++
		case "failed":
			failedCount++
		}
	}
	
	rm.systemStats.TotalPipelines = totalCount
	rm.systemStats.RunningPipelines = runningCount
	rm.systemStats.FailedPipelines = failedCount
	
	// Update memory stats (simplified - in production would use runtime.MemStats)
	rm.systemStats.MemoryUsage = MemoryStats{
		Allocated:    64,  // MB
		TotalAlloc:   128, // MB
		System:       256, // MB
		UsagePercent: 25.0,
	}
	
	// Update CPU usage (simplified)
	rm.systemStats.CPUUsage = 15.5
	
	// Determine system health
	healthStatus := "healthy"
	if failedCount > totalCount/2 {
		healthStatus = "degraded"
	}
	if runningCount == 0 && totalCount > 0 {
		healthStatus = "critical"
	}
	rm.systemStats.SystemHealth = healthStatus
}

// updatePerformanceStats collects performance metrics
func (rm *RealtimeMonitor) updatePerformanceStats() {
	rm.mu.Lock()
	defer rm.mu.Unlock()
	
	rm.performanceStats.Timestamp = time.Now()
	
	// Simulate performance metrics (in production, these would come from actual metrics)
	rm.performanceStats.RequestsPerSecond = 150.5
	rm.performanceStats.ErrorRate = 0.02
	rm.performanceStats.ThroughputMBps = 45.2
	rm.performanceStats.ActiveConnections = 25
	rm.performanceStats.QueueDepth = 5
	rm.performanceStats.CacheHitRate = 0.85
	
	rm.performanceStats.ResponseTime = PerformanceMetrics{
		Average: 45 * time.Millisecond,
		Median:  35 * time.Millisecond,
		P95:     120 * time.Millisecond,
		P99:     250 * time.Millisecond,
		Min:     5 * time.Millisecond,
		Max:     500 * time.Millisecond,
	}
}

// checkAlerts monitors for system alerts
func (rm *RealtimeMonitor) checkAlerts() {
	// Check for high error rate
	if rm.performanceStats.ErrorRate > 0.05 {
		alert := AlertInfo{
			ID:        uuid.New().String(),
			Type:      "error_rate",
			Severity:  "warning",
			Message:   "High error rate detected",
			Timestamp: time.Now(),
			Source:    "performance_monitor",
		}
		rm.broadcastAlert(alert)
	}
	
	// Check for high memory usage
	if rm.systemStats.MemoryUsage.UsagePercent > 80.0 {
		alert := AlertInfo{
			ID:        uuid.New().String(),
			Type:      "memory_usage",
			Severity:  "critical",
			Message:   "High memory usage detected",
			Timestamp: time.Now(),
			Source:    "system_monitor",
		}
		rm.broadcastAlert(alert)
	}
	
	// Check for failed pipelines
	if rm.systemStats.FailedPipelines > 0 {
		alert := AlertInfo{
			ID:        uuid.New().String(),
			Type:      "pipeline_failures",
			Severity:  "warning",
			Message:   "Pipeline failures detected",
			Timestamp: time.Now(),
			Source:    "pipeline_monitor",
		}
		rm.broadcastAlert(alert)
	}
}

// broadcastSystemStats sends system stats to WebSocket subscribers
func (rm *RealtimeMonitor) broadcastSystemStats() {
	rm.websocketManager.BroadcastToTopic("system_stats", "system_update", rm.systemStats)
}

// broadcastPerformanceStats sends performance stats to WebSocket subscribers
func (rm *RealtimeMonitor) broadcastPerformanceStats() {
	rm.websocketManager.BroadcastToTopic("performance", "performance_update", rm.performanceStats)
}

// broadcastAlert sends an alert to WebSocket subscribers
func (rm *RealtimeMonitor) broadcastAlert(alert AlertInfo) {
	rm.websocketManager.BroadcastToTopic("alerts", "alert", alert)
	rm.logger.Warn("Alert triggered",
		logging.F("alert_type", alert.Type),
		logging.F("severity", alert.Severity),
		logging.F("message", alert.Message),
	)
}

// OnPipelineStarted handles pipeline start events
func (rm *RealtimeMonitor) OnPipelineStarted(pipelineID uuid.UUID, name string, totalSteps int) {
	rm.mu.Lock()
	defer rm.mu.Unlock()
	
	stats := &PipelineStats{
		PipelineID:     pipelineID,
		Name:           name,
		Status:         "running",
		StartTime:      time.Now(),
		StepsCompleted: 0,
		TotalSteps:     totalSteps,
		Progress:       0.0,
		CurrentStep:    "initializing",
		Logs:           make([]LogEntry, 0),
		Metrics:        make(map[string]float64),
	}
	
	rm.pipelineStats[pipelineID.String()] = stats
	
	// Broadcast pipeline start
	rm.websocketManager.BroadcastToTopic("pipelines", "pipeline_started", stats)
	
	rm.logger.Info("Pipeline started",
		logging.F("pipeline_id", pipelineID.String()),
		logging.F("name", name),
	)
}

// OnPipelineProgress handles pipeline progress updates
func (rm *RealtimeMonitor) OnPipelineProgress(pipelineID uuid.UUID, currentStep string, stepsCompleted int, progress float64) {
	rm.mu.Lock()
	defer rm.mu.Unlock()
	
	if stats, exists := rm.pipelineStats[pipelineID.String()]; exists {
		stats.CurrentStep = currentStep
		stats.StepsCompleted = stepsCompleted
		stats.Progress = progress
		
		// Broadcast progress update
		rm.websocketManager.BroadcastToTopic("pipelines", "pipeline_progress", stats)
	}
}

// OnPipelineCompleted handles pipeline completion events
func (rm *RealtimeMonitor) OnPipelineCompleted(pipelineID uuid.UUID, success bool, errorMessage string) {
	rm.mu.Lock()
	defer rm.mu.Unlock()
	
	if stats, exists := rm.pipelineStats[pipelineID.String()]; exists {
		endTime := time.Now()
		stats.EndTime = &endTime
		stats.Duration = endTime.Sub(stats.StartTime)
		
		if success {
			stats.Status = "completed"
			stats.Progress = 100.0
		} else {
			stats.Status = "failed"
			stats.ErrorMessage = errorMessage
		}
		
		// Broadcast completion
		rm.websocketManager.BroadcastToTopic("pipelines", "pipeline_completed", stats)
		
		rm.logger.Info("Pipeline completed",
			logging.F("pipeline_id", pipelineID.String()),
			logging.F("success", success),
			logging.F("duration", stats.Duration.String()),
		)
	}
}

// OnPipelineLog handles pipeline log events
func (rm *RealtimeMonitor) OnPipelineLog(pipelineID uuid.UUID, level, message, source string, context map[string]interface{}) {
	rm.mu.Lock()
	defer rm.mu.Unlock()
	
	if stats, exists := rm.pipelineStats[pipelineID.String()]; exists {
		logEntry := LogEntry{
			Timestamp: time.Now(),
			Level:     level,
			Message:   message,
			Source:    source,
			Context:   context,
		}
		
		// Keep only recent logs (last 100 entries)
		stats.Logs = append(stats.Logs, logEntry)
		if len(stats.Logs) > 100 {
			stats.Logs = stats.Logs[1:]
		}
		
		// Broadcast log entry
		logData := map[string]interface{}{
			"pipeline_id": pipelineID.String(),
			"log":         logEntry,
		}
		rm.websocketManager.BroadcastToTopic("pipeline_logs", "pipeline_log", logData)
	}
}

// GetSystemStats returns current system statistics
func (rm *RealtimeMonitor) GetSystemStats() *SystemStats {
	rm.mu.RLock()
	defer rm.mu.RUnlock()
	
	// Return a copy to avoid race conditions
	statsCopy := *rm.systemStats
	return &statsCopy
}

// GetPipelineStats returns statistics for a specific pipeline
func (rm *RealtimeMonitor) GetPipelineStats(pipelineID uuid.UUID) (*PipelineStats, bool) {
	rm.mu.RLock()
	defer rm.mu.RUnlock()
	
	stats, exists := rm.pipelineStats[pipelineID.String()]
	if !exists {
		return nil, false
	}
	
	// Return a copy
	statsCopy := *stats
	return &statsCopy, true
}

// GetAllPipelineStats returns statistics for all pipelines
func (rm *RealtimeMonitor) GetAllPipelineStats() map[string]*PipelineStats {
	rm.mu.RLock()
	defer rm.mu.RUnlock()
	
	result := make(map[string]*PipelineStats)
	for id, stats := range rm.pipelineStats {
		statsCopy := *stats
		result[id] = &statsCopy
	}
	
	return result
}

// GetPerformanceStats returns current performance statistics
func (rm *RealtimeMonitor) GetPerformanceStats() *PerformanceStats {
	rm.mu.RLock()
	defer rm.mu.RUnlock()
	
	statsCopy := *rm.performanceStats
	return &statsCopy
}

// CleanupOldStats removes old pipeline statistics
func (rm *RealtimeMonitor) CleanupOldStats() {
	rm.mu.Lock()
	defer rm.mu.Unlock()
	
	cutoff := time.Now().Add(-rm.retentionPeriod)
	
	for id, stats := range rm.pipelineStats {
		if stats.EndTime != nil && stats.EndTime.Before(cutoff) {
			delete(rm.pipelineStats, id)
		}
	}
}