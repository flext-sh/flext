package server

import (
	"context"
	"net/http"
	"time"

	"github.com/flext-sh/flext/internal/infrastructure/config"
	"github.com/flext-sh/flext/internal/infrastructure/logging"
	"github.com/gin-contrib/cors"
	"github.com/gin-contrib/timeout"
	"github.com/gin-gonic/gin"
	"github.com/pkg/errors"
	"github.com/samber/lo"
)

// GinServer high-performance alternative using Gin framework
type GinServer struct {
	engine *gin.Engine
	config *config.Config
	logger logging.Logger
	server *http.Server
}

// NewGinServer creates a high-performance Gin-based server
func NewGinServer(cfg *config.Config, logger logging.Logger) *GinServer {
	// Set Gin mode based on environment
	if cfg.IsDevelopment() {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	engine := gin.New()

	s := &GinServer{
		engine: engine,
		config: cfg,
		logger: logger,
	}

	s.setupMiddleware()
	s.setupRoutes()

	return s
}

// setupMiddleware configures Gin middleware stack
func (s *GinServer) setupMiddleware() {
	// Custom logging middleware with zerolog
	s.engine.Use(s.loggingMiddleware())

	// Recovery middleware with custom handler
	s.engine.Use(s.recoveryMiddleware())

	// CORS middleware with advanced configuration
	if s.config.Server.EnableCORS {
		corsConfig := cors.Config{
			AllowOrigins:     []string{"*"},
			AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"},
			AllowHeaders:     []string{"Origin", "Content-Length", "Content-Type", "Authorization", "X-Request-ID"},
			AllowCredentials: true,
			MaxAge:           12 * time.Hour,
		}
		s.engine.Use(cors.New(corsConfig))
	}

	// Global timeout middleware
	s.engine.Use(timeout.New(
		timeout.WithTimeout(s.config.Server.ReadTimeout),
		timeout.WithHandler(func(c *gin.Context) {
			c.Next()
		}),
	))

	// Request ID middleware
	s.engine.Use(s.requestIDMiddleware())

	// Performance metrics middleware
	s.engine.Use(s.metricsMiddleware())
}

// setupRoutes configures Gin routes with advanced features
func (s *GinServer) setupRoutes() {
	// Health and info routes
	s.engine.GET("/health", s.healthCheck)
	s.engine.GET("/", s.apiInfo)

	// API v1 group with advanced middleware
	v1 := s.engine.Group("/api/v1")
	v1.Use(s.authMiddleware()) // Authentication for API routes

	// Pipeline routes with functional programming
	pipelines := v1.Group("/pipelines")
	{
		pipelines.GET("", s.listPipelines)
		pipelines.POST("", s.createPipeline)
		pipelines.GET("/:id", s.getPipeline)
		pipelines.PUT("/:id", s.updatePipeline)
		pipelines.DELETE("/:id", s.deletePipeline)
		pipelines.POST("/:id/execute", s.executePipeline)
		pipelines.GET("/:id/status", s.getPipelineStatus)
	}

	// Plugin routes
	plugins := v1.Group("/plugins")
	{
		plugins.GET("", s.listPlugins)
		plugins.POST("", s.registerPlugin)
		plugins.GET("/:id", s.getPlugin)
		plugins.PUT("/:id/toggle", s.togglePlugin)
	}

	// Advanced bulk operations
	bulk := v1.Group("/bulk")
	{
		bulk.POST("/pipelines", s.bulkCreatePipelines)
		bulk.PATCH("/pipelines/status", s.bulkUpdatePipelineStatus)
		bulk.DELETE("/pipelines", s.bulkDeletePipelines)
	}

	// Statistics and analytics
	stats := v1.Group("/stats")
	{
		stats.GET("/overview", s.getOverviewStats)
		stats.GET("/pipelines", s.getPipelineStats)
		stats.GET("/performance", s.getPerformanceStats)
	}
}

// Custom middleware implementations

// loggingMiddleware structured logging with zerolog
func (s *GinServer) loggingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		raw := c.Request.URL.RawQuery

		c.Next()

		latency := time.Since(start)

		if raw != "" {
			path = path + "?" + raw
		}

		s.logger.Info("Request completed",
			logging.F("method", c.Request.Method),
			logging.F("path", path),
			logging.F("status", c.Writer.Status()),
			logging.F("latency", latency.String()),
			logging.F("ip", c.ClientIP()),
			logging.F("user_agent", c.Request.UserAgent()),
			logging.F("request_id", c.GetString("request_id")),
		)
	}
}

// recoveryMiddleware custom panic recovery
func (s *GinServer) recoveryMiddleware() gin.HandlerFunc {
	return gin.CustomRecovery(func(c *gin.Context, recovered interface{}) {
		s.logger.Error("Panic recovered",
			logging.F("error", recovered),
			logging.F("path", c.Request.URL.Path),
			logging.F("method", c.Request.Method),
		)
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
			"error": "Internal server error",
			"code":  "PANIC_RECOVERED",
		})
	})
}

// requestIDMiddleware adds unique request ID
func (s *GinServer) requestIDMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = generateRequestID()
		}
		c.Set("request_id", requestID)
		c.Header("X-Request-ID", requestID)
		c.Next()
	}
}

// metricsMiddleware collects performance metrics
func (s *GinServer) metricsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		duration := time.Since(start)

		// Collect metrics (implementation would integrate with Prometheus)
		s.collectMetrics(c.Request.Method, c.FullPath(), c.Writer.Status(), duration)
	}
}

// authMiddleware JWT authentication
func (s *GinServer) authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Skip auth for health checks
		if c.Request.URL.Path == "/health" || c.Request.URL.Path == "/" {
			c.Next()
			return
		}

		// Extract and validate JWT token
		token := c.GetHeader("Authorization")
		if token == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error": "Authorization header required",
				"code":  "MISSING_AUTH",
			})
			return
		}

		// Validate token (implementation would validate JWT)
		if !s.validateToken(token) {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid authorization token",
				"code":  "INVALID_TOKEN",
			})
			return
		}

		c.Next()
	}
}

// Route handlers with functional programming

// listPipelines with advanced filtering and functional operations
func (s *GinServer) listPipelines(c *gin.Context) {
	// Extract query parameters
	status := c.Query("status")
	tags := c.QueryArray("tags")
	limit := c.DefaultQuery("limit", "20")
	offset := c.DefaultQuery("offset", "0")

	// Mock data for demonstration
	pipelines := s.getMockPipelines()

	// Filter using functional programming
	if status != "" {
		pipelines = lo.Filter(pipelines, func(p map[string]interface{}, _ int) bool {
			return p["status"] == status
		})
	}

	if len(tags) > 0 {
		pipelines = lo.Filter(pipelines, func(p map[string]interface{}, _ int) bool {
			pipelineTags := p["tags"].([]string)
			return lo.SomeBy(tags, func(tag string) bool {
				return lo.Contains(pipelineTags, tag)
			})
		})
	}

	// Transform response using lo.Map
	response := lo.Map(pipelines, func(p map[string]interface{}, _ int) map[string]interface{} {
		return map[string]interface{}{
			"id":         p["id"],
			"name":       p["name"],
			"status":     p["status"],
			"created_at": p["created_at"],
			"step_count": len(p["steps"].([]interface{})),
		}
	})

	c.JSON(http.StatusOK, gin.H{
		"data":   response,
		"total":  len(response),
		"limit":  limit,
		"offset": offset,
	})
}

// bulkCreatePipelines demonstrates advanced bulk operations
func (s *GinServer) bulkCreatePipelines(c *gin.Context) {
	var requests []map[string]interface{}
	if err := c.ShouldBindJSON(&requests); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request body",
			"code":  "INVALID_JSON",
		})
		return
	}

	// Process bulk creation using functional programming
	results := lo.Map(requests, func(req map[string]interface{}, index int) map[string]interface{} {
		// Validate and create pipeline
		if name, ok := req["name"].(string); ok && name != "" {
			return map[string]interface{}{
				"index":   index,
				"id":      generateRequestID(),
				"name":    name,
				"status":  "created",
				"success": true,
			}
		}
		return map[string]interface{}{
			"index":   index,
			"success": false,
			"error":   "Invalid pipeline name",
		}
	})

	// Count successes and failures
	successes := lo.CountBy(results, func(r map[string]interface{}) bool {
		return r["success"].(bool)
	})

	c.JSON(http.StatusOK, gin.H{
		"results":   results,
		"total":     len(requests),
		"succeeded": successes,
		"failed":    len(requests) - successes,
	})
}

// Start starts the Gin server
func (s *GinServer) Start() error {
	s.server = &http.Server{
		Addr:           s.config.Address(),
		Handler:        s.engine,
		ReadTimeout:    s.config.Server.ReadTimeout,
		WriteTimeout:   s.config.Server.WriteTimeout,
		MaxHeaderBytes: 1 << 20, // 1MB
	}

	s.logger.Info("Starting Gin server",
		logging.F("address", s.config.Address()),
		logging.F("mode", gin.Mode()),
	)

	if err := s.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		return errors.Wrap(err, "failed to start Gin server")
	}

	return nil
}

// Stop gracefully stops the server
func (s *GinServer) Stop(ctx context.Context) error {
	s.logger.Info("Stopping Gin server...")
	return s.server.Shutdown(ctx)
}

// Helper methods (simplified implementations)

func (s *GinServer) healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "ok",
		"framework": "gin",
		"version":   "1.0.0",
		"timestamp": time.Now().UTC(),
	})
}

func (s *GinServer) apiInfo(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"name":        "FLEXT API (Gin)",
		"description": "High-performance API with Gin framework",
		"version":     "1.0.0",
		"framework":   "gin",
	})
}

func (s *GinServer) createPipeline(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "create pipeline"})
}
func (s *GinServer) getPipeline(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "get pipeline"})
}
func (s *GinServer) updatePipeline(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "update pipeline"})
}
func (s *GinServer) deletePipeline(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "delete pipeline"})
}
func (s *GinServer) executePipeline(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "execute pipeline"})
}
func (s *GinServer) getPipelineStatus(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "pipeline status"})
}
func (s *GinServer) listPlugins(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "list plugins"})
}
func (s *GinServer) registerPlugin(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "register plugin"})
}
func (s *GinServer) getPlugin(c *gin.Context) { c.JSON(http.StatusOK, gin.H{"message": "get plugin"}) }
func (s *GinServer) togglePlugin(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "toggle plugin"})
}
func (s *GinServer) bulkUpdatePipelineStatus(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "bulk update"})
}
func (s *GinServer) bulkDeletePipelines(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "bulk delete"})
}
func (s *GinServer) getOverviewStats(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "overview stats"})
}
func (s *GinServer) getPipelineStats(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "pipeline stats"})
}
func (s *GinServer) getPerformanceStats(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "performance stats"})
}

func (s *GinServer) validateToken(token string) bool                                        { return true } // Simplified
func (s *GinServer) collectMetrics(method, path string, status int, duration time.Duration) {}              // Simplified
func generateRequestID() string                                                             { return "req-" + time.Now().Format("20060102150405") }

func (s *GinServer) getMockPipelines() []map[string]interface{} {
	return []map[string]interface{}{
		{
			"id":         "1",
			"name":       "Data Pipeline 1",
			"status":     "active",
			"tags":       []string{"data", "etl"},
			"created_at": time.Now(),
			"steps":      []interface{}{},
		},
		{
			"id":         "2",
			"name":       "Data Pipeline 2",
			"status":     "draft",
			"tags":       []string{"analytics"},
			"created_at": time.Now(),
			"steps":      []interface{}{},
		},
	}
}
