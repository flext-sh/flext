// Package server - HTTP Server implementation for FLEXT Service
package server

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/flext-sh/flext/pkg/config"
	"github.com/flext-sh/flext/pkg/logging"
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
	
	// FLEXT Service specific routes
	v1 := s.router.Group("/api/v1")
	{
		v1.GET("/status", s.statusCheck)
		v1.GET("/plugins", s.listPlugins)
		v1.GET("/meltano/projects", s.listMeltanoProjects)
		v1.GET("/singer/taps", s.listSingerTaps)
		v1.GET("/dbt/models", s.listDBTModels)
		v1.GET("/flexcore/health", s.flexcoreHealth)
	}
}

// RegisterHandler registers a handler (placeholder)
func (s *Server) RegisterHandler(handler interface{}) {
	s.logger.Info("Handler registered", logging.F("handler", fmt.Sprintf("%T", handler)))
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
			"health":    "/health",
			"status":    "/api/v1/status",
			"plugins":   "/api/v1/plugins",
			"meltano":   "/api/v1/meltano",
			"singer":    "/api/v1/singer",
			"dbt":       "/api/v1/dbt",
			"flexcore":  "/api/v1/flexcore",
		},
	})
}

// listPlugins handles plugin list requests (placeholder)
func (s *Server) listPlugins(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"plugins": []gin.H{},
		"message": "Plugin list endpoint - implementation pending",
	})
}

// listMeltanoProjects handles Meltano project list requests (placeholder)
func (s *Server) listMeltanoProjects(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"projects": []gin.H{},
		"message":  "Meltano projects list endpoint - implementation pending",
	})
}

// listSingerTaps handles Singer taps list requests (placeholder)
func (s *Server) listSingerTaps(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"taps":    []gin.H{},
		"message": "Singer taps list endpoint - implementation pending",
	})
}

// listDBTModels handles DBT models list requests (placeholder)
func (s *Server) listDBTModels(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"models":  []gin.H{},
		"message": "DBT models list endpoint - implementation pending",
	})
}

// flexcoreHealth handles FlexCore health check requests (placeholder)
func (s *Server) flexcoreHealth(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"flexcore_status": "unknown",
		"message":         "FlexCore health check endpoint - implementation pending",
		"flexcore_url":    s.config.FlexCore.URL,
	})
}