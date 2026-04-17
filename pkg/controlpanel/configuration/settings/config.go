// Package settings - Configuration management for FLEXT Service
package settings

import (
	"fmt"
	"strings"
	"time"

	"github.com/spf13/viper"
)

// Config represents the FLEXT service configuration
type Config struct {
	Server struct {
		Host        string `mapstructure:"host"`
		Port        int    `mapstructure:"port"`
		Environment string `mapstructure:"environment"`
		Debug       bool   `mapstructure:"debug"`
	} `mapstructure:"server"`

	Database struct {
		URL             string        `mapstructure:"url"`
		MaxConnections  int           `mapstructure:"max_connections"`
		ConnMaxLifetime time.Duration `mapstructure:"conn_max_lifetime"`
	} `mapstructure:"database"`

	Redis struct {
		URL        string `mapstructure:"url"`
		PoolSize   int    `mapstructure:"pool_size"`
		MaxRetries int    `mapstructure:"max_retries"`
	} `mapstructure:"redis"`

	FlexCore struct {
		URL                 string        `mapstructure:"url"`
		Timeout             time.Duration `mapstructure:"timeout"`
		MaxRetries          int           `mapstructure:"max_retries"`
		HealthCheckInterval time.Duration `mapstructure:"health_check_interval"`
	} `mapstructure:"flexcore"`

	Python struct {
		MeltanoProjectRoot string        `mapstructure:"meltano_project_root"`
		VirtualEnv         string        `mapstructure:"virtual_env"`
		RequirementsFile   string        `mapstructure:"requirements_file"`
		Timeout            time.Duration `mapstructure:"timeout"`
	} `mapstructure:"python"`

	Logging struct {
		Level          string `mapstructure:"level"`
		Format         string `mapstructure:"format"`
		Output         string `mapstructure:"output"`
		CorrelationIDs bool   `mapstructure:"correlation_ids"`
	} `mapstructure:"logging"`
}

// LoadConfig loads configuration from file path
func LoadConfig(configPath string) (*Config, error) {
	v := viper.New()

	// Set configuration sources
	v.SetConfigName("settings")
	v.SetConfigType("yaml")

	if configPath != "" {
		// Use specific settings file if provided
		v.SetConfigFile(configPath)
	} else {
		// Add default settings paths
		v.AddConfigPath(".")
		v.AddConfigPath("./settings")
		v.AddConfigPath("/etc/flext/")
	}

	// Environment variables (12-factor app)
	v.SetEnvPrefix("FLEXT")
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	v.AutomaticEnv()

	// Set defaults
	setDefaults(v)

	// Read settings file
	if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("error reading settings file: %w", err)
		}
		// Config file not found is OK, we'll use defaults and env vars
	}

	// Unmarshal into struct
	settings := &Config{}
	if err := v.Unmarshal(settings); err != nil {
		return nil, fmt.Errorf("error unmarshaling settings: %w", err)
	}

	// Validate configuration
	if err := validateConfig(settings); err != nil {
		return nil, fmt.Errorf("configuration validation failed: %w", err)
	}

	return settings, nil
}

// setDefaults sets default configuration values
func setDefaults(v *viper.Viper) {
	// Server defaults
	v.SetDefault("server.host", "0.0.0.0")
	v.SetDefault("server.port", 8081)
	v.SetDefault("server.environment", "development")
	v.SetDefault("server.debug", true)

	// Database defaults
	v.SetDefault("database.url", "postgresql://localhost:5433/flext")
	v.SetDefault("database.max_connections", 20)
	v.SetDefault("database.conn_max_lifetime", "1h")

	// Redis defaults
	v.SetDefault("redis.url", "redis://localhost:6380")
	v.SetDefault("redis.pool_size", 10)
	v.SetDefault("redis.max_retries", 3)

	// FlexCore defaults
	v.SetDefault("flexcore.url", "http://localhost:8080")
	v.SetDefault("flexcore.timeout", "30s")
	v.SetDefault("flexcore.max_retries", 3)
	v.SetDefault("flexcore.health_check_interval", "30s")

	// Python defaults
	v.SetDefault("python.meltano_project_root", "./meltano_project")
	v.SetDefault("python.virtual_env", "./venv")
	v.SetDefault("python.requirements_file", "requirements.txt")
	v.SetDefault("python.timeout", "300s")

	// Logging defaults
	v.SetDefault("logging.level", "info")
	v.SetDefault("logging.format", "json")
	v.SetDefault("logging.output", "stdout")
	v.SetDefault("logging.correlation_ids", true)
}

// validateConfig validates the configuration
func validateConfig(settings *Config) error {
	if settings.Server.Port <= 0 || settings.Server.Port > 65535 {
		return fmt.Errorf("server.port must be between 1 and 65535")
	}

	if settings.Server.Environment == "" {
		return fmt.Errorf("server.environment cannot be empty")
	}

	// Validate database URL
	if settings.Database.URL == "" {
		return fmt.Errorf("database.url cannot be empty")
	}

	return nil
}
