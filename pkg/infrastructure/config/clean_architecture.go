package config

import (
	"fmt"
	"time"
)

// CleanArchitectureConfig contains configuration for Clean Architecture components
type CleanArchitectureConfig struct {
	Enabled bool `mapstructure:"enabled" envconfig:"ENABLED" default:"true"`

	// Repository configurations
	Repository RepositoryConfig `mapstructure:"repository" envconfig:"REPOSITORY"`

	// Use case configurations
	UseCase UseCaseConfig `mapstructure:"usecase" envconfig:"USECASE"`

	// Event configurations
	Events EventConfig `mapstructure:"events" envconfig:"EVENTS"`

	// HTTP API configurations
	API APIConfig `mapstructure:"api" envconfig:"API"`

	// Performance configurations
	Performance PerformanceConfig `mapstructure:"performance" envconfig:"PERFORMANCE"`
}

// RepositoryConfig contains repository-specific configuration
type RepositoryConfig struct {
	// Connection pool settings
	MaxOpenConnections    int           `mapstructure:"max_open_connections" envconfig:"MAX_OPEN_CONNECTIONS" default:"25"`
	MaxIdleConnections    int           `mapstructure:"max_idle_connections" envconfig:"MAX_IDLE_CONNECTIONS" default:"25"`
	ConnectionMaxLifetime time.Duration `mapstructure:"connection_max_lifetime" envconfig:"CONNECTION_MAX_LIFETIME" default:"5m"`
	ConnectionMaxIdleTime time.Duration `mapstructure:"connection_max_idle_time" envconfig:"CONNECTION_MAX_IDLE_TIME" default:"5m"`

	// Query timeouts
	QueryTimeout       time.Duration `mapstructure:"query_timeout" envconfig:"QUERY_TIMEOUT" default:"30s"`
	TransactionTimeout time.Duration `mapstructure:"transaction_timeout" envconfig:"TRANSACTION_TIMEOUT" default:"60s"`

	// Retry settings
	MaxRetries    int           `mapstructure:"max_retries" envconfig:"MAX_RETRIES" default:"3"`
	RetryInterval time.Duration `mapstructure:"retry_interval" envconfig:"RETRY_INTERVAL" default:"1s"`

	// Health check settings
	HealthCheckInterval time.Duration `mapstructure:"health_check_interval" envconfig:"HEALTH_CHECK_INTERVAL" default:"30s"`
	HealthCheckTimeout  time.Duration `mapstructure:"health_check_timeout" envconfig:"HEALTH_CHECK_TIMEOUT" default:"5s"`
}

// UseCaseConfig contains use case-specific configuration
type UseCaseConfig struct {
	// Execution timeouts
	DefaultTimeout     time.Duration `mapstructure:"default_timeout" envconfig:"DEFAULT_TIMEOUT" default:"30s"`
	LongRunningTimeout time.Duration `mapstructure:"long_running_timeout" envconfig:"LONG_RUNNING_TIMEOUT" default:"5m"`

	// Validation settings
	ValidationEnabled bool `mapstructure:"validation_enabled" envconfig:"VALIDATION_ENABLED" default:"true"`
	StrictValidation  bool `mapstructure:"strict_validation" envconfig:"STRICT_VALIDATION" default:"false"`

	// Concurrency settings
	MaxConcurrentExecutions int `mapstructure:"max_concurrent_executions" envconfig:"MAX_CONCURRENT_EXECUTIONS" default:"10"`
	WorkerPoolSize          int `mapstructure:"worker_pool_size" envconfig:"WORKER_POOL_SIZE" default:"5"`

	// Rate limiting
	RateLimitEnabled bool `mapstructure:"rate_limit_enabled" envconfig:"RATE_LIMIT_ENABLED" default:"false"`
	RateLimitRPS     int  `mapstructure:"rate_limit_rps" envconfig:"RATE_LIMIT_RPS" default:"100"`
}

// EventConfig contains event system configuration
type EventConfig struct {
	// Event publishing
	PublishingEnabled bool `mapstructure:"publishing_enabled" envconfig:"PUBLISHING_ENABLED" default:"true"`
	Publishing        bool `mapstructure:"publishing" envconfig:"PUBLISHING" default:"true"`

	// Buffer settings
	BufferSize     int           `mapstructure:"buffer_size" envconfig:"BUFFER_SIZE" default:"1000"`
	FlushInterval  time.Duration `mapstructure:"flush_interval" envconfig:"FLUSH_INTERVAL" default:"1s"`
	PublishTimeout time.Duration `mapstructure:"publish_timeout" envconfig:"PUBLISH_TIMEOUT" default:"5s"`

	// Retry settings
	MaxRetries    int           `mapstructure:"max_retries" envconfig:"MAX_RETRIES" default:"3"`
	RetryInterval time.Duration `mapstructure:"retry_interval" envconfig:"RETRY_INTERVAL" default:"1s"`

	// Dead letter queue
	DeadLetterEnabled bool          `mapstructure:"dead_letter_enabled" envconfig:"DEAD_LETTER_ENABLED" default:"true"`
	DeadLetterTTL     time.Duration `mapstructure:"dead_letter_ttl" envconfig:"DEAD_LETTER_TTL" default:"24h"`
}

// APIConfig contains API-specific configuration
type APIConfig struct {
	// Request handling
	MaxRequestSize    int64         `mapstructure:"max_request_size" envconfig:"MAX_REQUEST_SIZE" default:"10485760"` // 10MB
	RequestTimeout    time.Duration `mapstructure:"request_timeout" envconfig:"REQUEST_TIMEOUT" default:"30s"`
	ReadHeaderTimeout time.Duration `mapstructure:"read_header_timeout" envconfig:"READ_HEADER_TIMEOUT" default:"10s"`

	// Response settings
	EnableCompression bool          `mapstructure:"enable_compression" envconfig:"ENABLE_COMPRESSION" default:"true"`
	EnableCaching     bool          `mapstructure:"enable_caching" envconfig:"ENABLE_CACHING" default:"false"`
	CacheTTL          time.Duration `mapstructure:"cache_ttl" envconfig:"CACHE_TTL" default:"5m"`

	// Pagination defaults
	DefaultPageSize int `mapstructure:"default_page_size" envconfig:"DEFAULT_PAGE_SIZE" default:"10"`
	MaxPageSize     int `mapstructure:"max_page_size" envconfig:"MAX_PAGE_SIZE" default:"1000"`

	// CORS settings for Clean Architecture endpoints
	CORSEnabled          bool     `mapstructure:"cors_enabled" envconfig:"CORS_ENABLED" default:"true"`
	CORSAllowedOrigins   []string `mapstructure:"cors_allowed_origins" envconfig:"CORS_ALLOWED_ORIGINS"`
	CORSAllowedMethods   []string `mapstructure:"cors_allowed_methods" envconfig:"CORS_ALLOWED_METHODS"`
	CORSAllowedHeaders   []string `mapstructure:"cors_allowed_headers" envconfig:"CORS_ALLOWED_HEADERS"`
	CORSExposedHeaders   []string `mapstructure:"cors_exposed_headers" envconfig:"CORS_EXPOSED_HEADERS"`
	CORSAllowCredentials bool     `mapstructure:"cors_allow_credentials" envconfig:"CORS_ALLOW_CREDENTIALS" default:"false"`
	CORSMaxAge           int      `mapstructure:"cors_max_age" envconfig:"CORS_MAX_AGE" default:"86400"`
}

// PerformanceConfig contains performance-related settings
type PerformanceConfig struct {
	// Metrics collection
	MetricsEnabled  bool          `mapstructure:"metrics_enabled" envconfig:"METRICS_ENABLED" default:"true"`
	MetricsInterval time.Duration `mapstructure:"metrics_interval" envconfig:"METRICS_INTERVAL" default:"15s"`
	DetailedMetrics bool          `mapstructure:"detailed_metrics" envconfig:"DETAILED_METRICS" default:"false"`

	// Tracing
	TracingEnabled    bool    `mapstructure:"tracing_enabled" envconfig:"TRACING_ENABLED" default:"false"`
	TracingSampleRate float64 `mapstructure:"tracing_sample_rate" envconfig:"TRACING_SAMPLE_RATE" default:"0.1"`
	TracingEndpoint   string  `mapstructure:"tracing_endpoint" envconfig:"TRACING_ENDPOINT"`

	// Profiling
	ProfilingEnabled bool   `mapstructure:"profiling_enabled" envconfig:"PROFILING_ENABLED" default:"false"`
	ProfilingHost    string `mapstructure:"profiling_host" envconfig:"PROFILING_HOST" default:"localhost"`
	ProfilingPort    int    `mapstructure:"profiling_port" envconfig:"PROFILING_PORT" default:"6060"`

	// Circuit breaker
	CircuitBreakerEnabled   bool          `mapstructure:"circuit_breaker_enabled" envconfig:"CIRCUIT_BREAKER_ENABLED" default:"false"`
	CircuitBreakerThreshold int           `mapstructure:"circuit_breaker_threshold" envconfig:"CIRCUIT_BREAKER_THRESHOLD" default:"5"`
	CircuitBreakerTimeout   time.Duration `mapstructure:"circuit_breaker_timeout" envconfig:"CIRCUIT_BREAKER_TIMEOUT" default:"60s"`

	// Memory optimization
	GCPercent              int `mapstructure:"gc_percent" envconfig:"GC_PERCENT" default:"100"`
	MaxMemoryMB            int `mapstructure:"max_memory_mb" envconfig:"MAX_MEMORY_MB" default:"512"`
	MemoryThresholdPercent int `mapstructure:"memory_threshold_percent" envconfig:"MEMORY_THRESHOLD_PERCENT" default:"80"`
}

// NewCleanArchitectureConfig creates a new Clean Architecture configuration with defaults
func NewCleanArchitectureConfig() *CleanArchitectureConfig {
	return &CleanArchitectureConfig{
		Enabled: true,
		Repository: RepositoryConfig{
			MaxOpenConnections:    25,
			MaxIdleConnections:    25,
			ConnectionMaxLifetime: 5 * time.Minute,
			ConnectionMaxIdleTime: 5 * time.Minute,
			QueryTimeout:          30 * time.Second,
			TransactionTimeout:    60 * time.Second,
			MaxRetries:            3,
			RetryInterval:         1 * time.Second,
			HealthCheckInterval:   30 * time.Second,
			HealthCheckTimeout:    5 * time.Second,
		},
		UseCase: UseCaseConfig{
			DefaultTimeout:          30 * time.Second,
			LongRunningTimeout:      5 * time.Minute,
			ValidationEnabled:       true,
			StrictValidation:        false,
			MaxConcurrentExecutions: 10,
			WorkerPoolSize:          5,
			RateLimitEnabled:        false,
			RateLimitRPS:            100,
		},
		Events: EventConfig{
			PublishingEnabled: true,
			Publishing:        true,
			BufferSize:        1000,
			FlushInterval:     1 * time.Second,
			PublishTimeout:    5 * time.Second,
			MaxRetries:        3,
			RetryInterval:     1 * time.Second,
			DeadLetterEnabled: true,
			DeadLetterTTL:     24 * time.Hour,
		},
		API: APIConfig{
			MaxRequestSize:       10 * 1024 * 1024, // 10MB
			RequestTimeout:       30 * time.Second,
			ReadHeaderTimeout:    10 * time.Second,
			EnableCompression:    true,
			EnableCaching:        false,
			CacheTTL:             5 * time.Minute,
			DefaultPageSize:      10,
			MaxPageSize:          1000,
			CORSEnabled:          true,
			CORSAllowedOrigins:   []string{"*"},
			CORSAllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
			CORSAllowedHeaders:   []string{"*"},
			CORSExposedHeaders:   []string{"X-Total-Count"},
			CORSAllowCredentials: false,
			CORSMaxAge:           86400,
		},
		Performance: PerformanceConfig{
			MetricsEnabled:          true,
			MetricsInterval:         15 * time.Second,
			DetailedMetrics:         false,
			TracingEnabled:          false,
			TracingSampleRate:       0.1,
			TracingEndpoint:         "",
			ProfilingEnabled:        false,
			ProfilingHost:           "localhost",
			ProfilingPort:           6060,
			CircuitBreakerEnabled:   false,
			CircuitBreakerThreshold: 5,
			CircuitBreakerTimeout:   60 * time.Second,
			GCPercent:               100,
			MaxMemoryMB:             512,
			MemoryThresholdPercent:  80,
		},
	}
}

// Validate validates the Clean Architecture configuration
func (c *CleanArchitectureConfig) Validate() error {
	// Repository validation
	if c.Repository.MaxOpenConnections <= 0 {
		return fmt.Errorf("repository max_open_connections must be > 0")
	}

	if c.Repository.MaxIdleConnections <= 0 {
		return fmt.Errorf("repository max_idle_connections must be > 0")
	}

	if c.Repository.QueryTimeout <= 0 {
		return fmt.Errorf("repository query_timeout must be > 0")
	}

	if c.Repository.TransactionTimeout <= 0 {
		return fmt.Errorf("repository transaction_timeout must be > 0")
	}

	if c.Repository.MaxRetries < 0 {
		return fmt.Errorf("repository max_retries must be >= 0")
	}

	// Use case validation
	if c.UseCase.DefaultTimeout <= 0 {
		return fmt.Errorf("usecase default_timeout must be > 0")
	}

	if c.UseCase.LongRunningTimeout <= 0 {
		return fmt.Errorf("usecase long_running_timeout must be > 0")
	}

	if c.UseCase.MaxConcurrentExecutions <= 0 {
		return fmt.Errorf("usecase max_concurrent_executions must be > 0")
	}

	if c.UseCase.WorkerPoolSize <= 0 {
		return fmt.Errorf("usecase worker_pool_size must be > 0")
	}

	if c.UseCase.RateLimitRPS <= 0 {
		return fmt.Errorf("usecase rate_limit_rps must be > 0")
	}

	// Events validation
	if c.Events.BufferSize <= 0 {
		return fmt.Errorf("events buffer_size must be > 0")
	}

	if c.Events.FlushInterval <= 0 {
		return fmt.Errorf("events flush_interval must be > 0")
	}

	if c.Events.PublishTimeout <= 0 {
		return fmt.Errorf("events publish_timeout must be > 0")
	}

	if c.Events.MaxRetries < 0 {
		return fmt.Errorf("events max_retries must be >= 0")
	}

	// API validation
	if c.API.MaxRequestSize <= 0 {
		return fmt.Errorf("api max_request_size must be > 0")
	}

	if c.API.RequestTimeout <= 0 {
		return fmt.Errorf("api request_timeout must be > 0")
	}

	if c.API.DefaultPageSize <= 0 {
		return fmt.Errorf("api default_page_size must be > 0")
	}

	if c.API.MaxPageSize <= 0 {
		return fmt.Errorf("api max_page_size must be > 0")
	}

	if c.API.DefaultPageSize > c.API.MaxPageSize {
		return fmt.Errorf("api default_page_size must be <= max_page_size")
	}

	// Performance validation
	if c.Performance.MetricsInterval <= 0 {
		return fmt.Errorf("performance metrics_interval must be > 0")
	}

	if c.Performance.TracingSampleRate < 0 || c.Performance.TracingSampleRate > 1 {
		return fmt.Errorf("performance tracing_sample_rate must be between 0 and 1")
	}

	if c.Performance.ProfilingPort <= 0 || c.Performance.ProfilingPort > 65535 {
		return fmt.Errorf("performance profiling_port must be between 1 and 65535")
	}

	if c.Performance.CircuitBreakerThreshold <= 0 {
		return fmt.Errorf("performance circuit_breaker_threshold must be > 0")
	}

	if c.Performance.CircuitBreakerTimeout <= 0 {
		return fmt.Errorf("performance circuit_breaker_timeout must be > 0")
	}

	if c.Performance.GCPercent < 0 {
		return fmt.Errorf("performance gc_percent must be >= 0")
	}

	if c.Performance.MaxMemoryMB <= 0 {
		return fmt.Errorf("performance max_memory_mb must be > 0")
	}

	if c.Performance.MemoryThresholdPercent <= 0 || c.Performance.MemoryThresholdPercent > 100 {
		return fmt.Errorf("performance memory_threshold_percent must be between 1 and 100")
	}

	return nil
}

// IsEnabled returns whether Clean Architecture is enabled
func (c *CleanArchitectureConfig) IsEnabled() bool {
	return c.Enabled
}

// GetRepositoryConfig returns repository configuration
func (c *CleanArchitectureConfig) GetRepositoryConfig() RepositoryConfig {
	return c.Repository
}

// GetUseCaseConfig returns use case configuration
func (c *CleanArchitectureConfig) GetUseCaseConfig() UseCaseConfig {
	return c.UseCase
}

// GetEventConfig returns event configuration
func (c *CleanArchitectureConfig) GetEventConfig() EventConfig {
	return c.Events
}

// GetAPIConfig returns API configuration
func (c *CleanArchitectureConfig) GetAPIConfig() APIConfig {
	return c.API
}

// GetPerformanceConfig returns performance configuration
func (c *CleanArchitectureConfig) GetPerformanceConfig() PerformanceConfig {
	return c.Performance
}
