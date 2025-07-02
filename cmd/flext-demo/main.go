package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/shared_kernel/application"
)

// DemoServer represents the demo server with its configuration
type DemoServer struct {
	nodeID      string
	clusterName string
	startTime   time.Time
	logger      logging.Logger
	config      *config.Config
	server      *http.Server
}

// NewDemoServer creates a new demo server instance
func NewDemoServer(nodeID, clusterName string, logger logging.Logger, config *config.Config) *DemoServer {
	return &DemoServer{
		nodeID:      nodeID,
		clusterName: clusterName,
		startTime:   time.Now(),
		logger:      logger,
		config:      config,
	}
}

// HealthResponse represents the health check response
type HealthResponse struct {
	Status    string            `json:"status"`
	Version   string            `json:"version"`
	Mode      string            `json:"mode"`
	Timestamp time.Time         `json:"timestamp"`
	Uptime    string            `json:"uptime"`
	Features  map[string]bool   `json:"features"`
	Env       map[string]string `json:"env"`
}

// ClusterStatus represents cluster information
type ClusterStatus struct {
	NodeID      string    `json:"node_id"`
	ClusterName string    `json:"cluster_name"`
	Role        string    `json:"role"`
	Status      string    `json:"status"`
	Nodes       []string  `json:"nodes"`
	Timestamp   time.Time `json:"timestamp"`
}

// MetricsResponse represents metrics information
type MetricsResponse struct {
	Requests       int64             `json:"requests_total"`
	Uptime         string            `json:"uptime"`
	Memory         map[string]string `json:"memory"`
	Cluster        ClusterStatus     `json:"cluster"`
	WorkerPool     map[string]int    `json:"worker_pool"`
	DistributedOps map[string]int64  `json:"distributed_operations"`
}

func main() {
	// Parse command line flags
	var (
		configPath = flag.String("config", "", "Path to configuration file")
		port       = flag.Int("port", 0, "Server port (overrides config)")
		nodeID     = flag.String("node-id", "", "Node ID for cluster identification")
		cluster    = flag.String("cluster", "", "Cluster name")
	)
	flag.Parse()

	// Create demo bootstrap
	bootstrap := application.NewAppBootstrap(application.AppTypeDemo, "flext-demo", "2.0.0")
	if *configPath != "" {
		bootstrap = bootstrap.WithConfigPath(*configPath)
	}

	// Initialize application
	appConfig, err := bootstrap.Initialize()
	if err != nil {
		fmt.Printf("Failed to initialize demo application: %v\n", err)
		os.Exit(1)
	}

	// Override configuration from flags and environment
	if *port > 0 {
		appConfig.Config.Server.Port = *port
	}

	nodeIDValue := getEnvOrFlag(*nodeID, "NODE_ID", "demo-node")
	clusterValue := getEnvOrFlag(*cluster, "CLUSTER_NAME", "flext-demo-cluster")

	// Log demo initialization
	appConfig.Logger.Info("Starting FLEXT Demo Server",
		logging.F("node_id", nodeIDValue),
		logging.F("cluster", clusterValue),
		logging.F("port", appConfig.Config.Server.Port),
		logging.F("version", "2.0.0-demo"))

	// Create demo server instance
	demoServer := NewDemoServer(nodeIDValue, clusterValue, appConfig.Logger, appConfig.Config)

	// Setup HTTP server and routes
	demoServer.setupServer()

	// Setup graceful shutdown
	shutdown := application.NewGracefulShutdownHandler(appConfig.Logger, appConfig.Config.Server.ShutdownTimeout)
	shutdown.AddShutdownFunc("demo-server", demoServer.Stop)

	// Start server
	go func() {
		addr := fmt.Sprintf(":%d", appConfig.Config.Server.Port)
		appConfig.Logger.Info("FLEXT Demo Server started",
			logging.F("address", addr),
			logging.F("mode", "demo"))
		if err := demoServer.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			appConfig.Logger.Error("Demo server failed to start", logging.F("error", err.Error()))
			os.Exit(1)
		}
	}()

	// Wait for shutdown
	shutdown.WaitForShutdown()
}

// setupServer configures the HTTP server and routes
func (ds *DemoServer) setupServer() {
	mux := http.NewServeMux()

	// Register all routes
	mux.HandleFunc("/", ds.handleRoot)
	mux.HandleFunc("/health", ds.handleHealth)
	mux.HandleFunc("/cluster/status", ds.handleClusterStatus)
	mux.HandleFunc("/metrics", ds.handleMetrics)
	mux.HandleFunc("/api/v1/pipelines", ds.handlePipelines)
	mux.HandleFunc("/api/v1/plugins", ds.handlePlugins)
	mux.HandleFunc("/worker/status", ds.handleWorkerStatus)
	mux.HandleFunc("/discovery/services", ds.handleDiscovery)

	// Create HTTP server
	ds.server = &http.Server{
		Addr:         fmt.Sprintf(":%d", ds.config.Server.Port),
		Handler:      mux,
		ReadTimeout:  ds.config.Server.ReadTimeout,
		WriteTimeout: ds.config.Server.WriteTimeout,
		IdleTimeout:  ds.config.Server.IdleTimeout,
	}
}

// Stop gracefully stops the server
func (ds *DemoServer) Stop(ctx context.Context) error {
	ds.logger.Info("Stopping demo server")
	return ds.server.Shutdown(ctx)
}

// handleRoot serves the API documentation
func (ds *DemoServer) handleRoot(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	apiInfo := map[string]interface{}{
		"name":        "FLEXT Distributed Demo API",
		"description": "Demonstration of FLEXT distributed clustering capabilities",
		"version":     "2.0.0-demo",
		"node_id":     ds.nodeID,
		"cluster":     ds.clusterName,
		"endpoints": map[string]interface{}{
			"health":         "GET /health",
			"cluster_status": "GET /cluster/status",
			"metrics":        "GET /metrics",
			"pipelines":      "GET /api/v1/pipelines",
			"plugins":        "GET /api/v1/plugins",
			"worker_status":  "GET /worker/status",
			"discovery":      "GET /discovery/services",
		},
		"features": []string{
			"Multi-node clustering",
			"Distributed coordination",
			"Load balancing",
			"Auto-scaling workers",
			"PostgreSQL integration",
			"Redis coordination",
			"Prometheus metrics",
			"Grafana monitoring",
			"Jaeger tracing",
		},
	}

	ds.logger.Debug("API info requested", logging.F("endpoint", "/"))
	json.NewEncoder(w).Encode(apiInfo)
}

// handleHealth serves health check information
func (ds *DemoServer) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	response := HealthResponse{
		Status:    "ok",
		Version:   "2.0.0-demo",
		Mode:      "distributed-demo",
		Timestamp: time.Now().UTC(),
		Uptime:    time.Since(ds.startTime).String(),
		Features: map[string]bool{
			"clustering":     true,
			"distributed":    true,
			"load_balancing": true,
			"auto_scaling":   true,
			"monitoring":     true,
			"database":       true,
		},
		Env: map[string]string{
			"node_id":      ds.nodeID,
			"cluster_name": ds.clusterName,
			"database":     os.Getenv("FLEXT_DB_URL"),
		},
	}

	ds.logger.Debug("Health check requested", logging.F("status", "ok"))
	json.NewEncoder(w).Encode(response)
}

// handleClusterStatus serves cluster information
func (ds *DemoServer) handleClusterStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	status := ClusterStatus{
		NodeID:      ds.nodeID,
		ClusterName: ds.clusterName,
		Role:        "worker",
		Status:      "active",
		Nodes: []string{
			"flext-node-1:8080",
			"flext-node-2:8080",
			"flext-node-3:8080",
		},
		Timestamp: time.Now().UTC(),
	}

	ds.logger.Debug("Cluster status requested", logging.F("cluster", ds.clusterName))
	json.NewEncoder(w).Encode(status)
}

// handleMetrics serves metrics information
func (ds *DemoServer) handleMetrics(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	metrics := MetricsResponse{
		Requests: 42,
		Uptime:   time.Since(ds.startTime).String(),
		Memory: map[string]string{
			"allocated": "25MB",
			"sys":       "45MB",
			"gc_cycles": "12",
		},
		Cluster: ClusterStatus{
			NodeID:      ds.nodeID,
			ClusterName: ds.clusterName,
			Role:        "worker",
			Status:      "active",
			Nodes: []string{
				"flext-node-1:8080",
				"flext-node-2:8080",
				"flext-node-3:8080",
			},
			Timestamp: time.Now().UTC(),
		},
		WorkerPool: map[string]int{
			"active_workers": 5,
			"max_workers":    10,
			"queue_size":     1000,
			"jobs_pending":   3,
		},
		DistributedOps: map[string]int64{
			"pipeline_executions":  127,
			"plugin_registrations": 15,
			"cluster_messages":     1052,
		},
	}

	ds.logger.Debug("Metrics requested")
	json.NewEncoder(w).Encode(metrics)
}

// handlePipelines serves pipelines information
func (ds *DemoServer) handlePipelines(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	pipelines := []map[string]interface{}{
		{
			"id":          "550e8400-e29b-41d4-a716-446655440001",
			"name":        "sample-etl-pipeline",
			"description": "Sample ETL pipeline for testing cluster functionality",
			"status":      "active",
			"tags":        []string{"etl", "test", "cluster"},
			"created_at":  time.Now().Add(-24 * time.Hour).Format(time.RFC3339),
			"node_id":     ds.nodeID,
		},
		{
			"id":          "550e8400-e29b-41d4-a716-446655440002",
			"name":        "data-sync-pipeline",
			"description": "Distributed data synchronization pipeline",
			"status":      "running",
			"tags":        []string{"sync", "distributed", "production"},
			"created_at":  time.Now().Add(-48 * time.Hour).Format(time.RFC3339),
			"node_id":     ds.nodeID,
		},
	}

	ds.logger.Debug("Pipelines list requested")
	json.NewEncoder(w).Encode(pipelines)
}

// handlePlugins serves plugins information
func (ds *DemoServer) handlePlugins(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	plugins := map[string]interface{}{
		"total":      15,
		"active":     12,
		"categories": []string{"extractors", "loaders", "transformers", "validators"},
		"plugins": []map[string]interface{}{
			{
				"name":        "tap-postgres",
				"type":        "extractor",
				"version":     "1.0.0",
				"status":      "active",
				"description": "PostgreSQL data extractor",
			},
			{
				"name":        "target-s3",
				"type":        "loader",
				"version":     "2.1.0",
				"status":      "active",
				"description": "AWS S3 data loader",
			},
		},
	}

	ds.logger.Debug("Plugins list requested")
	json.NewEncoder(w).Encode(plugins)
}

// handleWorkerStatus serves worker status
func (ds *DemoServer) handleWorkerStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	workers := map[string]interface{}{
		"pool_size":      10,
		"active_workers": 7,
		"idle_workers":   3,
		"queue_size":     1000,
		"pending_jobs":   5,
		"completed_jobs": 1247,
		"workers": []map[string]interface{}{
			{"id": "worker-1", "status": "active", "current_job": "pipeline-exec-001"},
			{"id": "worker-2", "status": "active", "current_job": "data-sync-002"},
			{"id": "worker-3", "status": "idle", "current_job": nil},
		},
	}

	ds.logger.Debug("Worker status requested")
	json.NewEncoder(w).Encode(workers)
}

// handleDiscovery serves service discovery information
func (ds *DemoServer) handleDiscovery(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	services := map[string]interface{}{
		"cluster_name": ds.clusterName,
		"node_id":      ds.nodeID,
		"services": []map[string]interface{}{
			{
				"name":     "flext-api",
				"type":     "rest-api",
				"endpoint": "http://localhost:8080",
				"health":   "/health",
				"status":   "healthy",
			},
			{
				"name":     "flext-worker",
				"type":     "background-worker",
				"endpoint": "tcp://localhost:9090",
				"health":   "/worker/health",
				"status":   "healthy",
			},
		},
	}

	ds.logger.Debug("Service discovery requested")
	json.NewEncoder(w).Encode(services)
}

// getEnvOrFlag returns flag value if provided, otherwise environment variable, or default
func getEnvOrFlag(flagValue, envKey, defaultValue string) string {
	if flagValue != "" {
		return flagValue
	}
	if envValue := os.Getenv(envKey); envValue != "" {
		return envValue
	}
	return defaultValue
}
