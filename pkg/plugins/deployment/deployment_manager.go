// Package deployment - Plugin Deployment Manager Implementation
//
// This package implements the plugin deployment manager that coordinates
// the deployment of plugins from FLEXT Service to multiple FlexCore instances.
//
// Architecture:
//   - FLEXT Service: Central deployment coordination
//   - FlexCore Instances: Distributed runtime targets
//   - Plugin Binaries: .so/.dll files deployed to FlexCore instances
//   - Communication Bus: Inter-FlexCore coordination via Redis/message queue
//
// Deployment Process:
//   1. Plugin binary transfer to FlexCore instances
//   2. Plugin loading and initialization
//   3. Plugin configuration and validation
//   4. Inter-plugin communication setup
//   5. Health monitoring and status tracking
//
// Author: FLEXT Development Team
// Version: 2.0.0
// License: MIT
package deployment

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
	"github.com/flext-sh/flext/pkg/plugins/registry"
)

// PluginDeploymentManager implements plugin deployment coordination
type PluginDeploymentManager struct {
	registry      *registry.PluginRegistry
	flexcoreClient plugins.FlexCoreClient
	communicator  plugins.PluginCommunicator
	httpClient    *http.Client
	deploymentQueue []DeploymentTask
	mu            sync.RWMutex
	ctx           context.Context
	cancel        context.CancelFunc
}

// DeploymentTask represents a plugin deployment task
type DeploymentTask struct {
	ID              string                         `json:"id"`
	PluginID        plugins.PluginID               `json:"plugin_id"`
	FlexCoreNodes   []string                       `json:"flexcore_nodes"`
	Action          string                         `json:"action"` // deploy, undeploy, update
	Config          map[string]interface{}         `json:"config"`
	Status          string                         `json:"status"`
	Progress        float64                        `json:"progress"`
	ErrorMessage    string                         `json:"error_message,omitempty"`
	CreatedAt       time.Time                      `json:"created_at"`
	StartedAt       *time.Time                     `json:"started_at,omitempty"`
	CompletedAt     *time.Time                     `json:"completed_at,omitempty"`
	Results         map[string]interface{}         `json:"results,omitempty"`
}

// DeploymentResult represents the result of a deployment operation
type DeploymentResult struct {
	TaskID        string                 `json:"task_id"`
	PluginID      plugins.PluginID       `json:"plugin_id"`
	Success       bool                   `json:"success"`
	DeployedNodes []string               `json:"deployed_nodes"`
	FailedNodes   []string               `json:"failed_nodes"`
	Results       map[string]interface{} `json:"results"`
	ErrorMessage  string                 `json:"error_message,omitempty"`
	Duration      time.Duration          `json:"duration"`
}

// NewPluginDeploymentManager creates a new deployment manager
func NewPluginDeploymentManager(registry *registry.PluginRegistry) *PluginDeploymentManager {
	ctx, cancel := context.WithCancel(context.Background())
	
	return &PluginDeploymentManager{
		registry:        registry,
		httpClient:      &http.Client{Timeout: 60 * time.Second},
		deploymentQueue: make([]DeploymentTask, 0),
		ctx:             ctx,
		cancel:          cancel,
	}
}

// SetFlexCoreClient sets the FlexCore client for communication
func (dm *PluginDeploymentManager) SetFlexCoreClient(client plugins.FlexCoreClient) {
	dm.mu.Lock()
	defer dm.mu.Unlock()
	dm.flexcoreClient = client
}

// SetCommunicator sets the plugin communicator
func (dm *PluginDeploymentManager) SetCommunicator(communicator plugins.PluginCommunicator) {
	dm.mu.Lock()
	defer dm.mu.Unlock()
	dm.communicator = communicator
}

// DeployPlugin deploys a plugin to specified FlexCore instances
func (dm *PluginDeploymentManager) DeployPlugin(ctx context.Context, pluginID plugins.PluginID, nodes []string, config map[string]interface{}) error {
	// Create deployment task
	task := DeploymentTask{
		ID:            fmt.Sprintf("deploy-%s-%d", pluginID, time.Now().Unix()),
		PluginID:      pluginID,
		FlexCoreNodes: nodes,
		Action:        "deploy",
		Config:        config,
		Status:        "queued",
		Progress:      0.0,
		CreatedAt:     time.Now(),
	}

	// Add to deployment queue
	dm.mu.Lock()
	dm.deploymentQueue = append(dm.deploymentQueue, task)
	dm.mu.Unlock()

	// Execute deployment asynchronously
	go dm.executeDeploymentTask(ctx, &task)

	return nil
}

// UndeployPlugin removes a plugin from FlexCore instances
func (dm *PluginDeploymentManager) UndeployPlugin(ctx context.Context, pluginID plugins.PluginID, nodes []string) error {
	// Create undeployment task
	task := DeploymentTask{
		ID:            fmt.Sprintf("undeploy-%s-%d", pluginID, time.Now().Unix()),
		PluginID:      pluginID,
		FlexCoreNodes: nodes,
		Action:        "undeploy",
		Status:        "queued",
		Progress:      0.0,
		CreatedAt:     time.Now(),
	}

	// Add to deployment queue
	dm.mu.Lock()
	dm.deploymentQueue = append(dm.deploymentQueue, task)
	dm.mu.Unlock()

	// Execute undeployment asynchronously
	go dm.executeDeploymentTask(ctx, &task)

	return nil
}

// GetDeploymentStatus returns deployment status for a plugin
func (dm *PluginDeploymentManager) GetDeploymentStatus(pluginID plugins.PluginID) ([]plugins.PluginDeployment, error) {
	return dm.registry.GetDeployments(pluginID)
}

// ListDeployments returns all plugin deployments
func (dm *PluginDeploymentManager) ListDeployments() ([]plugins.PluginDeployment, error) {
	allPlugins, err := dm.registry.ListPlugins()
	if err != nil {
		return nil, err
	}

	var allDeployments []plugins.PluginDeployment
	for _, plugin := range allPlugins {
		deployments, err := dm.registry.GetDeployments(plugin.ID)
		if err != nil {
			continue
		}
		allDeployments = append(allDeployments, deployments...)
	}

	return allDeployments, nil
}

// UpdatePluginConfig updates configuration for deployed plugin
func (dm *PluginDeploymentManager) UpdatePluginConfig(ctx context.Context, pluginID plugins.PluginID, nodes []string, config map[string]interface{}) error {
	// Create update task
	task := DeploymentTask{
		ID:            fmt.Sprintf("update-%s-%d", pluginID, time.Now().Unix()),
		PluginID:      pluginID,
		FlexCoreNodes: nodes,
		Action:        "update",
		Config:        config,
		Status:        "queued",
		Progress:      0.0,
		CreatedAt:     time.Now(),
	}

	// Add to deployment queue
	dm.mu.Lock()
	dm.deploymentQueue = append(dm.deploymentQueue, task)
	dm.mu.Unlock()

	// Execute update asynchronously
	go dm.executeDeploymentTask(ctx, &task)

	return nil
}

// RestartPlugin restarts a deployed plugin
func (dm *PluginDeploymentManager) RestartPlugin(ctx context.Context, pluginID plugins.PluginID, nodes []string) error {
	// Create restart task
	task := DeploymentTask{
		ID:            fmt.Sprintf("restart-%s-%d", pluginID, time.Now().Unix()),
		PluginID:      pluginID,
		FlexCoreNodes: nodes,
		Action:        "restart",
		Status:        "queued",
		Progress:      0.0,
		CreatedAt:     time.Now(),
	}

	// Add to deployment queue
	dm.mu.Lock()
	dm.deploymentQueue = append(dm.deploymentQueue, task)
	dm.mu.Unlock()

	// Execute restart asynchronously
	go dm.executeDeploymentTask(ctx, &task)

	return nil
}

// GetDeploymentTasks returns all deployment tasks
func (dm *PluginDeploymentManager) GetDeploymentTasks() []DeploymentTask {
	dm.mu.RLock()
	defer dm.mu.RUnlock()

	result := make([]DeploymentTask, len(dm.deploymentQueue))
	copy(result, dm.deploymentQueue)
	return result
}

// GetDeploymentTask returns a specific deployment task
func (dm *PluginDeploymentManager) GetDeploymentTask(taskID string) (*DeploymentTask, error) {
	dm.mu.RLock()
	defer dm.mu.RUnlock()

	for _, task := range dm.deploymentQueue {
		if task.ID == taskID {
			return &task, nil
		}
	}

	return nil, fmt.Errorf("deployment task %s not found", taskID)
}

// Start starts the deployment manager background services
func (dm *PluginDeploymentManager) Start() error {
	// Start deployment queue processor
	go dm.deploymentQueueProcessor()
	
	// Start deployment health monitor
	go dm.deploymentHealthMonitor()

	return nil
}

// Stop stops the deployment manager
func (dm *PluginDeploymentManager) Stop() error {
	dm.cancel()
	return nil
}

// executeDeploymentTask executes a deployment task
func (dm *PluginDeploymentManager) executeDeploymentTask(ctx context.Context, task *DeploymentTask) {
	// Update task status
	now := time.Now()
	task.StartedAt = &now
	task.Status = "running"
	task.Progress = 0.1
	dm.updateTask(*task)

	var result DeploymentResult
	result.TaskID = task.ID
	result.PluginID = task.PluginID
	result.Results = make(map[string]interface{})

	switch task.Action {
	case "deploy":
		result = dm.executeDeploy(ctx, *task)
	case "undeploy":
		result = dm.executeUndeploy(ctx, *task)
	case "update":
		result = dm.executeUpdate(ctx, *task)
	case "restart":
		result = dm.executeRestart(ctx, *task)
	default:
		result.Success = false
		result.ErrorMessage = fmt.Sprintf("unknown action: %s", task.Action)
	}

	// Update task with result
	completed := time.Now()
	task.CompletedAt = &completed
	task.Results = result.Results
	if result.Success {
		task.Status = "completed"
		task.Progress = 1.0
	} else {
		task.Status = "failed"
		task.ErrorMessage = result.ErrorMessage
	}
	
	dm.updateTask(*task)

	// Notify via communicator if available
	if dm.communicator != nil {
		message := map[string]interface{}{
			"operation":  "deployment.completed",
			"task_id":    task.ID,
			"plugin_id":  task.PluginID,
			"action":     task.Action,
			"success":    result.Success,
			"timestamp":  time.Now(),
		}
		dm.communicator.BroadcastMessage(ctx, plugins.PluginID("deployment-manager"), "", message)
	}
}

// executeDeploy executes plugin deployment
func (dm *PluginDeploymentManager) executeDeploy(ctx context.Context, task DeploymentTask) DeploymentResult {
	result := DeploymentResult{
		TaskID:        task.ID,
		PluginID:      task.PluginID,
		DeployedNodes: make([]string, 0),
		FailedNodes:   make([]string, 0),
		Results:       make(map[string]interface{}),
	}

	startTime := time.Now()

	// Get plugin binary path
	binaryPath, err := dm.registry.GetPluginBinary(task.PluginID)
	if err != nil {
		result.Success = false
		result.ErrorMessage = fmt.Sprintf("failed to get plugin binary: %v", err)
		return result
	}

	// Deploy to each FlexCore node
	for i, nodeURL := range task.FlexCoreNodes {
		task.Progress = 0.2 + (0.6 * float64(i) / float64(len(task.FlexCoreNodes)))
		dm.updateTask(task)

		if err := dm.deployToNode(ctx, nodeURL, task.PluginID, binaryPath, task.Config); err != nil {
			result.FailedNodes = append(result.FailedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": false,
				"error":   err.Error(),
			}
		} else {
			result.DeployedNodes = append(result.DeployedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": true,
				"message": "deployed successfully",
			}
		}
	}

	// Update registry with deployment information
	if len(result.DeployedNodes) > 0 {
		deployment := plugins.PluginDeployment{
			PluginID:        task.PluginID,
			FlexCoreNodes:   result.DeployedNodes,
			Status:          plugins.PluginStatusDeployed,
			Config:          task.Config,
			DeployedAt:      time.Now(),
			LastHealthCheck: time.Now(),
			HealthStatus:    "healthy",
		}
		dm.registry.AddDeployment(deployment)
	}

	result.Success = len(result.FailedNodes) == 0
	result.Duration = time.Since(startTime)

	return result
}

// executeUndeploy executes plugin undeployment
func (dm *PluginDeploymentManager) executeUndeploy(ctx context.Context, task DeploymentTask) DeploymentResult {
	result := DeploymentResult{
		TaskID:        task.ID,
		PluginID:      task.PluginID,
		DeployedNodes: make([]string, 0),
		FailedNodes:   make([]string, 0),
		Results:       make(map[string]interface{}),
	}

	startTime := time.Now()

	// Undeploy from each FlexCore node
	for i, nodeURL := range task.FlexCoreNodes {
		task.Progress = 0.2 + (0.6 * float64(i) / float64(len(task.FlexCoreNodes)))
		dm.updateTask(task)

		if err := dm.undeployFromNode(ctx, nodeURL, task.PluginID); err != nil {
			result.FailedNodes = append(result.FailedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": false,
				"error":   err.Error(),
			}
		} else {
			result.DeployedNodes = append(result.DeployedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": true,
				"message": "undeployed successfully",
			}
		}
	}

	// Update registry
	if len(result.DeployedNodes) > 0 {
		dm.registry.RemoveDeployment(task.PluginID, result.DeployedNodes)
	}

	result.Success = len(result.FailedNodes) == 0
	result.Duration = time.Since(startTime)

	return result
}

// executeUpdate executes plugin configuration update
func (dm *PluginDeploymentManager) executeUpdate(ctx context.Context, task DeploymentTask) DeploymentResult {
	result := DeploymentResult{
		TaskID:        task.ID,
		PluginID:      task.PluginID,
		DeployedNodes: make([]string, 0),
		FailedNodes:   make([]string, 0),
		Results:       make(map[string]interface{}),
	}

	startTime := time.Now()

	// Update configuration on each FlexCore node
	for i, nodeURL := range task.FlexCoreNodes {
		task.Progress = 0.2 + (0.6 * float64(i) / float64(len(task.FlexCoreNodes)))
		dm.updateTask(task)

		if err := dm.updateConfigOnNode(ctx, nodeURL, task.PluginID, task.Config); err != nil {
			result.FailedNodes = append(result.FailedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": false,
				"error":   err.Error(),
			}
		} else {
			result.DeployedNodes = append(result.DeployedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": true,
				"message": "configuration updated successfully",
			}
		}
	}

	result.Success = len(result.FailedNodes) == 0
	result.Duration = time.Since(startTime)

	return result
}

// executeRestart executes plugin restart
func (dm *PluginDeploymentManager) executeRestart(ctx context.Context, task DeploymentTask) DeploymentResult {
	result := DeploymentResult{
		TaskID:        task.ID,
		PluginID:      task.PluginID,
		DeployedNodes: make([]string, 0),
		FailedNodes:   make([]string, 0),
		Results:       make(map[string]interface{}),
	}

	startTime := time.Now()

	// Restart plugin on each FlexCore node
	for i, nodeURL := range task.FlexCoreNodes {
		task.Progress = 0.2 + (0.6 * float64(i) / float64(len(task.FlexCoreNodes)))
		dm.updateTask(task)

		if err := dm.restartPluginOnNode(ctx, nodeURL, task.PluginID); err != nil {
			result.FailedNodes = append(result.FailedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": false,
				"error":   err.Error(),
			}
		} else {
			result.DeployedNodes = append(result.DeployedNodes, nodeURL)
			result.Results[nodeURL] = map[string]interface{}{
				"success": true,
				"message": "restarted successfully",
			}
		}
	}

	result.Success = len(result.FailedNodes) == 0
	result.Duration = time.Since(startTime)

	return result
}

// deployToNode deploys a plugin to a specific FlexCore node
func (dm *PluginDeploymentManager) deployToNode(ctx context.Context, nodeURL string, pluginID plugins.PluginID, binaryPath string, config map[string]interface{}) error {
	// Open plugin binary file
	file, err := os.Open(binaryPath)
	if err != nil {
		return fmt.Errorf("failed to open plugin binary: %w", err)
	}
	defer file.Close()

	// Create multipart form for file upload
	var requestBody bytes.Buffer
	writer := multipart.NewWriter(&requestBody)

	// Add plugin binary
	part, err := writer.CreateFormFile("plugin_binary", filepath.Base(binaryPath))
	if err != nil {
		return fmt.Errorf("failed to create form file: %w", err)
	}

	if _, err := io.Copy(part, file); err != nil {
		return fmt.Errorf("failed to copy file data: %w", err)
	}

	// Add plugin configuration
	configJSON, _ := json.Marshal(config)
	writer.WriteField("plugin_id", string(pluginID))
	writer.WriteField("config", string(configJSON))

	writer.Close()

	// Send deployment request to FlexCore node
	url := fmt.Sprintf("%s/api/v1/plugins/deploy", nodeURL)
	req, err := http.NewRequestWithContext(ctx, "POST", url, &requestBody)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	resp, err := dm.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send deployment request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("deployment failed with status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// undeployFromNode undeploys a plugin from a specific FlexCore node
func (dm *PluginDeploymentManager) undeployFromNode(ctx context.Context, nodeURL string, pluginID plugins.PluginID) error {
	url := fmt.Sprintf("%s/api/v1/plugins/%s/undeploy", nodeURL, pluginID)
	req, err := http.NewRequestWithContext(ctx, "DELETE", url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := dm.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send undeployment request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("undeployment failed with status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// updateConfigOnNode updates plugin configuration on a specific FlexCore node
func (dm *PluginDeploymentManager) updateConfigOnNode(ctx context.Context, nodeURL string, pluginID plugins.PluginID, config map[string]interface{}) error {
	configJSON, _ := json.Marshal(config)
	
	url := fmt.Sprintf("%s/api/v1/plugins/%s/config", nodeURL, pluginID)
	req, err := http.NewRequestWithContext(ctx, "PUT", url, bytes.NewBuffer(configJSON))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := dm.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send config update request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("config update failed with status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// restartPluginOnNode restarts a plugin on a specific FlexCore node
func (dm *PluginDeploymentManager) restartPluginOnNode(ctx context.Context, nodeURL string, pluginID plugins.PluginID) error {
	url := fmt.Sprintf("%s/api/v1/plugins/%s/restart", nodeURL, pluginID)
	req, err := http.NewRequestWithContext(ctx, "POST", url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := dm.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send restart request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("restart failed with status %d: %s", resp.StatusCode, string(body))
	}

	return nil
}

// Helper methods

func (dm *PluginDeploymentManager) updateTask(task DeploymentTask) {
	dm.mu.Lock()
	defer dm.mu.Unlock()

	for i, t := range dm.deploymentQueue {
		if t.ID == task.ID {
			dm.deploymentQueue[i] = task
			break
		}
	}
}

func (dm *PluginDeploymentManager) deploymentQueueProcessor() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-dm.ctx.Done():
			return
		case <-ticker.C:
			dm.processQueuedTasks()
		}
	}
}

func (dm *PluginDeploymentManager) deploymentHealthMonitor() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-dm.ctx.Done():
			return
		case <-ticker.C:
			dm.monitorDeploymentHealth()
		}
	}
}

func (dm *PluginDeploymentManager) processQueuedTasks() {
	// Process queued tasks that haven't been started yet
	// This is a placeholder - actual implementation would be more sophisticated
}

func (dm *PluginDeploymentManager) monitorDeploymentHealth() {
	// Monitor health of all deployments
	// This is a placeholder - actual implementation would check plugin health on all nodes
}