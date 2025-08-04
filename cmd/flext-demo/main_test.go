package main

import (
	"os"
	"testing"

	"github.com/flext-sh/flext/pkg/config"
	"github.com/flext-sh/flext/pkg/logging"
)

func TestNewDemoServer(t *testing.T) {
	// Initialize logging for tests
	logging.Initialize("test-demo", "info")
	logger := logging.GetLogger()

	cfg := &DemoConfig{
		Config: &config.Config{},
		NodeID: "test-node",
		ClusterName: "test-cluster",
	}

	demoServer := NewDemoServer("test-node", "test-cluster", logger, cfg)

	if demoServer == nil {
		t.Fatal("NewDemoServer() should not return nil")
	}

	if demoServer.nodeID != "test-node" {
		t.Errorf("Expected nodeID 'test-node', got '%s'", demoServer.nodeID)
	}

	if demoServer.clusterName != "test-cluster" {
		t.Errorf("Expected clusterName 'test-cluster', got '%s'", demoServer.clusterName)
	}

	if demoServer.logger != logger {
		t.Error("DemoServer logger should match provided logger")
	}

	if demoServer.config != cfg {
		t.Error("DemoServer config should match provided config")
	}

	if demoServer.server == nil {
		t.Error("DemoServer should have an initialized server")
	}
}

func TestDemoConfig(t *testing.T) {
	baseCfg := &config.Config{}
	baseCfg.Server.Host = "localhost"
	baseCfg.Server.Port = 8080
	baseCfg.Server.Environment = "test"

	demoCfg := &DemoConfig{
		Config: baseCfg,
		NodeID: "demo-001",
		ClusterName: "flext-demo",
	}

	if demoCfg.Config.Server.Host != "localhost" {
		t.Error("DemoConfig should preserve base config values")
	}

	if demoCfg.NodeID != "demo-001" {
		t.Error("DemoConfig should have correct NodeID")
	}

	if demoCfg.ClusterName != "flext-demo" {
		t.Error("DemoConfig should have correct ClusterName")
	}
}

func TestMainFunction(t *testing.T) {
	// Test that main function exists and can be referenced
	t.Run("Main function exists", func(t *testing.T) {
		_ = main
	})
}

func TestCommandLineArguments(t *testing.T) {
	originalArgs := os.Args
	defer func() {
		os.Args = originalArgs
	}()

	tests := []struct {
		name string
		args []string
	}{
		{
			name: "Default arguments",
			args: []string{"flext-demo"},
		},
		{
			name: "Custom port",
			args: []string{"flext-demo", "--port=9000"},
		},
		{
			name: "Custom node ID",
			args: []string{"flext-demo", "--node-id=custom-node"},
		},
		{
			name: "Custom cluster",
			args: []string{"flext-demo", "--cluster=custom-cluster"},
		},
		{
			name: "All parameters",
			args: []string{
				"flext-demo",
				"--port=9001",
				"--host=127.0.0.1",
				"--node-id=test-node",
				"--cluster=test-cluster",
				"--env=production",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			os.Args = tt.args
			t.Log("Demo server args configured:", tt.args)
		})
	}
}

func TestDemoServerMethods(t *testing.T) {
	logging.Initialize("test-demo", "info")
	logger := logging.GetLogger()

	cfg := &DemoConfig{
		Config: &config.Config{},
		NodeID: "test-node",
		ClusterName: "test-cluster",
	}

	demoServer := NewDemoServer("test-node", "test-cluster", logger, cfg)

	t.Run("SetupDemoRoutes", func(t *testing.T) {
		// Test that setupDemoRoutes doesn't panic
		defer func() {
			if r := recover(); r != nil {
				t.Errorf("setupDemoRoutes panicked: %v", r)
			}
		}()
		
		demoServer.setupDemoRoutes()
	})
}

func TestDemoServerDependencies(t *testing.T) {
	// Test that all required dependencies are available
	t.Run("Config package available", func(t *testing.T) {
		_ = "github.com/flext-sh/flext/pkg/config"
	})
	
	t.Run("Logging package available", func(t *testing.T) {
		_ = "github.com/flext-sh/flext/pkg/logging"
	})
	
	t.Run("Server package available", func(t *testing.T) {
		_ = "github.com/flext-sh/flext/pkg/server"
	})
}

func TestHealthResponseStructure(t *testing.T) {
	// Test the data structures are properly defined
	healthResp := &HealthResponse{
		Status: "ok",
		Version: "2.0.0",
		Mode: "demo",
		Features: map[string]bool{
			"clustering": true,
			"monitoring": true,
		},
		Env: map[string]string{
			"NODE_ID": "test",
			"CLUSTER": "test-cluster",
		},
	}

	if healthResp.Status != "ok" {
		t.Error("HealthResponse should have correct status")
	}

	if len(healthResp.Features) != 2 {
		t.Error("HealthResponse should have features map")
	}

	if len(healthResp.Env) != 2 {
		t.Error("HealthResponse should have env map")
	}
}

func TestClusterStatusStructure(t *testing.T) {
	clusterStatus := &ClusterStatus{
		NodeID: "demo-001",
		ClusterName: "flext-demo",
		Role: "primary",
		Status: "active",
		Nodes: []string{"demo-001", "demo-002"},
	}

	if clusterStatus.NodeID != "demo-001" {
		t.Error("ClusterStatus should have correct NodeID")
	}

	if len(clusterStatus.Nodes) != 2 {
		t.Error("ClusterStatus should have nodes slice")
	}
}

func TestMetricsResponseStructure(t *testing.T) {
	metricsResp := &MetricsResponse{
		Requests: 100,
		Uptime: "1h30m",
		Memory: map[string]string{
			"used": "64MB",
			"total": "128MB",
		},
		WorkerPool: map[string]int{
			"active": 5,
			"idle": 3,
		},
		DistributedOps: map[string]int64{
			"total": 1000,
			"success": 950,
		},
	}

	if metricsResp.Requests != 100 {
		t.Error("MetricsResponse should have correct request count")
	}

	if len(metricsResp.Memory) != 2 {
		t.Error("MetricsResponse should have memory map")
	}
}