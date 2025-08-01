package application

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/flext/flexcore/internal/infrastructure/config"
	"github.com/flext/flexcore/internal/infrastructure/logging"
)

// AppType define o tipo de aplicação
type AppType string

const (
	AppTypeStandalone AppType = "standalone"
	AppTypeServer     AppType = "server"
	AppTypeCLI        AppType = "cli"
	AppTypeDemo       AppType = "demo"
)

// AppBootstrap configuração para bootstrap da aplicação
type AppBootstrap struct {
	AppType     AppType
	AppName     string
	Version     string
	ConfigPath  string
	LogLevel    string
	Environment string
}

// NewAppBootstrap cria um novo bootstrap
func NewAppBootstrap(appType AppType, appName, version string) *AppBootstrap {
	return &AppBootstrap{
		AppType:     appType,
		AppName:     appName,
		Version:     version,
		LogLevel:    "info",
		Environment: "development",
	}
}

// WithConfigPath define o caminho do arquivo de configuração
func (ab *AppBootstrap) WithConfigPath(path string) *AppBootstrap {
	ab.ConfigPath = path
	return ab
}

// WithLogLevel define o nível de log
func (ab *AppBootstrap) WithLogLevel(level string) *AppBootstrap {
	ab.LogLevel = level
	return ab
}

// WithEnvironment define o ambiente
func (ab *AppBootstrap) WithEnvironment(env string) *AppBootstrap {
	ab.Environment = env
	return ab
}

// AppConfig configuração da aplicação após bootstrap
type AppConfig struct {
	Config    *config.Config
	Logger    logging.Logger
	StartTime time.Time
}

// Initialize inicializa a aplicação seguindo o padrão comum
func (ab *AppBootstrap) Initialize() (*AppConfig, error) {
	startTime := time.Now()

	// 1. Carrega configuração
	cfg, err := ab.loadConfiguration()
	if err != nil {
		// Configura logging básico para erros de configuração
		logging.InitLogger(config.LoggingConfig{
			Level:  "error",
			Format: "json",
		})
		logger := logging.GetLogger()
		logger.Error("Failed to load configuration", logging.F("error", err.Error()))
		return nil, fmt.Errorf("configuration load failed: %w", err)
	}

	// 2. Valida configuração
	if err := cfg.Validate(); err != nil {
		// Usa configuração carregada mas com nível de erro
		errorConfig := cfg.Logging
		errorConfig.Level = "error"
		logging.InitLogger(errorConfig)
		logger := logging.GetLogger()
		logger.Error("Configuration validation failed", logging.F("error", err.Error()))
		return nil, fmt.Errorf("configuration validation failed: %w", err)
	}

	// 3. Configura logging estruturado
	if err := ab.setupLogging(cfg); err != nil {
		return nil, fmt.Errorf("logging setup failed: %w", err)
	}

	logger := logging.GetLogger()

	// 4. Log inicial da aplicação
	logger.Info("Initializing application",
		logging.F("app_name", ab.AppName),
		logging.F("app_type", string(ab.AppType)),
		logging.F("version", ab.Version),
		logging.F("environment", cfg.Server.Environment),
		logging.F("debug", cfg.Server.Debug),
	)

	return &AppConfig{
		Config:    cfg,
		Logger:    logger,
		StartTime: startTime,
	}, nil
}

// loadConfiguration carrega configuração com fallbacks
func (ab *AppBootstrap) loadConfiguration() (*config.Config, error) {
	var cfg *config.Config
	var err error

	if ab.ConfigPath != "" {
		cfg, err = config.LoadConfig(ab.ConfigPath)
		if err != nil {
			return nil, fmt.Errorf("failed to load config from file %s: %w", ab.ConfigPath, err)
		}
	} else {
		cfg = config.LoadFromEnv()
	}

	// Aplica overrides do bootstrap se necessário
	if ab.Environment != "" && ab.Environment != cfg.Server.Environment {
		cfg.Server.Environment = ab.Environment
	}

	if ab.LogLevel != "" && ab.LogLevel != cfg.Logging.Level {
		cfg.Logging.Level = ab.LogLevel
	}

	return cfg, nil
}

// setupLogging configura o sistema de logging
func (ab *AppBootstrap) setupLogging(cfg *config.Config) error {
	// Em desenvolvimento, promove log level para debug se for info
	if cfg.IsDevelopment() && cfg.Logging.Level == "info" {
		cfg.Logging.Level = "debug"
	}

	logging.InitLogger(cfg.Logging)
	return nil
}

// GracefulShutdownHandler gerencia shutdown graceful
type GracefulShutdownHandler struct {
	logger          logging.Logger
	shutdownTimeout time.Duration
	shutdownFuncs   []ShutdownFunc
}

// ShutdownFunc função de shutdown
type ShutdownFunc func(ctx context.Context) error

// NewGracefulShutdownHandler cria um novo handler de shutdown
func NewGracefulShutdownHandler(logger logging.Logger, timeout time.Duration) *GracefulShutdownHandler {
	return &GracefulShutdownHandler{
		logger:          logger,
		shutdownTimeout: timeout,
		shutdownFuncs:   make([]ShutdownFunc, 0),
	}
}

// AddShutdownFunc adiciona uma função de shutdown
func (gsh *GracefulShutdownHandler) AddShutdownFunc(name string, fn ShutdownFunc) {
	wrappedFn := func(ctx context.Context) error {
		gsh.logger.Info("Shutting down component", logging.F("component", name))
		err := fn(ctx)
		if err != nil {
			gsh.logger.Error("Failed to shutdown component",
				logging.F("component", name),
				logging.F("error", err.Error()))
		} else {
			gsh.logger.Info("Component shutdown complete", logging.F("component", name))
		}
		return err
	}

	gsh.shutdownFuncs = append(gsh.shutdownFuncs, wrappedFn)
}

// WaitForShutdown aguarda sinal de shutdown e executa shutdown graceful
func (gsh *GracefulShutdownHandler) WaitForShutdown() {
	// Setup signal handling
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	// Wait for shutdown signal
	sig := <-quit
	gsh.logger.Info("Received shutdown signal", logging.F("signal", sig.String()))

	// Create shutdown context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), gsh.shutdownTimeout)
	defer cancel()

	// Execute all shutdown functions
	gsh.logger.Info("Starting graceful shutdown...",
		logging.F("timeout", gsh.shutdownTimeout.String()),
		logging.F("components", len(gsh.shutdownFuncs)))

	for i, fn := range gsh.shutdownFuncs {
		if err := fn(ctx); err != nil {
			gsh.logger.Error("Shutdown function failed",
				logging.F("index", i),
				logging.F("error", err.Error()))
		}
	}

	gsh.logger.Info("Graceful shutdown complete")
}

// ContainerInterface interface para containers
type ContainerInterface interface {
	HealthCheck(ctx context.Context) error
	Shutdown(ctx context.Context) error
}

// ServerInterface interface para servidores
type ServerInterface interface {
	Start() error
	Stop(ctx context.Context) error
}
