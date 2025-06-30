package server

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/container"
	"github.com/flext-sh/flext/internal/infrastructure/http/middleware"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/go-playground/validator/v10"
	"github.com/labstack/echo/v4"
	echoMiddleware "github.com/labstack/echo/v4/middleware"
)

// Server representa o servidor HTTP com configuração
type Server struct {
	echo      *echo.Echo
	config    *config.Config
	container *container.Container
	logger    logging.Logger
}

// CustomValidator implementa a interface echo.Validator
type CustomValidator struct {
	validator *validator.Validate
}

func (cv *CustomValidator) Validate(i interface{}) error {
	if err := cv.validator.Struct(i); err != nil {
		return middleware.ValidationErrorHandler(err)
	}
	return nil
}

// NewServer cria uma nova instância do servidor
func NewServer(cfg *config.Config, container *container.Container) *Server {
	// Inicializar logger
	logging.InitLogger(cfg.Logging)
	logger := logging.GetLogger()

	// Criar instância do Echo
	e := echo.New()

	// Configurar error handler customizado
	e.HTTPErrorHandler = func(err error, c echo.Context) {
		middleware.ErrorHandler()(func(c echo.Context) error {
			return err
		})(c)
	}

	// Configurar validator
	e.Validator = &CustomValidator{validator: validator.New()}

	// Remover banner do Echo
	e.HideBanner = true

	server := &Server{
		echo:      e,
		config:    cfg,
		container: container,
		logger:    logger,
	}

	server.setupMiddleware()
	server.setupRoutes()

	return server
}

// setupMiddleware configura middlewares
func (s *Server) setupMiddleware() {
	// Request ID middleware
	s.echo.Use(echoMiddleware.RequestID())

	// Logger middleware com logging estruturado
	s.echo.Use(echoMiddleware.RequestLoggerWithConfig(echoMiddleware.RequestLoggerConfig{
		LogURI:    true,
		LogStatus: true,
		LogError:  true,
		LogLatency: true,
		LogMethod: true,
		LogValuesFunc: func(c echo.Context, values echoMiddleware.RequestLoggerValues) error {
			logger := s.logger.With(
				logging.F("method", values.Method),
				logging.F("uri", values.URI),
				logging.F("status", values.Status),
				logging.F("latency", values.Latency.String()),
				logging.F("request_id", c.Response().Header().Get(echo.HeaderXRequestID)),
			)

			if values.Error != nil {
				logger.Error("Request completed with error", logging.F("error", values.Error.Error()))
			} else {
				logger.Info("Request completed")
			}
			return nil
		},
	}))

	// Recovery middleware
	s.echo.Use(echoMiddleware.Recover())

	// CORS middleware se habilitado
	if s.config.Server.EnableCORS {
		s.echo.Use(echoMiddleware.CORS())
	}

	// Rate limiting básico
	s.echo.Use(echoMiddleware.RateLimiter(echoMiddleware.NewRateLimiterMemoryStore(20)))

	// Timeout middleware
	s.echo.Use(echoMiddleware.TimeoutWithConfig(echoMiddleware.TimeoutConfig{
		Timeout: s.config.Server.ReadTimeout,
	}))

	// Error handler middleware
	s.echo.Use(middleware.ErrorHandler())
}

// setupRoutes configura as rotas
func (s *Server) setupRoutes() {
	// Health check
	s.echo.GET("/health", s.healthCheck)

	// Root endpoint com documentação
	s.echo.GET("/", s.apiDocumentation)

	// Metrics endpoint
	s.echo.GET("/metrics", s.metricsEndpoint)

	// Registrar rotas dos handlers
	pipelineHandler := s.container.GetPipelineHandler()
	pipelineHandler.RegisterRoutes(s.echo)

	pluginHandler := s.container.GetPluginHandler()
	pluginHandler.RegisterRoutes(s.echo)
}

// healthCheck endpoint de health check
func (s *Server) healthCheck(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]interface{}{
		"status":    "ok",
		"version":   "1.0.0",
		"timestamp": time.Now().UTC(),
		"uptime":    time.Since(startTime).String(),
	})
}

// apiDocumentation endpoint de documentação da API
func (s *Server) apiDocumentation(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]interface{}{
		"name":        "FLEXT API",
		"description": "Unified Hexagonal Architecture + DDD Implementation",
		"version":     "1.0.0",
		"endpoints": map[string]interface{}{
			"health": "GET /health",
			"metrics": "GET /metrics",
			"pipelines": map[string]string{
				"create":    "POST /api/v1/pipelines",
				"get":       "GET /api/v1/pipelines/:id",
				"list":      "GET /api/v1/pipelines",
				"add_step":  "POST /api/v1/pipelines/:id/steps",
			},
			"plugins": map[string]string{
				"register": "POST /api/v1/plugins",
				"get":      "GET /api/v1/plugins/:id",
				"list":     "GET /api/v1/plugins",
			},
		},
	})
}

// metricsEndpoint endpoint básico de métricas
func (s *Server) metricsEndpoint(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]interface{}{
		"server": map[string]interface{}{
			"uptime": time.Since(startTime).String(),
			"version": "1.0.0",
		},
		"requests": map[string]interface{}{
			"total": "Not implemented", // TODO: implementar contador
		},
	})
}

// Start inicia o servidor com graceful shutdown
func (s *Server) Start() error {
	// Canal para capturar sinais do sistema
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)

	// Iniciar servidor em goroutine
	go func() {
		address := fmt.Sprintf("%s:%s", s.config.Server.Host, s.config.Server.Port)
		s.logger.Info("Starting FLEXT server", 
			logging.F("address", address),
			logging.F("environment", os.Getenv("ENVIRONMENT")),
		)
		
		if err := s.echo.Start(address); err != nil && err != http.ErrServerClosed {
			s.logger.Error("Server failed to start", logging.F("error", err.Error()))
		}
	}()

	// Aguardar sinal de shutdown
	<-quit
	s.logger.Info("Shutting down server...")

	// Criar contexto com timeout para shutdown
	ctx, cancel := context.WithTimeout(context.Background(), s.config.Server.ShutdownTimeout)
	defer cancel()

	// Graceful shutdown
	if err := s.echo.Shutdown(ctx); err != nil {
		s.logger.Error("Server forced to shutdown", logging.F("error", err.Error()))
		return err
	}

	s.logger.Info("Server stopped gracefully")
	return nil
}

// startTime para calcular uptime
var startTime = time.Now()