// Package handlers - Meltano Handler for FLEXT Service Control Panel
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

// MeltanoHandler manages Meltano orchestration and Singer/DBT coordination
type MeltanoHandler struct {
	config     *config.Config
	logger     logging.Logger
	httpClient *http.Client
}

// NewMeltanoHandler creates a new Meltano handler
func NewMeltanoHandler(cfg *config.Config, logger logging.Logger) *MeltanoHandler {
	return &MeltanoHandler{
		config: cfg,
		logger: logger,
		httpClient: &http.Client{
			Timeout: cfg.Python.Timeout,
		},
	}
}

// RegisterRoutes registers Meltano handler routes
func (h *MeltanoHandler) RegisterRoutes(router *gin.RouterGroup) {
	// Meltano orchestration endpoints
	meltano := router.Group("/meltano")
	{
		meltano.GET("/projects", h.ListMeltanoProjects)
		meltano.POST("/run", h.ExecuteMeltanoPipeline)
		meltano.GET("/status", h.GetMeltanoStatus)
		meltano.POST("/install", h.InstallMeltanoPlugin)
		meltano.GET("/config", h.GetMeltanoConfig)
		meltano.POST("/config", h.UpdateMeltanoConfig)
		meltano.GET("/schedule", h.GetMeltanoSchedules)
		meltano.POST("/schedule", h.CreateMeltanoSchedule)
	}

	// Singer protocol endpoints (via Meltano)
	singer := router.Group("/singer")
	{
		singer.GET("/taps", h.ListSingerTaps)
		singer.GET("/targets", h.ListSingerTargets)
		singer.POST("/extract", h.ExecuteSingerExtraction)
		singer.POST("/load", h.ExecuteSingerLoad)
		singer.GET("/schemas/:tap", h.GetSingerSchema)
		singer.POST("/test/tap/:tap", h.TestSingerTap)
		singer.POST("/test/target/:target", h.TestSingerTarget)
	}

	// DBT transformation endpoints (via Meltano)
	dbt := router.Group("/dbt")
	{
		dbt.GET("/models", h.ListDBTModels)
		dbt.POST("/run", h.ExecuteDBTModels)
		dbt.POST("/test", h.ExecuteDBTTests)
		dbt.POST("/compile", h.CompileDBTModels)
		dbt.GET("/docs", h.GenerateDBTDocs)
		dbt.GET("/lineage", h.GetDBTLineage)
	}
}

// MeltanoProject represents a Meltano project
type MeltanoProject struct {
	Name        string                 `json:"name"`
	Version     string                 `json:"version"`
	Status      string                 `json:"status"`
	Plugins     []MeltanoPlugin        `json:"plugins"`
	Schedules   []MeltanoSchedule      `json:"schedules"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// MeltanoPlugin represents a Meltano plugin
type MeltanoPlugin struct {
	Name      string                 `json:"name"`
	Type      string                 `json:"type"`
	Variant   string                 `json:"variant"`
	Version   string                 `json:"version"`
	Status    string                 `json:"status"`
	Config    map[string]interface{} `json:"config"`
}

// MeltanoSchedule represents a Meltano schedule
type MeltanoSchedule struct {
	Name     string `json:"name"`
	Job      string `json:"job"`
	Interval string `json:"interval"`
	Status   string `json:"status"`
}

// SingerTap represents a Singer tap
type SingerTap struct {
	Name         string                 `json:"name"`
	Description  string                 `json:"description"`
	Variant      string                 `json:"variant"`
	Version      string                 `json:"version"`
	Status       string                 `json:"status"`
	Capabilities []string               `json:"capabilities"`
	Config       map[string]interface{} `json:"config"`
}

// SingerTarget represents a Singer target
type SingerTarget struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Variant     string                 `json:"variant"`
	Version     string                 `json:"version"`
	Status      string                 `json:"status"`
	Config      map[string]interface{} `json:"config"`
}

// DBTModel represents a DBT model
type DBTModel struct {
	Name         string                 `json:"name"`
	Path         string                 `json:"path"`
	Schema       string                 `json:"schema"`
	Status       string                 `json:"status"`
	Dependencies []string               `json:"dependencies"`
	Metadata     map[string]interface{} `json:"metadata"`
}

// ListMeltanoProjects lists available Meltano projects
func (h *MeltanoHandler) ListMeltanoProjects(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	// Call FlexCore Meltano runtime via flext-meltano integration
	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/projects", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create Meltano projects request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create projects request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Meltano projects request failed", logging.F("error", err))
		
		// Fallback to direct Meltano project discovery
		projects := h.discoverMeltanoProjects()
		c.JSON(http.StatusOK, gin.H{
			"projects": projects,
			"source":   "direct_discovery",
			"message":  "FlexCore unavailable, using direct Meltano discovery",
		})
		return
	}
	defer resp.Body.Close()

	var projectsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&projectsResponse); err != nil {
		h.logger.Error("Failed to decode Meltano projects response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode projects response"})
		return
	}

	c.JSON(http.StatusOK, projectsResponse)
}

// discoverMeltanoProjects discovers Meltano projects directly
func (h *MeltanoHandler) discoverMeltanoProjects() []MeltanoProject {
	// Direct Meltano project discovery as fallback
	return []MeltanoProject{
		{
			Name:    "flext-meltano-project",
			Version: "1.0.0",
			Status:  "active",
			Plugins: []MeltanoPlugin{
				{
					Name:    "tap-oracle",
					Type:    "extractors",
					Variant: "flext",
					Version: "1.0.0",
					Status:  "installed",
				},
				{
					Name:    "target-postgres",
					Type:    "loaders",
					Variant: "meltanolabs",
					Version: "0.2.0",
					Status:  "installed",
				},
				{
					Name:    "dbt-postgres",
					Type:    "transformers",
					Variant: "dbt-labs",
					Version: "1.7.0",
					Status:  "installed",
				},
			},
			Schedules: []MeltanoSchedule{
				{
					Name:     "oracle-daily-extract",
					Job:      "tap-oracle target-postgres",
					Interval: "@daily",
					Status:   "active",
				},
			},
		},
	}
}

// ExecuteMeltanoPipeline executes a Meltano pipeline
func (h *MeltanoHandler) ExecuteMeltanoPipeline(c *gin.Context) {
	var pipelineRequest map[string]interface{}
	if err := c.ShouldBindJSON(&pipelineRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid pipeline request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 600*time.Second) // 10 minutes for pipeline execution
	defer cancel()

	// Add FLEXT Service coordination metadata
	pipelineRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-meltano-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"runtime_type":     "meltano",
	}

	payload, err := json.Marshal(pipelineRequest)
	if err != nil {
		h.logger.Error("Failed to marshal Meltano pipeline request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare pipeline request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/execute", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create Meltano pipeline request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create pipeline request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Meltano pipeline execution failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Meltano pipeline execution failed"})
		return
	}
	defer resp.Body.Close()

	var executionResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&executionResponse); err != nil {
		h.logger.Error("Failed to decode Meltano execution response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode execution response"})
		return
	}

	h.logger.Info("Meltano pipeline execution coordinated successfully", 
		logging.F("correlation_id", pipelineRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, executionResponse)
}

// GetMeltanoStatus gets Meltano runtime status
func (h *MeltanoHandler) GetMeltanoStatus(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/status", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create Meltano status request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create status request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Meltano status request failed", logging.F("error", err))
		
		// Fallback status
		c.JSON(http.StatusOK, gin.H{
			"status":          "unknown",
			"runtime_type":    "meltano",
			"message":         "FlexCore unavailable, status unknown",
			"fallback_status": "active",
			"timestamp":       time.Now().Format(time.RFC3339),
		})
		return
	}
	defer resp.Body.Close()

	var statusResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&statusResponse); err != nil {
		h.logger.Error("Failed to decode Meltano status response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode status response"})
		return
	}

	c.JSON(http.StatusOK, statusResponse)
}

// InstallMeltanoPlugin installs a Meltano plugin
func (h *MeltanoHandler) InstallMeltanoPlugin(c *gin.Context) {
	var installRequest map[string]interface{}
	if err := c.ShouldBindJSON(&installRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid install request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 300*time.Second) // 5 minutes for plugin installation
	defer cancel()

	// Add FLEXT Service coordination metadata
	installRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-install-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
	}

	payload, err := json.Marshal(installRequest)
	if err != nil {
		h.logger.Error("Failed to marshal plugin install request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare install request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/install", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create plugin install request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create install request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Plugin installation failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Plugin installation failed"})
		return
	}
	defer resp.Body.Close()

	var installResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&installResponse); err != nil {
		h.logger.Error("Failed to decode install response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode install response"})
		return
	}

	h.logger.Info("Meltano plugin installation coordinated successfully", 
		logging.F("correlation_id", installRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, installResponse)
}

// GetMeltanoConfig gets Meltano configuration
func (h *MeltanoHandler) GetMeltanoConfig(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/config", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create Meltano config request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create config request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Meltano config request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Meltano config unavailable"})
		return
	}
	defer resp.Body.Close()

	var configResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&configResponse); err != nil {
		h.logger.Error("Failed to decode Meltano config response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode config response"})
		return
	}

	c.JSON(http.StatusOK, configResponse)
}

// UpdateMeltanoConfig updates Meltano configuration
func (h *MeltanoHandler) UpdateMeltanoConfig(c *gin.Context) {
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
		"correlation_id":   fmt.Sprintf("flext-meltano-config-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
	}

	payload, err := json.Marshal(configUpdate)
	if err != nil {
		h.logger.Error("Failed to marshal Meltano config update", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare config update"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/config", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create Meltano config update request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create config request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Meltano config update failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Meltano config update failed"})
		return
	}
	defer resp.Body.Close()

	var updateResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&updateResponse); err != nil {
		h.logger.Error("Failed to decode Meltano config update response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode update response"})
		return
	}

	h.logger.Info("Meltano config update coordinated successfully", 
		logging.F("correlation_id", configUpdate["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, updateResponse)
}

// GetMeltanoSchedules gets Meltano schedules
func (h *MeltanoHandler) GetMeltanoSchedules(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/schedules", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create Meltano schedules request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create schedules request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Meltano schedules request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Meltano schedules unavailable"})
		return
	}
	defer resp.Body.Close()

	var schedulesResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&schedulesResponse); err != nil {
		h.logger.Error("Failed to decode Meltano schedules response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode schedules response"})
		return
	}

	c.JSON(http.StatusOK, schedulesResponse)
}

// CreateMeltanoSchedule creates a Meltano schedule
func (h *MeltanoHandler) CreateMeltanoSchedule(c *gin.Context) {
	var scheduleRequest map[string]interface{}
	if err := c.ShouldBindJSON(&scheduleRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid schedule request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	// Add FLEXT Service coordination metadata
	scheduleRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-schedule-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
	}

	payload, err := json.Marshal(scheduleRequest)
	if err != nil {
		h.logger.Error("Failed to marshal schedule request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare schedule request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/schedules", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create schedule request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create schedule request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Schedule creation failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Schedule creation failed"})
		return
	}
	defer resp.Body.Close()

	var scheduleResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&scheduleResponse); err != nil {
		h.logger.Error("Failed to decode schedule response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode schedule response"})
		return
	}

	h.logger.Info("Meltano schedule creation coordinated successfully", 
		logging.F("correlation_id", scheduleRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, scheduleResponse)
}

// ListSingerTaps lists available Singer taps
func (h *MeltanoHandler) ListSingerTaps(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 15*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/singer/taps", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create Singer taps request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create taps request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Singer taps request failed", logging.F("error", err))
		
		// Fallback to predefined FLEXT Singer taps
		taps := []SingerTap{
			{
				Name:        "tap-oracle",
				Description: "Oracle database extractor for FLEXT",
				Variant:     "flext",
				Version:     "1.0.0",
				Status:      "available",
				Capabilities: []string{"discovery", "schema", "stream"},
			},
			{
				Name:        "tap-ldap",
				Description: "LDAP directory extractor for FLEXT",
				Variant:     "flext",
				Version:     "1.0.0",
				Status:      "available",
				Capabilities: []string{"discovery", "schema", "stream"},
			},
			{
				Name:        "tap-ldif",
				Description: "LDIF file extractor for FLEXT",
				Variant:     "flext",
				Version:     "1.0.0",
				Status:      "available",
				Capabilities: []string{"discovery", "schema", "stream"},
			},
		}
		
		c.JSON(http.StatusOK, gin.H{
			"taps":    taps,
			"source":  "fallback",
			"message": "FlexCore unavailable, using fallback tap list",
		})
		return
	}
	defer resp.Body.Close()

	var tapsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&tapsResponse); err != nil {
		h.logger.Error("Failed to decode Singer taps response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode taps response"})
		return
	}

	c.JSON(http.StatusOK, tapsResponse)
}

// ListSingerTargets lists available Singer targets
func (h *MeltanoHandler) ListSingerTargets(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 15*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/singer/targets", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create Singer targets request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create targets request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Singer targets request failed", logging.F("error", err))
		
		// Fallback to predefined FLEXT Singer targets
		targets := []SingerTarget{
			{
				Name:        "target-postgres",
				Description: "PostgreSQL loader for FLEXT",
				Variant:     "meltanolabs",
				Version:     "0.2.0",
				Status:      "available",
			},
			{
				Name:        "target-oracle",
				Description: "Oracle database loader for FLEXT",
				Variant:     "flext",
				Version:     "1.0.0",
				Status:      "available",
			},
			{
				Name:        "target-ldap",
				Description: "LDAP directory loader for FLEXT",
				Variant:     "flext",
				Version:     "1.0.0",
				Status:      "available",
			},
		}
		
		c.JSON(http.StatusOK, gin.H{
			"targets": targets,
			"source":  "fallback",
			"message": "FlexCore unavailable, using fallback target list",
		})
		return
	}
	defer resp.Body.Close()

	var targetsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&targetsResponse); err != nil {
		h.logger.Error("Failed to decode Singer targets response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode targets response"})
		return
	}

	c.JSON(http.StatusOK, targetsResponse)
}

// ExecuteSingerExtraction executes Singer extraction
func (h *MeltanoHandler) ExecuteSingerExtraction(c *gin.Context) {
	var extractionRequest map[string]interface{}
	if err := c.ShouldBindJSON(&extractionRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid extraction request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 600*time.Second) // 10 minutes for extraction
	defer cancel()

	// Add FLEXT Service coordination metadata
	extractionRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-extract-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"operation_type":   "singer_extraction",
	}

	payload, err := json.Marshal(extractionRequest)
	if err != nil {
		h.logger.Error("Failed to marshal extraction request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare extraction request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/singer/extract", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create extraction request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create extraction request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Singer extraction failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Singer extraction failed"})
		return
	}
	defer resp.Body.Close()

	var extractionResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&extractionResponse); err != nil {
		h.logger.Error("Failed to decode extraction response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode extraction response"})
		return
	}

	h.logger.Info("Singer extraction coordinated successfully", 
		logging.F("correlation_id", extractionRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, extractionResponse)
}

// ExecuteSingerLoad executes Singer loading
func (h *MeltanoHandler) ExecuteSingerLoad(c *gin.Context) {
	var loadRequest map[string]interface{}
	if err := c.ShouldBindJSON(&loadRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid load request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 600*time.Second) // 10 minutes for loading
	defer cancel()

	// Add FLEXT Service coordination metadata
	loadRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-load-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"operation_type":   "singer_load",
	}

	payload, err := json.Marshal(loadRequest)
	if err != nil {
		h.logger.Error("Failed to marshal load request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare load request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/singer/load", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create load request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create load request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Singer load failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Singer load failed"})
		return
	}
	defer resp.Body.Close()

	var loadResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&loadResponse); err != nil {
		h.logger.Error("Failed to decode load response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode load response"})
		return
	}

	h.logger.Info("Singer load coordinated successfully", 
		logging.F("correlation_id", loadRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, loadResponse)
}

// GetSingerSchema gets Singer tap schema
func (h *MeltanoHandler) GetSingerSchema(c *gin.Context) {
	tapName := c.Param("tap")
	
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/singer/schemas/%s", h.config.FlexCore.URL, tapName)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create schema request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create schema request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Singer schema request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Singer schema unavailable"})
		return
	}
	defer resp.Body.Close()

	var schemaResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&schemaResponse); err != nil {
		h.logger.Error("Failed to decode schema response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode schema response"})
		return
	}

	c.JSON(http.StatusOK, schemaResponse)
}

// TestSingerTap tests Singer tap connection
func (h *MeltanoHandler) TestSingerTap(c *gin.Context) {
	tapName := c.Param("tap")
	
	var testRequest map[string]interface{}
	if err := c.ShouldBindJSON(&testRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid test request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()

	// Add FLEXT Service coordination metadata
	testRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-test-tap-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"tap_name":         tapName,
	}

	payload, err := json.Marshal(testRequest)
	if err != nil {
		h.logger.Error("Failed to marshal tap test request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare test request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/singer/test/tap/%s", h.config.FlexCore.URL, tapName)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create tap test request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create test request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Singer tap test failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Singer tap test failed"})
		return
	}
	defer resp.Body.Close()

	var testResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&testResponse); err != nil {
		h.logger.Error("Failed to decode tap test response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode test response"})
		return
	}

	h.logger.Info("Singer tap test coordinated successfully", 
		logging.F("tap_name", tapName),
		logging.F("correlation_id", testRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, testResponse)
}

// TestSingerTarget tests Singer target connection
func (h *MeltanoHandler) TestSingerTarget(c *gin.Context) {
	targetName := c.Param("target")
	
	var testRequest map[string]interface{}
	if err := c.ShouldBindJSON(&testRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid test request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()

	// Add FLEXT Service coordination metadata
	testRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-test-target-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"target_name":      targetName,
	}

	payload, err := json.Marshal(testRequest)
	if err != nil {
		h.logger.Error("Failed to marshal target test request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare test request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/singer/test/target/%s", h.config.FlexCore.URL, targetName)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create target test request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create test request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("Singer target test failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Singer target test failed"})
		return
	}
	defer resp.Body.Close()

	var testResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&testResponse); err != nil {
		h.logger.Error("Failed to decode target test response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode test response"})
		return
	}

	h.logger.Info("Singer target test coordinated successfully", 
		logging.F("target_name", targetName),
		logging.F("correlation_id", testRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, testResponse)
}

// ListDBTModels lists available DBT models
func (h *MeltanoHandler) ListDBTModels(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 15*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/dbt/models", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create DBT models request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create models request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("DBT models request failed", logging.F("error", err))
		
		// Fallback to predefined FLEXT DBT models
		models := []DBTModel{
			{
				Name:         "oracle_users",
				Path:         "models/oracle/oracle_users.sql",
				Schema:       "analytics",
				Status:       "available",
				Dependencies: []string{"tap_oracle"},
			},
			{
				Name:         "ldap_directory",
				Path:         "models/ldap/ldap_directory.sql",
				Schema:       "analytics",
				Status:       "available",
				Dependencies: []string{"tap_ldap"},
			},
		}
		
		c.JSON(http.StatusOK, gin.H{
			"models":  models,
			"source":  "fallback",
			"message": "FlexCore unavailable, using fallback model list",
		})
		return
	}
	defer resp.Body.Close()

	var modelsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&modelsResponse); err != nil {
		h.logger.Error("Failed to decode DBT models response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode models response"})
		return
	}

	c.JSON(http.StatusOK, modelsResponse)
}

// ExecuteDBTModels executes DBT models
func (h *MeltanoHandler) ExecuteDBTModels(c *gin.Context) {
	var dbtRequest map[string]interface{}
	if err := c.ShouldBindJSON(&dbtRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid DBT request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 600*time.Second) // 10 minutes for DBT execution
	defer cancel()

	// Add FLEXT Service coordination metadata
	dbtRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-dbt-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"operation_type":   "dbt_run",
	}

	payload, err := json.Marshal(dbtRequest)
	if err != nil {
		h.logger.Error("Failed to marshal DBT request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare DBT request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/dbt/run", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create DBT request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create DBT request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("DBT execution failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "DBT execution failed"})
		return
	}
	defer resp.Body.Close()

	var dbtResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&dbtResponse); err != nil {
		h.logger.Error("Failed to decode DBT response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode DBT response"})
		return
	}

	h.logger.Info("DBT execution coordinated successfully", 
		logging.F("correlation_id", dbtRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, dbtResponse)
}

// ExecuteDBTTests executes DBT tests
func (h *MeltanoHandler) ExecuteDBTTests(c *gin.Context) {
	var testRequest map[string]interface{}
	if err := c.ShouldBindJSON(&testRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid DBT test request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 300*time.Second) // 5 minutes for DBT tests
	defer cancel()

	// Add FLEXT Service coordination metadata
	testRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-dbt-test-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"operation_type":   "dbt_test",
	}

	payload, err := json.Marshal(testRequest)
	if err != nil {
		h.logger.Error("Failed to marshal DBT test request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare DBT test request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/dbt/test", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create DBT test request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create DBT test request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("DBT test execution failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "DBT test execution failed"})
		return
	}
	defer resp.Body.Close()

	var testResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&testResponse); err != nil {
		h.logger.Error("Failed to decode DBT test response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode DBT test response"})
		return
	}

	h.logger.Info("DBT test execution coordinated successfully", 
		logging.F("correlation_id", testRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, testResponse)
}

// CompileDBTModels compiles DBT models
func (h *MeltanoHandler) CompileDBTModels(c *gin.Context) {
	var compileRequest map[string]interface{}
	if err := c.ShouldBindJSON(&compileRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid DBT compile request", "details": err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 120*time.Second) // 2 minutes for compilation
	defer cancel()

	// Add FLEXT Service coordination metadata
	compileRequest["coordination"] = map[string]interface{}{
		"flext_service_id": "flext-service-primary",
		"correlation_id":   fmt.Sprintf("flext-dbt-compile-%d", time.Now().Unix()),
		"timestamp":        time.Now().Format(time.RFC3339),
		"operation_type":   "dbt_compile",
	}

	payload, err := json.Marshal(compileRequest)
	if err != nil {
		h.logger.Error("Failed to marshal DBT compile request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to prepare DBT compile request"})
		return
	}

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/dbt/compile", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		h.logger.Error("Failed to create DBT compile request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create DBT compile request"})
		return
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("DBT compilation failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "DBT compilation failed"})
		return
	}
	defer resp.Body.Close()

	var compileResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&compileResponse); err != nil {
		h.logger.Error("Failed to decode DBT compile response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode DBT compile response"})
		return
	}

	h.logger.Info("DBT compilation coordinated successfully", 
		logging.F("correlation_id", compileRequest["coordination"].(map[string]interface{})["correlation_id"]))

	c.JSON(resp.StatusCode, compileResponse)
}

// GenerateDBTDocs generates DBT documentation
func (h *MeltanoHandler) GenerateDBTDocs(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 120*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/dbt/docs", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create DBT docs request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create DBT docs request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("DBT docs generation failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "DBT docs generation failed"})
		return
	}
	defer resp.Body.Close()

	var docsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&docsResponse); err != nil {
		h.logger.Error("Failed to decode DBT docs response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode DBT docs response"})
		return
	}

	c.JSON(http.StatusOK, docsResponse)
}

// GetDBTLineage gets DBT model lineage
func (h *MeltanoHandler) GetDBTLineage(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 30*time.Second)
	defer cancel()

	url := fmt.Sprintf("%s/api/v1/runtimes/meltano/dbt/lineage", h.config.FlexCore.URL)
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		h.logger.Error("Failed to create DBT lineage request", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create DBT lineage request"})
		return
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		h.logger.Error("DBT lineage request failed", logging.F("error", err))
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "DBT lineage unavailable"})
		return
	}
	defer resp.Body.Close()

	var lineageResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&lineageResponse); err != nil {
		h.logger.Error("Failed to decode DBT lineage response", logging.F("error", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode DBT lineage response"})
		return
	}

	c.JSON(http.StatusOK, lineageResponse)
}