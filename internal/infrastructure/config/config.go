package config

import (
	"os"
	"strconv"
	"time"
)

// Config representa a configuração da aplicação
type Config struct {
	Server   ServerConfig   `json:"server"`
	Database DatabaseConfig `json:"database"`
	Logging  LoggingConfig  `json:"logging"`
	Events   EventsConfig   `json:"events"`
}

// ServerConfig configurações do servidor HTTP
type ServerConfig struct {
	Host            string        `json:"host"`
	Port            string        `json:"port"`
	ReadTimeout     time.Duration `json:"read_timeout"`
	WriteTimeout    time.Duration `json:"write_timeout"`
	ShutdownTimeout time.Duration `json:"shutdown_timeout"`
	EnableCORS      bool          `json:"enable_cors"`
}

// DatabaseConfig configurações de banco de dados
type DatabaseConfig struct {
	Type     string `json:"type"`
	Host     string `json:"host"`
	Port     string `json:"port"`
	Database string `json:"database"`
	Username string `json:"username"`
	Password string `json:"password"`
	SSLMode  string `json:"ssl_mode"`
}

// LoggingConfig configurações de logging
type LoggingConfig struct {
	Level      string `json:"level"`
	Format     string `json:"format"`
	Output     string `json:"output"`
	Structured bool   `json:"structured"`
}

// EventsConfig configurações do sistema de eventos
type EventsConfig struct {
	Publisher string `json:"publisher"`
	Buffer    int    `json:"buffer"`
	Workers   int    `json:"workers"`
}

// LoadConfig carrega configurações do ambiente
func LoadConfig() *Config {
	return &Config{
		Server: ServerConfig{
			Host:            getEnv("FLEXT_SERVER_HOST", "0.0.0.0"),
			Port:            getEnv("FLEXT_SERVER_PORT", "8081"),
			ReadTimeout:     getDurationEnv("FLEXT_SERVER_READ_TIMEOUT", 30*time.Second),
			WriteTimeout:    getDurationEnv("FLEXT_SERVER_WRITE_TIMEOUT", 30*time.Second),
			ShutdownTimeout: getDurationEnv("FLEXT_SERVER_SHUTDOWN_TIMEOUT", 30*time.Second),
			EnableCORS:      getBoolEnv("FLEXT_SERVER_ENABLE_CORS", true),
		},
		Database: DatabaseConfig{
			Type:     getEnv("FLEXT_DB_TYPE", "memory"),
			Host:     getEnv("FLEXT_DB_HOST", "localhost"),
			Port:     getEnv("FLEXT_DB_PORT", "5432"),
			Database: getEnv("FLEXT_DB_NAME", "flext"),
			Username: getEnv("FLEXT_DB_USERNAME", "flext"),
			Password: getEnv("FLEXT_DB_PASSWORD", ""),
			SSLMode:  getEnv("FLEXT_DB_SSL_MODE", "disable"),
		},
		Logging: LoggingConfig{
			Level:      getEnv("FLEXT_LOG_LEVEL", "info"),
			Format:     getEnv("FLEXT_LOG_FORMAT", "json"),
			Output:     getEnv("FLEXT_LOG_OUTPUT", "stdout"),
			Structured: getBoolEnv("FLEXT_LOG_STRUCTURED", true),
		},
		Events: EventsConfig{
			Publisher: getEnv("FLEXT_EVENTS_PUBLISHER", "memory"),
			Buffer:    getIntEnv("FLEXT_EVENTS_BUFFER", 1000),
			Workers:   getIntEnv("FLEXT_EVENTS_WORKERS", 4),
		},
	}
}

// Helper functions para parsing de environment variables

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getBoolEnv(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if parsed, err := strconv.ParseBool(value); err == nil {
			return parsed
		}
	}
	return defaultValue
}

func getIntEnv(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if parsed, err := strconv.Atoi(value); err == nil {
			return parsed
		}
	}
	return defaultValue
}

func getDurationEnv(key string, defaultValue time.Duration) time.Duration {
	if value := os.Getenv(key); value != "" {
		if parsed, err := time.ParseDuration(value); err == nil {
			return parsed
		}
	}
	return defaultValue
}