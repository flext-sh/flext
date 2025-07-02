package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
)

// UnifiedConfig provides centralized configuration management for all bounded contexts
type UnifiedConfig struct {
	Environment string
	Debug       bool
	
	// Application metadata
	AppName    string
	AppVersion string
	BuildTime  string
	CommitHash string
	
	// Server configuration
	Host         string
	Port         int
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration
	
	// Database configuration
	Database DatabaseConfig
	
	// Cache configuration
	Cache CacheConfig
	
	// Authentication configuration
	Auth AuthConfig
	
	// Observability configuration
	Observability ObservabilityConfig
	
	// Feature flags
	Features FeatureFlags
	
	// Bounded context configurations
	Pipeline PipelineConfig
	Plugin   PluginConfig
	Singer   SingerConfig
	Meltano  MeltanoConfig
	DBT      DBTConfig
	
	// External services
	External ExternalServicesConfig
}

// DatabaseConfig contains database connection settings
type DatabaseConfig struct {
	Driver          string
	Host            string
	Port            int
	Database        string
	Username        string
	Password        string
	SSLMode         string
	MaxOpenConns    int
	MaxIdleConns    int
	ConnMaxLifetime time.Duration
	MigrationsPath  string
	EnableLogging   bool
}

// CacheConfig contains cache settings
type CacheConfig struct {
	Driver     string // redis, memory, none
	Host       string
	Port       int
	Password   string
	Database   int
	TTL        time.Duration
	MaxEntries int
}

// AuthConfig contains authentication settings
type AuthConfig struct {
	JWTSecret       string
	JWTExpiry       time.Duration
	RefreshExpiry   time.Duration
	EnableBasicAuth bool
	EnableAPIKeys   bool
	EnableOAuth2    bool
	OAuth2Config    OAuth2Config
}

// OAuth2Config contains OAuth2 settings
type OAuth2Config struct {
	ClientID     string
	ClientSecret string
	RedirectURL  string
	Scopes       []string
	AuthURL      string
	TokenURL     string
}

// ObservabilityConfig contains monitoring and logging settings
type ObservabilityConfig struct {
	LogLevel       string
	LogFormat      string // json, text
	EnableMetrics  bool
	EnableTracing  bool
	MetricsPort    int
	TracingURL     string
	SentryDSN      string
	EnableProfiling bool
}

// FeatureFlags contains feature toggle settings
type FeatureFlags struct {
	DatabaseEnabled         bool
	WebSocketEnabled        bool
	AuthenticationEnabled   bool
	MetricsEnabled         bool
	TracingEnabled         bool
	CacheEnabled           bool
	CleanArchitectureEnabled bool
	AdvancedLoggingEnabled  bool
}

// PipelineConfig contains pipeline-specific settings
type PipelineConfig struct {
	DefaultTimeout    time.Duration
	MaxConcurrency    int
	RetryAttempts     int
	RetryDelay        time.Duration
	EnableValidation  bool
	EnableAudit       bool
	WorkingDirectory  string
	ArtifactsPath     string
}

// PluginConfig contains plugin-specific settings
type PluginConfig struct {
	PluginsDirectory  string
	AllowedTypes      []string
	EnableSandbox     bool
	PluginTimeout     time.Duration
	MaxMemoryUsage    int64
	EnableAutoUpdate  bool
	RegistryURL       string
}

// SingerConfig contains Singer protocol settings
type SingerConfig struct {
	WorkingDirectory string
	DefaultTimeout   time.Duration
	MaxLogSize       int64
	StateFilePath    string
	CatalogPath      string
	EnableValidation bool
}

// MeltanoConfig contains Meltano-specific settings
type MeltanoConfig struct {
	ProjectPath      string
	PythonPath       string
	VenvPath         string
	ConfigPath       string
	StateBackend     string
	EnableLogging    bool
	LogLevel         string
}

// DBTConfig contains dbt-specific settings
type DBTConfig struct {
	ProjectPath   string
	ProfilesDir   string
	PythonPath    string
	DBTPath       string
	VenvPath      string
	DefaultTarget string
	EnableDocs    bool
	DocsPort      int
}

// ExternalServicesConfig contains external service configurations
type ExternalServicesConfig struct {
	LDAP   LDAPConfig
	Oracle OracleConfig
	APIs   map[string]APIConfig
}

// LDAPConfig contains LDAP connection settings
type LDAPConfig struct {
	Host         string
	Port         int
	BaseDN       string
	BindDN       string
	BindPassword string
	UseSSL       bool
	SkipVerify   bool
	Timeout      time.Duration
}

// OracleConfig contains Oracle database settings
type OracleConfig struct {
	Host         string
	Port         int
	ServiceName  string
	Username     string
	Password     string
	Charset      string
	EnableLogging bool
}

// APIConfig contains external API settings
type APIConfig struct {
	BaseURL    string
	APIKey     string
	Timeout    time.Duration
	RetryCount int
	RateLimit  int
}

// NewUnifiedConfig creates a new configuration instance with environment variables
func NewUnifiedConfig() (*UnifiedConfig, error) {
	config := &UnifiedConfig{
		Environment: getEnvOrDefault("ENVIRONMENT", "development"),
		Debug:       getBoolEnvOrDefault("DEBUG", false),
		
		AppName:    getEnvOrDefault("APP_NAME", "flext"),
		AppVersion: getEnvOrDefault("APP_VERSION", "2.0.0"),
		BuildTime:  getEnvOrDefault("BUILD_TIME", time.Now().Format(time.RFC3339)),
		CommitHash: getEnvOrDefault("COMMIT_HASH", "unknown"),
		
		Host:         getEnvOrDefault("HOST", "0.0.0.0"),
		Port:         getIntEnvOrDefault("PORT", 8080),
		ReadTimeout:  getDurationEnvOrDefault("READ_TIMEOUT", 30*time.Second),
		WriteTimeout: getDurationEnvOrDefault("WRITE_TIMEOUT", 30*time.Second),
		IdleTimeout:  getDurationEnvOrDefault("IDLE_TIMEOUT", 120*time.Second),
	}
	
	if err := config.loadDatabaseConfig(); err != nil {
		return nil, fmt.Errorf("failed to load database config: %w", err)
	}
	
	if err := config.loadCacheConfig(); err != nil {
		return nil, fmt.Errorf("failed to load cache config: %w", err)
	}
	
	if err := config.loadAuthConfig(); err != nil {
		return nil, fmt.Errorf("failed to load auth config: %w", err)
	}
	
	if err := config.loadObservabilityConfig(); err != nil {
		return nil, fmt.Errorf("failed to load observability config: %w", err)
	}
	
	if err := config.loadFeatureFlags(); err != nil {
		return nil, fmt.Errorf("failed to load feature flags: %w", err)
	}
	
	if err := config.loadBoundedContextConfigs(); err != nil {
		return nil, fmt.Errorf("failed to load bounded context configs: %w", err)
	}
	
	if err := config.loadExternalServicesConfig(); err != nil {
		return nil, fmt.Errorf("failed to load external services config: %w", err)
	}
	
	return config, nil
}

func (c *UnifiedConfig) loadDatabaseConfig() error {
	c.Database = DatabaseConfig{
		Driver:          getEnvOrDefault("DB_DRIVER", "postgres"),
		Host:            getEnvOrDefault("DB_HOST", "localhost"),
		Port:            getIntEnvOrDefault("DB_PORT", 5432),
		Database:        getEnvOrDefault("DB_NAME", "flext"),
		Username:        getEnvOrDefault("DB_USER", "flext"),
		Password:        getEnvOrDefault("DB_PASSWORD", "flext"),
		SSLMode:         getEnvOrDefault("DB_SSL_MODE", "disable"),
		MaxOpenConns:    getIntEnvOrDefault("DB_MAX_OPEN_CONNS", 25),
		MaxIdleConns:    getIntEnvOrDefault("DB_MAX_IDLE_CONNS", 10),
		ConnMaxLifetime: getDurationEnvOrDefault("DB_CONN_MAX_LIFETIME", 5*time.Minute),
		MigrationsPath:  getEnvOrDefault("DB_MIGRATIONS_PATH", "./migrations"),
		EnableLogging:   getBoolEnvOrDefault("DB_ENABLE_LOGGING", false),
	}
	return nil
}

func (c *UnifiedConfig) loadCacheConfig() error {
	c.Cache = CacheConfig{
		Driver:     getEnvOrDefault("CACHE_DRIVER", "memory"),
		Host:       getEnvOrDefault("CACHE_HOST", "localhost"),
		Port:       getIntEnvOrDefault("CACHE_PORT", 6379),
		Password:   getEnvOrDefault("CACHE_PASSWORD", ""),
		Database:   getIntEnvOrDefault("CACHE_DATABASE", 0),
		TTL:        getDurationEnvOrDefault("CACHE_TTL", 1*time.Hour),
		MaxEntries: getIntEnvOrDefault("CACHE_MAX_ENTRIES", 10000),
	}
	return nil
}

func (c *UnifiedConfig) loadAuthConfig() error {
	c.Auth = AuthConfig{
		JWTSecret:       getEnvOrDefault("JWT_SECRET", generateDefaultSecret()),
		JWTExpiry:       getDurationEnvOrDefault("JWT_EXPIRY", 24*time.Hour),
		RefreshExpiry:   getDurationEnvOrDefault("REFRESH_EXPIRY", 7*24*time.Hour),
		EnableBasicAuth: getBoolEnvOrDefault("ENABLE_BASIC_AUTH", true),
		EnableAPIKeys:   getBoolEnvOrDefault("ENABLE_API_KEYS", true),
		EnableOAuth2:    getBoolEnvOrDefault("ENABLE_OAUTH2", false),
		OAuth2Config: OAuth2Config{
			ClientID:     getEnvOrDefault("OAUTH2_CLIENT_ID", ""),
			ClientSecret: getEnvOrDefault("OAUTH2_CLIENT_SECRET", ""),
			RedirectURL:  getEnvOrDefault("OAUTH2_REDIRECT_URL", ""),
			Scopes:       getStringSliceEnv("OAUTH2_SCOPES", []string{"read", "write"}),
			AuthURL:      getEnvOrDefault("OAUTH2_AUTH_URL", ""),
			TokenURL:     getEnvOrDefault("OAUTH2_TOKEN_URL", ""),
		},
	}
	return nil
}

func (c *UnifiedConfig) loadObservabilityConfig() error {
	c.Observability = ObservabilityConfig{
		LogLevel:        getEnvOrDefault("LOG_LEVEL", "info"),
		LogFormat:       getEnvOrDefault("LOG_FORMAT", "json"),
		EnableMetrics:   getBoolEnvOrDefault("ENABLE_METRICS", true),
		EnableTracing:   getBoolEnvOrDefault("ENABLE_TRACING", false),
		MetricsPort:     getIntEnvOrDefault("METRICS_PORT", 9090),
		TracingURL:      getEnvOrDefault("TRACING_URL", ""),
		SentryDSN:       getEnvOrDefault("SENTRY_DSN", ""),
		EnableProfiling: getBoolEnvOrDefault("ENABLE_PROFILING", false),
	}
	return nil
}

func (c *UnifiedConfig) loadFeatureFlags() error {
	c.Features = FeatureFlags{
		DatabaseEnabled:          getBoolEnvOrDefault("FEATURE_DATABASE", true),
		WebSocketEnabled:         getBoolEnvOrDefault("FEATURE_WEBSOCKET", false),
		AuthenticationEnabled:    getBoolEnvOrDefault("FEATURE_AUTH", true),
		MetricsEnabled:          getBoolEnvOrDefault("FEATURE_METRICS", true),
		TracingEnabled:          getBoolEnvOrDefault("FEATURE_TRACING", false),
		CacheEnabled:            getBoolEnvOrDefault("FEATURE_CACHE", true),
		CleanArchitectureEnabled: getBoolEnvOrDefault("FEATURE_CLEAN_ARCH", true),
		AdvancedLoggingEnabled:   getBoolEnvOrDefault("FEATURE_ADVANCED_LOGGING", true),
	}
	return nil
}

func (c *UnifiedConfig) loadBoundedContextConfigs() error {
	c.Pipeline = PipelineConfig{
		DefaultTimeout:   getDurationEnvOrDefault("PIPELINE_DEFAULT_TIMEOUT", 10*time.Minute),
		MaxConcurrency:   getIntEnvOrDefault("PIPELINE_MAX_CONCURRENCY", 5),
		RetryAttempts:    getIntEnvOrDefault("PIPELINE_RETRY_ATTEMPTS", 3),
		RetryDelay:       getDurationEnvOrDefault("PIPELINE_RETRY_DELAY", 5*time.Second),
		EnableValidation: getBoolEnvOrDefault("PIPELINE_ENABLE_VALIDATION", true),
		EnableAudit:      getBoolEnvOrDefault("PIPELINE_ENABLE_AUDIT", true),
		WorkingDirectory: getEnvOrDefault("PIPELINE_WORKING_DIR", "/tmp/flext-pipelines"),
		ArtifactsPath:    getEnvOrDefault("PIPELINE_ARTIFACTS_PATH", "/var/lib/flext/artifacts"),
	}
	
	c.Plugin = PluginConfig{
		PluginsDirectory: getEnvOrDefault("PLUGINS_DIRECTORY", "/var/lib/flext/plugins"),
		AllowedTypes:     getStringSliceEnv("PLUGIN_ALLOWED_TYPES", []string{"tap", "target", "transformer"}),
		EnableSandbox:    getBoolEnvOrDefault("PLUGIN_ENABLE_SANDBOX", true),
		PluginTimeout:    getDurationEnvOrDefault("PLUGIN_TIMEOUT", 5*time.Minute),
		MaxMemoryUsage:   getInt64EnvOrDefault("PLUGIN_MAX_MEMORY", 512*1024*1024), // 512MB
		EnableAutoUpdate: getBoolEnvOrDefault("PLUGIN_ENABLE_AUTO_UPDATE", false),
		RegistryURL:      getEnvOrDefault("PLUGIN_REGISTRY_URL", "https://hub.meltano.com"),
	}
	
	c.Singer = SingerConfig{
		WorkingDirectory: getEnvOrDefault("SINGER_WORKING_DIR", "/tmp/flext-singer"),
		DefaultTimeout:   getDurationEnvOrDefault("SINGER_DEFAULT_TIMEOUT", 30*time.Minute),
		MaxLogSize:       getInt64EnvOrDefault("SINGER_MAX_LOG_SIZE", 100*1024*1024), // 100MB
		StateFilePath:    getEnvOrDefault("SINGER_STATE_FILE", "/var/lib/flext/singer/state.json"),
		CatalogPath:      getEnvOrDefault("SINGER_CATALOG_PATH", "/var/lib/flext/singer/catalog.json"),
		EnableValidation: getBoolEnvOrDefault("SINGER_ENABLE_VALIDATION", true),
	}
	
	c.Meltano = MeltanoConfig{
		ProjectPath:   getEnvOrDefault("MELTANO_PROJECT_PATH", "."),
		PythonPath:    getEnvOrDefault("MELTANO_PYTHON_PATH", "/home/marlonsc/flext/.venv/bin/python3"),
		VenvPath:      getEnvOrDefault("MELTANO_VENV_PATH", "/home/marlonsc/flext/.venv"),
		ConfigPath:    getEnvOrDefault("MELTANO_CONFIG_PATH", "meltano.yml"),
		StateBackend:  getEnvOrDefault("MELTANO_STATE_BACKEND", "filesystem"),
		EnableLogging: getBoolEnvOrDefault("MELTANO_ENABLE_LOGGING", true),
		LogLevel:      getEnvOrDefault("MELTANO_LOG_LEVEL", "info"),
	}
	
	c.DBT = DBTConfig{
		ProjectPath:   getEnvOrDefault("DBT_PROJECT_PATH", "./dbt_project"),
		ProfilesDir:   getEnvOrDefault("DBT_PROFILES_DIR", "~/.dbt"),
		PythonPath:    getEnvOrDefault("DBT_PYTHON_PATH", "/home/marlonsc/flext/.venv/bin/python3"),
		DBTPath:       getEnvOrDefault("DBT_PATH", "dbt"),
		VenvPath:      getEnvOrDefault("DBT_VENV_PATH", "/home/marlonsc/flext/.venv"),
		DefaultTarget: getEnvOrDefault("DBT_DEFAULT_TARGET", "dev"),
		EnableDocs:    getBoolEnvOrDefault("DBT_ENABLE_DOCS", true),
		DocsPort:      getIntEnvOrDefault("DBT_DOCS_PORT", 8081),
	}
	
	return nil
}

func (c *UnifiedConfig) loadExternalServicesConfig() error {
	c.External = ExternalServicesConfig{
		LDAP: LDAPConfig{
			Host:         getEnvOrDefault("LDAP_HOST", "localhost"),
			Port:         getIntEnvOrDefault("LDAP_PORT", 389),
			BaseDN:       getEnvOrDefault("LDAP_BASE_DN", ""),
			BindDN:       getEnvOrDefault("LDAP_BIND_DN", ""),
			BindPassword: getEnvOrDefault("LDAP_BIND_PASSWORD", ""),
			UseSSL:       getBoolEnvOrDefault("LDAP_USE_SSL", false),
			SkipVerify:   getBoolEnvOrDefault("LDAP_SKIP_VERIFY", false),
			Timeout:      getDurationEnvOrDefault("LDAP_TIMEOUT", 30*time.Second),
		},
		Oracle: OracleConfig{
			Host:          getEnvOrDefault("ORACLE_HOST", "localhost"),
			Port:          getIntEnvOrDefault("ORACLE_PORT", 1521),
			ServiceName:   getEnvOrDefault("ORACLE_SERVICE_NAME", "XE"),
			Username:      getEnvOrDefault("ORACLE_USERNAME", "system"),
			Password:      getEnvOrDefault("ORACLE_PASSWORD", "oracle"),
			Charset:       getEnvOrDefault("ORACLE_CHARSET", "UTF8"),
			EnableLogging: getBoolEnvOrDefault("ORACLE_ENABLE_LOGGING", false),
		},
		APIs: make(map[string]APIConfig),
	}
	
	// Load API configurations dynamically based on environment variables
	for _, env := range os.Environ() {
		if strings.HasPrefix(env, "API_") && strings.Contains(env, "_BASE_URL=") {
			parts := strings.SplitN(env, "=", 2)
			if len(parts) == 2 {
				keyParts := strings.Split(parts[0], "_")
				if len(keyParts) >= 2 {
					apiName := strings.ToLower(keyParts[1])
					if _, exists := c.External.APIs[apiName]; !exists {
						c.External.APIs[apiName] = APIConfig{}
					}
					apiConfig := c.External.APIs[apiName]
					apiConfig.BaseURL = parts[1]
					apiConfig.APIKey = getEnvOrDefault(fmt.Sprintf("API_%s_KEY", strings.ToUpper(apiName)), "")
					apiConfig.Timeout = getDurationEnvOrDefault(fmt.Sprintf("API_%s_TIMEOUT", strings.ToUpper(apiName)), 30*time.Second)
					apiConfig.RetryCount = getIntEnvOrDefault(fmt.Sprintf("API_%s_RETRY_COUNT", strings.ToUpper(apiName)), 3)
					apiConfig.RateLimit = getIntEnvOrDefault(fmt.Sprintf("API_%s_RATE_LIMIT", strings.ToUpper(apiName)), 100)
					c.External.APIs[apiName] = apiConfig
				}
			}
		}
	}
	
	return nil
}

// Utility methods

// IsProduction returns true if running in production environment
func (c *UnifiedConfig) IsProduction() bool {
	return c.Environment == "production"
}

// IsDevelopment returns true if running in development environment
func (c *UnifiedConfig) IsDevelopment() bool {
	return c.Environment == "development"
}

// IsTest returns true if running in test environment
func (c *UnifiedConfig) IsTest() bool {
	return c.Environment == "test"
}

// GetAddress returns the server address as host:port
func (c *UnifiedConfig) GetAddress() string {
	return fmt.Sprintf("%s:%d", c.Host, c.Port)
}

// GetDatabaseDSN returns the database connection string
func (c *UnifiedConfig) GetDatabaseDSN() string {
	switch c.Database.Driver {
	case "postgres":
		return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
			c.Database.Host, c.Database.Port, c.Database.Username,
			c.Database.Password, c.Database.Database, c.Database.SSLMode)
	case "mysql":
		return fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
			c.Database.Username, c.Database.Password,
			c.Database.Host, c.Database.Port, c.Database.Database)
	case "sqlite":
		return c.Database.Database
	default:
		return ""
	}
}

// GetRedisAddress returns the Redis connection address
func (c *UnifiedConfig) GetRedisAddress() string {
	return fmt.Sprintf("%s:%d", c.Cache.Host, c.Cache.Port)
}

// Validate validates the configuration
func (c *UnifiedConfig) Validate() error {
	if c.AppName == "" {
		return fmt.Errorf("app name cannot be empty")
	}
	
	if c.Port <= 0 || c.Port > 65535 {
		return fmt.Errorf("invalid port: %d", c.Port)
	}
	
	if c.Features.DatabaseEnabled && c.Database.Driver == "" {
		return fmt.Errorf("database driver cannot be empty when database is enabled")
	}
	
	if c.Features.AuthenticationEnabled && c.Auth.JWTSecret == "" {
		return fmt.Errorf("JWT secret cannot be empty when authentication is enabled")
	}
	
	return nil
}

// Environment variable helper functions

func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getIntEnvOrDefault(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getInt64EnvOrDefault(key string, defaultValue int64) int64 {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.ParseInt(value, 10, 64); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getBoolEnvOrDefault(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}

func getDurationEnvOrDefault(key string, defaultValue time.Duration) time.Duration {
	if value := os.Getenv(key); value != "" {
		if duration, err := time.ParseDuration(value); err == nil {
			return duration
		}
	}
	return defaultValue
}

func getStringSliceEnv(key string, defaultValue []string) []string {
	if value := os.Getenv(key); value != "" {
		return strings.Split(value, ",")
	}
	return defaultValue
}

func generateDefaultSecret() string {
	return uuid.New().String()
}

// GetEnvWithDefault gets an environment variable with a default value
func (c *UnifiedConfig) GetEnvWithDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}