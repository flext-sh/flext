package registry

import (
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
)

// GetRegistryStats returns statistics about the plugin registry
func (pr *PluginRegistry) GetRegistryStats() map[string]interface{} {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	return map[string]interface{}{
		"total_plugins":      len(pr.plugins),
		"total_deployments":  pr.getTotalDeployments(),
		"total_nodes":        len(pr.flexcoreNodes),
		"healthy_nodes":      pr.getHealthyNodesCount(),
		"plugins_by_type":    pr.getPluginsByType(),
		"deployment_summary": pr.getDeploymentSummary(),
		"timestamp":          time.Now(),
	}
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
