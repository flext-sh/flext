package config

import (
	"fmt"
	"os"
	"reflect"
	"strconv"
	"time"

	"github.com/kelseyhightower/envconfig"
	"github.com/spf13/viper"
)

// ConfigType interface que todas as configurações devem implementar
type ConfigType interface {
	Validate() error
}

// ConfigLoader carregador genérico de configuração
type ConfigLoader[T ConfigType] struct {
	prefix    string
	defaults  T
	validator func(T) error
}

// NewConfigLoader cria um novo carregador de configuração
func NewConfigLoader[T ConfigType](prefix string, defaults T, validator func(T) error) *ConfigLoader[T] {
	return &ConfigLoader[T]{
		prefix:    prefix,
		defaults:  defaults,
		validator: validator,
	}
}

// Load carrega configuração de arquivo ou variáveis de ambiente
func (cl *ConfigLoader[T]) Load(configPath string) (T, error) {
	var config T

	// Começa com os defaults
	config = cl.defaults

	// Se tem arquivo de config, carrega usando Viper
	if configPath != "" {
		if err := cl.loadFromFile(configPath, &config); err != nil {
			return config, fmt.Errorf("failed to load config from file: %w", err)
		}
	}

	// Sobrescreve com variáveis de ambiente
	if err := cl.loadFromEnv(&config); err != nil {
		return config, fmt.Errorf("failed to load config from env: %w", err)
	}

	// Valida a configuração final
	if err := config.Validate(); err != nil {
		return config, fmt.Errorf("config validation failed: %w", err)
	}

	// Valida com validador customizado se fornecido
	if cl.validator != nil {
		if err := cl.validator(config); err != nil {
			return config, fmt.Errorf("custom validation failed: %w", err)
		}
	}

	return config, nil
}

// LoadFromEnv carrega configuração apenas de variáveis de ambiente
func (cl *ConfigLoader[T]) LoadFromEnv() (T, error) {
	config := cl.defaults

	if err := cl.loadFromEnv(&config); err != nil {
		return config, fmt.Errorf("failed to load config from env: %w", err)
	}

	if err := config.Validate(); err != nil {
		return config, fmt.Errorf("config validation failed: %w", err)
	}

	if cl.validator != nil {
		if err := cl.validator(config); err != nil {
			return config, fmt.Errorf("custom validation failed: %w", err)
		}
	}

	return config, nil
}

// loadFromFile carrega configuração usando Viper
func (cl *ConfigLoader[T]) loadFromFile(configPath string, config *T) error {
	viper.SetConfigFile(configPath)

	if err := viper.ReadInConfig(); err != nil {
		return err
	}

	return viper.Unmarshal(config)
}

// loadFromEnv carrega configuração usando envconfig
func (cl *ConfigLoader[T]) loadFromEnv(config *T) error {
	return envconfig.Process(cl.prefix, config)
}

// Config configuração base comum
type Config struct {
	Environment string        `mapstructure:"environment" envconfig:"ENVIRONMENT" default:"development"`
	Debug       bool          `mapstructure:"debug" envconfig:"DEBUG" default:"false"`
	Timeout     time.Duration `mapstructure:"timeout" envconfig:"TIMEOUT" default:"30s"`
	LogLevel    string        `mapstructure:"log_level" envconfig:"LOG_LEVEL" default:"info"`
}

// Validate valida a configuração base
func (c Config) Validate() error {
	validEnvs := []string{"development", "staging", "production", "test"}
	if !contains(validEnvs, c.Environment) {
		return fmt.Errorf("invalid environment: %s, must be one of %v", c.Environment, validEnvs)
	}

	validLogLevels := []string{"debug", "info", "warn", "error", "fatal"}
	if !contains(validLogLevels, c.LogLevel) {
		return fmt.Errorf("invalid log level: %s, must be one of %v", c.LogLevel, validLogLevels)
	}

	if c.Timeout <= 0 {
		return fmt.Errorf("timeout must be positive")
	}

	return nil
}

// IsProduction verifica se está em produção
func (c Config) IsProduction() bool {
	return c.Environment == "production"
}

// IsDevelopment verifica se está em desenvolvimento
func (c Config) IsDevelopment() bool {
	return c.Environment == "development"
}

// IsTest verifica se está em teste
func (c Config) IsTest() bool {
	return c.Environment == "test"
}

// ServerConfig configuração base para servidor HTTP
type ServerConfig struct {
	Host            string        `mapstructure:"host" envconfig:"HOST" default:"0.0.0.0"`
	Port            int           `mapstructure:"port" envconfig:"PORT" default:"8080"`
	ReadTimeout     time.Duration `mapstructure:"read_timeout" envconfig:"READ_TIMEOUT" default:"30s"`
	WriteTimeout    time.Duration `mapstructure:"write_timeout" envconfig:"WRITE_TIMEOUT" default:"30s"`
	IdleTimeout     time.Duration `mapstructure:"idle_timeout" envconfig:"IDLE_TIMEOUT" default:"120s"`
	ShutdownTimeout time.Duration `mapstructure:"shutdown_timeout" envconfig:"SHUTDOWN_TIMEOUT" default:"30s"`
	EnableCORS      bool          `mapstructure:"enable_cors" envconfig:"ENABLE_CORS" default:"true"`
	MaxHeaderBytes  int           `mapstructure:"max_header_bytes" envconfig:"MAX_HEADER_BYTES" default:"1048576"`
}

// Address retorna o endereço completo do servidor
func (s ServerConfig) Address() string {
	return fmt.Sprintf("%s:%d", s.Host, s.Port)
}

// Validate valida a configuração do servidor
func (s ServerConfig) Validate() error {
	if s.Port <= 0 || s.Port > 65535 {
		return fmt.Errorf("invalid port: %d, must be between 1 and 65535", s.Port)
	}

	if s.ReadTimeout <= 0 {
		return fmt.Errorf("read_timeout must be positive")
	}

	if s.WriteTimeout <= 0 {
		return fmt.Errorf("write_timeout must be positive")
	}

	if s.IdleTimeout <= 0 {
		return fmt.Errorf("idle_timeout must be positive")
	}

	if s.ShutdownTimeout <= 0 {
		return fmt.Errorf("shutdown_timeout must be positive")
	}

	if s.MaxHeaderBytes <= 0 {
		return fmt.Errorf("max_header_bytes must be positive")
	}

	return nil
}

// BaseDatabaseConfig configuração base para banco de dados
type BaseDatabaseConfig struct {
	Driver          string        `mapstructure:"driver" envconfig:"DRIVER" default:"memory"`
	Host            string        `mapstructure:"host" envconfig:"HOST" default:"localhost"`
	Port            int           `mapstructure:"port" envconfig:"PORT" default:"5432"`
	Database        string        `mapstructure:"database" envconfig:"DATABASE" default:"flext"`
	Username        string        `mapstructure:"username" envconfig:"USERNAME" default:"flext"`
	Password        string        `mapstructure:"password" envconfig:"PASSWORD" default:"flext"`
	SSLMode         string        `mapstructure:"ssl_mode" envconfig:"SSL_MODE" default:"disable"`
	MaxOpenConns    int           `mapstructure:"max_open_conns" envconfig:"MAX_OPEN_CONNS" default:"25"`
	MaxIdleConns    int           `mapstructure:"max_idle_conns" envconfig:"MAX_IDLE_CONNS" default:"25"`
	ConnMaxLifetime time.Duration `mapstructure:"conn_max_lifetime" envconfig:"CONN_MAX_LIFETIME" default:"5m"`
	ConnMaxIdleTime time.Duration `mapstructure:"conn_max_idle_time" envconfig:"CONN_MAX_IDLE_TIME" default:"5m"`
}

// ConnectionString retorna a string de conexão
func (d BaseDatabaseConfig) ConnectionString() string {
	switch d.Driver {
	case "postgres":
		return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
			d.Host, d.Port, d.Username, d.Password, d.Database, d.SSLMode)
	case "mysql":
		return fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
			d.Username, d.Password, d.Host, d.Port, d.Database)
	case "sqlite":
		return d.Database
	case "memory":
		return ":memory:"
	default:
		return ""
	}
}

// Validate valida a configuração do banco
func (d BaseDatabaseConfig) Validate() error {
	validDrivers := []string{"postgres", "mysql", "sqlite", "memory"}
	if !contains(validDrivers, d.Driver) {
		return fmt.Errorf("invalid driver: %s, must be one of %v", d.Driver, validDrivers)
	}

	if d.Driver != "memory" && d.Driver != "sqlite" {
		if d.Host == "" {
			return fmt.Errorf("host is required for driver %s", d.Driver)
		}
		if d.Port <= 0 || d.Port > 65535 {
			return fmt.Errorf("invalid port: %d", d.Port)
		}
		if d.Username == "" {
			return fmt.Errorf("username is required for driver %s", d.Driver)
		}
	}

	if d.Database == "" {
		return fmt.Errorf("database name is required")
	}

	if d.MaxOpenConns <= 0 {
		return fmt.Errorf("max_open_conns must be positive")
	}

	if d.MaxIdleConns <= 0 {
		return fmt.Errorf("max_idle_conns must be positive")
	}

	return nil
}

// GetEnvWithDefault retorna valor da variável de ambiente ou default
func GetEnvWithDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// GetEnvAsInt retorna valor da variável de ambiente como int ou default
func GetEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

// GetEnvAsBool retorna valor da variável de ambiente como bool ou default
func GetEnvAsBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}

// GetEnvAsDuration retorna valor da variável de ambiente como duration ou default
func GetEnvAsDuration(key string, defaultValue time.Duration) time.Duration {
	if value := os.Getenv(key); value != "" {
		if duration, err := time.ParseDuration(value); err == nil {
			return duration
		}
	}
	return defaultValue
}

// MergeConfigs mescla duas configurações usando reflection
func MergeConfigs[T any](base, override T) T {
	result := base

	baseValue := reflect.ValueOf(&result).Elem()
	overrideValue := reflect.ValueOf(override)

	mergeStructs(baseValue, overrideValue)

	return result
}

// mergeStructs mescla structs usando reflection
func mergeStructs(base, override reflect.Value) {
	for i := 0; i < base.NumField(); i++ {
		baseField := base.Field(i)
		overrideField := override.Field(i)

		if !baseField.CanSet() {
			continue
		}

		if baseField.Kind() == reflect.Struct && overrideField.Kind() == reflect.Struct {
			mergeStructs(baseField, overrideField)
		} else if !isZeroValue(overrideField) {
			baseField.Set(overrideField)
		}
	}
}

// isZeroValue verifica se o valor é zero
func isZeroValue(v reflect.Value) bool {
	switch v.Kind() {
	case reflect.String:
		return v.String() == ""
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return v.Int() == 0
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		return v.Uint() == 0
	case reflect.Bool:
		return !v.Bool()
	case reflect.Float32, reflect.Float64:
		return v.Float() == 0
	case reflect.Slice, reflect.Map, reflect.Interface:
		return v.IsNil()
	default:
		return reflect.DeepEqual(v.Interface(), reflect.Zero(v.Type()).Interface())
	}
}

// contains verifica se slice contém item
func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}
