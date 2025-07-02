package observability

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/cluster"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/go-redis/redis/v8"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// DistributedMetrics manages metrics collection across the cluster
type DistributedMetrics struct {
	nodeID              string
	redisClient         *redis.Client
	logger              logging.Logger
	clusterManager      *cluster.ClusterManager
	ctx                 context.Context
	cancel              context.CancelFunc
	localMetrics        map[string]*MetricValue
	clusterMetrics      map[string]*ClusterMetric
	metricsMutex        sync.RWMutex
	prometheusMetrics   *PrometheusMetrics
	alertManager        *AlertManager
	traceCollector      *DistributedTraceCollector
	metricsCollectors   map[string]MetricsCollector
	collectorsMutex     sync.RWMutex
}

// MetricValue represents a single metric value
type MetricValue struct {
	Name      string                 `json:"name"`
	Value     float64                `json:"value"`
	Labels    map[string]string      `json:"labels"`
	Timestamp time.Time              `json:"timestamp"`
	NodeID    string                 `json:"node_id"`
	Type      MetricType             `json:"type"`
	Metadata  map[string]interface{} `json:"metadata"`
}

// ClusterMetric represents aggregated metrics across the cluster
type ClusterMetric struct {
	Name      string                   `json:"name"`
	Values    map[string]*MetricValue  `json:"values"` // NodeID -> MetricValue
	Aggregate *AggregatedValue         `json:"aggregate"`
	LastUpdated time.Time              `json:"last_updated"`
}

// AggregatedValue contains aggregated metric calculations
type AggregatedValue struct {
	Sum     float64 `json:"sum"`
	Average float64 `json:"average"`
	Min     float64 `json:"min"`
	Max     float64 `json:"max"`
	Count   int     `json:"count"`
}

// MetricType defines the type of metric
type MetricType string

const (
	MetricTypeCounter   MetricType = "counter"
	MetricTypeGauge     MetricType = "gauge"
	MetricTypeHistogram MetricType = "histogram"
	MetricTypeSummary   MetricType = "summary"
)

// PrometheusMetrics contains Prometheus metric definitions
type PrometheusMetrics struct {
	// Cluster metrics
	ClusterNodes          prometheus.Gauge
	ClusterNodesOnline    prometheus.Gauge
	ClusterTotalJobs      prometheus.Counter
	ClusterCompletedJobs  prometheus.Counter
	ClusterFailedJobs     prometheus.Counter
	
	// Node metrics
	NodeActiveJobs        prometheus.Gauge
	NodeMemoryUsage       prometheus.Gauge
	NodeCPUUsage          prometheus.Gauge
	NodeNetworkBytes      prometheus.Counter
	
	// Service metrics
	ServiceRequests       prometheus.Counter
	ServiceResponseTime   prometheus.Histogram
	ServiceErrors         prometheus.Counter
	
	// Agent metrics
	AgentConnections      prometheus.Gauge
	AgentMessages         prometheus.Counter
	AgentMessageErrors    prometheus.Counter
}

// AlertRule defines conditions for triggering alerts
type AlertRule struct {
	Name        string            `json:"name"`
	MetricName  string            `json:"metric_name"`
	Condition   AlertCondition    `json:"condition"`
	Threshold   float64           `json:"threshold"`
	Duration    time.Duration     `json:"duration"`
	Labels      map[string]string `json:"labels"`
	Annotations map[string]string `json:"annotations"`
	Enabled     bool              `json:"enabled"`
}

// AlertCondition defines the condition for an alert
type AlertCondition string

const (
	AlertConditionGreaterThan AlertCondition = "greater_than"
	AlertConditionLessThan    AlertCondition = "less_than"
	AlertConditionEquals      AlertCondition = "equals"
	AlertConditionNotEquals   AlertCondition = "not_equals"
)

// Alert represents an active alert
type Alert struct {
	ID          string            `json:"id"`
	RuleName    string            `json:"rule_name"`
	MetricName  string            `json:"metric_name"`
	Value       float64           `json:"value"`
	Threshold   float64           `json:"threshold"`
	Labels      map[string]string `json:"labels"`
	Annotations map[string]string `json:"annotations"`
	StartTime   time.Time         `json:"start_time"`
	Resolved    bool              `json:"resolved"`
	ResolvedAt  *time.Time        `json:"resolved_at,omitempty"`
}

// AlertManager manages alert rules and notifications
type AlertManager struct {
	rules       map[string]*AlertRule
	alerts      map[string]*Alert
	mutex       sync.RWMutex
	logger      logging.Logger
	redisClient *redis.Client
	ctx         context.Context
	cancel      context.CancelFunc
}

// MetricsCollector defines the interface for collecting metrics
type MetricsCollector interface {
	CollectMetrics(ctx context.Context) ([]*MetricValue, error)
	GetName() string
}

// DistributedTraceCollector manages distributed tracing
type DistributedTraceCollector struct {
	nodeID      string
	redisClient *redis.Client
	logger      logging.Logger
	traces      map[string]*DistributedTrace
	tracesMutex sync.RWMutex
	ctx         context.Context
	cancel      context.CancelFunc
}

// DistributedTrace represents a trace across multiple nodes
type DistributedTrace struct {
	TraceID   string                   `json:"trace_id"`
	Spans     map[string]*TraceSpan    `json:"spans"`
	StartTime time.Time                `json:"start_time"`
	EndTime   *time.Time               `json:"end_time,omitempty"`
	Duration  *time.Duration           `json:"duration,omitempty"`
	Tags      map[string]string        `json:"tags"`
}

// TraceSpan represents a single span in a distributed trace
type TraceSpan struct {
	SpanID    string                 `json:"span_id"`
	ParentID  string                 `json:"parent_id,omitempty"`
	NodeID    string                 `json:"node_id"`
	Operation string                 `json:"operation"`
	StartTime time.Time              `json:"start_time"`
	EndTime   *time.Time             `json:"end_time,omitempty"`
	Duration  *time.Duration         `json:"duration,omitempty"`
	Tags      map[string]string      `json:"tags"`
	Logs      []map[string]interface{} `json:"logs"`
	Error     bool                   `json:"error"`
}

// NewDistributedMetrics creates a new distributed metrics collector
func NewDistributedMetrics(
	nodeID string,
	redisClient *redis.Client,
	clusterManager *cluster.ClusterManager,
	logger logging.Logger,
) *DistributedMetrics {
	ctx, cancel := context.WithCancel(context.Background())

	dm := &DistributedMetrics{
		nodeID:              nodeID,
		redisClient:         redisClient,
		logger:              logger,
		clusterManager:      clusterManager,
		ctx:                 ctx,
		cancel:              cancel,
		localMetrics:        make(map[string]*MetricValue),
		clusterMetrics:      make(map[string]*ClusterMetric),
		prometheusMetrics:   initPrometheusMetrics(),
		alertManager:        NewAlertManager(redisClient, logger),
		traceCollector:      NewDistributedTraceCollector(nodeID, redisClient, logger),
		metricsCollectors:   make(map[string]MetricsCollector),
	}

	return dm
}

// Start starts the distributed metrics collection
func (dm *DistributedMetrics) Start() error {
	dm.logger.Info("Starting distributed metrics collection", logging.F("node_id", dm.nodeID))

	// Start metrics collection loop
	go dm.metricsCollectionLoop()

	// Start cluster metrics aggregation
	go dm.clusterAggregationLoop()

	// Start alert evaluation
	go dm.alertManager.Start(dm.ctx)

	// Start trace collection
	go dm.traceCollector.Start()

	dm.logger.Info("Distributed metrics collection started")
	return nil
}

// Stop stops the distributed metrics collection
func (dm *DistributedMetrics) Stop() error {
	dm.logger.Info("Stopping distributed metrics collection")

	dm.cancel()
	dm.traceCollector.Stop()

	dm.logger.Info("Distributed metrics collection stopped")
	return nil
}

// RegisterCollector registers a metrics collector
func (dm *DistributedMetrics) RegisterCollector(collector MetricsCollector) {
	dm.collectorsMutex.Lock()
	defer dm.collectorsMutex.Unlock()

	dm.metricsCollectors[collector.GetName()] = collector
	dm.logger.Info("Metrics collector registered", logging.F("collector", collector.GetName()))
}

// RecordMetric records a metric value
func (dm *DistributedMetrics) RecordMetric(name string, value float64, metricType MetricType, labels map[string]string) {
	metric := &MetricValue{
		Name:      name,
		Value:     value,
		Labels:    labels,
		Timestamp: time.Now(),
		NodeID:    dm.nodeID,
		Type:      metricType,
	}

	dm.metricsMutex.Lock()
	dm.localMetrics[name] = metric
	dm.metricsMutex.Unlock()

	// Update Prometheus metrics
	dm.updatePrometheusMetrics(metric)

	// Store in Redis for cluster aggregation
	dm.storeMetricInRedis(metric)
}

// GetClusterMetrics returns all cluster metrics
func (dm *DistributedMetrics) GetClusterMetrics() map[string]*ClusterMetric {
	dm.metricsMutex.RLock()
	defer dm.metricsMutex.RUnlock()

	metrics := make(map[string]*ClusterMetric)
	for name, metric := range dm.clusterMetrics {
		metrics[name] = metric
	}
	return metrics
}

// GetNodeMetrics returns metrics for a specific node
func (dm *DistributedMetrics) GetNodeMetrics(nodeID string) map[string]*MetricValue {
	dm.metricsMutex.RLock()
	defer dm.metricsMutex.RUnlock()

	metrics := make(map[string]*MetricValue)
	for _, clusterMetric := range dm.clusterMetrics {
		if nodeMetric, exists := clusterMetric.Values[nodeID]; exists {
			metrics[clusterMetric.Name] = nodeMetric
		}
	}
	return metrics
}

// metricsCollectionLoop collects metrics from registered collectors
func (dm *DistributedMetrics) metricsCollectionLoop() {
	ticker := time.NewTicker(15 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-dm.ctx.Done():
			return
		case <-ticker.C:
			dm.collectMetrics()
		}
	}
}

// collectMetrics collects metrics from all registered collectors
func (dm *DistributedMetrics) collectMetrics() {
	collectors := dm.getActiveCollectors()

	for _, collector := range collectors {
		metrics := dm.collectFromSingleCollector(collector)
		dm.processCollectedMetrics(metrics)
	}
}

// storeMetricInRedis stores a metric in Redis for cluster aggregation
func (dm *DistributedMetrics) storeMetricInRedis(metric *MetricValue) {
	metricData, err := json.Marshal(metric)
	if err != nil {
		dm.logger.Error("Failed to marshal metric", logging.F("error", err.Error()))
		return
	}

	key := fmt.Sprintf("metrics:%s:%s", dm.nodeID, metric.Name)
	err = dm.redisClient.Set(dm.ctx, key, metricData, 2*time.Minute).Err()
	if err != nil {
		dm.logger.Error("Failed to store metric in Redis", logging.F("error", err.Error()))
	}
}

// clusterAggregationLoop aggregates metrics from all cluster nodes
func (dm *DistributedMetrics) clusterAggregationLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-dm.ctx.Done():
			return
		case <-ticker.C:
			dm.aggregateClusterMetrics()
		}
	}
}

// aggregateClusterMetrics aggregates metrics from all nodes in the cluster
func (dm *DistributedMetrics) aggregateClusterMetrics() {
	keys, err := dm.redisClient.Keys(dm.ctx, "metrics:*").Result()
	if err != nil {
		dm.logger.Error("Failed to get metric keys", logging.F("error", err.Error()))
		return
	}

	clusterMetrics := make(map[string]*ClusterMetric)

	for _, key := range keys {
		metricData, err := dm.redisClient.Get(dm.ctx, key).Result()
		if err != nil {
			continue
		}

		var metric MetricValue
		if err := json.Unmarshal([]byte(metricData), &metric); err != nil {
			continue
		}

		// Skip old metrics
		if time.Since(metric.Timestamp) > 5*time.Minute {
			continue
		}

		clusterMetric, exists := clusterMetrics[metric.Name]
		if !exists {
			clusterMetric = &ClusterMetric{
				Name:        metric.Name,
				Values:      make(map[string]*MetricValue),
				LastUpdated: time.Now(),
			}
			clusterMetrics[metric.Name] = clusterMetric
		}

		clusterMetric.Values[metric.NodeID] = &metric
	}

	// Calculate aggregations
	for _, clusterMetric := range clusterMetrics {
		clusterMetric.Aggregate = dm.calculateAggregation(clusterMetric.Values)
		clusterMetric.LastUpdated = time.Now()
	}

	// Update local cluster metrics
	dm.metricsMutex.Lock()
	dm.clusterMetrics = clusterMetrics
	dm.metricsMutex.Unlock()

	// Update cluster-level Prometheus metrics
	dm.updateClusterPrometheusMetrics(clusterMetrics)

	// Evaluate alerts
	dm.alertManager.EvaluateAlerts(clusterMetrics)
}

// calculateAggregation calculates aggregated values for a set of metrics
func (dm *DistributedMetrics) calculateAggregation(values map[string]*MetricValue) *AggregatedValue {
	if len(values) == 0 {
		return &AggregatedValue{}
	}

	var sum, min, max float64
	count := 0
	first := true

	for _, value := range values {
		sum += value.Value
		count++

		if first {
			min = value.Value
			max = value.Value
			first = false
		} else {
			if value.Value < min {
				min = value.Value
			}
			if value.Value > max {
				max = value.Value
			}
		}
	}

	return &AggregatedValue{
		Sum:     sum,
		Average: sum / float64(count),
		Min:     min,
		Max:     max,
		Count:   count,
	}
}

// updatePrometheusMetrics updates Prometheus metrics
func (dm *DistributedMetrics) updatePrometheusMetrics(metric *MetricValue) {
	switch metric.Name {
	case "node_active_jobs":
		dm.prometheusMetrics.NodeActiveJobs.Set(metric.Value)
	case "node_memory_usage":
		dm.prometheusMetrics.NodeMemoryUsage.Set(metric.Value)
	case "node_cpu_usage":
		dm.prometheusMetrics.NodeCPUUsage.Set(metric.Value)
	case "agent_connections":
		dm.prometheusMetrics.AgentConnections.Set(metric.Value)
	}
}

// updateClusterPrometheusMetrics updates cluster-level Prometheus metrics
func (dm *DistributedMetrics) updateClusterPrometheusMetrics(metrics map[string]*ClusterMetric) {
	if clusterNodes, exists := metrics["cluster_nodes"]; exists && clusterNodes.Aggregate != nil {
		dm.prometheusMetrics.ClusterNodes.Set(clusterNodes.Aggregate.Sum)
	}

	if onlineNodes, exists := metrics["cluster_nodes_online"]; exists && onlineNodes.Aggregate != nil {
		dm.prometheusMetrics.ClusterNodesOnline.Set(onlineNodes.Aggregate.Sum)
	}
}

// initPrometheusMetrics initializes Prometheus metrics
func initPrometheusMetrics() *PrometheusMetrics {
	return &PrometheusMetrics{
		ClusterNodes: promauto.NewGauge(prometheus.GaugeOpts{
			Name: "flext_cluster_nodes_total",
			Help: "Total number of nodes in the cluster",
		}),
		ClusterNodesOnline: promauto.NewGauge(prometheus.GaugeOpts{
			Name: "flext_cluster_nodes_online",
			Help: "Number of online nodes in the cluster",
		}),
		ClusterTotalJobs: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_cluster_jobs_total",
			Help: "Total number of jobs submitted to the cluster",
		}),
		ClusterCompletedJobs: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_cluster_jobs_completed_total",
			Help: "Total number of completed jobs in the cluster",
		}),
		ClusterFailedJobs: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_cluster_jobs_failed_total",
			Help: "Total number of failed jobs in the cluster",
		}),
		NodeActiveJobs: promauto.NewGauge(prometheus.GaugeOpts{
			Name: "flext_node_active_jobs",
			Help: "Number of active jobs on this node",
		}),
		NodeMemoryUsage: promauto.NewGauge(prometheus.GaugeOpts{
			Name: "flext_node_memory_usage_bytes",
			Help: "Memory usage of this node in bytes",
		}),
		NodeCPUUsage: promauto.NewGauge(prometheus.GaugeOpts{
			Name: "flext_node_cpu_usage_percent",
			Help: "CPU usage of this node as a percentage",
		}),
		NodeNetworkBytes: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_node_network_bytes_total",
			Help: "Total network bytes transferred by this node",
		}),
		ServiceRequests: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_service_requests_total",
			Help: "Total number of service requests",
		}),
		ServiceResponseTime: promauto.NewHistogram(prometheus.HistogramOpts{
			Name: "flext_service_response_time_seconds",
			Help: "Service response time in seconds",
		}),
		ServiceErrors: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_service_errors_total",
			Help: "Total number of service errors",
		}),
		AgentConnections: promauto.NewGauge(prometheus.GaugeOpts{
			Name: "flext_agent_connections",
			Help: "Number of active agent connections",
		}),
		AgentMessages: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_agent_messages_total",
			Help: "Total number of agent messages",
		}),
		AgentMessageErrors: promauto.NewCounter(prometheus.CounterOpts{
			Name: "flext_agent_message_errors_total",
			Help: "Total number of agent message errors",
		}),
	}
}

// NewAlertManager creates a new alert manager
func NewAlertManager(redisClient *redis.Client, logger logging.Logger) *AlertManager {
	ctx, cancel := context.WithCancel(context.Background())
	// Note: cancel will be called when AlertManager is stopped

	return &AlertManager{
		rules:       make(map[string]*AlertRule),
		alerts:      make(map[string]*Alert),
		logger:      logger,
		redisClient: redisClient,
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start starts the alert manager
func (am *AlertManager) Start(ctx context.Context) error {
	// Load alert rules from Redis
	am.loadAlertRules()

	// Start alert evaluation loop
	go am.alertEvaluationLoop(ctx)

	return nil
}

// AddAlertRule adds a new alert rule
func (am *AlertManager) AddAlertRule(rule *AlertRule) {
	am.mutex.Lock()
	defer am.mutex.Unlock()

	am.rules[rule.Name] = rule
	am.logger.Info("Alert rule added", logging.F("rule_name", rule.Name))
}

// EvaluateAlerts evaluates all alert rules against current metrics
func (am *AlertManager) EvaluateAlerts(metrics map[string]*ClusterMetric) {
	am.mutex.RLock()
	rules := make([]*AlertRule, 0, len(am.rules))
	for _, rule := range am.rules {
		if rule.Enabled {
			rules = append(rules, rule)
		}
	}
	am.mutex.RUnlock()

	for _, rule := range rules {
		am.evaluateRule(rule, metrics)
	}
}

// evaluateRule evaluates a single alert rule
func (am *AlertManager) evaluateRule(rule *AlertRule, metrics map[string]*ClusterMetric) {
	metric, exists := metrics[rule.MetricName]
	if !exists || metric.Aggregate == nil {
		return
	}

	value := metric.Aggregate.Average // Use average for cluster metrics
	triggered := false

	switch rule.Condition {
	case AlertConditionGreaterThan:
		triggered = value > rule.Threshold
	case AlertConditionLessThan:
		triggered = value < rule.Threshold
	case AlertConditionEquals:
		triggered = value == rule.Threshold
	case AlertConditionNotEquals:
		triggered = value != rule.Threshold
	}

	alertID := fmt.Sprintf("%s-%s", rule.Name, rule.MetricName)

	am.mutex.Lock()
	existingAlert, alertExists := am.alerts[alertID]
	am.mutex.Unlock()

	if triggered && !alertExists {
		// Create new alert
		alert := &Alert{
			ID:          alertID,
			RuleName:    rule.Name,
			MetricName:  rule.MetricName,
			Value:       value,
			Threshold:   rule.Threshold,
			Labels:      rule.Labels,
			Annotations: rule.Annotations,
			StartTime:   time.Now(),
			Resolved:    false,
		}

		am.mutex.Lock()
		am.alerts[alertID] = alert
		am.mutex.Unlock()

		am.logger.Warn("Alert triggered",
			logging.F("rule_name", rule.Name),
			logging.F("metric_name", rule.MetricName),
			logging.F("value", value),
			logging.F("threshold", rule.Threshold),
		)

	} else if !triggered && alertExists && !existingAlert.Resolved {
		// Resolve alert
		now := time.Now()
		existingAlert.Resolved = true
		existingAlert.ResolvedAt = &now

		am.logger.Info("Alert resolved",
			logging.F("rule_name", rule.Name),
			logging.F("metric_name", rule.MetricName),
		)
	}
}

// loadAlertRules loads alert rules from Redis
func (am *AlertManager) loadAlertRules() {
	// Implementation for loading rules from Redis
	// This would typically load predefined alert rules
}

// alertEvaluationLoop runs the alert evaluation loop
func (am *AlertManager) alertEvaluationLoop(ctx context.Context) {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			// Cleanup resolved alerts older than 1 hour
			am.cleanupOldAlerts()
		}
	}
}

// cleanupOldAlerts removes old resolved alerts
func (am *AlertManager) cleanupOldAlerts() {
	am.mutex.Lock()
	defer am.mutex.Unlock()

	threshold := time.Now().Add(-1 * time.Hour)
	for id, alert := range am.alerts {
		if alert.Resolved && alert.ResolvedAt != nil && alert.ResolvedAt.Before(threshold) {
			delete(am.alerts, id)
		}
	}
}

// NewDistributedTraceCollector creates a new distributed trace collector
func NewDistributedTraceCollector(nodeID string, redisClient *redis.Client, logger logging.Logger) *DistributedTraceCollector {
	ctx, cancel := context.WithCancel(context.Background())
	// Note: cancel will be called when TraceCollector is stopped

	return &DistributedTraceCollector{
		nodeID:      nodeID,
		redisClient: redisClient,
		logger:      logger,
		traces:      make(map[string]*DistributedTrace),
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start starts the trace collector
func (dtc *DistributedTraceCollector) Start() error {
	go dtc.traceCollectionLoop()
	return nil
}

// Stop stops the trace collector (using context cancellation)
func (dtc *DistributedTraceCollector) Stop() error {
	if dtc.cancel != nil {
		dtc.cancel()
	}
	return nil
}

// StartTrace starts a new distributed trace
func (dtc *DistributedTraceCollector) StartTrace(traceID string, tags map[string]string) *DistributedTrace {
	trace := &DistributedTrace{
		TraceID:   traceID,
		Spans:     make(map[string]*TraceSpan),
		StartTime: time.Now(),
		Tags:      tags,
	}

	dtc.tracesMutex.Lock()
	dtc.traces[traceID] = trace
	dtc.tracesMutex.Unlock()

	return trace
}

// AddSpan adds a span to a trace
func (dtc *DistributedTraceCollector) AddSpan(traceID, spanID, parentID, operation string, tags map[string]string) *TraceSpan {
	span := &TraceSpan{
		SpanID:    spanID,
		ParentID:  parentID,
		NodeID:    dtc.nodeID,
		Operation: operation,
		StartTime: time.Now(),
		Tags:      tags,
		Logs:      make([]map[string]interface{}, 0),
	}

	dtc.tracesMutex.Lock()
	if trace, exists := dtc.traces[traceID]; exists {
		trace.Spans[spanID] = span
	}
	dtc.tracesMutex.Unlock()

	return span
}

// traceCollectionLoop collects traces from Redis
func (dtc *DistributedTraceCollector) traceCollectionLoop() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-dtc.ctx.Done():
			return
		case <-ticker.C:
			dtc.collectTracesFromRedis()
		}
	}
}

// collectTracesFromRedis collects traces from other nodes
func (dtc *DistributedTraceCollector) collectTracesFromRedis() {
	// Implementation for collecting traces from Redis
	// This would aggregate spans from different nodes into complete traces
}

// Stop gracefully shuts down the AlertManager
func (am *AlertManager) Stop() {
	if am.cancel != nil {
		am.cancel()
	}
}

// Helper methods for collectMetrics

func (dm *DistributedMetrics) getActiveCollectors() []MetricsCollector {
	dm.collectorsMutex.RLock()
	defer dm.collectorsMutex.RUnlock()
	
	collectors := make([]MetricsCollector, 0, len(dm.metricsCollectors))
	for _, collector := range dm.metricsCollectors {
		collectors = append(collectors, collector)
	}
	return collectors
}

func (dm *DistributedMetrics) collectFromSingleCollector(collector MetricsCollector) []*MetricValue {
	ctx, cancel := context.WithTimeout(dm.ctx, 10*time.Second)
	defer cancel()
	
	metrics, err := collector.CollectMetrics(ctx)
	if err != nil {
		dm.logger.Error("Failed to collect metrics",
			logging.F("collector", collector.GetName()),
			logging.F("error", err.Error()),
		)
		return nil
	}
	
	return metrics
}

func (dm *DistributedMetrics) processCollectedMetrics(metrics []*MetricValue) {
	for _, metric := range metrics {
		dm.storeMetricLocally(metric)
		dm.updatePrometheusMetrics(metric)
		dm.storeMetricInRedis(metric)
	}
}

func (dm *DistributedMetrics) storeMetricLocally(metric *MetricValue) {
	dm.metricsMutex.Lock()
	dm.localMetrics[metric.Name] = metric
	dm.metricsMutex.Unlock()
}

