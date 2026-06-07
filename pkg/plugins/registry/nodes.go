package registry

import (
	"fmt"
	"time"

	"github.com/flext-sh/flext/pkg/plugins"
)

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
		if node.Status == "healthy" && nodeSupportsCapability(node, requiredCapability) {
			result = append(result, node)
		}
	}

	return result
}

func nodeSupportsCapability(node FlexCoreNode, requiredCapability string) bool {
	canRun := false
	for _, capability := range node.Capabilities {
		if capability == requiredCapability || capability == "plugin.all.runtime" {
			canRun = true
			break
		}
	}
	return canRun
}

func (pr *PluginRegistry) checkNodeHealth() {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	now := time.Now()
	for url, node := range pr.flexcoreNodes {
		if now.Sub(node.LastSeen) > 2*time.Minute {
			node.Status = "unhealthy"
			pr.flexcoreNodes[url] = node
		}
	}
}
