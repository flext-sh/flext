package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/flext/flexcore/internal/infrastructure/logging"
	"github.com/flext/flexcore/internal/shared_kernel/application"
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
	if err := json.NewEncoder(w).Encode(apiInfo); err != nil {
		ds.logger.Error("Failed to encode API info", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
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
	if err := json.NewEncoder(w).Encode(response); err != nil {
		ds.logger.Error("Failed to encode health response", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
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
	if err := json.NewEncoder(w).Encode(status); err != nil {
		ds.logger.Error("Failed to encode cluster status", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
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
	if err := json.NewEncoder(w).Encode(metrics); err != nil {
		ds.logger.Error("Failed to encode metrics", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
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
	if err := json.NewEncoder(w).Encode(pipelines); err != nil {
		ds.logger.Error("Failed to encode pipelines", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
}

// handlePlugins serves plugins information
func (ds *DemoServer) handlePlugins(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// DRY: Use specialized function to generate plugin mock data
	plugins := ds.generatePluginsMockData()

	ds.logger.Debug("Plugins list requested")
	if err := json.NewEncoder(w).Encode(plugins); err != nil {
		ds.logger.Error("Failed to encode plugins", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
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
	if err := json.NewEncoder(w).Encode(workers); err != nil {
		ds.logger.Error("Failed to encode worker status", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
}

// handleDiscovery serves service discovery information
func (ds *DemoServer) handleDiscovery(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// DRY: Use specialized function to generate service discovery mock data
	services := ds.generateServiceDiscoveryMockData()

	ds.logger.Debug("Service discovery requested")
	if err := json.NewEncoder(w).Encode(services); err != nil {
		ds.logger.Error("Failed to encode service discovery", logging.F("error", err.Error()))
		http.Error(w, "Internal server error", http.StatusInternalServerError)
	}
}

// DRY: Specialized mock data generators following SOLID SRP principle

// generatePluginsMockData creates mock plugins data - eliminates 16-line duplication (mass=64)
func (ds *DemoServer) generatePluginsMockData() map[string]interface{} {
	return map[string]interface{}{
		"total":      15,
		"active":     12,
		"categories": []string{"extractors", "loaders", "transformers", "validators"},
		"plugins":    ds.generatePluginInstancesMockData(),
	}
}

// MockDataBuilder - SOLID Builder Pattern for eliminating duplication
type MockDataBuilder struct {
	items []map[string]interface{}
}

// NewMockDataBuilder creates a new builder instance
func NewMockDataBuilder() *MockDataBuilder {
	return &MockDataBuilder{
		items: make([]map[string]interface{}, 0),
	}
}

// AddItem adds a new item to the builder - SOLID Single Responsibility
func (b *MockDataBuilder) AddItem(item map[string]interface{}) *MockDataBuilder {
	b.items = append(b.items, item)
	return b
}

// Build returns the final slice - SOLID Open/Closed Principle
func (b *MockDataBuilder) Build() []map[string]interface{} {
	return b.items
}

// MockDataTemplateFactory provides specialized templates for different mock data types
// SOLID SRP: Eliminates 18-line duplication (mass=90) by using template patterns
type MockDataTemplateFactory struct{}

// NewMockDataTemplateFactory creates a new template factory
func NewMockDataTemplateFactory() *MockDataTemplateFactory {
	return &MockDataTemplateFactory{}
}

// MockDataTemplate defines the structure for mock data templates
type MockDataTemplate struct {
	Type     string
	Items    []map[string]interface{}
	Builder  func() *MockDataBuilder
}

// CreatePluginInstancesTemplate creates template for plugin instances
// DRY PRINCIPLE: Uses shared template creation eliminating 24-line duplication (mass=98)
func (factory *MockDataTemplateFactory) CreatePluginInstancesTemplate() MockDataTemplate {
	return factory.createGenericTemplate("plugin_instances", factory.getPluginInstancesData())
}

// CreateServiceInstancesTemplate creates template for service instances
// DRY PRINCIPLE: Uses shared template creation eliminating 24-line duplication (mass=98)
func (factory *MockDataTemplateFactory) CreateServiceInstancesTemplate() MockDataTemplate {
	return factory.createGenericTemplate("service_instances", factory.getServiceInstancesData())
}

// DRY HELPER: Generic template creation eliminating 24-line duplication (mass=98)
// SOLID SRP: Single responsibility for template structure creation
func (factory *MockDataTemplateFactory) createGenericTemplate(templateType string, items []map[string]interface{}) MockDataTemplate {
	return MockDataTemplate{
		Type:  templateType,
		Items: items,
		Builder: func() *MockDataBuilder {
			return NewMockDataBuilder()
		},
	}
}

// DRY HELPER: Plugin instances data provider - eliminates data duplication
// SOLID SRP: Single responsibility for plugin data creation
func (factory *MockDataTemplateFactory) getPluginInstancesData() []map[string]interface{} {
	return factory.createItemList([]MockItemConfig{
		{Name: "tap-postgres", Type: "extractor", Version: "1.0.0", Status: "active", Description: "PostgreSQL data extractor"},
		{Name: "target-s3", Type: "loader", Version: "2.1.0", Status: "active", Description: "AWS S3 data loader"},
	})
}

// DRY HELPER: Service instances data provider - eliminates data duplication
// SOLID SRP: Single responsibility for service data creation
func (factory *MockDataTemplateFactory) getServiceInstancesData() []map[string]interface{} {
	return factory.createItemList([]MockItemConfig{
		{Name: "flext-api", Type: "rest-api", Endpoint: "http://localhost:8080", Health: "/health", Status: "healthy"},
		{Name: "flext-worker", Type: "background-worker", Endpoint: "tcp://localhost:9090", Health: "/worker/health", Status: "healthy"},
	})
}

// MockItemConfig represents configuration for creating mock data items
// SOLID SRP: Single responsibility for item configuration
type MockItemConfig struct {
	Name        string
	Type        string
	Version     string
	Status      string
	Description string
	Endpoint    string
	Health      string
}

// DRY HELPER: Generic item list creator eliminating 18-line duplication (mass=75)
// SOLID SRP: Single responsibility for converting config to map data
func (factory *MockDataTemplateFactory) createItemList(configs []MockItemConfig) []map[string]interface{} {
	items := make([]map[string]interface{}, 0, len(configs))
	for _, config := range configs {
		item := make(map[string]interface{})
		item["name"] = config.Name
		item["type"] = config.Type
		item["status"] = config.Status
		
		// Add optional fields if present
		if config.Version != "" {
			item["version"] = config.Version
		}
		if config.Description != "" {
			item["description"] = config.Description
		}
		if config.Endpoint != "" {
			item["endpoint"] = config.Endpoint
		}
		if config.Health != "" {
			item["health"] = config.Health
		}
		
		items = append(items, item)
	}
	return items
}

// BuildFromTemplate builds mock data from template eliminating duplication
// SOLID SRP: Single responsibility for template-based building
func (factory *MockDataTemplateFactory) BuildFromTemplate(template MockDataTemplate) []map[string]interface{} {
	builder := template.Builder()
	for _, item := range template.Items {
		builder.AddItem(item)
	}
	return builder.Build()
}

// generatePluginInstancesMockData creates mock plugin instances using template factory
// DRY PRINCIPLE: Eliminates 18-line duplication (mass=90) by using MockDataTemplateFactory
func (ds *DemoServer) generatePluginInstancesMockData() []map[string]interface{} {
	factory := NewMockDataTemplateFactory()
	template := factory.CreatePluginInstancesTemplate()
	return factory.BuildFromTemplate(template)
}

// generateServiceDiscoveryMockData creates mock service discovery data - eliminates 16-line duplication (mass=64)
func (ds *DemoServer) generateServiceDiscoveryMockData() map[string]interface{} {
	return map[string]interface{}{
		"cluster_name": ds.clusterName,
		"node_id":      ds.nodeID,
		"services":     ds.generateServiceInstancesMockData(),
	}
}

// generateServiceInstancesMockData creates mock service instances using template factory
// DRY PRINCIPLE: Eliminates 18-line duplication (mass=90) by using MockDataTemplateFactory
func (ds *DemoServer) generateServiceInstancesMockData() []map[string]interface{} {
	factory := NewMockDataTemplateFactory()
	template := factory.CreateServiceInstancesTemplate()
	return factory.BuildFromTemplate(template)
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
