package server

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/flext-sh/flext/pkg/controlpanel/configuration/config"
	"github.com/flext-sh/flext/pkg/logging"
)

func TestNewServer(t *testing.T) {
	// Initialize logging for tests
	logging.Initialize("test", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	cfg.Server.Environment = "development"
	cfg.Server.Port = 8081

	server := NewServer(cfg, logger)

	if server == nil {
		t.Fatal("NewServer() should not return nil")
	}

	if server.config != cfg {
		t.Error("Server config should match provided config")
	}

	if server.logger != logger {
		t.Error("Server logger should match provided logger")
	}

	if server.router == nil {
		t.Error("Server router should be initialized")
	}
}

func TestServerRoutes(t *testing.T) {
	logging.Initialize("test", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	cfg.Server.Environment = "test"
	cfg.Server.Port = 8081
	cfg.FlexCore.URL = "http://localhost:8080"

	server := NewServer(cfg, logger)
	server.SetupBasicRoutes()

	tests := []struct {
		name           string
		method         string
		path           string
		expectedStatus int
		expectedFields []string
	}{
		{
			name:           "Health check",
			method:         "GET",
			path:           "/health",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"status", "timestamp", "service", "version", "port"},
		},
		{
			name:           "API health check",
			method:         "GET",
			path:           "/api/v1/health",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"status", "timestamp", "service", "version", "port"},
		},
		{
			name:           "Status check",
			method:         "GET",
			path:           "/api/v1/status",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"service", "version", "status", "environment", "debug", "timestamp", "endpoints"},
		},
		{
			name:           "List plugins",
			method:         "GET",
			path:           "/api/v1/plugins",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"plugins", "message"},
		},
		{
			name:           "List Meltano projects",
			method:         "GET",
			path:           "/api/v1/meltano/projects",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"projects", "message"},
		},
		{
			name:           "List Singer taps",
			method:         "GET",
			path:           "/api/v1/singer/taps",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"taps", "message"},
		},
		{
			name:           "List DBT models",
			method:         "GET",
			path:           "/api/v1/dbt/models",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"models", "message"},
		},
		{
			name:           "FlexCore health",
			method:         "GET",
			path:           "/api/v1/flexcore/health",
			expectedStatus: http.StatusOK,
			expectedFields: []string{"flexcore_status", "message", "flexcore_url"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(tt.method, tt.path, nil)
			w := httptest.NewRecorder()

			server.router.ServeHTTP(w, req)

			if w.Code != tt.expectedStatus {
				t.Errorf("Expected status %d, got %d", tt.expectedStatus, w.Code)
			}

			// Check content type
			contentType := w.Header().Get("Content-Type")
			if contentType != "application/json; charset=utf-8" {
				t.Errorf("Expected JSON content type, got %s", contentType)
			}

			// Parse JSON response
			var response map[string]interface{}
			if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
				t.Fatalf("Failed to parse JSON response: %v", err)
			}

			// Check expected fields exist
			for _, field := range tt.expectedFields {
				if _, exists := response[field]; !exists {
					t.Errorf("Expected field '%s' not found in response", field)
				}
			}
		})
	}
}

func TestServerHealthCheck(t *testing.T) {
	logging.Initialize("test", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	cfg.Server.Port = 8081

	server := NewServer(cfg, logger)
	server.SetupBasicRoutes()

	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	var response map[string]interface{}
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to parse health check response: %v", err)
	}

	// Verify specific fields
	if response["status"] != "ok" {
		t.Errorf("Expected status 'ok', got %v", response["status"])
	}

	if response["service"] != "flext" {
		t.Errorf("Expected service 'flext', got %v", response["service"])
	}

	if response["version"] != "2.0.0" {
		t.Errorf("Expected version '2.0.0', got %v", response["version"])
	}

	if response["port"] != float64(8081) {
		t.Errorf("Expected port 8081, got %v", response["port"])
	}
}

func TestServerStatusCheck(t *testing.T) {
	logging.Initialize("test", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	cfg.Server.Environment = "test"
	cfg.Server.Debug = true

	server := NewServer(cfg, logger)
	server.SetupBasicRoutes()

	req := httptest.NewRequest("GET", "/api/v1/status", nil)
	w := httptest.NewRecorder()

	server.router.ServeHTTP(w, req)

	var response map[string]interface{}
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("Failed to parse status response: %v", err)
	}

	// Verify environment is preserved
	if response["environment"] != "test" {
		t.Errorf("Expected environment 'test', got %v", response["environment"])
	}

	if response["debug"] != true {
		t.Errorf("Expected debug true, got %v", response["debug"])
	}

	// Check endpoints field
	endpoints, ok := response["endpoints"].(map[string]interface{})
	if !ok {
		t.Error("Expected endpoints to be an object")
	} else {
		expectedEndpoints := []string{"health", "status", "plugins", "meltano", "singer", "dbt", "flexcore"}
		for _, endpoint := range expectedEndpoints {
			if _, exists := endpoints[endpoint]; !exists {
				t.Errorf("Expected endpoint '%s' not found", endpoint)
			}
		}
	}
}

func TestServerRegisterHandlers(t *testing.T) {
	logging.Initialize("test", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	server := NewServer(cfg, logger)

	// Test registering handlers doesn't panic
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("RegisterHandler panicked: %v", r)
		}
	}()

	server.RegisterHandler("test handler")
	server.RegisterCleanHandler("test", "test handler")
}

func TestServerProductionMode(t *testing.T) {
	logging.Initialize("test", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	cfg.Server.Environment = "production"

	server := NewServer(cfg, logger)
	if server == nil {
		t.Fatal("Server should be created in production mode")
	}

	// In production mode, gin should be in release mode
	// This is primarily tested by checking the server was created successfully
}

func TestInvalidRoutes(t *testing.T) {
	logging.Initialize("test", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	server := NewServer(cfg, logger)
	server.SetupBasicRoutes()

	tests := []struct {
		name   string
		method string
		path   string
		status int
	}{
		{"Invalid path", "GET", "/invalid", http.StatusNotFound},
		{"Invalid method", "POST", "/health", http.StatusNotFound}, // Gin returns 404 for undefined routes
		{"Invalid API path", "GET", "/api/v1/invalid", http.StatusNotFound},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(tt.method, tt.path, nil)
			w := httptest.NewRecorder()

			server.router.ServeHTTP(w, req)

			if w.Code != tt.status {
				t.Errorf("Expected status %d, got %d", tt.status, w.Code)
			}
		})
	}
}

// Benchmark tests
func BenchmarkHealthCheck(b *testing.B) {
	logging.Initialize("benchmark", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	cfg.Server.Port = 8081

	server := NewServer(cfg, logger)
	server.SetupBasicRoutes()

	req := httptest.NewRequest("GET", "/health", nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		server.router.ServeHTTP(w, req)
	}
}

func BenchmarkStatusCheck(b *testing.B) {
	logging.Initialize("benchmark", "info")
	logger := logging.GetLogger()

	cfg := &config.Config{}
	server := NewServer(cfg, logger)
	server.SetupBasicRoutes()

	req := httptest.NewRequest("GET", "/api/v1/status", nil)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		server.router.ServeHTTP(w, req)
	}
}
