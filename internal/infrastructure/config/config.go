package config

import (
	"fmt"
	"log"
	"net"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/kelseyhightower/envconfig"
	"github.com/spf13/viper"
)

// Config represents the application configuration
type Config struct {
	Server     ServerConfig     `mapstructure:"server" envconfig:"SERVER"`
	Database   DatabaseConfig   `mapstructure:"database" envconfig:"DATABASE"`
	Redis      RedisConfig      `mapstructure:"redis" envconfig:"REDIS"`
	JWT        JWTConfig        `mapstructure:"jwt" envconfig:"JWT"`
	WebSocket  WebSocketConfig  `mapstructure:"websocket" envconfig:"WEBSOCKET"`
	Monitoring MonitoringConfig `mapstructure:"monitoring" envconfig:"MONITORING"`
	Logging    LoggingConfig    `mapstructure:"logging" envconfig:"LOGGING"`
	Features   FeatureFlags     `mapstructure:"features" envconfig:"FEATURES"`
	
	// Clean Architecture configuration
	CleanArchitecture CleanArchitectureConfig `mapstructure:"clean_architecture" envconfig:"CLEAN_ARCHITECTURE"`
}

// ServerConfig contains HTTP server configuration
type ServerConfig struct {
	Host            string        `mapstructure:"host" envconfig:"HOST" default:"0.0.0.0"`
	Port            int           `mapstructure:"port" envconfig:"PORT" default:"8081"`
	ReadTimeout     time.Duration `mapstructure:"read_timeout" envconfig:"READ_TIMEOUT" default:"30s"`
	WriteTimeout    time.Duration `mapstructure:"write_timeout" envconfig:"WRITE_TIMEOUT" default:"30s"`
	IdleTimeout     time.Duration `mapstructure:"idle_timeout" envconfig:"IDLE_TIMEOUT" default:"120s"`
	MaxHeaderBytes  int           `mapstructure:"max_header_bytes" envconfig:"MAX_HEADER_BYTES" default:"1048576"`
	Environment     string        `mapstructure:"environment" envconfig:"ENVIRONMENT" default:"development"`
	Debug           bool          `mapstructure:"debug" envconfig:"DEBUG" default:"false"`
	EnableCORS      bool          `mapstructure:"enable_cors" envconfig:"ENABLE_CORS" default:"true"`
	ShutdownTimeout time.Duration `mapstructure:"shutdown_timeout" envconfig:"SHUTDOWN_TIMEOUT" default:"30s"`
}

// DatabaseConfig contains database connection configuration
type DatabaseConfig struct {
	Driver          string        `json:"driver" mapstructure:"driver"`
	Host            string        `json:"host" mapstructure:"host"`
	Port            int           `json:"port" mapstructure:"port"`
	Database        string        `json:"database" mapstructure:"database"`
	Username        string        `json:"username" mapstructure:"username"`
	Password        string        `json:"password" mapstructure:"password"`
	SSLMode         string        `json:"ssl_mode" mapstructure:"ssl_mode"`
	MaxOpenConns    int           `json:"max_open_conns" mapstructure:"max_open_conns"`
	MaxIdleConns    int           `json:"max_idle_conns" mapstructure:"max_idle_conns"`
	ConnMaxLifetime time.Duration `json:"conn_max_lifetime" mapstructure:"conn_max_lifetime"`
	ConnMaxIdleTime time.Duration `json:"conn_max_idle_time" mapstructure:"conn_max_idle_time"`
}

// JWTConfig contains JWT token configuration
type JWTConfig struct {
	SecretKey     string        `json:"secret_key" mapstructure:"secret_key"`
	ExpiryTime    time.Duration `json:"expiry_time" mapstructure:"expiry_time"`
	RefreshTime   time.Duration `json:"refresh_time" mapstructure:"refresh_time"`
	Issuer        string        `json:"issuer" mapstructure:"issuer"`
	Audience      string        `json:"audience" mapstructure:"audience"`
	SigningMethod string        `json:"signing_method" mapstructure:"signing_method"`
}

// WebSocketConfig contains WebSocket configuration
type WebSocketConfig struct {
	ReadBufferSize    int           `json:"read_buffer_size" mapstructure:"read_buffer_size"`
	WriteBufferSize   int           `json:"write_buffer_size" mapstructure:"write_buffer_size"`
	HandshakeTimeout  time.Duration `json:"handshake_timeout" mapstructure:"handshake_timeout"`
	PingPeriod        time.Duration `json:"ping_period" mapstructure:"ping_period"`
	PongWait          time.Duration `json:"pong_wait" mapstructure:"pong_wait"`
	WriteWait         time.Duration `json:"write_wait" mapstructure:"write_wait"`
	MaxMessageSize    int64         `json:"max_message_size" mapstructure:"max_message_size"`
	MaxConcurrentConn int           `json:"max_concurrent_conn" mapstructure:"max_concurrent_conn"`
}

// MonitoringConfig contains monitoring and metrics configuration
type MonitoringConfig struct {
	Enabled            bool          `json:"enabled" mapstructure:"enabled"`
	MetricsPath        string        `json:"metrics_path" mapstructure:"metrics_path"`
	HealthPath         string        `json:"health_path" mapstructure:"health_path"`
	CollectionInterval time.Duration `json:"collection_interval" mapstructure:"collection_interval"`
	RetentionPeriod    time.Duration `json:"retention_period" mapstructure:"retention_period"`
	AlertingEnabled    bool          `json:"alerting_enabled" mapstructure:"alerting_enabled"`
	ErrorThreshold     float64       `json:"error_threshold" mapstructure:"error_threshold"`
}

// LoggingConfig contains logging configuration
type LoggingConfig struct {
	Level      string `json:"level" mapstructure:"level"`
	Format     string `json:"format" mapstructure:"format"`
	Output     string `json:"output" mapstructure:"output"`
	Structured bool   `json:"structured" mapstructure:"structured"`
}

// FeatureFlags contains feature toggle configuration
type FeatureFlags struct {
	WebSocketEnabled    bool `json:"websocket_enabled" mapstructure:"websocket_enabled"`
	MetricsEnabled      bool `json:"metrics_enabled" mapstructure:"metrics_enabled"`
	SwaggerEnabled      bool `json:"swagger_enabled" mapstructure:"swagger_enabled"`
	DatabaseEnabled     bool `json:"database_enabled" mapstructure:"database_enabled"`
	AuthRequired        bool `json:"auth_required" mapstructure:"auth_required"`
	PluginSystemEnabled bool `json:"plugin_system_enabled" mapstructure:"plugin_system_enabled"`
	PipelineExecution   bool `json:"pipeline_execution" mapstructure:"pipeline_execution"`
	RedisEnabled        bool `json:"redis_enabled" mapstructure:"redis_enabled"`
	GormEnabled         bool `json:"gorm_enabled" mapstructure:"gorm_enabled"`
	SqlxEnabled         bool `json:"sqlx_enabled" mapstructure:"sqlx_enabled"`
	GinServerEnabled    bool `json:"gin_server_enabled" mapstructure:"gin_server_enabled"`
}

// RedisConfig contains Redis cache configuration
type RedisConfig struct {
	Host         string        `mapstructure:"host" envconfig:"REDIS_HOST" default:"localhost"`
	Port         int           `mapstructure:"port" envconfig:"REDIS_PORT" default:"6379"`
	Password     string        `mapstructure:"password" envconfig:"REDIS_PASSWORD"`
	Database     int           `mapstructure:"database" envconfig:"REDIS_DATABASE" default:"0"`
	PoolSize     int           `mapstructure:"pool_size" envconfig:"REDIS_POOL_SIZE" default:"10"`
	MinIdleConns int           `mapstructure:"min_idle_conns" envconfig:"REDIS_MIN_IDLE_CONNS" default:"5"`
	MaxRetries   int           `mapstructure:"max_retries" envconfig:"REDIS_MAX_RETRIES" default:"3"`
	DialTimeout  time.Duration `mapstructure:"dial_timeout" envconfig:"REDIS_DIAL_TIMEOUT" default:"5s"`
	ReadTimeout  time.Duration `mapstructure:"read_timeout" envconfig:"REDIS_READ_TIMEOUT" default:"3s"`
	WriteTimeout time.Duration `mapstructure:"write_timeout" envconfig:"REDIS_WRITE_TIMEOUT" default:"3s"`
	IdleTimeout  time.Duration `mapstructure:"idle_timeout" envconfig:"REDIS_IDLE_TIMEOUT" default:"5m"`
}

// Address returns Redis address
func (r RedisConfig) Address() string {
	return fmt.Sprintf("%s:%d", r.Host, r.Port)
}

// DefaultConfig returns a configuration with sensible defaults and advanced features enabled
func DefaultConfig() *Config {
	return &Config{
		Server: ServerConfig{
			Host:            "0.0.0.0",
			Port:            8081,
			ReadTimeout:     30 * time.Second,
			WriteTimeout:    30 * time.Second,
			IdleTimeout:     120 * time.Second,
			MaxHeaderBytes:  1 << 20, // 1MB
			Environment:     "development",
			Debug:           false,
			EnableCORS:      true,
			ShutdownTimeout: 30 * time.Second,
		},
		Database: DatabaseConfig{
			Driver:          "postgres", // Enable PostgreSQL by default for production readiness
			Host:            "localhost",
			Port:            5432,
			Database:        "flext_db",
			Username:        "flext",
			Password:        "flext",
			SSLMode:         "disable",
			MaxOpenConns:    25,
			MaxIdleConns:    25,
			ConnMaxLifetime: 5 * time.Minute,
			ConnMaxIdleTime: 5 * time.Minute,
		},
		JWT: JWTConfig{
			SecretKey:     "default-development-jwt-secret-key-32-chars-minimum-required",
			ExpiryTime:    24 * time.Hour,
			RefreshTime:   7 * 24 * time.Hour,
			Issuer:        "flext-api",
			Audience:      "flext-users",
			SigningMethod: "HS256",
		},
		WebSocket: WebSocketConfig{
			ReadBufferSize:    1024,
			WriteBufferSize:   1024,
			HandshakeTimeout:  10 * time.Second,
			PingPeriod:        54 * time.Second,
			PongWait:          60 * time.Second,
			WriteWait:         10 * time.Second,
			MaxMessageSize:    512,
			MaxConcurrentConn: 100,
		},
		Monitoring: MonitoringConfig{
			Enabled:            true,
			MetricsPath:        "/metrics",
			HealthPath:         "/health",
			CollectionInterval: 15 * time.Second,
			RetentionPeriod:    24 * time.Hour,
			AlertingEnabled:    false,
			ErrorThreshold:     0.05, // 5% error rate
		},
		Logging: LoggingConfig{
			Level:      "info",
			Format:     "json",
			Output:     "stdout",
			Structured: true,
		},
		Redis: RedisConfig{
			Host:         "localhost",
			Port:         6379,
			Password:     "",
			Database:     0,
			PoolSize:     10,
			MinIdleConns: 5,
			MaxRetries:   3,
			DialTimeout:  5 * time.Second,
			ReadTimeout:  3 * time.Second,
			WriteTimeout: 3 * time.Second,
			IdleTimeout:  5 * time.Minute,
		},
		Features: FeatureFlags{
			WebSocketEnabled:    true,
			MetricsEnabled:      true,
			SwaggerEnabled:      true,
			DatabaseEnabled:     true, // Enable database for production readiness
			AuthRequired:        false, // Default to no auth for development
			PluginSystemEnabled: true,
			PipelineExecution:   true,
			RedisEnabled:        false, // Disable Redis by default for easier setup
			GormEnabled:         true, // Enable GORM for production readiness
			SqlxEnabled:         true, // Enable SQLX for production readiness
			GinServerEnabled:    false, // Keep Gin disabled to avoid conflicts
		},
	}
}

// LoadConfig loads configuration using Viper and envconfig
func LoadConfig(configPath string) (*Config, error) {
	var config Config

	// Configure Viper
	viper.SetConfigType("yaml")
	viper.SetConfigName("config")
	viper.AddConfigPath(".")
	viper.AddConfigPath("./config")
	viper.AddConfigPath("/etc/flext")
	
	if configPath != "" {
		viper.SetConfigFile(configPath)
	}

	// Set environment variable prefix
	viper.SetEnvPrefix("FLEXT")
	viper.AutomaticEnv()

	// Read config file (optional)
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("failed to read config file: %w", err)
		}
	}

	// Set defaults from DefaultConfig
	defaults := DefaultConfig()
	setViperDefaults(defaults)

	// Unmarshal Viper config
	if err := viper.Unmarshal(&config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	// Process environment variables with envconfig
	if err := envconfig.Process("FLEXT", &config); err != nil {
		return nil, fmt.Errorf("failed to process environment variables: %w", err)
	}

	// Override with direct environment variables for better Docker compatibility
	processDirectEnvVars(&config)

	// Initialize Clean Architecture configuration
	config.CleanArchitecture = *NewCleanArchitectureConfig()

	// Validate configuration
	if err := config.Validate(); err != nil {
		return nil, fmt.Errorf("configuration validation failed: %w", err)
	}
	
	// Validate Clean Architecture configuration
	if err := config.CleanArchitecture.Validate(); err != nil {
		return nil, fmt.Errorf("clean architecture configuration validation failed: %w", err)
	}

	return &config, nil
}

// processDirectEnvVars handles direct environment variable overrides for Docker compatibility
func processDirectEnvVars(config *Config) {
	// Server configuration
	if port := os.Getenv("FLEXT_PORT"); port != "" {
		if p, err := strconv.Atoi(port); err == nil {
			config.Server.Port = p
		}
	}
	if host := os.Getenv("FLEXT_HOST"); host != "" {
		config.Server.Host = host
	}
	if logLevel := os.Getenv("FLEXT_LOG_LEVEL"); logLevel != "" {
		config.Logging.Level = logLevel
	}

	// Database configuration
	if dbType := os.Getenv("FLEXT_DB_TYPE"); dbType != "" {
		if dbType == "postgres" {
			config.Features.DatabaseEnabled = true
			config.Database.Driver = "postgres"
		} else {
			config.Features.DatabaseEnabled = false
		}
	}
	if dbURL := os.Getenv("FLEXT_DB_URL"); dbURL != "" {
		parsePostgresURL(dbURL, &config.Database)
		config.Features.DatabaseEnabled = true
	}

	// JWT configuration
	if jwtSecret := os.Getenv("JWT_SECRET_KEY"); jwtSecret != "" {
		config.JWT.SecretKey = jwtSecret
	}

	// Feature flags configuration
	if dbEnabled := os.Getenv("FLEXT_FEATURES_DATABASE_ENABLED"); dbEnabled != "" {
		config.Features.DatabaseEnabled = strings.ToLower(dbEnabled) == "true"
	}
	if redisEnabled := os.Getenv("FLEXT_FEATURES_REDIS_ENABLED"); redisEnabled != "" {
		config.Features.RedisEnabled = strings.ToLower(redisEnabled) == "true"
	}
	if gormEnabled := os.Getenv("FLEXT_FEATURES_GORM_ENABLED"); gormEnabled != "" {
		config.Features.GormEnabled = strings.ToLower(gormEnabled) == "true"
	}
	if sqlxEnabled := os.Getenv("FLEXT_FEATURES_SQLX_ENABLED"); sqlxEnabled != "" {
		config.Features.SqlxEnabled = strings.ToLower(sqlxEnabled) == "true"
	}
}

// LoadFromEnv loads configuration from environment variables (backward compatibility)
func LoadFromEnv() *Config {
	config, err := LoadConfig("")
	if err != nil {
		// Fallback to DefaultConfig if LoadConfig fails
		return DefaultConfig()
	}
	return config
}

// setViperDefaults sets default values in Viper from DefaultConfig
func setViperDefaults(defaults *Config) {
	viper.SetDefault("server.host", defaults.Server.Host)
	viper.SetDefault("server.port", defaults.Server.Port)
	viper.SetDefault("server.read_timeout", defaults.Server.ReadTimeout)
	viper.SetDefault("server.write_timeout", defaults.Server.WriteTimeout)
	viper.SetDefault("server.idle_timeout", defaults.Server.IdleTimeout)
	viper.SetDefault("server.max_header_bytes", defaults.Server.MaxHeaderBytes)
	viper.SetDefault("server.environment", defaults.Server.Environment)
	viper.SetDefault("server.debug", defaults.Server.Debug)
	viper.SetDefault("server.enable_cors", defaults.Server.EnableCORS)
	viper.SetDefault("server.shutdown_timeout", defaults.Server.ShutdownTimeout)

	viper.SetDefault("database.driver", defaults.Database.Driver)
	viper.SetDefault("database.host", defaults.Database.Host)
	viper.SetDefault("database.port", defaults.Database.Port)
	viper.SetDefault("database.database", defaults.Database.Database)
	viper.SetDefault("database.username", defaults.Database.Username)
	viper.SetDefault("database.password", defaults.Database.Password)
	viper.SetDefault("database.ssl_mode", defaults.Database.SSLMode)
	viper.SetDefault("database.max_open_conns", defaults.Database.MaxOpenConns)
	viper.SetDefault("database.max_idle_conns", defaults.Database.MaxIdleConns)
	viper.SetDefault("database.conn_max_lifetime", defaults.Database.ConnMaxLifetime)
	viper.SetDefault("database.conn_max_idle_time", defaults.Database.ConnMaxIdleTime)

	viper.SetDefault("jwt.secret_key", defaults.JWT.SecretKey)
	viper.SetDefault("jwt.expiry_time", defaults.JWT.ExpiryTime)
	viper.SetDefault("jwt.refresh_time", defaults.JWT.RefreshTime)
	viper.SetDefault("jwt.issuer", defaults.JWT.Issuer)
	viper.SetDefault("jwt.audience", defaults.JWT.Audience)
	viper.SetDefault("jwt.signing_method", defaults.JWT.SigningMethod)

	viper.SetDefault("features.websocket_enabled", defaults.Features.WebSocketEnabled)
	viper.SetDefault("features.metrics_enabled", defaults.Features.MetricsEnabled)
	viper.SetDefault("features.swagger_enabled", defaults.Features.SwaggerEnabled)
	viper.SetDefault("features.database_enabled", defaults.Features.DatabaseEnabled)
	viper.SetDefault("features.auth_required", defaults.Features.AuthRequired)
	viper.SetDefault("features.plugin_system_enabled", defaults.Features.PluginSystemEnabled)
	viper.SetDefault("features.pipeline_execution", defaults.Features.PipelineExecution)
}

// Validate validates the configuration
func (c *Config) Validate() error {
	if c.Server.Port < 1 || c.Server.Port > 65535 {
		return fmt.Errorf("invalid server port: %d", c.Server.Port)
	}

	if c.Database.Port < 1 || c.Database.Port > 65535 {
		return fmt.Errorf("invalid database port: %d", c.Database.Port)
	}

	if c.JWT.SecretKey == "" {
		return fmt.Errorf("JWT secret key is required")
	}

	if len(c.JWT.SecretKey) < 32 {
		return fmt.Errorf("JWT secret key must be at least 32 characters long")
	}

	if c.Features.DatabaseEnabled {
		if c.Database.Host == "" {
			return fmt.Errorf("database host is required when database is enabled")
		}
		if c.Database.Database == "" {
			return fmt.Errorf("database name is required when database is enabled")
		}
		if c.Database.Username == "" {
			return fmt.Errorf("database username is required when database is enabled")
		}
	}

	return nil
}

// Address returns the server address string with smart port resolution
func (c *Config) Address() string {
	port := c.GetAvailablePort()
	return fmt.Sprintf("%s:%d", c.Server.Host, port)
}

// GetAvailablePort returns an available port, resolving conflicts automatically
func (c *Config) GetAvailablePort() int {
	// Check if current port is available
	if c.isPortAvailable(c.Server.Port) {
		return c.Server.Port
	}
	
	// Find alternative port
	port := c.findAvailablePort(c.Server.Port)
	if port != c.Server.Port {
		log.Printf("Port conflict resolved: requested_port=%d, assigned_port=%d", c.Server.Port, port)
		c.Server.Port = port // Update config with available port
	}
	
	return port
}

// isPortAvailable checks if a port is available for binding
func (c *Config) isPortAvailable(port int) bool {
	address := fmt.Sprintf("%s:%d", c.Server.Host, port)
	listener, err := net.Listen("tcp", address)
	if err != nil {
		return false
	}
	listener.Close()
	return true
}

// findAvailablePort finds an available port starting from the given port
func (c *Config) findAvailablePort(startPort int) int {
	for port := startPort; port <= startPort+100; port++ {
		if c.isPortAvailable(port) {
			return port
		}
	}
	
	// If no port found in range, try system-assigned port
	listener, err := net.Listen("tcp", ":0")
	if err != nil {
		// Fallback to a high port number
		return 8080
	}
	defer listener.Close()
	
	addr := listener.Addr().(*net.TCPAddr)
	return addr.Port
}

// DatabaseURL returns the database connection URL
func (c *Config) DatabaseURL() string {
	return fmt.Sprintf("postgres://%s:%s@%s:%d/%s?sslmode=%s",
		c.Database.Username,
		c.Database.Password,
		c.Database.Host,
		c.Database.Port,
		c.Database.Database,
		c.Database.SSLMode,
	)
}

// IsProduction returns true if running in production environment
func (c *Config) IsProduction() bool {
	return strings.ToLower(c.Server.Environment) == "production"
}

// IsDevelopment returns true if running in development environment
func (c *Config) IsDevelopment() bool {
	return strings.ToLower(c.Server.Environment) == "development"
}

// IsTest returns true if running in test environment
func (c *Config) IsTest() bool {
	return strings.ToLower(c.Server.Environment) == "test"
}

// GetEnvWithDefault gets an environment variable with a default value
func (c *Config) GetEnvWithDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// parsePostgresURL parses a PostgreSQL URL and updates database config
func parsePostgresURL(url string, dbConfig *DatabaseConfig) {
	if !strings.HasPrefix(url, "postgres://") {
		return
	}

	url = strings.TrimPrefix(url, "postgres://")
	
	// Split credentials and connection parts
	parts := strings.SplitN(url, "@", 2)
	if len(parts) != 2 {
		return
	}

	// Parse credentials
	credentials := parts[0]
	if strings.Contains(credentials, ":") {
		credParts := strings.SplitN(credentials, ":", 2)
		dbConfig.Username = credParts[0]
		dbConfig.Password = credParts[1]
	} else {
		dbConfig.Username = credentials
	}

	// Parse connection details
	connection := parts[1]
	
	// Split database and query parameters
	connParts := strings.SplitN(connection, "?", 2)
	hostDatabase := connParts[0]
	
	// Parse query parameters
	if len(connParts) == 2 {
		queryParams := connParts[1]
		if strings.Contains(queryParams, "sslmode=") {
			for _, param := range strings.Split(queryParams, "&") {
				if strings.HasPrefix(param, "sslmode=") {
					dbConfig.SSLMode = strings.TrimPrefix(param, "sslmode=")
				}
			}
		}
	}

	// Parse host, port, and database
	if strings.Contains(hostDatabase, "/") {
		hostPortDatabase := strings.SplitN(hostDatabase, "/", 2)
		hostPort := hostPortDatabase[0]
		dbConfig.Database = hostPortDatabase[1]

		// Parse host and port
		if strings.Contains(hostPort, ":") {
			hostPortParts := strings.SplitN(hostPort, ":", 2)
			dbConfig.Host = hostPortParts[0]
			if port, err := strconv.Atoi(hostPortParts[1]); err == nil {
				dbConfig.Port = port
			}
		} else {
			dbConfig.Host = hostPort
			dbConfig.Port = 5432 // Default PostgreSQL port
		}
	}
}
