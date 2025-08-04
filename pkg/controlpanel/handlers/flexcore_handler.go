// Package handlers - FlexCore Handler for FLEXT Service Control Panel
package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/flext-sh/flext/pkg/controlpanel/configuration/config"
	"github.com/flext-sh/flext/pkg/logging"
	"github.com/gin-gonic/gin"
)

// FlexCoreHandler manages FlexCore service coordination and communication
type FlexCoreHandler struct {
	config     *config.Config
	logger     logging.Logger
	httpClient *http.Client
}

// NewFlexCoreHandler creates a new FlexCore handler
func NewFlexCoreHandler(cfg *config.Config, logger logging.Logger) *FlexCoreHandler {
	return &FlexCoreHandler{
		config: cfg,
		logger: logger,
		httpClient: &http.Client{
			Timeout: cfg.FlexCore.Timeout,
		},
	}
}

// RegisterRoutes registers FlexCore handler routes
func (h *FlexCoreHandler) RegisterRoutes(router *gin.RouterGroup) {
	flexcore := router.Group("/flexcore")
	{
		// FlexCore service coordination
		flexcore.GET("/health", h.GetFlexCoreHealth)
		flexcore.GET("/status", h.GetFlexCoreStatus)
		flexcore.GET("/instances", h.ListFlexCoreInstances)
		
		// Plugin management
		flexcore.GET("/plugins", h.ListFlexCorePlugins)
		flexcore.POST("/plugins/:id/execute", h.ExecuteFlexCorePlugin)
		flexcore.GET("/plugins/:id/status", h.GetPluginExecutionStatus)
		flexcore.DELETE("/plugins/:id/stop", h.StopPluginExecution)
		
		// Runtime coordination
		flexcore.GET("/runtimes", h.ListAvailableRuntimes)
		flexcore.POST("/runtimes/:type/execute", h.ExecuteOnRuntime)
		flexcore.GET("/runtimes/:type/status", h.GetRuntimeStatus)
		
		// Workflow management
		flexcore.GET("/workflows", h.ListActiveWorkflows)
		flexcore.POST("/workflows", h.CreateWorkflow)
		flexcore.GET("/workflows/:id", h.GetWorkflowStatus)
		flexcore.DELETE("/workflows/:id", h.StopWorkflow)
		
		// Configuration management
		flexcore.POST("/config/update", h.UpdateFlexCoreConfig)
		flexcore.GET("/config", h.GetFlexCoreConfig)
		
		// Coordination commands
		flexcore.POST("/coordination/command", h.ExecuteCoordinationCommand)
		flexcore.GET("/coordination/topology", h.GetServiceTopology)
	}
}

// FlexCoreHealthResponse represents FlexCore health check response
type FlexCoreHealthResponse struct {
	Status       string                 `json:"status"`
	Version      string                 `json:"version"`
	Uptime       string                 `json:"uptime"`
	Runtimes     []RuntimeStatus        `json:"runtimes"`
	Plugins      []PluginInfo          `json:"plugins"`
	Capabilities map[string]interface{} `json:"capabilities"`
	Metrics      HealthMetrics         `json:"metrics"`
	Timestamp    string                `json:"timestamp"`
}

// RuntimeStatus represents the status of a runtime
type RuntimeStatus struct {
	Type         string                 `json:"type"`
	Status       string                 `json:"status"`
	Version      string                 `json:"version"`
	LastActivity string                 `json:"last_activity"`
	Metrics      map[string]interface{} `json:"metrics"`
}

// PluginInfo represents plugin information
type PluginInfo struct {
	ID           string                 `json:"id"`
	Name         string                 `json:"name"`
	Version      string                 `json:"version"`
	Status       string                 `json:"status"`
	Capabilities []string               `json:"capabilities"`
	Metadata     map[string]interface{} `json:"metadata"`
}

// HealthMetrics represents health metrics
type HealthMetrics struct {
	CPUUsage    float64 `json:"cpu_usage"`
	MemoryUsage float64 `json:"memory_usage"`
	DiskUsage   float64 `json:"disk_usage"`
	Connections int     `json:"connections"`
	Requests    int64   `json:"requests"`
}

// GetFlexCoreHealth gets FlexCore health status
func (h *FlexCoreHandler) GetFlexCoreHealth(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	// Request detailed health check from FlexCore
	url := fmt.Sprintf("%s/api/v1/health?detail=true", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create FlexCore health request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to create health request",
			"details": err.Error(),
		})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("FlexCore health check failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"status":      "unhealthy",
			"error":       "FlexCore unreachable",
			"flexcore_url": h.config.FlexCore.URL,
			"details":     err.Error(),
			"timestamp":   time.Now().Format(time.RFC3339),
		})
		return
	}
	defer resp.Body.Close()

	var healthResponse FlexCoreHealthResponse
	if err := json.NewDecoder(resp.Body).Decode(&healthResponse); err != nil {
		h.logger.Error("Failed to decode FlexCore health response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to decode health response",
			"details": err.Error(),
		})
		return
	}

	// Add FLEXT Service coordination metadata
	response := gin.H{
		"flext_service": gin.H{
			"status":     "coordinating",
			"timestamp":  time.Now().Format(time.RFC3339),
			"version":    "2.0.0",
		},
		"flexcore": healthResponse,
		"coordination": gin.H{
			"active_connections": 1,
			"last_sync":         time.Now().Format(time.RFC3339),
			"coordination_mode": "active",
		},
	}

	c.JSON(http.StatusOK, response)
}

// GetFlexCoreStatus gets detailed FlexCore status
func (h *FlexCoreHandler) GetFlexCoreStatus(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 15*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/status", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create FlexCore status request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to create status request",
		})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("FlexCore status check failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error":       "FlexCore status unavailable",
			"flexcore_url": h.config.FlexCore.URL,
		})
		return
	}
	defer resp.Body.Close()

	var statusResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&statusResponse); err != nil {
		h.logger.Error("Failed to decode FlexCore status response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to decode status response",
		})
		return
	}

	c.JSON(http.StatusOK, statusResponse)
}

// ListFlexCoreInstances lists available FlexCore instances
func (h *FlexCoreHandler) ListFlexCoreInstances(c *gin.Context) {
	// For now, return the single configured FlexCore instance
	// In the future, this could discover multiple FlexCore instances via service discovery
	instances := []gin.H{
		{
			"id":         "flexcore-primary",
			"url":        h.config.FlexCore.URL,
			"status":     "active",
			"type":       "primary",
			"version":    "2.0.0",
			"last_seen":  time.Now().Format(time.RFC3339),
			"capabilities": []string{
				"meltano_runtime",
				"plugin_system",
				"workflow_orchestration",
			},
		},
	}

	c.JSON(http.StatusOK, gin.H{
		"instances": instances,
		"total":     len(instances),
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// ListFlexCorePlugins lists available FlexCore plugins
func (h *FlexCoreHandler) ListFlexCorePlugins(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/plugins", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create FlexCore plugins request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create plugins request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("FlexCore plugins request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "FlexCore plugins unavailable"})
		return
	}
	defer resp.Body.Close()

	var pluginsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&pluginsResponse); err != nil {
		h.logger.Error("Failed to decode FlexCore plugins response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode plugins response"})
		return
	}

	c.JSON(http.StatusOK, pluginsResponse)
}

// ExecuteFlexCorePlugin executes a FlexCore plugin
func (h *FlexCoreHandler) ExecuteFlexCorePlugin(c *gin.Context) {
	pluginID := c.Param("id")
	if pluginID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Plugin ID is required"})
		return
	}

	var executionRequest map[string]interface{}
	if err := c.ShouldBindJSON(&executionRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid execution request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()

	// Add FLEXT Service coordination metadata
	executionRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
	}

	payload, err := json.Marshal(executionRequest)
	if err != nil {
		h.logger.Error("Failed to marshal execution request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare execution request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/plugins/%s/execute", h.config.FlexCore.URL, pluginID)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create plugin execution request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create execution request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Plugin execution request failed", 
			logging.F("error", err),
			logging.F("plugin_id", pluginID))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Plugin execution failed"})
		return
	}
	defer resp.Body.Close()

	var executionResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&executionResponse); err != nil {
		h.logger.Error("Failed to decode plugin execution response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode execution response"})
		return
	}

	h.logger.Info("Plugin execution coordinated successfully", 
		logging.F("plugin_id", pluginID),
		logging.F("correlation_id", executionRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, executionResponse)
}

// GetPluginExecutionStatus gets plugin execution status
func (h *FlexCoreHandler) GetPluginExecutionStatus(c *gin.Context) {
	pluginID := c.Param("id")
	executionID := c.Query("execution_id")

	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/plugins/%s/status", h.config.FlexCore.URL, pluginID)
	if executionID != "" {
		url += fmt.Sprintf("?execution_id=%s", executionID)
	}

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create plugin status request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create status request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Plugin status request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Plugin status unavailable"})
		return
	}
	defer resp.Body.Close()

	var statusResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&statusResponse); err != nil {
		h.logger.Error("Failed to decode plugin status response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode status response"})
		return
	}

	c.JSON(resp.StatusCode, statusResponse)
}

// StopPluginExecution stops plugin execution
func (h *FlexCoreHandler) StopPluginExecution(c *gin.Context) {
	pluginID := c.Param("id")
	executionID := c.Query("execution_id")

	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/plugins/%s/stop", h.config.FlexCore.URL, pluginID)
	if executionID != "" {
		url += fmt.Sprintf("?execution_id=%s", executionID)
	}

	req, err := http.NewRequestWithContext(ctx, "DELETE", url, nil)
	if err != nil {
		h.logger.Error("Failed to create plugin stop request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create stop request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Plugin stop request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Plugin stop failed"})
		return
	}
	defer resp.Body.Close()

	var stopResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&stopResponse); err != nil {
		h.logger.Error("Failed to decode plugin stop response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode stop response"})
		return
	}

	h.logger.Info("Plugin execution stop coordinated", 
		logging.F("plugin_id", pluginID),
		logging.F("execution_id", executionID))

	c.JSON(resp.StatusCode, stopResponse)
}

// ListAvailableRuntimes lists available execution runtimes
func (h *FlexCoreHandler) ListAvailableRuntimes(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create runtimes request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create runtimes request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Runtimes request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Runtimes unavailable"})
		return
	}
	defer resp.Body.Close()

	var runtimesResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&runtimesResponse); err != nil {
		h.logger.Error("Failed to decode runtimes response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode runtimes response"})
		return
	}

	c.JSON(http.StatusOK, runtimesResponse)
}

// ExecuteOnRuntime executes a task on a specific runtime
func (h *FlexCoreHandler) ExecuteOnRuntime(c *gin.Context) {
	runtimeType := c.Param("type")
	if runtimeType == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Runtime type is required"})
		return
	}

	var executionRequest map[string]interface{}
	if err := c.ShouldBindJSON(&executionRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid execution request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 300*time.Second) // 5 minutes for runtime execution
	defer cancel()

	// Add FLEXT Service coordination metadata
	executionRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-runtime-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"runtime_type":     runtimeType,
	}

	payload, err := json.Marshal(executionRequest)
	if err != nil {
		h.logger.Error("Failed to marshal runtime execution request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare execution request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/%s/execute", h.config.FlexCore.URL, runtimeType)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create runtime execution request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create execution request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Runtime execution request failed", 
			logging.F("error", err),
			logging.F("runtime_type", runtimeType))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Runtime execution failed"})
		return
	}
	defer resp.Body.Close()

	var executionResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&executionResponse); err != nil {
		h.logger.Error("Failed to decode runtime execution response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode execution response"})
		return
	}

	h.logger.Info("Runtime execution coordinated successfully", 
		logging.F("runtime_type", runtimeType),
		logging.F("correlation_id", executionRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, executionResponse)
}

// GetRuntimeStatus gets runtime status
func (h *FlexCoreHandler) GetRuntimeStatus(c *gin.Context) {
	runtimeType := c.Param("type")
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/%s/status", h.config.FlexCore.URL, runtimeType)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create runtime status request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create status request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Runtime status request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Runtime status unavailable"})
		return
	}
	defer resp.Body.Close()

	var statusResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&statusResponse); err != nil {
		h.logger.Error("Failed to decode runtime status response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode status response"})
		return
	}

	c.JSON(resp.StatusCode, statusResponse)
}

// ListActiveWorkflows lists active workflows
func (h *FlexCoreHandler) ListActiveWorkflows(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/workflows", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create workflows request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create workflows request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Workflows request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Workflows unavailable"})
		return
	}
	defer resp.Body.Close()

	var workflowsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&workflowsResponse); err != nil {
		h.logger.Error("Failed to decode workflows response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode workflows response"})
		return
	}

	c.JSON(http.StatusOK, workflowsResponse)
}

// CreateWorkflow creates a new workflow
func (h *FlexCoreHandler) CreateWorkflow(c *gin.Context) {
	var workflowRequest map[string]interface{}
	if err := c.ShouldBindJSON(&workflowRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid workflow request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	// Add FLEXT Service coordination metadata
	workflowRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-workflow-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
	}

	payload, err := json.Marshal(workflowRequest)
	if err != nil {
		h.logger.Error("Failed to marshal workflow request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare workflow request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/workflows", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create workflow request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create workflow request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Workflow creation request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Workflow creation failed"})
		return
	}
	defer resp.Body.Close()

	var workflowResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&workflowResponse); err != nil {
		h.logger.Error("Failed to decode workflow response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode workflow response"})
		return
	}

	h.logger.Info("Workflow creation coordinated successfully", 
		logging.F("correlation_id", workflowRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, workflowResponse)
}

// GetWorkflowStatus gets workflow status
func (h *FlexCoreHandler) GetWorkflowStatus(c *gin.Context) {
	workflowID := c.Param("id")
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/workflows/%s", h.config.FlexCore.URL, workflowID)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create workflow status request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create status request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Workflow status request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Workflow status unavailable"})
		return
	}
	defer resp.Body.Close()

	var statusResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&statusResponse); err != nil {
		h.logger.Error("Failed to decode workflow status response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode status response"})
		return
	}

	c.JSON(resp.StatusCode, statusResponse)
}

// StopWorkflow stops a workflow
func (h *FlexCoreHandler) StopWorkflow(c *gin.Context) {
	workflowID := c.Param("id")
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/workflows/%s", h.config.FlexCore.URL, workflowID)
	req, err := http.NewRequestWithContext(ctx, "DELETE", url, nil)
	if err != nil {
		h.logger.Error("Failed to create workflow stop request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create stop request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Workflow stop request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Workflow stop failed"})
		return
	}
	defer resp.Body.Close()

	var stopResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&stopResponse); err != nil {
		h.logger.Error("Failed to decode workflow stop response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode stop response"})
		return
	}

	h.logger.Info("Workflow stop coordinated", logging.F("workflow_id", workflowID))

	c.JSON(resp.StatusCode, stopResponse)
}

// UpdateFlexCoreConfig updates FlexCore configuration
func (h *FlexCoreHandler) UpdateFlexCoreConfig(c *gin.Context) {
	var configUpdate map[string]interface{}
	if err := c.ShouldBindJSON(&configUpdate); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid config update", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	// Add FLEXT Service coordination metadata
	configUpdate["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-config-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
	}

	payload, err := json.Marshal(configUpdate)
	if err != nil {
		h.logger.Error("Failed to marshal config update", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare config update"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/config/update", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create config update request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create config request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Config update request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Config update failed"})
		return
	}
	defer resp.Body.Close()

	var updateResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&updateResponse); err != nil {
		h.logger.Error("Failed to decode config update response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode update response"})
		return
	}

	h.logger.Info("FlexCore config update coordinated successfully", 
		logging.F("correlation_id", configUpdate["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, updateResponse)
}

// GetFlexCoreConfig gets FlexCore configuration
func (h *FlexCoreHandler) GetFlexCoreConfig(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/config", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create config request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create config request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Config request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Config unavailable"})
		return
	}
	defer resp.Body.Close()

	var configResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&configResponse); err != nil {
		h.logger.Error("Failed to decode config response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode config response"})
		return
	}

	c.JSON(http.StatusOK, configResponse)
}

// ExecuteCoordinationCommand executes a coordination command
func (h *FlexCoreHandler) ExecuteCoordinationCommand(c *gin.Context) {
	var commandRequest map[string]interface{}
	if err := c.ShouldBindJSON(&commandRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid command request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()

	// Add FLEXT Service coordination metadata
	commandRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-command-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"command_type":     "coordination",
	}

	payload, err := json.Marshal(commandRequest)
	if err != nil {
		h.logger.Error("Failed to marshal command request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare command request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/coordination/command", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create coordination command request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create command request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Coordination command request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Coordination command failed"})
		return
	}
	defer resp.Body.Close()

	var commandResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&commandResponse); err != nil {
		h.logger.Error("Failed to decode command response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode command response"})
		return
	}

	h.logger.Info("Coordination command executed successfully", 
		logging.F("correlation_id", commandRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, commandResponse)
}

// GetServiceTopology gets service topology information
func (h *FlexCoreHandler) GetServiceTopology(c *gin.Context) {
	// Return current service topology managed by FLEXT Service
	topology := gin.H{
		"flext_service": gin.H{
			"id":       "flext-service-primary",
			"status":   "active",
			"role":     "control_panel",
			"port":     h.config.Server.Port,
			"version":  "2.0.0",
		},
		"flexcore_instances": []gin.H{
			{
				"id":         "flexcore-primary",
				"url":        h.config.FlexCore.URL,
				"status":     "active",
				"role":       "runtime_distribuida",
				"version":    "2.0.0",
				"runtimes":   []string{"meltano", "ray_future", "kubernetes_future"},
			},
		},
		"coordination": gin.H{
			"mode":           "active",
			"connections":    1,
			"last_sync":      time.Now().Format(time.RFC3339),
			"health_status":  "operational",
		},
		"infrastructure": gin.H{
			"database": gin.H{
				"url":    h.config.Database.URL,
				"status": "connected",
			},
			"redis": gin.H{
				"url":    h.config.Redis.URL,
				"status": "connected",
			},
		},
		"timestamp": time.Now().Format(time.RFC3339),
	}

	c.JSON(http.StatusOK, topology)
}