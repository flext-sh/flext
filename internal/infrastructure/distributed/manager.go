package distributed

import (
	"context"
	"fmt"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/agent"
	"github.com/flext-sh/flext/internal/infrastructure/cluster"
	"github.com/flext-sh/flext/internal/infrastructure/coordination"
	"github.com/flext-sh/flext/internal/infrastructure/discovery"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/infrastructure/observability"
	"github.com/flext-sh/flext/internal/infrastructure/worker"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
)

// DistributedManager manages all distributed system components
type DistributedManager struct {
	nodeID            string
	config            *DistributedConfig
	logger            logging.Logger

	// Core components
	redisClient       *redis.Client
	clusterManager    *cluster.ClusterManager
	workerPool        *worker.WorkerPool
	remoteAgent       *agent.RemoteAgent
	coordinator       *coordination.Coordinator
	serviceRegistry   *discovery.ServiceRegistry
	loadBalancer      *discovery.LoadBalancer
	distributedMetrics *observability.DistributedMetrics

	// State
	started           bool
	ctx               context.Context
	cancel            context.CancelFunc
}

// DistributedConfig contains configuration for the distributed system
type DistributedConfig struct {
	// Node configuration
	NodeCapabilities []string          `json:"node_capabilities"`
	MaxJobs          int               `json:"max_jobs"`
	Metadata         map[string]string `json:"metadata"`

	// Redis configuration
	RedisAddress  string `json:"redis_address"`
	RedisPassword string `json:"redis_password"`
	RedisDB       int    `json:"redis_db"`

	// Worker pool configuration
	MaxWorkers   int `json:"max_workers"`
	MinWorkers   int `json:"min_workers"`
	QueueSize    int `json:"queue_size"`

	// Cluster configuration
	EnableClustering   bool `json:"enable_clustering"`
	EnableLoadBalancing bool `json:"enable_load_balancing"`
	EnableMetrics      bool `json:"enable_metrics"`

	// Service configuration
	ServiceName    string            `json:"service_name"`
	ServiceVersion string            `json:"service_version"`
	ServiceTags    []string          `json:"service_tags"`
	ServiceAddress string            `json:"service_address"`
	ServicePort    int               `json:"service_port"`
}

// NewDistributedManager creates a new distributed manager
func NewDistributedManager(config *DistributedConfig, logger logging.Logger) *DistributedManager {
	ctx, cancel := context.WithCancel(context.Background())
	
	nodeID := uuid.New().String()

	return &DistributedManager{
		nodeID: nodeID,
		config: config,
		logger: logger,
		ctx:    ctx,
		cancel: cancel,
	}
}

// Start starts all distributed system components
func (dm *DistributedManager) Start() error {
	dm.logger.Info("Starting distributed manager", logging.F("node_id", dm.nodeID))

	if dm.started {
		return fmt.Errorf("distributed manager already started")
	}

	// Initialize Redis client
	if err := dm.initRedisClient(); err != nil {
		return fmt.Errorf("failed to initialize Redis client: %w", err)
	}

	// Initialize worker pool
	if err := dm.initWorkerPool(); err != nil {
		return fmt.Errorf("failed to initialize worker pool: %w", err)
	}

	// Initialize cluster manager if clustering is enabled
	if dm.config.EnableClustering {
		if err := dm.initClusterManager(); err != nil {
			return fmt.Errorf("failed to initialize cluster manager: %w", err)
		}
	}

	// Initialize remote agent if clustering is enabled
	if dm.config.EnableClustering {
		if err := dm.initRemoteAgent(); err != nil {
			return fmt.Errorf("failed to initialize remote agent: %w", err)
		}
	}

	// Initialize coordinator if clustering is enabled
	if dm.config.EnableClustering {
		if err := dm.initCoordinator(); err != nil {
			return fmt.Errorf("failed to initialize coordinator: %w", err)
		}
	}

	// Initialize service registry and load balancer
	if err := dm.initServiceDiscovery(); err != nil {
		return fmt.Errorf("failed to initialize service discovery: %w", err)
	}

	// Initialize distributed metrics if enabled
	if dm.config.EnableMetrics {
		if err := dm.initDistributedMetrics(); err != nil {
			return fmt.Errorf("failed to initialize distributed metrics: %w", err)
		}
	}

	// Register this service
	if err := dm.registerService(); err != nil {
		return fmt.Errorf("failed to register service: %w", err)
	}

	dm.started = true
	dm.logger.Info("Distributed manager started successfully")

	return nil
}

// Stop stops all distributed system components
func (dm *DistributedManager) Stop() error {
	dm.logger.Info("Stopping distributed manager")

	if !dm.started {
		return nil
	}

	dm.cancel()

	// Stop components in reverse order
	if dm.distributedMetrics != nil {
		dm.distributedMetrics.Stop()
	}

	if dm.coordinator != nil {
		dm.coordinator.Stop()
	}

	if dm.remoteAgent != nil {
		dm.remoteAgent.Stop()
	}

	if dm.clusterManager != nil {
		dm.clusterManager.Stop()
	}

	if dm.serviceRegistry != nil {
		dm.serviceRegistry.Stop()
	}

	if dm.workerPool != nil {
		dm.workerPool.Stop()
	}

	if dm.redisClient != nil {
		dm.redisClient.Close()
	}

	dm.started = false
	dm.logger.Info("Distributed manager stopped")

	return nil
}

// initRedisClient initializes the Redis client
func (dm *DistributedManager) initRedisClient() error {
	dm.redisClient = redis.NewClient(&redis.Options{
		Addr:     dm.config.RedisAddress,
		Password: dm.config.RedisPassword,
		DB:       dm.config.RedisDB,
	})

	// Test connection
	ctx, cancel := context.WithTimeout(dm.ctx, 5*time.Second)
	defer cancel()

	_, err := dm.redisClient.Ping(ctx).Result()
	if err != nil {
		return fmt.Errorf("failed to connect to Redis: %w", err)
	}

	dm.logger.Info("Redis client initialized", logging.F("address", dm.config.RedisAddress))
	return nil
}

// initWorkerPool initializes the worker pool
func (dm *DistributedManager) initWorkerPool() error {
	dm.workerPool = worker.NewWorkerPool(
		dm.config.MaxWorkers,
		dm.config.MinWorkers,
		dm.config.QueueSize,
		dm.logger,
	)

	if err := dm.workerPool.Start(); err != nil {
		return fmt.Errorf("failed to start worker pool: %w", err)
	}

	dm.logger.Info("Worker pool initialized",
		logging.F("max_workers", dm.config.MaxWorkers),
		logging.F("min_workers", dm.config.MinWorkers),
		logging.F("queue_size", dm.config.QueueSize),
	)

	return nil
}

// initClusterManager initializes the cluster manager
func (dm *DistributedManager) initClusterManager() error {
	dm.clusterManager = cluster.NewClusterManager(
		dm.nodeID,
		dm.redisClient,
		dm.logger,
	)

	nodeInfo := &cluster.NodeInfo{
		ID:           dm.nodeID,
		Address:      dm.config.ServiceAddress,
		Port:         dm.config.ServicePort,
		Capabilities: dm.config.NodeCapabilities,
		Metadata:     dm.config.Metadata,
		MaxJobs:      dm.config.MaxJobs,
		ActiveJobs:   0,
		LoadFactor:   0.0,
	}

	if err := dm.clusterManager.Start(nodeInfo); err != nil {
		return fmt.Errorf("failed to start cluster manager: %w", err)
	}

	dm.logger.Info("Cluster manager initialized")
	return nil
}

// initRemoteAgent initializes the remote agent
func (dm *DistributedManager) initRemoteAgent() error {
	dm.remoteAgent = agent.NewRemoteAgent(
		dm.nodeID,
		dm.clusterManager,
		dm.workerPool,
		dm.logger,
	)

	if err := dm.remoteAgent.Start(); err != nil {
		return fmt.Errorf("failed to start remote agent: %w", err)
	}

	dm.logger.Info("Remote agent initialized")
	return nil
}

// initCoordinator initializes the coordinator
func (dm *DistributedManager) initCoordinator() error {
	dm.coordinator = coordination.NewCoordinator(
		dm.nodeID,
		dm.clusterManager,
		dm.remoteAgent,
		dm.workerPool,
		dm.redisClient,
		dm.logger,
	)

	if err := dm.coordinator.Start(); err != nil {
		return fmt.Errorf("failed to start coordinator: %w", err)
	}

	dm.logger.Info("Coordinator initialized")
	return nil
}

// initServiceDiscovery initializes service discovery and load balancing
func (dm *DistributedManager) initServiceDiscovery() error {
	dm.serviceRegistry = discovery.NewServiceRegistry(
		dm.nodeID,
		dm.redisClient,
		dm.logger,
	)

	if err := dm.serviceRegistry.Start(); err != nil {
		return fmt.Errorf("failed to start service registry: %w", err)
	}

	if dm.config.EnableLoadBalancing {
		dm.loadBalancer = discovery.NewLoadBalancer(
			dm.serviceRegistry,
			discovery.StrategyRoundRobin,
			dm.logger,
		)
	}

	dm.logger.Info("Service discovery initialized")
	return nil
}

// initDistributedMetrics initializes distributed metrics collection
func (dm *DistributedManager) initDistributedMetrics() error {
	dm.distributedMetrics = observability.NewDistributedMetrics(
		dm.nodeID,
		dm.redisClient,
		dm.clusterManager,
		dm.logger,
	)

	if err := dm.distributedMetrics.Start(); err != nil {
		return fmt.Errorf("failed to start distributed metrics: %w", err)
	}

	// Register system metrics collectors
	dm.registerMetricsCollectors()

	dm.logger.Info("Distributed metrics initialized")
	return nil
}

// registerService registers this service in the service registry
func (dm *DistributedManager) registerService() error {
	serviceInfo := &discovery.ServiceInfo{
		ID:       dm.nodeID,
		Name:     dm.config.ServiceName,
		Version:  dm.config.ServiceVersion,
		Address:  dm.config.ServiceAddress,
		Port:     dm.config.ServicePort,
		Protocol: "http",
		Health:   discovery.HealthStatusHealthy,
		Metadata: dm.config.Metadata,
		Tags:     dm.config.ServiceTags,
	}

	if err := dm.serviceRegistry.RegisterService(serviceInfo); err != nil {
		return fmt.Errorf("failed to register service: %w", err)
	}

	dm.logger.Info("Service registered",
		logging.F("service_name", dm.config.ServiceName),
		logging.F("service_id", dm.nodeID),
	)

	return nil
}

// registerMetricsCollectors registers system metrics collectors
func (dm *DistributedManager) registerMetricsCollectors() {
	// Register worker pool metrics collector
	workerPoolCollector := &WorkerPoolMetricsCollector{
		workerPool: dm.workerPool,
		nodeID:     dm.nodeID,
	}
	dm.distributedMetrics.RegisterCollector(workerPoolCollector)

	// Register cluster metrics collector if clustering is enabled
	if dm.clusterManager != nil {
		clusterCollector := &ClusterMetricsCollector{
			clusterManager: dm.clusterManager,
			nodeID:         dm.nodeID,
		}
		dm.distributedMetrics.RegisterCollector(clusterCollector)
	}

	// Register agent metrics collector if remote agent is enabled
	if dm.remoteAgent != nil {
		agentCollector := &AgentMetricsCollector{
			remoteAgent: dm.remoteAgent,
			nodeID:      dm.nodeID,
		}
		dm.distributedMetrics.RegisterCollector(agentCollector)
	}
}

// GetClusterManager returns the cluster manager
func (dm *DistributedManager) GetClusterManager() *cluster.ClusterManager {
	return dm.clusterManager
}

// GetWorkerPool returns the worker pool
func (dm *DistributedManager) GetWorkerPool() *worker.WorkerPool {
	return dm.workerPool
}

// GetRemoteAgent returns the remote agent
func (dm *DistributedManager) GetRemoteAgent() *agent.RemoteAgent {
	return dm.remoteAgent
}

// GetCoordinator returns the coordinator
func (dm *DistributedManager) GetCoordinator() *coordination.Coordinator {
	return dm.coordinator
}

// GetServiceRegistry returns the service registry
func (dm *DistributedManager) GetServiceRegistry() *discovery.ServiceRegistry {
	return dm.serviceRegistry
}

// GetLoadBalancer returns the load balancer
func (dm *DistributedManager) GetLoadBalancer() *discovery.LoadBalancer {
	return dm.loadBalancer
}

// GetDistributedMetrics returns the distributed metrics collector
func (dm *DistributedManager) GetDistributedMetrics() *observability.DistributedMetrics {
	return dm.distributedMetrics
}

// GetNodeID returns the node ID
func (dm *DistributedManager) GetNodeID() string {
	return dm.nodeID
}

// IsStarted returns true if the distributed manager is started
func (dm *DistributedManager) IsStarted() bool {
	return dm.started
}

// SubmitDistributedTask submits a task for distributed execution
func (dm *DistributedManager) SubmitDistributedTask(task *coordination.DistributedTask) error {
	if dm.coordinator == nil {
		return fmt.Errorf("coordinator not available")
	}

	return dm.coordinator.SubmitTask(task)
}

// RegisterTaskHandler registers a handler for distributed tasks
func (dm *DistributedManager) RegisterTaskHandler(taskType string, handler coordination.TaskHandler) error {
	if dm.coordinator == nil {
		return fmt.Errorf("coordinator not available")
	}

	dm.coordinator.RegisterTaskHandler(taskType, handler)
	return nil
}

// RegisterJobHandler registers a handler for worker pool jobs
func (dm *DistributedManager) RegisterJobHandler(jobType string, handler worker.JobHandler) error {
	if dm.workerPool == nil {
		return fmt.Errorf("worker pool not available")
	}

	dm.workerPool.RegisterHandler(jobType, handler)
	return nil
}

// GetServiceURL returns the URL for a service using load balancing
func (dm *DistributedManager) GetServiceURL(serviceName string) (string, error) {
	if dm.loadBalancer == nil {
		return "", fmt.Errorf("load balancer not available")
	}

	return dm.loadBalancer.GetServiceURL(serviceName)
}

// RecordMetric records a metric value
func (dm *DistributedManager) RecordMetric(name string, value float64, metricType observability.MetricType, labels map[string]string) {
	if dm.distributedMetrics != nil {
		dm.distributedMetrics.RecordMetric(name, value, metricType, labels)
	}
}

// WorkerPoolMetricsCollector collects metrics from the worker pool
type WorkerPoolMetricsCollector struct {
	workerPool *worker.WorkerPool
	nodeID     string
}

func (c *WorkerPoolMetricsCollector) CollectMetrics(ctx context.Context) ([]*observability.MetricValue, error) {
	metrics := c.workerPool.GetMetrics()
	
	return []*observability.MetricValue{
		{
			Name:      "worker_pool_active_workers",
			Value:     float64(metrics.ActiveWorkers),
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "worker_pool_active_jobs",
			Value:     float64(metrics.ActiveJobs),
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "worker_pool_total_jobs",
			Value:     float64(metrics.TotalJobs),
			Type:      observability.MetricTypeCounter,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "worker_pool_completed_jobs",
			Value:     float64(metrics.CompletedJobs),
			Type:      observability.MetricTypeCounter,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "worker_pool_failed_jobs",
			Value:     float64(metrics.FailedJobs),
			Type:      observability.MetricTypeCounter,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "worker_pool_queue_length",
			Value:     float64(metrics.QueueLength),
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "worker_pool_throughput_per_sec",
			Value:     metrics.ThroughputPerSec,
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
	}, nil
}

func (c *WorkerPoolMetricsCollector) GetName() string {
	return "worker_pool"
}

// ClusterMetricsCollector collects metrics from the cluster manager
type ClusterMetricsCollector struct {
	clusterManager *cluster.ClusterManager
	nodeID         string
}

func (c *ClusterMetricsCollector) CollectMetrics(ctx context.Context) ([]*observability.MetricValue, error) {
	nodes := c.clusterManager.GetNodes()
	onlineNodes := 0
	
	for _, node := range nodes {
		if node.Status == cluster.NodeStatusOnline {
			onlineNodes++
		}
	}

	return []*observability.MetricValue{
		{
			Name:      "cluster_nodes_total",
			Value:     float64(len(nodes)),
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "cluster_nodes_online",
			Value:     float64(onlineNodes),
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
		{
			Name:      "node_is_leader",
			Value:     func() float64 { if c.clusterManager.IsLeader() { return 1 } else { return 0 } }(),
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
	}, nil
}

func (c *ClusterMetricsCollector) GetName() string {
	return "cluster"
}

// AgentMetricsCollector collects metrics from the remote agent
type AgentMetricsCollector struct {
	remoteAgent *agent.RemoteAgent
	nodeID      string
}

func (c *AgentMetricsCollector) CollectMetrics(ctx context.Context) ([]*observability.MetricValue, error) {
	connections := c.remoteAgent.GetConnections()

	return []*observability.MetricValue{
		{
			Name:      "agent_connections",
			Value:     float64(len(connections)),
			Type:      observability.MetricTypeGauge,
			NodeID:    c.nodeID,
			Timestamp: time.Now(),
		},
	}, nil
}

func (c *AgentMetricsCollector) GetName() string {
	return "agent"
}