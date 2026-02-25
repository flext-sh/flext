// Package server - HTTP Server implementation for FLEXT Service
package server

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/flext-sh/flext/pkg/controlpanel/configuration/config"
	"github.com/flext-sh/flext/pkg/logging"
	"github.com/gin-gonic/gin"
)

// Server represents the HTTP server for FLEXT Service
type Server struct {
	config     *config.Config
	logger     logging.Logger
	router     *gin.Engine
	httpServer *http.Server
}

// NewServer creates a new HTTP server
func NewServer(cfg *config.Config, logger logging.Logger) *Server {
	// Set gin mode based on environment
	if cfg.Server.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	} else {
		gin.SetMode(gin.DebugMode)
	}

	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	return &Server{
		config: cfg,
		logger: logger,
		router: router,
	}
}

// SetupBasicRoutes sets up basic health check routes
func (s *Server) SetupBasicRoutes() {
	s.router.GET("/health", s.healthCheck)
	s.router.GET("/api/v1/health", s.healthCheck)

	// FLEXT Service basic routes (detailed routes registered by handlers)
	v1 := s.router.Group("/api/v1")
	{
		v1.GET("/status", s.statusCheck)
		v1.GET("/info", s.getServiceInfo)
	}
}

// HandlerRegistrar interface for handlers that can register routes
type HandlerRegistrar interface {
	RegisterRoutes(router *gin.RouterGroup)
}

// RegisterHandler registers a handler with route registration
func (s *Server) RegisterHandler(handler interface{}) {
	if handlerRegistrar, ok := handler.(HandlerRegistrar); ok {
		// Register routes for handlers that implement HandlerRegistrar interface
		v1 := s.router.Group("/api/v1")
		handlerRegistrar.RegisterRoutes(v1)
		s.logger.Info("Handler registered with routes",
			logging.F("handler", fmt.Sprintf("%T", handler)),
			logging.F("routes", "✅ Routes registered"))
	} else {
		s.logger.Info("Handler registered (no routes)",
			logging.F("handler", fmt.Sprintf("%T", handler)))
	}
}

// RegisterCleanHandler registers a clean handler (placeholder)
func (s *Server) RegisterCleanHandler(name string, handler interface{}) {
	s.logger.Info("Clean handler registered", logging.F("name", name), logging.F("handler", fmt.Sprintf("%T", handler)))
}

// Start starts the HTTP server
func (s *Server) Start() error {
	addr := fmt.Sprintf("%s:%d", s.config.Server.Host, s.config.Server.Port)

	s.httpServer = &http.Server{
		Addr:         addr,
		Handler:      s.router,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	s.logger.Info("Starting FLEXT HTTP server", logging.F("address", addr))
	return s.httpServer.ListenAndServe()
}

// Stop gracefully stops the HTTP server
func (s *Server) Stop(ctx context.Context) error {
	if s.httpServer == nil {
		return nil
	}

	s.logger.Info("Stopping FLEXT HTTP server")
	return s.httpServer.Shutdown(ctx)
}

// healthCheck handles health check requests
func (s *Server) healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "ok",
		"timestamp": time.Now().Format(time.RFC3339),
		"service":   "flext",
		"version":   "2.0.0",
		"port":      s.config.Server.Port,
	})
}

// statusCheck handles status requests with detailed information
func (s *Server) statusCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"service":     "flext",
		"version":     "2.0.0",
		"status":      "operational",
		"environment": s.config.Server.Environment,
		"debug":       s.config.Server.Debug,
		"timestamp":   time.Now().Format(time.RFC3339),
		"endpoints": gin.H{
			"health":   "/health",
			"status":   "/api/v1/status",
			"info":     "/api/v1/info",
			"meltano":  "/api/v1/meltano",
			"singer":   "/api/v1/singer",
			"dbt":      "/api/v1/dbt",
			"flexcore": "/api/v1/flexcore",
		},
	})
}

// getServiceInfo handles service info requests
func (s *Server) getServiceInfo(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"service":      "flext-control-panel",
		"version":      "2.0.0",
		"description":  "FLEXT Service Control Panel - Manages and coordinates FlexCore distributed runtime services",
		"architecture": "Clean Architecture + DDD + CQRS",
		"environment":  s.config.Server.Environment,
		"debug":        s.config.Server.Debug,
		"timestamp":    time.Now().Format(time.RFC3339),
		"capabilities": []string{
			"flexcore_coordination",
			"meltano_orchestration",
			"singer_tap_management",
			"dbt_model_execution",
			"distributed_runtime_monitoring",
		},
		"handlers": gin.H{
			"flexcore": "FlexCore coordination and monitoring",
			"meltano":  "Meltano + Singer + DBT orchestration",
		},
	})
}

// Placeholder methods removed - implemented by real handlers
