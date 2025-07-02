package server

import (
	"context"
	"net/http"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/go-playground/validator/v10"
	"github.com/labstack/echo/v4"
	echomiddleware "github.com/labstack/echo/v4/middleware"
)

// Server represents an Echo-based HTTP server with comprehensive middleware
type Server struct {
	echo      *echo.Echo
	config    *config.Config
	logger    logging.Logger
	validator *validator.Validate
	server    *http.Server
	metrics   *MetricsCollector
	wsManager *WebSocketManager
}

// NewServer creates a new Echo server with advanced configuration
func NewServer(cfg *config.Config, logger logging.Logger) *Server {
	e := echo.New()
	e.HideBanner = true
	e.HidePort = true

	// Initialize validator
	v := validator.New()

	// Initialize metrics collector
	metricsCollector := NewMetricsCollector()

	// Initialize WebSocket manager if enabled
	var wsManager *WebSocketManager
	if cfg.Features.WebSocketEnabled {
		wsManager = NewWebSocketManager(logger)
		// Start WebSocket manager in background
		ctx := context.Background()
		go wsManager.Run(ctx)
	}

	s := &Server{
		echo:      e,
		config:    cfg,
		logger:    logger,
		validator: v,
		metrics:   metricsCollector,
		wsManager: wsManager,
	}

	// Setup template renderer
	if renderer, err := NewTemplateRenderer("web/templates"); err == nil {
		e.Renderer = renderer
		logger.Info("Template renderer initialized successfully")
	} else {
		logger.Warn("Failed to initialize template renderer", logging.F("error", err.Error()))
	}

	// Set custom validator
	e.Validator = &CustomValidator{validator: v}

	// Setup middleware and error handling
	s.setupMiddleware()
	s.setupErrorHandling()

	return s
}

// CustomValidator wraps the validator
type CustomValidator struct {
	validator *validator.Validate
}

func (cv *CustomValidator) Validate(i interface{}) error {
	return cv.validator.Struct(i)
}

// setupMiddleware configures all middleware with proper initialization
func (s *Server) setupMiddleware() {
	// Request ID middleware - FIRST to ensure all requests have IDs
	s.echo.Use(echomiddleware.RequestIDWithConfig(echomiddleware.RequestIDConfig{
		Generator: func() string {
			return generateEchoRequestID()
		},
	}))

	// Structured logging middleware
	s.echo.Use(echomiddleware.RequestLoggerWithConfig(echomiddleware.RequestLoggerConfig{
		LogURI:      true,
		LogStatus:   true,
		LogLatency:  true,
		LogMethod:   true,
		LogRemoteIP: true,
		LogValuesFunc: func(c echo.Context, v echomiddleware.RequestLoggerValues) error {
			s.logger.Info("Request completed",
				logging.F("method", v.Method),
				logging.F("uri", v.URI),
				logging.F("status", v.Status),
				logging.F("latency", v.Latency.String()),
				logging.F("request_id", c.Response().Header().Get(echo.HeaderXRequestID)),
			)
			return nil
		},
	}))

	// Recovery middleware with proper error handling
	s.echo.Use(echomiddleware.RecoverWithConfig(echomiddleware.RecoverConfig{
		StackSize: 1 << 10, // 1 KB
		LogErrorFunc: func(c echo.Context, err error, stack []byte) error {
			s.logger.Error("[PANIC RECOVER]",
				logging.F("error", err),
				logging.F("stack", string(stack)),
				logging.F("method", c.Request().Method),
				logging.F("uri", c.Request().RequestURI),
				logging.F("request_id", c.Response().Header().Get(echo.HeaderXRequestID)),
			)
			return nil
		},
	}))

	// Metrics middleware
	s.echo.Use(s.metrics.MetricsMiddleware())

	// CORS middleware if enabled
	if s.config.Server.EnableCORS {
		s.echo.Use(echomiddleware.CORSWithConfig(echomiddleware.CORSConfig{
			AllowOrigins:     []string{"*"},
			AllowMethods:     []string{http.MethodGet, http.MethodPost, http.MethodPut, http.MethodPatch, http.MethodDelete, http.MethodHead, http.MethodOptions},
			AllowHeaders:     []string{echo.HeaderOrigin, echo.HeaderContentType, echo.HeaderAccept, echo.HeaderAuthorization, echo.HeaderXRequestID},
			AllowCredentials: true,
			MaxAge:           int((12 * time.Hour).Seconds()),
		}))
	}

	// Timeout middleware disabled temporarily to fix panic issue
	// TODO: Fix timeout middleware nil pointer dereference
	// s.echo.Use(echomiddleware.TimeoutWithConfig(echomiddleware.TimeoutConfig{
	//	Timeout:      s.config.Server.ReadTimeout,
	//	ErrorMessage: `{"error": "Request timeout"}`,
	// }))

	// Rate limiting middleware
	s.echo.Use(echomiddleware.RateLimiterWithConfig(echomiddleware.RateLimiterConfig{
		Store: echomiddleware.NewRateLimiterMemoryStoreWithConfig(
			echomiddleware.RateLimiterMemoryStoreConfig{
				Rate:      10,
				Burst:     30,
				ExpiresIn: 3 * time.Minute,
			},
		),
		IdentifierExtractor: func(ctx echo.Context) (string, error) {
			id := ctx.RealIP()
			return id, nil
		},
		ErrorHandler: func(context echo.Context, err error) error {
			return context.JSON(http.StatusTooManyRequests, map[string]string{
				"error": "Rate limit exceeded",
			})
		},
		DenyHandler: func(context echo.Context, identifier string, err error) error {
			return context.JSON(http.StatusTooManyRequests, map[string]string{
				"error": "Too many requests",
			})
		},
	}))

	// Gzip compression
	s.echo.Use(echomiddleware.GzipWithConfig(echomiddleware.GzipConfig{
		Level: 5,
	}))

	// Security headers
	s.echo.Use(echomiddleware.SecureWithConfig(echomiddleware.SecureConfig{
		XSSProtection:         "1; mode=block",
		ContentTypeNosniff:    "nosniff",
		XFrameOptions:         "DENY",
		HSTSMaxAge:            31536000,
		ContentSecurityPolicy: "default-src 'self'",
	}))

	// Body limit
	s.echo.Use(echomiddleware.BodyLimit("10M"))
}

// setupErrorHandling configures custom error handling
func (s *Server) setupErrorHandling() {
	s.echo.HTTPErrorHandler = func(err error, c echo.Context) {
		// Don't alter response if already sent
		if c.Response().Committed {
			return
		}

		var (
			code = http.StatusInternalServerError
			msg  interface{}
		)

		if he, ok := err.(*echo.HTTPError); ok {
			code = he.Code
			msg = he.Message
		} else {
			msg = err.Error()
		}

		// Log the error
		s.logger.Error("HTTP error",
			logging.F("error", err),
			logging.F("code", code),
			logging.F("method", c.Request().Method),
			logging.F("uri", c.Request().RequestURI),
			logging.F("request_id", c.Response().Header().Get(echo.HeaderXRequestID)),
		)

		// Send error response
		if c.Request().Method == http.MethodHead {
			err = c.NoContent(code)
		} else {
			err = c.JSON(code, map[string]interface{}{
				"error":      msg,
				"status":     code,
				"request_id": c.Response().Header().Get(echo.HeaderXRequestID),
				"timestamp":  time.Now().Unix(),
			})
		}

		if err != nil {
			s.logger.Error("Failed to send error response", logging.F("error", err))
		}
	}
}

// RegisterHandler registers a handler that can register its own routes
func (s *Server) RegisterHandler(handler interface{}) {
	if h, ok := handler.(interface {
		RegisterRoutes(*echo.Echo)
	}); ok {
		h.RegisterRoutes(s.echo)
	}
}

// RegisterCleanHandler registers Clean Architecture handlers with proper logging
func (s *Server) RegisterCleanHandler(name string, handler interface{}) {
	if h, ok := handler.(interface {
		RegisterRoutes(*echo.Echo)
	}); ok {
		h.RegisterRoutes(s.echo)
		s.logger.Info("Clean Architecture handler registered",
			logging.F("handler", name))
	} else {
		s.logger.Warn("Failed to register Clean Architecture handler",
			logging.F("handler", name),
			logging.F("reason", "handler does not implement RegisterRoutes interface"))
	}
}

// SetupBasicRoutes sets up basic health and info routes
func (s *Server) SetupBasicRoutes() {
	// Health check
	s.echo.GET("/health", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]interface{}{
			"status":     "healthy",
			"timestamp":  time.Now().Unix(),
			"request_id": c.Response().Header().Get(echo.HeaderXRequestID),
		})
	})

	// API info
	s.echo.GET("/", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]interface{}{
			"name":       "FLEXT API",
			"message":    "FLEXT API v1.0",
			"version":    "1.0",
			"timestamp":  time.Now().Unix(),
			"request_id": c.Response().Header().Get(echo.HeaderXRequestID),
		})
	})

	// Prometheus metrics endpoint
	s.echo.GET("/metrics", func(c echo.Context) error {
		metrics := s.metrics.GetPrometheusMetrics()
		return c.String(http.StatusOK, metrics)
	})

	// WebSocket endpoint if enabled
	if s.config.Features.WebSocketEnabled && s.wsManager != nil {
		s.echo.GET("/ws", s.wsManager.HandleWebSocket)
	}
}

// Start starts the Echo server
func (s *Server) Start() error {
	s.server = &http.Server{
		Addr:           s.config.Address(),
		Handler:        s.echo,
		ReadTimeout:    s.config.Server.ReadTimeout,
		WriteTimeout:   s.config.Server.WriteTimeout,
		IdleTimeout:    s.config.Server.IdleTimeout,
		MaxHeaderBytes: 1 << 20, // 1MB
	}

	s.logger.Info("Starting Echo server",
		logging.F("address", s.config.Address()),
		logging.F("environment", s.config.Server.Environment),
	)

	// Start server in a goroutine to enable graceful shutdown
	go func() {
		if err := s.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			s.logger.Error("Server failed to start", logging.F("error", err.Error()))
		}
	}()

	return nil
}

// Stop gracefully stops the server
func (s *Server) Stop(ctx context.Context) error {
	s.logger.Info("Stopping Echo server...")
	return s.server.Shutdown(ctx)
}

// GetEcho returns the underlying Echo instance
func (s *Server) GetEcho() *echo.Echo {
	return s.echo
}

// generateEchoRequestID generates a unique request ID for Echo
func generateEchoRequestID() string {
	return "req-" + time.Now().Format("20060102150405") + "-" + generateRandomString(8)
}

// generateRandomString generates a random string of given length
func generateRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[time.Now().UnixNano()%int64(len(charset))]
	}
	return string(b)
}
