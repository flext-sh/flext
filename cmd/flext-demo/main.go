package main

import (
	"context"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/flext-sh/flext/pkg/controlpanel/configuration/config"
	"github.com/flext-sh/flext/pkg/controlpanel/monitoring/server"
	"github.com/flext-sh/flext/pkg/logging"
)

// DemoConfig extends the base config for demo-specific settings
type DemoConfig struct {
	*config.Config
	NodeID      string
	ClusterName string
}

// DemoServer represents the demo server with its configuration
type DemoServer struct {
	nodeID      string
	clusterName string
	startTime   time.Time
	logger      logging.Logger
	config      *DemoConfig
	server      *server.Server
	httpServer  *http.Server
}

// NewDemoServer creates a new demo server instance
func NewDemoServer(nodeID, clusterName string, log logging.Logger, cfg *DemoConfig) *DemoServer {
	// Create server instance
	srv := server.NewServer(cfg.Config, log)

	return &DemoServer{
		nodeID:      nodeID,
		clusterName: clusterName,
		startTime:   time.Now(),
		logger:      log,
		config:      cfg,
		server:      srv,
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

// Start starts the demo server
func (ds *DemoServer) Start() error {
	// Setup demo-specific routes
	ds.setupDemoRoutes()

	// Start the server
	return ds.server.Start()
}

// Stop gracefully stops the demo server
func (ds *DemoServer) Stop(ctx context.Context) error {
	return ds.server.Stop(ctx)
}

// setupDemoRoutes adds demo-specific routes
func (ds *DemoServer) setupDemoRoutes() {
	// Note: This is a simplified version - real implementation would use Gin router
	// For now, we'll let the server handle basic routes
	ds.server.SetupBasicRoutes()
}

func main() {
	// Parse command line flags
	port := flag.Int("port", 8080, "Server port")
	host := flag.String("host", "0.0.0.0", "Server host")
	nodeID := flag.String("node-id", "demo-001", "Node ID")
	cluster := flag.String("cluster", "flext-demo", "Cluster name")
	flag.Parse()

	// Initialize logging
	if err := logging.Initialize("flext-demo", "info"); err != nil {
		fmt.Printf("Failed to initialize logging: %v\n", err)
		os.Exit(1)
	}
	logger := logging.GetLogger()

	// Initialize configuration
	baseCfg := &config.Config{}
	baseCfg.Server.Host = *host
	baseCfg.Server.Port = *port
	baseCfg.Server.Environment = *env
	baseCfg.Server.Debug = (*env != "production")
	baseCfg.FlexCore.URL = "http://localhost:8080"

	cfg := &DemoConfig{
		Config:      baseCfg,
		NodeID:      *nodeID,
		ClusterName: *cluster,
	}

	// Create demo server
	demoServer := NewDemoServer(*nodeID, *cluster, logger, cfg)

	logger.Info("Starting FLEXT Demo Server",
		logging.F("port", *port),
		logging.F("host", *host),
		logging.F("node_id", *nodeID),
		logging.F("cluster", *cluster),
		logging.F("environment", *env))

	// Start server in a goroutine
	go func() {
		if err := demoServer.Start(); err != nil {
			logger.Error("Demo server failed to start", logging.F("error", err))
			os.Exit(1)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down FLEXT Demo Server...")

	// Create context with timeout for graceful shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := demoServer.Stop(ctx); err != nil {
		logger.Error("Demo server shutdown failed", logging.F("error", err))
		os.Exit(1)
	}

	logger.Info("FLEXT Demo Server shutdown complete")
}
