package container

import (
	"testing"

	"github.com/flext-sh/flext/pkg/config"
)

func TestNewContainer(t *testing.T) {
	tests := []struct {
		name        string
		config      *config.Config
		expectError bool
	}{
		{
			name:        "Valid config",
			config:      &config.Config{},
			expectError: false,
		},
		{
			name:        "Nil config",
			config:      nil,
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			container, err := NewContainer(tt.config)
			
			if (err != nil) != tt.expectError {
				t.Errorf("NewContainer() error = %v, expectError %v", err, tt.expectError)
				return
			}
			
			if !tt.expectError {
				if container == nil {
					t.Error("Expected non-nil container")
				}
				if container.config != tt.config {
					t.Error("Container config should match provided config")
				}
				if container.logger == nil {
					t.Error("Container logger should be initialized")
				}
			}
		})
	}
}

func TestContainerHandlers(t *testing.T) {
	cfg := &config.Config{}
	container, err := NewContainer(cfg)
	if err != nil {
		t.Fatalf("Failed to create container: %v", err)
	}

	t.Run("GetPluginHandler", func(t *testing.T) {
		handler := container.GetPluginHandler()
		// For now, handlers return nil as they're placeholders
		if handler != nil {
			t.Log("Plugin handler returned (placeholder implementation)")
		}
	})

	t.Run("GetUnifiedMeltanoHandler", func(t *testing.T) {
		handler := container.GetUnifiedMeltanoHandler()
		// For now, handlers return nil as they're placeholders
		if handler != nil {
			t.Log("Unified Meltano handler returned (placeholder implementation)")
		}
	})

	t.Run("GetFlexcoreHandler", func(t *testing.T) {
		handler := container.GetFlexcoreHandler()
		// For now, handlers return nil as they're placeholders
		if handler != nil {
			t.Log("FlexCore handler returned (placeholder implementation)")
		}
	})

	t.Run("GetPipelineHandler", func(t *testing.T) {
		handler := container.GetPipelineHandler()
		// For now, handlers return nil as they're placeholders
		if handler != nil {
			t.Log("Pipeline handler returned (placeholder implementation)")
		}
	})
}

func TestContainerWithRealConfig(t *testing.T) {
	cfg := &config.Config{}
	cfg.Server.Host = "localhost"
	cfg.Server.Port = 8081
	cfg.Server.Environment = "test"
	cfg.Server.Debug = true
	cfg.FlexCore.URL = "http://localhost:8080"
	cfg.Database.URL = "postgresql://localhost:5433/test"
	cfg.Redis.URL = "redis://localhost:6380"

	container, err := NewContainer(cfg)
	if err != nil {
		t.Fatalf("Failed to create container with real config: %v", err)
	}

	if container.config.Server.Host != "localhost" {
		t.Error("Container should preserve config values")
	}

	if container.config.Server.Port != 8081 {
		t.Error("Container should preserve config port")
	}
}

// Benchmark tests
func BenchmarkNewContainer(b *testing.B) {
	cfg := &config.Config{}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		container, err := NewContainer(cfg)
		if err != nil {
			b.Fatalf("Failed to create container: %v", err)
		}
		_ = container
	}
}

func BenchmarkContainerHandlers(b *testing.B) {
	cfg := &config.Config{}
	container, err := NewContainer(cfg)
	if err != nil {
		b.Fatalf("Failed to create container: %v", err)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = container.GetPluginHandler()
		_ = container.GetUnifiedMeltanoHandler()
		_ = container.GetFlexcoreHandler()
		_ = container.GetPipelineHandler()
	}
}