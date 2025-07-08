package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/container"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/flext-sh/flext/internal/infrastructure/server"
	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestBasicE2EIntegration tests the complete system end-to-end
func TestBasicE2EIntegration(t *testing.T) {
	// Setup test configuration
	cfg := &config.Config{
		Server: config.ServerConfig{
			Environment: "test",
			Host:        "localhost",
			Port:        0, // Use random port for testing
		},
		Features: config.FeatureFlags{
			DatabaseEnabled: false, // Use in-memory for E2E tests
		},
		Database: config.DatabaseConfig{
			Driver: "memory",
		},
	}

	// Create container
	c, err := container.NewContainer(cfg)
	require.NoError(t, err, "Failed to create container")
	defer c.Shutdown()

	// Create HTTP server
	e := echo.New()

	// Register routes
	pipelineHandler := c.GetPipelineHandler()
	pluginHandler := c.GetPluginHandler()

	require.NotNil(t, pipelineHandler, "Pipeline handler should not be nil")
	require.NotNil(t, pluginHandler, "Plugin handler should not be nil")

	// Register API routes
	pipelineHandler.RegisterRoutes(e)
	pluginHandler.RegisterRoutes(e)

	// Test server
	testServer := httptest.NewServer(e)
	defer testServer.Close()

	baseURL := testServer.URL

	t.Run("Health Check", func(t *testing.T) {
		resp, err := http.Get(baseURL + "/api/v1/health")
		require.NoError(t, err)
		defer resp.Body.Close()

		assert.Equal(t, http.StatusOK, resp.StatusCode)
	})

	t.Run("Complete Pipeline Workflow", func(t *testing.T) {
		// 1. Create a pipeline
		createPipelineReq := map[string]interface{}{
			"name":        "test-e2e-pipeline",
			"description": "E2E test pipeline",
			"type":        "etl",
			"created_by":  "e2e-test",
			"tags":        []string{"test", "e2e"},
		}

		reqBody, err := json.Marshal(createPipelineReq)
		require.NoError(t, err)

		resp, err := http.Post(
			baseURL+"/api/v1/pipelines",
			"application/json",
			bytes.NewBuffer(reqBody),
		)
		require.NoError(t, err)
		defer resp.Body.Close()

		// Debug response
		var responseBody []byte
		responseBody, err = io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("Pipeline creation response status: %d", resp.StatusCode)
		t.Logf("Pipeline creation response body: %s", string(responseBody))

		assert.Equal(t, http.StatusCreated, resp.StatusCode)

		var createResp map[string]interface{}
		err = json.Unmarshal(responseBody, &createResp)
		require.NoError(t, err)

		// Check if data field exists and extract pipeline_id from it
		data, exists := createResp["data"]
		require.True(t, exists, "Response should contain 'data' field")

		dataMap, ok := data.(map[string]interface{})
		require.True(t, ok, "Data field should be a map")

		pipelineID := dataMap["pipeline_id"].(string)
		assert.NotEmpty(t, pipelineID)

		// 2. Get the pipeline
		resp, err = http.Get(baseURL + "/api/v1/pipelines/" + pipelineID)
		require.NoError(t, err)
		defer resp.Body.Close()

		// Debug GET response
		responseBody, err = io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("Pipeline GET response status: %d", resp.StatusCode)
		t.Logf("Pipeline GET response body: %s", string(responseBody))

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var getResp map[string]interface{}
		err = json.Unmarshal(responseBody, &getResp)
		require.NoError(t, err)

		// Check if data field exists and extract pipeline info from it
		getData, exists := getResp["data"]
		require.True(t, exists, "GET response should contain 'data' field")

		getDataMap, ok := getData.(map[string]interface{})
		require.True(t, ok, "GET data field should be a map")

		assert.Equal(t, "test-e2e-pipeline", getDataMap["name"])
		assert.Equal(t, "E2E test pipeline", getDataMap["description"])

		// 3. List pipelines
		resp, err = http.Get(baseURL + "/api/v1/pipelines")
		require.NoError(t, err)
		defer resp.Body.Close()

		// Debug LIST response
		responseBody, err = io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("Pipeline LIST response status: %d", resp.StatusCode)
		t.Logf("Pipeline LIST response body: %s", string(responseBody))

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var listResp map[string]interface{}
		err = json.Unmarshal(responseBody, &listResp)
		require.NoError(t, err)

		// Check if data field exists and extract pipelines from it
		listData, exists := listResp["data"]
		require.True(t, exists, "LIST response should contain 'data' field")

		listDataMap, ok := listData.(map[string]interface{})
		require.True(t, ok, "LIST data field should be a map")

		pipelines := listDataMap["pipelines"].([]interface{})
		assert.GreaterOrEqual(t, len(pipelines), 1)
	})

	t.Run("Plugin Management Workflow", func(t *testing.T) {
		var responseBody []byte

		// 1. Register a plugin
		registerPluginReq := map[string]interface{}{
			"name":        "test-e2e-plugin",
			"type":        "source",
			"version":     "1.0.0",
			"description": "E2E test plugin",
			"entry_point": "/path/to/plugin",
		}

		reqBody, err := json.Marshal(registerPluginReq)
		require.NoError(t, err)

		resp, err := http.Post(
			baseURL+"/api/v1/plugins",
			"application/json",
			bytes.NewBuffer(reqBody),
		)
		require.NoError(t, err)
		defer resp.Body.Close()

		// Debug plugin registration response
		responseBody, err = io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("Plugin registration response status: %d", resp.StatusCode)
		t.Logf("Plugin registration response body: %s", string(responseBody))

		assert.Equal(t, http.StatusCreated, resp.StatusCode)

		var registerResp map[string]interface{}
		err = json.Unmarshal(responseBody, &registerResp)
		require.NoError(t, err)

		// Check if data field exists and extract plugin id from it
		registerData, exists := registerResp["data"]
		require.True(t, exists, "Plugin registration response should contain 'data' field")

		registerDataMap, ok := registerData.(map[string]interface{})
		require.True(t, ok, "Plugin registration data field should be a map")

		pluginIDUUID := registerDataMap["id"].(string)
		assert.NotEmpty(t, pluginIDUUID)
		pluginID := pluginIDUUID

		// 2. Get the plugin
		resp, err = http.Get(baseURL + "/api/v1/plugins/" + pluginID)
		require.NoError(t, err)
		defer resp.Body.Close()

		// Debug plugin GET response
		responseBody, err = io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("Plugin GET response status: %d", resp.StatusCode)
		t.Logf("Plugin GET response body: %s", string(responseBody))

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var getResp map[string]interface{}
		err = json.Unmarshal(responseBody, &getResp)
		require.NoError(t, err)

		// Check if data field exists and extract plugin info from it
		getPluginData, exists := getResp["data"]
		require.True(t, exists, "Plugin GET response should contain 'data' field")

		getPluginDataMap, ok := getPluginData.(map[string]interface{})
		require.True(t, ok, "Plugin GET data field should be a map")

		assert.Equal(t, "test-e2e-plugin", getPluginDataMap["name"])
		assert.Equal(t, "source", getPluginDataMap["type"])

		// 3. List plugins
		resp, err = http.Get(baseURL + "/api/v1/plugins")
		require.NoError(t, err)
		defer resp.Body.Close()

		// Debug plugin LIST response
		responseBody, err = io.ReadAll(resp.Body)
		require.NoError(t, err)
		t.Logf("Plugin LIST response status: %d", resp.StatusCode)
		t.Logf("Plugin LIST response body: %s", string(responseBody))

		assert.Equal(t, http.StatusOK, resp.StatusCode)

		var listResp map[string]interface{}
		err = json.Unmarshal(responseBody, &listResp)
		require.NoError(t, err)

		// Check if data field exists and extract plugins from it
		listPluginData, exists := listResp["data"]
		require.True(t, exists, "Plugin LIST response should contain 'data' field")

		listPluginDataMap, ok := listPluginData.(map[string]interface{})
		require.True(t, ok, "Plugin LIST data field should be a map")

		plugins := listPluginDataMap["plugins"].([]interface{})
		assert.GreaterOrEqual(t, len(plugins), 1)
	})
}

// TestContainerHealthCheck tests the container health check functionality
func TestContainerHealthCheck(t *testing.T) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Environment: "test",
		},
		Features: config.FeatureFlags{
			DatabaseEnabled: false,
		},
		Database: config.DatabaseConfig{
			Driver: "memory",
		},
	}

	c, err := container.NewContainer(cfg)
	require.NoError(t, err)
	defer c.Shutdown()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err = c.HealthCheck(ctx)
	assert.NoError(t, err, "Container health check should pass")
}

// TestServerStartupShutdown tests server lifecycle
func TestServerStartupShutdown(t *testing.T) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Environment: "test",
			Host:        "127.0.0.1",
			Port:        0, // Use random available port
		},
		Features: config.FeatureFlags{
			DatabaseEnabled: false,
		},
		Database: config.DatabaseConfig{
			Driver: "memory",
		},
	}

	// Test that server can start and shutdown gracefully
	logger := logging.GetLogger()
	srv := server.NewServer(cfg, logger)

	// Start server in goroutine
	started := make(chan bool)
	go func() {
		started <- true
		err := srv.Start()
		// Server stopped, which is expected
		assert.NoError(t, err)
	}()

	// Wait for server to start
	select {
	case <-started:
		// Server started successfully
	case <-time.After(2 * time.Second):
		t.Fatal("Server failed to start within timeout")
	}

	// Give server a moment to fully initialize
	time.Sleep(100 * time.Millisecond)

	// Shutdown server
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err := srv.Stop(ctx)
	assert.NoError(t, err, "Server should shutdown gracefully")
}

// TestDatabaseIntegration tests database connectivity and operations
func TestDatabaseIntegration(t *testing.T) {
	t.Run("Memory Database", func(t *testing.T) {
		cfg := &config.Config{
			Server: config.ServerConfig{
				Environment: "test",
			},
			Features: config.FeatureFlags{
				DatabaseEnabled: true,
			},
			Database: config.DatabaseConfig{
				Driver: "memory",
			},
		}

		c, err := container.NewContainer(cfg)
		require.NoError(t, err)
		defer c.Shutdown()

		db := c.GetDatabaseConnection()
		require.NotNil(t, db, "Database connection should not be nil")

		ctx := context.Background()
		err = db.HealthCheck(ctx)
		assert.NoError(t, err, "Database health check should pass")
	})

	t.Run("PostgreSQL Database", func(t *testing.T) {
		// Skip if PostgreSQL is not available
		cfg := &config.Config{
			Server: config.ServerConfig{
				Environment: "test",
			},
			Features: config.FeatureFlags{
				DatabaseEnabled: true,
			},
			Database: config.DatabaseConfig{
				Driver:   "postgres",
				Host:     "localhost",
				Port:     5432,
				Database: "flext",
				Username: "flext",
				Password: "flext",
				SSLMode:  "disable",
			},
		}

		c, err := container.NewContainer(cfg)
		if err != nil {
			t.Skip("PostgreSQL not available, skipping test")
			return
		}
		defer c.Shutdown()

		db := c.GetDatabaseConnection()
		require.NotNil(t, db, "Database connection should not be nil")

		ctx := context.Background()
		err = db.HealthCheck(ctx)
		assert.NoError(t, err, "PostgreSQL health check should pass")
	})
}

// BenchmarkE2EPipelineCreation benchmarks pipeline creation performance
func BenchmarkE2EPipelineCreation(b *testing.B) {
	cfg := &config.Config{
		Server: config.ServerConfig{
			Environment: "test",
		},
		Features: config.FeatureFlags{
			DatabaseEnabled: false,
		},
		Database: config.DatabaseConfig{
			Driver: "memory",
		},
	}

	c, err := container.NewContainer(cfg)
	require.NoError(b, err)
	defer c.Shutdown()

	e := echo.New()
	pipelineHandler := c.GetPipelineHandler()
	pipelineHandler.RegisterRoutes(e)

	testServer := httptest.NewServer(e)
	defer testServer.Close()

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		for pb.Next() {
			i++
			createPipelineReq := map[string]interface{}{
				"name":        fmt.Sprintf("benchmark-pipeline-%d", i),
				"description": "Benchmark test pipeline",
				"type":        "etl",
				"created_by":  "benchmark-test",
				"tags":        []string{"benchmark"},
			}

			reqBody, _ := json.Marshal(createPipelineReq)
			resp, err := http.Post(
				testServer.URL+"/api/v1/pipelines",
				"application/json",
				bytes.NewBuffer(reqBody),
			)
			if err != nil {
				b.Errorf("Failed to create pipeline: %v", err)
				continue
			}
			resp.Body.Close()

			if resp.StatusCode != http.StatusCreated {
				b.Errorf("Expected status 201, got %d", resp.StatusCode)
			}
		}
	})
}
