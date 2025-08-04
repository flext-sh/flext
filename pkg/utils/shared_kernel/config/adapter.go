package config

import (
	"fmt"
	"os"
	"time"

	"github.com/flext-sh/flext/pkg/infrastructure/config"
	sharedConfig "github.com/flext-sh/flext/pkg/config"
)

// ConfigAdapter adapts UnifiedConfig to existing config.Config interface
type ConfigAdapter struct {
	unified *sharedConfig.UnifiedConfig
	legacy  *config.Config
}

// NewConfigAdapter creates a new configuration adapter
func NewConfigAdapter() (*ConfigAdapter, error) {
	// Load unified configuration
	unified, err := sharedConfig.NewUnifiedConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to load unified config: %w", err)
	}

	// Validate unified configuration
	if err := unified.Validate(); err != nil {
		return nil, fmt.Errorf("unified config validation failed: %w", err)
	}

	// Create legacy config structure from unified config
	legacy := &config.Config{
		Database: config.DatabaseConfig{
			Driver:          unified.Database.Driver,
			Host:            unified.Database.Host,
			Port:            unified.Database.Port,
			Database:        unified.Database.Database,
			Username:        unified.Database.Username,
			Password:        unified.Database.Password,
			SSLMode:         unified.Database.SSLMode,
			MaxOpenConns:    unified.Database.MaxOpenConns,
			MaxIdleConns:    unified.Database.MaxIdleConns,
			ConnMaxLifetime: unified.Database.ConnMaxLifetime,
		},

		Features: config.FeatureFlags{
			DatabaseEnabled:  unified.Features.DatabaseEnabled,
			WebSocketEnabled: unified.Features.WebSocketEnabled,
		},

		CleanArchitecture: config.CleanArchitectureConfig{
			Enabled: unified.Features.CleanArchitectureEnabled,
		},

		Server: config.ServerConfig{
			Host:            unified.Host,
			Port:            unified.Port,
			Environment:     unified.Environment,
			Debug:           unified.Debug,
			ShutdownTimeout: 30 * time.Second, // Default from existing code
		},
	}

	// Set environment variables for legacy compatibility would go here
	// legacy.SetEnvDefaults() // Method doesn't exist, skipping

	return &ConfigAdapter{
		unified: unified,
		legacy:  legacy,
	}, nil
}

// GetUnifiedConfig returns the unified configuration
func (a *ConfigAdapter) GetUnifiedConfig() *sharedConfig.UnifiedConfig {
	return a.unified
}

// GetLegacyConfig returns the legacy configuration for backward compatibility
func (a *ConfigAdapter) GetLegacyConfig() *config.Config {
	return a.legacy
}

// UpdateFromEnvironment reloads configuration from environment variables
func (a *ConfigAdapter) UpdateFromEnvironment() error {
	// Reload unified config
	unified, err := sharedConfig.NewUnifiedConfig()
	if err != nil {
		return fmt.Errorf("failed to reload unified config: %w", err)
	}

	if err := unified.Validate(); err != nil {
		return fmt.Errorf("reloaded unified config validation failed: %w", err)
	}

	// Update adapter state
	a.unified = unified

	// Update legacy config to match
	a.legacy.Server.Environment = unified.Environment
	a.legacy.Server.Debug = unified.Debug
	a.legacy.Server.Host = unified.Host
	a.legacy.Server.Port = unified.Port

	// Update database config
	a.legacy.Database.Driver = unified.Database.Driver
	a.legacy.Database.Host = unified.Database.Host
	a.legacy.Database.Port = unified.Database.Port
	a.legacy.Database.Database = unified.Database.Database
	a.legacy.Database.Username = unified.Database.Username
	a.legacy.Database.Password = unified.Database.Password
	a.legacy.Database.SSLMode = unified.Database.SSLMode
	a.legacy.Database.MaxOpenConns = unified.Database.MaxOpenConns
	a.legacy.Database.MaxIdleConns = unified.Database.MaxIdleConns
	a.legacy.Database.ConnMaxLifetime = unified.Database.ConnMaxLifetime

	// Update feature flags
	a.legacy.Features.DatabaseEnabled = unified.Features.DatabaseEnabled
	a.legacy.Features.WebSocketEnabled = unified.Features.WebSocketEnabled

	// Update Clean Architecture config
	a.legacy.CleanArchitecture.Enabled = unified.Features.CleanArchitectureEnabled

	// Update server config
	a.legacy.Server.Environment = unified.Environment
	a.legacy.Server.Debug = unified.Debug

	return nil
}

// Address returns the server address
func (a *ConfigAdapter) Address() string {
	return a.unified.GetAddress()
}

// GetDatabaseDSN returns the database connection string
func (a *ConfigAdapter) GetDatabaseDSN() string {
	return a.unified.GetDatabaseDSN()
}

// GetEnvWithDefault returns environment variable value or default
func (a *ConfigAdapter) GetEnvWithDefault(key, defaultValue string) string {
	// Since legacy config doesn't have this method, implement it here
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

// IsProduction returns true if running in production
func (a *ConfigAdapter) IsProduction() bool {
	return a.unified.IsProduction()
}

// IsDevelopment returns true if running in development
func (a *ConfigAdapter) IsDevelopment() bool {
	return a.unified.IsDevelopment()
}

// IsTest returns true if running in test
func (a *ConfigAdapter) IsTest() bool {
	return a.unified.IsTest()
}

// GetAuthConfig returns authentication configuration
func (a *ConfigAdapter) GetAuthConfig() sharedConfig.AuthConfig {
	return a.unified.Auth
}

// GetPipelineConfig returns pipeline configuration
func (a *ConfigAdapter) GetPipelineConfig() sharedConfig.PipelineConfig {
	return a.unified.Pipeline
}

// GetPluginConfig returns plugin configuration
func (a *ConfigAdapter) GetPluginConfig() sharedConfig.PluginConfig {
	return a.unified.Plugin
}

// GetMeltanoConfig returns Meltano configuration
func (a *ConfigAdapter) GetMeltanoConfig() sharedConfig.MeltanoConfig {
	return a.unified.Meltano
}

// GetDBTConfig returns dbt configuration
func (a *ConfigAdapter) GetDBTConfig() sharedConfig.DBTConfig {
	return a.unified.DBT
}

// GetObservabilityConfig returns observability configuration
func (a *ConfigAdapter) GetObservabilityConfig() sharedConfig.ObservabilityConfig {
	return a.unified.Observability
}

// GetExternalServicesConfig returns external services configuration
func (a *ConfigAdapter) GetExternalServicesConfig() sharedConfig.ExternalServicesConfig {
	return a.unified.External
}

// GetCacheConfig returns cache configuration
func (a *ConfigAdapter) GetCacheConfig() sharedConfig.CacheConfig {
	return a.unified.Cache
}

// GetFeatureFlags returns feature flags
func (a *ConfigAdapter) GetFeatureFlags() sharedConfig.FeatureFlags {
	return a.unified.Features
}

// String returns a string representation of the configuration
func (a *ConfigAdapter) String() string {
	return fmt.Sprintf("ConfigAdapter{Environment: %s, Debug: %t, Address: %s}",
		a.unified.Environment, a.unified.Debug, a.unified.GetAddress())
}
