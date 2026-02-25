// Package registry - Plugin Registry Implementation for FLEXT Service
//
// This package implements the plugin registry that manages all deployable plugins
// in the FLEXT ecosystem. The registry runs in FLEXT Service (Control Panel) and
// coordinates plugin deployment to multiple FlexCore instances.
//
// Architecture:
//   - FLEXT Service: Central plugin registry and deployment coordination
//   - FlexCore Instances: Distributed runtime that receives and executes plugins
//   - Plugin Binaries: .so/.dll files that implement the Plugin interface
//
// Plugin Registry Functions:
//   - Plugin registration and discovery
//   - Plugin metadata management
//   - Plugin deployment coordination
//   - Inter-plugin communication coordination
//   - Plugin lifecycle management
//
// Author: FLEXT Development Team
// Version: 2.0.0
// License: MIT
package registry

import (
	"context"
	"fmt"
	"strings"
	"sync"
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
)

// PluginRegistry implements the central plugin registry for FLEXT Service
type PluginRegistry struct {
	plugins           map[plugins.PluginID]plugins.PluginMetadata
	deployments       map[plugins.PluginID][]plugins.PluginDeployment
	flexcoreNodes     map[string]FlexCoreNode
	pluginBinaries    map[plugins.PluginID]string
	communicator      plugins.PluginCommunicator
	deploymentManager plugins.PluginDeploymentManager
	mu                sync.RWMutex
	ctx               context.Context
	cancel            context.CancelFunc
}

// FlexCoreNode represents a FlexCore instance that can run plugins
type FlexCoreNode struct {
	URL           string                 `json:"url"`
	Name          string                 `json:"name"`
	Status        string                 `json:"status"`
	LastSeen      time.Time              `json:"last_seen"`
	LoadedPlugins []plugins.PluginID     `json:"loaded_plugins"`
	Capabilities  []string               `json:"capabilities"`
	Resources     map[string]interface{} `json:"resources"`
	Configuration map[string]interface{} `json:"configuration"`
}

// NewPluginRegistry creates a new plugin registry instance
func NewPluginRegistry() *PluginRegistry {
	ctx, cancel := context.WithCancel(context.Background())

	return &PluginRegistry{
		plugins:        make(map[plugins.PluginID]plugins.PluginMetadata),
		deployments:    make(map[plugins.PluginID][]plugins.PluginDeployment),
		flexcoreNodes:  make(map[string]FlexCoreNode),
		pluginBinaries: make(map[plugins.PluginID]string),
		ctx:            ctx,
		cancel:         cancel,
	}
}

// RegisterPlugin registers a new plugin in the registry
func (pr *PluginRegistry) RegisterPlugin(plugin plugins.Plugin) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	metadata := plugin.Metadata()

	// Validate plugin metadata
	if err := pr.validatePluginMetadata(metadata); err != nil {
		return fmt.Errorf("plugin metadata validation failed: %w", err)
	}

	// Check for duplicate plugins
	if _, exists := pr.plugins[metadata.ID]; exists {
		return fmt.Errorf("plugin with ID %s already exists", metadata.ID)
	}

	// Register plugin metadata
	pr.plugins[metadata.ID] = metadata

	// Initialize empty deployments
	pr.deployments[metadata.ID] = make([]plugins.PluginDeployment, 0)

	return nil
}

// UnregisterPlugin removes a plugin from the registry
func (pr *PluginRegistry) UnregisterPlugin(pluginID plugins.PluginID) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	// Check if plugin exists
	if _, exists := pr.plugins[pluginID]; !exists {
		return fmt.Errorf("plugin with ID %s not found", pluginID)
	}

	// Check if plugin is deployed anywhere
	if deployments, exists := pr.deployments[pluginID]; exists && len(deployments) > 0 {
		return fmt.Errorf("cannot unregister plugin %s: still deployed on %d nodes", pluginID, len(deployments))
	}

	// Remove plugin
	delete(pr.plugins, pluginID)
	delete(pr.deployments, pluginID)
	delete(pr.pluginBinaries, pluginID)

	return nil
}

// GetPlugin retrieves a plugin by ID
func (pr *PluginRegistry) GetPlugin(pluginID plugins.PluginID) (plugins.Plugin, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	metadata, exists := pr.plugins[pluginID]
	if !exists {
		return nil, fmt.Errorf("plugin with ID %s not found", pluginID)
	}

	// Create plugin instance based on type
	return pr.createPluginInstance(metadata)
}

// ListPlugins returns all registered plugins
func (pr *PluginRegistry) ListPlugins() ([]plugins.PluginMetadata, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0, len(pr.plugins))
	for _, metadata := range pr.plugins {
		result = append(result, metadata)
	}

	return result, nil
}

// ListPluginsByType returns plugins of specific type
func (pr *PluginRegistry) ListPluginsByType(pluginType plugins.PluginType) ([]plugins.PluginMetadata, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0)
	for _, metadata := range pr.plugins {
		if metadata.Type == pluginType {
			result = append(result, metadata)
		}
	}

	return result, nil
}

// FindPluginsByCapability finds plugins with specific capability
func (pr *PluginRegistry) FindPluginsByCapability(capability string) ([]plugins.PluginMetadata, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0)
	for _, metadata := range pr.plugins {
		for _, cap := range metadata.Capabilities {
			if cap == capability {
				result = append(result, metadata)
				break
			}
		}
	}

	return result, nil
}

// RegisterFlexCoreNode registers a FlexCore node that can run plugins
func (pr *PluginRegistry) RegisterFlexCoreNode(node FlexCoreNode) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	node.LastSeen = time.Now()
	pr.flexcoreNodes[node.URL] = node

	return nil
}

// UnregisterFlexCoreNode removes a FlexCore node from the registry
func (pr *PluginRegistry) UnregisterFlexCoreNode(nodeURL string) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	// Check if node has any deployed plugins
	for pluginID, deployments := range pr.deployments {
		for _, deployment := range deployments {
			for _, deployedNode := range deployment.FlexCoreNodes {
				if deployedNode == nodeURL {
					return fmt.Errorf("cannot unregister node %s: plugin %s is still deployed", nodeURL, pluginID)
				}
			}
		}
	}

	delete(pr.flexcoreNodes, nodeURL)
	return nil
}

// ListFlexCoreNodes returns all registered FlexCore nodes
func (pr *PluginRegistry) ListFlexCoreNodes() []FlexCoreNode {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]FlexCoreNode, 0, len(pr.flexcoreNodes))
	for _, node := range pr.flexcoreNodes {
		result = append(result, node)
	}

	return result
}

// GetAvailableNodes returns FlexCore nodes that can run a specific plugin type
func (pr *PluginRegistry) GetAvailableNodes(pluginType plugins.PluginType) []FlexCoreNode {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]FlexCoreNode, 0)
	requiredCapability := fmt.Sprintf("plugin.%s.runtime", pluginType)

	for _, node := range pr.flexcoreNodes {
		if node.Status == "healthy" {
			// Check if node supports this plugin type
			canRun := false
			for _, capability := range node.Capabilities {
				if capability == requiredCapability || capability == "plugin.all.runtime" {
					canRun = true
					break
				}
			}
			if canRun {
				result = append(result, node)
			}
		}
	}

	return result
}

// SetPluginBinary associates a plugin with its binary file path
func (pr *PluginRegistry) SetPluginBinary(pluginID plugins.PluginID, binaryPath string) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	if _, exists := pr.plugins[pluginID]; !exists {
		return fmt.Errorf("plugin with ID %s not found", pluginID)
	}

	pr.pluginBinaries[pluginID] = binaryPath
	return nil
}

// GetPluginBinary returns the binary path for a plugin
func (pr *PluginRegistry) GetPluginBinary(pluginID plugins.PluginID) (string, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	binaryPath, exists := pr.pluginBinaries[pluginID]
	if !exists {
		return "", fmt.Errorf("binary path not found for plugin %s", pluginID)
	}

	return binaryPath, nil
}

// SetCommunicator sets the plugin communicator for inter-plugin messaging
func (pr *PluginRegistry) SetCommunicator(communicator plugins.PluginCommunicator) {
	pr.mu.Lock()
	defer pr.mu.Unlock()
	pr.communicator = communicator
}

// SetDeploymentManager sets the plugin deployment manager
func (pr *PluginRegistry) SetDeploymentManager(deploymentManager plugins.PluginDeploymentManager) {
	pr.mu.Lock()
	defer pr.mu.Unlock()
	pr.deploymentManager = deploymentManager
}

// GetDeployments returns all deployments for a plugin
func (pr *PluginRegistry) GetDeployments(pluginID plugins.PluginID) ([]plugins.PluginDeployment, error) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	deployments, exists := pr.deployments[pluginID]
	if !exists {
		return nil, fmt.Errorf("plugin with ID %s not found", pluginID)
	}

	return deployments, nil
}

// AddDeployment adds a deployment record for a plugin
func (pr *PluginRegistry) AddDeployment(deployment plugins.PluginDeployment) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	if _, exists := pr.plugins[deployment.PluginID]; !exists {
		return fmt.Errorf("plugin with ID %s not found", deployment.PluginID)
	}

	deployments := pr.deployments[deployment.PluginID]
	deployments = append(deployments, deployment)
	pr.deployments[deployment.PluginID] = deployments

	return nil
}

// UpdateDeployment updates a deployment record
func (pr *PluginRegistry) UpdateDeployment(deployment plugins.PluginDeployment) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	deployments, exists := pr.deployments[deployment.PluginID]
	if !exists {
		return fmt.Errorf("plugin with ID %s not found", deployment.PluginID)
	}

	// Find and update the deployment
	for i, dep := range deployments {
		if pr.deploymentsMatch(dep, deployment) {
			deployments[i] = deployment
			pr.deployments[deployment.PluginID] = deployments
			return nil
		}
	}

	return fmt.Errorf("deployment not found for plugin %s", deployment.PluginID)
}

// RemoveDeployment removes a deployment record
func (pr *PluginRegistry) RemoveDeployment(pluginID plugins.PluginID, nodes []string) error {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	deployments, exists := pr.deployments[pluginID]
	if !exists {
		return fmt.Errorf("plugin with ID %s not found", pluginID)
	}

	// Filter out deployments matching the nodes
	filteredDeployments := make([]plugins.PluginDeployment, 0)
	for _, deployment := range deployments {
		if !pr.nodesMatch(deployment.FlexCoreNodes, nodes) {
			filteredDeployments = append(filteredDeployments, deployment)
		}
	}

	pr.deployments[pluginID] = filteredDeployments
	return nil
}

// GetRegistryStats returns statistics about the plugin registry
func (pr *PluginRegistry) GetRegistryStats() map[string]interface{} {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	stats := map[string]interface{}{
		"total_plugins":      len(pr.plugins),
		"total_deployments":  pr.getTotalDeployments(),
		"total_nodes":        len(pr.flexcoreNodes),
		"healthy_nodes":      pr.getHealthyNodesCount(),
		"plugins_by_type":    pr.getPluginsByType(),
		"deployment_summary": pr.getDeploymentSummary(),
		"timestamp":          time.Now(),
	}

	return stats
}

// SearchPlugins searches plugins by name, type, or capability
func (pr *PluginRegistry) SearchPlugins(query string) []plugins.PluginMetadata {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	result := make([]plugins.PluginMetadata, 0)

	for _, metadata := range pr.plugins {
		// Search in name, description, type, and capabilities
		if pr.matchesQuery(metadata, query) {
			result = append(result, metadata)
		}
	}

	return result
}

// Start starts the plugin registry background services
func (pr *PluginRegistry) Start() error {
	// Start node health checking
	go pr.nodeHealthChecker()

	// Start deployment monitoring
	go pr.deploymentMonitor()

	return nil
}

// Stop stops the plugin registry
func (pr *PluginRegistry) Stop() error {
	pr.cancel()
	return nil
}

// Helper methods

func (pr *PluginRegistry) validatePluginMetadata(metadata plugins.PluginMetadata) error {
	if metadata.ID == "" {
		return fmt.Errorf("plugin ID is required")
	}
	if metadata.Name == "" {
		return fmt.Errorf("plugin name is required")
	}
	if metadata.Version == "" {
		return fmt.Errorf("plugin version is required")
	}
	if metadata.Type == "" {
		return fmt.Errorf("plugin type is required")
	}
	return nil
}

func (pr *PluginRegistry) createPluginInstance(metadata plugins.PluginMetadata) (plugins.Plugin, error) {
	// This would normally load the plugin from binary
	// For now, create mock instances based on type
	switch metadata.Type {
	case plugins.PluginTypeMeltano:
		return nil, fmt.Errorf("plugin instance creation not implemented for %s", metadata.Type)
	case plugins.PluginTypeRay:
		return nil, fmt.Errorf("plugin instance creation not implemented for %s", metadata.Type)
	case plugins.PluginTypeKubernetes:
		return nil, fmt.Errorf("plugin instance creation not implemented for %s", metadata.Type)
	default:
		return nil, fmt.Errorf("unknown plugin type: %s", metadata.Type)
	}
}

func (pr *PluginRegistry) deploymentsMatch(dep1, dep2 plugins.PluginDeployment) bool {
	return pr.nodesMatch(dep1.FlexCoreNodes, dep2.FlexCoreNodes)
}

func (pr *PluginRegistry) nodesMatch(nodes1, nodes2 []string) bool {
	if len(nodes1) != len(nodes2) {
		return false
	}

	nodeMap := make(map[string]bool)
	for _, node := range nodes1 {
		nodeMap[node] = true
	}

	for _, node := range nodes2 {
		if !nodeMap[node] {
			return false
		}
	}

	return true
}

func (pr *PluginRegistry) getTotalDeployments() int {
	total := 0
	for _, deployments := range pr.deployments {
		total += len(deployments)
	}
	return total
}

func (pr *PluginRegistry) getHealthyNodesCount() int {
	count := 0
	for _, node := range pr.flexcoreNodes {
		if node.Status == "healthy" {
			count++
		}
	}
	return count
}

func (pr *PluginRegistry) getPluginsByType() map[string]int {
	counts := make(map[string]int)
	for _, metadata := range pr.plugins {
		counts[string(metadata.Type)]++
	}
	return counts
}

func (pr *PluginRegistry) getDeploymentSummary() map[string]interface{} {
	summary := make(map[string]interface{})

	for pluginID, deployments := range pr.deployments {
		if len(deployments) > 0 {
			summary[string(pluginID)] = map[string]interface{}{
				"deployment_count": len(deployments),
				"total_nodes":      pr.getTotalNodesForPlugin(deployments),
			}
		}
	}

	return summary
}

func (pr *PluginRegistry) getTotalNodesForPlugin(deployments []plugins.PluginDeployment) int {
	nodeSet := make(map[string]bool)
	for _, deployment := range deployments {
		for _, node := range deployment.FlexCoreNodes {
			nodeSet[node] = true
		}
	}
	return len(nodeSet)
}

func (pr *PluginRegistry) matchesQuery(metadata plugins.PluginMetadata, query string) bool {
	// Simple contains matching - could be enhanced with fuzzy search
	queryLower := strings.ToLower(query)

	if strings.Contains(strings.ToLower(metadata.Name), queryLower) {
		return true
	}
	if strings.Contains(strings.ToLower(metadata.Description), queryLower) {
		return true
	}
	if strings.Contains(strings.ToLower(string(metadata.Type)), queryLower) {
		return true
	}

	for _, capability := range metadata.Capabilities {
		if strings.Contains(strings.ToLower(capability), queryLower) {
			return true
		}
	}

	return false
}

func (pr *PluginRegistry) nodeHealthChecker() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-pr.ctx.Done():
			return
		case <-ticker.C:
			pr.checkNodeHealth()
		}
	}
}

func (pr *PluginRegistry) deploymentMonitor() {
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-pr.ctx.Done():
			return
		case <-ticker.C:
			pr.monitorDeployments()
		}
	}
}

func (pr *PluginRegistry) checkNodeHealth() {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	now := time.Now()
	for url, node := range pr.flexcoreNodes {
		// Check if node hasn't been seen for too long
		if now.Sub(node.LastSeen) > 2*time.Minute {
			node.Status = "unhealthy"
			pr.flexcoreNodes[url] = node
		}
	}
}

func (pr *PluginRegistry) monitorDeployments() {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	// Monitor deployment health and update status
	// This could be enhanced to actually check deployment status via FlexCore API
	for pluginID, deployments := range pr.deployments {
		for i, deployment := range deployments {
			// Update health check timestamp
			deployment.LastHealthCheck = time.Now()

			// Check if all nodes are healthy
			allNodesHealthy := true
			for _, nodeURL := range deployment.FlexCoreNodes {
				if node, exists := pr.flexcoreNodes[nodeURL]; !exists || node.Status != "healthy" {
					allNodesHealthy = false
					break
				}
			}

			if allNodesHealthy {
				deployment.HealthStatus = "healthy"
			} else {
				deployment.HealthStatus = "unhealthy"
			}

			deployments[i] = deployment
		}
		pr.deployments[pluginID] = deployments
	}
}
