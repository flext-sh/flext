package registry

import (
	"fmt"
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
)

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

	filteredDeployments := make([]plugins.PluginDeployment, 0)
	for _, deployment := range deployments {
		if !pr.nodesMatch(deployment.FlexCoreNodes, nodes) {
			filteredDeployments = append(filteredDeployments, deployment)
		}
	}

	pr.deployments[pluginID] = filteredDeployments
	return nil
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

func (pr *PluginRegistry) monitorDeployments() {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	for pluginID, deployments := range pr.deployments {
		for i, deployment := range deployments {
			deployment.LastHealthCheck = time.Now()
			deployment.HealthStatus = pr.deploymentHealthStatus(deployment)
			deployments[i] = deployment
		}
		pr.deployments[pluginID] = deployments
	}
}

func (pr *PluginRegistry) deploymentHealthStatus(deployment plugins.PluginDeployment) string {
	status := "healthy"
	for _, nodeURL := range deployment.FlexCoreNodes {
		if node, exists := pr.flexcoreNodes[nodeURL]; !exists || node.Status != "healthy" {
			status = "unhealthy"
			break
		}
	}
	return status
}
